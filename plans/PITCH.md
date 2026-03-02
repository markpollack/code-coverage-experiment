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

Every variant is scored against the **same fixed quality bar** — a judge that knows what good Spring Boot tests look like. Did the agent use the right test slices? Are the assertions checking real values? Are edge cases covered? Same bar for everyone.

The growth story shows: control scores low, variant-a scores better, variant-b scores well, variant-c scores best. Each jump has a cause you can point to.

## The Thesis

The biggest lever isn't the model — it's the knowledge. ChatGPT doesn't even know Spring Boot 4 shipped. Our knowledge base knows about `RestTestClient`, the new annotation packages, `@MockitoBean` replacing `@MockBean`. The agent with that KB will use the right patterns for Boot 4. The agent without it will use Boot 3 patterns that may not even compile.

And here's the punchline: **the knowledge base is swappable**. Our KB encodes Spring community best practices. Your team forks it, swaps in your idioms (Testcontainers instead of H2, RestAssured instead of MockMvc, whatever), runs the same experiment loop against your codebases, and gets an agent calibrated to your standards. No retraining. No prompting a frontier model to guess your preferences. The architecture is the artifact — not the model, not even the specific knowledge.

## Why This Matters

The industry default is "use the biggest model and hope it knows enough." We're showing that a structured knowledge base with proper orchestration is a more tunable, more portable, and cheaper path to reliable agent behavior. If you can get 80% of the way there with Haiku + good knowledge, you don't need Opus.

## The Feedback Loop

When the agent scores low, the judge tells you *why* — and that maps to a specific lever:

| Lever | What it means | Fix | Cost |
|-------|--------------|-----|------|
| Knowledge gap | Agent didn't know the right pattern | Add or clarify a KB file | Low — fast iteration |
| Orchestration gap | Agent wasted effort, wrong order, too many retries | Restructure the prompt | Medium |
| Tool gap | Agent kept reconstructing computable information | Build a dedicated tool | High — but reusable |
| Model gap | Agent failed despite good KB and orchestration | Try a stronger model | Highest — least tunable |

You iterate on the cheap levers first. That's what makes this practical.
