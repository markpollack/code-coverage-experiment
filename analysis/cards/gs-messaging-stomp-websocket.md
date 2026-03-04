# gs-messaging-stomp-websocket

## Scores by Variant

| Variant | Cov% | T3 | Eff | Eff:BE | Eff:Cost | Eff:RC | Cost | In Tok | Out Tok | Think |
|---------|------|-----|------|--------|----------|--------|------|--------|---------|-------|
| control | 92.3 | 0.45 | 0.796 | 0.75 | 0.922 | 0.75 | $0.39 | 11 | 4537 | 601 |
| variant-a | 84.6 | 0.65 | 0.883 | 0.875 | 0.905 | 0.875 | $0.47 | 14 | 7120 | 1021 |
| variant-b | 92.3 | 0.55 | 0.973 | 1.0 | 0.898 | 1.0 | $0.51 | 14 | 7104 | 1952 |
| variant-c | 88.5 | 0.5 | 0.964 | 1.0 | 0.864 | 1.0 | $0.68 | 16 | 10512 | 1862 |
| variant-d | 84.6 | 0.5 | 0.925 | 1.0 | 0.719 | 1.0 | $1.4 | 25 | 14489 | 2712 |

## T3 Practice Adherence — Criterion Details

### control

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.50 | 0.50 — Agent: [SpringBootTest, ExtendWith], Reference: [SpringBootTest] |
| assertion_quality | 0.50 | 0.50 — GreetingControllerTest has domain-meaningful assertions: assertEquals("Hello, World!", greeting.getContent()) and |
| assertion_style | 0.25 | 0.25 — Agent: 13 assertions, Reference: 1 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +92.3 pp (0.0% → 92.3%) |
| coverage_target_selection | 0.20 | 0.20 — GreetingTest (3 tests) and HelloMessageTest (4 tests) test POJO constructors, getters, and setters exclusively —  |
| domain_specific_test_patterns | 0.20 | 0.20 — The production code is a WebSocket/STOMP application (@EnableWebSocketMessageBroker, @MessageMapping, @SendTo). T |
| error_and_edge_case_coverage | 0.50 | 0.50 — GreetingControllerTest covers an important edge case: HTML/XSS escaping with a <script> input and special charact |
| import_alignment | 0.57 | 0.57 — Agent: 7 imports, Reference: 4 imports |
| injection_pattern | 1.00 | 1.00 — Agent: [], Reference: [] |
| line_coverage_preserved | — | Drop -92.3% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 13, Reference: 1 |
| test_slice_selection | 0.50 | 0.50 — Most tests avoid Spring context entirely (GreetingControllerTest, GreetingTest, HelloMessageTest, WebSocketConfig |
| version_aware_patterns | 0.80 | 0.80 — Boot 3.x project. All tests use JUnit 5 (@Test, @ExtendWith(MockitoExtension.class)) consistently. MessagingStomp |

### variant-a

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 1.00 | 1.00 — Agent: [SpringBootTest], Reference: [SpringBootTest] |
| assertion_quality | 0.50 | 0.50 — GreetingControllerTest has specific-value assertEquals assertions (e.g., assertEquals("Hello, World!", result.get |
| assertion_style | 0.20 | 0.20 — Agent: 15 assertions, Reference: 1 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +84.6 pp (0.0% → 84.6%) |
| coverage_target_selection | 0.50 | 0.50 — GreetingControllerTest and StompIntegrationTest target behaviorally significant code — the greeting() method's es |
| domain_specific_test_patterns | 0.50 | 0.50 — StompIntegrationTest correctly uses @SpringBootTest(RANDOM_PORT) with StandardWebSocketClient + WebSocketStompCli |
| error_and_edge_case_coverage | 0.60 | 0.60 — GreetingControllerTest covers XSS injection (greeting_escapesHtmlInName), ampersand escaping (greeting_escapesAmp |
| import_alignment | 0.67 | 0.67 — Agent: 6 imports, Reference: 4 imports |
| injection_pattern | 1.00 | 1.00 — Agent: [], Reference: [] |
| line_coverage_preserved | — | Drop -84.6% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 10, Reference: 1 |
| test_slice_selection | 0.80 | 0.80 — GreetingControllerTest uses plain JUnit with no Spring context — correct, since GreetingController.greeting() has |
| version_aware_patterns | 1.00 | 1.00 — Project uses Spring Boot 3.5.11 (Boot 3.x). No @MockBean or @SpyBean annotations are used anywhere — plain Mockit |

### variant-b

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 1.00 | 1.00 — Agent: [SpringBootTest], Reference: [SpringBootTest] |
| assertion_quality | 0.50 | 0.50 — GreetingControllerTest has specific value assertions (assertThat(greeting.getContent()).isEqualTo('Hello, World!' |
| assertion_style | 0.00 | 0.00 — Agent: 7 assertions, Reference: 1 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +92.3 pp (0.0% → 92.3%) |
| coverage_target_selection | 0.30 | 0.30 — HelloMessageTest tests getName() and setName() on a plain POJO with no business logic. GreetingTest tests getCont |
| domain_specific_test_patterns | 0.20 | 0.20 — The production code is a WebSocket/STOMP application (WebSocketConfig, GreetingController with @MessageMapping/@S |
| error_and_edge_case_coverage | 0.80 | 0.80 — GreetingControllerTest covers: plain name (happy path), XSS injection via '<script>alert()</script>' (security ed |
| import_alignment | 0.40 | 0.40 — Agent: 3 imports, Reference: 4 imports |
| injection_pattern | 1.00 | 1.00 — Agent: [], Reference: [] |
| line_coverage_preserved | — | Drop -92.3% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 8, Reference: 1 |
| test_slice_selection | 0.50 | 0.50 — GreetingControllerTest uses plain JUnit (no Spring context) to unit-test the STOMP controller method directly — p |
| version_aware_patterns | 1.00 | 1.00 — Boot 3.5.11 (3.x). No @MockBean or @MockitoBean used (no mocking needed). @SpringBootTest used correctly in Appli |

### variant-c

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.00 | 0.00 — Agent: [], Reference: [SpringBootTest] |
| assertion_quality | 0.50 | 0.50 — GreetingControllerTest.java uses domain-meaningful AssertJ assertions: isEqualTo("Hello, World!"), doesNotContain |
| assertion_style | 0.00 | 0.00 — Agent: 10 assertions, Reference: 1 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +88.5 pp (0.0% → 88.5%) |
| coverage_target_selection | 0.50 | 0.50 — GreetingControllerTest.java targets meaningful business logic: HTML escaping and greeting format — high value. Gr |
| domain_specific_test_patterns | 0.20 | 0.20 — The production code is a WebSocket/STOMP application (WebSocketConfig.java registers /gs-guide-websocket endpoint |
| error_and_edge_case_coverage | 0.50 | 0.50 — GreetingControllerTest.java includes a meaningful edge case: HTML-escaping of XSS input (<script> → &lt;script&gt |
| import_alignment | 0.50 | 0.50 — Agent: 5 imports, Reference: 4 imports |
| injection_pattern | 1.00 | 1.00 — Agent: [], Reference: [] |
| line_coverage_preserved | — | Drop -88.5% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 8, Reference: 1 |
| test_slice_selection | 0.50 | 0.50 — No test loads a Spring context unnecessarily — GreetingControllerTest, GreetingTest, HelloMessageTest, and WebSoc |
| version_aware_patterns | 0.80 | 0.80 — Boot 3.x project (spring-boot-starter-parent 3.5.11). No Spring test annotations are used in any test class, so t |

### variant-d

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 1.00 | 1.00 — Agent: [SpringBootTest], Reference: [SpringBootTest] |
| assertion_quality | 0.50 | 0.50 — GreetingControllerTest.java uses AssertJ with specific value checks — isEqualTo("Hello, World!"), doesNotContain( |
| assertion_style | 0.00 | 0.00 — Agent: 8 assertions, Reference: 1 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +84.6 pp (0.0% → 84.6%) |
| coverage_target_selection | 0.50 | 0.50 — GreetingControllerTest.java targets behaviorally meaningful logic — the HTML escaping transformation and content  |
| domain_specific_test_patterns | 0.20 | 0.20 — The project is a WebSocket/STOMP application. The prescribed pattern requires @SpringBootTest(webEnvironment=RAND |
| error_and_edge_case_coverage | 0.50 | 0.50 — GreetingControllerTest.java covers several meaningful edge cases: empty name input, HTML injection (XSS via <scri |
| import_alignment | 0.29 | 0.29 — Agent: 5 imports, Reference: 4 imports |
| injection_pattern | 0.00 | 0.00 — Agent: [ApplicationContext], Reference: [] |
| line_coverage_preserved | — | Drop -84.6% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 6, Reference: 1 |
| test_slice_selection | 0.50 | 0.50 — GreetingControllerTest.java uses plain JUnit with direct instantiation (no Spring context) — appropriate for test |
| version_aware_patterns | 0.80 | 0.80 — Boot 3.x project. WebSocketConfigIntegrationTest.java uses @SpringBootTest which is correct for Boot 3.x. Neither |
