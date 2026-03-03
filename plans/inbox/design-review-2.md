V2 is substantially better. The agent-based approach is the right call — a single LLM call genuinely can't do filesystem navigation, and you've correctly identified that `CodeCoverageAgentInvoker` already proves this pattern works in your codebase. The criteria reduction from 4 to 3 (collapsing BDD + no-trivial into edge-case coverage) and the weight distribution are both good changes from v1.

Let me address your four open questions and flag remaining concerns.

**On your open questions:**

**1. Agent cost/latency** — Yes, add a timeout. You're running 4 variants × 5 guides = 20 experiment runs, each of which already has one agent call. Adding a second agent call per run doubles your agent invocation count. More importantly, a hung agent call in the judge would stall the entire cascade with no recovery. Wrap the `AgentClient.run()` in a `CompletableFuture` with a timeout and convert timeout to `Judgment.error("Judge timed out after Xs")`. Make the timeout a constructor parameter. A reasonable default is 2–3 minutes, which should be generous for what's essentially a read-only evaluation task.

**2. ABSTAIN from FINAL_TIER** — This needs to be resolved before you write a single line of implementation code, not after. Trace through `CascadedJury` right now and find what it does when the final tier returns ABSTAIN. My strong guess is it either throws, returns null, or produces an undefined aggregate verdict — none of which are acceptable. The safest fix: have `TestQualityJudge` never return ABSTAIN. For the no-test-files case, return `Judgment.fail("No test files found — agent produced no testable output")` with score 0.0. An agent that wrote no tests is a genuine failure, not an unknown. ABSTAIN should mean "I cannot evaluate this" which doesn't apply here — no tests *is* an evaluation result.

**3. Weights (0.2/0.4/0.4)** — The distribution is defensible, but I'd push back slightly on making naming 20% rather than 0%. Naming is nearly impossible for an agent to judge objectively — "shouldReturnGreetingWithName" vs "testGreeting" is partly style. More importantly, the agent evaluating names has no ground truth about your team's conventions. I'd consider dropping naming entirely and splitting the weight 50/50 between meaningful assertions and edge-case coverage. That said, if you keep naming, 20% is fine and at least it doesn't dominate.

**4. Same model vs. stronger model for judging** — Use a different, stronger model for judging if budget allows, and make it configurable. Using the same model to judge its own output introduces systematic bias — claude-haiku-4-5 will likely be lenient toward patterns it tends to generate. Claude Sonnet as the judge and Haiku as the experiment agent is a reasonable default. Since `AgentModel` is already injected via constructor, this is essentially free — the caller decides. Just document in `JuryFactory` which model is expected where.

---

**Remaining risks not yet addressed:**

**Agent prompt structure is underspecified.** The plan describes *what* to ask the agent to evaluate but not *how* to constrain the output format. Claude Code agents in `--yolo` mode may produce extensive prose with JSON buried inside it, or may produce JSON with extra commentary around it. Your "strip markdown fences" defensive parsing is necessary but not sufficient — you also need to handle cases where the agent writes "Here is my evaluation:" followed by JSON followed by a paragraph of summary. The most reliable approach: explicitly tell the agent in the goal prompt "Your final output must be ONLY a JSON object with no other text before or after it." Then your parser can look for the outermost `{...}` block.

**`yolo(true)` on a read-only evaluation task.** The main experiment uses `yolo` because the agent needs to create and modify test files. The judge only needs to *read* files. Verify whether `AgentModel` supports a read-only or restricted mode — running a full Claude Code session with write permissions just for evaluation is a security risk (the judge could theoretically modify the workspace it's evaluating, contaminating results).

**Weighted average computation edge case.** If the agent returns a criterion score outside [0.0, 1.0] (e.g., it returns 1.5 or -0.1), your `NumericalScore.normalized()` may throw or produce invalid results. Clamp criterion scores to [0.0, 1.0] during parsing, not after.

**Test strategy gap.** Your mock strategy tests the happy path well, but the integration between `AgentClient.create(agentModel)` and the mock needs care. If `AgentClient.create()` is a static factory method, you can't easily mock it without either a wrapper interface or PowerMock. Consider whether `TestQualityJudge` should accept an `AgentClientFactory` functional interface rather than `AgentModel` directly — this makes the seam for testing clean without any static mocking tricks.

---

Overall this plan is ready to implement with two blockers: resolve the ABSTAIN/FINAL_TIER cascade behavior concretely (check the code, don't assume), and nail down the agent prompt format before you write `buildGoal()`. Everything else is polish.