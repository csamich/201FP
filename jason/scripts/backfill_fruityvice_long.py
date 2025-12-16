import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "GamerSoups_final_project.sqlite"

NAMES = ["carbohydrates", "protein", "fat", "calories", "sugar"]

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    for n in NAMES:
        conn.execute("INSERT OR IGNORE INTO nutrient_dim(nutrient_name) VALUES (?)", (n,))
    conn.commit()

    nutrient_ids = {
        name: conn.execute("SELECT nutrient_id FROM nutrient_dim WHERE nutrient_name = ?", (name,)).fetchone()[0]
        for name in NAMES
    }

    rows = conn.execute("""
        SELECT fruit_id, carbohydrates, protein, fat, calories, sugar
        FROM fruityvice_nutrition
    """).fetchall()

    inserted = 0
    for fruit_id, carbs, protein, fat, calories, sugar in rows:
        values = {
            "carbohydrates": carbs,
            "protein": protein,
            "fat": fat,
            "calories": calories,
            "sugar": sugar
        }
        for name, val in values.items():
            cur = conn.execute("""
                INSERT OR IGNORE INTO fruit_nutrient_long(fruit_id, nutrient_id, nutrient_value)
                VALUES (?, ?, ?)
            """, (fruit_id, nutrient_ids[name], val))
            inserted += cur.rowcount

    conn.commit()
    conn.close()
    print(f"Inserted {inserted} fruit_nutrient_long rows.")

if __name__ == "__main__":
    main()
