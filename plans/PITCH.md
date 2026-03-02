# The Experiment in Plain Terms

## The Question

When you ask an AI agent to write tests for your Spring Boot project, how much does it matter *what knowledge you give it* vs. *which model you use*?

## The Setup

We take 5 real Spring Boot projects from the official Spring Getting Started guides. Each one has some existing tests. We ask an AI agent to improve the test coverage to 80%.

We run the same task 4 times, changing **one thing** each time:

1. **Control** — "Improve test coverage to 80%." That's it. One sentence. The model figures it out from training data alone.

2. **Variant A** — Same model, but a better prompt: detect the Boot version, compile after every change, follow existing conventions. No knowledge base. This measures what prompt engineering alone buys you.

3. **Variant B** — Same prompt as A, plus 3 small files about coverage mechanics (how JaCoCo works, what not to test, which test slice to use). This measures what basic knowledge injection adds.

4. **Variant C** — Same prompt, but now the agent can navigate a full knowledge base: 8 cheatsheets covering JPA testing, REST controller testing, Security testing, WebFlux, WebSocket, AssertJ/Mockito idioms, and Boot 3→4 migration patterns. The agent reads a routing index and pulls only what's relevant to the code it's testing. This measures what *rich, navigable domain knowledge* adds.

## What We Measure

Every variant is evaluated on two separate dimensions:

**Functional correctness** (deterministic, no subjectivity): Does the code compile? Do the tests pass? Does coverage meet the threshold? These are T0/T1 tier judges — binary, unimpeachable.

**Practice adherence** (LLM-evaluated, same fixed rubric for all variants): Does the agent follow prescribed Spring testing practices? Did it use the narrowest applicable test slice? Are assertions checking domain-meaningful values? Are Boot 4 idioms used on a Boot 4 project? This rubric is derived from the knowledge base and applied identically to all variants — the same way a code review checklist works.

These scores are reported **separately**, never combined into a single number. The functional score shows the KB doesn't break anything. The adherence score shows whether the KB makes the agent follow your team's standards.

The growth story: all variants should compile and pass. The variants with knowledge should additionally follow the prescribed practices — and the gap should widen as target projects get more complex.

## The Thesis

**Hypothesis**: Knowledge + orchestration > model. The biggest lever isn't which model you use — it's what knowledge you give it and how you structure the work.

ChatGPT doesn't even know Spring Boot 4 shipped. Our knowledge base knows about `RestTestClient`, the new annotation packages, `@MockitoBean` replacing `@MockBean`. The agent with that KB will use the right patterns for Boot 4. The agent without it will use Boot 3 patterns that may not even compile.

And here's the punchline: **the knowledge base is swappable**. Our KB encodes Spring community best practices. Your team forks it, swaps in your idioms (Testcontainers instead of H2, RestAssured instead of MockMvc, whatever), runs the same experiment loop against your codebases, and gets an agent calibrated to your standards. No retraining. No prompting a frontier model to guess your preferences. The architecture is the artifact — not the model, not even the specific knowledge.

## What This Experiment Proves (and Doesn't)

This experiment demonstrates that **structured knowledge injection causes agents to follow prescribed practices**, measured against a fixed rubric. It shows the methodology works and that each lever (prompt hardening, basic KB, full navigable KB) contributes measurably.

What it does **not** yet prove is the full "knowledge > model" claim — that requires a cross-model comparison (cheap model + KB vs expensive model + no KB) and harder target projects. Those are planned iterations:

1. **Now**: 5 Getting Started guides — calibrate the methodology and tooling
2. **Next**: Pet Clinic + harder repos — genuine complexity where the KB advantage matters
3. **Next**: Cross-model variant (Haiku+KB vs Sonnet/Opus with no KB) — the headline comparison
4. **Later**: SWE-bench Lite (N=150) with external ground truth (resolve rate) — paper-grade evidence

The code-coverage experiment is the proving ground for the methodology. The SWE-bench experiment is where the paper-grade evidence comes from — and there, the primary metric (resolve rate against gold patches) has zero circularity.

## Why This Matters

The industry default is "use the biggest model and hope it knows enough." We're investigating whether a structured knowledge base with proper orchestration is a more tunable, more portable, and cheaper path to reliable agent behavior. If you can get 80% of the way there with Haiku + good knowledge, you don't need Opus.

## Presentation Framing (DevNexus / Blog Series)

For talks and blog posts, the honest and compelling framing is:

> "Here's a repeatable methodology for growing agents. Here's what we've seen so far — each lever (prompt, knowledge, orchestration) contributes measurably. The hypothesis is that knowledge and orchestration matter more than model choice. We're testing that rigorously on SWE-bench. Try this yourself — fork the KB, add your team's standards, run the experiment."

This is a "try it yourself" pitch with a strong directional claim, not an unsubstantiated conclusion. The audience gets something actionable (the forge methodology, the swappable KB pattern) regardless of whether the full thesis holds. "Knowledge + orchestration > model" is the **motivating hypothesis under investigation**, not a proven result — and that's a more credible position than overclaiming.

## The Feedback Loop

When the agent scores low, the judge tells you *why* — and that maps to a specific lever:

| Lever | What it means | Fix | Cost |
|-------|--------------|-----|------|
| Knowledge gap | Agent didn't know the right pattern | Add or clarify a KB file | Low — fast iteration |
| Orchestration gap | Agent wasted effort, wrong order, too many retries | Restructure the prompt | Medium |
| Tool gap | Agent kept reconstructing computable information | Build a dedicated tool | High — but reusable |
| Model gap | Agent failed despite good KB and orchestration | Try a stronger model | Highest — least tunable |

You iterate on the cheap levers first. That's what makes this practical.
