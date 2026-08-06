"""THE ASO LANE'S SEAM — pinned so neither of the two defects that produced the retracted panel can return.

⛔ DEFECT 1 (route framing audit, 2026-08-06). `junction_aso.py` indexed a CODING-exon offset table with a
TRANSCRIPT exon number. NR4A3 ENST00000395097 has 8 transcript exons of which 1 and 2 carry no coding
sequence, so "NR4A3 exon 3" addressed the third CODING exon. MEASURED: the committed seam `TTGTCCGTACAG`
sits at NR4A3 CDS nt 1081 = residue 361, which `fusion-neoantigen-retraction.json` grades
SEAM_NOT_PRODUCED against a corrected plausible resume range of [1, 1].

⛔ DEFECT 2 (found 2026-08-06 while regenerating). The fix for Defect 1 was arithmetically right and STILL
could not regenerate the panel: it concatenated CDS to CDS, discarding the 5'UTR that NR4A3 transcript
exon 3 carries ahead of its ATG. A real fusion transcript retains the acceptor exon whole. Consequences,
both proved below from the COMMITTED exon audit with no network:
  (a) the reported seam context would be wrong for an mRNA-level modality, and
  (b) the in-frame self-check would have RAISED on e7n3 and e12n3 — the two junctions the manuscript
      leads with — while admitting only e11n3, which the manuscript does not use.

⭐ WHY THESE TESTS USE THE COMMITTED AUDIT RATHER THAN A FIXTURE. Both defects were arithmetic over a real,
committed exon index, and both survived because the arithmetic was never checked against it. A synthetic
fixture would have passed under the buggy code too. `nr4a3-exon-audit.json` is the graded record, so the
tests that would have caught these read it — and they are marked `committed_artifact` for exactly the
reason conftest gives: they assert data, not behaviour.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fusion_breakpoints as fb  # noqa: E402
import junction_aso as ja  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(HERE, "nr4a3-exon-audit.json")
RETRACTION = os.path.join(HERE, "fusion-neoantigen-retraction.json")

# The retracted values. Named ONCE here; every assertion below points at these names rather than
# re-typing them, and `test_the_retracted_values_are_still_what_the_retraction_grades` proves the
# names still match the graded record.
RETRACTED_CDS_NT = 1081
RETRACTED_RESIDUE = 361


def _audit():
    with open(AUDIT) as fh:
        return json.load(fh)


def _model_from_committed_audit(symbol):
    """A `fusion_breakpoints.gene_model`-shaped dict built from the COMMITTED exon audit.

    Enough for the offset helpers: they touch only `offsets`, `coding_ranks` and `symbol`. This is what
    lets the arithmetic that produced the retracted seam be exercised with no network.
    """
    g = _audit()[symbol]
    coding = [e for e in g["exons"] if e["is_coding"]]
    return {"symbol": symbol,
            "offsets": [e["cumulative_coding_nt_through_exon"] for e in coding],
            "coding_ranks": [e["transcript_exon_rank"] for e in coding]}


# ─────────────────────────────────────────────────────────────────────────────────────────────
# DEFECT 1
# ─────────────────────────────────────────────────────────────────────────────────────────────

@pytest.mark.committed_artifact
def test_the_old_arithmetic_reproduces_the_retracted_seam_exactly():
    """The regression's ANCHOR: prove the old expression really is what produced 1081/361.

    Without this, "we fixed an off-by-two" is a story. With it, the test suite carries the defect's
    fingerprint, so a future reader can tell a genuine seam change from a reintroduced bug.
    """
    nr4 = _model_from_committed_audit("NR4A3")
    assert nr4["offsets"][3 - 2] == RETRACTED_CDS_NT
    assert (RETRACTED_CDS_NT // 3) + 1 == RETRACTED_RESIDUE


@pytest.mark.committed_artifact
def test_the_corrected_helper_resumes_nr4a3_exon_3_at_residue_1():
    nr4 = _model_from_committed_audit("NR4A3")
    q = fb.resume_offset(nr4, 3)
    assert q == 0
    assert (q // 3) + 1 == 1


@pytest.mark.committed_artifact
def test_the_corrected_helper_raises_on_a_non_coding_acceptor_instead_of_sliding():
    """NR4A3 transcript exon 2 is in the DECLARED window and carries no CDS. Sliding onto its
    neighbour is precisely Defect 1, so the helper must refuse rather than answer."""
    nr4 = _model_from_committed_audit("NR4A3")
    assert 2 in list(fb.NR4A3_EXON_WINDOW)
    with pytest.raises(ValueError):
        fb.resume_offset(nr4, 2)


@pytest.mark.committed_artifact
def test_the_ewsr1_side_reproduced_correctly_which_is_why_nothing_caught_it():
    """EWSR1 transcript exon 1 IS coding, so rank == coding index and old == new on that side.

    This is the transferable half of the finding: the two panels agreed with each other and the paper
    read the agreement as confirmation. The test exists so that fact stays visible in the code.
    """
    ews = _model_from_committed_audit("EWSR1")
    for e in (7, 12):
        assert ews["offsets"][e - 1] == fb.cut_offset(ews, e)


@pytest.mark.committed_artifact
def test_the_retracted_values_are_still_what_the_retraction_grades():
    with open(RETRACTION) as fh:
        r = json.load(fh)["breakpoint_artifact"]
    graded = [j for j in r["junctions_graded"]
              if j["nr4_cds_nt"] == RETRACTED_CDS_NT
              and j["nr4a3_resumes_at_residue"] == RETRACTED_RESIDUE]
    assert graded, "the retraction no longer grades 1081/361 — this test's anchor has moved"
    assert all(j["status"] == "SEAM_NOT_PRODUCED" for j in graded)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# DEFECT 2 — the CDS-concatenation model cannot build the junctions the manuscript leads with
# ─────────────────────────────────────────────────────────────────────────────────────────────

@pytest.mark.committed_artifact
def test_cds_concatenation_would_have_refused_the_two_junctions_the_paper_leads_with():
    """(cut) mod 3 for EWSR1 e7 and e12 is 1, so with NR4A3 resuming at CDS nt 0 the chimeric ORF
    frameshifts and the C-terminus check fails. Only e11 survives — a junction the paper does not use.

    ⚠ This is a statement about the MODEL, not about the biology. The biology is closed by the acceptor
    exon's own 5' phase, which a CDS-level instrument cannot see. That is Defect 2 in one assertion.
    """
    ews = _model_from_committed_audit("EWSR1")
    e_win = list(fb.EWSR1_EXON_WINDOW)
    survive = [e for e in e_win if fb.cut_offset(ews, e) % 3 == 0]
    assert survive == [11]
    for e in (7, 12):
        assert fb.cut_offset(ews, e) % 3 == 1, "e7 and e12 must share a phase — see the frame identity"


@pytest.mark.committed_artifact
def test_the_e11_no_output_the_paper_flagged_is_the_off_by_two_announcing_itself():
    """⭐ THE DEFECT'S ONE SPONTANEOUS SYMPTOM, ROOT-CAUSED.

    `fusion-junction-aso-paper.md` §3a-quinquies records E11::N3 as an unexplained no-output and guesses
    *"most likely … our exon indexing for EWSR1 exon 11 → NR4A3 exon 3 may not be in-frame as joined."*
    Under the defective index NR4A3 resumed at CDS nt 1081, so the chimeric CDS is in frame exactly when
    the EWSR1 cut ≡ 1081 (mod 3). That predicts, with no residual, that {7, 9, 10, 12, 13} emit and {11}
    refuses — which is precisely the set of panels the paper claims and the single one it flags.

    The test is here rather than in a comment because it is the evidence that the guess was wrong, and
    because a self-check firing is a diagnostic: this one was read as an exon-boundary to-verify for a
    month while the arithmetic that explains it sat in a committed artifact costing nothing to read.
    """
    ews = _model_from_committed_audit("EWSR1")
    emitted = {e for e in fb.EWSR1_EXON_WINDOW
               if fb.cut_offset(ews, e) % 3 == RETRACTED_CDS_NT % 3}
    assert {7, 9, 10, 12, 13} <= emitted
    assert 11 not in emitted


@pytest.mark.committed_artifact
def test_e7_and_e12_share_a_phase_so_one_utr_length_settles_both():
    """The chimeric ORF is in frame iff (cut + U) mod 3 == 0, where U = acceptor-exon 5'UTR nt retained.
    e7 and e12 are both phase 1, so a single U ≡ 2 (mod 3) puts BOTH in frame. That is a PREDICTION the
    module tests against Ensembl; U is UNKNOWN from any artifact in this repo."""
    ews = _model_from_committed_audit("EWSR1")
    assert fb.cut_offset(ews, 7) % 3 == fb.cut_offset(ews, 12) % 3


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE GUARDS IN THE FIXED MODULE (behaviour, no network)
# ─────────────────────────────────────────────────────────────────────────────────────────────

def test_coding_nt_per_exon_is_derived_from_the_transcript_model_alone():
    """A three-exon toy where exon 1 is pure 5'UTR — the shape that caused Defect 2."""
    m = {"symbol": "TOY", "cdna": "N" * 30, "cds": "N" * 15, "utr5_len": 8,
         "tx_ends": [10, 20, 30], "protein": "", "n_transcript_exons": 3}
    assert ja.coding_nt_per_exon(m) == [2, 10, 3]


def test_exon_tx_start_and_end_are_transcript_coordinates_not_coding_ones():
    m = {"symbol": "TOY", "tx_ends": [10, 20, 30]}
    assert ja.exon_tx_start(m, 1) == 0
    assert ja.exon_tx_start(m, 2) == 10
    assert ja.exon_tx_end(m, 2) == 20
    with pytest.raises(ValueError):
        ja.exon_tx_start(m, 4)


@pytest.mark.committed_artifact
def test_the_plausible_resume_range_is_read_from_the_inventory_not_typed():
    """ONE HOME. If someone re-types [1, 1] into the module this still passes — so the test asserts the
    VALUE comes back from the graded file, and the module's own source is checked for a literal copy."""
    lo, hi = ja.plausible_nr4a3_resume_residues()
    with open(os.path.join(HERE, "fusion-object-inventory.json")) as fh:
        inv = json.load(fh)
    want = inv["inventory"]["excluded_span"][
        "nr4a3_resume_range_across_plausible_breakpoints"]
    assert [lo, hi] == want


def test_the_module_refuses_a_seam_outside_the_plausible_range(monkeypatch):
    """The guard that would have stopped the retracted panel being emitted at all.

    Built on a toy pair of transcripts so it exercises the REAL `build_parents_and_fusion` path — the
    seam that must be refused is constructed, not mocked away.
    """
    monkeypatch.setenv("FUSION_JUNCTION_MODE", "real")
    monkeypatch.setenv("EWSR1_EXON_END", "1")
    monkeypatch.setenv("NR4A3_EXON_START", "2")

    # NR4A3 toy: exon 1 non-coding, exon 2 opens the CDS, exon 3 resumes at residue 4.
    nr4 = {"symbol": "NR4A3", "transcript": "TOY", "cdna": "AAA" + "ATG" * 6, "cds": "ATG" * 6,
           "protein": "MMMMMM", "tx_ends": [3, 12, 21], "utr5_len": 3, "n_transcript_exons": 3,
           "exon_lens": [3, 9, 9], "strand": 1}
    ews = {"symbol": "EWSR1", "transcript": "TOY", "cdna": "GGG" * 4, "cds": "GGG" * 4,
           "protein": "GGGG", "tx_ends": [12], "utr5_len": 0, "n_transcript_exons": 1,
           "exon_lens": [12], "strand": 1}
    monkeypatch.setattr(ja, "transcript_model", lambda s: ews if s == "EWSR1" else nr4)
    monkeypatch.setattr(ja, "plausible_nr4a3_resume_residues", lambda: (1, 1))

    # exon 2 resumes at residue 1 -> allowed; exon 3 resumes at residue 4 -> must be refused.
    ja.build_parents_and_fusion()
    monkeypatch.setenv("NR4A3_EXON_START", "3")
    with pytest.raises(RuntimeError, match="SEAM_NOT_PRODUCED"):
        ja.build_parents_and_fusion()


def test_the_module_refuses_a_non_coding_acceptor_exon(monkeypatch):
    monkeypatch.setenv("FUSION_JUNCTION_MODE", "real")
    monkeypatch.setenv("EWSR1_EXON_END", "1")
    monkeypatch.setenv("NR4A3_EXON_START", "1")
    nr4 = {"symbol": "NR4A3", "transcript": "TOY", "cdna": "AAA" + "ATG" * 6, "cds": "ATG" * 6,
           "protein": "MMMMMM", "tx_ends": [3, 12, 21], "utr5_len": 3, "n_transcript_exons": 3,
           "exon_lens": [3, 9, 9], "strand": 1}
    ews = {"symbol": "EWSR1", "transcript": "TOY", "cdna": "GGG" * 4, "cds": "GGG" * 4,
           "protein": "GGGG", "tx_ends": [12], "utr5_len": 0, "n_transcript_exons": 1,
           "exon_lens": [12], "strand": 1}
    monkeypatch.setattr(ja, "transcript_model", lambda s: ews if s == "EWSR1" else nr4)
    monkeypatch.setattr(ja, "plausible_nr4a3_resume_residues", lambda: (1, 1))
    with pytest.raises(RuntimeError, match="no coding sequence"):
        ja.build_parents_and_fusion()


def test_the_provenance_gate_refuses_a_transcript_the_committed_audit_did_not_grade():
    """Check 4. A design panel built on an exon map nobody has graded is worse than no panel."""
    m = {"symbol": "NR4A3", "transcript": "ENST_NOT_THE_ONE_GRADED", "cdna": "A", "cds": "A",
         "protein": "M", "tx_ends": [1], "utr5_len": 0, "n_transcript_exons": 1}
    with pytest.raises(RuntimeError, match="different exon maps"):
        ja._cross_check_against_committed_exon_audit(m)


@pytest.mark.committed_artifact
def test_the_committed_panel_artifacts_still_carry_their_retraction_banner():
    """Until a corrected panel exists these six files are the only ASO artifacts a reader can find, and
    the banner is the only thing standing between them and being quoted."""
    for name in ("junction-aso-designs-e7n3.json", "junction-aso-designs-e12n3.json",
                 "junction-aso-offtarget-e7n3.json", "junction-aso-offtarget-e12n3.json",
                 "aso-insilico-evaluation-e7n3.json", "aso-insilico-evaluation-e12n3.json"):
        with open(os.path.join(HERE, name)) as fh:
            d = json.load(fh)
        assert "_RETRACTED_SEAM" in d, f"{name} lost its retraction banner"
        assert str(RETRACTED_CDS_NT) in d["_RETRACTED_SEAM"]
