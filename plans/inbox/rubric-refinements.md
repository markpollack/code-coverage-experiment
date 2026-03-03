# Task: Rubric Refinements for judge-practice-adherence.txt

> **Source**: Research partner review, 2026-03-02
> **Target**: `prompts/judge-practice-adherence.txt`
> **Priority**: Do before first run — prevents ambiguous judge output

---

## Fix 1: Zero-tests escape hatch

Add after the existing "Important" section at the bottom:

> If src/test/ contains no test classes, return all scores as 0.0 with evidence "no test classes found" for each criterion.

The `TestQualityJudge` Java code should catch this case before invoking the judge (v5 design says `Judgment.fail()` with score 0.0 when no test files exist). But if the judge prompt is ever invoked on an empty test suite, it needs a defined behavior rather than hallucinating scores.

## Fix 2: Criterion 4 — explicit N/A for absent domains

Criterion 4 (DOMAIN-SPECIFIC TEST PATTERNS) has 5 domain sub-sections (JPA, MVC, WebFlux, Security, WebSocket). On most Getting Started guides, only 1-2 domains will be present.

Add guidance inside criterion 4, after the WebSocket sub-section and before the scoring anchors:

> If a domain is not present in the production code (e.g., no WebFlux controllers, no security configuration), mark that domain as "N/A" in the evidence and score based only on domains that are present.

This prevents the judge from averaging across sub-sections it can't meaningfully score, and makes downstream analysis cleaner — "scored low" vs "not applicable" are different signals.

## Fix 3: Evidence field guidance for multi-file citations

The `evidence` field is a single string. For criteria that span multiple files (especially criterion 4), the judge may need to cite several test classes.

Add to the "Important" section at the bottom:

> Evidence may reference multiple files — separate with semicolons (e.g., "GreetingControllerTest.java uses @WebMvcTest correctly; OrderRepositoryTest.java uses @SpringBootTest instead of @DataJpaTest").

## Fix 4: No composite score in JSON — confirm this is intentional

The rubric says equal weight but does not ask the judge to compute an average. This is correct — per the pre-flight review (Finding 1), functional and adherence scores should not be combined. The `TestQualityJudge` Java code computes any aggregation it needs from the 6 individual scores.

**No change needed to the rubric.** But confirm the `TestQualityJudge` implementation expects an array of 6 criterion scores without a rolled-up total.

## Fix 5: Update traceability doc

After editing the rubric, update `prompts/judge-practice-adherence-traceability.md` to note the refinements (zero-tests handling, N/A guidance, evidence format). A one-line note at the top is sufficient:

> **Refined 2026-03-02**: Added zero-tests escape hatch, N/A guidance for criterion 4, multi-file evidence format.
