This is a solid, well-structured plan. The architecture is clear, the cascade logic makes sense, and the proposed implementation follows established patterns in the codebase. Let me address your five questions and flag a few risks.

**On your specific questions:**

**1. LLMJudge base class vs. direct Judge implementation** — Extend `LLMJudge` for now. The base class handles the straightforward case well, and you're not yet at the point where you need retry logic or structured output badly enough to justify the boilerplate. That said, the one place this bites you is structured output: the base class gives you a raw `String`, so you're on your own for JSON parsing. If Spring AI's `ChatClient` supports `.call().entity(MyRecord.class)` with structured output, you might want to bypass `LLMJudge` entirely and call `chatClient` directly in `judge()`. This would be cleaner than `parseResponse()` doing fragile string-to-JSON extraction. Worth checking if `LLMJudge` lets you override `judge()` or if you need to just implement `Judge` directly for that use case.

**2. Evaluation criteria** — The four criteria are reasonable. One suggestion: collapse "BDD structure" and "no trivial tests" since they're highly correlated — a trivial test by definition lacks a meaningful act/assert phase. You could replace them with something more distinct like **exception and edge case coverage** (does the agent test nulls, boundaries, error paths?), which is often where AI-generated tests fall short. Also consider whether "test naming" is worth 25% of the score — it's the least informative criterion about actual test quality.

**3. Production code in the prompt** — Yes, include it, but be selective. You don't need all production code — just the classes under test that correspond to the generated test files. The LLM can't meaningfully evaluate whether assertions are "checking real behavior" without knowing what the code actually does. Without it, you risk the judge hallucinating quality scores. A reasonable approach: for each test file `FooTest.java`, include `Foo.java` from `src/main/` if it exists.

**4. Score type for Tier 3** — `NumericalScore.normalized()` is the right call. Since this is FINAL_TIER and always produces a verdict, the continuous score gives you more signal in the `ResultStore` for later analysis (you can always threshold for pass/fail). If you use `BooleanScore` you lose gradient — you won't be able to tell "barely failed" from "catastrophically failed" when comparing variants.

**5. Roadmap granularity** — Looks appropriately sized. Step 1.4 is self-contained and verifiable. The consolidation steps (1.5, 2.2) are a good instinct — learnings from running the actual experiments will invalidate assumptions baked into the judge.

---

**Risks not yet flagged in the plan:**

**JSON parsing brittleness** — The biggest risk in this step. LLMs don't reliably return clean JSON even when asked. Your `parseResponse()` needs defensive handling: strip markdown fences, handle partial JSON, fall back gracefully. Consider requesting the response in a very constrained format or using Spring AI's structured output if available. A malformed response that throws in `parseResponse()` should produce `Judgment.error(...)` not an uncaught exception propagating up through the cascade.

**Prompt token size** — If you include test files *and* production files for 5 Spring Getting Started guides with potentially many test files, you can easily hit context limits or incur high latency/cost per evaluation. Add a safeguard: truncate or summarize if total content exceeds a threshold, and log a warning.

**Threshold calibration (0.5)** — The 0.5 pass threshold is arbitrary and untested. Since this is an experiment, it would be worth logging the raw per-criterion scores in `metadata` regardless of pass/fail, so you can recalibrate after seeing real data. Don't hardcode 0.5 in business logic — make it a constructor parameter or a `@Value` property.

**No-test-files ABSTAIN propagates as what?** — Clarify how FINAL_TIER handles ABSTAIN. If `CascadedJury` doesn't have explicit handling for ABSTAIN from the final tier, you might get an undefined overall verdict. Trace through the cascade to confirm ABSTAIN from Tier 3 is handled explicitly.

---

Overall the plan is implementation-ready. The two things I'd resolve before writing code: (1) decide on structured output vs. raw string parsing, and (2) confirm how ABSTAIN flows through the cascade when Tier 3 abstains.