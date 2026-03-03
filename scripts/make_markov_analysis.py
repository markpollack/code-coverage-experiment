#!/usr/bin/env python3
"""
Markov chain analysis of agent tool-call traces — thin wrapper.

Defines the 9-state taxonomy and Spring/Maven-specific classifier,
then delegates to markov-agent-analysis library for all computation.

Requires:
    pip install markov-agent-analysis[all]
"""

from pathlib import Path
import duckdb
import matplotlib
matplotlib.use("Agg")  # non-interactive backend

from markov_agent_analysis import MarkovAnalysisPipeline

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "curated"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "latex" / "figures"
ANALYSIS_DIR = PROJECT_ROOT / "analysis"

# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------

STATES = [
    "EXPLORE", "READ_SOURCE", "READ_KB", "READ_SAE",
    "WRITE_TEST", "BUILD", "JAR_INSPECT", "JAR_FIND", "FIX_TEST",
]

COLORS = {
    "control":          "#999999",
    "variant-a":        "#0077BB",
    "variant-b":        "#EE7733",
    "variant-c":        "#009988",
    "variant-d":        "#CC3311",
    "variant-e":        "#117733",
    "claude-sonnet-sae":"#DDAA33",
    "claude-haiku":     "#AA3377",
    "claude-haiku-sae": "#BBBBBB",
}

STATE_COLORS = {
    # trap states — red
    "JAR_INSPECT": "#ef4444",
    "JAR_FIND":    "#fca5a5",
    # productive states — green
    "EXPLORE":     "#22c55e",
    "READ_SOURCE": "#86efac",
    "WRITE_TEST":  "#4ade80",
    "READ_SAE":    "#bbf7d0",
    "READ_KB":     "#67e8f9",
    # build/verify states — amber
    "BUILD":       "#f59e0b",
    "FIX_TEST":    "#fbbf24",
}

VARIANT_ORDER = [
    "control", "variant-a", "variant-b", "variant-c", "variant-d",
    "variant-e", "claude-sonnet-sae", "claude-haiku", "claude-haiku-sae",
]

CLUSTER_DEFINITIONS = {
    "JAR":       ["JAR_INSPECT", "JAR_FIND"],
    "BUILD_FIX": ["BUILD", "FIX_TEST"],
}

DELTA_PAIRS = [
    ("control",   "variant-a", "Effect of hardened prompt\n(variant-a minus control)"),
    ("variant-a", "variant-b", "Effect of 3-file KB\n(variant-b minus variant-a)"),
    ("variant-b", "variant-c", "Effect of full KB\n(variant-c minus variant-b)"),
]

NOTE_MAP = {
    "control":          "CC:Sonnet (naive)",
    "variant-a":        "CC:Sonnet (hardened)",
    "variant-b":        "CC:Sonnet (+3-file KB)",
    "variant-c":        "CC:Sonnet (+full KB)",
    "variant-d":        "CC:Sonnet (two-phase)",
    "variant-e":        "CC:Sonnet (+SAE)",
    "claude-sonnet-sae":"CC:Sonnet+SAE v2",
    "claude-haiku":     "CC:Haiku (hardened)",
    "claude-haiku-sae": "CC:Haiku (+SAE)",
}

# ---------------------------------------------------------------------------
# Classifier (Spring/Maven-specific)
# ---------------------------------------------------------------------------

def classify_state(tool_name: str, target: str) -> str | None:
    tool_lower = tool_name.lower() if tool_name else ""
    target_lower = target.lower() if target else ""

    if "jar" in tool_lower or "javap" in tool_lower:
        if "find" in tool_lower or ".m2" in target_lower:
            return "JAR_FIND"
        return "JAR_INSPECT"

    if tool_lower == "bash":
        if "mvnw" in target_lower:
            return "BUILD"
        if "mvn " in target_lower and not target_lower.lstrip().startswith("find"):
            return "BUILD"
        if "jar " in target_lower or target_lower.lstrip().startswith("jar"):
            if ".m2" in target_lower and "find" in target_lower:
                return "JAR_FIND"
            return "JAR_INSPECT"
        if "javap" in target_lower:
            return "JAR_INSPECT"
        if ".m2" in target_lower:
            return "JAR_FIND"
        return "EXPLORE"

    if tool_lower in ("write", "writefile") and "test" in target_lower:
        return "WRITE_TEST"

    if tool_lower in ("edit", "str_replace_editor"):
        return "FIX_TEST"

    if "project-analysis" in target_lower:
        return "READ_SAE"

    if tool_lower in ("read", "readfile"):
        if any(kb in target_lower for kb in [
            "knowledge/index", "/kb/", "plans/knowledge",
            "coverage-mechanic", "jacoco", "common-gaps",
            "coverage-fundamentals", "spring-test-slices", "jacoco-patterns",
            "memory/memory",
        ]):
            return "READ_KB"
        if "project-analysis" in target_lower:
            return "READ_SAE"
        return "READ_SOURCE"

    if tool_lower in ("glob", "grep", "find", "ls"):
        if ".m2" in target_lower:
            return "JAR_FIND"
        return "EXPLORE"

    return "EXPLORE"

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data():
    con = duckdb.connect()
    items = con.execute(f"SELECT * FROM '{DATA_DIR}/item_results.parquet'").df()
    tool_uses_path = DATA_DIR / "tool_uses.parquet"
    tools = con.execute(f"SELECT * FROM '{tool_uses_path}'").df() if tool_uses_path.exists() else None
    con.close()
    return items, tools

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import time
    t0 = time.time()
    print("Markov Chain Analysis of Agent Tool-Call Traces (library wrapper)")
    print("=" * 60)
    print("\nLoading data...")
    items, tools = load_data()
    if tools is None or tools.empty:
        print("ERROR: No tool_uses.parquet data found")
        raise SystemExit(1)
    print(f"  tool_uses: {len(tools)} rows, variants: {sorted(tools['variant'].unique())}")
    print(f"  item_results: {len(items)} rows")

    # Adapt column names to library expectations
    tools = tools.rename(columns={"item_slug": "item_id", "target": "tool_target"})
    tools = tools.sort_values(["variant", "item_id", "global_seq"])
    items = items.rename(columns={"item_slug": "item_id"})

    pipeline = MarkovAnalysisPipeline(
        classify_fn=classify_state,
        states=STATES,
        output_dir=OUTPUT_DIR,
        analysis_dir=ANALYSIS_DIR,
        colors=COLORS,
        variant_order=VARIANT_ORDER,
        cluster_definitions=CLUSTER_DEFINITIONS,
        delta_pairs=DELTA_PAIRS,
        note_map=NOTE_MAP,
        enable_sankey=False,
        tool_name_col="tool_name",
        target_col="tool_target",
    )

    results = pipeline.run(tools, items)

    # Generate Sankey with state-level colors (pipeline uses variant colors)
    from markov_agent_analysis.sankey import make_sankey_flow
    make_sankey_flow(
        results["classified_df"],
        STATES,
        colors=STATE_COLORS,
        output_dir=OUTPUT_DIR,
        variant_order=VARIANT_ORDER,
    )

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"Done in {elapsed:.1f}s")
    print(f"  Figures:      {OUTPUT_DIR}")
    print(f"  Summary:      {ANALYSIS_DIR / 'markov-findings.md'}")
    print(f"  Verification: {ANALYSIS_DIR / 'verification-report.md'}")
