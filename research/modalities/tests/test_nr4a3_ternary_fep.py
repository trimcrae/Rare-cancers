"""Unit tests for the ternary-cooperativity FEP harness (engine leg-planning + reducer math + io integration).

No OpenFE/OpenMM/GPU: exercises the PURE parts — leg expansion/derivation, the binary-vs-ternary cooperativity
cycle with SOLVENT CANCELLATION, replicate-SD + t-based CI, the recruitment/coupling separation, the NR-V04
affinity/recruitment margins, the $200-cap forecast, and that emitted per-leg records satisfy the
ternary_coop_io output schema. Real leg checkpoints are faked as JSON files in a temp dir."""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ternary_coop as tc          # noqa: E402
import nr4a3_ternary_fep as eng     # noqa: E402
import ternary_fep_reduce as red    # noqa: E402
import ternary_coop_io as tio       # noqa: E402


# --- leg planning -------------------------------------------------------------------------------------------
def test_expand_legs_is_four_frozen_plus_two_solvent():
    legs = eng.expand_pilot_legs()
    frozen = [leg["id"] for leg in tc.load_pilot_legs()]
    assert set(frozen) <= set(legs)                       # required-subset: frozen legs all present
    solvent = [l for l in legs if l.endswith("__solvent")]
    assert len(frozen) == 4 and len(solvent) == 2 and len(legs) == 6


def test_environment_and_morph_key():
    assert eng._environment_of("nrv04_active_to_epimer__binary_vhl") == "binary"
    assert eng._environment_of("nrv04_active_to_epimer__ternary_nr4a1") == "ternary"
    assert eng._environment_of("nrv04_active_to_epimer__solvent") == "solvent"
    for env in ("binary_vhl", "ternary_nr4a1", "solvent"):
        assert eng._morph_key("nrv04_active_to_epimer__" + env) == "nrv04_active_to_epimer"
    assert eng.solvent_leg_id("nrv04_active_to_epimer__ternary_nr4a1") == "nrv04_active_to_epimer__solvent"


def test_each_frozen_leg_has_a_solvent_sibling():
    legs = eng.expand_pilot_legs()
    for leg in tc.load_pilot_legs():
        assert eng.solvent_leg_id(leg["id"]) in legs


# --- reducer stats (pure) -----------------------------------------------------------------------------------
def test_sample_sd_and_ci():
    assert red._sample_sd([3.0]) is None                  # no replicate spread with n<2
    assert abs(red._sample_sd([2.8, 3.0, 3.2]) - 0.2) < 1e-9
    # t(.975, dof=2) = 4.303; half-width = 4.303 * 0.2 / sqrt(3)
    hw = red._ci_halfwidth(0.2, 3)
    assert abs(hw - 4.303 * 0.2 / math.sqrt(3)) < 1e-6


def _write_leg(tmp, leg_id, values, direction="fwd"):
    for i, v in enumerate(values):
        json.dump({"leg_id": leg_id, "environment": eng._environment_of(leg_id), "direction": direction,
                   "seed": i, "dg_morph_kcal": v},
                  open(os.path.join(tmp, "leg_%s_%s_r%d.json" % (leg_id, direction, i)), "w"))


def _stage_nrv04(tmp, solvent, binary, ternary):
    _write_leg(tmp, "nrv04_active_to_epimer__solvent", solvent)
    _write_leg(tmp, "nrv04_active_to_epimer__binary_vhl", binary)
    _write_leg(tmp, "nrv04_active_to_epimer__ternary_nr4a1", ternary)


def test_coop_cycle_solvent_cancels(tmp_path):
    tmp = str(tmp_path)
    red.CKPT = red.IN = tmp
    # solvent mean 5.0, binary mean 3.0, ternary mean 1.0  → ddg_bin=-2, ddg_tern=-4, ddg_coop=-2
    _stage_nrv04(tmp, [4.9, 5.0, 5.1], [2.9, 3.0, 3.1], [0.9, 1.0, 1.1])
    s = red.coop_for_morph("nrv04_active_to_epimer")
    assert s["available"]
    assert abs(s["ddg_alch_binary_kcal"] - (-2.0)) < 1e-9
    assert abs(s["ddg_alch_ternary_kcal"] - (-4.0)) < 1e-9
    assert abs(s["ddg_coop_kcal"] - (-2.0)) < 1e-9
    # solvent cancellation: ddg_coop must equal ternary_mean − binary_mean, regardless of the solvent value
    assert abs(s["ddg_coop_kcal"] - (1.0 - 3.0)) < 1e-9


def test_coop_cycle_independent_of_solvent_offset(tmp_path):
    tmp = str(tmp_path)
    red.CKPT = red.IN = tmp
    # shift the solvent leg by +100 kcal; ddg_coop (ternary−binary) must be unchanged
    _stage_nrv04(tmp, [105.0, 105.0, 105.0], [2.9, 3.0, 3.1], [0.9, 1.0, 1.1])
    s = red.coop_for_morph("nrv04_active_to_epimer")
    assert abs(s["ddg_coop_kcal"] - (-2.0)) < 1e-9        # invariant to the solvent reference
    # but the RECRUITMENT (relative ternary binding) DOES move with the solvent reference
    assert abs(s["effective_ternary_recruitment_kcal"] - (1.0 - 105.0)) < 1e-9


def test_recruitment_and_coupling_match_single_source(tmp_path):
    tmp = str(tmp_path)
    red.CKPT = red.IN = tmp
    _stage_nrv04(tmp, [5.0, 5.0, 5.0], [3.0, 3.0, 3.0], [1.0, 1.0, 1.0])
    s = red.coop_for_morph("nrv04_active_to_epimer")
    rc = tc.recruitment_and_coupling(s["ddg_alch_ternary_kcal"], s["ddg_alch_binary_kcal"])
    assert s["effective_ternary_recruitment_kcal"] == rc["effective_ternary_recruitment"]
    assert s["cooperative_coupling_kcal"] == rc["cooperative_coupling"]


def test_ci_propagates_in_quadrature(tmp_path):
    tmp = str(tmp_path)
    red.CKPT = red.IN = tmp
    _stage_nrv04(tmp, [4.9, 5.0, 5.1], [2.8, 3.0, 3.2], [0.9, 1.0, 1.1])
    s = red.coop_for_morph("nrv04_active_to_epimer")
    ci_bin = red._ci_halfwidth(red._sample_sd([2.8, 3.0, 3.2]), 3)
    ci_tern = red._ci_halfwidth(red._sample_sd([0.9, 1.0, 1.1]), 3)
    assert abs(s["ci95_coop_kcal"] - math.sqrt(ci_bin ** 2 + ci_tern ** 2)) < 1e-9


def test_hysteresis_from_reverse_leg(tmp_path):
    tmp = str(tmp_path)
    red.CKPT = red.IN = tmp
    _write_leg(tmp, "nrv04_active_to_epimer__binary_vhl", [3.0, 3.0, 3.0], direction="fwd")
    _write_leg(tmp, "nrv04_active_to_epimer__binary_vhl", [-2.6, -2.6, -2.6], direction="rev")
    agg = red.aggregate_leg("nrv04_active_to_epimer__binary_vhl")
    assert abs(agg["hysteresis_kcal"] - abs(3.0 + (-2.6))) < 1e-9   # |fwd + rev| = 0.4


def test_nrv04_margins_present_in_report(tmp_path):
    tmp = str(tmp_path)
    red.CKPT = red.IN = tmp
    _stage_nrv04(tmp, [5.0, 5.0, 5.0], [3.0, 3.0, 3.0], [1.0, 1.0, 1.0])
    rep = red.reduce_all()
    c = rep["nrv04_affinity_controls"]
    assert c is not None
    assert c["bar"]["binary_min_kcal"] == 3.0 and c["bar"]["effective_ternary_min_kcal"] == 2.0
    assert os.path.exists(os.path.join(tmp, "ternary_coop_reduction.json"))


def test_empty_when_no_checkpoints(tmp_path):
    tmp = str(tmp_path)
    red.CKPT = red.IN = tmp
    rep = red.reduce_all()
    assert rep["n_available_morphs"] == 0
    assert all(not s.get("available") for s in rep["morph_summaries"])


# --- io schema integration ----------------------------------------------------------------------------------
def test_emitted_leg_record_satisfies_output_schema(tmp_path):
    tmp = str(tmp_path)
    red.CKPT = red.IN = tmp
    _stage_nrv04(tmp, [4.9, 5.0, 5.1], [2.8, 3.0, 3.2], [0.9, 1.0, 1.1])
    rep = red.reduce_all()
    recs = rep["leg_output_records"]
    assert len(recs) == 2                                  # binary + ternary (solvent is the reference)
    for r in recs:
        assert r["schema_version"] == tio.SCHEMA_VERSION
        assert r["_schema_check"]["ok"], r["_schema_check"]["failures"]
        assert r["n_replicas"] == 3 and r["environment"] in ("binary", "ternary")


# --- cost cap -----------------------------------------------------------------------------------------------
def test_plan_forecast_reports_cap_fit():
    f = tc.plan(n_windows=16, n_replicas=3, unit_gpu_h=3.0, spot_hourly=0.50)
    assert "fits_cap" in f and "forecast_cost_usd" in f and f["hard_cap_usd"] == 200
    assert f["n_legs"] == 4                                # the frozen bundle drives the cap forecast
