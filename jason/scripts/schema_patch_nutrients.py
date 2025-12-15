import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "GamerSoups_final_project.sqlite"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS nutrient_dim (
        nutrient_id INTEGER PRIMARY KEY,
        nutrient_name TEXT UNIQUE NOT NULL
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS fruit_nutrient_long (
        fruit_id INTEGER NOT NULL,
        nutrient_id INTEGER NOT NULL,
        nutrient_value REAL,
        PRIMARY KEY (fruit_id, nutrient_id),
        FOREIGN KEY (fruit_id) REFERENCES fruits(fruit_id),
        FOREIGN KEY (nutrient_id) REFERENCES nutrient_dim(nutrient_id)
    );
    """)

    conn.commit()
    conn.close()
    print("nutrient tables created")
    
if __name__ == "__main__":
    main()
