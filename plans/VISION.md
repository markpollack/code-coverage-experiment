# Vision: Code Coverage Experiment

## Thesis

**Hypothesis: knowledge + orchestration > model.** To get specific, reliable behavior from an AI agent, you need domain knowledge and proper orchestration — not just a bigger model. A capable LLM has general training but not a refined knowledge base tuned for a specific task. The industry default ("use the frontier model and prompt it well") is the least tunable lever. Knowledge and orchestration are fast iteration cycles that compound.

This experiment demonstrates the methodology and calibrates the tooling. It proves "knowledge injection causes agents to follow prescribed practices." The stronger claim — that knowledge + cheap model beats expensive model — requires a cross-model comparison and harder targets, planned as follow-on iterations. Paper-grade evidence for "knowledge > model" comes from the separate SWE-bench experiment, where resolve rate against gold patches provides external ground truth with zero circularity.

The end goal: a knowledge-driven agent architecture where even mid-tier models can produce standards-compliant test suites — because the knowledge base, not the model's training data, governs behavior.

## Problem Statement

AI agents can improve JUnit test coverage on Spring Boot projects, but the impact of prompt engineering vs. domain knowledge injection is not well understood. We need ablation data showing which factor (prompt quality, knowledge breadth, knowledge depth) drives the most improvement.

## Experimental Approach

**One variable at a time.** Each variant changes exactly one dimension from the previous variant, so improvements can be attributed to a specific cause:

```
control (naive prompt, no KB)
  → variant-a: changed PROMPT only         → delta = prompt hardening effect
  → variant-b: added KNOWLEDGE (3 files)   → delta = knowledge injection effect
  → variant-c: added KNOWLEDGE DEPTH (+1)  → delta = knowledge depth effect
```

This ablation design means every score delta has an explanation: was it the prompt, the knowledge, or the depth of knowledge? The growth story is a causal narrative, not just a chart.

**Two evaluation dimensions, reported separately.** Every variant is scored on two independent dimensions that are never combined into a single number:

- **Functional correctness** (deterministic, T0–T2 judges): Does the code compile? Do the tests pass? Does coverage meet the threshold? Binary, unimpeachable, no subjectivity.
- **Practice adherence** (LLM-evaluated, T3 judge): Does the agent follow prescribed Spring testing practices? Did it use the narrowest test slice? Are assertions checking domain-meaningful values? Are Boot 4 idioms used on a Boot 4 project? This is a fixed rubric authored from the KB and applied identically to all variants.

The framing: all variants should produce compiling, passing tests. The knowledge-informed variants should *additionally* follow the prescribed practices. The practice adherence rubric is intentionally derived from the KB — measuring adherence to a standard using that standard as the rubric is how all compliance testing works. The product story is "fork the KB, add your team's idioms, the agent follows them."

**JIT context, not prompt stuffing.** The agent doesn't get the entire KB shoved into its prompt. It navigates a structured knowledge base at runtime using file tools (Read, Glob, Grep) — reading a 3KB routing index, then selectively loading only the cheatsheets relevant to the code it's testing. This is the same JIT context pattern proven in the refactoring-agent, where Haiku + knowledge stores beat Sonnet without them. It scales: the agent pays token cost only for what it actually needs.

**Knowledge base as configurable policy.** The KB is not a fixed answer key — it's a swappable opinion layer. The experiment validates the *mechanism* (does KB injection produce measurable adherence?), not the *opinions* (are these the right idioms?). Any team can fork the KB, get a matching judge, and calibrate their own agent. JPMorgan substitutes their idioms ("all repository tests must use Testcontainers not H2", "MockMvc is banned in favor of RestAssured"), runs the experiment loop against their codebases, and gets an agent tuned to their standards — without retraining, without prompting a frontier model to guess their preferences.

**Attributed improvement with diagnostic feedback.** When a variant scores low, the evidence strings in the judge output diagnose *why* — and that maps to a specific improvement lever. This follows the pattern established in the refactoring-agent `AIAnalyzer`, which categorizes gaps across runs:

| Lever | Signal | Fix | Iteration cost |
|-------|--------|-----|----------------|
| Knowledge gap | Low score on a criterion the KB addresses | Add or clarify a knowledge file | Low — fast |
| Orchestration gap | High tool usage, retries, wasted exploration | Restructure prompt, add planning steps | Medium |
| Tool gap | Agent repeatedly reconstructs computable information | Build a dedicated tool | High — but reusable |
| Model gap | Consistent failures despite good KB and orchestration | Try a more capable model | Highest — least tunable |

The experiment loop gives you data to know *which* lever to pull. This is what makes the architecture practical: you iterate on the cheap levers first.

## Hypothesis

Domain knowledge files injected into the agent's context will produce larger coverage improvements than prompt engineering alone. Specifically:
- Hardened prompts (v1) will improve over naive prompts (v0) by ~15pp
- Adding 3 knowledge files (v2+KB) will improve over hardened prompts by ~17pp
- Adding the 4th knowledge file (common-gaps) will add ~3pp more

## Success Criteria

- [ ] Agent achieves ≥80% line coverage on majority of benchmark items (variant-b or variant-c)
- [ ] Knowledge ablation shows measurable improvement (variant-b > variant-a by ≥10pp)
- [ ] Growth story demonstrates progressive improvement across all 4 variants with attributed causes
- [ ] Results reproducible across 5 Spring Getting Started guides

## Planned Iterations

This experiment is the first in a progression:

1. **Now**: 5 Getting Started guides — calibrate judge, KB pipeline, exhaust capture, growth story
2. **Next**: Pet Clinic + harder repos — genuine complexity where the KB advantage matters and ceiling effects are unlikely
3. **Next**: Cross-model variant (Haiku+KB vs Sonnet/Opus with no KB) — the headline comparison that transforms "knowledge helps" into "knowledge + cheap model beats expensive model"
4. **Later**: SWE-bench Lite (N=150) — paper-grade evidence with external ground truth (resolve rate against gold patches), zero circularity

## Scope

**In scope:**
- 4 variants (control, hardened prompt, hardened+3KB, hardened+4KB)
- 5 Spring Boot Getting Started guides as benchmark dataset
- JaCoCo line and branch coverage as primary metrics
- CascadedJury evaluation (build success, coverage preservation, coverage improvement, test quality)
- Growth story with per-variant attribution (what changed, what improved, why)
- Diagnostic gap analysis per the feedback loop levers

**Out of scope:**
- Cross-model comparison (same KB, different models) — planned follow-on
- MiniAgent contrast — separate experiment
- Production agent extraction — deferred to graduation phase

## Graduation Artifact

What gets graduated in Step 3.1 isn't just "the best coverage agent." It's a **knowledge-driven agent architecture with a reference KB and calibration loop**. The reference KB encodes Spring testing best practices, but the architecture is the durable contribution — the loop that lets any team validate and improve an agent for their context.
