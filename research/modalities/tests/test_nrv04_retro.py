#!/usr/bin/env python3
"""Offline tests for the NR-V04 retrospective panel, blinding and frozen gate.

These exist so the prereg's criteria are ENFORCED, not merely written down: the statistics are checked against
hand-computed values, the direction of the one-sided test is pinned, and the tiers are exercised on synthetic
leg sets that represent each pre-registered outcome (including the null that prereg §5c says is expected).
No MD, no network, no GPU.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nrv04_retro_blind as blind          # noqa: E402
import nrv04_retro_gate as gate            # noqa: E402
import nrv04_retro_panel as panel          # noqa: E402


# =============================================================================================================
# panel
# =============================================================================================================
def test_authorized_stages_are_r1_only():
    """AMENDMENT 3 defect 1 RETIRED R2; R3 (epimer) is conditional and Arm F (alchemical) is blocked. The
    default fan-out must contain none of them."""
    assert panel.AUTHORIZED_STAGES == ("R1",)
    assert panel.RETIRED_STAGES == ("R2",)
    assert {a.stage for a in panel.arms_for_stages()} == {"R1"}


def test_unit_count_is_the_authorized_18_not_the_frozen_24():
    """3 co-fold models x 2 MD replicas x 3 R1 arms. The 4th (covalent) arm is retired, so 24 -> 18.

    This is not bookkeeping. Each of those 6 covalent units raises in `nrv04_covalent_md.build_system` BEFORE
    a leg JSON is written, so Vast re-runs the onstart and the box crash-loops on a live meter — and the same
    6 never-landing units keep `panel_complete` False forever, which prereg §4f turns into a PERMANENTLY
    suppressed R1 verdict. Losing the result is the worse half."""
    units = panel.enumerate_units()
    # AMENDMENT 4 (2026-07-31): 16, not 18 — nr4a3 co-fold seed 3 is excluded by MEASURED INPUT FAULT
    # (A:GLU13:O / A:LYS181:NZ at 0.181 A, PE +2.109e15 kJ/mol before the ligand or any solvent exists).
    # Superseded, retained: the 18-of-18 panel. `include_excluded=True` still yields it, for provenance.
    assert len(units) == 16
    assert len(panel.enumerate_units(include_excluded=True)) == 18
    assert len({panel.unit_name(*u) for u in units}) == 16, "unit names must be unique (S3 prefixes collide otherwise)"
    assert not any(a.covalent for a, _m, _r in units), "no covalent unit may be enumerable after AMENDMENT 3"
    # The exclusion is scoped to ONE co-fold: nr4a3 keeps models 1-2, every other arm keeps all three.
    from collections import Counter
    per_arm = Counter(a.arm_id for a, _m, _r in units)
    assert per_arm["retro_noncov_nr4a3"] == 4 and per_arm["retro_noncov_nr4a1"] == 6
    assert not any(a.arm_id == "retro_noncov_nr4a3" and m == 3 for a, m, _r in units)


def test_a_retired_stage_can_never_be_enumerated():
    """Passing the retired stage explicitly must RAISE, not quietly return an empty list or re-authorize the
    arm. A retirement that a caller can undo with one string is not a retirement."""
    with pytest.raises(ValueError, match="RETIRED"):
        panel.arms_for_stages(("R1", "R2"))
    with pytest.raises(ValueError, match="RETIRED"):
        panel.enumerate_units(stages=("R2",))
    # ...and the arm stays in the FROZEN table, because a preregistered arm is never silently deleted.
    assert panel.arm_by_id("retro_cov_nr4a1").stage == "R2"


def test_label_prefix_has_one_home_and_is_disjoint_from_the_covalent_panels():
    """The CI reaper's label selector is derived from these. If they ever overlapped, one lane's teardown
    could reach the other lane's billing hosts."""
    import nrv04_covalent_panel as cov
    arm = panel.arm_by_id("retro_noncov_nr4a1")
    assert panel.unit_name(arm, 1, 0).startswith(panel.LABEL_PREFIX)
    assert not panel.LABEL_PREFIX.startswith(cov.LABEL_PREFIX)
    assert not cov.LABEL_PREFIX.startswith(panel.LABEL_PREFIX)


def test_the_contaminated_cofold_prefix_is_not_used():
    """nrv04-descriptive-v3 carries 14-3-3 epsilon where Elongin B belongs (2026-07-24 audit, CI run
    30122648680). Those assemblies cannot support a ternary-recruitment readout and must never be the panel's
    source, whatever else changes."""
    assert panel.COFOLD_PREFIX != "nrv04-descriptive-v3"
    assert panel.COFOLD_PREFIX not in ("nrv04-shakeout",)


def test_no_covalent_paralogue_leg_exists():
    """Leg 0 measured that Cys551 is unique to NR4A1 — a covalent NR4A2/NR4A3 leg would be fabricated chemistry."""
    for arm in panel.ARMS:
        if arm.covalent:
            assert arm.target == "NR4A1", f"{arm.arm_id} is covalent on {arm.target}, which has no reactive Cys"


def test_paralogue_arms_are_protocol_matched():
    """The three R1 arms may differ ONLY in their target/co-fold system — same ligand, same covalency."""
    r1 = [a for a in panel.ARMS if a.stage == "R1"]
    assert len(r1) == 3
    assert {a.ligand for a in r1} == {"nrv04"}
    assert {a.covalent for a in r1} == {False}
    assert {a.target for a in r1} == {"NR4A1", "NR4A2", "NR4A3"}


def test_all_r1_arms_draw_from_one_cofold_prefix():
    got = {panel.cofold_prefix_s3(a, "bkt", 1) for a in panel.ARMS if a.stage == "R1"}
    assert all(g.startswith(f"s3://bkt/{panel.COFOLD_PREFIX}/") for g in got)
    assert all(g.endswith("/seed_1/") for g in got), "the co-fold MODEL seed must be pinned (prereg §4a)"


def test_leg_env_carries_model_seed_and_covalent_flags():
    arm = panel.arm_by_id("retro_cov_nr4a1")
    env = panel.leg_env(arm, 2, 1)
    assert env["LEG_ID"] == "retro_cov_nr4a1__m2" and env["SEED"] == "1"
    assert env["COVALENT"] == "1" and env["COV_RESNUM"] == "551" and env["COV_LIG_ATOM"] == "C6"
    noncov = panel.leg_env(panel.arm_by_id("retro_noncov_nr4a2"), 3, 0)
    assert noncov["COVALENT"] == "0" and "COV_RESNUM" not in noncov
    assert noncov["PROD_NS"] == "5.0" and noncov["EQUIL_NS"] == "1.0"


# =============================================================================================================
# statistics
# =============================================================================================================
def test_mean_difference_and_empty_group():
    assert gate.mean_difference([1.0, 3.0], [2.0]) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        gate.mean_difference([], [1.0])


def test_primary_contrast_enumerates_84_arrangements():
    """n=3 vs n=6 -> C(9,3) = 84; the minimum attainable one-sided p is 1/84, which is why alpha=0.05 is
    reachable for the primary test and NOT for a 3-vs-3 pairwise one."""
    r = gate.exact_permutation_p([1.0, 1.1, 1.2], [2.0, 2.1, 2.2, 2.3, 2.4, 2.5], alternative="less")
    assert r["n_arrangements"] == 84
    assert r["min_attainable_p"] == pytest.approx(1 / 84)
    assert r["p"] == pytest.approx(1 / 84), "perfect separation must give the minimum p"


def test_pairwise_min_p_is_0point05():
    r = gate.exact_permutation_p([1.0, 1.1, 1.2], [2.0, 2.1, 2.2], alternative="less")
    assert r["n_arrangements"] == 20 and r["p"] == pytest.approx(0.05)


def test_one_sided_direction_is_pinned_to_the_registered_prediction():
    """'less' means NR4A1 has the LOWER (more stable) plateau. A reversed data set must NOT be significant."""
    lower_nr4a1 = gate.exact_permutation_p([1.0, 1.1, 1.2], [3.0, 3.1, 3.2, 3.3, 3.4, 3.5], "less")
    higher_nr4a1 = gate.exact_permutation_p([3.0, 3.1, 3.2], [1.0, 1.1, 1.2, 1.3, 1.4, 1.5], "less")
    assert lower_nr4a1["p"] < 0.05 < higher_nr4a1["p"]
    assert higher_nr4a1["p"] == pytest.approx(1.0)


def test_permutation_p_includes_the_observed_arrangement():
    """The observed split is counted — the standard non-anticonservative convention; p is never 0."""
    r = gate.exact_permutation_p([1.0, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0, 1.0, 1.0], "less")
    assert r["p"] == pytest.approx(1.0)
    assert gate.exact_permutation_p([0.0, 0.0, 0.0], [9.0, 9.0, 9.0, 9.0, 9.0, 9.0], "less")["p"] > 0


def test_model_level_collapse_averages_replicas_and_counts_failures():
    legs = [
        _leg("retro_noncov_nr4a1", 1, 0, 1.0), _leg("retro_noncov_nr4a1", 1, 1, 3.0),
        {"arm_id": "retro_noncov_nr4a1", "cofold_model_seed": 2, "replica": 0, "technical_failure": True},
    ]
    means, failures = gate.model_level_values(legs)
    assert means["retro_noncov_nr4a1"][1] == pytest.approx(2.0), "the two replicas of a model collapse to one value"
    assert failures["retro_noncov_nr4a1"] == 1


# =============================================================================================================
# verdict tiers
# =============================================================================================================
def _leg(arm, model, replica, e1, **kw):
    rec = {"arm_id": arm, "cofold_model_seed": model, "replica": replica, "e1_plateau_A": e1}
    rec.update(kw)
    return rec


def _panel_legs(nr4a1, nr4a2, nr4a3, cov=None):
    """Build a full synthetic leg set: each arg is 3 model-level values, split into 2 identical replicas."""
    legs = []
    for arm, vals in (("retro_noncov_nr4a1", nr4a1), ("retro_noncov_nr4a2", nr4a2),
                      ("retro_noncov_nr4a3", nr4a3)) + ((("retro_cov_nr4a1", cov),) if cov else ()):
        for i, v in enumerate(vals, start=1):
            legs += [_leg(arm, i, 0, v), _leg(arm, i, 1, v)]
    return legs


def test_concordant_requires_separation_and_significance():
    res = gate.verdict(_panel_legs([1.0, 1.1, 1.2], [3.0, 3.1, 3.2], [3.3, 3.4, 3.5]))
    assert res["tier"] == gate.TIER_CONCORDANT
    assert res["primary"]["stat"] < 0 and res["primary"]["p"] <= gate.ALPHA
    assert res["nr4a1_below_both_paralogues"]
    assert res["leave_one_model_out"]["survives"], "LOMO is still COMPUTED and still reported"


def test_lomo_is_reported_but_is_not_a_tier_condition():
    """AMENDMENT 3 defect 3. LOMO left the CONCORDANT conjunction because it was INERT: an adversarial search
    found 228,543 configurations reaching p <= alpha with the correct ordering and ZERO that then failed it.

    That inertness is exactly why no real leg set can exercise this — so the pin is STRUCTURAL. Force
    `survives=False` and the tier must be unchanged, which is only true if the branch does not read it.
    Pre-AMENDMENT this returned WEAKLY_CONCORDANT."""
    legs = _panel_legs([1.0, 1.1, 1.2], [3.0, 3.1, 3.2], [3.3, 3.4, 3.5])
    real = gate.leave_one_model_out
    try:
        gate.leave_one_model_out = lambda *a, **k: {"observed_stat": -2.0, "refits": [], "survives": False}
        res = gate.verdict(legs)
    finally:
        gate.leave_one_model_out = real
    assert res["tier"] == gate.TIER_CONCORDANT, "LOMO must not be able to demote a CONCORDANT result"
    assert res["leave_one_model_out"]["survives"] is False, "...and it must still be REPORTED, not dropped"
    assert "diagnostic" in res["leave_one_model_out_role"].lower()


def _tier_branch_tests(func):
    """The source of every `if`/`elif` condition that decides the tier inside `verdict`. AST, not grep: the
    module explains the struck branch in a COMMENT, and a text search would match its own documentation."""
    import ast
    import inspect
    import textwrap
    tree = ast.parse(textwrap.dedent(inspect.getsource(func)))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            body = ast.dump(node)
            if "TIER_CONCORDANT" in body or "TIER_WEAK" in body:
                out.append(ast.unparse(node.test))
    return out


def test_the_lomo_predicated_weak_branch_is_struck():
    """AMENDMENT 3 struck 'correct ordering and p <= alpha, but the sign fails LOMO' as unreachable. It is now
    unreachable BY CONSTRUCTION: with LOMO out of the conjunction, that case is CONCORDANT."""
    tests = _tier_branch_tests(gate.verdict)
    assert tests, "no tier-deciding branch found — the introspection is looking in the wrong place"
    for t in tests:
        assert "lomo" not in t.lower(), f"a tier branch still consults LOMO: {t!r}"
    weak = gate.verdict(_panel_legs([2.0, 2.1, 3.6], [2.5, 3.0, 3.2], [2.6, 3.1, 3.3]))
    assert weak["tier"] == gate.TIER_WEAK
    assert "p = " in weak["reason"] and "leave-one-model-out" not in weak["reason"].lower()


def test_weakly_concordant_when_ordering_right_but_not_significant():
    res = gate.verdict(_panel_legs([2.0, 2.1, 3.6], [2.5, 3.0, 3.2], [2.6, 3.1, 3.3]))
    assert res["tier"] == gate.TIER_WEAK
    assert res["primary"]["stat"] < 0 and res["primary"]["p"] > gate.ALPHA


def test_discordant_when_a_paralogue_is_more_stable():
    res = gate.verdict(_panel_legs([3.0, 3.1, 3.2], [1.0, 1.1, 1.2], [1.3, 1.4, 1.5]))
    assert res["tier"] == gate.TIER_DISCORDANT
    assert "reverse direction" in res["reason"] or res["primary"]["stat"] >= 0


def test_the_expected_null_is_discordant_not_a_crash():
    """Prereg §5c: if selectivity is pure warhead reactivity, the non-covalent arms should be indistinguishable.
    That must produce a clean, reportable tier — not an exception and not a silent pass."""
    res = gate.verdict(_panel_legs([2.0, 2.1, 2.2], [2.0, 2.1, 2.2], [2.0, 2.1, 2.2]))
    assert res["tier"] in (gate.TIER_DISCORDANT, gate.TIER_WEAK)
    assert res["primary"]["p"] > gate.ALPHA


def test_underpowered_arm_forces_indeterminate():
    legs = _panel_legs([1.0, 1.1, 1.2], [3.0, 3.1, 3.2], [3.3, 3.4, 3.5])
    legs += [{"arm_id": "retro_noncov_nr4a2", "cofold_model_seed": 9, "replica": r, "technical_failure": True}
             for r in (0, 1)]
    res = gate.verdict(legs)
    assert res["tier"] == gate.TIER_INDETERMINATE
    assert "retro_noncov_nr4a2" in res["underpowered_arms"]


def test_one_failed_leg_is_tolerated():
    legs = _panel_legs([1.0, 1.1, 1.2], [3.0, 3.1, 3.2], [3.3, 3.4, 3.5])
    legs.append({"arm_id": "retro_noncov_nr4a3", "cofold_model_seed": 9, "replica": 0, "technical_failure": True})
    assert gate.verdict(legs)["tier"] == gate.TIER_CONCORDANT


def test_missing_arm_is_indeterminate_never_a_partial_verdict():
    legs = [l for l in _panel_legs([1.0, 1.1, 1.2], [3.0, 3.1, 3.2], [3.3, 3.4, 3.5])
            if l["arm_id"] != "retro_noncov_nr4a3"]
    assert gate.verdict(legs)["tier"] == gate.TIER_INDETERMINATE


def test_extension_triggers_only_on_right_sign_in_the_p_window():
    """Prereg §4d: the extension is triggered by the p-value alone and may never rescue a wrong-sign result."""
    wrong_sign = gate.verdict(_panel_legs([3.0, 3.1, 3.2], [1.0, 1.1, 1.2], [1.3, 1.4, 1.5]))
    assert wrong_sign["extension_triggered"] is False
    strong = gate.verdict(_panel_legs([1.0, 1.1, 1.2], [3.0, 3.1, 3.2], [3.3, 3.4, 3.5]))
    assert strong["extension_triggered"] is False, "a clean pass needs no extension"


# ------------------------------------------------------------------ AMENDMENT 3 defect 2: the p-window
def test_extension_window_is_the_amended_one():
    """The frozen (0.012, 0.05] could never fire in the case its own text names: attainable p is k/84, so it
    held only {0.0238, 0.0357, 0.0476} — all <= alpha and therefore already CONCORDANT — while the smallest
    attainable p ABOVE alpha (5/84 = 0.0595) fell outside it."""
    assert gate.EXTENSION_P_WINDOW == (0.05, 0.12)
    lo, hi = gate.EXTENSION_P_WINDOW
    attainable = [k / 84 for k in range(1, 85)]
    inside = [round(p, 4) for p in attainable if lo < p <= hi]
    assert inside, "the amended window must contain attainable p-values — that was the whole defect"
    assert all(p > gate.ALPHA for p in inside), "every triggering p must be ABOVE alpha, i.e. NOT concordant"
    assert inside[0] == pytest.approx(5 / 84, abs=1e-4) and inside[-1] == pytest.approx(10 / 84, abs=1e-4)


#: Nine E1 values whose 84 three-element subset sums are ALL DISTINCT (binary place values), so every
#: attainable p = k/84 is reachable exactly once and no tie can smear the rank. Equally-spaced values cannot
#: do this — {1.0,1.1,1.5}, {1.0,1.2,1.4} and {1.1,1.2,1.3} all sum to 3.6 — which is why the p-lattice must
#: be built rather than assumed.
_DISTINCT_SUM_E1 = [1.0 + 0.05 * (2 ** i) for i in range(9)]


def _e1_for_rank_k(k):
    """A synthetic R1 leg set whose primary p is exactly k/84, with the correct ordering intact.

    The primary statistic is a RANK statistic (audit §3a: p == rank(sum of the NR4A1 trio) / 84), so the p is
    set purely by which 3 of the 9 model-level values the NR4A1 arm takes. The remaining 6 are interleaved
    across the two paralogue arms so both stay above NR4A1 — `below_both` is a separate tier condition and a
    boundary test must not accidentally exercise it."""
    from itertools import combinations
    vals = _DISTINCT_SUM_E1
    for pick in combinations(range(9), 3):
        a1 = [vals[i] for i in pick]
        rest = [vals[i] for i in range(9) if i not in pick]
        for split in ((rest[0::2], rest[1::2]), (rest[:3], rest[3:]),
                      (rest[0:1] + rest[2:4], rest[1:2] + rest[4:])):
            legs = _panel_legs(a1, split[0], split[1])
            res = gate.verdict(legs)
            # Match on the RANK, not on the float: `verdict` rounds its reported p to 6 dp, so `11/84` and the
            # emitted `0.130952` differ by ~4e-7 and an exact comparison silently finds nothing.
            if round(res["primary"]["p"] * 84) == k and res["nr4a1_below_both_paralogues"]:
                return legs, res
    raise AssertionError(f"no arrangement reaches p = {k}/84 with the correct ordering")


@pytest.mark.parametrize("k,expect_extend", [
    (4, False),    # 0.0476 — inside the OLD window, <= alpha, already CONCORDANT: must NOT extend
    (5, True),     # 0.0595 — the smallest attainable p above alpha; the case the rule was written for
    (10, True),    # 0.1190 — the top of the amended window, inclusive
    (11, False),   # 0.1310 — just outside
])
def test_extension_fires_exactly_inside_the_amended_window(k, expect_extend):
    """Boundary pins, on ATTAINABLE p-values rather than invented ones. k=4 is the regression guard: under the
    frozen window it triggered while ALSO being CONCORDANT, which is the incoherence AMENDMENT 3 removed."""
    _legs, res = _e1_for_rank_k(k)
    assert res["primary"]["stat"] < 0 and res["nr4a1_below_both_paralogues"]
    assert res["extension_triggered"] is expect_extend, (
        f"p = {res['primary']['p']:.4f} (k={k}) -> extension {res['extension_triggered']}, expected {expect_extend}")
    if expect_extend:
        assert res["tier"] == gate.TIER_WEAK, "an extension may only ever fire on a NON-concordant result"


def test_extension_can_never_promote_a_result():
    """AMENDMENT 3's integrity argument, pinned: `extension_triggered` is a reported field that the tier
    assignment never reads, and it fires only where the result is NOT CONCORDANT."""
    import inspect
    src = inspect.getsource(gate.verdict)
    assert src.index("tier, reason = TIER_CONCORDANT") < src.index("extend = bool("), \
        "the tier must be decided BEFORE the extension flag is computed"
    for k in range(1, 85):
        try:
            _legs, res = _e1_for_rank_k(k)
        except AssertionError:
            continue
        if res["extension_triggered"]:
            assert res["tier"] != gate.TIER_CONCORDANT


# ------------------------------------------------------------------ AMENDMENT 3 defect 4: the registered MDE
def test_the_registered_mde_travels_with_every_verdict():
    """A null is bounded by what this design can DETECT, not by the absence of an effect — and the reader who
    needs that bound is reading the verdict, not another file."""
    res = gate.verdict(_panel_legs([2.0, 2.1, 2.2], [2.0, 2.1, 2.2], [2.0, 2.1, 2.2]))
    mde = res["registered_mde"]
    assert mde["measured_leg_sigma_A"] == gate.MEASURED_LEG_SIGMA_A
    assert tuple(mde["mde_80pct_power_A"]) == gate.REGISTERED_MDE_A
    assert "did not resolve" in mde["null_licenses"]
    assert "warhead reactivity" in mde["null_may_NOT_claim"]


def test_covalency_decomposition_is_reported_but_never_gates():
    with_cov = gate.verdict(_panel_legs([1.0, 1.1, 1.2], [3.0, 3.1, 3.2], [3.3, 3.4, 3.5], cov=[0.5, 0.6, 0.7]))
    without = gate.verdict(_panel_legs([1.0, 1.1, 1.2], [3.0, 3.1, 3.2], [3.3, 3.4, 3.5]))
    assert with_cov["covalency_decomposition"]["stat_cov_minus_noncov"] == pytest.approx(-0.5)
    assert without["covalency_decomposition"] is None
    assert with_cov["tier"] == without["tier"], "the covalent arm must not change the primary verdict"


def test_verdict_always_carries_the_claim_ceiling():
    res = gate.verdict(_panel_legs([1.0, 1.1, 1.2], [3.0, 3.1, 3.2], [3.3, 3.4, 3.5]))
    ceiling = res["claim_ceiling"].lower()
    assert "directional concordance" in ceiling and "no free energy" in ceiling


# =============================================================================================================
# blinding
# =============================================================================================================
def test_tokens_are_deterministic_and_distinct():
    salt = blind.make_salt()
    key = blind.build_key([a.arm_id for a in panel.ARMS], salt)
    assert len(set(key["arm_to_token"].values())) == len(panel.ARMS)
    assert blind.token_for("retro_noncov_nr4a1", salt) == key["arm_to_token"]["retro_noncov_nr4a1"]


def test_token_hides_the_arm_identity():
    salt = blind.make_salt()
    tok = blind.token_for("retro_noncov_nr4a1", salt)
    for needle in ("nr4a1", "noncov", "retro_noncov"):
        assert needle not in tok


def test_blind_then_unblind_round_trips_and_scores_identically():
    salt = blind.make_salt()
    key = blind.build_key([a.arm_id for a in panel.ARMS], salt)
    legs = _panel_legs([1.0, 1.1, 1.2], [3.0, 3.1, 3.2], [3.3, 3.4, 3.5])
    blinded = blind.blind_leg_records(legs, key)
    assert all(rec["arm_id"].startswith("arm_") for rec in blinded)
    restored = blind.unblind_leg_records(blinded, key)
    assert [r["arm_id"] for r in restored] == [l["arm_id"] for l in legs]
    assert gate.verdict(restored)["tier"] == gate.verdict(legs)["tier"]


def test_key_digest_changes_if_the_mapping_is_swapped(tmp_path):
    """The committed digest is what makes a post-hoc swap of the mapping detectable."""
    key = blind.build_key([a.arm_id for a in panel.ARMS], blind.make_salt())
    p1 = str(tmp_path / "k1.json")
    d1 = blind.write_key(key, p1)
    swapped = json.loads(json.dumps(key))
    a, b = "retro_noncov_nr4a1", "retro_noncov_nr4a2"
    swapped["arm_to_token"][a], swapped["arm_to_token"][b] = key["arm_to_token"][b], key["arm_to_token"][a]
    d2 = blind.write_key(swapped, str(tmp_path / "k2.json"))
    assert d1 != d2
    assert blind.key_digest(p1) == d1
