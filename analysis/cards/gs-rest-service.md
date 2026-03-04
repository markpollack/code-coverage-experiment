# gs-rest-service

## Scores by Variant

| Variant | Cov% | T3 | Eff | Eff:BE | Eff:Cost | Eff:RC | Cost | In Tok | Out Tok | Think |
|---------|------|-----|------|--------|----------|--------|------|--------|---------|-------|
| control | 71.4 | 0.67 | 0.789 | 0.75 | 0.896 | 0.75 | $0.52 | 13 | 4201 | 418 |
| variant-a | 71.4 | 0.82 | 0.955 | 1.0 | 0.83 | 1.0 | $0.85 | 33 | 7042 | 812 |
| variant-b | 100.0 | 0.88 | 0.851 | 0.875 | 0.787 | 0.875 | $1.07 | 33 | 10160 | 2090 |
| variant-c | 71.4 | 0.88 | 0.835 | 0.875 | 0.725 | 0.875 | $1.38 | 38 | 11586 | 2170 |
| variant-d | 100.0 | 0.88 | 0.842 | 0.875 | 0.751 | 0.875 | $1.25 | 25 | 8332 | 1321 |

## T3 Practice Adherence — Criterion Details

### control

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.33 | 0.33 — Agent: [SpringBootTest, WebMvcTest], Reference: [SpringBootTest, AutoConfigureRestTestClient] |
| assertion_quality | 0.70 | 0.70 — GreetingControllerTest.java uses jsonPath with specific domain values (jsonPath("$.content", is("Hello, World!")) |
| assertion_style | 0.33 | 0.33 — Agent: 41 assertions, Reference: 4 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +71.4 pp (0.0% → 71.4%) |
| coverage_target_selection | 0.20 | 0.20 — GreetingTest.java tests the Greeting record's constructor, accessors (id(), content()), equals/hashCode, and toSt |
| domain_specific_test_patterns | 0.80 | 0.80 — GreetingControllerTest.java uses MockMvc with jsonPath assertions and scoped @WebMvcTest(GreetingController.class |
| error_and_edge_case_coverage | 0.50 | 0.50 — GreetingControllerTest.java covers default name, custom name, and special characters — reasonable for the happy p |
| import_alignment | 0.67 | 0.67 — Agent: 6 imports, Reference: 4 imports |
| injection_pattern | 0.00 | 0.00 — Agent: [MockMvc], Reference: [RestTestClient] |
| line_coverage_preserved | — | Drop -71.4% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 11, Reference: 2 |
| test_slice_selection | 0.80 | 0.80 — GreetingControllerTest.java uses @WebMvcTest(GreetingController.class) — correctly scoped to the specific control |
| version_aware_patterns | 1.00 | 1.00 — GreetingControllerTest.java imports org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest — the Boot 4.x  |

### variant-a

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.00 | 0.00 — Agent: [WebMvcTest], Reference: [SpringBootTest, AutoConfigureRestTestClient] |
| assertion_quality | 0.80 | 0.80 — GreetingControllerTest.java uses MockMvcTester with AssertJ fluent assertions (.hasStatusOk(), .bodyJson().extrac |
| assertion_style | 0.00 | 0.00 — Agent: 5 assertions, Reference: 4 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +71.4 pp (0.0% → 71.4%) |
| coverage_target_selection | 0.80 | 0.80 — Tests focus on the controller endpoint behavior (content formatting, id generation, incrementing counter) — all b |
| domain_specific_test_patterns | 0.80 | 0.80 — MVC domain: uses MockMvcTester (Boot 4.x MVC test client) with jsonPath-style assertions via .bodyJson().extracti |
| error_and_edge_case_coverage | 0.50 | 0.50 — GreetingControllerTest.java covers default param and custom param happy paths plus id increment behavior. No test |
| import_alignment | 0.80 | 0.80 — Agent: 5 imports, Reference: 4 imports |
| injection_pattern | 0.00 | 0.00 — Agent: [MockMvcTester], Reference: [RestTestClient] |
| line_coverage_preserved | — | Drop -71.4% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 4, Reference: 2 |
| test_slice_selection | 1.00 | 1.00 — GreetingControllerTest.java uses @WebMvcTest(GreetingController.class) — correctly scoped to the specific control |
| version_aware_patterns | 1.00 | 1.00 — GreetingControllerTest.java imports org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest (Boot 4.x path) |

### variant-b

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.00 | 0.00 — Agent: [WebMvcTest], Reference: [SpringBootTest, AutoConfigureRestTestClient] |
| assertion_quality | 0.80 | 0.80 — GreetingControllerTest.java uses jsonPath('$.content').value('Hello, World!') and jsonPath('$.content').value('He |
| assertion_style | 0.50 | 0.50 — Agent: 20 assertions, Reference: 4 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +100.0 pp (0.0% → 100.0%) |
| coverage_target_selection | 1.00 | 1.00 — GreetingControllerTest.java targets only GreetingController.greeting() — the sole behavioral code. Greeting recor |
| domain_specific_test_patterns | 1.00 | 1.00 — GreetingControllerTest.java uses MockMvc with jsonPath assertions, @WebMvcTest scoped to the specific controller. |
| error_and_edge_case_coverage | 0.50 | 0.50 — GreetingControllerTest.java covers default name, custom name, and empty-string name — all variations of the happy |
| import_alignment | 1.00 | 1.00 — Agent: 4 imports, Reference: 4 imports |
| injection_pattern | 0.00 | 0.00 — Agent: [MockMvc], Reference: [RestTestClient] |
| line_coverage_preserved | — | Drop -100.0% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 4, Reference: 2 |
| test_slice_selection | 1.00 | 1.00 — GreetingControllerTest.java uses @WebMvcTest(GreetingController.class) — scoped to the specific controller. No @S |
| version_aware_patterns | 1.00 | 1.00 — GreetingControllerTest.java imports org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest — the Boot 4.x  |

### variant-c

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.33 | 0.33 — Agent: [WebMvcTest, AutoConfigureRestTestClient], Reference: [SpringBootTest, AutoConfigureRestTestClient] |
| assertion_quality | 0.80 | 0.80 — GreetingControllerTest.java uses AssertJ fluent assertions checking specific domain values: body.content()).isEqu |
| assertion_style | 0.25 | 0.25 — Agent: 15 assertions, Reference: 4 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +71.4 pp (0.0% → 71.4%) |
| coverage_target_selection | 1.00 | 1.00 — GreetingControllerTest.java tests only the controller's behavioral logic (endpoint response, parameter handling,  |
| domain_specific_test_patterns | 1.00 | 1.00 — GreetingControllerTest.java uses RestTestClient with @AutoConfigureRestTestClient alongside @WebMvcTest(GreetingC |
| error_and_edge_case_coverage | 0.50 | 0.50 — GreetingControllerTest.java covers default param, custom param, and counter increment — all happy-path scenarios. |
| import_alignment | 0.80 | 0.80 — Agent: 5 imports, Reference: 4 imports |
| injection_pattern | 1.00 | 1.00 — Agent: [RestTestClient], Reference: [RestTestClient] |
| line_coverage_preserved | — | Drop -71.4% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 3, Reference: 2 |
| test_slice_selection | 1.00 | 1.00 — GreetingControllerTest.java uses @WebMvcTest(GreetingController.class) — scoped to the specific controller. No @S |
| version_aware_patterns | 1.00 | 1.00 — Boot 4.0.3 project. GreetingControllerTest.java imports org.springframework.boot.webmvc.test.autoconfigure.WebMvc |

### variant-d

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.00 | 0.00 — Agent: [WebMvcTest], Reference: [SpringBootTest, AutoConfigureRestTestClient] |
| assertion_quality | 0.80 | 0.80 — shouldReturnDefaultGreeting and shouldReturnNamedGreeting use jsonPath('$.content').value(...) and jsonPath('$.id |
| assertion_style | 0.33 | 0.33 — Agent: 23 assertions, Reference: 4 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +100.0 pp (0.0% → 100.0%) |
| coverage_target_selection | 1.00 | 1.00 — All three tests target GreetingController business behavior (endpoint response, name parameter substitution, atom |
| domain_specific_test_patterns | 1.00 | 1.00 — MVC domain only (no JPA, security, or WebFlux in production code). MockMvc injected via @Autowired, GET requests  |
| error_and_edge_case_coverage | 0.50 | 0.50 — Tests cover the default greeting (no name param) and a named greeting (name='Spring') and counter increment — all |
| import_alignment | 0.67 | 0.67 — Agent: 6 imports, Reference: 4 imports |
| injection_pattern | 0.00 | 0.00 — Agent: [MockMvc], Reference: [RestTestClient] |
| line_coverage_preserved | — | Drop -100.0% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 3, Reference: 2 |
| test_slice_selection | 1.00 | 1.00 — GreetingControllerTest.java uses @WebMvcTest(GreetingController.class) — the narrowest applicable slice, scoped t |
| version_aware_patterns | 1.00 | 1.00 — Boot 4.x project (spring-boot-starter-parent 4.0.3). Test imports org.springframework.boot.webmvc.test.autoconfig |
