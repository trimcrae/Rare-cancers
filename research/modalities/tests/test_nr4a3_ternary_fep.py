"""Unit tests for the ternary-cooperativity FEP harness (engine leg-planning + reducer math + io integration).

No OpenFE/OpenMM/GPU: exercises the PURE parts — leg expansion/derivation, the binary-vs-ternary cooperativity
cycle with SOLVENT CANCELLATION, replicate-SD + t-based CI, the recruitment/coupling separation, the NR-V04
affinity/recruitment margins, the $200-cap forecast, and that emitted per-leg records satisfy the
ternary_coop_io output schema. Real leg checkpoints are faked as JSON files in a temp dir."""
import json
import math
import os
import sys

import pytest

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


# ---------------------------------------------------------------- degenerate-atom-map guard (2026-07-26)
def test_expected_heavy_map_size_is_derived_from_the_frozen_endpoints():
    """The expectation the guard fires on is DERIVED from the two endpoint molecules, never typed.

    For the frozen valB_mini edge (Wurz cmpd1 -> cmpd4, a linker pyridine N -> benzene CH) both endpoints
    carry 59 heavy atoms and admit a COMPLETE 1:1 heavy-atom map with the single N<->C as the alchemical
    atom, so anything under 59 from LOMAP is a failed MCS search rather than a property of the chemistry."""
    import json
    from rdkit import Chem
    frozen = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                         "wurz-calib-frozen.json")))
    a = Chem.AddHs(Chem.MolFromSmiles(frozen["calib_hi"]["smiles"]))
    b = Chem.AddHs(Chem.MolFromSmiles(frozen["calib_lo"]["smiles"]))
    n, detail = eng.expected_heavy_map_size(Chem, a, b)
    assert detail["heavy_atoms_A"] == detail["heavy_atoms_B"] == 59
    assert n == 59, f"expected a complete 59-atom heavy map, derived {n}"
    assert detail["mcs_timed_out"] is False


def test_a_short_map_aborts_a_calibration_leg_before_any_sampling():
    """★ FAIL CLOSED. A timed-out LOMAP MCS returns a PARTIAL map silently; the unmapped atoms become
    dummies that are annihilated and recreated, and the leg then converges and returns a confident ΔG for a
    perturbation nobody designed. No other check in the pipeline can see it — protocol_hash covers the
    OpenFE settings, system identity covers particle counts (which dummy-isation leaves unchanged), and the
    5-part gate's item 2 reads unmapped atoms as evidence of "a real perturbation", i.e. it goes GREENER."""
    short = {"n_mapped_atoms": 80, "n_heavy_mapped": 45, "expected_heavy_mapped": 59,
             "heavy_atoms_A": 59, "heavy_atoms_B": 59, "lomap_time_s": 20,
             "degenerate": True, "mcs_timed_out": False, "mcs_timeout_s": 300}
    with pytest.raises(SystemExit) as ex:
        eng.assert_map_not_degenerate(short, "calib_hi_to_lo__ternary_vhl")
    assert "DEGENERATE ATOM MAP" in str(ex.value)
    # complete map -> no abort
    ok = dict(short, n_heavy_mapped=59, degenerate=False)
    assert eng.assert_map_not_degenerate(ok, "calib_hi_to_lo__ternary_vhl") is ok


def test_the_hard_abort_is_scoped_so_it_cannot_kill_another_lane_s_running_leg():
    """This engine is shared. Introducing a new hard abort underneath a leg already in flight — on an
    expectation not yet checked for that edge — would trade a silent wrong answer for a silent lost rental,
    so a non-calibration leg gets a LOUD WARNING and `RBFE_MAP_ASSERT` makes the choice explicit either way."""
    short = {"n_mapped_atoms": 80, "n_heavy_mapped": 45, "expected_heavy_mapped": 59,
             "heavy_atoms_A": 59, "heavy_atoms_B": 59, "lomap_time_s": 20,
             "degenerate": True, "mcs_timed_out": False, "mcs_timeout_s": 300}
    prev = os.environ.pop("RBFE_MAP_ASSERT", None)
    try:
        assert eng.assert_map_not_degenerate(short, "5aks_d0_to_d__ternary_nr4a3") is short   # warns
        os.environ["RBFE_MAP_ASSERT"] = "1"
        with pytest.raises(SystemExit):
            eng.assert_map_not_degenerate(short, "5aks_d0_to_d__ternary_nr4a3")
        os.environ["RBFE_MAP_ASSERT"] = "0"
        assert eng.assert_map_not_degenerate(short, "calib_hi_to_lo__ternary_vhl") is short
    finally:
        os.environ.pop("RBFE_MAP_ASSERT", None)
        if prev is not None:
            os.environ["RBFE_MAP_ASSERT"] = prev


# ---------------------------------------------------------------- valB_mini replicates: r1/r2 pre-flight
def test_each_replicate_seed_gets_its_own_system_fingerprint():
    """★ A RE-USED SEED MUST NOT BE ABLE TO MASQUERADE AS AN INDEPENDENT REPLICATE. The whole deliverable of
    r1+r2 is a BETWEEN-REPLICATE cycle SD, so two legs that were secretly the same trajectory would report a
    spuriously tight error bar — the one failure that makes the benchmark look better than it is.

    SEED is one of the fields `rbfe_spot_checkpoint.system_fingerprint` hashes, and a committed generation
    whose fingerprint differs from the running configuration is REFUSED on restore. So the guarantee is not
    "we remembered to pass different seeds", it is structural: a resume cannot cross replicates."""
    import rbfe_spot_checkpoint as ck
    assert "SEED" in ck.SYSTEM_FINGERPRINT_ENV
    base = {"LEG_ID": "calib_hi_to_lo__ternary_vhl", "DIRECTION": "fwd", "CHARGE_METHOD": "nagl",
            "SETUP_CACHE_VERSION": "v1pe", "N_WINDOWS": "12", "RBFE_TIMESTEP_FS": "4.0",
            "RBFE_WARMUP_TIMESTEP_FS": "1.0", "RBFE_CONSTRAIN_LIGAND_CH": "0"}
    fps = {s: ck.system_fingerprint({**base, "SEED": str(s)})[0] for s in (0, 1, 2)}
    assert len(set(fps.values())) == 3, f"seeds must not share a system fingerprint: {fps}"


def test_the_verdict_is_computed_from_replicate_sd_not_hand_applied(tmp_path):
    """Exercise the REAL reduce path end to end on synthetic leg files, so that when r1/r2 land the verdict
    is produced by the frozen gate rather than by someone doing the arithmetic in a report.

    Two properties are asserted because both have been got wrong in this repo before:
      * ΔΔG_coop is paired BY SEED (ternary_r − binary_r), and the solvent morph cancels inside each
        replicate cycle — so a missing per-replicate solvent leg is not a gap; and
      * the spread that reaches the gate is the BETWEEN-REPLICATE sample SD, never the MBAR SE.
    """
    import importlib
    for s, (tern, bina) in {0: (47.6131, 48.1256), 1: (47.70, 48.10), 2: (47.55, 48.20)}.items():
        for leg, dg in (("calib_hi_to_lo__ternary_vhl", tern), ("calib_hi_to_lo__binary_vhl", bina)):
            (tmp_path / f"leg_{leg}_fwd_r{s}.json").write_text(json.dumps({
                "leg_id": leg, "environment": eng._environment_of(leg), "direction": "fwd", "seed": s,
                "dg_morph_kcal": dg, "mbar_se_kcal": 0.13, "morph": "calib_hi_to_lo"}))
    os.environ["CKPT_DIR"] = os.environ["INPUT_DIR"] = str(tmp_path)
    r = importlib.reload(red)
    try:
        reps, n_paired = r.per_replicate_ddg_coop("calib_hi_to_lo")
        assert n_paired == 3
        # paired by seed, and the MBAR SE (0.13) plays no part in the spread
        assert reps == pytest.approx([47.6131 - 48.1256, 47.70 - 48.10, 47.55 - 48.20], abs=1e-6)
        sd_replicate = r._sample_sd(reps)
        gate = r.calibration_gate(reps, 0.944)
        # every value is negative against a +0.944 target -> a converged WRONG SIGN is a FAIL, verbatim
        assert gate["decision"] == "FAIL"
        assert gate["correct_sign"] is False
        assert gate["cycle_sd_kcal"] == pytest.approx(sd_replicate, abs=1e-9)
        # THE INVARIANT, stated as an invariant rather than as a lucky inequality: rewrite every leg's MBAR
        # SE and the cycle SD must not move by so much as a float. That is what "replicate SD, not MBAR SE"
        # actually means, and it is checkable in a way that "the SD is bigger than the SE" is not — on these
        # values the SD happens to be SMALLER than the SE, which is exactly why the loose form is worthless.
        for f in tmp_path.glob("leg_*.json"):
            d = json.loads(f.read_text()); d["mbar_se_kcal"] = 99.0; f.write_text(json.dumps(d))
        r2 = importlib.reload(red)
        assert r2.calibration_gate(r2.per_replicate_ddg_coop("calib_hi_to_lo")[0], 0.944)["cycle_sd_kcal"] \
            == pytest.approx(sd_replicate, abs=1e-12)
        # and n=1 must still refuse to decide, in the gate's own words
        one = r.calibration_gate(reps[:1], 0.944)
        assert one["decision"] == "INDETERMINATE"
        assert one["reason"] == "need >=2 independent replicates for a cycle SD."
    finally:
        for k in ("CKPT_DIR", "INPUT_DIR"):
            os.environ.pop(k, None)
        importlib.reload(red)
