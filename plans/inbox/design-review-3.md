V3 is clean and implementation-ready. The design decisions from v2 have all landed correctly — the functional interface for testability, FAIL instead of ABSTAIN for no-test-files, timeout wrapping, score clamping, and the JSON-only prompt constraint are all present and correct. The test suite is notably thorough for what it covers.

**On your two open items:**

**1. Read-only agent mode** — Copy the workspace to a temp dir. Don't rely on "the judge has no incentive to modify files." The risk isn't intentional modification — it's that Claude Code in `--yolo` mode running a `find`/read pass might occasionally write a `.claude` session file, update a cache, or trigger a build tool that creates `target/` artifacts. Any of those would corrupt the workspace state that your deterministic tiers already measured, making your results non-reproducible. The copy also gives you a clean isolation boundary: if the agent somehow hangs and leaves the workspace in a partial state, your experiment data is unaffected. The cost is one `Files.walkFileTree()` copy per invocation, which is trivial compared to the agent call duration.

**2. Anything remaining that would cause rework** — Two things, one minor and one worth addressing now:

The minor one: your `CompletableFuture` timeout approach has a thread leak. When `future.get(timeout, MILLISECONDS)` throws `TimeoutException`, the future continues running in the background — the agent process keeps executing. You need `future.cancel(true)` in the catch block, and you should pass an explicit `ExecutorService` rather than using the common fork-join pool, so you can actually interrupt the underlying thread. For a long-running agent call this matters.

The more significant one: your prompt asks the agent to navigate `src/test/` and find corresponding production classes under `src/main/`, but the Spring Getting Started guides don't all follow a strict `FooTest.java` → `Foo.java` naming convention. Some guides test controllers via `MockMvc` where the test class name doesn't map cleanly to a single production class, and some have multiple classes under test from one test file. The agent will handle this gracefully in practice since it's Claude, but your prompt should acknowledge this: tell the agent "if no direct counterpart exists, evaluate the tests against all production classes in src/main/" rather than leaving it implicit. Otherwise you'll get inconsistent evaluation behavior across the 5 guides, which introduces noise into your comparison across variants.

One small implementation trap in the test: `mockFactory` needs to return an `AgentClient` whose `goal().workingDirectory().run()` chain returns an `AgentClientResponse` containing your canned string. Make sure your mock wires the full fluent chain — if `AgentClient.goal()` returns a builder object rather than `AgentClient` itself, a naive mock of `AgentClient` will return null from `goal()` and NPE before `run()` is called. Worth verifying against the actual `AgentClient` API before writing the mock helper.

That's it. Fix the thread leak and the prompt edge case, copy the workspace before judging, and this is ready to implement.


q: why are we getting into completable futures.


a: Fair point. You're running this synchronously inside a `judge()` call that's already on some thread — wrapping in `CompletableFuture` just to call `get()` with a timeout is unnecessary complexity.

The simpler approach is to set a timeout directly on the agent invocation itself. `ClaudeAgentOptions` almost certainly has a timeout configuration — check if it has something like `.timeout(Duration)` or a max-execution-time setting. That's the right place for it since the agent runtime owns the process lifecycle and can actually cancel it cleanly, unlike `future.cancel(true)` which can't reliably interrupt blocking I/O anyway.

If `ClaudeAgentOptions` doesn't support timeout natively, the next simplest thing is a try/catch around the synchronous `run()` call with a note that timeout handling is a future concern. For 20 invocations in an experiment context, a hung call is annoying but not catastrophic — you'd notice and kill it manually.

Either way, drop the `CompletableFuture` from the design.