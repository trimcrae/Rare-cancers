#!/usr/bin/env python3
"""Offline unit tests for selectivity_margin_model — the invariants the strategy conclusions rest on."""
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import selectivity_margin_model as smm  # noqa: E402

FAST = dict(smm.DEFAULT_PARAMS, dose_points=31)


class TestFreeEnergyConversion(unittest.TestCase):
    def test_round_trip(self):
        for ddg in (0.0, 0.5, 1.7, 3.0):
            self.assertAlmostEqual(smm.ddg_from_fold(smm.fold_from_ddg(ddg)), ddg, places=9)

    def test_rt_scale_is_right(self):
        # a 10-fold affinity change is ~1.36 kcal/mol at 298 K
        self.assertAlmostEqual(smm.ddg_from_fold(10.0), 1.364, places=2)


class TestDegradation(unittest.TestCase):
    def test_zero_ubiquitination_efficiency_means_zero_degradation(self):
        """The unique-lysine mechanism in its limit: ternary complex forms, nothing is degraded."""
        self.assertEqual(smm.degradation(0.9, 0.0, 100.0), 0.0)

    def test_monotone_in_drive_and_bounded(self):
        prev = -1.0
        for f in (0.0, 0.1, 0.5, 0.9, 1.0):
            d = smm.degradation(f, 0.5, 20.0)
            self.assertGreaterEqual(d, prev)
            self.assertTrue(0.0 <= d < 1.0)
            prev = d


class TestCalibration(unittest.TestCase):
    def test_calibrated_arm_hits_its_target_dmax(self):
        p = dict(FAST)
        kappa = smm.calibrate_drive(p, p["kd_target_uM"], p["alpha_baseline"], p["ubiq_efficiency"])
        p2 = dict(p, k_ub_max_over_k_basal=kappa)
        _, degs = smm.dose_response(p["kd_target_uM"], p["kd_e3_uM"], p["alpha_baseline"],
                                    p["ubiq_efficiency"], p2)
        self.assertAlmostEqual(max(degs), p["on_target_dmax"], places=6)

    def test_returns_none_when_no_ubiquitination_is_possible(self):
        self.assertIsNone(smm.calibrate_drive(FAST, FAST["kd_target_uM"], FAST["alpha_baseline"], 0.0))


class TestWindowNull(unittest.TestCase):
    def test_identical_arms_pin_the_metric_to_the_ceiling(self):
        """THE key invariant: with no selectivity whatsoever the metric cannot exceed the ceiling. If this
        ever fails, the model is manufacturing selectivity out of nothing and every conclusion is void."""
        p = dict(FAST)
        kappa = smm.calibrate_drive(p, p["kd_target_uM"], p["alpha_baseline"], p["ubiq_efficiency"])
        p = dict(p, k_ub_max_over_k_basal=kappa)
        arm = (p["kd_target_uM"], p["kd_e3_uM"], p["alpha_baseline"], p["ubiq_efficiency"])
        w = smm.window(arm, arm, p)
        self.assertLessEqual(w["deg_nr4a3_at_ceiling"], p["paralogue_ceiling"] + 1e-9)

    def test_a_favourable_margin_beats_the_null(self):
        p = dict(FAST)
        a3 = p["alpha_baseline"] * smm.fold_from_ddg(2.0)
        kappa = smm.calibrate_drive(p, p["kd_target_uM"], a3, p["ubiq_efficiency"])
        p = dict(p, k_ub_max_over_k_basal=kappa)
        w = smm.window((p["kd_target_uM"], p["kd_e3_uM"], a3, p["ubiq_efficiency"]),
                       (p["kd_target_uM"], p["kd_e3_uM"], p["alpha_baseline"], p["ubiq_efficiency"]), p)
        self.assertGreater(w["deg_nr4a3_at_ceiling"], p["paralogue_ceiling"])


class TestRequiredMargin(unittest.TestCase):
    def test_thresholds_are_monotone_in_the_target(self):
        r = smm.required_margin(FAST, margin_grid=[0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0])
        t = r["required_margin_kcal_by_target"]
        got = [(float(k), v) for k, v in t.items() if v is not None]
        got.sort()
        self.assertEqual([v for _, v in got], sorted(v for _, v in got),
                         "a harder degradation target must never need LESS margin")


class TestMDD(unittest.TestCase):
    def test_known_value(self):
        self.assertAlmostEqual(smm.minimum_detectable_difference(0.7, 3), 1.96 * 0.7 * math.sqrt(2 / 3), places=9)

    def test_shrinks_with_replicates(self):
        self.assertLess(smm.minimum_detectable_difference(0.7, 8), smm.minimum_detectable_difference(0.7, 2))

    def test_rejects_zero_replicates(self):
        with self.assertRaises(ValueError):
            smm.minimum_detectable_difference(0.7, 0)


class TestCovalentKinetics(unittest.TestCase):
    def test_labelled_fraction_is_monotone_and_bounded(self):
        prev = -1.0
        for h in (0.0, 1.0, 6.0, 24.0, 72.0):
            L = smm.covalent_labelled_fraction(1.0, 0.1, 0.2, h)
            self.assertGreaterEqual(L, prev)
            self.assertTrue(0.0 <= L < 1.0)
            prev = L

    def test_no_exposure_means_no_adduct(self):
        self.assertEqual(smm.covalent_labelled_fraction(1.0, 0.1, 0.2, 0.0), 0.0)

    def test_kinetic_form_is_not_weaker_than_the_null(self):
        w = smm.covalent_kinetic_window(FAST)
        self.assertIsNotNone(w)
        self.assertGreaterEqual(w["deg_nr4a3_at_ceiling"], FAST["paralogue_ceiling"] - 1e-9)


class TestCategoricalAxes(unittest.TestCase):
    def setUp(self):
        self.cat = smm.categorical_axes(FAST)

    def test_null_scenario_is_the_ceiling(self):
        self.assertLessEqual(self.cat["interface_thermodynamics_only"]["deg_nr4a3_at_ceiling"],
                             FAST["paralogue_ceiling"] + 1e-9)

    def test_unique_lysine_beats_the_null_at_zero_margin(self):
        self.assertGreater(self.cat["unique_lysine"]["deg_nr4a3_at_ceiling"],
                           self.cat["interface_thermodynamics_only"]["deg_nr4a3_at_ceiling"])

    def test_kinetic_covalent_is_at_least_the_equilibrium_proxy(self):
        """The equilibrium proxy is documented as a LOWER bound — assert it actually is one."""
        self.assertGreaterEqual(self.cat["covalent_capture_KINETIC"]["deg_nr4a3_at_ceiling"],
                                self.cat["covalent_capture"]["deg_nr4a3_at_ceiling"])

    def test_every_scenario_respects_the_paralogue_ceiling(self):
        for k, v in self.cat.items():
            if k.startswith("_"):
                continue
            self.assertLessEqual(v["deg_paralogue"], FAST["paralogue_ceiling"] + 1e-9, k)


class TestResolvableMarginIsDerivedFromTheMEASUREDReplicateSD(unittest.TestCase):
    """★ THE FIGURE THIS PROGRAM STEERED BY FOR A MONTH WAS COMPUTED AT AN SD NOTHING HAD MEASURED.

    nr4a3-program-map.md's MECHANISM-FIRST bullet quotes a best-case resolvable difference, and that one number carried
    the demotion of the induced-interface axis to 'a confirmation tool operating near its limit', the Tier-3
    kill-switch semantics, the 5a-KS 'a null is likely' expectation, and the Spend-summary defence of
    mechanism-first. It was `minimum_detectable_difference(0.7, 3)` — and 0.7 was an ASSUMPTION. The n=3
    valB_mini replicates measured the replicate SD at 0.375, which is the value below.

    These tests exist so the live figure can never again be a typed one: they pin the arithmetic, the
    measured input, and the DIRECTION of the correction, so an edit that quietly reinstates 0.7 (or types a
    round number next to it) fails here rather than in a strategy re-read months later."""

    MEASURED_CYCLE_SD = 0.375        # valb_failure_propagation.MEASURED['cycle_sd_kcal'], n = 3
    SUPERSEDED_SD = 0.7              # never measured by anything in this program

    def test_the_live_resolvable_figure_is_what_the_model_computes(self):
        self.assertAlmostEqual(smm.minimum_detectable_difference(self.MEASURED_CYCLE_SD, 3), 0.60, places=2,
                               msg="nr4a3-program-map.md/paper state 0.60 — it must be this function's output, not prose")

    def test_the_measured_sd_agrees_with_the_module_that_measured_it(self):
        """One fact, one place: the SD used here must be the one valb_failure_propagation actually landed."""
        import valb_failure_propagation as P
        self.assertAlmostEqual(P.MEASURED["cycle_sd_kcal"], self.MEASURED_CYCLE_SD, places=3)

    def test_the_correction_improves_the_noise_floor_by_the_ratio_of_the_SDs(self):
        """MDD is linear in the SD, so the whole correction is 0.7/0.375 — worth pinning because it is the
        reason the required margin moved from ~1.8x the floor to ~3.3x."""
        old = smm.minimum_detectable_difference(self.SUPERSEDED_SD, 3)
        new = smm.minimum_detectable_difference(self.MEASURED_CYCLE_SD, 3)
        self.assertAlmostEqual(old / new, self.SUPERSEDED_SD / self.MEASURED_CYCLE_SD, places=6)
        self.assertGreater(old, new, "the measured SD is the SMALLER one — precision improved")

    def test_a_2p0_margin_now_sits_above_3x_the_floor(self):
        """The strategic claim the correction licenses, asserted rather than narrated. ⚠ It is a claim about
        PRECISION only — accuracy is measured separately at 1.543 kcal/mol wrong-sign and is not improved by
        anything in this module."""
        ratio = 2.0 / smm.minimum_detectable_difference(self.MEASURED_CYCLE_SD, 3)
        self.assertGreater(ratio, 3.0)
        self.assertLess(2.0 / smm.minimum_detectable_difference(self.SUPERSEDED_SD, 3), 2.0,
                        "and the superseded figure really did put it under 2x, which is why it read as marginal")

    def test_S_at_one_seed_per_arm_cannot_resolve_the_bottom_of_its_own_designed_effect(self):
        """The 5a-KS design consequence, in one assertion: at n = 1 the resolvable difference sits ABOVE the
        low end of the pair's expected 0.5-1.5 kcal/mol effect, so the pre-registered likely outcome (a null)
        is uninterpretable — and at n = 2 it does not."""
        at_n1 = smm.minimum_detectable_difference(self.MEASURED_CYCLE_SD, 1)
        at_n2 = smm.minimum_detectable_difference(self.MEASURED_CYCLE_SD, 2)
        self.assertGreater(at_n1, 1.0, "n=1 cannot see an effect at the top of the range either, comfortably")
        self.assertLess(at_n2, at_n1, "a second seed per arm is what buys the bound")


if __name__ == "__main__":
    unittest.main(verbosity=2)
