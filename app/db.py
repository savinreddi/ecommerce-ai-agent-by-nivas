import sqlite3
import pandas as pd
import os

# Define the path to your SQLite database
DB_PATH = os.path.join(os.path.dirname(__file__), "../data.db")  # Adjust path if needed

def execute_sql_query(query: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        return f"SQL Execution Error: {e}"
