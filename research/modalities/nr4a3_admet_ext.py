#!/usr/bin/env python3
"""
Extended ADMET / permeability liabilities for the lead binder (ledger F4/F5 + audit Tier-B #6).

WHY. The first-pass developability (`nr4a3_developability.py`) covered physchem + PAINS/BRENK + SA. The audit
(KEEP ×2) asked for the *permeability-relevant* layer a DMPK modeller would add for a molecule destined to
become a beyond-Rule-of-5 degrader: 3D exposure / conformational chameleonicity (intramolecular H-bonding that
lets a polar molecule hide its PSA to cross membranes), P-gp/BCRP efflux-substrate liability, and colloidal-
aggregation promiscuity (a distinct artifact class from PAINS). All RDKit / CPU, no GPU.

HONEST SCOPE. denovo_401 is the BINDER; the chameleonicity that really matters is the assembled PROTAC's (a
bRo5 molecule), which needs the linker/E3 build (ledger E4). Here we characterize the binder's 3D exposure
across its conformational ensemble (a genuine readout) and flag efflux/aggregation heuristically, and we note
where the full-PROTAC analysis must follow. Heuristics are labelled heuristics; nothing is a calibrated ADMET
prediction.

Output: nr4a-admet-ext.json.
"""

import json
import os
import sys

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "nr4a-admet-ext.json")
LEAD = {"name": "denovo_401", "smiles": "COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1"}


def _imhb_count(mol, conf_id):
    """Count intramolecular H-bonds (donor H ... acceptor within 2.5 A, not 1-2/1-3 bonded) in a 3D conformer."""
    from rdkit import Chem
    conf = mol.GetConformer(conf_id)
    donors_h, acceptors = [], []
    for a in mol.GetAtoms():
        if a.GetAtomicNum() in (7, 8):
            for nb in a.GetNeighbors():
                if nb.GetAtomicNum() == 1:
                    donors_h.append((nb.GetIdx(), a.GetIdx()))
            acceptors.append(a.GetIdx())
    n = 0
    for hidx, didx in donors_h:
        for acc in acceptors:
            if acc == didx:
                continue
            # skip if acceptor is bonded to the donor heavy atom (1-3)
            if mol.GetBondBetweenAtoms(didx, acc) is not None:
                continue
            d = conf.GetAtomPosition(hidx).Distance(conf.GetAtomPosition(acc))
            if d < 2.5:
                n += 1
    return n


def _rg(mol, conf_id):
    from rdkit.Chem import Descriptors3D
    return Descriptors3D.RadiusOfGyration(mol, confId=conf_id)


def chameleonicity_and_exposure(smiles, n_confs=60, seed=0xADDE7):
    from rdkit import Chem
    from rdkit.Chem import AllChem, rdMolDescriptors, Crippen, Lipinski, Descriptors
    m2d = Chem.MolFromSmiles(smiles)
    tpsa = rdMolDescriptors.CalcTPSA(m2d)
    clogp = Crippen.MolLogP(m2d)
    mw = Descriptors.MolWt(m2d)
    hbd, hba = Lipinski.NumHDonors(m2d), Lipinski.NumHAcceptors(m2d)
    m = Chem.AddHs(m2d)
    p = AllChem.ETKDGv3(); p.randomSeed = seed; p.numThreads = 0
    ids = AllChem.EmbedMultipleConfs(m, numConfs=n_confs, params=p)
    AllChem.MMFFOptimizeMoleculeConfs(m, mmffVariant="MMFF94s")
    imhb = [_imhb_count(m, c) for c in ids]
    rgs = [_rg(m, c) for c in ids]
    return {
        "tpsa_2d": round(tpsa, 1),
        "clogp": round(clogp, 2),
        "mw": round(mw, 1),
        "hbd": hbd, "hba": hba,
        "intramolecular_Hbonds_max": max(imhb) if imhb else 0,
        "intramolecular_Hbonds_mean": round(sum(imhb) / len(imhb), 2) if imhb else 0,
        "radius_of_gyration_min": round(min(rgs), 2) if rgs else None,
        "radius_of_gyration_max": round(max(rgs), 2) if rgs else None,
        "rg_range_chameleonicity": round(max(rgs) - min(rgs), 2) if rgs else None,
        "_note": "IMHB lets a molecule mask polar surface to cross membranes (relevant once it is a bRo5 "
                 "PROTAC); Rg range = conformational collapse/extension amplitude (chameleonicity proxy). "
                 "For the small binder TPSA is already low (29.5) so permeability is not PSA-limited.",
    }


def efflux_liability(smiles):
    """P-gp/BCRP substrate-likelihood HEURISTIC (not a calibrated model). Substrate risk rises with TPSA,
    HBA, MW; low here => low efflux risk for the binder."""
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors, Lipinski, Descriptors
    m = Chem.MolFromSmiles(smiles)
    tpsa = rdMolDescriptors.CalcTPSA(m); hba = Lipinski.NumHAcceptors(m); mw = Descriptors.MolWt(m)
    risk = (tpsa > 90) + (hba >= 8) + (mw > 500)
    return {"tpsa": round(tpsa, 1), "hba": hba, "mw": round(mw, 1),
            "pgp_substrate_risk_flags": int(risk),
            "assessment": "low" if risk == 0 else ("moderate" if risk == 1 else "elevated"),
            "_note": "heuristic (TPSA>90 / HBA>=8 / MW>500 raise P-gp substrate likelihood); binder is low-risk, "
                     "but efflux must be re-evaluated on the assembled bRo5 PROTAC."}


def aggregation_liability(smiles):
    """Colloidal-aggregation promiscuity HEURISTIC (distinct from PAINS). Aggregators skew lipophilic + flat +
    donor-poor; flag rises with clogp and aromatic content, falls with rotatable bonds/Fsp3."""
    from rdkit import Chem
    from rdkit.Chem import Crippen, rdMolDescriptors, Lipinski
    m = Chem.MolFromSmiles(smiles)
    clogp = Crippen.MolLogP(m); ar = rdMolDescriptors.CalcNumAromaticRings(m)
    fsp3 = rdMolDescriptors.CalcFractionCSP3(m); rot = Lipinski.NumRotatableBonds(m)
    flags = (clogp > 4) + (ar >= 3) + (fsp3 < 0.3)
    return {"clogp": round(clogp, 2), "aromatic_rings": ar, "fsp3": round(fsp3, 2), "rotatable_bonds": rot,
            "aggregation_risk_flags": int(flags),
            "assessment": "low" if flags <= 1 else ("moderate" if flags == 2 else "elevated"),
            "_note": "heuristic (high clogp / many aromatic rings / low Fsp3 raise colloidal-aggregation "
                     "likelihood). denovo_401 is high-Fsp3 (0.70) with one aromatic ring — low aggregation risk "
                     "despite clogp 4.63; the lipophilicity is the single watch-item, consistent with the "
                     "developability report."}


def main():
    res = {
        "_title": "Extended ADMET / permeability liabilities — lead binder (ledger F4/F5, audit Tier-B #6)",
        "_source": "RDKit (conformer ensemble IMHB/Rg; heuristic efflux + aggregation flags)",
        "lead": LEAD["name"],
        "chameleonicity_and_3d_exposure": chameleonicity_and_exposure(LEAD["smiles"]),
        "efflux_liability_heuristic": efflux_liability(LEAD["smiles"]),
        "aggregation_liability_heuristic": aggregation_liability(LEAD["smiles"]),
    }
    json.dump(res, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
