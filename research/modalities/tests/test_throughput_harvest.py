"""THE HARVEST — and the quantization defect that made its first answer wrong.

The headline test is `TestQuantizationRegression`. Reading the committed progress trail pairwise produced an
RTX 4090 warmup rate 2.5x the same instance's own full-span rate, purely because a short window happened to
contain one commit boundary — and that inflated number then "falsified" the benched RTX 4090 : RTX 4080 ratio.
A harvest that can manufacture a contradiction of the anchor table is worse than no harvest, so the span
estimator and its `quant_err` bound are pinned here with the exact numbers that exposed the bug.
"""
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import throughput_harvest as th  # noqa: E402
import vast_cost_model as vcm  # noqa: E402

T0 = datetime(2026, 7, 27, 0, 0, tzinfo=timezone.utc)
UNIT = "e_zaienne_cmpd19__cw_ev_5cooh__neutral__neutral_acid"
LABEL = "s1f-02-cw_ev_5cooh"


def snap(minutes, scalar, card="RTX 4090", iid=1, label=LABEL, util=95.0, dph=0.2):
    return (T0 + timedelta(minutes=minutes),
            {"instances": [{"id": iid, "gpu": card, "label": label, "gpu_util": util, "dph": dph}],
             "units": [{"unit_id": UNIT, "committed_scalar": scalar}]})


def complex_production(it):
    return 1 * th._PHASE_STRIDE + it       # leg=complex (0), phase=production (1)


def complex_warmup(it):
    return it


class TestScalarDecoding(unittest.TestCase):
    def test_the_strides_match_the_lane_that_writes_them(self):
        """These are decoded, not imported, so they must be pinned against the source that encodes them."""
        src = open(os.path.join(HERE, "..", "congeneric_fanout_vast.py")).read()
        self.assertIn("_PHASE_STRIDE = 1_000_000", src)
        self.assertIn("_LEG_STRIDE = 10_000_000", src)
        self.assertEqual(th._PHASE_STRIDE, 1_000_000)
        self.assertEqual(th._LEG_STRIDE, 10_000_000)

    def test_round_trip(self):
        self.assertEqual(th.decode_scalar(11001440), ("solvent", "production", 1440))
        self.assertEqual(th.decode_scalar(120), ("complex", "warmup", 120))

    def test_an_unreadable_census_is_not_zero_progress(self):
        self.assertEqual(th.decode_scalar(-1), (None, None, None))


class TestAttribution(unittest.TestCase):
    def test_a_label_maps_to_its_unit(self):
        self.assertEqual(th.unit_of_label(LABEL, [UNIT, "e_other__cw_bio_tetrazole__x__y"]), UNIT)

    def test_an_ambiguous_label_is_refused_rather_than_tie_broken(self):
        """Attributing an interval to the wrong unit invents a rate from two unrelated counters, and nothing
        downstream would catch it."""
        self.assertIsNone(th.unit_of_label("s1f-02-cw", [UNIT, "e_x__cw_bio__a__b"]))


class TestQuantizationRegression(unittest.TestCase):
    """The real trail that produced the false falsification, reduced to its essentials."""

    def setUp(self):
        # Warmup commits every 20 iterations. Eight ticks over 0.72 h advancing 100 iterations = 139.5/h.
        # One of the gaps is 3.6 min and contains a single 20-iteration boundary -> 344.8/h read pairwise.
        self.snaps = [snap(0, complex_warmup(0)), snap(12.6, complex_warmup(60)),
                      snap(22.3, complex_warmup(80)), snap(25.9, complex_warmup(100)),
                      snap(43.2, complex_warmup(100))]

    def test_the_pairwise_read_that_was_wrong_is_not_what_the_span_estimator_returns(self):
        obs = th.rate_observations(self.snaps, max_quant_err=1.0)
        self.assertEqual(len(obs), 1, "one instance, one phase -> exactly one span")
        self.assertAlmostEqual(obs[0]["iter_per_h"], 100 / (43.2 / 60.0), delta=1.0)
        self.assertLess(obs[0]["iter_per_h"], 200,
                        "the 344/h pairwise artifact must not survive the span estimator")

    def test_the_quantization_bound_is_reported_and_enforced(self):
        obs = th.rate_observations(self.snaps, max_quant_err=1.0)
        self.assertAlmostEqual(obs[0]["quant_err"], 2 * 20 / 100.0, places=6)
        self.assertEqual(th.rate_observations(self.snaps, max_quant_err=0.1), [],
                         "an observation that could be 40% high is not a lower bound on anything")

    def test_a_long_span_earns_a_tight_bound(self):
        long = [snap(0, complex_production(0)), snap(30, complex_production(40)),
                snap(90, complex_production(2000))]
        obs = th.rate_observations(long)
        self.assertEqual(len(obs), 1)
        self.assertLess(obs[0]["quant_err"], 0.05)

    def test_no_false_falsification_survives_the_fix(self):
        """The exact shape of the bug: a 4090 warmup span and a 4080S warmup span, where the pairwise read
        made the 4090 look 1.5x the 4080S against a benched ratio near 1.07."""
        s = self.snaps + [snap(60 + 12 * i, complex_warmup(80 * i), card="RTX 4080S", iid=2,
                               label="s1f-03-cw_ev_5oh") for i in range(4)]
        s.sort(key=lambda x: x[0])
        obs = th.rate_observations(s)
        self.assertEqual(th.falsifications(th.ratio_observations(obs)), [],
                         "the quantization gate must drop the observations that manufactured this")


class TestTheHarvestNeverBecomesATableEntry(unittest.TestCase):
    def test_the_realised_quantity_is_named_for_the_leg_not_the_table(self):
        obs = th.rate_observations([snap(0, complex_production(0)), snap(30, complex_production(40)),
                                    snap(90, complex_production(2000))])
        self.assertIn("ns_per_day_at_leg_size", obs[0])
        self.assertNotIn("ns_per_day", obs[0])
        self.assertIn("NOT the 84,534-particle", obs[0]["_quantity"])

    def test_the_module_never_writes_the_table(self):
        src = open(os.path.join(HERE, "..", "throughput_harvest.py")).read()
        self.assertNotIn("MEASURED_NS_PER_DAY_84K[", src.replace("_vcm.MEASURED_NS_PER_DAY_84K[", ""))
        self.assertNotIn("MEASURED_NS_PER_DAY_84K =", src)

    def test_a_ratio_needs_a_benched_reference_on_the_denominator(self):
        s = [snap(0, complex_production(0), card="H200 NVL", iid=1),
             snap(30, complex_production(40), card="H200 NVL", iid=1),
             snap(90, complex_production(2000), card="H200 NVL", iid=1),
             snap(0, complex_production(0), card="B200", iid=2, label="s1f-03-cw_ev_5oh"),
             snap(30, complex_production(40), card="B200", iid=2, label="s1f-03-cw_ev_5oh"),
             snap(90, complex_production(1000), card="B200", iid=2, label="s1f-03-cw_ev_5oh")]
        # both cards unbenched -> no anchor, so no ratio may be formed
        self.assertEqual(th.ratio_observations(th.rate_observations(sorted(s, key=lambda x: x[0]))), [])


class TestCoverageCensus(unittest.TestCase):
    def test_it_names_cards_that_are_new_to_the_table(self):
        cov = th.coverage([], [snap(0, 0, card="H200 NVL"), snap(10, 0, card="RTX 4090")])
        self.assertEqual(cov["n_new_cards"], 1)
        self.assertEqual(cov["n_already_benched"], 1)

    def test_a_conservative_alias_counts_as_benched_not_new(self):
        cov = th.coverage([], [snap(0, 0, card="RTX 4080S")])
        self.assertEqual(cov["n_new_cards"], 0)
        self.assertEqual(cov["cards"][0]["throughput_provenance"], "conservative_alias")


class TestGapsBreakChains(unittest.TestCase):
    def test_an_unobserved_gap_is_not_measured_across(self):
        """A long silence may hide a preemption, a relaunch or a stop; the endpoints cannot tell us."""
        s = [snap(0, complex_production(0)), snap(30, complex_production(40)),
             snap(90, complex_production(2000)),
             # a 2 h silence, then the same instance resumes
             snap(210, complex_production(2040)), snap(240, complex_production(2080)),
             snap(300, complex_production(4000))]
        obs = th.rate_observations(s)
        self.assertEqual(len(obs), 2, "the >1.5 h gap must split the chain, not average across it")

    def test_a_phase_change_is_never_measured_across(self):
        """The iteration counter restarts at each phase, so a straddling span subtracts two counters."""
        s = [snap(0, complex_warmup(0)), snap(30, complex_warmup(40)), snap(80, complex_warmup(1600)),
             snap(110, complex_production(40)), snap(170, complex_production(2000))]
        for o in th.rate_observations(s):
            self.assertGreater(o["d_iter"], 0)
            self.assertIn(o["phase"], ("warmup", "production"))


if __name__ == "__main__":
    unittest.main()


class TestAShallowCheckoutCannotFakeAgreement(unittest.TestCase):
    """OBSERVED 2026-07-27. actions/checkout clones at depth 1, so in CI `git log` over the progress artifact
    returned NOTHING and the census reported 0 snapshots / 0 cards / 0 new — which reads exactly like 'no
    production leg has ever run on an unbenched card', the conclusion this module argues for. A silent zero
    that agrees with your hypothesis is the worst failure available, so it must raise instead."""

    def test_an_empty_log_on_a_shallow_clone_raises_instead_of_returning_nothing(self):
        real = th._sh
        try:
            th._sh = lambda cmd: ("true" if "is-shallow" in cmd else "")
            with self.assertRaises(RuntimeError) as cm:
                th.load_snapshots()
            self.assertIn("SHALLOW", str(cm.exception))
            self.assertIn("fetch-depth", str(cm.exception))
        finally:
            th._sh = real

    def test_a_genuinely_empty_history_on_a_FULL_clone_is_not_an_error(self):
        """An artifact that simply has no commits yet is a real, reportable zero."""
        real = th._sh
        try:
            th._sh = lambda cmd: ("false" if "is-shallow" in cmd else "")
            self.assertEqual(th.load_snapshots(), [])
        finally:
            th._sh = real

    def test_the_workflow_asks_for_full_history(self):
        wf = os.path.join(HERE, "..", "..", "..", ".github", "workflows", "vast-bench-sweep.yml")
        self.assertIn("fetch-depth: 0", open(wf).read())
