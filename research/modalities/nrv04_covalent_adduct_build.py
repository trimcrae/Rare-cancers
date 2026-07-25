#!/usr/bin/env python3
"""
NR-V04 covalent panel — CONSTRUCT an A1-admissible preformed Michael adduct, or prove it cannot be constructed.

THE PROBLEM THIS SOLVES. Prereg AMENDMENT 1 criterion A1 requires a covalent leg to stage its electrophilic
carbon within `MAX_COVALENT_TETHER_A` of the target-chain Cys S-gamma. `nrv04_covalent_input_audit` measured A1
on every co-fold model in the bucket and every one FAILS at the frozen site: the celastrol electrophile sits
**28.4-39.1 A** from NR4A1 Cys551. The amendment's 8.99 A is the distance to a DIFFERENT cysteine (Cys566);
Cys551 was never the residue being measured.

So a co-folder will not produce this input, and the question becomes whether the adduct can be built **by
construction** -- which is the right way round anyway, because the covalent geometry is known chemistry rather
than something to hope a structure predictor discovers:

  * Celastrol reacts with a thiol by Michael addition at its A-ring quinone-methide beta-carbon
    (`nrv04_ligands.electrophile_atom_index`, the single frozen definition).
  * The reactive cysteine is Nur77/NR4A1 **C551**, established experimentally: Zhang et al., *Chem. Commun.*
    2018, 54, 13000-13003, doi:10.1039/C8CC06140H (PMID 30376017) -- celastrol is positioned by specific
    NONcovalent interactions next to the C551 thiol and then forms a REVERSIBLE covalent bond. The same work
    reports the solvent exposure of the six Nur77-LBD cysteines: C475/C505/C534 buried, C465/C566 partially
    exposed, **C551 highly exposed**. A highly exposed cysteine is a surface site, so an adduct there is not
    obviously blocked -- which is precisely what this script tests rather than assumes.

WHAT IT MEASURES, in order, stopping at the first thing that fails:

  1. **Is C551 present, and is its S-gamma actually exposed in THIS model?** Shrake-Rupley SASA on the S-gamma.
     A buried S-gamma cannot carry a preformed adduct at all.
  2. **REACHABILITY (the decisive one for the ternary legs).** With the VH032 recruiter held where the co-fold
     seats it in VHL, can the electrophile physically reach C551 S-gamma? Required = |anchor - S-gamma|.
     Available = the largest anchor->electrophile distance attainable by the actual molecule, measured over a
     large ETKDG conformer ensemble (an empirical, honest bound), with the all-anti topological bound reported
     alongside. If required > available the ternary co-fold's VHL-vs-NR4A1 placement is itself incompatible with
     a C551 adduct -- no pose search can fix that, only a different ternary arrangement.
  3. **Is there room at the adduct position?** Candidate C6 positions on the tetrahedral cone about
     CB->S-gamma; each scored for protein clash. All buried => no adduct geometry exists without remodelling
     the protein.
  4. **CONSTRUCTION.** Constrained conformer generation (C6 pinned at the adduct position, recruiter-in-VHL
     anchors pinned at their co-fold coordinates) followed by torsional/rigid-body refinement against a soft
     protein steric field. Best pose kept.
  5. **GATE.** The produced ligand pose is written back into a copy of the co-fold CIF (**protein coordinates
     untouched**) and A1 is re-measured on that artifact with the same code the driver uses. A construction that
     does not pass A1 is reported as a failure, not shipped.

The protein is RIGID throughout. This constructs an input; it does not relax a complex, and it makes no
affinity, cooperativity or efficacy claim. Language is 'a constructed preformed-adduct model', never a
prediction that the adduct forms.

$0: CPU only (rdkit + gemmi + numpy + scipy). Emits `nrv04-covalent-adduct-build.json` and, on success,
uploads the constructed CIF to a FRESH S3 prefix so it sits beside -- never on top of -- the co-folds it
derives from.
"""
from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nrv04_covalent_assemble import ligand_mol_from_coords  # noqa: E402
from nrv04_covalent_input_audit import (  # noqa: E402
    NR4A1_ACC,
    THREE2ONE,
    identify_chains_from_census,
    read_cif,
    resolve_lbd_offset,
    warhead_fragment_indices,
)
from nrv04_covalent_panel import TARGET_COV_RESNUM  # noqa: E402
from nrv04_ligands import LIGANDS, electrophile_atom_index  # noqa: E402

try:
    from nrv04_covalent_md import MAX_COVALENT_TETHER_A  # noqa: E402
except Exception:  # noqa: BLE001
    MAX_COVALENT_TETHER_A = float(os.environ.get("NRV04_MAX_TETHER_A", "8.0"))

CS_BOND_A = 1.81                 # C-S single bond, the prereg's restrained-covalent target length
CSC_ANGLE_DEG = 100.0            # C-S-C at a thioether sulfur (~100 deg, not tetrahedral)
CLASH_RMIN_A = 3.1               # heavy-atom soft-sphere contact distance for the steric term
SASA_PROBE_A = 1.4
# van der Waals radii (A) for the SASA calculation; Bondi.
VDW = {"C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80, "P": 1.80, "H": 1.20}


# ---------------------------------------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------------------------------------

def _np():
    import numpy as np
    return np


def sasa_shrake_rupley(all_xyz, all_elem, probe_idx, n_points=960):
    """Solvent-accessible surface area (A^2) of ONE atom in the context of the whole structure."""
    np = _np()
    xyz = np.asarray(all_xyz, dtype=float)
    radii = np.array([VDW.get(e, 1.70) for e in all_elem]) + SASA_PROBE_A
    c, r = xyz[probe_idx], radii[probe_idx]
    # golden-spiral sphere points
    k = np.arange(n_points) + 0.5
    phi = np.arccos(1 - 2 * k / n_points)
    theta = math.pi * (1 + 5 ** 0.5) * k
    pts = c + r * np.stack([np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)], axis=1)
    near = np.where((np.linalg.norm(xyz - c, axis=1) < r + radii.max()) &
                    (np.arange(len(xyz)) != probe_idx))[0]
    if len(near) == 0:
        return 4 * math.pi * r * r
    d = np.linalg.norm(pts[:, None, :] - xyz[near][None, :, :], axis=2)
    accessible = (d >= radii[near][None, :]).all(axis=1)
    return float(4 * math.pi * r * r * accessible.mean())


def adduct_candidate_positions(sg, cb, n_dihedral=72):
    """Candidate positions for the electrophilic carbon: CS_BOND_A from S-gamma, at CSC_ANGLE_DEG to CB,
    swept around the CB->S-gamma axis. Returns an (n,3) array."""
    np = _np()
    sg, cb = np.asarray(sg, float), np.asarray(cb, float)
    axis = sg - cb
    axis /= np.linalg.norm(axis)
    ref = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(ref, axis)) > 0.9:
        ref = np.array([0.0, 1.0, 0.0])
    u = np.cross(axis, ref)
    u /= np.linalg.norm(u)
    v = np.cross(axis, u)
    th = math.radians(180.0 - CSC_ANGLE_DEG)         # deviation of the S->C bond from the CB->S direction
    out = []
    for k in range(n_dihedral):
        p = 2 * math.pi * k / n_dihedral
        d = math.cos(th) * axis + math.sin(th) * (math.cos(p) * u + math.sin(p) * v)
        out.append(sg + CS_BOND_A * d)
    return np.array(out)


def clash_score(lig_xyz, tree, rmin=CLASH_RMIN_A, k=16):
    """Sum of squared soft-sphere overlaps against a KD-tree of protein heavy atoms, plus the worst overlap.

    Vectorised on purpose: this is the inner loop of the pose search and is evaluated ~10^5 times, so a
    per-pair Python loop makes the search cost hours instead of minutes."""
    np = _np()
    d, _ = tree.query(lig_xyz, k=k, distance_upper_bound=rmin)
    ov = np.clip(rmin - d, 0.0, None)                      # missing neighbours come back as inf -> 0
    ov = np.where(np.isfinite(ov), ov, 0.0)
    return float((ov ** 2).sum()), float(ov.max() if ov.size else 0.0)


# ---------------------------------------------------------------------------------------------------------
# ligand span
# ---------------------------------------------------------------------------------------------------------

def max_span(smiles, idx_a, idx_b, n_confs=300, seed=0xC0FFEE):
    """Largest distance between two heavy atoms attainable by the real molecule, over an ETKDG ensemble.

    This is an EMPIRICAL bound: ETKDG samples chemically reasonable conformers, so the maximum it finds is a
    conservative (low) estimate of the true maximum. Reported together with the all-anti topological bound
    (n_bonds x 1.25 A), which is an optimistic (high) estimate. A reachability call that is unambiguous under
    BOTH bounds is safe; one that falls between them is reported as such rather than decided."""
    from rdkit import Chem
    from rdkit.Chem import AllChem, rdmolops
    np = _np()
    m = Chem.AddHs(Chem.MolFromSmiles(smiles))
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    params.pruneRmsThresh = 0.5
    cids = AllChem.EmbedMultipleConfs(m, numConfs=n_confs, params=params)
    best = 0.0
    for cid in cids:
        c = m.GetConformer(cid)
        d = float(np.linalg.norm(np.array(c.GetAtomPosition(idx_a)) - np.array(c.GetAtomPosition(idx_b))))
        best = max(best, d)
    heavy = Chem.RemoveHs(m)
    path = rdmolops.GetShortestPath(heavy, idx_a, idx_b)
    n_bonds = max(len(path) - 1, 1)
    return {"empirical_max_A": round(best, 2), "n_conformers": len(cids),
            "topological_bonds": n_bonds, "all_anti_upper_bound_A": round(n_bonds * 1.25, 2)}


# ---------------------------------------------------------------------------------------------------------
# construction
# ---------------------------------------------------------------------------------------------------------

def rotatable_bonds(mol):
    from rdkit import Chem
    patt = Chem.MolFromSmarts("[!$(*#*)&!D1]-&!@[!$(*#*)&!D1]")
    return [tuple(b) for b in mol.GetSubstructMatches(patt)]


def torsion_quads(mol):
    """(i,j,k,l) dihedral definitions for every rotatable bond, for SetDihedralRad."""
    quads = []
    for j, k in rotatable_bonds(mol):
        nj = [a.GetIdx() for a in mol.GetAtomWithIdx(j).GetNeighbors() if a.GetIdx() != k]
        nk = [a.GetIdx() for a in mol.GetAtomWithIdx(k).GetNeighbors() if a.GetIdx() != j]
        if nj and nk:
            quads.append((nj[0], j, k, nk[0]))
    return quads


def _apply_state(mol, conf0_xyz, quads, x, base_mol):
    """Apply [3 translation, 3 rotation-vector, n torsions] to a copy of the reference conformer."""
    np = _np()
    from rdkit.Chem import rdMolTransforms as T
    from rdkit.Geometry import Point3D
    conf = base_mol.GetConformer()
    for i in range(base_mol.GetNumAtoms()):
        p = conf0_xyz[i]
        conf.SetAtomPosition(i, Point3D(float(p[0]), float(p[1]), float(p[2])))
    for q, ang in zip(quads, x[6:]):
        try:
            T.SetDihedralRad(conf, *q, float(ang))
        except Exception:  # noqa: BLE001 -- a degenerate quad; leave it alone
            pass
    xyz = np.array([list(conf.GetAtomPosition(i)) for i in range(base_mol.GetNumAtoms())])
    cen = xyz.mean(axis=0)
    rv = np.asarray(x[3:6], float)
    th = float(np.linalg.norm(rv))
    if th > 1e-9:
        k = rv / th
        K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
        R = np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * (K @ K)
        xyz = (xyz - cen) @ R.T + cen
    return xyz + np.asarray(x[:3], float)


def construct_adduct(heavy_mol, cofold_xyz, c6_idx, anchor_idx, anchor_xyz, target_pos, protein_tree,
                     w_cov=60.0, w_anchor=3.0, w_clash=12.0, n_restarts=12, seed=0, maxfev=15000):
    """Rigid-body + torsional search for a ligand pose that puts C6 at `target_pos`, keeps `anchor_idx` near
    `anchor_xyz`, and does not clash with the rigid protein. Returns the best state and its diagnostics."""
    np = _np()
    from scipy.optimize import minimize
    quads = torsion_quads(heavy_mol)
    base = type(heavy_mol)(heavy_mol)                     # working copy; its conformer is scratch space
    n = len(quads)
    rng = np.random.default_rng(seed)

    def objective(x):
        xyz = _apply_state(heavy_mol, cofold_xyz, quads, x, base)
        cov = float(np.linalg.norm(xyz[c6_idx] - target_pos)) ** 2
        anc = float(np.mean(np.linalg.norm(xyz[anchor_idx] - anchor_xyz, axis=1) ** 2)) if len(anchor_idx) else 0.0
        cl, _ = clash_score(xyz, protein_tree)
        return w_cov * cov + w_anchor * anc + w_clash * cl

    best = None
    for r in range(n_restarts):
        x0 = np.zeros(6 + n)
        if r > 0:
            x0[:3] = rng.normal(0, 2.0, 3)
            x0[3:6] = rng.normal(0, 0.5, 3)
            x0[6:] = rng.uniform(-math.pi, math.pi, n)
        res = minimize(objective, x0, method="Powell",
                       options={"maxfev": maxfev, "xtol": 1e-2, "ftol": 1e-2})
        if best is None or res.fun < best.fun:
            best = res
    xyz = _apply_state(heavy_mol, cofold_xyz, quads, best.x, base)
    cl, worst = clash_score(xyz, protein_tree)
    return {
        "xyz": xyz,
        "objective": float(best.fun),
        "c6_to_target_A": round(float(np.linalg.norm(xyz[c6_idx] - target_pos)), 2),
        "anchor_rmsd_A": (round(float(np.sqrt(np.mean(np.linalg.norm(xyz[anchor_idx] - anchor_xyz, axis=1) ** 2))), 2)
                          if len(anchor_idx) else None),
        "clash_sumsq": round(cl, 2),
        "worst_overlap_A": round(worst, 2),
        "n_torsions": n,
        "n_restarts": n_restarts,
    }


def write_cif_with_new_ligand(src_cif, dst_cif, new_lig_xyz):
    """Copy the co-fold CIF with ONLY the non-polymer ligand heavy atoms moved. Protein untouched, so the
    produced artifact differs from its source in exactly the quantity that was constructed."""
    import gemmi
    st = gemmi.read_structure(src_cif)
    k = 0
    for chain in st[0]:
        for res in chain:
            info = gemmi.find_tabulated_residue(res.name)
            is_poly = bool(info) and (info.is_amino_acid() or info.is_nucleic_acid()) and res.name in THREE2ONE
            if is_poly or res.name in ("HOH", "WAT"):
                continue
            for atom in res:
                if atom.element.name == "H":
                    continue
                p = new_lig_xyz[k]
                atom.pos = gemmi.Position(float(p[0]), float(p[1]), float(p[2]))
                k += 1
    if k != len(new_lig_xyz):
        raise SystemExit(f"[adduct] ligand atom count mismatch on write-back: wrote {k}, have {len(new_lig_xyz)}")
    st.setup_entities()
    doc = st.make_mmcif_document()
    doc.write_file(dst_cif)
    return k


# ---------------------------------------------------------------------------------------------------------

def build_from_model(cif_path, ligand_name, lbd_offset, out_cif=None, n_restarts=24):
    from rdkit import Chem
    from scipy.spatial import cKDTree
    np = _np()
    rep = {"source_cif": cif_path, "ligand": ligand_name, "frozen_site_fulllen": TARGET_COV_RESNUM}

    chains, lig = read_cif(cif_path)
    ident = identify_chains_from_census(chains)
    rep["chains"] = {k: ident[k] for k in ("census", "target_chain", "e3_chains", "e3_roles", "contaminant")}
    tgt = ident.get("target_chain")
    if not ident.get("admissible_assembly") or tgt is None:
        rep["verdict"] = "REJECTED_ASSEMBLY"
        rep["why"] = ident.get("why_no_target") or "contaminated assembly"
        return rep, None

    lbd_resid = TARGET_COV_RESNUM - lbd_offset
    cys = next((t for t in chains[tgt] if t[0] == lbd_resid), None)
    if cys is None or cys[1] != "CYS" or "SG" not in cys[2]:
        rep["verdict"] = "NO_FROZEN_SITE"
        rep["why"] = f"target residue {lbd_resid} (= full-length {TARGET_COV_RESNUM}) is not a CYS with SG"
        return rep, None
    sg, cb = np.array(cys[2]["SG"]), np.array(cys[2].get("CB", cys[2]["SG"]))

    # ---- protein atom cloud (all chains: the ligand must avoid the WHOLE assembly, not just the target) ----
    prot_xyz, prot_elem, prot_key = [], [], []
    for cid, residues in chains.items():
        for resid, resname, atoms in residues:
            for an, xyz in atoms.items():
                prot_xyz.append(xyz)
                prot_elem.append(an[0] if an[0] in VDW else "C")
                prot_key.append((cid, resid, an))
    prot_xyz = np.array(prot_xyz)
    tree = cKDTree(prot_xyz)

    # ---- (1) is C551 S-gamma exposed in THIS model? -------------------------------------------------------
    sg_i = prot_key.index((tgt, lbd_resid, "SG"))
    rep["frozen_site"] = {
        "lbd_resid": lbd_resid, "fulllen_resid": TARGET_COV_RESNUM,
        "sg_sasa_A2": round(sasa_shrake_rupley(prot_xyz, prot_elem, sg_i), 2),
        "reference": ("Zhang et al., Chem. Commun. 2018, doi:10.1039/C8CC06140H (PMID 30376017): celastrol "
                      "forms a REVERSIBLE covalent bond with Nur77/NR4A1 C551 after specific noncovalent "
                      "positioning; C551 is the highly-exposed cysteine of the six in the Nur77 LBD."),
    }

    # ---- ligand pose from the co-fold ---------------------------------------------------------------------
    mol = ligand_mol_from_coords(lig["elements"], lig["coords"], LIGANDS[ligand_name])
    heavy = Chem.RemoveHs(mol)
    c6_idx, _ = electrophile_atom_index(heavy)
    conf = heavy.GetConformer()
    lig_xyz = np.array([list(conf.GetAtomPosition(i)) for i in range(heavy.GetNumAtoms())])
    rep["electrophile_atom_idx"] = int(c6_idx)
    rep["as_cofold"] = {"c6_to_C551_sg_A": round(float(np.linalg.norm(lig_xyz[c6_idx] - sg)), 2)}

    # ---- anchors: recruiter heavy atoms actually touching VHL in the co-fold -------------------------------
    warhead = set(warhead_fragment_indices(heavy, c6_idx))
    vhl_chain = next((c for c, role in ident["e3_roles"].items() if role == "VHL"), None)
    vhl_xyz = np.array([xyz for resid, rn, atoms in chains.get(vhl_chain, []) for xyz in atoms.values()]) \
        if vhl_chain else np.zeros((0, 3))
    anchor_idx = []
    if len(vhl_xyz):
        vt = cKDTree(vhl_xyz)
        for i in range(len(lig_xyz)):
            if i in warhead:
                continue
            if vt.query_ball_point(lig_xyz[i], 4.5):
                anchor_idx.append(i)
    anchor_idx = np.array(anchor_idx, dtype=int)
    rep["anchors"] = {"n_recruiter_atoms_contacting_VHL": int(len(anchor_idx)),
                      "vhl_chain": vhl_chain,
                      "definition": "recruiter (non-warhead) heavy atoms within 4.5 A of VHL in the co-fold"}

    # ---- (2) REACHABILITY ---------------------------------------------------------------------------------
    if len(anchor_idx):
        # the anchor deepest in VHL is the reference point for the reach question
        deep = min(anchor_idx, key=lambda i: float(np.min(np.linalg.norm(vhl_xyz - lig_xyz[i], axis=1))))
        required = float(np.linalg.norm(lig_xyz[deep] - sg))
        span = max_span(LIGANDS[ligand_name], int(deep), int(c6_idx))
        rep["reachability"] = {
            "anchor_atom_idx": int(deep),
            "required_anchor_to_C551_sg_A": round(required, 2),
            "needed_allowing_for_the_C_S_bond_A": round(max(required - CS_BOND_A, 0.0), 2),
            **span,
            "reachable_under_empirical_bound": span["empirical_max_A"] >= required - CS_BOND_A,
            "reachable_under_topological_bound": span["all_anti_upper_bound_A"] >= required - CS_BOND_A,
        }
        rep["reachability"]["verdict"] = (
            "REACHABLE" if rep["reachability"]["reachable_under_empirical_bound"] else
            "AMBIGUOUS" if rep["reachability"]["reachable_under_topological_bound"] else
            "UNREACHABLE")
        if rep["reachability"]["verdict"] == "UNREACHABLE":
            rep["verdict"] = "UNREACHABLE"
            rep["why"] = (f"with the recruiter held in VHL as the co-fold places it, the electrophile must span "
                          f"{required:.1f} A to reach C551 S-gamma, but the molecule's largest attainable "
                          f"anchor->electrophile distance is {span['empirical_max_A']:.1f} A (all-anti upper "
                          f"bound {span['all_anti_upper_bound_A']:.1f} A). This ternary arrangement is "
                          f"incompatible with a C551 adduct; no pose search repairs it.")
            return rep, None
    else:
        rep["reachability"] = {"verdict": "N_A", "why": "no recruiter atoms contact VHL (free-warhead leg) — "
                                                        "the warhead is unconstrained, so reach is not limiting"}

    # ---- (3) is there room at the adduct position? --------------------------------------------------------
    cands = adduct_candidate_positions(sg, cb)
    room = []
    for p in cands:
        near = tree.query_ball_point(p, 6.0)
        near = [j for j in near if prot_key[j][:2] != (tgt, lbd_resid)]
        dmin = min((float(np.linalg.norm(p - prot_xyz[j])) for j in near), default=99.0)
        room.append({"pos": p, "min_protein_dist_A": dmin, "n_within_6A": len(near)})
    room.sort(key=lambda d: -d["min_protein_dist_A"])
    rep["adduct_site_room"] = {
        "n_candidates": len(cands),
        "best_min_protein_dist_A": round(room[0]["min_protein_dist_A"], 2),
        "n_candidates_with_clearance_ge_3.0A": sum(1 for d in room if d["min_protein_dist_A"] >= 3.0),
        "least_crowded_n_atoms_within_6A": room[0]["n_within_6A"],
    }
    if room[0]["min_protein_dist_A"] < 2.5:
        rep["verdict"] = "NO_ROOM"
        rep["why"] = (f"every candidate adduct position for C6 is within "
                      f"{room[0]['min_protein_dist_A']:.2f} A of a protein heavy atom — S-gamma is buried, so a "
                      f"preformed adduct cannot be staged without remodelling the protein")
        return rep, None
    target_pos = room[0]["pos"]

    # ---- (4) CONSTRUCT ------------------------------------------------------------------------------------
    built = construct_adduct(heavy, lig_xyz, int(c6_idx), anchor_idx,
                             lig_xyz[anchor_idx] if len(anchor_idx) else np.zeros((0, 3)),
                             target_pos, tree, n_restarts=n_restarts)
    new_xyz = built.pop("xyz")
    final_d = float(np.linalg.norm(new_xyz[c6_idx] - sg))
    rep["construction"] = built
    rep["construction"]["final_c6_to_C551_sg_A"] = round(final_d, 2)
    rep["construction"]["a1_limit_A"] = MAX_COVALENT_TETHER_A
    rep["construction"]["passes_A1"] = final_d <= MAX_COVALENT_TETHER_A
    rep["construction"]["at_covalent_bond_length"] = abs(final_d - CS_BOND_A) <= 0.25

    if out_cif:
        write_cif_with_new_ligand(cif_path, out_cif, new_xyz)
        rep["constructed_cif"] = out_cif
    rep["verdict"] = ("CONSTRUCTED" if rep["construction"]["passes_A1"] else "CONSTRUCTION_FAILED")
    if not rep["construction"]["passes_A1"]:
        rep["why"] = ("the constrained search could not bring the electrophile within the A1 limit without "
                      "an unacceptable clash or anchor displacement — see clash_sumsq / anchor_rmsd_A")
    return rep, (new_xyz if rep["construction"]["passes_A1"] else None)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Construct an A1-admissible preformed celastrol-C551 adduct.")
    ap.add_argument("--bucket", default=os.environ.get("VAST_CKPT_BUCKET", ""))
    ap.add_argument("--models", default="",
                    help="comma-sep S3 keys of co-fold CIFs; blank = read the audit JSON and take every clean one")
    ap.add_argument("--audit", default="research/modalities/nrv04-covalent-input-audit.json")
    ap.add_argument("--out", default="research/modalities/nrv04-covalent-adduct-build.json")
    ap.add_argument("--upload-prefix", default="",
                    help="FRESH S3 prefix for constructed CIFs (blank = do not upload)")
    ap.add_argument("--restarts", type=int, default=24)
    args = ap.parse_args(argv)

    import boto3
    s3 = boto3.client("s3") if args.bucket else None
    lbd_offset, off_prov = resolve_lbd_offset()

    jobs = []
    if args.models:
        for k in [x.strip() for x in args.models.split(",") if x.strip()]:
            sysname = next((s for s in ("nr4a1", "neg_inactive", "neg_celastrol") if f"/{s}/" in k), "nr4a1")
            jobs.append((k, {"nr4a1": "nrv04", "neg_inactive": "nrv04_epimer",
                             "neg_celastrol": "celastrol"}[sysname]))
    else:
        d = json.load(open(args.audit))
        for _p, pd in d["prefixes"].items():
            for _s, sd in pd["systems"].items():
                for r in (sd.get("models") or []):
                    if r.get("admissible_assembly"):
                        jobs.append((r["key"], sd["ligand"]))

    doc = {"lbd_offset": lbd_offset, "lbd_offset_provenance": off_prov,
           "a1_limit_A": MAX_COVALENT_TETHER_A, "cs_bond_A": CS_BOND_A,
           "uniprot": NR4A1_ACC, "models": []}
    print(f"[adduct] {len(jobs)} clean model(s) to attempt", flush=True)
    import time
    for n, (key, ligand) in enumerate(jobs, 1):
        # OBSERVABILITY (added after the first run took ~50 min with no way to tell advancing from stalled --
        # an in-progress GitHub job's log is not readable through the API). Per-model timing is printed, and the
        # partial JSON is mirrored to S3 after every model so a timeout still leaves the finished models.
        t0 = time.time()
        print(f"[adduct] ({n}/{len(jobs)}) starting {key}", flush=True)
        local = "/tmp/adduct_src.cif"
        s3.download_file(args.bucket, key, local)
        out_cif = "/tmp/adduct_built.cif"
        try:
            rep, xyz = build_from_model(local, ligand, lbd_offset, out_cif=out_cif, n_restarts=args.restarts)
        except Exception as e:  # noqa: BLE001
            rep, xyz = {"source_cif": key, "ligand": ligand, "verdict": "ERROR",
                        "why": f"{type(e).__name__}: {e}"}, None
        rep["s3_key"] = key
        rep["seconds"] = round(time.time() - t0, 1)
        if xyz is not None and args.upload_prefix and s3:
            dest = f"{args.upload_prefix.rstrip('/')}/{key.split('/')[-1].replace('.cif', '_adduct.cif')}"
            s3.upload_file(out_cif, args.bucket, dest)
            rep["uploaded"] = f"s3://{args.bucket}/{dest}"
        doc["models"].append(rep)
        print(f"  {key.split('/')[-1]:44s} verdict={rep['verdict']} "
              f"cofold_d={((rep.get('as_cofold') or {}).get('c6_to_C551_sg_A'))} "
              f"reach={(rep.get('reachability') or {}).get('verdict')} "
              f"built_d={((rep.get('construction') or {}).get('final_c6_to_C551_sg_A'))} "
              f"[{rep['seconds']}s]", flush=True)
        with open(args.out, "w") as f:
            json.dump(doc, f, indent=2, default=str)
        if s3 and args.upload_prefix:                      # continuous upload: a timeout keeps finished models
            try:
                s3.upload_file(args.out, args.bucket,
                               f"{args.upload_prefix.rstrip('/')}/_partial_adduct_build.json")
            except Exception as e:  # noqa: BLE001 -- observability must never fail the science
                print(f"[adduct] WARN partial upload failed: {e}", flush=True)

    ok = [m for m in doc["models"] if m.get("verdict") == "CONSTRUCTED"]
    doc["summary"] = {
        "n_attempted": len(doc["models"]),
        "n_constructed": len(ok),
        "admissible_input_exists": bool(ok),
        "best_final_c6_to_C551_sg_A": min((m["construction"]["final_c6_to_C551_sg_A"] for m in ok), default=None),
        "verdicts": {v: sum(1 for m in doc["models"] if m.get("verdict") == v)
                     for v in {m.get("verdict") for m in doc["models"]}},
    }
    with open(args.out, "w") as f:
        json.dump(doc, f, indent=2, default=str)
    print("\n=== ADDUCT CONSTRUCTION SUMMARY ===", flush=True)
    print(json.dumps(doc["summary"], indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
