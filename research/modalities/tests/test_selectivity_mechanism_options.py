"""THE SELECTIVITY-MECHANISM OPTIONS REGISTER — pinned on the things that would silently rot it.

WHY THESE ASSERTIONS AND NOT OTHERS. This artifact is an options register, so its failure mode is not a
wrong number — it is a grade that drifts loose from the evidence under it. Three things must therefore hold
mechanically, because prose discipline is exactly what has failed in this repo before:

  1. EVERY MECHANISM CARRIES ITS OWN REFUTABILITY FIELDS. A row without `positive_control_possible` or
     without `a_pass_does_not_license` is a recommendation wearing the costume of an analysis. The whole
     point of the register is that the second field is as long as the first.

  2. A MEASURED CLAIM MUST NOT OUTRANK ITS INSTRUMENT. Grade A is reserved for a mechanism whose claim is
     defensible today; the register's own rule is that leverage never raises a grade. `S10`
     (cooperativity) has the highest leverage measured anywhere in the file — 7.9x DC50 separation at zero
     binary margin — and its instrument returned the WRONG SIGN, so it must stay at D. If a future edit
     promotes it, that is the exact failure this test exists to catch.

  3. THE SIGNAL/NULL CONTRAST IN M3 IS THE FILE'S ONLY NEW POSITIVE RESULT, AND IT IS ONLY MEANINGFUL
     AGAINST ITS NULL. The null must be non-zero (a null of exactly zero would mean the test cannot produce
     a false positive, which is not credible for a rigid superposition) and the signal must exceed it. A
     future change that drops the conserved/shared control class would leave a bare 0.923 with nothing to
     grade it against — which is the shape of every result this program has had to withdraw.

Stdlib + pytest only. Reads the COMMITTED artifact; it does not re-run the ~2 min superposition.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

ARTIFACT = os.path.join(MOD, "selectivity-mechanism-options.json")


@pytest.fixture(scope="module")
def doc():
    if not os.path.exists(ARTIFACT):
        pytest.skip("selectivity-mechanism-options.json not built in this checkout")
    with open(ARTIFACT) as f:
        return json.load(f)


REQUIRED = ("id", "name", "status", "novelty", "physical_basis", "instrument",
            "known_answer_test_in_the_needed_regime", "positive_control_possible",
            "cheapest_decisive_test", "a_pass_licenses", "a_pass_does_not_license",
            "grade", "why_this_grade",
            "known_answer_short", "positive_control_short", "cheapest_test_short")


def test_every_mechanism_carries_its_refutability_fields(doc):
    for m in doc["mechanisms"]:
        for k in REQUIRED:
            assert k in m and m[k] not in (None, "", []), f"{m.get('id')} missing {k}"
        assert m["a_pass_does_not_license"], f"{m['id']} claims a licence with no limit"


def test_ids_are_unique_and_grades_are_on_the_declared_scale(doc):
    ids = [m["id"] for m in doc["mechanisms"]]
    assert len(ids) == len(set(ids))
    for m in doc["mechanisms"]:
        assert m["grade"][0] in doc["_grade_key"], f"{m['id']} grade {m['grade']} off-scale"
        assert m["grade"][1:] in ("", "+", "-")


def test_leverage_never_raises_a_grade(doc):
    """S10 has the file's largest measured leverage and a REFUTED instrument. It stays blocked."""
    s10 = next(m for m in doc["mechanisms"] if m["id"] == "S10")
    assert s10["grade"].startswith("D"), (
        "cooperativity was promoted above D. Its known-answer test returned the wrong sign in all three "
        "replicates at ~34x its uncertainty; a large prize is not evidence.")
    s2 = next(m for m in doc["mechanisms"] if m["id"] == "S2")
    assert s2["grade"].startswith("D"), "Route A's free-energy form requires an instrument that has no pass"


def test_only_the_incumbent_may_hold_an_A(doc):
    a_rows = [m["id"] for m in doc["mechanisms"] if m["grade"].startswith("A")]
    assert a_rows == ["S1"], (
        f"grade A is reserved for a mechanism whose claim is defensible today; got {a_rows}. "
        "Nothing new in this file has an instrument validated in the paralogue-scale regime.")


def test_m3_signal_is_graded_against_a_live_null(doc):
    g = doc["measurements"]["M3"]["by_position_class"]
    assert set(g) == {"unique_and_both_bulkier", "unique_not_bulkier", "conserved_or_shared"}
    null = g["conserved_or_shared"]["rate"]
    signal = g["unique_and_both_bulkier"]["rate"]
    assert null > 0.0, (
        "the conserved/shared null went to zero. A rigid-superposition clash test that cannot produce a "
        "false positive is not credible — check that the control positions are still in the set.")
    assert signal > null, "the steric signal no longer exceeds its own null"
    assert doc["measurements"]["M3"]["enrichment_signal_over_null"] == pytest.approx(signal / null, rel=0.02)


def test_m1_reports_a_replicate_SD_not_a_frame_SE(doc):
    """The honest error bar on 3 independent replicas is the replicate-SD. A per-frame SD over 75 frames
    would be ~4x smaller and would turn a null into a 'result' — which is the error this field prevents."""
    c = doc["measurements"]["M1"]["contrasts"]["NR4A3_minus_NR4A1"]
    assert "delta_replicate_SD" in c and c["delta_replicate_SD"] > 0
    assert abs(c["delta_over_replicate_SD"]) < 2.0, (
        "the NR4A3-vs-NR4A1 lysine-coverage gap has become resolvable. That would REVERSE this file's "
        "S7 finding, so it must be re-graded deliberately rather than by a silent artifact refresh.")


def test_m4_control_is_present_and_is_not_read_as_a_score(doc):
    m4 = doc["measurements"]["M4"]
    assert "⛔_the_scores_are_NOT_evidence" in m4, (
        "the per-species docking dG values must ship with the refusal to read them as a selectivity margin "
        "— single-snapshot scoring as a selectivity verdict is in the closed-route register as REFUTED.")
    for sp in ("NR4A1", "NR4A2"):
        assert m4["median_centroid_shift_A"][sp] > 0


def test_the_scope_disclaimers_survive(doc):
    blob = " ".join(doc["_scope"]).lower()
    for word in ("efficacy", "safety", "therapeutic window", "proteome-wide"):
        assert word in blob, f"the scope block no longer disclaims {word!r}"


def test_new_mechanisms_are_actually_marked_new(doc):
    new = [m["id"] for m in doc["mechanisms"] if m["novelty"].startswith("NEW")]
    assert doc["counts"]["n_new"] == len(new)
    assert "S3" in new and "S15" in new, "the two highest-graded new mechanisms lost their NEW marker"


def test_grade_sort_puts_plus_before_bare_before_minus():
    import selectivity_mechanism_options as SMO
    rows = [{"grade": g, "id": g} for g in ("B-", "A-", "B+", "B", "C+", "D")]
    assert [r["id"] for r in sorted(rows, key=SMO._grade_sort)] == ["A-", "B+", "B", "B-", "C+", "D"]
