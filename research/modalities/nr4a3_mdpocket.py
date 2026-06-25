#!/usr/bin/env python3
"""
Cryptic-pocket analysis of the NR4A3 LBD MD trajectory (post-processing for GPU experiment #1).

The "NR4A3 is undruggable" verdict rests on the orthosteric (Pocket-5) site being *collapsed* in a
single static AF2 model. This quantifies whether that site **opens** during the MD two ways:

  1. SASA of the Pocket-5 lining residues (406-534) per frame (mdtraj shrake_rupley). A transient
     rise above the static-model baseline is the cryptic-pocket signal — solvent reaching into a
     site that was closed in the AF2 snapshot.
  2. (best-effort) mdpocket transient-pocket density at the site, if the fpocket/mdpocket binary is
     present — the gold-standard map of where/when a pocket exists across the trajectory.

Inputs (env INPUT_DIR, default /opt/ml/processing/input): nr4a3-lbd-solvated.pdb + nr4a3-lbd-md.dcd
(produced by nr4a3_md.py). Outputs (env OUTPUT_DIR, default /opt/ml/processing/output): a summary
JSON, the per-frame SASA array, a SASA-vs-time plot, and any mdpocket grids.
"""
import json
import os
import shutil
import subprocess
import sys

LBD_FIRST = 373                               # AF2 LBD start (the trim used in nr4a3_md.py)
POCKET_FIRST, POCKET_LAST = 406, 534          # Pocket-5 lining span (nr4a3-degrader-design-spec.md)
NS_PER_FRAME = 0.05                            # DCDReporter wrote every 25000 steps * 2 fs = 50 ps
IN = os.environ.get("INPUT_DIR", "/opt/ml/processing/input")
OUT = os.environ.get("OUTPUT_DIR", "/opt/ml/processing/output")


def main():
    import numpy as np
    import mdtraj as md

    top = os.path.join(IN, "nr4a3-lbd-solvated.pdb")
    dcd = os.path.join(IN, "nr4a3-lbd-md.dcd")
    for p in (top, dcd):
        if not os.path.exists(p):
            sys.exit(f"  ABORT: missing input {p} (expected the MD outputs mounted at INPUT_DIR)")
    os.makedirs(OUT, exist_ok=True)

    print(f"  loading {dcd}", flush=True)
    t = md.load(dcd, top=top)
    prot = t.atom_slice(t.topology.select("protein"))      # strip water/ions
    print(f"  frames={t.n_frames} atoms={t.n_atoms} protein_atoms={prot.n_atoms}", flush=True)

    # Map Pocket-5 onto the trajectory residues via the unit-tested resolver (handles the solvated
    # PDB being renumbered from 1 vs. preserving AF2 numbering — see residue_map.py).
    import residue_map as rm
    prot_residues = list(prot.topology.residues)
    resseqs = [r.resSeq for r in prot_residues]
    pocket_pos, numbering = rm.resolve_positions(resseqs, range(POCKET_FIRST, POCKET_LAST + 1), LBD_FIRST)
    print(f"  residue numbering: {numbering} (resSeq {min(resseqs)}..{max(resseqs)}); "
          f"pocket residues matched: {len(pocket_pos)}", flush=True)
    if not pocket_pos:
        sys.exit(f"  ABORT: could not map Pocket-5 residues {POCKET_FIRST}-{POCKET_LAST} onto the "
                 f"{len(prot_residues)} protein residues (resSeq {min(resseqs)}..{max(resseqs)})")

    # Per-residue SASA, summed over the pocket-lining residues -> one value per frame (nm^2).
    sasa_res = md.shrake_rupley(prot, mode="residue")
    pocket_sasa = sasa_res[:, pocket_pos].sum(axis=1)
    np.save(os.path.join(OUT, "pocket_sasa_nm2.npy"), pocket_sasa)

    time_ns = np.arange(t.n_frames, dtype=float) * NS_PER_FRAME
    baseline = float(pocket_sasa[0])                       # frame 0 ~ the (minimized) static model
    opening = pocket_sasa - baseline
    summary = {
        "frames": int(t.n_frames),
        "ns_per_frame": NS_PER_FRAME,
        "pocket_residue_range": [POCKET_FIRST, POCKET_LAST],
        "residue_numbering": numbering,
        "pocket_residues_matched": len(pocket_pos),
        "pocket_sasa_nm2": {
            "baseline_frame0": baseline,
            "min": float(pocket_sasa.min()),
            "max": float(pocket_sasa.max()),
            "mean": float(pocket_sasa.mean()),
            "std": float(pocket_sasa.std()),
        },
        "opening_vs_baseline_nm2": {
            "max_increase": float(opening.max()),
            "frac_frames_more_open": float((opening > 0).mean()),
        },
        "interpretation": (
            "A sustained/transient max_increase well above thermal noise (std) indicates the "
            "Pocket-5 site opening beyond the static AF2 snapshot — the cryptic-pocket signal."
        ),
    }

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.figure(figsize=(8, 4))
        plt.plot(time_ns, pocket_sasa, lw=0.8)
        plt.axhline(baseline, color="k", ls="--", lw=0.7, label="frame-0 baseline")
        plt.xlabel("time (ns)")
        plt.ylabel("Pocket-5 SASA (nm$^2$)")
        plt.title(f"NR4A3 LBD Pocket-5 (res {POCKET_FIRST}-{POCKET_LAST}) SASA over MD")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(OUT, "pocket_sasa.png"), dpi=130)
    except Exception as e:  # noqa: BLE001 — plot is a nicety, don't fail the job on it
        print(f"  plot skipped: {e}", file=sys.stderr)

    summary["mdpocket"] = _mdpocket_best_effort(top, dcd)

    with open(os.path.join(OUT, "pocket_analysis_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print("  SUMMARY:", json.dumps(summary["pocket_sasa_nm2"]),
          json.dumps(summary["opening_vs_baseline_nm2"]), flush=True)


def _mdpocket_best_effort(top, dcd):
    """Run mdpocket if available; never fail the job on it (the SASA result stands alone)."""
    if not shutil.which("mdpocket"):
        return {"ran": False, "reason": "mdpocket binary not on PATH"}
    try:
        r = subprocess.run(
            ["mdpocket", "--trajectory_file", dcd, "--trajectory_format", "dcd", "-f", top],
            cwd=OUT, capture_output=True, text=True, timeout=3600)
        return {"ran": True, "returncode": r.returncode,
                "stdout_tail": r.stdout[-1500:], "stderr_tail": r.stderr[-1500:]}
    except Exception as e:  # noqa: BLE001
        return {"ran": False, "reason": str(e)}


if __name__ == "__main__":
    main()
