# Review Handoff v2: Step 1.4 — Implement TestQualityJudge (Tier 3)

> **Date**: 2026-03-01
> **Review round**: 2 (revised after first review + owner input)
> **Requesting**: Review the revised agent-based approach, flag anything before implementation

---

## What Changed Since v1

The first review recommended extending `LLMJudge` (a single `ChatClient.prompt().call()`). The project owner identified a critical flaw: a single LLM request can't navigate the filesystem. The judge needs to read test files, follow imports to production code, and understand project structure — the same way a developer would review tests.

**New approach**: Use `AgentClient`/`ClaudeAgentModel` (Claude Code as an agent) instead of `ChatClient`. The judge invokes an agent that can navigate the workspace, read files on demand, and produce a structured evaluation. This is the same pattern already used in `CodeCoverageAgentInvoker` for the main experiment loop.

This resolves several v1 risks:
- **Prompt token size** → agent reads files on demand, not all at once
- **Production code context** → agent naturally navigates to related source files
- **JSON parsing brittleness** → partially mitigated; agent can be prompted more carefully, but still needs defensive parsing

---

## Project Context (unchanged from v1)

An **agent experiment** measuring whether injecting domain knowledge into an AI coding agent improves JUnit test generation for Spring Boot projects. 4 variants (progressively more knowledge) run against 5 Spring Getting Started guides, scored by a 4-tier cascaded jury.

### Architecture

```
ExperimentApp → ExperimentRunner → CodeCoverageAgentInvoker → CascadedJury → ResultStore
                                                                                 ↓
                                                                       ComparisonEngine → GrowthStoryReporter
```

### 4-Tier Jury

| Tier | Judge | Type | Policy | Status |
|------|-------|------|--------|--------|
| 0 | BuildSuccessJudge | Deterministic | REJECT_ON_ANY_FAIL | Exists (library) |
| 1 | CoveragePreservationJudge | Deterministic | REJECT_ON_ANY_FAIL | Exists (library) |
| 2 | CoverageImprovementJudge | Deterministic | ACCEPT_ON_ALL_PASS | Exists (library) |
| 3 | **TestQualityJudge** | **Agent-based** | **FINAL_TIER** | **This step** |

### Cascade Flow

1. **Tier 0** (REJECT_ON_ANY_FAIL): Does the project still compile? Any fail → reject.
2. **Tier 1** (REJECT_ON_ANY_FAIL): Did coverage drop more than 5pp? Any fail → reject.
3. **Tier 2** (ACCEPT_ON_ALL_PASS): How much did coverage improve? All pass → accept. Otherwise escalate.
4. **Tier 3** (FINAL_TIER): Are the tests actually good quality? Always produces final verdict.

---

## Judge API Reference

### Core Interface

```java
@FunctionalInterface
public interface Judge {
    Judgment judge(JudgmentContext context);
}
```

### JudgmentContext — What Judges Receive

```java
public record JudgmentContext(
    String goal,                        // "Improve test coverage to 80%"
    Path workspace,                     // Working directory with source code
    Duration executionTime,
    Instant startedAt,
    Optional<String> agentOutput,       // Agent's conversation/output
    ExecutionStatus status,
    Optional<Throwable> error,
    Map<String, Object> metadata        // Custom data from AgentInvoker
)
```

Metadata from `CodeCoverageAgentInvoker`: `baselineCoverage`, `finalCoverage`, `coverageImprovement`, `baselineBranchCoverage`, `finalBranchCoverage` (String values).

### Judgment — What Judges Return

```java
public record Judgment(Score score, JudgmentStatus status, String reasoning,
                       List<Check> checks, Map<String, Object> metadata)
```

- **Score types**: `BooleanScore(true/false)`, `NumericalScore.normalized(0.0-1.0)`
- **Status**: `PASS`, `FAIL`, `ABSTAIN`, `ERROR`
- **Checks**: Sub-assertions: `Check.pass("name", "msg")`, `Check.fail("name", "msg")`
- **Convenience**: `Judgment.pass(reason)`, `Judgment.fail(reason)`, `Judgment.abstain(reason)`, `Judgment.error(reason, throwable)`

Builder:
```java
Judgment.builder()
    .score(NumericalScore.normalized(0.75))
    .status(JudgmentStatus.PASS)
    .reasoning("Human-readable explanation")
    .check(Check.pass("criterion_name", "detail"))
    .metadata("key", value)
    .build();
```

### TierPolicy Enum

```java
public enum TierPolicy {
    REJECT_ON_ANY_FAIL,   // Any fail → reject, all pass → escalate
    ACCEPT_ON_ALL_PASS,   // All pass → accept, any fail → escalate
    FINAL_TIER            // Always produces verdict, must be last tier
}
```

---

## AgentClient API (what the judge will use)

The project already uses `AgentClient`/`ClaudeAgentModel` in `CodeCoverageAgentInvoker`. Here's the existing pattern:

```java
// Build the agent model (Claude Code)
ClaudeAgentOptions options = ClaudeAgentOptions.builder()
    .model("claude-haiku-4-5-20251001")
    .yolo(true)  // non-interactive mode
    .build();

AgentModel agentModel = ClaudeAgentModel.builder()
    .workingDirectory(workspace)
    .defaultOptions(options)
    .build();

// Create client and run
AgentClient client = AgentClient.create(agentModel);
AgentClientResponse response = client
    .goal("Your goal prompt here")
    .workingDirectory(workspace)
    .run();

// response contains the agent's output text
```

The agent (Claude Code) can read files, navigate the project, follow imports, and understand structure — it has full filesystem access within the workspace.

---

## Current JuryFactory Code

```java
public class JuryFactory {
    private final Map<Integer, List<Judge>> tierJudges;
    private final Map<Integer, TierPolicy> tierPolicies;

    // Builder pattern:
    JuryFactory.builder()
        .addJudge(0, buildSuccessJudge)
        .tierPolicy(0, TierPolicy.REJECT_ON_ANY_FAIL)
        .addJudge(1, coveragePreservation)
        .tierPolicy(1, TierPolicy.REJECT_ON_ANY_FAIL)
        .addJudge(2, coverageImprovement)
        .tierPolicy(2, TierPolicy.ACCEPT_ON_ALL_PASS)
        // Step 1.4 adds:
        .addJudge(3, testQualityJudge)
        .tierPolicy(3, TierPolicy.FINAL_TIER)
        .build();

    public Jury build(VariantSpec variant) {
        // Iterates tiers in order, builds SimpleJury per tier
        // with ConsensusStrategy, wraps in CascadedJury
    }
}
```

Currently no `AgentModel` is passed in — Step 1.4 needs to add that.

---

## Proposed TestQualityJudge Design (v2 — Agent-Based)

### Class: `TestQualityJudge implements Judge`

**Constructor**: `TestQualityJudge(AgentModel agentModel, double passThreshold)`
- `agentModel`: pre-configured `ClaudeAgentModel` (caller controls model choice)
- `passThreshold`: configurable, default 0.5

**`judge(JudgmentContext context)` flow**:

1. **Quick check**: if no `*.java` files exist under `workspace/src/test/` → `Judgment.abstain("No test files found")`

2. **Build evaluation goal**: a prompt instructing the agent to:
   - Navigate `src/test/` and read all test files
   - For each test file, find and read the corresponding production class
   - Evaluate 3 criteria (each scored 0.0–1.0):
     - **Test naming** (weight: 0.2): Do methods describe behavior? (e.g., `shouldReturnGreetingWithName` vs `test1`)
     - **Meaningful assertions** (weight: 0.4): Are assertions checking real behavior? Not `assertTrue(true)` or just `assertNotNull`
     - **Exception/edge-case coverage** (weight: 0.4): Are nulls, boundaries, error paths tested?
   - Output a specific JSON structure with scores and reasoning

3. **Invoke agent**: `AgentClient.create(agentModel).goal(prompt).workingDirectory(workspace).run()`

4. **Parse response**: extract JSON from agent output (defensive: strip markdown fences, handle partial JSON)
   - Success → compute weighted average → `NumericalScore.normalized(avg)`
   - Parse failure → `Judgment.error("Failed to parse agent evaluation output")`
   - Agent exception → `Judgment.error("Agent evaluation failed: " + ex.getMessage())`

5. **Build Judgment**:
   - `Check` entry per criterion (pass if criterion score >= passThreshold)
   - Raw per-criterion scores stored in `metadata` for recalibration
   - PASS if weighted average >= passThreshold, FAIL otherwise

### Expected Agent JSON Output Format

```json
{
  "testNaming": { "score": 0.8, "reasoning": "Most tests use descriptive names..." },
  "meaningfulAssertions": { "score": 0.6, "reasoning": "Some assertions check real behavior..." },
  "edgeCaseCoverage": { "score": 0.3, "reasoning": "No null checks or boundary tests..." }
}
```

### JuryFactory Changes

- Builder accepts optional `AgentModel` for agent-based judges
- If `AgentModel` provided, creates and registers `TestQualityJudge` at tier 3

### Error Handling Summary

| Scenario | Result |
|----------|--------|
| No test files in workspace | `Judgment.abstain()` |
| Agent throws exception | `Judgment.error()` |
| Agent output not parseable as JSON | `Judgment.error()` |
| Agent returns valid JSON | `Judgment` with `NumericalScore` |

---

## Test Strategy

- Mock `AgentClient` to return canned `AgentClientResponse` with known JSON
- Verify: correct score computation from 3 criteria with weights
- Verify: `Check` entries created per criterion
- Verify: no-test-files → ABSTAIN
- Verify: malformed agent output → ERROR (not uncaught exception)
- Verify: agent exception → ERROR

---

## Open Questions for Reviewer

1. **Agent cost/latency**: Each judge invocation runs a full Claude Code session. Is this acceptable for the final tier, or should we add a timeout/cost guard? The main experiment agent already runs per item — this adds a second agent call per item for judging.

2. **ABSTAIN from FINAL_TIER**: What happens when the last tier in a `CascadedJury` returns ABSTAIN? Need to verify this doesn't produce an undefined verdict. Should the judge fall back to a default score instead of ABSTAIN?

3. **Evaluation criteria weights** (0.2 naming, 0.4 assertions, 0.4 edge-cases): Does this weighting make sense? Naming is least important per v1 review feedback, assertions and edge-cases are where AI-generated tests typically fail.

4. **Agent model for judging**: Should the judge agent use the same model as the experiment agent, or a different one? Using the same model means the judge has the same biases. Using a stronger model (e.g., opus for judging haiku's output) might give better evaluations but increases cost.
