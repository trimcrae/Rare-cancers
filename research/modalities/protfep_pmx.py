#!/usr/bin/env python3
"""GPU driver for ONE alchemical protein point-mutation leg — pmx + GROMACS route.

This replaces `protfep_run.py` (perses/OpenMM), which cannot run here: perses builds the old->new
residue atom map through a commercial, licence-gated OpenEye toolkit. See
`protfep-pmx-plan.md` for the evidence and the decision. Everything AROUND this file is unchanged —
`protfep_bench.py` stages the legs and holds the SKEMPI-verified references, `protfep_reduce.py`
turns legs into a verdict and a price — because only the build/sample layer was ever engine-specific.

WHAT ONE LEG IS (identical quantity, different machinery)
---------------------------------------------------------
One leg = one alchemical residue mutation (WT -> mutant) in ONE environment, sampled across
`n_states` lambda windows, reduced to a single dG. Two legs (complex, apo) make the cycle, and
`protfep_reduce.ddg_for` subtracts them. That is the same quantity `nr4a3_protein_fep` defines for
the wedge; only the engine underneath changed.

THE PIPELINE, and why each step is where it is
-----------------------------------------------
    pmx mutate      -> hybrid structure carrying BOTH residue identities
    gmx pdb2gmx     -> topology, using pmx's MUTATION force field (hybrid residues live there)
    pmx gentop      -> promotes the topology to a real A->B alchemical topology
    gmx editconf/solvate/genion -> periodic box, water, neutralising ions
    minimise -> NVT -> NPT      -> a relaxed physical system BEFORE any alchemy is switched on
    N lambda windows            -> the alchemical sampling
    gmx bar                     -> BAR estimate of dG with its error

The pre-alchemy equilibration is deliberate and is the ternary lane's hard-won lesson: a softcore
region started from an unrelaxed structure is where this repo has repeatedly hit NaNs, and plain-MD
pre-equilibration — not a smaller timestep — is what actually fixed it.

EQUILIBRIUM LAMBDA WINDOWS, NOT NON-EQUILIBRIUM — A DELIBERATE CHOICE, RECORDED
-------------------------------------------------------------------------------
pmx's *published* protocol is non-equilibrium (fast growth + Crooks/BAR). This driver runs
EQUILIBRIUM lambda windows reduced with BAR instead, for two operational reasons: a window is a
natural checkpoint unit on a preemptible spot host (GROMACS writes .cpt and `gmx mdrun -cpi` resumes
mid-window), and the control flow is simple enough to debug from a log. The two protocols are NOT
interchangeable when quoting a number, so `protocol` is stamped into every leg JSON. If convergence
is poor or the cost is unattractive, non-equilibrium is the documented fallback and pmx ships
estimators for both.

CHECKPOINTING
-------------
Two levels, because a spot host can vanish at any moment: GROMACS `-cpi/-cpo` resumes an interrupted
window from its own checkpoint, and a finished window is never re-run (its .xvg is the record). The
leg JSON is rewritten after every window, so a preempted leg leaves a readable partial rather than a
directory of binaries.
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import md_settings  # noqa: E402
import nr4a3_protein_fep as pf  # noqa: E402
import protfep_bench as bench  # noqa: E402

# ---- lane settings (env-overridable; these defaults ARE the recipe) ------------------------------
N_STATES = int(os.environ.get("PMX_N_STATES") or "16")
# pmx ships hybrid residue definitions only for ITS mutation force fields; a stock GROMACS ff cannot
# express an A->B residue at all, so this is not a free choice.
FORCEFIELD = os.environ.get("PMX_FORCEFIELD") or "amber99sb-star-ildn-mut"
WATER_MODEL = os.environ.get("PMX_WATER") or "tip3p"
BOX_NM = float(os.environ.get("PMX_BOX_NM") or md_settings.SOLVENT_PADDING_NM)
IONIC_M = float(os.environ.get("PMX_IONIC_M") or md_settings.IONIC_STRENGTH_M)
TEMPERATURE_K = float(os.environ.get("PMX_TEMPERATURE_K") or md_settings.TEMPERATURE_K)
TIMESTEP_FS = float(os.environ.get("PMX_TIMESTEP_FS") or "2.0")
EQUIL_PS = float(os.environ.get("PMX_EQUIL_PS") or "100")     # per window, before data collection
PROD_PS = float(os.environ.get("PMX_PROD_PS") or "2000")      # per window
MIN_STEPS = int(os.environ.get("PMX_MIN_STEPS") or "5000")
NVT_PS = float(os.environ.get("PMX_NVT_PS") or "100")         # system-level, once
NPT_PS = float(os.environ.get("PMX_NPT_PS") or "200")         # system-level, once
GMX = os.environ.get("GMX_BIN") or "gmx"
NT = os.environ.get("PMX_NT") or ""                           # blank = let GROMACS decide


def _log(msg):
    print(f"[pmx] {time.strftime('%H:%M:%S')} {msg}", flush=True)


def run(cmd, cwd=None, stdin_text=None, check=True, timeout=None):
    """Run a shell command, streaming its tail into the log on failure. Returns CompletedProcess.

    GROMACS failures are verbose and the useful line is usually near the end, so a failed step must
    surface that tail rather than an exit code — on a rented host, an opaque non-zero exit is another
    paid round trip.
    """
    _log("$ " + (" ".join(cmd) if isinstance(cmd, list) else str(cmd)))
    proc = subprocess.run(cmd, cwd=cwd, input=stdin_text, capture_output=True, text=True,
                          shell=isinstance(cmd, str), timeout=timeout)
    if proc.returncode != 0:
        tail = (proc.stdout or "")[-1500:] + "\n--- stderr ---\n" + (proc.stderr or "")[-2500:]
        _log(f"FAILED rc={proc.returncode}\n{tail}")
        if check:
            raise RuntimeError(f"command failed (rc={proc.returncode}): "
                               f"{cmd if isinstance(cmd, str) else ' '.join(cmd)}\n{tail[-1200:]}")
    return proc


def assert_gpu_gromacs():
    """Refuse to run a rented-GPU leg on a CPU-only GROMACS.

    Same reasoning as the perses lane's require_cuda_platform(): a CPU build still produces a dG, it
    just costs ~50x the rental to get there and nothing in the result says why. The image asserts
    this at bake time too; this is the runtime half, because the image is not the only way a leg can
    end up on the wrong binary.
    """
    out = run([GMX, "--version"], check=False).stdout or ""
    has_cuda = "GPU support:" in out and "CUDA" in out.split("GPU support:")[1][:40]
    if not has_cuda:
        msg = ("GROMACS reports no CUDA GPU support. Refusing to run a rented-GPU leg on a CPU build "
               "— it would produce a dG at ~50x the cost with nothing in the result to show for it. "
               "Set PMX_ALLOW_CPU=1 only for a deliberate CPU test.")
        if os.environ.get("PMX_ALLOW_CPU") != "1":
            raise RuntimeError(msg)
        _log(f"WARNING {msg} — proceeding because PMX_ALLOW_CPU=1")
        return "CPU"
    version = next((ln for ln in out.splitlines() if ln.strip().startswith("GROMACS version")), "?")
    _log(f"GROMACS with CUDA confirmed ({version.strip()})")
    return "CUDA"


# ------------------------------------------------------------------------------------------------
# mdp generation
# ------------------------------------------------------------------------------------------------
def lambda_vector(n_states):
    """Evenly spaced lambda points as a GROMACS mdp string. Pure.

    One vector drives all of coul/vdw/bonded simultaneously. That is the simple choice; if the
    overlap diagnostic shows a bottleneck, the remedy is more windows or a staged (coul-then-vdw)
    schedule, and the leg JSON records which was used.
    """
    if n_states < 2:
        raise ValueError("n_states must be >= 2")
    return " ".join(f"{i / (n_states - 1):.4f}" for i in range(n_states))


def _base_mdp(nsteps, dt_ps, extra):
    common = {
        "integrator": "md",
        "dt": f"{dt_ps}",
        "nsteps": str(int(nsteps)),
        "constraints": "h-bonds",
        "constraint-algorithm": "lincs",
        "cutoff-scheme": "Verlet",
        "coulombtype": "PME",
        "rcoulomb": f"{md_settings.NONBONDED_CUTOFF_NM}",
        "rvdw": f"{md_settings.NONBONDED_CUTOFF_NM}",
        "DispCorr": "EnerPres",
        "tcoupl": "v-rescale",
        "tc-grps": "System",
        "tau-t": "1.0",
        "ref-t": f"{TEMPERATURE_K}",
        "pbc": "xyz",
        "nstlist": "20",
    }
    common.update(extra)
    return "\n".join(f"{k} = {v}" for k, v in common.items()) + "\n"


def mdp_minimise():
    return ("integrator = steep\n"
            f"nsteps = {MIN_STEPS}\n"
            "emtol = 100.0\n"
            "cutoff-scheme = Verlet\n"
            "coulombtype = PME\n"
            f"rcoulomb = {md_settings.NONBONDED_CUTOFF_NM}\n"
            f"rvdw = {md_settings.NONBONDED_CUTOFF_NM}\n"
            "pbc = xyz\n")


def mdp_equil(ps, pressure):
    """NVT (pressure=False) or NPT (pressure=True) equilibration of the PHYSICAL system.

    Run before any alchemy is switched on. The ternary lane's diagnosis was that softcore instability
    comes from an unrelaxed starting structure, and that plain-MD pre-equilibration — not a smaller
    timestep — is the fix that actually worked.
    """
    dt_ps = TIMESTEP_FS / 1000.0
    extra = {"gen-vel": "yes" if not pressure else "no",
             "gen-temp": f"{TEMPERATURE_K}", "gen-seed": "-1",
             "nstenergy": "1000", "nstlog": "1000"}
    if pressure:
        extra.update({"pcoupl": "C-rescale", "pcoupltype": "isotropic",
                      "tau-p": "2.0", "ref-p": "1.0", "compressibility": "4.5e-5",
                      "continuation": "yes"})
    else:
        extra.update({"pcoupl": "no"})
    return _base_mdp(ps / dt_ps, dt_ps, extra)


def mdp_lambda_window(state_index, n_states, ps, collect_data):
    """One alchemical window.

    `calc-lambda-neighbors = -1` makes GROMACS write dH to EVERY other lambda, which is what BAR
    (and MBAR, if we ever want it) needs. `couple-intramol = no` keeps intramolecular interactions
    of the perturbed group intact — the standard choice for a residue mutation, where the mutated
    side chain is not being decoupled from its own protein.
    """
    dt_ps = TIMESTEP_FS / 1000.0
    vec = lambda_vector(n_states)
    extra = {
        "free-energy": "yes",
        "init-lambda-state": str(int(state_index)),
        "fep-lambdas": vec,
        "mass-lambdas": vec,
        "calc-lambda-neighbors": "-1",
        "sc-alpha": "0.3",
        "sc-power": "1",
        "sc-sigma": "0.25",
        "couple-intramol": "no",
        "nstdhdl": "100" if collect_data else "0",
        "dhdl-print-energy": "total",
        "pcoupl": "C-rescale", "pcoupltype": "isotropic",
        "tau-p": "2.0", "ref-p": "1.0", "compressibility": "4.5e-5",
        "continuation": "yes", "gen-vel": "no",
        "nstenergy": "1000", "nstlog": "5000",
    }
    return _base_mdp(ps / dt_ps, dt_ps, extra)


# ------------------------------------------------------------------------------------------------
# System construction
# ------------------------------------------------------------------------------------------------
def build_system(structure_path, mutation_spec, work_dir):
    """pmx mutate -> pdb2gmx -> pmx gentop -> box/solvate/ions -> minimise -> NVT -> NPT.

    Returns (npt_gro, hybrid_top, n_atoms). Everything up to the alchemy is plain CPU/GPU MD setup
    and is exactly what the free CI build-test exercises — the point being that a GPU is rented only
    once a hybrid system demonstrably builds.
    """
    os.makedirs(work_dir, exist_ok=True)
    m = pf.classify_mutation(mutation_spec)
    if not m["buildable"]:
        raise pf.MutationError(m["risk"])

    env = dict(os.environ)
    # pmx's hybrid residue library lives inside the package; GROMACS finds a force field by GMXLIB.
    import pmx
    pmx_data = os.path.join(os.path.dirname(pmx.__file__), "data", "mutff")
    if os.path.isdir(pmx_data):
        env["GMXLIB"] = pmx_data + (":" + env["GMXLIB"] if env.get("GMXLIB") else "")
        _log(f"GMXLIB -> {pmx_data}")
    else:
        _log(f"NOTE pmx mutation force fields not at {pmx_data}; relying on the default GMXLIB")

    mutant = os.path.join(work_dir, "mutant.pdb")
    # pmx's Python API is used rather than the CLI so the mutation is specified programmatically —
    # the CLI is interactive and would need a fragile stdin script.
    from pmx import Model
    from pmx.alchemy import mutate as pmx_mutate
    model = Model(structure_path, rename_atoms=True)

    # THE CHAIN MUST BE PASSED, AND THE RESULT MUST BE CHECKED.
    # In the COMPLEX leg both chains carry a residue 29 (barnase 1-110, barstar 1-89), so a
    # chain-blind mutate could perturb the wrong protein and return a perfectly converged, completely
    # wrong ddG. This repo has already had one chain mix-up in this exact benchmark — a hand-written
    # entry that put barstar's Y29 on chain A, which is barnase. `mut_chain` is passed when the
    # installed pmx accepts it, and the outcome is VERIFIED against the written file either way, so
    # a silently chain-blind pmx cannot go unnoticed.
    kwargs = {"m": model, "mut_resid": m["resid"], "mut_resname": m["mutant"], "ff": FORCEFIELD}
    import inspect as _inspect
    sig = _inspect.signature(pmx_mutate)
    chain_param = next((p for p in ("mut_chain", "chain", "mut_chain_id") if p in sig.parameters), None)
    if chain_param:
        kwargs[chain_param] = m["chain"]
        _log(f"pmx mutate: targeting chain {m['chain']} via `{chain_param}`")
    else:
        _log(f"NOTE this pmx's mutate() exposes no chain argument ({sorted(sig.parameters)}); "
             f"relying on the post-mutation verification below")
    mutated = pmx_mutate(**kwargs)
    mutated.write(mutant)
    _verify_mutation_site(mutant, m, structure_path)
    _log(f"pmx mutate: {m['wt']}{m['resid']}->{m['mutant']} (chain {m['chain']}) -> {mutant}")

    # pdb2gmx with the pmx mutation force field, which carries the hybrid residue definitions.
    run([GMX, "pdb2gmx", "-f", "mutant.pdb", "-o", "conf.pdb", "-p", "topol.top",
         "-ff", FORCEFIELD, "-water", WATER_MODEL, "-ignh"], cwd=work_dir)

    # gentop promotes the plain topology to an A->B alchemical one.
    from pmx.alchemy import gen_hybrid_top
    from pmx.forcefield import Topology
    top = Topology(os.path.join(work_dir, "topol.top"), ff=FORCEFIELD)
    hybrid, _staples = gen_hybrid_top(top)
    hybrid_top = os.path.join(work_dir, "hybrid.top")
    hybrid.write(hybrid_top, scale_mass=True)
    _log(f"pmx gentop -> {hybrid_top}")

    run([GMX, "editconf", "-f", "conf.pdb", "-o", "box.pdb", "-bt", "dodecahedron",
         "-d", str(BOX_NM)], cwd=work_dir)
    run([GMX, "solvate", "-cp", "box.pdb", "-cs", "spc216.gro", "-o", "solv.pdb",
         "-p", "hybrid.top"], cwd=work_dir)

    _write(os.path.join(work_dir, "em.mdp"), mdp_minimise())
    run([GMX, "grompp", "-f", "em.mdp", "-c", "solv.pdb", "-p", "hybrid.top", "-o", "ions.tpr",
         "-maxwarn", "5"], cwd=work_dir)
    # Neutralise + set the ionic strength. Group 'SOL' is selected on stdin.
    run([GMX, "genion", "-s", "ions.tpr", "-o", "ions.pdb", "-p", "hybrid.top",
         "-pname", "NA", "-nname", "CL", "-neutral", "-conc", str(IONIC_M)],
        cwd=work_dir, stdin_text="SOL\n")

    _mdrun_stage(work_dir, "em", mdp_minimise(), "ions.pdb")
    _mdrun_stage(work_dir, "nvt", mdp_equil(NVT_PS, pressure=False), "em.gro")
    _mdrun_stage(work_dir, "npt", mdp_equil(NPT_PS, pressure=True), "nvt.gro")

    n_atoms = _count_atoms(os.path.join(work_dir, "npt.gro"))
    _log(f"system built and equilibrated: {n_atoms} atoms")
    return os.path.join(work_dir, "npt.gro"), hybrid_top, n_atoms


def _verify_mutation_site(mutant_pdb, mutation, original_pdb):
    """Confirm pmx mutated the residue we asked for, on the CHAIN we asked for. Raises if not.

    A chain-blind mutation in the complex leg would perturb barnase instead of barstar and return a
    converged, confidently wrong ddG — the failure mode with no symptom. So rather than trust the
    call, read the written file back: the target chain/resid must NO LONGER be the wild-type residue,
    and every OTHER chain's residue at the same number must be UNCHANGED.

    pmx names a hybrid residue for the transformation (e.g. Y2A), so "no longer TYR" is the check
    that works without hard-coding pmx's naming scheme.
    """
    chain, resid, wt = mutation["chain"], mutation["resid"], mutation["wt"]
    after = bench.observed_residue(mutant_pdb, chain, resid)
    if after is None:
        raise RuntimeError(f"after pmx mutate, chain {chain} residue {resid} is absent from "
                           f"{mutant_pdb} — the mutation did not land where it was aimed")
    if after == wt:
        raise RuntimeError(
            f"after pmx mutate, chain {chain} residue {resid} is still {wt}. The mutation did not "
            f"apply to the intended chain. In the complex leg every chain has a residue {resid}, so "
            f"this would otherwise produce a converged ddG for the WRONG protein.")
    # Nothing else should have moved. Check the same residue number on every other chain.
    others = {}
    with open(original_pdb) as fh:
        for line in fh:
            if line[:6] == "ATOM  " and line[22:27].strip() == str(resid) and line[21] != chain:
                others.setdefault(line[21], line[17:20].strip().upper())
    for other_chain, before in others.items():
        now = bench.observed_residue(mutant_pdb, other_chain, resid)
        if now != before:
            raise RuntimeError(
                f"pmx mutate also changed chain {other_chain} residue {resid} ({before} -> {now}). "
                f"Only chain {chain} was meant to change; a second mutation makes the leg "
                f"uninterpretable.")
    _log(f"mutation-site verified: chain {chain} {resid} {wt} -> {after}"
         + (f"; {len(others)} other chain(s) at {resid} unchanged" if others else ""))
    return after


def _write(path, text):
    with open(path, "w") as fh:
        fh.write(text)


def _count_atoms(gro_path):
    """A .gro file's second line is its atom count. Pure-ish (reads a file)."""
    with open(gro_path) as fh:
        fh.readline()
        try:
            return int(fh.readline().strip())
        except ValueError:
            return 0


def _mdrun_stage(work_dir, name, mdp_text, start_structure, extra_grompp=()):
    """grompp + mdrun for one non-alchemical stage, resuming from a checkpoint if one exists."""
    _write(os.path.join(work_dir, f"{name}.mdp"), mdp_text)
    tpr = f"{name}.tpr"
    if not os.path.exists(os.path.join(work_dir, tpr)):
        run([GMX, "grompp", "-f", f"{name}.mdp", "-c", start_structure, "-p", "hybrid.top",
             "-o", tpr, "-maxwarn", "5", *extra_grompp], cwd=work_dir)
    cmd = [GMX, "mdrun", "-deffnm", name, "-cpi", f"{name}.cpt"]
    if NT:
        cmd += ["-nt", NT]
    run(cmd, cwd=work_dir)


# ------------------------------------------------------------------------------------------------
# Alchemical sampling
# ------------------------------------------------------------------------------------------------
def run_windows(work_dir, start_gro, n_states, on_window=None):
    """Run every lambda window, skipping any already finished. Returns the list of dhdl paths.

    A finished window is identified by its dhdl .xvg, so a re-dispatched leg never re-runs completed
    work; an interrupted window resumes from its GROMACS checkpoint via -cpi. That two-level scheme
    is what makes an interruptible spot bid safe here.
    """
    dhdls = []
    for i in range(n_states):
        name = f"lambda{i:02d}"
        dhdl = os.path.join(work_dir, f"{name}.xvg")
        if os.path.exists(dhdl) and os.path.getsize(dhdl) > 1000:
            _log(f"window {i}/{n_states - 1} already complete — skipping")
            dhdls.append(dhdl)
            if on_window:
                on_window(i, dhdl, skipped=True)
            continue
        t0 = time.time()
        _write(os.path.join(work_dir, f"{name}.mdp"),
               mdp_lambda_window(i, n_states, EQUIL_PS + PROD_PS, collect_data=True))
        tpr = os.path.join(work_dir, f"{name}.tpr")
        if not os.path.exists(tpr):
            run([GMX, "grompp", "-f", f"{name}.mdp", "-c", os.path.basename(start_gro),
                 "-p", "hybrid.top", "-o", f"{name}.tpr", "-maxwarn", "5"], cwd=work_dir)
        cmd = [GMX, "mdrun", "-deffnm", name, "-dhdl", f"{name}.xvg", "-cpi", f"{name}.cpt"]
        if NT:
            cmd += ["-nt", NT]
        run(cmd, cwd=work_dir)
        if not os.path.exists(dhdl):
            raise RuntimeError(f"window {i} produced no dhdl output at {dhdl}")
        dhdls.append(dhdl)
        _log(f"window {i}/{n_states - 1} done in {(time.time() - t0) / 60:.1f} min")
        if on_window:
            on_window(i, dhdl, skipped=False)
    return dhdls


def analyse(work_dir, n_states):
    """`gmx bar` over the per-window dhdl files -> (dG_kcal, err_kcal, diagnostics).

    GROMACS reports in kJ/mol; this repo speaks kcal/mol everywhere, so the conversion happens here,
    once, rather than being left for a reader of the leg JSON to remember.
    """
    xvgs = sorted(glob.glob(os.path.join(work_dir, "lambda*.xvg")))
    if len(xvgs) < 2:
        raise RuntimeError(f"need >= 2 window dhdl files to run BAR, found {len(xvgs)}")
    proc = run([GMX, "bar", "-f", *[os.path.basename(x) for x in xvgs], "-o", "bar.xvg",
                "-oi", "barint.xvg"], cwd=work_dir)
    text = (proc.stdout or "") + (proc.stderr or "")
    dg_kj = err_kj = None
    for line in text.splitlines():
        # The summary line reads e.g.:
        #   total   0 - 15,  DG  12.345 +/-  0.210
        if "total" in line and "DG" in line:
            parts = line.replace(",", " ").split()
            try:
                idx = parts.index("DG")
                dg_kj = float(parts[idx + 1])
                if "+/-" in parts:
                    err_kj = float(parts[parts.index("+/-") + 1])
            except (ValueError, IndexError):
                continue
    if dg_kj is None:
        raise RuntimeError("could not parse a total DG from gmx bar output:\n" + text[-2000:])
    kj_to_kcal = 1.0 / 4.184
    diagnostics = {"n_windows": len(xvgs), "estimator": "BAR (gmx bar)",
                   "dg_kj_per_mol": dg_kj, "err_kj_per_mol": err_kj,
                   "units_note": "GROMACS reports kJ/mol; converted to kcal/mol here, once"}
    return dg_kj * kj_to_kcal, ((err_kj or 0.0) * kj_to_kcal), diagnostics


# ------------------------------------------------------------------------------------------------
# Leg
# ------------------------------------------------------------------------------------------------
def run_leg(leg_id, structure_path, mutation_spec, out_dir, work_dir=None, n_states=None, meta=None):
    """Run one leg to completion (or resume it) and write `leg_<id>.json`.

    The JSON schema deliberately matches the perses lane's, because `protfep_reduce` — the scoring,
    the qualification verdict and the per-leg price — is engine-agnostic and must stay that way.
    """
    os.makedirs(out_dir, exist_ok=True)
    n_states = int(n_states or N_STATES)
    work_dir = work_dir or os.path.join(out_dir, f"work_{leg_id}")
    result_path = os.path.join(out_dir, f"leg_{leg_id}.json")

    record = {
        "leg_id": leg_id,
        "mutation": mutation_spec,
        "structure": os.path.basename(structure_path),
        "engine": "pmx (mutate+gentop) + GROMACS lambda windows + BAR",
        "protocol": "equilibrium lambda windows",
        "protocol_note": ("pmx's PUBLISHED protocol is non-equilibrium (fast growth + Crooks/BAR). "
                          "This is the equilibrium variant, chosen because a window is a natural "
                          "checkpoint unit on a preemptible host. The two are NOT interchangeable "
                          "when quoting a number — hence this field."),
        "forcefield": FORCEFIELD,
        "water_model": WATER_MODEL,
        "n_states": n_states,
        "timestep_fs": TIMESTEP_FS,
        "equil_ps_per_window": EQUIL_PS,
        "prod_ps_per_window": PROD_PS,
        "temperature_K": TEMPERATURE_K,
        "md_settings_deviation": (
            "2 fs, no HMR (canonical is 4 fs + HMR). A softcore alchemical region is where this "
            "repo's ternary lane repeatedly NaN'd; the timestep is empirical with no static "
            "predictor, so a new engine's first legs run conservatively. Escalate only after this "
            "lane survives a full leg, and record it — do not assume it transfers from another lane."),
        "status": "starting",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if meta:
        record["meta"] = meta

    def _commit(**updates):
        record.update(updates)
        record["updated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(result_path, "w") as fh:
            json.dump(record, fh, indent=2)

    _commit()
    t0 = time.time()
    try:
        record["platform"] = assert_gpu_gromacs()
        _commit(status="building")
        npt_gro, _hybrid_top, n_atoms = build_system(structure_path, mutation_spec, work_dir)
        _commit(status="sampling", n_particles=n_atoms)

        done = {"n": 0}

        def _on_window(i, _dhdl, skipped):
            done["n"] += 1
            elapsed = time.time() - t0
            _commit(status="sampling", windows_done=done["n"], n_states=n_states,
                    gpu_hours_so_far=round(elapsed / 3600.0, 3),
                    last_window=i, last_window_skipped=skipped)

        run_windows(work_dir, npt_gro, n_states, on_window=_on_window)
        _commit(status="analyzing")
        dg, err, diagnostics = analyse(work_dir, n_states)
        gpu_h = round((time.time() - t0) / 3600.0, 3)
        _commit(status="done", dg_kcal=dg, dg_mbar_se_kcal=err, analysis=diagnostics,
                gpu_hours=gpu_h,
                s_per_iter=round((time.time() - t0) / max(1, n_states), 1))
        _log(f"LEG DONE {leg_id}: dG = {dg:.3f} +/- {err:.3f} kcal/mol ({gpu_h:.2f} GPU-h)")
    except Exception as e:  # noqa: BLE001 — the partial record IS the deliverable on failure
        salvage = {}
        try:
            dg_p, err_p, _ = analyse(work_dir, n_states)
            salvage = {"dg_partial_kcal": round(dg_p, 3), "dg_partial_err_kcal": round(err_p, 3),
                       "partial_note": ("BAR over the windows that finished before the failure — NOT "
                                        "a converged leg result, and not usable in a wedge")}
        except Exception as e2:  # noqa: BLE001
            salvage = {"dg_partial_error": f"{type(e2).__name__}: {e2}"}
        _commit(status="failed", error=f"{type(e).__name__}: {e}",
                traceback=traceback.format_exc()[-4000:],
                gpu_hours=round((time.time() - t0) / 3600.0, 3), **salvage)
        _log(f"LEG FAILED {leg_id}: {type(e).__name__}: {e}")
        raise
    finally:
        # Trajectories are large and are not the deliverable; the dhdl .xvg files and the leg JSON
        # are. Keep them so a re-dispatch can skip finished windows, drop the bulk.
        if os.environ.get("PMX_KEEP_TRAJ") != "1":
            for pattern in ("*.trr", "*.xtc", "*.edr"):
                for path in glob.glob(os.path.join(work_dir, pattern)):
                    try:
                        os.remove(path)
                    except OSError:
                        pass
    return record


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Run ONE protein-mutation FEP leg (pmx + GROMACS)")
    ap.add_argument("--benchmark", default=os.environ.get("PROTFEP_BENCHMARK"))
    ap.add_argument("--environment", default=os.environ.get("PROTFEP_ENVIRONMENT", "complex"),
                    choices=["complex", "apo"])
    ap.add_argument("--replicate", type=int, default=int(os.environ.get("PROTFEP_REPLICATE") or "0"))
    ap.add_argument("--structure", default=os.environ.get("PROTFEP_STRUCTURE"))
    ap.add_argument("--mutation", default=os.environ.get("PROTFEP_MUTATION"))
    ap.add_argument("--leg-id", default=os.environ.get("LEG_ID"))
    ap.add_argument("--n-states", type=int, default=None)
    ap.add_argument("--in-dir", default=os.environ.get("INPUT_DIR", "/tmp/protfep_in"))
    ap.add_argument("--out-dir", default=os.environ.get("OUTPUT_DIR", "/tmp/protfep_out"))
    ap.add_argument("--build-only", action="store_true",
                    help="construct + equilibrate the hybrid system and stop (the free CI build-test)")
    args = ap.parse_args(argv)

    structure, mutation, leg_id, meta = args.structure, args.mutation, args.leg_id, None
    if args.benchmark:
        spec = bench.leg_spec(args.benchmark, args.environment, args.replicate)
        staged = bench.stage_leg(spec, args.in_dir)
        if not staged["report"].get("prepared"):
            raise SystemExit(f"staging produced no prepared structure "
                             f"({staged['report'].get('pdbfixer_skipped')}) — the MD stack is missing")
        structure = staged["report"]["prepared"]
        mutation = spec["mutation"]
        leg_id = leg_id or spec["leg_id"]
        meta = {"benchmark": args.benchmark, "cycle_role": spec["cycle_role"],
                "environment": spec["environment"], "replicate": spec["replicate"],
                "staging": staged["report"]}
    if not (structure and mutation and leg_id):
        raise SystemExit("need --benchmark, or all of --structure/--mutation/--leg-id")

    if args.build_only:
        work = os.path.join(args.out_dir, f"work_{leg_id}")
        _gro, _top, n_atoms = build_system(structure, mutation, work)
        print(f"BUILD-ONLY PASS: {n_atoms} atoms in the equilibrated hybrid system")
        return 0

    run_leg(leg_id, structure, mutation, args.out_dir, n_states=args.n_states, meta=meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
