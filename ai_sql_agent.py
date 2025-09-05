import sqlite3
from openai import OpenAI
import streamlit as st
import re

def setup_database():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')
    conn.commit()
    conn.close()

def add_user(name, age):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
    conn.commit()
    conn.close()

def execute_sql_query(sql_query):
    """Execute a given SQL query on the SQLite database and return results."""
    try:
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        return str(e)

# Agent interaction function
def query_agent(query_to_agent):
    """Send the user query to the LLM agent and return the generated SQL query and answer."""
    # OpenAI agent setup
    url = "http://localhost:1234/v1"
    client = OpenAI(base_url=url, api_key="lm-studio")

    agent_instruction = """You are an expert database querying assistant that can create simple and complex SQL queries to get 
    the answers to questions about employees that you are asked. You first need to get the schemas for the table in the database to then query the 
    database tables using a SQL statement then respond to the user with the answer to their question and
    the SQL statement used to answer the question. Use the getschema tool first to understand the schema
    of the table then create a SQL query to answer the user's question.
    Here is an example to query the table <example>SELECT * FROM employees LIMIT 10;</example> Do not use 
    quotes for the table name. Your final answer should be in plain English."""

    # Prepare agent interaction
    history = [
        {"role": "system", "content": agent_instruction},
        {"role": "user", "content": query_to_agent},
    ]

    completion = client.chat.completions.create(
        model="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
        messages=history,
        temperature=0.7,
        stream=False,
    )

    # Extract SQL query from assistant's response
    response_content = completion.choices[0].message.content if completion.choices else ""
    
    if not isinstance(response_content, str):
        raise ValueError("Expected response_content to be a string")

    sql_query = re.search(r"SELECT.*?;", response_content, re.DOTALL)
    sql_query = sql_query.group(0) if sql_query else None

    return response_content, sql_query

# Streamlit app
def main():
    # Streamlit interface
    st.title("Database Query Assistant")
    st.write("Ask natural language questions, and the assistant will generate SQL queries and fetch results from the database.")

    # Setup and populate database
    setup_database()
    add_user('John Doe', 28)
    add_user('Jane Smith', 32)

    # Input for user query
    query_to_agent = st.text_input("Enter your question about the database:")

    if st.button("Generate SQL and Query"):
        if query_to_agent:
            # Query the agent
            st.info("Sending query to the assistant...")
            response_content, sql_query = query_agent(query_to_agent)

            if sql_query:
                # Display the generated SQL
                st.code(sql_query, language="sql")

                # Execute the SQL query
                st.info("Executing SQL query...")
                result = execute_sql_query(sql_query)

                # Display results
                st.write("Query Results:")
                st.table(result)
            else:
                st.error("Failed to generate SQL query from the assistant.")
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()