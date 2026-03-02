# Integrate tuvium-knowledge Spring Testing KB

## Context

The code-coverage-experiment has a local `knowledge/` directory with 4 files focused on coverage mechanics (coverage-fundamentals, jacoco-patterns, spring-test-slices, common-gaps). A much richer Spring testing KB exists at `~/tuvium/projects/tuvium-knowledge/spring/testing/` — 8 files covering JPA, MVC, Security, WebFlux, WebSocket, AssertJ/Mockito idioms, cross-cutting patterns, and Boot 3.x/4.x version awareness. That KB has routing tables designed for JIT context navigation via Glob/Grep/Read.

The experiment thesis is "knowledge + orchestration > model" — the agent should navigate the KB at runtime to build JIT context, not have it all shoved into the prompt.

## What to do

### 1. Reorganize knowledge/ directory

Move the existing 4 local files into a subdirectory for isolation:

```
knowledge/
├── index.md                        ← top-level router (rewrite — see below)
├── coverage-mechanics/             ← local, experiment-owned
│   ├── coverage-fundamentals.md
│   ├── jacoco-patterns.md
│   ├── common-gaps.md
│   └── spring-test-slices.md
└── spring-testing/                 ← symlink (see step 2)
```

### 2. Symlink tuvium-knowledge testing KB

```bash
ln -s ~/tuvium/projects/tuvium-knowledge/spring/testing knowledge/spring-testing
```

This gives the agent access to 8 testing-pattern files with full routing tables, version-aware navigation, and anti-pattern guidance. The symlink target has its own `index.md` with question routing.

### 3. Rewrite knowledge/index.md

The top-level router should tell the agent:

- **Always read** `coverage-mechanics/` upfront — it's small and universally relevant (coverage strategy, JaCoCo config, what not to test)
- **Navigate** `spring-testing/index.md` for testing patterns — use its routing tables to find the right cheatsheet based on what code you're testing (JPA repo? read jpa-testing-cheatsheet.md. REST controller? read mvc-rest-testing-patterns.md. etc.)
- **Detect Boot version** from pom.xml/build.gradle first — each cheatsheet has a Boot 3.x → 4.x section at the bottom

### 4. Update experiment-config.yaml

The variant definitions currently list specific files. Update to reflect the new structure:

- `knowledgeDir` for variant-b/c should point to the restructured paths
- Or: the prompt itself tells the agent to read `knowledge/index.md` and navigate from there (preferred — this is the JIT context thesis)

### 5. Track KB version for reproducibility

Record the git SHA of tuvium-knowledge in experiment results. The KB will improve between experiment cycles — the SHA lets you attribute score deltas to KB changes.

```bash
# At experiment start, capture:
git -C ~/tuvium/projects/tuvium-knowledge rev-parse HEAD
```

Store this in the experiment output alongside variant results. Consider adding it to `KnowledgeManifest.java` if it doesn't already track external KB versions.

### 6. Graduation (future)

When graduating the agent to standalone:

```bash
# Resolve symlinks into real files
cp -rL knowledge/ knowledge-standalone/
```

This produces a self-contained directory with no external dependencies. The standalone agent ships with a frozen KB snapshot.

## What NOT to do

- Don't duplicate KB content — the symlink avoids drift between the authoritative KB and what the experiment uses
- Don't inject all KB files into the prompt — the agent navigates via index.md routing tables at runtime
- Don't clone the eval dataset repos (gs-accessing-data-jpa, gs-reactive-rest-service, etc.) into the KB — those are in the experiment's dataset/ directory and having them in the KB is data leakage
