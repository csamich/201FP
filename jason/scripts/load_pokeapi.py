import sqlite3
from pathlib import Path
import requests

DB_PATH = Path(__file__).resolve().parents[1] / "GamerSoups_final_project.sqlite"
BASE = "https://pokeapi.co/api/v2/pokemon/"
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

def fetch_pokemon(pid: int) -> dict:
    r = requests.get(f"{BASE}{pid}/", timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    next_id = int(get_meta(conn, "poke_next_id", "1"))
    inserted = 0
    attempted = 0

    while inserted < BATCH:
        pid = next_id
        next_id += 1
        attempted += 1

        try:
            data = fetch_pokemon(pid)
        except requests.HTTPError:
            break

        cur = conn.execute(
            "INSERT OR IGNORE INTO pokemon(pokemon_id, name, height, weight, base_experience) VALUES (?, ?, ?, ?, ?)",
            (pid, data.get("name"), data.get("height"), data.get("weight"), data.get("base_experience"))
        )
        if cur.rowcount == 0:
            continue

        inserted += 1

        for t in data.get("types", []):
            conn.execute(
                "INSERT OR IGNORE INTO pokemon_type(pokemon_id, slot, type_name) VALUES (?, ?, ?)",
                (pid, int(t["slot"]), t["type"]["name"])
            )

        for s in data.get("stats", []):
            stat_name = s["stat"]["name"]
            base_stat = int(s["base_stat"])
            effort = int(s["effort"])

            conn.execute("INSERT OR IGNORE INTO stat_dim(stat_name) VALUES (?)", (stat_name,))
            stat_id = conn.execute(
                "SELECT stat_id FROM stat_dim WHERE stat_name = ?",
                (stat_name,)
            ).fetchone()[0]

            conn.execute(
                "INSERT OR IGNORE INTO pokemon_stat(pokemon_id, stat_id, base_stat, effort) VALUES (?, ?, ?, ?)",
                (pid, stat_id, base_stat, effort)
            )

        conn.commit()

    set_meta(conn, "poke_next_id", str(next_id))
    conn.close()
    print(f"Inserted {inserted} new pokemon. Next start id = {next_id}. Attempted ids = {attempted}.")

if __name__ == "__main__":
    main()
