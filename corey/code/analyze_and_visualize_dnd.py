import sqlite3
from typing import Dict, List, Tuple
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


DB_PATH = Path(__file__).resolve().parents[2] / "GamerSoups_final_project.sqlite"


def connect_db(path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def spells_by_school_counts(conn: sqlite3.Connection) -> List[Tuple[str, int]]:
    # JOIN spells -> schools
    return conn.execute(
        """
        SELECT sc.name AS school, COUNT(*) AS n
        FROM spells sp
        JOIN schools sc ON sc.id = sp.school_id
        GROUP BY sc.name
        ORDER BY n DESC
        """
    ).fetchall()


def grouped_counts_by_school_level_bucket(conn: sqlite3.Connection) -> List[Tuple[str, str, int]]:
    return conn.execute(
        """
        SELECT
            sc.name AS school,
            CASE
                WHEN lv.level_num BETWEEN 1 AND 5 THEN '1–5'
                WHEN lv.level_num BETWEEN 6 AND 9 THEN '6–9'
                ELSE 'Other'
            END AS bucket,
            COUNT(*) AS n
        FROM spells sp
        JOIN schools sc ON sc.id = sp.school_id
        JOIN levels lv ON lv.id = sp.level_id
        WHERE lv.level_num BETWEEN 1 AND 9
        GROUP BY sc.name, bucket
        HAVING bucket IN ('1–5', '6–9')
        ORDER BY sc.name, bucket
        """
    ).fetchall()


def write_text_summary(
    school_counts: List[Tuple[str, int]],
    bucket_counts: List[Tuple[str, str, int]],
    out_path: str = "spell_summary.txt",
) -> None:
    total = sum(n for _, n in school_counts) or 1

    # build easy lookup for bucket counts
    bucket_map: Dict[Tuple[str, str], int] = {}
    for school, bucket, n in bucket_counts:
        bucket_map[(school, bucket)] = n

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Spells Database Summary (2014 SRD)\n")
        f.write("=" * 40 + "\n\n")

        f.write("Spells by School (Top 10)\n")
        for school, n in school_counts[:10]:
            f.write(f"- {school}: {n} ({(n/total)*100:.2f}%)\n")

        f.write("\nCounts by School and Level Bucket\n")
        for school, _ in school_counts:
            low = bucket_map.get((school, "1–5"), 0)
            high = bucket_map.get((school, "6–9"), 0)
            f.write(f"- {school}: 1–5 = {low}, 6–9 = {high}, Difference = {abs(low-high)}\n")

    print(f"Wrote {out_path}")


def pie_spells_by_school(school_counts: List[Tuple[str, int]], out_path: str = "spells_by_school_pie.png") -> None:
    # Pastel look
    sns.set_theme(style="white", context="talk")
    plt.figure(figsize=(9, 7))

    total = sum(n for _, n in school_counts)
    top = school_counts[:10]
    other = total - sum(n for _, n in top)

    labels = [s for s, _ in top] + (["Other"] if other > 0 else [])
    values = [n for _, n in top] + ([other] if other > 0 else [])

    # pastel palette (matplotlib will cycle, we can supply explicit pastel colors via seaborn)
    colors = sns.color_palette("pastel", n_colors=len(values))

    plt.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
        pctdistance=0.75,
    )
    plt.title("Spells by School (Percent)", fontsize=16, fontweight="bold")
    plt.tight_layout()
    plt.savefig(out_path, dpi=220)
    plt.close()
    print(f"Saved {out_path}")


def pastel_grouped_bar(bucket_counts: List[Tuple[str, str, int]], out_path: str = "spells_level_buckets_by_school.png") -> None:
    schools: List[str] = []
    buckets: List[str] = []
    counts: List[int] = []
    for school, bucket, n in bucket_counts:
        schools.append(school)
        buckets.append(bucket)
        counts.append(n)

    sns.set_theme(style="whitegrid", context="talk")
    plt.figure(figsize=(14, 8))

    ax = sns.barplot(
        x=schools,
        y=counts,
        hue=buckets,
        palette=sns.color_palette("pastel", 2),
    )

    ax.set_title("Spells by School: Low-Level (1–5) vs High-Level (6–9)", fontsize=16, fontweight="bold")
    ax.set_xlabel("School")
    ax.set_ylabel("Number of spells")
    plt.xticks(rotation=35, ha="right")
    plt.legend(title="Spell Level Bucket")

    plt.tight_layout()
    plt.savefig(out_path, dpi=220)
    plt.close()
    print(f"Saved {out_path}")


def main() -> None:
    conn = connect_db(DB_PATH)
    try:
        school_counts = spells_by_school_counts(conn)
        bucket_counts = grouped_counts_by_school_level_bucket(conn)

        if not school_counts:
            print("No spells found. Run ingest_to_db.py multiple times first (until you have 100+ spells).")
            return

        write_text_summary(school_counts, bucket_counts, Path(__file__).resolve().parents[1] / "output" / "spell_summary.txt")
        pie_spells_by_school(school_counts, Path(__file__).resolve().parents[1] / "output" / "spells_by_school_pie.png")
        pastel_grouped_bar(bucket_counts, Path(__file__).resolve().parents[1] / "output" / "spells_level_buckets_by_school.png")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
