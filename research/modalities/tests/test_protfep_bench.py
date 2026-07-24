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
    """Both inside 1.5 kcal/mol of their references, but ranked backwards -> FAIL.

    A wedge is read as a ranking, so ordering is the load-bearing property.
    """
    res = {"barnase_barstar_Y29A": _score("barnase_barstar_Y29A", 1.95),
           "barnase_barstar_Y29F": _score("barnase_barstar_Y29F", 1.99)}
    assert res["barnase_barstar_Y29A"]["within_tolerance"]
    assert res["barnase_barstar_Y29F"]["within_tolerance"]
    v = pb.qualify(res)
    assert v["qualified"] is False
    assert "ORDERING WRONG" in v["reason"]


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
    res = {"barnase_barstar_Y29A": _score("barnase_barstar_Y29A", 3.4),
           "barnase_barstar_Y29F": _score("barnase_barstar_Y29F", 0.5)}
    v = pb.qualify(res)
    assert v["qualified"] is True
    assert v["unverified_references"], "references are flagged unverified in BENCHMARKS"
    assert "PROVISIONAL" in v["caveat"]


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
