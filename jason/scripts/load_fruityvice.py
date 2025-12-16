import sqlite3
from pathlib import Path
import requests

DB_PATH = Path(__file__).resolve().parents[2] / "GamerSoups_final_project.sqlite"
URL = "https://www.fruityvice.com/api/fruit/all"
BATCH = 25

def get_meta(conn: sqlite3.Connection, key: str, default: str) -> str:
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    if row is None:
        conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)", (key, default))
        conn.commit()
        return default
    return row[0]

def set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)", (key, value))
    conn.commit()

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    offset = int(get_meta(conn, "fruit_offset", "0"))

    r = requests.get(URL, timeout=30)
    r.raise_for_status()
    all_fruits = r.json()

    inserted = 0
    idx = offset

    while inserted < BATCH and idx < len(all_fruits):
        f = all_fruits[idx]
        idx += 1

        fruit_id = int(f["id"])
        name = f["name"]
        family = f.get("family")
        genus = f.get("genus")
        order = f.get("order")
        nut = f.get("nutritions", {})

        cur = conn.execute(
            "INSERT OR IGNORE INTO fruits(fruit_id, name) VALUES (?, ?)",
            (fruit_id, name)
        )
        if cur.rowcount == 0:
            continue

        inserted += 1

        family_id = None
        if family:
            conn.execute("INSERT OR IGNORE INTO fruit_family(family_name) VALUES (?)", (family,))
            family_id = conn.execute(
                "SELECT family_id FROM fruit_family WHERE family_name = ?",
                (family,)
            ).fetchone()[0]

        conn.execute("""
            INSERT OR REPLACE INTO fruityvice_nutrition(
                fruit_id, family_id, genus, fruit_order,
                carbohydrates, protein, fat, calories, sugar
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fruit_id, family_id, genus, order,
            nut.get("carbohydrates"), nut.get("protein"), nut.get("fat"),
            nut.get("calories"), nut.get("sugar")
        ))

        conn.commit()

    set_meta(conn, "fruit_offset", str(idx))
    conn.close()
    print(f"Inserted {inserted} new fruits. Next offset = {idx} / {len(all_fruits)}.")

if __name__ == "__main__":
    main()
