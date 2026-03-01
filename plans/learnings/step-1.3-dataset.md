# Step 1.3: Populate and Verify Dataset

**Completed**: 2026-03-01

## Summary

Cloned 5 Spring Getting Started guides, verified all compile and pass tests, converted dataset format from `items.yaml` to experiment-core's `dataset.json` schema, and configured workspace materialization.

## Dataset Items

| Guide | Tests | Existing Coverage | Tags |
|-------|-------|-------------------|------|
| gs-rest-service | 2 pass | Minimal (controller tests only) | rest, web, mvc |
| gs-accessing-data-jpa | 1 pass | Minimal (repository test only) | jpa, data, persistence |
| gs-securing-web | 5 pass | Good baseline (security tests) | security, web, mvc |
| gs-reactive-rest-service | 1 pass | Minimal (router test only) | reactive, webflux, rest |
| gs-messaging-stomp-websocket | 1 pass | Minimal (integration test only) | messaging, websocket, stomp |

## Dataset Format Conversion

The forge scaffolding produced `items.yaml` (flat list with GitHub URLs). The experiment-core framework (`FileSystemDatasetManager`) expects:
- `dataset/dataset.json` — manifest with schema version, item entries pointing to subdirectories
- `dataset/items/{id}/item.json` — per-item metadata (developerTask, tags, knowledgeRefs)
- `dataset/items/{id}/before/` — source code snapshot to work on (copied from guide's `complete/` subdirectory)

The `items.yaml` is retained as documentation but is not consumed by the framework.

## Materialization

- `dataset/materialize.sh` — clones repos into `dataset/workspaces/` (shallow clone), copies `complete/` into `items/{id}/before/`
- `dataset/workspaces/` and `dataset/items/*/before/` are gitignored (generated content)
- Run `./dataset/materialize.sh --verify` to re-materialize and verify builds

## Workspace Preservation

The experiment framework creates temp workspaces initially, but with `preserveWorkspaces(true)` and `outputDir(results/)`, each run's workspaces are preserved at:
```
results/{experimentName}/{experimentId}/workspaces/{itemSlug}/
```
This allows post-hoc analysis of what the agent changed in each iteration.

## Build Tool Notes

- All 5 guides ship with `./mvnw` (Maven Wrapper) — always use `./mvnw` not `mvn`
- Gradle support is planned as a future agent option; Maven-first for the experiment
- JPA testing best practices — candidate for extraction into `knowledge/` for advanced variants

## Observations

- gs-securing-web has the richest existing test suite (5 tests) — good for testing coverage preservation
- Most guides have minimal tests — ideal targets for coverage improvement
- All guides use Spring Boot 4.0.x (latest)
