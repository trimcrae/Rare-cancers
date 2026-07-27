"""THE ADMISSION GATE — what may and may not become a `MEASURED_NS_PER_DAY_84K` entry.

Every case below is an incident this repo has actually had, or the direct inverse of one. The gate is the only
thing standing between a rented GPU and the constant that anchors every `$/ns` in the project, so a test here
is not coverage — it names the specific reasoning that breaks if the gate is loosened.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import vast_bench_sweep as sweep  # noqa: E402
import vast_cost_model as vcm  # noqa: E402


def rec(**kw):
    """A record that PASSES, so each test can break exactly one thing."""
    base = {
        "status": "OK", "atoms": sweep.BENCH_ATOMS, "platform": "CUDA",
        "device": "NVIDIA GeForce RTX 5090", "offer_gpu_name": "RTX 5090", "gpu_requested": "RTX 5090",
        "steps": 900000, "dt_fs": 4.0, "wall_s": 61.2, "blocks": 3,
        "blocks_ns_day": [900.0, 902.0, 898.0], "ns_per_day": 900.0,
        "cv": 0.0022, "final_temp_k": 299.4, "healthy": True,
    }
    base.update(kw)
    return base


class TestParse(unittest.TestCase):
    LINE = ("BENCH_RESULT tag=rtx5090 status=OK atoms=84534 platform=CUDA device=NVIDIA_GeForce_RTX_5090 "
            "steps=900000 dt_fs=4.0 wall_s=61.2 ns_per_day=900.00 sd=2.00 cv=0.0022 blocks=3 "
            "blocks_ns_day=900.00,902.00,898.00 final_temp_k=299.4 healthy=True")

    def test_round_trips_into_an_admissible_record(self):
        r = sweep.parse_bench_line(self.LINE)
        r["offer_gpu_name"] = "RTX 5090"
        r["gpu_requested"] = "RTX 5090"
        ok, why, entry = sweep.admit(r)
        self.assertTrue(ok, why)
        self.assertEqual(entry, ("RTX5090", 900.0))

    def test_the_underscored_device_name_is_restored(self):
        """gpu_md_bench underscores it because the line is split on spaces — `device='Quadro RTX 8000'`
        arrived as `device='Quadro'` on 2026-07-24 and a card went unidentified."""
        r = sweep.parse_bench_line(self.LINE)
        self.assertEqual(r["device"], "NVIDIA GeForce RTX 5090")

    def test_a_missing_line_does_not_raise(self):
        self.assertEqual(sweep.parse_bench_line("")["healthy"], False)


class TestProtocolIdentity(unittest.TestCase):
    def test_a_different_particle_count_is_a_different_quantity(self):
        ok, why, _ = sweep.admit(rec(atoms=36000))
        self.assertFalse(ok)
        self.assertTrue(any("particle count" in w for w in why), why)

    def test_a_different_timestep_is_refused(self):
        ok, why, _ = sweep.admit(rec(dt_fs=2.0))
        self.assertFalse(ok)
        self.assertTrue(any("timestep" in w for w in why), why)

    def test_an_opencl_or_cpu_run_is_refused(self):
        for plat in ("OpenCL", "CPU"):
            ok, why, _ = sweep.admit(rec(platform=plat))
            self.assertFalse(ok, plat)
            self.assertTrue(any("platform" in w for w in why), why)

    def test_a_single_timed_window_is_refused(self):
        ok, why, _ = sweep.admit(rec(blocks=1, blocks_ns_day=[900.0]))
        self.assertFalse(ok)
        self.assertTrue(any("timed block" in w for w in why), why)

    def test_short_blocks_are_refused__the_withdrawn_2026_07_24_grid(self):
        """Its windows were 0.9-4.5 s, which measured boost-clock ramp and ranked a 4080S above a 4090."""
        ok, why, _ = sweep.admit(rec(wall_s=6.0))
        self.assertFalse(ok)
        self.assertTrue(any("boost-clock" in w for w in why), why)

    def test_the_real_bench_duration_passes(self):
        self.assertTrue(sweep.admit(rec(wall_s=60.0))[0])


class TestDeviceIdentity(unittest.TestCase):
    def test_a_fallback_to_another_card_is_refused(self):
        """The 2026-07-24 failure: the offer search fell back to a Quadro RTX 8000 and it was tabulated as an
        A10. The number was fine; it belonged to a different card."""
        ok, why, _ = sweep.admit(rec(gpu_requested="A10", offer_gpu_name="Quadro RTX 8000",
                                     device="Quadro RTX 8000"))
        self.assertFalse(ok)
        self.assertTrue(any("card identity disagrees" in w for w in why), why)

    def test_a_vendor_prefix_is_not_a_disagreement(self):
        """The CUDA driver says 'NVIDIA GeForce RTX 4090'; the marketplace says 'RTX 4090'. Same card."""
        ok, why, entry = sweep.admit(rec(device="NVIDIA GeForce RTX 4090", offer_gpu_name="RTX 4090",
                                         gpu_requested="RTX 4090"))
        self.assertTrue(ok, why)
        self.assertEqual(entry[0], "RTX4090")

    def test_a_trailing_qualifier_IS_a_different_card(self):
        """`RTX 4090D` is the cut-down China SKU. Renting a 4090 and being handed a 4090D must not pass."""
        ok, why, _ = sweep.admit(rec(gpu_requested="RTX 4090", offer_gpu_name="RTX 4090",
                                     device="NVIDIA GeForce RTX 4090D"))
        self.assertFalse(ok)
        self.assertTrue(any("card identity disagrees" in w for w in why), why)


class TestPhysicsAndStability(unittest.TestCase):
    def test_a_blown_up_system_is_refused(self):
        """A diverged run integrates fast and reports a large, entirely fake ns/day."""
        ok, why, _ = sweep.admit(rec(healthy=False, final_temp_k=1e6))
        self.assertFalse(ok)
        self.assertTrue(any("physics check FAILED" in w for w in why), why)

    def test_a_contended_host_is_refused_on_cv_not_on_its_mean(self):
        ok, why, _ = sweep.admit(rec(cv=0.185, blocks_ns_day=[400.0, 900.0, 1400.0], ns_per_day=900.0))
        self.assertFalse(ok)
        self.assertTrue(any("CV" in w for w in why), why)

    def test_the_worst_kept_anchor_cv_still_passes(self):
        """The RTX 3090 anchor was kept at CV 1.31%; the gate must not retroactively reject an anchor."""
        self.assertTrue(sweep.admit(rec(cv=0.0131))[0])


class TestTheNumberIsDerivedNotAsserted(unittest.TestCase):
    def test_a_mean_that_disagrees_with_its_own_blocks_is_refused(self):
        ok, why, _ = sweep.admit(rec(ns_per_day=1500.0))
        self.assertFalse(ok)
        self.assertTrue(any("mean of its own blocks" in w for w in why), why)

    def test_missing_blocks_are_refused(self):
        ok, why, _ = sweep.admit(rec(blocks_ns_day=[]))
        self.assertFalse(ok)

    def test_the_admitted_entry_is_the_mean_of_the_blocks(self):
        _ok, _why, entry = sweep.admit(rec(blocks_ns_day=[100.0, 110.0, 120.0], ns_per_day=110.0))
        self.assertEqual(entry[1], 110.0)

    def test_every_refusal_is_reported_not_just_the_first(self):
        ok, why, _ = sweep.admit(rec(atoms=1, dt_fs=2.0, platform="CPU"))
        self.assertFalse(ok)
        self.assertGreaterEqual(len(why), 3)


class TestSpendCeilings(unittest.TestCase):
    def test_worst_case_is_the_full_runtime_not_an_expected_value(self):
        self.assertAlmostEqual(sweep.worst_case_usd(0.20, 0.01, 1800), 0.105, places=6)

    def test_a_dear_card_is_held_by_the_per_card_cap(self):
        # H200 NVL rather than RTX 5090: the 5090 was benched on 2026-07-27, and these cases need a card the
        # planner still has something to buy for.
        offers = [_offer("H200 NVL", min_bid=5.0)]
        rows = sweep.plan_sweep(offers, max_usd_per_card=0.20, max_usd_total=10.0, max_runtime_s=1800)
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["admit"])
        self.assertIn("per-card cap", rows[0]["reason"])

    def test_the_sweep_cap_HOLDS_rather_than_drops(self):
        offers = [_offer("H200 NVL", min_bid=0.30, oid=1, mid="1"),
                  _offer("L40S", min_bid=0.31, oid=2, mid="2"),
                  _offer("H100 NVL", min_bid=0.32, oid=3, mid="3")]
        rows = sweep.plan_sweep(offers, max_usd_per_card=1.0, max_usd_total=0.35, max_runtime_s=1800)
        self.assertTrue(rows[0]["admit"])
        held = [r for r in rows if not r["admit"]]
        self.assertTrue(held)
        self.assertIn("HELD, not dropped", held[0]["reason"])

    def test_a_card_already_measured_is_not_re_bought(self):
        rows = sweep.plan_sweep([_offer("RTX 4090"), _offer("H200 NVL", oid=2, mid="2")])
        self.assertEqual([r["gpu_name"] for r in rows], ["H200 NVL"])

    def test_a_conservative_alias_IS_still_worth_measuring(self):
        """`RTX 4080S` borrows the 4080's figure as a LOWER BOUND. That is a bridge, not a resting place —
        the sweep must still offer to turn it into a measurement."""
        rows = sweep.plan_sweep([_offer("RTX 4080S")])
        self.assertEqual([r["gpu_name"] for r in rows], ["RTX 4080S"])

    def test_the_cheapest_card_is_planned_first_so_the_budget_buys_breadth(self):
        rows = sweep.plan_sweep([_offer("H200 NVL", min_bid=0.40, oid=1, mid="1"),
                                 _offer("Titan RTX", min_bid=0.05, oid=2, mid="2")])
        self.assertEqual(rows[0]["gpu_name"], "Titan RTX")

    def test_a_host_that_fails_the_production_filters_is_never_benched(self):
        """A number measured on a host we could not rent for real work prices a machine we cannot buy."""
        rows = sweep.plan_sweep([_offer("H200 NVL", cuda=12.0)])
        self.assertEqual(rows, [])


class TestJobspec(unittest.TestCase):
    def test_the_card_is_a_HARD_constraint(self):
        spec = sweep.build_jobspec("RTX 5090", "branch", "bucket", wave="", max_runtime_s=1800)
        self.assertTrue(spec.resources.require_gpu,
                        "without require_gpu a 5090 bench lands on a 4090 and is filed under the 5090")
        self.assertEqual(spec.resources.gpu, "RTX 5090")

    def test_the_protocol_env_is_the_anchors_protocol(self):
        spec = sweep.build_jobspec("RTX 5090", "branch", "bucket", wave="", max_runtime_s=1800)
        self.assertEqual(spec.env["BENCH_EDGE_NM"], sweep.BENCH_EDGE_NM)
        self.assertEqual(float(spec.env["BENCH_DT_FS"]), sweep.BENCH_DT_FS)
        self.assertEqual(int(spec.env["BENCH_BLOCKS"]), sweep.BENCH_BLOCKS)

    def test_the_runtime_cap_bounds_the_bill(self):
        spec = sweep.build_jobspec("RTX 5090", "branch", "bucket", wave="", max_runtime_s=1800)
        self.assertLessEqual(spec.max_runtime_s, 3600)

    def test_it_runs_on_the_image_the_science_runs_on(self):
        """A bespoke bench image would measure a CUDA/OpenMM build we never use."""
        self.assertIn("nr4a3fep", sweep.build_jobspec("RTX 5090", "b", "k").image)


class TestNoSecondTable(unittest.TestCase):
    def test_this_module_holds_no_throughput_of_its_own(self):
        """A second table is exactly how a withdrawn 669 ns/day survived for a day."""
        src = open(os.path.join(HERE, "..", "vast_bench_sweep.py")).read()
        body = src.split('"""', 2)[2]
        # Reading the table is the point; DEFINING one is the bug.
        self.assertNotIn("MEASURED_NS_PER_DAY_84K =", body,
                         "the sweep must reference the table, never redefine it")
        self.assertIn("_vcm.MEASURED_NS_PER_DAY_84K", body)
        for v in vcm.MEASURED_NS_PER_DAY_84K.values():
            self.assertNotIn(str(v), src, f"{v} is typed into the sweep — it must come from the table")


def _offer(gpu, min_bid=0.20, storage=0.20, vram_gb=32, rel=0.99, cuda=13.5, mid="1", oid=1):
    return {"id": oid, "machine_id": mid, "gpu_name": gpu, "min_bid": min_bid, "storage_cost": storage,
            "gpu_ram": vram_gb * 1024, "reliability2": rel, "cuda_max_good": cuda, "num_gpus": 1,
            "rentable": True}


if __name__ == "__main__":
    unittest.main()


class TestReplicatesMeasureDIFFERENTHosts(unittest.TestCase):
    """A replicate exists to answer 'is this the CARD or was it this RENTAL?'. It answers nothing if it lands
    on the same machine, and it answers nothing if it overwrites its sibling's S3 key — the exact failure that
    made the 2026-07-24 host-variance control return a single number."""

    def test_each_replicate_gets_its_own_result_key(self):
        a = sweep.build_jobspec("RTX 4090", "b", "k", replicate=1, wave="")
        b = sweep.build_jobspec("RTX 4090", "b", "k", replicate=2, wave="")
        self.assertNotEqual(a.env["RESULT_S3"], b.env["RESULT_S3"])
        self.assertNotEqual(a.name, b.name)
        self.assertNotEqual(a.env["BENCH_TAG"], b.env["BENCH_TAG"])

    def test_the_first_replicate_keeps_the_plain_tag(self):
        self.assertEqual(sweep.build_jobspec("RTX 4090", "b", "k", wave="").env["BENCH_TAG"], "rtx4090")

    def test_a_replicate_can_exclude_the_machine_its_sibling_took(self):
        spec = sweep.build_jobspec("RTX 4090", "b", "k", exclude_machine_ids=("12345",), replicate=2, wave="")
        self.assertEqual(spec.resources.exclude_machine_ids, ("12345",))

    def test_an_already_measured_card_is_re_benchable_when_asked(self):
        """Re-measuring an ANCHOR is the whole point when its value is in question."""
        offers = [_offer("RTX 4090", min_bid=0.14)]
        self.assertEqual(sweep.plan_sweep(offers), [])
        rows = sweep.plan_sweep(offers, include_measured=True)
        self.assertEqual([r["gpu_name"] for r in rows], ["RTX 4090"])


class TestAFailedBenchProducesNoNumber(unittest.TestCase):
    """OBSERVED 2026-07-27: 2 of 6 calibration rentals died with `Particle coordinate is NaN` during
    minimise/warmup. `gpu_md_bench` then emits a `status=ERROR` line with no measurement at all. The gate must
    refuse it loudly rather than let a partly-parsed record become an entry — a rental that failed is the one
    case where a fabricated throughput would be easiest to produce and hardest to notice."""

    ERROR_LINE = ("BENCH_RESULT tag=rtx4090-r2 status=ERROR "
                  "err=OpenMMException:Particle coordinate is NaN.")

    def test_an_error_line_is_refused_and_yields_no_entry(self):
        r = sweep.parse_bench_line(self.ERROR_LINE)
        r["gpu_requested"] = "RTX 4090"
        ok, why, entry = sweep.admit(r)
        self.assertFalse(ok)
        self.assertIsNone(entry)
        self.assertTrue(any("status 'ERROR'" in w for w in why), why)

    def test_the_refusal_names_the_missing_evidence_not_just_the_status(self):
        """A single 'status != OK' would hide that there is no system, no timestep and no blocks either."""
        r = sweep.parse_bench_line(self.ERROR_LINE)
        r["gpu_requested"] = "RTX 4090"
        _ok, why, _e = sweep.admit(r)
        self.assertGreaterEqual(len(why), 5)

    def test_a_failed_rental_never_reaches_the_provenance_file(self):
        r = sweep.parse_bench_line(self.ERROR_LINE)
        r["gpu_requested"] = "RTX 4090"
        self.assertIsNone(sweep.admit(r)[2])


class TestDeviceNameEquivalences(unittest.TestCase):
    """An ALLOW-LIST, not a loosened heuristic. Two admissible measurements (A100 PCIe, RTX PRO 4000) were
    refused on 2026-07-27 because the CUDA string carries capacity/architecture tokens the marketplace name
    omits. The obvious fix — token containment — would admit `NVIDIA GeForce RTX 4090 D` as an RTX 4090,
    because its tokens are a strict SUPERSET. So equivalence is enumerated and everything else fails closed."""

    def _rec(self, device, requested):
        return rec(device=device, gpu_requested=requested, offer_gpu_name=requested,
                   blocks_ns_day=[500.0, 500.0, 500.0], ns_per_day=500.0)

    def test_a_capacity_token_in_the_middle_is_the_same_card(self):
        ok, why, entry = sweep.admit(self._rec("NVIDIA A100 80GB PCIe", "A100 PCIE"))
        self.assertTrue(ok, why)
        self.assertEqual(entry[0], "A100PCIE")

    def test_an_architecture_token_at_the_end_is_the_same_card(self):
        ok, why, entry = sweep.admit(self._rec("NVIDIA RTX PRO 4000 Blackwell", "RTX PRO 4000"))
        self.assertTrue(ok, why)
        self.assertEqual(entry[0], "RTXPRO4000")

    def test_the_4090D_GUARD_SURVIVES_THE_FIX(self):
        """The whole reason this is an allow-list. A cut-down SKU must never inherit the full card."""
        ok, why, _ = sweep.admit(self._rec("NVIDIA GeForce RTX 4090 D", "RTX 4090"))
        self.assertFalse(ok, "token containment would have admitted this")
        self.assertTrue(any("card identity disagrees" in w for w in why), why)

    def test_an_unlisted_mismatch_still_fails_closed(self):
        ok, _why, _e = sweep.admit(self._rec("Quadro RTX 8000", "A10"))
        self.assertFalse(ok)

    def test_no_equivalence_maps_two_different_benched_cards_together(self):
        """A typo here would silently merge two cards' measurements."""
        vals = list(sweep.DEVICE_NAME_EQUIVALENCES.values())
        self.assertEqual(len(vals), len(set(vals)) + vals.count("A100PCIE") - 1,
                         "only the A100 capacity variants may share a key")


class TestTheSpendGateIsNotProcessDependent(unittest.TestCase):
    """⛔ THE BUG THE CI GATE CAUGHT BEFORE IT COULD SPEND (2026-07-27).

    `plan_sweep` / `worst_case_usd` / `build_jobspec` are documented PURE, but they fell back to module
    constants read from `os.environ` at import. Under the launch job's env (`BENCH_MAX_RUNTIME_S=1200`,
    `BENCH_WAVE=w2`) the very same call returned a different worst-case cost and a different S3 tag than in a
    bare shell. For functions that decide what to RENT that is disqualifying — the ceiling that was tested is
    then not the ceiling that runs, and the tag that was unique is not the tag that gets written. Given
    explicit arguments the answer must not depend on the process."""

    def _run(self, env):
        old = {k: os.environ.get(k) for k in env}
        os.environ.update(env)
        try:
            offers = [_offer("H200 NVL", min_bid=0.30, oid=1, mid="1"),
                      _offer("L40S", min_bid=0.31, oid=2, mid="2"),
                      _offer("H100 NVL", min_bid=0.32, oid=3, mid="3")]
            rows = sweep.plan_sweep(offers, max_usd_per_card=1.0, max_usd_total=0.35, max_runtime_s=1800)
            tag = sweep.build_jobspec("RTX 4090", "b", "k", wave="", max_runtime_s=1800).env["BENCH_TAG"]
            return [(r["gpu_name"], r["admit"], r["worst_case_usd"]) for r in rows], tag
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_identical_arguments_give_identical_answers_under_different_env(self):
        bare = self._run({"BENCH_MAX_RUNTIME_S": "1800", "BENCH_WAVE": ""})
        launch = self._run({"BENCH_MAX_RUNTIME_S": "1200", "BENCH_WAVE": "w2"})
        self.assertEqual(bare, launch)

    def test_and_the_cap_still_holds_somebody_back(self):
        rows, _tag = self._run({"BENCH_MAX_RUNTIME_S": "1200", "BENCH_WAVE": "w2"})
        self.assertTrue(any(not admit for _n, admit, _c in rows),
                        "the sweep cap must HOLD a unit, not admit everything")


class TestReMeasuringAnAnchorIsNotSubjectToTheDiscoveryScreen(unittest.TestCase):
    """OBSERVED 2026-07-27: the plausibility screen silently refused to re-bench the RTX 4090, RTX 4080 and
    A100 PCIe — i.e. it would have left the REFERENCE CARD on the old one-host statistic, which is precisely
    the inconsistency the re-measurement exists to remove.

    The screen answers 'is this unknown card worth DISCOVERING at today's price'. A card already in the table
    is not being discovered; it is being moved onto the same estimator as every other entry, and that value
    does not depend on whether its price is attractive this minute."""

    def test_an_already_measured_card_survives_a_skip_verdict(self):
        # priced so the break-even lands far above the reference card -> `skip` for an unknown card
        offers = [_offer("RTX 4090", min_bid=0.55, oid=1, mid="1")]
        rows = sweep.plan_sweep(offers, include_measured=True, target_usd_per_ns=0.0005,
                                max_usd_per_card=1.0, max_usd_total=10.0, max_runtime_s=1800)
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["already_measured"])
        self.assertTrue(rows[0]["admit"], rows[0]["reason"])

    def test_an_unknown_card_at_the_same_price_is_still_skipped(self):
        offers = [_offer("H200 NVL", min_bid=0.55, oid=1, mid="1")]
        rows = sweep.plan_sweep(offers, include_measured=True, target_usd_per_ns=0.0005,
                                max_usd_per_card=1.0, max_usd_total=10.0, max_runtime_s=1800)
        self.assertFalse(rows[0]["admit"])
        self.assertIn("skip", rows[0]["reason"])

    def test_the_dollar_caps_still_bind_a_re_measurement(self):
        """Exempting the discovery screen must not exempt the spend ceiling."""
        offers = [_offer("RTX 4090", min_bid=5.0, oid=1, mid="1")]
        rows = sweep.plan_sweep(offers, include_measured=True, max_usd_per_card=0.20,
                                max_usd_total=10.0, max_runtime_s=1800)
        self.assertFalse(rows[0]["admit"])
        self.assertIn("per-card cap", rows[0]["reason"])
