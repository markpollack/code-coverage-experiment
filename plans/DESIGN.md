# Design: Code Coverage Experiment

## Architecture

This experiment uses the standard agent experiment loop:

```
ExperimentApp → ExperimentRunner → CodeCoverageAgentInvoker → CascadedJury → ResultStore
                                                                                 ↓
                                                                       ComparisonEngine
                                                                                 ↓
                                                                     GrowthStoryReporter
```

## Domain Agent

**AgentInvoker implementation:** `CodeCoverageAgentInvoker`

Workflow per dataset item:
1. Verify project compiles (`mvn clean compile`)
2. Measure baseline coverage (`mvn clean test jacoco:report` → `JaCoCoReportParser`)
3. Build prompt from variant's prompt file + baseline metrics
4. Invoke agent via `AgentClient.goal(prompt).workingDirectory(workspace).run()`
5. Measure final coverage
6. Store baseline/final metrics in `InvocationResult` metadata for judges

The agent operates autonomously on the workspace — it reads code, adds/modifies tests, and may add the JaCoCo Maven plugin if missing.

## Judges

| Judge | Tier | Type | Policy | What it checks |
|-------|------|------|--------|---------------|
| BuildSuccessJudge | 0 | Deterministic | REJECT_ON_ANY_FAIL | Project compiles and tests pass after agent |
| CoveragePreservationJudge | 1 | Deterministic | REJECT_ON_ANY_FAIL | Coverage didn't regress from baseline |
| CoverageImprovementJudge | 2 | Deterministic | ACCEPT_ON_ALL_PASS | Normalized coverage improvement score |
| TestQualityJudge | 3 | Agent-based | FINAL_TIER | Fixed quality bar — same criteria for all variants |

Tier 0–2 judges are "off the shelf" from `agent-judge-exec`. Tier 3 (`TestQualityJudge`) is the custom domain piece.

### TestQualityJudge: Fixed Quality Bar

The judge uses a **single handcrafted prompt** applied identically to all variants. It defines what good Spring Boot tests look like — period. It does not adapt to what the agent was told, and it does not derive criteria from the variant's prompt or knowledge files.

**Why fixed, not adaptive:** The judge is the target; the variants are different attempts to hit it. A fixed bar means:
- The audience understands the evaluation ("same bar for everyone")
- The LLM's built-in knowledge is rewarded, not penalized
- The growth story shows what knowledge injection *added on top of* what the model already knew

**Criteria** (scored 0.0–1.0 each):

| Criterion | What it measures | Low score example | High score example |
|-----------|-----------------|-------------------|--------------------|
| Assertion quality | Real assertions testing specific values | `assert x != null`, `assertTrue(true)` | `assertThat(response.getBody()).isEqualTo(expected)` |
| Spring slice usage | Correct test annotations for context | `@SpringBootTest` for everything | `@WebMvcTest` for controllers, `@DataJpaTest` for repos |
| Edge case coverage | Non-happy-path testing | Only tests the default success case | Null inputs, empty collections, error paths tested |

The criteria are **universal best practices** — not specific to any variant. The knowledge files *teach* these practices to the agent. The judge *measures* whether the agent applied them. This creates the ablation signal: how much closer to the fixed bar did each additional resource get?

**Implementation:** Agent-based (uses `ClaudeAgentModel` with read-only tools: `Read`, `Glob`, `Grep`) to navigate `src/main/` and `src/test/`. Returns JSON with per-criterion scores and evidence strings. Final score is weighted average → `NumericalScore.normalized()`.

### Knowledge Files Derive From Judge Criteria

The knowledge files and judge criteria form a closed loop:

```
Judge criteria (fixed target)
    ↑ measures against
    |
Knowledge files (teach agent to hit the target)
    ↓ injected into
Agent prompt (variant-specific)
```

`spring-test-slices.md` teaches `@WebMvcTest` usage → the judge scores slice usage. `coverage-fundamentals.md` teaches assertion quality → the judge scores assertion quality. The knowledge files should not teach things the judge doesn't measure, and the judge shouldn't measure things the knowledge files don't address (at least for higher variants).

### Future: Modernization Advisor (not a judge)

A separate concern from quality judging: detecting where existing test patterns could be upgraded to newer Boot idioms (e.g., `MockMvc` → `RestTestClient` on Boot 4+). This is **not a judge** — judges score the agent's output against a quality bar. Modernization advice is a recommendation for the project maintainer, orthogonal to coverage improvement. It could be a standalone report or a separate agent, but it should not influence the coverage agent's behavior during an experiment run. The coverage agent's job is to follow existing conventions and add coverage, not refactor test style.

## Variants

| Variant | Prompt | Knowledge | Expected Outcome |
|---------|--------|-----------|-----------------|
| control | v0-naive.txt ("Improve test coverage to 80%") | none | ~50% line coverage |
| variant-a | v1-hardened.txt (detailed constraints, examples) | none | ~65% line coverage |
| variant-b | v2-with-kb.txt (hardened + "read knowledge/") | coverage-fundamentals, jacoco-patterns, spring-test-slices | ~82% line coverage |
| variant-c | v2-with-kb.txt | all above + common-gaps | ~85% line coverage |

## Dataset

5 Spring Getting Started guides — small, well-structured projects that represent common Spring Boot patterns:

| Item | URL | Pattern |
|------|-----|---------|
| gs-rest-service | spring-guides/gs-rest-service | REST controller |
| gs-accessing-data-jpa | spring-guides/gs-accessing-data-jpa | JPA repository |
| gs-securing-web | spring-guides/gs-securing-web | Spring Security |
| gs-reactive-rest-service | spring-guides/gs-reactive-rest-service | WebFlux reactive |
| gs-messaging-stomp-websocket | spring-guides/gs-messaging-stomp-websocket | WebSocket messaging |

Each guide's `complete/` subdirectory is used as the workspace.

## Knowledge Files

| File | Content | Used by |
|------|---------|---------|
| coverage-fundamentals.md | Line/branch/method coverage, meaningful test criteria, what NOT to cover | variant-b, variant-c |
| jacoco-patterns.md | JaCoCo Maven plugin config, report structure, common issues | variant-b, variant-c |
| spring-test-slices.md | @WebMvcTest vs @DataJpaTest vs plain JUnit decision tree | variant-b, variant-c |
| common-gaps.md | Negative guidance: don't test records/main/config, DO test error handling | variant-c only |
