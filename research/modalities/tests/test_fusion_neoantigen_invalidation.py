#!/usr/bin/env python3
"""Guards for the neoantigen retraction grading.

⛔ THE ONE THING THIS MODULE MUST NEVER DO IS INVENT. It counts what is committed and it banners it; it does
not predict, re-predict, edit, delete or synthesise a peptide, a binder or an affinity. These tests hold that,
hold the count against the committed content, and hold the banner idempotent — a banner that stacks on every
run is a banner nobody reads.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, MOD)

import pytest                                                    # noqa: E402

import fusion_neoantigen_invalidation as FNI                     # noqa: E402


@pytest.fixture(scope="module")
def art():
    return json.load(open(FNI.BREAKPOINT_ARTIFACT, encoding="utf-8"))


def test_the_artifact_parses_and_leads_with_the_banner(art):
    assert list(art)[0] == FNI.BANNER_KEY, "the banner must be the FIRST key — a footnote is not a banner"
    b = art[FNI.BANNER_KEY]
    assert b["status"].startswith("RETRACTED")
    assert "DO NOT QUOTE" in b["status"]


def test_the_corrected_junction_is_read_from_the_gate_that_reproduced_it_not_typed():
    """⛔ Rule 1: one home. If R13-a's gate ever stops saying REPRODUCED, this must refuse rather than grade."""
    junction, gate = FNI._corrected_junction()
    inv = json.load(open(FNI.INVENTORY, encoding="utf-8"))
    assert junction == inv["gate"]["junction"] == "EWSR1(1-264)::NR4A3(1-626)"
    assert gate["status"] == "REPRODUCED"


def test_the_corrected_window_skips_the_non_coding_exon_instead_of_sliding():
    """The fix itself, exercised through the FIXED helpers over the committed exon map."""
    resumes, cuts, skipped = FNI.corrected_windows()
    assert 2 not in resumes, "NR4A3 transcript exon 2 carries no coding sequence and must be REFUSED"
    assert [s["transcript_exon"] for s in skipped] == [2]
    assert FNI.residue_of(resumes[3]) == 1, "the literature's 'NR4A3 exon 3' resumes at residue 1"
    assert FNI.residue_of(resumes[4]) == 318
    assert len(cuts) == 9 and cuts[7] == 793, "EWSR1 exon 1 is coding, so the EWSR1 half was never shifted"


def test_the_count_matches_the_committed_content_exactly(art):
    """⛔ COUNTED, never quoted from a prior agent or a remembered figure."""
    c = FNI.classify(art)["counts"]
    junctions = art["junctions"]
    assert c["n_junctions_committed"] == len(junctions) == art["n_inframe_junctions"]
    assert c["n_junctions_seam_not_produced"] + c["n_junctions_seam_relabelled"] == len(junctions)
    assert c["n_distinct_predicted_binders"] == len(art["predicted_binders_ranked"])
    assert (c["n_distinct_predicted_binders_only_at_seams_not_produced"]
            + c["n_distinct_predicted_binders_at_a_relabelled_seam"]) == c["n_distinct_predicted_binders"]
    assert (c["n_distinct_novel_peptides_only_at_seams_not_produced"]
            + c["n_distinct_novel_peptides_at_a_relabelled_seam"]) == c["n_distinct_novel_peptides"]
    assert c["n_junction_level_binder_rows"] == sum(j["n_binders"] for j in junctions)
    assert c["_selfcheck_ranked_equals_junction_level_binders"] is True
    assert c["_selfcheck_artifact_n_distinct_binders"] is True


def test_not_one_committed_nr4a3_label_reproduces_and_every_ewsr1_cut_does(art):
    """The signature of the defect: it is the NR4A3 half, and only the NR4A3 half."""
    c = FNI.classify(art)["counts"]
    assert c["n_junctions_with_a_reproduced_nr4a3_label"] == 0
    assert c["n_junctions_with_a_reproduced_ewsr1_cut"] == c["n_junctions_committed"]


def test_the_relabelled_seam_is_counted_separately_and_never_collapsed(art):
    """⛔ Collapsing 'produced under another label' into 'does not exist' is the same class of error as the
    off-by-two. One committed junction resumes where corrected transcript exon 4 does."""
    g = FNI.classify(art)
    rel = [r for r in g["rows"] if r["status"] == "SEAM_RELABELLED"]
    assert len(rel) == 1
    r = rel[0]
    assert r["nr4a3_resumes_at_residue"] == 318
    assert r["corrected_transcript_exon_that_produces_this_offset"] == [4]
    assert r["committed_label"].endswith("NR4A3 exon 2"), "the label is the thing that was wrong"


def test_the_banner_does_not_contradict_R13a(art):
    b = art[FNI.BANNER_KEY]
    inv = json.load(open(FNI.INVENTORY, encoding="utf-8"))
    flag = inv["neoantigen_lane_flag"]
    # both artifacts must agree on the two figures they BOTH state
    assert b["counts"]["n_junctions_committed"] == flag["n_junctions"]
    assert b["counts"]["n_distinct_predicted_binders"] == flag["n_predicted_binders"]
    # and the banner must explain the one place their wording differs, rather than leaving it to a reader
    assert "neoantigen_lane_flag" in b["⚠_how_this_reconciles_with_R13a"]
    assert "318" in b["⚠_how_this_reconciles_with_R13a"]


def test_the_banner_names_the_downstream_blast_radius(art):
    b = art[FNI.BANNER_KEY]
    cited = {r["path"] for r in b["downstream_citations"]}
    loaded = {r["path"] for r in b["downstream_consumers"] if r["kind"].startswith("CODE — LOADS")}
    # the two computational consumers are the serious half — neither prints a peptide of its own accord
    assert "research/modalities/hla_coverage.py" in loaded
    assert "research/modalities/vaccine_construct.py" in loaded
    # and the artifacts they produced quote the peptides directly
    assert "research/modalities/vaccine-construct.json" in cited
    assert all(r["n_peptides_quoted"] > 0 for r in b["downstream_citations"])


def test_no_peptide_binder_or_affinity_was_altered(art):
    """⛔ The banner is ADDITIVE. Every peptide, binder and affinity must be byte-identical to the committed
    content — this module retracts a claim, it does not edit evidence."""
    import subprocess
    blob = subprocess.run(["git", "show", "HEAD:research/modalities/fusion-breakpoint-neoantigens.json"],
                          capture_output=True, text=True, cwd=FNI.REPO)
    if blob.returncode != 0:                                     # pragma: no cover - shallow checkout
        pytest.skip("the committed blob is not reachable here")
    before = json.loads(blob.stdout)
    after = {k: v for k, v in art.items() if k != FNI.BANNER_KEY}
    assert {k: v for k, v in before.items() if k != FNI.BANNER_KEY} == after


def test_the_banner_is_idempotent(tmp_path, monkeypatch):
    """Re-grading must REPLACE the banner, never stack one inside another."""
    src = json.load(open(FNI.BREAKPOINT_ARTIFACT, encoding="utf-8"))
    p = tmp_path / "art.json"
    p.write_text(json.dumps(src, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(FNI, "BREAKPOINT_ARTIFACT", str(p))
    b1, a1 = FNI.breakpoint_banner("t", "t")
    assert FNI.BANNER_KEY not in a1, "the previous banner must be stripped before regrading"
    assert b1["counts"] == src[FNI.BANNER_KEY]["counts"]


def test_the_second_artifact_is_flagged_UNVERIFIED_and_not_called_the_off_by_two():
    """⚠ A DIFFERENT AND SMALLER DEFECT. Labelling it 'retracted for the off-by-two' would be wrong, and the
    phase question that would settle it is explicitly not settled here."""
    art2 = json.load(open(FNI.SINGLE_BREAKPOINT_ARTIFACT, encoding="utf-8"))
    b = art2[FNI.BANNER_KEY]
    assert b["status"].startswith("NOT VERIFIED")
    assert "does not carry the coding/transcript exon slip" in \
        b["⛔_this_is_a_different_defect_from_the_off_by_two"]
    assert b["modelled_junction"] == "EWSR1(1-264)::NR4A3(2-626)"
    assert b["corrected_junction"] == "EWSR1(1-264)::NR4A3(1-626)"
    assert "_phase_note" in b["⚠_what_this_does_NOT_settle"]


def test_the_met1_difference_is_measured_against_the_committed_sequence_cache():
    """⛔ Not asserted from memory: the seam is checked against the committed UniProt cache."""
    seqs = json.load(open(FNI.SEQ_CACHE, encoding="utf-8"))
    art2 = json.load(open(FNI.SINGLE_BREAKPOINT_ARTIFACT, encoding="utf-8"))
    assert seqs["NR4A3"][0] == "M" and len(seqs["NR4A3"]) == 626
    assert art2["_breakpoint_model"]["junction_context_right10"] == seqs["NR4A3"][1:11]


def test_the_routed_map_edit_points_at_the_artifact_and_restates_no_peptide(art):
    edits = FNI.map_edits(art[FNI.BANNER_KEY])
    assert edits and all(e["artifact"].startswith("fusion-breakpoint-neoantigens.json") for e in edits)
    peps = {b["peptide"] for b in art["predicted_binders_ranked"]}
    text = json.dumps(edits)
    assert not [p for p in peps if p in text], "a routed map edit must never carry a retracted peptide"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
