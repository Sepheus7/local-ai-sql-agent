from __future__ import annotations

import re


FORBIDDEN_PATTERNS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bATTACH\b",
    r"\bPRAGMA\b",
]


def is_select_only(sql: str) -> bool:
    return bool(re.match(r"^\s*SELECT\b", sql.strip(), flags=re.IGNORECASE))


def contains_forbidden(sql: str) -> bool:
    return any(re.search(p, sql, flags=re.IGNORECASE) for p in FORBIDDEN_PATTERNS)


def ensure_limit(sql: str, default_limit: int = 500) -> str:
    if re.search(r"\bLIMIT\s+\d+\b", sql, flags=re.IGNORECASE):
        return sql
    return f"{sql.rstrip(';')} LIMIT {default_limit};"


def strip_code_fences(text: str) -> str:
    text = text.strip()
    # Remove triple backticks blocks if present
    if text.startswith("```"):
        # remove first fence line
        parts = text.split("\n", 1)
        text = parts[1] if len(parts) == 2 else text
        if text.endswith("```"):
            text = text[: -3]
    return text.strip()


def extract_first_select(text: str) -> str:
    """Extract the first SQL SELECT statement from a model response.
    Handles plain text, code fences, and inline prose.
    """
    cleaned = strip_code_fences(text)
    # Find first SELECT ... ; (non-greedy)
    match = re.search(r"SELECT[\s\S]*?;", cleaned, flags=re.IGNORECASE)
    if match:
        return match.group(0).strip()
    # Fallback: if response looks like a single line SELECT without semicolon
    line_match = re.search(r"^\s*SELECT[\s\S]*", cleaned, flags=re.IGNORECASE)
    if line_match:
        sql = line_match.group(0).strip()
        if not sql.endswith(";"):
            sql += ";"
        return sql
    return cleaned


