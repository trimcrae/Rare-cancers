#!/usr/bin/env python3
"""Flat-bottom pocket restraint for the ternary lane's BINARY arm.

WHY THIS EXISTS. ΔΔG_coop = ΔG_ternary − ΔG_binary. In the BINARY leg the PROTAC has only ONE warhead bound —
the second protein is absent by construction — so the linker and distal warhead are in solvent and the bound
warhead is far less confined than in the ternary complex. Measured consequence, in BOTH cycles (2 fs and 4 fs,
different GPUs and providers): the ligand left its pocket in 8 of 12 replicas, contact-moiety RMSD max 16.6 Å /
median 6.99 Å, against the ternary arm's 2.77 / 1.64 in the same cycle (audit §L.3a–L.3d). Unbound configurations
then enter MBAR at physical λ, so ΔG_binary is not a free energy of the intended bound state and the
cooperativity number built on it is not a measurement of cooperativity.

WHAT §L.3c ESTABLISHED ABOUT THE MECHANISM, because it determines the shape of the fix:
  * INITIATION is λ-dependent — 7 of 8 departures begin in the alchemical interior, skewed to upper-λ where the
    softcore region is largest. The alchemical softening is what opens the door.
  * PERSISTENCE is λ-INdependent — once departed, the displaced configuration survives everywhere on the ladder;
    the physical Hamiltonian does not close the door again.
So the escape is alchemically FACILITATED but not alchemically CONFINED, which is why this is treated as a
protocol problem with a protocol remedy, and NOT as evidence that the binary complex model is wrong. §L.3c is
explicit that the data does not support the latter and it is not claimed here.

═══ DESIGN, and the three choices that make it defensible ═══

1 · FLAT-BOTTOM, NOT HARMONIC. The restraint is exactly zero inside a tolerance well around the starting
    centroid separation and turns on only outside it. That matters for comparability: the ternary arm is
    measured CLEAN in both directions (12/12 STABLE fwd, 11/12 rev), so a well wide enough to contain normal
    bound fluctuation is one the ternary leg would essentially never touch. The same restraint definition can
    therefore be applied to both arms of a cycle without changing what the ternary arm samples — a plain
    harmonic tether would bias every frame of both.
    ⚠ WHETHER IT *SHOULD* BE APPLIED TO BOTH ARMS IS A SEPARATE QUESTION, AND IT IS DECIDED ELSEWHERE.
    "The same restraint definition CAN sit on both arms" is a property of the flat bottom, not a
    recommendation. The standing ruling is that **only the BINARY arm is re-run restrained**, and its
    reasoning — including the rev leg's one 4.737 Å excursion, which does exceed this well and is
    nevertheless the wrong thing to restrain because it initiates at a *physical* endpoint — lives in
    `ternary-lane-guard-audit-2026-07-25.md` §L.3f. ONE HOME; do not restate the numbers here.

2 · λ-INDEPENDENT, ON MAPPED CORE ATOMS → IT CANCELS, SO THERE IS NO STANDARD-STATE CORRECTION.
    This is an RBFE, not an ABFE. The ligand is NEVER decoupled from the receptor here — both endpoints have a
    fully-interacting ligand in the pocket, and only the perturbed atoms change. A restraint that is identical
    at both endpoints and never scaled by λ contributes the SAME term to each, so it cancels exactly from
    ΔG(A→B). The Boresch-style analytic standard-state term in `nr4a3_abfe.boresch_standard_state_correction`
    exists because ABFE's decoupled endpoint has a non-interacting ligand confined to a restrained volume that
    must be released to 1 M — there is no such endpoint in this calculation, so importing that correction here
    would be wrong, not conservative. `restraint_standard_state_dg` is therefore deliberately NOT emitted, and
    `abfe_xtag_guard` (which REQUIRES that key on an ABFE complex leg) does not govern this lane.
    ⚠ The cancellation argument depends on the restrained atoms being present in BOTH endpoints. The restraint
    is built only from atoms in the ligand's CONTACT MOIETY; `unmapped_contact_atoms` records any that are
    alchemically perturbed so the assumption is checked rather than assumed (see `restraint_report`).

3 · THE REFERENCE IS THE STARTING FRAME. Contacts are derived from the frame the leg STARTS from, never from a
    later one — the same discipline `_contact_ligand_rows` is held to in the convergence analysis, and for the
    same reason: a ligand that has already escaped drops out of a later frame's contact set and erases its own
    evidence. Here it would be worse than erasure — the restraint would be built around wherever the ligand had
    drifted to, and would then hold it THERE.

ATOM IDENTIFICATION IS NOT REIMPLEMENTED. It reuses `ternary_fep_convergence`'s System-bond-graph route
(`molecules_from_edges` / `classify_components`), which needs only an OpenMM System — exactly what the driver
holds — and which is independently corroborated by the frozen 59-heavy-atom cross-check. Writing a second
identifier would be a second thing to get wrong.

DEFAULT OFF. `RBFE_RESTRAIN=0` (unset) is a no-op, so every existing lane is byte-identical until a leg opts in.
"""
from __future__ import annotations

import math
import os

# The tolerance well, in nm, added to the starting centroid separation before any force is felt. 0.30 nm is
# ~3x the ternary arm's median contact-moiety displacement (1.64 Å) and well inside the 4.0 Å pose-escape
# threshold the convergence gate flags on, so a leg that behaves like the measured-clean ternary arm never
# leaves the flat region, while the 16.6 Å binary departure is deep in the restrained zone.
DEFAULT_TOLERANCE_NM = 0.30
# Force constant on the wall outside the well. 1000 kJ/mol/nm^2 gives ~1.2 kcal/mol at 1 Å past the edge —
# firm enough to close an escape channel, soft enough that it cannot shock the integrator on a rough start.
DEFAULT_K = 1000.0
CONTACT_CUTOFF_NM = 0.45          # same shell the convergence analysis calls a contact; ONE definition
MIN_CONTACT_ATOMS = 3             # below this the centroid is not a meaningful anchor -> refuse, never guess


def _enabled():
    return str(os.environ.get("RBFE_RESTRAIN", "0")).strip().lower() in ("1", "true", "yes", "on")


def _as_xyz(positions):
    """positions -> an (N,3) float list in NANOMETRES, accepting an OpenMM Quantity or a bare array."""
    if hasattr(positions, "value_in_unit"):
        import openmm.unit as ommunit
        positions = positions.value_in_unit(ommunit.nanometer)
    return [[float(c) for c in row[:3]] for row in positions]


def _centroid(xyz, idx):
    n = len(idx)
    return [sum(xyz[i][d] for i in idx) / n for d in range(3)]


def _dist(a, b):
    return math.sqrt(sum((a[d] - b[d]) ** 2 for d in range(3)))


def select_restraint_groups(system, positions, cutoff_nm=CONTACT_CUTOFF_NM):
    """Pick the two atom groups the restraint acts between, from the STARTING frame.

    Returns a dict that always records HOW the answer was reached, and carries `ok=False` with a `reason`
    rather than a guess when identification fails — a restraint built on the wrong atoms would hold the ligand
    in the wrong place while every step still reported success, which is this lane's signature failure.
    """
    import ternary_fep_convergence as cv

    out = {"ok": False, "reason": None, "cutoff_nm": cutoff_nm}
    n = int(system.getNumParticles())
    masses = [cv._mass_da(system.getParticleMass(i)) for i in range(n)]
    edges, prov = cv._system_edges(system)
    out["bond_provenance"] = prov
    comps = cv.molecules_from_edges(n, edges)
    info = cv.classify_components(comps, None)
    lig = info.get("ligand")
    if not lig:
        # classify_components FAILS CLOSED — it returns ligand=None when 0 or 2+ candidates match, rather than
        # picking. Carry its own status through instead of inventing a reason.
        out["reason"] = "ligand not identified: %s" % info.get("status")
        out["size_histogram"] = info.get("size_histogram")
        return out
    # classify_components reports protein components as SIZES, not indices, so the index set is built here the
    # same way ternary_fep_convergence._ligand_atoms builds it (>= PROTEIN_MIN_ATOMS). ONE definition of
    # "protein"; a second threshold here would be a second thing to drift.
    prot = [i for c in comps if len(c) >= cv.PROTEIN_MIN_ATOMS for i in c]
    out["protein_chain_sizes"] = [len(c) for c in comps if len(c) >= cv.PROTEIN_MIN_ATOMS]
    if not prot:
        out["reason"] = ("no component reaches PROTEIN_MIN_ATOMS=%d — this System has no receptor, so there is "
                         "nothing to restrain the ligand TO (a solvent leg must never be restrained)"
                         % cv.PROTEIN_MIN_ATOMS)
        return out

    h_mass, h_note = cv.hydrogen_mass_da(lig, masses, edges)
    out["hydrogen_mass_da"], out["hydrogen_mass_note"] = h_mass, h_note
    if h_mass is None:
        out["reason"] = "hydrogen mass not measurable, so heavy atoms cannot be separated"
        return out
    cut = h_mass * cv.HEAVY_MASS_MARGIN
    lig_heavy = [i for i in lig if masses[i] > cut]
    prot_heavy = [i for i in prot if masses[i] > cut]
    out["n_ligand_heavy"], out["n_protein_heavy"] = len(lig_heavy), len(prot_heavy)

    xyz = _as_xyz(positions)
    if len(xyz) < n:
        out["reason"] = "positions (%d) shorter than the System (%d particles)" % (len(xyz), n)
        return out

    # contact moiety, from the STARTING frame (see the module docstring, choice 3)
    c2 = cutoff_nm * cutoff_nm
    contact_lig, anchor_prot = [], set()
    for i in lig_heavy:
        pi = xyz[i]
        touched = False
        for j in prot_heavy:
            pj = xyz[j]
            dx, dy, dz = pi[0] - pj[0], pi[1] - pj[1], pi[2] - pj[2]
            if dx * dx + dy * dy + dz * dz <= c2:
                touched = True
                anchor_prot.add(j)
        if touched:
            contact_lig.append(i)
    out["ligand_group"] = contact_lig
    out["receptor_group"] = sorted(anchor_prot)
    out["n_contact_ligand_atoms"] = len(contact_lig)
    out["n_anchor_receptor_atoms"] = len(out["receptor_group"])
    if len(contact_lig) < MIN_CONTACT_ATOMS or len(out["receptor_group"]) < MIN_CONTACT_ATOMS:
        out["reason"] = ("too few contact atoms to anchor a centroid (ligand %d, receptor %d, need >= %d each) "
                         "— the ligand may not be in the pocket in the starting frame, which is itself a finding"
                         % (len(contact_lig), len(out["receptor_group"]), MIN_CONTACT_ATOMS))
        return out

    out["r0_nm"] = _dist(_centroid(xyz, contact_lig), _centroid(xyz, out["receptor_group"]))
    out["ok"] = True
    return out


def add_flat_bottom_restraint(system, positions, tolerance_nm=None, k=None, cutoff_nm=CONTACT_CUTOFF_NM,
                              log=print):
    """Add the λ-independent flat-bottom pocket restraint to `system` IN PLACE. No-op unless RBFE_RESTRAIN=1.

    Returns a report dict (always; `applied` says whether a force was actually added). Never raises on a
    selection failure — it reports and declines, because silently restraining the wrong atoms is worse than
    running unrestrained, and the convergence gate still catches an unrestrained escape.
    """
    tolerance_nm = float(os.environ.get("RBFE_RESTRAIN_TOL_NM") or tolerance_nm or DEFAULT_TOLERANCE_NM)
    k = float(os.environ.get("RBFE_RESTRAIN_K") or k or DEFAULT_K)
    report = {"applied": False, "enabled": _enabled(), "tolerance_nm": tolerance_nm, "k_kj_mol_nm2": k,
              "lambda_dependent": False, "standard_state_correction_required": False,
              "standard_state_note": ("RBFE with a never-decoupled ligand and a λ-independent restraint on "
                                      "mapped core atoms: the restraint term is identical at both endpoints and "
                                      "cancels from ΔG(A→B). An ABFE-style analytic release term would be wrong "
                                      "here, not conservative.")}
    if not report["enabled"]:
        return report

    sel = select_restraint_groups(system, positions, cutoff_nm=cutoff_nm)
    report["selection"] = sel
    if not sel.get("ok"):
        log("[restraint] NOT APPLIED — %s" % sel.get("reason"))
        report["reason"] = sel.get("reason")
        return report

    import openmm
    r_flat = sel["r0_nm"] + tolerance_nm
    force = openmm.CustomCentroidBondForce(2, "0.5*k*max(0, distance(g1,g2) - r_flat)^2")
    force.addGlobalParameter("k", k)
    force.addGlobalParameter("r_flat", r_flat)
    g1 = force.addGroup(sel["ligand_group"])
    g2 = force.addGroup(sel["receptor_group"])
    force.addBond([g1, g2], [])
    force.setUsesPeriodicBoundaryConditions(True)
    # Its own force group, so the restraint's energy can be read back separately and shown to be ~0 in normal
    # bound sampling. A restraint you cannot measure is a restraint you cannot defend.
    used = {system.getForce(i).getForceGroup() for i in range(system.getNumForces())}
    fg = next((g for g in range(31, 0, -1) if g not in used), 0)
    force.setForceGroup(fg)
    report["force_group"] = fg
    report["force_index"] = system.addForce(force)
    report["r0_nm"] = sel["r0_nm"]
    report["r_flat_nm"] = r_flat
    report["applied"] = True
    log("[restraint] FLAT-BOTTOM pocket restraint APPLIED: %d ligand contact atoms <-> %d receptor anchor atoms, "
        "r0=%.3f nm, flat to %.3f nm, k=%.0f kJ/mol/nm^2, force group %d, λ-INDEPENDENT (cancels from ΔΔG; no "
        "standard-state correction)" % (sel["n_contact_ligand_atoms"], sel["n_anchor_receptor_atoms"],
                                        sel["r0_nm"], r_flat, k, fg))
    return report


def restraint_energy_kj(context, force_group):
    """Energy in the restraint's own force group — 0 inside the well. The check that it is not silently biasing
    normal bound sampling; call it after minimization and again in production."""
    st = context.getState(getEnergy=True, groups={int(force_group)})
    return float(st.getPotentialEnergy().value_in_unit(__import__("openmm").unit.kilojoule_per_mole))


def flat_bottom_energy(r_nm, r_flat_nm, k=DEFAULT_K):
    """The restraint's functional form as plain arithmetic — the same expression handed to OpenMM, so the tests
    can pin the physics (zero inside, quadratic outside, continuous at the edge) with no MD stack present."""
    d = r_nm - r_flat_nm
    return 0.0 if d <= 0 else 0.5 * k * d * d
