# Sweep 001: Getting Started Guides — Complete Experiment Report

**Date**: 2026-03-04
**Dataset**: 5 Spring Getting Started guides (bucket A — simple)
**Variants**: 5 (control, variant-a through variant-d)
**Model**: claude-sonnet-4-6 (all variants)
**Total data points**: 25 (5 variants × 5 items)
**Total cost**: ~$26.47

## Sessions Used

| Session | Variants Contributed | Notes |
|---------|---------------------|-------|
| 20260304-045624 | control, variant-a, variant-b | Main run (4 variants compiled, variant-d not yet in config) |
| 20260304-112636 | variant-c | Re-run to get golden similarity scores (stale binary in main run) |
| 20260304-064326 | variant-d | Separate run after two-phase invoker was compiled |

ETL command: `load_results.py --session 20260304-045624 --session 20260304-064326 --session 20260304-112636`

## Variant Definitions

| Variant | Prompt | Knowledge | Phase | Purpose |
|---------|--------|-----------|-------|---------|
| control | v0-naive.txt | none | single | Baseline — minimal instructions |
| variant-a | v1-hardened.txt | none | single | Prompt improvement — detailed testing guidance |
| variant-b | v2-with-kb.txt | 3 targeted KB files | single | Knowledge effect — curated subset |
| variant-c | v2-with-kb.txt | full KB tree (index.md) | single | Knowledge depth — entire knowledge base |
| variant-d | v3-explore.txt + v3-act.txt | full KB tree (index.md) | two-phase | Structured consumption — explore then act |

## Dataset Items

| Item | Description | Layers | Complexity |
|------|-------------|--------|------------|
| gs-rest-service | Single REST controller + record | 1 | Trivial |
| gs-accessing-data-jpa | Single JPA entity + repository | 1 | Trivial |
| gs-securing-web | MVC + Spring Security config | 1-2 | Simple |
| gs-reactive-rest-service | Reactive REST handler | 1 | Trivial |
| gs-messaging-stomp-websocket | WebSocket STOMP controller | 1 | Simple |

All items are single-layer, 1-3 production classes, Spring Boot 4.0.x, Maven.

## Summary Results

| Variant | Pass% | Avg Cov% | Avg T3 | Avg Golden | Avg Eff | Total Cost | Phase |
|---------|-------|----------|--------|------------|---------|------------|-------|
| control | 80% | 85.7 | 0.61 | 0.62 | 0.83 | $4.22 | 1ph |
| variant-a | 100% | 84.2 | 0.71 | 0.66 | 0.94 | $4.06 | 1ph |
| variant-b | 100% | 95.6 | 0.76 | 0.75 | 0.93 | $4.67 | 1ph |
| variant-c | 100% | 84.9 | 0.75 | 0.68 | 0.85 | $5.13 | 1ph |
| variant-d | 100% | 94.1 | 0.70 | 0.66 | 0.75 | $8.39 | 2ph |

*Note: Scores rounded to 2 decimal places. At N=1 per item-variant cell, differences of ~0.05 are indistinguishable from noise.*

## High-Confidence Findings

### 1. A hardened prompt is the single biggest lever

Control (naive prompt) fails 1 of 5 items (80% pass rate). Every other variant passes 100%. The control also has the lowest T3 practice adherence (0.61) and lowest golden similarity (0.62).

**Implication**: On simple projects, a well-crafted prompt is the dominant factor. The jump from control to variant-a is the largest measurable improvement in the experiment.

### 2. All improved variants perform similarly on simple guides

T3 adherence across variant-a through variant-d ranges from 0.70 to 0.76. Golden similarity ranges from 0.66 to 0.75. At this sample size with LLM-based judges, these differences are not reliably separable from noise.

**Implication**: Knowledge injection and two-phase execution do not measurably improve outcomes when the target project is trivially simple. The model already "knows" how to test a single REST controller.

### 3. Two-phase execution costs 2x with no measurable benefit here

Variant-d ($8.39) costs roughly double any single-phase variant ($4-5). Its T3 (0.70) and golden (0.66) scores are in the same range as variant-a (0.71, 0.66) which uses no knowledge at all.

**Implication**: The explore-then-act pattern adds overhead that isn't justified when the project can be understood in seconds. The hypothesis is that this overhead pays off on larger, multi-layer projects where upfront planning matters.

### 4. Coverage is a ceiling, not a differentiator

Three of five items show identical coverage across all variants:
- gs-accessing-data-jpa: 94.6% everywhere
- gs-securing-web: 91.3% everywhere
- gs-messaging-stomp-websocket: 85-92% (small variance)

Only gs-rest-service and gs-reactive-rest-service show any coverage variation (71-100%), and even there, it's binary — either the agent covered the gap or it didn't.

**Implication**: Coverage percentage is not a useful metric for comparing variants on simple projects. The coverage ceiling is reached too easily.

### 5. Per-item variance is high — no variant consistently dominates

Looking at T3 per item:
- gs-messaging-stomp-websocket: variant-a wins (0.65 vs 0.45-0.55 for others)
- gs-reactive-rest-service: variant-c wins (0.90 vs 0.73-0.82)
- gs-rest-service: variant-b, c, d tied (0.88)
- gs-securing-web: variant-b wins (0.83 vs 0.67-0.78)

No single variant wins on all items. This is consistent with stochastic variation at N=1 rather than a systematic advantage.

### 6. Golden similarity shows a possible KB signal on two items

- gs-accessing-data-jpa: variant-b and variant-c both score 0.88 golden vs 0.62-0.74 for others
- gs-securing-web: variant-b and variant-c both score 1.0 golden vs 0.70-0.92 for others

These are the two items with the most testing structure in their golden reference tests. The KB variants may be producing tests that more closely resemble expert-written tests — but N=1 means this needs validation on more data.

## Scoring Instrument Assessment

### T3 Practice Adherence (LLM judge, 6 criteria)
- Range: 0.45 to 0.90 across all cells
- Useful spread but noisy at N=1
- Clusters around 0.65-0.85 for improved variants — moderate discrimination

### Golden Test Similarity (AST-based, 5 weighted dimensions)
- Range: 0.36 to 1.0 across all cells
- Wider spread than T3 — more discriminating
- Structural comparison is deterministic (not LLM-based), so variance is from agent behavior, not judge noise

### Coverage (JaCoCo line coverage)
- Range: 71-100%
- Ceiling effect on simple guides — not useful for variant comparison
- May be more discriminating on complex projects (Pet Clinic)

### Efficiency (4 weighted metrics: build errors, tool use, cost, recovery cycles)
- Range: 0.50 to 0.97
- Variant-d consistently lower due to cost component (two phases)
- Useful for cost-quality tradeoff analysis

## Cost Breakdown

| Variant | Total | Per Item Avg | Agent Cost | Judge Cost (est.) |
|---------|-------|-------------|------------|-------------------|
| control | $4.22 | $0.84 | ~$0.60 | ~$0.25 |
| variant-a | $4.06 | $0.81 | ~$0.55 | ~$0.25 |
| variant-b | $4.67 | $0.93 | ~$0.70 | ~$0.25 |
| variant-c | $5.13 | $1.03 | ~$0.75 | ~$0.25 |
| variant-d | $8.39 | $1.68 | ~$1.40 | ~$0.25 |

*Judge cost estimated from T3 judge (Sonnet-based agent) at ~$0.10-0.25 per item. Remaining cost is the agent itself.*

Variant-d's higher cost is entirely from the agent side (two Sonnet invocations per item).

## Limitations

1. **N=1 per cell**: Every score is a single observation. No statistical power to distinguish variants within the 0.05-0.10 range.
2. **Simple dataset**: All items are single-layer, 1-3 class projects. This is deliberately below the complexity where knowledge injection should matter.
3. **Same model**: All variants use claude-sonnet-4-6. Cross-model comparison (Haiku+KB vs Sonnet) not yet tested.
4. **Stale binary issue**: Variant-c golden scores came from a re-run on a different binary than the other variants. The variant-c session used a fresh compile while control/variant-a/variant-b ran on the earlier binary.
5. **No repeated trials**: Stochastic variation in LLM outputs means a single run may not represent typical behavior for any variant.

## Hypotheses for Next Sweep (Pet Clinic)

1. **KB advantage should emerge on complex targets**: Pet Clinic has controllers, services, repositories, entities, validation, form handling. The agent can't figure all of this out from the prompt alone.
2. **Two-phase should help on complex targets**: Exploring a 15+ class project before writing tests should produce better test plans than diving in immediately.
3. **Coverage should be more discriminating**: Pet Clinic won't hit 90%+ by accident — there's real complexity to cover.
4. **Golden similarity should spread**: Pet Clinic has 17 reference test files (59 tests) vs 1 reference file per guide. More structure to compare against.
5. **Variant ranking may change**: If variant-b beats variant-a on Pet Clinic but not on simple guides, that validates the knowledge injection thesis.

## Artifacts Produced

- `data/curated/runs.parquet` — 5 rows (one per variant)
- `data/curated/item_results.parquet` — 25 rows (5 × 5)
- `data/curated/judge_details.parquet` — 350 rows
- `analysis/tables/variant-comparison.md` — summary + per-item pivot tables
- `analysis/figures/variant-radar.png` — radar chart
- `analysis/cards/*.md` — 5 per-item detail cards

## Next Steps

1. Run Pet Clinic sweep (all 5 variants × 1 item) — test thesis on harder target
2. Compare variant ranking between sweeps
3. Use DiagnosticAnalyzer gap categories to identify failure modes on Pet Clinic
4. If KB_GAP dominates: add Pet Clinic-specific knowledge, re-run, measure improvement
