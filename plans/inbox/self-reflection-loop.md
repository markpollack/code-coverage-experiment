# Brief: Self-Reflection Loop — Learn from Judge Verdicts

## Motivation

Judge verdicts contain criterion-level scores + evidence text that identify specific instruction-following failures (e.g., "Used MockMvc on Boot 4+ instead of RestTestClient"). Today these are observed post-hoc. A self-reflection loop would extract recurring low-scoring patterns and inject them as prompt patches for future runs.

## Design

```
Run N  →  Judge Verdicts  →  Reflection Extractor  →  lessons.yaml  →  Prompt Patch  →  Run N+1
```

### Step 1: Extract actionable patterns

Query `judge_details.parquet` for criteria scoring below threshold (e.g., < 0.7):

```sql
SELECT criterion_name, score, evidence, variant, item_slug
FROM judge_details j
JOIN item_results r ON j.run_id = r.run_id AND j.item_slug = r.item_slug
WHERE score < 0.7
ORDER BY criterion_name, score
```

Group by `criterion_name` to find recurring failures across items/variants.

### Step 2: Generate lessons.yaml

Structured file keyed by criterion, with extracted patterns:

```yaml
lessons:
  - criterion: test_slice_selection
    pattern: "Used @SpringBootTest for controller tests"
    fix: "Use @WebMvcTest for controller-only tests, @DataJpaTest for repository tests"
    seen_in: [loopy-haiku/gs-rest-service, control/gs-accessing-data-jpa]

  - criterion: version_aware_patterns
    pattern: "Used MockMvc on Boot 4+ project"
    fix: "Boot 4+ projects should use RestTestClient, not MockMvc"
    seen_in: [variant-a/gs-rest-service]
```

### Step 3: Inject into prompt at invocation time

`AbstractCoverageAgentInvoker.buildPrompt()` reads `lessons.yaml` and appends a "Known Pitfalls" section:

```
## Known Pitfalls (from prior runs)
- Boot 4+ projects: Use RestTestClient with @AutoConfigureRestTestClient, NOT MockMvc
- Use @WebMvcTest for controller tests, not @SpringBootTest
- Include at least one error/negative test per endpoint
```

### Step 4: Track effectiveness

New variant dimension: `variant-a-reflected` vs `variant-a`. Compare criterion scores before/after to measure whether reflection helps.

## Implementation phases

1. **Manual**: Script to extract low-scoring criteria, human curates into lessons.yaml
2. **Semi-auto**: Script generates candidate lessons, human approves/edits
3. **Auto**: LLM summarizes judge evidence into actionable prompt patches (use T3 judge's own evidence text as input)

## Also fix

The gs-rest-service **golden test reference** uses `@SpringBootTest` instead of `@WebMvcTest` — it penalizes agents that correctly follow best practices. Update the golden to use Boot 4 idioms (`@WebMvcTest` + `RestTestClient`).

## Dependencies

- `judge_details.parquet` with criterion-level scores (already available)
- `lessons.yaml` format and loader (new)
- Prompt injection point in `AbstractCoverageAgentInvoker.buildPrompt()` (small change)
