import csv
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "GamerSoups_final_project.sqlite"
OUT_DIR = Path(__file__).resolve().parents[1] / "outputs"

def ensure_outdir():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

def pokemon_avg_total_stats_by_type(conn):
    rows = conn.execute("""
        SELECT pt.type_name,
               AVG(s.total_stats) AS avg_total_stats,
               COUNT(*) AS pokemon_count
        FROM (
            SELECT ps.pokemon_id, SUM(ps.base_stat) AS total_stats
            FROM pokemon_stat ps
            GROUP BY ps.pokemon_id
        ) s
        JOIN pokemon_type pt ON pt.pokemon_id = s.pokemon_id AND pt.slot = 1
        GROUP BY pt.type_name
        ORDER BY avg_total_stats DESC;
    """).fetchall()

    out = [{"type": t, "avg_total_stats": float(avg), "count": int(c)} for (t, avg, c) in rows]
    return out

def pokemon_weight_vs_total_stats(conn):
    rows = conn.execute("""
        SELECT p.pokemon_id, p.name, p.weight,
               SUM(ps.base_stat) AS total_stats
        FROM pokemon p
        JOIN pokemon_stat ps ON ps.pokemon_id = p.pokemon_id
        GROUP BY p.pokemon_id
        ORDER BY p.pokemon_id;
    """).fetchall()

    out = [{"pokemon_id": int(pid), "name": name, "weight": w, "total_stats": int(ts)}
           for (pid, name, w, ts) in rows]
    return out

def fruit_avg_nutrients_by_family(conn):
    rows = conn.execute("""
        SELECT ff.family_name, nd.nutrient_name,
               AVG(fnl.nutrient_value) AS avg_value,
               COUNT(*) AS n_rows
        FROM fruit_nutrient_long fnl
        JOIN nutrient_dim nd ON nd.nutrient_id = fnl.nutrient_id
        JOIN fruityvice_nutrition fn ON fn.fruit_id = fnl.fruit_id
        JOIN fruit_family ff ON ff.family_id = fn.family_id
        GROUP BY ff.family_name, nd.nutrient_name
        ORDER BY ff.family_name, nd.nutrient_name;
    """).fetchall()

    out = [{"family": fam, "nutrient": nut, "avg_value": (None if avg is None else float(avg)), "rows": int(n)}
           for (fam, nut, avg, n) in rows]
    return out

def fruit_top_sugar(conn, topn=10):
    rows = conn.execute("""
        SELECT f.name, ff.family_name, fnl.nutrient_value AS sugar
        FROM fruit_nutrient_long fnl
        JOIN nutrient_dim nd ON nd.nutrient_id = fnl.nutrient_id
        JOIN fruits f ON f.fruit_id = fnl.fruit_id
        JOIN fruityvice_nutrition fn ON fn.fruit_id = f.fruit_id
        JOIN fruit_family ff ON ff.family_id = fn.family_id
        WHERE nd.nutrient_name = 'sugar'
        ORDER BY sugar DESC
        LIMIT ?;
    """, (topn,)).fetchall()

    out = [{"fruit": name, "family": fam, "sugar": (None if sugar is None else float(sugar))}
           for (name, fam, sugar) in rows]
    return out

def website_type_counts(conn):
    rows = conn.execute("""
        SELECT td.type_name, COUNT(*) AS n
        FROM web_pokemon_type wpt
        JOIN web_type_dim td ON td.type_id = wpt.type_id
        WHERE wpt.slot = 1
        GROUP BY td.type_name
        ORDER BY n DESC, td.type_name;
    """).fetchall()
    return [{"type": t, "count": int(n)} for (t, n) in rows]

def main():
    ensure_outdir()
    conn = sqlite3.connect(DB_PATH)

    poke_type_avgs = pokemon_avg_total_stats_by_type(conn)
    poke_scatter = pokemon_weight_vs_total_stats(conn)
    fruit_family_avgs = fruit_avg_nutrients_by_family(conn)
    fruit_top10_sugar = fruit_top_sugar(conn, 10)
    web_primary_type_counts = website_type_counts(conn)

    (OUT_DIR / "pokemon_avg_total_stats_by_type.json").write_text(
        json.dumps(poke_type_avgs, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "pokemon_weight_vs_total_stats.json").write_text(
        json.dumps(poke_scatter[:200], indent=2), encoding="utf-8"
    )
    (OUT_DIR / "fruit_avg_nutrients_by_family.json").write_text(
        json.dumps(fruit_family_avgs, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "fruit_top10_sugar.json").write_text(
        json.dumps(fruit_top10_sugar, indent=2), encoding="utf-8"
    )

    with open(OUT_DIR / "web_primary_type_counts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["type", "count"])
        for row in web_primary_type_counts:
            w.writerow([row["type"], row["count"]])

    conn.close()
    print("Wrote outputs to outputs/")

if __name__ == "__main__":
    main()
