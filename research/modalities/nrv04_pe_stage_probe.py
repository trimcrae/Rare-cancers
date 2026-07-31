#!/usr/bin/env python3
"""
WHERE DOES THE ENERGY GO NON-PHYSICAL? — a $0 CPU stage-by-stage single-point PE probe.

★★ WHY THIS EXISTS, and why it replaces the geometry scan retired the same afternoon.

`nrv04retro-retro_noncov_nr4a3-m3-r0` and `-m3-r1` — the only two of eighteen units that ever blew up —
reach `md-running`, produce `openmm.OpenMMException: Particle coordinate is NaN` at the FIRST production
step, and record

    blew_up=true  blow_phase="prod@frame0/5"  pe_pre_min = +2.108844e+15 kJ/mol

against working siblings on the same image, lane and code near -4.0e6. Both draw on the same co-fold
(`nrv04-descriptive-v4/nr4a3/seed_3`) and their `pe_pre_min` agree to TEN significant figures, so the fault
is deterministic in the built system.

⛔ WHAT I GOT WRONG FIRST, kept here because the correction is the point. I hypothesised the clash was the
closest inter-chain contact in the CO-FOLD and shipped a 1.5 A gate on it. The first run refuted it against
ground truth already in hand — `nr4a2/seed_1` has the SMALLEST contact in the whole set (1.055 A) and
produced the two landed 500-frame production legs, while `nr4a3/seed_3` sits ABOVE two working inputs at
1.365 A. The ordering is wrong, so no threshold on that measure can separate runnable from non-runnable
(`nrv04_cofold_audit.CLASH_MIN_INTERCHAIN_A`, now a census).

THE MEASURE THAT NEEDS NO THRESHOLD is the one the failure itself reports: the single-point potential energy,
taken at each construction stage. -4e6 runs; +2e15 does not; there is nothing to tune. The STAGE AT WHICH IT
FIRST GOES NON-PHYSICAL IS THE ANSWER:

  * non-physical at `protein_after_pdbfixer`  -> the fault is in the co-fold geometry (or PDBFixer's repair of
    it). A different seed or a changed input is the only route, and that is a PREREGISTRATION question.
  * first non-physical at `protein_plus_ligand` -> the ligand is being placed into the protein. Ours, in code.
  * first non-physical at `solvated`          -> `addSolvent` is placing water/ions inside the solute. Ours,
    in code, and the prior favours it: the co-fold is ~5,570 atoms of a ~315,000-atom built system, so ~98 %
    of what exists at the end was placed by our solvation, not by Boltz.
  * physical at every stage, only the MINIMISED energy wrong -> minimiser/integrator setup, a third fix.

⚠ IT MEASURES THE PRODUCTION PATH, NOT A COPY OF IT. `nrv04_covalent_md.build_system` takes a `stage_probe`
callback; this module supplies one. A probe that rebuilt the stages itself could drift from the real builder
and then answer confidently about a pipeline nobody runs — the same class of error as the geometry gate.

Runs on CPU in CI (MD env + AWS creds). No GPU, no MD, no Vast spend, no minimisation.

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
★★ THE ANSWER — measured 2026-07-31, 4:20 PM ET (run 30662210714, job 91260853705). THIS IS ITS ONE HOME:
the probe writes an artifact that GitHub ages out, so the numbers live here.

    stage                     n_atoms   nr4a3 seed 3 (FAILS)      nr4a3 seed 1 (CONTROL)     decades apart
    protein_after_pdbfixer     10,914   +2.109005036357692e+15    +2.522674e+05                   9.92
    protein_plus_ligand        11,080   +2.109005036360151e+15    +2.606874e+05                   9.91
    solvated                  ~320,000  +2.108844375741770e+15    -3.740431e+06                   8.75

READ IT IN THE ORDER THE PIPELINE RUNS, because the first row already settles it:

  1. **The energy is ALREADY +2.109e15 at `protein_after_pdbfixer`** — 10,914 atoms, before the ligand exists
     and before one water molecule has been placed. The control at the identical stage is +2.52e5, which is
     an entirely ordinary unminimised protein. Ten orders of magnitude, same code, same image, same stage.
  2. **Adding the ligand moves seed 3 by ~2,459 kJ/mol out of 2.1e15** (the 12th significant figure). Ligand
     placement is EXONERATED — it cannot be the cause of something that was already there.
  3. **Solvation DECREASES it** (2.109005e15 -> 2.108844e15) and it is the step that takes the system from
     ~11 k atoms to ~320 k. `addSolvent` is EXONERATED, and note that the solvated figure reproduces the
     production leg's own recorded `pe_pre_min = +2.108844e+15` to ten significant figures — the probe is
     measuring the real failure, not a lookalike.

⛔ THIS REFUTES THE PRIOR THE DIAGNOSTIC WAS COMMISSIONED UNDER, and that is worth stating plainly rather
than quietly not mentioning: the stated prior was "~98 % of the system is placed by our solvation, not by
Boltz, so the prior should be that the fault is ours." The prior was reasonable and it is wrong. The fault is
in the co-folded structure (or PDBFixer's repair of it) and is fully formed before our solvation touches it.

★★ AND THEN LOCALISED TO ONE ATOM PAIR — 4:42 PM ET, run 30663617181, job 91265356509. `protein_after_pdbfixer`
has TWO owners (Boltz's coordinates and our PDBFixer repair of them), so naming the stage was not yet an
answer. The force decomposition and the contact provenance settle it:

    NonbondedForce dominates:  +2.109e+15 kJ/mol   (not a bonded term -> geometry, not connectivity)
    clashing pairs under the cutoff:  2, and BOTH are co-fold heavy atom vs co-fold heavy atom
    worst:  A:GLU13:O  <->  A:LYS181:NZ   at   0.181 A

0.181 A between a carbonyl oxygen and a lysine side-chain nitrogen is two atoms occupying the same point.
Boltz placed both; nothing downstream of the prediction put them there and nothing in this pipeline can
separate them. `owner_of_the_fault` returns OWNER_INPUT: a different seed or a changed input, which is a
PREREGISTRATION question and not a code fix.

★★ RUN 3 — THE TWO BREAKER-BLOCKED UNITS ARE NOT INPUT FAULTS (5:16 PM ET, run 30665640363). This is what
keeps the panel's reachable ceiling at 16/18 instead of 14/18.

    solvated PE (kJ/mol)   what the leg then did
    nr4a2 seed 2   -3.85e+06   sibling replica m2-r1 LANDED a complete production leg
    nr4a2 seed 1   +2.78e+09   BOTH replicas (m1-r0, m1-r1) landed complete production legs
    nr4a2 seed 3   +1.94e+07   sibling replica m3-r1 running with real frames
    nr4a3 seed 3   +2.11e+15   never produced one frame, either replica

`first_divergent_stage: null` for nr4a2 seed 2 against seed 1. nr4a2 seed 3 is clean at the stage that
matters — `protein_after_pdbfixer` = +2.21e5, **zero contacts under the clash cutoff**, worst 1.676 A
(E:SER72:H / E:SER111:O, an ordinary hydrogen bond), and a wholly unremarkable force decomposition
(HarmonicBond +1.40e5, Nonbonded -5.44e4, Torsion +5.44e4, Angle +8.12e4 — no astronomic term anywhere).

⛔ AND THE ROW THAT LOOKS ALARMING IS THE ONE THAT PROVES THE RULE: nr4a2 seed 1 sits at **+2.78e9**
pre-minimisation and both of its replicas produced complete legs. So a POSITIVE pre-minimisation solvated
energy is NOT disqualifying, and this module must never acquire a cut between 2.8e9 and 2.1e15 — the data
does not support one, and inventing it would be the retired inter-chain-distance gate all over again.
What separates seed 3 of nr4a3 is not its sign, it is six further orders of magnitude and two heavy atoms
at 0.181 A.

⚠ THE CONTROL'S ENERGY IS NOT BIT-REPRODUCIBLE AND MUST NOT BE QUOTED AS IF IT WERE. Across the two runs the
FAILING unit reproduced to ten significant figures (2.109005036e15 both times — a hard geometric fact), while
the control moved ~20 % at an identical atom count (+2.522674e5 -> +2.082290e5), and the solvated atom count
moved too (316,243 -> 314,183). PDBFixer's hydrogen placement and `addSolvent`'s water packing are not
deterministic. This changes nothing about the reading — the gap is ten decades and the classifier's answer is
invariant from 1 to 9 — but it means the control is a ~1e5 SCALE, not a value.

⛔⛔ AND THE PROBE'S OWN FIRST TWO READOUTS WERE BOTH WRONG, in the SAME class of error, which is why the
verdict is now comparative (`compare_to_control`) rather than a boundary test:
  * run 1 reported `first_nonphysical_stage: "solvated"` because the pre-solvation stages RAISED and were
    unmeasurable — an absent reading read as a reading of absence (`single_point_kj`, `periodic=`).
  * run 2 reported `first_nonphysical_stage: "protein_after_pdbfixer"` for the CONTROL TOO, because the
    `PE <= 0` boundary it applied is only meaningful for a MINIMISED SOLVATED system, and no probe stage is
    either. A normal unminimised protein is positive. The raw magnitudes were unambiguous; the boolean on top
    of them was not, and a reader who trusted the summary line rather than the table would have concluded
    that the control was broken as well.
Both were caught by looking at the numbers instead of the verdict. The fix in each case was to make the
verdict answer the question actually asked — which here is not "is this stage physical?" (unanswerable
without minimisation) but "does this stage DIVERGE from a co-fold known to run?" (answerable, and answered).
═══════════════════════════════════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#: A MINIMISED solvated explicit-water system of this size is always strongly negative, and zero is the
#: physical boundary for one — not a tuned cut. That is the boundary
#: `nrv04_vast_launch.retro_input_quarantine` applies to `pe_post_min_kj`; it is stated once in each module
#: rather than imported (that module imports nothing from this one) and pinned equal by
#: tests/test_nrv04_pe_stage_probe.py.
#:
#: ⛔ IT DOES NOT APPLY TO A PROBE STAGE, and applying it was this module's second wrong readout. NONE of the
#: three stages is minimised and two are not solvated, so a positive energy is the EXPECTED reading — the
#: control is +2.5e5 at `protein_after_pdbfixer` and runs perfectly. The constant is kept because the
#: quarantine's boundary and this module's must not silently drift apart, not because the probe tests against
#: it. The probe's verdict is `compare_to_control`.
NONPHYSICAL_PE_KJ = 0.0

#: How far apart, in ORDERS OF MAGNITUDE at the same construction stage, before a unit is "divergent" from a
#: co-fold known to produce frames.
#:
#: ⚠ THIS IS NOT THE GEOMETRY GATE'S MISTAKE REPEATED WITH A NEW NUMBER, and the difference is testable rather
#: than asserted: the retired 1.5 A inter-chain cut was refuted because ground truth STRADDLED it (the smallest
#: contact in the set produced the two landed production legs). Here the observation is bimodal by ~10 decades
#: — 9.92 / 9.91 / 8.75 for the failing unit against its control — so every value from 1 to 9 returns the same
#: stage, and `tests/test_nrv04_pe_stage_probe.py::test_the_verdict_is_invariant_across_the_threshold` fails if
#: that ever stops being true. A threshold whose answer does not move across four orders of magnitude of
#: itself is a separator, not a tuning knob.
DIVERGENCE_DECADES = 3.0


def single_point_kj(topology, positions, sysgen, periodic=True):
    """Potential energy (kJ/mol) of one construction stage. No minimisation, no dynamics. CPU platform.

    ⚠ `periodic=False` FOR EVERY PRE-SOLVATION STAGE, and this was a real defect in the probe's first run
    (2026-07-31, 4:14 PM ET). `sysgen.create_system` applies the panel's production `forcefield_kwargs` — PME
    with a 0.9 nm cutoff — which require a periodic box at least twice the cutoff. An unsolvated topology has
    no such box, so BOTH pre-solvation stages returned

        OpenMMException: NonbondedForce: The cutoff distance cannot be greater than half the periodic box size

    for the failing unit AND the control. That made `first_nonphysical_stage` report `solvated` for a reason
    that had nothing to do with solvation: the earlier stages were unmeasurable, not clean. Reporting that as
    "the fault is in solvation" would be CLAUDE.md §4b's error exactly — an absent reading read as a reading
    of absence. An unsolvated system is priced with NO cutoff, which is the physically correct treatment for
    a non-periodic assembly and is what makes the three stages comparable at all.
    """
    from openmm import Platform, VerletIntegrator, unit
    from openmm import app
    if periodic:
        system = sysgen.create_system(topology)
    else:
        system = sysgen.forcefield.createSystem(topology, nonbondedMethod=app.NoCutoff,
                                                constraints=None, rigidWater=False)
    integ = VerletIntegrator(0.001)
    ctx = None
    try:
        ctx = __import__("openmm").Context(system, integ, Platform.getPlatformByName("CPU"))
        ctx.setPositions(positions)
        return ctx.getState(getEnergy=True).getPotentialEnergy().value_in_unit(
            unit.kilojoule_per_mole)
    finally:
        del ctx, integ


def decompose_by_force(system, positions):
    """{force: energy_kj} for one already-built system. WHICH TERM CARRIES THE ENERGY NAMES THE FIX.

    ★★ THE QUESTION `compare_to_control` LEAVES OPEN. Knowing the divergence is present at
    `protein_after_pdbfixer` says WHEN; it does not say WHAT, and the two candidates need opposite responses:

      * `NonbondedForce` -> atoms on top of each other. The LJ r^-12 term diverges, which is the only ordinary
        way to reach 1e15 kJ/mol, and it points at GEOMETRY.
      * `HarmonicBondForce` / `HarmonicAngleForce` -> a bond or angle spanning a distance it should not, i.e.
        a CONNECTIVITY error — two residues wrongly joined, a chain break stitched shut. Geometry would be
        innocent and no amount of re-seeding would help.

    Mutates force groups on the system it is handed, so hand it a throwaway.
    """
    from openmm import Context, Platform, VerletIntegrator, unit
    forces = list(system.getForces())
    for i, f in enumerate(forces):
        f.setForceGroup(min(i, 31))
    integ = VerletIntegrator(0.001)
    ctx = None
    out = {}
    try:
        ctx = Context(system, integ, Platform.getPlatformByName("CPU"))
        ctx.setPositions(positions)
        for i, f in enumerate(forces):
            e = ctx.getState(getEnergy=True, groups={min(i, 31)}).getPotentialEnergy().value_in_unit(
                unit.kilojoule_per_mole)
            out["%s[%d]" % (type(f).__name__, i)] = e
    finally:
        del ctx, integ
    return out


def cofold_atom_keys(complex_pdb):
    """{(chain, resSeq, atom_name)} present in the RAW co-fold PDB — i.e. placed by Boltz, not by our prep.

    The co-fold is heavy-atoms-only (see `nrv04_covalent_md.build_system`), so every hydrogen in the fixed
    topology is ours by construction and every heavy atom NOT in this set was added by `addMissingAtoms`.
    """
    keys = set()
    with open(complex_pdb) as fh:
        for ln in fh:
            if ln.startswith(("ATOM  ", "HETATM")):
                keys.add((ln[21], ln[22:26].strip(), ln[12:16].strip()))
    return keys


def _bonded_within_3(topology):
    """{frozenset({i, j})} for every 1-2 and 1-3 pair — these are SUPPOSED to be close and are excluded."""
    adj = {}
    for b in topology.bonds():
        i, j = b[0].index, b[1].index
        adj.setdefault(i, set()).add(j)
        adj.setdefault(j, set()).add(i)
    pairs = set()
    for i, ns in adj.items():
        for j in ns:
            pairs.add(frozenset((i, j)))
            for k in adj.get(j, ()):
                if k != i:
                    pairs.add(frozenset((i, k)))
    return pairs


def close_contacts(topology, positions, cofold_keys=None, cutoff_a=1.1, limit=25, scan_a=2.5):
    """The non-bonded atom pairs closer than `cutoff_a`, each annotated with WHO PLACED IT.

    ⛔ THE PROVENANCE COLUMN IS THE WHOLE POINT, and it is the difference between a decision for trimcrae and
    a bug for me. `compare_to_control` localises the fault to "the co-fold, or PDBFixer's repair of it" — one
    stage, two owners. If the offending pair is two Boltz-placed HEAVY atoms, the predicted structure is bad
    and re-seeding is the only route (a preregistration question). If either atom was added by our own
    `addMissingAtoms` / `addMissingHydrogens`, the input may be fine and the PREP is placing an atom on top of
    something — ours, in code, and fixable without touching the panel's design.
    """
    import numpy as np
    from openmm import unit
    xyz = np.array(positions.value_in_unit(unit.angstrom), dtype=float)
    atoms = list(topology.atoms())
    excluded = _bonded_within_3(topology)
    # ⚠ THE SCAN IS WIDER THAN THE CLASH CUTOFF ON PURPOSE. If nothing sits under `cutoff_a` this must still
    # return the closest pairs it DID find, because "no contact under 1.1 A" is itself decision-relevant — it
    # would mean the 1e15 is not a steric overlap at all. Returning an empty list instead would leave
    # `owner_of_the_fault` at UNDETERMINED for want of evidence that exists.
    # Cell list at the scan radius: 11 k atoms all-pairs is ~121 M distances, which is neither necessary nor kind.
    cell = max(float(scan_a), float(cutoff_a), 1e-6)
    keys = np.floor(xyz / cell).astype(np.int64)
    buckets = {}
    for idx, k in enumerate(map(tuple, keys)):
        buckets.setdefault(k, []).append(idx)
    seen, hits = set(), []
    offs = [(dx, dy, dz) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1)]
    for k, members in buckets.items():
        near = [n for o in offs for n in buckets.get((k[0] + o[0], k[1] + o[1], k[2] + o[2]), ())]
        for i in members:
            for j in near:
                if j <= i:
                    continue
                p = frozenset((i, j))
                if p in seen or p in excluded:
                    continue
                seen.add(p)
                d = float(np.linalg.norm(xyz[i] - xyz[j]))
                if d < cell:
                    hits.append((d, i, j))
    hits.sort()
    n_under_cutoff = sum(1 for d, _i, _j in hits if d < cutoff_a)

    # ⛔ THE PROVENANCE IS A STRUCTURED FLAG, NEVER A SUBSTRING OF THE PROSE (caught by this module's own test
    # before it ever ran, 2026-07-31). The first version derived `both_from_cofold` with
    # `"co-fold" in description`, and the hydrogen description reads "...the co-fold is heavy-atoms-only" —
    # so every PDBFixer hydrogen matched and was attributed to Boltz. That single boolean is what
    # `owner_of_the_fault` uses to decide between a code fix and a preregistration decision, so the bug would
    # have routed a fixable clash to trimcrae with a confident explanation attached.
    SRC_COFOLD, SRC_PREP, SRC_UNKNOWN = "cofold", "prep", "unknown"

    def _who(a):
        if a.element is not None and a.element.symbol == "H":
            return SRC_PREP, "OURS (hydrogen added by PDBFixer; the co-fold is heavy-atoms-only)"
        if cofold_keys is None:
            return SRC_UNKNOWN, "unknown — no raw co-fold supplied to compare against"
        key = (a.residue.chain.id, str(a.residue.id), a.name)
        return ((SRC_COFOLD, "co-fold (placed by Boltz)") if key in cofold_keys else
                (SRC_PREP, "OURS (heavy atom added by PDBFixer)"))

    def _lbl(a):
        return "%s:%s%s:%s" % (a.residue.chain.id, a.residue.name, a.residue.id, a.name)

    out = []
    for d, i, j in hits[:limit]:
        s1, w1 = _who(atoms[i])
        s2, w2 = _who(atoms[j])
        out.append({"distance_a": round(d, 4), "atom_1": _lbl(atoms[i]), "atom_2": _lbl(atoms[j]),
                    "placed_by_1": w1, "placed_by_2": w2, "source_1": s1, "source_2": s2,
                    # UNKNOWN is not co-fold. Without a raw structure to compare against, nothing may be
                    # attributed to Boltz — that attribution is the one that ends in a decision for trimcrae.
                    "under_clash_cutoff": bool(d < cutoff_a),
                    "both_from_cofold": (s1 == SRC_COFOLD and s2 == SRC_COFOLD)})
    return out, n_under_cutoff


def probe_unit(bucket, system_name, seed, leg_id="noncov_nr4a1", cofold_prefix=None, localise=False):
    """Build ONE (system, seed) through the production builder, recording PE at each stage.

    `leg_id` selects the panel leg whose ligand/covalent flags are used. The retrospective's legs are all
    non-covalent, so the NR4A1 non-covalent leg is the right shape for every arm — what varies between arms
    is the CO-FOLD, which is what this probe is varying.
    """
    import nrv04_retro_panel as retro
    from nrv04_build_smoke import _pull_cofold
    from nrv04_covalent_assemble import assemble_leg
    from nrv04_covalent_md import build_system
    from nrv04_covalent_panel import leg_by_id
    from nrv04_ligands import LIGANDS

    base = (cofold_prefix or retro.COFOLD_PREFIX).rstrip("/")
    tag = "%s_s%d" % (system_name, seed)
    cif = _pull_cofold(bucket, base, "%s/seed_%d" % (system_name, seed), "/tmp/peprobe_%s" % tag)
    leg = leg_by_id(leg_id)
    res = assemble_leg(cif, leg, LIGANDS[leg.ligand], "/tmp/pestage_%s" % tag)

    stages = []
    localised = {}
    cofold_keys = cofold_atom_keys(os.path.join(res["out"], "complex.pdb")) if localise else None

    def _localise(name, topo, pos, sysgen):
        """WHICH FORCE and WHICH ATOMS, at the stage the divergence is first present. Non-fatal by design —
        this is an explanation of a failure and must never become one."""
        from openmm import app
        try:
            sysd = sysgen.forcefield.createSystem(topo, nonbondedMethod=app.NoCutoff, constraints=None,
                                                  rigidWater=False)
            by_force = decompose_by_force(sysd, pos)
        except Exception as exc:  # noqa: BLE001
            by_force = {"error": "%s: %s" % (type(exc).__name__, exc)}
        try:
            contacts, n_total = close_contacts(topo, pos, cofold_keys=cofold_keys)
        except Exception as exc:  # noqa: BLE001
            contacts, n_total = [{"error": "%s: %s" % (type(exc).__name__, exc)}], None
        localised[name] = {"energy_by_force_kj": by_force, "n_close_contacts": n_total,
                           "worst_contacts": contacts}
        print("[pe-stage]   force decomposition at %s:" % name, flush=True)
        for k, v in sorted(by_force.items(), key=lambda kv: -abs(kv[1]) if isinstance(kv[1], float) else 0):
            print("[pe-stage]     %-28s %s" % (k, ("%+.6e kJ/mol" % v) if isinstance(v, float) else v),
                  flush=True)
        print("[pe-stage]   %s non-bonded pair(s) under the contact cutoff; worst:"
              % ("?" if n_total is None else n_total), flush=True)
        for c in contacts[:10]:
            print("[pe-stage]     %s" % json.dumps(c), flush=True)

    def _probe(name, topo, pos, sysgen):
        # ⛔ NO PER-STAGE VERDICT IS RECORDED HERE. An unminimised, mostly-unsolvated stage has no boundary to
        # be judged against; the one this used to apply (`PE <= 0`) flagged the healthy CONTROL. The stage
        # records a MEASUREMENT; `compare_to_control` records the judgement, against ground truth.
        try:
            e = single_point_kj(topo, pos, sysgen, periodic=(name == "solvated"))
            stages.append({"stage": name, "n_atoms": topo.getNumAtoms(), "pe_kj_per_mol": e})
            print("[pe-stage] %-12s %-22s n_atoms=%7d  PE=%+.6e kJ/mol"
                  % (tag, name, topo.getNumAtoms(), e), flush=True)
        except Exception as exc:                      # noqa: BLE001 — a stage we cannot price is UNKNOWN
            stages.append({"stage": name, "n_atoms": topo.getNumAtoms(),
                           "pe_kj_per_mol": None,
                           "error": "%s: %s" % (type(exc).__name__, exc)})
            print("[pe-stage] %-12s %-22s PE UNREADABLE: %s: %s"
                  % (tag, name, type(exc).__name__, exc), flush=True)
        # Only the FIRST stage is localised: it is where the divergence is already present, and every later
        # stage inherits it, so decomposing them would re-describe the same 1e15 three times.
        if localise and name == "protein_after_pdbfixer":
            _localise(name, topo, pos, sysgen)

    build_system(os.path.join(res["out"], "complex.pdb"),
                 os.path.join(res["out"], "ligand.sdf"),
                 leg.covalent, os.environ.get("COV_LIG_ATOM", "C6"), 551, leg.mutation,
                 target_chain=res["chains"]["target_chain"], stage_probe=_probe)

    return {"system": system_name, "seed": seed, "cofold_prefix": base, "cif": cif, "stages": stages,
            "localised": localised or None}


def compare_to_control(subject, control, decades=DIVERGENCE_DECADES):
    """Which construction stage first sends SUBJECT orders of magnitude away from a co-fold known to run? PURE.

    ★★ THE QUESTION A BOUNDARY TEST COULD NOT ANSWER. "Is this stage physical?" has no answer without
    minimisation — a real, runnable, unminimised protein is positive, so `PE <= 0` called the control broken
    (module docstring, run 2). "Does this stage diverge from a structure we have watched produce 500 frames?"
    is answerable from the same numbers and is the question that localises the fault.

    Returns {"stages": [...], "first_divergent_stage": str|None, "verdict": str}. A stage either side of which
    a PE is missing is UNKNOWN — never "converged", never "divergent" (CLAUDE.md §4b).
    """
    import math
    by_stage = {s.get("stage"): s for s in (control or {}).get("stages") or ()}
    rows, first = [], None
    for s in (subject or {}).get("stages") or ():
        name = s.get("stage")
        c = by_stage.get(name) or {}
        a, b = s.get("pe_kj_per_mol"), c.get("pe_kj_per_mol")
        row = {"stage": name, "n_atoms": s.get("n_atoms"),
               "pe_subject_kj": a, "pe_control_kj": b}
        if a is None or b is None or a == 0.0 or b == 0.0:
            row["decades_above_control"] = None
            row["status"] = "unknown — %s" % ("no control at this stage" if b is None else
                                              "subject unreadable" if a is None else "a PE of exactly zero")
        else:
            d = math.log10(abs(float(a))) - math.log10(abs(float(b)))
            row["decades_above_control"] = d
            row["sign_flip"] = (float(a) > 0) != (float(b) > 0)
            # ⚠ THE TEST IS ONE-SIDED, AND SAYING SO IS THE POINT (2026-07-31, nr4a2 run). `d` is
            # log10|subject| - log10|control|, so it can only ever flag a subject WORSE than its control.
            # When nr4a2:2 (solvated -3.85e6, healthy) was compared against nr4a2:1 (solvated +2.78e9), every
            # stage printed "consistent with the control" — which reads as "as good as", when in fact the
            # subject was orders BETTER and the control was the odd one. Same family as every other defect
            # this file records: a summary line asserting more than the number under it.
            if d >= decades:
                row["status"] = "DIVERGENT"
            elif name == "solvated" and float(a) < 0 <= float(b):
                # ★ SIGN BEATS MAGNITUDE AT THIS STAGE, and only at this stage. A solvated system's energy
                # going NEGATIVE is the runnable signature (`NONPHYSICAL_PE_KJ` is the same physics applied
                # post-minimisation); the control staying positive is the anomaly. Reporting that as
                # "consistent with the control" on a -2.86-decade gap would bury the one qualitative fact in
                # the table — which is how nr4a2:2's clean bill of health nearly read as a shrug.
                row["status"] = ("subject reaches a NEGATIVE solvated energy (%+.3e) while the control does "
                                 "not (%+.3e) — the runnable signature, and healthier than its yardstick"
                                 % (float(a), float(b)))
            elif d <= -decades:
                row["status"] = ("subject is %.1f decades BELOW the control — healthier than its yardstick, "
                                 "not merely consistent with it" % abs(d))
            else:
                row["status"] = "consistent with the control"
            if d >= decades and first is None:
                first = name
        rows.append(row)
    if first:
        # ⚠ "FIRST" ONLY MEANS FIRST AMONG STAGES WE COULD READ. An unreadable earlier stage must not be
        # silently reported as a clean one — that is precisely how run 1 concluded "solvated".
        before = rows[:[r["stage"] for r in rows].index(first)]
        unknown_before = [r["stage"] for r in before if r.get("decades_above_control") is None]
        verdict = ("energy first diverges from the control at: %s — every stage AFTER it inherits the "
                   "divergence rather than causing it" % first)
        if unknown_before:
            verdict += ("; ⚠ but %s could not be compared, so an EARLIER origin is not excluded"
                        % ", ".join(unknown_before))
        elif before:
            verdict += "; and every stage BEFORE it is consistent with the control"
        else:
            # THE STRONGEST READING THIS PROBE CAN RETURN, and the one it actually returned: the divergence is
            # present in the EARLIEST thing the pipeline builds, so nothing our code does afterwards caused it.
            verdict += ("; and it is the FIRST stage measured, so the divergence predates everything this "
                        "pipeline does — it is a property of the INPUT, not of the build")
    elif any(r.get("decades_above_control") is not None for r in rows):
        verdict = "no stage diverges from the control by >= %.1f decades" % decades
    else:
        verdict = "NO COMPARISON POSSIBLE — no stage could be priced for both units"
    # ⛔ A COMPARISON IS ONLY AS GOOD AS ITS CONTROL, AND A SICK CONTROL LAUNDERS A SICK SUBJECT.
    # This is the dangerous direction of the one-sidedness above: two inputs BOTH at 1e15 would print
    # "consistent with the control" at every stage and return OWNER_UNDETERMINED — a clean bill of health for
    # two broken structures. The check has to be ABSOLUTE, not relative, or it inherits the same blind spot.
    #
    # ⚠ AND THE ABSOLUTE SIGNAL IS DELIBERATELY WEAK, because the evidence only supports a weak one. Measured
    # pre-minimisation solvated energies against what the leg then did:
    #     nr4a2 seed 2   -3.85e+06   healthy sign
    #     nr4a2 seed 1   +2.78e+09   POSITIVE — and BOTH its replicas landed complete production legs
    #     nr4a2 seed 3   +1.94e+07   positive
    #     nr4a3 seed 3   +2.11e+15   never produced one frame
    # A positive pre-min solvated energy is therefore NOT disqualifying — +2.78e9 demonstrably runs — so this
    # refuses to invent a cut between 2.8e9 and 2.1e15 that the data does not support. It reports the control's
    # own solvated sign and says the comparison is relative, which is the honest amount of information.
    ctl_solv = next((s.get("pe_kj_per_mol") for s in (control or {}).get("stages") or ()
                     if s.get("stage") == "solvated"), None)
    control_note = None
    if ctl_solv is not None and float(ctl_solv) > 0:
        control_note = ("⚠ THE CONTROL'S OWN solvated energy is %+.3e kJ/mol (positive). A minimised solvated "
                        "system is strongly negative, so this control is not a pristine yardstick — read every "
                        "'consistent with the control' below as RELATIVE to it, not as a clean bill of health. "
                        "This is not disqualifying on its own: nr4a2 seed 1 read +2.78e+09 here and both of "
                        "its replicas landed complete production legs." % float(ctl_solv))
    return {"subject": "%s:%s" % ((subject or {}).get("system"), (subject or {}).get("seed")),
            "control": "%s:%s" % ((control or {}).get("system"), (control or {}).get("seed")),
            "decades_threshold": decades, "stages": rows,
            "control_solvated_kj": ctl_solv, "control_caveat": control_note,
            "first_divergent_stage": first, "verdict": verdict}


#: The three answers this diagnostic can return, and who has to act on each. Named constants rather than
#: prose, because "report a fork" is the failure mode: a diagnostic that ends in a menu has not decided.
OWNER_INPUT = "trimcrae — PREREGISTRATION"
OWNER_CODE = "me — a code fix in our prep"
OWNER_UNKNOWN = "UNDETERMINED"


def owner_of_the_fault(subject, comparison):
    """{"owner", "why", "action"} — who fixes this. PURE, from the localisation the probe already took.

    ★★ THE STAGE ANSWER ALONE DOES NOT ASSIGN OWNERSHIP, and stopping at it would have been a fork dressed as
    a finding. `protein_after_pdbfixer` is the output of TWO things: Boltz's predicted coordinates and our own
    PDBFixer repair of them. The discriminators are already measured:

      * `HarmonicBondForce`/`HarmonicAngleForce` carrying the energy -> CONNECTIVITY, not geometry. Ours to
        fix, and re-seeding would not touch it.
      * `NonbondedForce` carrying it, with the worst contact between TWO CO-FOLD HEAVY ATOMS -> the predicted
        structure has atoms on top of each other before we touch it. No code change reaches that; a different
        seed or input is the only route, and that is a preregistration question.
      * `NonbondedForce` carrying it, with an atom OUR prep added -> `addMissingAtoms`/`addMissingHydrogens`
        placed something into an occupied position. Ours, in code.
    """
    loc = ((subject or {}).get("localised") or {}).get("protein_after_pdbfixer") or {}
    forces = {k: v for k, v in (loc.get("energy_by_force_kj") or {}).items() if isinstance(v, float)}
    contacts = [c for c in (loc.get("worst_contacts") or ()) if "distance_a" in c]
    if not comparison.get("first_divergent_stage"):
        return {"owner": OWNER_UNKNOWN, "action": "no action — nothing diverged",
                "why": "no stage diverged from the control, so there is no fault to assign"}
    if not forces or not contacts:
        return {"owner": OWNER_UNKNOWN,
                "action": "re-run the probe with localisation enabled",
                "why": "the divergence is localised to a STAGE but not to a force or an atom pair, and that "
                       "stage has two owners (Boltz's coordinates and our PDBFixer repair). An unlocalised "
                       "answer cannot choose between them — CLAUDE.md §4b, an absent reading is not a reading "
                       "of absence."}
    dominant = max(forces.items(), key=lambda kv: abs(kv[1]))
    clashes = [c for c in contacts if c.get("under_clash_cutoff")]
    if dominant[0].startswith("Nonbonded") and not clashes:
        # A nonbonded blow-up with NO overlapping pair is not the story anyone expects, and it must not be
        # narrated as one. Say what was measured and stop.
        return {"owner": OWNER_UNKNOWN,
                "action": "investigate the nonbonded term without assuming a steric overlap",
                "why": "%s carries %+.3e kJ/mol, but the closest non-bonded pair is %.3f A and NOTHING is "
                       "under the clash cutoff. An r^-12 divergence is the usual route to this magnitude and "
                       "it is not present here, so the cause is something else (charges, an exclusion, a "
                       "parameter) and calling it a clash would be a story, not a diagnosis."
                       % (dominant[0], dominant[1], contacts[0]["distance_a"])}
    if not dominant[0].startswith("Nonbonded"):
        return {"owner": OWNER_CODE, "action": "fix the connectivity in our prep",
                "why": "%s carries the energy (%+.3e kJ/mol), so this is a bonded-term problem — a bond or "
                       "angle spanning a distance it should not. That is connectivity, not geometry, and a "
                       "different seed would not change it." % (dominant[0], dominant[1])}
    ours = [c for c in clashes if not c.get("both_from_cofold")]
    if ours:
        return {"owner": OWNER_CODE, "action": "fix the prep that places these atoms",
                "why": "%s dominates and %d of the %d clashing pairs involve an atom OUR prep placed, not one "
                       "Boltz did — worst %.3f A, %s / %s. The predicted structure is not exonerated, but a "
                       "code fix is available and must be tried before any re-seeding decision."
                       % (dominant[0], len(ours), len(clashes), ours[0]["distance_a"],
                          ours[0]["atom_1"], ours[0]["atom_2"])}
    return {"owner": OWNER_INPUT,
            "action": "a different seed or a changed input — a preregistration amendment, not a code change",
            "why": "%s dominates (%+.3e kJ/mol) and every one of the %d clashing pairs is between two CO-FOLD "
                   "HEAVY ATOMS — atoms Boltz placed, before our prep touches the structure. Worst %.3f A "
                   "(%s / %s). Nothing in this pipeline can separate them; the predicted structure itself is "
                   "unrunnable." % (dominant[0], dominant[1], len(clashes), clashes[0]["distance_a"],
                                    clashes[0]["atom_1"], clashes[0]["atom_2"])}


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--bucket", default=os.environ.get("VAST_CKPT_BUCKET", ""))
    # FAILING first, CONTROL second — the comparison is the deliverable, so both are the default and neither
    # is optional. A probe run on the broken input alone cannot say which stage is ABNORMAL.
    ap.add_argument("--units", default=os.environ.get("PE_PROBE_UNITS", "nr4a3:3,nr4a3:1"),
                    help="comma-sep system:seed pairs; default = the failing seed_3 then its working sibling")
    ap.add_argument("--out", default="nrv04-pe-stage-probe.json")
    # ⛔ ON BY DEFAULT. The stage answer localises the fault to "the co-fold, or PDBFixer's repair of it" —
    # one stage, TWO OWNERS — and which of those it is decides whether this is a bug I fix or a decision only
    # trimcrae can take. Making the discriminator opt-in would mean routinely stopping one measurement short
    # of the thing that matters, which is exactly the habit CLAUDE.md §2 exists to break.
    ap.add_argument("--no-localise", dest="localise", action="store_false", default=True,
                    help="skip the force decomposition and contact provenance (the discriminator)")
    a = ap.parse_args(argv)
    if not a.bucket:
        raise SystemExit("set --bucket or $VAST_CKPT_BUCKET")

    results = []
    for pair in [p for p in a.units.split(",") if p.strip()]:
        sysname, _, sd = pair.partition(":")
        print("\n=== %s seed %s ===" % (sysname, sd), flush=True)
        try:
            results.append(probe_unit(a.bucket, sysname.strip(), int(sd), localise=a.localise))
        except Exception as e:                        # noqa: BLE001 — one unit must not abort the comparison
            print("[pe-stage] %s seed %s FAILED to build: %s: %s" % (sysname, sd, type(e).__name__, e),
                  flush=True)
            results.append({"system": sysname.strip(), "seed": int(sd),
                            "error": "%s: %s" % (type(e).__name__, e)})

    # THE COMPARISON IS THE DELIVERABLE. Unit 1 is the subject, unit 2 the control — that is why both are the
    # default and neither is optional. A boundary applied to the subject alone was wrong twice (see docstring).
    priced = [r for r in results if r.get("stages")]
    comparison = (compare_to_control(priced[0], priced[1]) if len(priced) >= 2 else
                  {"verdict": "NO COMPARISON POSSIBLE — need a subject AND a control that both priced",
                   "first_divergent_stage": None, "stages": []})

    doc = {"_what": "Single-point potential energy at each construction stage, for a failing co-fold and a "
                    "working control. The stage at which the subject first diverges from the control by "
                    "orders of magnitude localises the fault.",
           "_why": "Replaces the retired inter-chain-distance gate, which was refuted by its own first run "
                   "(nrv04_cofold_audit.CLASH_MIN_INTERCHAIN_A).",
           "_not": "There is no per-stage 'physical' verdict: no probe stage is minimised and two are not "
                   "solvated, so a positive PE is expected and the zero boundary flagged the healthy control.",
           "nonphysical_above_kj_POST_MIN_ONLY": NONPHYSICAL_PE_KJ,
           "decades_threshold": DIVERGENCE_DECADES,
           "units": results, "comparison": comparison}
    json.dump(doc, open(a.out, "w"), indent=2)
    print("\n" + json.dumps(doc, indent=2), flush=True)

    doc["owner"] = owner_of_the_fault(priced[0] if priced else {}, comparison)

    # THE READING, said out loud rather than left to the reader.
    print("\n[pe-stage] %s" % comparison["verdict"], flush=True)
    if comparison.get("control_caveat"):
        print("[pe-stage] %s" % comparison["control_caveat"], flush=True)
    print("[pe-stage] OWNER: %s" % doc["owner"]["owner"], flush=True)
    print("[pe-stage]   %s" % doc["owner"]["why"], flush=True)
    for r in comparison.get("stages") or ():
        d = r.get("decades_above_control")
        print("[pe-stage]   %-22s subject=%s control=%s  %s  -> %s"
              % (r.get("stage"),
                 ("%+.6e" % r["pe_subject_kj"]) if r.get("pe_subject_kj") is not None else "unreadable",
                 ("%+.6e" % r["pe_control_kj"]) if r.get("pe_control_kj") is not None else "unreadable",
                 ("%.2f decades apart" % d) if d is not None else "not comparable",
                 r.get("status")), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
