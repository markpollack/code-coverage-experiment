# Review Handoff v4: Step 1.4 — TestQualityJudge (Final)

> **Date**: 2026-03-01
> **Review round**: 4 (final sign-off before implementation)
> **Prior reviews**: v1 → v2 → v3, all in `plans/inbox/design-review-{1,2,3}.md`
> **Ask**: Any last blockers? Otherwise we implement.

---

## Review Evolution (3 rounds)

**v1**: Proposed `LLMJudge` (single ChatClient call). Owner caught that a single prompt can't navigate the filesystem — switched to agent-based.

**v2**: Agent-based via `AgentClient`/`ClaudeAgentModel`. Reviewer resolved: no ABSTAIN (use FAIL), drop naming criterion (subjective), configurable threshold, stronger model for judging, functional interface for testability.

**v3**: Reviewer resolved: copy workspace to temp dir for isolation, drop CompletableFuture (use agent-level timeout or simple try/catch), fix prompt for non-standard test naming conventions, mock full fluent chain in tests.

**v4** (this doc): Consolidated final design. Nothing new — just confirming all decisions are coherent.

---

## Final Design Summary

**TestQualityJudge** is an agent-based judge at Tier 3 (FINAL_TIER) of a cascaded jury. It invokes Claude Code against a copy of the workspace to evaluate whether AI-generated tests are actually good, not just high-coverage.

### Class

```java
public class TestQualityJudge implements Judge {

    @FunctionalInterface
    public interface AgentClientFactory {
        AgentClient create(Path workspace);
    }

    private final AgentClientFactory agentClientFactory;
    private final double passThreshold;

    public TestQualityJudge(AgentClientFactory factory, double passThreshold) { ... }
    public TestQualityJudge(AgentClientFactory factory) { this(factory, 0.5); }
}
```

### Flow

```
judge(JudgmentContext context):
  1. Copy context.workspace() → temp dir (isolation)
  2. Check temp/src/test/**/*.java exists
     └─ None → return Judgment.fail("No test files", score=0.0)
  3. Build goal prompt (see below)
  4. try:
       AgentClient client = agentClientFactory.create(tempWorkspace)
       AgentClientResponse response = client.goal(prompt).workingDirectory(tempWorkspace).run()
     catch Exception:
       return Judgment.error("Agent evaluation failed: " + msg)
  5. Extract outermost {...} from response text
     └─ Not found → return Judgment.error("Failed to parse evaluation output")
  6. Parse JSON, clamp each score to [0.0, 1.0]
  7. weightedAvg = 0.5 * meaningfulAssertions + 0.5 * edgeCaseCoverage
  8. Return Judgment:
       score = NumericalScore.normalized(weightedAvg)
       status = weightedAvg >= passThreshold ? PASS : FAIL
       checks = [Check per criterion]
       metadata = {raw scores, agent model, eval duration}
  finally:
     Delete temp workspace copy
```

### Agent Prompt

```
You are evaluating the quality of JUnit test files in a Spring Boot project.

Navigate the workspace and:
1. Read all test files under src/test/
2. For each test file, find and read the corresponding production class under src/main/.
   If no direct counterpart exists, evaluate the tests against all production classes in src/main/.
3. Evaluate the tests on these criteria (score each 0.0 to 1.0):

   **meaningfulAssertions**: Are assertions checking real behavior of the production code?
   Score 0.0 if tests use assertTrue(true), only assertNotNull, or don't verify actual logic.
   Score 1.0 if assertions validate specific return values, state changes, and expected outputs.

   **edgeCaseCoverage**: Do tests cover error paths, null inputs, boundary conditions?
   Score 0.0 if only happy-path scenarios are tested.
   Score 1.0 if tests include null handling, empty collections, boundary values, and exception cases.

Your final output must be ONLY a JSON object with no other text before or after it:
{"meaningfulAssertions":{"score":0.0,"reasoning":"..."},"edgeCaseCoverage":{"score":0.0,"reasoning":"..."}}
```

### Error Handling

| Scenario | Result |
|----------|--------|
| No test files | FAIL, score 0.0 |
| Agent exception | ERROR |
| No JSON in output | ERROR |
| Valid JSON | PASS/FAIL based on weighted avg vs threshold |

### JuryFactory Change

```java
// Builder gains:
public Builder agentClientFactory(TestQualityJudge.AgentClientFactory factory) { ... }

// build() auto-registers if factory provided:
if (agentClientFactory != null) {
    addJudge(3, new TestQualityJudge(agentClientFactory));
    tierPolicy(3, TierPolicy.FINAL_TIER);
}
```

### Test Cases

```java
// 1. Happy path: valid JSON → correct weighted score
mockFactory returns: {"meaningfulAssertions":{"score":0.8,...},"edgeCaseCoverage":{"score":0.4,...}}
Expected: PASS, score=0.6, 2 checks, raw scores in metadata

// 2. No test files → FAIL, score 0.0
Empty workspace, factory never called

// 3. Malformed output → ERROR
mockFactory returns: "Here is my evaluation: not json"

// 4. Agent exception → ERROR
Factory throws RuntimeException("boom")

// 5. Score clamping
mockFactory returns: scores 1.5 and -0.2 → clamped to 1.0 and 0.0 → avg 0.5
```

---

## Context (for reference)

### 4-Tier Jury

| Tier | Judge | Policy |
|------|-------|--------|
| 0 | BuildSuccessJudge | REJECT_ON_ANY_FAIL |
| 1 | CoveragePreservationJudge | REJECT_ON_ANY_FAIL |
| 2 | CoverageImprovementJudge | ACCEPT_ON_ALL_PASS |
| 3 | **TestQualityJudge** | **FINAL_TIER** |

### Judge API (minimal)

```java
interface Judge { Judgment judge(JudgmentContext context); }
// JudgmentContext: goal, workspace (Path), agentOutput, metadata, executionTime, status
// Judgment: score, status (PASS/FAIL/ERROR), reasoning, checks, metadata
// Judgment.fail(reason), Judgment.error(reason, throwable)
// NumericalScore.normalized(0.0-1.0), Check.pass(name, msg), Check.fail(name, msg)
```

### AgentClient API (existing usage in CodeCoverageAgentInvoker)

```java
AgentModel agentModel = ClaudeAgentModel.builder()
    .workingDirectory(workspace)
    .defaultOptions(ClaudeAgentOptions.builder().model("claude-sonnet-4-6").yolo(true).build())
    .build();
AgentClient client = AgentClient.create(agentModel);
AgentClientResponse response = client.goal(prompt).workingDirectory(workspace).run();
```

---

## Open Items

None. Three review rounds have resolved all blockers. This is a final confirmation pass.
