# TestQualityJudge Design Brief v4: Two-Layer Scoring

> **Status**: Proposed — ready for review
> **Supersedes**: Hardcoded 2-criteria design (meaningful assertions 50%, edge cases 50%)
> **Context**: Step 1.4 in `plans/ROADMAP.md`

---

## Problem

The previous design hardcoded two evaluation criteria with fixed weights:

- Meaningful assertions (0.5)
- Exception/edge-case coverage (0.5)

This has two failures:

1. **Control variant gets a free pass.** The control prompt (`v0-naive.txt`) gives vague instructions. An adaptive judge that only checks "did the agent follow its prompt" would bless garbage — tests using Java `assert` keyword, `assertTrue(true)`, no real coverage. This happened with Gemini in prior experiments.

2. **Knowledge variants get no credit for applying knowledge.** When `v2-with-kb.txt` provides `spring-test-slices.md` and the agent correctly uses `@WebMvcTest` instead of `@SpringBootTest`, the hardcoded criteria don't notice. The judge can't distinguish between a test that follows best practices and one that ignores the knowledge it was given.

---

## Proposed Design: Two-Layer Scoring

### Layer 1 — Universal Quality Floor (fixed, small)

A minimal set of signals that define "is this even a real test." Applied to ALL variants regardless of prompt or knowledge. These are the Tier 3 equivalent of "does it compile" (Tier 0).

| Signal | What it catches |
|--------|----------------|
| Uses a real assertion library (AssertJ, JUnit assertions, Hamcrest) — not Java `assert` keyword | Gemini-style garbage |
| Assertions test actual behavior — not `assertTrue(true)` or `assertNotNull(new Object())` | Vacuous tests |
| Test methods invoke production code | Tests that test nothing |

This is deliberately small. Three signals, not a rubric. Binary pass/fail per signal, contributes a floor score.

### Layer 2 — Adaptive Rubric (derived from prompt + knowledge)

The judge receives:
- The **prompt file** that was given to the agent (e.g., `v0-naive.txt` or `v2-with-kb.txt`)
- The **knowledge files** the agent had access to (e.g., `spring-test-slices.md`, `jacoco-patterns.md`)

The judge then operates in two phases:

**Phase 1 — Plan:** Read the prompt and knowledge files. Synthesize a ranked list of evaluation criteria specific to what this variant was told to do. This becomes an auditable artifact in the judge output.

- For control (`v0-naive.txt`, no knowledge): rubric is thin — maybe "tests exist and exercise the code"
- For variant-c (`v2-with-kb.txt`, 4 KB files): rubric includes "uses `@WebMvcTest` for controller tests", "verifies exception paths from `common-gaps.md`", "follows JaCoCo exclusion patterns", etc.

**Phase 2 — Evaluate:** Navigate the workspace (src/main + src/test), evaluate the generated tests against the rubric from Phase 1. Score each criterion 0.0–1.0.

### Score Computation

```
floor_score   = (signals_passed / total_signals)    # e.g., 3/3 = 1.0, 2/3 = 0.67
adaptive_score = weighted_avg(phase2_criteria)       # 0.0–1.0
final_score    = (floor_weight * floor_score) + (adaptive_weight * adaptive_score)
```

Suggested weights: floor 0.3, adaptive 0.7. The floor prevents garbage from scoring above ~0.3 even if the adaptive layer is lenient. The adaptive layer provides the gradient that differentiates variants.

### Expected Score Distribution

| Variant | Floor | Adaptive | Final | Pass (>0.5)? |
|---------|-------|----------|-------|--------------|
| control (bad output — `assert` keyword) | 0.0 | 0.2 | 0.14 | FAIL |
| control (decent output) | 1.0 | 0.3 | 0.51 | BORDERLINE |
| variant-a (hardened prompt, no KB) | 1.0 | 0.5 | 0.65 | PASS |
| variant-b (3 KB files) | 1.0 | 0.7 | 0.79 | PASS |
| variant-c (4 KB files) | 1.0 | 0.8 | 0.86 | PASS |

This creates the gradient the growth story needs — control scores low, knowledge variants score progressively higher.

---

## Implementation Approach

### Single Agent Call vs Two Calls

**Recommendation: single call.** The plan step and evaluate step share context (they both need to read the same files). A single agent call with a structured prompt ("First, derive your rubric from these inputs. Then, evaluate the code against it. Return both.") avoids the overhead of two agent invocations and keeps the rubric + evaluation coherent.

The JSON output includes both the derived rubric and the per-criterion scores, making the plan step auditable without requiring a separate call.

### What the Judge Receives

The `TestQualityJudge` constructor takes:
- Agent factory (functional interface — testability seam)
- Pass threshold (default 0.5)
- Floor weight (default 0.3)

The `judge()` method receives `JudgmentContext` which must include:
- Workspace path (src/main + src/test)
- Prompt file content (from `VariantSpec.promptFile`)
- Knowledge file contents (from `VariantSpec.knowledgeFiles`, may be empty)

### JSON Output Schema

```json
{
  "rubric": [
    { "criterion": "Uses AssertJ or JUnit assertions", "source": "floor" },
    { "criterion": "Uses @WebMvcTest for controller tests", "source": "knowledge:spring-test-slices.md" },
    { "criterion": "Tests exception paths for null inputs", "source": "prompt:v2-with-kb.txt" }
  ],
  "scores": [
    { "criterion": "Uses AssertJ or JUnit assertions", "score": 1.0, "evidence": "All test files use assertThat()" },
    { "criterion": "Uses @WebMvcTest for controller tests", "score": 0.8, "evidence": "2 of 3 controller tests use @WebMvcTest" },
    { "criterion": "Tests exception paths for null inputs", "score": 0.5, "evidence": "Only 1 of 3 services has null-input tests" }
  ],
  "summary": "Tests follow most knowledge-base practices but miss some edge case coverage"
}
```

---

## What Stays the Same

These decisions from earlier reviews are unchanged:

- Agent-based judge using `AgentClient`/`ClaudeAgentModel` (not `LLMJudge`)
- Read-only: `allowedTools(List.of("Read", "Glob", "Grep"))`, `yolo(false)`
- Stronger model for judging than experiment agent
- Copy workspace to temp dir for isolation
- No test files → `Judgment.fail()` score 0.0
- `NumericalScore.normalized()` for continuous 0–1 scoring
- Outermost `{...}` JSON extraction, score clamping to [0.0, 1.0]
- Functional interface for agent creation (testability seam)
- Exhaust capture via messageListener (resolved in Step 1.4a)

---

## Open Questions

1. **Floor weight (0.3) vs adaptive weight (0.7)** — are these the right proportions? Floor could be lower (0.2) if we trust the adaptive layer more.

2. **Should the floor signals be evaluated by the agent or by static analysis?** Static analysis (grep for `import org.assertj`, absence of bare `assert `) is faster and deterministic. Agent-based is more nuanced but adds cost.

3. **How does `JudgmentContext` get the prompt/knowledge content?** Options:
   - `JuryFactory` resolves file paths and passes content strings
   - Judge reads files itself given paths from `VariantSpec`
   - New field on `JudgmentContext` (may require upstream change to agent-judge-core)
