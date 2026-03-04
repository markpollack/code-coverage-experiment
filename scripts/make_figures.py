#!/usr/bin/env python3
"""Generate publication-quality figures from experiment Parquet data."""

from pathlib import Path
import duckdb
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "curated"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "latex" / "figures"

# Publication-quality matplotlib settings
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
})

# Colorblind-friendly palette
COLORS = {
    "control": "#999999",
    "variant-a": "#0077BB",
    "variant-b": "#EE7733",
    "variant-c": "#009988",
    "variant-d": "#CC3311",
}


def load_data():
    con = duckdb.connect()
    runs = con.execute(f"SELECT * FROM '{DATA_DIR}/runs.parquet'").df()
    items = con.execute(f"SELECT * FROM '{DATA_DIR}/item_results.parquet'").df()
    return runs, items


def save_fig(fig, name):
    fig.savefig(OUTPUT_DIR / f"{name}.pdf")
    fig.savefig(OUTPUT_DIR / f"{name}.png")
    plt.close(fig)
    print(f"  {name}.pdf + .png")


def make_variant_radar(runs, items):
    """Radar chart comparing variants across metrics."""
    variants = sorted(items["variant"].unique())
    metrics = ["T3 Adherence", "Golden Sim.", "Coverage %", "Efficiency", "Pass Rate"]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]

    for v in variants:
        vi = items[items["variant"] == v]
        r = runs[runs["variant"] == v].iloc[0]
        values = [
            vi["t3_adherence"].mean(),
            vi["golden_similarity"].mean(),
            vi["coverage_final"].mean() / 100,
            vi["eff_composite"].mean(),
            r["pass_rate"],
        ]
        values += values[:1]
        ax.plot(angles, values, "o-", label=v, color=COLORS.get(v, "#333"), linewidth=1.5, markersize=4)
        ax.fill(angles, values, alpha=0.05, color=COLORS.get(v, "#333"))

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 1.05)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    ax.set_title("Variant Comparison — Multi-Metric Radar", pad=20)

    save_fig(fig, "variant-radar")


def make_per_item_bars(items):
    """Grouped bar chart: T3 per item, one bar per variant."""
    variants = sorted(items["variant"].unique())
    slugs = sorted(items["item_slug"].unique())
    n_variants = len(variants)
    width = 0.8 / n_variants
    x = np.arange(len(slugs))

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, v in enumerate(variants):
        vals = []
        for slug in slugs:
            cell = items[(items["item_slug"] == slug) & (items["variant"] == v)]
            vals.append(cell["t3_adherence"].iloc[0] if len(cell) == 1 else 0)
        offset = (i - n_variants / 2 + 0.5) * width
        ax.bar(x + offset, vals, width * 0.9, label=v, color=COLORS.get(v, "#333"))

    ax.set_xticks(x)
    ax.set_xticklabels([s.replace("gs-", "") for s in slugs], rotation=30, ha="right")
    ax.set_ylabel("T3 Practice Adherence")
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    ax.set_title("T3 Practice Adherence by Item and Variant")
    plt.tight_layout()

    save_fig(fig, "per-item-bars")


def make_growth_story(runs, items):
    """Stepped chart showing score progression as levers are added."""
    lever_order = ["control", "variant-a", "variant-b", "variant-c", "variant-d"]
    lever_labels = ["Baseline", "+Hardened\nPrompt", "+3 KB\nFiles", "+Full KB", "+Two-Phase"]
    metrics = {
        "T3 Adherence": "t3_adherence",
        "Golden Similarity": "golden_similarity",
        "Efficiency": "eff_composite",
    }

    present = [v for v in lever_order if v in items["variant"].unique()]
    labels = [lever_labels[lever_order.index(v)] for v in present]
    x = np.arange(len(present))

    fig, ax = plt.subplots(figsize=(8, 5))
    for label, col in metrics.items():
        vals = [items[items["variant"] == v][col].mean() for v in present]
        ax.plot(x, vals, "o-", label=label, linewidth=2, markersize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    ax.set_title("Score Progression as Levers Are Added")
    plt.tight_layout()

    save_fig(fig, "growth-story")


def make_cost_quality_scatter(runs, items):
    """Scatter plot: cost vs T3 quality per variant."""
    fig, ax = plt.subplots(figsize=(7, 5))

    variants = sorted(items["variant"].unique())
    for v in variants:
        vi = items[items["variant"] == v]
        r = runs[runs["variant"] == v].iloc[0]
        t3 = vi["t3_adherence"].mean()
        cost = r["total_cost_usd"]
        ax.scatter(cost, t3, s=120, color=COLORS.get(v, "#333"), zorder=5)
        ax.annotate(v, (cost, t3), textcoords="offset points",
                    xytext=(8, 4), fontsize=9)

    ax.set_xlabel("Total Cost (USD)")
    ax.set_ylabel("T3 Practice Adherence")
    ax.set_ylim(0.5, 1.0)
    ax.grid(alpha=0.3)
    ax.set_title("Cost vs. Quality Trade-off")
    plt.tight_layout()

    save_fig(fig, "cost-quality")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    runs, items = load_data()
    print("Generating figures:")
    make_variant_radar(runs, items)
    make_per_item_bars(items)
    make_growth_story(runs, items)
    make_cost_quality_scatter(runs, items)
    print(f"\nWritten to {OUTPUT_DIR}")
