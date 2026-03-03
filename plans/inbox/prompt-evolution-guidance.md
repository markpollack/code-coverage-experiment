# Prompt Evolution Guidance: Lessons from Forensics and Tuvium Infrastructure

> **Source**: Two independent evidence streams synthesized:
> 1. Forensic git analysis of the original coverage agent (`~/community/agent-client/agents/code-coverage-agent/`, October 2025)
> 2. Findings from Tuvium infrastructure projects (`tuvium-ir-experiment`, `tuvium-experiment-driver`, `tuvium-operabench`, `refactoring-agent`)
>
> **Date**: 2026-03-02
>
> **Purpose**: Guidance for how to evolve the coverage agent prompt across variants, based on what went wrong last time and what the Tuvium infrastructure has since proven. This document provides full context so the agent working on this project can make informed decisions without needing to explore other repositories.
>
> **Conference note**: This document is structured to support presentation at DevNexus 2026. All claims are attributed to their specific source. The October 2025 forensics and the Arize overfitting analysis are **independent evidence streams** that converge on the same conclusion — they should be presented as such.

---

## Part 1: Forensic History of the Original Coverage Agent

### The October 2025 Session

The original coverage agent prompt lives in `agent-client/agents/code-coverage-agent/`. Git forensics reveal exactly how it was built:

**Phase 0 (Sep 24, 2025)** — `coverage.yaml` created with a naive placeholder prompt as part of JBang launcher infrastructure work:
```
system: "You are an expert Java testing agent. Your role is to improve test coverage
         while maintaining code quality and following best practices."
user: "Increase line coverage in {module} to at least {target_coverage}%.
       Focus on {focus} tests."
```
This prompt has zero testing convention guidance — no mention of AssertJ, BDD naming, `@WebMvcTest`, or anything about avoiding `assert` statements. It was never actually executed against a real project.

**Phase 0.5 (Sep 27)** — The prompt section was deleted from `coverage.yaml` entirely. Architecture shifted to `AgentRunner` functional interface where prompts are internal to Java code.

**Phase 1 (Oct 5, 20:42 EDT)** — First real prompt committed in `CodeCoverageAgentRunner.buildCoverageGoal()`. This is the critical commit. The prompt was **already battle-hardened** with anti-pattern rules:

```
SPRING OSS TESTING BEST PRACTICES (MANDATORY):
- Use AssertJ assertions: assertThat(value).isEqualTo(expected)
  BAD: assert greeting.id() == 1
  BAD: assertEquals(1, greeting.id())
  GOOD: assertThat(greeting.id()).isEqualTo(1)

- BDD-style test naming: <method>[when<condition>]<expectation>
  BAD: test_greeting_with_param()
  BAD: testGreetingWithParam()
  GOOD: greetingShouldReturnCustomMessageWhenNameProvided()

- DO NOT write tests for main() methods or application startup
- DO NOT use plain assert statements (Java keyword)
- Focus on behavior, not implementation details
```

The lines `BAD: assert greeting.id() == 1` and `DO NOT use plain assert statements (Java keyword)` are evidence of prior experimentation — the author observed Gemini generating exactly those patterns. But the experiments that produced those failures were never committed. The commit message says "Achieve 71.4% coverage in integration test (target was 20%)" — this was already the successful run.

**Phase 2 (Oct 5, 21:04 EDT — 22 minutes later)** — Prompt extracted from inline Java to `/META-INF/prompts/coverage-agent-prompt.txt`. Content identical, just using `{variable}` template syntax.

**Phase 3 (Oct 5, 21:07 EDT — 3 minutes later)** — The final expansion. Commit message: "feat: enhance prompt with Spring WebMVC controller testing best practices" with note: "This update incorporates feedback from reviewing generated tests to ensure they follow Spring Framework's recommended patterns for web layer testing."

Added sections:
1. CONTROLLER TESTING (`@WebMvcTest` vs `@SpringBootTest`)
2. JSON RESPONSE VALIDATION (`jsonPath()` vs ObjectMapper)
3. EDGE CASES (boundary conditions)
4. AVOID TESTING IMPLEMENTATION DETAILS (no testing records, no main())

**Phase 4 (Oct 5, 21:47 EDT)** — No prompt changes, but commit message preserves the comparison data:
```
- Gemini (gemini-2.5-pro): 71.4% coverage, partial Spring best practices
- Claude (claude-sonnet-4-20250514): 71.4% coverage, FULL Spring best practices
  - Used @WebMvcTest (not @SpringBootTest)
  - Used jsonPath() (not manual ObjectMapper)
  - Used AssertJ assertThat()
  - BDD-style test naming
```

**Phase 5 (Oct 5, 22:04-22:10 EDT)** — Generated test outputs preserved as documentation artifacts:
- `GreetingControllerTests-claude.java` — 8 tests, `@WebMvcTest`, AssertJ, BDD naming, `jsonPath()`
- `GreetingControllerTests-gemini.java` — 6 tests, `@SpringBootTest`, no BDD naming
- `GreetingTests-gemini.java` — 4 tests testing Java record methods (`equals`, `hashCode`, `toString` — exactly what the prompt says NOT to test)

The Gemini output files show that **even after the prompt was hardened**, Gemini still used `@SpringBootTest` and tested record auto-generated methods. The `assert` keyword problem occurred in even earlier runs that were never committed.

**After October 5** — The prompt has not been modified in 5 months. All subsequent commits were mechanical refactors (imports, dependency coordinates, API patterns).

### What This Tells Us

1. **"Commit the solution, not the journey"** — The prompt evolution that would be most instructive was never versioned
2. **Inline rules accumulated reactively** — Each BAD/GOOD example was added in response to a specific observed failure
3. **The anti-pattern rules are domain knowledge disguised as prompt instructions** — They belong in a knowledge base, not inline text
4. **The prompt hit a ceiling** — Even with all the inline rules, Gemini still violated several of them. The rules didn't transfer reliably.

---

## Part 2: What the Tuvium Infrastructure Has Proven

### tuvium-ir-experiment: Prompt Optimization Overfits

> **Source attribution**: The findings below come from `~/tuvium/projects/tuvium-ir-experiment/`. The core evidence is from a forensic analysis of Arize's open-source repository (`github.com/Arize-ai/prompt-learning`), cloned to `vendor/arize-prompt-learning/`. The "intentional domain-specificity thesis" is an original synthesis by Mark Pollack. These findings are **separate from and independent of** the October 2025 coverage agent work described in Part 1.

The IR (Infrastructure vs. Prompts) experiment tested prompt-level optimization against infrastructure-level optimization on SWE-bench Lite. The factorial design:
- Control: baseline prompt
- Prompt-optimized: Arize-style prompt patching (add rules based on failures)
- KB-enriched: domain knowledge injected as infrastructure
- Combined: both

#### What Arize Published

Arize published a prompt optimization approach for coding agents:
- Cline baseline ~30% → optimized ~45% (+15 percentage points)
- Claude Code baseline ~40% → optimized ~45% (+5 percentage points, ZenML case study only)
- Plan Mode results with 11 optimization loops using LLM-as-Judge evaluation

#### What Forensic Analysis of Arize's Code Revealed (Unpublished)

Mark Pollack's forensic analysis of the open-source repository (documented in `tuvium-ir-experiment/plans/research/forensic-arize-overfitting.md`) discovered catastrophic overfitting **not discussed in Arize's published materials**:

| Ruleset | Total Rules | Django-Specific | Honestly Named | Test Accuracy |
|---------|------------|----------------|----------------|---------------|
| ruleset_0 | 24 | 2-3 | ~5 | 40% |
| ruleset_1 | 16 | 9 | 0 (all masked) | 45.2% |
| ruleset_2 | 16 | 9 | 0 (all masked) | **0%** |
| django_ruleset_2 | 30 | 21 | 21 (explicit) | 69.6% |

The smoking gun: `ruleset_2` achieved **0% test accuracy at loop 2** with byte-identical rules to loop 1. The mechanism:
- `django_ruleset_2` (69.6%) succeeds because it names its domain explicitly: "When handling Django's Q objects...", "AlterOrderWithRespectTo..."
- `ruleset_2` (0%) fails because it disguises Django patterns as universal principles. The agent applies them everywhere, causing failures on sympy/matplotlib/scikit-learn repos.

#### The Intentional Domain-Specificity Thesis (Original)

> **Attribution**: This is Mark Pollack's original hypothesis, synthesized from the forensic analysis.

"Prompt optimization on multi-repo tasks faces an impossible constraint: rules must be simultaneously general enough for all repos and specific enough to help on any given repo. The optimizer resolves this by learning repo-specific patterns and disguising them as general principles."

The solution: keep domain knowledge in **domain-scoped artifacts** (KB files, tool configs) where the scope is explicit, not in prompt text where it masquerades as universal instruction.

#### Why This Matters for the Coverage Experiment

The October 2025 approach (accumulating `BAD:` examples in the prompt) is structurally identical to Arize's approach — domain-specific rules disguised as general prompt instructions. The October 2025 rules worked for gs-rest-service but wouldn't reliably transfer to gs-accessing-data-jpa or gs-reactive-rest-service.

These are **two independent evidence streams converging on the same conclusion**:
1. **October 2025 (observed)**: Inline rules in the coverage agent prompt didn't prevent Gemini from violating them
2. **Arize forensics (measured)**: Inline rules optimized on training repos collapsed to 0% on held-out repos

Neither finding depends on the other. Together they make a strong case that the KB-based approach (variant-b/c) should outperform the inline-rules approach (variant-a).

### tuvium-experiment-driver: Diagnostic Feedback Loop

The experiment driver classifies failures into 8 gap categories via `DiagnosticAnalyzer`:
- AGENT_EXECUTION_GAP — agent didn't follow instructions
- PLAN_GENERATION_GAP — plan didn't cover the pattern
- KB_GAP — knowledge base missing the needed information
- TOOL_GAP — no tool handles the transformation
- ANALYSIS_GAP — static analysis missed a signal
- CRITERIA_GAP — VERIFY criteria were wrong
- EVALUATION_GAP — judge is wrong
- STOCHASTICITY_GAP — random variance

`DiagnosticReasoner` then produces `RemediationActions` with action types: ADD_RULE, ENHANCE_TOOL, IMPROVE_PROMPT, ADD_KB_ENTRY, etc. The philosophy is a **flywheel**: LLM proposes new deterministic artifacts → human reviews → committed to codebase → next run handles patterns deterministically (cheaper, faster, reproducible).

### tuvium-operabench: Prompt Parameterization Done Right

OperaBench compares 7 AI agent orchestration approaches using opera generation. Its prompt infrastructure demonstrates the pattern:
- `KnowledgeLoader` assembles KB bundles (separate writer vs. judge knowledge)
- `OperaPromptBuilder` with naive/informed factories — prompt stays constant, knowledge varies
- 7 experimental variants with controlled variable isolation
- Formal learnings capture per step via Forge methodology

**Key hypothesis (H5, strongly supported)**: Knowledge reduces per-step reasoning burden but does NOT eliminate the need for orchestration. Two-layer value: Layer 1 (orchestration reliability) + Layer 2 (domain knowledge). Both needed.

### refactoring-agent: JIT Navigation at Scale (148 Fixtures, 100% Pass)

The refactoring-agent proves the JIT context pattern at scale:

1. `fixture.json` carries `knowledgeRefs` (absolute paths to KB files)
2. `PromptBuilder` tells the agent: "Read the knowledge stores listed below before acting"
3. Knowledge stores have `index.md` routing tables (3KB entry point → detail files totaling 85KB)
4. Agent uses Read/Glob/Grep tools to navigate at runtime
5. Agent reads only what's relevant to the specific code it's modifying

**Design philosophy**: Knowledge stored as markdown files on disk, NOT injected into system prompt. Agent explores with file tools at runtime. Index files provide routing to detail files. Scales without token overhead. Vendor-independent (works with any LLM client that has file access tools).

**Result**: Developer-task framing + JIT KB navigation achieved 100% pass rate on 148 fixtures. Haiku matched Sonnet at 1/10th cost when given KB access. The KB was the differentiator, not the model.

---

## Part 3: How This Maps to the Coverage Experiment

### The Core Principle: KB Is the Lever, Not the Prompt

| Improvement lever | Cost to iterate | Scalability | Overfitting risk |
|---|---|---|---|
| **KB files** (markdown on disk) | Low — edit a file | High — forkable, version-specific, team-customizable | Low — scoped by design |
| **Prompt text** (inline rules) | Medium — monolithic edits | Low — hard to modularize | **High — proven to overfit** |
| **Tools** (deterministic pre-processing) | High — write code | High — reusable across agents | None |
| **Model** (upgrade to stronger model) | Highest — cost/latency tradeoff | Low — no tuning knob | None |

After each experiment run, the diagnostic feedback loop should primarily drive **KB refinements**, not prompt text changes. If the agent uses `@SpringBootTest` instead of `@WebMvcTest`, the fix is to sharpen `spring-test-slices.md`, not to add another `BAD:` example to the prompt.

### How knowledgeFiles Should Work Mechanically

The `knowledgeFiles` field in `experiment-config.yaml` controls **which KB files are present in the agent's workspace** before execution. The prompt (v2-with-kb.txt) stays identical across KB variants. The only independent variable is KB breadth.

**variant-b: Coverage Mechanics Only (Universal Guidance)**

Copy only the 3 coverage-mechanics files into `knowledge/`. No `index.md`, no `spring-testing/`. The agent gets:
- What coverage means, meaningful vs. vanity (coverage-fundamentals.md)
- JaCoCo plugin setup and report navigation (jacoco-patterns.md)
- Test slice decision tree: `@WebMvcTest` vs `@DataJpaTest` vs plain JUnit (spring-test-slices.md)

This tests whether **universal testing guidance** (applicable to any Spring project) improves over the hardened prompt alone.

**variant-c: Full KB with JIT Navigation (Technology-Specific Guidance)**

Copy the full `knowledge/` tree including `index.md` and `spring-testing/`. The agent reads `index.md` first, which routes to technology-specific files based on what the production code contains:
- REST controller → `mvc-rest-testing-patterns.md`
- JPA repository → `jpa-testing-cheatsheet.md`
- Secured endpoints → `security-testing-patterns.md`
- WebFlux reactive → `webflux-testing-patterns.md`
- WebSocket/STOMP → `websocket-stomp-testing-patterns.md`

This tests whether **JIT navigation to technology-specific patterns** adds value beyond universal guidance. The refactoring-agent proved this pattern: knowledge stores with routing tables outperform flat KB dumps.

**The ablation is clean**:
- **v0 → variant-a (control → hardened)**: Does prompt engineering help?
- **variant-a → variant-b (hardened → hardened + universal KB)**: Does KB injection help?
- **variant-b → variant-c (universal KB → full routed KB)**: Does technology-specific JIT KB help?

Each step isolates one variable. Don't blur these boundaries.

### The v1 → v2 delta is the whole experiment

The hardened prompt (v1) is essentially the October 2025 prompt rewritten: expert persona, process steps, good/bad examples, constraints — all inline text. The v2 prompt swaps inline rules for "read the knowledge/ directory." **The delta between variant-a and variant-b is the central measurement** — it tests whether JIT KB navigation produces better adherence than stuffing rules into the prompt.

Don't blur that boundary. Keep v1 self-contained (no KB references) and v2 lean (delegate to KB). The temptation will be to keep adding rules to v1 "just in case" — resist it.

---

## Part 4: What NOT to Do When Iterating

### Don't add rules to the prompt that belong in KB files

If variant-a scores poorly because the agent tests record classes, the fix is NOT to add `DO NOT test record classes` to v1-hardened.txt. That rule already exists in `common-gaps.md`. The correct response is:
- variant-a's poor score is **expected** — it doesn't have KB access
- Check whether variant-b/c avoided the problem — if yes, the KB mechanism works
- If variant-b/c also failed, sharpen the KB file (make the guidance more prominent, add examples)

### Don't keep accumulating inline anti-patterns

The October 2025 prompt grew to include:
- `BAD: assert greeting.id() == 1`
- `BAD: assertEquals(1, greeting.id())`
- `GOOD: assertThat(greeting.id()).isEqualTo(1)`
- `DO NOT use plain assert statements (Java keyword)`
- `DO NOT write tests for main() methods or application startup`
- `DO NOT use PowerMock or reflection hacks`

Every one of these is a domain fact that belongs in a KB file, not inline prompt text. The hardened prompt (v1) intentionally contains some of these to measure the "prompt engineering" approach against the "KB" approach. But after the experiment runs, further refinement should happen in KB files.

### Don't make v2-with-kb.txt variant-specific

The v2 prompt should remain a generic "read the KB and follow it" instruction. If variant-b and variant-c use different prompts, you've introduced a confounding variable. The **only** difference between them should be which files exist in `knowledge/`.

---

## Part 5: Post-Run Iteration Protocol

After each experiment run, classify failures using the diagnostic framework:

| Failure type | Evidence | Action | Cost |
|---|---|---|---|
| **KB gap** | Agent didn't know a pattern (e.g., used MockMvc on Boot 4+ instead of RestTestClient) | Add/refine KB file | Low |
| **Orchestration gap** | Agent knew the pattern but applied it wrong (e.g., read the KB but still used @SpringBootTest) | Restructure prompt process steps | Medium |
| **Tool gap** | Agent spent turns doing mechanical work (e.g., manually configuring JaCoCo) | Build a pre-processing tool | High |
| **Model gap** | Agent hallucinated APIs or couldn't follow instructions | Try stronger model | Highest |

**Iterate in cost order**: KB first, then orchestration, then tools, then model. This is the flywheel from `tuvium-experiment-driver`'s `DiagnosticAnalyzer` — promote LLM-discovered patterns into deterministic artifacts (KB files, tools) so future runs handle them cheaper and more reliably.

### The Flywheel in Practice

Run 1 (baseline):
1. Agent uses `@SpringBootTest` for controller test on gs-rest-service
2. Judge flags: "slice usage" score 0.3
3. Diagnostic: KB_GAP — `spring-test-slices.md` has the decision tree but no Boot 4+ specific guidance
4. Action: Add Boot 4+ section to `spring-test-slices.md` with `RestTestClient` example
5. Re-run variant-b/c → score improves

Run 2 (refined KB):
1. Agent uses `@WebMvcTest` correctly but MockMvc instead of RestTestClient (Boot 4+)
2. Judge flags: "assertion quality" score 0.6
3. Diagnostic: KB_GAP — `mvc-rest-testing-patterns.md` needs Boot 4+ RestTestClient examples
4. Action: Add version-conditional guidance to the MVC testing file
5. Re-run → score improves

Run 3 (stable):
1. Agent follows KB correctly across all 5 guides
2. Diagnostic: no gaps or only STOCHASTICITY_GAP
3. Action: Freeze KB, graduate agent

Each cycle refines the KB, not the prompt. The prompt is stable infrastructure; the KB is the tunable policy layer.

---

## Part 6: Connection to the Graduation Artifact

The experiment's graduation artifact (from VISION.md) is not just "the best agent." It's a **knowledge-driven agent architecture with a reference KB and calibration loop**:

1. **Reference KB**: The `knowledge/` directory, validated by the experiment to produce reliable behavior
2. **Calibration loop**: Run agent → judge → classify failures → refine KB → re-run
3. **Forkability**: Any team can substitute their own idioms into the KB and re-run the loop

This is the thesis in action: "Knowledge + orchestration > model." The experiment proves the mechanism. The KB is the portable, team-customizable artifact that makes it practical.

---

## Summary Directive

The `knowledgeFiles` field controls which KB files are copied into the workspace. For variant-b, copy only the 3 coverage-mechanics files (no index.md, no spring-testing/). For variant-c, copy the full knowledge/ tree including index.md and spring-testing/. The v2-with-kb.txt prompt stays identical for both — the only independent variable is KB breadth. Don't add rules to the prompt that belong in KB files. After runs, iterate on KB content, not prompt text.
