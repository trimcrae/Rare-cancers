"""The mandated LIGAND-ONLY pose RMSD — tests written to FAIL when the measurement is absent.

Context (valB_mini, 2026-07-25). Seven defects were found in the convergence diagnostic that gates this
programme, and *every one of them reported success while measuring nothing*. Two produced wrong verdicts: a
silent `diagnostics_ok=True`, and a hard FAIL fabricated by comparing a four-chain assembly RMSD to a LIGAND
pose threshold. So the test standard for this module is deliberately inverted from the usual one:

    it is not enough for a test to pass when the metric is present;
    the test must FAIL when the metric is absent, mis-targeted, or degenerate.

Concretely, every test below is built so that a `_kabsch_rmsd` returning 0.0, returning None, or being applied to
the wrong atom subset turns the test RED. The two load-bearing ones are:

  * test_pose_rmsd_detects_a_translated_ligand — the ligand is moved 10 Å out of its pocket and the metric must
    SEE it. A stub returning 0.0 fails here.
  * test_pose_rmsd_ignores_rigid_body_motion_of_the_whole_system — the entire complex is rotated and translated
    and the metric must NOT see it. This is defect #7's exact regression: the old whole-system/whole-solute RMSD
    reported ~79 Å / ~15 Å for precisely this non-event.

Pure stdlib + numpy; no openmm, no .nc, no GPU. The fake System exercises the REAL production functions
(`_ligand_atoms`, `_ligand_pose_block`, `classify_components`), not a reimplementation.
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ternary_fep_convergence as tfc  # noqa: E402

np = pytest.importorskip("numpy")


# ------------------------------------------------------------------ synthetic assembly builders

def _build_assembly(n_chains=4, chain_size=1500, n_waters=300, n_ions=12, ligand_size=120,
                    n_ligands=1, hydrogens_as_constraints=True):
    """A solvated ternary-like system: protein chains, waters, monatomic ions and `n_ligands` PROTAC-sized
    molecules. Returns (n_atoms, bond_edges, constraint_edges, masses, ligand_index_lists).

    Every second ligand/protein atom is a 'hydrogen' (mass 1.008) whose only connection is a CONSTRAINT, which
    is how OpenMM represents X–H under constraints=HBonds. That is not decoration: it is the reason
    `_system_edges` must read constraints, and `test_constraints_are_load_bearing` proves the omission breaks
    the identification rather than merely degrading it."""
    bonds, cons, masses, ligands = [], [], [], []
    nxt = 0

    def _chain(size, out_list=None):
        nonlocal nxt
        start = nxt
        idx = list(range(start, start + size))
        heavy = idx[0::2]
        for a, b in zip(heavy, heavy[1:]):
            bonds.append((a, b))
        for h in idx[1::2]:                      # each H hangs off the preceding heavy atom
            (cons if hydrogens_as_constraints else bonds).append((h - 1, h))
        masses.extend([12.011 if (i - start) % 2 == 0 else 1.008 for i in idx])
        nxt += size
        if out_list is not None:
            out_list.append(idx)
        return idx

    for _ in range(n_chains):
        _chain(chain_size)
    for _ in range(n_ligands):
        _chain(ligand_size, ligands)
    for _ in range(n_waters):                    # rigid water: O–H and H–H are all constraints
        o = nxt
        cons.extend([(o, o + 1), (o, o + 2), (o + 1, o + 2)])
        masses.extend([15.999, 1.008, 1.008])
        nxt += 3
    for _ in range(n_ions):
        masses.append(22.99)
        nxt += 1
    return nxt, bonds, cons, masses, ligands


class _FakeQuantity:
    def __init__(self, value, unit="dalton"):
        self._v, self.unit = value, unit

    def value_in_unit(self, _u):
        return self._v


class _FakeForce:
    def __init__(self, bonds):
        self._b = bonds

    def getNumBonds(self):
        return len(self._b)

    def getBondParameters(self, k):
        return (self._b[k][0], self._b[k][1], 0.15, 1000.0)


class _FakeSystem:
    def __init__(self, n, bonds, cons, masses):
        self._n, self._c, self._m = n, cons, masses
        half = len(bonds) // 2
        # two bonded forces, mirroring HarmonicBondForce + the softcore CustomBondForce OpenFE's
        # HybridTopologyFactory moves the alchemical region into
        self._forces = [_FakeForce(bonds[:half]), _FakeForce(bonds[half:])]

    def getNumParticles(self):
        return self._n

    def getNumForces(self):
        return len(self._forces)

    def getForce(self, k):
        return self._forces[k]

    def getNumConstraints(self):
        return len(self._c)

    # ONLY the name openmm.System actually exposes. The first version of this fake implemented `getConstraint`,
    # matching a typo in the production code, so the whole suite went green while the real analysis raised
    # AttributeError on GCS run 30167699679. A fake that mirrors the code instead of the API tests nothing.
    def getConstraintParameters(self, k):
        return (self._c[k][0], self._c[k][1], 0.1)

    def getParticleMass(self, i):
        return _FakeQuantity(self._m[i])


class _FakeState:
    def __init__(self, system=None, positions=None, box=None):
        self.system = system
        self.positions = _FakeQuantity(positions, unit="nanometer") if positions is not None else None
        self.box_vectors = box


class _FakeReporter:
    """Only the surface `_ligand_atoms` / `_ligand_pose_block` actually touch."""

    def __init__(self, system, subset, frames, box=None):
        self.analysis_particle_indices = list(subset)
        self._sys, self._frames, self._box = system, frames, box

    def read_end_thermodynamic_states(self):
        return [_FakeState(system=self._sys), _FakeState(system=self._sys)]

    def read_sampler_states(self, iteration=0, analysis_particles_only=False):
        xyz = self._frames[iteration]
        return [_FakeState(positions=x, box=self._box) for x in xyz]


# ------------------------------------------------------------------ identification

def test_molecules_from_edges_partitions_exactly():
    comps = tfc.molecules_from_edges(7, [(0, 1), (1, 2), (4, 5)])
    assert sorted(sorted(c) for c in comps) == [[0, 1, 2], [3], [4, 5], [6]]


def test_identifies_the_one_ligand_sized_molecule():
    n, bonds, cons, masses, ligs = _build_assembly()
    comps = tfc.molecules_from_edges(n, bonds + cons)
    subset = [i for i in range(n) if masses[i] != 15.999][:0] or list(range(n))
    info = tfc.classify_components(comps, subset)
    assert info["ligand"] is not None, info["status"]
    assert sorted(info["ligand"]) == sorted(ligs[0])
    assert info["n_ligand_sized_candidates"] == 1
    assert info["protein_components"] == [1500] * 4


def test_refuses_when_there_is_no_ligand():
    """The measurement-absent case. A classifier that 'always finds something' passes the happy-path test above
    and is still worthless; this is the test it cannot pass."""
    n, bonds, cons, masses, _ = _build_assembly(n_ligands=0)
    info = tfc.classify_components(tfc.molecules_from_edges(n, bonds + cons), list(range(n)))
    assert info["ligand"] is None
    assert info["n_ligand_sized_candidates"] == 0
    assert "refuses rather than pick" in info["status"]


def test_refuses_when_two_ligand_sized_molecules_are_present():
    n, bonds, cons, masses, ligs = _build_assembly(n_ligands=2)
    info = tfc.classify_components(tfc.molecules_from_edges(n, bonds + cons), list(range(n)))
    assert info["ligand"] is None and info["n_ligand_sized_candidates"] == 2


def test_refuses_when_the_ligand_is_not_retained_in_the_analysis_subset():
    """If the ligand's atoms were not stored, its positions do not exist — and reporting a number anyway would be
    the exact class of defect this module keeps producing."""
    n, bonds, cons, masses, ligs = _build_assembly()
    subset = [i for i in range(n) if i not in set(ligs[0])]
    info = tfc.classify_components(tfc.molecules_from_edges(n, bonds + cons), subset)
    assert info["ligand"] is None
    assert info["n_candidates_rejected_not_retained_in_subset"] == 1


def test_constraints_are_load_bearing():
    """Under constraints=HBonds the X–H bonds exist ONLY as constraints. Dropping them must BREAK the
    identification — if this test can pass with constraints omitted, `_system_edges` reading them is untested."""
    n, bonds, cons, masses, ligs = _build_assembly()
    with_cons = tfc.classify_components(tfc.molecules_from_edges(n, bonds + cons), list(range(n)))
    without = tfc.classify_components(tfc.molecules_from_edges(n, bonds), list(range(n)))
    assert with_cons["ligand"] is not None
    assert without["ligand"] is None or sorted(without["ligand"]) != sorted(ligs[0]), (
        "identification survived dropping the constraint edges — the constraint path is not exercised")


def test_system_edges_uses_the_documented_openmm_constraint_accessor():
    """A System exposing ONLY openmm's real accessor must work. If the production code reaches for any other
    name, this raises — which is what happened for real on GH run 30167699679 while the suite was green."""
    n, bonds, cons, masses, _ = _build_assembly(n_chains=1, chain_size=1200, n_waters=5, n_ions=1)
    sysm = _FakeSystem(n, bonds, cons, masses)
    assert not hasattr(sysm, "getConstraint"), "the fake must not offer a name openmm does not have"
    edges, prov = tfc._system_edges(sysm)
    assert prov["constraints"] == len(cons)


def test_system_edges_reads_every_bonded_force_and_the_constraints():
    n, bonds, cons, masses, _ = _build_assembly()
    edges, prov = tfc._system_edges(_FakeSystem(n, bonds, cons, masses))
    assert prov["constraints"] == len(cons)
    assert sum(v for k, v in prov.items() if k != "constraints") == len(bonds)
    assert len(edges) == len(bonds) + len(cons)


def test_ligand_atoms_end_to_end_through_the_real_function():
    n, bonds, cons, masses, ligs = _build_assembly()
    rep = _FakeReporter(_FakeSystem(n, bonds, cons, masses), list(range(n)), {})
    got = tfc._ligand_atoms(rep)
    assert got["ligand_atom_indices"] is not None, got.get("status")
    assert sorted(got["ligand_atom_indices"]) == sorted(ligs[0])
    assert got["n_ligand_heavy_atoms"] == len(ligs[0]) // 2      # every second atom is an H
    assert got["provenance"] == "read_end_thermodynamic_states"
    assert got["protein_chain_sizes"] == [1500] * 4


@pytest.mark.parametrize("available", ["openmm", "simtk", None])
def test_mass_units_are_resolved_once_per_identification(monkeypatch, available):
    """Preserve modern/legacy/fake quantity conversion without failed imports per atom."""
    import builtins
    from types import SimpleNamespace

    real_import = builtins.__import__
    attempts = []
    unit = object()

    def import_unit(name, *args, **kwargs):
        if name in ("openmm", "simtk"):
            attempts.append(name)
            if name == available:
                return SimpleNamespace(unit=SimpleNamespace(dalton=unit))
            raise ModuleNotFoundError(name)
        return real_import(name, *args, **kwargs)

    def value_in_unit(self, got):
        assert got is (unit if available else None)
        return self._v

    monkeypatch.setattr(builtins, "__import__", import_unit)
    monkeypatch.setattr(_FakeQuantity, "value_in_unit", value_in_unit)
    n, bonds, cons, masses, ligs = _build_assembly(n_chains=1, chain_size=1200, n_waters=0)
    reporter = _FakeReporter(_FakeSystem(n, bonds, cons, masses), list(range(n)), {})
    expected_imports = ["openmm"] if available == "openmm" else ["openmm", "simtk"]
    for repeat in (1, 2):
        got = tfc._ligand_atoms(reporter)
        assert sorted(got["ligand_atom_indices"]) == sorted(ligs[0])
        assert got["n_ligand_heavy_atoms"] == len(ligs[0]) // 2
        assert attempts == expected_imports * repeat
    assert tfc._mass_da(12.011) == 12.011
    assert attempts == expected_imports * 2  # Plain numbers need no optional dependency.


# ------------------------------------------------------------------ the RMSD itself

def _coords(n, seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(scale=2.0, size=(n, 3))


def test_pose_rmsd_detects_a_translated_ligand():
    """THE load-bearing test. Move the ligand 1.0 nm (10 Å) out of the pocket, leave the protein alone, and the
    receptor-superposed pose RMSD must report ~10 Å — above LIG_RMSD_MAX_A. A metric that measures nothing
    (returns 0.0, or None, or is applied to the protein instead of the ligand) FAILS here."""
    A = _coords(300)
    prot, lig = list(range(0, 250)), list(range(250, 300))
    B = A.copy()
    B[lig] += np.array([1.0, 0.0, 0.0])
    r = tfc._kabsch_rmsd(A, B, prot, lig)
    assert r == pytest.approx(10.0, abs=0.2)
    assert r > tfc.LIG_RMSD_MAX_A
    assert tfc._kabsch_rmsd(A, A.copy(), prot, lig) == pytest.approx(0.0, abs=1e-8)


def test_pose_rmsd_ignores_rigid_body_motion_of_the_whole_system():
    """Defect #7's regression. Rotate and translate the ENTIRE complex — nothing has changed physically. The old
    unaligned whole-system RMSD read ~79 Å for exactly this; the pose RMSD must read ~0."""
    A = _coords(300, seed=1)
    prot, lig = list(range(0, 250)), list(range(250, 300))
    th = 0.9
    R = np.array([[math.cos(th), -math.sin(th), 0.0], [math.sin(th), math.cos(th), 0.0], [0.0, 0.0, 1.0]])
    B = A @ R.T + np.array([5.0, -3.0, 2.0])
    assert tfc._kabsch_rmsd(A, B, prot, lig) == pytest.approx(0.0, abs=1e-6)
    naive = float(np.sqrt(((B[lig] - A[lig]) ** 2).sum(axis=1).mean()) * 10.0)
    assert naive > 20.0, "the naive unaligned RMSD must be large, else this test proves nothing"


def test_pose_rmsd_is_not_the_internal_rmsd():
    """Superposing on the LIGAND hides an escape; superposing on the PROTEIN reveals it. If these two were the
    same number the receptor-frame fit would be doing no work."""
    A = _coords(300, seed=2)
    prot, lig = list(range(0, 250)), list(range(250, 300))
    B = A.copy()
    B[lig] += np.array([0.8, 0.0, 0.0])           # rigid ligand translation: internal change is exactly zero
    assert tfc._kabsch_rmsd(A, B, lig, lig) == pytest.approx(0.0, abs=1e-8)
    assert tfc._kabsch_rmsd(A, B, prot, lig) == pytest.approx(8.0, abs=0.2)


def test_min_image_undoes_a_lattice_translation_on_a_triclinic_cell():
    """The valB box is a reduced-form truncated octahedron, rows [12.63,0,0] [0,12.63,0] [6.31,6.31,8.93] nm —
    componentwise wrapping is invalid there. A wrapped atom must come back to its true small displacement."""
    M = np.array([[12.63, 0.0, 0.0], [0.0, 12.63, 0.0], [6.31, 6.31, 8.93]])
    A = _coords(200, seed=3)
    true_d = np.random.default_rng(4).normal(scale=0.05, size=(200, 3))
    shifts = np.random.default_rng(5).integers(-1, 2, size=(200, 3)).astype(float)
    B = A + true_d + shifts @ M
    Bu, applied = tfc._min_image(A, B, M)
    assert applied
    assert np.abs((Bu - A) - true_d).max() < 1e-9


def test_min_image_refuses_a_degenerate_cell():
    A = _coords(10, seed=6)
    B = A + 1.0
    out, applied = tfc._min_image(A, B, None)
    assert applied is False and np.allclose(out, B)


# ------------------------------------------------------------------ the whole block, end to end

def _block_reporter(displace_ligand_nm=0.0, seed=7, n_replicas=3):
    n, bonds, cons, masses, ligs = _build_assembly(n_chains=2, chain_size=1200, n_waters=50, n_ions=4,
                                                   ligand_size=100)
    subset = [i for i in range(n) if masses[i] != 15.999 and masses[i] != 22.99]
    sysm = _FakeSystem(n, bonds, cons, masses)
    base = _coords(len(subset), seed=seed)
    lig_rows = [subset.index(i) for i in ligs[0]]
    f0 = [base.copy() for _ in range(n_replicas)]
    fN = []
    for k in range(n_replicas):
        x = base.copy()
        x[lig_rows] += np.array([displace_ligand_nm, 0.0, 0.0])
        fN.append(x)
    return _FakeReporter(sysm, subset, {0: f0, 10: fN}), ligs[0]


def test_ligand_pose_block_reports_a_stable_ligand_as_stable():
    rep, _ = _block_reporter(displace_ligand_nm=0.0)
    out = tfc._ligand_pose_block(rep, 0, 10)
    assert out["ligand_rmsd_A"] is not None, out.get("status")
    assert out["ligand_rmsd_A"] == pytest.approx(0.0, abs=1e-6)
    assert out["n_replicas"] == 3
    assert out["ligand_rmsd_A"] <= tfc.LIG_RMSD_MAX_A


def test_ligand_pose_block_reports_an_escaped_ligand_as_escaped():
    """End-to-end through the production function: identification -> row mapping -> per-replica pose RMSD ->
    the flagged value. If ANY link in that chain silently measures nothing, this returns ~0 and the test fails."""
    rep, _ = _block_reporter(displace_ligand_nm=1.2)
    out = tfc._ligand_pose_block(rep, 0, 10)
    assert out["ligand_rmsd_A"] == pytest.approx(12.0, abs=0.3)
    assert out["ligand_rmsd_A"] > tfc.LIG_RMSD_MAX_A
    assert out["internal_rmsd_max_A"] == pytest.approx(0.0, abs=1e-6)   # rigid translation: no internal change


def test_ligand_pose_block_leaves_the_flag_unmeasured_when_the_ligand_cannot_be_identified():
    n, bonds, cons, masses, _ = _build_assembly(n_chains=2, chain_size=1200, n_waters=20, n_ions=2, n_ligands=0)
    subset = list(range(n))
    rep = _FakeReporter(_FakeSystem(n, bonds, cons, masses), subset, {0: [_coords(n, 8)], 10: [_coords(n, 9)]})
    out = tfc._ligand_pose_block(rep, 0, 10)
    assert out["ligand_rmsd_A"] is None
    assert "ligand NOT identified" in out["status"]


def test_hydrogen_mass_is_measured_not_assumed_under_HMR():
    """The real ternary leg runs hydrogen-mass repartitioning: its ligand's masses are {3:51, 6:5, 8:6, 10:18,
    12:18, 14:8, 16:3, 32:1}. A fixed 2.5 Da 'heavy atom' cutoff calls all 51 hydrogens heavy — which is what
    shipped, and what made the first real run report 110 heavy atoms for a 59-heavy-atom molecule."""
    # 8 heavy atoms in a chain, each carrying one HMR'd hydrogen
    heavy_ids = list(range(0, 16, 2))
    edges = [(a, b) for a, b in zip(heavy_ids, heavy_ids[1:])] + [(h, h + 1) for h in heavy_ids]
    masses = []
    for i in range(16):
        masses.append(9.995 if i % 2 == 0 else 3.024)      # CH carbon under HMR / HMR'd hydrogen
    h, note = tfc.hydrogen_mass_da(list(range(16)), masses, edges)
    assert h == pytest.approx(3.0, abs=0.05), note
    assert "repartition" in note
    cut = h * tfc.HEAVY_MASS_MARGIN
    assert len([i for i in range(16) if masses[i] > cut]) == 8, "the HMR'd hydrogens must not count as heavy"


def test_hydrogen_mass_refuses_when_the_modal_terminal_atom_is_not_the_lightest():
    masses = [12.0, 79.9, 79.9, 79.9]                      # three terminal bromines, no hydrogens
    h, note = tfc.hydrogen_mass_da([0, 1, 2, 3], masses, [(0, 1), (0, 2), (0, 3)])
    assert h is None and "refusing" in note


def test_solvent_leg_ligand_check_is_not_applicable_rather_than_failed():
    """A free PROTAC in bulk water explores conformations — that is physics, not pose collapse. Flagging it
    against LIG_RMSD_MAX_A returned technical_failure=True on the real r0 solvent leg, which via the reducer
    would have handed valB_mini a hard FAIL. The check must be SKIPPED there, not failed and not left unmeasured."""
    n, bonds, cons, masses, ligs = _build_assembly(n_chains=0, chain_size=0, n_waters=200, n_ions=4,
                                                   ligand_size=100)
    subset = list(ligs[0])
    sysm = _FakeSystem(n, bonds, cons, masses)
    base = _coords(len(subset), seed=11)
    moved = base + np.random.default_rng(12).normal(scale=0.6, size=base.shape)   # a big conformational change
    rep = _FakeReporter(sysm, subset, {0: [base], 10: [moved]})
    out = tfc._ligand_pose_block(rep, 0, 10)
    assert out.get("check_applicable") is False, out.get("status")
    assert out["ligand_rmsd_A"] is None, "a solvent leg must not produce a value judged against a pose threshold"
    assert out["internal_rmsd_max_A"] is not None, "the internal RMSD is still reported, as information"


def test_ligand_pose_block_reports_a_missing_system_rather_than_a_number():
    class _NoStates:
        analysis_particle_indices = [0, 1, 2]

        def read_sampler_states(self, iteration=0, analysis_particles_only=False):
            return []

    out = tfc._ligand_pose_block(_NoStates(), 0, 10)
    assert out["ligand_rmsd_A"] is None and "could not deserialize" in out["status"]
