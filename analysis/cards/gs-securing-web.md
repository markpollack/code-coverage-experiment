# gs-securing-web

## Scores by Variant

| Variant | Cov% | T3 | Eff | Eff:BE | Eff:Cost | Eff:RC | Cost | In Tok | Out Tok | Think |
|---------|------|-----|------|--------|----------|--------|------|--------|---------|-------|
| control | 91.3 | 0.72 | 0.68 | 0.625 | 0.83 | 0.625 | $0.85 | 26 | 8597 | 1096 |
| variant-a | 91.3 | 0.68 | 0.962 | 1.0 | 0.856 | 1.0 | $0.72 | 22 | 9027 | 1531 |
| variant-b | 91.3 | 0.83 | 0.933 | 1.0 | 0.75 | 1.0 | $1.25 | 37 | 13025 | 1874 |
| variant-c | 91.3 | 0.78 | 0.955 | 1.0 | 0.833 | 1.0 | $0.84 | 26 | 8729 | 1098 |
| variant-d | 91.3 | 0.67 | 0.733 | 0.75 | 0.686 | 0.75 | $1.57 | 37 | 11641 | 1865 |

## T3 Practice Adherence — Criterion Details

### control

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 1.00 | 1.00 — Agent: [AutoConfigureMockMvc, SpringBootTest], Reference: [AutoConfigureMockMvc, SpringBootTest] |
| assertion_quality | 0.70 | 0.70 — WebSecurityConfigTest.java has strong HTTP assertions: status().is3xxRedirection(), redirectedUrl("/login"), auth |
| assertion_style | 0.38 | 0.38 — Agent: 48 assertions, Reference: 12 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +91.3 pp (0.0% → 91.3%) |
| coverage_target_selection | 0.50 | 0.50 — MvcConfigTest.java tests the MvcConfig @Configuration class (addViewControllers) — this is framework plumbing tha |
| domain_specific_test_patterns | 0.80 | 0.80 — Security domain (present): WebSecurityConfigTest.java uses @WithMockUser for authenticated scenarios, SecurityMoc |
| error_and_edge_case_coverage | 0.80 | 0.80 — WebSecurityConfigTest.java covers: unauthenticated redirect to /login (helloPageRedirectsToLoginWhenUnauthenticat |
| import_alignment | 0.83 | 0.83 — Agent: 5 imports, Reference: 6 imports |
| injection_pattern | 0.33 | 0.33 — Agent: [PasswordEncoder, UserDetailsService, MockMvc], Reference: [MockMvc] |
| line_coverage_preserved | — | Drop -91.3% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 22, Reference: 5 |
| test_slice_selection | 0.50 | 0.50 — MvcConfigTest.java and WebSecurityConfigTest.java both use @SpringBootTest + @AutoConfigureMockMvc for what are e |
| version_aware_patterns | 1.00 | 1.00 — Both MvcConfigTest.java and WebSecurityConfigTest.java import org.springframework.boot.webmvc.test.autoconfigure. |

### variant-a

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 1.00 | 1.00 — Agent: [AutoConfigureMockMvc, SpringBootTest], Reference: [AutoConfigureMockMvc, SpringBootTest] |
| assertion_quality | 0.50 | 0.50 — SecuringWebTests.java uses AssertJ-fluent assertions via MockMvcTester (assertThat(mvc.get().uri(...)).hasStatus( |
| assertion_style | 0.23 | 0.23 — Agent: 11 assertions, Reference: 12 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +91.3 pp (0.0% → 91.3%) |
| coverage_target_selection | 0.80 | 0.80 — SecuringWebTests.java focuses entirely on meaningful security behavior (authentication, authorization, form login |
| domain_specific_test_patterns | 0.80 | 0.80 — MVC/Security domain only (no JPA, WebFlux, or WebSocket in production code). SecuringWebTests.java correctly uses |
| error_and_edge_case_coverage | 0.50 | 0.50 — SecuringWebTests.java covers: unauthenticated redirect to login (helloRequiresAuthentication), authenticated acce |
| import_alignment | 1.00 | 1.00 — Agent: 6 imports, Reference: 6 imports |
| injection_pattern | 0.00 | 0.00 — Agent: [MockMvcTester], Reference: [MockMvc] |
| line_coverage_preserved | — | Drop -91.3% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 8, Reference: 5 |
| test_slice_selection | 0.50 | 0.50 — SecuringWebTests.java uses @SpringBootTest + @AutoConfigureMockMvc for all tests. The production code has no serv |
| version_aware_patterns | 1.00 | 1.00 — SecuringWebTests.java imports org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc (Boot 4.x-s |

### variant-b

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 1.00 | 1.00 — Agent: [AutoConfigureMockMvc, SpringBootTest], Reference: [AutoConfigureMockMvc, SpringBootTest] |
| assertion_quality | 0.80 | 0.80 — SecuringWebApplicationTests: asserts specific view names (view().name("home"), view().name("hello")), specific re |
| assertion_style | 1.00 | 1.00 — Agent: 30 assertions, Reference: 12 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +91.3 pp (0.0% → 91.3%) |
| coverage_target_selection | 0.80 | 0.80 — SecuringWebApplicationTests targets observable security policy outcomes (access control, login redirects, authent |
| domain_specific_test_patterns | 0.80 | 0.80 — MVC/Security domain (only domain present — no JPA, no WebFlux, no WebSocket): uses @WithMockUser for authenticate |
| error_and_edge_case_coverage | 0.80 | 0.80 — Covers unauthenticated redirect (helloPageRedirectsToLoginWhenUnauthenticated), wrong-password failure (formLogin |
| import_alignment | 1.00 | 1.00 — Agent: 6 imports, Reference: 6 imports |
| injection_pattern | 1.00 | 1.00 — Agent: [MockMvc], Reference: [MockMvc] |
| line_coverage_preserved | — | Drop -91.3% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 13, Reference: 5 |
| test_slice_selection | 0.80 | 0.80 — SecuringWebApplicationTests uses @SpringBootTest — justified because the tests exercise the full security filter  |
| version_aware_patterns | 1.00 | 1.00 — Boot version is 4.0.3. SecuringWebApplicationTests imports org.springframework.boot.webmvc.test.autoconfigure.Aut |

### variant-c

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 1.00 | 1.00 — Agent: [AutoConfigureMockMvc, SpringBootTest], Reference: [AutoConfigureMockMvc, SpringBootTest] |
| assertion_quality | 0.80 | 0.80 — WebSecurityConfigTest.java uses AssertJ throughout: assertThat(encoder.matches(...)).isTrue(), extracting("author |
| assertion_style | 1.00 | 1.00 — Agent: 32 assertions, Reference: 12 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +91.3 pp (0.0% → 91.3%) |
| coverage_target_selection | 0.50 | 0.50 — WebSecurityConfigTest.java tests the @Configuration class directly (WebSecurityConfig), which the rubric classifi |
| domain_specific_test_patterns | 0.80 | 0.80 — SecuringWebApplicationTests.java correctly uses @WithMockUser for authenticated tests, .with(csrf()) on all POST  |
| error_and_edge_case_coverage | 0.80 | 0.80 — SecuringWebApplicationTests.java covers: unauthenticated access to protected /hello (3xx redirect to /login), inv |
| import_alignment | 1.00 | 1.00 — Agent: 6 imports, Reference: 6 imports |
| injection_pattern | 1.00 | 1.00 — Agent: [MockMvc], Reference: [MockMvc] |
| line_coverage_preserved | — | Drop -91.3% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 15, Reference: 5 |
| test_slice_selection | 0.80 | 0.80 — SecuringWebApplicationTests.java uses @SpringBootTest + @AutoConfigureMockMvc, which is appropriate for testing t |
| version_aware_patterns | 1.00 | 1.00 — SecuringWebApplicationTests.java uses the Boot 4.x import path: org.springframework.boot.webmvc.test.autoconfigur |

### variant-d

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 1.00 | 1.00 — Agent: [AutoConfigureMockMvc, SpringBootTest], Reference: [AutoConfigureMockMvc, SpringBootTest] |
| assertion_quality | 0.50 | 0.50 — SecuringWebApplicationTests.contextLoads() has zero assertions — the test body is empty. MvcSecurityIntegrationTe |
| assertion_style | 0.75 | 0.75 — Agent: 21 assertions, Reference: 12 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +91.3 pp (0.0% → 91.3%) |
| coverage_target_selection | 0.50 | 0.50 — SecuringWebApplicationTests.contextLoads() is a zero-assertion test — it exercises Spring context loading and @Be |
| domain_specific_test_patterns | 0.80 | 0.80 — MvcSecurityIntegrationTest.java correctly uses @WithMockUser for authenticated tests; uses .with(csrf()) on POST  |
| error_and_edge_case_coverage | 0.70 | 0.70 — MvcSecurityIntegrationTest.java covers: unauthenticated redirect (helloRequiresAuthentication → 3xx to /login), a |
| import_alignment | 0.83 | 0.83 — Agent: 5 imports, Reference: 6 imports |
| injection_pattern | 1.00 | 1.00 — Agent: [MockMvc], Reference: [MockMvc] |
| line_coverage_preserved | — | Drop -91.3% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 7, Reference: 5 |
| test_slice_selection | 0.70 | 0.70 — MvcSecurityIntegrationTest.java uses @SpringBootTest(webEnvironment=MOCK)+@AutoConfigureMockMvc, which is appropr |
| version_aware_patterns | 0.80 | 0.80 — MvcSecurityIntegrationTest.java imports org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc — |
