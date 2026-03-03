# Step 2.0: Wire ExperimentApp Bootstrap — Learnings

**Completed**: 2026-03-02

## What was done

- Implemented `loadConfig(Path)` — parses `experiment-config.yaml` via SnakeYAML into `ExperimentVariantConfig` with `FileSystemDatasetManager`
- Implemented `main()` — CLI parsing (`--variant <name>`, `--run-all-variants`, `--project-root <path>`), component wiring, dispatch
- Refactored `ExperimentApp` to remove `AgentInvoker` from constructor — per-variant `CodeCoverageAgentInvoker` created in `runVariant()` via `createInvoker(VariantSpec)` (package-private, overridable for Step 2.1 knowledge injection)
- Built `buildJuryFactory(Path)` static method with 4-tier wiring

## Key decisions

### Per-variant invoker via createInvoker() seam

Instead of passing `AgentInvoker` to the constructor, `runVariant()` now calls `createInvoker(variant)` which returns a fresh `CodeCoverageAgentInvoker`. This is a package-private method that Step 2.1 will enhance to inject knowledge files based on variant config. For now, all variants get a no-knowledge invoker.

### Static helper methods for testability

`loadConfig()` and `buildJuryFactory()` are package-private static methods. This keeps `main()` clean and allows future unit testing of config parsing without bootstrapping the full app.

### CoverageImprovementJudge not in installed JAR

The class existed in agent-judge source but wasn't in the installed `0.9.0-SNAPSHOT` JAR. Required re-installing `agent-judge-exec` from local source (`~/community/agent-judge`). This is a pitfall for any new dependency class — always verify the installed JAR matches the source you're reading.

## Component wiring summary

```
main() → loadConfig() → ExperimentVariantConfig
       → buildJuryFactory() → JuryFactory (4 tiers)
       → FileSystemResultStore(results/)
       → ExperimentApp(config, juryFactory, resultStore, projectRoot)
       → dispatch: runVariant(variant) or runAllVariants()
```

## Verification

- `./mvnw compile` — clean
- `./mvnw test` — 11 tests pass (unchanged)
