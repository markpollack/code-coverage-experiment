# Brief: Experiment Run Archival via GitHub Releases

> **Date**: 2026-03-03
> **Context**: code-coverage-experiment needs a principled way to name, date, and archive experimental runs. Pattern proven in tuvium-knowledge-miner. Domain model exists in agent-journal. Should become a reusable forge-methodology capability.

## Problem

Experimental runs produce large output (results JSON, workspaces, logs, analysis artifacts) that is gitignored. Today these live as UUID-named directories under `results/code-coverage-experiment/{variant}/` with no naming convention, no dating, no metadata envelope, and no portability across machines. On a fresh checkout, the data is gone.

W&B solves this with a cloud service. We need a local-first equivalent using GitHub releases as the storage backend.

## Prior Art

### W&B Core Model (what we're adapting)

W&B organizes experiment data in a clear hierarchy:

| W&B Concept | Purpose | Our Equivalent |
|-------------|---------|----------------|
| **Project** | Groups related experiments | GitHub repository |
| **Run** | Single execution attempt with config (immutable inputs), summary (mutable outputs), history (time-series metrics) | agent-journal `Run` |
| **Run States** | `running → finished/failed/crashed` | agent-journal `RunStatus` |
| **Run Groups** | Logical grouping (e.g., distributed training, cross-validation folds) | Variant grouping |
| **Artifacts** | Versioned file collections linked to runs (type: "dataset", "model", etc.), sequential versioning (v0, v1...), aliases ("latest", "best") | Dated tarballs on GitHub releases |
| **Artifact Lineage** | DAG of run→artifact→run relationships (`logged_by()`, `used_by()`) | Release notes documenting provenance |
| **Config** | Immutable input parameters set at run start | agent-journal `Config` |
| **Summary** | Overwritable output metrics (final state of run) | agent-journal `Summary` |
| **Events/History** | Append-only time-series: LLM calls, tool calls, metrics | agent-journal `events.jsonl` |

W&B's cloud handles storage, versioning, and cross-machine access. We replace that with:
- **agent-journal** for the on-disk domain model (Experiment/Run/Config/Summary/Events/Artifacts)
- **GitHub Releases** for cross-machine portability (dated tarballs as release assets)

### W&B Weave (LLM/agent-specific layer)

Weave adds agent-native concepts on top of core W&B:
- **Ops** — decorated functions that auto-capture inputs/outputs (our `@weave.op` ≈ agent-journal `Call`)
- **Traces** — hierarchical call trees from ops (≈ agent-journal `CallTracker`)
- **Evaluations** — systematic scoring with Datasets + Scorers (≈ our jury/judge system)
- **Datasets** — versioned row collections for eval (≈ our `dataset/items.yaml` + golden tests)

Weave's trace tree and evaluation framework confirm agent-journal's `CallTracker` and event model are on the right track. The missing piece is the **artifact lifecycle**: how completed experiment data graduates from local disk to a durable, portable archive.

### tuvium-knowledge-miner Pattern (proven)

The `corpus-extraction-v1` release on `tuvium/tuvium-knowledge-miner` demonstrates the approach:

- **Three dated tarballs** attached to a single GitHub release:
  - `pytest-extractions-2026-03-01.tar.gz` (2.9 MB) — extraction output
  - `pytest-triage-2026-03-01.tar.gz` (298 KB) — scored/triered corpus
  - `pytest-supplementary-data-2026-03-01.tar.gz` (677 B) — reference data
- **Release notes** document: what's in each tarball, corpus statistics, extraction parameters, and `tar xzf` commands showing exactly where each archive extracts to
- **Naming convention**: `{target}-{content-description}-{YYYY-MM-DD}.tar.gz`
- **Tag convention**: `corpus-extraction-v1` (semantic name, not semver)

## agent-journal Domain Model (already built)

`~/projects/agent-journal/` provides the W&B-inspired on-disk layout:

```
{baseDir}/
├── experiments/
│   └── {experiment-id}/
│       ├── experiment.json          # name, description, tags, createdAt
│       └── runs/
│           └── {run-id}/
│               ├── run.json         # config, status, summary, tags, agentId
│               ├── events.jsonl     # append-only: LLMCall, ToolCall, StateChange, Git events
│               └── artifacts/
│                   └── {name}       # versioned file outputs
```

Key concepts:
- **Experiment** — groups related runs. Has id, name, description, tags.
- **Run** — single execution. Has config (immutable input), summary (overwritable output), events (append-only JSONL), metrics (counters/timers/gauges), artifacts (files). Supports `parentRunId` (sub-runs) and `previousRunId` (retry chains).
- **Events** — sealed type hierarchy: `LLMCallEvent`, `ToolCallEvent`, `StateChangeEvent`, `MetricEvent`, `GitCommitEvent`, `CustomEvent`
- **Call** — hierarchical call tracking via `CallTracker` (agent-loop → turn → tool-call)

Maps directly to W&B: Project = Experiment, Run = Run, `wandb.config` = Config, `wandb.summary` = Summary, `wandb.log()` = events.jsonl, Artifacts = artifacts/.

## What code-coverage-experiment Needs

### Current state (no structure)
```
results/code-coverage-experiment/
├── control/
│   ├── 05aa20bb-....json             # Result metadata (UUID-named, undated)
│   ├── 05aa20bb-.../workspaces/      # Full Maven project state per item
│   └── index.json                    # Append-only run index
├── variant-a/
├── variant-b/
├── variant-c/
└── full-suite-run.log                # 484 KB execution transcript
```
Total: ~110 MB across 4 variants. All gitignored (`results/` in `.gitignore`).

### What's missing

1. **Run naming/dating**: UUIDs are opaque. Need human-readable names with timestamps (like W&B's auto-generated `run-abc123` or user-provided names).

2. **Run metadata envelope**: Each run needs a manifest capturing:
   - Run name and date
   - Variant configuration (which prompt, which KB, which model)
   - Dataset version (which items.yaml)
   - Aggregate results (T0-T3 scores, coverage, cost, duration)
   - Environment (model, Java version, machine)

3. **Archival packaging**: Graduated runs should become dated tarballs on a GitHub release, with extraction instructions.

4. **Lineage**: Which dataset version + which variant config produced which results. W&B tracks this as artifact lineage; we track it in run metadata and release notes.

## Proposed Approach

### Layer 1: Adopt agent-journal layout for run storage

Migrate from flat UUID files to agent-journal's experiment/run hierarchy:

```
.tuvium/experiments/
└── code-coverage-experiment/
    ├── experiment.json
    └── runs/
        ├── full-suite-2026-03-03/           # Named + dated
        │   ├── run.json                     # Config, summary, status
        │   ├── events.jsonl                 # Execution trace
        │   └── artifacts/
        │       ├── control-results.json
        │       ├── variant-a-results.json
        │       ├── variant-b-results.json
        │       ├── variant-c-results.json
        │       └── workspaces/              # Optional: full project state
        └── variant-a-solo-2026-02-28/       # Earlier exploratory run
            ├── run.json
            └── artifacts/
                └── variant-a-results.json
```

### Layer 2: GitHub release archival (the tuvium-knowledge-miner pattern)

When a run is "graduated" (verified, analyzed, worth preserving):

```bash
# Package run artifacts as dated tarballs
tar czf code-coverage-full-suite-2026-03-03.tar.gz \
  -C .tuvium/experiments/code-coverage-experiment/runs/full-suite-2026-03-03 .

tar czf code-coverage-analysis-2026-03-03.tar.gz \
  -C analysis .

# Create GitHub release
gh release create full-suite-v1 \
  --title "Full Suite Run v1 (4 variants x 5 guides)" \
  --notes-file release-notes.md \
  code-coverage-full-suite-2026-03-03.tar.gz \
  code-coverage-analysis-2026-03-03.tar.gz
```

### Layer 3: Forge methodology integration

This pattern should become a reusable forge capability:
- **Concept doc** in `forge-methodology/concepts/`: "Experiment Run Archival"
- **Skill/command**: `forge-archive-run` or similar — packages a completed experiment run as a GitHub release
- **Template**: Release notes template with standard sections (run config, statistics, extraction instructions, provenance)
- **Convention**: All forge eval-agent and research projects use agent-journal layout for run data, with GitHub releases for graduation

## Naming Convention Proposal

Drawing from experimental physics lab notebook conventions:

| Element | Convention | Example |
|---------|-----------|---------|
| **Experiment** | `{descriptive-name}` | `code-coverage-experiment` |
| **Run name** | `{purpose}-{YYYY-MM-DD}` | `full-suite-2026-03-03` |
| **Run tag** | Freeform classification | `baseline`, `production`, `exploratory` |
| **Tarball** | `{experiment}-{run-purpose}-{YYYY-MM-DD}.tar.gz` | `code-coverage-full-suite-2026-03-03.tar.gz` |
| **Release tag** | `{run-purpose}-v{N}` | `full-suite-v1` |
| **Analysis tarball** | `{experiment}-analysis-{YYYY-MM-DD}.tar.gz` | `code-coverage-analysis-2026-03-03.tar.gz` |

## Scope of Work

### For code-coverage-experiment (immediate)
1. **Retrofit existing runs**: Convert the current `results/code-coverage-experiment/` data (4 variants, ~110 MB, UUID-named files) into agent-journal layout while the data is still on disk and the run context is fresh. Map each full-suite run ID to a named run, extract config/summary from result JSON metadata, preserve workspace artifacts. This is time-sensitive — the longer we wait, the harder provenance reconstruction becomes.
2. **Adopt agent-journal layout for new runs**: Future runs (Stage 4 variant-d, Pet Clinic expansion) write directly to agent-journal Experiment/Run structure from the start.
3. Create run manifest for the 2026-03-03 full suite run
4. Package and publish first GitHub release with dated tarballs
5. Document extraction instructions in release notes

### For forge-methodology (reusable capability)
1. Add `concepts/experiment-run-archival.md` — the pattern
2. Add release notes template to `templates/`
3. Consider a `forge-archive-run` skill that automates tarball creation + `gh release create`
4. Update eval-agent and research variant docs to reference this capability

### For agent-journal (domain model)
1. Validate that the existing Experiment/Run/Artifacts model covers the archival use case
2. Consider adding a `graduated` or `archived` run status
3. Consider an artifact manifest that lists what should be tarballed vs. what's ephemeral

## References

- **tuvium-knowledge-miner release**: `gh release view corpus-extraction-v1 -R tuvium/tuvium-knowledge-miner`
- **agent-journal source**: `~/projects/agent-journal/`
- **W&B Runs docs**: https://docs.wandb.ai/guides/runs
- **W&B Artifacts docs**: https://docs.wandb.ai/guides/artifacts
- **W&B Weave**: https://docs.wandb.ai/weave — LLM/agent-specific observability layer; traces + evaluations + datasets
- **W&B Artifact lineage**: https://docs.wandb.ai/guides/artifacts/explore-and-traverse-an-artifact-graph — DAG of run→artifact→run relationships
