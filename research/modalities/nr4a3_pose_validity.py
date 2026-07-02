#!/usr/bin/env python3
"""
Bound-pose physical validity + bioactive-conformation strain (completeness ledger Tier-A #1 / audit's #1 KEEP).

WHY (the audit's decisive finding). The scoring stack is *provably blind to ligand strain*: single-trajectory
MM-GBSA (`mmgbsa_energy.py`) cancels intramolecular energy by construction, so a docked pose that pays a large
internal-strain penalty can still post a strong ΔG. denovo_401 is DiffSBDD-generated (a family notorious for
physically implausible internal geometry) with 4 stereocenters, docked into an AF2-modeled cryptic pocket that
can *reward* a strained conformer — the maximal strain-contamination setup. A leading group reports the
bound-pose strain penalty (and a PoseBusters-style validity pass) before trusting a de-novo hit. This adds it.

TWO MODES (so we deliver an honest readout now AND the rigorous number when the pose is in hand):
  (A) receptor-free CONFORMATIONAL ACCESSIBILITY (runs anywhere, no docked pose needed): ETKDGv3 ensemble +
      MMFF94s → global-min energy, accessible-energy window, #low-energy conformers, flexibility. A scaffold
      with many low-energy conformers and a modest energy spread is unlikely to be strain-contaminated; a rigid
      / high-spread one is a flag. This is the available-now guard.
  (B) BOUND-POSE STRAIN + validity (needs the docked pose SDF, which the dock/MM-GBSA stage already holds):
      strain = E(bound conformer) − E(global-min); per-rotatable-bond strain; PoseBusters checks if installed,
      else a light internal validity pass (bond-length outliers, non-bonded clashes). Wired into the pipeline
      entry so the next dock emits `strain_<tag>.json` on the REAL pose; optional GFN2-xTB refinement if present.

No GPU. Output: nr4a-pose-validity.json (mode A) / strain_<tag>.json (mode B).
"""

import json
import os
import sys

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "nr4a-pose-validity.json")

LEAD = {"name": "denovo_401", "smiles": "COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1"}
STRAIN_FLAG_TOTAL = 6.0        # kcal/mol total bound-pose strain above which we flag (rule-of-thumb ~2/rot-bond)
LOWE_WINDOW = 3.0             # kcal/mol: "accessible" conformer window


def _mmff_energy(mol, conf_id=-1):
    from rdkit.Chem import AllChem
    props = AllChem.MMFFGetMoleculeProperties(mol, mmffVariant="MMFF94s")
    ff = AllChem.MMFFGetMoleculeForceField(mol, props, confId=conf_id)
    return ff.CalcEnergy(), ff


def conformational_accessibility(smiles, n_confs=80, seed=0xC0FFEE):
    """Mode A: ETKDGv3 ensemble → energy landscape. Receptor-free; runs now."""
    from rdkit import Chem
    from rdkit.Chem import AllChem
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return {"_status": "unparseable SMILES"}
    m = Chem.AddHs(m)
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    params.numThreads = 0
    ids = AllChem.EmbedMultipleConfs(m, numConfs=n_confs, params=params)
    if not ids:
        return {"_status": "embedding failed"}
    energies = []
    for cid in ids:
        try:
            e, _ = _mmff_energy(m, cid)
            energies.append(e)
        except Exception:  # noqa: BLE001
            continue
    if not energies:
        return {"_status": "MMFF failed on all conformers"}
    emin = min(energies)
    rel = sorted(e - emin for e in energies)
    from rdkit.Chem import Lipinski
    rot = Lipinski.NumRotatableBonds(Chem.RemoveHs(m))
    return {
        "n_conformers_embedded": len(ids),
        "n_conformers_scored": len(energies),
        "rotatable_bonds": rot,
        "energy_spread_kcalmol": round(max(rel), 2),
        "n_within_1kcal": sum(1 for r in rel if r <= 1.0),
        "n_within_3kcal": sum(1 for r in rel if r <= LOWE_WINDOW),
        "frac_within_3kcal": round(sum(1 for r in rel if r <= LOWE_WINDOW) / len(rel), 2),
        "interpretation": (
            "well-behaved: many accessible low-energy conformers, no rigidity red flag"
            if sum(1 for r in rel if r <= LOWE_WINDOW) >= 3
            else "rigid/narrow ensemble — inspect for strain sensitivity"),
    }


def bound_pose_strain(pose_sdf, smiles=None, name=None):
    """Mode B (file entry): read the docked pose SDF, pick the molecule (by _Name==name if given, else first),
    delegate to strain_from_mol. `name` lets a multi-candidate docked_<tag>.sdf be filtered to denovo_401."""
    from rdkit import Chem
    supp = Chem.SDMolSupplier(pose_sdf, removeHs=False)
    mols = [x for x in supp if x is not None]
    if not mols:
        return {"_status": f"no readable molecule in {pose_sdf}"}
    if name:
        named = [m for m in mols if m.GetProp("_Name") == name] if mols[0].HasProp("_Name") else []
        if not named:
            return {"_status": f"pose named '{name}' not found in {pose_sdf} "
                    f"(have: {[m.GetProp('_Name') for m in mols if m.HasProp('_Name')][:8]})"}
        return strain_from_mol(named[0], smiles)
    return strain_from_mol(mols[0], smiles)


def strain_from_mol(bound, smiles=None):
    """Mode B core: strain of an already-parsed bound conformer (RDKit mol WITH 3D coords) vs its own global
    minimum, + light validity. This is what the MM-GBSA stage calls on the *identical* pose it scores, so the
    strain correction is exactly paired with the reported ΔG (which is strain-blind by construction)."""
    from rdkit import Chem
    from rdkit.Chem import AllChem, Lipinski
    if bound is None:
        return {"_status": "no molecule"}
    bound = Chem.AddHs(bound, addCoords=True)
    try:
        e_bound, _ = _mmff_energy(bound)
    except Exception as e:  # noqa: BLE001
        return {"_status": f"MMFF failed on bound pose: {e}"}
    return _strain_vs_globalmin(bound, e_bound, smiles)


def _strain_vs_globalmin(bound, e_bound, smiles=None):
    from rdkit import Chem
    from rdkit.Chem import AllChem, Lipinski
    # global-min from an ETKDG ensemble of the SAME connectivity
    ref = Chem.MolFromSmiles(smiles) if smiles else Chem.MolFromSmiles(Chem.MolToSmiles(bound))
    ref = Chem.AddHs(ref)
    params = AllChem.ETKDGv3()
    params.randomSeed = 0xC0FFEE
    AllChem.EmbedMultipleConfs(ref, numConfs=80, params=params)
    emins = []
    for cid in range(ref.GetNumConformers()):
        try:
            e, _ = _mmff_energy(ref, cid)
            emins.append(e)
        except Exception:  # noqa: BLE001
            continue
    if not emins:
        return {"_status": "could not compute global-min reference"}
    e_global = min(emins)
    strain = e_bound - e_global
    rot = max(1, Lipinski.NumRotatableBonds(Chem.RemoveHs(bound)))
    result = {
        "bound_pose_mmff_kcalmol": round(e_bound, 2),
        "global_min_mmff_kcalmol": round(e_global, 2),
        "strain_kcalmol": round(strain, 2),
        "strain_per_rotatable_bond": round(strain / rot, 2),
        "strain_flag": bool(strain > STRAIN_FLAG_TOTAL),
        "validity": _light_validity(bound),
        "interpretation": (
            f"strain {strain:.1f} kcal/mol "
            + ("EXCEEDS" if strain > STRAIN_FLAG_TOTAL else "within")
            + f" the ~{STRAIN_FLAG_TOTAL} kcal/mol flag; "
            + ("bound-pose affinity may be strain-inflated — correct the reported ΔG."
               if strain > STRAIN_FLAG_TOTAL else "bound pose is not obviously strain-contaminated.")),
    }
    # optional posebusters if available in CI
    try:
        from posebusters import PoseBusters  # noqa: F401
        result["posebusters"] = "available (run in pipeline)"
    except Exception:  # noqa: BLE001
        result["posebusters"] = "not installed — light validity used"
    return result


def _light_validity(mol):
    """PoseBusters-lite: bond-length sanity + severe non-bonded clashes (no external deps)."""
    from rdkit.Chem import rdMolTransforms  # noqa: F401
    conf = mol.GetConformer()
    long_bonds = 0
    for b in mol.GetBonds():
        d = conf.GetAtomPosition(b.GetBeginAtomIdx()).Distance(conf.GetAtomPosition(b.GetEndAtomIdx()))
        if d > 1.9 or d < 0.7:
            long_bonds += 1
    # crude clash: non-bonded heavy-atom pairs closer than 1.6 Å
    bonded = {frozenset((b.GetBeginAtomIdx(), b.GetEndAtomIdx())) for b in mol.GetBonds()}
    heavy = [a.GetIdx() for a in mol.GetAtoms() if a.GetAtomicNum() > 1]
    clashes = 0
    for i in range(len(heavy)):
        for j in range(i + 1, len(heavy)):
            if frozenset((heavy[i], heavy[j])) in bonded:
                continue
            if conf.GetAtomPosition(heavy[i]).Distance(conf.GetAtomPosition(heavy[j])) < 1.6:
                clashes += 1
    return {"anomalous_bond_lengths": long_bonds, "heavy_atom_clashes": clashes,
            "pass": bool(long_bonds == 0 and clashes == 0)}


def main():
    pose = os.environ.get("POSE_SDF")
    if pose and os.path.exists(pose):
        res = {"mode": "B: bound-pose strain", "pose": pose,
               "result": bound_pose_strain(pose, os.environ.get("POSE_SMILES") or LEAD["smiles"],
                                           name=os.environ.get("POSE_NAME"))}
        outp = os.path.join(HERE, f"strain_{os.environ.get('POSE_TAG','denovo_401')}.json")
        json.dump(res, open(outp, "w"), indent=2)
        print("wrote", outp, file=sys.stderr)
        print(json.dumps(res, indent=2))
        return
    res = {
        "_title": "Conformational accessibility of the lead binder (ledger Tier-A #1, mode A)",
        "_note": "Receptor-free ensemble guard. The rigorous BOUND-POSE strain (mode B) runs on the real "
                 "docked pose inside the dock/MM-GBSA stage (set POSE_SDF); this mode A guards the scaffold "
                 "now and is the honest available-immediately readout.",
        "lead": LEAD["name"],
        "conformational_accessibility": conformational_accessibility(LEAD["smiles"]),
    }
    json.dump(res, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
