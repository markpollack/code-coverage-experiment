# Handoff: Golden Test Comparison Judge + Remaining Work

> Written from research-conversation-agent session, 2026-03-03. Pick up in code-coverage-experiment agent session.

## What Was Done (This Session)

### GoldenTestComparisonJudge — Implemented and Passing

A new deterministic judge that compares agent-written tests against reference golden tests using JavaParser AST analysis. This is the SWE-bench dimension — gold patch comparison that makes results externally credible.

**Files created/modified:**

| File | Action |
|------|--------|
| `pom.xml` | Added `com.github.javaparser:javaparser-core:3.26.3` |
| `src/main/java/.../GoldenTestComparisonJudge.java` | **NEW** (~270 lines) |
| `src/test/java/.../GoldenTestComparisonJudgeTest.java` | **NEW** (13 tests) |
| `src/main/java/.../ExperimentApp.java` | Added `new GoldenTestComparisonJudge()` to tier 2 (line 204) |

**Test count**: 34 pass (was 21, added 13).

### How It Works

Parses both agent and reference test files into ASTs, extracts 5 structural dimensions, compares each:

| Dimension | Weight | Metric |
|-----------|--------|--------|
| `test_method_coverage` | 0.20 | `min(agent_count / ref_count, 1.0)` |
| `annotation_alignment` | 0.25 | Jaccard similarity of Spring test annotations |
| `import_alignment` | 0.20 | Jaccard similarity of Spring/test imports |
| `assertion_style` | 0.20 | Count ratio × style overlap |
| `injection_pattern` | 0.15 | Jaccard similarity of injected types |

Returns composite `NumericalScore` in [0.0, 1.0]. ABSTAIN if no reference dir. FAIL(0.0) if no agent tests. Regex fallback for unparseable files (proven pattern).

### Design Decision: Tier 2 Policy

Kept `REJECT_ON_ANY_FAIL` (plan suggested `ACCEPT_ON_ALL_PASS`). Reason: `ACCEPT_ON_ALL_PASS` would cause tier 3 (TestQualityJudge) to be skipped whenever tier 2 passes — that's wrong, we always want practice adherence scores.

With `REJECT_ON_ANY_FAIL`: if either CoverageImprovement or GoldenTestComparison FAILs → cascade rejects. If both pass/abstain → escalates to tier 3 as expected. GoldenTestComparison ABSTAINs gracefully when no reference dir exists.

### How Reference Dir Flows Through the Pipeline

Already fully wired (no upstream changes needed):
1. `materialize.sh` preserves golden tests in `dataset/items/{id}/reference/src/test/`
2. `FileSystemDatasetManager` resolves `reference/` as `ResolvedItem.referenceDir()`
3. `ExperimentRunner.runItem()` passes `referenceDir` to `JudgmentContextFactory.create()`
4. `JudgmentContextFactory` stores it as `metadata("expectedDir", referenceDir)`
5. `GoldenTestComparisonJudge` reads `context.metadata().get("expectedDir")`

---

## What Still Needs to Be Done

### Immediate (Step 2.2c Completion)

- [ ] Add Step 2.2c to `plans/ROADMAP.md` (between Step 2.2b and Step 2.2)
- [ ] Update `CLAUDE.md` — add GoldenTestComparisonJudge to the 4-tier jury table (now 5 judges across 4 tiers), update "Current state" line
- [ ] Write `plans/learnings/step-2.2c-golden-judge.md`
- [ ] COMMIT all changes

### Step 2.2b Completion (Exhaust Capture Smoke Test)

Step 2.2b code is complete but exit criteria are NOT met:
- [ ] SMOKE TEST: `--variant control --item gs-rest-service` — verify phases non-empty in results JSON
- [ ] Write: `plans/learnings/step-2.2b-exhaust-capture.md` (exists but may need update after smoke test)
- [ ] Update ROADMAP checkboxes
- [ ] COMMIT

### Step 2.2: Re-run Control with Exhaust Capture

Prior runs (3/5 pass for control, 2/5 for variant-a) have zero exhaust data. Can't diagnose failures. Need full re-run with exhaust capture wired.

### Step 2.3: Run All Variants

Run all 4 variants, generate growth story. This is where GoldenTestComparison scores first appear in real results.

### Stage 3: Data Analysis Pipeline

Full plan is in `plans/inbox/python-data-analysis-stack.md` and already captured in ROADMAP.md Steps 3.0-3.4. Key sequence:

1. **Step 3.0: Data Audit** — audit all result JSON files for completeness (phases, efficiency, tokens). Decide re-run vs exclude for incomplete data.
2. **Step 3.1: Python ETL** — `uv venv`, DuckDB + pandas + matplotlib. `scripts/load_results.py` → parquet files. Follow `spring-ai-project-maint` pattern.
3. **Step 3.2: Variant Comparison** — core ablation analysis, thesis queries (Q1-Q5), radar charts, cost-vs-quality plots.
4. **Step 3.3: Growth Story + Sensitivity** — iteration trajectory, weight sweep, per-item cards.
5. **Step 3.4: Consolidation** — findings summary, compacted learnings.

**GoldenTestComparison adds a new column to the analysis**: `golden_similarity` alongside `coverage_delta`, `adherence_score`, `efficiency_composite`. The DuckDB schema in `python-data-analysis-stack.md` needs updating to include golden comparison scores. This is the measurement that tells you whether knowledge injection steers agents toward expert-like patterns (higher golden similarity) or just toward passing tests (high coverage but different structure).

### Stage 4: Graduation

Extract best variant → standalone agent project.

---

## Current State of Results Data

```
results/code-coverage-experiment/
├── control/     — 12 item runs (some pre-exhaust, some post)
├── variant-a/   — multiple item runs
├── variant-b/   — multiple item runs
├── variant-c/   — multiple item runs
└── index.json per variant
```

Known data quality issues (per ROADMAP Step 3.0):
- Early control/variant-a runs have zero phases, zero tokens, zero cost (pre-exhaust-capture)
- Efficiency scores only present in runs after DefaultEfficiencyEvaluator was wired
- Step 3.0 audit script will quantify exactly what's usable

---

## Key Reference Paths

| What | Path |
|------|------|
| ROADMAP (source of truth) | `plans/ROADMAP.md` |
| CLAUDE.md | `CLAUDE.md` |
| Learnings (compacted) | `plans/learnings/LEARNINGS.md` |
| Python analysis plan | `plans/inbox/python-data-analysis-stack.md` |
| spring-ai-project-maint (reference for analysis pattern) | `/home/mark/tuvium/projects/spring-ai-project-maint/` |
| GoldenTestComparisonJudge | `src/main/java/.../GoldenTestComparisonJudge.java` |
| GoldenTestComparisonJudgeTest | `src/test/java/.../GoldenTestComparisonJudgeTest.java` |
| Judge rubric | `prompts/judge-practice-adherence.txt` |
| Experiment config | `experiment-config.yaml` |

## Suggested First Action

1. Read this handoff
2. Run `./mvnw test` to verify 34 tests pass
3. Complete Step 2.2c exit criteria (ROADMAP update, CLAUDE.md update, learnings file, commit)
4. Then proceed to Step 2.2b smoke test → Step 2.2 → Step 2.3 → Stage 3
