from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator, List, Tuple, Dict, Set


DB_PATH = os.getenv("SQLITE_PATH", os.path.abspath("test.db"))


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def execute_readonly(sql: str, timeout_sec: int = 5) -> Tuple[List[str], List[Tuple]]:
    with get_conn() as conn:
        conn.execute("PRAGMA query_only = ON;")
        cursor = conn.execute(sql)
        col_names = [d[0] for d in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
    return col_names, rows


def list_tables() -> List[str]:
    with get_conn() as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        return [r[0] for r in cursor.fetchall()]


def preview_table(table_name: str, limit: int = 10) -> Tuple[List[str], List[Tuple]]:
    query = f"SELECT * FROM {table_name} LIMIT {limit};"
    return execute_readonly(query)


def get_table_columns(table_name: str) -> List[Tuple[str, str]]:
    with get_conn() as conn:
        rows = conn.execute(f"PRAGMA table_info({table_name});").fetchall()
        # rows: cid, name, type, notnull, dflt_value, pk
        return [(r[1], r[2]) for r in rows]


def get_schema_overview(max_tables: int = 20, max_columns: int = 50) -> str:
    tables = [t for t in list_tables() if not t.startswith("sqlite_")]
    lines: List[str] = []
    for t in tables[:max_tables]:
        cols = get_table_columns(t)
        if len(cols) > max_columns:
            cols = cols[:max_columns]
        col_str = ", ".join([f"{name} {dtype}" for name, dtype in cols])
        lines.append(f"Table {t}: {col_str}")
    return "\n".join(lines)


def get_foreign_keys(table_name: str) -> List[Tuple[str, str, str]]:
    """Return list of (from_column, ref_table, ref_column) for the table."""
    with get_conn() as conn:
        rows = conn.execute(f"PRAGMA foreign_key_list({table_name});").fetchall()
        fks: List[Tuple[str, str, str]] = []
        for r in rows:
            # r columns: id, seq, table, from, to, on_update, on_delete, match
            fks.append((r[3], r[2], r[4]))
        return fks


def build_erd_dot(max_columns_per_table: int = 12, include_columns: bool = True) -> str:
    """Build a Graphviz DOT ERD with basic aesthetics and heuristic links.

    If SQLite tables do not declare foreign keys, we infer edges using common
    naming patterns like playerID/player_id -> player.
    """
    tables = [t for t in list_tables() if not t.startswith("sqlite_")]
    if include_columns:
        node_line = '  node [shape=record, style="rounded,filled", fillcolor="#F6F8FA", color="#9AA0A6", fontname="Helvetica", fontsize=10];'
    else:
        node_line = '  node [shape=box, style="rounded,filled", fillcolor="#F6F8FA", color="#9AA0A6", fontname="Helvetica", fontsize=11];'

    lines: List[str] = [
        "digraph ERD {",
        "  rankdir=LR;",
        "  bgcolor=white;",
        node_line,
        "  edge [color=\"#9AA0A6\", arrowsize=0.7, fontname=\"Helvetica\", fontsize=9];",
    ]

    # Collect columns lower-cased for heuristics
    table_to_cols: Dict[str, List[str]] = {}
    for t in tables:
        cols = [c for c, _ in get_table_columns(t)]
        table_to_cols[t] = [c.lower() for c in cols]

    # Nodes with a limited list of columns
    for t in tables:
        safe_t = t.replace('-', '_')
        if include_columns:
            raw_cols = get_table_columns(t)
            cols = raw_cols[:max_columns_per_table] if max_columns_per_table else raw_cols
            field_lines = [f"<f{i}> {name}: {dtype}" for i, (name, dtype) in enumerate(cols)] or ["(no columns)"]
            title = t
            label = "{" + f"{title}|" + "|".join(field_lines) + "}"
            lines.append(f"  {safe_t} [label=\"{label}\"];")
        else:
            lines.append(f"  {safe_t} [label=\"{t}\"];")

    # Build edges: prefer declared FKs; then add inferred links
    edges: Set[Tuple[str, str, str]] = set()
    for t in tables:
        for from_col, ref_table, ref_col in get_foreign_keys(t):
            edges.add((t, ref_table, f"{from_col}->{ref_col}"))

    # Heuristic: link tables with playerID/player_id to 'player'
    player_table = None
    for candidate in ("player", "players"):
        if candidate in tables:
            player_table = candidate
            break
        for t in tables:
            if candidate in t.lower():
                player_table = t
                break
        if player_table:
            break

    if player_table:
        for t, cols in table_to_cols.items():
            if t == player_table:
                continue
            if any(c in cols for c in ("playerid", "player_id")):
                edges.add((t, player_table, "player_id"))

    # Generic heuristic: foo_id -> foo / foos
    def normalize(name: str) -> str:
        return name.lower().strip()

    table_names_norm = {normalize(t): t for t in tables}
    for t, cols in table_to_cols.items():
        for c in cols:
            if c.endswith("_id") or c.endswith("id"):
                base = c[:-3] if c.endswith("_id") else c[:-2]
                for cand in (base, base + "s"):
                    if cand and cand in table_names_norm:
                        target = table_names_norm[cand]
                        if target != t:
                            edges.add((t, target, c))

    # Render edges
    for src, dst, label in sorted(edges):
        safe_src = src.replace('-', '_')
        safe_dst = dst.replace('-', '_')
        lines.append(f"  {safe_src} -> {safe_dst} [label=\"{label}\"];")

    lines.append("}")
    return "\n".join(lines)


