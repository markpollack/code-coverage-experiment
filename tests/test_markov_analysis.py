"""
Unit tests for make_markov_analysis.py

Run with:
    .venv/bin/python -m pytest tests/test_markov_analysis.py -v
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Make scripts importable without installing
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from make_markov_analysis import (
    STATES,
    classify_state,
    build_transition_counts,
    normalize_to_probability_matrix,
    compute_fundamental_matrix,
    run_sanity_checks,
)


# ---------------------------------------------------------------------------
# classify_state
# ---------------------------------------------------------------------------

class TestClassifyState:
    def test_jar_inspect_bash_jar_tf(self):
        assert classify_state("Bash", "jar tf /tmp/foo.jar") == "JAR_INSPECT"

    def test_jar_inspect_bash_javap(self):
        assert classify_state("Bash", "javap -c Foo.class") == "JAR_INSPECT"

    def test_jar_find_bash_find_m2(self):
        assert classify_state("Bash", "find /home/.m2 -name '*.jar'") == "JAR_FIND"

    def test_jar_inspect_bash_jar_tf_in_m2(self):
        # "jar tf" inspects contents of a JAR — even if the JAR is in .m2.
        # JAR_FIND requires "find" in the command (searching by filename).
        assert classify_state("Bash", "jar tf /home/.m2/repository/foo.jar") == "JAR_INSPECT"

    def test_jar_find_bash_find_m2_by_name(self):
        # "find ... -name *.jar" in .m2 = searching for JARs = JAR_FIND
        assert classify_state("Bash", "find /home/.m2 -name 'slf4j*.jar'") == "JAR_FIND"

    def test_build_mvnw(self):
        assert classify_state("Bash", "./mvnw test") == "BUILD"

    def test_build_mvn_compile(self):
        assert classify_state("Bash", "mvn compile") == "BUILD"

    def test_explore_bash_generic(self):
        assert classify_state("Bash", "ls src/main/java") == "EXPLORE"

    def test_write_test(self):
        assert classify_state("Write", "src/test/java/com/example/FooTest.java") == "WRITE_TEST"

    def test_write_non_test_is_explore(self):
        # Write to non-test file: falls through to EXPLORE
        assert classify_state("Write", "src/main/java/Foo.java") == "EXPLORE"

    def test_fix_test_edit(self):
        assert classify_state("Edit", "src/test/java/FooTest.java") == "FIX_TEST"

    def test_fix_test_str_replace_editor(self):
        assert classify_state("str_replace_editor", "FooTest.java") == "FIX_TEST"

    def test_read_kb_knowledge_index(self):
        assert classify_state("Read", "/workspace/knowledge/index.md") == "READ_KB"

    def test_read_kb_jacoco(self):
        assert classify_state("Read", "/workspace/knowledge/jacoco-patterns.md") == "READ_KB"

    def test_read_kb_coverage_fundamentals(self):
        assert classify_state("Read", "/workspace/coverage-fundamentals.md") == "READ_KB"

    def test_read_source(self):
        assert classify_state("Read", "src/main/java/com/example/Service.java") == "READ_SOURCE"

    def test_read_sae(self):
        assert classify_state("Read", "/workspace/project-analysis/report.json") == "READ_SAE"

    def test_glob_explore(self):
        assert classify_state("Glob", "src/**/*.java") == "EXPLORE"

    def test_glob_m2_is_jar_find(self):
        assert classify_state("Glob", "/home/user/.m2/**/*.jar") == "JAR_FIND"

    def test_grep_explore(self):
        assert classify_state("Grep", "class FooService") == "EXPLORE"

    def test_empty_strings(self):
        # Should not raise; falls through to EXPLORE
        assert classify_state("", "") == "EXPLORE"

    def test_none_tool_name(self):
        result = classify_state(None, "something")
        assert result in STATES

    def test_case_insensitive_bash(self):
        # tool names coming from the harness may vary in case
        assert classify_state("BASH", "./mvnw test") == "BUILD"


# ---------------------------------------------------------------------------
# build_transition_counts
# ---------------------------------------------------------------------------

def _make_tools_df(variant, sequences):
    """Build a minimal tools DataFrame from a dict of item_slug -> state list."""
    rows = []
    seq = 0
    for item_slug, states in sequences.items():
        for state in states:
            rows.append({
                "variant": variant,
                "item_slug": item_slug,
                "global_seq": seq,
                "state": state,
                "tool_name": "Bash",
                "target": "",
            })
            seq += 1
    return pd.DataFrame(rows)


class TestBuildTransitionCounts:
    def test_single_item_simple_chain(self):
        df = _make_tools_df("v", {"item-1": ["EXPLORE", "BUILD", "BUILD"]})
        counts = build_transition_counts(df, "v")
        assert counts[("EXPLORE", "BUILD")] == 1
        assert counts[("BUILD", "BUILD")] == 1

    def test_two_items_isolated(self):
        # Transitions from item-1 must not bleed into item-2
        df = _make_tools_df("v", {
            "item-1": ["EXPLORE", "BUILD"],
            "item-2": ["READ_KB", "WRITE_TEST"],
        })
        counts = build_transition_counts(df, "v")
        # Cross-item boundary MUST NOT appear
        assert ("BUILD", "READ_KB") not in counts
        assert counts.get(("EXPLORE", "BUILD"), 0) == 1
        assert counts.get(("READ_KB", "WRITE_TEST"), 0) == 1

    def test_self_loop_counted(self):
        df = _make_tools_df("v", {"item-1": ["JAR_INSPECT", "JAR_INSPECT", "JAR_INSPECT"]})
        counts = build_transition_counts(df, "v")
        assert counts[("JAR_INSPECT", "JAR_INSPECT")] == 2

    def test_single_state_no_transitions(self):
        df = _make_tools_df("v", {"item-1": ["BUILD"]})
        counts = build_transition_counts(df, "v")
        assert len(counts) == 0

    def test_wrong_variant_excluded(self):
        df = _make_tools_df("v", {"item-1": ["EXPLORE", "BUILD"]})
        df2 = _make_tools_df("other", {"item-2": ["JAR_INSPECT", "JAR_FIND"]})
        combined = pd.concat([df, df2], ignore_index=True)
        counts = build_transition_counts(combined, "v")
        assert ("JAR_INSPECT", "JAR_FIND") not in counts


# ---------------------------------------------------------------------------
# normalize_to_probability_matrix
# ---------------------------------------------------------------------------

class TestNormalizeToProbabilityMatrix:
    def test_row_sums_to_one(self):
        counts = {("EXPLORE", "BUILD"): 3, ("EXPLORE", "READ_KB"): 1, ("BUILD", "BUILD"): 4}
        p = normalize_to_probability_matrix(counts, STATES)
        explore_idx = STATES.index("EXPLORE")
        build_idx = STATES.index("BUILD")
        assert abs(p[explore_idx].sum() - 1.0) < 1e-10
        assert abs(p[build_idx].sum() - 1.0) < 1e-10

    def test_empty_row_stays_zero(self):
        # States with no outgoing transitions should have row sum = 0, not 1
        counts = {("EXPLORE", "BUILD"): 5}
        p = normalize_to_probability_matrix(counts, STATES)
        build_idx = STATES.index("BUILD")
        # BUILD has no outgoing counts -> row is all zeros
        assert p[build_idx].sum() == 0.0

    def test_probability_values_correct(self):
        counts = {("EXPLORE", "BUILD"): 2, ("EXPLORE", "READ_KB"): 2}
        p = normalize_to_probability_matrix(counts, STATES)
        explore_idx = STATES.index("EXPLORE")
        build_idx = STATES.index("BUILD")
        read_kb_idx = STATES.index("READ_KB")
        assert abs(p[explore_idx, build_idx] - 0.5) < 1e-10
        assert abs(p[explore_idx, read_kb_idx] - 0.5) < 1e-10

    def test_self_loop_probability(self):
        counts = {("JAR_INSPECT", "JAR_INSPECT"): 3, ("JAR_INSPECT", "BUILD"): 1}
        p = normalize_to_probability_matrix(counts, STATES)
        idx = STATES.index("JAR_INSPECT")
        assert abs(p[idx, idx] - 0.75) < 1e-10

    def test_all_rows_sum_to_one_or_zero(self):
        counts = {("EXPLORE", "BUILD"): 1, ("BUILD", "FIX_TEST"): 2}
        p = normalize_to_probability_matrix(counts, STATES)
        row_sums = p.sum(axis=1)
        for i, s in enumerate(STATES):
            assert row_sums[i] < 1e-10 or abs(row_sums[i] - 1.0) < 1e-10, \
                f"State {s} row sum = {row_sums[i]}"


# ---------------------------------------------------------------------------
# compute_fundamental_matrix
# ---------------------------------------------------------------------------

class TestComputeFundamentalMatrix:
    def test_zero_Q_gives_identity(self):
        # Q = 0: agent never revisits any transient state; N = inv(I - 0) = I
        Q = np.zeros((3, 3))
        N = compute_fundamental_matrix(Q)
        np.testing.assert_allclose(N, np.eye(3), atol=1e-10)

    def test_scalar_geometric_series(self):
        # Q = [[0.5]]: agent stays in state with prob 0.5 each step.
        # N = inv(I - [[0.5]]) = inv([[0.5]]) = [[2.0]]
        # Expected visits = 1 + 0.5 + 0.25 + ... = 2.0
        Q = np.array([[0.5]])
        N = compute_fundamental_matrix(Q)
        np.testing.assert_allclose(N, np.array([[2.0]]), atol=1e-10)

    def test_two_state_chain(self):
        # Two transient states: P(stay A) = 0.5, P(A->B) = 0.5, P(stay B) = 0.0
        # Q = [[0.5, 0.5], [0, 0]]
        # I - Q = [[0.5, -0.5], [0, 1]]
        # N = inv(I-Q) = [[2, 1], [0, 1]]
        Q = np.array([[0.5, 0.5], [0.0, 0.0]])
        N = compute_fundamental_matrix(Q)
        expected = np.array([[2.0, 1.0], [0.0, 1.0]])
        np.testing.assert_allclose(N, expected, atol=1e-10)

    def test_expected_visits_positive(self):
        # N diagonal entries (expected visits to each state) must be >= 1
        Q = np.array([[0.3, 0.2], [0.1, 0.4]])
        N = compute_fundamental_matrix(Q)
        assert all(N[i, i] >= 1.0 for i in range(2)), \
            f"Diagonal entries should be >= 1: {np.diag(N)}"

    def test_returns_numpy_array(self):
        Q = np.array([[0.2, 0.1], [0.0, 0.3]])
        N = compute_fundamental_matrix(Q)
        assert isinstance(N, np.ndarray)
        assert N.shape == (2, 2)


# ---------------------------------------------------------------------------
# run_sanity_checks (with synthetic data)
# ---------------------------------------------------------------------------

def _make_p_matrices_all_pass():
    """Craft P matrices and fundamental results that satisfy all 7 checks."""
    n = len(STATES)
    jar_idx = STATES.index("JAR_INSPECT")
    jar_find_idx = STATES.index("JAR_FIND")
    build_idx = STATES.index("BUILD")
    explore_idx = STATES.index("EXPLORE")

    # variant-a: JAR_INSPECT self-loop = 0.6 (> 0.2 -> Check 2 PASS)
    va_p = np.zeros((n, n))
    va_p[jar_idx, jar_idx] = 0.6
    va_p[jar_idx, jar_find_idx] = 0.4
    va_p[jar_find_idx, jar_idx] = 1.0
    va_p[build_idx, build_idx] = 1.0  # absorbing for test
    # Fill remaining rows so they sum to 1
    for i in range(n):
        if va_p[i].sum() == 0:
            va_p[i, build_idx] = 1.0

    # variant-c: JAR loop much lower
    vc_p = np.zeros((n, n))
    vc_p[jar_idx, jar_idx] = 0.1
    vc_p[jar_idx, build_idx] = 0.9
    vc_p[jar_find_idx, build_idx] = 1.0
    vc_p[build_idx, build_idx] = 1.0
    for i in range(n):
        if vc_p[i].sum() == 0:
            vc_p[i, build_idx] = 1.0

    # variant-b: same as variant-c but with slightly different BUILD transitions
    vb_p = vc_p.copy()

    p_matrices = {"variant-a": va_p, "variant-b": vb_p, "variant-c": vc_p}

    # fundamental results: variant-a expected_steps > variant-c (Check 3 PASS)
    fundamental_results = {
        "variant-a": {"expected_steps": 40.0, "p_success": 0.8},
        "variant-b": {"expected_steps": 30.0, "p_success": 0.85},
        "variant-c": {"expected_steps": 20.0, "p_success": 0.9},
    }

    # thrash results: JAR states in top SCC for variant-a (Check 4 PASS)
    thrash_results = {
        "variant-a": [{"scc_states": ["JAR_INSPECT", "JAR_FIND"], "thrash_score": 0.9}],
        "claude-haiku-sae": [{"scc_states": ["BUILD", "FIX_TEST"], "thrash_score": 0.95}],
    }

    # R^2 > 0.3 (Check 6 PASS)
    r2_jar = 0.5

    # Intervention delta: variant-c - variant-b should have
    # ΔP(BUILD->BUILD) > 0 and ΔP(BUILD->EXPLORE) < 0 (Check 7 PASS)
    vc_int = vc_p.copy()
    vb_int = vb_p.copy()
    # Make variant-c have higher BUILD->BUILD and lower BUILD->EXPLORE than variant-b
    vc_int[build_idx, build_idx] = 0.7
    vc_int[build_idx, explore_idx] = 0.1
    vc_int[build_idx, jar_idx] = 0.2
    vb_int[build_idx, build_idx] = 0.4
    vb_int[build_idx, explore_idx] = 0.4
    vb_int[build_idx, jar_idx] = 0.2
    intervention_p_matrices = {"variant-b": vb_int, "variant-c": vc_int}

    return p_matrices, fundamental_results, thrash_results, r2_jar, intervention_p_matrices


class TestRunSanityChecks:
    def test_all_pass_scenario(self, tmp_path):
        p_matrices, fundamental_results, thrash_results, r2_jar, intervention_p_matrices = \
            _make_p_matrices_all_pass()
        output = tmp_path / "verification-report.md"
        checks = run_sanity_checks(
            p_matrices, fundamental_results, thrash_results,
            r2_jar, intervention_p_matrices, output,
        )
        fails = [c for c in checks if c["result"] in ("FAIL", "FAIL_HYP")]
        assert fails == [], f"Expected all PASS, got: {[(c['id'], c['result']) for c in fails]}"

    def test_report_written(self, tmp_path):
        p_matrices, fundamental_results, thrash_results, r2_jar, intervention_p_matrices = \
            _make_p_matrices_all_pass()
        output = tmp_path / "verification-report.md"
        run_sanity_checks(
            p_matrices, fundamental_results, thrash_results,
            r2_jar, intervention_p_matrices, output,
        )
        assert output.exists()
        content = output.read_text()
        assert "Markov Analysis Verification Report" in content

    def test_fail_hyp_distinguished_from_fail(self, tmp_path):
        p_matrices, fundamental_results, thrash_results, r2_jar, intervention_p_matrices = \
            _make_p_matrices_all_pass()
        # Force Check 3 to fail: variant-a steps < variant-c
        fundamental_results["variant-a"]["expected_steps"] = 10.0
        fundamental_results["variant-c"]["expected_steps"] = 40.0
        # Force Check 6 to fail: R^2 below threshold
        r2_jar = 0.01
        output = tmp_path / "verification-report.md"
        checks = run_sanity_checks(
            p_matrices, fundamental_results, thrash_results,
            r2_jar, intervention_p_matrices, output,
        )
        results_by_id = {c["id"]: c["result"] for c in checks}
        # Check 3 and 6 are hypothesis failures, not implementation bugs
        assert results_by_id[3] == "FAIL_HYP"
        assert results_by_id[6] == "FAIL_HYP"
        # Check 1 should still pass (row sums are correct)
        assert results_by_id[1] == "PASS"

    def test_summary_counts_in_report(self, tmp_path):
        p_matrices, fundamental_results, thrash_results, r2_jar, intervention_p_matrices = \
            _make_p_matrices_all_pass()
        r2_jar = 0.01  # force FAIL_HYP on Check 6
        output = tmp_path / "verification-report.md"
        run_sanity_checks(
            p_matrices, fundamental_results, thrash_results,
            r2_jar, intervention_p_matrices, output,
        )
        content = output.read_text()
        assert "FAIL_HYP" in content

    def test_check1_fails_on_bad_row_sums(self, tmp_path):
        p_matrices, fundamental_results, thrash_results, r2_jar, intervention_p_matrices = \
            _make_p_matrices_all_pass()
        # Corrupt variant-a: make a row sum to 1.5 (implementation bug)
        bad_p = p_matrices["variant-a"].copy()
        bad_p[0, 0] = 1.5
        p_matrices["variant-a"] = bad_p
        output = tmp_path / "verification-report.md"
        checks = run_sanity_checks(
            p_matrices, fundamental_results, thrash_results,
            r2_jar, intervention_p_matrices, output,
        )
        check1 = next(c for c in checks if c["id"] == 1)
        assert check1["result"] == "FAIL"

    def test_check7_correct_transitions(self, tmp_path):
        p_matrices, fundamental_results, thrash_results, r2_jar, intervention_p_matrices = \
            _make_p_matrices_all_pass()
        # Reverse the BUILD deltas so Check 7 fails
        build_idx = STATES.index("BUILD")
        explore_idx = STATES.index("EXPLORE")
        # variant-c BUILD->BUILD < variant-b BUILD->BUILD
        intervention_p_matrices["variant-c"][build_idx, build_idx] = 0.1
        intervention_p_matrices["variant-b"][build_idx, build_idx] = 0.7
        output = tmp_path / "verification-report.md"
        checks = run_sanity_checks(
            p_matrices, fundamental_results, thrash_results,
            r2_jar, intervention_p_matrices, output,
        )
        check7 = next(c for c in checks if c["id"] == 7)
        assert check7["result"] == "FAIL"
