import pytest
from app.database import execute_postgresql_query, create_table_from_dataframe, get_connection, get_table_schema
import pandas as pd

def test_execute_postgresql_query(mocker):
    # Mock psycopg2 connection and cursor
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchall.return_value = [(28,)]
    mock_conn = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mocker.patch('psycopg2.connect', return_value=mock_conn)

    # Test SQL execution
    sql_query = "SELECT age FROM employees WHERE name = 'John Doe';"
    result = execute_postgresql_query(sql_query)

    assert result == [(28,)]
    mock_cursor.execute.assert_called_with(sql_query)
    mock_conn.close.assert_called_once()

def test_create_table_from_dataframe(mocker):
    # Mock psycopg2 connection and cursor
    mock_cursor = mocker.MagicMock()
    mock_conn = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mocker.patch('psycopg2.connect', return_value=mock_conn)

    # Create DataFrame
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'department': ['HR', 'Engineering', 'Sales'],
        'salary': [50000, 60000, 70000],
        'join_date': pd.to_datetime(['2020-01-01', '2019-01-01', '2018-01-01'])
    })
    table_name = "test_employees"

    # Test table creation
    create_table_from_dataframe(df, table_name)
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called_once()

def test_get_table_schema():
    # Create DataFrame
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'department': ['HR', 'Engineering', 'Sales'],
        'salary': [50000, 60000, 70000],
        'join_date': pd.to_datetime(['2020-01-01', '2019-01-01', '2018-01-01'])
    })
    table_name = "test_employees"

    # Test schema generation
    schema = get_table_schema(df, table_name)
    assert "CREATE TABLE IF NOT EXISTS" in schema
    assert table_name in schema