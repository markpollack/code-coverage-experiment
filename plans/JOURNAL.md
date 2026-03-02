# Project Journal

## 2026-03-01

### Step 1.4 Design Review

**Reviewer**: Claude (web, via uploaded handoff doc at `plans/outbox/step-1.4-review-handoff.md`)
**Process**: Out-of-band manual review (not yet automated in forge methodology)
**Response**: `plans/inbox/design-review.md`

Key feedback:
- Extend `LLMJudge` for now, but consider bypassing for structured output
- Collapse BDD + no-trivial criteria; replace with exception/edge-case coverage
- Include production source alongside test files in prompt (match `FooTest.java` → `Foo.java`)
- Use `NumericalScore.normalized()` (continuous) not `BooleanScore` — preserves gradient
- Risks: JSON parsing brittleness, prompt token size, threshold calibration, ABSTAIN handling in FINAL_TIER

**Critical insight from project owner**: The LLM judge should use Claude Code (agent with filesystem access) not a single `ChatClient` request. The judge needs to navigate the workspace intelligently — follow imports, examine related files, understand project structure. A single prompt stuffed with file contents won't scale and loses the agent's ability to explore.

### Step 1.4 Design Review v2

**Reviewer**: Claude (web, via uploaded `plans/outbox/step-1.4-review-handoff-v2.md`)
**Process**: Out-of-band manual review (not yet automated in forge methodology)
**Response**: `plans/inbox/design-review-2.md`

Key decisions from v2 review:
- **Timeout**: Wrap agent call in CompletableFuture with configurable timeout (default 2-3 min). Timeout → `Judgment.error()`
- **No ABSTAIN**: Never return ABSTAIN from FINAL_TIER. No test files = genuine failure (score 0.0), not "cannot evaluate"
- **Drop naming criterion**: Split weight 50/50 between meaningful assertions and edge-case coverage (naming is subjective, no team convention ground truth)
- **Stronger model for judging**: Use a different (stronger) model than the experiment agent to avoid self-bias. Configurable via `AgentModel` injection
- **Agent prompt**: Final output must be ONLY a JSON object — explicit constraint. Parser looks for outermost `{...}` block
- **Read-only concern**: Check if `ClaudeAgentOptions` supports restricted/read-only mode for the judge agent
- **Testability**: Accept `AgentClientFactory` functional interface instead of `AgentModel` directly to avoid static factory mocking
- **Score clamping**: Clamp criterion scores to [0.0, 1.0] during parsing

Two blockers resolved:
1. ABSTAIN → use FAIL with score 0.0 instead
2. Agent prompt format → constrain to JSON-only output, parse outermost `{...}`

### Step 1.4 Design Review v3 (final)

**Reviewer**: Claude (web, via uploaded `plans/outbox/step-1.4-review-handoff-v3.md`)
**Process**: Out-of-band manual review (not yet automated in forge methodology)
**Response**: `plans/inbox/design-review-3.md`

Final adjustments:
- **Copy workspace to temp dir** before judging — isolate judge from corrupting measured state (session files, build artifacts)
- **Drop CompletableFuture** — use `ClaudeAgentOptions` timeout if available, otherwise simple try/catch on synchronous `run()`
- **Prompt fix**: tell agent "if no direct counterpart exists, evaluate against all production classes in src/main/" — Spring guides don't always follow strict `FooTest` → `Foo` naming
- **Test mock note**: wire full fluent chain (`goal().workingDirectory().run()`) — `AgentClient.goal()` may return a builder, not self

Design approved for implementation.

### Step 1.4 Design Review v4 (final sign-off)

**Reviewer**: Claude (web, via uploaded `plans/outbox/step-1.4-review-handoff-v4.md`)
**Process**: Out-of-band manual review (not yet automated in forge methodology)
**Response**: `plans/inbox/design-review-4.md` (verbal — approved)

Approved with one implementation note:
- **Verify `workingDirectory()` scope**: `ClaudeAgentModel.builder().workingDirectory()` vs `AgentClient.goal().workingDirectory()` — the existing `CodeCoverageAgentInvoker` sets it in both places. Understand why before passing temp dir in only one location. Check agent-client source.

### Source Code Investigation (post-v4)

Investigated `AgentClient` and `ClaudeAgentOptions` source to resolve open items from v4 review.

**Findings**:
1. **`workingDirectory` priority chain** (from `DefaultAgentClient.determineWorkingDirectory()`):
   - Request-level (`goal().workingDirectory(path)`) > goal-level > builder default > cwd
   - For the judge: set on request-level only — it overrides everything else
   - `CodeCoverageAgentInvoker` sets it in both places for safety; judge only needs request-level

2. **`ClaudeAgentOptions.timeout(Duration)`** — confirmed available, default 10 minutes
   - Use `ClaudeAgentOptions.builder().timeout(Duration.ofMinutes(3)).build()` for judge
   - No need for CompletableFuture or external timeout wrapper

3. **Read-only mode** — `ClaudeAgentOptions` supports:
   - `allowedTools(List<String>)` — whitelist specific tools (e.g., `"Read"`, `"Glob"`, `"Grep"`)
   - `disallowedTools(List<String>)` — blacklist specific tools
   - Combined with `yolo(false)` — judge agent cannot write to workspace
   - Recommend: `allowedTools(List.of("Read", "Glob", "Grep"))` with `yolo(false)`

All v4 open items resolved. Design is fully implementation-ready.

### Exhaust / Agent Trail Investigation

**Problem**: The judge needs an audit trail — what files did it read, what tool calls did it make, what reasoning did it follow? Without this we can't verify judge behavior or debug scoring anomalies.

**Findings across 3 layers**:

1. **claude-agent-sdk-java** (SDK): Streams rich `ParsedMessage` objects — `ToolUseBlock` (name, id, input), `ToolResultBlock` (output, errors), `ThinkingBlock`, `ResultMessage` (cost, tokens, turns, sessionId, duration). Full data available.

2. **claude-sdk-capture** (`refactoring-agent/claude-sdk-capture/`): `SessionLogParser` consumes `Iterator<ParsedMessage>` → `PhaseCapture` record (tokens, cost, tool uses, tool results, thinking, duration, sessionId). `BaseRunRecorder` bridges `PhaseCapture` → `tuvium-runtime-core` tracking events. **Problem**: buried in `refactoring-agent` — needs to be promoted to standalone library ("agent-journal").

3. **agent-client** (`ClaudeAgentModel.call()`): Consumes the `ParsedMessage` iterator internally, only keeps concatenated assistant text. `iterate()` and `stream()` also discard tool calls/results/thinking via same `convertMessageToResponse()` bottleneck. **No hook/listener/callback to observe the stream.** This is the gap.

**Decision for TestQualityJudge**: Use `ClaudeSyncClient` directly (SDK level) + `SessionLogParser` to get full `PhaseCapture`. Bypass `AgentClient` abstraction for the judge. This gives us:
- Full tool call trail (what files the judge read)
- Thinking blocks (judge reasoning)
- Cost/token tracking per evaluation
- Session ID for reproducibility

**Longer-term**: Two changes needed in community libraries:
1. Promote `claude-sdk-capture` out of `refactoring-agent` → standalone "agent-journal" library
2. Add `ParsedMessageListener` (or similar) to `ClaudeAgentModel` so agent-client consumers can observe exhaust without data loss

**Additional finding — agent-client Hook system**: `ClaudeAgentModel` does have an event interception mechanism via hooks:
- `@PostToolUse` — fires after each tool call with `toolName`, `toolInput`, `toolResponse`
- `@PreToolUse` — fires before each tool call, can block/modify
- `@Stop` — fires at session end with `transcriptPath` (CLI's on-disk transcript file)
- All hooks carry `sessionId` + `transcriptPath`

This is a partial solution — `@PostToolUse` captures tool events but misses thinking blocks, token usage, cost, and the full message stream. The `transcriptPath` on `@Stop` could recover the full transcript from disk but depends on CLI internals.

**Three approaches for judge exhaust**:
1. **SDK direct** (`ClaudeSyncClient` + `SessionLogParser`): Full data, bypasses `AgentClient`
2. **Hooks** (`@PostToolUse` + `@Stop`): Partial data via `AgentClient`, tool calls captured, transcript file recoverable
3. **Fix agent-client**: Add `ParsedMessageListener` to `ClaudeAgentModel` — right fix, community PR

**Decision for TestQualityJudge**: Start with approach 1 (SDK direct). The `claude-sdk-capture` module already does exactly what we need. Long-term, promote it to `agent-journal` project as a sibling module of `tracking-core`.

**Impact on design**: `AgentClientFactory` interface changes — factory creates a `ClaudeSyncClient` (not `AgentClient`), judge owns the parsing loop via `SessionLogParser`, returns both result text and full `PhaseCapture`. `PhaseCapture` stored in `Judgment.metadata()` for audit trail.

**Architectural note**: `claude-sdk-capture` should be promoted from `refactoring-agent` to a module in `agent-journal` (to-be-renamed `tuvium-runtime-core`). It's the natural home — a `claude-code-capture` module alongside `tracking-core`.
