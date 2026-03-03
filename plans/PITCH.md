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

> **knowledge + structured execution > model**

The biggest lever isn't which model you use — it's what knowledge you give it and how you direct its work. We call this **knowledge-directed execution**.

**Knowledge** = curated domain opinions encoded in navigable files. Not raw documentation — opinionated guidance that a senior engineer would give a junior one. "Use `@DataJpaTest` not `@SpringBootTest` for repository tests." "Prefer AssertJ over Hamcrest." "Use `@MockitoBean` not `@MockBean` on Boot 4." ChatGPT doesn't even know Spring Boot 4 shipped. Our KB does.

**Structured execution** = how the agent's work is organized. Detect Boot version before generating tests. Compile after every edit. Navigate a routing index to find the relevant cheatsheet instead of reading everything. Run deterministic judges before expensive LLM judges. This is the difference between "write some tests" and a disciplined process with checkpoints at every stage.

**The equation's claim**: these two levers contribute more to agent quality than model choice. A mid-tier model with knowledge-directed execution outperforms a frontier model winging it.

And here's the punchline: **the knowledge base is swappable**. Our KB encodes Spring community best practices — curated opinions, not fixed answers. Your team forks it, swaps in your idioms (Testcontainers instead of H2, RestAssured instead of MockMvc, whatever), runs the same experiment loop against your codebases, and gets an agent calibrated to your standards. No retraining. No prompting a frontier model to guess your preferences. The knowledge directs the execution — not the model, not even the specific opinions.

## What This Experiment Proves (and Doesn't)

This experiment demonstrates the equation step by step. Each variant adds one lever and the delta tells you what it contributed:

| Delta | What it isolates | Equation term |
|---|---|---|
| Control → Variant A | Value of structured execution alone (no knowledge) | **structured execution** |
| Variant A → Variant B | Value of basic knowledge on top of structure | **basic knowledge** |
| Variant B → Variant C | Value of knowledge depth and JIT navigation | **deep knowledge + navigation** |

This proves that **knowledge-directed execution causes agents to follow prescribed practices**, measured against a fixed rubric. It shows the methodology works and that each lever contributes measurably.

What it does **not** yet prove is the full equation — that knowledge + structured execution outweighs a stronger model. That requires a cross-model comparison and harder target projects. Those are planned iterations:

1. **Now**: 5 Getting Started guides — calibrate the methodology, demonstrate the growth story
2. **Next**: Pet Clinic + harder repos — genuine complexity where the KB advantage matters
3. **Next**: Cross-model variant (Haiku+KB vs Sonnet/Opus with no KB) — tests the ">" in the equation
4. **Later**: SWE-bench Lite (N=150) with external ground truth (resolve rate) — paper-grade evidence

The code-coverage experiment is the proving ground for knowledge-directed execution. The SWE-bench experiment is where the paper-grade evidence comes from — and there, the primary metric (resolve rate against gold patches) has zero circularity.

### External Validation

Stripe independently built the same architecture at $1T payment scale (Feb 2026). Their "blueprints" are structured execution; their "rules files" are knowledge. 1,300 PRs/week, zero human-written code. As Anup Jadhav wrote analyzing their system: "The walls matter more than the model." — that's the equation in four words.

Stripe can't tell you how much each lever contributes. Our ablation experiment can. That's the novel contribution.

## Why This Matters

The industry default is "use the biggest model and hope it knows enough." Knowledge-directed execution is the alternative: curate domain knowledge, structure the agent's work, and iterate on the cheap levers first. If you can get 80% of the way there with Haiku + good knowledge + structured execution, you don't need Opus.

## Presentation Framing (DevNexus / Blog Series)

The equation is the hook. Knowledge-directed execution is the formal name. The forge methodology is the product.

**Talk title**: knowledge + structured execution > model

**Arc**:
1. State the equation — let it be provocative
2. Decompose: knowledge (curated opinions) + structured execution (checkpoints, scoped context, tiered validation)
3. The experiment — 4 variants, each adds one lever, measure the delta
4. Stripe independently proved it — blueprints + rules files at $1T scale, same architecture, different vocabulary
5. What we add — the controlled measurement of what each lever contributes
6. The forge methodology — the repeatable way to build knowledge-directed execution for YOUR domain
7. Try it yourself — fork the KB, add your team's idioms, run the experiment

**The one-liner**:

> "Everyone's optimizing the model. We're optimizing the knowledge and the execution structure. Stripe proved the architecture works. We measured how much each lever contributes. The methodology is called Forge — and the knowledge base is yours to fork."

The equation is the **motivating hypothesis under investigation**, not a proven result. That's a more credible position than overclaiming — and the audience gets something actionable (the forge methodology, the swappable KB pattern) regardless of whether the full ">" holds for all cases.

## The Feedback Loop

When the agent scores low, the judge tells you *why* — and that maps to a specific lever:

| Lever | What it means | Fix | Cost |
|-------|--------------|-----|------|
| Knowledge gap | Agent didn't know the right pattern | Add or clarify a KB file | Low — fast iteration |
| Execution gap | Agent wasted effort, wrong order, too many retries | Restructure the execution flow | Medium |
| Tool gap | Agent kept reconstructing computable information | Build a dedicated tool | High — but reusable |
| Model gap | Agent failed despite good KB and orchestration | Try a stronger model | Highest — least tunable |

You iterate on the cheap levers first. That's what makes this practical.
