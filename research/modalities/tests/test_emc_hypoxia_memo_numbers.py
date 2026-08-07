"""Every load-bearing figure in `emc-hypoxia-reading.md` must be DERIVABLE from the artifact.

⛔ WHY. CLAUDE.md §1: one fact, one place. A memo that types a t-statistic has made a second home
for it, and the second home is the one that goes stale — silently, because prose does not fail a
build. This test derives each figure from `emc-hypoxia-confounds.json` at run time, formats it the
way the memo writes it, and asserts the memo contains that exact string. If the analysis is re-run
and a number moves, the memo goes red instead of going quietly wrong.

⚠ IT ALSO CATCHES THE OPPOSITE ERROR, which is the one that actually happened while the memo was
being written: two figures were typed from an exploratory script rather than from the artifact and
were wrong in the third significant figure (a score-correlation ceiling of 0.96 that was 0.954, and
a random-null floor of 8 % that was 6.3 %). Neither would have been caught by reading.

⛔ WHAT THIS TEST IS NOT. It does not check that the memo's PROSE is right — only that its numbers
are the artifact's numbers. A correct number inside a wrong sentence passes here, which is why the
language rules are `lint_claims.py`'s job and the honesty rules are the audit module's.
"""

import json
import os

import pytest

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(MOD)
ART = os.path.join(MOD, "emc-hypoxia-confounds.json")
MEMO = os.path.join(REPO, "manuscripts", "emc-hypoxia-reading.md")

G6 = "GSE24369_series_matrix.txt.gz"
G3 = "GSE4303-GPL3290_series_matrix.txt.gz"


def _ascii_minus(s):
    """⚠ The memo is typeset prose and writes U+2212 MINUS SIGN; `f"{-0.28:.2f}"` writes U+002D.
    Comparing them raw makes a correct figure fail, which trains the next reader to loosen the
    test rather than fix the number — so both sides are normalised, and only here."""
    return s.replace("−", "-").replace("–", "-").replace("—", "-")


@pytest.fixture(scope="module")
def art():
    if not os.path.exists(ART):
        pytest.skip("the confound artifact is not on this branch")
    with open(ART, "r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def memo():
    if not os.path.exists(MEMO):
        pytest.skip("the memo is not on this branch")
    with open(MEMO, "r", encoding="utf-8") as fh:
        return fh.read()


def _t(art, plat, path):
    node = art["platforms"][plat]
    for k in path:
        node = node[k]
    return node


def test_the_arm_sizes_and_myxoid_composition_are_the_artifacts(art, memo):
    p6 = art["platforms"][G6]
    p3 = art["platforms"][G3]
    assert (p6["n_EMC"], p6["n_comparator"]) == (6, 29)
    assert (p3["n_EMC"], p3["n_comparator"]) == (10, 6)
    cc = p6["C1_C2_comparator_composition_and_reference_pool"]["comparator_classes"]
    myx = sum(v["n"] for v in cc.values() if v.get("myxoid"))
    tot = sum(v["n"] for v in cc.values())
    assert f"**{myx} of {tot}**" in memo, (
        f"the memo does not carry the measured myxoid composition {myx} of {tot}")
    # GPL3290 must be recorded as having none, or §2.1's whole argument is misstated
    cc3 = p3["C1_C2_comparator_composition_and_reference_pool"]["comparator_classes"]
    assert not any(v.get("myxoid") for v in cc3.values())
    assert f"**0 of {p3['n_comparator']}**" in memo


def test_the_myxoid_vs_non_myxoid_split_is_the_artifacts(art, memo):
    """§2.1's load-bearing sentence — the one test that can address the physical-matrix hypothesis.

    ⚠ The claim is `the same to within noise`, and the honest way to hold a test to that is the
    SPLIT, not a threshold: if the physical hypothesis were right the contrast would shrink against
    myxoid comparators in every signature, so a 6-0 split either way is the finding, and 4-2 is not.
    """
    ps = art["platforms"][G6][
        "C1_C2_comparator_composition_and_reference_pool"]["per_signature"]
    non_larger = sum(1 for r in ps.values()
                     if r["vs_non_myxoid_comparators_pooled"]["delta_a_minus_b"] >
                     r["vs_myxoid_comparators_pooled"]["delta_a_minus_b"])
    myx_larger = len(ps) - non_larger
    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
    assert (f"{words[non_larger]} marginally larger against non-myxoid, "
            f"{words[myx_larger]} marginally larger against myxoid") in memo, (
        f"the memo's myxoid split does not match the artifact's {non_larger}/{myx_larger}")
    assert 0 < non_larger < len(ps), (
        "the split is unanimous — that is a real finding in one direction or the other and the "
        "memo's `same to within noise` sentence would be wrong")


def test_every_permutation_p_in_the_memo_table_is_the_artifacts(art, memo):
    """The §2.7 table, to the precision the memo prints."""
    quoted = {
        (G6, "hypoxia_buffa"): "0.015", (G6, "hypoxia_winter"): "0.19",
        (G6, "hypoxia_harris"): "0.24", (G6, "hypoxia_elvidge"): "0.092",
        (G6, "hypoxia_hallmark"): "0.074", (G6, "hypoxia_gobp_response"): "0.0041",
        (G3, "hypoxia_buffa"): "0.0011", (G3, "hypoxia_winter"): "0.0014",
        (G3, "hypoxia_harris"): "0.0015", (G3, "hypoxia_elvidge"): "0.0029",
        (G3, "hypoxia_hallmark"): "0.00012", (G3, "hypoxia_gobp_response"): "0.00037",
    }
    for (plat, slot), shown in quoted.items():
        p = _t(art, plat, ["C8_C9_C10_resampling", "per_signature", slot,
                           "C8_label_permutation_null", "one_sided_p"])
        # the memo rounds; the rounded artifact value must equal what it prints
        dec = len(shown.split(".")[1])
        assert f"{p:.{dec}f}".rstrip("0").rstrip(".") == shown.rstrip("0").rstrip(".") or \
            round(p, dec) == float(shown), (
                f"{plat}/{slot}: memo prints {shown}, artifact holds {p}")
        assert shown in memo, f"{shown} ({plat}/{slot}) is not in the memo"


def test_the_exactness_of_the_GPL3290_permutation_is_stated(art, memo):
    """8008 splits are enumerable and 1.6M are not; calling a sampled p `exact` would be a lie."""
    assert _t(art, G3, ["C8_C9_C10_resampling", "per_signature", "hypoxia_buffa",
                        "C8_label_permutation_null", "exact"]) is True
    assert _t(art, G6, ["C8_C9_C10_resampling", "per_signature", "hypoxia_buffa",
                        "C8_label_permutation_null", "exact"]) is False
    assert "exact" in memo


def test_the_leave_one_out_claim_matches_the_artifact_on_both_platforms(art, memo):
    """§2.7's sharpest sentence: none survives on GPL6244, all six do on GPL3290."""
    g6 = [_t(art, G6, ["C8_C9_C10_resampling", "per_signature", s, "C9_leave_one_EMC_out",
                       "all_at_or_above_2"])
          for s in art["cross_platform"]["C7_signature_independence"]["membership_jaccard"]]
    g3 = [_t(art, G3, ["C8_C9_C10_resampling", "per_signature", s, "C9_leave_one_EMC_out",
                       "all_at_or_above_2"])
          for s in art["cross_platform"]["C7_signature_independence"]["membership_jaccard"]]
    assert not any(g6), "the memo says NONE survives leave-one-out at |t|>=2 on GPL6244"
    assert all(g3), "the memo says ALL SIX survive leave-one-out on GPL3290"
    lo = _t(art, G6, ["C8_C9_C10_resampling", "per_signature", "hypoxia_buffa",
                      "C9_leave_one_EMC_out"])
    body = _ascii_minus(memo)
    assert f"{lo['t_min']:.2f}" in body and f"{lo['t_max']:.2f}" in body, (
        f"the memo's Buffa leave-one-out range does not match {lo['t_min']}-{lo['t_max']}")


def test_the_signature_independence_figures_are_the_artifacts(art, memo):
    body = _ascii_minus(memo)
    ind = art["cross_platform"]["C7_signature_independence"]
    js = [v for a, row in ind["membership_jaccard"].items() for b, v in row.items() if a != b]
    assert f"**{min(js):.2f}-{max(js):.2f}**" in body, (
        f"memo's Jaccard range does not match {min(js):.2f}-{max(js):.2f}")
    assert f"{ind['union_n_genes']} genes in the union" in memo
    assert f"{ind['n_genes_in_exactly_one_set']} of them in exactly one set" in memo
    for plat, corr in ind["score_correlation_per_platform"].items():
        rs = [v for a, row in corr.items() for b, v in row.items() if a != b]
        assert f"**r = {min(rs):.2f}-{max(rs):.2f}**" in body, (
            f"{plat}: memo's score-correlation range does not match "
            f"{min(rs):.2f}-{max(rs):.2f}")


def test_the_random_gene_set_null_range_and_its_bias_are_the_artifacts(art, memo):
    for plat in (G6, G3):
        rows = [r["C10_random_gene_set_null_CACHED_UNIVERSE"]
                for r in art["platforms"][plat]["C8_C9_C10_resampling"]["per_signature"].values()
                if "C10_random_gene_set_null_CACHED_UNIVERSE" in r]
        fr = [r["fraction_of_random_sets_reaching_observed_t"] for r in rows]
        # ONE DECIMAL, so no rounding convention has to be agreed between prose and test. The
        # integer form failed on 20.5 % — Python rounds it to 20 and a human writes 21.
        want = f"{min(fr) * 100:.1f}-{max(fr) * 100:.1f} %"
        assert want in _ascii_minus(memo), (
            f"{plat}: memo's random-null range does not match {want}")
        bias = rows[0]["fraction_of_universe_that_is_signature_membership"]
        assert 0.30 < bias < 0.40, (
            "the memo says the null's universe is 33-34 % signature membership; the artifact "
            f"says {bias}")


def test_the_fusion_vs_tissue_correlations_are_the_artifacts(art, memo):
    """§3's discriminating table — the numbers the tissue-not-fusion reading rests on."""
    for plat in (G6, G3):
        d = _t(art, plat, ["fusion_vs_tissue", "discriminators"])
        ca9 = d["CA9_the_oxygen_specific_readout"][
            "within_EMC_correlation_with_hypoxia_score_CA9_removed"]["r"]
        assert ca9 > 0, "the memo says CA9 tracks the score within EMC on BOTH platforms"
        assert f"+{ca9:.2f}" in memo, f"{plat}: CA9 within-EMC r {ca9} is not in the memo"
        nr = d["within_EMC_fusion_output_vs_hypoxia"]["genes"]["NR4A3"][
            "within_EMC_correlation_with_hypoxia_score"]["r"]
        assert nr < 0, "the memo says NR4A3 is negative on both platforms"
        assert f"{nr:.2f}" in _ascii_minus(memo), (
            f"{plat}: NR4A3 within-EMC r {nr} is not in the memo")


def test_the_glycolytic_decomposition_ranges_are_the_artifacts(art, memo):
    """§3 Findings 1 and 2 — the numbers that decide how much of the reading is metabolism.

    ⚠ The first draft of Finding 1 said `3–5×` and Finding 2 said `five of six sets`. The measured
    ratio reaches 11.6× and the remainder is positive in SIX of six. Both were typed from an
    exploratory script; both are the reason this test exists."""
    body = _ascii_minus(memo)
    for plat in (G6, G3):
        dec = art["platforms"][plat]["fusion_vs_tissue"]["decomposition_glycolytic_vs_rest"]
        ratios, rest_t = [], []
        for v in dec.values():
            cg = v["glycolytic_members"]["contrast"]
            cr = v["non_glycolytic_remainder"]["contrast"]
            if cr:
                rest_t.append(cr["t"])
            if cg and cr and cr["delta_a_minus_b"]:
                ratios.append(cg["delta_a_minus_b"] / cr["delta_a_minus_b"])
        assert f"{min(ratios):.1f}-{max(ratios):.1f}×" in body, (
            f"{plat}: memo's glycolytic/remainder ratio range does not match "
            f"{min(ratios):.1f}-{max(ratios):.1f}×")
        assert all(t > 0 for t in rest_t), (
            "the memo says the non-glycolytic remainder is positive in EVERY set on both platforms")
        assert len(rest_t) == 6, f"{plat}: expected six scoreable remainders, got {len(rest_t)}"


def test_finding_5_the_ENO3_vs_rest_of_glycolysis_test_is_the_artifacts(art, memo):
    """The sharpest fusion-vs-tissue test: does ENO3 co-vary with the programme it sits in?

    ⚠ The claim is `it does not reproduce`, and the only thing worth reading at n = 6 and n = 10 is
    whether the SIGN agrees. So the test asserts the signs DISagree — if a future run made them
    agree, the memo's sentence would be wrong in the direction that matters."""
    body = _ascii_minus(memo)
    rs = []
    for plat in (G6, G3):
        r = art["platforms"][plat]["fusion_vs_tissue"]["discriminators"][
            "within_EMC_glycolysis_minus_ENO3_vs_ENO3"]["within_EMC_correlation"]["r"]
        rs.append(r)
        assert f"{r:.2f}" in body, f"{plat}: ENO3-vs-rest r {r} is not in the memo"
    assert rs[0] * rs[1] < 0, (
        "the memo says this correlation does not reproduce; the two platforms now agree in sign "
        "and the sentence would have to change")


def test_the_enolase_removal_figures_are_the_artifacts(art, memo):
    for plat in (G6, G3):
        full = _t(art, plat, ["fusion_vs_tissue", "discriminators", "glycolysis_curated",
                              "contrast", "t"])
        none = _t(art, plat, ["fusion_vs_tissue", "discriminators",
                              "glycolysis_minus_all_enolases", "contrast", "t"])
        assert f"+{full:.2f}" in memo and f"+{none:.2f}" in memo, (
            f"{plat}: the enolase-removal pair {full}/{none} is not in the memo")
        assert none > 2, "the memo claims the programme survives removing every enolase"


def test_EPAS1_the_isoform_the_only_approved_HIF_agent_targets_has_an_artifact_home(art, memo):
    """§5's HIF row turns entirely on this, so it may not be quoted from inside a module score."""
    for plat, sign in ((G6, "+"), (G3, "+")):
        row = _t(art, plat, ["C3_C6_biological_confounds", "single_genes_a_reading_will_name",
                             "genes", "EPAS1"])
        assert row["readable"] is True
        t = row["EMC_vs_comparator"]["t"]
        assert f"{sign}{t:.2f}" in memo, f"{plat}: EPAS1 t={t} is not in the memo"


def test_the_memo_does_not_restate_the_panels_headline_t_statistics(memo):
    """CLAUDE.md §1 — those six have one home and it is emc-expression-panels.json."""
    for typed in ("+0.206", "+0.540", "t = +2.01", "t = +4.13", "t=+5.13"):
        assert typed not in memo, (
            f"{typed!r} is the panels artifact's headline figure; the memo must point at it, "
            f"never restate it")
