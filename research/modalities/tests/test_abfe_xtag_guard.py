"""Unit tests for the two cross-tag ABFE reduction safeguards (external reviewer §8 + §2.6/§7).

PURE-LOGIC tests (no pymbar / numpy / openmm) fully exercise:
  * abfe_xtag_guard.check_xtag_compatibility  — synthetic meta dicts: matching→compatible; mismatched
    ligand/temperature/restraint-convention→incompatible; missing safety-critical fields→unverifiable +
    fail-closed.
  * abfe_xtag_guard.ddg_direct_from_complex_diff — pure arithmetic: the two ΔΔG routes agree and match a
    hand-computed value (incl. the concrete NR4A3/NR4A2 example from the task).

pymbar-dependent tests (independent_reduce_leg / compare_reducers) are guarded by pytest.importorskip so the
suite passes in the pymbar-free sandbox. They use a synthetic harmonic-window dataset (NOT fabricated ΔG
results — a standard MBAR unit-test construction) and assert only that the two reducers AGREE on the same data.

conftest.py puts the modalities dir on sys.path, so these import as top-level modules.
"""
import json
import os

import pytest

import abfe_xtag_guard as guard


# ============================================================ check_xtag_compatibility (pure logic)

def _matching_metas():
    """A fully-recorded, compatible cross-tag pair (dense complex + standard solvent). Everything a
    fail-closed guard needs to positively confirm is present and consistent."""
    complex_meta = {
        "leg": "complex", "n_ligand_atoms": 44, "temperature_K": 300.0,
        "ligand_inchikey": "ABCDEFGHIJKLMN-UHFFFAOYSA-N", "ligand_smiles": "CC(=O)Oc1ccccc1",
        "restraint_standard_state_dg": -8.79, "restraint_convention": "boresch-6dof-analytic-ssc",
        "thermodynamic_endpoints": [[1.0, 1.0], [0.0, 0.0]], "seed": 1, "n_windows": 16,
    }
    solvent_meta = {
        "leg": "solvent", "n_ligand_atoms": 44, "temperature_K": 300.0,
        "ligand_inchikey": "ABCDEFGHIJKLMN-UHFFFAOYSA-N", "ligand_smiles": "CC(=O)Oc1ccccc1",
        "thermodynamic_endpoints": [[1.0, 1.0], [0.0, 0.0]], "seed": 0, "n_windows": 12,
    }
    return complex_meta, solvent_meta


def test_matching_metas_compatible():
    c, s = _matching_metas()
    r = guard.check_xtag_compatibility(c, s, complex_hashes="deadbeef", solvent_hashes="deadbeef")
    assert r["compatible"] is True, r
    assert r["mismatches"] == []
    # window COUNT legitimately differs (16 dense vs 12 standard) and must NOT be a mismatch:
    assert not any("window" in m.lower() for m in r["mismatches"])
    # the safety-critical items were all positively confirmed → no critical unverifiable:
    assert not any("SAFETY-CRITICAL" in u for u in r["unverifiable"]), r["unverifiable"]


def test_mismatched_ligand_incompatible():
    c, s = _matching_metas()
    s["ligand_inchikey"] = "ZZZZZZZZZZZZZZ-UHFFFAOYSA-N"  # different ligand
    r = guard.check_xtag_compatibility(c, s)
    assert r["compatible"] is False
    assert any("ligand identity" in m for m in r["mismatches"]), r["mismatches"]


def test_mismatched_temperature_incompatible():
    c, s = _matching_metas()
    s["temperature_K"] = 310.0
    r = guard.check_xtag_compatibility(c, s)
    assert r["compatible"] is False
    assert any("temperature" in m for m in r["mismatches"]), r["mismatches"]


def test_mismatched_ligand_atom_count_incompatible():
    c, s = _matching_metas()
    s["n_ligand_atoms"] = 45
    r = guard.check_xtag_compatibility(c, s)
    assert r["compatible"] is False
    assert any("n_ligand_atoms" in m for m in r["mismatches"]), r["mismatches"]


def test_mismatched_restraint_convention_incompatible():
    """If BOTH legs record a convention key (e.g. standard_state_convention) and they DIFFER, that is a real
    convention mismatch and must be incompatible."""
    c, s = _matching_metas()
    c["standard_state_convention"] = "boresch-6dof-analytic-ssc-1M"
    s["standard_state_convention"] = "flat-bottom-different-convention"
    r = guard.check_xtag_compatibility(c, s)
    assert r["compatible"] is False
    assert any("convention" in m for m in r["mismatches"]), r["mismatches"]


def test_recorded_restraint_convention_accepted():
    c, s = _matching_metas()  # complex carries restraint_convention=boresch-6dof-analytic-ssc
    r = guard.check_xtag_compatibility(c, s)
    assert any("restraint convention recorded" in ch for ch in r["checked"]), r["checked"]


def test_missing_restraint_convention_fail_closed():
    c, s = _matching_metas()
    del c["restraint_convention"]  # convention tag absent → cannot confirm → fail closed
    r = guard.check_xtag_compatibility(c, s)
    assert r["compatible"] is False
    assert any("convention" in u and "SAFETY-CRITICAL" in u for u in r["unverifiable"]), r["unverifiable"]


def test_missing_complex_ssc_is_mismatch():
    c, s = _matching_metas()
    del c["restraint_standard_state_dg"]
    r = guard.check_xtag_compatibility(c, s)
    assert r["compatible"] is False
    assert any("restraint_standard_state_dg" in m for m in r["mismatches"]), r["mismatches"]


def test_solvent_with_restraint_is_mismatch():
    c, s = _matching_metas()
    s["restraint_standard_state_dg"] = -8.5  # solvent must NOT be restrained
    r = guard.check_xtag_compatibility(c, s)
    assert r["compatible"] is False
    assert any("solvent leg unexpectedly" in m for m in r["mismatches"]), r["mismatches"]


def test_missing_ligand_identity_fail_closed():
    c, s = _matching_metas()
    for k in ("ligand_inchikey", "ligand_smiles"):
        c.pop(k, None)
        s.pop(k, None)
    r = guard.check_xtag_compatibility(c, s)
    assert r["compatible"] is False
    assert any("ligand identity" in u and "SAFETY-CRITICAL" in u for u in r["unverifiable"]), r["unverifiable"]


def test_missing_temperature_fail_closed():
    c, s = _matching_metas()
    c.pop("temperature_K")
    s.pop("temperature_K")
    r = guard.check_xtag_compatibility(c, s)
    assert r["compatible"] is False
    assert any("temperature" in u and "SAFETY-CRITICAL" in u for u in r["unverifiable"]), r["unverifiable"]


def test_identity_can_come_from_aux():
    """A safety-critical field recorded in reference_aux.json (not meta.json) still counts as confirmed."""
    c, s = _matching_metas()
    c.pop("ligand_inchikey"); c.pop("ligand_smiles")
    s.pop("ligand_inchikey"); s.pop("ligand_smiles")
    c_aux = {"ligand_inchikey": "ABCDEFGHIJKLMN-UHFFFAOYSA-N"}
    s_aux = {"ligand_inchikey": "ABCDEFGHIJKLMN-UHFFFAOYSA-N"}
    r = guard.check_xtag_compatibility(c, s, complex_aux=c_aux, solvent_aux=s_aux)
    assert any("ligand identity" in ch for ch in r["checked"]), r["checked"]
    assert not any("ligand identity" in u for u in r["unverifiable"]), r["unverifiable"]


def test_solvent_hash_mismatch_incompatible():
    c, s = _matching_metas()
    r = guard.check_xtag_compatibility(c, s, complex_hashes={"window_00.jsonl": "aaa"},
                                       solvent_hashes={"window_00.jsonl": "bbb"})
    assert r["compatible"] is False
    assert any("solvent-leg object hashes differ" in m for m in r["mismatches"]), r["mismatches"]


def test_solvent_hash_absent_is_soft_unverifiable():
    c, s = _matching_metas()
    r = guard.check_xtag_compatibility(c, s)  # no hashes provided
    assert r["compatible"] is True  # not provided is optional → does NOT block
    assert any("object hashes not provided" in u for u in r["unverifiable"]), r["unverifiable"]


def test_return_shape():
    c, s = _matching_metas()
    r = guard.check_xtag_compatibility(c, s)
    assert set(r) == {"compatible", "mismatches", "checked", "unverifiable"}
    assert isinstance(r["compatible"], bool)
    for key in ("mismatches", "checked", "unverifiable"):
        assert isinstance(r[key], list)


# ============================================================ ddg_direct_from_complex_diff (pure arithmetic)

def test_ddg_two_routes_agree_concrete_example():
    """The exact worked example from the task: complex_dg(nr4a3)=+29.31, complex_dg(nr4a2)=+23.61,
    solvent=+23.13, ssc_nr4a3=-8.79, ssc_nr4a2=-8.56.
      ΔG_bind = solvent − complex − ssc
      ΔG_bind(nr4a3) = 23.13 − 29.31 − (−8.79) = +2.61
      ΔG_bind(nr4a2) = 23.13 − 23.61 − (−8.56) = +8.08
      ΔΔG(nr4a3 − nr4a2) = 2.61 − 8.08 = −5.47   (both routes)."""
    r = guard.ddg_direct_from_complex_diff(complex_dg_target=29.31, complex_dg_off=23.61,
                                           ssc_target=-8.79, ssc_off=-8.56, solvent_dg=23.13)
    assert r["dg_bind_target"] == pytest.approx(2.61, abs=1e-9)
    assert r["dg_bind_off"] == pytest.approx(8.08, abs=1e-9)
    # both routes equal the hand-computed value...
    assert r["ddg_via_full_abfe"] == pytest.approx(-5.47, abs=1e-9)
    assert r["ddg_direct_from_complex_diff"] == pytest.approx(-5.47, abs=1e-9)
    # ...and equal each other to the tight tolerance:
    assert r["agree"] is True
    assert r["abs_diff"] <= 1e-6


@pytest.mark.parametrize("ct,co,st,so,solv", [
    (29.31, 23.61, -8.79, -8.56, 23.13),
    (10.0, 10.0, -5.0, -5.0, 3.0),        # identical paralogues → ΔΔG must be exactly 0
    (12.5, -4.2, -9.1, -7.8, 100.0),      # solvent large → must still cancel
    (-3.0, 7.0, 0.0, -2.0, -50.0),        # negative/mixed values
])
def test_ddg_routes_always_agree(ct, co, st, so, solv):
    r = guard.ddg_direct_from_complex_diff(ct, co, st, so, solv)
    assert r["agree"] is True, r
    assert r["abs_diff"] <= 1e-6
    # independent hand form: ΔΔG = -(ct-co) - (st-so), solvent cancels
    assert r["ddg_direct_from_complex_diff"] == pytest.approx(-(ct - co) - (st - so), abs=1e-12)


def test_ddg_solvent_cancels_exactly():
    """Changing ONLY the shared solvent value leaves ΔΔG unchanged (proof of cancellation)."""
    a = guard.ddg_direct_from_complex_diff(29.31, 23.61, -8.79, -8.56, 23.13)
    b = guard.ddg_direct_from_complex_diff(29.31, 23.61, -8.79, -8.56, -999.0)
    assert a["ddg_via_full_abfe"] == pytest.approx(b["ddg_via_full_abfe"], abs=1e-9)
    assert a["ddg_direct_from_complex_diff"] == pytest.approx(b["ddg_direct_from_complex_diff"], abs=1e-12)


# ============================================================ independent reducer (needs pymbar → import-skip)

def _write_harmonic_leg(leg_dir, K=4, n=150, seed=0):
    """Write a synthetic MBAR-solvable leg: K harmonic states with unit-variance reduced potentials
    u_j(x) = 0.5*(x - mu_j)^2, samples of state k drawn from N(mu_k, 1) (its own Boltzmann distribution).
    Same width for every state → true Δf ≈ 0. This is a standard MBAR test construction, NOT a fabricated
    scientific ΔG. Includes a DUPLICATE iter line per window to exercise dedup identically in both reducers."""
    import numpy as np
    rng = np.random.default_rng(seed)
    mus = np.linspace(0.0, 3.0, K)
    os.makedirs(leg_dir, exist_ok=True)
    for k in range(K):
        xs = rng.normal(mus[k], 1.0, n)
        with open(os.path.join(leg_dir, f"window_{k:02d}.jsonl"), "w") as fh:
            for it, x in enumerate(xs):
                u = [0.5 * (x - mus[j]) ** 2 for j in range(K)]
                fh.write(json.dumps({"w": k, "iter": it, "u": u}) + "\n")
            # duplicate the last iteration with the SAME u → dedup must keep exactly one:
            last_x = xs[-1]
            u_dup = [0.5 * (last_x - mus[j]) ** 2 for j in range(K)]
            fh.write(json.dumps({"w": k, "iter": n - 1, "u": u_dup}) + "\n")


def test_independent_reduce_matches_primary(tmp_path):
    pytest.importorskip("numpy")
    pytest.importorskip("pymbar")
    import abfe_independent_reduce as ind

    leg = str(tmp_path / "leg")
    _write_harmonic_leg(leg, K=4, n=150, seed=1)
    out = ind.compare_reducers(leg, temperature_K=300.0, tol=0.05)
    # both reducers read the SAME data → must agree tightly:
    assert out["agree"] is True, out
    assert out["abs_diff"] <= 0.05
    # dedup worked: independent reducer saw exactly n unique iterations per window (not n+1):
    dg, se = ind.independent_reduce_leg(leg, temperature_K=300.0)
    assert dg == pytest.approx(out["independent"]["dg"], abs=1e-9)


def test_independent_reduce_dedups_by_iteration(tmp_path):
    pytest.importorskip("numpy")
    pytest.importorskip("pymbar")
    import abfe_independent_reduce as ind

    leg = str(tmp_path / "leg")
    _write_harmonic_leg(leg, K=3, n=80, seed=2)
    # _read_window_dedup returns exactly n unique iterations despite the injected duplicate line:
    samples = ind._read_window_dedup(os.path.join(leg, "window_00.jsonl"))
    assert len(samples) == 80


def test_independent_reduce_empty_dir_raises(tmp_path):
    pytest.importorskip("numpy")
    pytest.importorskip("pymbar")
    import abfe_independent_reduce as ind
    with pytest.raises(FileNotFoundError):
        ind.independent_reduce_leg(str(tmp_path / "nonexistent"))


def test_independent_reduce_wrong_u_length_raises(tmp_path):
    pytest.importorskip("numpy")
    pytest.importorskip("pymbar")
    import abfe_independent_reduce as ind
    leg = str(tmp_path / "leg")
    os.makedirs(leg)
    # two windows but a sample with 3 energies → corrupt/mixed leg must fail loudly
    with open(os.path.join(leg, "window_00.jsonl"), "w") as fh:
        fh.write(json.dumps({"w": 0, "iter": 0, "u": [0.0, 1.0, 2.0]}) + "\n")
    with open(os.path.join(leg, "window_01.jsonl"), "w") as fh:
        fh.write(json.dumps({"w": 1, "iter": 0, "u": [0.0, 1.0, 2.0]}) + "\n")
    with pytest.raises(ValueError):
        ind.independent_reduce_leg(leg)


# _discover_windows / _read_window_dedup are pure (no numpy/pymbar) — test them unguarded.

def test_discover_windows_pure(tmp_path):
    import abfe_independent_reduce as ind
    leg = str(tmp_path / "leg")
    os.makedirs(leg)
    for k in range(3):
        with open(os.path.join(leg, f"window_{k:02d}.jsonl"), "w") as fh:
            fh.write(json.dumps({"w": k, "iter": 0, "u": [0.0, 0.0, 0.0]}) + "\n")
    assert ind._discover_windows(leg) == 3
    assert ind._discover_windows(str(tmp_path / "none")) == 0


def test_read_window_dedup_keeps_last(tmp_path):
    import abfe_independent_reduce as ind
    p = str(tmp_path / "window_00.jsonl")
    with open(p, "w") as fh:
        fh.write(json.dumps({"w": 0, "iter": 0, "u": [1.0]}) + "\n")
        fh.write(json.dumps({"w": 0, "iter": 1, "u": [2.0]}) + "\n")
        fh.write(json.dumps({"w": 0, "iter": 0, "u": [9.0]}) + "\n")  # dup of iter 0 → last (9.0) wins
        fh.write("\n")                                                # blank line ignored
        fh.write('{"w": 0, "iter": 2, "u": [3.0]')                    # torn final line ignored
    samples = ind._read_window_dedup(p)
    assert samples == [[9.0], [2.0]]  # iter 0 -> 9.0 (last), iter 1 -> 2.0; torn iter 2 dropped
