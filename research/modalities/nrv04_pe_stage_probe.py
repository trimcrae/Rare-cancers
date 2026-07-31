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
By this module's own decision tree above, that is the branch where a different seed or a changed input is the
only route — a PREREGISTRATION question, not a code fix.

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

    build_system(os.path.join(res["out"], "complex.pdb"),
                 os.path.join(res["out"], "ligand.sdf"),
                 leg.covalent, os.environ.get("COV_LIG_ATOM", "C6"), 551, leg.mutation,
                 target_chain=res["chains"]["target_chain"], stage_probe=_probe)

    return {"system": system_name, "seed": seed, "cofold_prefix": base, "cif": cif, "stages": stages}


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
            row["status"] = "DIVERGENT" if d >= decades else "consistent with the control"
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
    return {"subject": "%s:%s" % ((subject or {}).get("system"), (subject or {}).get("seed")),
            "control": "%s:%s" % ((control or {}).get("system"), (control or {}).get("seed")),
            "decades_threshold": decades, "stages": rows,
            "first_divergent_stage": first, "verdict": verdict}


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

    # THE READING, said out loud rather than left to the reader.
    print("\n[pe-stage] %s" % comparison["verdict"], flush=True)
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
