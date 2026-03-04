# Design Brief: Experiment Run Composition & Versioning

## Problem

A "complete experimental run" (all variants × all items) rarely happens in one clean invocation. Variants run separately, on different machines, get re-run when stale. Today we have Sessions (one invocation) but no concept grouping sessions into a logical experiment run.

The ETL handles this with `--session s1 --session s2` merge, but that's ad-hoc — the composition isn't recorded anywhere durable.

## Missing Domain Concept: Campaign / Sweep

### What we have
```
Experiment (fixed name)
  └─ Session (one invocation)
      └─ Variant → Items
```

### What we need
```
Experiment
  └─ Campaign (logical run: "all 5 variants on getting-started guides")
      └─ Session(s) that contribute variant results
          └─ Variant → Items
```

A Campaign would:
- Declare expected variants (from experiment-config.yaml)
- Track which session(s) contributed each variant's results
- Know when it's "complete" (all variants covered)
- Support incremental assembly from partial runs
- Be the unit the analysis pipeline operates on

### Prior art to research
- **Weights & Biases Sweeps**: hyperparameter sweep = group of runs. W&B also has "Groups" for arbitrary run grouping.
- **W&B Weave**: newer evaluation/tracing product — may have different composition model
- **MLflow Experiments**: groups runs under an experiment, with tags for sub-grouping
- **Optuna Studies**: study = group of trials with a shared objective

## Versioning Gap: What Changed Between Runs?

We version some inputs but not others:

| Input | Versioned? | How |
|-------|-----------|-----|
| Knowledge base | Yes | Git hash recorded |
| Prompt | Partially | Filename has v0/v1/v2 suffix, but no hash or content snapshot |
| Model | Yes | Recorded in result JSON |
| Judge config | No | Jury wiring is in code, not recorded |
| Dataset | No | items.yaml changes aren't tracked per-run |
| experiment-config.yaml | No | Not snapshotted per-run |

### Questions
- Should the Campaign/Session record a snapshot of the experiment config?
- Should prompt content be hashed and stored (not just filename)?
- Should the jury configuration be serialized into run metadata?
- Is git commit hash sufficient as a proxy for "what code/config was used"?

## Action Items
- [ ] Research W&B Sweeps, Weave, and MLflow experiment grouping models
- [ ] Design Campaign concept for experiment-driver (or determine if Session.metadata suffices)
- [ ] Decide on input versioning strategy (snapshot vs git hash vs explicit version fields)
