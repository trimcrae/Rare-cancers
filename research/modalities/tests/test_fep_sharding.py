import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import fep_sharding as fs  # noqa: E402


def test_enumerate_units_one_per_receptor():
    units = fs.enumerate_units(n_windows=12)
    assert len(units) == 3                              # one full-ABFE Yank unit per receptor
    assert [u["id"] for u in units] == ["nr4a3", "nr4a1", "nr4a2"]
    assert {u["id"] for u in units} == set(u["receptor"] for u in units)
    assert all(u["n_windows"] == 12 for u in units)     # λ-path length carried as a protocol param


def test_enumerate_rejects_too_few_windows():
    for bad in (0, 1):
        try:
            fs.enumerate_units(n_windows=bad)
            assert False, "should raise"
        except ValueError:
            pass


def test_assign_shards_balanced_and_covers_all():
    units = fs.enumerate_units(n_windows=12)           # 3 units
    shards = fs.assign_shards(units, 3)
    assert len(shards) == 3
    sizes = [len(s) for s in shards]
    assert max(sizes) - min(sizes) <= 1                # balanced
    flat = [u["id"] for s in shards for u in s]
    assert sorted(flat) == sorted(u["id"] for u in units)   # no loss/dup


def test_assign_shards_more_shards_than_units():
    units = fs.enumerate_units(receptors=("nr4a3",))   # 1 unit
    shards = fs.assign_shards(units, 8)
    assert len(shards) == 1                             # capped at #units
    assert all(len(s) == 1 for s in shards)


def test_pending_units_resume():
    units = fs.enumerate_units(n_windows=12)
    done = {units[0]["id"]}                             # nr4a3 done
    pend = fs.pending_units(units, done)
    assert len(pend) == 2
    assert all(u["id"] not in done for u in pend)


def test_shard_plan_resume_reduces_and_reshards():
    plan = fs.shard_plan(n_windows=12, n_shards=8, done_ids={"nr4a3", "nr4a1"})   # only nr4a2 left
    assert plan["n_units_total"] == 3
    assert plan["n_units_pending"] == 1
    assert plan["n_shards"] == 1                        # capped to pending
    assert sum(plan["per_shard_sizes"]) == 1


def test_binding_dg_identity():
    # ΔG_bind = solvent − complex + restraint_corr
    dg = fs.binding_dg({"solvent": -5.0, "complex": -30.0}, restraint_corr=2.0)
    assert abs(dg - (-5.0 - (-30.0) + 2.0)) < 1e-9     # = 27.0


def test_binding_dg_requires_both_legs():
    try:
        fs.binding_dg({"solvent": -5.0})
        assert False
    except ValueError:
        pass


def test_selectivity_ddg_sign():
    # NR4A3 tighter (more negative ΔG_bind) than paralogues -> ΔΔG < 0 (reference-selective)
    binding = {"nr4a3": -12.0, "nr4a1": -8.0, "nr4a2": -7.0}
    ddg = fs.selectivity_ddg(binding, reference="nr4a3")
    assert ddg["nr4a1"] == -4.0 and ddg["nr4a2"] == -5.0
    assert all(v < 0 for v in ddg.values())


def test_combine_error_quadrature():
    assert abs(fs.combine_error(3.0, 4.0) - 5.0) < 1e-9


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
