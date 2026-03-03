# Step 2.2b Learnings: Wire Agent Exhaust Capture

## What Was Done

Wired end-to-end agent exhaust capture across 4 repos so `InvocationResult` contains full `PhaseCapture` data (tool calls, thinking blocks, tokens, cost, session metadata).

## Key Decisions

1. **SessionLogParser consumes iterator directly** — rather than collecting messages first. Added `TeeingIterator` inner class for backward-compatible `messageListener` support (wraps iterator to forward each message to listener before yielding to parser).

2. **PhaseCapture stored in providerFields** — `AgentResponseMetadata` extends `HashMap<String, Object>`, so `phaseCapture` goes into providerFields alongside `inputTokens`, `outputTokens`, `thinkingTokens`, `totalCostUsd` as individual keys too (for consumers that want simple values without pulling full capture).

3. **Typed accessor pattern** — `AgentClientResponse.getPhaseCapture()` follows existing `getJudgment()`/`getVerdict()` pattern with `@SuppressWarnings("unchecked")` generic return.

4. **Coordinate consolidation** — `com.tuvium:claude-sdk-capture` → `io.github.markpollack:claude-code-capture`. Total 8 files updated (5 main + 3 test, one had inline FQN reference).

## Gotchas

- **Test files have imports too**: The initial experiment-core install with `-DskipTests` succeeded, but actual compilation still failed because test files had old `com.tuvium.claude.capture` imports. One test file had an inline fully-qualified `com.tuvium.claude.capture.PhaseCapture` reference (not an import statement) that needed separate fixing.

- **Prompt log truncation was cosmetic only**: The `Math.min(50, ...)` in `DefaultClaudeSyncClient` was only truncating the log message, not the actual prompt sent to the agent. But it was confusing during debugging.

## Repos Modified

| Repo | Files Changed |
|------|---------------|
| `claude-agent-sdk-java` | `DefaultClaudeSyncClient.java` |
| `agent-client` | `ClaudeAgentModel.java`, `AgentClientResponse.java` |
| `tuvium-experiment-driver` | `experiment-core/pom.xml` + 8 Java files (imports) |
| `code-coverage-experiment` | `CodeCoverageAgentInvoker.java` |

## Verification

- `code-coverage-experiment`: 21 tests pass
- `experiment-core`: 372 tests pass
- `agent-client`: full reactor build succeeds
- Smoke test with actual agent run still pending (Step 2.2)
