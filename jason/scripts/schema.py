import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "GamerSoups_final_project.sqlite"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pokemon (
        pokemon_id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        height INTEGER,
        weight INTEGER,
        base_experience INTEGER
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pokemon_type (
        pokemon_id INTEGER NOT NULL,
        slot INTEGER NOT NULL,
        type_name TEXT NOT NULL,
        PRIMARY KEY (pokemon_id, slot),
        FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS stat_dim (
        stat_id INTEGER PRIMARY KEY,
        stat_name TEXT UNIQUE NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pokemon_stat (
        pokemon_id INTEGER NOT NULL,
        stat_id INTEGER NOT NULL,
        base_stat INTEGER NOT NULL,
        effort INTEGER NOT NULL,
        PRIMARY KEY (pokemon_id, stat_id),
        FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id),
        FOREIGN KEY (stat_id) REFERENCES stat_dim(stat_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS fruits (
        fruit_id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS fruit_family (
        family_id INTEGER PRIMARY KEY,
        family_name TEXT UNIQUE NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS fruityvice_nutrition (
        fruit_id INTEGER PRIMARY KEY,
        family_id INTEGER,
        genus TEXT,
        fruit_order TEXT,
        carbohydrates REAL,
        protein REAL,
        fat REAL,
        calories REAL,
        sugar REAL,
        FOREIGN KEY (fruit_id) REFERENCES fruits(fruit_id),
        FOREIGN KEY (family_id) REFERENCES fruit_family(family_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS wiki_fruit_info (
        fruit_id INTEGER PRIMARY KEY,
        source_page TEXT NOT NULL,
        note TEXT,
        FOREIGN KEY (fruit_id) REFERENCES fruits(fruit_id)
    );
    """)

    conn.commit()
    conn.close()
    print(f"Created/updated schema at {DB_PATH}")

if __name__ == "__main__":
    main()
