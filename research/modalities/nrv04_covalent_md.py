#!/usr/bin/env python3
"""
NR-V04 covalent feasibility panel — endpoint-MD driver (prereg §2/§4).

Runs plain (non-alchemical) endpoint MD on ONE panel leg + seed, imposing the frozen restrained-covalent bond on
covalent legs, and emits the R1-R4 readouts. Env-driven by nrv04_covalent_panel.leg_env(); consumed by the Vast
launcher (one instance per leg+seed).

Force field: amber14 (protein) + GAFF/OpenFF small-molecule via openmmforcefields.SystemGenerator (the standard
non-alchemical path; the RBFE lane's OpenFE machinery is alchemy-only and not reused here). Covalent bond =
a stiff harmonic C6->Sγ bond + two flanking angle restraints (prereg §2), NOT a reparameterized junction.

MODE=smoke: build + minimize + a few hundred MD steps + run the readouts on that tiny trajectory (proves the leg
assembles + the whole pipeline executes end-to-end, ~cents). MODE=run: EQUIL_NS + PROD_NS production.

The OpenMM build/run needs the MD env (CI/Vast); the pure geometry helpers (kabsch, interface selection,
restraint indexing) are unit-tested offline. Nothing here is fabricated — a missing input exits loudly.
"""
from __future__ import annotations

import json
import math
import os
import sys

# ---- pure geometry helpers (no MD deps) -> unit-tested offline --------------------------------------------


def kabsch_rmsd(mobile, ref):
    """RMSD of `mobile` onto `ref` after optimal superposition (Kabsch). Both are Nx3 lists/arrays. Returns the
    post-fit RMSD. numpy only (present in the MD env); imported lazily so the module imports without numpy."""
    import numpy as np
    P = np.asarray(mobile, float)
    Q = np.asarray(ref, float)
    if P.shape != Q.shape or P.shape[0] == 0:
        raise ValueError("kabsch_rmsd: shape mismatch or empty")
    Pc = P - P.mean(0)
    Qc = Q - Q.mean(0)
    V, _, Wt = np.linalg.svd(Pc.T @ Qc)
    d = np.sign(np.linalg.det(V @ Wt))
    D = np.diag([1.0, 1.0, d])
    U = V @ D @ Wt
    Prot = Pc @ U
    return float(np.sqrt(np.mean(np.sum((Prot - Qc) ** 2, axis=1))))


def interface_atom_indices(positions_nm, chain_ids, e3_chains, target_chains, cutoff_nm=0.8):
    """Heavy-atom indices at the E3<->target interface: any E3 atom within cutoff of a target atom (and vice
    versa), split into (e3_side, target_side). `chain_ids` is per-atom chain id. Pure (O(n_e3*n_target))."""
    e3 = [i for i, c in enumerate(chain_ids) if c in e3_chains]
    tg = [i for i, c in enumerate(chain_ids) if c in target_chains]
    c2 = cutoff_nm * cutoff_nm
    e3_side, tg_side = set(), set()
    for i in e3:
        xi = positions_nm[i]
        for j in tg:
            xj = positions_nm[j]
            if (xi[0] - xj[0]) ** 2 + (xi[1] - xj[1]) ** 2 + (xi[2] - xj[2]) ** 2 <= c2:
                e3_side.add(i); tg_side.add(j)
    return sorted(e3_side), sorted(tg_side)


# ---- OpenMM build / run (MD env only) --------------------------------------------------------------------


def _require(cond, msg):
    if not cond:
        raise SystemExit(f"[nrv04-md] {msg}")


def pdb_text_atom_count(pdb_text):
    return sum(1 for ln in pdb_text.splitlines() if ln[:6].strip() in ("ATOM", "HETATM"))


def build_system(complex_pdb, ligand_sdf, covalent, cov_lig_atom, cov_resnum, mutation):
    """Build a solvated OpenMM system for one leg. Returns (simulation, meta). CI/Vast only."""
    import numpy as np  # noqa: F401
    from openmm import app, unit, HarmonicBondForce, HarmonicAngleForce, Platform
    from openff.toolkit import Molecule
    from openmmforcefields.generators import SystemGenerator

    import md_settings as MD                                   # canonical hyperparameters (single source of truth)

    _require(os.path.exists(complex_pdb), f"missing complex.pdb: {complex_pdb}")
    _require(os.path.exists(ligand_sdf), f"missing ligands.sdf: {ligand_sdf}")

    # Identify the reactive cysteine by GEOMETRY (nearest Sγ to the warhead electrophile in the co-fold pose) —
    # NOT by the hardcoded resnum 551, which does not exist in the co-fold's renumbered chains. This resolves the
    # target chain + the residue used by BOTH the C551A mutation and the covalent restraint, so they stay
    # consistent and are immune to renumbering.
    pdb_text = open(complex_pdb).read()
    cov_pair = None
    react_chain, react_resid, react_dist = _reactive_cys_by_geometry(pdb_text, ligand_sdf, cov_lig_atom)
    print(f"[nrv04-md] reactive Cys = chain {react_chain} resid {react_resid} "
          f"(Sγ {react_dist:.2f} Å from the warhead electrophile; cov_resnum={cov_resnum} is co-fold-renumbered)",
          flush=True)
    if react_dist > 8.0:
        print(f"[nrv04-md] WARN reactive Sγ is {react_dist:.1f} Å from the electrophile (>8 Å) — the co-fold may "
              f"not have posed the warhead in the pocket; the covalent restraint tether may be geometrically strained",
              flush=True)
    if mutation == "C551A":                                    # the panel's 'C551A' = knock out the reactive Cys
        from nrv04_covalent_stage import mutate_cys_to_ala
        pdb_text = mutate_cys_to_ala(pdb_text, react_chain, react_resid)
    tmp_pdb = complex_pdb + ".staged.pdb"
    open(tmp_pdb, "w").write(pdb_text)

    # PREP THE PREDICTED PROTEIN WITH PDBFIXER — the co-fold complex.pdb is heavy-atoms-only AND a multi-chain
    # predicted assembly (VHL/EloB/EloC/target) with uncapped chain termini, so a bare addHydrogens/createSystem
    # fails ("No template found ... missing terminal capping group / missing H"). PDBFixer is the standard prep:
    # add missing heavy atoms, cap termini, add hydrogens. We DON'T let it build long missing loops
    # (missingResidues={}) — the co-fold is sequence-complete; we only fix atoms/termini/H on existing residues.
    from pdbfixer import PDBFixer
    fixer = PDBFixer(filename=tmp_pdb)
    fixer.findMissingResidues(); fixer.missingResidues = {}
    fixer.findNonstandardResidues(); fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(keepWater=False)
    fixer.findMissingAtoms(); fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)
    n_before = pdb_text_atom_count(pdb_text)
    fixed_topology, fixed_positions = fixer.topology, fixer.positions
    n_after_h = fixed_topology.getNumAtoms()

    lig = Molecule.from_file(ligand_sdf)
    if isinstance(lig, list):
        lig = lig[0]

    # LIGAND CHARGES: assign md_settings.CHARGE_METHOD (NAGL) to the molecule BEFORE the SystemGenerator, using the
    # SAME shared helper every ternary lane uses (ternary_endpoint_stability.assign_rbfe_charges). This is THE fix
    # for the sqm intractability — AM1-BCC via AmberTools sqm ran >85 min on the 166-atom nrv04 recruiter without
    # converging (measured 2026-07-22), whereas NAGL (a deterministic ML AM1-BCC surrogate) charges it in seconds.
    # openmmforcefields then uses the molecule's pre-assigned charges instead of calling sqm. Because charging is
    # now instant + deterministic, there is NO charge cache (cache=None): a stale/partial am1bcc cache could
    # otherwise contaminate one leg's charges and silently break cross-leg consistency.
    if not lig.conformers:
        lig.generate_conformers(n_conformers=1)
    from ternary_endpoint_stability import assign_rbfe_charges
    charge_used = assign_rbfe_charges(lig, MD.CHARGE_METHOD)
    _require(charge_used is not None,
             f"could not assign {MD.CHARGE_METHOD} charges to the ligand (openff-nagl missing from the env?)")

    # ALL integration/FF/solvation hyperparameters come from md_settings (canonical). Do NOT hardcode here — a
    # per-driver value is exactly how the 2 fs-vs-4 fs drift crept in. Sharing md_settings with the RBFE lane is
    # ENGINE HYGIENE (same integrator/FF, no unexplained knobs) — NOT validation transfer: ValB validates the
    # free-energy method for the NR4A RBFE matrix, not this endpoint-MD panel. This panel reports geometric
    # readouts and is validated by its own biological control (NR-V04 selectivity). See md_settings.py
    # "SCOPE OF WHAT SHARING THESE BUYS".
    sysgen = SystemGenerator(
        forcefields=list(MD.PROTEIN_FORCEFIELDS),
        small_molecule_forcefield=MD.SMALL_MOLECULE_FORCEFIELD,
        molecules=[lig],
        forcefield_kwargs=MD.systemgenerator_forcefield_kwargs(),
        cache=None,
    )

    modeller = app.Modeller(fixed_topology, fixed_positions)   # PDBFixer already added protein H + capped termini
    lig_top = lig.to_topology().to_openmm()
    lig_pos = lig.conformers[0].to_openmm()
    modeller.add(lig_top, lig_pos)
    modeller.addSolvent(sysgen.forcefield, model=MD.WATER_MODEL,
                        padding=MD.SOLVENT_PADDING_NM * unit.nanometer,
                        ionicStrength=MD.IONIC_STRENGTH_M * unit.molar)

    system = sysgen.create_system(modeller.topology)

    meta = {"n_atoms": modeller.topology.getNumAtoms(),
            "protein_heavy_atoms": n_before, "after_addH": n_after_h, "charge_method": charge_used,
            "reactive_cys": {"chain": react_chain, "resid": react_resid, "sg_electrophile_dist_A": round(react_dist, 2)}}
    if covalent:
        cov_pair = _covalent_indices(modeller.topology, ligand_sdf, cov_lig_atom, react_resid, react_chain)
        _add_covalent_restraint(system, cov_pair)
        meta["covalent_pair"] = {k: v for k, v in cov_pair.items() if k.endswith("_idx")}

    integrator = MD.openmm_integrator()                        # canonical LangevinMiddle (4 fs, matches ValB/OpenFE)
    platform = _select_platform(Platform)
    sim = app.Simulation(modeller.topology, system, integrator, platform)
    sim.context.setPositions(modeller.positions)
    return sim, modeller.topology, meta


def _select_platform(Platform):
    """Pick CUDA (GPU legs) else CPU (CI smoke). A conda-pack'd env can carry a STALE compiled OpenMM plugin dir
    so NO platform auto-loads — not even the built-in CPU (verified 2026-07-22 on Vast: 'no registered Platform
    called CPU' from the baked env). So if no platforms are present, explicitly load plugins from this env's
    lib/plugins first. OPENMM_REQUIRE_CUDA=1 (set for GPU legs) forbids the silent CPU fallback, which on a
    466k-atom system would be catastrophically slow instead of failing fast."""
    import glob
    have = lambda: [Platform.getPlatform(i).getName() for i in range(Platform.getNumPlatforms())]
    names = have()
    if "CUDA" not in names and "CPU" not in names:            # plugins didn't auto-load -> load them explicitly
        cands = []
        pref = os.environ.get("CONDA_PREFIX") or os.environ.get("OPENMM_PREFIX") or "/opt/mamba/envs/md"
        cands.append(os.path.join(pref, "lib", "plugins"))
        try:
            cands.append(Platform.getDefaultPluginsDirectory())
        except Exception:  # noqa: BLE001
            pass
        cands += glob.glob("/opt/mamba/envs/*/lib/plugins") + glob.glob(os.path.join(pref, "lib*", "plugins"))
        loaded = []
        for d in cands:
            if d and os.path.isdir(d):
                try:
                    Platform.loadPluginsFromDirectory(d); loaded.append(d)
                except Exception as e:  # noqa: BLE001
                    print(f"[nrv04-md] plugin load {d} failed: {e}", flush=True)
        names = have()
        print(f"[nrv04-md] reloaded OpenMM plugins from {loaded}; platforms now: {names}", flush=True)
    require_cuda = os.environ.get("OPENMM_REQUIRE_CUDA") == "1"
    if "CUDA" in names:
        return Platform.getPlatformByName("CUDA")
    if require_cuda:
        raise SystemExit(f"[nrv04-md] CUDA platform unavailable (platforms: {names}); OPENMM_REQUIRE_CUDA=1 "
                         f"forbids the slow CPU fallback — check the GPU/driver + OpenMM plugin load on this host")
    if "CPU" in names:
        return Platform.getPlatformByName("CPU")
    raise SystemExit(f"[nrv04-md] no usable OpenMM platform even after plugin reload (platforms: {names})")


def _add_covalent_restraint(system, cov):
    """Impose the frozen restrained-covalent geometry: stiff C6->Sγ bond + CB-Sγ-C6 and Sγ-C6-Cn angle
    restraints (prereg §2). Not a reparameterized junction — a geometric tether for endpoint MD."""
    from openmm import HarmonicBondForce, HarmonicAngleForce, unit
    k_bond = 300000.0 * unit.kilojoule_per_mole / unit.nanometer ** 2
    k_ang = 500.0 * unit.kilojoule_per_mole / unit.radian ** 2
    bf = HarmonicBondForce()
    bf.addBond(cov["sg_idx"], cov["ligc_idx"], 0.181 * unit.nanometer, k_bond)
    system.addForce(bf)
    af = HarmonicAngleForce()
    if cov.get("cb_idx") is not None:
        af.addAngle(cov["cb_idx"], cov["sg_idx"], cov["ligc_idx"], 1.90 * unit.radian, k_ang)   # ~109 deg
    if cov.get("lign_idx") is not None:
        af.addAngle(cov["sg_idx"], cov["ligc_idx"], cov["lign_idx"], 1.90 * unit.radian, k_ang)
    system.addForce(af)


def _target_chain_for_resnum(pdb_text, resnum):
    """Chain id carrying a CYS at `resnum` (the target LBD chain)."""
    for line in pdb_text.splitlines():
        if line[:6].strip() in ("ATOM", "HETATM") and line[17:20].strip() == "CYS":
            try:
                if int(line[22:26]) == resnum:
                    return line[21]
            except ValueError:
                pass
    raise SystemExit(f"[nrv04-md] no CYS at resnum {resnum} to anchor the covalent bond / mutation")


def _covalent_indices(topology, ligand_sdf, cov_lig_atom, cov_resnum, cov_chain=None):
    """Map the restraint atoms to OpenMM particle indices: Cys Sγ, Cys CB, ligand C6, and C6's ligand
    neighbour (for the second angle). The Cys is identified by (cov_chain, cov_resnum) as resolved by geometry in
    build_system (robust to the co-fold's renumbering); cov_chain=None falls back to resid-only matching."""
    sg_idx = cb_idx = ligc_idx = lign_idx = None
    cys_inventory = {}                                          # (chain,resid) -> set of atom names, for diagnostics
    for atom in topology.atoms():
        res = atom.residue
        if res.name == "CYS":
            cys_inventory.setdefault((getattr(res.chain, "id", "?"), res.id), set()).add(atom.name)
        chain_ok = cov_chain is None or getattr(res.chain, "id", None) == cov_chain
        if res.name == "CYS" and _resid(res) == cov_resnum and chain_ok:
            if atom.name == "SG":
                sg_idx = atom.index
            elif atom.name == "CB":
                cb_idx = atom.index
    # ligand atoms: SystemGenerator names them by element+serial in the ligand residue; match cov_lig_atom by
    # order in the SDF (C6 = the electrophile) and its first heavy neighbour.
    from rdkit import Chem
    mol = Chem.SDMolSupplier(ligand_sdf, removeHs=False)[0]
    c6_sdf_idx, neigh_sdf_idx = _electrophile_and_neighbour(mol, cov_lig_atom)
    lig_atoms = [a for a in topology.atoms() if a.residue.name in ("UNK", "LIG", "UNL")]
    if lig_atoms:
        if c6_sdf_idx < len(lig_atoms):
            ligc_idx = lig_atoms[c6_sdf_idx].index
        if neigh_sdf_idx is not None and neigh_sdf_idx < len(lig_atoms):
            lign_idx = lig_atoms[neigh_sdf_idx].index
    if sg_idx is None or ligc_idx is None:
        inv = ", ".join(f"{c}:{r}{'(+SG)' if 'SG' in a else ''}" for (c, r), a in sorted(cys_inventory.items()))
        raise SystemExit(f"[nrv04-md] could not locate covalent atoms (sg={sg_idx}, ligc={ligc_idx}) for "
                         f"cov_resnum={cov_resnum}. CYS residues present (chain:resid): [{inv}]")
    return {"sg_idx": sg_idx, "cb_idx": cb_idx, "ligc_idx": ligc_idx, "lign_idx": lign_idx}


def _electrophile_and_neighbour(mol, cov_lig_atom):
    """The celastrol Michael-acceptor carbon + a heavy neighbour, as 0-based SDF atom indices. Delegates to the
    single frozen definition in nrv04_ligands so the restraint site can't drift between the ligand builder and
    the MD driver. `cov_lig_atom` is kept for interface compatibility (the choice is structural, not name-based)."""
    from nrv04_ligands import electrophile_atom_index
    return electrophile_atom_index(mol)


def _resid(res):
    try:
        return int(res.id)
    except (ValueError, TypeError):
        return None


def _reactive_cys_by_geometry(pdb_text, ligand_sdf, cov_lig_atom):
    """Identify the reactive cysteine as the CYS whose Sγ is NEAREST the ligand's electrophilic carbon in the
    co-fold pose. Robust to the co-fold's residue renumbering (Boltz numbers from 1, so the UniProt 'Cys551'
    label does NOT appear — confirmed 2026-07-22: the target chain's cysteines were 121/131/161/190/207/222).
    Because the co-fold placed the celastrol warhead in the NR4A1 pocket, the nearest Sγ IS the modeled covalent
    partner, and this auto-selects the target chain (the warhead end of the PROTAC sits on NR4A1, not the E3).
    Returns (chain_id, resid_int, distance_angstrom). Raises if there are no cysteines."""
    from rdkit import Chem
    mol = Chem.SDMolSupplier(ligand_sdf, removeHs=False)[0]
    c6_idx, _ = _electrophile_and_neighbour(mol, cov_lig_atom)
    conf = mol.GetConformer()
    ep = conf.GetAtomPosition(c6_idx)                          # electrophile xyz (Å, same frame as complex.pdb)
    best = None                                                # (dist2, chain, resid)
    for line in pdb_text.splitlines():
        if line[:6].strip() not in ("ATOM", "HETATM"):
            continue
        if line[17:20].strip() != "CYS" or line[12:16].strip() != "SG":
            continue
        try:
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
            resid = int(line[22:26])
        except ValueError:
            continue
        d2 = (x - ep.x) ** 2 + (y - ep.y) ** 2 + (z - ep.z) ** 2
        if best is None or d2 < best[0]:
            best = (d2, line[21], resid)
    if best is None:
        raise SystemExit("[nrv04-md] no CYS Sγ found in the complex — cannot anchor the covalent warhead")
    return best[1], best[2], best[0] ** 0.5


# ---- orchestration --------------------------------------------------------------------------------------


def _aws_bin():
    import shutil
    return shutil.which("aws") or "/opt/mamba/envs/md/bin/aws"


def _s3_cp(src, dst, timeout=600):
    """Best-effort aws s3 cp (the aws CLI lives in the md env). Returns True on success, never raises."""
    import subprocess
    try:
        r = subprocess.run([_aws_bin(), "s3", "cp", src, dst], capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0
    except Exception:  # noqa: BLE001
        return False


def _ckpt_paths(out_dir, leg_id, seed):
    # OpenMM SERIALIZED STATE (XML) not saveCheckpoint(): the state is PORTABLE across hosts/GPUs, so a spot
    # preemption that re-lands the leg on a *different* box can still resume (saveCheckpoint is hardware-locked).
    return (os.path.join(out_dir, f"ckpt_{leg_id}_s{seed}.state.xml"),
            os.path.join(out_dir, f"ckpt_{leg_id}_s{seed}.ckpt.json"))


def _save_ckpt(sim, state_path, cj_path, state, result_s3):
    """Persist the simulation state (portable XML) + accumulated-readout JSON, then mirror both to S3 so a
    re-dispatched (preempted) leg can resume. Atomic local writes; S3 mirror is best-effort."""
    tmp = state_path + ".tmp"
    sim.saveState(tmp); os.replace(tmp, state_path)
    tmpj = cj_path + ".tmp"
    json.dump(state, open(tmpj, "w")); os.replace(tmpj, cj_path)
    if result_s3:
        _s3_cp(state_path, f"{result_s3}/{os.path.basename(state_path)}")
        _s3_cp(cj_path, f"{result_s3}/{os.path.basename(cj_path)}")


def _load_resume(state_path, cj_path, result_s3, leg_id, seed):
    """Return the accumulated-readout dict if a VALID in-progress production checkpoint exists (pull from S3 if
    not already local), else None. The caller then does sim.loadState(state_path)."""
    if result_s3 and not (os.path.exists(state_path) and os.path.exists(cj_path)):
        _s3_cp(f"{result_s3}/{os.path.basename(state_path)}", state_path)
        _s3_cp(f"{result_s3}/{os.path.basename(cj_path)}", cj_path)
    if not (os.path.exists(state_path) and os.path.exists(cj_path)):
        return None
    try:
        st = json.load(open(cj_path))
    except Exception:  # noqa: BLE001
        return None
    if (st.get("leg_id") == leg_id and st.get("seed") == seed and st.get("phase") == "production"
            and 0 < int(st.get("done_frames", 0)) < int(st.get("frames", 0))):
        return st
    return None


def _rm_ckpt(state_path, cj_path, result_s3):
    """Delete the checkpoint (local + S3) once the leg has finished, so a later re-dispatch re-runs cleanly
    instead of resuming a completed/terminated leg."""
    import subprocess
    for p in (state_path, cj_path):
        try:
            os.remove(p)
        except OSError:
            pass
    if result_s3:
        for name in (os.path.basename(state_path), os.path.basename(cj_path)):
            try:
                subprocess.run([_aws_bin(), "s3", "rm", f"{result_s3}/{name}"], capture_output=True, timeout=120)
            except Exception:  # noqa: BLE001
                pass


def _built_paths(out_dir, leg_id, seed):
    # The EXACT solvated system that produced a checkpoint (System XML + solvated topology as mmCIF + meta).
    # A resume MUST reload THIS rather than re-solvating: addSolvent/PDBFixer on a different host do NOT
    # reproduce a bit-identical atom count, so a rebuilt Context has the wrong particle count and
    # sim.loadState() throws "wrong number of positions". mmCIF (not PDB) carries the ~466k-atom topology
    # without the PDB 99999-atom-serial limit.
    b = os.path.join(out_dir, f"built_{leg_id}_s{seed}")
    return {"system": b + ".system.xml", "cif": b + ".solv.cif", "meta": b + ".built.json"}


def _save_built_system(bp, sim, topology, meta, result_s3):
    """Persist the solvated System (portable XML) + topology (mmCIF) + meta once at fresh build, so a later
    resume on a DIFFERENT host reloads this exact system and its atom count matches the checkpoint. S3 mirror
    is best-effort; a failed upload just means that preemption falls back to a clean restart."""
    from openmm import XmlSerializer, app
    tmp = bp["system"] + ".tmp"
    with open(tmp, "w") as f:
        f.write(XmlSerializer.serialize(sim.system))
    os.replace(tmp, bp["system"])
    pos = sim.context.getState(getPositions=True).getPositions()
    tmpc = bp["cif"] + ".tmp"
    with open(tmpc, "w") as f:
        app.PDBxFile.writeFile(topology, pos, f, keepIds=True)
    os.replace(tmpc, bp["cif"])
    json.dump(meta, open(bp["meta"], "w"))
    if result_s3:
        for p in bp.values():
            _s3_cp(p, f"{result_s3}/{os.path.basename(p)}")


def _load_built_system(bp, result_s3):
    """Reconstruct the Simulation from a persisted built-system snapshot (System XML + solvated mmCIF), so a
    resumed leg's Context matches the checkpoint's atom count exactly. Returns (sim, topology, meta) or None
    if the snapshot is unavailable/unreadable (-> caller does a clean fresh start). The existence check runs
    BEFORE any heavy import so the 'no snapshot' fallback needs neither OpenMM nor md_settings."""
    if result_s3:
        for p in bp.values():
            if not os.path.exists(p):
                _s3_cp(f"{result_s3}/{os.path.basename(p)}", p)
    if not all(os.path.exists(p) for p in bp.values()):
        return None
    import md_settings as MD
    from openmm import XmlSerializer, Platform, app
    try:
        cif = app.PDBxFile(bp["cif"])
        with open(bp["system"]) as f:
            system = XmlSerializer.deserialize(f.read())
        meta = json.load(open(bp["meta"]))
    except Exception:  # noqa: BLE001
        return None
    integrator = MD.openmm_integrator()
    platform = _select_platform(Platform)
    sim = app.Simulation(cif.topology, system, integrator, platform)
    sim.context.setPositions(cif.positions)                   # placeholder; loadState overwrites with the checkpoint
    return sim, cif.topology, meta


def run_leg(env):
    """Execute one leg from an env dict (see nrv04_covalent_panel.leg_env). Writes <OUTPUT_DIR>/leg_<id>_s<seed>.json.
    Checkpoint/resume: production is saved (portable OpenMM state + readout JSON) every CKPT_EVERY_FRAMES frames and
    mirrored to RESULT_S3, so a spot-preempted + re-dispatched leg RESUMES from the last saved frame. Resume reloads
    the EXACT persisted solvated system (built-system snapshot), never re-solvates, so the Context matches the
    checkpoint atom count (a rebuild would not -> loadState 'wrong number of positions')."""
    from openmm import unit, app

    import md_settings as MD                                   # canonical hyperparameters (single source of truth)

    leg_id = env["LEG_ID"]; seed = int(env["SEED"]); mode = env.get("MODE", "smoke")
    covalent = env.get("COVALENT") == "1"
    in_dir = os.path.join(env.get("INPUT_DIR", "/opt/ml/input/data"), leg_id)
    out_dir = env.get("OUTPUT_DIR", env.get("CKPT_DIR", "."))
    os.makedirs(out_dir, exist_ok=True)

    import numpy as _np
    import time

    def _pe_kj(_sim):
        return _sim.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(
            unit.kilojoule_per_mole)

    def _finite(_sim):
        p = _sim.context.getState(getPositions=True).getPositions(asNumpy=True)._value
        return bool(_np.isfinite(p).all())

    # sampling lengths canonical (env may override for a shakeout, else the md_settings defaults)
    prod_ns = float(env.get("PROD_NS", MD.PROD_NS)); equil_ns = float(env.get("EQUIL_NS", MD.EQUIL_NS))
    dt_ns = MD.TIMESTEP_NS
    if mode == "smoke":
        equil_steps, prod_steps, stride = 0, 500, 100          # ~cents; proves the pipeline
    else:
        equil_steps = int(equil_ns / dt_ns); prod_steps = int(prod_ns / dt_ns)
        stride = MD.frame_stride_steps()                       # ~10 ps frame cadence (timestep-independent)
    frames = max(1, prod_steps // stride)

    # --- checkpoint/resume: production is the multi-hour cost, so a spot preemption must not throw it away.
    # A resume needs BOTH a valid production checkpoint AND the built-system snapshot that produced it (reloaded
    # verbatim, never re-solvated). A checkpoint with no matching snapshot (a pre-fix leg) is un-resumable -> we
    # drop it and restart the leg cleanly (and persist a snapshot this time so future preemptions resume). ---
    result_s3 = env.get("RESULT_S3")
    ckpt_every = max(1, int(env.get("CKPT_EVERY_FRAMES", "50")))
    state_path, cj_path = _ckpt_paths(out_dir, leg_id, seed)
    built_paths = _built_paths(out_dir, leg_id, seed)
    resume = _load_resume(state_path, cj_path, result_s3, leg_id, seed)
    reloaded = _load_built_system(built_paths, result_s3) if resume is not None else None
    if resume is not None and reloaded is None:
        print("[nrv04-md] checkpoint present but no matching built-system snapshot -> restarting leg from frame 0",
              flush=True)
        _rm_ckpt(state_path, cj_path, result_s3)
        resume = None

    if resume is not None:
        sim, topology, meta = reloaded                         # exact persisted solvated system (atom count matches)
    else:
        sim, topology, meta = build_system(
            os.path.join(in_dir, "complex.pdb"), os.path.join(in_dir, "ligand.sdf"),
            covalent, env.get("COV_LIG_ATOM", "C6"), int(env.get("COV_RESNUM", "551")), env.get("MUTATION", ""))
        _save_built_system(built_paths, sim, topology, meta, result_s3)   # persist so future preemptions can resume
    chain_ids, e3_chains, target_chains, lys_nz = _topology_indices(topology)

    blew_up = False; blow_phase = None
    _timed_accum = 0.0; _wall_accum = 0.0
    if resume is not None:
        sim.loadState(state_path)                              # portable state -> resumes on ANY host/GPU
        e_pre = resume["e_pre"]; e_min = resume["e_min"]
        e3_side = resume["e3_side"]; tg_side = resume["tg_side"]; iface = resume["iface"]
        ref_iface = resume["ref_iface"]; ref_e3ca = resume["ref_e3ca"]; proxy = tuple(resume["proxy"])
        per_frame_contacts = resume["per_frame_contacts"]; iface_rmsds = resume["iface_rmsds"]
        lys_frames = resume["lys_frames"]; _done_frames = int(resume["done_frames"])
        _timed_accum = float(resume.get("timed_ns_accum", 0.0)); _wall_accum = float(resume.get("wall_accum", 0.0))
        print(f"[nrv04-md] RESUMED from checkpoint at frame {_done_frames}/{frames} (spot-preemption safe)", flush=True)
    else:
        # The covalent restraint imposes a stiff bond (k=3e5, eq 0.181 nm) across the co-fold's *non-bonded*
        # Sγ···C6 gap -> a large initial strain (~0.5·k·Δ² can reach tens of thousands of kJ/mol). Minimize then
        # equilibration must dissipate it; if they can't, the 4 fs HMR integrator blows up (NaN coords) and the
        # Kabsch SVD fails. Record energies + a finite guard so a blow-up is a REPORTED 'blew_up' outcome.
        e_pre = _pe_kj(sim)
        sim.minimizeEnergy()
        e_min = _pe_kj(sim)
        _pull_A = (meta.get("reactive_cys") or {}).get("sg_electrophile_dist_A")
        print(f"[nrv04-md] covalent={covalent} pull={_pull_A} Å  PE pre-min={e_pre:.4g} post-min={e_min:.4g} kJ/mol",
              flush=True)
        sim.context.setVelocitiesToTemperature(MD.TEMPERATURE_K * unit.kelvin, seed + 1)
        if equil_steps:                                        # equilibrate in chunks with a finite guard so a
            n_chunks = max(1, min(20, equil_steps // 500))     # blow-up is caught (and pinpointed) here, not later
            per = max(1, equil_steps // n_chunks); done = 0
            for _c in range(n_chunks):
                n = per if _c < n_chunks - 1 else (equil_steps - done)
                if n <= 0:
                    break
                sim.step(n); done += n
                if not _finite(sim):
                    blew_up = True; blow_phase = f"equil@{done}steps/{equil_steps}"
                    print(f"[nrv04-md] BLOW-UP in {blow_phase}: PE={_pe_kj(sim):.4g} kJ/mol", flush=True)
                    break
        # reference frame for R1 alignment (post-equil); indices are from this reference geometry
        ref_positions = _positions_nm(sim)
        e3_side, tg_side = interface_atom_indices(ref_positions, chain_ids, e3_chains, target_chains)
        iface = e3_side + tg_side
        ref_iface = [ref_positions[i] for i in iface]
        ref_e3ca = [ref_positions[i] for i in _ca_indices(topology, e3_chains)]
        proxy = _catalytic_proxy(ref_positions, chain_ids, e3_chains)
        per_frame_contacts, iface_rmsds, lys_frames = [], [], []
        _done_frames = 0
        if not blew_up:
            sim.step(stride)                                   # one warmup stride (kernel compile/JIT) before timing

    def _ckpt_state():
        return {"leg_id": leg_id, "seed": seed, "phase": "production", "frames": frames,
                "done_frames": _done_frames, "e_pre": e_pre, "e_min": e_min,
                "e3_side": e3_side, "tg_side": tg_side, "iface": iface,
                "ref_iface": ref_iface, "ref_e3ca": ref_e3ca, "proxy": list(proxy),
                "per_frame_contacts": per_frame_contacts, "iface_rmsds": iface_rmsds, "lys_frames": lys_frames,
                "timed_ns_accum": _done_frames * stride * dt_ns, "wall_accum": _wall_accum + (time.time() - _t0)}

    _t0 = time.time(); _resumed_from = _done_frames
    for _k in range(_done_frames, frames):
        if blew_up:
            break
        sim.step(stride)
        pos = _positions_nm(sim)
        if not _np.isfinite(_np.asarray(pos)).all():           # integrator diverged -> stop, record honestly
            blew_up = True; blow_phase = f"prod@frame{_k}/{frames}"
            print(f"[nrv04-md] BLOW-UP in {blow_phase}: PE={_pe_kj(sim):.4g} kJ/mol", flush=True)
            break
        per_frame_contacts.append(_contacts(pos, e3_side, tg_side))
        cur_e3ca = [pos[i] for i in _ca_indices(topology, e3_chains)]
        cur_iface = [pos[i] for i in iface]
        iface_rmsds.append(_aligned_iface_rmsd(cur_e3ca, ref_e3ca, cur_iface, ref_iface))
        lys_frames.append([pos[i] for i in lys_nz])
        _done_frames += 1
        if _done_frames % ckpt_every == 0 and _done_frames < frames:     # continuous checkpoint -> S3
            _save_ckpt(sim, state_path, cj_path, _ckpt_state(), result_s3)
            print(f"[nrv04-md] checkpoint @ frame {_done_frames}/{frames} -> S3", flush=True)

    _wall_accum += max(1e-6, time.time() - _t0)                # active-compute wall (excludes idle/preemption gaps)
    _timed_ns = _done_frames * stride * dt_ns
    _prod_wall_s = max(1e-6, _wall_accum)
    ns_per_day = round(_timed_ns / (_prod_wall_s / 86400.0), 2) if _done_frames else 0.0  # throughput -> $/ns
    print(f"[nrv04-md] production throughput: {ns_per_day} ns/day ({_timed_ns:.4f} ns in {_prod_wall_s:.1f}s active, "
          f"{_done_frames}/{frames} frames, resumed_from={_resumed_from}, blew_up={blew_up})", flush=True)

    # readouts (guarded: a blow-up may leave zero/partial frames -> report None, not a divide-by-zero crash)
    import nrv04_readouts as R
    r2 = R.recruitment(per_frame_contacts) if per_frame_contacts else {"recruited": None, "note": "no frames"}
    if iface_rmsds:
        _tail = iface_rmsds[len(iface_rmsds) // 2:]
        r1 = {"rmsd_series_mean": round(sum(iface_rmsds) / len(iface_rmsds), 3),
              "plateau_A": round(sum(_tail) / max(1, len(_tail)), 3)}
        r1["stable"] = r1["plateau_A"] < R.INTERFACE_RMSD_STABLE_A
    else:
        r1 = {"rmsd_series_mean": None, "plateau_A": None, "stable": False, "note": "no frames (blew up)"}
    r3 = R.lys_presentation(lys_frames, proxy) if (lys_nz and lys_frames) else {"min_A": None, "note": "no target Lys/frames"}

    result = {"panel": "nrv04_covalent_feasibility", "leg_id": leg_id, "seed": seed, "mode": mode,
              "covalent": covalent, "mutation": env.get("MUTATION", ""), "meta": meta,
              "md_settings": MD.summary(),                     # RECORD the exact canonical hyperparameters used
              "prod_ns": prod_ns, "equil_ns": equil_ns,
              "blew_up": blew_up, "blow_phase": blow_phase,    # numerical-stability outcome (covalent-pull strain)
              "pe_pre_min_kj": round(e_pre, 1), "pe_post_min_kj": round(e_min, 1),
              "ns_per_day": ns_per_day, "timed_ns": round(_timed_ns, 5), "prod_wall_s": round(_prod_wall_s, 1),
              "n_frames": len(per_frame_contacts), "R1_interface": r1, "R2_recruitment": r2, "R3_lys": r3}
    out = os.path.join(out_dir, f"leg_{leg_id}_s{seed}.json")
    json.dump(result, open(out, "w"), indent=2)
    print(f"[nrv04-md] wrote {out}: recruited={r2['recruited']} stable={r1['stable']}", flush=True)
    _rm_ckpt(state_path, cj_path, result_s3)                   # leg finished -> drop the checkpoint (a re-dispatch
    return result                                             # should re-run cleanly, not resume a completed leg)


def _aligned_iface_rmsd(cur_e3ca, ref_e3ca, cur_iface, ref_iface):
    """R1 per-frame: superpose the current frame's E3 CAs onto the reference, apply to the interface atoms,
    RMSD in Å. Uses the E3 CA superposition so the metric captures target motion relative to E3."""
    import numpy as np
    P = np.asarray(cur_e3ca); Q = np.asarray(ref_e3ca)
    if not (np.isfinite(P).all() and np.isfinite(Q).all()):    # non-finite coords -> caller's finite guard handles it
        return float("nan")
    Pc = P - P.mean(0); Qc = Q - Q.mean(0)
    try:
        V, _, Wt = np.linalg.svd(Pc.T @ Qc)
    except np.linalg.LinAlgError:                              # ill-conditioned covariance -> skip this frame's R1
        return float("nan")
    d = np.sign(np.linalg.det(V @ Wt))
    U = V @ np.diag([1, 1, d]) @ Wt
    ci = (np.asarray(cur_iface) - P.mean(0)) @ U
    ri = np.asarray(ref_iface) - Q.mean(0)
    return float(np.sqrt(np.mean(np.sum((ci - ri) ** 2, axis=1))) * 10.0)   # nm -> Å


def _contacts(pos, e3_side, tg_side, cutoff_nm=0.45):
    c2 = cutoff_nm ** 2; n = 0
    for i in e3_side:
        xi = pos[i]
        for j in tg_side:
            xj = pos[j]
            if (xi[0] - xj[0]) ** 2 + (xi[1] - xj[1]) ** 2 + (xi[2] - xj[2]) ** 2 <= c2:
                n += 1
    return n


def _positions_nm(sim):
    from openmm import unit
    return [(v.x, v.y, v.z) for v in sim.context.getState(getPositions=True).getPositions().value_in_unit(unit.nanometer)]


def _topology_indices(topology):
    chain_ids = [a.residue.chain.id for a in topology.atoms()]
    prot_chains = sorted({a.residue.chain.id for a in topology.atoms()
                          if a.residue.name not in ("HOH", "NA", "CL", "UNK", "LIG", "UNL")})
    # convention: E3 (VHL/EloB/EloC) are the first assembled chains, target LBD is the last protein chain
    e3_chains = set(prot_chains[:-1]) if len(prot_chains) > 1 else set(prot_chains)
    target_chains = {prot_chains[-1]} if len(prot_chains) > 1 else set()
    lys_nz = [a.index for a in topology.atoms()
              if a.residue.name == "LYS" and a.name == "NZ" and a.residue.chain.id in target_chains]
    return chain_ids, e3_chains, target_chains, lys_nz


def _ca_indices(topology, chains):
    return [a.index for a in topology.atoms() if a.name == "CA" and a.residue.chain.id in chains]


def _catalytic_proxy(positions_nm, chain_ids, e3_chains):
    """Coarse E2~Ub-presentation proxy: centroid of the E3 (VHL) chains (R3 is descriptive only, not a gate)."""
    pts = [positions_nm[i] for i, c in enumerate(chain_ids) if c in e3_chains]
    n = len(pts) or 1
    return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n, sum(p[2] for p in pts) / n)


def main():
    env = dict(os.environ)
    if "LEG_ID" not in env:
        raise SystemExit("[nrv04-md] LEG_ID not set (run via nrv04_covalent_panel.leg_env)")
    run_leg(env)


if __name__ == "__main__":
    sys.exit(main())
