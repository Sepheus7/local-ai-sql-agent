import unittest
from app.agent import query_agent

class TestAgent(unittest.TestCase):
    def setUp(self):
        self.history = []
        self.default_schema = """CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            age INTEGER,
            department VARCHAR(100),
            salary FLOAT,
            join_date DATE
        );"""

    def test_query_agent(self):
        query = "What is the average salary of employees?"
        response_content, sql_query = query_agent(query, self.history, [self.default_schema])
        self.assertIn("SELECT", sql_query)
        self.assertIn("salary", sql_query)

if __name__ == "__main__":
    unittest.main()