"""Tests for `selectivity_resolution_options` — the derivation behind the selectivity-resolution memo.

Per TESTING.md rule 7 these assert PROPERTIES, not labels and not population counts: the option list is
expected to grow, so nothing here counts options or pins wording. What is pinned is the arithmetic the
memo's argument rests on — above all that a reference-set bound is a function of MODEL counts and that
replicates cannot move it, because that is the claim an option would be bought or not bought on.
"""
import json
import math
import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nrv04_retro_gate as gate  # noqa: E402
import selectivity_resolution_options as S  # noqa: E402


# ---------------------------------------------------------------------------------------------------
# the fast permutation path must BE the frozen scorer, not merely agree with it on one case
# ---------------------------------------------------------------------------------------------------
def test_fast_permutation_p_is_bit_identical_to_the_frozen_scorer():
    rng = random.Random(20260801)
    worst = 0.0
    for _ in range(200):
        na, nb = rng.randint(2, 5), rng.randint(2, 6)
        a = [rng.gauss(4.0, 1.2) for _ in range(na)]
        b = [rng.gauss(4.0, 1.2) for _ in range(nb)]
        worst = max(worst, abs(S._p_less(a, b) - gate.exact_permutation_p(a, b, "less")["p"]))
    assert worst == 0.0, f"fast path diverged from the frozen scorer by {worst}"


def test_fast_permutation_p_handles_ties_the_same_way():
    a, b = [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]
    assert S._p_less(a, b) == gate.exact_permutation_p(a, b, "less")["p"] == 1.0


# ---------------------------------------------------------------------------------------------------
# the structural bound
# ---------------------------------------------------------------------------------------------------
def test_min_attainable_p_is_one_over_the_enumeration():
    for na in range(1, 7):
        for nb in range(1, 7):
            assert S.min_attainable_p(na, nb) == pytest.approx(1.0 / math.comb(na + nb, na))


def test_min_attainable_p_matches_what_the_frozen_scorer_reports():
    """The bound must not be an independent belief about the scorer — it must be the scorer's own."""
    rng = random.Random(7)
    for na, nb in ((3, 5), (3, 2), (3, 3), (4, 4)):
        a = [rng.gauss(4, 1) for _ in range(na)]
        b = [rng.gauss(4, 1) for _ in range(nb)]
        assert gate.exact_permutation_p(a, b, "less")["min_attainable_p"] == pytest.approx(
            S.min_attainable_p(na, nb))


def test_the_landed_pairwise_shape_cannot_reach_alpha_and_the_primary_can():
    """The finding the whole memo turns on, asserted as arithmetic rather than quoted from a JSON."""
    assert not S.reaches_alpha(3, 2)                      # NR4A1 vs NR4A3 at the authorized panel
    assert S.min_attainable_p(3, 2) > gate.ALPHA
    assert S.reaches_alpha(3, 5)                          # the primary contrast
    assert S.min_attainable_p(3, 5) < gate.ALPHA


def test_smallest_n_reaching_alpha_is_the_first_n_that_clears_it():
    n = S.smallest_n_reaching_alpha(3)
    assert S.reaches_alpha(n, 3)
    assert not S.reaches_alpha(n - 1, 3)


def test_paired_design_reference_set_is_smaller_than_unpaired_at_small_n():
    """A paired design is not automatically an improvement — at n = 3 it is strictly worse."""
    assert S.paired_min_attainable_p(3) > S.min_attainable_p(3, 3)
    assert S.paired_min_attainable_p(5) < S.min_attainable_p(5, 5) * 10   # it does overtake later


def test_exact_size_bound_never_exceeds_alpha_and_matches_the_lattice():
    for na, nb in ((3, 5), (3, 3), (4, 8), (5, 10)):
        c = math.comb(na + nb, na)
        s = S.exact_size_bound(na, nb)
        assert s <= gate.ALPHA
        assert s == pytest.approx(math.floor(gate.ALPHA * c) / c)


# ---------------------------------------------------------------------------------------------------
# ★ the load-bearing negative result: replicates cannot move a reference set
# ---------------------------------------------------------------------------------------------------
def test_replicates_do_not_move_any_reference_set():
    """Run the FROZEN verdict on the same model means at 2 and at 100 legs per model.

    Negative control for this test: if `gate.model_level_values` ever stopped collapsing legs to model
    means, the reference sets would grow with the replica count and this assertion would fail naming the
    property. That is exactly the regression it exists to catch.
    """
    means = {"retro_noncov_nr4a1": {1: 3.0, 2: 4.0, 3: 5.0},
             "retro_noncov_nr4a2": {1: 3.5, 2: 4.5, 3: 5.5},
             "retro_noncov_nr4a3": {1: 3.2, 2: 4.2}}
    seen = []
    for n_rep in (2, 7, 100):
        legs = [{"arm_id": a, "cofold_model_seed": s, "e1_plateau_A": v}
                for a, ms in means.items() for s, v in ms.items() for _ in range(n_rep)]
        v = gate.verdict(legs)
        seen.append((v["primary"]["n_arrangements"],
                     v["pairwise_secondary"]["retro_noncov_nr4a3"]["n_arrangements"],
                     v["primary"]["p"]))
    assert len(set(seen)) == 1, f"replicate count changed the reference set or the p-value: {seen}"
    assert seen[0][0] == math.comb(8, 3)
    assert seen[0][1] == math.comb(5, 3)


def test_adding_models_DOES_move_the_reference_set():
    """The other half of the same property — otherwise the test above would pass on a broken scorer."""
    base = {"retro_noncov_nr4a1": {1: 3.0, 2: 4.0, 3: 5.0},
            "retro_noncov_nr4a2": {1: 3.5, 2: 4.5, 3: 5.5},
            "retro_noncov_nr4a3": {1: 3.2, 2: 4.2}}
    grown = {a: dict(ms) for a, ms in base.items()}
    grown["retro_noncov_nr4a3"][3] = 4.9
    n_base = gate.verdict([{"arm_id": a, "cofold_model_seed": s, "e1_plateau_A": v}
                           for a, ms in base.items() for s, v in ms.items()])
    n_grown = gate.verdict([{"arm_id": a, "cofold_model_seed": s, "e1_plateau_A": v}
                            for a, ms in grown.items() for s, v in ms.items()])
    assert (n_grown["pairwise_secondary"]["retro_noncov_nr4a3"]["n_arrangements"]
            > n_base["pairwise_secondary"]["retro_noncov_nr4a3"]["n_arrangements"])


# ---------------------------------------------------------------------------------------------------
# noise
# ---------------------------------------------------------------------------------------------------
def test_variance_decomposition_is_self_consistent_or_refuses():
    d = S.variance_decomposition(1.2, 0.8, replicas_per_model=2)
    assert d["admissible"]
    assert d["variance_from_replicates"] + d["variance_between_models"] == pytest.approx(1.2 ** 2, abs=1e-3)
    assert d["sigma_between_models_A"] < 1.2                     # the floor is below the current noise
    bad = S.variance_decomposition(0.4, 2.0, replicas_per_model=2)
    assert not bad["admissible"]
    assert bad["sigma_between_models_A"] is None
    assert "why_inadmissible" in bad


def test_replicates_cannot_take_model_noise_below_sigma_between():
    floor = 0.8312
    prev = None
    for r in (1, 2, 4, 16, 256):
        s = S.sigma_model_at_replicas(floor, 0.855, r)
        assert s > floor
        if prev is not None:
            assert s < prev
        prev = s
    assert S.sigma_model_at_replicas(floor, 0.855, 10000) == pytest.approx(floor, abs=5e-4)


def test_power_is_zero_when_the_design_cannot_reach_alpha_however_large_the_effect():
    """A structurally-blocked test has power zero at ANY separation. Stated as the memo states it."""
    for delta in (1.0, 5.0, 50.0):
        assert S.power_pairwise(3, 2, 1.03, delta, n_sims=50) == 0.0


def test_power_rises_with_effect_and_with_models():
    lo = S.power_primary(3, 3, 3, 1.03, 0.5, n_sims=600, seed=3)
    hi = S.power_primary(3, 3, 3, 1.03, 2.5, n_sims=600, seed=3)
    assert hi > lo
    small = S.power_pairwise(3, 3, 1.03, 1.5, n_sims=600, seed=3)
    big = S.power_pairwise(5, 5, 1.03, 1.5, n_sims=600, seed=3)
    assert big > small


def test_power_returns_None_rather_than_a_sampled_substitute_past_the_cap():
    assert S.power_primary(12, 12, 12, 1.0, 1.0, n_sims=10) is None


# ---------------------------------------------------------------------------------------------------
# costs — DERIVED, never typed
# ---------------------------------------------------------------------------------------------------
def test_prices_are_the_cost_model_rate_times_the_cost_model_basis():
    rates = S.planning_rates()
    p = S.price_units(10, S.ENDPOINT_MD_LEG_REF_GPU_H, rates)
    assert p["plan_usd"] == pytest.approx(
        10 * S.ENDPOINT_MD_LEG_REF_GPU_H * rates["plan_usd_per_reference_gpu_h"], abs=0.01)
    assert p["range_usd"][0] < p["plan_usd"] < p["range_usd"][1]


def test_endpoint_md_basis_comes_from_the_cost_model_not_from_this_module():
    import vast_cost_model as vcm
    assert S.ENDPOINT_MD_LEG_REF_GPU_H == vcm.ENDPOINT_MD_REF_GPU_H_PER_LEG


def test_review_gate_is_judged_on_the_TOP_of_the_range():
    cheap = {"range_usd": [1.0, 49.0]}
    dear = {"range_usd": [1.0, 51.0]}
    assert not S.needs_review_gate(cheap)
    assert S.needs_review_gate(dear)


def test_sequence_cumulative_totals_are_the_running_sum_of_their_steps():
    seq = S.recommended_sequence()
    running = 0.0
    for s in seq["steps"]:
        running += s["cost"]["plan_usd"]
        assert s["cumulative_plan_usd"] == pytest.approx(running, abs=0.02)
    assert seq["total_plan_usd"] == pytest.approx(running, abs=0.02)


def test_every_step_that_can_cancel_the_rest_precedes_one_that_cannot():
    """The sequence must be ordered by decision value, which is what makes serializing legitimate."""
    flags = [s["could_cancel_the_rest"] for s in S.recommended_sequence()["steps"]]
    assert flags[0] and flags[1] and not flags[-1]


# ---------------------------------------------------------------------------------------------------
# the committed artifact must be regenerable from the committed code
# ---------------------------------------------------------------------------------------------------
def test_committed_artifact_agrees_with_a_fresh_derivation_on_everything_deterministic():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "selectivity-resolution-options.json")
    if not os.path.exists(path):
        pytest.skip("artifact not generated in this checkout")
    with open(path) as f:
        got = json.load(f)
    fresh_panel = S.landed_panel()
    assert got["landed_panel"]["pooled_within_arm_model_level_SD_A"] == pytest.approx(
        fresh_panel["pooled_within_arm_model_level_SD_A"])
    assert got["binding_constraint"]["pairwise_nr4a1_vs_nr4a3"]["reaches_alpha"] is False
    assert got["binding_constraint"]["primary_contrast"]["reaches_alpha"] is True
    assert got["planning_rates"] == S.planning_rates()
    for opt in got["options"]:
        assert "cannot_buy" in opt and opt["cannot_buy"], f"{opt['option']} states no limit"
        assert "cost" in opt and "range_usd" in opt["cost"]


def test_every_option_declares_which_problem_it_attacks():
    for opt in S.build_options(n_sims=40):
        assert opt.get("attacks"), f"{opt['option']} does not say which problem it solves"
