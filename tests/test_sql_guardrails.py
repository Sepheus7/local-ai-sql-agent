from src.agent.sql_guardrails import is_select_only, contains_forbidden, ensure_limit, extract_first_select


def test_is_select_only():
    assert is_select_only("SELECT * FROM t;")
    assert not is_select_only("UPDATE t SET a=1;")


def test_contains_forbidden():
    assert contains_forbidden("DROP TABLE t;")
    assert not contains_forbidden("SELECT * FROM t;")


def test_ensure_limit():
    assert ensure_limit("SELECT * FROM t;", 5).strip().lower().endswith("limit 5;")
    assert "limit 10" in ensure_limit("SELECT * FROM t LIMIT 10;", 5).lower()


def test_extract_first_select():
    txt = """Here is your query:
```sql
SELECT a FROM t;
```
"""
    assert extract_first_select(txt).strip().lower().startswith("select")


