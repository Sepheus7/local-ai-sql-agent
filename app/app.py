import os
import sys
import time
from typing import List

import pandas as pd
import streamlit as st

# Ensure project root is on sys.path when running via "streamlit run app/app.py"
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.agent.sql_guardrails import ensure_limit, contains_forbidden, is_select_only
from src.db.sqlite import execute_readonly, list_tables, preview_table, get_schema_overview, build_erd_dot
from src.agent.providers import (
    get_provider,
    LLMProvider,
    generate_sql_openai,
    generate_sql_bedrock,
)


st.set_page_config(page_title="AI SQL Agent (Bedrock)", layout="wide")


def render_schema_help():
    st.sidebar.header("Settings")
    st.sidebar.info("Local SQLite DB (test.db). Use the Data model tab to seed and inspect schema.")


def main():
    st.title("AI SQL Agent — Amazon Bedrock + Streamlit")
    st.write("Enter a natural language question. The agent will propose SQL and run it safely.")

    render_schema_help()

    if "proposed_sql" not in st.session_state:
        st.session_state.proposed_sql = None

    provider = st.sidebar.selectbox("LLM Provider", [LLMProvider.OPENAI, LLMProvider.BEDROCK], index=0)
    if provider == LLMProvider.OPENAI:
        openai_key = st.sidebar.text_input("OPENAI_API_KEY", type="password")
    else:
        st.sidebar.info("Using AWS credentials from env for Bedrock")

    # Tabs for main content
    tab_query, tab_model = st.tabs(["Query", "Data model"])

    with tab_query:
        question = st.text_input("Ask a question")
        generate_clicked = st.button("Generate SQL")

    with tab_model:
        st.subheader("Data model")
        if st.button("Seed demo data"):
            try:
                from src.data.seed_sqlite import seed_baseball
                seed_baseball()
                st.success("Seeded Baseball tables into SQLite.")
            except Exception as e:
                st.error(str(e))

        st.caption("Schema overview (tables and columns):")
        st.code(get_schema_overview() or "No tables found. Use Seed demo data.")

        st.caption("Entity-Relationship Diagram (auto-generated):")
        # Show a cleaner ERD with only table names and relationship arrows
        dot = build_erd_dot(include_columns=False)
        st.graphviz_chart(dot)
        with st.expander("Show ERD DOT source"):
            st.code(dot, language="dot")

        # Schema dropdowns: tables → columns and types
        st.caption("Schema details:")
        tbls = [t for t in list_tables() if not t.startswith("sqlite_")]
        for t in tbls:
            with st.expander(t, expanded=False):
                try:
                    from src.db.sqlite import get_table_columns
                    cols = get_table_columns(t)
                    if cols:
                        df_cols = pd.DataFrame(cols, columns=["column", "type"])
                        st.table(df_cols)
                    else:
                        st.write("No columns.")
                except Exception as e:
                    st.write(str(e))

        # Table row counts chart
        try:
            tbls = [t for t in list_tables() if not t.startswith("sqlite_")]
            if tbls:
                counts = []
                for t in tbls:
                    cols, rows = execute_readonly(f"SELECT COUNT(*) AS count FROM {t};")
                    cnt = int(rows[0][0]) if rows and rows[0] else 0
                    counts.append({"table": t, "rows": cnt})
                if counts:
                    st.caption("Row counts by table:")
                    df_counts = pd.DataFrame(counts).set_index("table")
                    st.bar_chart(df_counts)
        except Exception:
            pass

    if generate_clicked and question:
        prompt = (
            "Return only a valid SQL SELECT statement ending with a semicolon; "
            "avoid DDL/DML; include a LIMIT 50 if not specified.\n"
            f"Schema:\n{get_schema_overview()}\n"
            f"Question: {question}"
        )
        if provider == LLMProvider.OPENAI:
            if not openai_key:
                st.error("Please provide OPENAI_API_KEY.")
                return
            proposed_sql = generate_sql_openai(prompt, api_key=openai_key)
        else:
            proposed_sql = generate_sql_bedrock(prompt)

        if not is_select_only(proposed_sql) or contains_forbidden(proposed_sql):
            st.error("Generated SQL failed safety checks.")
            return

        proposed_sql = ensure_limit(proposed_sql, default_limit=50)
        st.session_state.proposed_sql = proposed_sql
        st.success("SQL generated and saved. Review below and click Run SQL.")

    # Show current SQL (if any) and a persistent Run button
    if st.session_state.proposed_sql:
        st.write("Current SQL:")
        st.code(st.session_state.proposed_sql, language="sql")

    if st.button("Run SQL", disabled=not bool(st.session_state.proposed_sql)):
        try:
            start = time.time()
            columns, rows = execute_readonly(st.session_state.proposed_sql)
            elapsed = time.time() - start
            df = pd.DataFrame(rows, columns=columns)
            st.caption(f"Query completed in {elapsed:.2f}s; {len(df)} rows")
            st.dataframe(df, use_container_width=True)
            # Quick charts: try to find numeric columns for bar, date-like for line
            if not df.empty:
                num_cols = df.select_dtypes(include=["number"]).columns.tolist()
                if len(num_cols) >= 1:
                    st.bar_chart(df[num_cols])
                date_cols = [c for c in df.columns if c.lower().endswith("date") or c.lower() in ("date", "event_date")]
                if date_cols:
                    dcol = date_cols[0]
                    try:
                        dff = df.copy()
                        dff[dcol] = pd.to_datetime(dff[dcol], errors="coerce")
                        dff = dff.set_index(dcol).sort_index()
                        st.line_chart(dff.select_dtypes(include=["number"]))
                    except Exception:
                        pass
            st.download_button("Download CSV", df.to_csv(index=False), "results.csv", "text/csv")
        except Exception as e:
            st.error(str(e))


if __name__ == "__main__":
    main()


