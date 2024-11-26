import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from app.database import create_table_from_dataframe, get_table_schema
from app.agent import query_agent

class TestStreamlitApp(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'department': ['HR', 'Engineering', 'Sales'],
            'salary': [50000, 60000, 70000],
            'join_date': pd.to_datetime(['2020-01-01', '2019-01-01', '2018-01-01'])
        })
        self.table_name = "test_employees"
        self.history = []

    @patch('app.database.get_connection')
    def test_create_table_from_dataframe(self, mock_get_connection):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        create_table_from_dataframe(self.df, self.table_name)

        # Add assertions to verify the table creation
        expected_schema = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (id INTEGER, name TEXT, age INTEGER, department TEXT, salary INTEGER, join_date TIMESTAMP);"""
        schema = get_table_schema(self.df, self.table_name)
        self.assertEqual(schema.strip(), expected_schema.strip())

        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
        mock_conn.close.assert_called_once()

    @patch('app.database.get_connection')
    def test_query_agent(self, mock_get_connection):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn

        query = "What is the average salary of employees?"
        response_content, sql_query = query_agent(query, self.history, [self.table_name])
        self.assertIn("SELECT", sql_query)
        self.assertIn("salary", sql_query)

if __name__ == "__main__":
    unittest.main()