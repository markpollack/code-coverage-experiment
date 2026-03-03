# Step 1.5: Stage 1 Consolidation — Summary

**Completed**: 2026-03-02

## What Stage 1 built

| Step | Deliverable | Tests |
|------|-------------|-------|
| 1.0 | VISION.md, DESIGN.md, ROADMAP.md; project scaffolded from forge template | — |
| 1.1 | `CodeCoverageAgentInvoker` — baseline/final JaCoCo measurement, agent invocation | — |
| 1.2 | 3 prompt files, 13 KB files (coverage-mechanics + spring-testing), experiment-config.yaml (4 variants) | — |
| 1.3 | 5 dataset items (Spring Getting Started guides), materialize.sh, dataset.json manifest | 10 guide tests |
| 1.4a | `agent-journal` repo (journal-core + claude-code-capture), messageListener in agent-client | 307 (across repos) |
| 1.4 | `TestQualityJudge.java`, 6-criteria rubric prompt, traceability doc | 11 unit tests |

## Design evolution

The judge design went through 5 rounds of review (v1–v5), each tightening the approach:

- **v1**: `LLMJudge` subclass, single ChatClient call → rejected (can't navigate files)
- **v2**: Agent-based, CompletableFuture timeout, 4 criteria → timeout dropped (native support), criteria refined
- **v3**: Copy workspace, fix prompt for Spring guides, mock fluent chain → workspace copy deferred
- **v4**: Verify workingDirectory scope, confirm read-only tools → all confirmed in source
- **v5**: Fixed quality bar (one static rubric for all variants), KB as forkable policy layer, 6 criteria from 13 KB files

The critical pivot was from "judge adapts per-variant" to "judge applies a fixed bar derived from KB authorship." This means the experiment measures whether variants produce code that meets a predetermined standard, not whether the judge can be coached.

## Readiness for Stage 2

**Infrastructure complete**:
- 4-tier jury wired (T0-T2 deterministic from agent-judge-exec, T3 agent-based custom)
- 5 dataset items verified (compile + test)
- 4 variant configs defined (control, prompt-improved, KB-3, KB-4)
- Exhaust capture pipeline end-to-end (messageListener → SessionLogParser → PhaseCapture → journal events)

**Known unknowns going into Stage 2**:
- Judge latency per evaluation (budget: 2-3 min per item per variant = ~60-75 min total for T3 alone)
- Whether `gs-securing-web` (5 existing tests) will show meaningful coverage *preservation* failures
- Whether the rubric's 0.5 threshold produces meaningful PASS/FAIL discrimination across variants
- Token/cost per judge invocation (tracked via exhaust capture, no estimate yet)
