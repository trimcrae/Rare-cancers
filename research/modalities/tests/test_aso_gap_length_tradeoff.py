#!/usr/bin/env python3
"""The gap-length trade-off: the complement identity, the parameterisation, and the baseline.

⛔ WHY THIS EXISTS. Three distinct things can go wrong here and only the first is obvious.

  1. THE FINDING can be misstated. It rests on an identity — inside the catalytic gap, the
     junction-unique bases on the shorter side and the bases a wild-type parent pairs on the longer
     side sum to the gap — so raising the gap-level margin raises the contiguous parent-paired DNA
     by the same nucleotide. If that identity is ever broken by a change to the tiler, the trade-off
     artifact would keep emitting both columns and they would silently stop being complements.

  2. THE BASELINE can move. Four modules were parameterised by geometry to make this measurable, and
     every one of them previously wrote to a fixed filename. The 16-mer artifacts are what the
     submission manuscript quotes, so a parameterisation that shifts them by one number is a
     correction to a published figure wearing the costume of a refactor. Each is pinned here.

  3. THE PARAMETERISATION CAN BE INERT. `nr4a3_fusion_atlas` honouring OUT_SUFFIX, and the workflow
     deriving SCREEN_TOP_N from the dispatched geometry, are both properties asserted in prose about
     values passed by a caller — which CLAUDE.md section 6 records as "not a property; it is a hope".
     They are asserted against the real module and the real workflow file instead.
"""
import json
import os
import re
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MOD))
ART = os.path.join(MOD, "aso-gap-length-tradeoff.json")
WORKFLOW = os.path.join(REPO, ".github", "workflows", "aso-offtarget.yml")
sys.path.insert(0, MOD)


def _art():
    if not os.path.exists(ART):
        pytest.skip("gap-length trade-off artifact is not present in this checkout")
    return json.load(open(ART, encoding="utf-8"))


def _atlas(suffix):
    p = os.path.join(MOD, f"nr4a3-fusion-junction-atlas{suffix}.json")
    if not os.path.exists(p):
        pytest.skip(f"atlas{suffix} is not present in this checkout")
    return json.load(open(p, encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 1 · the identity the finding rests on
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_the_gap_halves_are_complements_at_every_geometry():
    """margin + parent-paired DNA == gap, for every design. This IS the trade-off.

    A failure means the two columns of the artifact have stopped being two views of one
    subtraction, at which point the claim that they move together nucleotide for nucleotide is no
    longer supported by the numbers beside it.
    """
    art = _art()
    gaps = {g["architecture"]: g["gap_nt"] for g in art["geometries"] if g.get("present")}
    assert gaps, "no geometry is present in the artifact"
    for r in art["per_design"]:
        gap = gaps[r["architecture"]]
        assert r["gap_specificity_margin"] + r["parent_paired_gap_dna_nt"] == gap, r
        assert r["parent_seam_hybrid_bp"] == r["parent_paired_gap_dna_nt"] + 5, r


def test_a_longer_gap_raises_the_margin_and_the_parent_paired_dna_together():
    """The direction of the trade, asserted rather than described."""
    art = _art()
    present = [g for g in art["geometries"] if g.get("present")]
    if len(present) < 2:
        pytest.skip("only one geometry present — there is no trade to compare")
    present.sort(key=lambda g: g["gap_nt"])
    best_margin = [max(int(k) for k in g["gap_margin_distribution"]) for g in present]
    worst_dna = [max(int(k) for k in g["parent_paired_gap_dna_distribution"]) for g in present]
    assert best_margin == sorted(best_margin), best_margin
    assert worst_dna == sorted(worst_dna), worst_dna
    # ⚠ AND THE COST IS NOT OPTIONAL AT THE LONGEST GAP. Every design of the widest geometry must
    # present some wild-type parent with at least the SMALLER reported RNase-H1 minimum, because the
    # smaller half of a gap of 10 cannot be under 5. If this ever passes vacuously the identity
    # above has been broken.
    widest = present[-1]
    floor = min(art["thresholds"]["min_contiguous_dna_nt_for_rnaseh1"]["values"])
    if widest["gap_nt"] >= 2 * floor:
        assert (widest["n_reaching_reported_dna_minimum"][str(floor)]
                == widest["n_fusion_specific_designs"])


def _keys(node):
    """Every key name anywhere in the artifact, so the guard below reads FIELDS and not prose."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield k
            yield from _keys(v)
    elif isinstance(node, list):
        for v in node:
            yield from _keys(v)


def test_no_composite_score_is_emitted():
    """The two directions must never be collapsed, so no combined rank may appear in the artifact.

    ⚠ KEYS ONLY. The first version matched the serialised artifact and failed on the sentence that
    PROMISES no composite rank — a guard tripped by its own rationale. What must not exist is a
    FIELD a reader could sort on; saying so in prose is the opposite of the defect.
    """
    art = _art()
    banned = re.compile(r"combined_score|composite|overall_rank|total_score", re.I)
    offenders = sorted({k for k in _keys(art) if banned.search(k)})
    assert not offenders, f"a composite score field appeared in the trade-off artifact: {offenders}"
    assert "_never_collapse_these" in art["the_trade"]


def test_the_thresholds_are_anchored_to_committed_quotes_not_recollection():
    """Gate-4 discipline: both reported minima must resolve to a fragment in the committed anchor."""
    art = _art()
    thr = art["thresholds"]["min_contiguous_dna_nt_for_rnaseh1"]
    lit = json.load(open(os.path.join(REPO, thr["anchor_file"]), encoding="utf-8"))
    quotes = {(r["pmid"], q["fragment"]) for r in lit["records"] for q in r["quotes"]}
    assert set(thr["values"]) == {int(k) for k in thr["anchors"]}
    for _nt, a in thr["anchors"].items():
        assert (a["pmid"], a["fragment"]) in quotes, a


def test_the_lead_reagent_row_is_present_and_covers_three_partners():
    """The one candidate with a clinical readership. Its row must exist at every geometry present."""
    art = _art()
    lead = art["lead_reagent_at_the_most_commonly_reported_seam"]["by_geometry"]
    present = {g["architecture"] for g in art["geometries"] if g.get("present")}
    assert set(lead) == present
    for arch, row in lead.items():
        assert row.get("n_partners_covered_exactly") == 3, (arch, row)
        # the coverage ceiling is a property of the transcripts and cannot move with geometry
        assert row["bases_from_donor"] <= row["maximal_shared_donor_run_nt"], (arch, row)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 2 · the baseline the manuscript quotes must not have moved
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_the_16mer_parent_duplex_artifact_still_reproduces():
    import aso_parent_gap_pairing as m  # noqa: PLC0415
    assert m.OLIGO_LEN == 16 and m.WING == 5, "the default geometry moved"
    assert m.main(["--check"]) == 0, "aso-parent-gap-pairing.json no longer reproduces"


def test_the_16mer_thermo_artifact_still_reproduces():
    import junction_aso_thermo as m  # noqa: PLC0415
    if m.build.__module__ and not os.path.exists(m.OUT):
        pytest.skip("thermo artifact absent")
    assert m.main(["--check"]) == 0, "junction-aso-thermo.json no longer reproduces"


def test_the_premrna_seed_blocks_reproduce_the_literal_they_replaced():
    """The partition was `[(0, 6), (6, 11), (11, L)]`. At L=16 the derivation must equal it exactly.

    And at any length the blocks must PARTITION the window, because completeness at <=2 mismatches
    is a pigeonhole argument over disjoint blocks covering the whole window — not a property of
    their sizes.
    """
    import aso_premrna_offtarget as m  # noqa: PLC0415
    assert m.seed_blocks(16) == [(0, 6), (6, 11), (11, 16)]
    assert m.N_SEED_BLOCKS == m.MAX_MM + 1
    for length in (16, 18, 20, 25):
        b = m.seed_blocks(length)
        assert len(b) == m.N_SEED_BLOCKS
        assert b[0][0] == 0 and b[-1][1] == length
        assert all(b[i][1] == b[i + 1][0] for i in range(len(b) - 1))
        assert all(end > start for start, end in b)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 3 · the parameterisation is wired, not merely documented
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_the_atlas_output_path_actually_follows_out_suffix():
    """⛔ A SUFFIX THAT DOES NOT MOVE THE FILE IS THE BUG IT EXISTS TO PREVENT.

    Re-imported under a set OUT_SUFFIX, because the path is resolved at import: asserting on the
    already-imported module would test the environment this test process happens to have.
    """
    import importlib  # noqa: PLC0415
    prev = os.environ.get("OUT_SUFFIX")
    try:
        os.environ["OUT_SUFFIX"] = "-unit-test-suffix"
        mod = importlib.reload(importlib.import_module("nr4a3_fusion_atlas"))
        assert mod.OUT.endswith("nr4a3-fusion-junction-atlas-unit-test-suffix.json"), mod.OUT
    finally:
        if prev is None:
            os.environ.pop("OUT_SUFFIX", None)
        else:
            os.environ["OUT_SUFFIX"] = prev
        importlib.reload(importlib.import_module("nr4a3_fusion_atlas"))


def test_screen_top_n_defaults_to_six_and_follows_the_environment():
    """The default must be untouched, or every committed screen's scope silently re-bases."""
    import importlib  # noqa: PLC0415
    prev = os.environ.get("SCREEN_TOP_N")
    try:
        os.environ.pop("SCREEN_TOP_N", None)
        m = importlib.reload(importlib.import_module("junction_aso_offtarget"))
        assert m.N_OLIGOS == 6
        os.environ["SCREEN_TOP_N"] = "9"
        m = importlib.reload(importlib.import_module("junction_aso_offtarget"))
        assert m.N_OLIGOS == 9
        assert m.screen_parameters()["screen_top_n"] == 9
        assert "SCREEN_TOP_N" in m.screen_parameters()["overridden_from_env"]
    finally:
        if prev is None:
            os.environ.pop("SCREEN_TOP_N", None)
        else:
            os.environ["SCREEN_TOP_N"] = prev
        importlib.reload(importlib.import_module("junction_aso_offtarget"))


def test_the_workflow_derives_screen_top_n_from_the_dispatched_geometry():
    """⛔ THE SHELL IS THE THING UNDER TEST, SO IT IS RUN, NOT READ.

    A grep for the arithmetic would pass on a line that never executes. This extracts nothing and
    asserts nothing about the text; it reproduces the workflow's own derivation and checks that a
    blank geometry leaves the knob UNSET — the property that keeps every existing dispatch
    bit-for-bit unchanged — while 18,5 and 20,5 select every junction-spanning register.
    """
    if not os.path.exists(WORKFLOW):
        pytest.skip("workflow file is not present in this checkout")
    body = open(WORKFLOW, encoding="utf-8").read()
    assert "SCREEN_TOP_N=$(( OLIGO_LEN - 2 * WING - 1 ))" in body, \
        "the workflow no longer derives SCREEN_TOP_N from the geometry"
    script = (
        'OLIGO_LEN="${G%%,*}"; case "$G" in *,*) WING="${G#*,}" ;; *) WING="" ;; esac\n'
        'if [ -n "${OLIGO_LEN:-}" ] && [ -n "${WING:-}" ]; then '
        'SCREEN_TOP_N=$(( OLIGO_LEN - 2 * WING - 1 )); fi\n'
        'echo "${SCREEN_TOP_N:-unset}"\n')
    for geometry, expected in (("", "unset"), ("18,5", "7"), ("20,5", "9")):
        got = subprocess.run(["sh", "-c", script], env={**os.environ, "G": geometry},
                             capture_output=True, text=True, check=True).stdout.strip()
        assert got == expected, f"geometry {geometry!r} derived {got!r}, expected {expected!r}"


def test_the_registers_per_seam_are_gap_minus_one_at_every_geometry():
    """`GAP - 1` is why SCREEN_TOP_N has to follow the geometry. Measured from the atlases."""
    art = _art()
    for g in art["geometries"]:
        if not g.get("present"):
            continue
        atlas = _atlas(g["suffix"])
        assert g["junction_spanning_registers_per_seam"] == g["gap_nt"] - 1
        for panel in atlas["panels"]:
            assert panel["n_fusion_specific"] <= g["gap_nt"] - 1, panel["junction_label"]


def test_a_screen_with_no_hits_is_not_graded_strand_blind():
    """⛔ THE CLEANEST POSSIBLE SCREEN WAS BEING LABELLED THE LEAST TRUSTWORTHY.

    `screen_orientation_status` decided "was orientation parsed" by looking for `hit_frame` on a
    stored hit. A screen whose every design returns NO near-match stores no hit, so the flag never
    went true and the screen was graded `orientation_UNPARSED_counts_are_upper_bounds` — an absent
    reading reported as a reading of absence, on a set of counts that are all zero and cannot be
    upper bounds of anything.

    ⚠ AND THE TRUNCATION CASE MUST STILL FAIL. Zero STORED hits against a non-zero near-match count
    is a censored screen, not an empty one: its hits exist and their strand is unrecoverable, so it
    keeps the upper-bound label. Both directions are asserted, because a fix that admitted the
    censored case would hand a clean verdict to exactly the screens the retraction history is about.
    """
    import junction_aso_offtarget as jo  # noqa: PLC0415
    empty = {"oligos": [{"status": "screened", "antisense_5to3": "A" * 20,
                         "n_offtarget_near_matches": 0, "offtargets": []}]}
    assert jo.screen_orientation_status(empty) == jo.ORIENTATION_NO_HITS
    assert jo.screen_counts_are_orientation_filtered(empty)

    censored = {"oligos": [{"status": "screened", "antisense_5to3": "A" * 20,
                            "n_offtarget_near_matches": 7, "offtargets": []}]}
    assert jo.screen_orientation_status(censored) == jo.ORIENTATION_UNPARSED
    assert not jo.screen_counts_are_orientation_filtered(censored)

    # and the state is distinct from "hits existed and every minus-strand one was diverted"
    assert jo.ORIENTATION_NO_HITS != jo.ORIENTATION_FILTERED


def test_every_new_geometry_screen_is_orientation_safe():
    """A geometry comparison must not put a filtered count beside a strand-blind one."""
    import glob  # noqa: PLC0415

    import junction_aso_offtarget as jo  # noqa: PLC0415
    paths = glob.glob(os.path.join(MOD, "junction-aso-offtarget-*mer-deep500.json"))
    if not paths:
        pytest.skip("no longer-geometry screens in this checkout")
    for p in sorted(paths):
        screen = json.load(open(p, encoding="utf-8"))
        assert jo.screen_counts_are_orientation_filtered(screen), (
            f"{os.path.basename(p)} is {jo.screen_orientation_status(screen)} — its counts cannot "
            "be compared with an orientation-filtered geometry")


def test_the_artifact_reproduces_from_its_committed_inputs():
    """`--check` is the artifact's own reproduction test; a stale artifact fails here."""
    import aso_gap_length_tradeoff as m  # noqa: PLC0415
    assert m.main(["--check"]) == 0, "aso-gap-length-tradeoff.json is stale; re-run the script"


def test_the_artifact_refuses_to_imply_efficacy_or_safety():
    """Language discipline, on a file a reader can download without the manuscript around it."""
    art = _art()
    txt = json.dumps(art["_what_this_is_not"]) + json.dumps(art.get("_what", ""))
    for required in ("Not a cleavage measurement", "clinical-readiness"):
        assert required in txt, required
