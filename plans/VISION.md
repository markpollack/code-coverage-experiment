# Vision: Code Coverage Experiment

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

**Fixed quality bar.** All variants are measured against the same judge — a fixed definition of what good Spring Boot tests look like. The judge doesn't adapt to what the agent was told; it asks "did the agent get there?" regardless of how. This rewards the LLM's built-in knowledge: if the model already knows `@WebMvcTest` without being told, it scores. The interesting finding is how much knowledge injection adds *on top of* what the model already knows.

**Attributed improvement.** When a variant scores higher, the growth story explains *why* — which variable changed, and what that variable contributed. This follows the pattern established in the refactoring-agent experiment loop: scores have reasons, and those reasons map to actionable levers (write a better prompt, inject more knowledge, choose a better model).

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

## Scope

**In scope:**
- 4 variants (control, hardened prompt, hardened+3KB, hardened+4KB)
- 5 Spring Boot Getting Started guides as benchmark dataset
- JaCoCo line and branch coverage as primary metrics
- CascadedJury evaluation (build success, coverage preservation, coverage improvement, test quality)
- Growth story with per-variant attribution (what changed, what improved, why)

**Out of scope:**
- Model comparison (Claude vs Gemini) — deferred to bake-off phase
- MiniAgent contrast — separate experiment
- Production agent extraction — deferred to graduation phase
