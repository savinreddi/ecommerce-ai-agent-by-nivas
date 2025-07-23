import os
import sqlite3
import pandas as pd

# Paths
DATA_DIR = "data"
DB_PATH = "data.db"  # Already present

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect(DB_PATH)

# Loop through all CSV files in the data folder
for filename in os.listdir(DATA_DIR):
    if filename.endswith(".csv"):
        file_path = os.path.join(DATA_DIR, filename)
        table_name = filename.replace(".csv", "")

        df = pd.read_csv(file_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        print(f"✅ Loaded {filename} as table '{table_name}'")

conn.close()
print("🎉 All CSVs loaded into data.db")
