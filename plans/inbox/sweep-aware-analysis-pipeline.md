# Design Brief: Sweep-Aware Analysis Pipeline

## Context

The experiment-driver is adding Sweep support (grouping sessions into logical experiment runs). The analysis pipeline needs to be sweep-aware so we can compare results across sweeps (e.g., "getting-started guides" vs "pet clinic" vs "mixed dataset").

## Current State

Four scripts run sequentially, all reading from / writing to hardcoded paths:

```
scripts/load_results.py         → data/curated/*.parquet
scripts/variant_comparison.py   → analysis/tables/variant-comparison.md
scripts/plot_variant_radar.py   → analysis/figures/variant-radar.png
scripts/generate_item_cards.py  → analysis/cards/{slug}.md
```

Each sweep overwrites the previous outputs. No way to retain or compare.

## Proposed Changes

### 1. Sweep-namespaced outputs

```
data/curated/{sweep-name}/              # parquet per sweep
analysis/{sweep-name}/tables/           # comparison tables
analysis/{sweep-name}/figures/          # charts
analysis/{sweep-name}/cards/            # per-item cards
analysis/cross-sweep/                   # cross-sweep comparison outputs
```

### 2. Add `--sweep` parameter to all scripts

- `load_results.py --sweep gs-guides-v1 --session s1 --session s2`
- `variant_comparison.py --sweep gs-guides-v1`
- `plot_variant_radar.py --sweep gs-guides-v1`
- `generate_item_cards.py --sweep gs-guides-v1`

### 3. Single entry point

`analyze.py --sweep gs-guides-v1 --session s1 --session s2` runs the full pipeline.

### 4. Cross-sweep comparison script

`cross_sweep_comparison.py --sweeps gs-guides-v1 petclinic-v1` produces:
- Side-by-side variant ranking (did the same variant win on both datasets?)
- Per-variant delta (does variant-b's advantage grow on harder targets?)
- Cost comparison across datasets
- Coverage ceiling analysis (are harder targets more discriminating?)

### 5. Statistical summary

Flag scores that are indistinguishable at the current sample size. Round to 1 decimal place for presentation. Group variants into "tiers" rather than precise rankings.

## Dependencies

- Sweep concept in experiment-driver (in progress)
- Second sweep (Pet Clinic) to motivate cross-sweep comparison

## Action Items

- [ ] Add `--sweep` parameter to all 4 scripts
- [ ] Create `analyze.py` single entry point
- [ ] Create `cross_sweep_comparison.py`
- [ ] Add statistical tier grouping (avoid false precision)
- [ ] Test with getting-started + pet clinic sweeps
