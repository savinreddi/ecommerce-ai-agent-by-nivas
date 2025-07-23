import sqlite3

def check_database():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Get all tables
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    print("Tables:", tables)
    
    # Check total_sales_metrics table structure
    try:
        columns = cursor.execute("PRAGMA table_info(total_sales_metrics);").fetchall()
        print("total_sales_metrics columns:", columns)
    except sqlite3.OperationalError as e:
        print("Error accessing total_sales_metrics:", e)
    
    # Try to get a sample query
    try:
        result = cursor.execute("SELECT SUM(total_sales) FROM total_sales_metrics;").fetchone()
        print("Total sales sum:", result[0])
    except sqlite3.OperationalError as e:
        print("Error in sum query:", e)
    
    conn.close()

if __name__ == "__main__":
    check_database()
