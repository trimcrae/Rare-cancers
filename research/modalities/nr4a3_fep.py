#!/usr/bin/env python3
"""Selectivity-FEP compute for ONE shard of per-RECEPTOR units — Yank absolute binding FEP, spot-priced, resumable.

Runs inside a SageMaker managed-**spot** Training job (see nr4a3_fep_sagemaker.py). The shard (a JSON list of
per-receptor units from fep_sharding) is read from $FEP_SHARD_FILE; each unit is one complete Yank ABFE
experiment for that receptor (Yank does the two-leg double-decoupling, Boresch restraint + standard-state
correction, auto-trailblazed λ path, Hamiltonian replica exchange, and MBAR internally → ΔG_bind directly).
The per-receptor result marker (dg_bind_kcal) is written to $FEP_CHECKPOINT_DIR, and Yank's own .nc live under
$FEP_CHECKPOINT_DIR/<receptor>/ — both S3-synced (checkpoint_s3_uri), so a spot interruption resumes the Yank
experiment mid-run (resume_simulation) and a re-dispatch skips any receptor whose marker already exists.

TWO modes:
  --smoke : trivial per-receptor stub (no Yank, no heavy env) writing a synthetic ΔG_bind. Validates the spot +
            checkpoint + resume + fan-in plumbing for cents. Used by gpu-fep-aws.yml mode=smoke.
  (real)  : one Yank ABFE experiment per receptor. **First-pass protocol — iteration counts / auto λ-path /
            solvent box are defaults that need a shakeout before the ΔΔG numbers are trusted.** GPU only.

report_fep.py collects the per-receptor ΔG_bind and forms the NR4A3-vs-paralogue ΔΔG (fan-in).
"""
import glob
import json
import os
import sys
import time

SHARD_FILE = os.environ.get("FEP_SHARD_FILE", "")
# Per-unit results are written into the CHECKPOINT dir, which SageMaker syncs continuously to
# checkpoint_s3_uri. So (1) they survive a spot interruption, (2) the reducer reads them directly (no
# model.tar untar), and (3) each result file's existence IS the completion marker used for resume.
CKPT_DIR = os.environ.get("FEP_CHECKPOINT_DIR", "/opt/ml/checkpoints")
LIGAND = os.environ.get("FEP_LIGAND", "denovo_401")
RECEPTOR_DIR = os.environ.get("FEP_RECEPTOR_DIR", ".")        # holds <receptor>-opened.pdb
POSE_DIR = os.environ.get("FEP_POSE_DIR", ".")               # holds docked_<receptor>.sdf
# Yank protocol knobs (SHAKEOUT-CALIBRATED LATER — not trusted numbers yet). Yank iterations, not ps:
PILOT_ITER = int(os.environ.get("FEP_PILOT_ITER", "500"))    # short PILOT (fast early-stop ΔΔG signal)
PROD_ITER = int(os.environ.get("FEP_PROD_ITER", "3000"))     # full production per receptor experiment
N_WINDOWS = int(os.environ.get("FEP_N_WINDOWS", "12"))       # λ-path length inside each Yank experiment
PLATFORM = os.environ.get("FEP_PLATFORM", "OpenCL")          # g5: OpenCL (CUDA PTX dead on this image)


def _phase_of(unit_id):
    """Return the phase ('pilot'|'prod') of an existing result, or None if absent/torn."""
    p = os.path.join(CKPT_DIR, unit_id + ".json")
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p)).get("phase")
    except Exception:  # noqa: BLE001 — torn spot write
        return None


def _write(unit, payload):
    os.makedirs(CKPT_DIR, exist_ok=True)
    rec = {**unit, **payload}
    tmp = os.path.join(CKPT_DIR, unit["id"] + ".json.tmp")
    json.dump(rec, open(tmp, "w"))
    os.replace(tmp, os.path.join(CKPT_DIR, unit["id"] + ".json"))   # atomic: result file == completion marker
    print(f"  [fep] wrote {unit['id']}", flush=True)


def run_smoke(unit, phase="prod"):
    """Trivial, deterministic per-receptor stub — proves orchestration/spot/checkpoint/resume without Yank/MD.
    Synthetic ΔG_bind: NR4A3 tighter (more negative) than the paralogues, so the monitor's ΔΔG early-stop
    gating can be exercised end-to-end without running MD."""
    synth = {"nr4a3": -12.0, "nr4a1": -9.0, "nr4a2": -9.5}
    dg = synth.get(unit["receptor"], -9.0)
    _write(unit, {"mode": "smoke", "phase": phase, "dg_bind_kcal": dg, "ddg_err_kcal": 0.3, "_t": 0.0})


def _extract_ligand_sdf(receptor, workdir):
    """Pull the single LIGAND record out of the multi-molecule docked_<receptor>.sdf into its own SDF (Yank
    wants one ligand per file). SDF records end with a '$$$$' line and start with the molecule title (= the
    RDKit _Name the pose was written with). Text-only (no rdkit dep in the yank env)."""
    src = os.path.join(POSE_DIR, f"docked_{receptor}.sdf")
    if not os.path.exists(src):
        raise FileNotFoundError(f"docked pose sdf not found: {src}")
    rec, cur = [], []
    for line in open(src):
        cur.append(line)
        if line.strip() == "$$$$":
            rec.append("".join(cur)); cur = []
    for block in rec:
        title = block.splitlines()[0].strip()
        if title == LIGAND:
            out = os.path.join(workdir, "lig.sdf")
            open(out, "w").write(block if block.endswith("\n") else block + "\n")
            return out
    have = [b.splitlines()[0].strip() for b in rec][:8]
    raise ValueError(f"ligand '{LIGAND}' not in {src} (have: {have})")


def _sdf_to_mol2(sdf, workdir):
    """Convert the ligand SDF → MOL2 via antechamber. Yank's SDF reader needs the commercial OpenEye toolkit
    ('Cannot support sdf files without OpenEye OEChem'); its MOL2 path uses AmberTools only. antechamber writes
    scratch files in cwd, so run it there. No charges here — Yank's `antechamber: {charge_method: bcc}` block
    computes AM1-BCC charges + parmchk frcmod at setup."""
    import subprocess
    mol2 = os.path.join(workdir, "lig.mol2")
    r = subprocess.run(["antechamber", "-i", sdf, "-fi", "sdf", "-o", mol2, "-fo", "mol2", "-dr", "no"],
                       cwd=workdir, capture_output=True, text=True, timeout=600)
    if not os.path.exists(mol2):
        raise RuntimeError(f"antechamber sdf->mol2 failed (rc={r.returncode}):\n"
                           f"{(r.stdout or '')[-600:]}\n{(r.stderr or '')[-600:]}")
    return mol2


def _yank_yaml(receptor, n_iter, out_dir, lig_sdf, rec_pdb):
    """A Yank absolute-binding-FEP YAML for one receptor. Yank owns the physics: explicit-solvent (PME) double-
    decoupling, a Boresch orientational restraint + its standard-state correction, an auto-trailblazed λ path,
    Hamiltonian replica exchange, and MBAR. `resume_*: yes` makes Yank resume from its own .nc checkpoints under
    out_dir (which lives in the SageMaker checkpoint dir → S3-synced → spot-interruption-safe)."""
    return f"""---
options:
  minimize: yes
  verbose: no
  output_dir: {out_dir}
  temperature: 300*kelvin
  pressure: 1*atmosphere
  default_number_of_iterations: {n_iter}
  default_nsteps_per_iteration: 500
  checkpoint_interval: 50
  platform: {PLATFORM}
  resume_setup: yes
  resume_simulation: yes
molecules:
  lig:
    filepath: {lig_sdf}
    antechamber:
      charge_method: bcc
  rec:
    filepath: {rec_pdb}
solvents:
  pme:
    nonbonded_method: PME
    clearance: 12*angstroms
    nonbonded_cutoff: 9*angstroms
    switch_distance: 8*angstroms
    ewald_error_tolerance: 1.0e-4
    positive_ion: Na+
    negative_ion: Cl-
systems:
  binding:
    receptor: rec
    ligand: lig
    solvent: pme
    leap:
      parameters: [leaprc.protein.ff14SB, leaprc.gaff2, leaprc.water.tip3p]
protocols:
  abfe:
    complex:
      alchemical_path: auto
    solvent:
      alchemical_path: auto
experiments:
  system: binding
  protocol: abfe
  restraint:
    type: Boresch
"""


def _parse_dg(out_dir):
    """ΔG_bind (kcal/mol) + stderr from a finished Yank experiment. Runs `yank analyze` and parses the binding
    free energy line; more negative = tighter binding."""
    import re
    import subprocess
    store = os.path.join(out_dir, "experiments")
    r = subprocess.run(["yank", "analyze", "--store", store], capture_output=True, text=True, timeout=1800)
    txt = (r.stdout or "") + "\n" + (r.stderr or "")
    # Yank prints e.g. "Free energy of binding: -8.42 +- 0.55 kcal/mol"
    m = re.search(r"free energy of binding[:\s]+(-?\d+\.?\d*)\s*(?:\+/-|\+-|±)\s*(\d+\.?\d*)\s*kcal", txt, re.I)
    if not m:
        m = re.search(r"binding[^\n]*?(-?\d+\.\d+)\s*(?:\+/-|\+-|±)\s*(\d+\.\d+)\s*kcal", txt, re.I)
    if not m:
        raise ValueError(f"could not parse ΔG_bind from yank analyze output:\n{txt[-1500:]}")
    return float(m.group(1)), float(m.group(2))


def run_real(unit, phase="prod"):
    """One full Yank absolute-binding-FEP experiment for ONE receptor → ΔG_bind. phase='pilot' runs fewer
    iterations for a fast early-stop ΔΔG signal; 'prod' extends the SAME output dir to the full iteration
    count (Yank resume = extend). GPU only (runs inside the fep conda env; `yank` CLI on PATH)."""
    import subprocess
    t0 = time.time()
    receptor = unit["receptor"]
    n_iter = PILOT_ITER if phase == "pilot" else PROD_ITER
    out_dir = os.path.join(CKPT_DIR, receptor)                # Yank's .nc live here → S3-synced → resumable
    os.makedirs(out_dir, exist_ok=True)
    lig_sdf = _extract_ligand_sdf(receptor, out_dir)
    lig_mol2 = _sdf_to_mol2(lig_sdf, out_dir)                 # Yank needs MOL2 (SDF reader wants OpenEye)
    rec_pdb = os.path.join(RECEPTOR_DIR, f"{receptor}-opened.pdb")
    if not os.path.exists(rec_pdb):
        raise FileNotFoundError(f"receptor pdb not found: {rec_pdb}")
    yaml_path = os.path.join(out_dir, "experiment.yaml")
    open(yaml_path, "w").write(_yank_yaml(receptor, n_iter, out_dir, lig_mol2, rec_pdb))
    print(f"[fep] {receptor} {phase}: yank script ({n_iter} iters, platform {PLATFORM})", flush=True)
    r = subprocess.run(["yank", "script", "--yaml", yaml_path])
    if r.returncode != 0:
        raise RuntimeError(f"yank script failed for {receptor} (rc={r.returncode})")
    dg, err = _parse_dg(out_dir)
    _write(unit, {"mode": "yank", "phase": phase, "dg_bind_kcal": round(dg, 3),
                  "ddg_err_kcal": round(err, 3), "n_iterations": n_iter, "_t": round(time.time() - t0, 1)})
    print(f"[fep] {receptor} {phase}: ΔG_bind = {dg:.2f} ± {err:.2f} kcal/mol", flush=True)


def main():
    smoke = "--smoke" in sys.argv
    run = run_smoke if smoke else run_real
    if not SHARD_FILE or not os.path.exists(SHARD_FILE):
        sys.exit(f"[fep] FEP_SHARD_FILE not found: {SHARD_FILE}")
    units = json.load(open(SHARD_FILE))
    # PASS 1 — PILOT each receptor first (few iterations), so the central monitor gets an early ΔΔG signal
    # across ALL receptors fast and can StopTrainingJob the fleet before full production burns the spot budget.
    pilot_todo = [u for u in units if _phase_of(u["id"]) is None]      # neither pilot nor prod yet
    print(f"[fep] PASS 1 pilot: {len(pilot_todo)}/{len(units)} receptors (mode={'smoke' if smoke else 'yank'})",
          flush=True)
    for u in pilot_todo:
        run(u, phase="pilot")
    # PASS 2 — full PRODUCTION (Yank extends the same output dir). Resume/interruption: skip receptors at prod.
    prod_todo = [u for u in units if _phase_of(u["id"]) != "prod"]
    print(f"[fep] PASS 2 production: {len(prod_todo)}/{len(units)} receptors", flush=True)
    for u in prod_todo:
        run(u, phase="prod")
    print(f"[fep] shard complete: pilots {len(pilot_todo)}, productions {len(prod_todo)}", flush=True)


if __name__ == "__main__":
    main()
