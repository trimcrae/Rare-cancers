import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import fep_sharding as fs  # noqa: E402


def test_enumerate_units_count_and_shape():
    units = fs.enumerate_units(n_windows=12)
    assert len(units) == 3 * 2 * 12
    ids = {u["id"] for u in units}
    assert len(ids) == len(units)                      # ids unique
    assert units[0]["lambda"] == 0.0
    # endpoints present for each (receptor, leg)
    assert any(u["window"] == 11 and u["lambda"] == 1.0 for u in units)


def test_enumerate_rejects_too_few_windows():
    for bad in (0, 1):
        try:
            fs.enumerate_units(n_windows=bad)
            assert False, "should raise"
        except ValueError:
            pass


def test_assign_shards_balanced_and_covers_all():
    units = fs.enumerate_units(n_windows=12)          # 72 units
    shards = fs.assign_shards(units, 8)
    assert len(shards) == 8
    sizes = [len(s) for s in shards]
    assert max(sizes) - min(sizes) <= 1               # balanced
    flat = [u["id"] for s in shards for u in s]
    assert sorted(flat) == sorted(u["id"] for u in units)   # no loss/dup


def test_assign_shards_more_shards_than_units():
    units = fs.enumerate_units(receptors=("nr4a3",), legs=("solvent",), n_windows=3)  # 3 units
    shards = fs.assign_shards(units, 8)
    assert len(shards) == 3                            # capped at #units
    assert all(len(s) == 1 for s in shards)


def test_pending_units_resume():
    units = fs.enumerate_units(n_windows=12)
    done = {units[0]["id"], units[5]["id"], units[71]["id"]}
    pend = fs.pending_units(units, done)
    assert len(pend) == len(units) - 3
    assert all(u["id"] not in done for u in pend)


def test_shard_plan_resume_reduces_and_reshards():
    all_ids = [u["id"] for u in fs.enumerate_units(n_windows=12)]
    done = set(all_ids[:70])                            # only 2 left
    plan = fs.shard_plan(n_windows=12, n_shards=8, done_ids=done)
    assert plan["n_units_total"] == 72
    assert plan["n_units_pending"] == 2
    assert plan["n_shards"] == 2                        # capped to pending
    assert sum(plan["per_shard_sizes"]) == 2


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
