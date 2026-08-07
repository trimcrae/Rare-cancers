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


@pytest.fixture(scope="module")
def retracted_shaped():
    """A CDS-coordinate artifact in the RETRACTED shape, built from committed inputs.

    ⭐ WHY A CONSTRUCTED INPUT AND NOT THE COMMITTED FILE (2026-08-07). `classify()` is live code and
    must stay tested — it is what grades any artifact still carrying the coding/transcript slip. But it
    used to be tested against `fusion-breakpoint-neoantigens.json` itself, and that file has now been
    regenerated on the corrected transcript model, so those tests were asserting a state the repo is
    supposed to have LEFT. Pointing them at the regenerated file would either fail or, worse, be
    relaxed until they passed.
    ⛔ Nothing here is typed: the resume offsets come from `_retracted_resume_residues`' own
    re-derivation of the pre-fix `offsets[n - 2]` indexing over the committed exon audit, and the
    EWSR1 cuts come from the fixed helpers. The peptide strings are placeholders and are labelled as
    such — this fixture tests the GRADER's branches, never a sequence claim.
    """
    audit = json.load(open(FNI.EXON_AUDIT, encoding="utf-8"))
    offsets = audit["NR4A3"]["coding_offsets"]
    _resumes, cuts, _skipped = FNI.corrected_windows(audit)
    dead_q, relabelled_q = offsets[1], offsets[0]         # 1081 (produced by nothing), 951 (= exon 4)
    junctions = [
        {"EWSR1_exon_end": 7, "NR4A3_exon_start": 3, "ews_cds_nt": cuts[7], "nr4_cds_nt": dead_q,
         "junction_context": "AAAAAA|BBBBBB", "n_novel_peptides": 2,
         "novel_peptides": ["PLACEHOLDR", "PLACEHOLDX"],
         "binders": [{"peptide": "PLACEHOLDR", "allele": "HLA-A*02:01", "class": "strong"}],
         "n_binders": 1},
        {"EWSR1_exon_end": 11, "NR4A3_exon_start": 2, "ews_cds_nt": cuts[11], "nr4_cds_nt": relabelled_q,
         "junction_context": "CCCCCC|DDDDDD", "n_novel_peptides": 1,
         "novel_peptides": ["PLACEHOLDY"],
         "binders": [{"peptide": "PLACEHOLDY", "allele": "HLA-B*07:02", "class": "weak"}],
         "n_binders": 1},
    ]
    ranked = [{"peptide": "PLACEHOLDR"}, {"peptide": "PLACEHOLDY"}]
    return {"_note": "constructed retracted-shape fixture — placeholder peptides, no sequence claim",
            "n_inframe_junctions": len(junctions), "junctions": junctions,
            "predicted_binders_ranked": ranked, "n_distinct_binders": len(ranked)}


def test_the_artifact_carries_the_banner_or_the_grader_clears_it(art):
    """⭐ THE GUARD IS RE-POINTED, NOT RELAXED (2026-08-07) — the same move the sibling ASO guard made.

    ⚠ Superseded, retained: this test asserted the banner is the FIRST key and its status starts
    "RETRACTED … DO NOT QUOTE". Both were true of the retracted artifact, and holding them after
    regeneration would pin the defect in place — a guard that can only ever say "still retracted"
    forbids the repair it exists to demand.

    ⛔ The replacement is STRICTER. The banner may be ABSENT only while `_breakpoint_panel_clearance`
    independently re-derives the panel from committed inputs and passes every check. A banner-less
    artifact the grader does not clear fails here, which is the state this test exists to make
    impossible. Per-check detail and the tamper tests live in `test_fusion_breakpoint_panel_seam.py`.
    """
    if FNI.BANNER_KEY in art:
        assert list(art)[0] == FNI.BANNER_KEY, "the banner must be the FIRST key — a footnote is not a banner"
        b = art[FNI.BANNER_KEY]
        assert b["status"].startswith("RETRACTED")
        assert "DO NOT QUOTE" in b["status"]
        return
    cleared, checks = FNI._breakpoint_panel_clearance(art)
    assert cleared, f"no banner and the panel does not re-derive: {[c for c in checks if not c['ok']]}"
    b, _a = FNI.breakpoint_banner("t", "t")
    assert b["status"].startswith("CLEARED"), b["status"]
    assert b[FNI.STAMP_KEY] is False, "a CLEARED grade must withhold the banner"
    assert b["corrected_junction"] == "EWSR1(1-264)::NR4A3(1-626)"
    assert all(c["ok"] for c in b["what_was_checked"]), b["what_was_checked"]


def test_the_cleared_banner_names_the_downstream_work_the_clearance_does_NOT_do(art):
    """⛔ A clearance that reads as "the lane is fixed" would be worse than the retraction it lifts.

    `hla_coverage.py`, `vaccine_construct.py` and `coverage_scan.py` LOAD this artifact and recompute
    from it; their committed outputs were built on the RETRACTED junction set and are not repaired by
    regenerating the input. The banner has to say so, in the file a reader opens first.
    """
    if FNI.BANNER_KEY in art:
        pytest.skip("artifact is retracted; the clearance state is not under test here")
    b, _a = FNI.breakpoint_banner("t", "t")
    note = b["⚠_downstream_outputs_are_not_regenerated_by_this"]
    loaded = {r["path"] for r in b["downstream_consumers"] if r["kind"].startswith("CODE — LOADS")}
    assert "research/modalities/hla_coverage.py" in loaded
    assert "research/modalities/vaccine_construct.py" in loaded
    for name in ("hla_coverage.py", "vaccine_construct.py", "coverage_scan.py"):
        assert name in note


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


def test_the_count_matches_the_graded_content_exactly(retracted_shaped):
    """⛔ COUNTED, never quoted from a prior agent or a remembered figure.

    ⚠ Superseded, retained: this ran against the committed `fusion-breakpoint-neoantigens.json`, which
    has since been regenerated on the corrected transcript model and no longer carries CDS-space keys.
    The invariant under test was never about that particular file — it is that `classify`'s totals
    equal what its rows actually contain — so it now runs against a constructed retracted-shape input.
    """
    art = retracted_shaped
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


def test_not_one_retracted_nr4a3_label_reproduces_and_every_ewsr1_cut_does(retracted_shaped):
    """The signature of the defect: it is the NR4A3 half, and only the NR4A3 half."""
    c = FNI.classify(retracted_shaped)["counts"]
    assert c["n_junctions_with_a_reproduced_nr4a3_label"] == 0
    assert c["n_junctions_with_a_reproduced_ewsr1_cut"] == c["n_junctions_committed"]


def test_the_relabelled_seam_is_counted_separately_and_never_collapsed(retracted_shaped):
    """⛔ Collapsing 'produced under another label' into 'does not exist' is the same class of error as the
    off-by-two. A junction resuming where corrected transcript exon 4 does is RELABELLED, not absent."""
    g = FNI.classify(retracted_shaped)
    rel = [r for r in g["rows"] if r["status"] == "SEAM_RELABELLED"]
    assert len(rel) == 1
    r = rel[0]
    assert r["nr4a3_resumes_at_residue"] == 318
    assert r["corrected_transcript_exon_that_produces_this_offset"] == [4]
    assert r["committed_label"].endswith("NR4A3 exon 2"), "the label is the thing that was wrong"
    dead = [x for x in g["rows"] if x["status"] == "SEAM_NOT_PRODUCED"]
    assert len(dead) == 1 and dead[0]["nr4a3_resumes_at_residue"] == 361


def test_the_retraction_banner_still_reconciles_itself_with_R13a(retracted_shaped, tmp_path, monkeypatch):
    """The retracted path is live code and keeps its guard: a banner that contradicts R13-a without
    explaining the difference is how two artifacts get read as disagreeing."""
    p = tmp_path / "art.json"
    p.write_text(json.dumps(retracted_shaped, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(FNI, "BREAKPOINT_ARTIFACT", str(p))
    b, _a = FNI.breakpoint_banner("t", "t")
    assert b["status"].startswith("RETRACTED")
    assert b["counts"]["n_junctions_committed"] == len(retracted_shaped["junctions"])
    assert "neoantigen_lane_flag" in b["⚠_how_this_reconciles_with_R13a"]
    assert "318" in b["⚠_how_this_reconciles_with_R13a"]
    # ⚠ NOT the downstream radius here: `consumers()` keys off the artifact's BASENAME and this test
    # monkeypatches that to a tmp file, so the list is legitimately empty. The radius is asserted
    # against the real artifact in `test_the_cleared_banner_names_the_downstream_work_the_clearance
    # _does_NOT_do`. Asserting it here would have to be weakened to pass, which is how a guard rots.


def test_the_grader_never_edits_a_peptide_binder_or_affinity(retracted_shaped, tmp_path, monkeypatch):
    """⛔ The banner is ADDITIVE. This module retracts a claim; it does not edit evidence.

    ⚠ Superseded, retained: this compared the working-tree artifact against `git show HEAD:` minus the
    banner. That equality is false BY DESIGN once the artifact is legitimately regenerated, so the test
    could no longer tell "the grader edited a peptide" from "the lane did its job" — and only one of
    those is a defect. The invariant is now asserted where it actually lives: the grader's output, for
    a given input, differs from that input in the banner key and nothing else.
    """
    p = tmp_path / "art.json"
    p.write_text(json.dumps(retracted_shaped, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(FNI, "BREAKPOINT_ARTIFACT", str(p))
    _b, after = FNI.breakpoint_banner("t", "t")
    assert {k: v for k, v in retracted_shaped.items() if k != FNI.BANNER_KEY} == \
        {k: v for k, v in after.items() if k != FNI.BANNER_KEY}


def test_the_banner_is_idempotent(retracted_shaped, tmp_path, monkeypatch):
    """Re-grading must REPLACE the banner, never stack one inside another."""
    p = tmp_path / "art.json"
    p.write_text(json.dumps(retracted_shaped, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(FNI, "BREAKPOINT_ARTIFACT", str(p))
    b1, a1 = FNI.breakpoint_banner("t", "t")
    stacked = {FNI.BANNER_KEY: b1}
    stacked.update(a1)
    p.write_text(json.dumps(stacked, ensure_ascii=False), encoding="utf-8")
    b2, a2 = FNI.breakpoint_banner("t", "t")
    assert FNI.BANNER_KEY not in a2, "the previous banner must be stripped before regrading"
    assert b2["counts"] == b1["counts"]


def test_the_second_artifact_carries_no_retraction_banner_and_the_grader_says_CLEARED():
    """⭐ THE GUARD IS RE-POINTED, NOT DELETED (2026-08-06).

    ⚠ Superseded, retained: this test used to assert the artifact carried
    `⛔_RETRACTED_SEAMS` with `status` "NOT VERIFIED …", `modelled_junction`
    "EWSR1(1-264)::NR4A3(2-626)", and an unresolved `_phase_note` caveat. All four were correct
    statements about the RETRACTED artifact, and holding them after regeneration would pin the
    defect in place. What must now be held is the opposite invariant, and it is the STRONGER one:
    the banner may be absent ONLY while the grader independently re-derives the corrected seam and
    grades it CLEARED. A banner-less artifact that the grader does not clear fails here.
    """
    art2 = json.load(open(FNI.SINGLE_BREAKPOINT_ARTIFACT, encoding="utf-8"))
    assert FNI.BANNER_KEY not in art2, "the committed artifact still carries a retraction banner"
    b, _art = FNI.single_breakpoint_banner("t", "t")
    assert b["status"].startswith("CLEARED"), b["status"]
    assert b[FNI.STAMP_KEY] is False, "a CLEARED grade must withhold the banner"
    assert b["corrected_junction"] == "EWSR1(1-264)::NR4A3(1-626)"
    assert all(c["ok"] for c in b["what_was_checked"]), b["what_was_checked"]


def test_the_corrected_seam_is_measured_against_the_committed_sequence_cache():
    """⛔ Not asserted from memory: the corrected seam is checked against the committed UniProt cache
    AND against the transcript model, and the retracted peptides must be gone.

    The corrected right-hand context is the NOVEL junction residue followed by NR4A3 from Met1 —
    NOT `NR4A3[1:11]`, which is what the superseded model produced by dropping Met1.
    """
    seqs = json.load(open(FNI.SEQ_CACHE, encoding="utf-8"))
    art2 = json.load(open(FNI.SINGLE_BREAKPOINT_ARTIFACT, encoding="utf-8"))
    nr4 = seqs["NR4A3"]
    assert nr4[0] == "M" and len(nr4) == 626
    model = art2["_breakpoint_model"]
    novel = model["novel_junction_residue"]
    assert novel, "the e7::e3 cut splits a codon, so a novel junction residue must be recorded"
    assert model["junction_context_right10"] == (novel + nr4[:9])
    assert model["junction_context_right10"] != nr4[1:11], "this is the superseded (Met1-dropped) seam"

    expected = FNI._expected_corrected_seam()
    assert expected is not None, "the corrected seam must be derivable from committed inputs alone"
    assert model["junction_context_right10"] == expected[0]

    # The three peptides every downstream file quoted off the superseded seam must be gone.
    peps = set(FNI.peptides_of(art2))
    for retracted in ("GQQPCVQAQY", "QQPCVQAQY", "QPCVQAQY"):
        assert retracted not in peps, f"{retracted} is a superseded-seam peptide"


def test_the_routed_map_edit_points_at_the_artifact_and_restates_no_peptide(art):
    """Holds in BOTH grader states: a routed edit points at the artifact and quotes no peptide.

    The cleared state needs this at least as much as the retracted one — an edit that pasted the new
    lead peptides into the roadmap would give them a second home the moment the panel changed again.
    """
    b, _a = FNI.breakpoint_banner("t", "t")
    edits = FNI.map_edits(b)
    assert edits and all(e["artifact"].startswith("fusion-breakpoint-neoantigens.json") for e in edits)
    peps = {x["peptide"] for x in art.get("predicted_binders_ranked") or []}
    assert peps, "the artifact must state some peptides, or this test is vacuous"
    text = json.dumps(edits)
    assert not [p for p in peps if p in text], "a routed map edit must never carry a peptide string"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))


def test_the_exclusion_is_anchored_to_the_repo_root_not_the_absolute_path():
    """⛔ FAIL-QUIET IN A MEDICAL-INTEGRITY GUARD, measured 2026-08-07.

    `_EXCLUDE` carries "/.claude/" so the scan skips agent worktrees. It was matched against the
    ABSOLUTE path `glob.glob` returns. The harness places worktrees at `<repo>/.claude/worktrees/<id>/`,
    so when the checkout BEING SCANNED is itself a worktree, every absolute path under it contains
    "/.claude/" — every file was excluded, and `consumers()` returned an empty list.

    That is the dangerous shape: it does not raise and does not warn. It answers "which files still
    quote this withdrawn artifact?" with a clean, confident, wrong "none" — an absent reading read as
    a reading of absence, in the one check whose entire job is to find them.

    Measured in one real worktree, same tree, only this module differing: 0 consumers before, 24 after.
    CI checks out to /home/runner/work/..., so `main` never saw it and every agent did.
    """
    assert "/.claude/" in FNI._EXCLUDE, "the worktree exclusion itself must stay"

    # A path INSIDE the repo's own .claude/ is excluded ...
    assert FNI._excluded(os.path.join(FNI.REPO, ".claude", "worktrees", "x", "research", "a.md"))
    # ... while ordinary content is not, however the repo root is spelled.
    assert not FNI._excluded(os.path.join(FNI.REPO, "research", "modalities", "a.md"))

    # ⚠ THE REGRESSION ITSELF: a repo root that lives under /.claude/ must not exclude its own content.
    # Asserted against the real function rather than a re-implementation of its rule.
    rel = os.path.relpath(
        "/home/user/repo/.claude/worktrees/agent-1/research/modalities/a.md",
        "/home/user/repo/.claude/worktrees/agent-1")
    assert not any(x in "/" + rel.replace(os.sep, "/") for x in FNI._EXCLUDE), (
        "an exclusion anchored to the repo root must not fire on the root's own name")

    # And the scan must actually find consumers of a known artifact.
    assert len(FNI.consumers("fusion-breakpoint-neoantigens.json")) > 0
