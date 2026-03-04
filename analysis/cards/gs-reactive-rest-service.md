# gs-reactive-rest-service

## Scores by Variant

| Variant | Cov% | T3 | Eff | Eff:BE | Eff:Cost | Eff:RC | Cost | In Tok | Out Tok | Think |
|---------|------|-----|------|--------|----------|--------|------|--------|---------|-------|
| control | 78.9 | 0.73 | 0.908 | 1.0 | 0.656 | 1.0 | $1.72 | 31 | 29244 | 6899 |
| variant-a | 78.9 | 0.82 | 0.953 | 1.0 | 0.823 | 1.0 | $0.89 | 29 | 10535 | 1848 |
| variant-b | 100.0 | 0.82 | 0.959 | 1.0 | 0.846 | 1.0 | $0.77 | 23 | 9473 | 1415 |
| variant-c | 78.9 | 0.9 | 0.855 | 0.875 | 0.798 | 0.875 | $1.01 | 29 | 11119 | 1471 |
| variant-d | 100.0 | 0.73 | 0.725 | 0.75 | 0.656 | 0.75 | $1.72 | 33 | 15150 | 2653 |

## T3 Practice Adherence — Criterion Details

### control

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.50 | 0.50 — Agent: [SpringBootTest], Reference: [SpringBootTest, AutoConfigureWebTestClient] |
| assertion_quality | 0.80 | 0.80 — GreetingHandlerTest.java uses jsonPath("$.message").isEqualTo("Hello, Spring!"), expectBody(Greeting.class).isEqu |
| assertion_style | 0.67 | 0.67 — Agent: 12 assertions, Reference: 2 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +78.9 pp (0.0% → 78.9%) |
| coverage_target_selection | 0.50 | 0.50 — GreetingTest.java (all 6 tests) targets the Greeting record exclusively — testing constructorAndMessageAccessor,  |
| domain_specific_test_patterns | 0.80 | 0.80 — WebFlux/Reactive domain: GreetingHandlerTest.java uses WebTestClient (correct), no .block() (correct), bindToRout |
| error_and_edge_case_coverage | 0.50 | 0.50 — GreetingHandlerTest.nonHelloPathReturnsNotFound() tests the 404 error path — the one meaningful error case in a s |
| import_alignment | 0.71 | 0.71 — Agent: 6 imports, Reference: 6 imports |
| injection_pattern | 0.00 | 0.00 — Agent: [], Reference: [WebTestClient] |
| line_coverage_preserved | — | Drop -78.9% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 19, Reference: 1 |
| test_slice_selection | 0.80 | 0.80 — GreetingHandlerTest.java uses no Spring annotation and binds directly to the router function via WebTestClient.bi |
| version_aware_patterns | 1.00 | 1.00 — Boot 4.x project. No @MockBean or @SpyBean (deprecated in Boot 4.x) appear anywhere in the test suite — mocking i |

### variant-a

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 1.00 | 1.00 — Agent: [SpringBootTest, AutoConfigureWebTestClient], Reference: [SpringBootTest, AutoConfigureWebTestClient] |
| assertion_quality | 0.80 | 0.80 — GreetingHandlerTest.java line 44 uses AssertJ .value() consumer asserting greeting.message().isEqualTo("Hello, Sp |
| assertion_style | 0.67 | 0.67 — Agent: 6 assertions, Reference: 2 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +78.9 pp (0.0% → 78.9%) |
| coverage_target_selection | 0.80 | 0.80 — Tests cover GreetingHandler.hello() (handler logic), full routing via integration test, and GreetingClient.getMes |
| domain_specific_test_patterns | 1.00 | 1.00 — GreetingHandlerTest.java uses WebTestClient.bindToRouterFunction() — correct lightweight reactive testing without |
| error_and_edge_case_coverage | 0.50 | 0.50 — GreetingRouterIntegrationTest.java tests a 404 for /unknown (line 43-49) and a 4xx for wrong Accept header (text/ |
| import_alignment | 0.86 | 0.86 — Agent: 7 imports, Reference: 6 imports |
| injection_pattern | 0.50 | 0.50 — Agent: [GreetingClient, WebTestClient], Reference: [WebTestClient] |
| line_coverage_preserved | — | Drop -78.9% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 8, Reference: 1 |
| test_slice_selection | 0.80 | 0.80 — GreetingHandlerTest.java uses no Spring context at all — WebTestClient.bindToRouterFunction() wires handler direc |
| version_aware_patterns | 1.00 | 1.00 — GreetingRouterIntegrationTest.java line 5 imports org.springframework.boot.webtestclient.autoconfigure.AutoConfig |

### variant-b

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.50 | 0.50 — Agent: [SpringBootTest], Reference: [SpringBootTest, AutoConfigureWebTestClient] |
| assertion_quality | 0.80 | 0.80 — GreetingHandlerTest.hello_returnsGreetingMessage uses AssertJ assertThat on specific value 'Hello, Spring!' via . |
| assertion_style | 1.00 | 1.00 — Agent: 5 assertions, Reference: 2 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +100.0 pp (0.0% → 100.0%) |
| coverage_target_selection | 0.80 | 0.80 — Tests target GreetingHandler (functional routing behavior) and GreetingClient (WebClient message extraction) — bo |
| domain_specific_test_patterns | 1.00 | 1.00 — GreetingHandlerTest uses WebTestClient.bindToRouterFunction (correct for WebFlux functional routing, not .block() |
| error_and_edge_case_coverage | 0.50 | 0.50 — GreetingHandlerTest.hello_withWrongAcceptHeader_returnsNotAcceptable tests one negative path (wrong Accept header |
| import_alignment | 0.71 | 0.71 — Agent: 6 imports, Reference: 6 imports |
| injection_pattern | 0.00 | 0.00 — Agent: [], Reference: [WebTestClient] |
| line_coverage_preserved | — | Drop -100.0% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 6, Reference: 1 |
| test_slice_selection | 1.00 | 1.00 — GreetingHandlerTest loads no Spring context at all — uses WebTestClient.bindToRouterFunction with manually constr |
| version_aware_patterns | 0.80 | 0.80 — Boot 4.x project. No @MockBean used (none needed — no Spring context in unit tests). No javax.* imports. WebTestC |

### variant-c

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.00 | 0.00 — Agent: [ExtendWith, WebFluxTest], Reference: [SpringBootTest, AutoConfigureWebTestClient] |
| assertion_quality | 0.80 | 0.80 — GreetingRouterTest.java asserts specific domain value via assertThat(greeting.message()).isEqualTo("Hello, Spring |
| assertion_style | 0.67 | 0.67 — Agent: 5 assertions, Reference: 2 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +78.9 pp (0.0% → 78.9%) |
| coverage_target_selection | 0.80 | 0.80 — No tests for Greeting record (compiler-generated), ReactiveWebServiceApplication.main(), or inherited framework p |
| domain_specific_test_patterns | 1.00 | 1.00 — GreetingRouterTest.java uses WebTestClient with expectStatus()/expectHeader()/expectBody() — correct reactive int |
| error_and_edge_case_coverage | 0.80 | 0.80 — GreetingRouterTest.java covers wrong Accept header (TEXT_PLAIN) yielding 404; GreetingClientTest.java tests getMe |
| import_alignment | 0.46 | 0.46 — Agent: 13 imports, Reference: 6 imports |
| injection_pattern | 0.17 | 0.17 — Agent: [WebClient.RequestHeadersUriSpec, WebTestClient, WebClient.RequestHeadersSpec, WebClient.ResponseSpec, Web |
| line_coverage_preserved | — | Drop -78.9% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 6, Reference: 1 |
| test_slice_selection | 1.00 | 1.00 — GreetingRouterTest.java uses @WebFluxTest + @Import({GreetingRouter.class, GreetingHandler.class}) — correct slic |
| version_aware_patterns | 1.00 | 1.00 — GreetingRouterTest.java imports org.springframework.boot.webflux.test.autoconfigure.WebFluxTest — the Boot 4.x pa |

### variant-d

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.33 | 0.33 — Agent: [SpringBootTest, WebFluxTest], Reference: [SpringBootTest, AutoConfigureWebTestClient] |
| assertion_quality | 0.80 | 0.80 — GreetingHandlerTest.java asserts HTTP status (isOk()), Content-Type header, and specific domain value via .value( |
| assertion_style | 1.00 | 1.00 — Agent: 3 assertions, Reference: 2 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +100.0 pp (0.0% → 100.0%) |
| coverage_target_selection | 0.80 | 0.80 — Tests target behaviorally significant code: the WebFlux handler endpoint and the WebClient-based GreetingClient.  |
| domain_specific_test_patterns | 0.50 | 0.50 — GreetingHandlerTest.java correctly uses WebTestClient with .exchange()/.expectStatus()/.expectBody() — textbook W |
| error_and_edge_case_coverage | 0.50 | 0.50 — GreetingHandlerTest.java covers happy path (200 OK with JSON) and one error path (404 when accept header is TEXT_ |
| import_alignment | 0.86 | 0.86 — Agent: 7 imports, Reference: 6 imports |
| injection_pattern | 0.50 | 0.50 — Agent: [GreetingClient, WebTestClient], Reference: [WebTestClient] |
| line_coverage_preserved | — | Drop -100.0% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 3, Reference: 1 |
| test_slice_selection | 0.80 | 0.80 — GreetingHandlerTest.java uses @WebFluxTest with @Import({GreetingRouter.class, GreetingHandler.class}) — correct  |
| version_aware_patterns | 1.00 | 1.00 — GreetingHandlerTest.java imports org.springframework.boot.webflux.test.autoconfigure.WebFluxTest — the correct Bo |
