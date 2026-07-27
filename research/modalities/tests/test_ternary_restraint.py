#!/usr/bin/env python3
"""The binary-arm pocket restraint: correct physics, correct atoms, and it REFUSES rather than guesses.

WHY THIS EXISTS. The binary leg's ligand left its pocket in 8 of 12 replicas (max 16.6 Å) in both cycles, so
ΔG_binary is not a free energy of the intended bound state and ΔΔG_coop = ΔG_ternary − ΔG_binary is not a
measurement of cooperativity (audit §L.3a–L.3d). The remedy §L.3c names is a restraint on the receptor-contacting
moiety. A restraint is a change to the Hamiltonian, so it earns more scrutiny than most fixes: applied to the
wrong atoms it holds the ligand somewhere wrong while every step still reports success — this lane's signature
failure — and applied too tightly it biases the very number it is meant to rescue.

WHAT IS PINNED, in both directions throughout:
  * flat inside the well (so a clean ternary-like leg is UNPERTURBED), quadratic outside, continuous at the edge
  * the atoms chosen are the CONTACT moiety and its receptor anchors, from the STARTING frame
  * a solvent leg (no receptor) is REFUSED — restraining one would be a physics error, not a near miss
  * an unidentifiable ligand is REFUSED rather than guessed
  * disabled by default, so every existing lane is untouched until a leg opts in

Pure stdlib + a stub System. No OpenMM, no MD, runs in the dev sandbox.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import ternary_restraint as tr


# ----------------------------------------------------------------- a stub OpenMM System (bond graph + masses)
class _StubSystem:
    """Only the four methods the identification path touches: particle count, masses, force count, and the
    HarmonicBondForce that _system_edges reads connectivity from."""

    def __init__(self, masses, bonds):
        self._m, self._b = masses, bonds

    def getNumParticles(self):
        return len(self._m)

    def getParticleMass(self, i):
        return self._m[i]

    def getNumForces(self):
        return 1

    def getForce(self, i):
        return _StubBondForce(self._b)

    # _system_edges reads DISTANCE CONSTRAINTS as well as bonded forces — that is where X-H bonds live under
    # constraints=HBonds, which this lane uses. A stub without them is not a stand-in for the real System, and
    # omitting them here initially made every selection test error out. Only the DOCUMENTED accessor name is
    # implemented: ternary_fep_convergence carries a note about a fake that implemented `getConstraint` (which
    # does not exist on openmm.System) and so agreed with the code instead of with reality.
    def getNumConstraints(self):
        return 0

    def getConstraintParameters(self, i):
        raise IndexError(i)


class _StubBondForce:
    def __init__(self, bonds):
        self._b = bonds

    def getNumBonds(self):
        return len(self._b)

    def getBondParameters(self, i):
        a, b = self._b[i]
        return [a, b, 0.1, 1000.0]


def _chain(start, n, mass, bonds, masses, with_h=True):
    """A connected run of `n` heavy atoms from index `start`, each carrying one hydrogen so the hydrogen-mass
    measurement has something to find."""
    idx = []
    i = start
    for k in range(n):
        masses.append(mass)
        heavy = i
        idx.append(heavy)
        i += 1
        if with_h:
            masses.append(1.008)
            bonds.append((heavy, i))
            i += 1
        if k:
            bonds.append((idx[k - 1], heavy))
    return idx, i


def _build(n_protein_heavy=1200, ligand_in_pocket=True, with_protein=True):
    """A receptor slab plus a 60-heavy-atom 'PROTAC': half in contact with the receptor, half out in solvent."""
    masses, bonds = [], []
    i = 0
    prot = []
    if with_protein:
        prot, i = _chain(i, n_protein_heavy, 12.011, bonds, masses)
    lig, i = _chain(i, 60, 12.011, bonds, masses)
    n = len(masses)

    xyz = [[0.0, 0.0, 0.0] for _ in range(n)]
    for k, a in enumerate(prot):                       # receptor: a flat slab at z = 0
        xyz[a] = [0.05 * (k % 40), 0.05 * (k // 40 % 40), 0.0]
        if a + 1 < n:
            xyz[a + 1] = list(xyz[a])
    # bound warhead: first 30 heavy atoms 0.3 nm above the slab (inside the 0.45 nm contact shell)
    # distal end: last 30 heavy atoms 3 nm away, never in contact
    for k, a in enumerate(lig):
        z = 0.30 if k < 30 else 3.0
        base = [0.05 * (k % 30), 0.05, z]
        if not ligand_in_pocket:
            base[2] += 5.0
        xyz[a] = base
        if a + 1 < n:
            xyz[a + 1] = list(base)
    return _StubSystem(masses, bonds), xyz, prot, lig


# ----------------------------------------------------------------------------------- the functional form
def test_flat_inside_the_well_is_exactly_zero():
    """The whole design rests on this. The ternary arm is measured clean (12/12 and 11/12 STABLE), so the
    restraint must be a literal no-op on a leg that behaves like it — not 'small', zero."""
    for r in (0.0, 0.5, 1.0, 1.2999):
        assert tr.flat_bottom_energy(r, 1.3) == 0.0, f"restraint must be identically zero at r={r} inside the well"


def test_quadratic_outside_and_continuous_at_the_edge():
    r_flat, k = 1.3, tr.DEFAULT_K
    assert tr.flat_bottom_energy(r_flat, r_flat, k) == 0.0, "must be continuous AT the edge, not stepped"
    assert abs(tr.flat_bottom_energy(r_flat + 0.1, r_flat, k) - 0.5 * k * 0.01) < 1e-9
    assert abs(tr.flat_bottom_energy(r_flat + 0.2, r_flat, k) - 0.5 * k * 0.04) < 1e-9
    # and it must actually grow — a flat-everywhere "restraint" would pass the test above and do nothing
    assert tr.flat_bottom_energy(r_flat + 0.2, r_flat, k) > tr.flat_bottom_energy(r_flat + 0.1, r_flat, k) > 0


def test_the_measured_escape_is_deep_in_the_restrained_zone_and_the_clean_arm_is_not():
    """Calibration against the two real measurements, so the constants are not free parameters.

    Binary arm departed to 16.6 Å; the ternary arm's median contact displacement is 1.64 Å with the pose-escape
    gate at 4.0 Å. The well (0.30 nm = 3.0 Å) must contain the second and exclude the first.
    """
    tol = tr.DEFAULT_TOLERANCE_NM
    assert tol * 10 > 1.64, "the well must contain the clean ternary arm's normal fluctuation (1.64 Å median)"
    assert tol * 10 <= 4.0, "the well must not extend past the 4.0 Å pose-escape threshold the gate flags on"
    r0 = 0.5
    assert tr.flat_bottom_energy(r0 + 0.164, r0 + tol) == 0.0, "a clean-arm-sized displacement must cost nothing"
    assert tr.flat_bottom_energy(r0 + 1.66, r0 + tol) > 100.0, (
        "the measured 16.6 Å departure must be strongly opposed, else the restraint does not address §L.3c")


# ------------------------------------------------------------------------------------- atom selection
def test_selects_the_contact_moiety_not_the_whole_ligand():
    system, xyz, prot, lig = _build()
    sel = tr.select_restraint_groups(system, xyz)
    assert sel["ok"], sel.get("reason")
    assert sel["n_contact_ligand_atoms"] == 30, (
        "exactly the 30 bound-warhead heavy atoms should be in contact, got %d. Picking up the distal warhead "
        "would tether the free end that is in solvent BY CONSTRUCTION in a binary complex."
        % sel["n_contact_ligand_atoms"])
    assert set(sel["ligand_group"]).issubset(set(lig))
    assert set(sel["receptor_group"]).issubset(set(prot))
    assert sel["n_anchor_receptor_atoms"] >= tr.MIN_CONTACT_ATOMS


def test_a_SOLVENT_leg_is_refused():
    """A solvent leg has no receptor. Restraining a free ligand to nothing is a physics error, and the ABFE
    guard's own rule (`abfe_xtag_guard`: the solvent leg must NOT be restrained) says so independently."""
    system, xyz, _, _ = _build(with_protein=False)
    sel = tr.select_restraint_groups(system, xyz)
    assert not sel["ok"]
    assert "PROTEIN_MIN_ATOMS" in sel["reason"] or "receptor" in sel["reason"], sel["reason"]


def test_a_ligand_already_out_of_the_pocket_is_refused_not_tethered_where_it_drifted():
    """If the starting frame has no contact, that is a FINDING. Building the restraint anyway would hold the
    ligand at whatever wrong place it started, and the leg would look healthy while measuring the wrong state."""
    system, xyz, _, _ = _build(ligand_in_pocket=False)
    sel = tr.select_restraint_groups(system, xyz)
    assert not sel["ok"], "no contact in the starting frame must refuse"
    assert "too few contact atoms" in sel["reason"], sel["reason"]


def test_r0_is_measured_from_the_given_frame():
    system, xyz, _, _ = _build()
    sel = tr.select_restraint_groups(system, xyz)
    assert 0.0 < sel["r0_nm"] < 2.0, sel["r0_nm"]


# ------------------------------------------------------------------------------------- the on/off contract
def test_disabled_by_default_is_a_true_no_op():
    os.environ.pop("RBFE_RESTRAIN", None)
    system, xyz, _, _ = _build()
    rep = tr.add_flat_bottom_restraint(system, xyz, log=lambda *a: None)
    assert rep["applied"] is False and rep["enabled"] is False, (
        "unset RBFE_RESTRAIN must add nothing — every existing lane stays byte-identical until a leg opts in")
    assert "selection" not in rep, "a disabled restraint must not even run the selection"


def test_env_flag_parsing():
    for v, want in (("1", True), ("true", True), ("YES", True), ("on", True),
                    ("0", False), ("", False), ("no", False)):
        os.environ["RBFE_RESTRAIN"] = v
        assert tr._enabled() is want, f"RBFE_RESTRAIN={v!r} should be {want}"
    os.environ.pop("RBFE_RESTRAIN", None)


def test_enabled_but_unselectable_declines_instead_of_raising():
    """A selection failure must not kill a leg that is already running — it reports and runs unrestrained, and
    the convergence gate still catches an escape. Losing 44 h of GPU to an exception here would be the worse
    outcome of the two."""
    os.environ["RBFE_RESTRAIN"] = "1"
    try:
        system, xyz, _, _ = _build(with_protein=False)
        msgs = []
        rep = tr.add_flat_bottom_restraint(system, xyz, log=msgs.append)
        assert rep["applied"] is False and rep["enabled"] is True
        assert rep.get("reason"), "a decline must say why"
        assert any("NOT APPLIED" in m for m in msgs), msgs
    finally:
        os.environ.pop("RBFE_RESTRAIN", None)


# ------------------------------------------------------------------------------- the standard-state claim
def test_no_standard_state_correction_is_claimed_or_required():
    """The load-bearing scientific claim. This is RBFE with a never-decoupled ligand and a λ-independent
    restraint, so the restraint term is identical at both endpoints and cancels from ΔG(A→B). Importing ABFE's
    analytic release term would be WRONG here, not conservative — and emitting the key would additionally trip
    abfe_xtag_guard, which requires it only on an ABFE complex leg."""
    os.environ.pop("RBFE_RESTRAIN", None)
    rep = tr.add_flat_bottom_restraint(*_build()[:2], log=lambda *a: None)
    assert rep["standard_state_correction_required"] is False
    assert rep["lambda_dependent"] is False, (
        "if this ever becomes λ-dependent the cancellation argument collapses and a correction IS required")
    assert "restraint_standard_state_dg" not in rep, (
        "must not emit the ABFE standard-state key — this lane has no decoupled endpoint")


def test_the_module_never_imports_the_abfe_correction():
    """AST, not grep. The first cut of this searched the source text for "boresch" and fired on the module
    docstring's own explanation of why the term does NOT apply — the identical false positive the co-fold
    regression check hit the same day. Walk the tree: no import of the ABFE module, no call to anything named
    after the correction. The docstring is free to discuss it; the code is not free to use it."""
    import ast
    import inspect
    tree = ast.parse(inspect.getsource(tr))
    imported = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imported += [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module:
            imported.append(n.module)
    assert not [m for m in imported if "abfe" in m.lower()], (
        "the RBFE restraint must not import the ABFE lane: %r" % imported)
    names = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    names |= {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    bad = {n for n in names if "boresch" in n.lower() or "standard_state_correction" == n.lower()}
    assert not bad, ("the Boresch standard-state correction must not be applied in an RBFE lane (no decoupled "
                     "endpoint exists here): %r" % bad)


# The runner stays LAST: tests defined below a `__main__` block are silently skipped, which has already happened
# twice in this directory. Add new test_* functions ABOVE this line.
if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except AssertionError as e:
                print("FAIL", name, "\n      ", e)
                fails += 1
            except Exception as e:  # noqa: BLE001
                print("ERROR", name, "\n      ", type(e).__name__, e)
                fails += 1
    print("\n%d failure(s)" % fails)
    sys.exit(1 if fails else 0)
