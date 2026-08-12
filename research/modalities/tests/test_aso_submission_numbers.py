#!/usr/bin/env python3
"""Every quantitative claim in the ASO submission manuscript, tied to the artifact that produces it.

⛔ WHY THIS EXISTS. On 2026-08-12 the manuscript's abstract said 42% of apparent gap-spanning risks
were minus-strand and its Results said half; the range was given as 0-89% when one junction sits at
100%; the design count was given as "five at each" of twenty junctions when the corpus holds 75
across sixteen; and the censoring denominator was 108 for a corpus of 75. Every one of those is the
kind of error a reviewer finds by adding a column, and none was caught by a linter, because none is
a false claim in isolation - each is a number that disagrees with another number somewhere else.

⛔⛔ AND THE DEFECT UNDERNEATH THEM WAS NOT ARITHMETIC. `screen_orientation_status` reported a
screen as orientation-parsed whenever any hit carried `hit_frame` - testing that the FIELD EXISTED
rather than that any count had been computed from it. Four screens carry the field on every hit and
were classified before the filter read it, so 83 minus-strand hits were being counted as cleavage
risks inside a corpus the manuscript described as filtered throughout. A populated field is not a
measured one, and the assertions below are on the LABELS for that reason.

These tests read the committed artifacts, never a remembered value. A failure means the manuscript
and its evidence have diverged - fix whichever is wrong, but do not relax the assertion.
"""
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MOD))
PAPER = os.path.join(REPO, "research", "manuscripts", "aso",
                     "fusion-junction-aso-short-communication.md")
COLLAPSE = os.path.join(MOD, "junction-aso-offtarget-locus-collapse.json")
sys.path.insert(0, MOD)

from junction_aso_offtarget import (  # noqa: E402
    ORIENTATION_FILTERED, ORIENTATION_LABELS_STRAND_BLIND,
    screen_counts_are_orientation_filtered, screen_orientation_status)


def _collapse():
    if not os.path.exists(COLLAPSE):
        pytest.skip("locus-collapse artifact is not present in this checkout")
    return json.load(open(COLLAPSE))


def _paper():
    if not os.path.exists(PAPER):
        pytest.skip("submission manuscript is not present in this checkout")
    return open(PAPER, encoding="utf-8").read()


def _screens(orientation=None):
    scr = _collapse()["screens"]
    return [s for s in scr if orientation is None or s["orientation"] == orientation]


def _raw(s):
    return json.load(open(os.path.join(MOD, s["screen"])))


def _filtered_screens():
    return _screens(ORIENTATION_FILTERED)


# ───────────────────────────────────────────────────── the orientation audit itself
def test_a_screen_with_strand_blind_labels_is_not_reported_as_filtered():
    """The regression that motivated this file: field presence is not filtering.

    A screen whose hits carry `hit_frame` but whose labels never consulted it must be demoted, or
    its upper-bound counts render as measurements.
    """
    blind = {"oligos": [{"offtargets": [
        {"acc": "NM_1", "hit_frame": -1, "is_minus_strand": True,
         "risk": "true_cleavage_risk", "gap_mismatches": 0}]}]}
    assert screen_orientation_status(blind) == ORIENTATION_LABELS_STRAND_BLIND
    assert not screen_counts_are_orientation_filtered(blind)

    good = dict(blind)
    good = {"oligos": [{"offtargets": [
        {"acc": "NM_1", "hit_frame": -1, "is_minus_strand": True,
         "risk": "minus_strand_not_hybridisable", "gap_mismatches": 0}]}]}
    assert screen_orientation_status(good) == ORIENTATION_FILTERED
    assert screen_counts_are_orientation_filtered(good)


def test_the_predicate_is_not_a_substring_sniff():
    """`"UNPARSED" not in status` answered True for the strand-blind state. Nothing may do that."""
    assert not screen_counts_are_orientation_filtered(ORIENTATION_LABELS_STRAND_BLIND)
    assert "UNPARSED" not in ORIENTATION_LABELS_STRAND_BLIND
    assert not screen_counts_are_orientation_filtered("some_future_state_nobody_has_written_yet")


def test_no_filtered_screen_still_carries_a_minus_strand_cleavage_risk():
    """The property the whole orientation argument rests on, asserted over the real corpus."""
    for s in _filtered_screens():
        for o in _raw(s).get("oligos", []):
            for h in o.get("offtargets", []):
                if h.get("is_minus_strand") is True:
                    assert h.get("risk") == "minus_strand_not_hybridisable", (
                        f"{s['screen']} / {o['antisense_5to3']}: a minus-strand hit is labelled "
                        f"{h.get('risk')!r} inside a screen reported as orientation-filtered")


# ───────────────────────────────────────────────────────── corpus size claims
def test_manuscript_corpus_counts_match_the_artifact():
    filt = _filtered_screens()
    n_junctions = len(filt)
    n_designs = sum(s["n_oligos"] for s in filt)
    txt = _paper()
    assert n_junctions == 16, n_junctions
    assert n_designs == 75, n_designs
    assert "Sixteen junctions were screened with orientation parsed and filtered" in txt
    assert f"{n_designs} designs across them" in txt
    # every junction with a screen, filtered or not, minus the one that returned nothing
    labelled = [s for s in _collapse()["screens"] if s["junction_label"]]
    with_results = [s for s in labelled if s["n_oligos"]]
    assert len(with_results) == 24, len(with_results)
    assert "Twenty-four\njunctions were screened" in txt or "Twenty-four junctions were screened" in txt


def test_unfiltered_screens_are_disclosed_and_counted():
    unfiltered = [s for s in _collapse()["screens"]
                  if s["junction_label"] and s["n_oligos"]
                  and not screen_counts_are_orientation_filtered(s["orientation"])]
    assert len(unfiltered) == 8, [s["junction_label"] for s in unfiltered]
    blind = [s for s in unfiltered if s["orientation"] == ORIENTATION_LABELS_STRAND_BLIND]
    assert len(blind) == 4, [s["junction_label"] for s in blind]
    txt = _paper()
    assert "eight" in txt.lower()
    assert "four parse it and were classified" in txt


# ─────────────────────────────────────────────────────── the strand arithmetic
def _apparent_gap_spanning(screens):
    """An apparent gap-spanning risk = gap fully covered with zero gap mismatches, either strand.

    This is `classify()`'s own definition of `true_cleavage_risk` with the orientation branch
    removed, i.e. exactly what the count would have been before the filter.
    """
    tot = minus = 0
    per = {}
    for s in screens:
        a = m = 0
        for o in _raw(s).get("oligos", []):
            for h in o.get("offtargets", []):
                if h.get("gap_mismatches") == 0:
                    a += 1
                    m += bool(h.get("is_minus_strand"))
        per[s["junction_label"]] = (a, m)
        tot += a
        minus += m
    return tot, minus, per


def test_minus_strand_fraction_matches_the_manuscript():
    tot, minus, _ = _apparent_gap_spanning(_filtered_screens())
    assert (minus, tot) == (362, 777), (minus, tot)
    pct = round(100 * minus / tot)
    assert pct == 47, pct
    txt = _paper()
    assert f"{pct}% of apparent" in txt, "abstract percentage"
    assert f"({minus} of\n{tot})" in txt or f"({minus} of {tot})" in txt, "results count"


def test_per_junction_range_matches_the_manuscript():
    _, _, per = _apparent_gap_spanning(_filtered_screens())
    props = {k: 100 * m / a for k, (a, m) in per.items() if a}
    lo_k = min(props, key=props.get)
    hi_k = max(props, key=props.get)
    assert lo_k.startswith("TFG_e2"), lo_k
    assert hi_k.startswith("TCF12_e7"), hi_k
    assert round(props[lo_k]) == 4, props[lo_k]
    assert round(props[hi_k]) == 100, props[hi_k]
    txt = _paper()
    assert "from 4% at *TFG* exon 2 to 100% at *TCF12* exon 7" in txt


def test_the_reordering_example_is_exact():
    """EWSR1 e7 vs e13 - the paper's evidence that the filter reorders rather than rescales."""
    _, _, per = _apparent_gap_spanning(_filtered_screens())
    a7, m7 = per["EWSR1_e7__NR4A3_e3"]
    a13, m13 = per["EWSR1_e13__NR4A3_e3"]
    assert (a7, a13) == (55, 57), (a7, a13)
    assert (a7 - m7, a13 - m13) == (6, 53), (a7 - m7, a13 - m13)
    assert "return 55 and 57 apparent gap-spanning hits" in _paper()
    assert "they stand at 6 and 53" in _paper()


# ────────────────────────────────────────────────────────────── censoring
def test_censoring_counts_match_the_manuscript():
    counts = [o.get("n_offtarget_near_matches") for s in _filtered_screens()
              for o in _raw(s).get("oligos", [])
              if o.get("status") == "screened" and o.get("n_offtarget_near_matches") is not None]
    assert len(counts) == 75, len(counts)
    at_cap = sum(1 for c in counts if c >= 50)
    censored = sum(1 for c in counts if c > 15)
    uncensored = sum(1 for c in counts if c <= 15)
    assert (at_cap, censored, uncensored) == (15, 51, 24), (at_cap, censored, uncensored)
    txt = _paper()
    assert "15 of the 75 filtered designs reach that cap" in txt
    assert "a further 36 exceed the 15 hits" in txt
    assert "51 in all carry right-censored counts" in txt
    assert "Only 24 of those 75" in txt


def test_locus_inflation_matches_the_manuscript():
    import statistics
    names = {s["screen"] for s in _filtered_screens()}
    infl = [o["inflation_factor"] for s in _collapse()["screens"] if s["screen"] in names
            for o in s["per_oligo"] if o.get("inflation_factor") is not None]
    assert len(infl) == 24, len(infl)
    assert round(statistics.median(infl), 2) == 2.50, statistics.median(infl)
    assert max(infl) == 7.0, max(infl)
    txt = _paper()
    assert "over the 24 filtered designs whose lists are not" in txt
    assert "inflation of 2.50 transcript records" in txt


# ──────────────────────────────────────────────────────── the headline result
def test_the_four_clean_designs_are_exactly_what_the_artifacts_support():
    """The paper's headline. Clean = zero hybridisable near-matches, over an UNCENSORED list only.

    The censoring restriction is load-bearing: a design whose stored 15 hits are all minus-strand
    says nothing about the 35 it did not store, so it cannot be called clean.
    """
    clean = []
    for s in _filtered_screens():
        for o in _raw(s).get("oligos", []):
            if o.get("status") != "screened":
                continue
            n = o.get("n_offtarget_near_matches")
            if n is None or n > 15:
                continue
            if not [h for h in o.get("offtargets", []) if not h.get("is_minus_strand")]:
                clean.append((s["junction_label"], o["antisense_5to3"]))
    assert len(clean) == 4, clean
    assert {j for j, _ in clean} == {"TCF12_e17__NR4A3_e3", "TCF12_e7__NR4A3_e3",
                                     "TCF12_e9__NR4A3_e3"}, clean
    txt = _paper()
    for _, seq in clean:
        assert seq in txt, f"clean design {seq} is not named in the manuscript"
    assert "four designs at three *TCF12* junctions" in txt


def test_section_3_3_partner_minima_match():
    """Per junction, the minimum over its designs of hybridisable gap-spanning LOCI.

    Read from `n_loci_with_a_gap_spanning_hit`, which is computed before the top-15 truncation and
    is therefore exact. Recounting from the stored hits instead silently answers zero for censored
    designs, which is the flattering direction.
    """
    minima = {}
    for s in _filtered_screens():
        vals = [o.get("n_loci_with_a_gap_spanning_hit") for o in _raw(s).get("oligos", [])
                if o.get("status") == "screened"
                and o.get("n_loci_with_a_gap_spanning_hit") is not None]
        if vals:
            minima[s["junction_label"]] = min(vals)
    tcf12 = {k: v for k, v in minima.items() if k.startswith("TCF12")}
    fet = {k: v for k, v in minima.items()
           if k.split("_")[0] in ("EWSR1", "TAF15", "FUS")}
    tfg = {k: v for k, v in minima.items() if k.startswith("TFG")}
    assert len(tcf12) == 8 and sum(1 for v in tcf12.values() if v == 0) == 3, tcf12
    assert len(fet) == 6 and min(fet.values()) == 1, fet
    assert tfg["TFG_e6__NR4A3_e3"] == 0 and tfg["TFG_e2__NR4A3_e3"] == 1, tfg
    txt = _paper()
    assert "three of the eight *TCF12* junctions" in txt
    assert "six filtered *EWSR1*, *TAF15* and *FUS*" in txt


# ───────────────────────────────────────────────────── no stale value survives
@pytest.mark.parametrize("stale", [
    "539 of", "1,074", "42% of apparent", "0% to 89%", "25 of 108",
    "26 of\n95", "2.25 transcript records", "five designs at each",
    "Twenty junctions were screened",
])
def test_superseded_values_do_not_reappear_in_the_manuscript(stale):
    """Rule 1.2: a corrected number must not be quotable from the live text."""
    assert stale not in _paper(), f"superseded value {stale!r} is back in the manuscript"
