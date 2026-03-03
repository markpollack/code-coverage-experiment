# Step 2.2a: Dry-run Pipeline Validation

## Date: 2026-03-02

## What was done

Fixed 3 critical plumbing issues that would have caused coverage judges to abstain instead of scoring:

### Issue 1: JudgmentContextFactory metadata pass-through (experiment-core)
- `JudgmentContextFactory.create()` did NOT forward `InvocationResult.metadata()` to `JudgmentContext`
- Coverage metrics stored by invoker (`baselineCoverage`, `finalCoverage`) never reached judges
- **Fix**: Added iteration over `invocationResult.metadata()` entries, adding each to the builder before `build()`
- String values from `Map<String, String>` pass through as `Object` in `Map<String, Object>` — no conversion needed

### Issue 2: Coverage judges only accepted CoverageMetrics objects (agent-judge-exec)
- `CoveragePreservationJudge` and `CoverageImprovementJudge` both did `instanceof CoverageMetrics` checks
- `CodeCoverageAgentInvoker` stores `String.valueOf(baseline.lineCoverage())` — a double-as-string
- Even with metadata pass-through, `instanceof CoverageMetrics` would fail → abstain
- **Fix**: Added String fallback in both judges — parse as double, construct minimal `CoverageMetrics(lineCoverage, 0.0, 0.0, 0, 0, 0, 0, 0, 0, "from-metadata")`
- Backward compatible — `CoverageMetrics` instances still work via the original path

### Issue 3: No --item CLI filter for smoke testing
- Added `--item <slug>` CLI argument to `ExperimentApp` for single-item runs
- Implemented `SlugFilteringDatasetManager` wrapper that delegates to real `DatasetManager` but filters items by slug
- `ExperimentVariantConfig` gained `itemSlugFilter` field and `withItemFilter(slug)` method

## Key decisions

- **String fallback, not type change**: Instead of changing the invoker to store `CoverageMetrics` objects (which would require the invoker to serialize/deserialize complex objects through a `Map<String, String>`), added String parsing to the judges. Simpler, backward compatible.
- **Decorator over upstream change**: `SlugFilteringDatasetManager` wraps the dataset manager rather than adding slug filtering to `ItemFilter` upstream. Keeps the change local to this project.

## Upstream changes made (installed locally)

| Repo | File | Change |
|------|------|--------|
| tuvium-experiment-driver | `experiment-core/.../JudgmentContextFactory.java` | Forward `invocationResult.metadata()` to JudgmentContext |
| agent-judge | `agent-judge-exec/.../CoveragePreservationJudge.java` | Accept String baseline (parse as double) |
| agent-judge | `agent-judge-exec/.../CoverageImprovementJudge.java` | Accept String baseline (parse as double) |

## Verification

- `./mvnw compile` — passes
- `./mvnw test` — 17 tests pass
- Upstream installs: `experiment-core` and `agent-judge-exec` installed to local `.m2`
