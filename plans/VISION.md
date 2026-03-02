# Vision: Code Coverage Experiment

## Thesis

**Knowledge + orchestration > model.** To get specific, reliable behavior from an AI agent, you need domain knowledge and proper orchestration — not just a bigger model. A capable LLM has general training but not a refined knowledge base tuned for a specific task. The industry default ("use the frontier model and prompt it well") is the least tunable lever. Knowledge and orchestration are fast iteration cycles that compound.

The end goal: a knowledge-driven agent architecture where even mid-tier models can produce high-quality, standards-compliant test suites — because the knowledge base, not the model's training data, governs behavior.

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

**Fixed quality bar, derived from the knowledge base.** The judge prompt is generated from the KB — the KB is the single source of truth for what "good" looks like. The judge applies this bar identically to all variants. It doesn't adapt to what the agent was told; it asks "did the agent get there?" regardless of how. This rewards the LLM's built-in knowledge: if the model already knows `@WebMvcTest` without being told, it scores. The interesting finding is how much knowledge injection adds *on top of* what the model already knows.

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

## Planned Follow-On: Cross-Model Validation

To fully validate "knowledge + orchestration > model", a follow-on experiment holds the KB constant and varies the model — run the best variant's prompt+KB against a smaller model (Haiku, Qwen, etc.) and compare with variant-a on the frontier model. Even one such comparison would generate evidence for whether knowledge injection compensates for model capability. This is out of scope for the current run but should be designed in from the start.

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
