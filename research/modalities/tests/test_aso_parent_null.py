#!/usr/bin/env python3
"""The null screen 4 had been reported without, and the two ways it could quietly be wrong.

⛔ WHY THIS EXISTS. `aso_parent_null.py` answers an external reviewer's objection to the submission
manuscript: 87 of 190 designs let a mature wild-type parent pair the catalytic gap, and that count
had nothing to be large or small relative to. A null is only worth having if it cannot be silently
too low, because a null that is too low manufactures the excess it was built to test. Two mechanisms
could do that here and each has an assertion below:

  (a) THE INDEX. The null runs 266,000 queries, so it looks the gap 6-mer up in a precomputed index
      instead of scanning 19,921 parent windows per query. An index that dropped hits would lower
      every null rate and leave the observed arm untouched, which is exactly the direction that
      flatters the paper. `test_index_and_brute_force_agree_on_every_real_design` runs the slow path
      over all 190 real designs and demands identity.
  (b) THE ARITHMETIC. The analytic expectation is a check on the sampled ensembles and vice versa,
      and the first version of it was WRONG in the same flattering direction — it counted the 7
      placements of a 10-wide run in a 16-mer without requiring them to contain the gap, and then
      union-bounded over nine-tenths-overlapping events. Both assertions below pin the corrected
      quantity against a hand-derived value, so a future edit cannot re-introduce either.

⚠ THE MANUSCRIPT SENTENCES ARE ASSERTED TOO. A number that arrives by review is exactly the kind
that drifts back out when the prose is next edited.
"""
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MOD))
ART = os.path.join(MOD, "aso-parent-null.json")
PAPER = os.path.join(REPO, "research", "manuscripts", "aso",
                     "fusion-junction-aso-research-article.md")
sys.path.insert(0, MOD)


def _art():
    if not os.path.exists(ART):
        pytest.skip("parent-null artifact is not present in this checkout")
    return json.load(open(ART, encoding="utf-8"))


def _paper():
    if not os.path.exists(PAPER):
        pytest.skip("submission manuscript is not present in this checkout")
    return open(PAPER, encoding="utf-8").read()


def _mods():
    try:
        import aso_parent_gap_pairing as pgp
        import aso_parent_null as npl
    except Exception as exc:                                    # noqa: BLE001
        pytest.skip(f"null modules do not import here: {exc}")
    return pgp, npl


# ───────────────────────────────────────────────────────────────────── (a) the index cannot lie
def test_index_and_brute_force_agree_on_every_real_design():
    """The fast path and screen 4's own scan must return the same longest run, design for design."""
    pgp, npl = _mods()
    if not os.path.exists(pgp.SEQS) or not os.path.exists(pgp.ATLAS):
        pytest.skip("parent sequences or atlas not present")
    parents = pgp.mature_parents()
    idx = npl._gap_index(parents)
    atlas = json.load(open(pgp.ATLAS, encoding="utf-8"))
    n = 0
    for panel in atlas["panels"]:
        for d in panel.get("designs") or []:
            if not d.get("fusion_specific"):
                continue
            target = d["target_mRNA_5to3"]
            fast_run, fast_gene = npl._best_run(target, parents, idx)
            slow_run, slow_gene, _ = pgp.best_parent_duplex(target, parents)
            assert fast_run == slow_run, f"{target}: index {fast_run} vs scan {slow_run}"
            if fast_run:
                assert fast_gene == slow_gene
            n += 1
    assert n == 190, f"expected the 190 fusion-specific design records, walked {n}"


def test_index_and_brute_force_agree_on_scrambled_queries_too():
    """The real designs are a soft test of the index — they mostly HIT. Scrambles mostly miss."""
    pgp, npl = _mods()
    if not os.path.exists(pgp.SEQS) or not os.path.exists(pgp.ATLAS):
        pytest.skip("parent sequences or atlas not present")
    parents = pgp.mature_parents()
    idx = npl._gap_index(parents)
    atlas = json.load(open(pgp.ATLAS, encoding="utf-8"))
    targets = [d["target_mRNA_5to3"]
               for p in atlas["panels"] for d in (p.get("designs") or [])
               if d.get("fusion_specific")]
    rng = npl.Rng(4242)
    checked = 0
    for t in targets[:40]:
        for _ in range(5):
            q = npl.scramble_mono(t, rng)
            assert npl._best_run(q, parents, idx)[0] == pgp.best_parent_duplex(q, parents)[0]
            checked += 1
    assert checked == 200


# ─────────────────────────────────────────────────────────────── (b) the arithmetic cannot lie
def test_analytic_site_probability_is_the_containment_calculation_not_the_placement_one():
    """Hand-derived: the gap must pair (4^-6) and the run must then extend by four more (1/64)."""
    pgp, npl = _mods()
    p_gap, p_extend = npl.analytic_p_site(len(pgp.GAP))
    assert p_gap == pytest.approx(0.25 ** 6)
    # L and R are truncated geometrics with success 1/4; P(L + R >= 4) works out to exactly 1/64.
    assert p_extend == pytest.approx(1.0 / 64.0, rel=1e-12)
    # ⛔ the discarded formula. 7 placements x 4^-10 is 1.7x this and is what the first pass used.
    naive = (pgp.OLIGO_LEN - pgp.MIN_DUPLEX_BP + 1) * (0.25 ** pgp.MIN_DUPLEX_BP)
    assert naive > p_gap * p_extend


def test_the_analytic_and_sampled_uniform_nulls_agree():
    """Two routes to the same rate. If they diverge, one of them is broken and neither is trusted."""
    a = _art()
    analytic = a["analytic_expectation"]["expected_rate_liable_poisson"]
    sampled = a["null_ensembles"]["random_uniform"]["rate_liable"]
    lo, hi = a["null_ensembles"]["random_uniform"]["rate_liable_wilson95"]
    assert 0.05 < sampled < 0.09, sampled
    # Poisson sits slightly high because sites within one transcript overlap; a factor beyond 1.3
    # in either direction means one of the two is wrong rather than mildly idealised.
    assert 0.77 < sampled / analytic < 1.3, (sampled, analytic, lo, hi)


# ──────────────────────────────────────────────────────────────────────────── what it found
def test_every_null_ensemble_is_far_below_the_observed_rate():
    a = _art()
    obs = a["observed"]["rate_liable"]
    assert a["observed"]["n_liable"] == 87 and a["observed"]["n_designs"] == 190
    for name, e in a["null_ensembles"].items():
        assert e["rate_liable"] < obs, f"{name} is not below the observed rate"
        assert e["n_draws"] == 190 * a["method"]["draws_per_design_per_ensemble"]


def test_the_scrambled_null_is_the_reviewers_question_and_it_is_answered():
    a = _art()
    s = a["null_ensembles"]["scrambled_mononucleotide"]
    assert 0.04 < s["rate_liable"] < 0.09
    # the NR4A3-specific arm is the one the modality turns on, and it separates much harder
    assert s["rate_liable_against_NR4A3"] < 0.04
    assert a["observed"]["rate_liable_against_NR4A3"] > 0.30


def test_the_parent_chimera_arm_sits_between_chance_and_the_observed_rate():
    """The load-bearing arm: real breakpoints are worse than arbitrary parent-to-parent chimeras.

    If this arm ever reached the observed rate, screen 4's headline would be a restatement of the
    design rule rather than a finding, and the manuscript sentence that says otherwise would be
    wrong. It is asserted from both sides for that reason.
    """
    a = _art()
    chim = a["null_ensembles"]["random_parent_chimera"]["rate_liable"]
    scram = a["null_ensembles"]["scrambled_mononucleotide"]["rate_liable"]
    obs = a["observed"]["rate_liable"]
    assert scram < chim < obs, (scram, chim, obs)
    assert chim / scram > 2.0
    assert obs / chim > 1.5


def test_the_dinucleotide_shuffle_almost_never_falls_back():
    a = _art()
    fb = a["null_ensembles"]["scrambled_dinucleotide"].get("_mononucleotide_fallbacks")
    assert fb is not None, "the fallback count must be reported, not silently dropped"
    assert fb < 0.01 * a["null_ensembles"]["scrambled_dinucleotide"]["n_draws"]


def test_the_dinucleotide_shuffle_actually_preserves_dinucleotides():
    pgp, npl = _mods()
    rng = npl.Rng(99)
    seq = "GTCCACGGATATGCCC"

    def dinucs(s):
        d = {}
        for a, b in zip(s, s[1:]):
            d[a + b] = d.get(a + b, 0) + 1
        return d

    ref = dinucs(seq)
    for _ in range(200):
        out, fell_back = npl.scramble_dinucleotide(seq, rng)
        if fell_back:
            continue
        assert len(out) == len(seq)
        assert out[0] == seq[0] and out[-1] == seq[-1]
        assert dinucs(out) == ref


def test_the_prng_is_deterministic_across_processes():
    _pgp, npl = _mods()
    a = [npl.Rng(7).next_u64() for _ in range(3)]
    b = [npl.Rng(7).next_u64() for _ in range(3)]
    assert a == b
    assert npl.Rng(7).shuffled("ACGTACGT") == npl.Rng(7).shuffled("ACGTACGT")


# ────────────────────────────────────────────────────────────── the manuscript quotes it right
def _pct(art, path):
    node = art
    for k in path:
        node = node[k]
    return node


def test_the_manuscript_states_the_null_and_states_it_from_the_artifact():
    """⛔ NO SKIP CONDITION. The null is in the paper; a test that could quietly opt out of checking
    it would be exactly the "reports while measuring nothing" defect the manuscript is about."""
    a = _art()
    txt = _paper()
    for key in ("scrambled_mononucleotide", "scrambled_dinucleotide", "random_uniform",
                "random_composition_matched", "wings_scrambled_gap_held",
                "gap_scrambled_wings_held", "random_parent_chimera"):
        val = round(100 * a["null_ensembles"][key]["rate_liable"], 1)
        assert re.search(rf"\b{val:.1f}\s*%", txt), \
            f"{key} = {val}% is not stated anywhere in the manuscript"
    obs = round(100 * a["observed"]["rate_liable"], 1)
    assert re.search(rf"\b{obs:.1f}\s*%", txt), f"the observed {obs}% is not in the manuscript"


def test_the_exon_terminus_arms_exist_and_the_acceptor_is_what_moves_the_rate():
    """⛔ ROUND-7 B5-F1, PINNED. The published chimera draws BOTH halves at uniform interior
    windows, so it destroys exon-terminal context along with the breakpoint and cannot support an
    apportionment between "generic" and "specific to the real junctions".

    The three corrected arms are asserted here so the apportionment cannot be re-derived from the
    uniform arm by a later edit, and so the ORDERING that carries the conclusion is pinned:
    requiring the DONOR half to end at a real exon 3' terminus moves nothing, and requiring the
    *NR4A3* half to BEGIN at a real exon 5' terminus is what lifts the null to near the observed
    rate. The mechanism is the acceptor boundary, which is narrower than the filed charge.
    """
    a = _art()
    e = a["null_ensembles"]
    for k in ("donor_terminus_chimera", "exon_terminus_chimera",
              "exon_terminus_chimera_novel_acceptor"):
        assert k in e, f"the corrected null arm {k} is gone"

    uniform = e["random_parent_chimera"]["rate_liable"]
    donor = e["donor_terminus_chimera"]["rate_liable"]
    both = e["exon_terminus_chimera"]["rate_liable"]
    novel = e["exon_terminus_chimera_novel_acceptor"]["rate_liable"]
    obs = a["observed"]["rate_liable"]

    assert abs(donor - uniform) < 0.05, (
        "the donor terminus is supposed to move the rate hardly at all; if it now does, the "
        "acceptor-boundary mechanism recorded in the ledger no longer holds"
    )
    assert both > uniform + 0.10, "requiring both exon termini must lift the null well above uniform"
    assert both > 0.85 * obs, (
        "the corrected null no longer reproduces most of the observed rate -- the apportionment "
        "question is reopened and the manuscript sentences must be re-derived, not left standing"
    )
    # ⚠ THE SENSITIVITY THAT LICENSES THE CONCLUSION. Every reported junction uses the NR4A3 exon-3
    # acceptor, which is one of the seven the arm draws from; if excluding it mattered, the null
    # would be partly reproducing the disease's own junction.
    assert abs(both - novel) < 0.01, (
        "excluding the real acceptor now changes the null materially, so the exon-terminus result "
        "rests on drawing the disease's own acceptor and cannot be reported as it stands"
    )


def test_the_junction_offset_is_an_antisense_offset_not_a_donor_base_count():
    """⛔ THE SPLIT `draw_parent_chimera` USES IS THE MIRROR OF EACH DESIGN'S OWN SPLIT.

    `junction_offset_in_oligo` counts bases in the ANTISENSE oligo, in which the *NR4A3* half comes
    first -- it equals `bases_from_NR4A3` for all 190 records. `draw_parent_chimera` takes that many
    bases from the DONOR, so it builds each design's mirror.

    ⭐ ITS TOTALS SURVIVE, AND THAT IS THE PROPERTY ASSERTED HERE rather than described: every
    junction tiles offsets 6..10, symmetric about 8, so the multiset of donor lengths drawn per
    junction is identical either way and the published 23.8% is unaffected. If a future atlas breaks
    that symmetry -- a different tiling, an odd oligo length -- the published arm silently stops
    being the ensemble it claims to be, and this test is what says so.
    """
    pgp, _ = _mods()
    atlas = json.load(open(pgp.ATLAS, encoding="utf-8"))
    seen = 0
    for panel in atlas["panels"]:
        designs = [d for d in panel.get("designs") or [] if d.get("fusion_specific")]
        if not designs:
            continue
        seen += 1
        offsets = sorted(d["junction_offset_in_oligo"] for d in designs)
        donor_lens = sorted(pgp.OLIGO_LEN - d["junction_offset_in_oligo"] for d in designs)
        assert offsets == donor_lens, (
            f"{panel['junction_label']}: the offset tiling is no longer symmetric, so the chimera "
            "arm's mirrored split now changes its own ensemble totals"
        )
        for d in designs:
            assert d["junction_offset_in_oligo"] == d["bases_from_NR4A3"], (
                f"{panel['junction_label']}: junction_offset_in_oligo has stopped meaning "
                "'bases from NR4A3', which is the premise the corrected arms are built on"
            )
    assert seen == 38, f"expected 38 junction panels with designs, saw {seen}"


def test_the_manuscript_does_not_present_the_null_as_a_significance_test():
    """The artifact refuses a p-value for a stated reason; the prose must not smuggle one back."""
    # ⛔ THE WINDOW IS BOUNDED BY THE SECTION'S OWN TEXT, NOT BY A CHARACTER COUNT (fixed
    # 2026-08-16). This read 2,600 characters forward from "without a null", which made the guard a
    # hostage to section LENGTH: the 2026-08-16 corrected-null work added three ensembles and a
    # paragraph, the non-independence statement moved to 179 characters BEFORE the anchor and to the
    # section's close 3,465 after it, and the guard went red while the manuscript said the required
    # thing MORE clearly and in TWO places. A guard that fails when the text improves gets widened
    # reflexively until it checks nothing; anchoring it on the section's real end instead means the
    # span grows with the section.
    txt = _paper().lower()
    start = txt.find("a nominal binomial")
    if start < 0:                                  # the Wilson sentence opens the null discussion
        start = txt.find("without a null")
    assert start > 0, "the null paragraph has moved or been removed from the manuscript"
    end = txt.find("none of these rates is a significance", start)
    assert end > start, (
        "the null section's closing sentence is gone — it is the one that refuses a p-value, so "
        "its absence is itself the defect this test exists to catch"
    )
    window = txt[start:end + 400]
    for banned in ("p < 0.", "p = 0.", "p-value", "significantly more", "statistically significant"):
        assert banned not in window, f"the null section claims significance: {banned!r}"
    # ⚠ The 190 records are 176 molecules tiled at overlapping registers across 38 junctions, so a
    # binomial interval on them is narrower than the truth. The paper must say so somewhere in this
    # span; WHERE it says it is an editorial choice and not this test's business.
    assert "independent draws" in window, (
        "the null section no longer states that the 190 design records are not independent draws, "
        "so its Wilson intervals now read as if they were"
    )
