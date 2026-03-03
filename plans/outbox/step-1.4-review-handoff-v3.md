# Review Handoff v3: Step 1.4 — Implement TestQualityJudge (Tier 3)

> **Date**: 2026-03-01
> **Review round**: 3 (final before implementation)
> **Prior reviews**: `plans/inbox/design-review.md` (v1), `plans/inbox/design-review-2.md` (v2)
> **Ask**: Final sign-off. Flag any remaining blockers or implementation traps.

---

## Review History

**v1** proposed extending `LLMJudge` (single `ChatClient` call). Reviewer accepted but flagged JSON parsing brittleness, ABSTAIN handling, and prompt token size risks.

**v2** switched to agent-based approach (`AgentClient`/`ClaudeAgentModel` — Claude Code with filesystem access). Reviewer approved and resolved open questions:
- Add timeout on agent call (configurable, default 2-3 min)
- Never ABSTAIN from FINAL_TIER — no test files = FAIL with score 0.0
- Drop naming criterion (subjective) → 2 criteria at 50/50
- Use stronger model for judging to avoid self-bias
- Accept functional interface for testability (not static `AgentClient.create()`)
- Constrain agent output to JSON-only, parse outermost `{...}`, clamp scores

**v3** (this doc) presents the final consolidated design ready for implementation.

---

## Project Context

An agent experiment measuring whether knowledge injection improves AI-generated JUnit tests. 4 variants × 5 Spring Getting Started guides, scored by a 4-tier cascaded jury.

```
ExperimentApp → ExperimentRunner → CodeCoverageAgentInvoker → CascadedJury → ResultStore
```

| Tier | Judge | Type | Policy | Status |
|------|-------|------|--------|--------|
| 0 | BuildSuccessJudge | Deterministic | REJECT_ON_ANY_FAIL | Exists |
| 1 | CoveragePreservationJudge | Deterministic | REJECT_ON_ANY_FAIL | Exists |
| 2 | CoverageImprovementJudge | Deterministic | ACCEPT_ON_ALL_PASS | Exists |
| 3 | **TestQualityJudge** | **Agent-based** | **FINAL_TIER** | **This step** |

---

## Judge API (unchanged from v2)

```java
@FunctionalInterface
public interface Judge {
    Judgment judge(JudgmentContext context);
}

// context provides: goal, workspace (Path), agentOutput, metadata, executionTime, status
// metadata from invoker: baselineCoverage, finalCoverage, coverageImprovement (Strings)

// Judgment has: score, status (PASS/FAIL/ERROR), reasoning, checks, metadata
// Score types: NumericalScore.normalized(0.0-1.0), BooleanScore
// Checks: Check.pass("name", "msg"), Check.fail("name", "msg")
```

## AgentClient API (existing pattern from CodeCoverageAgentInvoker)

```java
ClaudeAgentOptions options = ClaudeAgentOptions.builder()
    .model("claude-sonnet-4-6")  // stronger model for judging
    .yolo(true)
    .build();

AgentModel agentModel = ClaudeAgentModel.builder()
    .workingDirectory(workspace)
    .defaultOptions(options)
    .build();

AgentClient client = AgentClient.create(agentModel);
AgentClientResponse response = client
    .goal("evaluation prompt here")
    .workingDirectory(workspace)
    .run();
// response contains agent's output text
```

---

## Final Design: TestQualityJudge

### Class Signature

```java
public class TestQualityJudge implements Judge {

    @FunctionalInterface
    public interface AgentClientFactory {
        AgentClient create(Path workspace);
    }

    private final AgentClientFactory agentClientFactory;
    private final double passThreshold;
    private final Duration timeout;

    public TestQualityJudge(AgentClientFactory agentClientFactory,
                            double passThreshold, Duration timeout) { ... }

    public TestQualityJudge(AgentClientFactory agentClientFactory) {
        this(agentClientFactory, 0.5, Duration.ofMinutes(3));
    }
}
```

### `judge(JudgmentContext context)` Flow

```
1. Check for test files under workspace/src/test/**/*.java
   └─ None found → Judgment.fail("No test files", score=0.0)

2. Build evaluation goal prompt (see below)

3. Invoke agent with timeout:
   AgentClient client = agentClientFactory.create(context.workspace());
   CompletableFuture<AgentClientResponse> future =
       CompletableFuture.supplyAsync(() -> client.goal(prompt).workingDirectory(workspace).run());
   AgentClientResponse response = future.get(timeout.toMillis(), MILLISECONDS);
   └─ TimeoutException → Judgment.error("Judge timed out")
   └─ Other exception → Judgment.error("Agent evaluation failed: " + msg)

4. Parse agent output:
   - Extract outermost {...} from response text
   - Deserialize JSON to evaluation record
   - Clamp each criterion score to [0.0, 1.0]
   └─ Parse failure → Judgment.error("Failed to parse evaluation output")

5. Compute score:
   weightedAvg = 0.5 * meaningfulAssertions + 0.5 * edgeCaseCoverage
   score = NumericalScore.normalized(weightedAvg)
   status = weightedAvg >= passThreshold ? PASS : FAIL

6. Return Judgment with:
   - score, status, reasoning (from agent)
   - Check per criterion (pass if criterion >= passThreshold)
   - metadata: raw per-criterion scores, agent model used, evaluation duration
```

### Agent Evaluation Prompt

```
You are evaluating the quality of JUnit test files in a Spring Boot project.

Navigate the workspace and:
1. Read all test files under src/test/
2. For each test file, find and read the corresponding production class under src/main/
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

### Expected JSON Output

```json
{
  "meaningfulAssertions": {
    "score": 0.7,
    "reasoning": "Most tests verify specific return values from controller endpoints, but two tests only check assertNotNull on response body."
  },
  "edgeCaseCoverage": {
    "score": 0.3,
    "reasoning": "No tests for null input handling. No boundary value tests. One test verifies 404 on missing resource."
  }
}
```

### Error Handling Matrix

| Scenario | Judgment |
|----------|---------|
| No test files in workspace | `FAIL`, score 0.0, "No test files found" |
| Agent timeout | `ERROR`, "Judge timed out after {N}s" |
| Agent throws exception | `ERROR`, "Agent evaluation failed: {msg}" |
| Agent output has no JSON | `ERROR`, "Failed to parse evaluation output" |
| Agent returns valid JSON | `PASS`/`FAIL` based on weighted avg vs threshold |

### JuryFactory Changes

```java
public class JuryFactory {
    // Existing fields...

    public static class Builder {
        // Existing methods...

        // New: accept agent factory for agent-based judges
        public Builder agentClientFactory(TestQualityJudge.AgentClientFactory factory) {
            this.agentClientFactory = factory;
            return this;
        }

        public JuryFactory build() {
            // If agentClientFactory provided, auto-register TestQualityJudge at tier 3
            if (agentClientFactory != null) {
                addJudge(3, new TestQualityJudge(agentClientFactory));
                tierPolicy(3, TierPolicy.FINAL_TIER);
            }
            return new JuryFactory(tierJudges, tierPolicies);
        }
    }
}
```

---

## Test Strategy

```java
class TestQualityJudgeTest {
    @TempDir Path workspace;

    // Happy path: valid JSON from agent
    @Test void shouldComputeWeightedScore() {
        var factory = mockFactory("""
            {"meaningfulAssertions":{"score":0.8,"reasoning":"good"},
             "edgeCaseCoverage":{"score":0.4,"reasoning":"limited"}}""");
        var judge = new TestQualityJudge(factory);
        // Create a dummy test file so judge doesn't short-circuit
        writeFile(workspace, "src/test/java/FooTest.java", "class FooTest {}");

        Judgment j = judge.judge(buildContext(workspace));

        assertThat(j.status()).isEqualTo(JudgmentStatus.PASS);  // 0.6 >= 0.5
        assertThat(((NumericalScore) j.score()).value()).isCloseTo(0.6, within(0.001));
        assertThat(j.checks()).hasSize(2);
        assertThat(j.metadata()).containsKeys("meaningfulAssertions", "edgeCaseCoverage");
    }

    // No test files → FAIL with score 0.0
    @Test void shouldFailWhenNoTestFiles() {
        var judge = new TestQualityJudge(mockFactory("unused"));
        Judgment j = judge.judge(buildContext(workspace));  // empty workspace
        assertThat(j.status()).isEqualTo(JudgmentStatus.FAIL);
        assertThat(((NumericalScore) j.score()).value()).isEqualTo(0.0);
    }

    // Malformed output → ERROR
    @Test void shouldErrorOnMalformedOutput() {
        var factory = mockFactory("Here is my evaluation: not json at all");
        writeFile(workspace, "src/test/java/FooTest.java", "class FooTest {}");
        Judgment j = new TestQualityJudge(factory).judge(buildContext(workspace));
        assertThat(j.status()).isEqualTo(JudgmentStatus.ERROR);
    }

    // Agent exception → ERROR
    @Test void shouldErrorOnAgentException() {
        AgentClientFactory factory = ws -> { throw new RuntimeException("boom"); };
        writeFile(workspace, "src/test/java/FooTest.java", "class FooTest {}");
        Judgment j = new TestQualityJudge(factory).judge(buildContext(workspace));
        assertThat(j.status()).isEqualTo(JudgmentStatus.ERROR);
    }

    // Score clamping
    @Test void shouldClampScoresOutsideRange() {
        var factory = mockFactory("""
            {"meaningfulAssertions":{"score":1.5,"reasoning":"over"},
             "edgeCaseCoverage":{"score":-0.2,"reasoning":"under"}}""");
        writeFile(workspace, "src/test/java/FooTest.java", "class FooTest {}");
        Judgment j = new TestQualityJudge(factory).judge(buildContext(workspace));
        // clamped: (1.0 + 0.0) / 2 = 0.5
        assertThat(((NumericalScore) j.score()).value()).isCloseTo(0.5, within(0.001));
    }
}
```

---

## Open Items (for reviewer)

1. **Read-only agent mode**: We haven't yet confirmed whether `ClaudeAgentOptions` supports restricting the judge agent to read-only. If not, the judge runs with write access to the workspace it's evaluating. Is this acceptable for now (the judge has no incentive to modify files), or should we copy the workspace to a temp dir before judging?

2. **Is this design complete enough to implement?** We've had two review rounds and resolved all prior blockers. Anything remaining that would cause rework if discovered during implementation?
