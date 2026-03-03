# Task: Author the Judge Rubric

> **Source**: Research partner session, 2026-03-02
> **Depends on**: `pre-flight-review-findings.md` (Finding 1: split scoring, practice adherence framing)
> **Output**: `prompts/judge-practice-adherence.txt` + `prompts/judge-practice-adherence-traceability.md`

---

## What to do

Read the entire knowledge base — all 13 files under `knowledge/` (start with `knowledge/index.md`, then read every file it references). Distill these into a fixed evaluation rubric that an LLM judge will use to score test suites.

## Context

This rubric is applied **identically to all 4 experiment variants** — including the control which has no KB access. It measures whether a test suite follows prescribed Spring testing practices. It does NOT measure functional correctness (compile/pass/coverage are handled by separate deterministic judges).

The rubric must be a **frozen artifact** — the judge gets this prompt + read-only access to the workspace (`src/main/`, `src/test/`, `pom.xml`). It does NOT read the knowledge base at runtime.

## Output format

Write `prompts/judge-practice-adherence.txt` with this structure:

```
You are evaluating the practice adherence of a JUnit test suite for a Spring Boot project.

First, read pom.xml to determine the Spring Boot version (Boot 3.x vs 4.x).
Then navigate src/main/ to understand the production code architecture.
Then navigate src/test/ to evaluate the test suite.

Score the test suite on these criteria (0.0–1.0 each):

1. TEST SLICE SELECTION
   [When to score high vs low — distilled from spring-test-slices.md and cross-cutting-testing-patterns.md]

2. ASSERTION QUALITY
   [When to score high vs low — distilled from assertj-mockito-idioms.md]

3. ...additional criteria...

N. VERSION-AWARE PATTERNS
   [When to score high vs low — distilled from Boot 3→4 migration sections across all cheatsheets]

Return JSON only:
{
  "boot_version": "3.x or 4.x",
  "criteria": [
    { "name": "...", "score": 0.0, "evidence": "specific code reference" },
    ...
  ]
}
```

## Guidelines for criteria selection

- **Derive criteria from the KB files** — every criterion should trace to specific guidance in one or more KB files. This is intentional, not a bug (see `pre-flight-review-findings.md` Finding 1).
- **Frame as "practice adherence"** not "quality" — the rubric checks whether tests follow prescribed Spring testing practices.
- **Include concrete anchors** for scoring: what does a 0.2 look like vs a 0.8? Use real examples (e.g., "0.2: uses `@SpringBootTest` for a controller-only test; 0.8: uses `@WebMvcTest` with focused component scan").
- **Prefer criteria that are observable in code** — the judge has file access, not runtime access. It can see annotations, assertion patterns, imports, config. It cannot run tests.
- **Keep to 5-7 criteria** — enough to cover the KB's main concerns, few enough for consistent scoring. Too many dilutes signal.
- **Version awareness should be a separate criterion** — it's a key differentiator for the experiment story (models don't know Boot 4 shipped; the KB does).
- **Equal weight** across criteria unless you have a strong reason otherwise — simpler to explain, easier to interpret.
- **Don't include criteria the KB doesn't address** — if the KB has nothing to say about performance testing or mutation testing, don't add those criteria. The rubric should reflect what the KB teaches.

## What NOT to include in the rubric

- Functional correctness (compilation, test passing, coverage %) — handled by deterministic judges
- Style preferences that aren't in the KB (formatting, naming conventions)
- Criteria that require running the tests (execution time, flakiness)

## After writing the rubric

Add a companion file `prompts/judge-practice-adherence-traceability.md` that maps each criterion back to its source KB file(s). This documents the derivation chain for later review.
