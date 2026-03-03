# Task: Integrate Pre-Flight Review Findings into Planning Docs

> **Source**: Research partner session, 2026-03-02
> **Input**: `pre-flight-review-findings.md`
> **Output**: Updated VISION.md, DESIGN.md, ROADMAP.md

---

## What to do

Read `plans/inbox/pre-flight-review-findings.md` — it contains a validity review of the experiment design with four findings and concrete decisions. Then update these three files:

### 1. `plans/VISION.md`

The "Fixed quality bar" paragraph (starting "Fixed quality bar, derived from the knowledge base") needs updating:
- Replace the single "quality bar" concept with the two-tier split: **functional correctness** (deterministic: compile + pass + coverage) and **practice adherence** (LLM judge, KB-derived rubric)
- Change "quality" language to "practice adherence" for the LLM judge tier
- The "Knowledge base as configurable policy" paragraph is fine — it already frames the KB as a swappable opinion layer

The "Thesis" section should frame "knowledge + orchestration > model" as the **hypothesis under investigation**, not a proven claim. This experiment demonstrates the methodology; the SWE-bench experiment (separate project) provides paper-grade evidence with external ground truth.

### 2. `plans/DESIGN.md`

The "TestQualityJudge: Fixed Quality Bar from KB" section (~line 40) needs updating:
- Replace the single composite score with two separate dimensions: functional (T0/T1 deterministic) + adherence (T3 LLM). Scores are **never combined** into a single number.
- The "Implementation" line says "Final score is weighted average → NumericalScore.normalized()" — this is now wrong. The judge returns functional pass/fail + per-criterion adherence scores separately.
- Frame the LLM judge criteria as "practice adherence" not "quality"
- The "Why fixed, not adaptive" and "Why static, not runtime KB navigation" rationale sections are still correct — keep them.

The "Knowledge Base as Configurable Policy" section is fine as-is.

### 3. `plans/ROADMAP.md`

- The overview line says "Demonstrate that knowledge injection > prompt engineering > model choice" — soften to "Investigate whether..." or "Test the hypothesis that..."
- If Step 1.4 (TestQualityJudge) has implementation details, update to reflect split scoring
- Add a note to Stage 2 or Stage 3 about planned future iterations: Pet Clinic + harder repos, cross-model variant (Haiku+KB vs Opus/no-KB)

### What NOT to change
- `plans/PITCH.md` — already updated
- The diagnostic feedback loop section in DESIGN.md — still correct
- The KB structure/forkability sections — still correct
- Don't add new stages or restructure the roadmap — just update the language and judge design details within existing steps
