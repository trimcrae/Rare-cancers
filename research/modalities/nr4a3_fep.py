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
    """Convert the ligand SDF → MOL2 **adding explicit hydrogens** via OpenBabel. The docked pose is
    heavy-atom-only (no H); AmberTools antechamber (which Yank runs at setup) then mistypes carbons as sp
    (`c1`) and dies with 'Weird atomic valence ... Possible open valence'. `obabel -h` adds Hs at their
    geometric positions while KEEPING the docked heavy-atom coordinates (so the binding pose is preserved),
    and writes a MOL2 (Yank's SDF reader needs OpenEye; MOL2 path is AmberTools-only). Yank's
    `antechamber: {charge_method: bcc}` block then computes AM1-BCC charges + parmchk frcmod at setup."""
    import subprocess
    mol2 = os.path.join(workdir, "lig.mol2")
    r = subprocess.run(["obabel", sdf, "-O", mol2, "-h"],
                       cwd=workdir, capture_output=True, text=True, timeout=600)
    if not os.path.exists(mol2):
        raise RuntimeError(f"obabel sdf->mol2 (+H) failed (rc={r.returncode}):\n"
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
    solvent_model: tip3p
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


def _residues_in_order(pdb_in):
    """[(reskey, [atom_lines])] in file order + {reskey: CA_xyz}, over ATOM (protein) records only."""
    order, atoms, ca = [], {}, {}
    for line in open(pdb_in):
        if line.startswith("ATOM"):
            key = (line[21:22], line[22:27])
            if key not in atoms:
                order.append(key)
                atoms[key] = []
            atoms[key].append(line)
            if line[12:16].strip() == "CA":
                try:
                    ca[key] = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
                except ValueError:
                    pass
    return order, atoms, ca


def _trim_floppy_termini(pdb_in, workdir, margin=8.0, min_thresh=25.0, max_trim_frac=0.35):
    """Trim disordered N/C-terminal tails that flap far from the folded core, so the explicit-solvent box is not
    ballooned by a hinge. JUSTIFIED by the fold-sanity check (`nr4a3_frame_sanity.py`): the opened frame's CORE
    is intact — helix content retained (retention ~1.01 vs the AF2 LBD) and core CA-RMSD ~1.76 Å — so the ~99 Å
    elongation is a floppy terminal hinge, not a melt; ABFE is properly run on the folded LBD, not a disordered
    tail. Adaptive per receptor: a core centroid from the interior residues, then trim CONTIGUOUS terminal
    residues whose CA lies beyond (85th-pct core radius + margin). The pocket is interior and never trimmed. A
    guard refuses to trim >max_trim_frac of the chain (falls back to untrimmed), so this can only help."""
    import math
    order, atoms, ca = _residues_in_order(pdb_in)
    cas = [ca[k] for k in order if k in ca]
    n = len(order)
    if len(cas) < 20:
        return pdb_in
    lo, hi = int(0.15 * len(cas)), int(0.85 * len(cas))
    interior = cas[lo:hi] or cas
    cx = sum(p[0] for p in interior) / len(interior)
    cy = sum(p[1] for p in interior) / len(interior)
    cz = sum(p[2] for p in interior) / len(interior)

    def dist(p):
        return math.sqrt((p[0] - cx) ** 2 + (p[1] - cy) ** 2 + (p[2] - cz) ** 2)

    ds = sorted(dist(p) for p in interior)
    core_r = ds[int(0.85 * (len(ds) - 1))]
    thresh = max(core_r + margin, min_thresh)
    keep_lo = 0
    for i, k in enumerate(order):
        if k in ca and dist(ca[k]) > thresh:
            keep_lo = i + 1
        else:
            break
    keep_hi = n - 1
    for i in range(n - 1, -1, -1):
        k = order[i]
        if k in ca and dist(ca[k]) > thresh:
            keep_hi = i - 1
        else:
            break
    cap = int(max_trim_frac * n)
    total_trim = keep_lo + (n - 1 - keep_hi)
    if keep_hi <= keep_lo or keep_lo > cap or (n - 1 - keep_hi) > cap or total_trim > cap:
        print(f"[fep] trim guard tripped (keep {keep_lo}..{keep_hi} of {n}, total_trim={total_trim}>{cap}); "
              "using untrimmed receptor", flush=True)
        return pdb_in
    if keep_lo == 0 and keep_hi == n - 1:
        return pdb_in                                          # nothing floppy to trim
    kept = order[keep_lo:keep_hi + 1]
    out = os.path.join(workdir, "rec_trim.pdb")
    with open(out, "w") as f:
        for k in kept:
            for ln in atoms[k]:
                f.write(ln)
        f.write("TER\nEND\n")
    print(f"[fep] trimmed floppy termini: kept residues {keep_lo + 1}..{keep_hi + 1} of {n} "
          f"(dropped {keep_lo} N-term + {n - 1 - keep_hi} C-term; core_r={core_r:.1f} thresh={thresh:.1f} Å)",
          flush=True)
    return out


def _prep_receptor(rec_pdb, workdir):
    """Clean the MD/AlphaFold-derived receptor PDB for LEaP with pdb4amber (AmberTools, present in the fep env).
    The docked ligand-only 'solvent' leg builds fine, but the 'complex' leg (which adds this receptor) dies in
    tleap with exit 31 — the classic raw-MD/AF-PDB → LEaP breakage: MD hydrogens whose names don't match the
    ff14SB templates, plus any crystallographic waters/ions/HETATM. pdb4amber strips hydrogens (LEaP re-adds
    ff14SB-correct ones), drops waters/ions (--dry), adds TER at chain breaks, and renames to Amber conventions;
    its report (renamed/missing atoms) is printed for diagnosis. Falls back to the raw PDB if pdb4amber is
    unavailable or produces nothing, so this can only help."""
    import subprocess
    rec_pdb = _trim_floppy_termini(rec_pdb, workdir)          # drop disordered hinge → compact box (fits g5.xlarge)
    out = os.path.join(workdir, "rec_clean.pdb")
    try:
        r = subprocess.run(["pdb4amber", "-i", rec_pdb, "-o", out, "--dry", "--nohyd"],
                           capture_output=True, text=True, timeout=600)
    except FileNotFoundError:
        print(f"[fep] pdb4amber not on PATH; using raw receptor {rec_pdb}", flush=True)
        return rec_pdb
    print(f"[fep] pdb4amber prep {rec_pdb} (rc={r.returncode}):\n"
          f"{(r.stdout or '')[-1200:]}\n{(r.stderr or '')[-2500:]}", flush=True)
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return out
    print("[fep] pdb4amber produced no output; falling back to raw receptor", flush=True)
    return rec_pdb


def _dump_setup_logs(out_dir):
    """On a `yank script` failure, Yank's own error is an opaque wrapper (e.g. 'Solvent pme: Some things went
    wrong with LEaP') — the ACTUAL diagnostic (the missing GAFF parameter, the atom-valence complaint, the
    antechamber/parmchk stderr) lives in per-leg log FILES under the setup tree, NOT in stdout. Glob every
    LEaP/antechamber/tleap log Yank wrote and echo its tail to stdout so the real cause is visible in the job's
    CloudWatch/`get_job_logs` output — one dispatch reveals the error instead of a round-trip to fish the file
    out of S3. Pure diagnostics; never raises."""
    pats = ["**/*.leap.log", "**/leap.log", "**/*leap*.log", "**/*.ac.log", "**/*antechamber*",
            "**/tleap.in", "**/*.frcmod"]
    seen = set()
    for pat in pats:
        for f in sorted(glob.glob(os.path.join(out_dir, pat), recursive=True)):
            if f in seen or not os.path.isfile(f):
                continue
            seen.add(f)
            try:
                txt = open(f, errors="replace").read()
            except Exception as e:  # noqa: BLE001
                print(f"  [leap-log] (could not read {f}: {e})", flush=True)
                continue
            print(f"\n===== SETUP LOG {f} ({len(txt)} bytes) =====", flush=True)
            print(txt[-4000:], flush=True)
    if not seen:
        print(f"  [leap-log] no setup logs found under {out_dir} (setup failed before writing any)", flush=True)


# Yank's trailblaze phase writes its λ-path checkpoint NON-atomically: a spot interruption DURING that write
# corrupts the .nc so yank refuses to resume ("The trailblaze algorithm was interrupted while writing the
# checkpoint file and it is now unable to resume. Please delete the files in .../<receptor>/experiments/").
# Confirmed on the nr4a1 shard, 2026-07-03. The remediation yank itself prescribes — delete the experiments/
# store and restart — is safe because system SETUP (molecules/, systems/) lives OUTSIDE experiments/ and is
# preserved, so only the alchemical sampling restarts (short trailblaze + iterations since the last good
# checkpoint). We do it automatically so a spot kill self-heals inside the same job instead of bricking the
# shard. This is the documented spot-exception handling, not a reason to abandon spot.
_TRAILBLAZE_CORRUPT = ("trailblaze algorithm was interrupted", "unable to resume")


def _run_yank_resilient(receptor, yaml_path, out_dir, max_restarts=1):
    """Run `yank script`, streaming to console AND capturing to yank_run.log (S3-synced, tail-able via the
    status tool). On a trailblaze-checkpoint corruption (spot-kill mid-write), clear only <out_dir>/experiments/
    and retry once with a fresh trailblaze — setup is preserved. Returns the final return code."""
    import subprocess
    log_path = os.path.join(out_dir, "yank_run.log")
    attempts = 0
    while True:
        attempts += 1
        with open(log_path, "w") as fh:
            r = subprocess.Popen(["yank", "script", "--yaml", yaml_path],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in r.stdout:                             # tee: live console + on-disk (S3-synced) capture
                sys.stdout.write(line)
                fh.write(line)
            r.wait()
        if r.returncode == 0:
            return 0
        try:
            tail = open(log_path, errors="replace").read()[-8000:].lower()
        except Exception:  # noqa: BLE001
            tail = ""
        corrupt = all(s in tail for s in _TRAILBLAZE_CORRUPT)
        exp = os.path.join(out_dir, "experiments")
        if corrupt and attempts <= max_restarts and os.path.isdir(exp):
            print(f"[fep] {receptor}: trailblaze checkpoint corrupted by a spot interruption — clearing "
                  f"{exp} and restarting the alchemical phase fresh (setup preserved; attempt {attempts}).",
                  flush=True)
            import shutil
            shutil.rmtree(exp, ignore_errors=True)
            continue
        return r.returncode


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
    rec_pdb = _prep_receptor(rec_pdb, out_dir)                 # clean MD/AF PDB for LEaP (complex-leg fix)
    yaml_path = os.path.join(out_dir, "experiment.yaml")
    open(yaml_path, "w").write(_yank_yaml(receptor, n_iter, out_dir, lig_mol2, rec_pdb))
    print(f"[fep] {receptor} {phase}: yank script ({n_iter} iters, platform {PLATFORM})", flush=True)
    rc = _run_yank_resilient(receptor, yaml_path, out_dir)
    if rc != 0:
        _dump_setup_logs(out_dir)                             # surface the real LEaP/antechamber diagnostic
        raise RuntimeError(f"yank script failed for {receptor} (rc={rc})")
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
