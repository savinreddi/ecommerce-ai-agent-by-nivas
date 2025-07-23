import sqlite3

DB_PATH = "db/ecommerce.db"

def execute_sql(sql: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()

        result = [dict(zip(columns, row)) for row in rows]
        return result if result else "No data found."
    except Exception as e:
        return f"SQL Execution Error: {e}"
