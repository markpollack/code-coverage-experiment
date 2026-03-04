# LaTeX Report Pipeline for Code Coverage Experiment

> Written from research-conversation-agent session, 2026-03-04.
> Model: spring-ai-project-maint report style (article class, executive summary, findings tables).
> NOT academic conference format — this is a technical report / blog-grade paper.

---

## What Exists

The DuckDB + Parquet pipeline is already built:

| Script | What it does | Output |
|--------|-------------|--------|
| `scripts/load_results.py` | ETL: JSON results → DuckDB → Parquet (runs, item_results, judge_details) | `data/curated/*.parquet` |
| `scripts/variant_comparison.py` | DuckDB pivots → markdown tables | `analysis/tables/variant-comparison.md` |
| `scripts/plot_variant_radar.py` | Matplotlib radar chart | `analysis/figures/variant-radar.png` |
| `scripts/generate_item_cards.py` | Per-item markdown summaries | `analysis/cards/*.md` |

Analysis outputs:
- `analysis/sweep-001-getting-started-guides.md` — 150-line experiment report (markdown)
- `analysis/findings-summary.md` — key findings
- `analysis/growth-story.md` — variant progression narrative
- `analysis/tables/variant-comparison.md` — per-variant metrics
- `analysis/figures/variant-radar.png` — radar chart
- `analysis/cards/*.md` — 6 per-item cards

**Gap**: All outputs are markdown. No LaTeX. No publication-quality tables or figures.

---

## What to Build

### Two new scripts + one LaTeX template

**`scripts/make_tables.py`** — Generate LaTeX tables from Parquet

Modeled on `~/tuvium/spring-ai-classification/scripts/make_tables.py` which uses `tabulate` with `latex_booktabs` format. Tables to generate:

1. **Variant comparison table** (`tables/variant-comparison.tex`)
   - Rows: variants (control, variant-a through variant-d)
   - Columns: pass rate, T3 practice adherence, golden similarity, coverage, cost
   - Color-code: best value per column in bold green, worst in red
   - Include standard deviation or range if we have multiple runs

2. **Per-item breakdown** (`tables/per-item-breakdown.tex`)
   - Rows: items (gs-rest-service, gs-accessing-data-jpa, etc.)
   - Columns: one per variant, showing T3 score
   - Highlights items where KB variants outperform (JPA, securing-web)

3. **Judge cascade results** (`tables/judge-cascade.tex`)
   - Rows: judge names (BuildSuccess, TestPreservation, CoverageImprovement, PracticeAdherence, GoldenTestComparison)
   - Columns: variants
   - Shows where each variant fails/passes in the cascade

4. **Cost analysis** (`tables/cost-analysis.tex`)
   - Per-variant: mean cost, tokens (input/output), duration
   - Variant-d (two-phase) vs single-phase cost comparison

**`scripts/make_figures.py`** — Generate publication-quality figures

Modeled on `~/tuvium/spring-ai-classification/scripts/make_figures.py` (300 DPI, serif fonts, tight bbox). Figures to generate:

1. **Variant radar chart** (`figures/variant-radar.pdf`) — already exists as PNG, upgrade to PDF with better styling
2. **Per-item bar chart** (`figures/per-item-bars.pdf`) — grouped bars, one group per item, one bar per variant
3. **Growth story chart** (`figures/growth-story.pdf`) — stacked or stepped chart showing how scores improve as levers are added (control → +structure → +KB → +deep KB → +two-phase)
4. **Cost vs quality scatter** (`figures/cost-quality.pdf`) — x=cost, y=T3 score, one point per variant, labeled

**`docs/latex/code-coverage-report.tex`** — LaTeX report

Modeled on `~/tuvium/projects/spring-ai-project-maint/docs/latex/spring-ai-v2-pruning.tex`. Structure:

```latex
\documentclass[11pt,a4paper]{article}
% booktabs, xcolor, colortbl, graphicx, float, hyperref

\title{Code Coverage Agent: Ablation Study\\
\large Testing knowledge + structured execution > model}
\author{Mark Pollack}
\date{March 2026}

\begin{document}
\maketitle

\begin{abstract}
We evaluate the effect of domain knowledge injection and structured
execution on AI-generated test quality for Spring Boot projects...
\end{abstract}

\tableofcontents

\section{Executive Summary}
% Key findings, variant comparison summary table

\section{Experimental Design}
% Task description, golden test set methodology, 5 variants
% Judge cascade (4 tiers)
% Split scoring: functional correctness + practice adherence

\section{Results: Getting Started Guides}
% Variant comparison table
% Per-item breakdown
% Growth story chart
% Honest: ceiling effect on simple tasks

\section{Results: Pet Clinic}
% [When available] The complex target
% Where knowledge separation should emerge

\section{Analysis}
% Cost vs quality
% Where KB helps (JPA, security) vs doesn't (simple REST)
% Two-phase overhead analysis
% Lever ordering (from experiment data)

\section{Discussion}
% Connection to Stripe convergence
% The three-layer model (BOM/Blueprint/Rules)
% When to invest in KB vs when model is sufficient
% Limitations and threats to validity

\section{Conclusion}
% Thesis equation + what the data shows
% Next steps (Pet Clinic, cross-model, passive activation)

\end{document}
```

---

## Reference Projects

| Project | Path | What to Copy |
|---------|------|-------------|
| spring-ai-project-maint | `~/tuvium/projects/spring-ai-project-maint/` | LaTeX report template, color-coded tables, article class structure |
| spring-ai-classification | `~/tuvium/spring-ai-classification/` | `make_tables.py` pattern (tabulate + latex_booktabs), `make_figures.py` pattern (300 DPI matplotlib), paper sections structure |
| code-coverage-experiment | (this project) | Existing DuckDB pipeline, Parquet data, markdown analysis |

Key files to reference:
- `~/tuvium/projects/spring-ai-project-maint/docs/latex/spring-ai-v2-pruning.tex` — report template
- `~/tuvium/spring-ai-classification/scripts/make_tables.py` — LaTeX table generation
- `~/tuvium/spring-ai-classification/scripts/make_figures.py` — figure generation
- `~/tuvium/spring-ai-classification/papers/02-classifier/latex/main.tex` — academic paper structure (for future escalation to conference submission)

---

## Pipeline

```
load_results.py (existing)     →  data/curated/*.parquet
    ↓
make_tables.py (new)           →  docs/latex/tables/*.tex
make_figures.py (new)          →  docs/latex/figures/*.pdf
    ↓
code-coverage-report.tex (new) →  \input{tables/...} \includegraphics{figures/...}
    ↓
pdflatex                       →  docs/latex/code-coverage-report.pdf
```

Add a `Makefile` or shell script:
```bash
#!/bin/bash
# scripts/build-report.sh
cd "$(dirname "$0")/.."
python scripts/load_results.py --session 20260304-045624 20260304-064326 20260304-112636
python scripts/make_tables.py
python scripts/make_figures.py
cd docs/latex && pdflatex code-coverage-report.tex && pdflatex code-coverage-report.tex
```

Two `pdflatex` passes for ToC + cross-references.

---

## Python Dependencies (add to requirements.txt or pyproject.toml)

```
duckdb          # already used
pandas          # already used
tabulate        # for latex_booktabs table generation
matplotlib      # already used (radar chart)
seaborn         # for styled figures (optional but nice)
```

---

## Sequencing

1. **Now**: Write `make_tables.py` — generates `.tex` files from existing Parquet data
2. **Now**: Write `make_figures.py` — upgrades existing PNG to publication-quality PDF
3. **Now**: Write `code-coverage-report.tex` skeleton with `\input{}` includes
4. **After Pet Clinic run**: Add Section 4 (Pet Clinic results)
5. **For Barcelona/JetBrains**: Escalate to conference format (ACM sigconf, from classification paper template)

The report should be buildable TODAY from existing sweep-001 data. Pet Clinic section is a placeholder until those results land.
