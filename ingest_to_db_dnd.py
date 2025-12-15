"""
ingest_to_db.py

Ingests ONLY spell name, school, and level into ONE SQLite database.

Tables:
- spells
- schools
- levels

Per run:
- Inserts <= 25 NEW spells
- No duplicate data
"""

from __future__ import annotations

import sqlite3
from typing import Dict, Optional

import requests

from dnd5e_api import list_spells, fetch_spell_detail_trimmed

DB_PATH = "GamerSoups_final_project.sqlite"
MAX_NEW_PER_RUN = 25


# ----------------------------
# DB helpers
# ----------------------------
def connect_db(path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level_num INTEGER UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS spells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_index TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            school_id INTEGER NOT NULL,
            level_id INTEGER NOT NULL,
            FOREIGN KEY (school_id) REFERENCES schools(id),
            FOREIGN KEY (level_id) REFERENCES levels(id)
        );

        CREATE INDEX IF NOT EXISTS idx_spells_school ON spells(school_id);
        CREATE INDEX IF NOT EXISTS idx_spells_level ON spells(level_id);
        """
    )
    conn.commit()


def get_or_create_id(conn: sqlite3.Connection, table: str, column: str, value: int | str) -> int:
    cur = conn.cursor()
    cur.execute(f"INSERT OR IGNORE INTO {table} ({column}) VALUES (?)", (value,))
    cur.execute(f"SELECT id FROM {table} WHERE {column} = ?", (value,))
    return int(cur.fetchone()[0])


def spell_exists(conn: sqlite3.Connection, api_index: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM spells WHERE api_index = ? LIMIT 1",
        (api_index,),
    ).fetchone() is not None


def insert_spell(conn: sqlite3.Connection, spell: Dict) -> bool:
    api_index = spell.get("api_index")
    name = spell.get("name")
    level = spell.get("level")
    school = spell.get("school_name")

    if not api_index or not name or level is None or not school:
        return False

    if spell_exists(conn, api_index):
        return False

    school_id = get_or_create_id(conn, "schools", "name", school)
    level_id = get_or_create_id(conn, "levels", "level_num", int(level))

    conn.execute(
        """
        INSERT INTO spells (api_index, name, school_id, level_id)
        VALUES (?, ?, ?, ?)
        """,
        (api_index, name, school_id, level_id),
    )
    return True


def ingest_spells_capped(conn: sqlite3.Connection, session: requests.Session, max_new: int) -> int:
    inserted = 0
    for item in list_spells(session):
        if inserted >= max_new:
            break

        api_index = item.get("index")
        url = item.get("url")
        if not api_index or not url:
            continue

        if spell_exists(conn, api_index):
            continue

        detail = fetch_spell_detail_trimmed(session, url)
        if insert_spell(conn, detail):
            inserted += 1

    return inserted


def main() -> None:
    conn = connect_db(DB_PATH)
    try:
        init_schema(conn)
        with requests.Session() as session:
            new_spells = ingest_spells_capped(conn, session, MAX_NEW_PER_RUN)
            conn.commit()

        total = conn.execute("SELECT COUNT(*) FROM spells").fetchone()[0]
        print(f"Inserted NEW spells this run: {new_spells} (max {MAX_NEW_PER_RUN})")
        print(f"Total spells currently in DB: {total}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
