#!/usr/bin/env python3
"""Every clustered-interval figure in §2.5 is recomputed from the artifact and matched to the prose.

⛔ WHY THIS EXISTS. On 2026-08-19 §2.5 printed "a design effect of 1.43, an effective sample of 133
and an interval of 37.5–54.3%". Recomputing it from `aso-parent-gap-pairing.json` gives 1.42, 134
and 37.6–54.2%. Nothing was wrong with the paper's conclusion and no reader would have been misled
about the result — but three numbers had been typed from a one-off calculation whose method was
never written down, so nobody could tell whether the difference was a rounding convention, a
different intraclass-correlation estimator, or an arithmetic slip. A statistic that exists in one
place and is checked by nothing is not a reported quantity; it is a remembered one.

★ THIS TEST IS THE DEFINITION, NOT A CHECK OF IT. The estimator is fixed here and stated in the
prose: one-way analysis of variance on the 38 junctions, equal cluster size 5, design effect
1 + (m − 1)·ICC, effective sample n/deff, and a Wilson 95% interval evaluated at that effective
sample with no intermediate rounding. If a future recomputation wants a different estimator, it
changes this file and the sentence together — which is the point, because that is the change a
reader would need to be told about.

⚠ THE SECOND ARM IS THE ONE WORTH READING. The *NR4A3*-specific arm has a design effect BELOW one
(0.82): the five registers tiled from one junction disagree about *NR4A3* more than two designs
drawn at random would. A design effect below one would NARROW the interval, and narrowing a real
interval on the strength of a slightly negative variance-component estimate is a precision claim the
data does not support. The paper reports the nominal interval there and says so; this test asserts
the deff is in fact below one, so the sentence explaining why cannot outlive the fact it explains.
"""
from __future__ import annotations

import collections
import json
import math
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
PAPER = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-research-article.md")
PAIRING = os.path.join(REPO, "research", "modalities", "aso-parent-gap-pairing.json")

#: The registers tiled from each junction. Asserted rather than assumed — an unequal panel would
#: make the equal-cluster-size design effect below the wrong formula, silently.
REGISTERS_PER_JUNCTION = 5

Z = 1.959963984540054  # two-sided 95%


def _paper() -> str:
    if not os.path.exists(PAPER):
        pytest.skip("the manuscript is not present in this checkout")
    return " ".join(open(PAPER, encoding="utf-8").read().split())


def _by_junction():
    if not os.path.exists(PAIRING):
        pytest.skip("aso-parent-gap-pairing.json is not present in this checkout")
    byj = collections.defaultdict(list)
    for rec in json.load(open(PAIRING, encoding="utf-8"))["per_design"]:
        byj[rec["junction"]].append(rec)
    sizes = {len(v) for v in byj.values()}
    assert sizes == {REGISTERS_PER_JUNCTION}, (
        f"the panel is no longer {REGISTERS_PER_JUNCTION} registers per junction ({sizes}); the "
        "equal-cluster-size design effect below no longer applies — use the unequal-size form")
    return byj


def _wilson(k: float, n: float) -> tuple[float, float]:
    p = k / n
    den = 1 + Z * Z / n
    centre = (p + Z * Z / (2 * n)) / den
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return 100 * (centre - half), 100 * (centre + half)


def _clustered(pred):
    """ANOVA design effect and effective sample for a 0/1 outcome over equal-size clusters."""
    byj = _by_junction()
    flags = {j: [1 if pred(r) else 0 for r in v] for j, v in byj.items()}
    counts = [sum(v) for v in flags.values()]
    k, m = len(counts), REGISTERS_PER_JUNCTION
    n = k * m
    p = sum(counts) / n
    msb = sum(m * (c / m - p) ** 2 for c in counts) / (k - 1)
    msw = sum(sum((x - c / m) ** 2 for x in flags[j])
              for j, c in zip(flags, counts)) / (n - k)
    icc = (msb - msw) / (msb + (m - 1) * msw)
    deff = 1 + (m - 1) * icc
    return sum(counts), n, p, deff, n / deff


def _liable(r):
    return bool(r["counts_as_liability"])


def _liable_nr4a3(r):
    return bool(r["counts_as_liability"]) and r["parent"] == "NR4A3"


def test_the_aggregate_arm_prints_the_design_effect_it_actually_has():
    k, n, p, deff, neff = _clustered(_liable)
    assert (k, n) == (87, 190), (k, n)
    lo, hi = _wilson(p * neff, neff)
    txt = _paper()
    sentence = (f"gives a design effect of {deff:.2f}, an effective sample of {round(neff)} and an "
                f"interval of {lo:.1f}–{hi:.1f}%")
    assert sentence in txt, (
        f"§2.5 does not carry the clustered figures the artifact gives. Expected: {sentence!r}. "
        "Recompute the sentence rather than the estimator.")


def test_the_aggregate_arm_still_prints_its_nominal_interval_beside_the_clustered_one():
    """The nominal interval is what the clustered one is contrasted with; dropping it strands the
    word "nominal" and leaves a reader unable to see which direction clustering moved the answer."""
    k, n, _, _, _ = _clustered(_liable)
    lo, hi = _wilson(k, n)
    assert f"Wilson 95% interval of {lo:.1f}–{hi:.1f}%" in _paper()


def test_the_nr4a3_arm_carries_an_interval_where_it_is_compared_to_a_null():
    """⛔ 32.1% was compared against a 28.8% null with no interval of any kind attached to it."""
    k, n, _, _, _ = _clustered(_liable_nr4a3)
    assert (k, n) == (61, 190), (k, n)
    lo, hi = _wilson(k, n)
    assert f"nominal interval is {lo:.1f}–{hi:.1f}%" in _paper(), (
        f"the *NR4A3* arm is compared to a null without an interval; it is {lo:.1f}–{hi:.1f}%")


def test_the_nr4a3_arms_design_effect_is_below_one_and_the_paper_says_which_way_that_cuts():
    """The explanation in the prose is only honest while the deff really is sub-binomial."""
    _, _, _, deff, _ = _clustered(_liable_nr4a3)
    assert deff < 1, (
        f"the *NR4A3* arm's design effect is now {deff:.3f}, not below one. §2.5 reports the "
        "nominal interval there BECAUSE clustering would narrow it; that sentence is now wrong")
    txt = _paper()
    #: ⚠ RE-ANCHORED 2026-08-19: "arm" carried five senses in this paper, two of them alternating
    #: inside this very paragraph — a drawn null ensemble and an observed sub-analysis — while their
    #: rates were being compared. The *NR4A3* one is now "sub-analysis" and "arm" is left to the
    #: nulls, so the pin follows the wording rather than holding the collision in place.
    assert f"its design effect is {deff:.2f} rather than" in txt
    assert "A design effect below one would narrow the interval" in txt, (
        "the reason the nominal interval is reported for this arm has been dropped")
