# Pet Clinic Sweep Findings (2026-03-04)

## Context

Ran 4 variants against spring-petclinic (Spring Boot 4, ~15 production classes, 4 layers: model/repository/service/controller). All single runs (N=1). All variants passed 100%.

## Raw Results

| Variant | Description | T3 | Golden | Eff | Cost | Duration | Tool Calls |
|---------|-------------|-----|--------|------|------|----------|------------|
| variant-a | Hardened prompt, no KB, no planning | 0.867 | 0.655 | 0.685 | $4.19 | 17 min | 69 |
| variant-b | KB injection, single phase | 0.867 | 0.679 | 0.458 | $6.14 | 21 min | 109 |
| variant-d | Two-phase explore→act (flat spec) | 0.800 | 0.706 | 0.167 | $8.10 | 30 min | 117 |
| variant-e | Two-phase Forge plan→act (staged roadmap) | 0.950 | 0.579 | 0.167 | $8.55 | 24 min | 303 |

## Key Findings

### 1. Planning overhead mostly doesn't pay for itself

**variant-a ($4.19, T3=0.867) is the best bang-for-buck by a wide margin.** A well-written prompt with clear process instructions (compile after every batch, fix before proceeding, use correct annotations) gets 87% practice adherence at half the cost of any two-phase variant.

### 2. Flat-spec planning (variant-d) actively hurts quality

variant-d scored T3=0.800 — **worse than variant-a's 0.867** — despite costing 2x as much and taking nearly 2x as long. The explore phase produced a 400-line spec listing 14 test classes with test case tables, but the act phase treated it as a "big blob" — no staged execution, no validation gates, no error recovery protocol. The plan added overhead without adding discipline.

The agent timeline visualization confirms this: variant-d's act phase is an undifferentiated wall of Write-Bash-Write-Bash with no internal structure.

### 3. Forge methodology (variant-e) produced the best T3, but the margin is modest

variant-e's T3=0.950 is the highest we've measured. The TEST-LEARNINGS.md captured genuinely useful findings (Boot 4 package renames, spring-javaformat tab requirement, H2 data loading behavior) that informed later steps. The step-by-step protocol with compile/test validation after each step is visibly more disciplined.

**But 0.950 vs 0.867 is a +0.083 improvement at 2x the cost.** On N=1, this could be noise. It's not the "massive" improvement you'd want to justify the ceremony.

### 4. Golden similarity tells an interesting counter-story

variant-d had the **highest** Golden similarity (0.706) while variant-e had the **lowest** (0.579). The Forge process may produce structurally different tests — valid but organized differently from the reference implementation. This needs investigation: is variant-e's low Golden score because it wrote better-but-different tests, or because the staged approach led it down a different path that missed some patterns?

### 5. KB injection doesn't help on simple-to-moderate projects

variant-b matched variant-a's T3 exactly (0.867) but cost 47% more. The KB reading adds tool calls and tokens without improving outcomes on projects where the model already knows the patterns. This was also true on the Getting Started Guides (Stage 3 finding).

**KB may only help on projects with unusual patterns** the model hasn't seen — proprietary frameworks, uncommon annotations, non-standard test setups.

### 6. Efficiency is identical for both two-phase variants

Both variant-d and variant-e scored Eff=0.167. The planning overhead (explore or Forge plan) consumes tokens and time that tanks the efficiency score regardless of plan quality. The efficiency metric penalizes the planning cost itself, not just wasted recovery cycles.

## Honest Assessment

**The data does not strongly support investing in planning structure for code coverage tasks.** A good prompt (variant-a) gets you 87% of the way there at the lowest cost. The Forge methodology (variant-e) squeezed out an extra 8 percentage points of practice adherence, but at double the cost and with lower Golden similarity.

### Where planning MIGHT help (untested hypotheses)

1. **Harder projects**: Pet Clinic has 15 classes but they're well-structured Spring MVC. Projects with unusual architectures, custom frameworks, or deeply nested dependencies might benefit more from upfront analysis.

2. **Failure recovery**: All 4 variants passed on Pet Clinic. The real test is projects where the unstructured approach fails entirely — timeouts, cascading compile errors, wrong test annotations. The Forge step-by-step protocol would catch these at step boundaries instead of at the end.

3. **Consistency across runs**: N=1 means we're measuring one sample. Structured planning might reduce variance even if it doesn't raise the mean — you'd need 5-10 runs per variant to measure this.

4. **Cross-model transfer**: Forge methodology might help weaker models (Haiku) more than Sonnet, which already knows Spring testing patterns well enough to produce good results with just a prompt.

### What we should try next

- **Re-run variant-d with the improved prompts** we wrote today (structured spec with execution order, risks, layer-by-layer execution). If improved-d closes the gap to variant-a, then the original prompts were the problem, not the two-phase architecture.
- **Run at N=3 or N=5** on Pet Clinic to measure variance, not just mean.
- **Find a harder benchmark project** where variant-a might actually fail — something with custom frameworks, complex entity graphs, or non-standard test patterns.
- **Measure whether variant-e's learnings file actually prevented errors** — diff the tool-use data to count compile failures per step vs variant-d's compile failures in the blob.

## Data Locations

- Session 20260304-134654: variant-a
- Session 20260304-145558: variant-b
- Session 20260304-151741: variant-d (old prompts)
- Session 20260304-160929: variant-e
- Preserved workspaces: `results/code-coverage-experiment/sessions/{session}/workspaces/`
- Agent timeline: `docs/latex/figures/agent-timeline-petclinic.png`
- Parquet: `data/curated/{runs,item_results,tool_uses,judge_details}.parquet`

## Prompts Used

| Variant | Explore/Plan | Act |
|---------|-------------|-----|
| variant-a | — | `prompts/v1-hardened.txt` |
| variant-b | — | `prompts/v2-with-kb.txt` |
| variant-d | `prompts/v3-explore.txt` (OLD — anemic) | `prompts/v3-act.txt` (OLD) |
| variant-e | `prompts/v4-forge-plan.txt` | `prompts/v4-forge-act.txt` |

Note: variant-d prompts have been rewritten (improved structure) but NOT re-run yet. The results above are from the old prompts.
