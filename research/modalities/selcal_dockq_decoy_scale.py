#!/usr/bin/env python3
"""What does DockQ 0.03 actually mean? Calibrate the scale with displaced-native decoys. ($0 CPU)

★ THE QUESTION THIS ANSWERS. Our 12 selcal co-folds score DockQ **0.023-0.046** with **fnat 0.000** on the
degradation-target<->VHL interface of 9DTY/9DTX, measured by two independent implementations. That is a
number, not yet a meaning. "Below the Acceptable bar" is DockQ's own class boundary and says the pose is
wrong; it does not say HOW wrong, and the difference matters to the paper: a co-fold that is nearly right
but rotated is a different diagnosis from one that is placed as if at random.

★ THE CALIBRATION, and it introduces no new instrument. Take the deposited complex itself. Hold VHL fixed.
Displace the TRUE target chain by a rigid rotation+translation of known magnitude, and score the result with
the same DockQ, against the same reference, on the same interface. Sweep the magnitude. That produces a
DockQ-versus-displacement curve for a structure that is otherwise perfect -- every side chain, every
contact, the right protein, the right copy -- so the only variable is placement.

Reading it: the displacement at which the native itself falls to ~0.03 is the displacement our co-folds are
indistinguishable from. If that displacement is large, the co-folds are not "nearly right"; they are placed
elsewhere, and the paper should say so in those terms.

⛔ WHAT THIS IS NOT. It is not a model, not a prediction, and not a threshold. It moves no verdict and
re-scores no leg. It is a ruler, built from the reference the measurement already uses, so that a number the
paper quotes can be read by someone who does not know DockQ's classes by heart.

⚠ AND IT IS A NEGATIVE CONTROL, WHICH IS ONLY HALF OF WHAT A NUMBER NEEDS. The matching positive control --
does this harness register a CORRECT ternary at all? -- is `selcal_deepternary_poscontrol.py`. Neither is
worth much without the other: a scorer that returns ~0 for everything would produce this curve too.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))

#: Displacement magnitudes, in Å, applied to the true target chain. Spans "crystallographic noise" to "the
#: other side of the E3", so the curve brackets the co-folds' reading rather than assuming where it lands.
DISPLACEMENTS_A = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0)

#: Independent random directions per magnitude. Small, because the curve's shape is the deliverable and each
#: point costs a DockQ invocation; the spread is reported rather than averaged away.
N_DIRECTIONS = 5

#: Fixed seed. The decoys must be reproducible for the curve to be quotable.
SEED = 0xDEC0


def random_rotation(rng, angle_rad):
    """A rotation of EXACTLY `angle_rad` about a uniformly random axis (Rodrigues)."""
    import numpy as np
    axis = rng.normal(size=3)
    axis = axis / np.linalg.norm(axis)
    K = np.array([[0.0, -axis[2], axis[1]], [axis[2], 0.0, -axis[0]], [-axis[1], axis[0], 0.0]])
    return np.eye(3) + np.sin(angle_rad) * K + (1.0 - np.cos(angle_rad)) * (K @ K)


def displace(atoms, magnitude_a, rng):
    """Rigid-body move of `atoms` whose RMS atomic displacement is `magnitude_a`.

    ★ THE MAGNITUDE IS THE THING BEING SWEPT, so it is MEASURED after the move rather than assumed from the
    parameters: a rotation about the centroid moves distant atoms much further than near ones, so 'a 10°
    rotation' is not a displacement anyone can read. Rotation and translation are combined and then scaled
    so the realised RMSD is the requested one, and the realised value is returned and reported."""
    import numpy as np
    import selcal_deepternary_frame as FR
    P = np.array([[a.x, a.y, a.z] for a in atoms], dtype=float)
    if magnitude_a <= 0.0:
        return list(atoms), 0.0
    c = P.mean(axis=0)
    R = random_rotation(rng, rng.uniform(0.0, np.pi))
    tdir = rng.normal(size=3)
    tdir = tdir / np.linalg.norm(tdir)
    moved = (R @ (P - c).T).T + c + tdir            # unit-length translation on top of the rotation
    delta = moved - P
    rms = float(np.sqrt((delta ** 2).sum(axis=1).mean()))
    if rms <= 1e-9:
        return list(atoms), 0.0
    scaled = P + delta * (magnitude_a / rms)
    realised = float(np.sqrt(((scaled - P) ** 2).sum(axis=1).mean()))
    return [FR.copy_atom(a, x=float(x), y=float(y), z=float(z))
            for a, (x, y, z) in zip(atoms, scaled)], round(realised, 3)


def build_curve(native_path, degrader_comp, roles, workdir, displacements=DISPLACEMENTS_A,
                n_directions=N_DIRECTIONS, seed=SEED):
    """DockQ of the deposited complex against itself after displacing the target chain. Returns a doc."""
    import numpy as np
    import selcal_cofold_validate as V
    import selcal_deepternary_frame as FR
    import selcal_deepternary_run as RUN
    import selcal_dockq_crosscheck as X

    os.makedirs(workdir, exist_ok=True)
    doc = {"_what": "DockQ vs rigid displacement of the TRUE target chain, same reference, same instrument",
           "native": os.path.basename(native_path), "roles": roles, "dockq_version": X.dockq_version(),
           "seed": seed, "points": []}

    atoms = V.parse_structure(native_path)
    tgt, e3, deg, err = FR.native_copy(atoms, roles, degrader_comp)
    if err:
        doc["error"] = err
        return doc

    ref = os.path.join(workdir, "decoy_reference.pdb")
    RUN.write_pdb([FR.copy_atom(a, chain="A") for a in tgt] + [FR.copy_atom(a, chain="B") for a in e3], ref)
    doc["reference_atoms"] = {"target": len(tgt), "e3": len(e3)}

    rng = np.random.default_rng(seed)
    for mag in displacements:
        vals, realised = [], []
        for k in range(1 if mag == 0.0 else n_directions):
            moved, r = displace(tgt, mag, rng)
            realised.append(r)
            model = os.path.join(workdir, "decoy_%s_%d.pdb" % (str(mag).replace(".", "p"), k))
            RUN.write_pdb([FR.copy_atom(a, chain="A") for a in moved] +
                          [FR.copy_atom(a, chain="B") for a in e3], model)
            d, derr = X.run_dockq(model, ref)
            if derr:
                vals.append({"error": derr})
                continue
            iface, ierr = X.target_e3_interface(d, "A", "B")
            if ierr:
                # No interface left to score IS the reading at large displacement, and it is not a zero
                # DockQ: it is "these two chains no longer touch". Recorded as such.
                vals.append({"no_interface": ierr[:120]})
                continue
            vals.append({"DockQ": iface["DockQ"], "fnat": iface["fnat"], "iRMSD_A": iface["iRMS"]})
        scored = [v["DockQ"] for v in vals if v.get("DockQ") is not None]
        doc["points"].append({
            "requested_rmsd_A": mag,
            "realised_rmsd_A": {"min": min(realised), "max": max(realised)} if realised else None,
            "n_decoys": len(vals), "n_scored": len(scored),
            "n_no_interface": sum(1 for v in vals if v.get("no_interface")),
            "DockQ": ({"min": round(min(scored), 4), "median": round(sorted(scored)[len(scored) // 2], 4),
                       "max": round(max(scored), 4)} if scored else None),
            "detail": vals,
        })
    return doc


def read_cofold_range(path=None):
    """(min, max) DockQ over the committed co-fold measurements — read, never typed."""
    path = path or os.path.join(HERE, "selcal-cofold-dockq.json")
    if not os.path.exists(path):
        return None, "%s absent" % os.path.basename(path)
    vals = [r["dockq"]["DockQ"] for r in json.load(open(path)).get("records", [])
            if r.get("dockq") and r["dockq"].get("DockQ") is not None]
    if not vals:
        return None, "no scored co-fold records in %s" % os.path.basename(path)
    return (round(min(vals), 4), round(max(vals), 4)), None


def interpret(doc):
    """The one sentence the paper can quote, or an honest refusal."""
    rng, rerr = read_cofold_range()
    doc["cofold_DockQ_range"] = rng
    doc["cofold_range_error"] = rerr
    pts = [p for p in doc.get("points", []) if p.get("DockQ")]
    if not pts:
        doc["sentence"] = ("No decoy could be scored, so the scale is UNMEASURED — which is not a statement "
                           "about the co-folds.")
        return doc
    if not rng:
        doc["sentence"] = ("Decoy scale measured, but the co-fold range could not be read (%s), so the two "
                           "are not compared here." % rerr)
        return doc
    hi = rng[1]
    at_or_below = [p for p in pts if p["DockQ"]["median"] <= hi]
    first = min(at_or_below, key=lambda p: p["requested_rmsd_A"]) if at_or_below else None
    doc["displacement_matching_cofolds_A"] = first["requested_rmsd_A"] if first else None
    doc["sentence"] = (
        "Displacing the TRUE target chain of %s by %.1f A rigid RMSD drops DockQ to a median of %.3f — at or "
        "below the best of our 12 co-folds (%.3f-%.3f). So the co-folds are not a near-miss on placement: "
        "they score like the correct structure moved %.0f A."
        % (doc["native"], first["requested_rmsd_A"], first["DockQ"]["median"], rng[0], rng[1],
           first["requested_rmsd_A"])
        if first else
        "Even the largest displacement tested (%.1f A) still scores above our co-folds' best (%.3f), so the "
        "co-folds sit BELOW this whole decoy scale and the scale should be extended before it is quoted."
        % (max(p["requested_rmsd_A"] for p in pts), rng[1]))
    return doc


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Calibrate the DockQ scale with displaced-native decoys ($0).")
    ap.add_argument("--native-dir", default="/tmp/selcal_cofolds/_native")
    ap.add_argument("--pdb", default="9DTY")
    ap.add_argument("--degrader-comp", default=None,
                    help="default: read from selcal_panel.REFERENCE['ligand_ccd']")
    ap.add_argument("--workdir", default="/tmp/selcal_decoys")
    ap.add_argument("--out", default=os.path.join(HERE, "selcal-dockq-decoy-scale.json"))
    args = ap.parse_args(argv)

    import valb_frame_transfer_check as F
    roles, rerr = F.roles_from_selcal_artifact(args.pdb)
    if rerr:
        json.dump({"error": rerr, "native": args.pdb}, open(args.out, "w"), indent=1)
        print("[decoy-scale] REFUSED: %s" % rerr, flush=True)
        return 3

    comp = args.degrader_comp
    if comp is None:
        import selcal_panel as P
        comp = P.REFERENCE["ligand_ccd"]

    native = os.path.join(args.native_dir, "%s.cif" % args.pdb)
    if not os.path.exists(native):
        native = os.path.join(args.native_dir, "%s.pdb" % args.pdb)
    doc = interpret(build_curve(native, comp, roles, args.workdir))
    json.dump(doc, open(args.out, "w"), indent=1)
    for p in doc.get("points", []):
        print("  %6.1f A -> %s  (%d/%d scored, %d with no interface left)"
              % (p["requested_rmsd_A"], p["DockQ"] or "no interface", p["n_scored"], p["n_decoys"],
                 p["n_no_interface"]), flush=True)
    print(doc.get("sentence", doc.get("error", "(nothing)")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
