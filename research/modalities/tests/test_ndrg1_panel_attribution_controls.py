#!/usr/bin/env python3
"""THE TWO CONTROLS IN `ndrg1_panel_attribution.py` ARE LOAD-BEARING, NOT DECORATIVE (AUT-PROP-048).

⛔⛔ THIS FILE EXISTS BECAUSE BOTH CONTROLS CHANGE THE ANSWER, AND A READER WHO DOES NOT KNOW THAT
WILL READ THE ARTIFACT AS A WEAKER RESULT THAN IT IS — OR A STRONGER ONE.

  * WITHOUT LEAVE-ONE-OUT the comparison is NDRG1 against a mean that CONTAINS NDRG1. It returns a
    large positive number for a panel of any composition, so it cannot discriminate between the two
    hypotheses at all — it is not a weak measurement, it is not a measurement.
  * WITHOUT THE SIZE-MATCHED NULL the smaller series (n=16) reads as a clean replication. It is not:
    a RANDOM panel of the same size already reaches rho ≈ +0.25 to +0.42 there, because on a
    single-channel array every gene carries a shared array-level component and 16 samples across
    three classes is dominated by between-class structure. The null is the entire reason the
    committed verdict says ONE series and not two.

★ EACH TEST BELOW MUTATES THE CONTROL AND ASSERTS THE ANSWER MOVES. A guard that still passes with
its mechanism removed is guarding nothing (`paper-hardening` records seven one-of-a-pair defects
found exactly this way). ⚠ Every mutation is applied to LOCAL COPIES of the inputs — never to the
module and never to the committed artifact — which is research-loop §3's measured rule.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MODALITIES = os.path.dirname(HERE)
sys.path.insert(0, MODALITIES)

import ndrg1_panel_attribution as N  # noqa: E402

BIG = "GSE24369_series_matrix.txt.gz"      # 35 samples — the series that separates
SMALL = "GSE4303-GPL3290_series_matrix.txt.gz"  # 16 samples — the one that cannot


@pytest.fixture(scope="module")
def committed():
    with open(N.OUT, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def src():
    with open(N.PANELS, encoding="utf-8") as fh:
        return json.load(fh)


def _cache(src, matrix):
    gr = src["gene_reads"]
    return {g: N.sample_z(gr, g, matrix) for g in gr}


# ------------------------------------------------------------------ the artifact is what it says
def test_the_committed_artifact_rederives_from_its_generator():
    """⛔ The seeded null makes this checkable at all. An unseeded one would fail here for a reason
    that is not a defect, which is why SEED is part of the module rather than a run-time choice."""
    assert N.main(["--check"]) == 0, (
        "ndrg1-panel-attribution.json does not re-derive. Regenerate it and commit the result.")


def test_the_verdict_reports_one_series_not_two(committed):
    """★ THE HONEST WEIGHT, PINNED. If a future change makes this read two series, that is either a
    real improvement (more per-sample genes, a better null) or the null being weakened — and the
    difference must be argued in a commit message, not discovered in a manuscript."""
    assert committed["series"][BIG]["separates_hypoxia_from_pparg"] is True
    assert committed["series"][SMALL]["separates_hypoxia_from_pparg"] is False
    assert committed["verdict"]["separating_series"] == [BIG]


# ------------------------------------------------------------------ control 1: leave-one-out
def test_including_the_subject_in_its_own_panels_manufactures_the_correlation(src, committed):
    """⛔⛔ THE MUTATION. Put NDRG1 back into the hypoxia panels it belongs to and the correlation
    jumps, because the panel mean now contains the variable it is being correlated against.

    ★ THE ASSERTION IS THE GAP, NOT THE MUTANT'S VALUE. A mutant that merely differed could differ
    by noise; a mutant that rises materially on every panel containing the subject is the signature
    of self-correlation.
    """
    cache = _cache(src, BIG)
    subject = cache[N.SUBJECT]
    gsms = sorted(subject)
    sig = src["signature_scores"]

    inflated = []
    for panel, row in committed["series"][BIG]["panels"].items():
        if not row.get("scored") or row["family"] != "hypoxia":
            continue
        readable = (sig[panel]["per_platform"][BIG].get("genes_readable") or [])
        if N.SUBJECT not in readable:
            continue                      # this set does not contain the subject; nothing to mutate
        members = [g for g in readable if cache.get(g)]        # ⛔ subject NOT removed — the mutation
        mutant, _n = N.panel_rho(members, subject, gsms, cache)
        inflated.append((panel, row["rho"], mutant))

    assert inflated, (
        "no scored hypoxia panel on this platform contains NDRG1, so this mutation exercised "
        "nothing and the leave-one-out has not been shown to matter here")
    for panel, honest, mutant in inflated:
        assert mutant > honest, (
            f"{panel}: including the subject did not raise rho ({mutant:+.3f} vs {honest:+.3f}). "
            "Either the exclusion is not doing what this module claims, or panel_rho is not "
            "reading the members it is given.")


def test_every_scored_panel_counts_its_members_after_the_exclusion(src, committed):
    """The bookkeeping half. `n_panel_members` must be the count the score actually used, so a
    reader can see how thin a panel is without re-deriving it."""
    sig = src["signature_scores"]
    for matrix, s in committed["series"].items():
        if not s.get("subject_readable"):
            continue
        cache = _cache(src, matrix)
        for panel, row in s["panels"].items():
            if not row.get("scored"):
                continue
            readable = [g for g in (sig[panel]["per_platform"][matrix].get("genes_readable") or [])
                        if g != N.SUBJECT]
            assert row["n_panel_readable"] == len(readable)
            assert row["n_panel_members"] == len([g for g in readable if cache.get(g)])
            assert row["n_panel_members"] <= row["n_panel_readable"]


# ------------------------------------------------------------------ control 2: the size-matched null
def test_the_smaller_series_null_is_high_enough_to_swallow_the_raw_correlations(committed):
    """⛔⛔ THE FINDING THE NULL EXISTS FOR, ASSERTED RATHER THAN DESCRIBED. In the 16-sample series
    a random size-matched panel reaches a substantial positive rho on its own. Any reading of that
    series' raw correlations is reading the array, not the biology."""
    small = committed["series"][SMALL]
    lo, hi = small["null_median_range"]
    assert lo > 0.15, (
        f"the small series' random-panel null median has fallen to {lo:+.3f}. If that is real the "
        "series may now be usable — but it must be argued, because this module's verdict rests on "
        "that null being large.")
    big_lo, big_hi = committed["series"][BIG]["null_median_range"]
    assert abs(big_hi) < 0.1 and abs(big_lo) < 0.1, (
        f"the LARGER series' null is no longer centred near zero ({big_lo:+.3f}..{big_hi:+.3f}), so "
        "its separation may be array structure too")


def test_no_single_raw_rho_threshold_reproduces_the_committed_verdict(committed):
    """⛔⛔ THE MUTATION FOR CONTROL 2, AND THE FIRST VERSION OF THIS TEST ASSERTED SOMETHING FALSE.

    ⚠ It claimed a naive raw-rho rule would flip the SMALL series to 'separating'. It does not — it
    calls that series non-separating too, for the wrong reason (three PPARγ panels are also high
    there). Writing the assertion the tempting way and running it is what caught that, which is the
    argument for mutations being executed rather than reasoned about.

    ★ THE TRUE STATEMENT IS STRONGER AND IS WHAT IS ASSERTED NOW: **no single global rho threshold
    reproduces the committed verdict on both series.** In the large series a threshold does exist —
    every hypoxia panel sits above every PPARγ panel — so a naive rule happens to agree there. In
    the small series the PPARγ maximum EXCEEDS the hypoxia minimum, so no threshold can separate
    them at all, and a rule that reported the large series correctly would be doing so by luck of
    where the constant landed. A per-panel, size-matched null needs no constant and answers both.
    """
    spans = {}
    for matrix, s in committed["series"].items():
        if not s.get("subject_readable"):
            continue
        scored = [r for r in s["panels"].values() if r.get("scored")]
        hyp = [r["rho"] for r in scored if r["family"] == "hypoxia"]
        ppg = [r["rho"] for r in scored if r["family"] == "pparg"]
        assert hyp and ppg, f"{matrix} scored one family only, so this proves nothing"
        spans[matrix] = (min(hyp), max(ppg))

    separable = {m for m, (h_lo, p_hi) in spans.items() if h_lo > p_hi}
    assert BIG in separable, (
        f"the large series' families now overlap on raw rho {spans[BIG]}, so the claim that a "
        "threshold agrees there is stale")
    assert SMALL not in separable, (
        f"a raw-rho threshold now separates the SMALL series {spans[SMALL]}. That would make this "
        "test's premise stale — re-derive it rather than deleting it, because the committed verdict "
        "says that series cannot discriminate and the two must not disagree silently.")
    assert separable != set(spans), (
        "a single threshold would now reproduce the verdict on every series, so the null is no "
        "longer earning its place and that should be argued explicitly")


def test_a_panel_that_clears_on_the_pparg_side_makes_the_verdict_false(src):
    """★ THE VERDICT IS A JOINT STATEMENT AND MUST FAIL CLOSED. One PPARγ panel clearing its null
    makes 'separates' false however strong the hypoxia side is — otherwise a result where BOTH
    programmes track the subject would be reported as a hypoxia finding."""
    doc = N.build(n_draws=200)
    for matrix, s in doc["series"].items():
        if not s.get("subject_readable"):
            continue
        if s["n_pparg_above_null_p95"] > 0:
            assert s["separates_hypoxia_from_pparg"] is False, (
                f"{matrix}: a PPARγ panel cleared its null and the verdict still says the "
                "programmes separate")
