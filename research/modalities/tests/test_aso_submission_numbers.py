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
    assert n_junctions == 38, n_junctions
    assert n_designs == 183, n_designs
    assert "All 38 frame-compatible junctions were screened with orientation parsed and filtered" in txt
    # ⚠ WHITESPACE-TOLERANT: the manuscript hard-wraps, so the phrase can straddle a newline.
    import re as _re
    assert _re.search(rf"{n_designs}\s+designs\s+across\s+them", txt), "design count"
    # every junction with a screen, filtered or not, minus the one that returned nothing
    labelled = [s for s in _collapse()["screens"] if s["junction_label"]]
    with_results = [s for s in labelled if s["n_oligos"]]
    assert len(with_results) == 38, len(with_results)
    assert "All 38 were screened with orientation filtered" in txt


def test_unfiltered_screens_are_disclosed_and_counted():
    unfiltered = [s for s in _collapse()["screens"]
                  if s["junction_label"] and s["n_oligos"]
                  and not screen_counts_are_orientation_filtered(s["orientation"])]
    assert unfiltered == [], [s["junction_label"] for s in unfiltered]
    txt = _paper()
    assert "no junction here carries an unfiltered count" in txt


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
    assert (minus, tot) == (738, 1677), (minus, tot)
    pct = round(100 * minus / tot)
    assert pct == 44, pct
    txt = _paper()
    assert f"{pct}% of\napparent" in txt or f"{pct}% of apparent" in txt, "abstract percentage"
    t = f"{tot:,}"
    assert f"({minus} of\n{t})" in txt or f"({minus} of {t})" in txt, "results count"


def test_per_junction_range_matches_the_manuscript():
    _, _, per = _apparent_gap_spanning(_filtered_screens())
    props = {k: 100 * m / a for k, (a, m) in per.items() if a}
    lo_k = min(props, key=props.get)
    assert lo_k.startswith("TFG_e4"), lo_k
    assert round(props[lo_k]) == 0, props[lo_k]
    # ⚠ ASSERT THE SET AT THE MAXIMUM, NOT `max()`. Two junctions now sit at exactly 100% and
    # `max()` picks between them by dict order, so a test naming one of them would fail the day a
    # third arrived, or worse, silently start describing a different junction. The manuscript names
    # both for the same reason.
    at_max = sorted(k for k, v in props.items() if round(v) == 100)
    assert at_max == ["EWSR1_e1__NR4A3_e3", "TCF12_e7__NR4A3_e3"], at_max
    txt = _paper()
    assert "from 0% at *TFG* exon 4" in txt and "100% at both *EWSR1* exon 1 and" in txt


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
    assert len(counts) == 183, len(counts)
    at_cap = sum(1 for c in counts if c >= 50)
    censored = sum(1 for c in counts if c > 15)
    uncensored = sum(1 for c in counts if c <= 15)
    assert (at_cap, censored, uncensored) == (35, 136, 47), (at_cap, censored, uncensored)
    txt = _paper()
    assert "35 of the 183 filtered designs reach that cap" in txt
    assert "a further 101 exceed the 15 hits" in txt
    assert "136 in all carry right-censored counts" in txt
    assert "Only 44 of those 183" in txt


def test_locus_inflation_matches_the_manuscript():
    import statistics
    names = {s["screen"] for s in _filtered_screens()}
    infl = [o["inflation_factor"] for s in _collapse()["screens"] if s["screen"] in names
            for o in s["per_oligo"] if o.get("inflation_factor") is not None]
    assert len(infl) == 44, len(infl)
    assert round(statistics.median(infl), 2) == 2.20, statistics.median(infl)
    assert max(infl) == 11.0, max(infl)
    txt = _paper()
    assert "over the 44 filtered designs whose lists are not" in txt
    assert "inflation of 2.20 transcript records" in txt


# ──────────────────────────────────────────────────────── the headline result
def test_the_clean_designs_are_exactly_what_the_artifacts_support():
    """The paper's headline. Clean = zero hybridisable near-matches, over an UNCENSORED list only.

    The censoring restriction is load-bearing: a design whose stored 15 hits are all minus-strand
    says nothing about the 35 it did not store, so it cannot be called clean.

    ⚠ WAS FOUR DESIGNS AT THREE *TCF12* JUNCTIONS, over a 16-junction filtered corpus. Screening
    the remaining 22 junctions took it to nine at six, spanning four of the five partners — and
    that dissolved a partner effect the paper had reported. Recorded here because the count moving
    is expected when coverage grows; what must never move silently is the SET.
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
    assert len(clean) == 9, clean
    assert {j for j, _ in clean} == {
        "EWSR1_e1__NR4A3_e3", "FUS_e8__NR4A3_e3", "TAF15_e1__NR4A3_e3",
        "TCF12_e17__NR4A3_e3", "TCF12_e7__NR4A3_e3", "TCF12_e9__NR4A3_e3"}, clean
    txt = _paper()
    for _, seq in clean:
        assert seq in txt, f"clean design {seq} is not named in the manuscript"
    assert "nine designs at six junctions" in txt


def test_section_3_3_partner_minima_match():
    """Per junction, the minimum over its designs of hybridisable gap-spanning LOCI.

    Read from `n_loci_with_a_gap_spanning_hit`, which is computed before the top-15 truncation and
    is therefore exact. Recounting from the stored hits instead silently answers zero for censored
    designs, which is the flattering direction.

    ⛔ THIS TEST GUARDS A CLAIM THAT WAS ONCE FALSE FOR WANT OF COVERAGE. Over 16 filtered
    junctions the zero-minimum junctions were all *TCF12*, and the paper reported specificity as a
    partner effect. Over all 37 every partner has one, and the effect is gone. The assertion is
    therefore on the per-partner counts rather than on any partner being special.
    """
    minima = {}
    for s in _filtered_screens():
        vals = [o.get("n_loci_with_a_gap_spanning_hit") for o in _raw(s).get("oligos", [])
                if o.get("status") == "screened"
                and o.get("n_loci_with_a_gap_spanning_hit") is not None]
        if vals:
            minima[s["junction_label"]] = min(vals)
    by_partner = {}
    for k, v in minima.items():
        by_partner.setdefault(k.split("_")[0], []).append(v)
    zeros = {p: sum(1 for x in v if x == 0) for p, v in by_partner.items()}
    assert zeros == {"EWSR1": 2, "FUS": 3, "TAF15": 1, "TCF12": 3, "TFG": 1}, zeros
    assert all(n > 0 for n in zeros.values()), (
        "a partner with no zero-minimum junction would restore the partner effect this paper "
        "explicitly withdrew; re-derive the prose rather than relaxing this")
    txt = _paper()
    assert "Specificity does not sort by partner" in txt
    assert "three of eight at both" in txt
