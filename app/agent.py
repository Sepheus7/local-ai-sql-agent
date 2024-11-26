from openai import OpenAI
import os
import re

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "lm-studio")
LLM_HOST = "localhost"
if os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true":
    LLM_HOST = "host.docker.internal"

default_table_schema = """CREATE TABLE IF NOT EXISTS employees (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        age INTEGER,
        department VARCHAR(100),
        salary FLOAT,
        join_date DATE
    );"""

# Agent interaction function
def query_agent(query_to_agent, history, additional_schemas=[]):
    """Send the user query to the LLM agent and return the generated SQL query and answer."""
    # OpenAI agent setup
    url = f"http://{LLM_HOST}:1234/v1"
    client = OpenAI(base_url=url, api_key=OPENAI_API_KEY)

    # Combine default schema with additional schemas
    all_schemas = [default_table_schema] + additional_schemas
    combined_schemas = "\n".join(all_schemas)

    agent_instruction = f"""You are an expert database querying assistant that can create simple and complex SQL queries to get 
    the answers to questions about the database that you are asked. The database schema is as follows:
    {combined_schemas}
    After generating the SQL query to answer the question, provide a plain text explanation of the result for the user. 
    The explanation should summarize the result in simple terms. Example:
    "The result shows that John Doe is 28 years old and works in the Sales department."
    Use the getschema tool first to understand the schema of the table then create a SQL query to answer the user's question.
    Here is an example to query the table <example>SELECT * FROM employees LIMIT 10;</example> Do not use quotes for the table name."""

    # Prepare agent interaction
    history.append({"role": "system", "content": agent_instruction})
    history.append({"role": "user", "content": query_to_agent})

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

    explanation_match = re.search(r"The result shows.*", response_content, re.DOTALL)
    explanation = explanation_match.group(0) if explanation_match else "No explanation provided."

    history.append({"role": "system", "content": response_content})

    return response_content, sql_query, explanation