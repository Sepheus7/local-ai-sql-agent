import streamlit as st
import re
import pandas as pd
from app.database import execute_postgresql_query, create_table_from_dataframe, get_table_schema
from app.agent import query_agent

# Streamlit app
def main():
    # Initialize session state for history and schemas
    if "history" not in st.session_state:
        st.session_state.history = []
    if "schemas" not in st.session_state:
        st.session_state.schemas = []

    # Streamlit interface
    st.title("Database Query Assistant")
    st.write("Ask natural language questions, and the assistant will generate SQL queries and fetch results from the database.")

    # File upload
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        # Process the uploaded file
        df = pd.read_csv(uploaded_file)
        st.write("Uploaded Data:")
        st.write(df)

        # Create table and insert data into the database
        table_name = uploaded_file.name.split('.')[0]
        create_table_from_dataframe(df, table_name)
        st.success(f"Data from {uploaded_file.name} has been ingested into the database as table '{table_name}'.")

        # Get the table schema and add to session state
        table_schema = get_table_schema(df, table_name)
        st.session_state.schemas.append(table_schema)

    # Select table to query
    table_options = ["employees"] + [schema.split()[5] for schema in st.session_state.schemas]
    selected_table = st.selectbox("Select a table to query:", table_options)

    # Input for user query
    query_to_agent = st.text_input("Enter your question about the database:")

    if st.button("Generate SQL and Query"):
        if query_to_agent:
            # Query the agent
            st.info("Sending query to the assistant...")
            response_content, sql_query, explanation = query_agent(query_to_agent, st.session_state.history, st.session_state.schemas)

            if sql_query:
                # Display the generated SQL
                st.code(sql_query, language="sql")

                # Execute the SQL query
                st.info("Executing SQL query...")
                result = execute_postgresql_query(sql_query)

                # Display results
                st.write("Query Results:")
                st.table(result)

                # Display plain text explanation
                st.write("Explanation:")
                st.write(explanation)

if __name__ == "__main__":
    main()