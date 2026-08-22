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


def _every_site(prose, pattern, expected, what):
    """⛔⛔ EVERY SITE THAT STATES THE QUANTITY, NOT WHETHER IT APPEARS SOMEWHERE.

    The first draft of this file asserted `value in prose`, and a mutation test walked straight
    through it: 45.8% is stated at three sites and 40.6% at two, so corrupting ONE left the others
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


def test_the_panels_own_rate_is_the_screens_rate(prose, null):
    """45.8% is 87/190 read off the screen, not a figure typed beside it."""
    rate = _pct(null["observed"]["rate_liable"])
    what = "the panel's own liability rate at the adopted criterion (observed.rate_liable)"
    # The abstract states it beside the chimeric null; §3 states it beside the weakest null; §3's
    # geometry sentence opens the 5-6-5 / 5-8-5 / 5-10-5 series with it. All three are this rate.
    _every_site(prose, r"same screen at \d+\.\d% against the panel's (\d+\.\d%)", rate, what)
    _every_site(prose, r"against (\d+\.\d%) for the panel", rate, what)
    _every_site(prose, r"does — (\d+\.\d%) to \d+\.\d% to \d+\.\d%", rate, what)


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
    for cut in ("10", "9", "8", "7", "6"):
        assert re.search(rf"\b{ladder[cut]}\b", prose), \
            f"at a {cut} bp cut the artifact clears {ladder[cut]} of {junctions} junctions and that " \
            "count is not in the article"
    _every_site(prose, rf"(\d+) of the {junctions}[^.]*?clear(?:s|ing)? the parent screen",
                str(ladder["10"]),
                f"how many of the {junctions} junctions clear the parent screen at the adopted "
                "criterion")
    assert published["10"] == 5, \
        "the article says all five published-breakpoint junctions clear at the adopted criterion; " \
        f"the artifact now says {published['10']}"
    assert published["7"] == 0 and published["6"] == 0, \
        "the article says none of the published junctions clears at seven or six; the artifact now " \
        f"says {published['7']} and {published['6']}"


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
                r"ensembles reaches (\d+\.\d%) at seven against the panel's (\d+\.\d%)",
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
    assert f"{lo}%" in prose and f"{hi}%" in prose, \
        f"the two-reagent interval {lo}-{hi}% is not printed with its point estimate"
    assert 0.0 <= lo <= two["percent"] <= hi <= 100.0, \
        f"the coverage interval {lo}-{hi} does not bracket its own point estimate {two['percent']}"
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
