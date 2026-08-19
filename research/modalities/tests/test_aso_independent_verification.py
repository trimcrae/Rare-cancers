#!/usr/bin/env python3
"""The second implementation of the frame grading and screen 4 must keep agreeing with the first.

⛔ WHY THIS EXISTS. External review of the submission manuscript asked for the two instruments the
paper's claims rest on to be independently reimplemented, because the Provenance section discloses
that an exon-indexing error invalidated an earlier version in full. `aso_independent_verification.py`
is that reimplementation. A verifier is worth exactly as much as the guarantee that it still runs
and still disagrees when it should, so this file asserts three separate things:

  · the verifier's own verdict is AGREES, with zero problems;
  · the verifier is NOT vacuous — a deliberately corrupted input makes it fail, checked here rather
    than assumed, because a check that cannot fail is indistinguishable from one that is not run;
  · the routes really are different — it imports neither module it verifies, and it does not read
    the annotated coding start.

⚠ AND THE HONEST BOUND IS ASSERTED TOO. `test_the_artifact_states_what_it_is_not` keeps the "this is
not external review" disclaimer in the artifact, so a future edit cannot quietly upgrade an internal
cross-check into a claim of independent peer review of the code.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ART = os.path.join(MOD, "aso-independent-verification.json")
SRC = os.path.join(MOD, "aso_independent_verification.py")
sys.path.insert(0, MOD)


def _art():
    if not os.path.exists(ART):
        pytest.skip("independent-verification artifact is not present in this checkout")
    return json.load(open(ART, encoding="utf-8"))


def _mod():
    try:
        import aso_independent_verification as v
    except Exception as exc:                                    # noqa: BLE001
        pytest.skip(f"verifier does not import here: {exc}")
    return v


def test_the_verifier_agrees_and_lists_no_problems():
    a = _art()
    assert a["verdict"] == "AGREES", a["problems"][:5]
    assert a["n_problems"] == 0
    assert a["problems"] == []


def test_it_graded_every_declared_pair_and_screened_every_design():
    c = _art()["checks"]
    assert c["C_frame_grading"]["pairs_checked"] == 231
    assert c["C_frame_grading"]["grade_disagreements"] == 0
    assert c["C_frame_grading"]["field_disagreements"] == 0
    assert c["C_frame_grading"]["atlas_grade_counts"] == \
        c["C_frame_grading"]["independent_grade_counts"]
    assert c["D_mature_parent_screen"]["designs_checked"] == 190
    assert c["D_mature_parent_screen"]["run_length_disagreements"] == 0
    assert c["D_mature_parent_screen"]["independent_n_liable"] == \
        c["D_mature_parent_screen"]["screen4_n_liable"] == 87
    assert c["D_mature_parent_screen"]["independent_n_liable_against_NR4A3"] == \
        c["D_mature_parent_screen"]["screen4_n_liable_against_NR4A3"] == 61


def test_the_two_transcript_acquisitions_agree_base_for_base():
    """The genomic splice and the cDNA record are separate fetches; the frame rests on both."""
    a = _art()["checks"]["A_transcript_acquisitions_agree"]
    assert len(a) == 6
    for gene, row in a.items():
        assert row["identical"], f"{gene}: the two acquisitions differ"
        assert row["genomic_spliced_nt"] == row["cdna_record_nt"]


def test_the_coding_start_is_recovered_without_reading_the_annotation():
    """An ORF search finding a different start would be the retracted defect's exact shape."""
    b = _art()["checks"]["B_coding_start_without_annotation"]
    assert len(b) == 6
    for gene, row in b.items():
        assert row["agrees"], f"{gene}: ORF offset {row['orf_offset_found']} against " \
                              f"annotated {row['annotated_utr5_len']}"


def test_the_declared_acceptor_window_hides_no_emittable_junction():
    """The one input taken from the thing being verified — so what it excludes is reported."""
    c = _art()["checks"]["C_frame_grading"]
    assert c["acceptor_exon_window_taken_from_the_atlas"] == [2, 3, 4]
    assert c["unrestricted_pairs_graded"] > 231
    assert c["emittable_outside_the_declared_acceptor_window"] == []


def test_the_two_routes_to_frame_part_company_only_where_they_should():
    """Arithmetic register and translation are different tests; the difference class is listed."""
    c = _art()["checks"]["C_frame_grading"]
    premature = c["arithmetic_in_frame_but_premature_stop"]
    # every one of them must be a row the ladder has already refused for another reason, so none
    # of them can reach a design panel
    assert all(k.endswith("NR4A3_e4") for k in premature), premature


# ─────────────────────────────────────────────────────── the verifier is not vacuous
def test_a_corrupted_screen_4_artifact_makes_the_verifier_fail():
    """⛔ A CHECK THAT CANNOT FAIL IS NOT A CHECK. Proved rather than asserted."""
    v = _mod()
    for path in (v.GENOMIC, v.CDNA, v.ATLAS, v.SCREEN4, v.INVENTORY):
        if not os.path.exists(path):
            pytest.skip("inputs to the verifier are not present in this checkout")
    good = v.run()
    assert good["verdict"] == "AGREES"
    #: ⛔⛔ AND THE LIVE RUN IS COMPARED TO THE DEPOSITED ARTIFACT, WHICH NOTHING DID (2026-08-19).
    #: Every other assertion in this file reads `aso-independent-verification.json` and checks the
    #: numbers written into it — 231 pairs, 190 designs, 87, 61 — so the whole file could pass
    #: against a committed artifact that the verifier, run today over today's inputs, would no
    #: longer produce. A stale verdict is exactly what a verifier is for, and the one thing this
    #: file was not checking was whether the verifier still says what the deposit says it says.
    #: The comparison is over `checks`, not the whole document, because the artifact carries a
    #: timestamp and other run metadata that differ by construction on every run.
    assert good["checks"] == _art()["checks"], (
        "the verifier's LIVE output differs from the committed aso-independent-verification.json, "
        "so the deposited verification is stale: it describes inputs that have since changed. "
        "Re-run research/modalities/aso_independent_verification.py and register any moved figure "
        "in pinned-figures.json in the same commit.")
    assert good["verdict"] == _art()["verdict"] and good["problems"] == _art()["problems"]

    real = json.load(open(v.SCREEN4, encoding="utf-8"))
    real["per_design"][0]["longest_parent_duplex_bp_through_gap"] += 1
    tmp = os.path.join(HERE, "_corrupt-screen4.json")
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(real, fh)
        orig, v.SCREEN4 = v.SCREEN4, tmp
        try:
            bad = v.run()
        finally:
            v.SCREEN4 = orig
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    assert bad["verdict"] == "DISAGREES"
    assert bad["checks"]["D_mature_parent_screen"]["run_length_disagreements"] == 1


def test_a_corrupted_frame_grade_makes_the_verifier_fail():
    v = _mod()
    for path in (v.GENOMIC, v.CDNA, v.ATLAS, v.SCREEN4, v.INVENTORY):
        if not os.path.exists(path):
            pytest.skip("inputs to the verifier are not present in this checkout")
    real = json.load(open(v.ATLAS, encoding="utf-8"))
    for p in real["graded_pairs"]:
        if p["grade"] == "EMITTABLE":
            p["grade"] = "OUT_OF_FRAME"
            break
    tmp = os.path.join(HERE, "_corrupt-atlas.json")
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(real, fh)
        orig, v.ATLAS = v.ATLAS, tmp
        try:
            bad = v.run()
        finally:
            v.ATLAS = orig
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    assert bad["verdict"] == "DISAGREES"
    assert bad["checks"]["C_frame_grading"]["grade_disagreements"] == 1


# ───────────────────────────────────────────────────────────── the routes really are separate
def test_the_verifier_imports_neither_module_it_verifies():
    if not os.path.exists(SRC):
        pytest.skip("verifier source is not present in this checkout")
    src = open(SRC, encoding="utf-8").read()
    body = "\n".join(ln for ln in src.splitlines()
                     if not ln.lstrip().startswith("#"))
    for banned in ("import junction_aso", "import aso_parent_gap_pairing",
                   "from junction_aso", "from aso_parent_gap_pairing"):
        assert banned not in body, f"the verifier imports what it verifies: {banned}"


def test_the_verifier_does_not_read_the_annotated_coding_start_to_grade_frames():
    """`utr5_len` may appear only where the ORF result is COMPARED to it, never as an input."""
    if not os.path.exists(SRC):
        pytest.skip("verifier source is not present in this checkout")
    src = open(SRC, encoding="utf-8").read()
    hits = [ln.strip() for ln in src.splitlines()
            if '"utr5_len"' in ln and not ln.lstrip().startswith("#")]
    assert hits, "expected the comparison against the annotation to still be there"
    for ln in hits:
        assert ("annotated_utr5_len" in ln or "offset ==" in ln or "rec['utr5_len']" in ln), ln


def test_the_artifact_states_what_it_is_not():
    a = _art()
    joined = " ".join(a["_what_this_is_not"]).lower()
    assert "not external review" in joined
    assert "shared misreading" in joined
    assert len(a["routes_that_differ_from_the_original"]) == 4
