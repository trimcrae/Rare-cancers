"""THE BREAKPOINT-RESOLVED NEOANTIGEN PANEL — its seam, its denominator, and the gate that clears it.

Sibling of `test_junction_aso_seam.py`, same discipline and for the same reason: every defect this file
pins was arithmetic over a real committed exon index, and every one of them survived because the
arithmetic was never checked against it. A synthetic fixture would have passed under the buggy code.

⛔ DEFECT (three generations, all of them measured, none of them a rounding error).
  GEN 1 — `fusion_breakpoints.py` indexed a CODING-exon offset table with TRANSCRIPT exon numbers, so
    "NR4A3 exon 3" resumed at CDS nt 1081 = residue 361. 7 junctions, 26 binders, retracted 2026-08-03.
  GEN 2 — the index fix was arithmetically right and STILL wrong: `main()` built the chimera as
    `ews_cds[:p] + nr4_cds[q:]`, CDS onto CDS, discarding the 2 nt of 5'UTR that NR4A3 transcript exon 3
    carries ahead of its ATG. A fusion transcript retains the acceptor exon WHOLE.
  GEN 3 — this module, rebuilt on the transcript model 2026-08-07.

⭐ THE CONSEQUENCE IS PINNED BELOW BECAUSE IT IS COUNTER-INTUITIVE. Dropping 2 nt does not perturb the
junction set; it REPLACES it. With the UTR discarded the in-frame predicate reduces to `cut % 3 == 0`;
with it retained the predicate is `(cut + 2) % 3 == 0`. Two is not a multiple of three, so the two
predicates select DISJOINT residue classes and the two junction sets cannot share a single member. The
CDS instrument admits {e11n3, e11n4} and refuses e7 and e12 — the two junctions the manuscripts lead
with — while the transcript model admits {e7, e9, e10, e12, e13} × n3 and refuses e11.

⛔ AND THE BANNER IS GATED BY RE-DERIVATION, NOT BY THE FILE HAVING BEEN REWRITTEN. The panel may drop
its retraction banner ONLY while independently reproducing the seams, the frames and the peptide sets
that `junction_aso`'s transcript model derives from committed inputs. `test_the_panel_may_drop_its
_banner_only_while_it_re_derives` is the guard; the three tamper tests prove the gate can actually say
no, because a gate that has never refused anything is a decoration.
"""
import copy
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("TRANSCRIPT_SOURCE", "cache")             # $0, no network, committed cache

import fusion_breakpoints as fb  # noqa: E402
import fusion_neoantigen as fn  # noqa: E402
import fusion_neoantigen_invalidation as inv  # noqa: E402
import junction_aso as ja  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(HERE, "fusion-breakpoint-neoantigens.json")
CONSTRUCT_INPUTS = os.path.join(HERE, "emc-construct-inputs.json")

# The retracted resume residues. Named once; `test_the_retracted_residues_are_re_derived` proves these
# names still equal what the pre-fix arithmetic produces over the committed exon audit.
RETRACTED_RESIDUES = [318, 361, 419]


def _panel():
    with open(PANEL) as fh:
        return json.load(fh)


def _models():
    return ja.transcript_model("EWSR1"), ja.transcript_model("NR4A3")


# ─────────────────────────────────────────────────────────────────────────────────────────────
# U = 2 — the number the whole correction turns on, re-derived two independent ways
# ─────────────────────────────────────────────────────────────────────────────────────────────

@pytest.mark.committed_artifact
def test_U_is_two_and_two_independent_derivations_agree():
    """`U` = NR4A3 transcript-exon-3 bases 5' of the ATG. Both derivations read committed data only.

    (a) utr5_len − (exon 1 + exon 2), because exons 1 and 2 are entirely non-coding.
    (b) exon 3's transcript length − exon 3's coding nt.
    They come from different fields of the same measurement, so agreement is a real check on the
    record rather than a restatement of it.
    """
    with open(CONSTRUCT_INPUTS) as fh:
        g = json.load(fh)["genes"]["NR4A3"]
    exons = g["exons"]
    assert [e["is_coding"] for e in exons[:2]] == [False, False], \
        "NR4A3 exons 1 and 2 are non-coding — that fact is the root cause of the off-by-two"
    a = g["utr5_len"] - (exons[0]["exon_length_nt"] + exons[1]["exon_length_nt"])
    b = exons[2]["exon_length_nt"] - exons[2]["coding_nt_in_exon"]
    assert a == b == 2

    # …and the transcript model reproduces it as the retained acceptor 5'UTR of a real junction.
    ews, nr4 = _models()
    assert ja.mrna_junction(ews, nr4, 7, 3)["nr4a3_acceptor_exon_5utr_nt_retained"] == 2


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE DIAGNOSIS — the two coordinate systems select disjoint junction sets
# ─────────────────────────────────────────────────────────────────────────────────────────────

@pytest.mark.committed_artifact
def test_the_cds_and_transcript_models_select_disjoint_junction_sets():
    """The claim the rebuild rests on, exercised through the REAL retained CDS helpers."""
    ews, nr4 = _models()
    cds_sel, _skipped = fb.superseded_cds_selection(ews, nr4)
    tx_sel = [r["junction_label"] for r in ja.graded_window(ews, nr4) if r["grade"] == ja.EMITTABLE]
    assert cds_sel and tx_sel, "both models must select something, or the comparison is vacuous"
    assert not (set(cds_sel) & set(tx_sel)), \
        f"the two models must be disjoint; they share {sorted(set(cds_sel) & set(tx_sel))}"


@pytest.mark.committed_artifact
def test_the_cds_model_would_have_refused_the_two_junctions_the_manuscripts_lead_with():
    """The counterfactual, stated as a test so it cannot decay into a story in a docstring."""
    ews, nr4 = _models()
    cds_sel, _ = fb.superseded_cds_selection(ews, nr4)
    assert "EWSR1_e7__NR4A3_e3" not in cds_sel
    assert "EWSR1_e12__NR4A3_e3" not in cds_sel
    assert "EWSR1_e11__NR4A3_e3" in cds_sel                    # and admitted one nothing uses


@pytest.mark.committed_artifact
def test_the_cds_model_dropped_the_non_coding_acceptor_without_leaving_a_row():
    """An absent reading is not a reading of absence (CLAUDE.md §4). NR4A3 exon 2 vanished to stderr."""
    ews, nr4 = _models()
    _sel, skipped = fb.superseded_cds_selection(ews, nr4)
    assert {r["junction_label"] for r in skipped} == {
        f"EWSR1_e{e}__NR4A3_e2" for e in fb.EWSR1_EXON_WINDOW}
    # the replacement grades every one of them explicitly instead
    rows = ja.graded_window(ews, nr4)
    e2 = [r for r in rows if r["NR4A3_exon_start"] == 2]
    assert len(e2) == len(list(fb.EWSR1_EXON_WINDOW))
    assert {r["grade"] for r in e2} == {"NON_CODING_ACCEPTOR"}
    assert {r["nr4a3_acceptor_exon_5utr_nt_retained"] for r in e2} == {176}


@pytest.mark.committed_artifact
def test_e11_drops_because_its_cut_is_codon_aligned():
    """e11 is the ONLY declared donor cut on a codon boundary, which is exactly why the two models
    disagree about it: phase 0 composes with U=0 and fails with U=2."""
    ews, nr4 = _models()
    rows = {r["junction_label"]: r for r in ja.graded_window(ews, nr4)}
    e11 = rows["EWSR1_e11__NR4A3_e3"]
    assert e11["ewsr1_coding_phase"] == 0
    assert e11["frame_sum_mod3"] == 2 and e11["in_frame"] is False
    assert e11["grade"] == "OUT_OF_FRAME"


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE SEAM — a novel codon belonging to neither parent
# ─────────────────────────────────────────────────────────────────────────────────────────────

@pytest.mark.committed_artifact
def test_every_emitted_seam_carries_a_novel_codon_and_nr4a3_met1_survives():
    ews, nr4 = _models()
    emitted = [r for r in ja.graded_window(ews, nr4, keep_sequences=True)
               if r["grade"] == ja.EMITTABLE]
    assert emitted
    for r in emitted:
        row = fb.emit_junction(ews, nr4, r)
        assert row["ewsr1_coding_phase"] == 1                   # 1 leftover donor nt …
        assert row["nr4a3_acceptor_exon_5utr_nt_retained"] == 2  # … + 2 retained UTR nt = one codon
        assert row["seam_codon_residue"] in ("N", "D")
        assert row["nr4a3_first_residue"] == 1
        assert row["junction_context_protein_seam"].endswith("MPCVQAQYSP")


@pytest.mark.committed_artifact
def test_the_e7_seam_is_the_one_the_single_junction_artifact_carries():
    """Two lanes, one seam. The corrected single-junction artifact and this panel must agree at e7n3,
    or one of them is wrong — which is precisely how the retracted pair went undetected (two artifacts
    agreeing is not evidence when one defect produces both; here they are produced by different code)."""
    ews, nr4 = _models()
    row = fb.emit_junction(ews, nr4, ja.mrna_junction(ews, nr4, 7, 3))
    assert row["junction_context_protein_seam"] == "SQQSSSYGQQ-N-MPCVQAQYSP"
    single = json.load(open(os.path.join(HERE, "fusion-neoantigen-predictions.json")))
    m = single["_breakpoint_model"]
    assert m["junction_context_left10"] + m["junction_context_right10"] == "SQQSSSYGQQ" + "NMPCVQAQYS"
    # and the peptide sets must be identical, not merely overlapping
    assert len(row["novel_peptides"]) == single["n_spanning_peptides"]
    quoted = {r["peptide"] for r in single["top_predictions"]} | {r["peptide"] for r in single["binders"]}
    assert quoted <= set(row["novel_peptides"])


def test_junction_peptides_has_exactly_one_definition():
    """⛔ The two modules held DIFFERENT definitions of "junction-spanning" for the same seam (38 vs 34
    peptides), which is how the panel dropped the single-junction artifact's own top-ranked peptide.
    `fusion_neoantigen` now delegates; this fails if anyone reintroduces a private copy."""
    toy, j0 = "AAAAAXBBBBB", 5
    assert fn.junction_peptides(toy, j0, [3], True) == fb.junction_peptides(toy, j0, [3], True)
    with_novel = fb.junction_peptides(toy, j0, [3], novel_residue=True)
    straddle = fb.junction_peptides(toy, j0, [3], novel_residue=False)
    assert "XBB" in with_novel and "XBB" not in straddle       # the k-mer that begins at the novel residue
    assert set(straddle) < set(with_novel)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE BANNER GATE — a file that is merely rewritten is not a file that is verified
# ─────────────────────────────────────────────────────────────────────────────────────────────

@pytest.mark.committed_artifact
def test_the_retracted_residues_are_re_derived_not_read_from_a_field_that_drains():
    """`neoantigen_lane_flag.stale_resume_residues` is computed BY READING THE ARTIFACT, so it empties
    the moment the artifact is regenerated. A guard sourced from it would then pass on anything."""
    assert inv._retracted_resume_residues() == RETRACTED_RESIDUES


@pytest.mark.committed_artifact
def test_the_panel_may_drop_its_banner_only_while_it_re_derives():
    """⭐ THE GUARD. Either the banner is present, or the panel independently reproduces the corrected
    seams, frames, resume residues and peptide sets. "Banner removed" is never the whole test."""
    art = _panel()
    if inv.BANNER_KEY in art:
        assert "RETRACT" in art[inv.BANNER_KEY]["status"].upper()
        return
    cleared, checks = inv._breakpoint_panel_clearance(art)
    failed = [c for c in checks if not c["ok"]]
    assert cleared, f"the panel carries no retraction banner and does not re-derive: {failed}"
    # and the things a reader would quote must be present and honestly labelled
    assert art["n_inframe_junctions"] == len(art["junctions"]) >= 1
    assert "SCREEN" in art["⛔_what_this_is_not"]
    for j in art["junctions"]:
        assert j["nr4a3_first_residue"] == 1 and j["in_frame"] is True
        assert j["nr4a3_first_residue"] not in RETRACTED_RESIDUES


@pytest.mark.committed_artifact
def test_the_gate_refuses_a_junction_set_padded_back_to_the_retracted_denominator():
    """The specific failure this task was told not to commit: padding 5 back to 7."""
    art = _panel()
    art.pop(inv.BANNER_KEY, None)
    padded = copy.deepcopy(art)
    extra = copy.deepcopy(padded["junctions"][0])
    extra["junction_label"] = "EWSR1_e11__NR4A3_e3"
    padded["junctions"].append(extra)
    cleared, checks = inv._breakpoint_panel_clearance(padded)
    assert not cleared
    assert any("junction set is exactly" in c["check"] and not c["ok"] for c in checks)


@pytest.mark.committed_artifact
def test_the_gate_refuses_a_seam_that_does_not_re_derive():
    art = _panel()
    art.pop(inv.BANNER_KEY, None)
    tampered = copy.deepcopy(art)
    tampered["junctions"][0]["junction_context_protein_seam"] = "SQQSSSYGQQ--PCVQAQYSPS"
    tampered["junctions"][0]["seam_codon_residue"] = None
    cleared, checks = inv._breakpoint_panel_clearance(tampered)
    assert not cleared
    assert any("seam reproduces" in c["check"] and not c["ok"] for c in checks)


@pytest.mark.committed_artifact
def test_the_gate_refuses_a_peptide_that_occurs_in_a_parent_protein():
    """A junction peptide that exists in EWSR1 or NR4A3 is not fusion-specific, whatever the seam says."""
    art = _panel()
    art.pop(inv.BANNER_KEY, None)
    nr4 = ja.transcript_model("NR4A3")["protein"]
    tampered = copy.deepcopy(art)
    tampered["junctions"][0]["novel_peptides"] = sorted(
        set(tampered["junctions"][0]["novel_peptides"]) | {nr4[100:109]})
    cleared, checks = inv._breakpoint_panel_clearance(tampered)
    assert not cleared
    assert any("absent from BOTH parent proteins" in c["check"] and not c["ok"] for c in checks)


@pytest.mark.committed_artifact
def test_the_gate_refuses_a_panel_whose_refusals_were_dropped():
    """Every declared exon pair must carry a graded row. Silent omission is the GEN-2 failure mode."""
    art = _panel()
    art.pop(inv.BANNER_KEY, None)
    tampered = copy.deepcopy(art)
    tampered["junctions_graded"] = [r for r in tampered["junctions_graded"]
                                    if r.get("grade") == "EMITTABLE"]
    cleared, checks = inv._breakpoint_panel_clearance(tampered)
    assert not cleared
    assert any("graded row, refusals included" in c["check"] and not c["ok"] for c in checks)


@pytest.mark.committed_artifact
def test_the_committed_panel_reports_its_honest_denominator_and_the_superseded_comparison():
    art = _panel()
    if inv.BANNER_KEY in art:
        pytest.skip("panel is retracted; the clearance test above covers that state")
    assert art["n_candidate_exon_pairs"] == len(art["junctions_graded"])
    assert sum(art["grade_counts"].values()) == art["n_candidate_exon_pairs"]
    assert art["grade_counts"]["EMITTABLE"] == art["n_inframe_junctions"]
    comp = art["_superseded_cds_model_comparison"]
    assert comp["sets_are_disjoint"] is True and comp["intersection"] == []
