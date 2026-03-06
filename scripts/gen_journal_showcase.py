#!/usr/bin/env python3
"""Generate a before/after agent-journal showcase image.

Left panel:  CC:Sonnet (hardened) on gs-rest-service — jar-inspect spiral visible
Right panel: CC:Haiku (+SAE v2) on gs-rest-service — zero jar-inspect calls

Each tool call is a colored square in sequence, like a filmstrip.
"""

import re
import duckdb
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "curated"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "latex" / "figures"

CATEGORY_COLORS = {
    "jar-inspect": "#e74c3c",   # red — the waste
    "Bash":        "#95a5a6",   # grey
    "Read":        "#3498db",   # blue
    "Write":       "#2ecc71",   # green
    "Edit":        "#f39c12",   # orange
    "Glob":        "#9b59b6",   # purple
}

def classify(tool_name, target):
    t = str(target or "")
    if re.search(r"jar\s+(-)?[tx]f", t) or ("find" in t and ".m2" in t):
        return "jar-inspect"
    if tool_name == "Bash":
        return "Bash"
    return tool_name


def load_sequence(con, variant, item="gs-rest-service"):
    df = con.execute(f"""
        SELECT tool_name, target, global_seq
        FROM '{DATA_DIR}/tool_uses.parquet'
        WHERE variant = '{variant}' AND item_slug = '{item}'
        ORDER BY global_seq
    """).df()
    df["category"] = df.apply(lambda r: classify(r["tool_name"], r["target"]), axis=1)
    return df


def draw_filmstrip(ax, df, title, cols=10):
    """Draw tool calls as colored squares in a grid."""
    n = len(df)
    rows = int(np.ceil(n / cols))

    for idx, (_, row) in enumerate(df.iterrows()):
        r = idx // cols
        c = idx % cols
        color = CATEGORY_COLORS.get(row["category"], "#bdc3c7")
        is_jar = row["category"] == "jar-inspect"
        rect = mpatches.FancyBboxPatch(
            (c, rows - 1 - r), 0.85, 0.85,
            boxstyle="round,pad=0.05",
            facecolor=color,
            edgecolor="#c0392b" if is_jar else "#7f8c8d",
            linewidth=2.0 if is_jar else 0.5,
            alpha=1.0 if is_jar else 0.8,
        )
        ax.add_patch(rect)

    ax.set_xlim(-0.3, cols + 0.3)
    ax.set_ylim(-0.5, rows + 0.5)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.axis("off")


def main():
    con = duckdb.connect()
    va = load_sequence(con, "variant-a")
    sae = load_sequence(con, "claude-haiku-sae")

    jar_count_va = (va["category"] == "jar-inspect").sum()
    jar_count_sae = (sae["category"] == "jar-inspect").sum()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 5.5),
                                    gridspec_kw={"wspace": 0.15})
    fig.suptitle("Agent Execution Trace — gs-rest-service",
                 fontsize=16, fontweight="bold", y=0.98)

    draw_filmstrip(ax1, va,
        f"Before: CC:Sonnet (hardened)\n{len(va)} tool calls, {jar_count_va} jar-inspect",
        cols=8)
    draw_filmstrip(ax2, sae,
        f"After: CC:Haiku (+SAE v2)\n{len(sae)} tool calls, {jar_count_sae} jar-inspect",
        cols=8)

    # Legend
    legend_items = [
        mpatches.Patch(facecolor="#e74c3c", edgecolor="#c0392b", linewidth=2, label="jar-inspect (wasted exploration)"),
        mpatches.Patch(facecolor="#95a5a6", label="Bash (build, test)"),
        mpatches.Patch(facecolor="#3498db", label="Read"),
        mpatches.Patch(facecolor="#2ecc71", label="Write"),
        mpatches.Patch(facecolor="#f39c12", label="Edit"),
    ]
    fig.legend(handles=legend_items, loc="lower center", ncol=5,
               fontsize=11, frameon=True, fancybox=True,
               bbox_to_anchor=(0.5, 0.02))

    plt.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.10)

    for ext in ("png", "pdf"):
        out = OUTPUT_DIR / f"journal-showcase.{ext}"
        fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Written to {OUTPUT_DIR}/journal-showcase.{{png,pdf}}")


if __name__ == "__main__":
    main()
