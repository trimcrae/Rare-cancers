"""Tests for `hybrid_intron.py` — the hybrid-intron premise audit.

The load-bearing assertions here are the ones that would have caught this lane's two historical
defects and the one new failure mode the intron introduces:

  * the intron is named in TRANSCRIPT-exon rank and the CODING-rank alias is a different intron
    (the 2026-08-06 off-by-two, in the one place it would recur);
  * a seam's fusion-unique budget is GAP-1 windows and the committed panels agree, so "kilobases"
    is checkable rather than rhetorical;
  * the committed screen's `is_parent()` filter would DROP a perfect wild-type pre-mRNA match,
    which is the intron arm's fatal liability being reported as an intended hit.

Everything runs offline: `TRANSCRIPT_SOURCE=cache` is forced so no test touches the network.
"""
import json
import os

import pytest

import hybrid_intron as hi                                     # noqa: E402
import junction_aso as ja                                      # noqa: E402


# ⛔ NO MODULE-LEVEL `os.environ.setdefault(...)` HERE. `junction_aso.transcript_model` reads
# TRANSCRIPT_SOURCE at CALL time precisely so a test can scope it, and an import-time setdefault
# would leak the value into every other test module in the same pytest process — the cross-module
# env leak that module's own comment records having been bitten by. The fixture scopes it instead.
@pytest.fixture(autouse=True)
def _cache_only(monkeypatch):
    monkeypatch.setenv("TRANSCRIPT_SOURCE", "cache")
    monkeypatch.delenv("HYBRID_INTRON_MODE", raising=False)


def test_the_intron_is_named_in_transcript_rank_and_the_coding_rank_alias_is_a_different_intron():
    """⛔ The 2026-08-06 defect, in the one place it can recur.

    NR4A3 transcript exons 1-2 carry no CDS, so transcript exon 3 IS coding exon 1. An agent that
    reaches for the coding index — as `fusion_breakpoints.gene_model` invites — names NR4A3 intron
    4 while meaning NR4A3 intron 2. The artifact must carry BOTH numbers so the reader can see
    which is in use.
    """
    conv = hi.coordinate_convention()
    assert conv["rank_space"].startswith("TRANSCRIPT")
    n = conv["NR4A3"]
    assert n["acceptor_exon_transcript_rank"] == 3
    assert n["acceptor_exon_coding_rank"] == 1
    assert n["transcript_rank_equals_coding_rank"] is False
    assert "intron 2" in n["intron_named"]
    assert "intron 4" in n["intron_if_coding_rank_were_used_instead"]
    # the 2 nt of NR4A3 5'UTR the fusion transcript retains — the second historical defect
    assert n["acceptor_exon_5utr_nt_the_fusion_retains"] == 2
    assert conv["EWSR1"]["transcript_rank_equals_coding_rank"] is True


def test_a_non_coding_acceptor_exon_is_refused_rather_than_slid_onto_a_neighbour(monkeypatch):
    monkeypatch.setattr(hi, "NR4A3_ACCEPTOR_EXON", 2)
    with pytest.raises(RuntimeError, match="no coding sequence"):
        hi.coordinate_convention()


def test_the_unique_budget_is_gap_minus_one_and_the_committed_panels_agree():
    """The whole 'kilobases vs ~20 nt' claim, reduced to a checkable number."""
    b = hi.unique_budget()
    assert b["predicted"]["unique_windows_of_length_L"] == b["oligo_len"] - 1
    assert b["predicted"]["rnaseh_usable_windows"] == b["gap"] - 1
    obs = b["observed_in_committed_exon_junction_panels"]
    for tag in ("e7n3", "e12n3"):
        if obs[tag] is None:                     # absent reading, not a reading of absence
            continue
        assert obs[tag]["n_candidates"] == b["gap"] - 1


def test_the_budget_raises_if_a_committed_panel_stops_agreeing(tmp_path, monkeypatch):
    """A silent disagreement with the panels would make the head-to-head meaningless."""
    monkeypatch.setattr(hi, "HERE", str(tmp_path))
    (tmp_path / "junction-aso-designs-e7n3.json").write_text(json.dumps(
        {"n_candidates": 99, "n_fusion_specific": 99, "oligo_length": ja.OLIGO_LEN,
         "architecture": "5-6-5"}))
    with pytest.raises(RuntimeError, match="do not carry"):
        hi.unique_budget()


def test_the_screens_parent_filter_would_hide_a_perfect_wildtype_premrna_match():
    """★ The intron arm's fatal liability, measured through the committed screen's own functions.

    `screen_one` counts off-targets over `not is_parent(h)`. A perfect, gap-spanning match to
    wild-type EWSR1 is exactly what an intron-body oligo produces, and `is_parent` drops it — so an
    unmodified run would score that oligo clean. This test asserts the mechanism, not a narrative.
    """
    a = hi.wildtype_identity_audit()["screen_behaviour_measured_not_asserted"]
    assert a["is_parent_on_wildtype_EWSR1_hit"] is True
    assert a["classify_on_the_same_hit"] == "true_cleavage_risk"
    assert a["classify_on_the_same_alignment_if_it_were_NOT_a_parent"] == "true_cleavage_risk"
    assert a["is_parent_filters_it_out_of_the_offtarget_count"] is True


@pytest.mark.committed_artifact
def test_both_committed_junction_panels_still_regenerate_from_the_committed_cache():
    """A head-to-head against a record this code can no longer reproduce would be worthless.

    Marked `committed_artifact`: it asserts agreement between code and two mutable committed files,
    so it fails for a different reason than a code test does.
    """
    r = hybrid_intron_regen = hi.regeneration_check()
    assert hybrid_intron_regen["panels"], "no committed panels found to check against"
    for tag, row in r["panels"].items():
        if row is None:
            continue                                 # absent reading, not a reading of absence
        assert row["designs_identical"] is True, f"{tag} designs drifted"
        assert row["seam_fresh"] == row["seam_committed"], f"{tag} seam drifted"
    assert r["all_reproduce"] is True


def test_regeneration_check_restores_the_environment_it_borrowed(monkeypatch):
    """It sets FUSION_JUNCTION_MODE / exon env vars; leaking them would silently change every
    later call in the same process — the class of bug junction_aso's own env block records."""
    monkeypatch.setenv("FUSION_JUNCTION_MODE", "sentinel")
    monkeypatch.delenv("EWSR1_EXON_END", raising=False)
    hi.regeneration_check()
    assert os.environ["FUSION_JUNCTION_MODE"] == "sentinel"
    assert "EWSR1_EXON_END" not in os.environ


def test_screen_applicability_names_the_assumption_that_survives_and_the_ones_that_do_not():
    rows = hi.screen_applicability()
    assert any(r["holds_for_intron"] for r in rows), "at least one assumption must survive"
    broken = [r for r in rows if not r["holds_for_intron"]]
    assert len(broken) >= 3
    for r in broken:
        assert r["fix"], "a broken assumption must say what would fix it, not just that it broke"


def test_measure_unique_extent_recovers_exactly_L_minus_1_on_a_synthetic_locus():
    """The identity, exercised by the real function on sequence it has never seen.

    Two synthetic 'parent loci'; the hybrid is a prefix of one joined to a suffix of the other. Only
    the windows straddling the join can be absent from both, and there are exactly L-1 of them.
    """
    import random
    rng = random.Random(20260807)
    p1 = "".join(rng.choice("ACGT") for _ in range(4000))
    p2 = "".join(rng.choice("ACGT") for _ in range(4000))
    hybrid = p1[:1500] + p2[2500:]
    L = ja.OLIGO_LEN
    m = hi.measure_unique_extent(hybrid, [p1, p2], oligo_len=L)
    assert m["n_windows_absent_from_both_parent_loci"] == L - 1
    assert m["n_windows_that_are_a_perfect_match_to_a_parent_locus"] == \
        m["n_windows_total"] - (L - 1)


def test_the_intron_boundary_gate_refuses_a_non_gt_ag_read(monkeypatch):
    """A strand or off-by-one error must stop the run, not produce an intron.

    The network is the INPUT here and is stubbed; the gate itself is the code under test.
    """
    monkeypatch.setattr(hi, "_exon_genomic_spans", lambda symbol: {
        "symbol": symbol, "transcript": "ENSTTEST", "chrom": "22", "strand": 1,
        "exons": [{"rank": 1, "start": 100, "end": 199}, {"rank": 2, "start": 400, "end": 499}],
        "_gate": "stub"})
    monkeypatch.setattr(hi, "_region_seq", lambda c, lo, hi_, s: "AC" + "T" * ((hi_ - lo + 1) - 4)
                        + "CA")
    with pytest.raises(RuntimeError, match="GT...AG"):
        hi.fetch_intron("EWSR1", 1)


def test_the_intron_boundary_gate_passes_a_canonical_read(monkeypatch):
    monkeypatch.setattr(hi, "_exon_genomic_spans", lambda symbol: {
        "symbol": symbol, "transcript": "ENSTTEST", "chrom": "22", "strand": 1,
        "exons": [{"rank": 1, "start": 100, "end": 199}, {"rank": 2, "start": 400, "end": 499}],
        "_gate": "stub"})
    monkeypatch.setattr(hi, "_region_seq", lambda c, lo, hi_, s: "GT" + "T" * ((hi_ - lo + 1) - 4)
                        + "AG")
    rec = hi.fetch_intron("EWSR1", 1)
    assert rec["genomic_start"] == 200 and rec["genomic_end"] == 399
    assert rec["length_nt"] == 200
    assert rec["donor_dinucleotide"] == "GT" and rec["acceptor_dinucleotide"] == "AG"


def test_offline_mode_declares_what_it_did_not_measure(tmp_path, monkeypatch):
    """⛔ An artifact that is silent about an unmeasured field reads as a measured zero."""
    monkeypatch.setattr(hi, "OUT", str(tmp_path / "hybrid-intron-model.json"))
    monkeypatch.delenv("HYBRID_INTRON_MODE", raising=False)
    hi.main()
    d = json.loads((tmp_path / "hybrid-intron-model.json").read_text())
    assert d["mode"] == "offline"
    assert d["measured"] is None and d["seam_screens"] is None
    assert d["_what_is_unmeasured"], "offline mode must list what it could not measure"
    assert "UNMEASURED" in d["head_to_head"]["hybrid_intron"]["screen_result"]
    assert "$0" in d["_cost"] and "No network call" in d["_cost"]


def test_the_committed_artifact_matches_a_fresh_offline_run(tmp_path, monkeypatch):
    """The committed model is reproducible from committed inputs alone (timestamps aside)."""
    committed = os.path.join(hi.HERE, "hybrid-intron-model.json")
    if not os.path.exists(committed):
        pytest.skip("hybrid-intron-model.json not committed yet")
    with open(committed) as fh:
        old = json.load(fh)
    if old.get("mode") != "offline":
        pytest.skip("committed artifact is a CI run; the offline reproduction does not apply")
    monkeypatch.setattr(hi, "OUT", str(tmp_path / "m.json"))
    monkeypatch.delenv("HYBRID_INTRON_MODE", raising=False)
    hi.main()
    new = json.loads((tmp_path / "m.json").read_text())

    def _findings(d):
        """Everything except run provenance.

        ⚠ `_transcript_source.requested` records WHICH SOURCE THIS RUN ASKED FOR, and
        `junction_aso.transcript_source_provenance` reads that off an import-time constant. It
        legitimately differs between a run launched with TRANSCRIPT_SOURCE=cache and one left on
        `auto`, and it is provenance rather than a finding. The FINDINGS must not move; that is what
        is asserted. `used_per_gene` — which source actually answered — is checked separately below.
        """
        out = json.loads(json.dumps(d))
        out["coordinate_convention"].pop("_transcript_source", None)
        return out

    a, b = _findings(new), _findings(old)
    for k in ("coordinate_convention", "regeneration_check", "fusion_unique_budget",
              "wildtype_identity_audit", "mechanism_and_confidence_cost",
              "composition_is_not_the_binding_constraint", "screen_applicability", "head_to_head"):
        assert a[k] == b[k], f"{k} drifted from the committed artifact"
    used = old["coordinate_convention"]["_transcript_source"]["used_per_gene"]
    assert set(used.values()) == {"committed_cache"}, (
        "the committed offline artifact must record that both genes came from the committed cache")


def test_no_efficacy_or_clinical_language_in_the_artifact():
    """Medical-integrity guard: a sequence proposal is never a therapeutic claim."""
    committed = os.path.join(hi.HERE, "hybrid-intron-model.json")
    if not os.path.exists(committed):
        pytest.skip("hybrid-intron-model.json not committed yet")
    text = open(committed).read().lower()
    for banned in ("therapeutic window", "well tolerated", "is safe", "cures", "clinically ready",
                   "ready for the clinic"):
        assert banned not in text, f"artifact carries a clinical claim: {banned!r}"
