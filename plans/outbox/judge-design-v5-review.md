# TestQualityJudge Design Brief v5 — Final Review

> **Status**: Proposed — requesting final review before implementation
> **Context**: Step 1.4 in the code-coverage-experiment ROADMAP
> **Reviewer context**: You have reviewed v1–v4 of this design. v4 introduced the fixed quality bar. This brief resolves remaining ambiguity about how the judge prompt relates to the knowledge base.

---

## The Experiment (30-second recap)

We run 4 variants of a coverage agent against 5 Spring Boot Getting Started guides (4 on Boot 4.x, 1 on Boot 3.x). Each variant changes one variable:

| Variant | What changes | What it measures |
|---------|-------------|-----------------|
| control | Naive prompt, no KB | LLM baseline |
| variant-a | Hardened prompt, no KB | Prompt engineering effect |
| variant-b | + coverage-mechanics KB (3 files, read upfront) | Basic knowledge injection |
| variant-c | + full Spring testing KB (8 files, JIT navigation via routing tables) | Rich domain knowledge |

The thesis: **knowledge + orchestration > model**. The growth story shows what each lever contributes.

---

## The Judge Design

### What it is

A single static prompt file (`prompts/judge-quality.txt`) that defines what good Spring Boot tests look like. Applied identically to all 4 variants. The judge agent gets this prompt + the workspace to evaluate. That's it.

### How the prompt is authored

A human reads the full knowledge base (coverage-mechanics/ + spring-testing/) and distills the best practices into concrete evaluation criteria with scoring rubrics. The prompt is then a **frozen artifact** — it does not change between runs.

### What the judge does NOT do

- Does NOT read the KB at runtime
- Does NOT adapt criteria per variant
- Does NOT know which variant produced the code it's evaluating
- Does NOT navigate files to discover what "good" means — it already knows, because the criteria are baked into the prompt

### Why static, not runtime KB navigation

We considered having the judge navigate the KB at runtime (read `knowledge/index.md`, build its own understanding). Rejected because:
- **Non-deterministic**: different reads could yield different criteria across runs
- **Explainability**: "same fixed bar for everyone" is a clean story; "judge reads KB and decides what matters" is not
- **The coverage agent already does JIT navigation** — that's the treatment variable. The judge should be the control.

### How it relates to the KB

```
Knowledge base (source of truth)
    ↓ human reads, distills (once)       ↓ subset per variant (at runtime)
Judge prompt                            Agent KB files
(static file, versioned)                (JIT navigation via index.md)
    ↓ same for all variants                 ↓
Scores ←──────────────────────────── Agent output
```

The KB informs the judge prompt's **authorship**. It does not inform the judge's **runtime behavior**. If the KB evolves between experiment cycles, we update the judge prompt as a deliberate versioned step — not automatically.

---

## Judge Prompt Structure (sketch)

The actual prompt needs to be authored, but here's the intended shape:

```
You are evaluating the quality of a JUnit test suite for a Spring Boot project.

Navigate src/main/ and src/test/ to understand the production code and generated tests.

Score the test suite on these criteria (0.0–1.0 each):

1. ASSERTION QUALITY
   [concrete description, examples of 0.2 vs 0.8 scores]

2. TEST SLICE USAGE
   [concrete description, examples of 0.2 vs 0.8 scores]

3. EDGE CASE COVERAGE
   [concrete description, examples of 0.2 vs 0.8 scores]

4. VERSION-AWARE PATTERNS
   [concrete description — does the test use Boot 4 idioms on a Boot 4 project?]

Return JSON only:
{
  "criteria": [
    { "name": "...", "score": 0.0-1.0, "evidence": "..." },
    ...
  ],
  "summary": "..."
}
```

The criteria above are illustrative — the final set will be distilled from the KB content. The key constraint is that they're **baked into the prompt text**, not discovered at runtime.

---

## Implementation

### TestQualityJudge.java

- Implements `Judge` directly (from agent-judge-core)
- Constructor takes: agent factory (functional interface), judge prompt file path, pass threshold (default 0.5)
- `judge()` method:
  1. Copy workspace to temp dir (isolation)
  2. Check for test files — if none, return `Judgment.fail()` with score 0.0
  3. Load judge prompt from file
  4. Invoke agent: read-only tools (`Read`, `Glob`, `Grep`), `yolo(false)`, timeout 3 min
  5. Parse outermost `{...}` from agent output
  6. Clamp scores to [0.0, 1.0], compute weighted average → `NumericalScore.normalized()`
  7. Return `Judgment` with `Check` entries per criterion + raw scores in metadata
  8. On agent failure or unparseable output → `Judgment.error()`
  9. Clean up temp dir
- Uses stronger model than experiment agent (e.g., Sonnet for judging, Haiku for agent)
- Agent factory is a functional interface (testability seam — mock in unit tests)

### Exhaust capture

Already wired (Step 1.4a): `ClaudeAgentModel.messageListener` → `SessionLogParser` → `PhaseCapture` → journal-core. The judge's agent call is captured the same way as the coverage agent's.

### Unit tests

- Mock agent factory, verify score computation from JSON response
- No-test-files → FAIL with score 0.0
- Malformed JSON → ERROR (not uncaught exception)
- Agent exception → ERROR
- Score clamping for out-of-range values

---

## What stays the same from v4

- Fixed quality bar, same for all variants
- Agent-based (not `LLMJudge`), read-only filesystem tools
- `NumericalScore.normalized()` for continuous 0–1 gradient
- KB as forkable policy layer — any team forks the KB + judge prompt together
- Diagnostic feedback: evidence strings map to improvement levers
- Rewards built-in LLM knowledge (control/variant-a score on model training alone)

## What changed from v4

| v4 | v5 |
|----|-----|
| "Judge prompt derived from KB" (ambiguous — could mean runtime) | Judge prompt is a static file, authored by reading KB, frozen between runs |
| Criteria listed as illustrative in design doc | Criteria will be baked into `prompts/judge-quality.txt` as the deliverable |
| No explicit work item for authoring judge prompt | First work item in Step 1.4 is writing the prompt |

---

## Open Questions for Reviewer

1. **Number of criteria**: The sketch shows 4 (assertion quality, slice usage, edge cases, version awareness). Should version awareness be a separate criterion or folded into slice usage? Fewer criteria = simpler scoring, but version awareness is a key differentiator for the experiment story.

2. **Weighting**: Equal weight across all criteria, or should some matter more? Equal weight is simplest to explain. Unequal weight needs justification.

3. **Judge model**: Plan is to use a stronger model for judging (Sonnet) than the experiment agent (Haiku). Is that the right split, or should the judge also use a frontier model (Opus) for maximum evaluation quality?

4. **Prompt authoring process**: Should we author the judge prompt manually by reading the KB, or use a one-time LLM-assisted generation step (read KB → generate prompt → human reviews and freezes)? Manual is more controlled. LLM-assisted might catch criteria we'd miss.
