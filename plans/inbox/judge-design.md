is there a simpler approach.  perhaps going 'adaptive' wasn't the correct way.  we hand craft the judge prompt based on the ever increasing stage.  i'm worried this will be difficult to explain to an audience and seems to penalize whatever build it knowlede the llm has.

12:28 PM
Simpler Approach: One Handcrafted Prompt, Staged Expectations
Your instinct is right. The adaptive approach has a fundamental explainability problem: "the judge changes based on what the agent was told" is hard to defend to an audience because it conflates evaluation with instruction. It also, as you note, ignores what the LLM already knows about good Java testing — knowledge that exists independent of what you injected.

The Simpler Model
One fixed judge prompt that encodes what a good Spring Boot test suite looks like, period.

Not adaptive. Not derived from the agent's prompt. Just: here is what good Java/Spring testing looks like, score this test suite against that standard.

You are evaluating JUnit test quality for a Spring Boot project.
Score the test suite on these criteria:

1. Assertion quality (0-1): Tests use AssertJ or JUnit assertions to verify 
   specific expected values — not just assertNotNull(), not Java assert keyword.
   Controller tests assert status AND response body. JPA tests assert field values.

2. Spring slice usage (0-1): Tests use appropriate Spring test slices 
   (@WebMvcTest, @DataJpaTest) rather than @SpringBootTest where applicable.
   Unit tests use Mockito (@ExtendWith(MockitoExtension.class)) for dependencies.

3. Edge case coverage (0-1): Null inputs, empty collections, error paths, and 
   boundary conditions are tested — not just the happy path.

Return JSON: { "assertion_quality": 0.0-1.0, "spring_slice_usage": 0.0-1.0, 
               "edge_cases": 0.0-1.0, "evidence": "..." }
That's it. Same prompt for all four variants. No adaptation.

Why This Is Better for Your Purpose
Explainability: "We measured every variant against the same fixed quality bar" is a clean story. The audience understands that control variants are expected to score low — not because the judge was calibrated against them, but because they genuinely produced worse tests.

It rewards built-in LLM knowledge. If variant-a (hardened prompt, no KB) produces @WebMvcTest usage because the agent already knew to do that, it gets credit. Your adaptive design would not score this because the rubric for variant-a doesn't include it. That's the penalization you're worried about — and it's real.

The growth story becomes cleaner. Control scores 0.3. Variant-a scores 0.5. Variant-b scores 0.7. Variant-c scores 0.85. The progression shows what the knowledge files added on top of what a capable LLM already knew. That's actually a more interesting story — knowledge injection as an amplifier, not a baseline.

The criteria you care about are universal anyway. AssertJ over raw assertions, @WebMvcTest for controllers, Mockito for unit tests, edge case coverage — these aren't specific to any variant. They're just good Spring Boot testing practice. The knowledge files should help the agent do these things, and the judge measures whether it did.

What You Keep From v4
The floor signals (static analysis, fast, free): catches assert keyword, assertTrue(true), no production code invoked
The JSON output schema with evidence strings (auditable)
Agent-based evaluation with read-only tools for filesystem navigation
Score clamping, temp workspace isolation, error → Judgment.error()
What You Drop
The two-phase plan/evaluate loop
JudgmentContext carrying prompt and knowledge file content
All the complexity of deriving rubric from variant inputs
One Thing to Add
Since the judge prompt is now fixed and handcrafted, invest the effort you saved into making the criteria concrete and Spring-specific. The prompt above is a sketch — the real version should include examples of what scores 0.2 vs 0.8 on each criterion. That's where the quality of the judge lives, and it's a one-time cost.

The Honest Tradeoff
The one thing you give up: the fixed judge will find it harder to distinguish variant-b from variant-c (both KB variants) because they both follow the same practices — just with slightly different breadth. If your growth story needs a clear gap between those two, you may need a fourth criterion specifically about exception/error path coverage, which is what common-gaps.md (variant-c only) specifically teaches. That's the one place where a small amount of adaptive behavior is defensible — one additional criterion that only variant-c was explicitly taught to address.

But start fixed. You can always add nuance after you see the actual score distribution.

so then, we are starting from the premise of having collecting a full set of 'best practices' and watching the agent slowly grow to meet them?  so the knowledge collection happens up front?

12:29 PM
Yes, exactly. And that reframe actually clarifies the whole experiment structure.

The Corrected Mental Model
You're not measuring "did the agent follow its instructions." You're measuring "how close did the agent get to a known quality bar" — and the independent variable is what resources you gave it to get there.

The judge is a fixed target. The variants are different attempts to hit that target.

Fixed Quality Bar (judge prompt)
        ↑
        |  how close did each variant get?
        |
control ──── variant-a ──── variant-b ──── variant-c
(naive)    (better prompt)  (+3 KB)       (+4 KB)
The knowledge files you inject into the agent are your attempt to teach the agent to hit the bar the judge already knows about. The judge doesn't care how the agent was taught — it just asks "did it get there?"

This Changes the Knowledge File Strategy
The knowledge files you write for the agent should be derived from the judge criteria, not independent of them. If the judge scores on @WebMvcTest usage, then spring-test-slices.md should teach exactly that. If the judge scores on AssertJ assertion specificity, then coverage-fundamentals.md should address that.

The experiment then has a clean internal logic:

Define the quality bar first (judge prompt criteria)
Write knowledge files that teach those criteria to the agent
Ablate: how much of the bar does the agent hit with no help? With a better prompt? With 3 KB files? With 4?
This also means your knowledge files have a clear scope boundary — they shouldn't teach things the judge doesn't measure, and the judge shouldn't measure things the knowledge files don't address (at least for the higher variants).

The One Remaining Question
How much of the quality bar can a capable LLM (Claude, in this case) hit with zero knowledge injection — just from its training? That's actually the most interesting data point in the whole experiment. If variant-a (hardened prompt, no KB) scores 0.6 on a fixed bar, you know the LLM already knew 60% of good Spring testing practice. The KB files bought you the remaining 0.25-0.3. That's a much more honest and interesting story than "knowledge injection works" — it's "here's exactly what it added, on top of what the model already knew."