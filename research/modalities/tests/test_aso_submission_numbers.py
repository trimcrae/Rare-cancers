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
                     "fusion-junction-aso-research-article.md")
# ⭐ THE SUBMISSION'S SUPPLEMENTARY INFORMATION, ADDED 2026-08-16. The editorial restructure moved
# apparatus — not claims — out of the main text and into this companion file, which ships with the
# submission. RELOCATION IS NOT LOSS, but it is only not-loss while something still asserts the fact
# where it landed, so the guards below read the SI directly rather than dropping what moved.
SUPPLEMENT = os.path.join(REPO, "research", "manuscripts", "aso",
                          "fusion-junction-aso-supplementary-information.md")
COLLAPSE = os.path.join(MOD, "junction-aso-offtarget-locus-collapse.json")
sys.path.insert(0, MOD)

import aso_screen_sets as ass  # noqa: E402
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


def _supplement():
    if not os.path.exists(SUPPLEMENT):
        pytest.skip("the supplementary information is not present in this checkout")
    return open(SUPPLEMENT, encoding="utf-8").read()


# ⚠ ONE TABLE FOR THE SPELT-OUT COUNTS THE PROSE USES. Several guards below derive a count from an
# artifact and then have to find it in a sentence that spells it, and the manuscript's own house
# style spells a number that opens a sentence and prints a numeral that does not — so a guard has to
# accept whichever form the sentence happens to need. Kept in one place so a count that grows past a
# guard's private little dict fails with a KeyError naming the number rather than passing on a
# `.get()` that quietly returned None.
_NUMBER_WORDS = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
                 7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve",
                 13: "thirteen", 14: "fourteen", 15: "fifteen"}


def _spelt(n):
    """`n` as the manuscript may spell it, capitalised or not — KeyError if nobody has spelt it."""
    return _NUMBER_WORDS[n]


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
    assert (f"parsed and filtered in all {n_junctions} junction screens and the {n_designs} "
            "designs they hold") in _flat(txt)
    # ⚠ WHITESPACE-TOLERANT: the manuscript hard-wraps, so the phrase can straddle a newline.
    import re as _re
    assert _re.search(rf"covering\s+{n_designs}\s+designs", txt), "design count"
    # every junction with a screen, filtered or not, minus the one that returned nothing
    labelled = [s for s in _collapse()["screens"] if s["junction_label"]]
    with_results = [s for s in labelled if s["n_oligos"]]
    assert len(with_results) == 38, len(with_results)
    assert "All 38 in-frame junctions were screened with orientation filtered" in txt


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
    # ⚠ THE DEAD-PHRASE CHECKS ARE FLATTENED, 2026-08-16. They were run against the RAW text, which
    # is the unsafe direction for an ABSENCE: a superseded sentence returning across a line break
    # would have passed a raw `not in` silently. Verified clean against the flattened text when the
    # change was made, so this tightens the guard rather than moving it.
    txt = _flat(_paper())
    assert "in all 38 junction screens" in txt
    for dead in ("the sixteen screens", "The remaining eight are reported as upper",
                 "25 of the 27", "marked in Table 2"):
        assert dead not in txt, f"superseded Methods phrasing is back: {dead!r}"


def test_unfiltered_screens_are_disclosed_and_counted():
    unfiltered = [s for s in _collapse()["screens"]
                  if s["junction_label"] and s["n_oligos"]
                  and not screen_counts_are_orientation_filtered(s["orientation"])]
    assert unfiltered == [], [s["junction_label"] for s in unfiltered]
    # ⭐ RELOCATED AND SHARPENED, NOT LOST — the editorial restructure of 2026-08-16. This guard
    # pinned the Results sentence "All 38 in-frame junctions are screened with the orientation filter
    # applied, so no junction here carries an unfiltered count". That disclosure now sits in the
    # Methods' strand-orientation paragraph and states the same fact from the other side, naming the
    # exceptions instead of denying them: "Only two released screens are unfiltered, and neither
    # carries a junction or supports a claim here (SI §S5)". Read with the sibling assertion in
    # `test_manuscript_corpus_counts_match_the_artifact` ("parsed and filtered in all 38 junction
    # screens and the 183 designs they hold") it is strictly more than the old wording said.
    # ⚠ DERIVED FROM THE ARTIFACT, NOT TYPED: the count of unfiltered releases and the fact that none
    # of them carries a junction label are both read off the collapse file, so a third unfiltered
    # screen — or an unfiltered screen that acquired a junction — fails on the sentence.
    releases = [s for s in _collapse()["screens"]
                if not screen_counts_are_orientation_filtered(s["orientation"])]
    assert all(s["junction_label"] is None for s in releases), [s["screen"] for s in releases]
    txt = _flat(_paper())
    # ⚠ THE NOUN IS FLEXIBLE, THE FACTS ARE NOT (re-anchored 2026-08-17). A cold reader found the
    # bare "carries no junction" ambiguous, because these two ARE modelled control junctions — what
    # they carry no junction FROM is the 38-junction panel. The SI was clarified and this pin blocked
    # the same clarification in section 6, so the pin now accepts either phrasing while still
    # requiring the derived count, the no-junction fact and the no-claim fact in ONE sentence.
    assert re.search(
        rf"Only {_spelt(len(releases))} released screens are unfiltered, and neither carries a "
        rf"junction(?: from the 38-junction panel)? or supports a claim here", txt), (
        [s["screen"] for s in releases])


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
    assert f"{minus} sit on the minus strand, or {pct}%" in _flat(txt), "minus-strand percentage"
    t = f"{tot:,}"
    assert f"Of the {t} apparent cleavage risks" in _flat(txt), "results count"


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
    assert "return 55 and 57 apparent gap-spanning hits" in _flat(_paper())
    assert "they stand at 6 and 53" in _flat(_paper())


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
    txt = _flat(_paper())
    # ⭐ REWORDED, NOT LOST — the editorial restructure of 2026-08-16. §3.6's three sentences ("The
    # alignment screen returns at most 50 hits per query, and 35 of the 183 filtered designs reach
    # that cap. A further 101 exceed the 15 hits retained per design, so 136 in all carry
    # right-censored counts") are one clause in §5: "so 136 of the 183 filtered designs carry
    # right-censored counts: 35 at the cap, 101 more past the 15 hits retained". The same three
    # counts against the same denominator, in the same order. ⚠ EVERY NUMBER IS DERIVED FROM THE
    # ARTIFACT AND ONLY THEN MATCHED AGAINST THE PROSE, including the 101, which is now a
    # subtraction in the sentence and so must be one here too — typing it would let the three
    # published figures stop summing without anything failing.
    assert (f"{censored} of the {len(counts)} filtered designs carry right-censored counts: "
            f"{at_cap} at the cap, {censored - at_cap} more past the 15 hits retained") in txt
    # ⚠ THE CENSORING DENOMINATOR IS 47, NOT 44, AND THE PAPER SAID 44 (2026-08-13). 44 is the
    # subset with a computable locus `inflation_factor`, which is the LOCUS claim's denominator in
    # the test below; the number of designs whose hit list is complete enough to be assessed for
    # cleanliness at all is 47. Two nearby quantities, one of them borrowed for the other's
    # sentence — and the smaller one made the paper sound more cautious than its evidence required.
    # ⚠ "those" ADMITTED 2026-08-17. A3-F3's restoration introduces the same 47 one sentence
    # earlier, so the bare "Only 47 …" became a second introduction of a number that now has an
    # antecedent — the one-fact-one-place rule reaching into grammar. The count is still asserted
    # from the artifact; only the article in front of it is optional.
    assert (f"Only {uncensored} of the {len(counts)} hit lists are short enough to assess" in txt
            or f"Only those {uncensored} of the {len(counts)} hit lists are short enough to assess"
            in txt)


def test_locus_inflation_matches_the_manuscript():
    import statistics
    names = {s["screen"] for s in _filtered_screens()}
    infl = [o["inflation_factor"] for s in _collapse()["screens"] if s["screen"] in names
            for o in s["per_oligo"] if o.get("inflation_factor") is not None]
    assert len(infl) == 44, len(infl)
    assert round(statistics.median(infl), 2) == 2.25, statistics.median(infl)
    assert max(infl) == 11.0, max(infl)
    # ⚠ WHITESPACE-TOLERANT FROM 2026-08-16: the manuscript hard-wraps and the population qualifier
    # now straddles a line break, so a raw-text match silently found neither half.
    txt = _flat(_paper())
    # ⛔ THE POPULATION QUALIFIER WAS DROPPED BY THE EDITORIAL PASS AND RESTORED RATHER THAN
    # UNPINNED (2026-08-16). The compressed sentence read "over the 44 designs whose hit lists permit
    # a locus recount", which names the predicate but not the corpus — and the corpus is the whole
    # point, for the reason recorded below: the artifact's own headline median is 2.25 as well, over
    # 49 uncensored oligos that include two modelled control screens. Without "of the 38 junction
    # screens" the paper's 44 and the artifact's 49 read as one predicate over one corpus returning
    # two different sizes. The prose was put back.
    assert f"over the {len(infl)} designs of the 38 junction screens" in txt
    # ⭐ "2.25 transcript records per locus" is now "2.25 records per locus", under a paragraph head
    # that defines the unit ("Records are not genes"), and the maximum travels in the same clause —
    # so both are derived from the artifact here rather than only the median.
    assert (f"the median inflation is {statistics.median(infl):.2f} records per locus and the "
            f"maximum {max(infl):.1f}") in txt
    # ⚠ SUPERSEDED, RETAINED: 2.20 over these same 44 designs, and 2.14 as the artifact's headline.
    # Both were computed with a `locus_of` that split the definition on its FIRST comma, which lost
    # the symbol for every gene whose DESCRIPTION contains one — `germ cell-less 1, spermatogenesis
    # associated (GMCL1)` degraded to nine accession fallbacks, so one locus counted as nine. The
    # fix resolved 888 of 25,893 hits repo-wide and corrected 7 mis-symbolled ones, RAISING the
    # inflation factor because loci merged: 188 distinct loci became 174 over the same hit lists.
    # The population did not change; only the locus assignment did.
    assert "2.20" not in txt
    # The artifact's headline median and this 44-design figure now coincide at 2.25, which they did
    # not before (2.14 vs 2.20). That is arithmetic coincidence, not one number: the headline is
    # over 49 uncensored oligos INCLUDING two modelled control screens, this is over the 38 junction
    # screens. Keep the populations named in the prose so the coincidence cannot be read as identity.
    assert "of the 38 junction screens" in txt


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
    assert "three of eight at both" in _flat(txt)
    # ⛔ AND THE DENOMINATORS MUST SUM TO THE CORPUS. The paper read "one of five at *TFG*" while
    # the atlas, Table 1 and the per-junction specificity table's six TFG rows all say six, so §3.3's five per-partner
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
            r"of (\w+) at\s+(?:both\s+)?((?:\*[A-Z0-9]+\*(?:,?\s+and\s+)?)+)", _flat(txt)):
        if word not in words:
            continue
        for partner in re.findall(r"\*([A-Z0-9]+)\*", partners):
            seen[partner] = words[word]
    assert seen == per_partner, (
        f"§3.3's per-partner denominators {seen} disagree with the atlas {per_partner}")


def _deep_screens():
    """Every deep re-screen as (junction, design) -> record. Keyed by the PAIR, never the sequence:
    nine designs span three seams at once and a sequence key silently keeps the last one read."""
    # ⛔ MEASURED DEPTH AT ONE MEASURED GEOMETRY, NOT A `*deep500*` GLOB (2026-08-14). That pattern
    # admitted all twelve 18-mer and 20-mer screens into a dict this file pins manuscript numbers
    # off. ⚠ It moved no number, because this dict is keyed by (junction, SEQUENCE) and a longer
    # geometry's designs are different sequences, so the contaminants matched no lookup — the lucky
    # outcome, not a defence, and the same coincidence `test_aso_parent_gap_pairing` records.
    out = {}
    for s_ in ass.load_screens(ass.MANUSCRIPT_GEOMETRY, ass.BLAST_SCREEN, root=MOD,
                               select=ass.is_deep, allow_empty=True):
        d = s_.artifact
        for o in d.get("oligos", []):
            if o.get("status") == "screened" and o.get("n_offtarget_near_matches") is not None:
                out.setdefault((d["junction_label"], o["antisense_5to3"]), o)
    return out


def _flat(txt):
    return re.sub(r"\s+", " ", txt)



def _collapse_censored():
    """(junction, antisense) -> right_censored, from the collapse artifact.

    Separate from the count map above because `right_censored` is the pipeline's OWN judgement that
    a hit list is complete — which is exactly the claim the worked examples test.
    """
    return {(s["junction_label"], o["antisense_5to3"]): o["right_censored"]
            for s in _collapse()["screens"] if s["junction_label"] for o in s["per_oligo"]}


def test_the_deeper_ceiling_raises_counts_across_the_whole_corpus():
    """§3.6's censoring bound, over every design screened at both ceilings.

    ⚠ SUPERSEDED, RETAINED: "23 designs ... 20 of the 23", and in Limitations "141 of 157 comparable
    designs return a higher count and 125 of those had not reached the 50-hit cap". Neither
    population is reproducible from the committed artifacts under any natural definition — the
    corpus is 183 filtered design records, 180 of which also have a deep record — so both were
    computed against a deep corpus that has since grown. The three worked examples in that sentence
    were correct and are kept.
    """
    deep = _deep_screens()
    if not deep:
        pytest.skip("the deep re-screens are not present in this checkout")
    default = {(s["junction_label"], o["antisense_5to3"]): o["n_transcript_near_matches_reported"]
               for s in _collapse()["screens"] if s["junction_label"] for o in s["per_oligo"]}
    assert len(default) == 183, len(default)
    comparable = [k for k in default if k in deep]
    higher = [k for k in comparable
              if deep[k]["n_offtarget_near_matches"] > default[k]]
    not_at_cap = [k for k in higher if default[k] < 50]
    assert (len(comparable), len(higher), len(not_at_cap)) == (180, 164, 129), (
        len(comparable), len(higher), len(not_at_cap))
    txt = _flat(_paper())
    # ⭐ REWORDED, NOT LOST — the editorial restructure of 2026-08-16. "raised the count of 164 of the
    # 180 designs screened at both depths, and 129 of those had not approached the 50-hit cap" is now
    # "raised the count for 164 of the 180 designs screened at both depths, 129 of which had never
    # approached the cap", in a sentence whose own preceding clause establishes that the cap is 50
    # hits. Same two populations, same denominator, same conclusion drawn from them.
    assert f"raised the count for {len(higher)} of the {len(comparable)} designs screened at both " \
           f"depths, {len(not_at_cap)} of which had never approached the cap" in txt
    # ⛔ AND THE CAP MUST STILL BE NAMED, or "the cap" in the sentence above bounds nothing.
    assert "stores at most 50 hits per query" in txt
    for dead in ("23 designs at a tenfold deeper ceiling", "141 of 157 comparable designs"):
        assert dead not in txt, f"superseded censoring population is back: {dead!r}"

    # ⛔ THE WORKED EXAMPLES, RESTORED 2026-08-17 AND NOW GUARDED (round-7 A3-F3).
    # The docstring above has said "The three worked examples in that sentence were correct and are
    # kept" since the restructure — and it was FALSE: commit 1076707f4 deleted them, and nothing
    # here noticed, because the guard asserted the two POPULATIONS and never the demonstration
    # those populations exist to support. A claim in a test's own docstring is not a check.
    # ⭐ THEY ARE THE ONLY PLACE THE PAPER SHOWS, AT THE LEVEL OF ONE DESIGN, THAT REACHING THE CAP
    # IS NOT WHAT CENSORS A COUNT: a list the pipeline marks UNCENSORED still grew ~14-fold. Every
    # value below is re-derived from the artifacts, never typed, so a corpus change fails the gate
    # instead of quietly falsifying the sentence.
    uncensored = [k for k in comparable if not _collapse_censored()[k]]
    rose = [k for k in uncensored if deep[k]["n_offtarget_near_matches"] > default[k]]
    fell = [k for k in uncensored if deep[k]["n_offtarget_near_matches"] < default[k]]
    assert not fell, f"a deeper ceiling returned FEWER hits, which the sentence says never happens: {fell}"
    assert f"of the {len(uncensored)} designs whose" in txt, (
        f"the untruncated population ({len(uncensored)}) is no longer stated")
    assert f"{len(rose)} returned more at the deeper ceiling and none" in txt, (
        f"the {len(rose)}-rose/0-fell result is no longer stated")
    # the four worked examples, each (default -> deep) read from the artifacts
    by_default = {}
    for k in uncensored:
        by_default.setdefault(default[k], []).append(deep[k]["n_offtarget_near_matches"])
    for reported, shown in ((9, 34), (10, 110), (15, 204), (15, 374)):
        assert shown in by_default.get(reported, []), (
            f"no design reporting {reported} returns {shown} at depth any more; the manuscript's "
            f"worked example is stale. Available: {sorted(by_default.get(reported, []))}")
        assert f"returned {shown}" in txt or f"returning {shown}" in txt, (
            f"the worked example {reported} -> {shown} has left the manuscript")


def test_the_released_screen_and_graded_counts_are_the_ones_on_disk():
    """The Methods' inventory of what is released, which grew silently under a fixed number.

    ⚠ SUPERSEDED, RETAINED: "39 of the 45 screens released in total … and the five deeper
    re-screens of §3.6". 45 was the corpus when only five junctions had been re-screened at depth.
    ⚠ SUPERSEDED, RETAINED: 78 total and 38 deep, which was the corpus before the gap-length work of
    §3.10 released 15 further deep screens at 5-8-5 and 5-10-5 (7 and 8). The total is 93 and the
    ungraded set is 53 deep re-screens plus the one coverage-only control.

    ⛔ THE GRADED COUNT HAS NEVER MOVED, WHICH IS THE WHOLE HAZARD HERE. 39 was right at 45, at 78
    and at 93, so the sentence keeps reading as current while its denominator drifts underneath it.
    Only the total is load-bearing, and it is asserted against the disk rather than remembered.
    """
    # ⚠ THE RELEASE INVENTORY IS EVERY GEOMETRY ON PURPOSE — it is what the deposit ships — so it
    # unions the loader's per-geometry mapping HERE, visibly, rather than reaching for a glob that
    # happens to return the same set today and would silently return a different one tomorrow.
    screens = [s.path for _g, ss in ass.iter_geometries(ass.BLAST_SCREEN, root=MOD) for s in ss]
    graded = {s.name.replace("-graded.json", ".json")
              for _g, ss in ass.iter_geometries(ass.GRADED_RESCORE, root=MOD) for s in ss}
    ungraded = [p for p in screens if os.path.basename(p) not in graded]
    deep = [p for p in ungraded if "deep500" in p]
    assert (len(screens), len(graded)) == (93, 39), (len(screens), len(graded))
    assert len(deep) == 53 and len(ungraded) - len(deep) == 1, (len(deep), len(ungraded))
    txt = _flat(_paper())
    assert (f"all 38 junction screens, and {len(graded)} of the {len(screens)} screens released in "
            f"total") in txt
    # ⭐ THE UNGRADED BREAKDOWN MOVED TO SI §S4, 2026-08-16, AND THIS GUARD FOLLOWED IT. The main text
    # keeps the load-bearing total (39 of 93) and hands the screen-by-screen bookkeeping to the
    # supplement — which is where "the 53 deeper re-screens are released ungraded" now lives, beside
    # the one coverage-only control. Both halves are still asserted, and the POINTER is asserted too:
    # a supplement nobody is sent to would make this a deletion wearing a relocation's clothes.
    assert "(SI §S4)" in txt, "the main text no longer points at the release inventory"
    si = _flat(_supplement())
    assert (f"all 38 junction screens, and {len(graded)} of the {len(screens)} screens released in "
            f"total") in si
    assert f"the {len(deep)} deeper re-screens are released ungraded" in si
    assert "One coverage-only control screen records no gap-mismatch depth" in si
    for dead in ("39 of the 45 screens", "the five deeper re-screens",
                 "twenty-two of them screened or re-screened"):
        assert dead not in txt, f"superseded release inventory is back: {dead!r}"
        assert dead not in si, f"superseded release inventory is back in the SI: {dead!r}"


def test_the_taf15_exon6_locus_counts_are_the_deep_ceiling_ones():
    """§3.2's *TAF15* exon-6 sentence — the junction patients with that partner are reported to carry.

    ⛔ EVERY FIGURE HERE WAS PRODUCED BY A LOCUS PARSER THAT SPLIT ONE GENE ACROSS ACCESSIONS. The
    sentence read "four loci at best and seven for the design its gap-level margin ranks first, five
    of those seven annotated only as predicted gene models", off default-depth screens where three
    of the five designs are truncated and the locus fields predate the fix. At the deeper ceiling
    every hit list is complete and the recount is current, which is the only depth at which a
    per-design locus count at this junction is a measurement rather than a bound.
    """
    from collections import Counter  # noqa: PLC0415

    import junction_aso_locus_collapse as C  # noqa: PLC0415
    import junction_aso_offtarget as ja  # noqa: PLC0415

    deep = {seq: o for (lab, seq), o in _deep_screens().items() if lab == "TAF15_e6__NR4A3_e3"}
    if not deep:
        pytest.skip("the deep re-screen of the TAF15 e6 junction is not in this checkout")
    lo, hi = ja.GAP_REGION_1BASED
    margins = {r["antisense_5to3"]: r["gap_specificity_margin"]
               for r in json.load(open(os.path.join(MOD, "aso-parent-gap-pairing.json"),
                                       encoding="utf-8"))["per_design"]}
    loci, predicted_only = {}, {}
    for seq, o in deep.items():
        hits = o["offtargets"]
        assert len(hits) == o["n_offtarget_near_matches"], "a truncated deep list bounds nothing"
        paired = [h for h in hits if not h.get("is_minus_strand")
                  and h["q_from"] <= lo and h["q_to"] >= hi and h.get("gap_mismatches") == 0]
        by = {}
        for h in paired:
            by.setdefault(C.locus_of(h), set()).add(C.accession_class(h))
        loci[seq] = len(by)
        predicted_only[seq] = sum(1 for v in by.values() if v == {"predicted"})
        assert paired, f"{seq} has no gap-spanning near-match; the sentence says every one has"
    assert len(loci) == 5, sorted(loci)
    leader = max(loci, key=lambda s: margins.get(s) or -1)
    assert leader == "GGGCATATCTTGTGTG" and margins[leader] == 3, leader
    assert min(loci.values()) == 3 and min(loci, key=loci.get) == "AGGGCATATCTTGTGT", loci
    assert loci[leader] == 5 and predicted_only[leader] == 3, (loci, predicted_only)
    txt = _flat(_paper())
    #: ⚠ SPLIT IN TWO, 2026-08-17. The sentence used to cite "(Table 2)" for the whole clause, and a
    #: blind screen of the built PDF pointed out that Table 2 has no predicted-gene-model column —
    #: the annotation is a property of the deep hit list, which no table here prints. The locus
    #: counts DO come from Table 2, so the citation moved to cover only them and the clause was
    #: separated. Both halves are still pinned; only the punctuation between them changed, and the
    #: artifact assertions above are what actually establish the numbers.
    assert ("those recount to three gene loci at best, and five for the design its gap-level "
            "margin ranks first") in txt
    assert "three of those five are annotated only as predicted gene models" in txt
    # ⚠ ONE FLATTENED CHECK, 2026-08-16: the raw half of this pair only caught the phrase when it
    # wrapped at exactly that word, so it added nothing the flattened half does not already do.
    assert "four loci at best" not in txt


def test_the_tcf12_exon5_gap_spanning_load_is_one_locus_not_seventeen():
    """§3.3, and the sharpest instance of the same parser defect.

    ⛔ The sentence called this junction "the highest gap-spanning near-match load in the panel: 17
    loci for its best-margin design, 12 of them predicted gene models". Those 17 records are
    seventeen transcript variants of ONE curated locus, PIK3CG, whose description carries a comma
    ("phosphatidylinositol-4,5-bisphosphate ...") and so fell to one accession fallback per variant.
    Not the highest load in the panel, and not predicted models.
    """
    from collections import Counter  # noqa: PLC0415

    import junction_aso_locus_collapse as C  # noqa: PLC0415
    import junction_aso_offtarget as ja  # noqa: PLC0415

    o = _deep_screens().get(("TCF12_e5__NR4A3_e3", "GGGCATATCCATCAGA"))
    if o is None:
        pytest.skip("the deep re-screen of the TCF12 e5 junction is not in this checkout")
    lo, hi = ja.GAP_REGION_1BASED
    paired = [h for h in o["offtargets"] if not h.get("is_minus_strand")
              and h["q_from"] <= lo and h["q_to"] >= hi and h.get("gap_mismatches") == 0]
    loci = Counter(C.locus_of(h) for h in paired)
    assert dict(loci) == {"PIK3CG": 17}, loci
    assert {C.accession_class(h) for h in paired} != {"predicted"}, "the sentence says curated"
    txt = _flat(_paper())
    assert ("retains 17 gap-spanning near-matches at the deeper ceiling, every one of them a "
            "variant of a single curated locus, *PIK3CG*") in txt
    for dead in ("highest gap-spanning near-match load in the panel", "17 loci for its best-margin"):
        assert dead not in txt, f"superseded TCF12 e5 claim is back: {dead!r}"


def test_the_discussion_recommends_the_two_published_junctions():
    """⛔ THE RECOMMENDATION USED TO BE THREE DESIGNS AT JUNCTIONS NO PATIENT IS REPORTED TO CARRY.

    Those three are specificity-clean and remain in the paper as mechanism controls. What a reader
    deciding whether to synthesise needs is the best available reagent at the junctions patients
    actually carry, and both exist at the top gap-level margin with no parent liability. Asserted
    against the per-junction table so the prose cannot drift off it.
    """
    art = os.path.join(MOD, "aso-per-junction-table.json")
    if not os.path.exists(art):
        pytest.skip("the per-junction table is not present in this checkout")
    d = json.load(open(art, encoding="utf-8"))
    published = {j["junction_label"]: j for j in d["junctions"]
                 if j["clinical_tier"] == "published_exon_resolved_breakpoint"}
    assert set(published) == {"EWSR1_e12__NR4A3_e3", "EWSR1_e13__NR4A3_e3",
                              "TAF15_e6__NR4A3_e3", "TCF12_e5__NR4A3_e3",
                              "TFG_e7__NR4A3_e3"}, sorted(published)
    txt = _flat(_paper())
    for label, seq in (("EWSR1_e12__NR4A3_e3", "GGGCATATCATCAAAC"),
                       ("TAF15_e6__NR4A3_e3", "GGGCATATCTTGTGTG")):
        best = published[label]["best_available"]
        assert best["antisense_5to3"] == seq, (label, best)
        assert best["gap_specificity_margin"] == 3 and not best["parent_is_liability"], best
        assert f"5′-{seq}-3′" in txt, f"{label}'s reagent is not named in the manuscript"
    assert "the reagents to synthesise are the best available at the two most frequently " \
           "reported junctions with a published exon-resolved breakpoint" in txt
    # ⛔ AND THE OTHER PUBLISHED JUNCTIONS MUST NOT GO UNMENTIONED. The pilot pair stays two, but a
    # paper whose own tiering names four published junctions and whose Discussion names reagents at
    # two owes the reader the rest and what each buys. Asserted against the ladder artifact so the
    # prose cannot drift off it.
    assert "*EWSR1* exon 13 to *NR4A3* exon 3" in txt
    # ⭐ WHAT THAT REAGENT BUYS MOVED INTO THE GENERATED COVERAGE-LADDER TABLE, 2026-08-16 (it was
    # Table 7 then and is Table 5 since the 2026-08-17 renumber), AND THIS GUARD MOVED WITH
    # IT. The prose used to carry "takes the set from 68.4% to 79.0%"; the editorial pass replaced
    # the whole hand-typed coverage ladder with a generated table and a pointer at it. That is an
    # improvement rather than a loss — the increment now travels with its Wilson interval and its
    # rung, and a table generated from `fusion-junction-aso-coverage-ladder.json` cannot go stale the
    # way the sentence could. So the same fact is asserted three ways: the ladder artifact says the
    # rung, the generated coverage-ladder table prints it, and the main text still states the base figure and sends the
    # reader to the table for the rungs above it.
    lad = json.load(open(os.path.join(REPO, "research", "manuscripts", "aso",
                                      "fusion-junction-aso-coverage-ladder.json"),
                         encoding="utf-8"))["ladder"]
    base = lad[0]
    rung = next(r for r in lad[1:] if "EWSR1_e13__NR4A3_e3" in r["junctions"])
    assert set(base["junctions"]) == set(published) - {
        "EWSR1_e13__NR4A3_e3", "TCF12_e5__NR4A3_e3", "TFG_e7__NR4A3_e3"}, base["junctions"]
    assert (base["coverage_percent"], rung["coverage_percent"]) == (68.4, 79.0), (base, rung)
    assert rung["delta_percent_vs_previous"] == round(
        rung["coverage_percent"] - base["coverage_percent"], 1), rung
    if os.path.exists(TABLES):
        tab = open(TABLES, encoding="utf-8").read()
        assert "**Table 5." in tab, "the coverage-ladder table is not in the generated tables file"
        for r, suffix in ((base, ""), (rung, f" (+{rung['delta_percent_vs_previous']})")):
            lo, hi = r["coverage_percent_range"]
            assert f"| {r['coverage_percent']}% ({lo}–{hi}){suffix} |" in tab, r["panel"]
    assert f"the two are {base['coverage_percent']}%" in txt
    assert "Table 5 gives that figure, the rungs above it and the reagent at each" in txt
    # ⭐ THE FOURTH, ADDED 2026-08-15 WITH THE DEPOSIT THAT RESOLVED IT. Two things must both be in
    # the prose and they pull in opposite directions: the reagent EXISTS and is screened, and its
    # arm is priced at its CEILING because one tumour has ever been sequenced there. Naming the
    # first without the second is how 98.3% would start reading as a reachable target.
    assert "5′-GGGCATATCCATCAGA-3′ at *TCF12* exon 5" in txt
    # ⚠ WHITESPACE-TOLERANT FROM 2026-08-16. These four were pinned against the RAW text with a
    # hard-coded newline inside them, which made every one of them a hostage to the line wrap: the
    # editorial pass re-flowed the paragraph and the claim went on reading identically while the
    # assertion stopped finding it. Worse in the dead-phrase direction — a superseded sentence that
    # came back on ONE line would have passed a raw check silently. Flattened both ways.
    assert "resolved to the nucleotide by the deposited chimeric cDNA" in txt
    # ⭐ RE-PINNED 2026-08-17, round 7 P1 (B3-F1 first half). The old assertion read
    #     "the resulting 98.3% is an upper bound rather than a reachable target"
    # and it pinned a sentence that named ONE reason for the bound. The ladder reaches 98.3 by two
    # steps and the TCF12 arm is the SMALLER of them: +15.9 points for "every remaining EWSR1
    # breakpoint covered" (three further reagents the retrieved record does not resolve to an exon)
    # and +3.4 for TCF12. Attributing the whole bound to TCF12 made the EWSR1 step invisible, which
    # is the larger unbuildable assumption. The upper-bound property is still pinned; what is added
    # is that BOTH reasons are named, with each step's size derived from the ladder rather than
    # spelled here, so a re-priced rung cannot leave this assertion asserting a stale number.
    assert "is an upper bound rather than a reachable target for two reasons and not one" in txt
    _ewsr1_step = next(r for r in lad
                       if r["panel"] == "BOUND — every remaining EWSR1 breakpoint covered")
    _tcf12_step = next(r for r in lad
                       if r["panel"] == "BOUND — the above plus TCF12")
    assert f"{_tcf12_step['delta_percent_vs_previous']} percentage points" in txt, _tcf12_step
    assert f"{_ewsr1_step['delta_percent_vs_previous']}" in txt, _ewsr1_step
    _num_word = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
    assert (f"needs {_num_word[_ewsr1_step['n_reagents_additional_unnamed']]} further reagents"
            in txt), _ewsr1_step
    for dead in ("whose junction has never been published as an exon",
                 "inference from a residue count against this transcript model"):
        assert dead not in txt, f"superseded TCF12 claim is back: {dead!r}"
    # the acceptor-side blind spot, and what is now designed at it
    # ⚠ WHITESPACE-TOLERANT AND TIGHTENED, 2026-08-16. This was a raw newline match with a fallback
    # so loose ("exon 7 to *NR4A3* exon") that the fallback carried the assertion and the exon number
    # was never actually checked. Flattened, the full phrase can be required.
    assert "*EWSR1* exon 7 to *NR4A3* exon 2" in txt
    # ⭐ SUPERSEDED WITHIN THE DAY AND REPLACED RATHER THAN DROPPED, 2026-08-15. This line used to
    # assert "none should be assumed to exist" — the manuscript's statement that no design existed at
    # the exon-2 acceptors. Five designs now exist at each of four such seams and all five deep
    # screens have run at the manuscript geometry, so pinning the old sentence would pin a retracted
    # claim. What replaces it is stronger: the reagents the screened table ranks best are READ from
    # that table and required to appear in the prose, so the paragraph cannot drift off the artifact
    # the way a hand-typed sentence did.
    nc = os.path.join(MOD, "noncoding-acceptor", "aso-noncoding-acceptor-screened-table.json")
    if os.path.exists(nc):
        ncd = json.load(open(nc, encoding="utf-8"))
        screened = [j for j in ncd["junctions"] if j.get("screens_complete")]
        assert len(screened) == 4, [j["junction_label"] for j in screened]
        for j in screened:
            best = j["best_available"]
            seq = best["antisense_5to3"]
            assert f"5′-{seq}-3′" in txt, (j["junction_label"], seq)
            # ⛔ THE LOAD TRAVELS WITH THE SEQUENCE OR THE SENTENCE IS AN ADVERTISEMENT. Each of
            # these four is named for synthesis, and none of them is clean; the margin and the
            # gap-paired count over its locus recount are what a reader weighs before ordering.
            assert f"margin {best['gap_specificity_margin']} and " \
                   f"{best['n_gap_paired']} " in txt or \
                   f"{best['n_gap_paired']} gap-paired near-matches over " \
                   f"{best['n_gap_paired_loci']} loci" in txt, (j["junction_label"], best)
            assert f"{best['n_gap_paired']} over {best['n_gap_paired_loci']}" in txt or \
                   f"{best['n_gap_paired']} gap-paired near-matches over " \
                   f"{best['n_gap_paired_loci']} loci" in txt, (j["junction_label"], best)
        assert "are now designed and screened to the panel's depth" in txt
        assert "None of the four is clean" in txt
        # and they must NOT be pooled into the panel's own counts
        # ⚠ WHITESPACE-TOLERANT FROM 2026-08-16, for the same reason as above: the sentence is
        # unchanged, the line wrap around it is not.
        assert "reported beside the panel and never pooled into it" in txt
    # the gap-length risk is disclosed in the Methods and must be ranked first in the Discussion
    assert "Two risks attach, in this order. The first is architectural" in txt
    assert "The three designs that survive every screen are mechanism controls" in txt
    # and no design clears the parent screen at three junctions, which the paper must not omit
    none_clearing = [j["junction_label"] for j in d["junctions"] if j["best_available"] is None]
    assert len(none_clearing) == 3, none_clearing
    assert "at three of them every design pairs a wild-type parent through the catalytic gap" in txt


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


def test_the_chance_baseline_legend_matches_the_series_it_describes():
    """⛔ THE LEGEND AND THE FIGURE DISAGREED, AND THE FIGURE WAS RIGHT.

    ⚠ Named for the FIGURE, not its number. This was `test_the_figure_3_legend_...` until
    2026-08-15, when the chance-baseline chart moved to Supplementary Figure S1 and a new Figure 2
    took the gap-length identity. A test named after an ordinal goes stale the first time a figure
    is reordered, and then points a future reader at the wrong panel. ⚠ Vindicated on 2026-08-17:
    the deposit was renumbered to first-citation order, the gap-length panel became Figure 3 and the
    multi-partner seam Figure 2 — the second reshuffle in three days, and this test needed no edit.

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
    assert f"nine of the 16-mers" in txt and "five at three junctions and four at two" in txt
    for dead in ("114 molecules", "77 of the 114", "five at three junctions and one at two"):
        assert dead not in txt, f"superseded chance-baseline legend value is back: {dead!r}"


def test_the_accessibility_range_is_the_one_the_artifacts_produce():
    """"0.160 to 0.707 across the 130 designs ... median 0.476" — 130 and 0.476 had NO home.

    The eval artifacts hold 195 accessibility values (190 at real exon junctions, 176 distinct
    sequences); no subset of them has n=130, and no subset has median 0.476. The range was right and
    both other figures were unproducible, which is the most dangerous shape for a wrong number: two
    thirds of the sentence checks out.
    """
    import statistics
    vals = []
    # ⛔ THE PRIMARY CORPUS ONLY, AT ONE GEOMETRY, AND BOTH HALVES ARE NEEDED. This test failed the
    # moment the deep re-screens landed, because an `in name` exclusion list let five
    # `...-deep500.json` files join the denominator and the count went 190 -> 215 with nothing
    # saying so. A parallel corpus taken at a different search ceiling is a DIFFERENT measurement;
    # it must not silently enlarge a population the manuscript quotes. The name rule that replaced
    # that exclusion list is right about depth and says NOTHING about geometry — it is now
    # `aso_screen_sets.is_primary_panel`, applied to a set the loader has already narrowed to the
    # manuscript's 16-mer 5-6-5, so a `...-18mer-...n3.json` emitted tomorrow could not enter this
    # denominator even if its name matched.
    for screen in ass.load_screens(ass.MANUSCRIPT_GEOMETRY, ass.DESIGN_EVALUATION, root=MOD,
                                   select=ass.is_primary_panel):
        for r in screen.artifact.get("top_designs") or []:
            if r.get("site_accessibility") is not None:
                vals.append(r["site_accessibility"])
    assert len(vals) == 190, len(vals)
    txt = _paper()
    assert f"across all {len(vals)} designs at real exon junctions" in txt
    assert f"with a median of {statistics.median(vals):.3f}" in _flat(txt)
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
    # ⛔ MEASURED DEPTH AT ONE MEASURED GEOMETRY, NOT A FILENAME SUFFIX (2026-08-14). This selected
    # `endswith("-deep500.json")`, which was wrong in BOTH directions once the campaigns diverged:
    # it admitted all twelve 18-mer and 20-mer screens — a mixed bag under an assertion that pins
    # `decided == 6` — and it MISSED 27 legitimate 16-mer deep re-screens spelled `-deep500-b1`/`-b2`.
    # ⚠ Neither error moved `decided`: this dict is keyed by (junction, SEQUENCE), and a longer
    # geometry's designs are different sequences, so the contaminants matched no candidate. That is
    # the lucky outcome, not a defence. MEASURED both ways before and after the change: 7 candidates,
    # 6 decided, none still clean.
    deep = {}
    for s_ in ass.load_screens(ass.MANUSCRIPT_GEOMETRY, ass.BLAST_SCREEN, root=MOD,
                               select=ass.is_deep, allow_empty=True):
        for o in s_.artifact.get("oligos", []):
            if o.get("status") == "screened":
                deep[(s_.junction_label, o["antisense_5to3"])] = o
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
    assert "decided six of the seven" in _flat(txt)
    assert "none of the six is clean" in _flat(txt)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# §3.10 — the gap-length trade. Added 2026-08-14 when the screen was folded into the manuscript.
# ─────────────────────────────────────────────────────────────────────────────────────────────
GAPLEN = os.path.join(MOD, "aso-gap-length-tradeoff.json")
TABLES = os.path.join(REPO, "research", "manuscripts", "aso",
                      "fusion-junction-aso-submission-tables.md")


def _gaplen():
    if not os.path.exists(GAPLEN):
        pytest.skip("gap-length trade-off artifact is not present in this checkout")
    return json.load(open(GAPLEN, encoding="utf-8"))


def test_the_gap_length_trade_is_an_identity_and_the_paper_states_it_as_one():
    """⛔ THE ONE CLAIM IN §3.10 THAT IS NOT A COUNT, AND THE ONLY ONE THAT COULD NOT BE FIXED LATER.

    The section's load-bearing sentence is that inside the catalytic gap the junction-unique bases
    and the bases one wild-type parent pairs are COMPLEMENTS summing to the gap. If that were merely
    a strong correlation the conclusion would be "longer gaps tend to cost parent specificity", which
    is a much weaker paper and an honest one; the paper says it holds for every design, so it is
    checked for every design here rather than on the artifact's summary of itself.
    """
    gap = _gaplen()
    arch_gap = {g["architecture"]: g["gap_nt"] for g in gap["geometries"]}
    bad = [r for r in gap["per_design"]
           if r["gap_specificity_margin"] + r["parent_paired_gap_dna_nt"]
           != arch_gap[r["architecture"]]]
    assert not bad, f"{len(bad)} design(s) break the complement identity, e.g. {bad[:2]}"
    assert len(gap["per_design"]) == 798, len(gap["per_design"])

    txt = _flat(_paper())
    assert "are complements: they sum to the gap" in txt
    assert "move inversely" in txt and "parent-paired gap DNA" in txt
    # ⛔ THE SIGN ERROR THIS REPLACED, PINNED AS AN ABSENCE SO IT CANNOT COME BACK. The paper used to
    # say no design could gain a nucleotide of margin "without handing RNase-H1 one more nucleotide of
    # contiguous wild-type-parent duplex". That is true ACROSS geometries and backwards WITHIN one:
    # margin + parent-paired gap DNA = gap length (aso_gap_length_tradeoff.py:373,
    # `parent_dna = max(gl, gr)  # = gap - margin`), so at fixed gap the two move inversely — 38
    # designs at margin 3 concede three nucleotides, 76 at margin 2 concede four, 76 at margin 1
    # concede five. Found and verified round 5, 2026-08-15.
    assert "one more nucleotide of contiguous wild-type-parent duplex" not in txt


def test_the_lead_reagent_row_of_section_3_10_is_the_artifacts():
    """The three molecules §3.10 and §4 name, and every number quoted beside them."""
    gap = _gaplen()
    lead = gap["lead_reagent_at_the_most_commonly_reported_seam"]["by_geometry"]
    assert lead["5-6-5"]["antisense_5to3"] == "GGGCATATCATCAAAC"
    assert lead["5-8-5"]["antisense_5to3"] == "AGGGCATATCATCAAACC"
    assert lead["5-10-5"]["antisense_5to3"] == "CAGGGCATATCATCAAACCA"

    risks = [lead[a]["alignment_screen"]["n_true_cleavage_risk"] for a in ("5-6-5", "5-8-5", "5-10-5")]
    loci = [lead[a]["alignment_screen"]["loci"]["n_loci_with_a_gap_spanning_hit"]
            for a in ("5-6-5", "5-8-5", "5-10-5")]
    margins = [lead[a]["gap_specificity_margin"] for a in ("5-6-5", "5-8-5", "5-10-5")]
    dna = [lead[a]["parent_paired_gap_dna_nt"] for a in ("5-6-5", "5-8-5", "5-10-5")]
    dg = [round(lead[a]["dg37_most_stable_parent_duplex"], 2) for a in ("5-6-5", "5-8-5", "5-10-5")]
    assert (risks, loci, margins, dna, dg) == (
        [123, 3, 0], [6, 1, 0], [3, 4, 5], [3, 4, 5], [-7.77, -8.66, -10.25])

    txt = _flat(_paper())
    assert "123 sense-strand cleavage risks across the gap at six gene loci become 3 at one locus" in txt
    assert "from 3 to 4 to 5 nucleotides, and the" in txt
    assert "−7.77 to −8.66 to −10.25 kcal/mol" in txt
    # §4's named second reagent, and the cost it does NOT buy
    assert "5′-AGGGCATATCATCAAACC-3′ is the 5-8-5 design" in txt
    assert "from −7.77 to −8.66 kcal/mol" in txt


def test_the_matched_seam_population_is_complete_and_the_paper_quotes_it():
    """⛔ MATCHED SEAMS, NOT CORPUS TOTALS. The geometries are not screened at the same junctions, so
    only the six seams all three reached support a like-for-like contrast. The paper must quote that
    population and not the per-geometry one, which differs in coverage rather than in specificity.

    ⚠ AND EVERY RECORD MUST BE PRESENT. An earlier state of this screen had three designs dropped by
    the remote service, which made the zero-risk counts lower bounds; they were closed by unioning
    two same-depth runs. A reappearing drop would silently turn these counts back into bounds while
    the prose still reads them as exact.
    """
    gap = _gaplen()
    m = gap["the_trade"]["transcriptome_coincidence_falls_but_it_MUST"]["matched_junctions"]
    assert m["n_junctions"] == 6, m["n_junctions"]
    by = m["by_geometry"]
    for arch in ("5-6-5", "5-8-5", "5-10-5"):
        assert by[arch]["n_designs_the_remote_service_dropped"] == 0, arch
        assert by[arch]["n_designs_with_an_incomplete_hit_list"] == 0, arch
        assert by[arch]["n_designs_whose_locus_recount_is_exact"] == \
            by[arch]["n_designs_with_alignment_counts"], arch
    n = [by[a]["n_designs_with_alignment_counts"] for a in ("5-6-5", "5-8-5", "5-10-5")]
    zero = [by[a]["n_with_zero_hybridisable_gap_spanning_risk"] for a in ("5-6-5", "5-8-5", "5-10-5")]
    maxloci = [by[a]["loci_with_a_gap_spanning_hit"]["max"] for a in ("5-6-5", "5-8-5", "5-10-5")]
    nonear = [by[a]["n_with_no_near_match_at_all"] for a in ("5-6-5", "5-8-5", "5-10-5")]
    assert (n, zero, maxloci, nonear) == ([30, 42, 54], [8, 28, 54], [7, 2, 0], [0, 7, 39])

    txt = _flat(_paper())
    assert "from 8 of 30 to 28 of 42 to 54 of 54" in txt
    assert "from seven to two to none" in txt


def test_the_corpus_parent_liability_numbers_in_section_3_10():
    """The costed side of the trade, corpus-wide, including the count that cannot be avoided."""
    gap = _gaplen()
    geom = {g["architecture"]: g for g in gap["geometries"]}
    order = ("5-6-5", "5-8-5", "5-10-5")
    ge5 = [geom[a]["n_reaching_reported_dna_minimum"]["5"] for a in order]
    tot = [geom[a]["n_fusion_specific_designs"] for a in order]
    whole = [geom[a]["mature_parent_whole_gap_duplex"]["n_with_any_gap_pairing_window"] for a in order]
    pre = [geom[a]["premrna_hybridisable_gap_paired"]["n_designs_with_at_least_one"] for a in order]
    med = [round(geom[a]["dg37_most_stable_parent_duplex"]["median"], 2) for a in order]
    assert (ge5, tot, whole, pre, med) == (
        [76, 228, 342], [190, 266, 342], [181, 130, 87], [19, 11, 9], [-8.66, -11.60, -14.58])
    # the 5-10-5 count is every design, and the paper says that is forced rather than observed
    assert ge5[-1] == tot[-1]
    assert tot[0] - ge5[0] == 114, tot[0] - ge5[0]

    txt = _flat(_paper())
    assert "from 76 of 190 to 228 of 266 to 342 of 342" in txt
    assert "−8.66 to −14.58 kcal/mol" in txt
    # ⚠ "smaller" -> "larger", round 6. The counted quantity is `max(gl, gr)`
    # (aso_gap_length_tradeoff.py: `parent_dna = max(gl, gr)`), so what cannot be under five at a gap
    # of ten is the LARGER half; the smaller half runs 1 to 5. This guard pinned the wrong word and
    # would have held the error in place -- it is the second time in two rounds that a test asserted
    # a defective sentence, which is worth knowing about substring-pinned guards generally.
    assert "the larger half of a gap of ten cannot be under five" in txt
    assert "At 5-6-5, 114 of 190 designs keep the parent below it" in txt
    # ⚠ THE CRITERION MUST TRAVEL WITH THESE THREE COUNTS. "Pair the whole gap" is a 6-nt condition at
    # 5-6-5 and a 10-nt one at 5-10-5, so 181/190 against 87/342 is not one test read three times —
    # comparing them without saying so reads as a liability that falls with gap length when, held to
    # the ten-base-pair criterion used everywhere else, it is flat. Both halves are asserted together
    # for that reason; pinning only the first would re-open the gap round 5 closed.
    assert "181 of 190 designs at 5-6-5, 130 of 266 at 5-8-5 and 87 of 342 at 5-10-5" in txt
    assert "87 of 190, 88 of 266 and 87 of 342" in txt
    assert "from 19 of 190 to 9 of 342" in txt


def test_the_paper_states_the_two_bounds_that_make_the_fall_partly_arithmetic():
    """⛔ THE HONEST BOUND, AND THE ONE MOST LIKELY TO BE DROPPED IN AN EDIT FOR LENGTH.

    Part of the near-match fall is guaranteed by the instrument: at a fixed absolute mismatch budget
    a longer probe's reachable loci are a SUBSET of its own sub-windows'. Without that sentence the
    section reads as though a longer gap were measured to be cleaner, which is a claim this design
    cannot support. The genome-scan absence is the same shape — structural, not merely unrun.
    """
    txt = _flat(_paper())
    assert "guaranteed by the instrument rather than measured" in txt
    assert "reachable set can only shrink" in txt
    assert "fractionally stricter test at 20 nucleotides than at 16" in txt
    assert "Only the size of the fall, and which designs reach zero, are measurements" in txt
    assert "unavailable at 18 and 20 nucleotides by construction rather than merely unrun" in txt
    # ⭐ REWORDED, NOT LOST — the editorial restructure of 2026-08-16. "so that bound is an available
    # next step and not a result" is now "so the nesting bound on a longer design's genome liability
    # is a next step and not a result". The load-bearing half is "and not a result"; "available"
    # said only that the scan could be run, which the clause it now shares a sentence with already
    # establishes. Pinned on the half that keeps the bound from reading as a finding, and the
    # SUBJECT is pinned with it so the sentence cannot start disclaiming something else.
    assert "the nesting bound on a longer design's genome liability is a next step and not a " \
           "result" in txt
    # and the placeholder it replaced must not come back
    assert "every result reported here is specific to that geometry" not in txt


def test_the_gap_length_table_cells_are_the_artifacts_and_the_paper_points_at_it():
    """The gap-length table is generated; this asserts it agrees with the artifact it reads.

    ⚠ NAMED FOR WHAT THE TABLE SHOWS, NOT FOR ITS NUMBER. It was `test_table5_…` until the deposit
    was renumbered to citation order on 2026-08-17 and this table became Table 7 — the same
    staleness a figure test next door was renamed out of on 2026-08-15. The number below is a pin
    on the generated file and has to move with it; the test's NAME does not have to be a second
    copy of that number.
    """
    if not os.path.exists(TABLES):
        pytest.skip("submission tables are not present in this checkout")
    gap, txt = _gaplen(), open(TABLES, encoding="utf-8").read()
    lead = gap["lead_reagent_at_the_most_commonly_reported_seam"]["by_geometry"]
    assert "**Table 7. Gap length against junction specificity" in txt
    # ⛔ THE COLUMN SET IS DERIVED FROM THE ARTIFACT, NOT TYPED (2026-08-14). It was
    # `("5-6-5", "5-8-5", "5-10-5")` here and the identical tuple in the generator — two copies of
    # one list, so a fourth geometry would have been omitted from the table AND from the check that
    # is supposed to catch the omission. A guard that types the same list as the thing it guards
    # agrees with it while both are wrong.
    present = tuple(g["architecture"] for g in sorted(
        (g for g in gap["geometries"] if g.get("present")), key=lambda g: g["gap_nt"]))
    assert len(present) >= 3, present
    for arch in present:
        assert lead[arch]["antisense_5to3"] in txt, arch
    assert "| sense-strand gap-spanning cleavage risks | 123 | 3 | 0 |" in txt
    assert "| designs carrying none | 8 of 30 | 28 of 42 | 54 of 54 |" in txt
    assert "| a mature parent can pair the whole gap | 181 of 190 | 130 of 266 | 87 of 342 |" in txt
    # ⛔ THE ROW BELOW WAS ADDED AND THE ONE UNDER IT RENAMED (round-7 review, 2026-08-16), AND THIS
    # GUARD MOVED WITH THEM RATHER THAN BEING LOOSENED. §2.9 neutralises the whole gap-length win
    # with "held to the ten-base-pair criterion applied everywhere else here, the liability is flat:
    # 87 of 190, 88 of 266 and 87 of 342" — the sentence the title's "nearly half" survives on — and
    # `88 of 266` was in no table at all. Its two NEIGHBOURS were: 181/130/87 above and 76/228/342
    # below, both plausible, neither the quoted number, and the second wearing the headline's own
    # words ("a ten-base-pair hybrid") against a different quantity. A reviewer checking the
    # sentence landed on a contradiction rather than on an omission.
    # ⚠ DERIVED FROM THE ARTIFACT, NOT TYPED, so a re-screen that moves the counts fails on the
    # sentence rather than agreeing with a stale cell.
    tenbp = " | ".join(f"{g['mature_parent_whole_gap_duplex']['n_at_or_above_min_duplex_bp']} of "
                       f"{g['n_fusion_specific_designs']}"
                       for g in sorted((g for g in gap["geometries"] if g.get("present")),
                                       key=lambda g: g["gap_nt"]))
    assert ("| …and that duplex reaches ten base pairs, the criterion applied throughout | "
            f"{tenbp} |") in txt
    assert f"87 of 190, 88 of 266 and 87 of 342" in _flat(_paper()), (
        "the paper's threshold-controlled sentence and the row that carries it must agree")
    # the merged row rests on wing == 5; the generator refuses if that stops holding. Its label now
    # says WHERE the hybrid is, because the two ten-base-pair rows are different measurements: this
    # one is arithmetic at the design's own seam, the one above is the mature-parent search.
    assert "| at the design's own seam, the parent pairs ≥5 nt of contiguous gap DNA |" in txt
    assert _flat(_paper()).count("Table 7") >= 1

    # ⛔ AND THE POINTER MUST COVER EVERY TABLE THAT EXISTS. The manuscript keeps its tables in a
    # generated companion file and names the range in one sentence; that sentence read "Tables 1 to
    # 4" for as long as it took to notice, which is the same defect this generator's own docstring
    # records — a cross-reference that is neither a false claim nor a style violation, and that reads
    # perfectly while pointing at nothing. Derived from the generated file, never typed.
    n_tables = len(re.findall(r"^\*\*Table (\d+)\.", txt, re.M))
    assert n_tables >= 5, n_tables
    assert f"Tables 1 to {n_tables} are in" in _flat(_paper()), (
        f"the manuscript's table pointer does not cover all {n_tables} generated tables")


EXPRESSION = os.path.join(MOD, "aso-offtarget-tissue-expression.json")


def _expression():
    if not os.path.exists(EXPRESSION):
        pytest.skip("the off-target expression artifact is not present in this checkout")
    return json.load(open(EXPRESSION, encoding="utf-8"))


def _loci_of_design(expr, seq):
    """The loci ONE design returns, not the loci its seam returns.

    ⛔ THIS DISTINCTION IS THE WHOLE REASON THIS HELPER EXISTS. The *TAF15* exon 6 seam is tiled by
    five designs and its panel holds 17 loci; the reagent §4 actually recommends returns 5 of them.
    A seam-level figure written against a named reagent overstates that reagent's load by more than
    threefold, and reads as a measurement of the molecule when it is a measurement of the window it
    was slid through. §3.11 and §4 both speak about reagents, so both are pinned per design.
    """
    return [L for L in expr["per_locus"] if seq in L["designs_hitting_it"]]


def test_section_3_11_expression_figures_are_the_artifacts():
    """Every number in §3.11, read from the expression artifact rather than from a summary.

    ⛔ WRITTEN BECAUSE THE HAND-OFF THAT COMMISSIONED THIS SECTION CARRIED TWO FIGURES THE ARTIFACT
    DOES NOT SUPPORT: it described the *TAF15* reagent's load as "six of seventeen" loci reaching the
    exposure organs, which is the SEAM's panel across five tiling registers rather than the
    reagent's five loci, and it ranked *NRP1* "eleventh of seventeen" by record count where the
    artifact puts it seventh. Neither reached the manuscript. This test is what keeps that true.
    """
    expr, txt = _expression(), _flat(_paper())
    tiss = expr["method"]["exposure_tissues"]
    assert tiss == ["Liver", "Kidney - Cortex", "Kidney - Medulla"], tiss

    # ── the lead, at EWSR1 exon 12 ────────────────────────────────────────────────────────────
    lead = _loci_of_design(expr, "GGGCATATCATCAAAC")
    assert len(lead) == 6, [L["locus"] for L in lead]
    assert sum(L["screen_records"]["n_transcript_records"] for L in lead) == 123
    # ⭐ 278 -> 649 ON 2026-08-15. Not a re-count of the same panel: the expression panel grew
    # from two seams to four when EWSR1 e13 and TCF12 e5 got their readings, and this total is
    # over the panel, not over the lead design. Superseded, retained (CLAUDE.md rule 1.2): 278.
    assert expr["panel"]["n_gap_paired_hybridisable"] == 649
    assert expr["panel"]["n_seams"] == 4
    # and the total must be the sum of its parts rather than a typed figure (rule 1.1)
    assert sum(L["screen_records"]["n_transcript_records"] for L in expr["per_locus"]) == 649
    readable = [L for L in lead if L["exposure_compartment_liver_kidney"]["readable"]]
    assert len(readable) == 4, [L["locus"] for L in readable]
    # the claim is "none of the four measurable ones reaches the upper cut"
    assert not [L for L in lead if L["tier"] == "EXPRESSED_IN_AN_EXPOSURE_ORGAN"]
    # ⛔ THE NOUN, CORRECTED 2026-08-16. `n_transcript_records` is incremented once per gap-paired
    # hit PER DESIGN (aso_offtarget_tissue_expression._seam_rows), and the module's own selftest
    # asserts `n_gap_paired_hybridisable == sum(n_transcript_records)`. So it is a HIT COUNT, not
    # annotation depth, and the paper said the latter in four places. NRP1 is the clinching case:
    # five records over ONE accession, one per design — annotation depth cannot depend on how many
    # designs were run. This pin follows the corrected noun; it previously pinned the wrong one.
    # ⚠ AND THE DENOMINATOR, CORRECTED 2026-08-17. 649 is the gap-paired hit total over the FOUR
    # junctions of Table 6, not over the 38-junction panel: `panel.n_seams` is 4 and the per-locus
    # records sum to exactly 649. "the panel's 649" read as one reagent carrying 19% of the whole
    # panel's off-target burden, which is not what the artifact says.
    assert ("The *EWSR1* exon 12 reagent's six loci carry 123 of the 649 gap-paired hits returned "
            "across the four junctions of Table 6, and none of the four measurable ones reaches "
            "the upper cut") in txt

    anks = next(L for L in lead if L["locus"] == "ANKS1B")
    assert anks["screen_records"]["n_transcript_records"] == 67
    assert anks["tier"] == "BELOW_DETECTION_IN_EXPOSURE_ORGANS"
    top = anks["whole_body_context"]["top_tissues"][0]
    assert top["tissue"].startswith("Brain") and round(top["median_tpm"], 1) == 24.9, top
    assert "*ANKS1B* supplies 67 of them and sits below the lower cut in all" in txt
    # ⚠ MATCHED AROUND THE UNIT, NOT THROUGH IT (2026-08-17). TPM is now expanded at this, its
    # first use — a firewalled cold reader reported it, GTEx and LNA as never expanded anywhere in
    # the three documents. The value and its tissue are what this pin is for, so it asserts those
    # and lets the gloss between them vary.
    assert "peaking instead in brain at 24.9" in txt and "TPM" in txt

    # ⭐ THE GUT READING MOVED HERE FROM §4.1, 2026-08-16. §4.1 used to close its exposure comparison
    # with "its largest sitting instead in brain and gut", which was the ONLY home of the gut half —
    # Table 6's soft-tissue column carries neither. Collapsing that comparison to one site would have
    # deleted a reading, so it landed in §2.8 beside the brain one, and is pinned against the same
    # whole-body block rather than typed: which locus, and that its top tissue really is gut.
    chst5 = next(L for L in lead if L["locus"] == "CHST5")
    assert chst5["screen_records"]["n_transcript_records"] == min(
        L["screen_records"]["n_transcript_records"] for L in lead), "CHST5 is the smallest of the six"
    gut = chst5["whole_body_context"]["top_tissues"][0]["tissue"]
    assert any(w in gut for w in ("Intestine", "Colon", "Stomach")), gut
    assert "*CHST5*, the smallest of the six by hit count, peaks in gut" in txt

    # ── the TAF15 exon 6 reagent ──────────────────────────────────────────────────────────────
    taf = _loci_of_design(expr, "GGGCATATCTTGTGTG")
    assert len(taf) == 5, [L["locus"] for L in taf]
    nrp1 = next(L for L in taf if L["locus"] == "NRP1")
    vals = nrp1["exposure_compartment_liver_kidney"]["values"]
    assert round(min(vals.values()), 1) == 6.6 and round(max(vals.values()), 1) == 17.8, vals
    assert all(v >= 1.0 for v in vals.values()), "the sentence says across all three"
    assert nrp1["tier"] == "EXPRESSED_IN_AN_EXPOSURE_ORGAN"
    # ⚠ NOT TWO AXES — THAT WAS THE DEFECT. At NRP1 "five registers" and "five records" are the
    # SAME fact stated twice: the record count is per design, so five designs returning one
    # accession yield five records. The equality asserted below is therefore an identity, not a
    # coincidence, and the manuscript now says "five gap-paired hits to a single accession".
    n_des = {s["junction_label"]: s["n_designs"] for s in expr["panel"]["panel"]}
    assert nrp1["n_designs_hitting_it"] == n_des["TAF15_e6__NR4A3_e3"] == 5
    assert nrp1["screen_records"]["n_transcript_records"] == 5
    assert [L["locus"] for L in expr["per_locus"]
            if L["n_designs_hitting_it"] == n_des.get(L["seams"][0])
            and L["seams"][0] == "TAF15_e6__NR4A3_e3"] == ["NRP1"], "NRP1 is the only such locus"
    assert ("*NRP1* reaches 6.6 to 17.8 TPM across all three exposure tissues and is the only one "
            "all five of that junction's tiling registers return, on five gap-paired hits to a "
            "single accession") in txt

    # ── the tumour compartment, which is a SEPARATE axis and ordered differently ───────────────
    # ⭐ THE PANEL'S HIGHEST MOVED WHEN THE PANEL GREW, AND THAT IS WHY THIS IS DERIVED.
    # Superseded, retained (CLAUDE.md rule 1.2): LAMA4 at 268.6 TPM was the panel's highest
    # tumour-compartment value over two seams. At four seams TCF12 e5's HNRNPA2B1 reaches 656.6 in
    # tibial nerve. A hand-typed "the panel's highest" would still read as true and would be wrong,
    # so the top locus is taken from the artifact and only then matched against the prose.
    top = max((L for L in expr["per_locus"]
               if L["tumour_compartment_normal_tissue_proxy"].get("readable")),
              key=lambda L: max(L["tumour_compartment_normal_tissue_proxy"]["values"].values()))
    tu = top["tumour_compartment_normal_tissue_proxy"]
    top_v = round(max(tu["values"].values()), 1)
    assert (top["locus"], top_v, tu["max_tissue_in_block"]) == (
        "HNRNPA2B1", 656.6, "Nerve - Tibial"), (top["locus"], top_v, tu["max_tissue_in_block"])
    lama = next(L for L in expr["per_locus"] if L["locus"] == "LAMA4")
    assert round(max(lama["tumour_compartment_normal_tissue_proxy"]["values"].values()), 1) == 268.6
    assert lama["tier"] != "EXPRESSED_IN_AN_EXPOSURE_ORGAN", "LAMA4 is the reverse case"
    # ⭐ THE EXEMPLAR MOVED INTO GENERATED TABLE 6, 2026-08-16, AND THE HAND-TYPED SUPERLATIVE LEFT
    # THE PROSE WITH IT. This pinned "*HNRNPA2B1* carrying the panel's highest value there at 656.6
    # TPM in tibial nerve, ahead of *LAMA4* at 268.6 TPM"; §2.8 now states the claim that sentence
    # was an instance of — that the tumour compartment orders the loci a third way — and leaves the
    # values to the table. That removes the exact hazard the comment above records, since a
    # superlative nobody types cannot go stale, but only if something still checks the values where
    # they landed. So the SAME fact is asserted against the generated table: both cells are its own
    # artifact's, and the artifact's top locus is required to be the top of the PRINTED column, which
    # is a stronger statement than the prose ever made.
    # ⛔ AND THE "THREE ORDERINGS" CLAIM WAS ITSELF PART OF THE MISLABEL (corrected 2026-08-16).
    # Presenting register-robustness and the record count as independent axes was wrong for the same
    # reason the noun was: the count is per design, so a locus returned by more registers accrues
    # more hits BY CONSTRUCTION. NRP1 is the proof — top on register robustness, near the bottom on
    # hits, five records over one accession. The prose now states that dependence instead of
    # implying independence, so this pin follows the corrected claim and asserts the DEPENDENCE
    # clause specifically, which is the part a future shortening pass would drop first.
    assert "robustness to register orders the loci differently again" in txt
    assert ("not\nindependently of the hit count" in _paper()
            or "not independently of the hit count" in txt), (
        "§2.8 no longer states that register robustness and the hit count are dependent — the "
        "sentence has reverted to implying three independent orderings"
    )
    assert "the tumour-compartment proxy orders them a third way" in txt
    if os.path.exists(TABLES):
        tab = open(TABLES, encoding="utf-8").read()
        body = tab[tab.index("**Table 6."):]
        body = body[:body.index("**Table 7.")] if "**Table 7." in body else body
        for L in (top, lama):
            t = L["tumour_compartment_normal_tissue_proxy"]
            v = round(max(t["values"].values()), 1)
            row = next(r for r in body.splitlines() if f"*{L['locus']}*" in r)
            assert f"| {v} ({t['max_tissue_in_block']}) |" in row, (L["locus"], row)
        printed = [float(x) for x in re.findall(r"\| (\d+(?:\.\d+)?) \([A-Z][^)|]*\) \|", body)]
        assert printed and max(printed) == top_v, (top["locus"], top_v, sorted(printed)[-3:])


def test_the_expression_limits_are_stated_and_the_unmeasured_loci_are_accounted():
    """The Limitations sentence: three instruments returning nothing is not a reading of absence.

    ⛔ THE NUMBERS HERE ARE THE ONES THAT MAKE THE LIMIT CHECKABLE. Without the record count behind
    the unread loci a reader cannot tell whether the unanswered fraction is trivial or dominant,
    which is exactly the judgement the limit exists to enable.

    ⭐ RESTATED FOR A FOUR-SEAM PANEL, 2026-08-15. Superseded, retained (CLAUDE.md rule 1.2): "Seven
    loci carry no exposure reading; three are attributable to what the locus is and four are not,
    and those four carry 11 of the panel's 278 records", over 23 loci with 16 readable. The panel
    grew to four seams when EWSR1 e13 and TCF12 e5 got their readings, so every one of those figures
    moved together; none of them was a correction to the old panel.

    ⚠ THE ASSERTIONS ARE DERIVED FROM THE ARTIFACT AND ONLY THEN COMPARED WITH THE PROSE, so a
    changed panel fails on the sentence rather than silently agreeing with a stale one.
    """
    expr, txt = _expression(), _flat(_paper())
    unread = [L for L in expr["per_locus"]
              if not L["exposure_compartment_liver_kidney"]["readable"]]
    n_loci = expr["summary"]["n_loci"]
    n_readable = expr["summary"]["n_loci_with_a_readable_exposure_reading"]
    assert (n_loci, n_readable, len(unread)) == (46, 33, 13), (n_loci, n_readable, len(unread))
    unread_records = sum(L["screen_records"]["n_transcript_records"] for L in unread)
    assert unread_records == 52, unread_records
    # ⭐ REWORDED, NOT LOST — the editorial restructure of 2026-08-16. "Thirteen of the 46 loci
    # returned no reading, and they carry 52 of the panel's 649 records, so for those the exposure
    # question is unanswered rather than answered negatively" now reads "13 of the 46 loci returned
    # no reading and carry 52 of the panel's 649 records, so there the exposure question is
    # unanswered rather than answered negatively" — the count is a numeral because the clause no
    # longer starts the sentence, and "for those" is "there". Both figures and the whole
    # unanswered-not-negative distinction are intact, so the count is matched in either spelling and
    # everything after it verbatim.
    assert (f"{len(unread)} of the {n_loci} loci returned no" in txt
            or f"{_spelt(len(unread)).capitalize()} of the {n_loci} loci returned no"
            in txt), len(unread)
    # ⚠ DENOMINATOR CORRECTED 2026-08-17: 649 is the four-junction total of this table, not the
    # 38-junction panel's — `panel.n_seams` is 4 in aso-offtarget-tissue-expression.json.
    assert (f"carry {unread_records} of those "
            f"{expr['panel']['n_gap_paired_hybridisable']} hits, so there the exposure "
            "question is unanswered rather than answered negatively") in txt
    # ⭐ "No expression figure is a predicted cleavage event" MOVED TO WHERE THE CHOICE IS MADE. The
    # de-duplication sweep collapsed three copies of the exposure-vs-count comparison into one, in
    # §4.1, and this firewall travelled with it: "no cleavage is predicted at any of them, and an
    # expressed gene is necessary and not sufficient for an effect". The Limitations paragraph that
    # carries the 13/46 and 52/649 figures keeps the same claim as its own thesis, in its heading.
    # ⛔ BOTH ARE ASSERTED. The firewall standing only beside the numbers would let a reader take the
    # recommendation without it; standing only beside the recommendation would let the numbers be
    # read as predicted events. It has to be in both places, so both are required here.
    assert "Hybridisation, not cleavage, and not exposure." in txt
    assert "no cleavage is predicted at any of them, and an expressed gene is necessary and not " \
           "sufficient for an effect" in txt


def test_section_4_separates_the_two_reagents_without_making_a_safety_claim():
    """§4's use of the expression result, and the two properties it must not acquire.

    ⛔ THE ARTIFACT CARRIES NO RISK COLUMN AND NO HAZARD ORDERING, AND A TEST WALKS ITS KEYS TO KEEP
    IT SO. That guarantee is worth nothing if the prose reintroduces the ordering the artifact
    refused, so the same refusal is asserted on the manuscript: the paragraph may report where the
    loci are expressed and may say the two reagents differ, and may not call either one risky, safe,
    concerning or a hazard. It must also keep the ranking it had, because expression is not
    cleavage and nothing here establishes that a two-mismatch duplex engages any locus.

    ⛔⛔ THIS GUARD PINNED A FALSE CLAUSE FOR THREE DAYS AND THE CLAUSE WAS CORRECTED, NOT RESTORED
    (2026-08-16). It required §4 to read "the *TAF15* reagent's five include *NRP1*, which is
    expressed at that level in all three" — "that level" being the upper cut, and "all three" the
    exposure tissues. *NRP1* is at 6.62 TPM in liver against an upper cut of 10.0, so it is at or
    above the cut in TWO of the three, not all three; Table 6 has printed the disagreeing number the
    whole time. The manuscript now says "which is", with §2.8 carrying the exact count.

    ⚠ AND THE FALSE VERSION IS PINNED AS AN ABSENCE. A guard that merely stopped requiring the wrong
    sentence would let it come back on the next edit for symmetry. THIS IS THE THIRD TIME IN THIS
    FILE that a substring-pinned guard has held a defective sentence in place — see
    `test_the_corpus_parent_liability_numbers_in_section_3_10` on "smaller" for "larger", and
    `test_the_taf15_exon6_locus_counts_are_the_deep_ceiling_ones` on the split-locus counts. The
    lesson each time is the same: pin the fact against the artifact, and pin the prose only as the
    place the fact has to appear.
    """
    import aso_offtarget_tissue_expression as X  # noqa: PLC0415
    expr, txt = _expression(), _flat(_paper())
    lead = _loci_of_design(expr, "GGGCATATCATCAAAC")
    taf = _loci_of_design(expr, "GGGCATATCTTGTGTG")
    assert not [L for L in lead if L["tier"] == "EXPRESSED_IN_AN_EXPOSURE_ORGAN"]
    assert [L["locus"] for L in taf
            if L["tier"] == "EXPRESSED_IN_AN_EXPOSURE_ORGAN"] == ["NRP1"]
    # ⛔ "four measurable", NEVER "six". Two of the lead's six loci have NO exposure reading, so a
    # sentence saying none of the six is expressed would convert an absent reading into a reading of
    # absence — in the one paragraph a reader takes a recommendation from.
    assert len([L for L in lead
                if not L["exposure_compartment_liver_kidney"]["readable"]]) == 2, "two unreadable"
    # ⛔ HOW MANY EXPOSURE TISSUES *NRP1* ACTUALLY REACHES THE UPPER CUT IN, COUNTED FROM THE
    # ARTIFACT. Everything below is written against this number rather than against a remembered one.
    nrp1 = next(L for L in taf if L["locus"] == "NRP1")
    vals = nrp1["exposure_compartment_liver_kidney"]["values"]
    n_tiss = len(expr["method"]["exposure_tissues"])
    at_upper = sorted(t for t, v in vals.items() if v >= X.EXPRESSED_TPM)
    assert (len(at_upper), n_tiss) == (2, 3), (at_upper, vals)
    assert min(vals.values()) < X.EXPRESSED_TPM, vals    # liver, at 6.62 — the refuting reading
    assert min(vals.values()) >= X.PRESENT_TPM, vals     # but above the LOWER cut in all three
    # ⚠ "four measurable" -> "measurable" IN §4.3 ONLY, 2026-08-16. The count of readable loci was
    # printed at THREE sites — §2.8, §4.1 and here — and the editorial pass collapsed the
    # exposure-vs-count comparison to one home. What this guard exists for is the word "measurable",
    # not the word "four": a sentence saying none of the SIX is expressed converts an absent reading
    # into a reading of absence, and "measurable" is what refuses that. The number itself is still
    # pinned against the artifact three lines above (two unreadable of six) and still printed in
    # §2.8, whose sentence is asserted verbatim in
    # `test_section_3_11_expression_figures_are_the_artifacts`.
    assert "reagent's four measurable loci" not in txt or txt.count("four measurable") == 1
    assert ("none of the *EWSR1* reagent's measurable loci is expressed at the upper cut in "
            "the organs a systemic dose reaches, while the *TAF15* reagent's five include *NRP1*, "
            "which is.") in txt
    # the exact count lives in §2.8, and is derived here so it can never drift back to "all three"
    assert (f"It is at or above the upper cut in {_spelt(len(at_upper))} of those "
            f"{_spelt(n_tiss)}") in txt
    for dead in ("which is expressed at that level in all three",
                 f"reaches the upper cut in all {_spelt(n_tiss)}"):
        assert dead not in txt, (
            f"the refuted *NRP1* claim is back: {dead!r}. Liver is {vals['Liver']:.2f} TPM against "
            f"an upper cut of {X.EXPRESSED_TPM:g}; the reagent's locus is at or above it in "
            f"{len(at_upper)} of {n_tiss} exposure tissues, not all of them.")
    assert "reagent's six loci is expressed" not in txt
    assert "That does not reverse the ranking" in txt
    assert "it is not a statement about safety" in txt

    # the paragraph that carries the expression result must not acquire a hazard vocabulary
    # ⚠ THE ANCHOR MOVED WITH THE PARAGRAPH, 2026-08-16: "Expression reads the two loads
    # differently" became "Expression separates the two reagents the other way" when the three copies
    # of this comparison were collapsed into one. The span is the same span — from the expression
    # sentence to the start of the controls paragraph.
    para = txt[txt.index("Expression separates the two reagents the other way"):]
    para = para[:para.index("The three designs that survive every screen")]
    for banned in ("high-risk", "high risk", "concerning", "dangerous", "unsafe", "hazard",
                   "toxic", "safety concern", "safer", "riskier"):
        assert banned not in para.lower(), f"§4 acquired hazard framing: {banned!r}"


def test_table6_cells_are_the_artifact_and_its_two_compartments_stay_separate():
    """Table 6 is generated from the expression artifact, and never merges the two compartments.

    ⚠ THE REGISTER COLUMN CARRIES ITS DENOMINATOR ON PURPOSE. One seam contributes a single design
    and the other five, so a bare count would read as a difference in robustness where one of the
    two is every register there is.
    """
    tables = os.path.join(REPO, "research", "manuscripts", "aso",
                          "fusion-junction-aso-submission-tables.md")
    if not os.path.exists(tables):
        pytest.skip("the generated tables file is not present in this checkout")
    expr = _expression()
    txt = open(tables, encoding="utf-8").read()
    assert "**Table 6." in txt, "Table 6 is not in the generated tables file"
    body = txt[txt.index("**Table 6."):]

    for t in expr["method"]["exposure_tissues"]:
        assert t in body, t
    # one row per locus, every locus, with its own record count
    for L in expr["per_locus"]:
        assert f"*{L['locus']}*" in body, L["locus"]
    n_des = {s["junction_label"]: s["n_designs"] for s in expr["panel"]["panel"]}
    for L in expr["per_locus"]:
        assert f"| {L['n_designs_hitting_it']} of {n_des[L['seams'][0]]} |" in body, L["locus"]

    # an unreadable locus prints its reason, never a zero
    for L in expr["per_locus"]:
        if not L["exposure_compartment_liver_kidney"]["readable"]:
            row = next(r for r in body.splitlines() if f"*{L['locus']}*" in r)
            assert "0.00" not in row, f"{L['locus']} rendered an absent reading as a number"

    # the two compartments are separate columns and the table carries no risk ordering
    assert "soft-tissue proxy maximum" in body and "exposure-organ reading" in body
    for banned in ("risk", "hazard", "concerning", "safety", "priority", "rank "):
        assert banned not in body.lower().split("| junction |")[1][:4000], banned

    # the cuts are the module's, not re-typed into the legend
    import aso_offtarget_tissue_expression as X  # noqa: PLC0415
    assert f"below {X.PRESENT_TPM:g} TPM in all three exposure" in body
    assert f"at or above {X.EXPRESSED_TPM:g} TPM in any of them" in body


# ── the wild-type-allele liability, and the rule that decides it ─────────────────────────────────
NONCODING_TABLE = os.path.join(MOD, "noncoding-acceptor",
                               "aso-noncoding-acceptor-screened-table.json")
CRYPTIC_TAF15 = os.path.join(MOD, "aso-taf15-intron2-designs.json")
MODEL_EVIDENCE = os.path.join(MOD, "emc-model-junction-evidence.json")


def test_the_wild_type_allele_liability_is_named_with_the_designs_it_condemns():
    """§4's wild-type-*NR4A3* paragraph, read out of the scans that produced it.

    ⛔ WHY EVERY PART OF THIS IS PINNED. The finding's whole content is that a design can PASS the
    mature-parent screen and still pair its catalytic gap on the patient's un-rearranged allele, so
    the sequences it condemns are the one thing a reader ordering oligonucleotides acts on. A prose
    list that drifted from the scan by one sequence would be worse than no list: it would read as a
    checked exclusion while omitting a molecule the instrument condemned.

    ⚠ THE SCAN'S OWN POSITIVE CONTROL IS ASSERTED TOO. A liability scan that fires on nothing is
    indistinguishable from a clean panel, and this one is required to fire on exactly one known
    design at the sibling cryptic-exon seam. If that control stops passing, no verdict above it
    means anything and the manuscript's exclusions are unsupported.
    """
    for p in (NONCODING_TABLE, CRYPTIC_TAF15):
        if not os.path.exists(p):
            pytest.skip("the non-canonical acceptor artifacts are not present in this checkout")
    nc = json.load(open(NONCODING_TABLE, encoding="utf-8"))
    liab = nc["⭐_wild_type_NR4A3_cleavage_liability"]
    txt, raw = _flat(_paper()), _paper()

    # the control fired, on exactly the design it had to fire on
    ctrl = liab["positive_control"]
    assert ctrl["passed"] and ctrl["observed_designs"] == ["TGATGAGGGCCTTGTG"], ctrl
    assert ctrl["observed_n_cleavage_competent_designs"] == 1, ctrl

    # every condemned design is named in the manuscript, and none is quietly dropped
    condemned = list(liab["designs_cleaving_wild_type_NR4A3"]) + list(ctrl["observed_designs"])
    assert len(condemned) == 3, condemned
    for seq in condemned:
        assert f"5′-{seq}-3′" in txt, f"{seq} is condemned by the scan and not named in the paper"
    assert "named here as not to be carried forward" in txt

    # and no condemned design survives in any best_* field of either artifact
    for j in nc["junctions"]:
        best = (j.get("best_available") or {}).get("antisense_5to3")
        assert best not in liab["designs_cleaving_wild_type_NR4A3"], j["junction_label"]
    cryptic = json.load(open(CRYPTIC_TAF15, encoding="utf-8"))
    assert cryptic["best_by_gap_specificity_margin"] not in condemned

    # ⛔ THE DECIDER IS DONOR SEQUENCE IN THE GAP, NOT THE MARGIN, and the paper must say so — an
    # earlier reading of this repository credited the margin and was refuted by the exon-2 seams.
    assert "It is not the gap-level margin" in txt
    assert "how much donor sequence the gap holds" in txt
    assert "a design at the same seam with a margin of 1 and five donor bases in its gap is clean" \
        in txt
    # the mechanism, from the measurement rather than from the sentence
    ev = json.load(open(MODEL_EVIDENCE, encoding="utf-8"))["nr4a3_wild_type_acceptor_context"]
    intron1 = ev["nr4a3_intron1_last_12_nt"]
    e13 = ev["donor_last_12_nt_vs_nr4a3_intron1_last_12_nt"]["EWSR1_e13"]
    t6 = ev["donor_last_12_nt_vs_nr4a3_intron1_last_12_nt"]["TAF15_e6"]
    assert f"ends {e13['donor_last_12_nt']} against the" in txt
    assert f"last twelve nucleotides of *NR4A3* intron 1, {intron1}, matching at " \
           f"{e13['identity_over_12']} of 12 positions" in txt
    assert f"ends {t6['donor_last_12_nt']} and matches at {t6['identity_over_12']}" in txt

    # ⛔ THE REASON THE PARENT SCREEN IS NO DEFENCE, DERIVED RATHER THAN ASSERTED. The claim is that
    # every condemned design cleared the mature-parent exclusion, AND so did every sibling design at
    # its seam — which is what makes a clean parent column at such a seam uninformative rather than
    # merely lucky. ⚠ It is NOT the claim that all 20 scanned designs cleared it: two did not, at
    # seams that condemn nothing, and writing the wider version would have been false.
    by_seq = {des["antisense_5to3"]: (j, des)
              for j in nc["junctions"] for des in j["designs"]}
    for seq in liab["designs_cleaving_wild_type_NR4A3"]:
        j, des = by_seq[seq]
        assert des["parent_is_liability"] is False, seq
        assert j["n_designs_clearing_the_parent_screen"] == j["n_designs_screened"], j["junction_label"]
    assert cryptic["n_clearing_the_parent_exclusion"] == cryptic["n_designs_spanning_the_seam"]
    # ⭐ REWORDED, NOT LOST — the editorial restructure of 2026-08-16 promoted this finding out of the
    # Discussion and into Results, where the three sequences are named in the sentence before it, so
    # "each of the three" became "Each" and "every other design tiled at its seam" lost the redundant
    # participle. Both halves of the claim survive verbatim in substance: each condemned design had
    # cleared the mature-parent exclusion, AND so had every sibling at its seam — which is what makes
    # a clean parent column at such a seam uninformative rather than lucky.
    assert "had already cleared the mature-parent exclusion, and so had every other design at " \
           "its seam" in txt
    # ⛔ AND THE ANTECEDENT MUST STILL BE THE THREE. "Each had already cleared…" bounds nothing if the
    # sentence before it stopped counting them, so the count is required in the same paragraph.
    assert f"matter more than the {_spelt(len(condemned))} sequences" in txt, len(condemned)

    # ⛔ "RETURNED INDEPENDENTLY BY THE GENOME SCAN" IS A SEPARATE INSTRUMENT AND IS CHECKED AS ONE.
    # The genome screen's named-target stratum is a lookup over the whole assembly rather than over
    # one locus, so its agreeing on the same designs is corroboration; asserting the prose without
    # asserting the lookup would let the sentence outlive the arm it credits.
    gen = os.path.join(MOD, "aso-genome-offtarget-noncoding-acceptor.json")
    if os.path.exists(gen):
        st3 = json.load(open(gen, encoding="utf-8"))["headline"]["stratum_3_named_targets"]
        assert st3["genes_hit_gap_paired_and_hybridisable"] == ["NR4A3"], st3
        assert st3["n_designs_with_a_named_gap_paired_site"] == \
            len(liab["designs_cleaving_wild_type_NR4A3"]) == 2
        assert all(s["gap_fully_paired"] and s["hybridisable"] for s in st3["sites"]), st3["sites"]
    assert "returned independently by an exhaustive scan" in txt
    # ⛔ "cleave" -> "pair their whole catalytic gap against" (round-7 D1-F7/B5-F3, applied
    # 2026-08-17). §5 says all five screens address hybridisation only, and the producing artifact's
    # own verdict string is a competence statement. The abstract and Box 1 always had it right; this
    # pin was holding the one hazard claim stated above its evidence.
    assert ("**Some designs pair their whole catalytic gap against the patient's own un-rearranged "
            "*NR4A3* allele") in raw


def test_the_testable_surface_states_the_only_catalogued_line_cannot_test_a_junction_reagent():
    """§4's test-article paragraph: the operational fact, and the four things it must not become.

    ⚠ H-EMC-SS (OBJ-LINE-HEMCSS) is registered in research/manuscripts/emc-systems-map.json with
    identity DISPUTED, and this test exists to keep the manuscript's use of it inside what that
    verdict supports.

    ⛔ WHY THE PROHIBITIONS ARE ASSERTED AND NOT ONLY THE CLAIM. The evidence here is four indirect
    readings and one figure-legend sentence. It supports exactly one operational statement — no
    reagent named here can be tested in that line — and it does NOT support a misidentification
    call, a statement of what the line is instead, a count of affected papers, or any imputation to
    an author. Those are the sentences that would be easy to write and impossible to defend, so the
    test refuses them by name.
    """
    if not os.path.exists(MODEL_EVIDENCE):
        pytest.skip("the model-junction evidence artifact is not present in this checkout")
    ev = json.load(open(MODEL_EVIDENCE, encoding="utf-8"))
    block = ev["⛔⛔_the_only_purchasable_EMC_line_cannot_test_a_junction_reagent"]
    assert block["line"] == "H-EMC-SS"
    txt = _flat(_paper())

    assert "H-EMC-SS" in txt
    assert "no reagent named here can be tested in that line" in txt
    # the fairness constraints, both of which the evidence requires
    assert "This is not a statement that the line is misidentified" in txt
    # ⚠ ABBREVIATED 2026-08-16: "fusion-negative extraskeletal myxoid chondrosarcoma tumours are"
    # became "fusion-negative EMC tumours are" when §3 was made consistent with the rest of the
    # paper, which defines (EMC) at first use in the abstract and uses the abbreviation everywhere
    # else. The CLAUSE this guard exists for — that a fusion-negative tumour is a recognised
    # category, so absence of the fusion is not a reclassification — is unchanged; only the disease
    # name's spelling moved. Pinned on the load-bearing half so a respelling cannot silently
    # delete the fairness constraint with it.
    assert "fusion-negative EMC tumours are" in txt
    assert "themselves a recognised minority category" in txt
    # already reported, never examined — the novelty limit
    assert "The observation is also not new" in txt

    # ⛔ THE FOUR SENTENCES THE EVIDENCE DOES NOT SUPPORT.
    for banned in ("misidentified line", "wrongly diagnosed", "STR misidentification",
                   "papers rely on", "contaminated the literature"):
        assert banned not in txt, banned
    # no count of affected papers may appear: the triage was abstract-level and says so
    assert not re.search(r"\b\d+ (?:of \d+ )?(?:papers|records|studies)[^.\n]{0,40}H-EMC-SS", txt)

    # the five test articles, and that each has a reagent at its junction
    #
    # ⛔ THE OLD PIN HELD A SENTENCE ITS OWN PARAGRAPH CONTRADICTED (2026-08-17). It read "five test
    # articles, and each of the five now has a matching reagent" — and four lines later the same
    # paragraph says the third construct's reagent "cannot be certified under the criterion §4.5
    # states", while §2.6 says that reagent is not certifiable. A blind screen of the built PDF
    # filed the pair as a MAJOR: a reader cannot tell whether the deliverable set is five reagents
    # or four. The headline now states the count AND the qualification, so what is pinned is the
    # honest version rather than the tidier one.
    assert "five test articles" in txt
    assert "Each of the five has a reagent at its junction" in txt
    assert "four certifiable reagents and a fifth carried under that qualification" in txt
    for arm in ("E-N", "T-N*", "T-N"):
        assert arm in txt, arm
    # what a rebuilt construct cannot buy, and the binding constraint
    assert "not to activity at endogenous expression from an endogenous locus" in txt
    assert "the rate-limiting step is a laboratory rather than a line" in txt


def test_the_tfg_deposit_is_reported_without_moving_a_coverage_figure():
    """§3.3's *TFG* paragraph, read off the nuccore sweep that produced it.

    ⛔ TWO HALVES THAT MUST TRAVEL TOGETHER. The deposit supplies an EXON — TFG's first exon-resolved
    breakpoint anywhere in this repository — and supplies no DISTRIBUTION, and TFG is absent from the
    58-case cohort the coverage denominators use. A sentence carrying only the first half would read
    as a partner arm that could be priced.

    ⚠ THE PATENT RECORDS ARE CORROBORATION OF A SEQUENCE, NOT OF FOUR PATIENTS, and the artifact says
    so in terms. Asserting the prose keeps that qualification attached to the count.
    """
    art = os.path.join(MOD, "nr4a3-deposited-junctions.json")
    if not os.path.exists(art):
        pytest.skip("the deposited-junction sweep is not present in this checkout")
    rec = json.load(open(art, encoding="utf-8"))["junctions"]["TFG_e7__NR4A3_e3"]
    txt = _flat(_paper())
    assert rec["records"][0] == "AY532911.1", rec["records"]
    assert len(rec["records"]) - 1 == 4, rec["records"]
    assert "not_a_frequency" in " ".join(rec.keys())
    assert "GenBank AY532911.1" in txt
    assert "*TFG* exon 7\njoined to *NR4A3* exon 3" in _paper() or \
           "*TFG* exon 7 joined to *NR4A3* exon 3" in txt
    assert "Four patent sequence records agree" in txt
    assert "one family from one group" in txt
    assert "no source states what fraction of *TFG*-rearranged tumours break there" in txt
    # ⛔ and TFG must remain absent from the coverage denominator, or the paragraph is wrong
    sys.path.insert(0, os.path.join(REPO, "research", "manuscripts"))
    import aso_reagent_coverage as RC  # noqa: PLC0415
    assert "TFG" not in RC.PARTNER_COHORT["counts"], RC.PARTNER_COHORT["counts"]
    assert "so this changes which junctions are reported and no percentage" in txt
