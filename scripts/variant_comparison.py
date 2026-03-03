"""
Core ablation analysis: per-variant aggregates and per-item breakdowns.

Produces analysis/tables/variant-comparison.md with:
- Summary table across all variants
- Per-item T3 breakdown pivoted by variant
- Per-item efficiency breakdown
- Per-item golden similarity

Dynamically handles whatever variants are in the parquet data.

Usage:
    python scripts/variant_comparison.py
"""

from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CURATED_DIR = PROJECT_ROOT / "data" / "curated"
TABLES_DIR = PROJECT_ROOT / "analysis" / "tables"
ITEM_RESULTS = CURATED_DIR / "item_results.parquet"


def get_variants(con) -> list[str]:
    """Get sorted list of variants in the data."""
    rows = con.execute(f"SELECT DISTINCT variant FROM '{ITEM_RESULTS}' ORDER BY variant").fetchall()
    return [r[0] for r in rows]


def pivot_query(con, metric: str, variants: list[str]) -> list[tuple]:
    """Build and execute a pivot query for a metric across variants."""
    cases = ", ".join(
        f"MAX(CASE WHEN variant='{v}' THEN ROUND({metric}, 3) END) AS \"{v}\""
        for v in variants
    )
    return con.execute(f"""
        SELECT item_slug, {cases}
        FROM '{ITEM_RESULTS}'
        GROUP BY item_slug ORDER BY item_slug
    """).fetchall()


def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()

    variants = get_variants(con)
    print(f"Variants: {variants}")

    lines = ["# Variant Comparison\n"]

    # 1. Summary table
    lines.append("## Summary\n")
    summary = con.execute(f"""
        SELECT variant,
            COUNT(*) AS items,
            SUM(CASE WHEN passed THEN 1 ELSE 0 END) * 100 / COUNT(*) AS pass_pct,
            ROUND(AVG(coverage_final), 1) AS avg_cov,
            ROUND(AVG(t3_adherence), 3) AS avg_t3,
            ROUND(AVG(golden_similarity), 3) AS avg_golden,
            ROUND(AVG(eff_composite), 3) AS avg_eff,
            ROUND(SUM(cost_usd), 2) AS total_cost,
            ROUND(AVG(cost_usd), 2) AS avg_cost,
            MAX(phase_count) AS phases
        FROM '{ITEM_RESULTS}'
        GROUP BY variant ORDER BY variant
    """).fetchall()

    lines.append("| Variant | Pass% | Avg Cov% | Avg T3 | Avg Golden | Avg Eff | Total Cost | Phases |")
    lines.append("|---------|-------|----------|--------|------------|---------|------------|--------|")
    for row in summary:
        phase_label = f"{row[9]}ph" if row[9] and row[9] > 1 else "1ph"
        lines.append(f"| {row[0]} | {row[2]}% | {row[3]} | {row[4]} | {row[5]} | {row[6]} | ${row[7]} | {phase_label} |")
    lines.append("")

    print("=== VARIANT SUMMARY ===")
    for row in summary:
        phase_label = f"{row[9]}ph" if row[9] and row[9] > 1 else "1ph"
        print(f"  {row[0]:12s}  pass={row[2]}%  cov={row[3]}%  T3={row[4]}  golden={row[5]}  eff={row[6]}  cost=${row[7]}  {phase_label}")
    print()

    # 2. Per-item T3 breakdown
    lines.append("## Per-Item T3 Practice Adherence\n")
    t3_data = pivot_query(con, "t3_adherence", variants)

    header = "| Item | " + " | ".join(variants) + " |"
    sep = "|------|" + "|".join(["------"] * len(variants)) + "|"
    lines.append(header)
    lines.append(sep)
    for row in t3_data:
        vals = row[1:]
        non_none = [v for v in vals if v is not None]
        best = max(non_none) if non_none else None
        cells = []
        for v in vals:
            if v is None:
                cells.append("—")
            elif v == best:
                cells.append(f"**{v}**")
            else:
                cells.append(str(v))
        lines.append(f"| {row[0]} | " + " | ".join(cells) + " |")
    lines.append("")

    # 3. Per-item golden similarity
    lines.append("## Per-Item Golden Test Similarity\n")
    golden_data = pivot_query(con, "golden_similarity", variants)

    lines.append(header)
    lines.append(sep)
    for row in golden_data:
        vals = row[1:]
        non_none = [v for v in vals if v is not None]
        best = max(non_none) if non_none else None
        cells = []
        for v in vals:
            if v is None:
                cells.append("—")
            elif v == best:
                cells.append(f"**{v}**")
            else:
                cells.append(str(v))
        lines.append(f"| {row[0]} | " + " | ".join(cells) + " |")
    lines.append("")

    # 4. Per-item coverage
    lines.append("## Per-Item Coverage (%)\n")
    cov_data = pivot_query(con, "coverage_final", variants)

    lines.append(header)
    lines.append(sep)
    for row in cov_data:
        vals = row[1:]
        cells = [str(v) if v is not None else "—" for v in vals]
        lines.append(f"| {row[0]} | " + " | ".join(cells) + " |")
    lines.append("")

    # 5. Per-item efficiency
    lines.append("## Per-Item Efficiency\n")
    eff_data = pivot_query(con, "eff_composite", variants)

    lines.append(header)
    lines.append(sep)
    for row in eff_data:
        vals = row[1:]
        cells = [str(v) if v is not None else "—" for v in vals]
        lines.append(f"| {row[0]} | " + " | ".join(cells) + " |")
    lines.append("")

    # Write markdown
    output = TABLES_DIR / "variant-comparison.md"
    output.write_text("\n".join(lines))
    print(f"Written to {output}")

    con.close()


if __name__ == "__main__":
    main()
