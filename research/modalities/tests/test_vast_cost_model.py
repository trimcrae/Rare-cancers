#!/usr/bin/env python3
"""Offline unit tests for vast_cost_model — the invariants the Vast spend policy rests on.

These are not coverage tests. Each one pins a claim the policy makes, so that if someone later changes a
constant or a formula the specific reasoning that breaks is named in the failure.
"""
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import vast_cost_model as vcm  # noqa: E402


def offer(gpu="RTX 4090", min_bid=0.13, storage=0.20, vram_gb=24, rel=0.99, cuda=12.9, mid="1", oid=1,
          num_gpus=1, rentable=True):
    return {"id": oid, "machine_id": mid, "gpu_name": gpu, "min_bid": min_bid, "storage_cost": storage,
            "gpu_ram": vram_gb * 1024, "reliability2": rel, "cuda_max_good": cuda, "num_gpus": num_gpus,
            "rentable": rentable}


class TestCardTable(unittest.TestCase):
    def test_only_benched_cards_are_known(self):
        self.assertEqual(vcm.card_of("RTX 4090"), "RTX4090")
        self.assertEqual(vcm.card_of("RTX 3090"), "RTX3090")
        # SUPER normalises onto the benched 4080 entry.
        self.assertEqual(vcm.card_of("RTX 4080 SUPER"), "RTX4080")

    def test_unbenched_card_returns_none_rather_than_a_guess(self):
        # The whole point: an unmeasured card gets NO throughput, so it cannot be ranked on a proxy.
        for name in ("RTX 5090", "A10", "L4", "H100 SXM", "Tesla P4", ""):
            self.assertIsNone(vcm.card_of(name), name)
            self.assertIsNone(vcm.ns_per_hour(name), name)

    def test_measured_values_match_the_validated_2026_07_24_grid(self):
        # If these drift, a bench was overwritten by an unvalidated one — the exact failure that produced the
        # retracted 669 ns/day figure still sitting in vast_bid_optimizer.
        self.assertAlmostEqual(vcm.MEASURED_NS_PER_DAY_84K["RTX4090"], 755.36)
        self.assertAlmostEqual(vcm.MEASURED_NS_PER_DAY_84K["RTX4080"], 703.51)
        self.assertAlmostEqual(vcm.MEASURED_NS_PER_DAY_84K["RTX3090"], 359.36)

    def test_4090_beats_3090_by_2_10x_not_2_42x(self):
        # pricing.md quoted 2.42x from the WITHDRAWN grid. The validated ratio is 2.10.
        r = vcm.MEASURED_NS_PER_DAY_84K["RTX4090"] / vcm.MEASURED_NS_PER_DAY_84K["RTX3090"]
        self.assertAlmostEqual(r, 2.102, places=2)


class TestStorage(unittest.TestCase):
    def test_storage_is_per_month_prorated_to_hours(self):
        # $0.20/GB/month on 40 GB = $8/month = ~$0.01096/hr. This term bills while PAUSED too (F4).
        self.assertAlmostEqual(vcm.storage_usd_per_h(0.20, 40), 8.0 / 730.0, places=6)

    def test_smaller_disk_is_strictly_cheaper(self):
        self.assertLess(vcm.storage_usd_per_h(0.20, 20), vcm.storage_usd_per_h(0.20, 40))

    def test_missing_storage_cost_is_zero_not_a_crash(self):
        self.assertEqual(vcm.storage_usd_per_h(None, 40), 0.0)


class TestCostFunction(unittest.TestCase):
    def test_zero_hazard_reduces_to_price_over_throughput(self):
        upn = vcm.usd_per_ns(0.13, 0.0, 755.36 / 24.0, hazard_per_h=0.0, restart_h=0.0)
        self.assertAlmostEqual(upn, 0.13 / (755.36 / 24.0), places=9)

    def test_cost_increases_with_bid(self):
        kw = dict(storage_usd_h=0.011, ns_per_h=31.47, hazard_per_h=0.1, restart_h=0.25, downtime_h=0.25)
        self.assertLess(vcm.usd_per_ns(0.10, **kw), vcm.usd_per_ns(0.20, **kw))

    def test_cost_increases_with_hazard(self):
        kw = dict(compute_usd_h=0.13, storage_usd_h=0.011, ns_per_h=31.47, restart_h=0.25, downtime_h=0.25)
        self.assertLess(vcm.usd_per_ns(hazard_per_h=0.05, **kw), vcm.usd_per_ns(hazard_per_h=0.5, **kw))

    def test_tighter_checkpointing_lowers_cost_at_no_price(self):
        # R5: retention is bought with engineering, not dollars. Same bid, smaller R, strictly cheaper.
        kw = dict(compute_usd_h=0.13, storage_usd_h=0.011, ns_per_h=31.47, hazard_per_h=0.3, downtime_h=0.25)
        self.assertLess(vcm.usd_per_ns(restart_h=vcm.restart_overhead_h(0.25), **kw),
                        vcm.usd_per_ns(restart_h=vcm.restart_overhead_h(2.0), **kw))

    def test_unknown_throughput_returns_none(self):
        self.assertIsNone(vcm.usd_per_ns(0.13, 0.011, None))

    def test_hazard_faster_than_progress_raises_rather_than_pricing_nonsense(self):
        with self.assertRaises(ValueError):
            vcm.usd_per_ns(0.13, 0.011, 31.47, hazard_per_h=5.0, restart_h=0.5)

    def test_restart_overhead_is_half_the_checkpoint_interval(self):
        self.assertAlmostEqual(vcm.restart_overhead_h(0.5), 0.25)
        # And carries NO image-reload term: that cost was self-inflicted and is fixed (F3).
        self.assertEqual(vcm.restart_overhead_h(0.0), 0.0)


class TestBid(unittest.TestCase):
    def test_bid_is_just_above_the_floor_not_a_multiple_of_it(self):
        b = vcm.recommended_bid(0.1333)
        self.assertGreater(b, 0.1333)
        self.assertLess(b, 0.1333 * 1.10)

    def test_bid_never_sits_at_or_below_the_floor(self):
        # A bid at/below min_bid can leave the instance created-but-stopped (verified 2026-07-23).
        for floor in (0.0147, 0.08, 0.1333, 0.56):
            self.assertGreater(vcm.recommended_bid(floor), floor)

    def test_bid_is_capped_at_on_demand(self):
        # F1: Vast itself caps the CHARGE at on-demand, measured to 17 s.f. on machine 142136. We clamp too,
        # because bidding into the cap still spends real money on every hour up to it.
        self.assertLessEqual(vcm.recommended_bid(0.10, ondemand_base=0.105), 0.105)

    def test_cap_below_floor_does_not_produce_an_unstartable_bid(self):
        # The failure mode that caused the earlier cap to be removed: a cap under min_bid must not win.
        self.assertGreaterEqual(vcm.recommended_bid(0.20, ondemand_base=0.05), 0.20)

    def test_old_multiples_are_all_rejected_by_the_policy(self):
        floor = 0.1333
        b = vcm.recommended_bid(floor)
        for mult in (1.25, 1.5, 1.9):
            self.assertLess(b, floor * mult, f"policy bid should undercut the retired x{mult} rule")

    def test_bad_input_returns_none(self):
        self.assertIsNone(vcm.recommended_bid(None))
        self.assertIsNone(vcm.recommended_bid(0))


class TestPolicyTheorems(unittest.TestCase):
    def test_premium_breakeven_is_implausibly_steep_at_market_numbers(self):
        # R2 as a falsifiable number: a premium only pays if the hazard falls faster than this with the bid.
        slope = vcm.premium_breakeven_dlam_db(compute_usd_h=0.10, storage_usd_h=0.011,
                                              hazard_per_h=0.1, restart_h=0.25, downtime_h=0.25)
        self.assertGreater(slope, 20.0)   # ~30+/hr per $/hr: no over-supplied market delivers this

    def test_premium_becomes_worthwhile_when_restarts_are_catastrophic(self):
        # The model is not rigged: make a preemption cost 10 h of redone work and the threshold collapses,
        # which is exactly the regime the old x1.9 was tuned in (a ~20-min reload on a churning tail leg).
        cheap = vcm.premium_breakeven_dlam_db(0.10, 0.011, hazard_per_h=0.05, restart_h=10.0)
        dear = vcm.premium_breakeven_dlam_db(0.10, 0.011, hazard_per_h=0.05, restart_h=0.05)
        self.assertLess(cheap, dear)

    def test_interruptible_wins_unless_preempted_absurdly_often(self):
        # R4 on today's board: cheapest 4090 floor $0.08 vs cheapest on-demand $0.1333.
        be = vcm.breakeven_hazard_vs_ondemand(bid_usd_h=0.0816, ondemand_usd_h=0.1333,
                                              storage_usd_h=0.011, restart_h=0.25, downtime_h=0.25)
        self.assertGreater(be, 1.0)

    def test_on_demand_wins_when_the_floor_is_not_actually_cheaper(self):
        be = vcm.breakeven_hazard_vs_ondemand(bid_usd_h=0.20, ondemand_usd_h=0.19, storage_usd_h=0.011)
        self.assertEqual(be, 0.0)


class TestSelection(unittest.TestCase):
    def test_ranks_by_usd_per_ns_not_usd_per_hour(self):
        # The canonical inversion: a cheaper-per-hour 3090 losing to a dearer-per-hour 4090.
        cheap3090 = offer(gpu="RTX 3090", min_bid=0.103, oid="a")
        dear4090 = offer(gpu="RTX 4090", min_bid=0.149, oid="b")
        ranked = vcm.rank_offers([cheap3090, dear4090], vcm.JobProfile())
        self.assertEqual(ranked[0].offer_id, "b")
        self.assertLess(ranked[0].usd_per_ns, ranked[1].usd_per_ns)
        self.assertGreater(ranked[0].min_bid, ranked[1].min_bid)   # dearer per HOUR, cheaper per ns

    def test_a_deep_discount_3090_does_beat_a_4090(self):
        # And the converse, so the rule is genuinely $/ns and not a disguised card preference: the live board
        # had a $0.0147 3090, which is 4.25x better per ns than the cheapest 4090 on the same board.
        ranked = vcm.rank_offers([offer(gpu="RTX 3090", min_bid=0.0147, oid="a"),
                                  offer(gpu="RTX 4090", min_bid=0.1310, oid="b")], vcm.JobProfile())
        self.assertEqual(ranked[0].offer_id, "a")

    def test_unbenched_cards_are_excluded_not_guessed(self):
        ranked = vcm.rank_offers([offer(gpu="RTX 5090", min_bid=0.001, oid="ghost"),
                                  offer(gpu="RTX 4090", min_bid=0.50, oid="real")], vcm.JobProfile())
        self.assertEqual([r.offer_id for r in ranked], ["real"])

    def test_hard_filters_reject_unusable_hosts(self):
        job = vcm.JobProfile()
        for bad in (offer(vram_gb=16, oid="lowvram"), offer(rel=0.5, oid="flaky"),
                    offer(cuda=11.8, oid="oldcuda"), offer(num_gpus=2, oid="multi"),
                    offer(rentable=False, oid="gone")):
            self.assertFalse(vcm.passes_filters(bad, job), bad["id"])
        self.assertTrue(vcm.passes_filters(offer(), job))

    def test_storage_rate_changes_the_ranking_between_equal_priced_hosts(self):
        # Two identical 4090s at the same floor; the one with dearer storage must lose.
        ranked = vcm.rank_offers([offer(min_bid=0.13, storage=1.0, oid="dear"),
                                  offer(min_bid=0.13, storage=0.05, oid="cheap")], vcm.JobProfile())
        self.assertEqual(ranked[0].offer_id, "cheap")

    def test_abandon_threshold_is_the_next_candidate(self):
        ranked = vcm.rank_offers([offer(min_bid=0.13, oid="a"), offer(min_bid=0.20, oid="b")],
                                 vcm.JobProfile())
        self.assertAlmostEqual(vcm.verify_and_abandon_threshold(ranked), ranked[1].usd_per_ns)

    def test_abandon_threshold_is_none_without_a_fallback(self):
        ranked = vcm.rank_offers([offer(min_bid=0.13, oid="a")], vcm.JobProfile())
        self.assertIsNone(vcm.verify_and_abandon_threshold(ranked))

    def test_continuity_sensitive_leg_is_flagged(self):
        job = vcm.JobProfile(min_uninterrupted_h=4.0, hazard_per_h=0.3)
        s = vcm.score_offer(offer(), job)
        self.assertTrue(any("uninterrupted" in n for n in s.notes))

    def test_continuity_requirement_scales_with_card_speed(self):
        # A 3090 needs 2.10x the wall clock for the same leg, so the same continuity requirement is 2.10x
        # harder there. Without this scaling the cheap-3090 tail would look free of continuity risk, which is
        # exactly the trap the covalent tail legs fell into.
        job = vcm.JobProfile(min_uninterrupted_h=2.0, hazard_per_h=0.3)
        fast = vcm.score_offer(offer(gpu="RTX 4090"), job)
        slow = vcm.score_offer(offer(gpu="RTX 3090"), job)
        self.assertEqual(fast.notes, [])                       # 2 h on a 4090: P(clean) = 0.55, no flag
        self.assertTrue(any("uninterrupted" in n for n in slow.notes))   # 4.2 h on a 3090: P(clean) = 0.28

    def test_reference_gpu_hour_conversion_is_self_consistent(self):
        # $/ns x (reference ns per hour) must reproduce the $/hr we would pay on a reference-card host.
        s = vcm.score_offer(offer(gpu="RTX 4090", min_bid=0.13, storage=0.0), vcm.JobProfile(
            hazard_per_h=0.0, checkpoint_interval_h=0.0))
        self.assertAlmostEqual(s.usd_per_reference_gpu_h, s.bid, places=4)


class TestSummary(unittest.TestCase):
    def test_summary_reports_best_and_robust_best_k(self):
        offers = [offer(min_bid=0.10 + 0.01 * i, oid=i) for i in range(20)]
        summ = vcm.summarise_market(vcm.rank_offers(offers, vcm.JobProfile()), top=10)
        self.assertEqual(summ["n_offers"], 20)
        self.assertLess(summ["best_usd_per_ns"], summ["best10_mean_usd_per_ns"])
        self.assertLess(summ["best10_mean_usd_per_ns"], summ["median_usd_per_ns"])
        self.assertTrue(summ["hazard_is_prior"])

    def test_summary_of_empty_market_is_none(self):
        self.assertIsNone(vcm.summarise_market([]))


if __name__ == "__main__":
    unittest.main()
