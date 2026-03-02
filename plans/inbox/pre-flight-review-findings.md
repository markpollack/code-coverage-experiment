# Pre-Flight Review Findings — Judge Design & Experiment Validity

> **Source**: Research partner review session, 2026-03-02
> **Reviewed**: `judge-design-v5-review.md` against full Tuvium research corpus (thesis, publication strategy, competitor dossier, experiment-driver architecture)
> **Method**: Rudolf Weiss test — "three ways the experiment is lying to you"

---

## Finding 1: Judge circularity — grading on the answer key

**Problem**: The judge prompt is authored by reading the KB. Variant-c reads the same KB at runtime. The judge is therefore testing "did the agent use the material I gave it?" rather than testing objective quality independently.

**Precise restatement**: The circularity isn't about whether the criteria are good (using `@DataJpaTest` IS better than `@SpringBootTest` for repository tests). The problem is that you can't distinguish "the agent learned from the KB" from "the agent already knew this from training data." If variant-a also uses `@DataJpaTest` because the model saw enough Spring testing examples in training, the KB didn't cause the improvement.

**Resolution — Option B (split scoring)**:

Report two separate score dimensions:

| Dimension | Source of truth | Circularity risk |
|-----------|----------------|------------------|
| **Functional correctness** | Compile + pass + coverage delta (deterministic) | None |
| **Practice adherence** | KB-derived criteria (LLM judge) | Intentional — that's the point |

The framing becomes:

> "All variants produce compiling, passing tests. The knowledge-informed variants additionally follow prescribed Spring testing practices — measured by a fixed rubric derived from the team's knowledge base."

This reframes circularity as a feature: **measuring adherence to a standard using that standard as the rubric is how all compliance testing works.** The product story is "fork the KB, add your team's idioms, the agent follows them." The judge checks adherence to YOUR standards.

### Impact on TestQualityJudge implementation

- The judge should produce two clearly separated outputs:
  1. **Functional score**: deterministic (compile + pass + coverage ≥ threshold) — this is the T0/T1 tier
  2. **Adherence score**: LLM-evaluated against KB-derived criteria — this is the T3 tier
- Do NOT combine these into a single composite score. Report them separately.
- The adherence criteria should be labeled as "practice adherence" in the judge prompt, not "quality" — honest framing matters for later publication.

### Impact on judge prompt authoring

When writing `prompts/judge-quality.txt`:
- Frame criteria as "adherence to prescribed Spring testing practices"
- It's fine that the criteria come from the KB — that's the experimental design
- But avoid criteria that ONLY the KB could teach (like internal project conventions). Prefer criteria that reflect genuine Spring testing best practices that happen to be in the KB.

---

## Finding 2: Simple targets are fine for bootstrap — plan the progression

N=5 Getting Started guides are trivially simple. The KB is overkill. Ceiling and floor effects are likely.

**This is accepted and intentional.** These are bootstrap runs to calibrate instrumentation. The progression:

1. **Now**: 5 Getting Started guides — calibrate judge, KB pipeline, exhaust capture
2. **Next**: Pet Clinic + harder repos — genuine complexity where KB matters
3. **Later**: Cross-model comparison (Haiku+KB vs Opus/no-KB)

The simple targets have an advantage: past experience shows simple prompts still fail even here, so there should be signal even at this level. And when the experiment moves to complex targets, the adherence gap between variants should widen because the projects actually need the practices the KB teaches.

---

## Finding 3: Current experiment proves "knowledge helps," not "knowledge > model"

The thesis is "knowledge + orchestration > model." The current experiment holds the model constant (all Haiku) and varies knowledge. It doesn't compare against a stronger model.

**This is accepted and deferred.** The cross-model comparison (Haiku+KB vs Opus/no-KB) comes in a later iteration. For now, bootstrapping the framework is the priority.

**When the cross-model variant is added**: It's cheap (5 additional runs with Sonnet or Opus using the control prompt). It transforms the experiment from "knowledge helps" into "knowledge + cheap model beats expensive model."

---

## Finding 4: Two-experiment strategy — different claims, different evidence

The code-coverage experiment and the IR/SWE-bench experiment serve different purposes:

| | Code-Coverage | IR/SWE-bench |
|---|---|---|
| **Primary metric** | Practice adherence (KB-derived) | Resolve rate (external ground truth) |
| **Circularity risk** | Present, acceptable | **Absent** — gold patches are independent |
| **Model comparison** | Deferred | Required |
| **Claim scope** | Blog series / methodology demo | Paper-grade evidence |

**Why this matters for the code-coverage experiment**: Don't over-claim. This experiment demonstrates the methodology and calibrates the tooling. The paper-grade "knowledge > model" evidence comes from SWE-bench where resolve rate (deterministic, external ground truth) is the primary metric and there's no circularity at all.

**What code-coverage provides for the paper**:
- Working judge/KB/exhaust pipeline (transfers to SWE-bench)
- Growth story narrative for blog series and talks
- Second domain demonstrating cross-domain generalization
- Calibrated instrumentation before deploying on N=150

---

## Immediate Actions for This Project

1. **TestQualityJudge**: Implement Option B split scoring — functional (deterministic) + adherence (LLM) reported separately
2. **Judge prompt**: Author with explicit "practice adherence" framing, not "quality"
3. **Do not combine** deterministic and LLM scores into a single number
4. **Run the bootstrap** on 5 Getting Started guides — the signal is where variants diverge
5. **Plan expansion**: Pet Clinic next, then harder repos, then cross-model variant
