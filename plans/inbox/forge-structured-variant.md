# Design Brief: Forge-Structured Planning Variant (variant-e)

## Origin

From code-coverage-experiment Stage 6 discussion. Variant-d's TEST_PLAN.md on Pet Clinic was examined — it's a thorough *specification* (400 lines, 14 test classes, specific test cases) but has no *methodology*. It's a flat list of what to build, not a staged plan for how to build it. The act phase then becomes a "big blob of thinking" with no checkpoints, no validation gates, and no self-correction. The agent spent 22 minutes thrashing through compile-fix cycles with no structure.

## The Problem with variant-d's "Explore → Act"

**What the plan looks like:**
- Project summary, Boot 4 annotation reference
- 14 test class specs with test case tables and mock strategies
- Coverage estimation table
- Execution priority order

**What the plan lacks:**
- No stages or phases of work
- No entry/exit criteria per stage
- No validation gates ("compile and verify before moving on")
- No learnings capture between stages
- No self-correction mechanism ("Stage 2 revealed X, adjust Stage 3")
- No scope management ("if running out of time/budget, what to cut")

**Result:** The act phase gets a massive spec and tries to implement it all at once. When things break, it thrashes without a protocol for prioritization or staged recovery.

## Proposed: variant-e (forge-plan → forge-act)

Replace the flat spec with a full Forge methodology plan. The agent produces structured planning artifacts, then executes them stage-by-stage with validation and learnings at each boundary.

### Phase 1: Forge Planning

The agent applies Forge methodology (from `~/tuvium/projects/forge-methodology/`) compressed into a single planning turn. It produces **three documents**:

#### 1. TEST-VISION.md
- **Problem**: What are we testing and why?
- **Success criteria**: Measurable outcomes (80% coverage, all tests pass, correct annotations)
- **Scope boundaries**: What's in (controllers, services, repos, model logic) / what's out (config classes, main(), trivial getters)
- **Unknowns**: What needs investigation (test data strategy, framework-specific patterns, H2 schema loading)
- **Assumptions**: Each is a risk if wrong (e.g., "H2 auto-loads schema.sql")

#### 2. TEST-DESIGN.md
- **Test architecture**: Which test types for which layers
  - Controller → `@WebMvcTest` with `MockMvc`
  - Repository → `@DataJpaTest` with H2
  - Model/Validator → plain JUnit 5
  - Service → unit test with `@MockitoBean`
- **Fixture strategy**: Shared test data builders vs per-test setup
- **Mock boundaries**: What gets mocked, what uses real implementations
- **Dependency decisions**: Which test annotations, assertion library (AssertJ vs Hamcrest), etc.
- **Risks**: Form-based MVC testing patterns, entity relationship setup, PetTypeFormatter as @Component

#### 3. TEST-ROADMAP.md (full Forge step format)

```markdown
## Stage 1: Test Infrastructure

### Step 1.0: Verify project compiles and understand test baseline

**Entry criteria**:
- Read TEST-VISION.md and TEST-DESIGN.md

**Work items**:
- [ ] Run ./mvnw compile — verify clean
- [ ] Check JaCoCo config — ensure report generation works
- [ ] Check H2 schema/data loading — verify @DataJpaTest has data
- [ ] Identify any framework quirks (PetTypeFormatter, spring-javaformat, etc.)

**Exit criteria**:
- [ ] Project compiles
- [ ] Key risks from TEST-VISION.md validated or flagged
- [ ] Create: TEST-LEARNINGS.md with Step 1.0 findings

### Step 1.1: Plain unit tests (no Spring context)

**Entry criteria**:
- [ ] Step 1.0 complete
- [ ] Read: TEST-LEARNINGS.md

**Work items**:
- [ ] WRITE: OwnerTest, VetTest, VetsTest, PetValidatorTest, PetTypeFormatterTest
- [ ] VERIFY: ./mvnw test — all pass
- [ ] CHECK: coverage report — establish first coverage baseline

**Exit criteria**:
- [ ] All unit tests pass
- [ ] Coverage baseline recorded
- [ ] Update TEST-LEARNINGS.md with mocking patterns that worked/failed

### Step 1.2: Controller slice tests (@WebMvcTest)

**Entry criteria**:
- [ ] Step 1.1 complete
- [ ] Read: TEST-LEARNINGS.md — apply fixture patterns from Step 1.1

**Work items**:
- [ ] WRITE: WelcomeControllerTest, CrashControllerTest (trivial — validate approach)
- [ ] WRITE: VetControllerTest (medium complexity)
- [ ] VERIFY: ./mvnw test — all pass before continuing
- [ ] WRITE: OwnerControllerTest (highest complexity — form handling, pagination)
- [ ] WRITE: PetControllerTest (PetTypeFormatter dependency, PetValidator)
- [ ] WRITE: VisitControllerTest
- [ ] VERIFY: ./mvnw test — all pass

**Exit criteria**:
- [ ] All controller tests pass
- [ ] Update TEST-LEARNINGS.md with form testing patterns, @MockitoBean patterns

### Step 1.3: Repository slice tests (@DataJpaTest)

**Entry criteria**:
- [ ] Step 1.2 complete
- [ ] Read: TEST-LEARNINGS.md

**Work items**:
- [ ] WRITE: OwnerRepositoryTest, PetTypeRepositoryTest, VetRepositoryTest
- [ ] VERIFY: ./mvnw test — all pass

**Exit criteria**:
- [ ] All repository tests pass
- [ ] Update TEST-LEARNINGS.md with H2/JPA testing patterns

### Step 1.4: Coverage validation and gap-filling

**Entry criteria**:
- [ ] Steps 1.1-1.3 complete
- [ ] Read: TEST-LEARNINGS.md

**Work items**:
- [ ] RUN: ./mvnw clean test jacoco:report
- [ ] READ: coverage report — identify gaps
- [ ] IF below 80%: write targeted tests for uncovered code
- [ ] VERIFY: ./mvnw test — all still pass

**Exit criteria**:
- [ ] Coverage ≥ 80%
- [ ] All tests pass
- [ ] Update TEST-LEARNINGS.md with final findings
```

### Phase 2: Forge Execution

The agent reads all three documents, then executes the roadmap **step by step**:

1. Execute Step 1.0 — validate infrastructure, update TEST-LEARNINGS.md
2. Execute Step 1.1 — write unit tests, compile, run, update learnings
3. Execute Step 1.2 — write controller tests, applying learnings from Step 1.1
4. Execute Step 1.3 — write repo tests
5. Execute Step 1.4 — validate coverage, fill gaps

**Key difference from variant-d**: The agent validates (compile + test) at each step boundary and captures learnings before moving to the next step. If Step 1.2 reveals that PetTypeFormatter causes unexpected issues, that learning is available before Step 1.3.

## Why This Should Work Better

| Aspect | variant-d (explore → act) | variant-e (forge-plan → forge-act) |
|--------|--------------------|--------------------|
| Plan output | Flat spec (what to build) | VISION + DESIGN + ROADMAP (what, why, how) |
| Execution | All at once, one big blob | Stage by stage with validation gates |
| Failure recovery | Thrash through compile-fix cycles | Fix within current step, learnings inform next step |
| Self-correction | None | Per-step learnings, explicit unknowns tracking |
| Scope management | None — try to do everything | Exit criteria define "done" per step |
| Compile verification | At the end (or whenever agent remembers) | After every step (mandated by exit criteria) |
| Time management | No awareness of budget | Can cut scope at step boundaries if needed |

## Hypothesis

**Forge-structured planning > flat spec exploration** on complex projects, because:
- Staged execution catches errors earlier (validate after each step, not at the end)
- Learnings from early steps improve later steps (unit test patterns inform slice tests)
- The roadmap format gives the agent a protocol for self-correction
- Scope management prevents the "try everything, fix nothing" failure mode

## Implementation

### Files to create

| File | Purpose |
|------|---------|
| `prompts/v4-forge-plan.txt` | Planning phase — Forge methodology instructions, produce VISION + DESIGN + ROADMAP |
| `prompts/v4-forge-act.txt` | Execution phase — read documents, execute roadmap steps with learnings |

### Config

```yaml
- name: variant-e
  promptFile: v4-forge-plan.txt
  actPromptFile: v4-forge-act.txt
  knowledgeDir: knowledge
  knowledgeFiles:
    - index.md
```

### Infrastructure

Uses same `TwoPhaseCodeCoverageAgentInvoker` and `ClaudeSyncClient` session continuity as variant-d. No new Java code needed — only new prompts.

### Key prompt design decisions

1. **Planning phase should NOT write code** — only produce the three documents
2. **Act phase should explicitly reference the roadmap steps** — not freestyle
3. **Learnings file is updated after each step** — not at the end
4. **Validation is mandatory** — `./mvnw test` after every step, not optional
5. **KB navigation via routing tables** — agent reads `knowledge/index.md` and navigates on demand, not a flat dump

## Reference

- Forge methodology: `~/tuvium/projects/forge-methodology/`
- Step format template: `templates/ROADMAP-TEMPLATE.md`
- Phase definitions: `phases/00-vision.md` through `phases/04-learning-loop.md`
- Refactoring agent (Forge in practice): `~/tuvium/projects/refactoring-agent/`
- Forge slash commands: `/forge-project`, `/forge-eval-agent`, `/forge-kb`, `/plan-to-roadmap`
- variant-d TEST_PLAN.md (what to improve on): `results/.../variant-d/spring-petclinic/TEST_PLAN.md`

## Sequencing

1. Complete Pet Clinic sweep-002 (variant-a, b, d) — in progress
2. Run analysis on sweep-002 — compare variant-d against a, b
3. Write v4-forge-plan.txt and v4-forge-act.txt prompts
4. Run variant-e on Pet Clinic — compare against variant-d on same item
5. If promising, run on getting-started guides to confirm overhead profile
