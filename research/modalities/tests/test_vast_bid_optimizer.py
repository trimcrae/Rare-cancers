#!/usr/bin/env python3
"""Offline unit tests for vast_bid_optimizer — the invariants the bidding policy rests on."""
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import vast_bid_optimizer as vbo  # noqa: E402

MARKET = [0.10, 0.12, 0.15, 0.20, 0.25, 0.30, 0.40, 0.60]
FLOOR = 0.10


class TestHazard(unittest.TestCase):
    def test_hazard_equals_lambda_ref_at_the_floor(self):
        self.assertAlmostEqual(vbo.hazard(FLOOR, FLOOR, MARKET, 1.0), 1.0, places=9)

    def test_hazard_is_monotone_non_increasing_in_bid(self):
        prev = float("inf")
        for b in (0.10, 0.15, 0.20, 0.30, 0.50, 0.70):
            h = vbo.hazard(b, FLOOR, MARKET, 1.0)
            self.assertLessEqual(h, prev + 1e-12)
            prev = h

    def test_hazard_is_zero_above_the_whole_market(self):
        self.assertEqual(vbo.hazard(1.00, FLOOR, MARKET, 1.0), 0.0)

    def test_below_floor_is_unusable_not_merely_risky(self):
        """A sub-floor bid leaves the box created-but-stopped — it must never look attractive."""
        self.assertEqual(vbo.hazard(0.05, FLOOR, MARKET, 1.0), float("inf"))

    def test_no_market_data_credits_a_higher_bid_with_NO_protection(self):
        """With no observable competing offers we cannot tell how much a higher bid buys, so the hazard must
        stay at lambda_ref rather than decay — crediting unobservable protection is how you talk yourself into
        a bid that does nothing. Conservative by design, not a bug."""
        self.assertEqual(vbo.hazard(0.2, 0.1, [], 1.0), 1.0)
        self.assertEqual(vbo.hazard(5.0, 0.1, [], 1.0), 1.0)


class TestRestartOverhead(unittest.TestCase):
    def test_tighter_checkpointing_lowers_the_overhead(self):
        loose = vbo.restart_overhead_h(checkpoint_interval_iters=200, sec_per_iter=16.0)
        tight = vbo.restart_overhead_h(checkpoint_interval_iters=20, sec_per_iter=16.0)
        self.assertLess(tight, loose)

    def test_reload_dominates_when_checkpointing_is_tight(self):
        r = vbo.restart_overhead_h(image_reload_h=0.33, checkpoint_interval_iters=2, sec_per_iter=1.0)
        self.assertAlmostEqual(r, 0.33, places=2)


class TestWallClock(unittest.TestCase):
    def test_no_preemption_means_wall_equals_work(self):
        self.assertAlmostEqual(vbo.expected_wall_h(10.0, 0.0, 0.33), 10.0)

    def test_preemption_drag_inflates_the_wall_clock(self):
        self.assertGreater(vbo.expected_wall_h(10.0, 0.5, 0.5), 10.0)

    def test_runaway_regime_is_infinite_not_cheap(self):
        """lambda*R >= 1 means preemptions arrive faster than recovery — the job never finishes."""
        self.assertEqual(vbo.expected_wall_h(10.0, 4.0, 0.5), float("inf"))


class TestOptimalBid(unittest.TestCase):
    def test_recommends_at_or_above_the_floor(self):
        p = vbo.optimal_bid(FLOOR, 0.80, MARKET, work_gpu_h=6.0, restart_h=0.4)
        self.assertGreaterEqual(p["best_interruptible"]["bid_usd_per_h"], FLOOR)

    def test_zero_restart_overhead_drives_the_bid_to_the_floor(self):
        """With nothing lost to a preemption, insurance is worthless — bid the floor."""
        p = vbo.optimal_bid(FLOOR, 0.80, MARKET, work_gpu_h=6.0, restart_h=0.0)
        self.assertAlmostEqual(p["best_interruptible"]["multiple_of_floor"], 1.0, places=2)

    def test_expensive_restarts_push_the_bid_up(self):
        cheap = vbo.optimal_bid(FLOOR, 0.80, MARKET, 6.0, restart_h=0.02)["best_interruptible"]
        dear = vbo.optimal_bid(FLOOR, 0.80, MARKET, 6.0, restart_h=0.60)["best_interruptible"]
        self.assertGreaterEqual(dear["multiple_of_floor"], cheap["multiple_of_floor"])

    def test_on_demand_is_evaluated_as_a_real_alternative(self):
        """A short job on a floor close to on-demand should just take on-demand — the question the fixed
        multiple never asks."""
        p = vbo.optimal_bid(0.50, 0.55, [0.50, 0.52, 0.54, 0.60], work_gpu_h=1.0, restart_h=0.5,
                            lambda_ref=2.0)
        self.assertTrue(p["recommended"].get("on_demand"))
        self.assertIn("on-demand", p["verdict"])

    def test_wall_clock_cap_is_respected(self):
        p = vbo.optimal_bid(FLOOR, 0.80, MARKET, work_gpu_h=6.0, restart_h=0.4, wall_max_h=6.5)
        if p.get("best_interruptible"):
            self.assertLessEqual(p["best_interruptible"]["wall_h"], 6.5 + 1e-9)

    def test_infeasible_cap_is_reported_not_silently_relaxed(self):
        p = vbo.optimal_bid(FLOOR, None, MARKET, work_gpu_h=6.0, restart_h=0.4, wall_max_h=1.0)
        self.assertFalse(p["feasible_interruptible"])
        self.assertIn("wall-clock", p["verdict"])

    def test_recommended_is_never_worse_than_the_fixed_multiple(self):
        """The whole point: optimising must not lose to the incumbent policy on its own objective."""
        for work in (2.0, 6.0, 20.0):
            for R in (0.1, 0.4, 0.8):
                p = vbo.optimal_bid(FLOOR, 0.80, MARKET, work, R)
                rec = p["recommended"]["cost_usd"]
                fixed, _, _ = vbo.plan_cost(FLOOR * 1.9, FLOOR, MARKET, work, R)
                if math.isfinite(fixed):
                    self.assertLessEqual(rec, fixed + 1e-9, f"work={work} R={R}")


class TestThroughputScale(unittest.TestCase):
    def test_reference_card_scales_to_one(self):
        s, basis = vbo.throughput_scale({"gpu_name": "RTX 4090"}, 146_000)
        self.assertAlmostEqual(s, 1.0, places=6)
        self.assertEqual(basis, "measured_bench")

    def test_3090_is_slower_at_the_measured_size(self):
        s, basis = vbo.throughput_scale({"gpu_name": "RTX 3090"}, 444_000)
        self.assertLess(s, 1.0)
        self.assertEqual(basis, "measured_bench")

    def test_unknown_card_falls_back_and_says_so(self):
        s, basis = vbo.throughput_scale({"gpu_name": "RTX 5000 Ada"}, 146_000)
        self.assertIn(basis, ("dlperf_proxy_WEAK", "assumed_equal_UNKNOWN"))

    def test_interpolation_is_monotone_decreasing_in_system_size(self):
        prev = float("inf")
        for atoms in (35_000, 85_000, 200_000, 444_000):
            ns = vbo._interp(vbo.MEASURED_NS_PER_DAY["rtx4090"], atoms)
            self.assertLessEqual(ns, prev)
            prev = ns


class TestRanking(unittest.TestCase):
    OFFERS = [
        {"id": 1, "gpu_name": "RTX 3090", "min_bid": 0.10, "dph_base": 0.30, "reliability2": 0.98},
        {"id": 2, "gpu_name": "RTX 4090", "min_bid": 0.16, "dph_base": 0.50, "reliability2": 0.97},
    ]

    def test_ranks_by_expected_cost_not_by_the_floor(self):
        """The 3090 has the cheaper floor; at 444k atoms it is 2.42x slower, so it should NOT win on cost."""
        ranked = vbo.rank_offers(self.OFFERS, work_gpu_h_reference=10.0, atoms=444_000, restart_h=0.4)
        self.assertEqual(ranked[0]["gpu"], "RTX 4090")
        self.assertLess(ranked[0]["expected_cost_usd"], ranked[1]["expected_cost_usd"])

    def test_slower_card_gets_more_work_hours(self):
        ranked = {r["gpu"]: r for r in vbo.rank_offers(self.OFFERS, 10.0, 444_000, 0.4)}
        self.assertGreater(ranked["RTX 3090"]["work_gpu_h_here"], ranked["RTX 4090"]["work_gpu_h_here"])

    def test_flags_a_fixed_multiple_that_breaches_on_demand(self):
        offers = [{"id": 9, "gpu_name": "RTX 4090", "min_bid": 0.30, "dph_base": 0.40}]
        ranked = vbo.rank_offers(offers, 5.0, 146_000, 0.4)
        self.assertTrue(ranked[0]["vs_current_policy"]["exceeds_on_demand"])
        self.assertIn("dominated", ranked[0]["vs_current_policy"]["note"])


class TestCalibration(unittest.TestCase):
    def _rec(self, bid, hours, censored):
        return vbo.LaunchRecord(bid_usd_per_h=bid, min_bid_usd_per_h=FLOOR,
                                market_prices=MARKET, hours_observed=hours, censored=censored)

    def test_no_events_means_unidentified_not_a_made_up_number(self):
        out = vbo.fit_lambda_ref([self._rec(0.15, 5.0, True), self._rec(0.20, 8.0, True)])
        self.assertIsNone(out["lambda_ref"])
        self.assertIn("not identified", out["note"])

    def test_events_give_a_positive_rate(self):
        out = vbo.fit_lambda_ref([self._rec(0.10, 1.0, False), self._rec(0.10, 2.0, False),
                                  self._rec(0.10, 3.0, True)])
        self.assertIsNotNone(out["lambda_ref"])
        self.assertGreater(out["lambda_ref"], 0.0)
        self.assertEqual(out["n_events"], 2)

    def test_more_exposure_at_the_same_event_count_lowers_the_rate(self):
        few = vbo.fit_lambda_ref([self._rec(0.10, 1.0, False)])["lambda_ref"]
        many = vbo.fit_lambda_ref([self._rec(0.10, 10.0, False)])["lambda_ref"]
        self.assertLess(many, few)

    def test_censored_records_still_count_as_exposure(self):
        a = vbo.fit_lambda_ref([self._rec(0.10, 1.0, False)])["lambda_ref"]
        b = vbo.fit_lambda_ref([self._rec(0.10, 1.0, False), self._rec(0.10, 9.0, True)])["lambda_ref"]
        self.assertLess(b, a)


class TestReservationPrice(unittest.TestCase):
    """P* is the object the fixed multiple could not express: an absolute target price held while the market
    moves, with a floor set by the job's own restart overhead."""

    HISTORY = [0.10, 0.11, 0.12, 0.15, 0.18, 0.20, 0.25, 0.30, 0.40, 0.55]

    def test_no_history_refuses_to_invent_a_target(self):
        out = vbo.reservation_price([], restart_h=0.4)
        self.assertIsNone(out["reservation_price"])
        self.assertIn("over TIME", out["note"])

    def test_targets_the_cheap_end_not_todays_price(self):
        out = vbo.reservation_price(self.HISTORY, restart_h=0.0, target_quantile=0.25)
        self.assertLessEqual(out["reservation_price"], 0.15)
        self.assertEqual(out["binding"], "price_quantile")

    def test_lower_quantile_gives_a_lower_target(self):
        lo = vbo.reservation_price(self.HISTORY, 0.0, target_quantile=0.1)["reservation_price"]
        hi = vbo.reservation_price(self.HISTORY, 0.0, target_quantile=0.5)["reservation_price"]
        self.assertLess(lo, hi)

    def test_churn_floor_can_bind_above_the_quantile(self):
        """A fat-image job in a hot market cannot chase the cheap end — the restart overhead binds first."""
        out = vbo.reservation_price(self.HISTORY, restart_h=0.9, market_prices=MARKET, floor=FLOOR,
                                    target_quantile=0.1, lambda_ref=2.0)
        self.assertEqual(out["binding"], "churn_floor")
        self.assertGreaterEqual(out["reservation_price"], out["quantile_price"])

    def test_reservation_never_below_either_component(self):
        out = vbo.reservation_price(self.HISTORY, 0.5, market_prices=MARKET, floor=FLOOR)
        self.assertGreaterEqual(out["reservation_price"], out["quantile_price"])
        if out["churn_floor"]:
            self.assertGreaterEqual(out["reservation_price"], out["churn_floor"])


class TestChurnFloor(unittest.TestCase):
    def test_zero_restart_overhead_allows_the_floor(self):
        self.assertAlmostEqual(vbo.churn_floor_price(FLOOR, MARKET, restart_h=0.0), FLOOR, places=4)

    def test_bigger_restart_overhead_raises_the_floor(self):
        cheap = vbo.churn_floor_price(FLOOR, MARKET, 0.05, lambda_ref=2.0)
        dear = vbo.churn_floor_price(FLOOR, MARKET, 0.45, lambda_ref=2.0)
        self.assertGreaterEqual(dear, cheap)

    def test_churn_floor_actually_satisfies_its_own_constraint(self):
        b = vbo.churn_floor_price(FLOOR, MARKET, 0.4, lambda_ref=2.0)
        self.assertIsNotNone(b)
        self.assertLessEqual(vbo.hazard(b, FLOOR, MARKET, 2.0) * 0.4, vbo.DEFAULT_MAX_CHURN_FRACTION + 1e-9)


class TestWaitingValue(unittest.TestCase):
    HISTORY = [0.10, 0.12, 0.15, 0.20, 0.30, 0.40, 0.55, 0.60]

    def test_quantifies_the_gap_to_the_cheap_end(self):
        out = vbo.waiting_value(self.HISTORY, current_price=0.55, target_quantile=0.25)
        self.assertGreater(out["saving_per_gpu_h"], 0)
        self.assertGreater(out["saving_pct"], 0)

    def test_reports_how_often_the_target_is_actually_reachable(self):
        out = vbo.waiting_value(self.HISTORY, 0.55, target_quantile=0.25)
        self.assertGreater(out["frac_of_samples_at_or_below_target"], 0.0)
        self.assertLessEqual(out["frac_of_samples_at_or_below_target"], 1.0)

    def test_no_history_returns_none_rather_than_a_guess(self):
        self.assertIsNone(vbo.waiting_value([], 0.5))


class TestDutyCycle(unittest.TestCase):
    """The acceptance quantile is DERIVED (fraction of remaining time we must be running), not tuned."""

    def test_slack_gives_a_small_quantile(self):
        self.assertAlmostEqual(vbo.duty_cycle(10.0, 100.0), 0.10, places=6)

    def test_behind_schedule_saturates_at_one(self):
        self.assertGreaterEqual(vbo.duty_cycle(100.0, 10.0), 1.0)

    def test_no_time_left_means_take_anything(self):
        self.assertEqual(vbo.duty_cycle(5.0, 0.0), 1.0)

    def test_more_capacity_lowers_the_required_duty_cycle(self):
        self.assertLess(vbo.duty_cycle(10.0, 100.0, capacity=4), vbo.duty_cycle(10.0, 100.0, capacity=1))


class TestColdStart(unittest.TestCase):
    def test_geometric_mean_of_bound_and_ceiling(self):
        self.assertAlmostEqual(vbo.cold_start_price(0.10, 0.40), 0.2, places=3)

    def test_sits_strictly_between_the_bounds(self):
        p = vbo.cold_start_price(0.10, 0.40)
        self.assertGreater(p, 0.10)
        self.assertLess(p, 0.40)

    def test_works_with_no_lower_bound_observed_at_all(self):
        """Zero knowledge really means zero: no observations, only the on-demand ceiling."""
        self.assertIsNotNone(vbo.cold_start_price(None, 0.40))

    def test_no_ceiling_means_no_answer(self):
        self.assertIsNone(vbo.cold_start_price(0.1, None))


class TestUCBQuantile(unittest.TestCase):
    OBS = [0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.24, 0.30, 0.40, 0.55]

    def test_thin_sample_is_shaded_UP_not_down(self):
        """A thin sample biased low would make us hold out for a price that does not exist."""
        few = vbo.ucb_quantile(self.OBS[:4], 0.25)
        many = vbo.ucb_quantile(self.OBS * 20, 0.25)
        self.assertGreaterEqual(few, many)

    def test_converges_toward_the_plain_empirical_quantile(self):
        big = self.OBS * 200
        ucb = vbo.ucb_quantile(big, 0.25)
        plain = sorted(big)[int(0.25 * len(big))]
        self.assertLessEqual(abs(ucb - plain), 0.02)

    def test_monotone_in_the_quantile(self):
        self.assertLessEqual(vbo.ucb_quantile(self.OBS, 0.2), vbo.ucb_quantile(self.OBS, 0.8))

    def test_no_observations_returns_none(self):
        self.assertIsNone(vbo.ucb_quantile([], 0.3))


class TestAdaptivePolicy(unittest.TestCase):
    OBS = [0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.24, 0.30, 0.40, 0.55, 0.11, 0.13, 0.17, 0.22]
    OD = 0.60

    def test_works_with_ZERO_knowledge(self):
        out = vbo.adaptive_reservation_price([], self.OD, work_remaining_gpu_h=10.0, time_remaining_h=200.0)
        self.assertIsNotNone(out["reservation_price"])
        self.assertEqual(out["phase"], "cold_start_geometric_mean")

    def test_switches_to_empirical_once_enough_observations(self):
        out = vbo.adaptive_reservation_price(self.OBS, self.OD, 10.0, 200.0)
        self.assertEqual(out["phase"], "empirical_ucb_quantile")
        self.assertEqual(out["n_observations"], len(self.OBS))

    def test_deadline_pressure_raises_the_price_to_on_demand(self):
        out = vbo.adaptive_reservation_price(self.OBS, self.OD, work_remaining_gpu_h=500.0,
                                             time_remaining_h=10.0)
        self.assertEqual(out["phase"], "deadline_binding")
        self.assertAlmostEqual(out["reservation_price"], self.OD, places=4)

    def test_more_slack_gives_a_lower_price(self):
        tight = vbo.adaptive_reservation_price(self.OBS, self.OD, 50.0, 100.0)["reservation_price"]
        loose = vbo.adaptive_reservation_price(self.OBS, self.OD, 5.0, 500.0)["reservation_price"]
        self.assertLessEqual(loose, tight)

    def test_never_exceeds_on_demand(self):
        for w, t in ((1.0, 1000.0), (100.0, 10.0), (10.0, 1.0)):
            out = vbo.adaptive_reservation_price(self.OBS, self.OD, w, t)
            self.assertLessEqual(out["reservation_price"], self.OD + 1e-9)

    def test_never_below_the_churn_floor(self):
        out = vbo.adaptive_reservation_price(self.OBS, self.OD, 5.0, 5000.0, restart_h=0.9,
                                             market_prices=MARKET, floor=FLOOR, lambda_ref=2.0)
        self.assertGreaterEqual(out["reservation_price"], out["churn_floor"] - 1e-9)

    def test_cold_start_to_empirical_handoff_does_not_jump_upward(self):
        """The finite-sample penalty exists so the transition is smooth — assert it actually is."""
        cold = vbo.adaptive_reservation_price(self.OBS[:5], self.OD, 10.0, 200.0)["reservation_price"]
        warm = vbo.adaptive_reservation_price(self.OBS, self.OD, 10.0, 200.0)["reservation_price"]
        self.assertLessEqual(warm, cold + 1e-9)

    def test_reports_what_is_binding(self):
        out = vbo.adaptive_reservation_price(self.OBS, self.OD, 10.0, 200.0)
        self.assertIn(out["binding"], ("cold_start_geometric_mean", "empirical_ucb_quantile",
                                       "churn_floor", "on_demand_cap", "deadline_binding"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
