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


def _self_sha256():
    """First 12 hex chars of this file's SHA-256, or None if it cannot be read. Never raises.

    A provenance field must not be able to fail a leg — an unreadable source file would be bizarre,
    but recording `null` beats a traceback three hours into a paid run.
    """
    import hashlib
    try:
        with open(os.path.abspath(__file__), "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()[:12]
    except OSError:
        return None


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
        # sc-coul MUST be on whenever a single lambda vector drives coulomb and vdW together.
        # GROMACS 2026 refuses the combination outright:
        #   For state 1, vdw-lambdas (0.5) is changing with vdw softcore, while coul-lambdas (0.5)
        #   is nonzero without coulomb softcore: this will lead to crashes, and is not supported.
        # The usual ligand answer — decharge first on a separate coul schedule, then decouple vdW —
        # does not transfer to a RESIDUE MUTATION, where charges and vdW change on the same atoms
        # simultaneously and cannot be cleanly separated. Softcore on both is what pmx's own
        # published protein-mutation protocols do, so this keeps the lane on the engine's convention
        # rather than inventing a schedule for it.
        "sc-coul": "yes",
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
def _split_topology_guard(work_dir):
    """Refuse to continue if pdb2gmx still split the topology into per-chain .itp files.

    pmx's gen_hybrid_top converts the topology it is handed. If the molecule definitions live in
    included per-chain files instead, it converts a file of #includes, the mutated chain keeps its
    plain-force-field parameters, and grompp fails later with a wall of "No default Angle types"
    that names the .itp rather than the real cause. `-merge all` prevents the split; this asserts it
    actually did, because a silent split costs a full leg to rediscover.
    """
    import glob as _glob
    split = sorted(_glob.glob(os.path.join(work_dir, "topol_*.itp")))
    if split:
        raise RuntimeError(
            f"pdb2gmx split the topology into {[os.path.basename(p) for p in split]} despite "
            f"`-merge all`. pmx's gentop would convert only the top-level file and the mutated "
            f"chain would keep plain force-field parameters — grompp then fails with 'No default "
            f"Angle types' against the .itp, which points at the symptom and not the cause.")
    _log("topology is inline (no per-chain .itp split) — gentop will see the real molecule")


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

    # RESUMPTION SHORT-CIRCUIT. Setup (pdb2gmx x2, mutate, gentop, solvate, ions, minimise, NVT, NPT)
    # is deterministic and takes minutes; if a previous attempt's outputs were restored from S3 there
    # is nothing to gain by redoing it, and on a preempted leg the whole point is to resume where it
    # stopped. Both files are required: hybrid.top without npt.gro (or vice versa) is a partial
    # restore, and continuing from half a system is worse than rebuilding it.
    existing_gro = os.path.join(work_dir, "npt.gro")
    existing_top = os.path.join(work_dir, "hybrid.top")
    if os.path.exists(existing_gro) and os.path.exists(existing_top):
        n_atoms = _count_atoms(existing_gro)
        ff_name, ff_root = resolve_forcefield(FORCEFIELD)
        os.environ["GMXLIB"] = ff_root + (":" + os.environ["GMXLIB"] if os.environ.get("GMXLIB") else "")
        _log(f"RESUMING from a restored system: {n_atoms} atoms, skipping setup entirely")
        return existing_gro, existing_top, n_atoms, ff_name

    ff_name, ff_root = resolve_forcefield(FORCEFIELD)
    # GROMACS finds a force field via GMXLIB; pmx's hybrid residue definitions live in ITS data tree,
    # so both pdb2gmx and pmx must be pointed at the same place or they will disagree about what a
    # hybrid residue is. Set it in the process environment so the gmx subprocesses inherit it.
    os.environ["GMXLIB"] = ff_root + (":" + os.environ["GMXLIB"] if os.environ.get("GMXLIB") else "")
    _log(f"GMXLIB -> {ff_root}; force field: {ff_name}")

    # PDB2GMX RUNS *BEFORE* THE MUTATION, NOT AFTER — this order is load-bearing.
    # pmx builds the hybrid residue by copying coordinates from the old residue BY ATOM NAME
    # (alchemy._set_conformation: `atom.x = old_res[atom.name].x`). If the structure's atom naming is
    # not already the force field's, that lookup misses and pmx dies with a bare
    # `IndexError: list index out of range` from deep inside molecule.__getitem__ — which says
    # nothing about naming at all. Running pdb2gmx first normalises names and protonation to the
    # force field, so the mutation operates on exactly what the force field expects. `-ignh` drops
    # PDBFixer's hydrogens and lets pdb2gmx add its own: two protonation schemes disagreeing is the
    # same class of failure.
    prepped = os.path.join(work_dir, "prepped.pdb")
    if not os.path.exists(prepped):
        shutil.copy(structure_path, os.path.join(work_dir, "input.pdb"))
        run([GMX, "pdb2gmx", "-f", "input.pdb", "-o", "prepped.pdb", "-p", "prep.top",
             "-ff", ff_name, "-water", WATER_MODEL, "-ignh"], cwd=work_dir)
    _log("pdb2gmx pass 1: atom names + protonation normalised to the force field")

    mutant = os.path.join(work_dir, "mutant.pdb")
    # pmx's Python API is used rather than the CLI so the mutation is specified programmatically —
    # the CLI is interactive and would need a fragile stdin script.
    from pmx import Model
    from pmx.alchemy import mutate as pmx_mutate
    model = Model(prepped, rename_atoms=True)

    # THE CHAIN MUST BE PASSED, AND THE RESULT MUST BE CHECKED.
    # In the COMPLEX leg both chains carry a residue 29 (barnase 1-110, barstar 1-89), so a
    # chain-blind mutate could perturb the wrong protein and return a perfectly converged, completely
    # wrong ddG. This repo has already had one chain mix-up in this exact benchmark — a hand-written
    # entry that put barstar's Y29 on chain A, which is barnase. `mut_chain` is passed when the
    # installed pmx accepts it, and the outcome is VERIFIED against the written file either way, so
    # a silently chain-blind pmx cannot go unnoticed.
    # Resolve against PMX'S OWN Model, not against the file. prepped.pdb contained `D:29` and the
    # text-based resolver returned exactly that, yet pmx still raised `resid 29 not found in chain
    # "D"` — because pmx's Model does not necessarily expose the file's chain letters. The mutation
    # is addressed to the Model, so the Model is what resolution must consult.
    target_chain, target_resid = resolve_target_in_model(model, structure_path, m)
    kwargs = {"m": model, "mut_resid": target_resid, "mut_resname": m["mutant"], "ff": ff_name}
    import inspect as _inspect
    sig = _inspect.signature(pmx_mutate)
    chain_param = next((p for p in ("mut_chain", "chain", "mut_chain_id") if p in sig.parameters), None)
    if chain_param:
        kwargs[chain_param] = target_chain
        _log(f"pmx mutate: targeting {target_chain}:{target_resid} via `{chain_param}`")
    else:
        _log(f"NOTE this pmx's mutate() exposes no chain argument ({sorted(sig.parameters)}); "
             f"relying on the post-mutation verification below")
    mutated = pmx_mutate(**kwargs)
    mutated.write(mutant)
    _verify_mutation_site(mutant, dict(m, chain=target_chain, resid=target_resid), prepped)
    _log(f"pmx mutate: {m['wt']}{m['resid']}->{m['mutant']} (staged {m['chain']}:{m['resid']}, built {target_chain}:{target_resid}) -> {mutant}")

    # pdb2gmx pass 2, on the MUTANT: this is the one that produces the topology gentop promotes.
    #
    # NO -ignh HERE, and that asymmetry with pass 1 is the whole point. pmx writes the hybrid residue
    # (Y2A for TYR->ALA) with its dummy/vanishing atoms already placed; -ignh would strip them and
    # force pdb2gmx to rebuild them from the hydrogen database, which does not carry every hybrid
    # hydrogen. Observed exactly that on the free build-test:
    #     atom HH is missing in residue Y2A 29 ... add atom HH to the hydrogen database of
    #     building block Y2A in the file mutres.hdb
    #     -> There were 12 missing atoms in molecule Protein_chain_D
    # HV1/HV2/HV3 are the vanishing hydrogens pmx had just placed. Pass 1 strips hydrogens to
    # normalise protonation on the WILD-TYPE structure; pass 2 must preserve what pmx built.
    # `-missing` would "fix" this by building an INCOMPLETE topology — the wrong kind of green.
    # `-merge all` IS LOAD-BEARING FOR ANY MULTI-CHAIN LEG.
    # With more than one chain, pdb2gmx splits the topology into per-chain topol_Protein_chain_X.itp
    # files and leaves topol.top as little more than #includes. pmx's gen_hybrid_top then converts
    # the top-level file — which no longer contains the molecule definitions — so the hybrid
    # residue's B-state parameters never reach the chain that was actually mutated. grompp then
    # rejects the result with a wall of "No default Angle types" / "No default Per. Imp. Dih. types"
    # against topol_Protein_chain_D.itp: 19 of them on the complex leg.
    #
    # This is precisely why the apo leg has worked from the start and the complex leg never could —
    # single-chain systems get everything inline, so gentop sees the real topology. Merging into one
    # [moleculetype] keeps it inline for the complex too. The chains are not covalently joined and
    # nothing about the physics changes; only the topology's file layout does.
    run([GMX, "pdb2gmx", "-f", "mutant.pdb", "-o", "conf.pdb", "-p", "topol.top",
         "-ff", ff_name, "-water", WATER_MODEL, "-merge", "all"], cwd=work_dir)
    _split_topology_guard(work_dir)

    # gentop promotes the plain topology to an A->B alchemical one.
    from pmx.alchemy import gen_hybrid_top
    from pmx.forcefield import Topology
    top = Topology(os.path.join(work_dir, "topol.top"), ff=ff_name)
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
    _log(f"system built and equilibrated: {n_atoms} atoms (force field {ff_name})")
    return os.path.join(work_dir, "npt.gro"), hybrid_top, n_atoms, ff_name


def chain_residue_lists(pdb_path):
    """{chain_id: [(resid, resname), ...]} in file order. Pure.

    Deliberately plain text parsing: this has to work on both the author-numbered RCSB structure and
    whatever pdb2gmx emits, without either a structure library's opinions or ours.
    """
    chains, seen = {}, set()
    with open(pdb_path) as fh:
        for line in fh:
            if line[:6] not in ("ATOM  ", "HETATM"):
                continue
            chain = line[21]
            key = (chain, line[22:27])
            if key in seen:
                continue
            seen.add(key)
            try:
                resid = int(line[22:26])
            except ValueError:
                continue
            chains.setdefault(chain, []).append((resid, line[17:20].strip().upper()))
    return chains


def model_residue_lists(model):
    """{chain_id: [(resid, resname), ...]} as PMX ITSELF sees the structure. Pure (given the model).

    THIS is the representation the mutation is addressed against, so it is the one resolution must
    use. Resolving against the FILE was the bug: prepped.pdb plainly contained `D:29`, the text-based
    resolver duly returned ("D", 29), and pmx then raised `resid 29 not found in chain "D"` — because
    pmx's Model does not necessarily expose the file's chain letters. Two different representations
    of the same structure, and the mutation was aimed using the wrong one.

    pmx's chain id attribute has moved across versions, so it is read defensively; a chain whose id
    cannot be determined is keyed by its index, which still lets sequence matching find it.
    """
    out = {}
    for idx, chain in enumerate(getattr(model, "chains", []) or []):
        cid = getattr(chain, "id", None)
        if cid is None:
            cid = getattr(chain, "chain_id", None)
        if cid is None:
            cid = str(idx)
        residues = []
        for res in getattr(chain, "residues", []) or []:
            rid = getattr(res, "id", None)
            if rid is None:
                rid = getattr(res, "resnr", None)
            rname = (getattr(res, "resname", None) or getattr(res, "name", "") or "").strip().upper()
            if rid is not None and rname:
                residues.append((int(rid), rname))
        out[cid] = residues
    return out


def _match_target_chain(orig_chains, candidate_chains, mutation):
    """Shared resolution logic: find the candidate chain matching the staged target. Pure.

    Returns (chain_id, resid). Raises with a diagnostic naming what was actually present, because
    "not found" without the alternatives costs a round trip to answer "well, what IS there?".
    """
    m = mutation
    if m["chain"] not in orig_chains:
        raise RuntimeError(f"chain {m['chain']} absent from the staged structure "
                           f"(present: {sorted(orig_chains)})")
    target = orig_chains[m["chain"]]
    names = [rn for _rid, rn in target]
    index = next((i for i, (rid, _rn) in enumerate(target) if rid == m["resid"]), None)
    if index is None:
        raise RuntimeError(f"residue {m['resid']} absent from staged chain {m['chain']}")

    def _similarity(other):
        n = min(len(names), len(other))
        if n == 0:
            return 0.0
        return sum(1 for a, b in zip(names[:n], other[:n]) if a == b) / max(len(names), len(other))

    scored = sorted(((_similarity([rn for _r, rn in res]), cid)
                     for cid, res in candidate_chains.items()), reverse=True)
    if not scored:
        raise RuntimeError("the prepared structure exposes no chains at all")
    best_score, best_chain = scored[0]
    present = {c: len(r) for c, r in candidate_chains.items()}
    if best_score < 0.9:
        raise RuntimeError(f"could not identify the target chain: best match {best_chain!r} at "
                           f"{best_score:.0%}. Chains present: {present}. Refusing to guess.")
    if len(scored) > 1 and scored[1][0] > best_score - 0.05:
        raise RuntimeError(f"target chain is AMBIGUOUS: {best_chain!r} at {best_score:.0%} vs "
                           f"{scored[1][1]!r} at {scored[1][0]:.0%}. Refusing to pick.")
    resolved = candidate_chains[best_chain]
    if index >= len(resolved):
        raise RuntimeError(f"chain {best_chain!r} ({len(resolved)} residues) is shorter than the "
                           f"target position {index}")
    resid, resname = resolved[index]
    if resname != m["wt"]:
        raise RuntimeError(f"resolved {best_chain}:{resid} is {resname}, not the expected {m['wt']}")
    return best_chain, resid


def resolve_target_in_model(model, original_pdb, mutation):
    """Resolve the mutation target against PMX'S OWN view of the structure. Returns (chain, resid).

    Logs pmx's chain inventory unconditionally: when this goes wrong the useful question is always
    "what does pmx think is in there?", and on a rented host that answer costs another leg.
    """
    orig = chain_residue_lists(original_pdb)
    pmx_chains = model_residue_lists(model)
    _log("pmx Model inventory: " + ", ".join(
        f"{cid!r}:{len(res)}res[{res[0][0]}..{res[-1][0]}]" if res else f"{cid!r}:empty"
        for cid, res in sorted(pmx_chains.items(), key=lambda kv: str(kv[0]))))
    chain, resid = _match_target_chain(orig, pmx_chains, mutation)
    if (chain, resid) != (mutation["chain"], mutation["resid"]):
        _log(f"target resolved against pmx's Model: {mutation['chain']}:{mutation['resid']} "
             f"-> {chain}:{resid}")
    return chain, resid


def resolve_target_after_prep(prepped_pdb, original_pdb, mutation):
    """File-based resolution. Retained for tests and for diagnostics that only have the PDB.

    NOTE: build_system does NOT use this — it resolves against pmx's Model, because that is the
    representation the mutation is addressed to and the two can disagree (they did). Both share
    `_match_target_chain`, so there is one matching rule rather than two that can drift.
    """
    return _match_target_chain(chain_residue_lists(original_pdb),
                               chain_residue_lists(prepped_pdb), mutation)


def discover_forcefields():
    """Every mutation force field pmx actually ships, as {name: containing_directory}.

    pmx's data layout has moved between releases, and `get_ff_path` raises a bare
    `forcefield path "X" not found` that names neither where it looked nor what exists. Rather than
    guess the directory again, walk pmx's data tree for `*.ff` directories — the answer then comes
    from the installation instead of from a remembered layout.
    """
    import pmx
    root = os.path.join(os.path.dirname(pmx.__file__), "data")
    found = {}
    for dirpath, dirnames, _files in os.walk(root):
        for d in dirnames:
            if d.endswith(".ff"):
                found.setdefault(d[:-3], dirpath)
    return found


def resolve_forcefield(requested):
    """Resolve the mutation force field to (name, containing_dir), or raise with what IS available.

    A missing force field must fail with the list of real options, not with a bare "not found" — the
    latter costs a round trip to answer "well, what IS there?". If the requested name is absent, an
    amber99sb*-mut field is preferred as the closest equivalent, since that is the family pmx's
    protein-mutation benchmarks were built on; the substitution is logged and recorded, never silent.
    """
    available = discover_forcefields()
    if not available:
        raise RuntimeError(
            "pmx ships no *.ff mutation force fields in its data tree. A stock GROMACS force field "
            "cannot express an A->B hybrid residue at all, so there is nothing to fall back to.")
    if requested in available:
        return requested, available[requested]
    preferred = sorted(n for n in available if n.startswith("amber99sb") and "mut" in n)
    chosen = preferred[0] if preferred else sorted(available)[0]
    _log(f"NOTE requested force field {requested!r} is not in this pmx install. "
         f"Available: {sorted(available)}. Falling back to {chosen!r}.")
    return chosen, available[chosen]


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
        # Fingerprint of the driver that produced this record. Set by the Vast onstart from
        # `sha256sum protfep_pmx.py`; falls back to hashing this file directly so a local or CI run
        # is fingerprinted too. Provenance on a result is worth having on its own, but the immediate
        # reason is staleness: an old `failed` record sits in S3 until the next attempt overwrites
        # it, and only the code hash distinguishes "the fix did not take" from "you are reading the
        # attempt from before the fix."
        "driver_sha256": os.environ.get("PROTFEP_CODE_SHA256") or _self_sha256(),
    }
    if meta:
        record["meta"] = meta

    def _commit(**updates):
        record.update(updates)
        record["updated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(result_path, "w") as fh:
            json.dump(record, fh, indent=2)

    # GPU-HOURS MUST ACCUMULATE ACROSS RESUMES.
    # A preempted leg reports only its FINAL segment otherwise, and protfep_reduce prices the rung
    # from exactly this field. The apo pilot leg was preempted at 14/16 windows and finished in 0.073
    # GPU-h; the reducer duly published usd_per_benchmark_leg=0.015 and a ~$0.59 wedge projection,
    # roughly 20x low, because the ~1.3 GPU-h before the preemption had vanished with the host. A
    # cost basis that silently omits preempted work is worse than no cost basis.
    prior_gpu_h = 0.0
    if os.path.exists(result_path):
        try:
            with open(result_path) as fh:
                prior = json.load(fh)
            prior_gpu_h = float(prior.get("gpu_hours_cumulative")
                                or prior.get("gpu_hours")
                                or prior.get("gpu_hours_so_far") or 0.0)
            if prior_gpu_h:
                _log(f"carrying {prior_gpu_h:.3f} GPU-h forward from a previous attempt")
        except Exception as e:  # noqa: BLE001 — a corrupt prior record must not block the rerun
            _log(f"could not read prior GPU-hours ({type(e).__name__}: {e}); counting this run only")
    record["gpu_hours_prior_attempts"] = round(prior_gpu_h, 3)

    _commit()
    t0 = time.time()
    try:
        record["platform"] = assert_gpu_gromacs()
        _commit(status="building")
        npt_gro, _hybrid_top, n_atoms, ff_used = build_system(structure_path, mutation_spec, work_dir)
        _commit(status="sampling", n_particles=n_atoms, forcefield=ff_used)

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
        this_run_h = (time.time() - t0) / 3600.0
        gpu_h = round(prior_gpu_h + this_run_h, 3)
        _commit(status="done", dg_kcal=dg, dg_mbar_se_kcal=err, analysis=diagnostics,
                gpu_hours=gpu_h, gpu_hours_cumulative=gpu_h,
                gpu_hours_this_run=round(this_run_h, 3),
                # s_per_iter is per WINDOW and only meaningful for windows this run actually ran;
                # across a resume it would otherwise average in windows that were merely restored.
                s_per_iter=round(this_run_h * 3600.0 / max(1, n_states), 1))
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
                gpu_hours=round(prior_gpu_h + (time.time() - t0) / 3600.0, 3), **salvage)
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
        _gro, _top, n_atoms, ff_used = build_system(structure, mutation, work)
        print(f"BUILD-ONLY PASS: {n_atoms} atoms in the equilibrated hybrid system "
              f"(force field {ff_used})")
        return 0

    run_leg(leg_id, structure, mutation, args.out_dir, n_states=args.n_states, meta=meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
