"""Offline tests for the CREBBP/BRD4 selectivity-ABFE price.

The point of these is not that the arithmetic is hard — it is that every figure stays DERIVED. A hand-carried
total is what CLAUDE.md §1.1 exists to stop, so the tests assert the derivation rather than the digits: change
the engine's λ-schedule or the plan's receptor list and the price must move on its own.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import abfe_selectivity_cost as C  # noqa: E402
import nr4a3_abfe  # noqa: E402


def test_work_is_derived_from_the_engine_not_typed():
    """ns/leg must follow the engine's OWN schedule length, not a remembered 12."""
    w = C.work_per_leg()
    assert w["n_windows"] == nr4a3_abfe.n_windows()
    # 2000 iters x 500 steps x 2 fs = 1e6 fs = 1 ns... x2 because steps_per_iter*timestep = 1 ps/iter
    assert w["ns_per_window"] == pytest.approx(2.0)
    assert w["ns_per_leg"] == pytest.approx(w["n_windows"] * w["ns_per_window"])


def test_dense_schedule_reprices_itself(monkeypatch):
    """The 16-window λ-repair schedule is 4/3 the work — the price must track it with no edit here."""
    monkeypatch.setenv("ABFE_LAMBDA_SCHEDULE", "dense")
    assert nr4a3_abfe.n_windows() == 16
    assert C.work_per_leg()["ns_per_leg"] == pytest.approx(32.0)


def test_leg_count_comes_from_the_plan():
    """2 complex legs + ONE shared solvent leg, read from selectivity-benchmark.json's own receptors."""
    lc = C.leg_counts()
    assert lc["receptors"] == ["crebbp", "brd4bd1"]
    assert (lc["n_complex_legs"], lc["n_solvent_legs"], lc["n_legs"]) == (2, 1, 3)


def test_n_iter_comes_from_the_plan_not_the_engine_default():
    """The engine's default is 1000; the benchmark's plan says 2000. The plan must win."""
    assert C.work_per_leg()["n_iter"] == 2000
    assert C.work_per_leg()["n_iter"] != 1000


def test_total_is_derived_never_typed():
    """usd == billable_h_total x the measured rate, exactly. No independent total may exist."""
    for n in (1, 2, 3):
        p = C.price(n_replicates=n)
        assert p["usd"] == pytest.approx(p["billable_h_total"] * C.USD_PER_BILLABLE_H_G5_XLARGE)
        assert p["billable_h_total"] == pytest.approx(p["billable_h_per_pass"] * n)


def test_replicates_scale_linearly_because_each_needs_its_own_tag():
    """A replicate is a full re-run, not a fraction — see C.replicate_tag_defect."""
    one, three = C.price(1)["usd"], C.price(3)["usd"]
    assert three == pytest.approx(3 * one)


def test_resumes_are_excluded_from_the_range():
    """A re-dispatch does only the REMAINING iterations, so it must not pose as a cheap complete leg."""
    complete = C.complete_complex_legs(2000)
    assert 0.484 not in complete and 0.746 not in complete, "a resume leaked into the range"
    assert min(complete) >= C.t4l_scaled_complex_leg_h(2000)[0]
    # and every kept value is a real observation, not something invented
    assert set(complete).issubset(set(C.COMPLEX_LEG_BILLABLE_H_ALL))


def test_range_brackets_the_point_estimate():
    p = C.price(1)
    assert p["usd_range"][0] < p["usd"] < p["usd_range"][1]


def test_basis_is_the_median_of_three_independent_legs():
    """Mirrors vast_bench_sweep.median_over_hosts — N>=3, median not max/mean."""
    assert len(C.COMPLEX_LEG_BILLABLE_H) >= 3
    assert C.price(1)["billable_h_per_complex_leg"] == pytest.approx(2.943)


def test_the_bromodomain_basis_is_a_one_sided_over_estimate():
    """The size-appropriate T4L cross-check must sit BELOW the NR4A-LBD quote, or the 'conservative' claim
    in the docstring is false."""
    p = C.price(1)
    assert p["usd_t4l_scaled_likely"] < p["usd"]


def test_under_the_review_threshold():
    """CLAUDE.md §3 reserves a reviewer block for >$50 GPU spend. Both the single-replicate benchmark and the
    full 3-replicate campaign must be under it at the TOP of their range, or the recommendation changes."""
    assert C.price(1)["usd_range"][1] < 50
    assert C.price(3)["usd_range"][1] < 50


def test_it_refuses_to_fabricate_a_ladder_ratio():
    """THE HONEST-REFUSAL PROPERTY. The A10G is deliberately absent from the Vast throughput table, so no
    $/ref-GPU-h or drift multiple is derivable for this lane. The module must not grow one by accident."""
    p = C.price(1)
    for k in p:
        assert "ref_gpu_h" not in k and "ratio_vs_basis" not in k, f"{k} fabricates a ladder conversion"
    from vast_cost_model import card_of
    assert card_of("A10G") is None, "A10G became benched — this lane can now be priced against the ladder"


def test_emit_round_trips(tmp_path):
    out = C.emit(path=str(tmp_path / "cost.json"))
    on_disk = json.load(open(tmp_path / "cost.json"))
    assert on_disk["cases"]["1_replicate"]["usd"] == pytest.approx(out["cases"]["1_replicate"]["usd"])
    assert on_disk["_provider"].startswith("AWS SageMaker")


def test_superseded_calibration_costs_are_registered_not_dropped():
    """CLAUDE.md §1.2 — a corrected number keeps its old value on the record."""
    assert C.SUPERSEDED_CALIBRATION_COSTS["hydration_gate"] == 0.24
    assert C.SUPERSEDED_CALIBRATION_COSTS["binding_gate"] == 0.10
