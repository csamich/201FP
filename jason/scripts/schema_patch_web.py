import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "GamerSoups_final_project.sqlite"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS web_pokemon (
        dex_num INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS web_type_dim (
        type_id INTEGER PRIMARY KEY,
        type_name TEXT UNIQUE NOT NULL
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS web_pokemon_type (
        dex_num INTEGER NOT NULL,
        slot INTEGER NOT NULL,
        type_id INTEGER NOT NULL,
        PRIMARY KEY (dex_num, slot),
        FOREIGN KEY (dex_num) REFERENCES web_pokemon(dex_num),
        FOREIGN KEY (type_id) REFERENCES web_type_dim(type_id)
    );
    """)

    conn.commit()
    conn.close()
    print("web tables created")

if __name__ == "__main__":
    main()
