# Review Handoff: Step 1.4 — Implement TestQualityJudge (Tier 3)

> **Date**: 2026-03-01
> **Review scope**: ROADMAP Step 1.4 plan and implementation approach
> **Ask**: Review the proposed design, flag risks, suggest improvements

---

## Project Context

This is an **agent experiment** that measures whether injecting domain knowledge into an AI coding agent improves its ability to write JUnit tests for Spring Boot projects. The experiment runs 4 variants (progressively more knowledge) against 5 Spring Getting Started guides and scores results via a 4-tier cascaded jury.

### Architecture

```
ExperimentApp → ExperimentRunner → CodeCoverageAgentInvoker → CascadedJury → ResultStore
                                                                                 ↓
                                                                       ComparisonEngine → GrowthStoryReporter
```

The `CodeCoverageAgentInvoker` measures baseline JaCoCo coverage, invokes an AI agent to write tests, then measures final coverage. The `CascadedJury` evaluates whether the agent did a good job.

### 4-Tier Jury (current state)

| Tier | Judge | Type | Policy | Status |
|------|-------|------|--------|--------|
| 0 | BuildSuccessJudge | Deterministic | REJECT_ON_ANY_FAIL | Exists (library) |
| 1 | CoveragePreservationJudge | Deterministic | REJECT_ON_ANY_FAIL | Exists (library) |
| 2 | CoverageImprovementJudge | Deterministic | ACCEPT_ON_ALL_PASS | Exists (library) |
| 3 | **TestQualityJudge** | **LLM-driven** | **FINAL_TIER** | **Step 1.4 (this plan)** |

Tiers 0–2 are gate-based: they reject bad results or accept good ones and escalate uncertain ones. Tier 3 is the terminal tier — it always produces a verdict. It's the only LLM-driven judge.

### Cascade Flow

1. **Tier 0** (REJECT_ON_ANY_FAIL): Does the project still compile? Any judge fail → reject immediately.
2. **Tier 1** (REJECT_ON_ANY_FAIL): Did coverage drop more than 5pp? Any fail → reject.
3. **Tier 2** (ACCEPT_ON_ALL_PASS): How much did coverage improve? All pass → accept. Otherwise escalate.
4. **Tier 3** (FINAL_TIER): Are the tests actually good quality? Always produces final verdict.

---

## What Step 1.4 Does

Implement `TestQualityJudge` — an LLM-powered judge that reads the AI-generated test files and evaluates their quality beyond just coverage numbers.

### Why This Matters

Coverage numbers alone don't tell you if tests are useful. An agent could generate `assertTrue(true)` 100 times and hit high coverage. The TestQualityJudge catches this by evaluating whether the tests follow best practices.

---

## Judge API Reference

### Core Interface

```java
@FunctionalInterface
public interface Judge {
    Judgment judge(JudgmentContext context);
}
```

### What Judges Receive (JudgmentContext)

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

The `CodeCoverageAgentInvoker` populates metadata with: `baselineCoverage`, `finalCoverage`, `coverageImprovement`, `baselineBranchCoverage`, `finalBranchCoverage` (as String values).

### What Judges Return (Judgment)

```java
public record Judgment(Score score, JudgmentStatus status, String reasoning,
                       List<Check> checks, Map<String, Object> metadata)
```

- **Score types**: `BooleanScore(true/false)`, `NumericalScore.normalized(0.0-1.0)`, `NumericalScore.outOfTen(7.5)`
- **Status**: `PASS`, `FAIL`, `ABSTAIN`, `ERROR`
- **Checks**: Sub-assertions for transparency: `Check.pass("name", "msg")`, `Check.fail("name", "msg")`
- **Convenience**: `Judgment.pass(reason)`, `Judgment.fail(reason)`, `Judgment.abstain(reason)`

Builder for rich judgments:
```java
Judgment.builder()
    .score(NumericalScore.normalized(0.75))
    .status(JudgmentStatus.PASS)
    .reasoning("Human-readable explanation")
    .check(Check.pass("criterion_name", "detail"))
    .metadata("key", value)
    .build();
```

### LLMJudge Base Class (from agent-judge-llm library)

```java
public abstract class LLMJudge implements JudgeWithMetadata {
    protected final ChatClient chatClient;

    protected LLMJudge(String name, String description,
                       ChatClient.Builder chatClientBuilder) {
        this.metadata = new JudgeMetadata(name, description, JudgeType.LLM_POWERED);
        this.chatClient = chatClientBuilder.build();
    }

    // Subclasses implement these two hooks:
    protected abstract String buildPrompt(JudgmentContext context);
    protected abstract Judgment parseResponse(String response, JudgmentContext context);

    @Override
    public Judgment judge(JudgmentContext context) {
        String prompt = buildPrompt(context);
        String response = this.chatClient.prompt().user(prompt).call().content();
        return parseResponse(response, context);
    }
}
```

### TierPolicy Enum

```java
public enum TierPolicy {
    REJECT_ON_ANY_FAIL,   // Any fail → reject (stop cascade). All pass → escalate.
    ACCEPT_ON_ALL_PASS,   // All pass → accept (stop cascade). Any fail → escalate.
    FINAL_TIER            // Always produces verdict. Must be last tier.
}
```

### Reference: Existing Deterministic Judge Pattern (CoverageImprovementJudge)

```java
public class CoverageImprovementJudge extends DeterministicJudge {
    @Override
    public Judgment judge(JudgmentContext context) {
        // 1. Extract baseline from context.metadata()
        // 2. Parse workspace state (JaCoCo reports)
        // 3. Compute normalized score (0-1)
        // 4. Return Judgment with score, status, reasoning, checks, metadata
        return Judgment.builder()
            .score(NumericalScore.normalized(normalizedScore))
            .status(improvement > 0 ? JudgmentStatus.PASS : JudgmentStatus.FAIL)
            .reasoning(String.format("Line coverage improved %.1f pp", improvement))
            .check(Check.pass("coverage_improved", "+30.0 pp"))
            .metadata("improvementPp", improvement)
            .build();
    }
}
```

### Reference: Existing LLM Judge Pattern (CorrectnessJudge)

```java
public class CorrectnessJudge extends LLMJudge {
    public CorrectnessJudge(ChatClient.Builder chatClientBuilder) {
        super("Correctness", "Evaluates if agent accomplished the goal", chatClientBuilder);
    }

    @Override
    protected String buildPrompt(JudgmentContext context) {
        return String.format("""
            Goal: %s
            Workspace: %s
            Agent Output: %s
            Did the agent accomplish the goal? Answer YES or NO, followed by reasoning.
            """, context.goal(), context.workspace(), context.agentOutput().orElse("No output"));
    }

    @Override
    protected Judgment parseResponse(String response, JudgmentContext context) {
        boolean pass = response.toUpperCase().contains("YES");
        return Judgment.builder()
            .score(new BooleanScore(pass))
            .status(pass ? JudgmentStatus.PASS : JudgmentStatus.FAIL)
            .reasoning(response)
            .build();
    }
}
```

---

## Current JuryFactory Code

```java
public class JuryFactory {
    private final Map<Integer, List<Judge>> tierJudges;
    private final Map<Integer, TierPolicy> tierPolicies;

    public Jury build(VariantSpec variant) {
        // Iterates tiers in order, builds SimpleJury per tier with ConsensusStrategy,
        // wraps in CascadedJury with per-tier policies
    }

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        public Builder addJudge(int tier, Judge judge) { ... }
        public Builder tierPolicy(int tier, TierPolicy policy) { ... }
        public JuryFactory build() { ... }
    }
}
```

Currently no `ChatClient.Builder` is accepted — Step 1.4 needs to add it for LLM judges.

---

## Proposed TestQualityJudge Design

### Class: `TestQualityJudge extends LLMJudge`

**Constructor**: takes `ChatClient.Builder`

**`buildPrompt(JudgmentContext context)`**:
1. Scan workspace `src/test/` for `*.java` files
2. Include their full content in the prompt
3. Ask LLM to evaluate on 4 criteria:
   - **Test naming**: Do test methods describe behavior? (e.g., `shouldReturnGreetingWithName` vs `test1`)
   - **Meaningful assertions**: Are assertions checking real behavior? (not `assertTrue(true)`, not just `assertNotNull`)
   - **BDD structure**: Do tests follow arrange-act-assert / given-when-then?
   - **No trivial tests**: Are tests exercising real logic, not just calling getters/setters?
4. Request structured JSON response with per-criterion score (0.0-1.0) and reasoning

**`parseResponse(String response, JudgmentContext context)`**:
1. Parse JSON response
2. Compute weighted average of 4 criterion scores → `NumericalScore.normalized()`
3. Create `Check` entry per criterion (pass if score >= 0.5, fail otherwise)
4. PASS if overall score >= 0.5, FAIL otherwise

**Edge case**: No test files in workspace → `Judgment.abstain("No test files found")`

### JuryFactory Changes

- Accept optional `ChatClient.Builder` in constructor or builder
- Register `TestQualityJudge` at tier 3 with `TierPolicy.FINAL_TIER`

### Dependency to Add

```xml
<dependency>
    <groupId>org.springaicommunity</groupId>
    <artifactId>agent-judge-llm</artifactId>
    <version>${agent-judge.version}</version>  <!-- 0.9.0-SNAPSHOT -->
</dependency>
```

This pulls in Spring AI's `ChatClient` transitively.

### Unit Test Plan

- Mock `ChatClient.Builder` → `ChatClient` → returns canned JSON response
- Verify judge parses response into correct score, status, checks
- Verify no-test-files edge case → ABSTAIN

---

## ROADMAP Step 1.4 (as written)

**Entry criteria**:
- [x] Step 1.3 complete
- [ ] Read: `plans/learnings/step-1.3-dataset.md`

**Work items**:
- [ ] ADD `agent-judge-llm` dependency to `pom.xml`
- [ ] IMPLEMENT `TestQualityJudge` extending `LLMJudge`
- [ ] WIRE UP `JuryFactory` to accept `ChatClient.Builder`, register at Tier 3 with `FINAL_TIER`
- [ ] WRITE unit test `TestQualityJudgeTest` with mock `ChatClient`
- [ ] VERIFY: `./mvnw compile` and `./mvnw test` pass

**Exit criteria**:
- [ ] TestQualityJudge compiles and passes tests
- [ ] All tests pass: `./mvnw test`
- [ ] Create: `plans/learnings/step-1.4-test-quality-judge.md`
- [ ] Update `CLAUDE.md` with distilled learnings
- [ ] Update `ROADMAP.md` checkboxes
- [ ] COMMIT

---

## Questions for Reviewer

1. **Base class choice**: Is extending `LLMJudge` the right approach, or should we implement `Judge` directly for more control over the LLM interaction (e.g., structured output, retry logic)?

2. **Evaluation criteria**: Are the 4 criteria (naming, assertions, BDD, no-trivial) the right set? Should we add/remove any?

3. **Production code context**: Should the prompt include production source code alongside the tests, so the LLM can evaluate test-to-code coverage relevance? This would make the prompt larger but more informative.

4. **Score type**: Is `NumericalScore.normalized()` (continuous 0-1) the right score type for the final tier, or should it be `BooleanScore` with a quality threshold?

5. **Roadmap structure**: The ROADMAP was upgraded to Forge methodology format with consolidation steps (1.5, 2.2) and convention sections. Does the step granularity look right?
