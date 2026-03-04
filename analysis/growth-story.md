# Growth Story

> Generated: 2026-03-04T04:42:44.980161229Z

## Variant Progression

### control (Baseline)

| Metric | Value |
|--------|-------|
| Pass Rate | 100.0% |
| Total Cost | $0.7664 |
| Total Tokens | 8,645 |
| Duration | 250s |

**Scores:**

| Judge | Mean Score |
|-------|------------|
| efficiency.recoveryCycles | 0.750 |
| CommandJudge | 1.000 |
| efficiency.cost | 0.847 |
| Judge#1 | 0.683 |
| GoldenTestComparisonJudge | 0.500 |
| efficiency.composite | 0.776 |
| CoverageImprovementJudge | 1.000 |
| efficiency.buildErrors | 0.750 |
| CoveragePreservationJudge | 1.000 |

### variant-a (vs previous)

| Judge | Current | Baseline | Delta | Improved | Regressed |
|-------|---------|----------|-------|----------|----------|
| efficiency.recoveryCycles | 0.875 | 0.750 | +0.125 | 1 | 0 |
| CommandJudge | 1.000 | 1.000 | +0.000 | 0 | 0 |
| efficiency.cost | 0.855 | 0.847 | +0.008 | 1 | 0 |
| Judge#1 | 0.900 | 0.683 | +0.217 | 1 | 0 |
| GoldenTestComparisonJudge | 0.360 | 0.500 | -0.140 | 0 | 1 |
| efficiency.composite | 0.870 | 0.776 | +0.094 | 1 | 0 |
| CoverageImprovementJudge | 1.000 | 1.000 | +0.000 | 0 | 0 |
| efficiency.buildErrors | 0.875 | 0.750 | +0.125 | 1 | 0 |
| CoveragePreservationJudge | 1.000 | 1.000 | +0.000 | 0 | 0 |

Pass rate: 100.0% | Cost: $0.7243 | Tokens: 9,239

### variant-b (vs previous)

| Judge | Current | Baseline | Delta | Improved | Regressed |
|-------|---------|----------|-------|----------|----------|
| efficiency.recoveryCycles | 1.000 | 0.875 | +0.125 | 1 | 0 |
| CommandJudge | 1.000 | 1.000 | +0.000 | 0 | 0 |
| efficiency.cost | 0.849 | 0.855 | -0.006 | 0 | 1 |
| Judge#1 | 0.850 | 0.900 | -0.050 | 0 | 1 |
| GoldenTestComparisonJudge | 0.500 | 0.360 | +0.140 | 1 | 0 |
| efficiency.composite | 0.960 | 0.870 | +0.090 | 1 | 0 |
| CoverageImprovementJudge | 1.000 | 1.000 | +0.000 | 0 | 0 |
| efficiency.buildErrors | 1.000 | 0.875 | +0.125 | 1 | 0 |
| CoveragePreservationJudge | 1.000 | 1.000 | +0.000 | 0 | 0 |

Pass rate: 100.0% | Cost: $0.7555 | Tokens: 8,511

### variant-c (vs previous)

| Judge | Current | Baseline | Delta | Improved | Regressed |
|-------|---------|----------|-------|----------|----------|
| efficiency.recoveryCycles | 1.000 | 1.000 | +0.000 | 0 | 0 |
| CommandJudge | 1.000 | 1.000 | +0.000 | 0 | 0 |
| efficiency.cost | 0.848 | 0.849 | -0.001 | 0 | 1 |
| Judge#1 | 0.850 | 0.850 | +0.000 | 0 | 0 |
| GoldenTestComparisonJudge | 0.360 | 0.500 | -0.140 | 0 | 1 |
| efficiency.composite | 0.960 | 0.960 | -0.000 | 0 | 1 |
| CoverageImprovementJudge | 1.000 | 1.000 | +0.000 | 0 | 0 |
| efficiency.buildErrors | 1.000 | 1.000 | +0.000 | 0 | 0 |
| CoveragePreservationJudge | 1.000 | 1.000 | +0.000 | 0 | 0 |

Pass rate: 100.0% | Cost: $0.7583 | Tokens: 7,123

### variant-d (vs previous)

| Judge | Current | Baseline | Delta | Improved | Regressed |
|-------|---------|----------|-------|----------|----------|
| efficiency.recoveryCycles | 0.625 | 1.000 | -0.375 | 0 | 1 |
| CommandJudge | 1.000 | 1.000 | +0.000 | 0 | 0 |
| efficiency.cost | 0.652 | 0.848 | -0.197 | 0 | 1 |
| Judge#1 | 0.867 | 0.850 | +0.017 | 1 | 0 |
| GoldenTestComparisonJudge | 0.523 | 0.360 | +0.163 | 1 | 0 |
| efficiency.composite | 0.632 | 0.960 | -0.327 | 0 | 1 |
| CoverageImprovementJudge | 1.000 | 1.000 | +0.000 | 0 | 0 |
| efficiency.buildErrors | 0.625 | 1.000 | -0.375 | 0 | 1 |
| CoveragePreservationJudge | 1.000 | 1.000 | +0.000 | 0 | 0 |

Pass rate: 100.0% | Cost: $1.7414 | Tokens: 15,235

## Analysis

_TODO: Add analysis of what drove improvements across variants._
