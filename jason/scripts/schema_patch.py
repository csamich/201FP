import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "GamerSoups_final_project.sqlite"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS scraped_fruit_rows (
        row_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_page TEXT NOT NULL,
        item_name TEXT NOT NULL,
        item_value TEXT,
        UNIQUE(source_page, item_name, item_value)
    );
    """)

    conn.commit()
    conn.close()
    print("schema patch applied")

if __name__ == "__main__":
    main()
