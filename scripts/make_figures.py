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
    "claude-haiku": "#AA3377",
    "loopy-haiku": "#BBBBBB",
    "loopy-qwen3-coder": "#332288",
}

# Ordered variant list for consistent chart ordering
VARIANT_ORDER = [
    "control", "variant-a", "variant-b", "variant-c", "variant-d",
    "variant-e", "claude-sonnet-sae",
    "claude-haiku", "claude-haiku-sae",
    "loopy-sonnet", "loopy-haiku", "loopy-haiku-sae",
    "loopy-qwen3-coder",
]

# Human-readable labels showing model + framework
VARIANT_LABELS = {
    "control": "control\n(CC+Sonnet)",
    "variant-a": "variant-a\n(CC+Sonnet)",
    "variant-b": "variant-b\n(CC+Sonnet)",
    "variant-c": "variant-c\n(CC+Sonnet)",
    "variant-d": "variant-d\n(CC+Sonnet)",
    "variant-e": "variant-e\n(CC+Sonnet forge)",
    "claude-sonnet-sae": "claude-sonnet-sae\n(CC+Sonnet+SAE)",
    "claude-haiku": "claude-haiku\n(CC+Haiku)",
    "claude-haiku-sae": "claude-haiku-sae\n(CC+Haiku+SAE)",
    "loopy-sonnet": "loopy-sonnet\n(Loopy+Sonnet)",
    "loopy-haiku": "loopy-haiku\n(Loopy+Haiku)",
    "loopy-haiku-sae": "loopy-haiku-sae\n(Loopy+Haiku+SAE)",
    "loopy-qwen3-coder": "loopy-qwen\n(Loopy+Qwen3)",
}

# Framework grouping
CLAUDE_VARIANTS = {"control", "variant-a", "variant-b", "variant-c", "variant-d", "variant-e", "claude-sonnet-sae", "claude-haiku", "claude-haiku-sae"}
LOOPY_VARIANTS = {"loopy-sonnet", "loopy-haiku", "loopy-haiku-sae", "loopy-qwen3-coder"}


def ordered_variants(variants):
    """Sort variants in presentation order."""
    order = {v: i for i, v in enumerate(VARIANT_ORDER)}
    return sorted(variants, key=lambda v: order.get(v, 999))


def load_data():
    con = duckdb.connect()
    runs = con.execute(f"SELECT * FROM '{DATA_DIR}/runs.parquet'").df()
    items = con.execute(f"SELECT * FROM '{DATA_DIR}/item_results.parquet'").df()
    tool_uses_path = DATA_DIR / "tool_uses.parquet"
    tools = con.execute(f"SELECT * FROM '{tool_uses_path}'").df() if tool_uses_path.exists() else None
    return runs, items, tools


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


def make_agent_timeline(tools, items):
    """Strip chart: tool uses over turns per variant, showing agent execution pattern.

    Each row is a variant. X-axis is the global turn sequence. Markers are colored
    by tool type. Phase boundaries are shown as vertical lines. This makes the
    "big blob of thinking" pattern in variant-d visually obvious.
    """
    if tools is None or tools.empty:
        print("  agent-timeline: no tool_uses data, skipping")
        return

    # Tool type → color mapping
    TOOL_COLORS = {
        "Read": "#4477AA",     # blue — reading/exploring
        "Glob": "#4477AA",
        "Grep": "#4477AA",
        "Write": "#228833",    # green — creating files
        "Edit": "#66CCEE",     # cyan — modifying files
        "Bash": "#EE6677",     # red — executing commands
        "TodoWrite": "#BBBBBB",
    }
    DEFAULT_COLOR = "#CCBB44"  # yellow for anything else

    # Tool type → y-position within a variant lane
    TOOL_Y = {"Read": 0, "Glob": 0, "Grep": 0, "Write": 1, "Edit": 1, "Bash": 2}
    TOOL_LABELS = {0: "Read/Search", 1: "Write/Edit", 2: "Bash"}

    # Only show items that have tool data
    item_slugs = sorted(tools["item_slug"].unique())
    variants = sorted(tools["variant"].unique())

    for item_slug in item_slugs:
        item_tools = tools[tools["item_slug"] == item_slug]
        item_variants = ordered_variants(item_tools["variant"].unique())
        n = len(item_variants)
        if n == 0:
            continue

        # Compute shared x-axis max across all variants for this item
        x_max = item_tools["global_seq"].max() + 1

        lane_height = 4.0  # height per variant lane
        fig, axes = plt.subplots(n, 1, figsize=(14, lane_height * n),
                                 sharex=True, squeeze=False)

        for row_idx, v in enumerate(item_variants):
            ax = axes[row_idx, 0]
            vt = item_tools[item_tools["variant"] == v].sort_values("global_seq")

            # Plot each tool use as a marker
            for _, t in vt.iterrows():
                x = t["global_seq"]
                y = TOOL_Y.get(t["tool_name"], 2)
                color = TOOL_COLORS.get(t["tool_name"], DEFAULT_COLOR)
                ax.scatter(x, y, c=color, s=30, alpha=0.8, edgecolors="none", zorder=3)

            # Phase boundaries as vertical lines
            phases = vt.groupby("phase_name")["global_seq"].agg(["min", "max"])
            for phase_name, bounds in phases.iterrows():
                ax.axvline(bounds["min"], color="#333333", linewidth=1, linestyle="--", alpha=0.5)
                # Label the phase at the top
                mid = (bounds["min"] + bounds["max"]) / 2
                ax.text(mid, 2.6, phase_name, ha="center", va="bottom", fontsize=8,
                        fontstyle="italic", color="#555555")

            ax.set_xlim(0, x_max)
            ax.set_yticks([0, 1, 2])
            ax.set_yticklabels(["Read/Search", "Write/Edit", "Bash"])
            ax.set_ylim(-0.5, 3.2)
            label = VARIANT_LABELS.get(v, v).replace("\n", " ")
            ax.set_ylabel(label, fontsize=9, fontweight="bold")
            ax.grid(axis="x", alpha=0.2)

            # Show turn count and cost from item_results if available
            vi = items[(items["variant"] == v) & (items["item_slug"] == item_slug)]
            if len(vi) == 1:
                cost = vi["cost_usd"].iloc[0]
                duration_s = vi["duration_ms"].iloc[0] / 1000
                ax.text(0.98, 0.95, f"${cost:.2f} · {duration_s:.0f}s",
                        transform=ax.transAxes, ha="right", va="top", fontsize=8,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

        axes[-1, 0].set_xlabel("Tool Call Sequence (turn)")

        # Legend
        from matplotlib.lines import Line2D
        legend_items = [
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#4477AA", markersize=8, label="Read/Search"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#228833", markersize=8, label="Write"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#66CCEE", markersize=8, label="Edit"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#EE6677", markersize=8, label="Bash"),
        ]
        axes[0, 0].legend(handles=legend_items, loc="upper left", ncol=4, fontsize=8)

        slug_short = item_slug.replace("gs-", "").replace("spring-", "")
        fig.suptitle(f"Agent Execution Timeline — {item_slug}", fontsize=13, fontweight="bold")
        plt.tight_layout()
        save_fig(fig, f"agent-timeline-{slug_short}")


def make_step_count_distribution(items):
    """Histogram of turn counts per task, grouped by variant."""
    variants = ordered_variants(items["variant"].unique())

    fig, ax = plt.subplots(figsize=(9, 5))
    # Use total_tokens as proxy for turns if no turn column — check what we have
    # items may have phase_count but not per-item turn count in parquet
    # Use duration_ms / 1000 as a proxy, or check for tool counts
    # Actually we can get turn count from tool_uses if available, but simpler:
    # use input_tokens + output_tokens as a measure of "work done"

    # Group by variant, show cost per item as proxy for effort
    width = 0.8 / len(variants)
    slugs = sorted(items["item_slug"].unique())
    x = np.arange(len(slugs))

    for i, v in enumerate(variants):
        vals = []
        for slug in slugs:
            cell = items[(items["item_slug"] == slug) & (items["variant"] == v)]
            if len(cell) == 1:
                # Use output_tokens as a proxy for "steps/effort"
                vals.append(cell["output_tokens"].iloc[0] / 1000)
            else:
                vals.append(0)
        offset = (i - len(variants) / 2 + 0.5) * width
        ax.bar(x + offset, vals, width * 0.9, label=v,
               color=COLORS.get(v, "#333"), alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels([s.replace("gs-", "").replace("spring-", "") for s in slugs],
                       rotation=30, ha="right")
    ax.set_ylabel("Output Tokens (K)")
    ax.legend(fontsize=7, ncol=2)
    ax.grid(axis="y", alpha=0.3)
    ax.set_title("Agent Effort per Item (Output Tokens)")
    plt.tight_layout()

    save_fig(fig, "step-count-distribution")


def _parse_bash_tool(target):
    """Extract the actual Unix utility from a bash command string."""
    if not target:
        return "bash"
    cmd = target.strip()
    # Skip env vars, cd, sudo prefixes
    for prefix in ("sudo ", "cd ", "env "):
        if cmd.startswith(prefix):
            cmd = cmd[len(prefix):]
    # Get first word
    first = cmd.split()[0] if cmd.split() else "bash"
    # Strip path
    first = first.rsplit("/", 1)[-1]
    # Map common patterns
    if first in ("./mvnw", "mvn", "mvnw"):
        return "mvn"
    if first in ("./gradlew", "gradle", "gradlew"):
        return "gradle"
    if first == "jar":
        return "jar-inspect"
    if first in ("cat", "head", "tail", "less"):
        return "cat"
    if first in ("find", "ls", "tree"):
        return "ls"
    if first in ("rm", "mkdir", "cp", "mv", "chmod"):
        return "fs-ops"
    return first


def make_tool_usage_frequency(tools):
    """Bar chart: tool call frequency with bash decomposed to actual utilities."""
    if tools is None or tools.empty:
        print("  tool-usage-frequency: no tool_uses data, skipping")
        return

    # Decompose bash into actual tools
    resolved = tools.copy()
    mask = resolved["tool_name"] == "Bash"
    resolved.loc[mask, "tool_name"] = resolved.loc[mask, "target"].apply(_parse_bash_tool)

    variants = ordered_variants(resolved["variant"].unique())

    fig, axes = plt.subplots(1, len(variants), figsize=(4 * len(variants), 6),
                             sharey=True, squeeze=False)

    for i, v in enumerate(variants):
        ax = axes[0, i]
        vt = resolved[resolved["variant"] == v]
        counts = vt["tool_name"].value_counts().sort_values(ascending=True)
        # Top 12 tools
        counts = counts.tail(12)
        ax.barh(range(len(counts)), counts.values,
                color=COLORS.get(v, "#333"), alpha=0.85)
        ax.set_yticks(range(len(counts)))
        ax.set_yticklabels(counts.index, fontsize=8)
        ax.set_title(VARIANT_LABELS.get(v, v), fontsize=9, fontweight="bold")
        ax.set_xlabel("Count")
        ax.grid(axis="x", alpha=0.3)

    fig.suptitle("Tool Usage Frequency (Bash Decomposed)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    save_fig(fig, "tool-usage-frequency")


def make_tool_transition_heatmap(tools):
    """Heatmap of tool-to-tool transitions across all variants."""
    if tools is None or tools.empty:
        print("  tool-transition-heatmap: no tool_uses data, skipping")
        return

    # Decompose bash
    resolved = tools.copy()
    mask = resolved["tool_name"] == "Bash"
    resolved.loc[mask, "tool_name"] = resolved.loc[mask, "target"].apply(_parse_bash_tool)

    variants = ordered_variants(resolved["variant"].unique())

    # Build per-variant transition matrices
    ncols = min(len(variants), 4)
    nrows = (len(variants) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4.5 * nrows), squeeze=False)

    for idx, v in enumerate(variants):
        ax = axes[idx // ncols, idx % ncols]
        vt = resolved[resolved["variant"] == v].sort_values(["item_slug", "global_seq"])

        # Build transitions per item then aggregate
        transitions = {}
        for item_slug in vt["item_slug"].unique():
            item_tools = vt[vt["item_slug"] == item_slug]["tool_name"].tolist()
            for a, b in zip(item_tools[:-1], item_tools[1:]):
                transitions[(a, b)] = transitions.get((a, b), 0) + 1

        if not transitions:
            ax.set_title(v)
            ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
            continue

        # Get top tools by frequency
        tool_counts = {}
        for (a, b), c in transitions.items():
            tool_counts[a] = tool_counts.get(a, 0) + c
            tool_counts[b] = tool_counts.get(b, 0) + c
        top_tools = sorted(tool_counts, key=tool_counts.get, reverse=True)[:8]

        matrix = np.zeros((len(top_tools), len(top_tools)))
        for i, a in enumerate(top_tools):
            for j, b in enumerate(top_tools):
                matrix[i, j] = transitions.get((a, b), 0)

        im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")
        ax.set_xticks(range(len(top_tools)))
        ax.set_xticklabels(top_tools, rotation=45, ha="right", fontsize=7)
        ax.set_yticks(range(len(top_tools)))
        ax.set_yticklabels(top_tools, fontsize=7)
        ax.set_title(v, fontsize=10, fontweight="bold")
        ax.set_xlabel("To")
        ax.set_ylabel("From")

        # Annotate cells
        for i in range(len(top_tools)):
            for j in range(len(top_tools)):
                val = int(matrix[i, j])
                if val > 0:
                    ax.text(j, i, str(val), ha="center", va="center", fontsize=6,
                            color="white" if val > matrix.max() * 0.6 else "black")

    # Hide unused subplots
    for idx in range(len(variants), nrows * ncols):
        axes[idx // ncols, idx % ncols].set_visible(False)

    fig.suptitle("Tool Transition Heatmap (From → To)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    save_fig(fig, "tool-transition-heatmap")


def make_token_burn_chart(items):
    """Stacked bar: input vs output vs thinking tokens per variant.

    Split into two figures — Claude Code variants and Loopy variants — because
    Loopy's unbounded context accumulation (18M+ input tokens) dwarfs the Claude
    Code numbers, making them unreadable on the same scale.
    """
    variants = ordered_variants(items["variant"].unique())

    # Aggregate per variant
    all_data = []
    for v in variants:
        vi = items[items["variant"] == v]
        all_data.append({
            "variant": v,
            "label": VARIANT_LABELS.get(v, v),
            "input": vi["input_tokens"].sum() / 1000,
            "output": vi["output_tokens"].sum() / 1000,
            "thinking": vi["thinking_tokens"].sum() / 1000,
            "is_loopy": v in LOOPY_VARIANTS,
        })

    for group_name, is_loopy in [("claude", False), ("loopy", True)]:
        data = [d for d in all_data if d["is_loopy"] == is_loopy]
        if not data:
            continue

        x = np.arange(len(data))
        fig, ax = plt.subplots(figsize=(max(8, 2.5 * len(data)), 5))

        input_vals = [d["input"] for d in data]
        output_vals = [d["output"] for d in data]
        thinking_vals = [d["thinking"] for d in data]

        ax.bar(x, input_vals, label="Input Tokens", color="#4477AA")
        ax.bar(x, output_vals, bottom=input_vals, label="Output Tokens", color="#EE7733")
        bottoms = [i + o for i, o in zip(input_vals, output_vals)]
        ax.bar(x, thinking_vals, bottom=bottoms, label="Thinking Tokens", color="#228833")

        ax.set_xticks(x)
        ax.set_xticklabels([d["label"] for d in data], rotation=30, ha="right", fontsize=9)
        ax.set_ylabel("Tokens (K)")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

        if is_loopy:
            ax.set_title("Token Consumption — Loopy Variants (no context compaction)")
        else:
            ax.set_title("Token Consumption — Claude Code Variants (managed context)")

        plt.tight_layout()
        save_fig(fig, f"token-burn-{group_name}")


def make_cost_vs_quality_multi(runs, items):
    """Enhanced scatter: cost vs T3, sized by coverage, labeled with model info."""
    fig, ax = plt.subplots(figsize=(9, 6))

    variants = ordered_variants(items["variant"].unique())
    for v in variants:
        vi = items[items["variant"] == v]
        r = runs[runs["variant"] == v]
        if r.empty:
            continue
        r = r.iloc[0]
        t3 = vi["t3_adherence"].mean()
        cost = r["total_cost_usd"]
        cov = vi["coverage_final"].mean()
        pass_rate = r["pass_rate"]

        # Size by coverage, color by variant
        size = max(cov * 3, 40)  # min size 40
        marker = "o" if pass_rate >= 0.8 else "x"
        ax.scatter(cost, t3, s=size, color=COLORS.get(v, "#333"),
                   marker=marker, zorder=5, linewidths=2)
        ax.annotate(v, (cost, t3), textcoords="offset points",
                    xytext=(8, 4), fontsize=8)

    ax.set_xlabel("Total Cost (USD)")
    ax.set_ylabel("T3 Practice Adherence")
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.3)
    ax.set_title("Cost vs. Quality — All Variants\n(circle = ≥80% pass, × = <80% pass, size ∝ coverage)")
    plt.tight_layout()

    save_fig(fig, "cost-quality-all")


def make_model_comparison_bars(items):
    """Side-by-side bars comparing the same prompt across different models/frameworks."""
    # Group variants by prompt type for comparison
    # v1-hardened prompt: variant-a (Sonnet/Claude), claude-haiku, loopy-haiku, loopy-qwen3-coder
    comparison_variants = [v for v in ["variant-a", "claude-haiku", "loopy-haiku", "loopy-qwen3-coder"]
                          if v in items["variant"].unique()]
    if len(comparison_variants) < 2:
        print("  model-comparison: need at least 2 comparable variants, skipping")
        return

    metrics = {
        "T3 Adherence": "t3_adherence",
        "Coverage %": "coverage_final",
        "Efficiency": "eff_composite",
    }

    x = np.arange(len(metrics))
    width = 0.8 / len(comparison_variants)
    fig, ax = plt.subplots(figsize=(9, 5))

    for i, v in enumerate(comparison_variants):
        vi = items[items["variant"] == v]
        vals = []
        for label, col in metrics.items():
            val = vi[col].mean()
            if col == "coverage_final":
                val = val / 100  # normalize to 0-1
            vals.append(val if not np.isnan(val) else 0)
        offset = (i - len(comparison_variants) / 2 + 0.5) * width
        ax.bar(x + offset, vals, width * 0.9, label=v,
               color=COLORS.get(v, "#333"), alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(metrics.keys())
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Score (normalized)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    ax.set_title("Model/Framework Comparison (Same Prompt: v1-hardened)")
    plt.tight_layout()

    save_fig(fig, "model-comparison")


def make_guides_only_comparison(items):
    """Token + cost comparison on guides only (excluding petclinic) for apples-to-apples."""
    guides = items[items["item_slug"] != "spring-petclinic"]
    claude_variants = [v for v in ordered_variants(guides["variant"].unique())
                       if v in CLAUDE_VARIANTS]
    if len(claude_variants) < 2:
        print("  guides-only-comparison: need at least 2 Claude variants, skipping")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: token breakdown (guides only)
    data = []
    for v in claude_variants:
        vi = guides[guides["variant"] == v]
        data.append({
            "label": VARIANT_LABELS.get(v, v),
            "output": vi["output_tokens"].sum() / 1000,
            "thinking": vi["thinking_tokens"].sum() / 1000,
            "color": COLORS.get(v, "#333"),
        })

    x = np.arange(len(data))
    ax1.bar(x, [d["output"] for d in data], label="Output", color="#EE7733")
    ax1.bar(x, [d["thinking"] for d in data],
            bottom=[d["output"] for d in data], label="Thinking", color="#228833")
    ax1.set_xticks(x)
    ax1.set_xticklabels([d["label"] for d in data], rotation=30, ha="right", fontsize=8)
    ax1.set_ylabel("Tokens (K)")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)
    ax1.set_title("Token Usage — Guides Only")

    # Right: T3 + cost (guides only)
    for v in claude_variants:
        vi = guides[guides["variant"] == v]
        t3 = vi["t3_adherence"].mean()
        cost = vi["cost_usd"].sum()
        ax2.scatter(cost, t3, s=150, color=COLORS.get(v, "#333"), zorder=5)
        ax2.annotate(v, (cost, t3), textcoords="offset points",
                     xytext=(8, 4), fontsize=9)
    ax2.set_xlabel("Cost (USD) — Guides Only")
    ax2.set_ylabel("T3 Practice Adherence")
    ax2.set_ylim(0.4, 1.0)
    ax2.grid(alpha=0.3)
    ax2.set_title("Cost vs Quality — Guides Only (5 items)")

    fig.suptitle("Apples-to-Apples: Claude+Sonnet Variants on Getting Started Guides",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    save_fig(fig, "guides-only-comparison")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    runs, items, tools = load_data()
    print("Generating figures:")
    make_variant_radar(runs, items)
    make_per_item_bars(items)
    make_growth_story(runs, items)
    make_cost_quality_scatter(runs, items)
    make_agent_timeline(tools, items)
    make_step_count_distribution(items)
    make_tool_usage_frequency(tools)
    make_tool_transition_heatmap(tools)
    make_token_burn_chart(items)
    make_cost_vs_quality_multi(runs, items)
    make_model_comparison_bars(items)
    make_guides_only_comparison(items)
    print(f"\nWritten to {OUTPUT_DIR}")
