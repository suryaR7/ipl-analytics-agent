import pandas as pd
import sqlite3
DB_NAME = "ipl.db"
def load_csv_to_db():
    """
    Loads local ipl.csv into SQLite database.
    """
    conn = sqlite3.connect(DB_NAME)
    print("Loading IPL CSV into database...")
    df = pd.read_csv("ipl.csv", low_memory=False)
    df.to_sql("ipl", conn, if_exists="replace", index=False)
    conn.close()
    print("Database ready.")
def execute_query(query):
    """
    Executes only SELECT queries safely.
    """
    if not query.strip().lower().startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results
def get_schema():
    """
    Returns table schema for LLM context.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(ipl);")
    schema = cursor.fetchall()
    conn.close()
    return schema
