#!/usr/bin/env python3
"""The transcript→locus collapse, and the censoring guard that stops it lying.

⛔ THE DANGEROUS FAILURE IS THE FLATTERING ONE. Every mistake this module can make — merging two
loci under one fallback key, counting a truncated top-15 sample as if it were the whole hit list —
makes a candidate look CLEANER than it is. Those are the cases asserted first.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import junction_aso_locus_collapse as C  # noqa: E402


def _hit(acc, defn, risk="true_cleavage_risk"):
    return {"acc": acc, "defn": defn, "risk": risk}


def test_transcript_variants_of_one_gene_collapse_to_one_locus():
    hits = [_hit("NM_001001973", "Homo sapiens ATP synthase F1 subunit gamma (ATP5F1C), "
                                 "transcript variant 1, mRNA; nuclear gene"),
            _hit("NM_005174", "Homo sapiens ATP synthase F1 subunit gamma (ATP5F1C), "
                              "transcript variant 2, mRNA"),
            _hit("NM_001320886", "Homo sapiens ATP synthase F1 subunit gamma (ATP5F1C), "
                                 "transcript variant 3, mRNA")]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 3})
    assert out["n_distinct_loci"] == 1
    assert out["inflation_factor"] == 3.0
    assert out["right_censored"] is False


def test_two_different_genes_do_not_collapse():
    hits = [_hit("NM_005174", "Homo sapiens ATP synthase F1 subunit gamma (ATP5F1C), variant 2"),
            _hit("NM_001271022", "Homo sapiens ATR interacting protein (ATRIP), variant 3, mRNA")]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 2})
    assert out["n_distinct_loci"] == 2


def test_a_truncated_hit_list_is_marked_censored_and_publishes_no_inflation_factor():
    """⛔ THE GUARD THIS MODULE EXISTS UNDER. The screens save `ranked[:15]` and report the full
    count separately; 41 of 67 committed oligonucleotides are truncated, one of them from 50. If
    the collapse read the stored list as complete, a 16-mer with 50 near-matches would be published
    as touching one locus — the single most flattering error available here."""
    hits = [_hit(f"NM_{i:06d}", f"Homo sapiens gene {i} (GENE{i}), mRNA") for i in range(15)]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 50})
    assert out["right_censored"] is True
    assert out["inflation_factor"] is None, "a ratio of truncated to truncated bounds nothing"
    assert out["n_distinct_loci_is_a_lower_bound"] is True
    # and the count itself is still reported — a lower bound is information, silence is not
    assert out["n_distinct_loci"] == 15


def test_an_exactly_full_but_uncensored_list_is_not_marked_censored():
    hits = [_hit(f"NM_{i:06d}", f"Homo sapiens gene {i} (GENE{i}), mRNA") for i in range(15)]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 15})
    assert out["right_censored"] is False and out["inflation_factor"] == 1.0


def test_an_unparseable_definition_falls_back_to_the_accession_and_cannot_merge_loci():
    """⚠ THE FALLBACK DIRECTION IS LOAD-BEARING. A shared sentinel would merge every unparseable
    hit into one locus and UNDERCOUNT; falling back to the accession can only over-count."""
    hits = [_hit("NM_000001", "no parenthetical here at all"),
            _hit("NM_000002", "nor here")]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 2})
    assert out["n_distinct_loci"] == 2
    assert out["n_loci_unresolved_to_a_symbol"] == 2


def test_curated_and_predicted_records_are_separated_not_pooled():
    hits = [_hit("XM_017018783", "Homo sapiens DEP domain containing 4 (DEPDC4), mRNA"),
            _hit("XR_007073896", "Homo sapiens uncharacterized LOC105374140 (LOC105374140), ncRNA"),
            _hit("NM_005174", "Homo sapiens ATP synthase F1 subunit gamma (ATP5F1C), variant 2")]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 3})
    assert out["n_transcripts_predicted"] == 2 and out["n_transcripts_curated"] == 1
    assert out["n_loci_seen_only_as_predicted_models"] == 2
    assert out["n_loci_with_a_curated_transcript"] == 1


def test_a_locus_with_one_curated_and_one_predicted_variant_counts_as_curated_not_predicted_only():
    hits = [_hit("XM_017018783", "Homo sapiens DEP domain containing 4 (DEPDC4), mRNA"),
            _hit("NM_017018783", "Homo sapiens DEP domain containing 4 (DEPDC4), variant 1")]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 2})
    assert out["n_distinct_loci"] == 1
    assert out["n_loci_seen_only_as_predicted_models"] == 0


def test_a_locus_is_a_gap_spanning_risk_if_any_of_its_variants_is():
    hits = [_hit("NM_000001", "Homo sapiens thing (AAA), variant 1", risk="gap_disrupted_no_cleavage"),
            _hit("NM_000002", "Homo sapiens thing (AAA), variant 2", risk="true_cleavage_risk")]
    out = C.collapse_oligo({"offtargets": hits, "n_offtarget_near_matches": 2})
    assert out["n_loci_with_a_gap_spanning_hit"] == 1 and out["loci_with_a_gap_spanning_hit"] == ["AAA"]


@pytest.mark.committed_artifact
def test_the_committed_collapse_summarises_only_uncensored_oligos():
    """⛔ ASSERTED AGAINST THE REAL ARTIFACT, NOT A FIXTURE. The headline medians are what the
    manuscript quotes, and the one way they go wrong is by silently including censored rows."""
    path = os.path.join(MOD, "junction-aso-offtarget-locus-collapse.json")
    if not os.path.exists(path):
        pytest.skip("locus-collapse artifact is not present in this checkout")
    d = json.load(open(path))
    every = [o for s in d["screens"] for o in s["per_oligo"]]
    assert len(every) == d["n_oligos"]
    assert d["n_oligos_uncensored"] == sum(1 for o in every if not o["right_censored"])
    assert d["n_oligos_right_censored"] == sum(1 for o in every if o["right_censored"])
    assert d["n_oligos_right_censored"] > 0, (
        "if nothing is censored the guard is untested by the real data — check the screens still "
        "truncate, rather than assuming the collapse is safe")
    clean = [o for o in every if not o["right_censored"]]
    t = d["totals_over_uncensored_oligos_only"]
    assert t["distinct_loci_summed_over_oligos"] == sum(o["n_distinct_loci"] for o in clean)
    assert t["transcript_near_matches"] == sum(o["n_transcript_near_matches_stored"] for o in clean)
    assert all(o["inflation_factor"] is None for o in every if o["right_censored"])


@pytest.mark.committed_artifact
def test_the_lead_candidates_gap_spanning_load_is_the_three_loci_the_manuscript_claims():
    """The manuscript names three loci and "not one curated transcript among them" for
    5′-GGGCATATCATCAAAC-3′. That is a checkable claim about a committed artifact, so it is checked
    here rather than trusted — and it is the sentence a reviewer is most likely to test."""
    path = os.path.join(MOD, "junction-aso-offtarget-locus-collapse.json")
    if not os.path.exists(path):
        pytest.skip("locus-collapse artifact is not present in this checkout")
    d = json.load(open(path))
    rows = [o for s in d["screens"] for o in s["per_oligo"]
            if o["antisense_5to3"] == "GGGCATATCATCAAAC"]
    assert rows, "the lead candidate is absent from every committed screen"
    for o in rows:
        assert o["right_censored"] is False, "the claim would be a lower bound, not a count"
        assert o["n_loci_with_a_gap_spanning_hit"] == 3, o["loci_with_a_gap_spanning_hit"]
        curated_and_gap_spanning = (set(o["loci_with_a_gap_spanning_hit"])
                                    - set(o["loci_seen_only_as_predicted_models"]))
        assert not curated_and_gap_spanning, (
            f"the manuscript says none of the gap-spanning loci is curated, but {sorted(curated_and_gap_spanning)} "
            f"carries a curated transcript. Fix the manuscript, not this test.")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))


def test_every_blast_submission_happens_before_any_poll():
    """⛔ THE SCREEN'S WHOLE COST WAS THIS ORDERING (measured 2026-08-12). Submitting, blocking to
    READY, fetching, then starting the next design made a five-design junction pay five full BLAST
    round-trips back to back: 27.6 min per junction, ~5.5 h for the paper's twelve against a
    six-hour job ceiling. NCBI's URL API continues a search server-side whether or not anyone is
    waiting, so the searches were always parallel and only this client was serialising them.

    Asserted as an ORDERING rather than a duration, because a timing test would be flaky and would
    not say what went wrong. If a future edit reintroduces submit-then-wait inside the loop, the
    first poll moves ahead of the last submit and this fails."""
    import junction_aso_offtarget as M
    order = []
    put, poll, hits, sleep = M.blast_put, M.blast_poll, M.blast_hits, M.time.sleep
    try:
        M.blast_put = lambda seq: (order.append(("put", seq)), f"RID_{seq}")[1]
        M.blast_poll = lambda rid: order.append(("poll", rid))
        M.blast_hits = lambda rid: []
        M.time.sleep = lambda s: None
        designs = [{"target_mRNA_5to3": f"SEQ{i}", "antisense_5to3": f"A{i}",
                    "gc_percent": 50.0, "specificity_margin": 3} for i in range(5)]
        recs = M.screen_all(designs)
    finally:
        M.blast_put, M.blast_poll, M.blast_hits, M.time.sleep = put, poll, hits, sleep
    kinds = [k for k, _ in order]
    assert kinds.count("put") == 5 and kinds.count("poll") == 5 and len(recs) == 5
    assert max(i for i, k in enumerate(kinds) if k == "put") \
        < min(i for i, k in enumerate(kinds) if k == "poll"), (
        "a poll happened before the last submission — the screen is serial again")


def test_one_failed_submission_does_not_lose_the_other_designs():
    """Four transport failures are already on record and they are per-oligo. Batching must not turn
    one of them into a lost junction."""
    import junction_aso_offtarget as M
    put, poll, hits, sleep = M.blast_put, M.blast_poll, M.blast_hits, M.time.sleep
    try:
        def flaky(seq):
            if seq == "SEQ2":
                raise RuntimeError("Remote end closed connection without response")
            return f"RID_{seq}"
        M.blast_put, M.blast_hits, M.time.sleep = flaky, (lambda rid: []), (lambda s: None)
        M.blast_poll = lambda rid: None
        designs = [{"target_mRNA_5to3": f"SEQ{i}", "antisense_5to3": f"A{i}",
                    "gc_percent": 50.0, "specificity_margin": 3} for i in range(5)]
        recs = M.screen_all(designs)
    finally:
        M.blast_put, M.blast_poll, M.blast_hits, M.time.sleep = put, poll, hits, sleep
    assert len(recs) == 5
    assert sum(1 for r in recs if r.get("status") == "screened") == 4
    assert sum(1 for r in recs if r.get("status") == "screen_failed") == 1
