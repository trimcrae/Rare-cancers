"""Tests for the GPU throughput bench's validation logic.

WHY THIS FILE EXISTS. On 2026-07-24 the bench grid reported an RTX 4080 SUPER as 4% FASTER than an RTX 4090 at
84,534 atoms, and a "$0.0377/hr A10" as the cheapest card per ns. Both were artifacts:

  * every timed window was 0.9-4.5 s long (4000 steps x 4 fs = 0.016 ns of MD, start to finish), so the numbers
    measured boost-clock ramp and kernel-launch overhead rather than steady-state throughput; and
  * the "A10" was a Quadro RTX 8000 the offer search had fallen back to.

A ranking was built on that and reported. The lesson encoded here: a throughput number must ARRIVE WITH THE
EVIDENCE THAT IT IS TRUSTWORTHY — block-to-block spread and a physics check — rather than being asserted to be
fine afterwards. `block_stats` and `health_check` are the pure halves of that, and they run without OpenMM
installed, so the logic is exercised here rather than only ever on a rented GPU.
"""
import importlib.util
import math
import os
import unittest

_SPEC = importlib.util.spec_from_file_location(
    "gpu_md_bench", os.path.join(os.path.dirname(__file__), "..", "gpu_md_bench.py"))
bench = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(bench)


class TestBlockStats(unittest.TestCase):
    def test_steady_blocks_have_near_zero_cv(self):
        mean, sd, cv = bench.block_stats([700.0, 701.0, 699.0])
        self.assertAlmostEqual(mean, 700.0, places=6)
        self.assertLess(cv, 0.01)

    def test_a_contended_host_is_exposed_by_the_cv_not_the_mean(self):
        """THE case a single timed window cannot distinguish: identical mean, wildly different reliability."""
        steady = bench.block_stats([700.0, 700.0, 700.0])
        contended = bench.block_stats([400.0, 700.0, 1000.0])
        self.assertAlmostEqual(steady[0], contended[0], places=6)   # same mean
        self.assertLess(steady[2], 0.001)
        self.assertGreater(contended[2], 0.4)                       # only the CV separates them

    def test_single_block_reports_zero_sd_and_does_not_divide_by_zero(self):
        mean, sd, cv = bench.block_stats([512.0])
        self.assertEqual((mean, sd, cv), (512.0, 0.0, 0.0))

    def test_empty_is_zero_not_an_exception(self):
        self.assertEqual(bench.block_stats([]), (0.0, 0.0, 0.0))

    def test_sd_is_the_sample_sd(self):
        _, sd, _ = bench.block_stats([10.0, 20.0])
        self.assertAlmostEqual(sd, math.sqrt(50.0), places=9)   # n-1 denominator

    def test_cv_is_scale_free_so_it_compares_across_cards(self):
        """A 4090 and an L4 differ ~2x in ns/day; stability must be comparable between them regardless."""
        _, _, fast = bench.block_stats([1000.0, 1100.0, 900.0])
        _, _, slow = bench.block_stats([100.0, 110.0, 90.0])
        self.assertAlmostEqual(fast, slow, places=9)


class TestHealthCheck(unittest.TestCase):
    """A diverged run integrates FAST and reports a large, fake ns/day — the exact failure a throughput bench is
    blind to unless it checks the physics."""

    @staticmethod
    def _ke_for(temp_k, n_atoms, n_constraints):
        dof = max(1, 3 * n_atoms - n_constraints)
        return temp_k * dof * bench._KB_KJ / 2.0

    def test_a_healthy_300K_run_passes(self):
        n, c = 84534, 28178
        temp, ok = bench.health_check(-1.2e6, self._ke_for(300.0, n, c), n, c)
        self.assertAlmostEqual(temp, 300.0, places=6)
        self.assertTrue(ok)

    def test_a_blown_up_run_is_rejected(self):
        n, c = 84534, 28178
        temp, ok = bench.health_check(-1.2e6, self._ke_for(5000.0, n, c), n, c)
        self.assertGreater(temp, 450.0)
        self.assertFalse(ok)

    def test_a_frozen_run_is_rejected(self):
        n, c = 84534, 28178
        _, ok = bench.health_check(-1.2e6, self._ke_for(10.0, n, c), n, c)
        self.assertFalse(ok)

    def test_nan_energy_is_rejected_rather_than_crashing(self):
        n, c = 84534, 28178
        nan = float("nan")
        self.assertFalse(bench.health_check(nan, self._ke_for(300.0, n, c), n, c)[1])
        self.assertFalse(bench.health_check(-1.2e6, nan, n, c)[1])

    def test_infinite_energy_is_rejected(self):
        n, c = 84534, 28178
        self.assertFalse(bench.health_check(float("inf"), self._ke_for(300.0, n, c), n, c)[1])

    def test_boundaries_are_where_they_are_documented(self):
        n, c = 1000, 0
        self.assertTrue(bench.health_check(-1.0, self._ke_for(300.0, n, c), n, c)[1])
        self.assertFalse(bench.health_check(-1.0, self._ke_for(149.0, n, c), n, c)[1])
        self.assertFalse(bench.health_check(-1.0, self._ke_for(451.0, n, c), n, c)[1])

    def test_dof_never_divides_by_zero(self):
        temp, _ = bench.health_check(-1.0, 1.0, 0, 0)
        self.assertTrue(math.isfinite(temp))



class TestBenchRejectionGate(unittest.TestCase):
    """The collector must REJECT unusable legs, not print them beside good ones and hope the reader notices.
    Every case here is a real failure mode from the 2026-07-24 grid."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "nrv04_vast_launch", os.path.join(os.path.dirname(__file__), "..", "nrv04_vast_launch.py"))
        cls.L = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(cls.L)
        except Exception as e:            # noqa: BLE001 - heavy optional deps
            raise unittest.SkipTest(f"launcher not importable here: {e}")

    @staticmethod
    def _row(**kw):
        d = {"status": "OK", "healthy": "True", "gpu_requested": "rtx4090", "wall_s": 60.0, "cv": 0.02,
             "_raw": "device='NVIDIA GeForce RTX 4090'"}
        d.update(kw)
        return d

    def test_a_good_leg_is_usable(self):
        self.assertEqual(self.L._bench_flags(self._row()), [])

    def test_the_two_second_window_is_rejected(self):
        self.assertIn("window_too_short", self.L._bench_flags(self._row(wall_s=2.1)))

    def test_the_fallback_to_a_different_card_is_rejected(self):
        """The 'A10' that was really a Quadro RTX 8000."""
        flags = self.L._bench_flags(self._row(gpu_requested="a10", _raw="device='Quadro RTX 8000'"))
        self.assertTrue(any(f.startswith("wrong_card") for f in flags), flags)

    def test_a_matching_card_with_extra_suffix_still_passes(self):
        """'rtx4080' requested, 'NVIDIA GeForce RTX 4080 SUPER' delivered — same family, not a fallback."""
        flags = self.L._bench_flags(
            self._row(gpu_requested="rtx4080", _raw="device='NVIDIA GeForce RTX 4080 SUPER'"))
        self.assertFalse(any(f.startswith("wrong_card") for f in flags), flags)

    def test_an_unstable_host_is_rejected(self):
        self.assertIn("unstable_cv", self.L._bench_flags(self._row(cv=0.35)))

    def test_a_legacy_single_shot_leg_cannot_pass_silently(self):
        self.assertIn("no_replicate_spread", self.L._bench_flags(self._row(cv=None)))

    def test_unphysical_run_is_rejected(self):
        self.assertIn("unphysical", self.L._bench_flags(self._row(healthy="False")))

    def test_an_errored_leg_short_circuits(self):
        self.assertEqual(self.L._bench_flags(self._row(status="ERROR")), ["errored"])

if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestOutbidIsNotDead(unittest.TestCase):
    """An outbid interruptible instance looks identical to a dead one — status "stopped" — but its disk is
    intact and Vast resumes it automatically. Destroying it discards that disk and buys a ~20-minute image
    reload on the re-rent. That self-inflicted reload was the ENTIRE justification for bidding floor x 1.9."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            "nrv04_vast_launch", os.path.join(os.path.dirname(__file__), "..", "nrv04_vast_launch.py"))
        cls.L = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(cls.L)
        except Exception as e:            # noqa: BLE001
            raise unittest.SkipTest(f"launcher not importable here: {e}")

    @staticmethod
    def _i(**kw):
        d = {"is_bid": True, "actual_status": "stopped", "intended_status": "running",
             "min_bid": 0.30, "price": 0.20}
        d.update(kw)
        return d

    def test_outbid_box_is_preserved(self):
        """min_bid 0.30 has risen above our 0.20 bid -> paused by the market, keep the disk."""
        self.assertTrue(self.L.instance_outbid(self._i()))

    def test_a_still_winning_stopped_box_is_not_called_outbid(self):
        """Our bid still clears the machine price, so 'stopped' means something else went wrong."""
        self.assertFalse(self.L.instance_outbid(self._i(min_bid=0.10, price=0.20)))

    def test_an_exited_container_is_dead_and_must_still_be_reaped(self):
        """The job finished or self-terminated. Destroying it is correct — this is the anti-idle guarantee."""
        self.assertFalse(self.L.instance_outbid(self._i(actual_status="exited")))

    def test_an_on_demand_instance_can_never_be_outbid(self):
        self.assertFalse(self.L.instance_outbid(self._i(is_bid=False)))

    def test_an_instance_we_asked_to_stop_is_ours_not_the_markets(self):
        self.assertFalse(self.L.instance_outbid(self._i(intended_status="stopped")))

    def test_a_running_instance_is_not_outbid(self):
        self.assertFalse(self.L.instance_outbid(self._i(actual_status="running")))

    def test_missing_price_data_keeps_the_disk_rather_than_destroying_it(self):
        """Destroying is irreversible; not destroying is caught by the over-age backstop minutes later."""
        self.assertTrue(self.L.instance_outbid(self._i(min_bid=None)))
        self.assertTrue(self.L.instance_outbid(self._i(price="?")))
