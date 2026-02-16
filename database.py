import sqlite3
import pandas as pd

DB_NAME = "ipl.db"
TABLE_NAME = "ipl"


def load_csv_to_db(csv_path="ipl.csv"):
    print("📥 Loading IPL CSV into database...")
    df = pd.read_csv(csv_path)
    conn = sqlite3.connect(DB_NAME)
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
    conn.close()
    print("✅ Database ready.")


def get_schema():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    schema = cursor.fetchall()
    conn.close()
    return schema


def execute_query(query: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result
