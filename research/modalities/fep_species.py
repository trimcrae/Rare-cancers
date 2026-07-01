#!/usr/bin/env python3
"""Enumerate the 3D species to resolve BEFORE FEP — so we FEP the right molecule (pre-FEP checklist, F-plan).

denovo_401 has 4 DiffSBDD-assigned stereocenters (arbitrary chirality) → 16 diastereomers; we must confirm the
generated one is competitive (or switch to the best). denovo_111 has a basic pyrrolidine → neutral vs cationic
at pH 7.4 must be resolved. This module emits those species as a candidate set in the SAME shape the de-novo
dock funnel consumes (nr4a3_matrix.py candidate/SPECIES mode → dock into NR4A3/NR4A1/NR4A2 → MM-GBSA rank),
mirroring how decoy_library feeds the decoy control.

Pure logic + RDKit; the enumerated SMILES are stable so the set is reproducible.
"""

LEADS = {
    "denovo_401": "COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1",   # 4 stereocentres, neutral
    "denovo_111": "CC[C@H](C)c1cc(OCCO)cc(N2CCCC2)c1F",                       # basic pyrrolidine
}


def stereoisomers(smiles):
    """All distinct stereoisomers of a SMILES (canonical SMILES list). Marks nothing — caller tags."""
    from rdkit import Chem
    from rdkit.Chem.EnumerateStereoisomers import EnumerateStereoisomers, StereoEnumerationOptions
    m = Chem.MolFromSmiles(smiles)
    opts = StereoEnumerationOptions(onlyUnassigned=False, unique=True)
    out = []
    for iso in EnumerateStereoisomers(m, opts):
        out.append(Chem.MolToSmiles(iso))
    return sorted(set(out))


def protonation_variants(smiles):
    """Return {label: smiles} for the neutral form and, if a basic amine is present, the +1 cationic form
    (physiological pH 7.4). Aliphatic tertiary/secondary amine → protonated."""
    from rdkit import Chem
    m = Chem.MolFromSmiles(smiles)
    variants = {"neutral": Chem.MolToSmiles(m)}
    basic = Chem.MolFromSmarts("[NX3;!$(N=*);!$(N-C=[O,N,S]);!$(n)]")
    matches = m.GetSubstructMatches(basic)
    if matches:
        rw = Chem.RWMol(m)
        n_idx = matches[0][0]
        rw.GetAtomWithIdx(n_idx).SetFormalCharge(1)
        mh = rw.GetMol()
        Chem.SanitizeMol(mh)
        variants["cation"] = Chem.MolToSmiles(mh)
    return variants


def species_candidate_json():
    """denovo-funnel-shaped candidate set: denovo_401's stereoisomers (the generated one tagged) + denovo_111's
    protonation variants. Consumed by nr4a3_matrix.py SPECIES mode exactly like a generation set / the decoys."""
    from rdkit import Chem
    cands = []
    # denovo_401: 16 stereoisomers, flag the one matching the generated SMILES
    gen401 = Chem.MolToSmiles(Chem.MolFromSmiles(LEADS["denovo_401"]))
    for i, smi in enumerate(stereoisomers(LEADS["denovo_401"])):
        tag = "denovo_401_gen" if smi == gen401 else f"denovo_401_iso{i:02d}"
        cands.append({"name": tag, "smiles": smi, "denovo_promise": 1.0})
    # denovo_111: neutral + cation
    for label, smi in protonation_variants(LEADS["denovo_111"]).items():
        cands.append({"name": f"denovo_111_{label}", "smiles": smi, "denovo_promise": 1.0})
    return {"_note": "pre-FEP species resolution: denovo_401 stereoisomers + denovo_111 protonation variants",
            "campaign": "fep-species", "candidates": cands}


if __name__ == "__main__":
    import json
    print(json.dumps(species_candidate_json(), indent=2))
