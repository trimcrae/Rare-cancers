#!/usr/bin/env python3
"""Every headline quantity in the JOURNAL ARTICLE, tied to the artifact that produces it.

⛔ WHY THIS EXISTS — THE SIXTH ONE-OF-A-PAIR GUARD. The submission ships as two documents: the
extended report (`fusion-junction-aso-research-article.md`) and the short journal article
(`fusion-junction-aso-journal-article.md`). `research/modalities/tests/test_aso_submission_numbers.py`
carries ~200 prose-against-artifact assertions and binds ALL of them to `PAPER`, the extended report
alone. Five sibling guards had the same shape and were widened in rounds 8-11; this one could not be,
because the journal article is not a subset of the extended report's prose — it restates the same
quantities in its own sentences. So the numbers in the short document had NO artifact binding at all:
a value could drift in the journal article, disagree with the artifact that produces it, and every
test in the repository would still pass.

That is not hypothetical for this pair. Round 12 dropped an unsupported search-depth multiple from
one of the two sentences carrying it and left the other standing, and the commit message reported the
claim "dropped". Nothing failed, because nothing was reading this document for its numbers.

⛔ THE ASSERTIONS ARE ON DERIVED VALUES, NEVER ON REMEMBERED ONES. Each block loads the artifact,
computes what the prose should say, and looks for that. A failure means the journal article and its
evidence have diverged — fix whichever is wrong, but do not relax the assertion, and do not paste the
artifact's current value in as a literal to make it green.
"""
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MANUSCRIPTS))
ASO = os.path.join(MANUSCRIPTS, "aso")
MOD = os.path.join(REPO, "research", "modalities")

sys.path.insert(0, MANUSCRIPTS)
import aso_falsification_power  # noqa: E402

ARTICLE = os.path.join(ASO, "fusion-junction-aso-journal-article.md")
GAP_PAIRING = os.path.join(MOD, "aso-parent-gap-pairing.json")
NULL = os.path.join(MOD, "aso-parent-null.json")
COVERAGE = os.path.join(ASO, "fusion-junction-aso-reagent-coverage.json")


def _required(path, what):
    """⛔ An artifact that is not there is a finding, never a silent pass.

    Same rule as the submission-numbers guard: every path below is `git ls-files`-tracked, so its
    absence is a broken tree rather than a partial checkout, and a guard that disappears with its
    input is indistinguishable from one that never ran.
    """
    if not os.path.exists(path):
        pytest.fail(f"{what} is missing at {path}. It is committed, so regenerate it rather than "
                    "passing over the assertions that depend on it.")
    return path


@pytest.fixture(scope="module")
def prose():
    return open(_required(ARTICLE, "the journal article"), encoding="utf-8").read()


@pytest.fixture(scope="module")
def pairing():
    return json.load(open(_required(GAP_PAIRING, "the mature-parent gap-pairing screen")))


@pytest.fixture(scope="module")
def null():
    return json.load(open(_required(NULL, "the null-ensemble artifact")))


def _pct(x):
    """The share as the article prints it — one decimal place, percent."""
    return f"{round(x * 100, 1):.1f}%"


def _flat(text):
    """The prose with its hard wrapping collapsed.

    The article is wrapped at ~100 columns, so almost every construction worth binding straddles a
    line break — the first version of this file failed to match "at\n6.2% against" for exactly that
    reason. Matching against the flattened text keeps the patterns readable as sentences.
    """
    return re.sub(r"\s+", " ", text)


def _word(n):
    """The published-breakpoint counts are SPELLED OUT in §3 ("and two", "and none").

    A count that reaches the page as a word is still a count, and binding it as one is what lets
    `_every_site` read the sentence the article actually prints instead of a paraphrase of it.
    """
    return ("none", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
            "ten", "eleven", "twelve", "thirteen")[n]


def _every_site(prose, pattern, expected, what):
    """⛔⛔ EVERY SITE THAT STATES THE QUANTITY, NOT WHETHER IT APPEARS SOMEWHERE.

    The first draft of this file asserted `value in prose`, and a mutation test walked straight
    through it: 45.8% and 40.6% are each stated at THREE sites, so corrupting ONE left the others
    standing and the assertion green — while the document now said two different things about the
    same measurement. That is the ONE FACT, ONE PLACE defect exactly, and an instrument that only
    asks "is the right number in here anywhere" cannot see it.

    So `pattern` captures the number(s) from the CONSTRUCTION that states them and every match is
    checked. `expected` is a string for a one-group pattern or a tuple for several.

    ⚠ THE PATTERNS ARE DELIBERATELY NARROW, because the loose ones are ambiguous: "the panel's
    <rate>" introduces the panel's rate at the ten-base-pair criterion in one sentence and at the
    seven-base-pair criterion in another, and a guard that matched both would assert two different
    measurements are equal. Each pattern therefore carries enough of its sentence to name which
    reading it is binding.

    At least one match is required: a pattern that has stopped matching is a guard that has silently
    stopped guarding, which is the failure mode this whole file exists for.
    """
    found = re.findall(pattern, _flat(prose))
    assert found, (f"nothing in the journal article matches the construction that states {what} "
                   f"(/{pattern}/) — either the sentence was reworded and this guard needs to "
                   "follow it, or the claim was dropped")
    wrong = [f for f in found if f != expected]
    assert not wrong, (f"{what} is {expected!r} in the artifact, and the article states "
                       f"{wrong!r} at {len(wrong)} of its {len(found)} site(s)")


def test_the_criterion_the_article_states_is_the_one_the_screen_used(prose, null):
    """⛔⛔ THE CUT IS A WORD, SO NO NUMERIC INSTRUMENT EVER READ IT (round 15 seat 2, BLOCKER).

    The abstract says 87 designs pair the gap "over TEN or more contiguous base pairs" and §8 says
    "over a contiguous run of TEN base pairs or more, TEN being adopted rather than measured". Both
    were bound by nothing: mutation-confirmed on the full workflow — replace ten with seven, rebuild
    both journal PDFs, run all thirteen gates, green. The shipped abstract then states the count at
    a criterion at which the same screen returns 175 of 190, on a page whose title still reads
    `at 10 bp` and whose §3 still says "the ten-base-pair criterion".

    ⛔ AND THE BINDING ALREADY EXISTED, FOR THE OTHER PAPER.
    `research/modalities/tests/test_aso_parent_gap_pairing.py` requires one sentence to carry the
    denominator, the count, "a TEN-base-pair criterion in any wording" and the *NR4A3* share, and
    its own comment says why: "at a seven-base-pair criterion the same screen returns 175 of 190".
    Its `PAPER` is the extended report alone — the same one-of-a-pair shape this review has now
    closed a dozen times, in the guard written specifically to stop THIS sentence losing THIS
    criterion.

    ★ DERIVED FROM `method.min_duplex_bp`, so a re-run at another cut fails here rather than
    shipping a count under a criterion it was not counted at.
    """
    cut = null["method"]["min_duplex_bp"]
    _every_site(prose, r"pair their whole catalytic gap over (\w+) or more contiguous base pairs",
                _word(cut), "the criterion the abstract states its count at")
    _every_site(prose,
                r"pairs its whole catalytic gap over a contiguous run of (\w+) base pairs or more, "
                r"(\w+) being adopted rather than measured",
                (_word(cut), _word(cut)),
                "the criterion §8 defines liability at, and the word it repeats")


def test_the_panel_and_its_liable_count_are_the_screens_own(prose, pairing):
    """190 designs, 87 liable, 61 of them against NR4A3 — the abstract's opening arithmetic."""
    corpus = pairing["corpus"]
    n = corpus["n_designs"]
    liable = corpus["n_with_parent_duplex_through_gap"]
    nr4a3 = corpus["which_parent_supplies_it"]["NR4A3"]
    assert re.search(rf"\b{n}\b[^.]*?16-mers", prose), \
        f"the panel size {n} from {os.path.basename(GAP_PAIRING)} is not the one the abstract tiles"
    assert re.search(rf"\b{liable}\b", prose), f"the liable count {liable} is absent from the article"
    assert re.search(rf"\b{nr4a3}\b of (?:the {liable}|those)", prose), \
        f"{nr4a3} of {liable} against wild-type NR4A3 is the screen's attribution and the prose " \
        "does not carry it"
    # ⛔ THE DENOMINATOR TOO, AT THE SITE THAT PRINTS IT. The line above accepts "61 of those"
    # from the abstract, so §3's own "61 of the 87" was never examined and `87 → 88` there passed
    # every gate — the article stating one count four times and another once.
    _every_site(prose, r"and (\d+) of the (\d+) do so against wild-type", (str(nr4a3), str(liable)),
                "the wild-type NR4A3 attribution, with the denominator it is a share of")


def test_the_panels_own_rate_is_the_screens_rate(prose, null):
    """45.8% is 87/190 read off the screen, not a figure typed beside it."""
    rate = _pct(null["observed"]["rate_liable"])
    what = "the panel's own liability rate at the adopted criterion (observed.rate_liable)"
    # The abstract states it beside the chimeric null; §3 states it beside the weakest null; §3's
    # geometry sentence opens the 5-6-5 / 5-8-5 / 5-10-5 series with it. All three are this rate.
    _every_site(prose, r"same screen at \d+\.\d% against the panel's (\d+\.\d%)", rate, what)
    _every_site(prose, r"against (\d+\.\d%) for the panel", rate, what)
    # ⚠ ONE SITE IS GONE ON PURPOSE (2026-08-22, page budget). §3's three-geometry series — the
    # share falling 45.8% to 33.1% to 25.4% across 5-6-5, 5-8-5 and 5-10-5 — was moved whole to the
    # extended report to fit the article in six typeset pages. Its binding is deleted rather than
    # loosened, because a pattern kept alive against prose that no longer exists is a guard
    # reporting on nothing.
    #
    # ⛔ THAT NOTE ONCE READ "the two sites above still hold the figure", AND THAT WAS A CENSUS OF A
    # DOCUMENT THAT DID NOT EXIST. Removing the geometry series left THREE sites, not two: §3's
    # adopted-cut sentence states 45.8% a third time, beside a third statement of 40.6%. Both were
    # bound by nothing and both mutated cleanly through every gate. They are bound in
    # `test_the_adopted_cut_is_not_exempt_from_its_own_null`, which owns that sentence and already
    # derives the null it compares against.


def test_the_chimeric_null_the_abstract_quotes_is_the_exon_terminus_arm(prose, null):
    """⭐ THE ARM MATTERS, NOT JUST THE NUMBER. Ten nulls are screened and they span 6.2% to 40.6%.

    The abstract's claim — that most of the liability is what joining two exon termini of these genes
    gives — rests on the `exon_terminus_chimera` arm specifically. Quoting a different arm's rate
    would leave the sentence looking supported while measuring something else.
    """
    arms = null["null_ensembles"]
    chimera = _pct(arms["exon_terminus_chimera"]["rate_liable"])
    _every_site(prose, r"same screen at (\d+\.\d%) against the panel's \d+\.\d%", chimera,
                "the exon-terminus chimeric null, as the abstract states it")
    _every_site(prose, r"meet it at (\d+\.\d%)", chimera,
                "the exon-terminus chimeric null, as §3 states it")
    weakest = min(a["rate_liable"] for a in arms.values())
    _every_site(prose, r"at (\d+\.\d%) against \d+\.\d% for the panel", _pct(weakest),
                f"the weakest of the {len(arms)} nulls screened")
    assert arms["scrambled_mononucleotide"]["rate_liable"] == weakest, \
        "the article names mononucleotide scrambles as the weakest null; the artifact now makes a " \
        "different arm weakest, so the sentence names the wrong one"


def test_the_junction_clearing_ladder_is_the_artifacts_ladder(prose, null):
    """⛔ EVERY RUNG THE PROSE STATES, AGAINST THE CUT IT CLAIMS IT FOR.

    §7 cross-references this ladder, so a rung that drifts silently breaks a claim two sections away.
    The published-breakpoint column is checked with it because the two are quoted as a pair in the
    same sentences and it is the pair, not either count, that carries the availability argument.
    """
    cs = null["cut_sensitivity"]
    junctions = cs["n_junctions"]
    ladder = cs["n_junctions_with_a_clearing_design_by_cut"]
    published = cs["n_published_breakpoint_junctions_with_a_clearing_design_by_cut"]
    n_published = len(cs["published_breakpoint_junctions"])
    # ⛔ BARE PRESENCE IS NOT A BINDING WHEN THE NUMERAL IS NOT DISTINCTIVE. Until 2026-08-22 each
    # rung was `assert re.search(rf"\b{ladder[cut]}\b", prose)`, and every one of those numerals
    # already stood somewhere else in this document: 23 in `<sup>23</sup>`, 9 in
    # `<sup>6,7,8,9,10,11</sup>`, 6 in "*TAF15* exon 6" and thirteen other places, 35 inside "0.35"
    # (`\b` matches after a decimal point). Corrupting a rung passed every gate. So each rung is
    # now captured from the CONSTRUCTION that states it, together with the published-breakpoint
    # count quoted beside it — which had no prose binding of any kind and was asserted against the
    # artifact it came from.
    _every_site(prose, rf"(\d+) of the {junctions}[^.]*?clear(?:s|ing)? the parent screen",
                str(ladder["10"]),
                f"how many of the {junctions} junctions clear the parent screen at the adopted "
                "criterion")
    _every_site(prose, r"and all (\w+) junctions with a published exon-resolved breakpoint have one",
                _word(published["10"]),
                "how many published-breakpoint junctions clear at the adopted criterion")
    assert published["10"] == n_published, (
        "the article says ALL published-breakpoint junctions clear at the adopted criterion; the "
        f"artifact now clears {published['10']} of {n_published}")
    _every_site(prose,
                r"At nine base pairs (\d+) of the (\d+) still clear and (\w+) of the "
                r"(\w+) published ones do",
                (str(ladder["9"]), str(junctions), _word(published["9"]), _word(n_published)),
                "the nine-base-pair rung, with both of its counts and both denominators")
    _every_site(prose,
                r"at eight, (\d+) and (\w+); at seven, (\d+) and (\w+); at six, (\d+) and (\w+)",
                (str(ladder["8"]), _word(published["8"]), str(ladder["7"]), _word(published["7"]),
                 str(ladder["6"]), _word(published["6"])),
                "the loose rungs of the cut ladder, each with its published-breakpoint count")


def test_the_loose_cuts_are_printed_with_the_null_that_makes_them_chance(prose, null):
    """⭐ A LIABILITY RATE WITHOUT ITS NULL IS NOT A READING (round 12).

    The 6 and 7 bp rungs condemn almost the whole panel, and the scrambled null condemns almost the
    whole panel too — so the loose readings are at chance. Both halves have to be present; the count
    alone reads as a finding.
    """
    cs = null["cut_sensitivity"]["observed_cut_ladder"]

    def strongest(cut):
        """⭐ 'THE STRONGEST NULL' IS A DERIVATION OVER THE ARMS, NOT AN ARM NAME.

        The article does not name which of the ten arms is strongest at the loose cuts, and it
        should not have to: whichever it is, it is the one the comparison has to survive. Binding
        this to `exon_terminus_chimera` by name would pass silently on the day another arm
        overtakes it and the sentence stops being true.
        """
        return max(a["cut_ladder"][cut]["rate_liable"] for a in null["null_ensembles"].values())

    for cut in ("6", "7"):
        assert re.search(rf"\b{cs[cut]['n_liable']}\b", prose), \
            f"the {cut} bp rung condemns {cs[cut]['n_liable']} designs and the article omits it"
    # ⭐ ONE CONSTRUCTION, BOTH RATES, so the pair cannot drift apart. The sentence's whole force is
    # that these two numbers are close; checking them separately would let a repair move one.
    _every_site(prose,
                r"strongest null\s+reaches (\d+\.\d%) at seven against the panel's (\d+\.\d%)",
                (_pct(strongest("7")), _pct(cs["7"]["rate_liable"])),
                "the strongest null's rate at a seven-base-pair cut, beside the panel's own")
    assert strongest("6") > cs["6"]["rate_liable"], \
        "the article says that at six the null exceeds the panel outright; the artifact no longer " \
        f"agrees ({_pct(strongest('6'))} null against {_pct(cs['6']['rate_liable'])} panel)"


def test_the_adopted_cut_is_not_exempt_from_its_own_null(prose, null):
    """⭐ THE CLAIM THAT COSTS THE PAPER THE MOST, SO IT IS THE ONE MOST WORTH PINNING.

    §2 says the strongest null falls inside the panel's own 95% interval at the ADOPTED cut, and at
    every cut from seven to thirteen but eleven. An earlier draft quarantined "at chance" to the
    loose cuts of six and seven, which read as though the ten-base-pair criterion escaped the
    comparison; it does not. Both halves are derived here so that neither the exemption nor the
    range can drift back in.

    ⚠ WHICH INTERVAL, AND WHY THE NOMINAL ONE IS THE RIGHT TEST HERE (round 14 seat 3). The extended
    report says the interval "to read" for this rate is the design-effect-corrected one — the 190
    records are 176 distinct molecules tiled at overlapping registers across 38 junctions, so a
    Wilson interval at n=190 is over-narrow; corrected at an effective sample of 133.57 it is
    37.6-54.2% against the nominal 38.9-52.9%. `rate_liable_wilson95` is the NOMINAL interval, and
    that is deliberate for this assertion in one direction only: the corrected interval CONTAINS the
    nominal one, so containment in the nominal implies containment in the corrected, and asserting
    the tighter one is the conservative test of a claim that says the null falls INSIDE. It would be
    the wrong field the day this test is inverted to assert something falls OUTSIDE.
    """
    cs = null["cut_sensitivity"]["observed_cut_ladder"]
    arms = null["null_ensembles"]

    def strongest(cut):
        return max(a["cut_ladder"][cut]["rate_liable"] for a in arms.values())

    inside = [c for c in sorted(cs, key=int)
              if cs[c]["rate_liable_wilson95"][0] <= strongest(c) <= cs[c]["rate_liable_wilson95"][1]]
    assert "10" in inside, (
        "the article says the strongest null falls inside the panel's interval at the adopted "
        f"ten-base-pair cut; the artifact now puts it outside ({_pct(strongest('10'))} against "
        f"{[round(x, 4) for x in cs['10']['rate_liable_wilson95']]})")
    expected = [c for c in sorted(cs, key=int) if 7 <= int(c) <= 13 and c != "11"]
    assert inside == expected, (
        "the article says 'every cut from seven to thirteen but eleven'; the artifact now puts the "
        f"strongest null inside the panel's interval at {inside} rather than {expected}")
    # ⛔ THE THIRD SITE OF BOTH FIGURES, WHICH IS THIS SENTENCE. 45.8% and 40.6% are each stated
    # three times in this article and the other two tests bind two sites each; this sentence prints
    # the third of each, and until 2026-08-22 nothing read it.
    #
    # ⚠ THE NULL IS DERIVED, NEVER NAMED. `exon_terminus_chimera` (0.40568) and
    # `exon_terminus_chimera_novel_acceptor` (0.40513) are 21 draws apart in 38,000 and round to
    # 40.6% and 40.5%. Binding this to the arm by name would leave §3's "meet it at 40.6%" true and
    # "the strongest null's 40.6%" false the day the maximum flips — which is exactly what
    # `strongest()` above exists to prevent.
    _every_site(prose,
                r"the strongest null's (\d+\.\d%) falls inside the panel's own 95% interval on "
                r"(\d+\.\d%)",
                (_pct(strongest("10")), _pct(null["observed"]["rate_liable"])),
                "the strongest null at the adopted cut, beside the panel's own rate")


def test_the_falsification_power_figures_are_derived_not_typed(prose):
    """⛔⛔ ROUND 11 SEATS 2 AND 3, INDEPENDENTLY, P1 — CONVERGENT.

    Both seats hand-recomputed the Discussion's power and void-SD figures via noncentral-t and
    found every one numerically correct as printed, and both found the same gap: no artifact in
    the repository derived them. `aso_falsification_power.py` is that artifact now — it exists
    for exactly this test to import, so the manuscript's five figures have one source rather than
    zero.
    """
    # ⚠ "ABOUT 80%" / "ABOUT 30%", NOT 81.28% / 30.42% — the prose deliberately states power to
    # the nearest ten points rather than printing the noncentral-t calculation's own precision, so
    # the binding rounds the same way rather than demanding a false extra digit of agreement.
    def _nearest_ten(pct):
        return f"{round(pct / 10) * 10}"

    _every_site(
        prose,
        r"six independent biological replicates\s+give about (\d+)% power to falsify a true "
        r"selectivity of (\d+) and three give about (\d+)%",
        (_nearest_ten(aso_falsification_power.power_pct(6)),
         f"{int(aso_falsification_power.TRUE_SELECTIVITY)}",
         _nearest_ten(aso_falsification_power.power_pct(3))),
        "the falsification experiment's power at six and three replicates, against a true "
        "selectivity of 3")
    _every_site(
        prose,
        r"about (\d+\.\d+) at three replicates — (\d+\.\d+) at six, (\d+\.\d+) at ten",
        (f"{aso_falsification_power.void_sd(3):.2f}",
         f"{aso_falsification_power.void_sd(6):.2f}",
         f"{aso_falsification_power.void_sd(10):.2f}"),
        "the realised-SD void thresholds at three, six and ten replicates")


def test_the_coverage_readings_are_both_the_coverage_modules_own(prose):
    """⛔ TWO READINGS, BOTH PRINTED, NEITHER DERIVED BY HAND.

    `aso_reagent_coverage.py` emits what the two named reagents cover and what a third published
    breakpoint would add. The article prints both. Deriving either by subtraction is how the
    112.8% interval got in, so the delta is checked against the module's own field.
    """
    cov = json.load(open(_required(COVERAGE, "the reagent-coverage artifact")))
    two = cov["coverage"]
    three = cov["if_a_third_published_breakpoint_were_added"]
    assert f"{two['percent']}%" in prose, \
        f"the two-reagent coverage {two['percent']}% is not in the article"
    assert f"{three['percent']}%" in prose, \
        f"the three-reagent coverage {three['percent']}% is not in the article"
    lo, hi = two["percent_range"]
    assert 0.0 <= lo <= two["percent"] <= hi <= 100.0, \
        f"the coverage interval {lo}-{hi} does not bracket its own point estimate {two['percent']}"
    # ⛔ IN ORDER, AT THE SITE THAT PRINTS IT. Presence of both endpoints was the whole test until
    # 2026-08-22, so "82.8% to 39.9%" — the range printed backwards — satisfied it, and the
    # ordering assertion above says nothing about the sentence because it reads the artifact.
    _every_site(prose, r"The range (\d+\.\d%) to (\d+\.\d%) quoted with it",
                (f"{lo}%", f"{hi}%"),
                "the two-reagent coverage interval, low end first")
    # ⛔ THE GAIN IS THE MODULE'S OWN FIELD, NOT hi-lo ARITHMETIC IN THE PROSE. Deriving it by
    # subtraction is exactly the shape of the defect that produced a `partner_only` of 1.741.
    assert round(three["percent"] - two["percent"], 1) == three["gain_percentage_points"], \
        "the coverage module's stated gain no longer equals the difference of its own two readings"


def test_no_headline_share_is_printed_outside_zero_to_one_hundred(prose):
    """⛔ THE 112.8% CLASS OF DEFECT, CAUGHT IN THE PROSE RATHER THAN IN THE MODULE.

    A Wilson bound taken over the wrong denominator ran to 112.8% once and reached the manuscript.
    The module that produced it is fixed; this reads the shipped sentences, which is the only place
    the defect is actually visible to a reviewer.
    """
    bad = [m for m in re.findall(r"\b\d+(?:\.\d+)?%", prose)
           if float(m.rstrip("%")) > 100.0]
    assert not bad, f"the article prints share(s) above 100%: {bad}"


# ---------------------------------------------------------------------------------------------
# ⛔⛔ §2 AND §3's HEADLINE COUNTS, WHICH WERE BOUND BY NOTHING AT ALL (round 15 seat 2).
#
# Five numbers a referee reads as measurements — 93, 85, 19, 47 and the pair of parent-duplex
# lengths — were in no pin context and in no `_every_site` pattern, and every one was mutated
# cleanly through the full workflow (mutate, rebuild both journal PDFs, run all thirteen gates).
# The most consequential is the pair the paper's whole product rests on: swap the two named
# reagents' seams, or swap their duplex lengths, and the prose contradicts the table four inches
# below it while nothing fires. `lint_claims` and `lint_style` read the tables file since round 14,
# but both are LANGUAGE linters; nothing joined a table cell to the sentence that restates it.
# ---------------------------------------------------------------------------------------------

PREMRNA = os.path.join(REPO, "research", "modalities", "aso-premrna-offtarget.json")
SEQUENCES = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-sequences.csv")


#: Table 1 of the generated display items — the table §2's sentence restates, four inches above it.
JOURNAL_TABLES = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-journal-tables.md")

#: `| *EWSR1* e12::*NR4A3* e3 | 5′-GGGCATATCATCAAAC-3′ | 3 | 8 bp, wild-type *TFG* | ≥ 26.6 | … |`
_TABLE1_ROW = re.compile(
    r"^\|\s*\*?(?P<donor>[A-Z0-9]+)\*?\s+e(?P<dexon>\d+)::\*?(?P<acc>[A-Z0-9]+)\*?\s+e(?P<aexon>\d+)"
    r"\s*\|\s*(?P<seq>5′-[ACGT]+-3′)\s*\|[^|]*\|\s*(?P<duplex>\d+)\s*bp[^|]*\|\s*"
    r"(?:—|≥\s*(?P<dtm>[\d.]+))\s*\|", re.M)

THERMO = os.path.join(MOD, "junction-aso-thermo.json")


def _named_reagents():
    """The two reagents the paper names, READ OUT OF TABLE 1 — the table §2's sentence restates.

    ★ NOT BY SEQUENCE LITERAL, AND NOT FROM THE CSV'S `role` COLUMN. Typing the two sequences here
    would be a third home for a fact Table 1 owns, and `role` does not distinguish these two from
    the other thirty-five "best available at this junction" rows. Binding prose to the table is also
    exactly the disagreement this test was written for: the mutation that motivated it swapped the
    two reagents between seams, leaving the sentence and the table four inches below it in direct
    contradiction with every gate green.
    """
    text = open(_required(JOURNAL_TABLES, "the generated journal display items"), encoding="utf-8").read()
    named = {}
    for m in _TABLE1_ROW.finditer(text):
        named[m.group("donor")] = m.groupdict()
    return named


def test_the_two_named_reagents_carry_their_own_seams_and_their_own_duplex_lengths(prose):
    """⛔ THE PAIR OF NUMBERS THE PAPER'S PRODUCT RESTS ON, AGAINST THE FILE A LAB ORDERS FROM.

    Mutation-confirmed as unguarded before this test: swapping the two sequences between seams, and
    swapping `eight` and `nine`, each passed every gate. A reader ordering from the prose would get
    the wrong molecule for the patient in front of them — the harm the text-layer guard exists to
    prevent, arriving through attribution rather than through typesetting.
    """
    named = _named_reagents()
    assert {"EWSR1", "TAF15"} <= set(named), (
        "Table 1 no longer lists an EWSR1 and a TAF15 reagent; it lists "
        f"{sorted(named)} — re-anchor this guard, or the paper has changed its product")
    ew, taf = named["EWSR1"], named["TAF15"]
    _every_site(prose,
                r"(5′-[ACGT]{16}-3′) at \*?EWSR1\*? exon (\d+) joined to \*?NR4A3\*? exon (\d+), and\s*"
                r"(5′-[ACGT]{16}-3′) at \*?TAF15\*? exon (\d+)",
                (ew["seq"], ew["dexon"], ew["aexon"], taf["seq"], taf["dexon"]),
                "the two named reagents, each against the seam Table 1 assigns it")
    _every_site(prose,
                r"The \*?EWSR1\*? reagent's longest wild-type parent duplex through the whole gap is\s*"
                r"(\w+) base pairs and the \*?TAF15\*? reagent's is (\w+)",
                (_word(int(ew["duplex"])), _word(int(taf["duplex"]))),
                "each named reagent's longest wild-type parent duplex, in the order §2 states them")
    # ⚠ AND THE ABSTRACT SAYS IT AGAIN, IN ITS OWN CONSTRUCTION. The first version of this test
    # bound §2 alone and the abstract's "of eight and nine base pairs" mutated straight through —
    # the same site-census mistake round 14 recorded against 45.8% and 40.6%, one round later.
    # ⚠ RE-ANCHORED 2026-08-23, AND THE LOOSENING IS BOUNDED ON PURPOSE. Cutting the abstract to
    # Nucleic Acid Therapeutics' 200-word cap rewrote "duplexes through the whole gap of eight and
    # nine" as "gap duplexes eight and nine", and this row went red — correctly: it had stopped
    # matching, which is the failure this file exists to make loud. The pattern now binds the
    # SEMANTIC CORE ("longest wild-type parent ... duplexes ... X and Y base pairs") and lets the
    # connective words between them vary, instead of enumerating one phrasing. ⛔ It is still
    # narrow, and must stay so: §2 states the SAME two numbers in a different construction
    # ("... are eight base pairs against wild-type *EWSR1* and nine against ..."), which this
    # pattern deliberately does not reach — `[\w\s]` cannot cross the `*` of a gene name, and the
    # windows are short enough that "X and Y base pairs" cannot be assembled from it.
    _every_site(prose,
                r"longest wild-type parent[\w\s-]{0,20}duplexes[\w\s]{0,20}?(\w+) and (\w+) base pairs",
                (_word(int(ew["duplex"])), _word(int(taf["duplex"]))),
                "the same two duplex lengths as the abstract states them")


def test_the_two_named_reagents_carry_their_own_dtm_floor(prose):
    """⛔⛔ THE SEVENTH ONE-OF-A-PAIR GUARD (round 11 seat 2, P1). Table 1's "ΔTm floor (°C)"
    column — 26.6 for the *EWSR1* reagent, 36.0 for the *TAF15* one — is generated fresh from
    `fusion-junction-aso-sequences.csv`'s own `predicted_tm_fusion_c` / `predicted_tm_best_parent_c`
    columns every time (`aso_journal_tables.py:_tm`), and `aso_journal_tables.py --check` (gate 8)
    already proves the committed table file reproduces from that generator. What neither of those
    proves is that the CSV's two Tm columns are still what `junction-aso-thermo.json`'s own
    `per_design` records say they are — the artifact this whole thermodynamics claim traces back to.
    Nothing bound the printed floor to that source for the journal article family; this does.
    """
    named = _named_reagents()
    ew, taf = named["EWSR1"], named["TAF15"]
    assert ew.get("dtm") and taf.get("dtm"), (
        "Table 1's ΔTm floor cell did not parse for one or both named reagents — re-anchor "
        "_TABLE1_ROW against the current table text before trusting this test")
    thermo = json.load(open(_required(THERMO, "the junction-thermo artifact")))
    by_seq = {}
    for rec in thermo["per_design"]:
        seq = rec.get("antisense_5to3")
        pair = (rec.get("tm_fusion_duplex_c"), rec.get("tm_best_parent_duplex_c"))
        if seq is not None and None not in pair:
            held = by_seq.setdefault(seq, pair)
            assert held == pair, (
                f"the thermo artifact gives {seq} two different Tm pairs, {held} and {pair} — "
                "this test's lookup assumes one pair per sequence, same as the manifest does")
    for reagent, gene in ((ew, "EWSR1"), (taf, "TAF15")):
        pair = by_seq.get(reagent["seq"].replace("5′-", "").replace("-3′", ""))
        assert pair, f"no thermo record for the {gene} reagent's sequence {reagent['seq']!r}"
        expected = round(pair[0] - pair[1], 1)
        assert float(reagent["dtm"]) == expected, (
            f"Table 1 prints a ΔTm floor of {reagent['dtm']} for the {gene} reagent; "
            f"{THERMO} now computes {expected} ({pair[0]} - {pair[1]})")


def test_the_loose_cut_rungs_are_bound_to_the_cut_each_is_claimed_for(prose, null):
    """⛔ ONE-OF-A-PAIR INSIDE THE FIX FOR ONE-OF-A-PAIR (round 15 seat 2).

    Round 14 replaced bare-presence rungs with construction bindings — for
    `n_junctions_with_a_clearing_design_by_cut`, and not for `observed_cut_ladder[...]["n_liable"]`
    in the next test down, which kept `assert re.search(rf"\\b{n}\\b", prose)`. So swapping the two
    rungs passed every gate, leaving the article saying a LOOSER cut condemns FEWER designs, which
    is impossible for a monotone ladder; and the denominator was read at neither site.
    """
    cs = null["cut_sensitivity"]["observed_cut_ladder"]
    n = null["cut_sensitivity"]["n_designs"]
    _every_site(prose,
                rf"the loose cuts condemn almost everything: (\d+) of (\d+) at seven and (\d+) at six",
                (str(cs["7"]["n_liable"]), str(n), str(cs["6"]["n_liable"])),
                "the loose-cut design counts, each against the cut it is claimed for")
    assert cs["6"]["n_liable"] >= cs["7"]["n_liable"], (
        "the artifact now condemns fewer designs at six than at seven, which is impossible for a "
        "monotone ladder — the screen, not the prose, has gone wrong")


def test_the_union_of_the_two_screens_and_the_own_parent_share_are_derived(prose, pairing):
    """⛔ 93 AND 85 ARE DERIVATIONS OVER THE PER-DESIGN RECORDS, NOT NUMBERS BESIDE THEM.

    The article says the two screens condemn 93 of 190 "as a union rather than a sum", and that 85
    of the 87 are paired by one of the design's own two parent genes. Both were free to drift.
    Deriving them is also the only way to keep the union honest: 87 + 19 = 106, and the sentence's
    whole point is that the answer is not that.
    """
    per = pairing["per_design"]
    liable = {(d["junction"], d["antisense_5to3"]) for d in per if d.get("counts_as_liability")}
    pre = json.load(open(_required(PREMRNA, "the precursor-RNA screen")))["per_design"]
    invisible = {(d["junction_label"], d["antisense_5to3"]) for d in pre
                 if (d.get("n_invisible_to_mature_screens") or 0) > 0}
    own = sum(1 for d in per if d.get("counts_as_liability")
              and d.get("parent") in re.match(r"^([A-Z0-9]+)_e\d+__([A-Z0-9]+)_e\d+$",
                                              d["junction"]).groups())
    _every_site(prose, r"(\d+) designs carry a sense-strand near-match in parent precursor RNA",
                str(len(invisible)), "the precursor-RNA class, from its own screen")
    _every_site(prose, r"(\d+) are paired by one of the design's own two parent genes",
                str(own), "how many of the liable designs are paired by their OWN parents")
    _every_site(prose, r"the two screens condemn (\d+) of the (\d+)",
                (str(len(liable | invisible)), str(pairing["corpus"]["n_designs"])),
                "the union of the two screens, derived over the per-design records")


# ---------------------------------------------------------------------------
# Round 18 (AUT-PD-082): the three refuted interpretation claims, and the
# Introduction sibling that carried the fourth copy of the same overclaim.
#
# ⛔ WHY THESE THREE GUARDS EXIST. The claim audit
# (`fusion-junction-aso-claim-audit-verdicts.json`, seat s33-claimaudit) refuted three
# INTERPRETATION sentences, and every one failed the same way: a bare universal quantifier
# ("at any threshold", "every design here", "most plausible") over a panel whose own artifacts
# return exceptions. The repairs replaced each universal with the bounded statement plus the
# observation that bounds it — which puts three new counts into the prose that nothing read.
# An unbound number is how the universal grows back: reword the sentence, drop the seven, and
# "mostly, not wholly, invisible" reads as "invisible" again with every gate still green.
#
# ★ EACH COUNT IS RECOMPUTED HERE FROM THE ARTIFACT, never asserted against a literal. The
# identity block in particular re-splices the mature parents rather than reading a stored field,
# because no committed field holds it: the refutation exists precisely because the alignment
# screens never report identity at a parent site — they exclude parent records by name first.
SCREEN_E10 = os.path.join(MOD, "junction-aso-offtarget-e10n3.json")
PREMRNA_SEQS = os.path.join(MOD, "aso-premrna-sequences.json")
ENERGY = os.path.join(MOD, "aso-offtarget-duplex-energy.json")

_COMPLEMENT = str.maketrans("ACGTU", "TGCAA")


def _revcomp(s):
    return s.translate(_COMPLEMENT)[::-1]


def _mature(seqs, gene):
    """The spliced parent transcript, assembled from the exon spans the artifact records.

    ⚠ The gap-pairing screen's `parent_start_0based` indexes THIS, not the pre-mRNA: reproducing
    `method.parent_nt_searched` from the spans is the check that the two agree.
    """
    g = seqs["genes"][gene]
    return "".join(g["sequence"][a:b + 1] for a, b in g["exon_spans_0based_inclusive"])


PREMRNA_OFFTARGET = os.path.join(MOD, "aso-premrna-offtarget.json")

_JUNCTION = re.compile(r"^([A-Z0-9]+)_e\d+__([A-Z0-9]+)_e\d+$")


def _longest_run(a, b):
    best = cur = 0
    for x, y in zip(a, b):
        cur = cur + 1 if x == y else 0
        best = max(best, cur)
    return best


def _own_parent_runs(pairing):
    """The longest run a design's OWN parent forms, over BOTH compartments the sentence names.

    ⛔⛔ WHY BOTH. The first version of this guard read `longest_parent_duplex_bp_through_gap` alone
    and so measured the MATURE arm only, while the sentence it bound named the mature transcript AND
    the precursor splice junction in its own antecedent. A blind regression seat found the gap on the
    commit that introduced it: the precursor arm carries a 14-base-pair hybridisable run, one longer
    than the mature maximum, so an unscoped "no parent pairs more than 13" was false as written.

    ★ AND THE SCOPE THAT MAKES IT TRUE IS "ITS OWN PARENT", NOT "A PARENT". That 14-mer is TCF12
    against a TFG::NR4A3 design — TCF12 is a parent gene of the panel and not a parent of that
    design. Both readings are defensible English and only one of them is what the paragraph is
    about, so the guard computes the one the sentence claims and the prose says which it means.
    """
    runs = [d["longest_parent_duplex_bp_through_gap"] for d in pairing["per_design"]
            if d.get("counts_as_liability")]
    seqs = json.load(open(_required(PREMRNA_SEQS, "the parent transcript sequences")))
    pre = json.load(open(_required(PREMRNA_OFFTARGET, "the precursor-RNA off-target screen")))
    for d in pre["per_design"]:
        m = _JUNCTION.match(d["junction_label"])
        assert m, f"{d['junction_label']!r} is not a junction label this guard can read"
        parents = set(m.groups())
        target = _revcomp(d["antisense_5to3"])
        for hit in d.get("hits", ()):
            if not hit.get("hybridisable") or hit["gene"] not in parents:
                continue
            site = seqs["genes"][hit["gene"]]["sequence"][
                hit["premrna_start_0based"]:hit["premrna_end_0based"] + 1]
            runs.append(_longest_run(site, target))
    assert runs, "no own-parent runs were measured at all, so the bound below is unmeasured"
    return runs


@pytest.fixture(scope="module")
def parent_site_identity(pairing):
    """Identity of each liable design against its parent, at the site the screen names.

    Returns the list of match counts out of the oligo length, one per liable design.
    """
    seqs = json.load(open(_required(PREMRNA_SEQS, "the parent transcript sequences")))
    mature = {gene: _mature(seqs, gene) for gene in pairing["method"]["parents_searched"]}
    for gene, nt in pairing["method"]["parent_nt_searched"].items():
        assert len(mature[gene]) == nt, (
            f"the spliced {gene} transcript is {len(mature[gene])} nt and the screen says it "
            f"searched {nt} — the spans and the screen disagree, so no identity computed against "
            "them can be trusted")
    n = pairing["method"]["oligo_len"]
    out = []
    for d in pairing["per_design"]:
        if not d.get("counts_as_liability"):
            continue
        start = d["parent_start_0based"]
        site = mature[d["parent"]][start:start + n]
        assert len(site) == n, f"the parent site for {d['junction']} runs off the transcript"
        out.append(sum(1 for a, b in zip(site, _revcomp(d["antisense_5to3"])) if a == b))
    return out


def test_the_parent_visibility_the_article_states_is_recomputed_not_asserted(
        prose, pairing, parent_site_identity):
    """⛔ THE REFUTED CLAIM: "invisible … at ANY threshold that instrument is normally run at".

    It is not. Recomputing identity at each liable design's own parent site — the site the
    gap-pairing screen names, against the mature parent spliced from its own exon spans — gives a
    distribution that reaches the near-match threshold the manuscript's alignment screens run at.
    The universal was wrong; the mechanism it was reaching for is right for most of the panel, and
    what actually keeps every parent off the returned lists is `method.parent_set`, an explicit
    exclusion by name and accession, not the threshold.

    ★ BOTH HALVES ARE DERIVED: the count from the recomputation, the threshold from a screen's own
    `method.near_match_threshold`. Re-run the screen at another threshold and this fails here
    rather than shipping a sentence under a threshold nobody used.
    """
    n = pairing["method"]["oligo_len"]
    screen = json.load(open(_required(SCREEN_E10, "an alignment screen, for its threshold")))
    m = re.search(r"(\d+)\s*/\s*(\d+)", screen["method"]["near_match_threshold"])
    assert m, ("the alignment screen no longer states its near-match threshold as k/n, so the "
               "identity the article quotes cannot be tied to it")
    cut, denom = int(m.group(1)), int(m.group(2))
    assert denom == n, (f"the alignment screen calls a near-match at {denom} bases and the panel "
                        f"is tiled at {n} — the article's identity claim spans two geometries")
    reaching = sum(1 for i in parent_site_identity if i >= cut)
    assert 0 < reaching < len(parent_site_identity), (
        "the recomputation puts either none or all of the liable designs at the near-match "
        f"threshold ({reaching} of {len(parent_site_identity)}); 'mostly, not wholly, invisible' "
        "is then the wrong sentence in one direction or the other")
    _every_site(prose,
                r"(\w+) of the (\d+) liable designs reach their parent at the (\d+)-of-(\d+) "
                r"identity these screens run at",
                (_word(reaching), str(len(parent_site_identity)), str(cut), str(denom)),
                "how many liable designs the ordinary screen's own threshold would reach")


def test_the_shared_sequences_the_article_concedes_are_the_panels_own(prose, pairing):
    """⛔ THE REFUTED CLAIM: "EVERY design here being specific to the exon pair it was tiled at".

    The panel's own rows say otherwise, and so does this paper's Figure 1 legend — "One 16-mer
    spans three partners' breakpoints" — which is the one-of-a-pair shape at its plainest: two
    sentences of one document contradicting each other, with nothing reading either.

    ★ DERIVED BY GROUPING `per_design` on the antisense sequence. Both numbers move together if
    the panel is re-tiled, so neither can drift alone.
    """
    by_seq = {}
    for d in pairing["per_design"]:
        by_seq.setdefault(d["antisense_5to3"], set()).add(d["junction"])
    shared = sum(1 for junctions in by_seq.values() if len(junctions) > 1)
    _every_site(prose, r"(\w+) of the panel's (\d+) distinct sequences",
                (_word(shared), str(len(by_seq))),
                "how many of the panel's distinct sequences sit at more than one exon pair")


def test_the_strongest_returned_liability_is_the_two_screens_own(prose, pairing):
    """⛔ THE REFUTED CLAIM: a junction design's "MOST PLAUSIBLE" wild-type liability is its parent.

    Refuted as a comparative ranking on this repository's own artifacts: the parent screen never
    returns a run longer than its panel maximum, while the energy re-evaluation returns off-target
    duplexes paired over the whole oligo at ddG 0.000, in curated RefSeq records rather than
    predicted models — so the paper's own "mostly predicted transcript models" caveat does not
    dispose of them. The honest bound stays in the sentence: the alignment screen excludes parent
    records by name, so the two arms are not on a common scale.

    ★ THE CURATED COUNT IS THE ONE THAT CARRIES THE ARGUMENT, so it is derived from the accession
    prefixes rather than from the seat's report of them: RefSeq NM_/NR_ are curated, XM_/XR_ are
    model-predicted. (The audit verdict said six of eight; recomputing gives five — recorded as a
    correction on the verdict record.)
    """
    energy = json.load(open(_required(ENERGY, "the off-target duplex-energy re-evaluation")))
    n = pairing["method"]["oligo_len"]
    longest_parent = max(_own_parent_runs(pairing))
    full = [d for d in energy["designs"] if d.get("max_run_len_hybridisable") == n]
    assert len(full) == energy["summary"]["n_designs_with_a_fully_paired_offtarget_duplex"], (
        "the fully-paired designs recomputed from max_run_len_hybridisable disagree with the "
        "artifact's own summary count — one of the two is wrong and the prose rests on both")
    records = [(d.get("closest_gap_paired_record") or {}) for d in full]
    curated = sum(1 for r in records if r.get("acc", "").startswith(("NM_", "NR_")))
    # ⚠ TWO INDEPENDENT MARKERS OF THE SAME FACT, ASSERTED AGAINST EACH OTHER. The accession prefix
    # says curated (NM_/NR_) or model-predicted (XM_/XR_); RefSeq also writes "PREDICTED:" at the
    # head of a model record's definition. If the two ever disagree, the classification the sentence
    # rests on is not established and the count must not be printed as though it were.
    for r in records:
        predicted_by_prefix = r.get("acc", "").startswith(("XM_", "XR_"))
        predicted_by_defn = r.get("defn", "").startswith("PREDICTED:")
        assert predicted_by_prefix == predicted_by_defn, (
            f"{r.get('acc')!r} is classed one way by its accession prefix and the other by its "
            f"definition ({r.get('defn', '')[:40]!r}) — the curated count in the article rests on "
            "the two agreeing")
    assert longest_parent < n, (
        f"a parent now pairs {longest_parent} of {n} bases, so the comparison the sentence draws "
        "between the two arms no longer runs in the direction it states")
    _every_site(prose,
                r"no design's own parent pairs more than (\d+) base pairs in either compartment, "
                r"against the whole (\d+) for the (\w+) fully paired off-target duplexes above, "
                r"(\w+) of them curated records",
                (str(longest_parent), str(n), _word(len(full)), _word(curated)),
                "the two arms' strongest returns, and how many of the fully paired are curated")


# ⛔⛔ THE QUANTIFIER IS THE CLAIM HERE, AND EVERY GUARD ABOVE READS ONLY THE NUMBERS.
# §8a of `paper-hardening`: "a claim is a QUANTITY and a RELATION, and the whole guard set was built
# on the quantity half". This round's four repairs ARE the relation half — each replaced a universal
# with a bounded quantifier — so binding only their counts would leave the thing that was actually
# wrong unwatched. Deleting ", not wholly," from the first sentence leaves every count correct, every
# pattern above matching, and the paper back to the claim the audit refuted.
#
# ★ REQUIRE AND FORBID ARE ASSERTED SEPARATELY, because "the narrowed wording is present" and "the
# universal is absent" fail differently: a rewrite can satisfy the first while reintroducing the
# second somewhere else in the same paragraph.
#
# ⛔⛔ AND THE FORBID SIDE IS A CLASS PATTERN, NEVER THE SENTENCE THAT WAS THERE. This repository has
# already paid for the other shape:
# `test_universal_claims_are_scoped_to_what_was_measured.py` records that five of its six sections
# shipped as EXACT-STRING BLACKLISTS, and every one of the six contradictions it existed to stop
# could be reinstated in synonyms with no test turning red. So each `forbid` below matches the
# QUANTIFIER GOVERNING THE NOUN — a universal over `design(s) ... specific to`, a superlative over
# `liability`, a `never/no ... returns a parent`, an `at any/every threshold` beside `invisible` —
# and the synonym reinstatements are in this file's mutation record, not left to inspection.
NARROWED_QUANTIFIERS = [
    ("the Introduction's account of what an ordinary off-target search returns",
     "of a conventional off-target search, though not for every design",
     r"(?:never|not once|no(?:t a)? single)\s+(?:\w+\s+){0,3}returns?\s+(?:a|the|any)\s+parent"
     r"|returns?\s+no\s+parent"
     r"|cannot\s+return\s+(?:a|the|any)\s+parent"),
    ("§Selection's account of how visible the parent liability is",
     "is mostly but not wholly invisible to the instrument",
     r"invisible[^.]{0,80}\bat\s+(?:any|every|all|whatever)\s+(?:threshold|cut|setting)"
     r"|\bat\s+(?:any|every|all|whatever)\s+(?:threshold|setting)[^.]{0,80}invisible"),
    ("§Test articles' account of how junction-specific the panel is",
     "most designs here are specific to the exon pair they were tiled at",
     r"\b(?:every|each|all|any)\s+designs?\s+(?:here\s+)?(?:being\s+|is\s+|are\s+|was\s+|were\s+)?"
     r"specific\s+to\s+(?:the|its|their)\s+(?:exon\s+pair|junction)"),
    ("§Interpretation's account of which wild-type liability is strongest",
     "The wild-type liability that follows from a junction design's construction is its own parent",
     r"\b(?:most|more)\s+(?:plausible|likely|probable|credible)\b[^.]{0,40}\bliability"
     r"|\bliability[^.]{0,40}\b(?:most|more)\s+(?:plausible|likely|probable|credible)\b"
     r"|\b(?:strongest|principal|dominant|chief|foremost|greatest)\s+"
     r"(?:predicted\s+|wild-type\s+|)liability\s+is\s+its\s+own\s+parent"),
]


@pytest.mark.parametrize("what,require,forbid", NARROWED_QUANTIFIERS,
                         ids=[q[0].split("'")[0] for q in NARROWED_QUANTIFIERS])
def test_the_narrowed_quantifiers_stay_narrow(prose, what, require, forbid):
    """⛔ EACH OF THESE FOUR SENTENCES CARRIED A UNIVERSAL THAT THIS PAPER'S OWN ARTIFACTS REFUTE.

    Verdicts: `fusion-junction-aso-claim-audit-verdicts.json`, lines 194, 295 and 348, plus the
    Introduction sibling that carried the fourth copy — two of the four were contradicted by this
    document's own text (the Figure 1 legend, and the next sentence).

    ⚠ IF THIS FAILS, CHECK THE MEANING BEFORE THE REGEX. The narrowed wording is the finding, not a
    phrasing preference: re-anchoring this guard to a reworded sentence is only correct when the new
    sentence says the same bounded thing. A sentence that has become universal again is the defect
    this guard exists for, and it will look exactly like a rewording.
    """
    flat = _flat(prose)
    assert require in flat, (
        f"{what} no longer carries its narrowed wording ({require!r}). If the sentence was reworded, "
        "check that it still bounds the claim before you re-anchor this guard — the audited defect "
        "was a bare universal, and a rewrite that drops the bound looks identical to one that keeps it")
    found = re.search(forbid, flat)
    assert not found, (
        f"{what} has gone universal again: {found.group(0)!r} is the wording the claim audit refuted, "
        "and the artifacts that refuted it have not changed")


GAP_TRADEOFF = os.path.join(MOD, "aso-gap-length-tradeoff.json")


def test_the_three_geometries_are_reported_as_a_rate_and_not_a_bare_count(prose):
    """⛔ THE RAW COUNT POINTED THE OPPOSITE WAY FROM THE DENOMINATED ONE (round 18, seat 3).

    The article said "across three geometries the liable count does not fall", which is true — 87,
    88, 87 — and it was the whole evidence that a longer catalytic gap does not buy the design out
    of the liability. The three panels are 190, 266 and 342 designs, sizes the article never printed,
    so the rate falls 45.8% -> 33.1% -> 25.4% and the count is not even monotone. A statistic whose
    denominator is withheld is not a weaker version of the claim; it is the reverse of it.

    ★ AND THE LAST FIGURE IS A CONSTRUCTION ARTEFACT, WHICH THE PROSE NOW SAYS. MIN_DUPLEX_BP is an
    absolute hybrid length that does not scale with the gap, so at 5-10-5 the catalytic gap alone is
    already a ten-base-pair hybrid and every gap-pairing window clears the criterion by construction
    — the artifact's own `_threshold_note`, and visible here as the two counts converging.
    """
    geoms = json.load(open(_required(GAP_TRADEOFF, "the gap-length trade-off series")))["geometries"]
    present = [g for g in geoms if g.get("present")]
    assert len(present) == 3, (
        f"the series now holds {len(present)} measured geometries, not the three the article "
        "reports — the sentence names its own denominators and must follow the artifact")
    counts = [g["mature_parent_whole_gap_duplex"]["n_at_or_above_min_duplex_bp"] for g in present]
    sizes = [g["n_fusion_specific_designs"] for g in present]
    rates = [_pct(c / n) for c, n in zip(counts, sizes)]
    _every_site(prose,
                r"the liable count holds at (\d+), (\d+) and (\d+) while the panel grows from (\d+) "
                r"designs to (\d+) and (\d+), so the rate falls from ([\d.]+%) to ([\d.]+%) and "
                r"([\d.]+%)",
                tuple(str(c) for c in counts) + tuple(str(n) for n in sizes) + tuple(rates),
                "the three geometries' liable counts, their panel sizes and the resulting rates")
    last = present[-1]["mature_parent_whole_gap_duplex"]
    assert last["n_with_any_gap_pairing_window"] == last["n_at_or_above_min_duplex_bp"], (
        "the two counts no longer converge at the longest geometry, so the article's 'met by the "
        "catalytic gap alone, so that last figure is a floor' has lost the observation behind it")


def test_the_ddg_separations_are_reported_with_the_direction_their_artifact_records(prose):
    """⛔ A ONE-DIRECTIONAL BOUND QUOTED AS A POINT VALUE READS AS MARGIN (round 18, seat 5).

    The article's evidence that neither named reagent falls in the fully-paired or within-2-kcal
    classes is "the closest to each being 3.2 and 3.0 kcal/mol weaker". Its own artifact says, in a
    field written for exactly this: scoring only the longest perfectly paired run "UNDERSTATES a
    near-match's true stability and therefore OVERSTATES its separation from the intended duplex.
    Every ddG here is an upper bound on that separation." Beside a concern band the paper itself
    sets at 2 kcal/mol, dropping that direction turns a ceiling into a clearance.

    ⚠ AND THE OTHER BOUND MUST NOT BE MERGED IN. The artifact also records that unmodelled LNA
    points the other way and that the two "are not a range and must not be quoted as one", so this
    guard requires the run-length direction and does NOT ask for a two-sided interval.

    ★ THE REQUIREMENT IS DERIVED FROM THE ARTIFACT'S OWN FIELD, so if that field is ever rewritten
    to say something else, this fails rather than going on enforcing a sentence nobody stands behind.
    """
    energy = json.load(open(_required(ENERGY, "the off-target duplex-energy re-evaluation")))
    field = next((v for k, v in energy.items()
                  if "bound" in k and "one_way" in k and isinstance(v, str)), None)
    assert field and "upper bound on that separation" in field, (
        "the energy artifact no longer records that its ddG values are upper bounds on the "
        "separation; the article's wording below was derived from that field and must be re-derived "
        "rather than left standing")
    flat = _flat(prose)
    assert "upper bounds on" in flat and "that separation" in flat, (
        "the article quotes the ddG separations without the direction its artifact records. Every "
        "ddG there is an UPPER bound on the separation, so a bare 3.2 / 3.0 reads as more margin "
        "than was measured — beside a concern band this paper sets at 2 kcal/mol.")
    assert "range" not in flat.split("upper bounds on")[1][:200], (
        "the two bounds point opposite ways and the artifact says they must not be quoted as a "
        "range; this sentence appears to have merged them")
