import os
import psycopg2
import pandas as pd
from psycopg2 import sql

# Determine the database host
DB_HOST = "localhost"
if os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true":
    DB_HOST = "host.docker.internal"

# Database connection
def get_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="mysecretpassword",
        host=DB_HOST,
        port=5432
    )

def execute_postgresql_query(sql_query):
    """Execute a given SQL query on the PostgreSQL database and return results."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        return str(e)

def map_dtype_to_sql(dtype):
    """Map pandas dtype to SQL type."""
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "TIMESTAMP"
    else:
        return "TEXT"

def sanitize_column_name(name):
    """Sanitize column name to be a valid SQL identifier."""
    return name.replace(" ", "_").replace(":", "_").replace("-", "_")

def create_table_from_dataframe(df, table_name):
    """Create a table in the database from a DataFrame and insert data."""
    conn = get_connection()
    cursor = conn.cursor()

    # Sanitize column names
    df.columns = [sanitize_column_name(col) for col in df.columns]

    # Create table
    columns = ", ".join([f"{col} {map_dtype_to_sql(df[col].dtype)}" for col in df.columns])
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
    cursor.execute(create_table_query)
    conn.commit()

    # Insert data
    for _, row in df.iterrows():
        insert_query = sql.SQL("INSERT INTO {} VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(", ").join(sql.Placeholder() * len(row))
        )
        cursor.execute(insert_query, tuple(row))
    conn.commit()
    conn.close()

def get_table_schema(df, table_name):
    """Generate the SQL schema for a given DataFrame."""
    columns = ", ".join([f"{col} {map_dtype_to_sql(df[col].dtype)}" for col in df.columns])
    return f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"