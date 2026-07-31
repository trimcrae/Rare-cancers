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
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#: A solvated explicit-water system of this size is always strongly negative. Zero is the physical boundary,
#: not a tuned cut — the same one `nrv04_vast_launch.retro_input_quarantine` uses, imported there rather than
#: re-typed here would be circular (that module imports nothing from this one), so it is stated once in each
#: and pinned equal by tests/test_nrv04_pe_stage_probe.py.
NONPHYSICAL_PE_KJ = 0.0


def single_point_kj(topology, positions, sysgen):
    """Potential energy (kJ/mol) of one construction stage. No minimisation, no dynamics. CPU platform."""
    from openmm import Platform, VerletIntegrator, unit
    from openmm import app  # noqa: F401  (kept: import parity with the builder's namespace)
    system = sysgen.create_system(topology)
    integ = VerletIntegrator(0.001)
    ctx = None
    try:
        ctx = __import__("openmm").Context(system, integ, Platform.getPlatformByName("CPU"))
        ctx.setPositions(positions)
        return ctx.getState(getEnergy=True).getPotentialEnergy().value_in_unit(
            unit.kilojoule_per_mole)
    finally:
        del ctx, integ


def probe_unit(bucket, system_name, seed, leg_id="noncov_nr4a1", cofold_prefix=None):
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

    def _probe(name, topo, pos, sysgen):
        try:
            e = single_point_kj(topo, pos, sysgen)
            ok = e <= NONPHYSICAL_PE_KJ
            stages.append({"stage": name, "n_atoms": topo.getNumAtoms(),
                           "pe_kj_per_mol": e, "physical": bool(ok)})
            print("[pe-stage] %-12s %-22s n_atoms=%7d  PE=%+.6e kJ/mol  %s"
                  % (tag, name, topo.getNumAtoms(), e, "ok" if ok else "** NON-PHYSICAL **"), flush=True)
        except Exception as exc:                      # noqa: BLE001 — a stage we cannot price is UNKNOWN
            stages.append({"stage": name, "n_atoms": topo.getNumAtoms(),
                           "pe_kj_per_mol": None, "physical": None,
                           "error": "%s: %s" % (type(exc).__name__, exc)})
            print("[pe-stage] %-12s %-22s PE UNREADABLE: %s: %s"
                  % (tag, name, type(exc).__name__, exc), flush=True)

    build_system(os.path.join(res["out"], "complex.pdb"),
                 os.path.join(res["out"], "ligand.sdf"),
                 leg.covalent, os.environ.get("COV_LIG_ATOM", "C6"), 551, leg.mutation,
                 target_chain=res["chains"]["target_chain"], stage_probe=_probe)

    bad = [s for s in stages if s.get("physical") is False]
    first = bad[0]["stage"] if bad else None
    return {"system": system_name, "seed": seed, "cofold_prefix": base, "cif": cif,
            "stages": stages, "first_nonphysical_stage": first,
            "verdict": ("physical at every construction stage" if not bad else
                        "energy first goes non-physical at: %s" % first)}


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--bucket", default=os.environ.get("VAST_CKPT_BUCKET", ""))
    # FAILING first, CONTROL second — the comparison is the deliverable, so both are the default and neither
    # is optional. A probe run on the broken input alone cannot say which stage is ABNORMAL.
    ap.add_argument("--units", default=os.environ.get("PE_PROBE_UNITS", "nr4a3:3,nr4a3:1"),
                    help="comma-sep system:seed pairs; default = the failing seed_3 then its working sibling")
    ap.add_argument("--out", default="nrv04-pe-stage-probe.json")
    a = ap.parse_args(argv)
    if not a.bucket:
        raise SystemExit("set --bucket or $VAST_CKPT_BUCKET")

    results = []
    for pair in [p for p in a.units.split(",") if p.strip()]:
        sysname, _, sd = pair.partition(":")
        print("\n=== %s seed %s ===" % (sysname, sd), flush=True)
        try:
            results.append(probe_unit(a.bucket, sysname.strip(), int(sd)))
        except Exception as e:                        # noqa: BLE001 — one unit must not abort the comparison
            print("[pe-stage] %s seed %s FAILED to build: %s: %s" % (sysname, sd, type(e).__name__, e),
                  flush=True)
            results.append({"system": sysname.strip(), "seed": int(sd),
                            "error": "%s: %s" % (type(e).__name__, e)})

    doc = {"_what": "Single-point potential energy at each construction stage, for a failing co-fold and a "
                    "working control. The stage at which PE first goes non-physical localises the fault.",
           "_why": "Replaces the retired inter-chain-distance gate, which was refuted by its own first run "
                   "(nrv04_cofold_audit.CLASH_MIN_INTERCHAIN_A). PE needs no threshold: -4e6 runs, +2e15 "
                   "does not.",
           "nonphysical_above_kj": NONPHYSICAL_PE_KJ, "units": results}
    json.dump(doc, open(a.out, "w"), indent=2)
    print("\n" + json.dumps(doc, indent=2), flush=True)

    # THE READING, said out loud rather than left to the reader — this is a diagnostic whose whole value is
    # the comparison between the two units.
    fails = {r["system"] + ":" + str(r["seed"]): r.get("first_nonphysical_stage")
             for r in results if "stages" in r}
    print("\n[pe-stage] first non-physical stage per unit: %s" % json.dumps(fails), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
