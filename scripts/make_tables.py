#!/usr/bin/env python3
"""Generate LaTeX tables from experiment Parquet data."""

from pathlib import Path
import duckdb
from tabulate import tabulate

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "curated"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "latex" / "tables"

# Use latex_raw so tabulate doesn't re-escape our LaTeX commands,
# then post-process \hline to booktabs rules.
TABLE_FMT = "latex_raw"

# Short labels for tables: agent:model notation
VARIANT_TABLE_LABELS = {
    "control": "CC:Sonnet (naive)",
    "variant-a": "CC:Sonnet (hardened)",
    "variant-b": "CC:Sonnet (+3 KB)",
    "variant-c": "CC:Sonnet (+full KB)",
    "variant-d": "CC:Sonnet (two-phase)",
    "claude-haiku": "CC:Haiku",
    "loopy-haiku": "Loopy:Haiku",
    "loopy-qwen3-coder": "Loopy:Qwen3",
    "claude-haiku-sae": "CC:Haiku (+SAE)",
    "claude-sonnet-sae": "CC:Sonnet (+SAE)",
    "loopy-haiku-sae": "Loopy:Haiku (+SAE)",
    "loopy-sonnet": "Loopy:Sonnet",
    "variant-e": "CC:Sonnet (forge)",
}

VARIANT_ORDER = [
    "control", "variant-a", "variant-b", "variant-c", "variant-d",
    "variant-e", "claude-sonnet-sae",
    "claude-haiku", "claude-haiku-sae",
    "loopy-sonnet", "loopy-haiku", "loopy-haiku-sae",
    "loopy-qwen3-coder",
]


def variant_label(v: str) -> str:
    return escape_latex(VARIANT_TABLE_LABELS.get(v, v))


def ordered_variants(variants):
    order = {v: i for i, v in enumerate(VARIANT_ORDER)}
    return sorted(variants, key=lambda v: order.get(v, 999))


def escape_latex(s: str) -> str:
    return s.replace("_", r"\_").replace("&", r"\&").replace("%", r"\%")


def to_booktabs(body: str) -> str:
    """Replace \\hline with \\toprule, \\midrule, \\bottomrule."""
    lines = body.split("\n")
    hline_indices = [i for i, l in enumerate(lines) if l.strip() == r"\hline"]
    if len(hline_indices) >= 3:
        lines[hline_indices[0]] = r"\toprule"
        lines[hline_indices[1]] = r"\midrule"
        lines[hline_indices[2]] = r"\bottomrule"
    elif len(hline_indices) == 2:
        lines[hline_indices[0]] = r"\toprule"
        lines[hline_indices[1]] = r"\bottomrule"
    return "\n".join(lines)


def wrap_table(body: str, caption: str, label: str) -> str:
    return (
        "\\begin{table}[t]\n"
        "\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{{label}}}\n"
        "\\small\n"
        f"{to_booktabs(body)}\n"
        "\\end{table}\n"
    )


def load_data():
    con = duckdb.connect()
    runs = con.execute(f"SELECT * FROM '{DATA_DIR}/runs.parquet'").df()
    items = con.execute(f"SELECT * FROM '{DATA_DIR}/item_results.parquet'").df()
    judges = con.execute(f"SELECT * FROM '{DATA_DIR}/judge_details.parquet'").df()
    return runs, items, judges


def make_variant_comparison(runs, items):
    """Table 1: Variant comparison summary."""
    rows = []
    for v in ordered_variants(runs["variant"].unique()):
        r = runs[runs["variant"] == v].iloc[0]
        vi = items[items["variant"] == v]
        cov = vi["coverage_final"].mean()
        rows.append([
            variant_label(v),
            f"{int(r['item_count'])}",
            f"{r['pass_rate'] * 100:.0f}\\%",
            f"{cov:.1f}",
            f"{vi['t3_adherence'].mean():.2f}" if vi['t3_adherence'].notna().any() else "---",
            f"{vi['eff_composite'].mean():.2f}",
            f"\\${r['total_cost_usd']:.2f}",
            f"\\${r['total_cost_usd'] / r['item_count']:.2f}",
        ])

    headers = ["Agent:Model", "N", "Pass\\%", "Cov\\%", "T3", "Eff", "Total", "Per Item"]
    body = tabulate(rows, headers=headers, tablefmt=TABLE_FMT)

    tex = wrap_table(body,
        "Variant comparison (N=1 per cell, sorted by variant progression)",
        "tab:variant-comparison")
    (OUTPUT_DIR / "variant-comparison.tex").write_text(tex)
    print("  variant-comparison.tex")


def make_per_item_breakdown(items):
    """Table 2: T3 score per item x variant."""
    variants = ordered_variants(items["variant"].unique())
    slugs = sorted(items["item_slug"].unique())

    rows = []
    for slug in slugs:
        row = [escape_latex(slug)]
        for v in variants:
            cell = items[(items["item_slug"] == slug) & (items["variant"] == v)]
            if len(cell) == 1:
                row.append(f"{cell['t3_adherence'].iloc[0]:.2f}")
            else:
                row.append("---")
        rows.append(row)

    headers = ["Item"] + [variant_label(v) for v in variants]
    body = tabulate(rows, headers=headers, tablefmt=TABLE_FMT)

    tex = wrap_table(body,
        "T3 practice adherence per item (higher is better)",
        "tab:per-item-breakdown")
    (OUTPUT_DIR / "per-item-breakdown.tex").write_text(tex)
    print("  per-item-breakdown.tex")


def make_judge_cascade(items):
    """Table 3: Judge pass/fail per variant."""
    variants = ordered_variants(items["variant"].unique())

    judge_cols = [
        ("t0_build", "Build Success"),
        ("t1_preservation", "Coverage Preservation"),
        ("t2_improvement", "Coverage Improvement"),
        ("t3_adherence", "Practice Adherence"),
        ("golden_similarity", "Golden Similarity"),
    ]

    rows = []
    for col, label in judge_cols:
        row = [label]
        for v in variants:
            vi = items[items["variant"] == v]
            val = vi[col].mean()
            if col in ("t0_build", "t1_preservation", "t2_improvement"):
                row.append(f"{val * 100:.0f}\\%")
            else:
                row.append(f"{val:.2f}")
        rows.append(row)

    headers = ["Judge"] + [variant_label(v) for v in variants]
    body = tabulate(rows, headers=headers, tablefmt=TABLE_FMT)

    tex = wrap_table(body,
        "Judge cascade results per variant (tier 0--3 + golden)",
        "tab:judge-cascade")
    (OUTPUT_DIR / "judge-cascade.tex").write_text(tex)
    print("  judge-cascade.tex")


def make_cost_analysis(runs, items):
    """Table 4: Cost and token breakdown per variant."""
    rows = []
    for v in ordered_variants(runs["variant"].unique()):
        r = runs[runs["variant"] == v].iloc[0]
        vi = items[items["variant"] == v]
        rows.append([
            variant_label(v),
            f"\\${r['total_cost_usd']:.2f}",
            f"\\${r['total_cost_usd'] / r['item_count']:.2f}",
            f"{vi['input_tokens'].sum():,}",
            f"{vi['output_tokens'].sum():,}",
            f"{vi['thinking_tokens'].sum():,}",
            f"{r['total_duration_ms'] / 1000:.0f}s",
        ])

    headers = ["Agent:Model", "Total", "Per Item", "In Tok", "Out Tok", "Think Tok", "Duration"]
    body = tabulate(rows, headers=headers, tablefmt=TABLE_FMT)

    tex = wrap_table(body,
        "Cost and token breakdown per variant",
        "tab:cost-analysis")
    (OUTPUT_DIR / "cost-analysis.tex").write_text(tex)
    print("  cost-analysis.tex")


def make_efficiency_breakdown(items):
    """Table 5: Efficiency sub-metrics per variant."""
    variants = ordered_variants(items["variant"].unique())

    rows = []
    for v in variants:
        vi = items[items["variant"] == v]
        rows.append([
            variant_label(v),
            f"{vi['eff_build_errors'].mean():.2f}",
            f"{vi['eff_cost'].mean():.2f}",
            f"{vi['eff_recovery_cycles'].mean():.2f}",
            f"{vi['eff_composite'].mean():.2f}",
            f"{vi['output_tokens'].mean():,.0f}",
            f"{vi['thinking_tokens'].mean():,.0f}",
            f"{vi['duration_ms'].mean() / 1000:.0f}s",
        ])

    headers = ["Agent:Model", "Build Err", "Cost Eff", "Recovery", "Composite",
               "Avg Out Tok", "Avg Think Tok", "Avg Duration"]
    body = tabulate(rows, headers=headers, tablefmt=TABLE_FMT)

    tex = wrap_table(body,
        "Efficiency breakdown per variant (higher is better, except tokens/duration)",
        "tab:efficiency-breakdown")
    (OUTPUT_DIR / "efficiency-breakdown.tex").write_text(tex)
    print("  efficiency-breakdown.tex")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    runs, items, judges = load_data()
    print("Generating LaTeX tables:")
    make_variant_comparison(runs, items)
    make_per_item_breakdown(items)
    make_judge_cascade(items)
    make_cost_analysis(runs, items)
    make_efficiency_breakdown(items)
    print(f"\nWritten to {OUTPUT_DIR}")
