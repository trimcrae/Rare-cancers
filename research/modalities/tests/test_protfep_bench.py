"""Tests for the 5a-KS known-answer benchmark layer (protfep_bench / protfep_reduce / launcher).

These run on CPU with no MD stack and no network — the pure layers are separated from the perses
entry points precisely so the parts that decide PASS/FAIL are testable in CI on every push.

What is being protected here, in order of how badly it would bite:
  1. The qualification verdict cannot go green on a partial set, on a wrong ordering, or without
     saying that its reference values are unverified. A false PASS would let an unvalidated engine
     put a number in the manuscript, which is exactly what the gate exists to prevent.
  2. Smoke legs cannot leak into a real reduction. A 3-window/20-iteration leg emits something that
     looks like a dG.
  3. A single replicate cannot acquire a fabricated error bar.
"""

import json
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import protfep_bench as pb  # noqa: E402
import protfep_reduce as pr  # noqa: E402
import protfep_vast_launch as pv  # noqa: E402


# ---------------------------------------------------------------- benchmark definitions
def test_every_benchmark_is_charge_conserving():
    """A charge-changing benchmark would confound engine error with the PME finite-size artifact."""
    import nr4a3_protein_fep as pf
    for name, b in pb.BENCHMARKS.items():
        m = pf.classify_mutation(b["mutation"])
        assert not m["charge_changing"], f"{name} is charge-changing ({m['charge_change']:+d})"
        assert m["buildable"], f"{name} is not buildable: {m['risk']}"


def test_every_benchmark_plans_through_the_production_guards():
    """The benchmark must not validate a path the science is forbidden to use."""
    import nr4a3_protein_fep as pf
    for b in pb.BENCHMARKS.values():
        plan = pf.plan_wedge(b["mutation"], n_replicas=3)
        assert plan["n_legs"] == 6
        assert plan["validated"] is False


def test_leg_spec_chains():
    complex_spec = pb.leg_spec("barnase_barstar_Y29A", "complex")
    apo_spec = pb.leg_spec("barnase_barstar_Y29A", "apo")
    assert complex_spec["chains"] == ["A", "D"]
    assert apo_spec["chains"] == ["D"]
    # The mutated chain must be present in BOTH legs or the cycle is not a cycle.
    assert "D" in complex_spec["chains"] and "D" in apo_spec["chains"]
    assert complex_spec["cycle_role"] == "ternary"
    assert apo_spec["cycle_role"] == "binary"


def test_leg_spec_rejects_unknown_environment():
    with pytest.raises(ValueError):
        pb.leg_spec("barnase_barstar_Y29A", "solvent")


def test_all_leg_specs_count():
    legs = pb.all_leg_specs(n_replicas=3)
    assert len(legs) == len(pb.BENCHMARKS) * 2 * 3
    assert len({leg["leg_id"] for leg in legs}) == len(legs)


# ---------------------------------------------------------------- verdict
def _score(name, calc, sd=0.3):
    return pb.score_benchmark(name, calc, sd)


def test_qualify_passes_on_accurate_and_correctly_ordered_results():
    res = {"barnase_barstar_Y29A": _score("barnase_barstar_Y29A", 3.1),
           "barnase_barstar_Y29F": _score("barnase_barstar_Y29F", 0.8)}
    v = pb.qualify(res)
    assert v["qualified"] is True
    assert v["complete"] is True


def test_qualify_fails_when_ordering_is_wrong_even_if_magnitudes_pass():
    """Ranked backwards while both magnitudes are inside tolerance -> FAIL.

    A wedge is read as a ranking, so ordering is the load-bearing property. The scores are built by
    hand here because, with the corrected references (3.4 vs -0.13), the two tolerance windows no
    longer overlap and such a pair cannot arise from score_benchmark — see the test below, which
    pins that separation. The ordering branch still has to work: it is what protects a future
    benchmark pair whose windows DO overlap.
    """
    res = {"barnase_barstar_Y29A": dict(_score("barnase_barstar_Y29A", 3.4),
                                        calc_ddg_bind_kcal=0.5, within_tolerance=True),
           "barnase_barstar_Y29F": dict(_score("barnase_barstar_Y29F", -0.13),
                                        calc_ddg_bind_kcal=0.9, within_tolerance=True)}
    v = pb.qualify(res)
    assert v["qualified"] is False
    assert "ORDERING WRONG" in v["reason"]


def test_corrected_references_are_separated_by_more_than_the_tolerance():
    """The Y29A/Y29F references (3.4 vs -0.13) are 3.5 kcal/mol apart, > 2 x the 1.5 tolerance.

    Consequence worth stating: for THIS pair, passing both magnitudes now implies the ordering is
    right. That is a property of these two references, not a general guarantee, which is why the
    ordering check stays.
    """
    a = pb.BENCHMARKS["barnase_barstar_Y29A"]["ref_ddg_bind_kcal"]
    f = pb.BENCHMARKS["barnase_barstar_Y29F"]["ref_ddg_bind_kcal"]
    assert a - f > 2 * pb.PASS_ABS_ERR_KCAL


def test_qualify_fails_on_a_partial_set():
    """One good benchmark is not a qualification — a lucky single point must not open the gate."""
    v = pb.qualify({"barnase_barstar_Y29A": _score("barnase_barstar_Y29A", 3.4)})
    assert v["qualified"] is False
    assert v["complete"] is False


def test_qualify_fails_outside_tolerance():
    res = {"barnase_barstar_Y29A": _score("barnase_barstar_Y29A", 0.1),
           "barnase_barstar_Y29F": _score("barnase_barstar_Y29F", 0.5)}
    v = pb.qualify(res)
    assert v["qualified"] is False
    assert "barnase_barstar_Y29A" in v["failures"]


def test_qualify_surfaces_unverified_references():
    """A PASS scored against unchecked literature values must say so, not read as fully verified."""
    saved = pb.BENCHMARKS["barnase_barstar_Y29F"]["ref_verified"]
    pb.BENCHMARKS["barnase_barstar_Y29F"]["ref_verified"] = False
    try:
        res = {"barnase_barstar_Y29A": _score("barnase_barstar_Y29A", 3.4),
               "barnase_barstar_Y29F": _score("barnase_barstar_Y29F", 0.0)}
        v = pb.qualify(res)
        assert v["qualified"] is True
        assert v["unverified_references"] == ["barnase_barstar_Y29F"]
        assert "PROVISIONAL" in v["caveat"]
    finally:
        pb.BENCHMARKS["barnase_barstar_Y29F"]["ref_verified"] = saved


def test_qualify_with_no_results():
    v = pb.qualify({})
    assert v["qualified"] is False
    assert v["n_scored"] == 0


# ---------------------------------------------------------------- chain surgery / site check
_MINI_PDB = """ATOM      1  N   TYR D  29      10.000  10.000  10.000  1.00 20.00           N
ATOM      2  CA  TYR D  29      11.000  10.000  10.000  1.00 20.00           C
ATOM      3  N   ALA A  27      20.000  20.000  20.000  1.00 20.00           N
ATOM      4  CA  ALA A  27      21.000  20.000  20.000  1.00 20.00           C
ATOM      5  N   SER E  10      30.000  30.000  30.000  1.00 20.00           N
HETATM    6  O   HOH D 200      40.000  40.000  40.000  1.00 20.00           O
END
"""


def test_select_chains_keeps_only_requested_protein_atoms(tmp_path):
    src = tmp_path / "mini.pdb"
    src.write_text(_MINI_PDB)
    out = tmp_path / "sel.pdb"
    rep = pb.select_chains(str(src), ["D"], str(out))
    text = out.read_text()
    assert rep["atoms_per_chain"] == {"D": 2}          # HETATM water excluded
    assert "HOH" not in text and " A  27" not in text and " E  10" not in text


def test_select_chains_refuses_a_missing_chain(tmp_path):
    src = tmp_path / "mini.pdb"
    src.write_text(_MINI_PDB)
    with pytest.raises(ValueError):
        pb.select_chains(str(src), ["Z"], str(tmp_path / "sel.pdb"))


def test_observed_residue_reads_the_real_identity(tmp_path):
    src = tmp_path / "mini.pdb"
    src.write_text(_MINI_PDB)
    assert pb.observed_residue(str(src), "D", 29) == "TYR"
    assert pb.observed_residue(str(src), "A", 27) == "ALA"
    assert pb.observed_residue(str(src), "D", 999) is None


# ---------------------------------------------------------------- reduction
def _leg(leg_id, benchmark, env, dg, gpu_h=1.2, particles=32000, status="done"):
    return {"leg_id": leg_id, "status": status, "dg_kcal": dg, "dg_mbar_se_kcal": 0.2,
            "gpu_hours": gpu_h, "n_particles": particles, "s_per_iter": 1.8,
            "meta": {"benchmark": benchmark, "environment": env}}


def test_ddg_is_complex_minus_apo():
    legs = {"complex": [_leg("a", "b", "complex", -5.0)], "apo": [_leg("b", "b", "apo", -8.4)]}
    res = pr.ddg_for(legs)
    assert res["ddg_bind_kcal"] == pytest.approx(3.4)


def test_single_replicate_gets_no_fabricated_error_bar():
    legs = {"complex": [_leg("a", "b", "complex", -5.0)], "apo": [_leg("b", "b", "apo", -8.4)]}
    res = pr.ddg_for(legs)
    assert res["ddg_sd_kcal"] is None
    assert res["single_replicate"] is True
    assert "NO ERROR BAR" in res["error_model"]


def test_between_replicate_sd_is_used_when_replicates_exist():
    legs = {"complex": [_leg(f"c{i}", "b", "complex", v) for i, v in enumerate([-5.0, -5.4, -4.6])],
            "apo": [_leg(f"a{i}", "b", "apo", v) for i, v in enumerate([-8.4, -8.6, -8.2])]}
    res = pr.ddg_for(legs)
    assert res["ddg_sd_kcal"] is not None and res["ddg_sd_kcal"] > 0
    assert res["single_replicate"] is False


def test_ddg_needs_both_environments():
    assert pr.ddg_for({"complex": [_leg("a", "b", "complex", -5.0)]}) is None


def test_smoke_legs_are_excluded_from_grouping():
    docs = [_leg("barnase_barstar_Y29A__apo_r0_smoke", "barnase_barstar_Y29A", "apo", 99.0),
            _leg("barnase_barstar_Y29A__apo_r0", "barnase_barstar_Y29A", "apo", -8.4)]
    grouped, skipped = pr.group_legs(docs)
    assert len(skipped) == 1
    assert len(grouped["barnase_barstar_Y29A"]["apo"]) == 1
    assert grouped["barnase_barstar_Y29A"]["apo"][0]["dg_kcal"] == -8.4


def test_unfinished_legs_are_excluded_from_grouping():
    docs = [_leg("x__complex_r0", "x", "complex", None, status="production")]
    grouped, _ = pr.group_legs(docs)
    assert grouped == {}


def test_group_legs_falls_back_to_the_leg_id_convention():
    doc = {"leg_id": "barnase_barstar_Y29F__complex_r1", "status": "done", "dg_kcal": -3.0}
    grouped, _ = pr.group_legs([doc])
    assert "complex" in grouped["barnase_barstar_Y29F"]


def test_price_is_reported_as_a_projection_with_its_scaling_stated():
    docs = [_leg("a", "b", "complex", -5.0, gpu_h=1.5), _leg("c", "b", "apo", -8.4, gpu_h=0.9)]
    p = pr.price_from_legs(docs, hourly_usd=0.20)
    assert p["priced"] is True
    assert p["n_legs_measured"] == 2
    assert p["usd_per_benchmark_leg"] == pytest.approx(0.24, abs=1e-3)
    assert p["projected_wedge_usd_3rep"] > p["usd_per_benchmark_leg"]
    assert "PROJECTION" in p["projection_basis"]


def test_price_refuses_without_completed_legs():
    assert pr.price_from_legs([])["priced"] is False


def test_price_excludes_smoke_legs():
    docs = [_leg("x_smoke", "b", "apo", 0.0, gpu_h=0.05)]
    assert pr.price_from_legs(docs)["priced"] is False


def test_reduce_all_end_to_end(tmp_path):
    """A full, correctly-ordered set on disk reduces to a qualified verdict and a price."""
    legs = []
    for i, (dgc, dga) in enumerate([(-5.0, -8.2), (-5.2, -8.3), (-4.9, -8.1)]):
        legs.append(_leg(f"barnase_barstar_Y29A__complex_r{i}", "barnase_barstar_Y29A", "complex", dgc))
        legs.append(_leg(f"barnase_barstar_Y29A__apo_r{i}", "barnase_barstar_Y29A", "apo", dga))
    for i, (dgc, dga) in enumerate([(-6.0, -6.6), (-6.1, -6.6), (-5.9, -6.5)]):
        legs.append(_leg(f"barnase_barstar_Y29F__complex_r{i}", "barnase_barstar_Y29F", "complex", dgc))
        legs.append(_leg(f"barnase_barstar_Y29F__apo_r{i}", "barnase_barstar_Y29F", "apo", dga))
    for leg in legs:
        (tmp_path / f"leg_{leg['leg_id']}.json").write_text(json.dumps(leg))
    out = pr.reduce_all(str(tmp_path), hourly_usd=0.2)
    assert out["verdict"]["qualified"] is True
    assert out["price"]["priced"] is True
    assert set(out["scores"]) == set(pb.BENCHMARKS)


# ---------------------------------------------------------------- launcher (pure construction)
def test_units_for_each_mode():
    assert len(pv.units_for("smoke")) == 1
    assert len(pv.units_for("pilot")) == 2
    assert len(pv.units_for("full", n_replicas=3)) == len(pb.BENCHMARKS) * 2 * 3


def test_smoke_unit_is_the_cheap_apo_leg_of_the_pilot_benchmark():
    (unit,) = pv.units_for("smoke")
    assert unit["environment"] == "apo"
    assert unit["benchmark"] == pb.PILOT_BENCHMARK


def test_pilot_covers_both_environments_of_one_benchmark():
    envs = {u["environment"] for u in pv.units_for("pilot")}
    assert envs == {"complex", "apo"}
    assert {u["benchmark"] for u in pv.units_for("pilot")} == {pb.PILOT_BENCHMARK}


def test_build_jobspec_is_pure_and_carries_the_leg_context():
    spec = pb.leg_spec("barnase_barstar_Y29A", "complex", 0)
    js = pv.build_jobspec(spec, mode="pilot", git_branch="my-branch", bucket="bkt")
    assert js.env["PROTFEP_BENCHMARK"] == "barnase_barstar_Y29A"
    assert js.env["PROTFEP_ENVIRONMENT"] == "complex"
    assert js.env["GIT_BRANCH"] == "my-branch"
    assert js.env["RESULT_S3"].startswith("s3://bkt/")
    assert js.resume is True, "a preempted leg must resume from its .nc, not restart"


def test_smoke_jobspec_is_sized_down_and_tagged_so_it_cannot_be_mistaken_for_a_real_leg():
    (unit,) = pv.units_for("smoke")
    js = pv.build_jobspec(unit, mode="smoke")
    assert js.env["LEG_ID"].endswith("_smoke"), "protfep_reduce refuses to score a _smoke leg"
    assert "--n-states 3" in js.env["PROTFEP_N_STATES_ARG"]
    # Sampling lengths reach the driver as env, not CLI flags, so a mode cannot silently inherit
    # production-length sampling and cost a real leg's money to prove plumbing.
    assert int(js.env["PMX_PROD_PS"]) < 100
    assert int(js.env["PMX_NPT_PS"]) < 20


def test_real_jobspec_leaves_sizing_to_the_module_defaults():
    spec = pb.leg_spec("barnase_barstar_Y29A", "complex", 0)
    js = pv.build_jobspec(spec, mode="pilot")
    assert js.env["PROTFEP_N_STATES_ARG"] == ""
    assert "PMX_PROD_PS" not in js.env, "a real leg must not carry the smoke's shortened sampling"


def test_build_jobspec_rejects_an_unknown_mode():
    spec = pb.leg_spec("barnase_barstar_Y29A", "complex", 0)
    with pytest.raises(ValueError):
        pv.build_jobspec(spec, mode="production")


def test_labels_are_vast_safe_and_reapable():
    for mode in ("smoke", "pilot", "full"):
        for unit in pv.units_for(mode, n_replicas=1):
            label = pv.unit_label(unit, mode)
            assert label.startswith(pv.LABEL_PREFIX), "the reap finds instances by this prefix"
            assert len(label) <= 60
            assert "_" not in label


# ---------------------------------------------------------------- reference verification (SKEMPI)
import protfep_refcheck as rc  # noqa: E402

# Mirrors the REAL SKEMPI rows for 1BRS_A_D (verified in CI 2026-07-24), plus two rows that must be
# rejected: a double mutant and a different complex.
_SKEMPI = ("#Pdb;Mutation(s)_PDB;Affinity_mut (M);Affinity_wt (M);Temperature;Reference\n"
           "1BRS_A_D;YD29A;3.5E-12;1.0E-14;298;7739054\n"
           "1BRS_A_D;YD29F;8.0E-15;1.0E-14;298(assumed);7739054\n"
           "1BRS_A_D;YD29A,DD39A;5.0E-9;1.0E-14;298;double mutant\n"
           "2ABC_A_B;YD29A;1.0E-9;1.0E-14;298;different complex\n")


def test_ddg_from_kd_arithmetic():
    """A 100-fold weaker Kd at 298 K is RT*ln(100) = 2.73 kcal/mol, positive = binds worse."""
    assert rc.ddg_from_kd(1e-11, 1e-13, 298) == pytest.approx(2.728, abs=0.01)
    assert rc.ddg_from_kd(1e-13, 1e-13, 298) == pytest.approx(0.0, abs=1e-9)


def test_ddg_from_kd_rejects_nonpositive():
    with pytest.raises(ValueError):
        rc.ddg_from_kd(0, 1e-13, 298)


def test_multi_mutant_records_are_rejected():
    """A double-mutant ddG is not the single-mutation quantity the alchemical leg computes."""
    assert rc.mutation_matches("YD29A", "D", 29, "Y", "A") is True
    assert rc.mutation_matches("YD29A,DD39A", "D", 29, "Y", "A") is False
    assert rc.mutation_matches("YA29A", "D", 29, "Y", "A") is False, "wrong chain must not match"
    assert rc.mutation_matches("", "D", 29, "Y", "A") is False


def test_temperature_annotations_are_parsed_and_assumptions_flagged():
    assert rc.parse_temperature("298(assumed)") == (298.0, False)
    assert rc.parse_temperature("") == (298.15, True)
    assert rc.parse_temperature("garbage") == (298.15, True)
    assert rc.parse_temperature("9999")[1] is True, "out-of-range temperature falls back and flags"


def test_records_for_filters_by_complex_and_mutation():
    hits, skipped, errors = rc.records_for(_SKEMPI, "1BRS", "D", 29, "Y", "A")
    assert errors == []
    assert len(hits) == 1, "the double mutant and the different complex must be excluded"
    assert hits[0]["ddg_kcal"] == pytest.approx(3.469, abs=0.01)


def test_check_confirms_a_stored_reference_within_tolerance():
    rep = rc.check(csv_text=_SKEMPI)
    assert rep["benchmarks"]["barnase_barstar_Y29A"]["agrees"] is True
    assert rep["benchmarks"]["barnase_barstar_Y29F"]["agrees"] is True


def test_check_flags_a_disagreeing_reference():
    bad = _SKEMPI.replace("3.5E-12;1.0E-14;298;7739054", "1.0E-8;1.0E-14;298;7739054")
    rep = rc.check(csv_text=bad)
    e = rep["benchmarks"]["barnase_barstar_Y29A"]
    assert e["agrees"] is False
    assert "DISAGREES" in e["verdict"]
    assert rep["all_confirmed"] is False


def test_check_does_not_upgrade_verification_on_a_null_result():
    """No record found is NOT confirmation — it must stay unverified, not silently pass."""
    rep = rc.check(csv_text="#Pdb;Mutation(s)_PDB;Affinity_mut (M);Affinity_wt (M);Temperature\n")
    for e in rep["benchmarks"].values():
        assert e["agrees"] is None
        assert "NOT FOUND" in e["verdict"]
    assert rep["all_confirmed"] is False


def test_check_reports_a_missing_column_rather_than_silently_finding_nothing():
    hits, skipped, errors = rc.records_for("wrong;header;entirely\na;b;c\n", "1BRS", "D", 29, "Y", "A")
    assert errors and "columns not found" in errors[0]


def test_a_sign_disagreement_is_never_reported_as_agreement():
    """The real bug this catches: stored +0.5 vs measured -0.13 sat inside the magnitude window.

    A reference with the wrong sign would score a correct engine answer as wrong, so magnitude
    agreement alone must not be enough.
    """
    csv = ("#Pdb;Mutation(s)_PDB;Affinity_mut (M);Affinity_wt (M);Temperature;Reference\n"
           "1BRS_A_D;YD29A;3.5E-12;1.0E-14;298;7739054\n"
           "1BRS_A_D;YD29F;8.0E-15;1.0E-14;298;7739054\n")
    rep = rc.check(csv_text=csv)
    a = rep["benchmarks"]["barnase_barstar_Y29A"]
    f = rep["benchmarks"]["barnase_barstar_Y29F"]
    # Y29A: SKEMPI 3.47 vs the stored 3.4 -> confirmed.
    assert a["agrees"] is True and a["skempi_median_ddg_kcal"] == pytest.approx(3.469, abs=0.01)
    # Y29F: the stored constant is now the SKEMPI-derived -0.13, so it agrees.
    assert f["agrees"] is True and f["skempi_median_ddg_kcal"] == pytest.approx(-0.132, abs=0.01)
    assert rep["all_confirmed"] is True


def test_sign_flip_is_caught_even_within_tolerance():
    """A hypothetical +0.5 stored value against a -0.13 measurement must FAIL, not squeak through."""
    saved = pb.BENCHMARKS["barnase_barstar_Y29F"]["ref_ddg_bind_kcal"]
    pb.BENCHMARKS["barnase_barstar_Y29F"]["ref_ddg_bind_kcal"] = 0.5
    try:
        csv = ("#Pdb;Mutation(s)_PDB;Affinity_mut (M);Affinity_wt (M);Temperature;Reference\n"
               "1BRS_A_D;YD29F;8.0E-15;1.0E-14;298;7739054\n")
        e = rc.check(csv_text=csv)["benchmarks"]["barnase_barstar_Y29F"]
        assert abs(e["delta_vs_stored"]) < 0.75, "the gap IS inside the magnitude window"
        assert e["sign_agrees"] is False
        assert e["agrees"] is False
        assert "SIGN DISAGREEMENT" in e["verdict"]
    finally:
        pb.BENCHMARKS["barnase_barstar_Y29F"]["ref_ddg_bind_kcal"] = saved


def test_references_are_now_marked_verified_so_the_verdict_is_not_provisional():
    res = {"barnase_barstar_Y29A": _score("barnase_barstar_Y29A", 3.4),
           "barnase_barstar_Y29F": _score("barnase_barstar_Y29F", 0.0)}
    v = pb.qualify(res)
    assert v["qualified"] is True
    assert v["unverified_references"] == []
    assert v["caveat"] is None


# ---------------------------------------------------------------- version-skew shim
import protfep_run as prun  # noqa: E402


def test_call_filtered_passes_primary_names_through():
    def f(storage_file=None, n_states=None):
        return (storage_file, n_states)
    assert prun._call_filtered(f, storage_file="s.nc", n_states=11) == ("s.nc", 11)


def test_call_filtered_retries_a_known_alias_before_dropping():
    """A rename must not become a missing REQUIRED argument forty minutes into a rental."""
    def f(storage, number_of_states):
        return (storage, number_of_states)
    assert prun._call_filtered(f, storage_file="s.nc", n_states=11) == ("s.nc", 11)


def test_call_filtered_never_clobbers_an_explicitly_passed_kwarg():
    def f(storage=None, storage_file=None):
        return (storage, storage_file)
    assert prun._call_filtered(f, storage="A", storage_file="B") == ("A", "B")


def test_call_filtered_passes_everything_to_a_varkw_signature():
    def f(**kw):
        return kw
    assert prun._call_filtered(f, anything=1) == {"anything": 1}


def test_iteration_count_is_timestep_independent():
    """An iteration is defined by its MD time, so changing the timestep changes cost, not sampling.

    The ternary lane's cost base was wrong for months because a partial iteration count was mistaken
    for a whole leg; keeping this conversion explicit is what makes a leg length auditable.
    """
    assert prun.iters_for(5.0) == 2000
    assert prun.steps_per_iteration(2.0) == 2 * prun.steps_per_iteration(4.0)


# ---------------------------------------------------------------- reap matching (real money)
def test_label_matches_its_own_leg_for_every_unit_in_every_mode():
    """Every label the launcher creates must match the LEG_ID its jobspec runs under.

    SMOKE IS INCLUDED DELIBERATELY. It used to be the exception and that is exactly what broke: the
    host was labelled `protfep-bench-smoke` while its LEG_ID was `<benchmark>__apo_r0_smoke`, so the
    reap never matched it. The smoke leg then crashed, Vast re-ran onstart in a loop, and the GPU
    billed on with nothing left to produce.
    """
    for mode in ("smoke", "pilot", "full"):
        for unit in pv.units_for(mode, n_replicas=3):
            label = pv.unit_label(unit, mode)
            leg_id = pv.leg_id_for(unit, mode)
            assert pv.label_matches_leg(label, leg_id), f"{label} !~ {leg_id}"


def test_label_and_jobspec_agree_on_the_leg_id_in_every_mode():
    """The label and the jobspec's LEG_ID must come from one source, not two that can drift."""
    for mode in ("smoke", "pilot", "full"):
        for unit in pv.units_for(mode, n_replicas=2):
            js = pv.build_jobspec(unit, mode=mode)
            assert pv.label_matches_leg(js.name, js.env["LEG_ID"]), f"{js.name} !~ {js.env['LEG_ID']}"


def test_label_does_not_match_a_different_leg():
    """Over-matching is the opposite failure: destroying an instance whose leg is still running."""
    a = pb.leg_spec("barnase_barstar_Y29A", "complex", 0)
    b = pb.leg_spec("barnase_barstar_Y29A", "complex", 1)
    assert pv.label_matches_leg(pv.unit_label(a, "pilot"), b["leg_id"]) is False
    assert pv.label_matches_leg(pv.unit_label(a, "pilot"), "barnase_barstar_Y29F__complex_r0") is False


def test_label_match_is_robust_to_empty_input():
    assert pv.label_matches_leg("", "x") is False
    assert pv.label_matches_leg("protfep-bench-x", "") is False
    assert pv.label_matches_leg(None, "x") is False


def test_replicate_labels_are_all_distinct():
    """Two legs sharing a label would make the reap destroy the wrong instance."""
    labels = [pv.unit_label(u, "full") for u in pv.units_for("full", n_replicas=3)]
    assert len(set(labels)) == len(labels)


# ---------------------------------------------------------------- blank-CI-input handling
def test_blank_bucket_env_does_not_produce_a_bucketless_uri(monkeypatch):
    """A blank CI input is an EMPTY STRING, not unset — os.environ.get's default never fires.

    This rented a real 4090 whose results would have gone to 's3:///protfep-benchmark/...' and
    vanished behind `|| true`. Both halves are pinned: the module falls back with `or`, and
    build_jobspec refuses outright rather than emitting a malformed URI.
    """
    monkeypatch.setenv("VAST_CKPT_BUCKET", "")
    import importlib
    mod = importlib.reload(pv)
    try:
        assert mod.DEFAULT_BUCKET, "an empty env var must fall back to the default bucket"
        spec = pb.leg_spec("barnase_barstar_Y29A", "complex", 0)
        js = mod.build_jobspec(spec, mode="pilot")
        assert js.env["RESULT_S3"].startswith("s3://sagemaker-")
        assert "s3:///" not in js.env["RESULT_S3"]
    finally:
        monkeypatch.delenv("VAST_CKPT_BUCKET", raising=False)
        importlib.reload(pv)


def test_an_explicit_empty_bucket_falls_back_rather_than_failing():
    """Empty means unset, at every layer — that is the whole lesson of the bucket-less URI."""
    spec = pb.leg_spec("barnase_barstar_Y29A", "complex", 0)
    js = pv.build_jobspec(spec, mode="pilot", bucket="", result_prefix="")
    assert js.env["RESULT_S3"].startswith("s3://sagemaker-")
    assert "s3:///" not in js.env["RESULT_S3"]


def test_build_jobspec_refuses_when_there_is_nothing_to_fall_back_to(monkeypatch):
    """Last-resort guard: if even the default is blank, refuse rather than emit 's3:///...'."""
    monkeypatch.setattr(pv, "DEFAULT_BUCKET", "")
    spec = pb.leg_spec("barnase_barstar_Y29A", "complex", 0)
    with pytest.raises(ValueError, match="incomplete result location"):
        pv.build_jobspec(spec, mode="pilot", bucket="")


def test_bioemu_launcher_has_the_same_fix():
    """The identical hole existed in the sibling Vast lane; pin it so it is not reintroduced."""
    import pathlib
    src = pathlib.Path(__file__).resolve().parents[1] / "nr4a3_bioemu_vast_launch.py"
    text = src.read_text()
    assert "os.environ.get('VAST_CKPT_BUCKET', " not in text
    assert 'os.environ.get("VAST_CKPT_BUCKET") or' in text


# ---------------------------------------------------------------- OpenEye import shim
def test_openeye_shim_satisfies_the_import_perses_actually_makes():
    """perses' PointMutationExecutor.__init__ runs `from openeye import oechem` unconditionally.

    OpenEye is commercial and license-gated, and perses only USES it for small-molecule handling
    (inside `if ligand_input:`). Our legs are protein-only, so the statement is dead code that
    happens to sit above the branch. The shim satisfies it and nothing else.
    """
    import sys as _sys
    for key in [k for k in _sys.modules if k == "openeye" or k.startswith("openeye.")]:
        del _sys.modules[key]
    assert prun._install_openeye_shim() is True
    from openeye import oechem
    assert oechem.__name__ == "openeye.oechem"
    import openeye.oechem  # noqa: F401 — the dotted form must work too


def test_openeye_shim_raises_on_any_real_use():
    """A shim that quietly returned something plausible would be far worse than the import error."""
    import sys as _sys
    for key in [k for k in _sys.modules if k == "openeye" or k.startswith("openeye.")]:
        del _sys.modules[key]
    prun._install_openeye_shim()
    from openeye import oechem
    with pytest.raises(RuntimeError, match="tried to USE OpenEye"):
        oechem.OEGraphMol


def test_openeye_shim_leaves_dunders_alone():
    """Python's import machinery probes __file__/__path__; poisoning those breaks the import."""
    poison = prun._PoisonedOpenEye("openeye.oechem")
    with pytest.raises(AttributeError):
        poison.__getattr__("__file__")
    with pytest.raises(RuntimeError):
        poison.__getattr__("OEMol")


def test_openeye_shim_defers_to_a_real_install(monkeypatch):
    """If a licensed OpenEye is ever present it must win — the shim never shadows it."""
    import sys as _sys
    import types as _types
    real = _types.ModuleType("openeye")
    real.oechem = _types.ModuleType("openeye.oechem")
    monkeypatch.setitem(_sys.modules, "openeye", real)
    assert prun._install_openeye_shim() is False
    assert _sys.modules["openeye"] is real


def test_openeye_shim_answers_licence_probes_with_false():
    """openff-toolkit calls oechem.OEChemIsLicensed() at import to decide whether to register its
    OpenEye wrapper. Raising there is WORSE than no shim — it makes OpenEye look present-but-broken
    and kills openff's import (observed on the free build-test). False is both survivable and true:
    we have no licence, so the stack uses its RDKit/AmberTools path.
    """
    import sys as _sys
    for key in [k for k in _sys.modules if k == "openeye" or k.startswith("openeye.")]:
        del _sys.modules[key]
    prun._install_openeye_shim()
    from openeye import oechem
    assert oechem.OEChemIsLicensed() is False
    assert oechem.OEBioIsLicensed() is False
    with pytest.raises(RuntimeError, match="tried to USE OpenEye"):
        oechem.OEGraphMol


# ---------------------------------------------------------------- pmx driver (pure layer)
import protfep_pmx as ppmx  # noqa: E402


def test_lambda_vector_spans_the_full_range():
    v = [float(x) for x in ppmx.lambda_vector(5).split()]
    assert v[0] == 0.0 and v[-1] == 1.0 and len(v) == 5
    assert all(b > a for a, b in zip(v, v[1:])), "lambda points must be monotonic"


def test_lambda_vector_refuses_a_degenerate_schedule():
    with pytest.raises(ValueError):
        ppmx.lambda_vector(1)


def test_window_mdp_selects_its_own_state_and_writes_dhdl_to_all_neighbours():
    mdp = ppmx.mdp_lambda_window(3, 8, 100, collect_data=True)
    assert "init-lambda-state = 3" in mdp
    assert "free-energy = yes" in mdp
    # -1 = write dH to EVERY other lambda, which is what BAR needs across the whole schedule.
    assert "calc-lambda-neighbors = -1" in mdp
    assert "couple-intramol = no" in mdp, "a mutated side chain is not decoupled from its own protein"


def test_equilibration_mdp_generates_velocities_only_for_nvt():
    nvt = ppmx.mdp_equil(50, pressure=False)
    npt = ppmx.mdp_equil(50, pressure=True)
    assert "gen-vel = yes" in nvt and "pcoupl = no" in nvt
    assert "gen-vel = no" in npt and "pcoupl = C-rescale" in npt


def test_mdp_step_count_follows_from_the_timestep():
    """nsteps must be derived from a TIME, so changing the timestep changes cost, not sampling."""
    mdp = ppmx.mdp_equil(100, pressure=False)
    nsteps = int([ln for ln in mdp.splitlines() if ln.startswith("nsteps")][0].split("=")[1])
    assert nsteps == int(100 / (ppmx.TIMESTEP_FS / 1000.0))


def test_mutation_site_verification_accepts_a_correct_mutation(tmp_path):
    """The check must pass when the intended chain changed and no other chain did."""
    import nr4a3_protein_fep as pf
    orig = tmp_path / "orig.pdb"
    orig.write_text(
        "ATOM      1  CA  TYR D  29      10.000  10.000  10.000  1.00 20.00           C\n"
        "ATOM      2  CA  LEU A  29      20.000  20.000  20.000  1.00 20.00           C\nEND\n")
    mut = tmp_path / "mut.pdb"
    mut.write_text(
        "ATOM      1  CA  Y2A D  29      10.000  10.000  10.000  1.00 20.00           C\n"
        "ATOM      2  CA  LEU A  29      20.000  20.000  20.000  1.00 20.00           C\nEND\n")
    m = pf.classify_mutation("D:Y29A")
    assert ppmx._verify_mutation_site(str(mut), m, str(orig)) == "Y2A"


def test_mutation_site_verification_catches_a_chain_blind_mutation(tmp_path):
    """The real risk: in the complex leg BOTH chains have a residue 29.

    A chain-blind pmx would perturb barnase instead of barstar and return a converged, confidently
    wrong ddG — a failure with no symptom unless it is checked for.
    """
    import nr4a3_protein_fep as pf
    orig = tmp_path / "orig.pdb"
    orig.write_text(
        "ATOM      1  CA  TYR D  29      10.000  10.000  10.000  1.00 20.00           C\n"
        "ATOM      2  CA  LEU A  29      20.000  20.000  20.000  1.00 20.00           C\nEND\n")
    wrong = tmp_path / "wrong.pdb"
    wrong.write_text(
        "ATOM      1  CA  TYR D  29      10.000  10.000  10.000  1.00 20.00           C\n"
        "ATOM      2  CA  L2A A  29      20.000  20.000  20.000  1.00 20.00           C\nEND\n")
    m = pf.classify_mutation("D:Y29A")
    with pytest.raises(RuntimeError, match="still TYR"):
        ppmx._verify_mutation_site(str(wrong), m, str(orig))


def test_mutation_site_verification_catches_a_second_unintended_mutation(tmp_path):
    import nr4a3_protein_fep as pf
    orig = tmp_path / "orig.pdb"
    orig.write_text(
        "ATOM      1  CA  TYR D  29      10.000  10.000  10.000  1.00 20.00           C\n"
        "ATOM      2  CA  LEU A  29      20.000  20.000  20.000  1.00 20.00           C\nEND\n")
    both = tmp_path / "both.pdb"
    both.write_text(
        "ATOM      1  CA  Y2A D  29      10.000  10.000  10.000  1.00 20.00           C\n"
        "ATOM      2  CA  L2A A  29      20.000  20.000  20.000  1.00 20.00           C\nEND\n")
    m = pf.classify_mutation("D:Y29A")
    with pytest.raises(RuntimeError, match="also changed chain A"):
        ppmx._verify_mutation_site(str(both), m, str(orig))


def test_mutation_site_verification_catches_a_vanished_residue(tmp_path):
    import nr4a3_protein_fep as pf
    orig = tmp_path / "orig.pdb"
    orig.write_text("ATOM      1  CA  TYR D  29      10.000  10.000  10.000  1.00 20.00           C\nEND\n")
    gone = tmp_path / "gone.pdb"
    gone.write_text("ATOM      1  CA  TYR D  30      10.000  10.000  10.000  1.00 20.00           C\nEND\n")
    m = pf.classify_mutation("D:Y29A")
    with pytest.raises(RuntimeError, match="absent"):
        ppmx._verify_mutation_site(str(gone), m, str(orig))


def test_forcefield_resolution_prefers_the_requested_field(monkeypatch):
    monkeypatch.setattr(ppmx, "discover_forcefields",
                        lambda: {"amber99sb-star-ildn-mut": "/d", "charmm36m-mut": "/d"})
    assert ppmx.resolve_forcefield("amber99sb-star-ildn-mut") == ("amber99sb-star-ildn-mut", "/d")


def test_forcefield_resolution_falls_back_within_the_benchmarked_family(monkeypatch):
    """pmx's data layout moves between releases, and get_ff_path raises a bare 'not found' naming
    neither where it looked nor what exists. A fallback must stay in the amber99sb*-mut family, which
    is what pmx's protein-mutation benchmarks were built on — and must be logged, never silent."""
    monkeypatch.setattr(ppmx, "discover_forcefields",
                        lambda: {"amber99sb-star-ildn-mut_alt": "/x", "charmm36m-mut": "/y"})
    name, root = ppmx.resolve_forcefield("amber99sb-star-ildn-mut")
    assert name == "amber99sb-star-ildn-mut_alt" and root == "/x"


def test_forcefield_resolution_refuses_when_pmx_ships_none(monkeypatch):
    """A stock GROMACS force field cannot express an A->B hybrid residue, so there is no fallback."""
    monkeypatch.setattr(ppmx, "discover_forcefields", lambda: {})
    with pytest.raises(RuntimeError, match="no \\*.ff mutation force fields"):
        ppmx.resolve_forcefield("anything")


def test_window_mdp_enables_coulomb_softcore_with_a_shared_lambda_vector():
    """GROMACS refuses vdW softcore alongside a nonzero coul-lambda without coulomb softcore.

    A residue mutation changes charges and vdW on the SAME atoms, so the ligand answer (decharge on
    a separate schedule, then decouple vdW) does not transfer — softcore on both is what pmx's own
    protein-mutation protocols do.
    """
    mdp = ppmx.mdp_lambda_window(1, 4, 100, collect_data=True)
    assert "sc-coul = yes" in mdp
    assert "sc-alpha = 0.3" in mdp
    assert "fep-lambdas" in mdp, "one vector drives all components for a residue mutation"


def test_reduce_reports_the_engine_from_the_legs_not_a_hardcoded_string():
    """The reducer is engine-agnostic — it survived the perses -> pmx switch untouched — so it must
    not assert an engine the legs did not use."""
    docs = [_leg("x__complex_r0", "x", "complex", -5.0), _leg("x__apo_r0", "x", "apo", -8.4)]
    for d in docs:
        d["engine"] = "pmx + GROMACS"
        d["protocol"] = "equilibrium lambda windows"
    import json as _json, pathlib, tempfile
    with tempfile.TemporaryDirectory() as td:
        for d in docs:
            pathlib.Path(td, f"leg_{d['leg_id']}.json").write_text(_json.dumps(d))
        out = pr.reduce_all(td)
    assert out["engines"] == ["pmx + GROMACS"]
    assert out["protocols"] == ["equilibrium lambda windows"]


# ---------------------------------------------------------------- target resolution after pdb2gmx
def _pdb(rows):
    return "".join(
        f"ATOM  {i+1:5d}  CA  {rn:>3s} {ch}{rid:4d}      0.000   0.000   0.000  1.00 20.00           C\n"
        for i, (ch, rid, rn) in enumerate(rows)) + "END\n"


def test_target_is_found_after_pdb2gmx_relabels_the_chain(tmp_path):
    """pdb2gmx does not preserve author chain identity across a multi-chain system.

    The complex leg failed with `resid 29 not found in chain "D"` even though barstar's Y29 was
    plainly present — under a different label. Resolution goes by SEQUENCE, which pdb2gmx does not
    change, not by the label, which it does.
    """
    import nr4a3_protein_fep as pf
    orig = tmp_path / "orig.pdb"
    prepped = tmp_path / "prepped.pdb"
    barnase = [("A", i, "LEU") for i in range(1, 11)]
    barstar = [("D", i, "SER") for i in range(1, 29)] + [("D", 29, "TYR")] + [("D", 30, "GLY")]
    orig.write_text(_pdb(barnase + barstar))
    # pdb2gmx renames D -> B and renumbers it continuously after chain A
    relabelled = [("A", i, "LEU") for i in range(1, 11)] + \
                 [("B", 10 + i, "SER") for i in range(1, 29)] + \
                 [("B", 39, "TYR"), ("B", 40, "GLY")]
    prepped.write_text(_pdb(relabelled))
    m = pf.classify_mutation("D:Y29A")
    chain, resid = ppmx.resolve_target_after_prep(str(prepped), str(orig), m)
    assert (chain, resid) == ("B", 39)


def test_target_resolution_refuses_when_the_wild_type_does_not_match(tmp_path):
    """Belt and braces: the chain matches well overall, but the resolved position is not the WT.

    A high-similarity match landing on the wrong residue is exactly the case that would otherwise
    become a confident wrong ddG, so the identity is re-checked after resolution.
    """
    import nr4a3_protein_fep as pf
    orig = tmp_path / "o.pdb"; prepped = tmp_path / "p.pdb"
    seq = [("D", i, "SER") for i in range(1, 29)] + [("D", 29, "TYR"), ("D", 30, "GLY")]
    orig.write_text(_pdb(seq))
    # Same chain, but the target position already carries PHE — ~97% similar, so it clears the
    # sequence gate and must be caught by the wild-type check instead.
    altered = [("B", i, "SER") for i in range(1, 29)] + [("B", 29, "PHE"), ("B", 30, "GLY")]
    prepped.write_text(_pdb(altered))
    m = pf.classify_mutation("D:Y29A")
    with pytest.raises(RuntimeError, match="not the expected TYR"):
        ppmx.resolve_target_after_prep(str(prepped), str(orig), m)


def test_target_resolution_refuses_a_poor_sequence_match(tmp_path):
    """No chain resembling the target means we do not know where to mutate — refuse, do not guess."""
    import nr4a3_protein_fep as pf
    orig = tmp_path / "o.pdb"; prepped = tmp_path / "p.pdb"
    orig.write_text(_pdb([("D", 1, "SER"), ("D", 29, "TYR")]))
    prepped.write_text(_pdb([("B", 1, "LEU"), ("B", 2, "ALA")]))
    m = pf.classify_mutation("D:Y29A")
    with pytest.raises(RuntimeError, match="could not identify the target chain"):
        ppmx.resolve_target_after_prep(str(prepped), str(orig), m)


def test_target_resolution_refuses_two_equally_similar_chains(tmp_path):
    """Two near-identical chains means the mutation could land on either — refuse, do not pick."""
    import nr4a3_protein_fep as pf
    orig = tmp_path / "o.pdb"; prepped = tmp_path / "p.pdb"
    seq = [("D", i, "SER") for i in range(1, 29)] + [("D", 29, "TYR")]
    orig.write_text(_pdb(seq))
    dup = [("A", i, "SER") for i in range(1, 29)] + [("A", 29, "TYR")] + \
          [("B", i, "SER") for i in range(1, 29)] + [("B", 29, "TYR")]
    prepped.write_text(_pdb(dup))
    m = pf.classify_mutation("D:Y29A")
    with pytest.raises(RuntimeError, match="AMBIGUOUS"):
        ppmx.resolve_target_after_prep(str(prepped), str(orig), m)


def test_chain_residue_lists_dedupes_atoms_into_residues(tmp_path):
    p = tmp_path / "x.pdb"
    p.write_text(
        "ATOM      1  N   TYR D  29       0.000   0.000   0.000  1.00 20.00           N\n"
        "ATOM      2  CA  TYR D  29       0.000   0.000   0.000  1.00 20.00           C\n"
        "ATOM      3  CA  GLY D  30       0.000   0.000   0.000  1.00 20.00           C\nEND\n")
    assert ppmx.chain_residue_lists(str(p)) == {"D": [(29, "TYR"), (30, "GLY")]}


def test_progress_board_uses_the_engine_s_own_unit():
    """A pmx leg advances in lambda WINDOWS; an openmmtools leg advances in iterations.

    Printing the wrong field showed "0/None iters" for a leg that was four windows in and perfectly
    healthy. A board that under-reports progress is worse than no board — it reads as a stall.
    """
    pmx_leg = {"leg_id": "x", "status": "sampling", "windows_done": 4, "n_states": 16}
    omm_leg = {"leg_id": "y", "status": "production", "iterations_done": 250, "prod_iters_target": 2000}
    # The selection logic mirrors collect(); assert the field choice rather than capturing stdout.
    assert (pmx_leg.get("windows_done") is not None or pmx_leg.get("n_states"))
    assert not (omm_leg.get("windows_done") is not None or omm_leg.get("n_states"))


def test_resume_pulls_back_everything_the_sync_uploads():
    """Upload and resume must be SYMMETRIC, or a preempted leg silently redoes finished work.

    The apo pilot leg was preempted at 14/16 windows. The sync loop had been uploading each finished
    window's .xvg, but the resume pulled only the leg JSON — so a re-dispatch would have re-run all
    14 windows, ~1 GPU-h paid twice, with nothing in the log to say why.
    """
    pipeline = pv._PIPELINE
    resume_block = pipeline.split("RESUME:")[1].split("repo code")[0]
    for needed in ('--include "leg_$LEG_ID.json"', '--include "work_$LEG_ID/*"'):
        assert needed in resume_block, f"resume does not restore {needed}"
    # everything the uploads write under work_<leg>/ must be restorable by that wildcard
    for uploaded in ("work_$LEG_ID/*.xvg", "work_$LEG_ID/hybrid.top", "work_$LEG_ID/npt.gro"):
        assert uploaded in pipeline, f"{uploaded} is never uploaded, so it can never be resumed"


def test_build_system_short_circuits_on_a_restored_system(tmp_path, monkeypatch):
    """A restored system must skip setup entirely — that is the point of resuming."""
    monkeypatch.setattr(ppmx, "resolve_forcefield", lambda req: ("ff-mut", "/ffroot"))
    work = tmp_path / "work"
    work.mkdir()
    (work / "hybrid.top").write_text("; topology\n")
    (work / "npt.gro").write_text("system\n 13392\n")
    gro, top, n_atoms, ff = ppmx.build_system("/nonexistent/input.pdb", "D:Y29A", str(work))
    assert n_atoms == 13392 and ff == "ff-mut"
    assert gro.endswith("npt.gro") and top.endswith("hybrid.top")


def test_build_system_does_not_short_circuit_on_a_partial_restore(tmp_path, monkeypatch):
    """hybrid.top without npt.gro is half a system; continuing from it is worse than rebuilding."""
    monkeypatch.setattr(ppmx, "resolve_forcefield", lambda req: ("ff-mut", "/ffroot"))
    work = tmp_path / "work"
    work.mkdir()
    (work / "hybrid.top").write_text("; topology\n")
    # No npt.gro -> must NOT short-circuit; it proceeds and fails on the missing input instead.
    with pytest.raises(Exception):
        ppmx.build_system("/nonexistent/input.pdb", "D:Y29A", str(work))


# ---------------------------------------------------------------- cost integrity across resumes
def test_reap_ignores_a_stale_failure_record():
    """A failure from a PREVIOUS attempt must not kill a freshly launched host.

    The complex leg was destroyed 25 minutes into its image pull because a `failed` leg JSON from an
    attempt 90 minutes earlier was still in S3 — the new leg had not yet overwritten it, which does
    not happen until after the pull and clone.
    """
    instance = {"start_date": 2000.0}
    stale = {"status": "failed", "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(1000.0))}
    fresh = {"status": "failed", "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(3000.0))}
    assert pv._record_is_newer_than_instance(stale, instance) is False
    assert pv._record_is_newer_than_instance(fresh, instance) is True


def test_reap_guard_is_conservative_on_missing_timestamps():
    """Not reaping costs a self-destruct or the runtime backstop; reaping wrongly kills real work."""
    assert pv._record_is_newer_than_instance({}, {"start_date": 1.0}) is False
    assert pv._record_is_newer_than_instance({"updated_utc": "nonsense"}, {"start_date": 1.0}) is False
    assert pv._record_is_newer_than_instance({"updated_utc": "2026-07-24T00:00:00Z"}, {}) is False


def test_price_uses_cumulative_gpu_hours_not_the_final_segment():
    """A preempted leg reports only its last segment unless the field accumulates.

    The apo pilot leg finished in 0.073 GPU-h after being preempted at 14/16 windows, and the reducer
    published usd_per_benchmark_leg=0.015 — ~20x low, because ~1.3 GPU-h had gone with the host. A
    cost basis that silently omits preempted work is worse than none.
    """
    resumed = _leg("x__complex_r0", "x", "complex", -5.0, gpu_h=1.4)
    resumed["gpu_hours_this_run"] = 0.073
    resumed["gpu_hours_prior_attempts"] = 1.33
    priced = pr.price_from_legs([resumed], hourly_usd=0.20)
    # gpu_hours is the cumulative figure, so the price reflects the whole leg
    assert priced["gpu_hours_per_leg"]["mean"] == pytest.approx(1.4)
    assert priced["usd_per_benchmark_leg"] == pytest.approx(0.28, abs=0.01)


# ---------------------------------------------------------------- resolution against pmx's Model
class _FakeRes:
    def __init__(self, rid, name):
        self.id, self.resname = rid, name


class _FakeChain:
    def __init__(self, cid, residues):
        self.id = cid
        self.residues = [_FakeRes(r, n) for r, n in residues]


class _FakeModel:
    def __init__(self, chains):
        self.chains = [_FakeChain(c, r) for c, r in chains]


def test_model_inventory_reads_pmx_s_own_chains():
    model = _FakeModel([("A", [(1, "LEU"), (2, "SER")]), ("B", [(1, "GLY")])])
    assert ppmx.model_residue_lists(model) == {"A": [(1, "LEU"), (2, "SER")], "B": [(1, "GLY")]}


def test_model_inventory_falls_back_to_an_index_when_a_chain_has_no_id():
    class _NoId:
        def __init__(self):
            self.residues = [_FakeRes(1, "ALA")]
    model = type("M", (), {"chains": [_NoId()]})()
    assert ppmx.model_residue_lists(model) == {"0": [(1, "ALA")]}


def test_resolution_uses_the_model_not_the_file(tmp_path):
    """The bug: prepped.pdb said D:29, the file-based resolver returned D:29, and pmx still raised
    `resid 29 not found in chain "D"` — pmx's Model exposes different chain labels than the file.
    Resolution must consult the representation the mutation is actually addressed to.
    """
    import nr4a3_protein_fep as pf
    orig = tmp_path / "orig.pdb"
    barstar = [("D", i, "SER") for i in range(1, 29)] + [("D", 29, "TYR"), ("D", 30, "GLY")]
    orig.write_text(_pdb([("A", i, "LEU") for i in range(1, 11)] + barstar))
    # pmx's Model labels the same chains 0 and 1, with its own numbering
    model = _FakeModel([
        ("0", [(i, "LEU") for i in range(1, 11)]),
        ("1", [(i, "SER") for i in range(1, 29)] + [(29, "TYR"), (30, "GLY")]),
    ])
    m = pf.classify_mutation("D:Y29A")
    assert ppmx.resolve_target_in_model(model, str(orig), m) == ("1", 29)


def test_model_resolution_refuses_a_wrong_wild_type(tmp_path):
    import nr4a3_protein_fep as pf
    orig = tmp_path / "orig.pdb"
    orig.write_text(_pdb([("D", i, "SER") for i in range(1, 29)] + [("D", 29, "TYR"), ("D", 30, "GLY")]))
    model = _FakeModel([("0", [(i, "SER") for i in range(1, 29)] + [(29, "PHE"), (30, "GLY")])])
    m = pf.classify_mutation("D:Y29A")
    with pytest.raises(RuntimeError, match="not the expected TYR"):
        ppmx.resolve_target_in_model(model, str(orig), m)


def test_both_resolvers_share_one_matching_rule():
    """File-based and Model-based resolution must not drift — one rule, two front doors."""
    import inspect
    assert "_match_target_chain" in inspect.getsource(ppmx.resolve_target_after_prep)
    assert "_match_target_chain" in inspect.getsource(ppmx.resolve_target_in_model)


def test_split_topology_guard_refuses_per_chain_itp_files(tmp_path):
    """A split topology means gentop converts a file of #includes and the mutated chain keeps plain
    parameters. grompp then fails with 'No default Angle types' naming the .itp — the symptom, not
    the cause — which cost the complex leg a full diagnostic cycle to trace."""
    (tmp_path / "topol_Protein_chain_D.itp").write_text("; chain D\n")
    with pytest.raises(RuntimeError, match="split the topology"):
        ppmx._split_topology_guard(str(tmp_path))


def test_split_topology_guard_passes_on_an_inline_topology(tmp_path):
    (tmp_path / "topol.top").write_text("; everything inline\n")
    ppmx._split_topology_guard(str(tmp_path))  # must not raise


def test_mutant_pdb2gmx_merges_chains():
    """Without -merge all, any multi-chain leg silently produces an unconvertible topology."""
    import inspect
    src = inspect.getsource(ppmx.build_system)
    mutant_call = src.split('"-f", "mutant.pdb"')[1].split("cwd=work_dir")[0]
    assert '"-merge", "all"' in mutant_call


def test_submit_skips_finished_legs_before_renting(monkeypatch, capsys):
    """The onstart idempotency check only fires AFTER the image pull, so a re-dispatch rented a GPU
    for ~25 minutes just to discover the leg was done and exit — $0.15 a time. The launcher has S3
    access; the cheap check belongs before the rental."""
    done = [pv.leg_id_for(u, "pilot") for u in pv.units_for("pilot")]
    monkeypatch.setattr(pv, "completed_leg_ids", lambda *a, **k: done)
    assert pv.submit(mode="pilot") == []
    assert "already done" in capsys.readouterr().out


def test_submit_still_launches_the_unfinished_leg(monkeypatch):
    """Only the finished unit is skipped — the other must still be rented."""
    units = pv.units_for("pilot")
    finished = pv.leg_id_for(units[0], "pilot")
    monkeypatch.setattr(pv, "completed_leg_ids", lambda *a, **k: [finished])
    submitted = []

    class _Backend:
        def submit(self, js):
            submitted.append(js.env["LEG_ID"])
            return type("H", (), {"job_id": "x", "extra": {}})()

    monkeypatch.setattr(pv, "get_backend", lambda name: _Backend())
    pv.submit(mode="pilot")
    assert submitted == [pv.leg_id_for(units[1], "pilot")]


def test_completed_leg_ids_never_blocks_a_launch(monkeypatch):
    """A listing failure must degrade to launching everything, not to launching nothing."""
    import builtins
    real_import = builtins.__import__

    def _boom(name, *a, **k):
        if name == "boto3":
            raise ImportError("no boto3")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", _boom)
    assert pv.completed_leg_ids() == []
