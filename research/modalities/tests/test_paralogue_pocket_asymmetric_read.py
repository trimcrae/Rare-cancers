"""Pure-function tests for IC-4-A — the split (mandatory / best-effort) re-read of the paralogue contrast.

No fpocket, no MD, no network. Every statistic in `paralogue_pocket_asymmetric_read` is an exact
enumeration, so each one has a hand-checkable answer and that is what these pin.

★ THE TWO TESTS THAT MATTER MOST ARE THE ONES THAT CAN KILL THE FINDING:
  * `test_the_exact_test_cannot_beat_its_own_floor_at_3_vs_3` — the design ceiling. If this ever passes
    with a p below 0.05 the enumeration is wrong, and every "separated" statement built on it is wrong too.
  * `test_the_rule_is_the_source_artifacts_rule_with_the_conjunction_removed_and_nothing_else` — the whole
    intervention is deleting one `and`. A test that lets the rule drift would turn a re-read into a
    re-tune, which is the outcome-selection defect the harmonized rerun exists to remove.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import paralogue_pocket_asymmetric_read as A  # noqa: E402
import paralogue_pocket_contrast as PPC       # noqa: E402

MOD = os.path.abspath(os.path.join(HERE, ".."))

# The committed replicate fractions, as they stand in paralogue-pocket-contrast.json ->
# contrast.<sp>.replicate_spread.per_replicate_frac_ge_dstar. Written here ONLY so the pure functions have
# a fixture; the artifact remains their one home and `test_the_fixture_still_matches_the_committed_artifact`
# fails the build if these ever drift from it.
NR4A3 = [0.56, 0.4, 0.8]
NR4A1 = [0.28, 0.32, 0.12]
NR4A2 = [0.44, 0.24, 0.16]


# ---------------------------------------------------------------------------------------------------------
# the exact statistics
# ---------------------------------------------------------------------------------------------------------
def test_midranks_average_ties():
    assert A.midranks([1.0, 2.0, 2.0, 5.0]) == [1.0, 2.5, 2.5, 4.0]


def test_the_exact_test_cannot_beat_its_own_floor_at_3_vs_3():
    """C(6,3) = 20, so the smallest attainable one-sided p is 1/20 = 0.05 — for ANY data."""
    r = A.exact_ranksum([9.0, 9.1, 9.2], [0.0, 0.1, 0.2])
    assert r["n_permutations"] == 20
    assert r["p_one_sided_floor"] == 0.05
    assert r["p_one_sided_a_greater"] == 0.05
    assert r["achieved_the_design_floor"] is True
    assert r["p_two_sided"] == 0.1


def test_complete_separation_is_exactly_what_hits_the_floor():
    assert A.exact_ranksum(NR4A3, NR4A1)["achieved_the_design_floor"] is True
    # NR4A2's best (0.44) beats NR4A3's worst (0.40), so one pair inverts and the floor is missed.
    assert A.exact_ranksum(NR4A3, NR4A2)["achieved_the_design_floor"] is False
    assert A.exact_ranksum(NR4A3, NR4A2)["p_one_sided_a_greater"] == 0.1


def test_a_tie_at_the_boundary_does_not_count_as_separation():
    """The contested-`C2` case: NR4A3's worst equals NR4A1's best. `>` is strict, so this is NOT separated —
    and the rank test must not report the floor either."""
    a, b = [0.6, 0.44, 0.8], [0.44, 0.36, 0.12]
    assert min(a) > max(b) is False or min(a) == max(b)
    assert A.exact_ranksum(a, b)["achieved_the_design_floor"] is False


def test_cliffs_delta_is_1_exactly_when_every_pair_favours_a():
    assert A.cliffs_delta(NR4A3, NR4A1)["delta"] == 1.0
    assert A.cliffs_delta(NR4A3, NR4A2)["n_a_lt_b"] == 1


def test_design_effect_is_measured_against_the_binomial_variance():
    d = A.design_effect(NR4A3, 25)
    assert d["binomial_variance_if_frames_independent"] > 0
    # 3 replicas spread far wider than independent frames would → deff > 1 → effective n well below 75.
    assert d["design_effect"] > 1.0
    assert d["effective_n"] < 75
    lo_u, hi_u = d["wilson95_uncorrected"]
    lo_c, hi_c = d["wilson95_design_corrected"]
    assert lo_c < lo_u and hi_c > hi_u, "correcting for clustering must WIDEN, never narrow"


def test_design_effect_correction_never_narrows_below_the_binomial_interval():
    """deff < 1 is a real reading; using it would produce an interval narrower than the anti-conservative
    one, which is the wrong direction. It must be floored at 1.0 for the correction."""
    d = A.design_effect([0.50, 0.50, 0.52], 25)
    assert d["design_effect"] < 1.0
    assert d["design_effect_used_for_correction"] == 1.0


def test_cluster_bootstrap_is_exhaustive_and_therefore_seedless():
    b1 = A.cluster_bootstrap_difference(NR4A3, NR4A1)
    b2 = A.cluster_bootstrap_difference(NR4A3, NR4A1)
    assert b1 == b2
    assert b1["n_distinct_per_arm"] == 27 and b1["n_resamples"] == 729


def test_t2_cdf_is_the_closed_form_and_reproduces_the_known_quantile():
    assert abs(A.t2_cdf(0.0) - 0.5) < 1e-12
    assert abs(A.t2_cdf(4.302652729911275) - 0.975) < 1e-10


def test_holm_cannot_clear_0_05_when_the_per_test_floor_is_0_05():
    adj = A.holm([("NR4A1", 0.05), ("NR4A2", 0.10)])
    assert adj["NR4A1"] == 0.1
    assert min(adj.values()) >= 0.1


def test_intervals_overlap_reports_the_gap_and_the_width():
    assert A.intervals_overlap([0.0, 0.4], [0.5, 0.9])["overlap"] is False
    assert A.intervals_overlap([0.0, 0.6], [0.5, 0.9])["overlap_width"] == 0.1


# ---------------------------------------------------------------------------------------------------------
# the rule — this is the whole intervention and it must not drift
# ---------------------------------------------------------------------------------------------------------
def test_the_rule_is_the_source_artifacts_rule_with_the_conjunction_removed_and_nothing_else():
    """`pairwise_verdict` must agree with `paralogue_pocket_contrast`'s `sep` whenever the conjunction is
    evaluated over a single paralogue. Checked against the source module's live source text, so a change
    to the frozen rule breaks this build rather than silently re-scoping the finding."""
    src = open(os.path.join(MOD, "paralogue_pocket_contrast.py")).read()
    assert "sep = all(v is not None for v in (r3[0], r1[1], r2[1])) and r3[0] > r1[1] and r3[0] > r2[1]" \
        in src, "the source rule moved — re-derive the split before trusting this artifact"
    v = A.pairwise_verdict(NR4A3, NR4A1, 0.5867, 0.24)
    assert v["separated"] is (min(NR4A3) > max(NR4A1)) is True
    assert v["verdict"] == "SEPARATED at replicate granularity"
    v2 = A.pairwise_verdict(NR4A3, NR4A2, 0.5867, 0.28)
    assert v2["separated"] is False and v2["ranked"] is True
    assert v2["verdict"] == "RANKED but replicate ranges OVERLAP"


def test_a_paralogue_that_out_ranks_nr4a3_is_reported_as_not_ranked():
    v = A.pairwise_verdict([0.1, 0.2, 0.3], [0.7, 0.8, 0.9], 0.2, 0.8)
    assert v["verdict"] == "NOT RANKED in NR4A3's favour"


# ---------------------------------------------------------------------------------------------------------
# provenance — the fixture, and the promise that nothing is re-run or overwritten
# ---------------------------------------------------------------------------------------------------------
def test_the_fixture_still_matches_the_committed_artifact():
    path = os.path.join(MOD, "paralogue-pocket-contrast.json")
    if not os.path.exists(path):
        return
    c = json.load(open(path))
    for sp, want in (("NR4A3", NR4A3), ("NR4A1", NR4A1), ("NR4A2", NR4A2)):
        assert c["contrast"][sp]["replicate_spread"]["per_replicate_frac_ge_dstar"] == want


def test_the_module_reads_the_source_artifact_and_never_writes_it():
    src = open(os.path.join(MOD, "paralogue_pocket_asymmetric_read.py")).read()
    assert A.OUT != PPC.OUT
    assert "paralogue-pocket-asymmetric-read.json" in A.OUT
    # the only open-for-write in the module is its own output
    assert src.count('open(args.out, "w")') == 1
    assert 'open(CONTRAST, "w")' not in src and 'open(ACCEPTED, "w")' not in src


def test_it_runs_no_compute_no_fpocket_and_names_no_gpu_path():
    """Checked against the module's IMPORTS and CALLS, not its prose — the docstrings discuss fpocket and
    GPUs at length and a substring scan would fire on the explanation rather than on any behaviour."""
    import ast
    tree = ast.parse(open(os.path.join(MOD, "paralogue_pocket_asymmetric_read.py")).read())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    for forbidden in ("subprocess", "shutil", "requests", "urllib", "boto3", "socket",
                      "paralogue_pocket_contrast", "pocket_tracking"):
        assert forbidden not in imported, f"{forbidden} has no business in a $0 artifact re-read"
    assert imported <= {"__future__", "argparse", "itertools", "json", "math", "os", "sys", "map_edits"}
