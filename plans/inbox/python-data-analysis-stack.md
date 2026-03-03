# Python Data Analysis Stack for Code-Coverage Experiment

## Context

The code-coverage experiment produces structured results (JSON) with per-item scores across three dimensions: functional correctness, practice adherence, and efficiency. As the experiment scales to multiple variants, models, and iterations, we need an analysis pipeline to query results, compute aggregates, visualize trends, and produce publication-ready artifacts.

This is a proven pattern — the `spring-ai-project-maint` project used DuckDB + Python to go from raw data to research paper. The workflow there was highly effective: describe the analysis you want in natural language, Claude writes the DuckDB SQL + Python script, run it, review the output, iterate. It's interactive analysis without the notebook — conversational data science.

## Reference Implementation

**Project**: `/home/mark/tuvium/projects/spring-ai-project-maint/`

**What it does**: Ingests git history + GitHub issue/PR data, computes a Module Vitality Index, produces quadrant visualizations and sensitivity analyses for a research paper on module maintenance.

**Key files to study**:

| File | What to learn |
|------|---------------|
| `plans/DESIGN.md` | Full data model, DuckDB schema, analysis program specs, design decisions (DD-1 through DD-3), directory layout — **read this first** |
| `scripts/compute_mvi.py` | Pattern for loading parquet → DuckDB queries → percentile normalization → composite scores → parquet output |
| `scripts/plot_quadrants.py` | Pattern for DuckDB → matplotlib publication-quality figures with color coding and annotations |
| `scripts/sensitivity_analysis.py` | Pattern for weight sweep analysis (vary parameters, measure classification stability) |
| `scripts/parse_git_history.py` | Pattern for raw data → parquet ETL |
| `scripts/compute_issue_metrics.py` | Pattern for joining external data sources via DuckDB |
| `scripts/compute_pr_metrics.py` | Pattern for PR data aggregation with DuckDB |
| `scripts/generate_module_cards.py` | Pattern for per-item detail reports (markdown from query results) |

**Analysis outputs**: `analysis/module-pruning/figures/` (quadrant PNGs), `analysis/module-pruning/cards/` (per-module markdown), `analysis/sensitivity/` (weight sensitivity report)

**Data layout**: `data/curated/` holds parquet files (git_commits, git_module_changes, module_mvi, issue_metrics, pr_metrics, etc.). DuckDB reads parquet directly — no separate database file needed for most queries.

## Stack

| Component | Version | Role |
|-----------|---------|------|
| Python | 3.11+ | Runtime |
| DuckDB | latest | Analytical SQL over parquet/JSON — the core query engine |
| pandas | >= 2.0 | DataFrame manipulation, enrichment, export |
| matplotlib | >= 3.7 | Publication-quality static charts |
| numpy | >= 1.24 | Numerical computing (percentile ranks, normalization) |

**Environment**: Use `uv` for dependency management (consistent with other projects). Create a `requirements.txt` or `pyproject.toml` in the experiment root.

**Why DuckDB over pandas-only**: Complex joins (scores × variants × models × items) become unwieldy in pure pandas. DuckDB SQL is readable, composable, and fast over parquet. Write the query in SQL, get a DataFrame back, plot it. Best of both worlds.

## What to Build for Code-Coverage

### Data Model

The experiment already produces JSON results per run. The analysis pipeline reads these and loads into DuckDB for querying.

**Core tables** (created from results JSON):

```sql
-- One row per experiment run
CREATE TABLE runs (
  run_id        VARCHAR PRIMARY KEY,  -- timestamp or UUID
  variant       VARCHAR,              -- control, variant-a, variant-b, variant-c
  model         VARCHAR,              -- opus, sonnet, haiku, local-qwen, etc.
  run_date      TIMESTAMP,
  config        JSON                  -- full experiment config snapshot
);

-- One row per dataset item per run
CREATE TABLE item_results (
  run_id        VARCHAR REFERENCES runs(run_id),
  item_id       VARCHAR,              -- dataset item identifier
  project       VARCHAR,              -- e.g. "spring-petclinic"
  -- Functional correctness (deterministic)
  build_success BOOLEAN,
  tests_pass    BOOLEAN,
  coverage_baseline DOUBLE,
  coverage_final    DOUBLE,
  coverage_delta    DOUBLE,
  -- Practice adherence (LLM judge)
  adherence_score   DOUBLE,           -- composite T3 score
  -- Efficiency scores
  efficiency_build_errors    DOUBLE,
  efficiency_cost            DOUBLE,
  efficiency_recovery_cycles DOUBLE,
  efficiency_composite       DOUBLE,
  -- Cost
  input_tokens  BIGINT,
  output_tokens BIGINT,
  total_cost_usd DOUBLE,
  duration_ms   BIGINT,
  PRIMARY KEY (run_id, item_id)
);

-- Per-item judge detail scores (one row per judge criterion per item)
CREATE TABLE judge_scores (
  run_id        VARCHAR,
  item_id       VARCHAR,
  judge_name    VARCHAR,              -- e.g. "practice-adherence"
  criterion     VARCHAR,              -- e.g. "uses-datafaker", "avoids-springboottest"
  score         DOUBLE,
  rationale     VARCHAR,
  FOREIGN KEY (run_id, item_id) REFERENCES item_results(run_id, item_id)
);
```

### Analysis Scripts to Write

Each script follows the spring-ai-project-maint pattern: load parquet/JSON → DuckDB SQL → pandas DataFrame → output (parquet, figure, or markdown).

**1. `scripts/load_results.py`** — ETL: read experiment results JSON, normalize into parquet files matching the schema above. Run after each experiment batch.

**2. `scripts/variant_comparison.py`** — The core ablation analysis:
```sql
-- Per-variant aggregate scores
SELECT variant, model,
  AVG(coverage_delta) AS avg_coverage_gain,
  AVG(adherence_score) AS avg_adherence,
  AVG(efficiency_composite) AS avg_efficiency,
  AVG(total_cost_usd) AS avg_cost,
  COUNT(*) FILTER (WHERE build_success) * 100.0 / COUNT(*) AS build_success_pct
FROM item_results
JOIN runs USING (run_id)
GROUP BY variant, model
ORDER BY variant, model;
```

This directly tests the thesis: does `variant-c` (full KB) beat `control` on all three dimensions?

**3. `scripts/plot_variant_radar.py`** — Radar/spider chart: one polygon per variant showing correctness, adherence, efficiency. Visual proof of the three-dimensional growth story.

**4. `scripts/plot_cost_vs_quality.py`** — Scatter plot: cost (x) vs coverage gain (y), colored by variant. Shows whether knowledge reduces cost while maintaining quality.

**5. `scripts/growth_story.py`** — Track improvement across iterations of the growth loop: run → judge → add knowledge → run again. Line chart showing scores over iterations.

**6. `scripts/model_comparison.py`** — Cross-model analysis: same variant, different models. Tests whether `knowledge + structured execution > model` — does Haiku + KB beat Opus without KB?

**7. `scripts/sensitivity_analysis.py`** — Vary efficiency weights, check if variant ordering is stable. Follows the spring-ai-project-maint pattern exactly.

**8. `scripts/generate_item_cards.py`** — Per-item detail cards (markdown): coverage before/after, judge scores, efficiency breakdown, agent trajectory summary. Useful for debugging and appendix material.

### Directory Layout

```
code-coverage-experiment/
├── data/
│   └── curated/              # Parquet files (gitignored)
│       ├── runs.parquet
│       ├── item_results.parquet
│       └── judge_scores.parquet
├── scripts/
│   ├── load_results.py       # JSON → parquet ETL
│   ├── variant_comparison.py # Ablation aggregate tables
│   ├── plot_variant_radar.py # Three-dimension radar charts
│   ├── plot_cost_vs_quality.py
│   ├── growth_story.py       # Iteration-over-iteration improvement
│   ├── model_comparison.py   # Cross-model ablation
│   ├── sensitivity_analysis.py
│   └── generate_item_cards.py
├── analysis/
│   ├── figures/              # Generated PNGs
│   ├── tables/               # Generated markdown tables
│   └── cards/                # Per-item detail cards
└── requirements.txt          # duckdb, pandas, matplotlib, numpy
```

### The Workflow

This is the key insight from spring-ai-project-maint: **you don't need notebooks**. The workflow is:

1. Run the experiment (Java) → results JSON lands in `results/`
2. Run `load_results.py` → parquet files in `data/curated/`
3. Tell Claude what you want to see: "show me coverage gain by variant" or "which items did variant-c improve most vs control?"
4. Claude writes a DuckDB query, wraps it in a script, runs it
5. Review output, iterate: "now break that down by model" or "add error bars"
6. When a query stabilizes, it becomes a named script in `scripts/`

Steps 3-5 are interactive analysis — conversational data science. The DuckDB SQL is the shared language between you and the agent. Much faster than clicking through notebook cells.

### Key Queries for the Thesis

These are the questions the analysis pipeline should answer:

**Q1: Does knowledge improve correctness?**
```sql
SELECT variant, AVG(coverage_delta) AS avg_gain, STDDEV(coverage_delta) AS std_gain
FROM item_results JOIN runs USING (run_id)
GROUP BY variant ORDER BY avg_gain DESC;
```

**Q2: Does knowledge improve efficiency?**
```sql
SELECT variant, AVG(efficiency_composite) AS avg_eff, AVG(total_cost_usd) AS avg_cost
FROM item_results JOIN runs USING (run_id)
GROUP BY variant ORDER BY avg_eff DESC;
```

**Q3: Does model matter less than knowledge?** (the thesis test)
```sql
-- Compare: expensive model + no KB vs cheap model + full KB
SELECT variant, model, AVG(coverage_delta), AVG(efficiency_composite), AVG(total_cost_usd)
FROM item_results JOIN runs USING (run_id)
WHERE (variant = 'control' AND model = 'opus')
   OR (variant = 'variant-c' AND model = 'haiku')
GROUP BY variant, model;
```

**Q4: What's the growth loop trajectory?**
```sql
-- Iteration-over-iteration improvement for a given variant
SELECT r.run_date::DATE AS iteration, AVG(coverage_delta), AVG(adherence_score)
FROM item_results i JOIN runs r USING (run_id)
WHERE r.variant = 'variant-c'
GROUP BY iteration ORDER BY iteration;
```

**Q5: Where does knowledge help most?** (per-item delta)
```sql
SELECT c.item_id, c.coverage_delta AS control_gain, v.coverage_delta AS kbe_gain,
       v.coverage_delta - c.coverage_delta AS knowledge_lift
FROM item_results c
JOIN item_results v ON c.item_id = v.item_id
JOIN runs rc ON c.run_id = rc.run_id AND rc.variant = 'control'
JOIN runs rv ON v.run_id = rv.run_id AND rv.variant = 'variant-c'
ORDER BY knowledge_lift DESC;
```

## What NOT to Build Now

- **Interactive REPL** (prplot-style) — overkill for now. The conversational workflow with Claude writing ad-hoc DuckDB queries is faster and more flexible. Add interactive tooling later if the dataset grows large enough to warrant it.
- **Notebooks** — the scripts + conversational approach is more reproducible and version-controllable.
- **Dashboard** — save for when there's a stable set of metrics to monitor across many runs.
