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

    # optional C551A mutation applied at the text level before load (nrv04_covalent_stage)
    pdb_text = open(complex_pdb).read()
    cov_pair = None
    if mutation == "C551A":
        from nrv04_covalent_stage import mutate_cys_to_ala
        # target chain is resolved from the pair finder BEFORE mutation; here we mutate on the resolved chain
        chain = _target_chain_for_resnum(pdb_text, cov_resnum)
        pdb_text = mutate_cys_to_ala(pdb_text, chain, cov_resnum)
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

    # ALL integration/FF/solvation hyperparameters come from md_settings (canonical). Do NOT hardcode here — a
    # per-driver value is exactly how the 2 fs-vs-4 fs drift crept in. The endpoint-MD + ValB/RBFE lanes share
    # these so their MD is directly comparable.
    # FORCE-FIELD CHARGE CACHE (NRV04_FFCACHE): openmmforcefields keys the AM1-BCC-charged GAFF template by the
    # ligand's connectivity-only isomeric SMILES, so a cache pre-computed ONCE on free CPU (nrv04_charge_cache.py)
    # is reused by every leg — no GPU box ever pays the ~40-min single-core sqm charge of the 166-atom recruiter.
    # None (unset) => current behaviour (charge in-process). The same md_settings FF strings that populated the
    # cache are used here, so the keys match (baked-image env == cache-build env == this env).
    ffcache = os.environ.get("NRV04_FFCACHE") or None
    sysgen = SystemGenerator(
        forcefields=list(MD.PROTEIN_FORCEFIELDS),
        small_molecule_forcefield=MD.SMALL_MOLECULE_FORCEFIELD,
        molecules=[lig],
        forcefield_kwargs=MD.systemgenerator_forcefield_kwargs(),
        cache=ffcache,
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
            "protein_heavy_atoms": n_before, "after_addH": n_after_h}
    if covalent:
        cov_pair = _covalent_indices(modeller.topology, ligand_sdf, cov_lig_atom, cov_resnum)
        _add_covalent_restraint(system, cov_pair)
        meta["covalent_pair"] = {k: v for k, v in cov_pair.items() if k.endswith("_idx")}

    integrator = MD.openmm_integrator()                        # canonical LangevinMiddle (4 fs, matches ValB/OpenFE)
    try:
        platform = Platform.getPlatformByName("CUDA")
    except Exception:                                        # noqa: BLE001 — smoke on CPU CI runners
        platform = Platform.getPlatformByName("CPU")
    sim = app.Simulation(modeller.topology, system, integrator, platform)
    sim.context.setPositions(modeller.positions)
    return sim, modeller.topology, meta


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


def _covalent_indices(topology, ligand_sdf, cov_lig_atom, cov_resnum):
    """Map the restraint atoms to OpenMM particle indices: Cys Sγ, Cys CB, ligand C6, and C6's ligand
    neighbour (for the second angle). Reads C6's neighbour from the SDF via rdkit."""
    sg_idx = cb_idx = ligc_idx = lign_idx = None
    for atom in topology.atoms():
        res = atom.residue
        if res.name == "CYS" and _resid(res) == cov_resnum:
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
    _require(sg_idx is not None and ligc_idx is not None,
             f"could not locate covalent atoms (sg={sg_idx}, ligc={ligc_idx})")
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


# ---- orchestration --------------------------------------------------------------------------------------


def run_leg(env):
    """Execute one leg from an env dict (see nrv04_covalent_panel.leg_env). Writes <OUTPUT_DIR>/leg_<id>_s<seed>.json."""
    from openmm import unit, app

    import md_settings as MD                                   # canonical hyperparameters (single source of truth)

    leg_id = env["LEG_ID"]; seed = int(env["SEED"]); mode = env.get("MODE", "smoke")
    covalent = env.get("COVALENT") == "1"
    in_dir = os.path.join(env.get("INPUT_DIR", "/opt/ml/input/data"), leg_id)
    out_dir = env.get("OUTPUT_DIR", env.get("CKPT_DIR", "."))
    os.makedirs(out_dir, exist_ok=True)

    sim, topology, meta = build_system(
        os.path.join(in_dir, "complex.pdb"), os.path.join(in_dir, "ligand.sdf"),
        covalent, env.get("COV_LIG_ATOM", "C6"), int(env.get("COV_RESNUM", "551")), env.get("MUTATION", ""))

    sim.context.setVelocitiesToTemperature(MD.TEMPERATURE_K * unit.kelvin, seed + 1)
    sim.minimizeEnergy()

    # sampling lengths canonical (env may override for a shakeout, else the md_settings defaults)
    prod_ns = float(env.get("PROD_NS", MD.PROD_NS)); equil_ns = float(env.get("EQUIL_NS", MD.EQUIL_NS))
    dt_ns = MD.TIMESTEP_NS
    if mode == "smoke":
        equil_steps, prod_steps, stride = 0, 500, 100          # ~cents; proves the pipeline
    else:
        equil_steps = int(equil_ns / dt_ns); prod_steps = int(prod_ns / dt_ns)
        stride = MD.frame_stride_steps()                       # ~10 ps frame cadence (timestep-independent)
    if equil_steps:
        sim.step(equil_steps)

    # collect interface + Lys frames on the fly (NVT internal metrics need no alignment; R1 uses Kabsch)
    chain_ids, e3_chains, target_chains, lys_nz = _topology_indices(topology)
    ref_positions = _positions_nm(sim)
    e3_side, tg_side = interface_atom_indices(ref_positions, chain_ids, e3_chains, target_chains)
    iface = e3_side + tg_side
    ref_iface = [ref_positions[i] for i in iface]
    ref_e3ca = [ref_positions[i] for i in _ca_indices(topology, e3_chains)]

    per_frame_contacts, iface_rmsds, lys_frames = [], [], []
    frames = max(1, prod_steps // stride)
    for _ in range(frames):
        sim.step(stride)
        pos = _positions_nm(sim)
        per_frame_contacts.append(_contacts(pos, e3_side, tg_side))
        cur_e3ca = [pos[i] for i in _ca_indices(topology, e3_chains)]
        cur_iface = [pos[i] for i in iface]
        iface_rmsds.append(_aligned_iface_rmsd(cur_e3ca, ref_e3ca, cur_iface, ref_iface))
        lys_frames.append([pos[i] for i in lys_nz])

    # readouts
    import nrv04_readouts as R
    r2 = R.recruitment(per_frame_contacts)
    r1 = {"rmsd_series_mean": round(sum(iface_rmsds) / len(iface_rmsds), 3),
          "plateau_A": round(sum(iface_rmsds[len(iface_rmsds) // 2:]) / max(1, len(iface_rmsds) - len(iface_rmsds) // 2), 3)}
    r1["stable"] = r1["plateau_A"] < R.INTERFACE_RMSD_STABLE_A
    proxy = _catalytic_proxy(ref_positions, chain_ids, e3_chains)
    r3 = R.lys_presentation(lys_frames, proxy) if lys_nz else {"min_A": None, "note": "no target Lys"}

    result = {"panel": "nrv04_covalent_feasibility", "leg_id": leg_id, "seed": seed, "mode": mode,
              "covalent": covalent, "mutation": env.get("MUTATION", ""), "meta": meta,
              "md_settings": MD.summary(),                     # RECORD the exact canonical hyperparameters used
              "prod_ns": prod_ns, "equil_ns": equil_ns,
              "n_frames": len(per_frame_contacts), "R1_interface": r1, "R2_recruitment": r2, "R3_lys": r3}
    out = os.path.join(out_dir, f"leg_{leg_id}_s{seed}.json")
    json.dump(result, open(out, "w"), indent=2)
    print(f"[nrv04-md] wrote {out}: recruited={r2['recruited']} stable={r1['stable']}", flush=True)
    return result


def _aligned_iface_rmsd(cur_e3ca, ref_e3ca, cur_iface, ref_iface):
    """R1 per-frame: superpose the current frame's E3 CAs onto the reference, apply to the interface atoms,
    RMSD in Å. Uses the E3 CA superposition so the metric captures target motion relative to E3."""
    import numpy as np
    P = np.asarray(cur_e3ca); Q = np.asarray(ref_e3ca)
    Pc = P - P.mean(0); Qc = Q - Q.mean(0)
    V, _, Wt = np.linalg.svd(Pc.T @ Qc)
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
