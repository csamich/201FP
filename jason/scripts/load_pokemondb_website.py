import sqlite3
from pathlib import Path
import requests
from bs4 import BeautifulSoup

DB_PATH = Path(__file__).resolve().parents[1] / "GamerSoups_final_project.sqlite"
URL = "https://pokemondb.net/pokedex/all"
HEADERS = {"User-Agent": "Mozilla/5.0"}
BATCH = 25

def get_meta(conn, key, default):
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    if row is None:
        conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)", (key, str(default)))
        conn.commit()
        return str(default)
    return row[0]

def set_meta(conn, key, value):
    conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)", (key, str(value)))
    conn.commit()

def parse_rows(html: str):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table#pokedex")
    if table is None:
        raise RuntimeError("Could not find table#pokedex")
    out = []
    for tr in table.select("tbody tr"):
        tds = tr.find_all("td")
        if len(tds) < 3:
            continue
        dex_num = int(tds[0].get_text(strip=True).lstrip("#"))
        name = tds[1].get_text(strip=True)
        types = [a.get_text(strip=True).lower() for a in tds[2].select("a")]
        out.append((dex_num, name, types))
    return out

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    offset = int(get_meta(conn, "web_offset", 0))

    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    rows = parse_rows(r.text)

    inserted = 0
    i = offset
    while inserted < BATCH and i < len(rows):
        dex_num, name, types = rows[i]
        i += 1

        cur = conn.execute(
            "INSERT OR IGNORE INTO web_pokemon(dex_num, name) VALUES (?, ?)",
            (dex_num, name)
        )
        if cur.rowcount == 0:
            continue

        inserted += 1

        for slot, tname in enumerate(types, start=1):
            conn.execute("INSERT OR IGNORE INTO web_type_dim(type_name) VALUES (?)", (tname,))
            type_id = conn.execute(
                "SELECT type_id FROM web_type_dim WHERE type_name = ?",
                (tname,)
            ).fetchone()[0]
            conn.execute(
                "INSERT OR IGNORE INTO web_pokemon_type(dex_num, slot, type_id) VALUES (?, ?, ?)",
                (dex_num, slot, type_id)
            )

        conn.commit()

    set_meta(conn, "web_offset", i)
    conn.close()
    print(f"Inserted {inserted} web_pokemon rows. Next offset = {i} / {len(rows)}.")

if __name__ == "__main__":
    main()
