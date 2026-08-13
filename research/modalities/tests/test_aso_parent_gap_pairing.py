#!/usr/bin/env python3
"""The mature-parent gap-pairing screen, tied to the manuscript sentences that quote it.

⛔ WHY THIS EXISTS. This screen was added on 2026-08-13 because an adversarial review found that
five of the nine designs the manuscript called clean form an 11- or 12-base-pair duplex with a
mature wild-type parent that pairs the whole catalytic gap — one of them with wild-type NR4A3, the
transcript the modality must spare. None of the three screens that preceded it could see that: the
alignment screen excludes parent records and filters at >=14/16 identity, the exhaustive scan admits
<=1 mismatch, and the pre-mRNA arm searches unspliced sequence and so cannot reach a mature
exon-exon junction.

A finding that arrived by review is exactly the kind that drifts back out again when the prose is
next edited, so every number the manuscript states about it is asserted here against the artifact
rather than against a remembered value. A failure means the two have diverged — fix whichever is
wrong, and do not relax the assertion.
"""
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MOD))
ART = os.path.join(MOD, "aso-parent-gap-pairing.json")
PAPER = os.path.join(REPO, "research", "manuscripts", "aso",
                     "fusion-junction-aso-short-communication.md")
sys.path.insert(0, MOD)


def _art():
    if not os.path.exists(ART):
        pytest.skip("parent gap-pairing artifact is not present in this checkout")
    return json.load(open(ART, encoding="utf-8"))


def _paper():
    if not os.path.exists(PAPER):
        pytest.skip("submission manuscript is not present in this checkout")
    return open(PAPER, encoding="utf-8").read()


def _flat(txt):
    return re.sub(r"\s+", " ", txt)


def test_the_corpus_counts_match_the_manuscript():
    c = _art()["corpus"]
    txt = _flat(_paper())
    assert c["n_designs"] == 190
    assert f"{c['n_with_parent_duplex_through_gap']} of {c['n_designs']} pair" in txt
    nr4a3 = c["which_parent_supplies_it"]["NR4A3"]
    assert f"{nr4a3} of those against wild-type *NR4A3*" in txt


def test_the_margin_gradient_matches_the_manuscript():
    """The gradient is the reason the paper can still recommend by margin. It must be quoted right."""
    by = _art()["corpus"]["by_gap_specificity_margin"]
    txt = _flat(_paper())
    for m in ("1", "2", "3"):
        b = by[m]
        assert f"{b['n_with_parent_duplex']} of {b['n_designs']}" in txt, f"margin {m}"
    assert by["1"]["n_with_parent_duplex"] > by["2"]["n_with_parent_duplex"] > \
        by["3"]["n_with_parent_duplex"], "the gradient the manuscript asserts is not in the data"


def test_five_of_the_nine_clean_designs_carry_a_parent_duplex():
    """The finding itself. If this stops being five, the Abstract and §3.8 are both wrong."""
    sys.path.insert(0, HERE)
    from test_aso_submission_numbers import _clean_set  # noqa: E402  (one home for the predicate)
    clean = {seq for _, seq in _clean_set()}
    rows = {r["antisense_5to3"]: r for r in _art()["per_design"]}
    liable = sorted(s for s in clean if rows[s]["counts_as_liability"])
    free = sorted(s for s in clean if not rows[s]["counts_as_liability"])
    assert len(clean) == 9
    assert len(liable) == 5 and len(free) == 4, (liable, free)
    txt = _flat(_paper())
    assert "Five of the nine designs called clean above carry such" in txt
    for s in free:
        assert f"5′-{s}-3′" in txt, f"a design that survives every screen is not named: {s}"


def test_the_wild_type_nr4a3_case_is_named():
    """The most consequential single row: the one design passing all four conventional rules
    forms a 12 bp duplex with wild-type NR4A3. A paper that drops this keeps a recommendation
    the evidence withdrew."""
    rows = {r["antisense_5to3"]: r for r in _art()["per_design"]}
    r = rows["CAGGGCATATCTTGCA"]
    assert r["parent"] == "NR4A3" and r["longest_parent_duplex_bp_through_gap"] >= 10
    assert "5′-CAGGGCATATCTTGCA-3′, against wild-type *NR4A3*" in _flat(_paper())


def test_the_screen_reproduces_from_committed_inputs():
    """`--check` is the artifact's own reproduction test; run it so a stale artifact fails here."""
    import aso_parent_gap_pairing as m  # noqa: E402
    assert m.main(["--check"]) == 0, "aso-parent-gap-pairing.json is stale; re-run the script"


def test_the_threshold_is_stated_as_a_choice_not_a_measurement():
    """MIN_DUPLEX_BP is a judgement. If it is ever presented as measured, this fails."""
    a = _art()
    assert a["method"]["min_duplex_bp"] == 10
    assert any("STATED threshold" in s for s in a["_what_this_is_not"])
    assert "a stated\nthreshold, not a measured one" in _paper() or \
        "a stated threshold, not a measured one" in _flat(_paper())
