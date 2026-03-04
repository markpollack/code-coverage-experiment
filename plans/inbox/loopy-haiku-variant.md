# Loopy + Haiku Variant for Code Coverage Experiment

> Written from research-conversation-agent session, 2026-03-04.
> Motivation: DevNexus talk needs "expensive black box vs cheap agent you built" contrast.
> Simplest implementation path — no AgentClient wrapper, no SDK, no subprocess.

---

## Why This Matters

The thesis is `knowledge + structured execution > model`. The strongest proof:

- **Claude Code** (Sonnet, off-the-shelf, ~$0.50/run) vs **Loopy + Haiku** (your own agent, cheap model, good KB, ~$0.02/run)
- If Loopy+Haiku+KB matches or beats Claude Code on code-coverage, that's the headline
- Audience takeaway: "they built their own Claude Code in ~13 Java classes and it competed with the real thing"

---

## What MiniAgent Already Provides

MiniAgent (vendored in Loopy, ~13 classes) is a Spring AI `ChatClient` with an agent loop:

```java
MiniAgent agent = MiniAgent.builder()
    .model(chatModel)                    // Any Spring AI ChatModel — Haiku, Sonnet, Ollama
    .config(MiniAgentConfig.builder()
        .workingDirectory(workspace)
        .systemPrompt(prompt)
        .maxTurns(50)
        .build())
    .sessionMemory()                     // In-memory, preserves context across run() calls
    .build();

MiniAgentResult result = agent.run(task);
// result.totalTokens(), result.toolCallsExecuted(), result.estimatedCost()
```

Tools included: BashTool, FileSystemTools, GlobTool, GrepTool, SubmitTool, TodoWriteTool, TaskTool.

**Session continuity is free**: with `sessionMemory()`, each `run()` call sees the full conversation history. Plan+act is just two `run()` calls on the same instance. No subprocess management, no SDK, no ClaudeSyncClient equivalent needed.

---

## Implementation: LoopyCoverageAgentInvoker

### The Simplest Path

Don't wrap Loopy in AgentClient. Don't write a loopy-agent-sdk. Construct MiniAgent directly in a new invoker class. The experiment-driver already has the template-method pattern for this.

### New Dependencies (pom.xml)

```xml
<!-- Spring AI Anthropic (for Haiku ChatModel) -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-anthropic</artifactId>
</dependency>

<!-- Spring AI Agent Utils (tools: BashTool, FileSystem, Glob, Grep) -->
<dependency>
    <groupId>org.springaicommunity</groupId>
    <artifactId>spring-ai-agent-utils</artifactId>
    <version>0.5.0-SNAPSHOT</version>
</dependency>
```

Spring AI BOM should already be in the dependency management from spring-ai-agent-client. If not, add it.

### Vendoring MiniAgent Classes

Two options:

**Option A — Copy ~5 essential classes** (recommended for speed):
- `MiniAgent.java` — the agent loop wrapper
- `MiniAgentConfig.java` — configuration record
- `MiniAgentResult` — already a record inside MiniAgent
- `BashTool.java` — shell execution (from Loopy's vendored copy)
- `AgentLoopAdvisor.java` + supporting loop classes — the Spring AI advisor that drives the tool call loop

Copy into `io.github.markpollack.experiment.coverage.agent` package. Strip out TUI/interactive/callback code — keep only headless `run()` path.

**Option B — Depend on Loopy as Maven artifact**:
- Requires `mvn install` of Loopy first
- Pulls in tui4j and other TUI deps (unnecessary)
- More coupling than needed

Option A is cleaner. The essential agent loop is ~200 lines of real code.

### LoopyCoverageAgentInvoker.java (~80 lines)

```java
public class LoopyCoverageAgentInvoker extends AbstractCoverageAgentInvoker {

    @Override
    protected AgentResult invokeAgent(InvocationContext context, CoverageMetrics baseline)
            throws Exception {

        Path workspace = context.workspace();
        String model = context.model();  // "claude-haiku-4-5-20251001" or "claude-sonnet-4-6"

        // Create Spring AI ChatModel for Anthropic
        AnthropicApi api = AnthropicApi.builder()
            .apiKey(System.getenv("ANTHROPIC_API_KEY"))
            .build();
        AnthropicChatModel chatModel = AnthropicChatModel.builder()
            .anthropicApi(api)
            .defaultOptions(AnthropicChatOptions.builder()
                .model(model)
                .maxTokens(8192)
                .build())
            .build();

        // Build MiniAgent with session memory (for two-phase support)
        MiniAgent agent = MiniAgent.builder()
            .model(chatModel)
            .config(MiniAgentConfig.builder()
                .workingDirectory(workspace)
                .systemPrompt(context.systemPrompt())
                .maxTurns(80)
                .commandTimeout(Duration.ofSeconds(120))
                .build())
            .sessionMemory()  // enables plan+act in same session
            .build();

        if (context.variant().isTwoPhase()) {
            // Two-phase: explore then act, session memory preserves context
            String explorePrompt = buildPrompt(context.prompt(), baseline);
            MiniAgentResult exploreResult = agent.run(explorePrompt);

            PhaseCapture explore = toPhaseCapture(exploreResult, "explore", explorePrompt);

            String actPrompt = context.actPrompt();
            MiniAgentResult actResult = agent.run(actPrompt);

            PhaseCapture act = toPhaseCapture(actResult, "act", actPrompt);

            return new AgentResult(List.of(explore, act), UUID.randomUUID().toString());
        } else {
            // Single-phase
            String prompt = buildPrompt(context.prompt(), baseline);
            MiniAgentResult result = agent.run(prompt);

            PhaseCapture capture = toPhaseCapture(result, "single", prompt);
            return new AgentResult(List.of(capture), UUID.randomUUID().toString());
        }
    }

    private PhaseCapture toPhaseCapture(MiniAgentResult result, String phase, String prompt) {
        return PhaseCapture.builder()
            .phase(phase)
            .prompt(prompt)
            .output(result.output())
            .status(result.status())
            .totalTokens(result.totalTokens())
            .toolCallsExecuted(result.toolCallsExecuted())
            .estimatedCost(result.estimatedCost())
            .build();
    }
}
```

### Variant Configuration (experiment-config.yaml)

Add new variants:

```yaml
  # Loopy + Haiku — cheap model, same knowledge
  - name: loopy-haiku-control
    agent: loopy
    model: claude-haiku-4-5-20251001
    promptFile: v0-naive.txt
    knowledgeFiles: []

  - name: loopy-haiku-kb
    agent: loopy
    model: claude-haiku-4-5-20251001
    promptFile: v2-with-kb.txt
    knowledgeFiles:
      - index.md

  # Loopy + Sonnet — same model as Claude Code, your own agent
  - name: loopy-sonnet-kb
    agent: loopy
    model: claude-sonnet-4-6
    promptFile: v2-with-kb.txt
    knowledgeFiles:
      - index.md
```

### Dispatcher Update (ExperimentApp.java)

```java
private AgentInvoker createInvoker(VariantSpec variant) {
    if ("loopy".equals(variant.agent())) {
        return new LoopyCoverageAgentInvoker(...);
    } else if (variant.isTwoPhase()) {
        return new TwoPhaseCodeCoverageAgentInvoker(...);
    } else {
        return new CodeCoverageAgentInvoker(...);
    }
}
```

---

## What This Tests

| Comparison | What it isolates |
|-----------|-----------------|
| Claude Code (Sonnet) vs Loopy (Sonnet), same KB | Agent quality: does the off-the-shelf agent outperform a simple loop? |
| Claude Code (Sonnet) vs Loopy (Haiku), same KB | Model vs knowledge: can a cheap model + good KB beat an expensive agent? |
| Loopy (Haiku) control vs Loopy (Haiku) + KB | Knowledge value on a cheap model: does KB help MORE when the model is weaker? |
| Loopy (Haiku) vs Loopy (Sonnet), same KB | Model scaling: is the Sonnet premium worth it when you have good knowledge? |

The DevNexus headline comparison: **Claude Code Sonnet (~$0.50/run) vs Loopy Haiku + KB (~$0.02/run)**.

---

## Exhaust Capture Gap

MiniAgentResult gives us tokens and estimated cost, but NOT the full conversation log (individual messages, tool call details). For the experiment this is acceptable — we get the metrics we need for comparison. Full exhaust capture (à la spring-ai-exhaust) is a future enhancement.

What we capture:
- ✓ Total tokens (input + output)
- ✓ Tool calls executed count
- ✓ Estimated cost
- ✓ Status (completed, turn limit, timeout)
- ✓ Final output text
- ✗ Per-turn token breakdown
- ✗ Individual tool call details
- ✗ Thinking/reasoning content

For the ablation comparison, the aggregate metrics are sufficient.

---

## Sequencing

1. **Copy MiniAgent essentials** (~5 classes) into experiment-driver, headless only
2. **Add Spring AI Anthropic + agent-utils deps** to pom.xml
3. **Write LoopyCoverageAgentInvoker** (~80 lines)
4. **Add loopy-haiku-control variant** to experiment-config.yaml
5. **Smoke test**: `--variant loopy-haiku-control --item gs-rest-service`
6. **Add loopy-haiku-kb and loopy-sonnet-kb variants**
7. **Run full comparison**: all variants × all items
8. **Compare**: Claude Code vs Loopy+Haiku in results table

Steps 1-5 should take one session. The key risk is whether Haiku has enough capability for the code-coverage task — it might struggle with complex test generation. That's data, not a problem.

---

## Why Not AgentClient?

AgentClient wraps external CLI agents via subprocess. Loopy's value here is that it runs **in-process** — same JVM as the experiment-driver. Benefits:

- No subprocess management overhead
- Session continuity via ChatMemory (plan+act is two `run()` calls)
- Direct access to Spring AI ChatModel — swap models in one line
- Token/cost metrics without parsing CLI output
- No agent-journal dependency for exhaust capture

The AgentClient wrapper for Loopy is a separate concern — useful for Spring AI Bench ("bring your agent") but not needed for this experiment. Build it later when bench needs it.

---

## Connection to Talk

Act 4 (The Benchmark) can show this comparison:

> "Claude Code — Anthropic's flagship coding agent. $0.50 per run. Sonnet 4.6."
> "Loopy — 13 Java classes. Spring AI. Haiku. $0.02 per run."
> "Same task. Same judges. Same grading."
> [Show results table]
> "Knowledge and structure beat model. Twenty-five times cheaper."

That's the water cooler moment.
