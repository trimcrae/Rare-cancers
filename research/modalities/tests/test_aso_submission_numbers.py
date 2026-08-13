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
    ORIENTATION_FILTERED, ORIENTATION_LABELS_STRAND_BLIND, SAVED_HITS_PER_DESIGN,
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


def _clean_set():
    """(junction, sequence) for every design with no hybridisable near-match over a complete list.

    One home for the predicate the paper's headline rests on, so the two tests that need it cannot
    drift apart from each other — which is the same failure this whole file exists to catch.
    """
    out = []
    for s in _filtered_screens():
        for o in _raw(s).get("oligos", []):
            if o.get("status") != "screened":
                continue
            n = o.get("n_offtarget_near_matches")
            if n is None or n > SAVED_HITS_PER_DESIGN:
                continue
            if not [h for h in o.get("offtargets", []) if not h.get("is_minus_strand")]:
                out.append((s["junction_label"], o["antisense_5to3"]))
    return sorted(out)


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
    assert "All 38 were screened with alignment orientation filtered" in txt


def test_the_methods_do_not_still_describe_the_sixteen_junction_corpus():
    """⛔ THE METHODS CONTRADICTED THE RESULTS FOR AS LONG AS THE CORPUS HAD BEEN COMPLETE.

    "Orientation is parsed and filtered in the sixteen screens on which every cleanliness statement
    here rests. The remaining eight are reported as upper bounds, marked in Table 2" — while the
    Results said all 38, the artifacts said all 38, and Table 2 marked nothing. A reader who
    believed the Methods would conclude that two thirds of the corpus carried no claim.

    Nothing here can be phrased as a positive assertion about the current text alone, because the
    failure mode is a stale number surviving beside a correct one. So both directions are asserted:
    the artifact-true count is in the paper, and the superseded framing is not.
    """
    txt = _paper()
    assert "in all 38 junction\nscreens" in txt or "in all 38 junction screens" in txt
    for dead in ("the sixteen screens", "The remaining eight are reported as upper",
                 "25 of the 27", "marked in Table 2"):
        assert dead not in txt, f"superseded Methods phrasing is back: {dead!r}"


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
    # ⚠ THE CENSORING DENOMINATOR IS 47, NOT 44, AND THE PAPER SAID 44 (2026-08-13). 44 is the
    # subset with a computable locus `inflation_factor`, which is the LOCUS claim's denominator in
    # the test below; the number of designs whose hit list is complete enough to be assessed for
    # cleanliness at all is 47. Two nearby quantities, one of them borrowed for the other's
    # sentence — and the smaller one made the paper sound more cautious than its evidence required.
    assert f"Only {uncensored} of those 183" in txt


def test_locus_inflation_matches_the_manuscript():
    import statistics
    names = {s["screen"] for s in _filtered_screens()}
    infl = [o["inflation_factor"] for s in _collapse()["screens"] if s["screen"] in names
            for o in s["per_oligo"] if o.get("inflation_factor") is not None]
    assert len(infl) == 44, len(infl)
    assert round(statistics.median(infl), 2) == 2.20, statistics.median(infl)
    assert max(infl) == 11.0, max(infl)
    txt = _paper()
    assert f"over the {len(infl)} designs of the 38 junction screens" in txt
    assert "inflation of 2.20 transcript records" in txt
    # The collapse artifact's own headline median is 2.14 over 46 oligos, because it includes the
    # two modelled control screens. 2.20 is the figure restricted to the 38 junction screens, which
    # is what the paper is about — so the paper must say which population it means.
    assert "2.14" not in txt


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
    clean = _clean_set()
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
    partner effect. Over all 38 every partner has one, and the effect is gone. The assertion is
    therefore on the per-partner counts rather than on any partner being special.

    ⚠ THIS DOCSTRING SAID "all 37" UNTIL 2026-08-13, the same off-by-one as the paper's "one of five
    at *TFG*" and from the same cause: TFG contributes six frame-compatible junctions, not five.
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
    # ⛔ AND THE DENOMINATORS MUST SUM TO THE CORPUS. The paper read "one of five at *TFG*" while
    # the atlas, Table 1 and Table 2's six TFG rows all say six, so §3.3's five per-partner
    # denominators summed to 37 against a 38-junction corpus. An arithmetic error a reviewer finds
    # by adding a row, in the one paragraph whose whole point is a per-partner comparison.
    atlas = json.load(open(os.path.join(MOD, "nr4a3-fusion-junction-atlas.json")))
    per_partner = {p: len([1 for r in atlas["graded_pairs"]
                           if r["grade"] == "EMITTABLE" and r["donor_symbol"] == p])
                   for p in atlas["partners_scored"]}
    assert sum(per_partner.values()) == 38, per_partner
    words = {"four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}
    # Each clause reads "<n> of <denominator> at [both] *PARTNER*[ and *PARTNER*]", so the
    # denominator and the partners it covers are pulled out of the sentence and checked against the
    # atlas. Parsed rather than string-matched because the sentence groups two partners under one
    # denominator, and a check that could not survive that grouping would have to be dropped.
    seen = {}
    # ⚠ WHITESPACE-TOLERANT: the manuscript hard-wraps, and "at both" sits at the end of a line with
    # its two partners on the next one, so a pattern with literal spaces silently matched neither.
    for word, partners in re.findall(
            r"of (\w+) at\s+(?:both\s+)?((?:\*[A-Z0-9]+\*(?:,?\s+and\s+)?)+)", txt):
        if word not in words:
            continue
        for partner in re.findall(r"\*([A-Z0-9]+)\*", partners):
            seen[partner] = words[word]
    assert seen == per_partner, (
        f"§3.3's per-partner denominators {seen} disagree with the atlas {per_partner}")


def test_the_clean_designs_mostly_fail_conventional_triage():
    """§3.8's sharpest claim, and it moved when the corpus grew from four clean designs to nine.

    The paper had "two of the four ... contain a CpG ... a third sits at 37.5% GC". Over nine, the
    statement is stronger and less comfortable: eight of the nine would be rejected by at least one
    conventional rule. Asserted because a claim that reads as advocacy for the paper's own method is
    exactly the kind that must be re-derived rather than carried forward.
    """
    thermo = json.load(open(os.path.join(MOD, "junction-aso-thermo.json")))
    rules = {}
    for r in thermo["per_design"]:
        rules.setdefault(r["antisense_5to3"], r["design_rules"])
    clean = _clean_set()
    audited = [rules[seq] for _, seq in clean if seq in rules]
    assert len(audited) == 9, len(audited)
    all_pass = [r for r in audited if all(r.values())]
    cpg = [r for r in audited if r["no_cpg"] is False]
    gc = [r for r in audited if r["gc_in_band"] is False]
    assert (len(all_pass), len(cpg), len(gc)) == (1, 7, 4), (len(all_pass), len(cpg), len(gc))
    txt = _paper()
    assert "exactly one satisfies all four rules" in txt
    assert "Seven contain a CpG" in txt
    assert "four fall outside the 40–60% GC window" in txt


def test_the_figure_3_legend_matches_the_series_it_describes():
    """⛔ THE LEGEND AND THE FIGURE DISAGREED, AND THE FIGURE WAS RIGHT.

    The legend said 125 design records collapse to 114 molecules, 77 at or below the chance band and
    37 above, from six multi-seam designs. The artifact says 190 records, 176 molecules, 125 at or
    below, 51 above, nine multi-seam — and the rendered SVG prints the artifact's numbers, because
    the drawing script computes nothing. The legend had read `n_at_or_below_chance_upper` (125) as a
    record count and carried the error down the whole sentence.

    `aso_chance_baseline_figure.py` states the tie-break in its own header: the artifact is the
    arbiter. This test is that rule, enforced.
    """
    fs = json.load(open(os.path.join(MOD, "offtarget-chance-baseline.json")))["figure_series"]
    txt = _paper()
    records = sum(r["n_junctions"] for r in fs["series"])
    assert records == 190, records
    assert f"The {records}" in txt and f"collapse to {fs['n_plotted']} molecules" in txt
    assert f"{fs['n_at_or_below_chance_upper']} of the {fs['n_plotted']} fall at or below" in txt
    assert f"and {fs['n_above_chance_upper']} exceed it" in txt
    spans = {}
    for r in fs["series"]:
        spans[r["n_junctions"]] = spans.get(r["n_junctions"], 0) + 1
    assert spans[3] == 5 and spans[2] == 4, spans
    assert f"nine of the 16-mers" in txt and "five at three seams and four at two" in txt
    for dead in ("114 molecules", "77 of the 114", "five at three seams and one at two"):
        assert dead not in txt, f"superseded Figure 3 legend value is back: {dead!r}"


def test_the_accessibility_range_is_the_one_the_artifacts_produce():
    """"0.160 to 0.707 across the 130 designs ... median 0.476" — 130 and 0.476 had NO home.

    The eval artifacts hold 195 accessibility values (190 at real exon junctions, 176 distinct
    sequences); no subset of them has n=130, and no subset has median 0.476. The range was right and
    both other figures were unproducible, which is the most dangerous shape for a wrong number: two
    thirds of the sentence checks out.
    """
    import statistics
    vals = []
    for name in sorted(os.listdir(MOD)):
        # ⛔ THE PRIMARY CORPUS ONLY, AND THE PATTERN IS THE GUARD. This test failed the moment the
        # deep re-screens landed, because an `in name` exclusion list let five
        # `...-deep500.json` files join the denominator and the count went 190 -> 215 with nothing
        # saying so. A parallel corpus taken at a different search ceiling is a DIFFERENT
        # measurement; it must not silently enlarge a population the manuscript quotes. Primary
        # files end at the junction tag (`...e1n3.json`), so anything carrying a further suffix —
        # a modelled control seam, a deeper re-screen, or whatever is added next — is excluded by
        # construction rather than by being remembered here.
        if not re.fullmatch(r"aso-insilico-evaluation-[a-z0-9]+n3\.json", name):
            continue
        for r in json.load(open(os.path.join(MOD, name))).get("top_designs") or []:
            if r.get("site_accessibility") is not None:
                vals.append(r["site_accessibility"])
    assert len(vals) == 190, len(vals)
    txt = _paper()
    assert f"across all {len(vals)} designs at real exon junctions" in txt
    assert f"(median {statistics.median(vals):.3f})" in txt
    assert f"{min(vals):.3f} to {max(vals):.3f}" in txt
    assert "0.476" not in txt and "130 designs" not in txt


def test_the_censoring_guard_was_tested_and_is_load_bearing():
    """§3.6's deeper re-screen, and the reason the guard is not merely cautious.

    ⛔ THE ALTERNATIVE WAS A FALSE HEADLINE. Relax the censoring restriction — call a design clean
    because its RETAINED hits are all minus-strand — and the count goes from nine designs at six
    junctions to twenty-four at eighteen. Seven records sat exactly there: no hybridisable retained
    hit, and a raw count above the retention depth but below the search's own ceiling, so retention
    alone was withholding the verdict. Re-screened at a tenfold deeper ceiling, six of the seven are
    decided and NONE is clean; one design's 21 near-matches become 196 with 119 hybridisable. The
    caution the paper exercised is what stopped six wrong entries, and this test is that evidence.

    ⚠ The deep artifacts are a SEPARATE measurement under their own suffix. A count taken at a deeper
    ceiling does not correct the shallower one, and nothing in the manuscript is restated from these.
    """
    deep = {}
    for name in sorted(os.listdir(MOD)):
        if name.startswith("junction-aso-offtarget-") and name.endswith("-deep500.json"):
            d = json.load(open(os.path.join(MOD, name)))
            for o in d.get("oligos", []):
                if o.get("status") == "screened":
                    deep[(d["junction_label"], o["antisense_5to3"])] = o
    if not deep:
        pytest.skip("the deep re-screens are not present in this checkout")

    # The population: retained-clean, raw count over the retention depth, under the BLAST ceiling.
    candidates = []
    for s in _filtered_screens():
        for o in _raw(s).get("oligos", []):
            n = o.get("n_offtarget_near_matches")
            if o.get("status") != "screened" or n is None:
                continue
            if SAVED_HITS_PER_DESIGN < n < 50 and not [
                    h for h in o.get("offtargets", []) if not h.get("is_minus_strand")]:
                candidates.append((s["junction_label"], o["antisense_5to3"], n))
    assert len(candidates) == 7, candidates

    decided, still_clean = 0, []
    for lab, seq, shallow_n in candidates:
        o = deep.get((lab, seq))
        if o is None:
            continue                      # its deeper query failed at the remote service
        stored = len(o.get("offtargets") or [])
        n = o.get("n_offtarget_near_matches") or 0
        if stored < n:
            continue                      # still censored even at the deeper depth
        decided += 1
        hyb = [h for h in o.get("offtargets") or [] if not h.get("is_minus_strand")]
        assert n > shallow_n, (
            f"{lab}/{seq}: a deeper ceiling returned {n} against {shallow_n}; a deeper search cannot "
            f"find fewer, so either the screen or this comparison is wrong")
        if not hyb:
            still_clean.append((lab, seq))
    assert decided == 6, decided
    assert not still_clean, (
        f"a censored design turned out clean after all: {still_clean}. That is a RESULT, not a test "
        f"failure — the manuscript says every decided record was not clean, so update §3.6 and the "
        f"clean set rather than relaxing this")
    txt = _paper()
    assert "decided six of\nthe seven" in txt or "decided six of the seven" in txt
    assert "every one of the six is not clean" in txt
