import os
import psycopg2
from psycopg2 import sql
from faker import Faker

# Determine the database host
DB_HOST = "localhost"
if os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true":
    DB_HOST = "host.docker.internal"

# Database connection
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="mysecretpassword",
    host=DB_HOST,
    port=5432
)
cursor = conn.cursor()

# Create a synthetic table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        age INTEGER,
        department VARCHAR(100),
        salary FLOAT,
        join_date DATE
    )
""")
conn.commit()

# Generate synthetic data
fake = Faker()
for _ in range(1000):
    cursor.execute(
        "INSERT INTO employees (name, age, department, salary, join_date) VALUES (%s, %s, %s, %s, %s)",
        (fake.name(), fake.random_int(20, 60), fake.job(), fake.random_int(30000, 150000), fake.date_this_decade())
    )
conn.commit()

print("Synthetic data populated!")
conn.close()