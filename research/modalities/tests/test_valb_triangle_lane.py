"""The valB closure triangle as a RUNNABLE lane — the invariants that decide whether R means anything.

`test_valb_triangle_closure.py` already covers the arithmetic (does the cycle close, what is R blind to, what
does it cost). This file covers the things that can silently convert R from a PATH-error detector into a
PROTOCOL-DIFFERENCE detector, each of which is a green run that measures the wrong quantity:

  * the timestep pin — 2 fs, matching r0, beating a lane-wide 4 fs env export;
  * the seed pin — 0 on every leg, matching r0;
  * no solvent legs (they cancel exactly inside ddG_coop);
  * the launcher, the watchdog and the fetchers agreeing on the unit ids;
  * the spend ceiling coming from the TRIANGLE's own price, not from another rung's ladder band;
  * the reducer refusing every cycle it cannot honestly compute, and quoting no MBAR SE as an error bar.

Pure stdlib: no RDKit, no network, no GPU. The chemistry half (`valb_triangle_legs.derive`) needs RDKit and is
exercised in CI inside the parity image by `task=triangle-freeze`, which fails closed on a route disagreement.
"""
import json
import math
import os
import random
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nr4a3_ternary_fep as eng          # noqa: E402
import ternary_vast_launch as tv         # noqa: E402
import ternary_vast_watchdog as twd      # noqa: E402
import valb_triangle_closure as vtc      # noqa: E402
import valb_triangle_legs as tlegs       # noqa: E402
import valb_triangle_reduce as tred      # noqa: E402


# ---------------------------------------------------------------------------------------------------------
# 1. the legs are the four the design buys, and they parse the way the engine expects
# ---------------------------------------------------------------------------------------------------------
def test_four_new_legs_and_r0_is_not_one_of_them():
    """The triangle's whole economy is that r0 IS T1. If T1's legs appeared in the new-leg registry they
    would be re-bought — 6 legs and ~$10.25 instead of 4 and $6.83 — and the reuse that justified the design
    would be gone."""
    assert len(tlegs.NEW_LEG_IDS) == 4
    assert all(l.startswith("calib_") for l in tlegs.NEW_LEG_IDS)
    assert "calib_hi_to_lo__ternary_vhl" not in tlegs.NEW_LEG_IDS
    assert "calib_hi_to_lo__binary_vhl" not in tlegs.NEW_LEG_IDS
    assert tlegs.TRIANGLE_LEGS["T1"]["ternary"] == "calib_hi_to_lo__ternary_vhl"


def test_leg_ids_classify_to_the_right_environment():
    """A single-underscore id would classify a ternary leg as BINARY, drop the target chain, and converge
    perfectly well on the wrong system. This is the trap `nr4a3_5aks_cofold` documents; check it holds here."""
    for lid, spec in tlegs.LEG_MAP.items():
        assert eng._environment_of(lid) == spec["environment"], lid


def test_engine_resolves_every_new_leg():
    for lid, spec in tlegs.LEG_MAP.items():
        leg, env = eng.leg_spec(lid)
        assert leg["morph"] == spec["morph"]
        assert env == spec["environment"]


def test_morph_keys_are_distinct_from_the_already_run_edge():
    """T1's morph key must not collide with T2's or T3's, or the solvent-leg derivation and the stage cache
    would alias two different edges onto one set of inputs."""
    keys = {eng._morph_key(l) for l in tlegs.NEW_LEG_IDS}
    assert keys == {"calib_lo_to_lo2", "calib_hi_to_lo2"}
    assert eng._morph_key("calib_hi_to_lo__ternary_vhl") not in keys


def test_the_three_edges_use_the_coefficients_the_closure_identity_uses():
    """A sign error here is undetectable downstream — R would be a well-formed number for the wrong cycle."""
    by_name = {n: s for n, _a, _b, s in vtc.TRIANGLE}
    for edge, spec in tlegs.TRIANGLE_LEGS.items():
        assert spec["coefficient"] == by_name[edge], edge


# ---------------------------------------------------------------------------------------------------------
# 2. the mode pins — each of these is a way R silently stops being a closure residual
# ---------------------------------------------------------------------------------------------------------
def test_triangle_mode_runs_exactly_the_four_new_legs_at_seed_zero():
    units = tv.units_for("triangle")
    assert sorted(l for l, _s, _d in units) == sorted(tlegs.NEW_LEG_IDS)
    assert {s for _l, s, _d in units} == {0}, "a mixed-seed triangle is not a closure"
    assert {d for _l, _s, d in units} == {"fwd"}


def test_triangle_buys_no_solvent_leg():
    """The solvent morph enters ddG_alch,ternary and ddG_alch,binary with the SAME sign and cancels exactly
    inside ddG_coop, so a triangle whose deliverable is R needs 2 legs per edge, not 3."""
    assert not [l for l, _s, _d in tv.units_for("triangle") if l.endswith("__solvent")]


def test_the_timestep_pin_beats_a_lane_wide_env_export():
    """THE ONE THAT COSTS A WHOLE FLEET IF IT REGRESSES. The workflow exports TVAST_TIMESTEP_FS lane-wide and
    this lane's default is RUNG 2b's 4 fs, while r0 — the triangle's T1 edge — is 2 fs. A 4 fs T2/T3 around a
    2 fs T1 makes R measure the TIMESTEP difference rather than the path error."""
    old = os.environ.get("TVAST_TIMESTEP_FS")
    os.environ["TVAST_TIMESTEP_FS"] = "4.0"
    try:
        assert tv.resolve_timesteps("triangle") == ("2.0", "1.0")
        assert tv.resolve_timesteps("triangle_smoke") == ("2.0", "1.0")
        # ...and a mode with no pin still honours the env, so the pin is a pin and not a global override.
        assert tv.resolve_timesteps("edge")[0] == "4.0"
        spec = tv.build_jobspec("calib_hi_to_lo2__ternary_vhl", 0, "fwd", mode="triangle")
        assert spec.env["RBFE_TIMESTEP_FS"] == "2.0"
        assert spec.env["RBFE_WARMUP_TIMESTEP_FS"] == "1.0"
        assert "dt2.0fs" in spec.env["UNIT_ID"]
    finally:
        if old is None:
            os.environ.pop("TVAST_TIMESTEP_FS", None)
        else:
            os.environ["TVAST_TIMESTEP_FS"] = old


def test_an_explicit_timestep_still_wins_over_the_pin():
    """A deliberate re-run at another dt must stay possible — and must land in a DIFFERENT unit id, so it can
    never resume into the pinned run's checkpoints."""
    a = tv.build_jobspec("calib_hi_to_lo2__ternary_vhl", 0, "fwd", mode="triangle")
    b = tv.build_jobspec("calib_hi_to_lo2__ternary_vhl", 0, "fwd", mode="triangle", timestep_fs="4.0")
    assert b.env["RBFE_TIMESTEP_FS"] == "4.0"
    assert a.env["UNIT_ID"] != b.env["UNIT_ID"]
    assert a.env["COMMIT_S3"] != b.env["COMMIT_S3"]


def test_watchdog_arms_the_unit_ids_that_were_actually_rented():
    """An env-only derivation in the watchdog would arm 4 fs unit ids for 2 fs legs: `--verify-armed` would
    fail a correct launch, and the cron watchdog would watch four units that do not exist while four billed
    ones ran unwatched."""
    old = os.environ.get("TVAST_TIMESTEP_FS")
    os.environ["TVAST_TIMESTEP_FS"] = "4.0"
    try:
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "watch.json")
            twd.arm("triangle", path=path)
            armed = twd.verify_armed("triangle", path=path)
        rented = {tv.build_jobspec(l, s, dd, mode="triangle").env["UNIT_ID"]
                  for (l, s, dd) in tv.units_for("triangle")}
        assert set(armed) == rented
        assert all("dt2.0fs" in u for u in armed)
    finally:
        if old is None:
            os.environ.pop("TVAST_TIMESTEP_FS", None)
        else:
            os.environ["TVAST_TIMESTEP_FS"] = old


def test_the_strict_provenance_flag_is_on():
    """These commit prefixes do not exist yet, so every generation they will ever restore was written by the
    configuration that stamps it — the concession has nothing to buy here, and turning it off closes the
    'resume accepted a generation from another configuration' hole for free."""
    spec = tv.build_jobspec("calib_lo_to_lo2__binary_vhl", 0, "fwd", mode="triangle")
    assert spec.env["RBFE_STRICT_PROVENANCE"] == "1"
    assert spec.env["RBFE_MAP_ASSERT"] == "1", "calib_ legs must fail closed on a short atom map"


def test_labels_round_trip_and_do_not_alias_between_triangle_units():
    """A lossy 60-character label makes `collect` reap the wrong host — or fail to reap the right one, which
    bills a GPU until the runtime backstop hours later."""
    uids = [tv.build_jobspec(l, s, d, mode="triangle").env["UNIT_ID"] for (l, s, d) in tv.units_for("triangle")]
    labels = [tv.unit_label(u) for u in uids]
    assert len(set(labels)) == len(labels)
    for u, lab in zip(uids, labels):
        assert len(lab) <= 60
        assert tv.label_matches_unit(lab, u)
        for other in uids:
            if other != u:
                assert not tv.label_matches_unit(lab, other)


# ---------------------------------------------------------------------------------------------------------
# 3. the spend gate is judged against the TRIANGLE's authorisation, not another rung's
# ---------------------------------------------------------------------------------------------------------
def test_the_band_is_derived_from_price_triangle_and_nothing_else():
    plan4, ceil4 = tv.triangle_band_usd(4)
    v = vtc.price_triangle()["variants"]
    scout = next(v[k] for k in v if k.startswith("n1_scout_R_only"))
    assert abs(plan4 - scout["plan_usd"]) < 0.02
    assert abs(ceil4 - scout["range_usd"][1]) < 0.02
    # per leg, so a partial fan-out is priced correctly rather than all-or-nothing
    plan1, ceil1 = tv.triangle_band_usd(1)
    assert abs(plan1 * 4 - plan4) < 0.05 and abs(ceil1 * 4 - ceil4) < 0.05


def test_the_triangle_band_is_not_the_4fs_recalibration_band():
    """Judging one experiment's spend by another's approval is how a guard refuses a small authorised
    purchase for a reason that does not apply to it — or, worse, permits one it should not."""
    assert tv.triangle_band_usd(4) != tv.rung_band_usd(4)


def test_the_gate_readout_names_the_purchase_it_priced():
    """A hold snapshot is read hours later by someone who was not here. One naming the wrong experiment is
    worse than one with no label at all."""
    assert "TRIANGLE" in tv._gate_what("triangle")
    assert "replicates" in tv._gate_what("edge_reps")
    assert tv._gate_what("triangle") != tv._gate_what("edge_reps")


def test_every_rental_still_faces_the_absolute_buy_line():
    """CLAUDE.md §1: the line is an ABSOLUTE $/ns, and §6: a relaunch is a new purchase, so the cap travels
    with the JobSpec into selection rather than being a step someone must remember."""
    import inflight_usd_per_ns as iu
    spec = tv.build_jobspec("calib_hi_to_lo2__ternary_vhl", 0, "fwd", mode="triangle")
    assert spec.resources.max_usd_per_ns is not None
    assert abs(spec.resources.max_usd_per_ns - iu.APPROVED_USD_PER_NS) < 1e-9


# ---------------------------------------------------------------------------------------------------------
# 4. the reducer — what it computes, and everything it refuses
# ---------------------------------------------------------------------------------------------------------
def _leg_file(d, leg_id, dg, seed=0, **kw):
    rec = {"leg_id": leg_id, "environment": eng._environment_of(leg_id), "direction": "fwd", "seed": seed,
           "dg_morph_kcal": dg, "mbar_se_kcal": 0.045, "protocol_hash": "h0", "n_particles": 146284,
           "charge_method": "nagl", "setup_cache_version": "v1pe", "n_windows": 12}
    rec.update(kw)
    with open(os.path.join(d, "leg_%s_fwd_r%d.json" % (leg_id, rec["seed"])), "w") as fh:
        json.dump(rec, fh)


def _six(d, tern, binr, **kw):
    for edge, legs in tlegs.TRIANGLE_LEGS.items():
        _leg_file(d, legs["ternary"], tern[edge], **kw)
        _leg_file(d, legs["binary"], binr[edge], **kw)


def test_R_is_exactly_zero_for_a_perfect_cycle():
    """The state values are arbitrary: a zero here is the telescoping identity holding, not a coincidence of
    one dataset."""
    rng = random.Random(5)
    for _ in range(12):
        st = {s: rng.uniform(-50, 50) for s in ("c1", "c4", "c4p")}
        sb = {s: rng.uniform(-50, 50) for s in ("c1", "c4", "c4p")}
        tern = {"T1": st["c4"] - st["c1"], "T2": st["c4p"] - st["c4"], "T3": st["c4p"] - st["c1"]}
        binr = {"T1": sb["c4"] - sb["c1"], "T2": sb["c4p"] - sb["c4"], "T3": sb["c4p"] - sb["c1"]}
        with tempfile.TemporaryDirectory() as d:
            _six(d, tern, binr)
            r = tred.reduce_triangle(d)
        assert abs(r["R_kcal"]) < 1e-6
        assert abs(r["R_ternary_kcal"]) < 1e-6 and abs(r["R_binary_kcal"]) < 1e-6
        assert r["decision"] == "R_CONSISTENT_WITH_ZERO"


def test_R_is_blind_to_a_per_endpoint_state_function_error():
    """The load-bearing property, checked on the REDUCER rather than only on the arithmetic module: force
    field, homology model, NAGL charges and protonation are all per-endpoint biases, and R must not see any
    of them. If this ever fails, the experiment's entire claim is void."""
    rng = random.Random(9)
    st = {s: rng.uniform(-50, 50) for s in ("c1", "c4", "c4p")}
    eps = {s: rng.uniform(-9, 9) for s in ("c1", "c4", "c4p")}         # a large state-function error
    tern = {"T1": (st["c4"] + eps["c4"]) - (st["c1"] + eps["c1"]),
            "T2": (st["c4p"] + eps["c4p"]) - (st["c4"] + eps["c4"]),
            "T3": (st["c4p"] + eps["c4p"]) - (st["c1"] + eps["c1"])}
    with tempfile.TemporaryDirectory() as d:
        _six(d, tern, {k: 0.0 for k in tern})
        r = tred.reduce_triangle(d)
    assert abs(r["R_ternary_kcal"]) < 1e-6


def test_R_sees_a_path_error_and_reports_it_as_resolved():
    tern = {"T1": 1.0, "T2": 1.0, "T3": 2.0 + 6.0}      # a 6 kcal/mol path error on the closing edge
    with tempfile.TemporaryDirectory() as d:
        _six(d, tern, {k: 0.0 for k in tern})
        r = tred.reduce_triangle(d)
    assert abs(abs(r["R_kcal"]) - 6.0) < 1e-6
    assert r["decision"] == "R_RESOLVED_PATH_ERROR"


def test_an_intermediate_R_is_reported_as_underpowered_not_as_evidence():
    """The n=1 scout can ADMIT a cycle but cannot CONVICT it: one draw cannot separate a systematic from an
    unlucky sample when sigma_leg is unknown by a factor of ~15."""
    tern = {"T1": 1.0, "T2": 1.0, "T3": 2.0 + 1.478}
    with tempfile.TemporaryDirectory() as d:
        _six(d, tern, {k: 0.0 for k in tern})
        r = tred.reduce_triangle(d)
    assert r["decision"] == "AMBIGUOUS_AT_n1"
    assert "UNDERPOWERED" in r["reading"] or "cannot" in r["reading"]


def test_no_mbar_se_is_ever_quoted_as_the_error_bar():
    """This programme's error bar is the BETWEEN-REPLICATE SD. The MBAR SE is a lower bound that does not see
    slow modes, and at n=1 the honest answer is that no replicate SD exists."""
    with tempfile.TemporaryDirectory() as d:
        _six(d, {"T1": 1.0, "T2": 1.0, "T3": 2.0}, {"T1": 0.0, "T2": 0.0, "T3": 0.0})
        r = tred.reduce_triangle(d)
    assert r["replicate_sd_kcal"] is None
    assert r["error_bar_kind"] == "NONE QUOTED AT n=1"
    assert "PROVENANCE_ONLY" in " ".join(r.keys())


def test_reducer_refuses_a_mixed_seed_cycle():
    with tempfile.TemporaryDirectory() as d:
        _leg_file(d, tlegs.TRIANGLE_LEGS["T1"]["ternary"], 1.0, seed=0)
        _leg_file(d, tlegs.TRIANGLE_LEGS["T1"]["binary"], 0.0, seed=0)
        _leg_file(d, tlegs.TRIANGLE_LEGS["T2"]["ternary"], 1.0, seed=0)
        _leg_file(d, tlegs.TRIANGLE_LEGS["T2"]["binary"], 0.0, seed=0)
        _leg_file(d, tlegs.TRIANGLE_LEGS["T3"]["ternary"], 2.0, seed=1)     # <- different Hamiltonian
        _leg_file(d, tlegs.TRIANGLE_LEGS["T3"]["binary"], 0.0, seed=1)
        r = tred.reduce_triangle(d)
    assert r["decision"] == "REFUSED"
    assert "seed" in r["reason"]


def test_reducer_refuses_a_solvent_leg():
    with tempfile.TemporaryDirectory() as d:
        _six(d, {"T1": 1.0, "T2": 1.0, "T3": 2.0}, {"T1": 0.0, "T2": 0.0, "T3": 0.0})
        _leg_file(d, "calib_hi_to_lo2__solvent", 47.8)
        r = tred.reduce_triangle(d)
    assert r["decision"] == "REFUSED"
    assert "solvent" in r["reason"]


def test_reducer_reports_incomplete_rather_than_a_partial_cycle():
    """Five legs cannot close a triangle. An R from a partial cycle is not a smaller-n R, it is a different
    number — and it would look exactly like a real one."""
    with tempfile.TemporaryDirectory() as d:
        _six(d, {"T1": 1.0, "T2": 1.0, "T3": 2.0}, {"T1": 0.0, "T2": 0.0, "T3": 0.0})
        os.remove(os.path.join(d, "leg_%s_fwd_r0.json" % tlegs.TRIANGLE_LEGS["T3"]["binary"]))
        r = tred.reduce_triangle(d)
    assert r["decision"] == "INCOMPLETE"


def test_reducer_flags_a_protocol_hash_disagreement():
    """R is only a closure residual if every edge ran the same protocol — the reason T2/T3's binary legs run
    UNRESTRAINED and the mode is pinned to 2 fs."""
    with tempfile.TemporaryDirectory() as d:
        _six(d, {"T1": 1.0, "T2": 1.0, "T3": 2.0}, {"T1": 0.0, "T2": 0.0, "T3": 0.0})
        _leg_file(d, tlegs.TRIANGLE_LEGS["T2"]["binary"], 0.0, protocol_hash="OTHER")
        r = tred.reduce_triangle(d)
    assert "protocol_hash_disagreement" in r


def test_R_equals_R_ternary_minus_R_binary_and_both_are_reported():
    """Reporting R alone is strictly weaker: a clean R can be two large closures cancelling, and both come
    free from the same six legs."""
    tern = {"T1": 1.0, "T2": 1.0, "T3": 2.0 + 3.0}
    binr = {"T1": 0.5, "T2": 0.5, "T3": 1.0 + 3.0}       # the SAME 3.0 in both -> R cancels to zero
    with tempfile.TemporaryDirectory() as d:
        _six(d, tern, binr)
        r = tred.reduce_triangle(d)
    assert abs(r["R_kcal"] - (r["R_ternary_kcal"] - r["R_binary_kcal"])) < 1e-9
    assert abs(r["R_kcal"]) < 1e-6
    assert abs(r["R_ternary_kcal"]) > 1.0 and abs(r["R_binary_kcal"]) > 1.0
    assert r["cancellation_risk"] is True, "two large closures cancelling must be flagged, not celebrated"


def test_noise_floor_is_carried_at_both_sigma_bounds():
    with tempfile.TemporaryDirectory() as d:
        _six(d, {"T1": 1.0, "T2": 1.0, "T3": 2.0}, {"T1": 0.0, "T2": 0.0, "T3": 0.0})
        r = tred.reduce_triangle(d)
    assert r["sigma_leg_bounds"]["lower_MBAR_SE"] == 0.045
    assert r["sigma_leg_bounds"]["upper_repo_assumed_replicate_SD"] == 0.7
    assert "prereg_verdict_at_upper_sigma" in r
    # SD(R) = sqrt(6) * sigma_leg, and the reducer must not quietly use a tighter formula
    rows = {row["sigma_leg"]: row for row in r["noise_floor"]["rows"]}
    assert abs(rows[0.045]["SD_R_analytic"] - math.sqrt(6) * 0.045) < 5e-5   # the row is rounded to 4 dp


def test_the_honest_limit_travels_with_the_number():
    with tempfile.TemporaryDirectory() as d:
        _six(d, {"T1": 1.0, "T2": 1.0, "T3": 2.0}, {"T1": 0.0, "T2": 0.0, "T3": 0.0})
        r = tred.reduce_triangle(d)
    for phrase in ("INTERNAL CONSISTENCY", "force-field", "homology", "APPARENT cooperativity"):
        assert phrase in r["honest_limit"]


def test_reducer_refuses_a_restrained_leg_record():
    """A separate lane is running a RESTRAINED binary re-run of this same calibrator, into the SAME bucket
    r0's records live in. One restrained leg inside this triangle makes R measure the PROTOCOL DIFFERENCE
    between two lanes rather than the path error — and it would look completely normal."""
    with tempfile.TemporaryDirectory() as d:
        _six(d, {"T1": 1.0, "T2": 1.0, "T3": 2.0}, {"T1": 0.0, "T2": 0.0, "T3": 0.0})
        # the filename marker the GCP lane writes
        src = os.path.join(d, "leg_%s_fwd_r0.json" % tlegs.TRIANGLE_LEGS["T1"]["binary"])
        with open(src) as fh:
            rec = json.load(fh)
        with open(os.path.join(d, "leg_%s_fwd_r0_rst.json" % tlegs.TRIANGLE_LEGS["T1"]["binary"]), "w") as fh:
            json.dump(rec, fh)
        r = tred.reduce_triangle(d)
    assert r["decision"] == "REFUSED"
    assert "restrained" in r["reason"]


def test_reducer_refuses_a_leg_whose_record_declares_a_restraint():
    """Belt and braces: the filename marker can be lost by a copy, the recorded field cannot."""
    with tempfile.TemporaryDirectory() as d:
        _six(d, {"T1": 1.0, "T2": 1.0, "T3": 2.0}, {"T1": 0.0, "T2": 0.0, "T3": 0.0})
        _leg_file(d, tlegs.TRIANGLE_LEGS["T2"]["binary"], 0.0, restrain=1)
        r = tred.reduce_triangle(d)
    assert r["decision"] in ("REFUSED", "INCOMPLETE")
    assert "restrained" in r["reason"] or "missing" in r["reason"]


# ---------------------------------------------------------------------------------------------------------
# 5. the crystal ligand is a property of the STRUCTURE, not of the morph
# ---------------------------------------------------------------------------------------------------------
def test_every_calib_leg_names_cmpd1_as_the_crystal_ligand():
    """⛔ THE ONE THAT WOULD HAVE KILLED BOTH T2 LEGS. Both endpoints are built from the same crystal pose,
    and `_repair_pose` needs the crystal ligand's TRUE identity to assign bond orders before anything is
    mutated. The engine inferred it from the morph's endpoint A — correct for every leg whose morph starts at
    the co-crystallised compound, which every calib leg did until T2 (`calib_lo -> calib_lo2`) started at
    cmpd4, a DERIVED molecule that exists in no crystal. Assigning cmpd1's coordinates against a cmpd4
    template is the RECORDED failure on this lane: the thiazole loses its aromatic C-H and NAGL rejects the
    molecule with RadicalsNotSupportedError."""
    import ternary_coop_prep as prep
    import ternary_coop as tcoop
    hi = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                     "wurz-calib-frozen.json")))["calib_hi"]["smiles"]
    for lid in list(tlegs.NEW_LEG_IDS) + ["calib_hi_to_lo__ternary_vhl", "calib_hi_to_lo__binary_vhl"]:
        leg, _env = eng.leg_spec(lid)
        assert prep.crystal_ligand_smiles(leg) == hi, lid
    # T2 is the case that regressed: its endpoint A is cmpd4, and it must NOT be taken as the crystal ligand
    t2, _ = eng.leg_spec(tlegs.TRIANGLE_LEGS["T2"]["ternary"])
    m = prep._morph_endpoints(t2, resolve_smiles=True)
    assert m["smiles_a"] != hi, "T2's endpoint A is cmpd4 — this test is meaningless if that ever changes"


def test_other_families_keep_the_endpoint_a_fallback():
    """The fix must not reach legs where endpoint A genuinely IS the staged ligand — 5a-KS stages from a
    co-fold built around its own endpoint A."""
    import ternary_coop_prep as prep
    for lid, spec in eng._extra_leg_map().items():
        if lid in tlegs.LEG_MAP:
            continue
        assert prep.crystal_ligand_smiles(dict(spec, id=lid)) is None, lid


def test_the_rate_line_binds_before_the_dollar_ceiling_and_the_refusal_says_which():
    """CLAUDE.md §6: a rental must clear BOTH its rung's derived DOLLAR ceiling and the ABSOLUTE $/ns line,
    the effective ceiling is the lower, and a refusal must NAME the one it hit — conflating them is what made
    an earlier round of hold readouts unreadable.

    On this rung the RATE line binds first, and by a wide margin: a board at 2.6x basis still projects $14.79
    against a $15.40 authorisation, so a dollar-only gate would have bought the whole fan-out at nearly
    double the $/ns trimcrae said he would rather pause than pay."""
    import unittest.mock as mock
    from congeneric_fanout import basis_usd_per_ns
    basis = basis_usd_per_ns()

    def _board(mult):
        return [(mult * basis, 0.20, {"gpu_name": "RTX 4090", "machine_id": 999})] * 8

    def _gate(mult):
        with mock.patch.object(tv, "_vast_request", return_value={"offers": [{}] * 8}), \
             mock.patch("gpu_backend.rank_offers_by_usd_per_ns", return_value=(_board(mult), [{}] * 8)):
            return tv.market_gate(4, key="x", mode="triangle")

    hold, out = _gate(0.9)
    assert not hold and out["projected_usd"] < out["ceiling_usd"]

    hold, out = _gate(2.6)
    assert hold, "a board at 2.6x basis must not be bought"
    assert out["fails_ratio_ceiling"] is True
    assert out["fails_dollar_ceiling"] is False, (
        "if this ever flips, the dollar ceiling started binding first and the test below is measuring "
        "something else")
    assert "drift line" in out["reason"], "the refusal must NAME which ceiling it hit"
    # ...and the dollars alone would have permitted it, which is the whole point of having two tests
    assert out["projected_usd"] < out["ceiling_usd"]
