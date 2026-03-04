# spring-petclinic

## Scores by Variant

| Variant | Cov% | T3 | Eff | Eff:BE | Eff:Cost | Eff:RC | Cost | In Tok | Out Tok | Think |
|---------|------|-----|------|--------|----------|--------|------|--------|---------|-------|
| variant-a | 0.0 | 0.87 | 0.685 | 0.875 | 0.163 | 0.875 | $4.19 | 52 | 50633 | 9922 |

## T3 Practice Adherence — Criterion Details

### variant-a

| Criterion | Score | Evidence |
|-----------|-------|----------|
| annotation_alignment | 0.60 | 0.60 — Agent: [WebMvcTest, MockitoBean, ExtendWith], Reference: [SpringBootTest, DataJpaTest, WebMvcTest, MockitoBean, E |
| assertion_quality | 0.80 | 0.80 — Domain model tests use rich AssertJ assertions: VetTest.java uses extracting(Specialty::getName).containsExactly( |
| assertion_style | 0.38 | 0.38 — Agent: 134 assertions, Reference: 214 assertions |
| command_execution | — | Command executed successfully |
| coverage_target_selection | 0.80 | 0.80 — Tests focus on behaviorally significant code: OwnerTest.java covers domain logic in Owner.addPet(), getPet(String |
| domain_specific_test_patterns | 0.80 | 0.80 — MVC tests correctly use MockMvc with @WebMvcTest scoped to specific controllers. VetControllerTest.java includes  |
| error_and_edge_case_coverage | 0.80 | 0.80 — Validation errors well covered: OwnerControllerTest.java tests processCreationFormWithErrorsReturnsCreateForm and |
| import_alignment | 0.65 | 0.65 — Agent: 13 imports, Reference: 20 imports |
| injection_pattern | 0.67 | 0.67 — Agent: [VetRepository, OwnerRepository, MockMvc, PetTypeRepository], Reference: [RestTemplateBuilder, TestRestTem |
| test_method_coverage | 1.00 | 1.00 — Agent: 60, Reference: 59 |
| test_slice_selection | 1.00 | 1.00 — Every controller test uses @WebMvcTest scoped to a specific controller (e.g., OwnerControllerTest.java @WebMvcTes |
| version_aware_patterns | 1.00 | 1.00 — Boot version is 4.0.1. All mock injection uses @MockitoBean (org.springframework.test.context.bean.override.mocki |
