#!/usr/bin/env python3
"""The TAF15 e6 :: NR4A3-intron-2 cryptic-exon lane, tested offline.

WHAT IS ACTUALLY AT RISK HERE, and therefore what these tests are aimed at. This lane's whole value
is that a 75-nt sequence which is NOT in any committed transcript gets attached to a design panel. A
wrong sequence, or a sequence that was constructed rather than measured, would produce an artifact
indistinguishable from a real one — five plausible 16-mers, a plausible seam, a plausible margin. So
the tests below are weighted towards the refusals rather than the happy path:

  · the exon LENGTH is derived from measured transcript arithmetic and reproduces the source paper's
    own "25 additional amino acids", and the competing reading of that sentence is excluded by frame
  · the candidate enumerator applies all three criteria it claims to
  · every way of getting an unmeasured sequence into the design module is refused

Everything runs offline: `TRANSCRIPT_SOURCE=cache` is forced so no test touches the network.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("TRANSCRIPT_SOURCE", "cache")   # $0, offline, no Ensembl call in a unit test

import nr4a3_intron2_cryptic_exon as cx               # noqa: E402
import aso_taf15_intron2_designs as td                # noqa: E402
import junction_aso as ja                             # noqa: E402
import aso_screen_sets as ass                         # noqa: E402


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    # junction_aso reads TRANSCRIPT_SOURCE at CALL time, so scoping it per test is meaningful.
    monkeypatch.setenv("TRANSCRIPT_SOURCE", "cache")


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The derivation — the step that makes the retrieval falsifiable
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_the_derived_length_reproduces_the_papers_own_25_amino_acids():
    """★ THE LOAD-BEARING TEST. PMID 31020999 says T-N encodes '25 additional amino acids prior to
    the NR4A3 ATG'. If the measured TAF15 cut and the measured NR4A3 exon-3 5'UTR do not reproduce
    that number at exactly one exon length, the retrieval has no target and every design downstream
    is a guess dressed as a measurement."""
    d = cx.derive_required_length()
    assert d["difference_aa"] == cx.ADDITIONAL_AA_BEFORE_NR4A3_ATG
    assert d["derived_length_nt"] == 3 * cx.ADDITIONAL_AA_BEFORE_NR4A3_ATG == 75
    assert d["derived_length_nt"] % 3 == 0, "a length that shifts the register cannot be the answer"


def test_the_competing_reading_of_the_sentence_is_excluded_by_frame_not_by_preference():
    """The paper's sentence admits a second reading — 25 aa TOTAL before the ATG rather than 25
    ADDITIONAL. It is rejected because it breaks the reading frame the same sentence asserts, and
    that rejection must be recorded in the artifact rather than made silently."""
    d = cx.derive_required_length()
    alt = d["derived_length_nt"] - d["acceptor_exon_5utr_nt_retained"]
    assert alt % 3 != 0, "the competing reading must be excluded by arithmetic, not by taste"
    assert "Rejected by arithmetic" in d["_reading_B_rejected"]


def test_the_derivation_uses_measured_values_not_typed_ones():
    """`cut` and `U` must come out of the committed transcript models. If either were typed into the
    module, changing the model would not change the derivation — which is the whole failure mode."""
    d = cx.derive_required_length()
    donor = ja.transcript_model("TAF15")
    acceptor = ja.transcript_model("NR4A3")
    assert d["donor_coding_nt_through_cut"] == sum(ja.coding_nt_per_exon(donor)[:6])
    assert d["acceptor_exon_5utr_nt_retained"] == (
        acceptor["utr5_len"] - ja.exon_tx_start(acceptor, 3))
    # T-N* must itself be in register, or the "additional" arithmetic has no baseline.
    assert (d["donor_coding_nt_through_cut"] + d["acceptor_exon_5utr_nt_retained"]) % 3 == 0


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The candidate enumerator — does it apply the criteria it advertises?
# ─────────────────────────────────────────────────────────────────────────────────────────────
def _intron_with_one_planted_exon(exon, cut):
    """A synthetic intron carrying exactly one AG|exon|GT window, plus decoys that each fail one
    criterion. The point is to prove the filter discriminates, not that it returns something."""
    filler = "CCCCCCCCCC"
    return filler + "AG" + exon + "GT" + filler


def test_the_enumerator_requires_the_canonical_splice_flanks():
    cut = cx.derive_required_length()["donor_coding_nt_through_cut"]
    exon = "A" * 75
    good = _intron_with_one_planted_exon(exon, cut)
    assert len(cx.enumerate_candidates(good, 75, cut)) == 1
    # same window, acceptor flank broken -> not a candidate
    bad_acc = good.replace("CCAG" + exon, "CCCC" + exon, 1)
    assert cx.enumerate_candidates(bad_acc, 75, cut) == []
    # same window, donor flank broken -> not a candidate
    bad_don = good.replace(exon + "GT", exon + "CC", 1)
    assert cx.enumerate_candidates(bad_don, 75, cut) == []


def test_the_enumerator_rejects_a_window_with_a_stop_codon_in_the_fusion_frame():
    """The paper says T-N encodes the whole NR4A3 CDS, so the ORF reads THROUGH the cryptic exon.
    A window carrying a stop in that frame cannot be it — and the frame is set by the TAF15 cut,
    not by the window's own first base, which is the part that is easy to get wrong."""
    cut = cx.derive_required_length()["donor_coding_nt_through_cut"]
    off = cx._codon_offset_into_cryptic(cut)
    assert off == (-cut) % 3
    exon = list("A" * 75)
    exon[off:off + 3] = list("TAA")                      # a stop in the READING frame
    stopped = _intron_with_one_planted_exon("".join(exon), cut)
    assert cx.enumerate_candidates(stopped, 75, cut) == []
    # the same three bases one position earlier are NOT in frame, so they must not disqualify it
    exon2 = list("A" * 75)
    exon2[off + 1:off + 4] = list("TAA")
    assert len(cx.enumerate_candidates(_intron_with_one_planted_exon("".join(exon2), cut),
                                       75, cut)) == 1


def test_a_sequence_that_is_not_in_the_measured_intron_is_refused():
    """⛔ The one check that stands between this lane and a fabricated 75-mer."""
    with pytest.raises(RuntimeError, match="constructed rather than measured"):
        cx._assert_from_measured_intron("ACGTACGTACGT", "TTTTTTTTTTTT")
    with pytest.raises(RuntimeError):
        cx._assert_from_measured_intron("", "ACGT")
    assert cx._assert_from_measured_intron("CGTA", "ACGTAC") is True


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The design module's refusals — every route to an unmeasured sequence
# ─────────────────────────────────────────────────────────────────────────────────────────────
def _seam_record(tmp_path, **over):
    # ⚠ THE FIXTURE MUST BE A *VALID* RECORD BY DEFAULT, or every test that needs one gets the
    # refusal path instead and fails for a reason it is not about. `load_seam_record` now requires
    # `reproduces_the_papers_25aa_claim_under` to be non-empty — the check that the resolved exon
    # actually reproduces PMID 31020999's "25 additional amino acids" under a stated reading — and
    # this fixture predates it, so three tests were failing on a missing key rather than on the
    # behaviour they assert. Tests that want the refusal clear it explicitly, below.
    exon = over.pop("sequence", "A" * 75)
    rec = {"resolved_cryptic_exon": {"sequence": exon,
                                     "is_a_substring_of_the_fetched_intron": True,
                                     "reproduces_the_papers_25aa_claim_under": ["reading_ENCODED_aa"],
                                     "aa_accounting": {"frame_preserved": True},
                                     "how": "unit-test fixture"},
           "length_derivation": {"derived_length_nt": 75},
           "intron": {"chrom": "9", "strand": 1, "genomic_start": 1, "genomic_end": 2},
           "candidate_enumeration": {"n_candidates": 1},
           "annotated_exons_of_the_derived_length": []}
    rec["resolved_cryptic_exon"].update(over.pop("resolved", {}))
    rec.update(over)
    p = tmp_path / "seam.json"
    p.write_text(json.dumps(rec))
    return str(p)


def test_the_design_module_refuses_when_the_seam_record_is_absent(monkeypatch, tmp_path):
    monkeypatch.setattr(td, "SEAM_RECORD", str(tmp_path / "nope.json"))
    with pytest.raises(RuntimeError, match="is missing"):
        td.load_seam_record()


def test_the_design_module_refuses_an_unresolved_seam(monkeypatch, tmp_path):
    """An artifact that RAN but did not identify the exon is a measurement of ignorance. It must
    stop the designs, not be read as an empty-but-usable record."""
    monkeypatch.setattr(td, "SEAM_RECORD",
                        _seam_record(tmp_path, resolved={"sequence": None}))
    with pytest.raises(RuntimeError, match="NO resolved cryptic exon"):
        td.load_seam_record()


def test_the_design_module_refuses_a_sequence_not_drawn_from_the_measured_intron(monkeypatch,
                                                                                 tmp_path):
    monkeypatch.setattr(td, "SEAM_RECORD", _seam_record(
        tmp_path, resolved={"is_a_substring_of_the_fetched_intron": False}))
    with pytest.raises(RuntimeError, match="constructed, not measured"):
        td.load_seam_record()


def test_the_design_module_refuses_a_record_that_contradicts_its_own_derivation(monkeypatch,
                                                                               tmp_path):
    """⚠ MATCHED ON THE REFUSAL'S SUBJECT, NOT ON ONE ADJECTIVE. This asserted `match=
    "self-inconsistent"`, and the module's message was rewritten to name the paper's claim and the
    consequence — "does not reproduce PMID 31020999's '25 additional amino acids' ... no design may
    be built on it" — which is the better message and dropped the word. The test then failed while
    the behaviour it guards was intact and improved.

    A refusal test should pin THAT THE MODULE REFUSES and WHAT IT REFUSES ABOUT, not the wording,
    or every improvement to an error message reads as a regression.
    """
    monkeypatch.setattr(td, "SEAM_RECORD", _seam_record(
        tmp_path, sequence="A" * 72, resolved={"reproduces_the_papers_25aa_claim_under": []}))
    with pytest.raises(RuntimeError, match="no design may be built on it"):
        td.load_seam_record()


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The acceptor model and the seam it produces
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_the_synthetic_acceptor_passes_the_same_self_checks_a_fetched_model_does():
    """A synthetic transcript model that skipped the checks would be a second, ungated source of
    truth — the failure junction_aso's provenance gate exists to prevent."""
    nr4 = ja.transcript_model("NR4A3")
    cryptic = "ACG" * 25
    m = td.build_tn_acceptor_model(cryptic)
    assert sum(m["exon_lens"]) == len(m["cdna"])
    assert m["cdna"].count(m["cds"]) == 1
    assert m["cdna"].index(m["cds"]) == m["utr5_len"]
    assert m["utr5_len"] == len(cryptic) + 2
    assert ja.coding_nt_per_exon(m)[0] == 0, "the cryptic exon lies 5' of the ATG; it is not coding"
    assert m["exon_lens"][1:] == nr4["exon_lens"][2:], "NR4A3 exons 3-8 must follow unchanged"


def test_a_cryptic_exon_of_the_wrong_length_breaks_the_frame_and_is_caught():
    """⭐ THE CHECK THAT TIES THE SEQUENCE BACK TO THE PAPER. A 74-nt exon builds a perfectly
    well-formed transcript model and a perfectly plausible-looking seam — and silently destroys the
    NR4A3 ORF, contradicting the paper's own 'Both T-N and T-N* encode the whole coding sequence of
    NR4A3'. Frame is the property that makes a wrong retrieval visible."""
    donor = ja.transcript_model("TAF15")
    for L, want in ((75, True), (74, False), (76, False)):
        m = td.build_tn_acceptor_model("A" * L)
        j = ja.mrna_junction_generic(donor, m, 6, 1)
        assert j["in_frame"] is want, f"L={L} should be in_frame={want}"


def test_the_TN_seam_is_not_the_TN_star_seam():
    """The reason this molecule exists: a T-N* reagent cannot reach a T-N transcript. If the two
    seams' acceptor sides agreed, the panel would already cover it and this lane would be pointless."""
    donor = ja.transcript_model("TAF15")
    nr4 = ja.transcript_model("NR4A3")
    j_star = ja.mrna_junction_generic(donor, nr4, 6, 3)
    j_tn = ja.mrna_junction_generic(donor, td.build_tn_acceptor_model("ACG" * 25), 6, 1)
    assert j_star["junction_context_mRNA"] != j_tn["junction_context_mRNA"]
    # donor sides identical (same TAF15 exon 6), acceptor sides different — that is the whole point
    assert j_star["_left"] == j_tn["_left"]
    assert j_star["_right"][:12] != j_tn["_right"][:12]


#: ⛔ THE WHITELIST MEMBERSHIP IS PINNED BY HAND ON PURPOSE, AND THIS IS THE ONE PLACE IN THIS SUITE
#: WHERE THAT IS RIGHT. Everything else here is derived, because a hand-typed value goes stale. This
#: is the opposite case: the whitelist is the ONLY thing standing between this module and
#: junction_aso's coding-acceptor guard, so a new entry appearing without anyone noticing is exactly
#: the failure to catch. Deriving the set from the module would make the test agree with whatever the
#: module says, which is not a check.
#: ⭐ GREW 1 -> 2 ON 2026-08-15 (commit abae9502e, EWSR1 e10 :: NR4A3 intron-2 cryptic exon). The
#: test still asserted a single entry and had been failing since. Superseded, retained (CLAUDE.md
#: rule 1.2): a whitelist of exactly one, ("TAF15", 6, "NR4A3", "intron2_cryptic_exon").
EXPECTED_CRYPTIC_WHITELIST = {
    ("TAF15", 6, "NR4A3", "intron2_cryptic_exon"),
    ("EWSR1", 10, "NR4A3", "intron2_cryptic_exon"),
}


def test_the_whitelist_is_what_reaches_this_seam_and_it_names_its_source():
    """This module routes AROUND junction_aso's coding-acceptor guard, exactly as
    aso_noncoding_acceptor_designs.py does. What makes that a documented route rather than a bypass
    is that every junction it can reach is named explicitly, with a published breakpoint.

    ⚠ THE EVIDENCE FORM IS NOT ALWAYS A PMID, AND REQUIRING ONE WAS TOO NARROW. The EWSR1 exon-10
    seam's breakpoint was never published as an exon in prose — it was DEPOSITED, and its evidence
    strings cite GenBank AF524261.1. That is the same shape as the TCF12 junction the coverage ladder
    resolved from AF289510.1. What the test actually needs is that every entry cites a RETRIEVABLE
    identifier, so both forms are admitted and an entry citing neither still fails.
    """
    got = set(td.PUBLISHED_CRYPTIC_ACCEPTOR_JUNCTIONS)
    assert got == EXPECTED_CRYPTIC_WHITELIST, (
        "the cryptic-acceptor whitelist changed. Every entry here bypasses the coding-acceptor "
        f"guard, so a change is a decision, not a detail: {sorted(got ^ EXPECTED_CRYPTIC_WHITELIST)}")
    for key, meta in td.PUBLISHED_CRYPTIC_ACCEPTOR_JUNCTIONS.items():
        assert meta["excluded_from_the_panel_by"] == "NON_CODING_ACCEPTOR", key
        assert meta["evidence"], key
        # ⚠ AT LEAST ONE evidence string must carry an identifier, not every one. The EWSR1 entry's
        # last line is a DERIVATION — how the seam was recomputed from the deposit's own nucleotides
        # rather than from its annotation notes — and that is corroboration a citation cannot be.
        # Requiring an identifier on every line would push a redundant accession into a sentence
        # whose whole point is that it depends on no annotation.
        assert any("PMID" in e or "GenBank" in e for e in meta["evidence"]), (key, meta["evidence"])
        assert meta["n_independent_sources"] == 1, key


def test_the_guard_in_junction_aso_is_not_weakened():
    """⛔ The coding-acceptor guard catches a COORDINATE SLIP and must still raise. This lane must
    not have relaxed it on the way past."""
    src = open(ja.__file__, encoding="utf-8").read()
    assert "refusing to slide" in src
    assert "carries no coding sequence" in src


def test_the_geometry_is_asserted_against_the_manuscript_panel(monkeypatch, tmp_path):
    """Designs emitted at a different geometry cannot be compared with the panel's, so the module
    must refuse rather than quietly emit them."""
    monkeypatch.setattr(td, "SEAM_RECORD", _seam_record(tmp_path, sequence="ACG" * 25))
    monkeypatch.setattr(ja, "OLIGO_LEN", ass.MANUSCRIPT_GEOMETRY.oligo_len + 4)
    with pytest.raises(AssertionError, match="geometry drift"):
        td.build()


def test_the_side_atlas_is_readable_by_the_deep_screens_and_is_not_the_panel(monkeypatch, tmp_path):
    """The side atlas exists so the five deep screens can run at this seam. If its shape drifted,
    the screens would silently read zero designs — and a screen that measured nothing reports the
    same empty off-target load as a screen that measured a clean design."""
    monkeypatch.setattr(td, "SEAM_RECORD", _seam_record(tmp_path, sequence="ACG" * 25))
    atlas, art = td.build()
    assert atlas["panels"] and atlas["panels"][0]["designs"]
    assert atlas["panels"][0]["junction_label"] == art["junction_label"]
    assert "NOT the manuscript panel" in atlas["_read_this"]
    for d in atlas["panels"][0]["designs"]:
        assert {"antisense_5to3", "target_mRNA_5to3", "fusion_specific"} <= set(d)
    # every design really spans the seam: it must draw bases from both sides
    for d in atlas["panels"][0]["designs"]:
        assert d["gap_bases_from_EWSR1"] >= 1 and d["gap_bases_from_NR4A3"] >= 1


def test_the_panel_reach_check_is_a_measurement_and_can_report_a_hit(monkeypatch, tmp_path):
    """★ THE CLAIM THIS LANE RESTS ON IS CHECKED, NOT ARGUED: no reagent in the 38-junction panel
    engages a T-N transcript. A check that could only ever return zero would be decoration, so the
    positive case is exercised too — if the panel DID reach this seam, the artifact has to say so."""
    monkeypatch.setattr(td, "SEAM_RECORD", _seam_record(tmp_path, sequence="ACG" * 25))
    _, art = td.build()
    reach = art["does_the_published_panel_reach_this_transcript"]
    assert reach["n_panel_designs_tested"] > 100, "the check must actually test the panel"
    assert reach["n_engaging_the_T_N_transcript"] == 0
    assert reach["engaging_designs"] == []

    # the positive branch: a fusion that literally contains a panel design's window must report it
    atlas = json.load(open(td.PANEL_ATLAS, encoding="utf-8"))
    win = atlas["panels"][0]["designs"][0]["target_mRNA_5to3"]
    hit = td.panel_reach_check("TTTT" + win + "TTTT")
    assert hit["n_engaging_the_T_N_transcript"] >= 1
    assert "⚠ NON-ZERO" in hit["_reading"]


def test_a_missing_panel_atlas_is_reported_as_an_absent_reading(monkeypatch):
    """An absent reading is not a reading of absence — a missing atlas must not render as 'zero
    panel reagents reach it', which is the same sentence a real clean result produces."""
    monkeypatch.setattr(td, "PANEL_ATLAS", "/nonexistent/atlas.json")
    r = td.panel_reach_check("ACGT")
    assert r["n_engaging_the_T_N_transcript"] is None
    assert "could not run" in r["_status"]


def test_the_artifact_states_the_coverage_consequence_without_inventing_a_number(monkeypatch,
                                                                                tmp_path):
    """★★ THE HONESTY TEST. The source paper orders the two isoforms and reports no count. An
    artifact that converted 'less common' into a percentage would be fabricating the one number the
    literature declines to give — and it would look exactly like a measurement."""
    monkeypatch.setattr(td, "SEAM_RECORD", _seam_record(tmp_path, sequence="ACG" * 25))
    _, art = td.build()
    cc = art["_coverage_consequence"]
    assert "No number moves" in cc["what_does_not_change"]
    assert "unmeasured" in cc["what_would_settle_it"] or "count" in cc["what_does_not_change"]
    blob = json.dumps(art)
    assert "NOT A COVERAGE NUMBER" in blob
    # the pre-mRNA/genome caveat must survive: the acceptor half here is intronic sequence
    assert "INTRONIC sequence" in blob


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
