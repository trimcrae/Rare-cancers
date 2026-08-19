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
                     "fusion-junction-aso-research-article.md")
sys.path.insert(0, MOD)


def _art():
    #: ⛔ NOT A SKIP (2026-08-19, lane C2 audit): committed artifact, so an absence is a broken
    #: tree, and skipping makes the guard disappear with its input while the run reports green.
    if not os.path.exists(ART):
        pytest.fail(f"the parent gap-pairing artifact is missing at {ART}; it is committed, and "
                    "the 87/190 criterion count rests on it.")
    return json.load(open(ART, encoding="utf-8"))


def _paper():
    if not os.path.exists(PAPER):
        pytest.fail(f"the submission manuscript is missing at {PAPER}; it is committed, and every "
                    "prose pin in this file is unchecked without it.")
    return open(PAPER, encoding="utf-8").read()


def _flat(txt):
    return re.sub(r"\s+", " ", txt)


def test_the_corpus_counts_match_the_manuscript():
    # ⭐ REWORDED, NOT LOST — the editorial restructure of 2026-08-16 cut the abstract from 593 words
    # to 306 and rebuilt this sentence around the corpus rather than around the screen: "87 of 190
    # candidates pair that gap … 61 of those against healthy *NR4A3*" is now "Of 190 candidates
    # across the 38 in-frame junctions of the five modelled partners, 87 pair their catalytic gap
    # against a mature parent transcript over a contiguous duplex of at least ten base pairs, 61
    # against healthy *NR4A3*". All three figures survive against the same denominator.
    # ⛔ EACH NUMBER IS PINNED WITH THE CRITERION IT WAS COUNTED UNDER. 87 without "a contiguous
    # duplex of at least ten base pairs" is the sentence §5's threshold caveat exists to bound — at a
    # seven-base-pair criterion the same screen returns 175 of 190 — so a guard that pinned the
    # number alone would let the abstract quote a threshold-dependent count with no threshold on it.
    # ⚠ ONE SENTENCE, NOT THREE SUBSTRINGS: `[^.]` forbids a full stop between them, so the
    # denominator, the count, its threshold and the *NR4A3* share cannot end up in different
    # sentences about different populations while three separate `in` checks all still pass.
    c = _art()["corpus"]
    txt = _flat(_paper())
    assert c["n_designs"] == 190
    nr4a3 = c["which_parent_supplies_it"]["NR4A3"]
    assert re.search(
        # ⚠ "candidates" -> "junction-spanning designs" 2026-08-17, and the pin follows the PROPERTY
        # rather than the noun. A cold reader found the abstract using "candidate" for a design
        # record while §2.7 and §4.5 reserve it for a design that has CLEARED the screens, so a
        # reader meets the loose sense first and the strict sense twenty pages later. This guard
        # exists for the three FIGURES and the ten-base-pair criterion they were counted under; the
        # word in front of them was never what it was protecting, and pinning it blocked a correct
        # edit until someone noticed. Either noun satisfies it.
        rf"Of {c['n_designs']} (?:candidates|junction-spanning designs)[^.]{{0,160}}?"
        rf"{c['n_with_parent_duplex_through_gap']} pair their catalytic gap against a mature parent "
        # ⚠ "over a contiguous duplex of at least ten base pairs" -> "over ten or more contiguous
        # base pairs" (found 2026-08-19, red on main). Third rewording to trip this pin, and the two
        # alternations above are the precedent: the guard follows the PROPERTY, which is the three
        # figures and the ten-base-pair criterion they were counted under, never the sentence that
        # carries them. Both phrasings state the same threshold, so both satisfy it.
        rf"transcript over (?:a contiguous duplex of at least ten base pairs"
        rf"|ten or more contiguous base pairs), "
        # ⚠ "healthy" -> "wild-type" 2026-08-17: a cold reader found the abstract was the only
        # place in the paper using "healthy"; every other home says wild-type. Either spelling
        # satisfies this pin, which is for the three FIGURES and their ten-base-pair criterion.
        # ⚠ "61 against" -> "61 of those 87 against" (2026-08-19): the restatement of the
        # denominator is a clarification, and 61 stays pinned either way.
        rf"{nr4a3}(?: of those {c['n_with_parent_duplex_through_gap']})? "
        rf"against (?:healthy|wild-type) \*NR4A3\*", txt), (
        "the abstract's parent-duplex sentence no longer carries all three figures with the "
        "ten-base-pair criterion they were counted under")


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
    """The finding itself. If this stops being five, the Abstract and §3.7 are both wrong.

    ⚠ The section reference below tracks a RENUMBER, not a relaxation: the clean-design section was
    §3.5 until the Results were rebalanced (the 104-word strand-orientation stub was folded into it
    as its opening), then §3.4, and it is §2.4 now that the editorial pass of 2026-08-16 moved
    Methods to the back and renumbered every Results subsection. ⛔ THE ORDINAL IS NO LONGER TYPED
    HERE — it is READ out of the sentence and then CHECKED, by requiring the section it names to be
    the one that actually names all nine designs. That is the invariant the old assertion was
    standing in for, and unlike the ordinal it cannot go stale on a renumber: a pointer at a section
    that no longer holds the designs it is counting now fails on the pointer, and a renumber that
    keeps the content passes without anyone editing this file.
    """
    sys.path.insert(0, HERE)
    from test_aso_submission_numbers import _clean_set  # noqa: E402  (one home for the predicate)
    clean = {seq for _, seq in _clean_set()}
    rows = {r["antisense_5to3"]: r for r in _art()["per_design"]}
    liable = sorted(s for s in clean if rows[s]["counts_as_liability"])
    free = sorted(s for s in clean if not rows[s]["counts_as_liability"])
    assert len(clean) == 9
    assert len(liable) == 5 and len(free) == 4, (liable, free)
    words = {4: "Four", 5: "Five", 6: "Six", 8: "eight", 9: "nine", 10: "ten"}
    m = re.search(rf"{words[len(liable)]} of the {words[len(clean)]} designs of "
                  r"§([0-9]+(?:\.[0-9]+)?) carry such", _flat(_paper()))
    assert m, (
        f"the paper no longer states that {len(liable)} of the {len(clean)} clean designs carry a "
        f"mature-parent duplex through the gap")
    raw, sec = _paper(), m.group(1)
    head = re.search(rf"^#+ {re.escape(sec)} · .*$", raw, re.M)
    assert head, f"§{sec} is cited for the clean designs and does not exist"
    after = re.search(r"^#+ [0-9]", raw[head.end():], re.M)
    body = raw[head.start():head.end() + (after.start() if after else len(raw))]
    missing = sorted(s for s in clean if s not in body)
    assert not missing, (
        f"§{sec} is cited as the home of the {len(clean)} clean designs but does not name "
        f"{missing}; the cross-reference has drifted off the section it points at")


def test_the_candidate_set_is_what_both_screens_leave():
    """⛔ THE PAPER'S CANDIDATE SET, AND IT IS AN INTERSECTION OF TWO SCREENS.

    Surviving the mature-parent screen is not enough and neither is surviving the deeper alignment
    re-screen: `GGCATATCAAGCGCTG` passes the second and fails the first, `GGGCATATCCGTGGAC` the
    reverse. Only the intersection is a candidate, and the paper names it in the Abstract, §3.8 and
    §4 — three places that must not be able to drift apart, which is why this asserts the
    intersection rather than a remembered pair.
    """
    import aso_screen_sets as ass  # noqa: PLC0415
    rows = {r["antisense_5to3"]: r for r in _art()["per_design"]}
    art_len = len(next(iter(rows)))
    deep = {}
    # ⚠ EVERY deep screen, not just the first batch: the panel is 38 junctions and a candidate
    # can come from any of them. Globbing one batch would have silently scoped the answer.
    # ⛔ AND THE GEOMETRY IS THE LOADER'S NOW, NOT AN INLINE LENGTH FILTER (2026-08-14). This globbed
    # `*deep500*` — unambiguous while one geometry existed, and not from the moment a 5-8-5 deep
    # re-screen was published as `...-18mer-deep500.json`. It matched, its 18-mers were looked up in
    # this 16-mer artifact's rows, and the test died on a KeyError — the lucky outcome. The inline
    # `!= art_len` skip added here was correct and was a SECOND copy of a rule five other modules
    # also needed; the geometry of the artifact under test now selects the screens directly, so
    # there is no filter for a sixth module to get subtly different. `art_len` is still read from
    # the artifact so the two cannot disagree.
    geom = next(g for g in (ass.MANUSCRIPT_GEOMETRY, ass.GEOMETRY_18MER_585,
                            ass.GEOMETRY_20MER_5_10_5) if g.oligo_len == art_len)
    for s in ass.load_screens(geom, ass.BLAST_SCREEN, root=MOD, select=ass.is_deep,
                              allow_empty=True):
        for o in s.artifact.get("oligos", []):
            if o.get("status") != "screened":
                continue
            hits = o.get("offtargets") or []
            assert len(hits) == o["n_offtarget_near_matches"], (
                "the deeper re-screen was supposed to retain every hit; this list is truncated")
            deep[o["antisense_5to3"]] = [h for h in hits if not h.get("is_minus_strand")]
    #: ⛔ NOT A SKIP (2026-08-19, lane C2 audit). The deep re-screens are committed; an empty set
    #: means the join stopped finding them, which is exactly when this comparison must speak.
    assert deep, (
        "no deep re-screen artifact was joined, so the comparison below covers nothing. The "
        "re-screens are committed — a join that returns nothing is a naming or path change, not "
        "an absent input.")

    sys.path.insert(0, HERE)
    from test_aso_submission_numbers import _clean_set  # noqa: E402
    clean = {seq for _, seq in _clean_set()}
    assert clean <= set(deep), "a design called clean at the default depth was never re-screened"

    # ⚠ THE DEEP-CLEAN SET IS NOT A SUBSET OF THE DEFAULT-DEPTH `clean` SET, AND ASSUMING IT WAS
    # WOULD UNDERCOUNT. Seven designs FAILED at the remote service at the default ceiling and carried
    # no count at all; all seven returned at the deeper one, and `GGGCATATCAAGCGCT` came back with no
    # hybridisable near-match. A design the shallower pass never screened is a candidate the
    # shallower pass could not have found, so the population here is every deep-screened design.
    deep_clean = sorted(s for s, hy in deep.items() if not hy)
    assert clean - set(deep_clean), "the deeper pass is supposed to have withdrawn some of the nine"
    survivors = sorted(s for s in deep_clean if not rows[s]["counts_as_liability"])
    assert survivors == ["AGGGCATATCGGAGTC", "GGGCATATCAAGCGCT",
                         "GGGCATATCCGACATG"], survivors
    txt = _flat(_paper())
    for s in survivors:
        assert f"5′-{s}-3′" in txt, f"a surviving candidate is not named in the paper: {s}"
    # ⚠ RE-ANCHORED 2026-08-17. The sentence now reads "leaves three of those four candidates in
    # the whole panel", because it previously credited the §2.6 un-rearranged-allele exclusions —
    # which remove nothing from the 38-junction panel — with dropping the fourth design. The
    # mature-parent screen of §2.5 does that, via an eleven-base-pair duplex with wild-type TCF12.
    assert "candidates in the whole panel" in txt and "three" in txt

    # ⭐ AND THE TIERING MUST SURVIVE EDITING. Two of the three have a longest parent run of ZERO, so
    # they are candidates at ANY threshold; the third is BELOW the stated cut rather than absent, so
    # it is a candidate at this cut and not at a stricter one. Collapsing that distinction would
    # present a threshold-dependent result as a threshold-independent one, which is the whole reason
    # `MIN_DUPLEX_BP` is documented as a choice.
    unconditional = sorted(s for s in survivors
                           if rows[s]["longest_parent_duplex_bp_through_gap"] == 0)
    assert unconditional == ["AGGGCATATCGGAGTC", "GGGCATATCCGACATG"], unconditional
    conditional = [s for s in survivors if s not in unconditional]
    assert len(conditional) == 1, conditional
    assert rows[conditional[0]]["longest_parent_duplex_bp_through_gap"] == 8
    assert "below the threshold rather than absent" in txt
    # and the design an earlier draft recommended must be named as withdrawn, not quietly dropped
    assert "5′-GGGCATATCTCTATAA-3′ at *TCF12* exon\n17" in _paper() or \
        "5′-GGGCATATCTCTATAA-3′ at *TCF12* exon 17" in txt


def test_the_wild_type_nr4a3_case_is_named():
    """The most consequential single row: the one design passing all four conventional rules
    forms a 12 bp duplex with wild-type NR4A3. A paper that drops this keeps a recommendation
    the evidence withdrew."""
    rows = {r["antisense_5to3"]: r for r in _art()["per_design"]}
    r = rows["CAGGGCATATCTTGCA"]
    assert r["parent"] == "NR4A3" and r["longest_parent_duplex_bp_through_gap"] >= 10
    assert "5′-CAGGGCATATCTTGCA-3′ against wild-type *NR4A3*" in _flat(_paper())


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
