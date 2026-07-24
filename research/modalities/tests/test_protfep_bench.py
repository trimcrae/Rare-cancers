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
    assert js.env["LEG_ID"].endswith("_smoke")
    assert "--n-states 3" in js.env["PROTFEP_N_STATES_ARG"]
    assert "--prod-iters 20" in js.env["PROTFEP_PROD_ITERS_ARG"]


def test_real_jobspec_leaves_sizing_to_the_module_defaults():
    spec = pb.leg_spec("barnase_barstar_Y29A", "complex", 0)
    js = pv.build_jobspec(spec, mode="pilot")
    assert js.env["PROTFEP_N_STATES_ARG"] == ""
    assert js.env["PROTFEP_PROD_ITERS_ARG"] == ""


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
def test_label_matches_its_own_leg_for_every_unit():
    """Every label the launcher creates must match back to its leg, or the reap misses it.

    A missed match leaves a FINISHED leg's GPU billing until the runtime backstop hours later.
    """
    for mode in ("pilot", "full"):
        for unit in pv.units_for(mode, n_replicas=3):
            label = pv.unit_label(unit, mode)
            assert pv.label_matches_leg(label, unit["leg_id"]), f"{label} !~ {unit['leg_id']}"


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
