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

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MANUSCRIPTS))
ASO = os.path.join(MANUSCRIPTS, "aso")
MOD = os.path.join(REPO, "research", "modalities")

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

#: `| *EWSR1* e12::*NR4A3* e3 | 5′-GGGCATATCATCAAAC-3′ | 3 | 8 bp, wild-type *TFG* | … |`
_TABLE1_ROW = re.compile(
    r"^\|\s*\*?(?P<donor>[A-Z0-9]+)\*?\s+e(?P<dexon>\d+)::\*?(?P<acc>[A-Z0-9]+)\*?\s+e(?P<aexon>\d+)"
    r"\s*\|\s*(?P<seq>5′-[ACGT]+-3′)\s*\|[^|]*\|\s*(?P<duplex>\d+)\s*bp", re.M)


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
    _every_site(prose,
                r"longest wild-type parent duplexes through the whole gap of (\w+) and (\w+) base pairs",
                (_word(int(ew["duplex"])), _word(int(taf["duplex"]))),
                "the same two duplex lengths as the abstract states them")


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
