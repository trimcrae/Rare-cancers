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
def test_authorized_stages_are_r1_r2_only():
    """R3 (epimer) is conditional and Arm F (alchemical) is blocked — the default fan-out must not include them."""
    assert panel.AUTHORIZED_STAGES == ("R1", "R2")
    stages = {a.stage for a in panel.arms_for_stages()}
    assert stages == {"R1", "R2"}


def test_unit_count_is_3_models_x_2_replicas_x_4_arms():
    units = panel.enumerate_units()
    assert len(units) == 24
    assert len({panel.unit_name(*u) for u in units}) == 24, "unit names must be unique (S3 prefixes collide otherwise)"


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


def test_concordant_requires_separation_significance_and_lomo():
    res = gate.verdict(_panel_legs([1.0, 1.1, 1.2], [3.0, 3.1, 3.2], [3.3, 3.4, 3.5]))
    assert res["tier"] == gate.TIER_CONCORDANT
    assert res["primary"]["stat"] < 0 and res["primary"]["p"] <= gate.ALPHA
    assert res["leave_one_model_out"]["survives"] and res["nr4a1_below_both_paralogues"]


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
