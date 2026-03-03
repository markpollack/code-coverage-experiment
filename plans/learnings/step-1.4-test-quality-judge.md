# Step 1.4: TestQualityJudge — Learnings

## What was built

- `TestQualityJudge.java` — agent-based judge implementing `Judge` interface
- `TestQualityJudgeTest.java` — 11 unit tests covering all edge cases
- `prompts/judge-practice-adherence.txt` — 6-criteria rubric distilled from 13 KB files
- `prompts/judge-practice-adherence-traceability.md` — maps each criterion to source KB files

## Key design decisions

1. **`Function<Path, AgentClient>` factory** — testability seam. Tests mock the factory without touching static methods or real agent infrastructure. The `defaultAgentClientFactory` static method provides the production wiring.

2. **`parseJudgment()` is package-private** — allows direct unit testing of JSON parsing without mocking the agent chain. Most test logic lives here.

3. **No workspace copy** — the design doc called for copying workspace to a temp dir before judging. Deferred this: the judge agent has read-only tools (`Read`, `Glob`, `Grep`), so isolation is already enforced at the tool level. If we find the judge modifying files in practice, add the copy.

4. **`NumericalScore.normalized(averageScore)`** — the average of 6 criterion scores. Individual per-criterion scores are in the `Check` list. The CascadedJury sees the average; downstream analysis reads the checks.

5. **Score clamping** — LLM outputs sometimes produce scores outside 0-1 range. `Math.max(0.0, Math.min(1.0, rawScore))` catches this silently. Logged as a check message so it's visible.

## API patterns discovered

- `AgentClient.AgentClientRequestSpec` — nested interface inside `AgentClient`, not a top-level class
- `AgentGeneration` (not `AgentResult`) — the model result type with `getOutput()`
- `AgentClientResponse.getResult()` — convenience method that delegates to `agentResponse.getResult().getOutput()`
- `NumericalScore` constructor validates range — throws on out-of-bounds, so clamping before construction is required

## What's next

- Step 1.5: Stage 1 consolidation
- Then Stage 2: run all variants and collect data
