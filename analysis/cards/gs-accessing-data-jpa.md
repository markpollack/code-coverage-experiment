# gs-accessing-data-jpa

## Scores by Variant

| Variant | Cov% | T3 | Eff | Eff:BE | Eff:Cost | Eff:RC | Cost | In Tok | Out Tok | Think |
|---------|------|-----|------|--------|----------|--------|------|--------|---------|-------|
| control | 94.6 | 0.5 | 0.96 | 1.0 | 0.852 | 1.0 | $0.74 | 28 | 7496 | 855 |
| variant-a | 94.6 | 0.6 | 0.94 | 1.0 | 0.774 | 1.0 | $1.13 | 32 | 14972 | 2815 |
| variant-b | 94.6 | 0.73 | 0.943 | 1.0 | 0.785 | 1.0 | $1.08 | 30 | 13054 | 2999 |
| variant-c | 94.6 | 0.68 | 0.66 | 0.625 | 0.754 | 0.625 | $1.23 | 1010 | 14071 | 3323 |
| variant-d | 94.6 | 0.73 | 0.503 | 0.5 | 0.51 | 0.5 | $2.45 | 1070 | 21171 | 4446 |

## T3 Practice Adherence — Criterion Details

### control

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.00 | 0.00 — Agent: [SpringBootTest], Reference: [DataJpaTest] |
| assertion_quality | 0.50 | 0.50 — CustomerRepositoryTest.java testSaveAndFindAll uses hasSizeGreaterThanOrEqualTo(2) — shallow, contaminated by dat |
| assertion_style | 1.00 | 1.00 — Agent: 17 assertions, Reference: 1 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +94.6 pp (0.0% → 94.6%) |
| coverage_target_selection | 0.50 | 0.50 — CustomerTest.java tests plain constructor, getters (getFirstName, getLastName, getId), and toString() on a JPA en |
| domain_specific_test_patterns | 0.20 | 0.20 — CustomerRepositoryTest.java uses @SpringBootTest instead of @DataJpaTest — wrong slice for a repository test; tes |
| error_and_edge_case_coverage | 0.50 | 0.50 — CustomerRepositoryTest.java testFindByLastNameNoResults covers the empty-result edge case with assertThat(result) |
| import_alignment | 0.80 | 0.80 — Agent: 5 imports, Reference: 4 imports |
| injection_pattern | 0.50 | 0.50 — Agent: [CustomerRepository], Reference: [CustomerRepository, TestEntityManager] |
| line_coverage_preserved | — | Drop -94.6% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 10, Reference: 1 |
| test_slice_selection | 0.50 | 0.50 — CustomerRepositoryTest.java uses @SpringBootTest where @DataJpaTest would suffice — this is a pure repository tes |
| version_aware_patterns | 0.80 | 0.80 — Boot 4.x project; Customer.java uses jakarta.persistence.* imports (correct for Boot 3.x+, not javax.*); no @Mock |

### variant-a

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.33 | 0.33 — Agent: [DataJpaTest, TestConfiguration, ExtendWith], Reference: [DataJpaTest] |
| assertion_quality | 0.50 | 0.50 — CustomerRepositoryTest.java uses AssertJ extracting(Customer::getFirstName).containsExactlyInAnyOrder(...) — good |
| assertion_style | 0.50 | 0.50 — Agent: 33 assertions, Reference: 1 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +94.6 pp (0.0% → 94.6%) |
| coverage_target_selection | 0.50 | 0.50 — CustomerTest.java tests toString(), constructor, and getters on a plain JPA entity — low behavioral value, simila |
| domain_specific_test_patterns | 0.50 | 0.50 — CustomerRepositoryTest.java correctly uses TestEntityManager for setup and calls flush() in most tests. However,  |
| error_and_edge_case_coverage | 0.50 | 0.50 — CustomerRepositoryTest.java includes findByLastName_noMatch_returnsEmptyList() — tests the empty-result edge case |
| import_alignment | 0.44 | 0.44 — Agent: 9 imports, Reference: 4 imports |
| injection_pattern | 1.00 | 1.00 — Agent: [CustomerRepository, TestEntityManager], Reference: [CustomerRepository, TestEntityManager] |
| line_coverage_preserved | — | Drop -94.6% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 20, Reference: 1 |
| test_slice_selection | 0.80 | 0.80 — CustomerRepositoryTest.java uses @DataJpaTest — correct slice for JPA. CustomerTest.java uses plain JUnit with no |
| version_aware_patterns | 0.80 | 0.80 — CustomerRepositoryTest.java uses Boot 4.x import paths: org.springframework.boot.data.jpa.test.autoconfigure.Data |

### variant-b

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.50 | 0.50 — Agent: [SpringBootTest, DataJpaTest], Reference: [DataJpaTest] |
| assertion_quality | 0.80 | 0.80 — CustomerRepositoryTest.java uses AssertJ fluent assertions with extracting(Customer::getFirstName).containsExactl |
| assertion_style | 1.00 | 1.00 — Agent: 22 assertions, Reference: 1 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +94.6 pp (0.0% → 94.6%) |
| coverage_target_selection | 0.50 | 0.50 — CustomerTest.java (5 tests) exclusively tests the Customer entity's constructor, getters, id nullability before p |
| domain_specific_test_patterns | 0.50 | 0.50 — CustomerRepositoryTest.java correctly injects TestEntityManager for test data setup and calls entityManager.flush |
| error_and_edge_case_coverage | 0.80 | 0.80 — CustomerRepositoryTest.java covers: empty result (findByLastNameReturnsEmptyWhenNoMatch), single match, multiple  |
| import_alignment | 1.00 | 1.00 — Agent: 4 imports, Reference: 4 imports |
| injection_pattern | 1.00 | 1.00 — Agent: [CustomerRepository, TestEntityManager], Reference: [CustomerRepository, TestEntityManager] |
| line_coverage_preserved | — | Drop -94.6% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 15, Reference: 1 |
| test_slice_selection | 0.80 | 0.80 — CustomerRepositoryTest.java correctly uses @DataJpaTest (not @SpringBootTest); CustomerTest.java uses plain JUnit |
| version_aware_patterns | 1.00 | 1.00 — CustomerRepositoryTest.java uses Boot 4.x reorganized import paths: org.springframework.boot.data.jpa.test.autoco |

### variant-c

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.50 | 0.50 — Agent: [SpringBootTest, DataJpaTest], Reference: [DataJpaTest] |
| assertion_quality | 0.80 | 0.80 — CustomerRepositoryTest uses AssertJ extracting(Customer::getFirstName).containsExactlyInAnyOrder('Alice','Bob') a |
| assertion_style | 1.00 | 1.00 — Agent: 21 assertions, Reference: 1 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +94.6 pp (0.0% → 94.6%) |
| coverage_target_selection | 0.50 | 0.50 — CustomerTest.java tests getters (getFirstName_returnsValueSetInConstructor, getLastName_returnsValueSetInConstruc |
| domain_specific_test_patterns | 0.50 | 0.50 — CustomerRepositoryTest correctly uses TestEntityManager for data setup and calls flush() before reads (entityMana |
| error_and_edge_case_coverage | 0.50 | 0.50 — CustomerRepositoryTest.findByLastName_noMatch_returnsEmpty() covers the empty-result edge case. However, no tests |
| import_alignment | 1.00 | 1.00 — Agent: 4 imports, Reference: 4 imports |
| injection_pattern | 1.00 | 1.00 — Agent: [CustomerRepository, TestEntityManager], Reference: [CustomerRepository, TestEntityManager] |
| line_coverage_preserved | — | Drop -94.6% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 12, Reference: 1 |
| test_slice_selection | 0.80 | 0.80 — CustomerRepositoryTest.java uses @DataJpaTest (correct slice for JPA); CustomerTest.java uses plain JUnit with no |
| version_aware_patterns | 1.00 | 1.00 — CustomerRepositoryTest.java imports org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest and org.spri |

### variant-d

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.33 | 0.33 — Agent: [SpringBootTest, DataJpaTest, MockitoBean], Reference: [DataJpaTest] |
| assertion_quality | 0.70 | 0.70 — CustomerRepositoryTest.java uses AssertJ with specific value checks in most tests (e.g., assertThat(found.get(0). |
| assertion_style | 1.00 | 1.00 — Agent: 17 assertions, Reference: 1 assertions |
| command_execution | — | Command executed successfully |
| coverage_improved | — | +94.6 pp (0.0% → 94.6%) |
| coverage_target_selection | 0.40 | 0.40 — CustomerTest.java (5 tests) targets entirely low-value code: constructor behavior, getter returns, and toString f |
| domain_specific_test_patterns | 0.70 | 0.70 — CustomerRepositoryTest.java correctly uses @DataJpaTest, @Autowired TestEntityManager for test data setup (not th |
| error_and_edge_case_coverage | 0.80 | 0.80 — CustomerRepositoryTest.java covers: empty result (findByLastName_returnsEmptyList_whenNoMatch), case-sensitivity  |
| import_alignment | 0.80 | 0.80 — Agent: 5 imports, Reference: 4 imports |
| injection_pattern | 0.67 | 0.67 — Agent: [CustomerRepository, CommandLineRunner, TestEntityManager], Reference: [CustomerRepository, TestEntityMana |
| line_coverage_preserved | — | Drop -94.6% <= 5.0% threshold |
| test_method_coverage | 1.00 | 1.00 — Agent: 15, Reference: 1 |
| test_slice_selection | 0.80 | 0.80 — CustomerRepositoryTest.java uses @DataJpaTest (correct narrow slice for JPA); CustomerTest.java uses plain JUnit  |
| version_aware_patterns | 1.00 | 1.00 — CustomerRepositoryTest.java uses @MockitoBean (correct Boot 4.x annotation, not deprecated @MockBean); imports or |
