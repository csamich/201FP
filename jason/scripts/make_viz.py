import json
import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "GamerSoups_final_project.sqlite"
OUT_DIR = ROOT / "jason" / "outputs"
VIZ_DIR = ROOT / "jason" / "viz"

def ensure_dirs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    VIZ_DIR.mkdir(parents=True, exist_ok=True)

def bar_avg_stats_by_type():
    data = json.loads((OUT_DIR / "pokemon_avg_total_stats_by_type.json").read_text(encoding="utf-8"))
    types = [d["type"] for d in data]
    avgs = [d["avg_total_stats"] for d in data]

    plt.figure()
    plt.bar(types, avgs)
    plt.title("Average Total Base Stats by Primary Type (PokeAPI)")
    plt.xlabel("Primary Type")
    plt.ylabel("Avg Total Base Stats")
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "pokemon_avg_stats_by_type.png", dpi=200)
    plt.close()

def scatter_weight_vs_total_stats():
    data = json.loads((OUT_DIR / "pokemon_weight_vs_total_stats.json").read_text(encoding="utf-8"))
    x = [d["weight"] for d in data if d["weight"] is not None]
    y = [d["total_stats"] for d in data if d["weight"] is not None]

    plt.figure()
    plt.scatter(x, y, s=12)
    plt.title("Weight vs Total Base Stats (PokeAPI)")
    plt.xlabel("Weight")
    plt.ylabel("Total Base Stats")
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "pokemon_weight_vs_total_stats.png", dpi=200)
    plt.close()

def bar_web_primary_type_counts():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT td.type_name, COUNT(*) AS n
        FROM web_pokemon_type wpt
        JOIN web_type_dim td ON td.type_id = wpt.type_id
        WHERE wpt.slot = 1
        GROUP BY td.type_name
        ORDER BY n DESC, td.type_name;
    """).fetchall()
    conn.close()

    types = [t for (t, _) in rows]
    counts = [n for (_, n) in rows]

    plt.figure()
    plt.bar(types, counts)
    plt.title("Website (PokemonDB) Primary Type Counts")
    plt.xlabel("Primary Type")
    plt.ylabel("Count")
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    plt.savefig(VIZ_DIR / "web_primary_type_counts.png", dpi=200)
    plt.close()

def main():
    ensure_dirs()
    bar_avg_stats_by_type()
    scatter_weight_vs_total_stats()
    bar_web_primary_type_counts()
    print("Saved plots to viz/")

if __name__ == "__main__":
    main()
