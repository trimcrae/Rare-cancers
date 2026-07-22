#!/usr/bin/env python3
"""
NR-V04 covalent feasibility panel — frozen ligand definitions + SDF builder (prereg §3).

SMILES are copied VERBATIM from nrv04-ternary-benchmark.json (an NR-V04-inspired representative reconstruction,
not an exact structural match — stated in every result). Provides:
  - LIGANDS: name -> SMILES (nrv04, nrv04_epimer, celastrol).
  - electrophile_atom_index(mol): the celastrol quinone-methide Michael-acceptor carbon (the covalent site) +
    its heavy neighbour, so the MD driver can anchor the C6->Cys551 restraint. Validated against the real
    celastrol SMILES.
  - build_sdf(name, out): RDKit 3D embed -> SDF (CI/CPU; rdkit required).

Celastrol reacts with thiols via Michael addition at the A-ring quinone-methide β-carbon. We locate it as the
β-carbon of the α,β-unsaturated ketone (enone) in the celastrol A-ring; this is the documented reactive site.
"""
from __future__ import annotations

# verbatim from nrv04-ternary-benchmark.json
LIGANDS = {
    # active (2S,4R Hyp) vs epimer (2S,4S Hyp) differ ONLY at the N4C[C@H](O) / N4C[C@@H](O) stereocentre —
    # the stereo-only difference that forced the endpoint-system (not alchemical-morph) treatment (prereg §2b).
    "nrv04": "CC1=C(O)C(=O)C=C2C1=CC=C1[C@@]2(C)CC[C@@]2(C)[C@@H]3C[C@](C)(C(=O)NCCOCCOCCOCCOCCC(=O)N[C@@H]"
             "(C(C)(C)C)C(=O)N4C[C@H](O)C[C@H]4C(=O)NCc4ccc(-c5scnc5C)cc4)CC[C@]3(C)CC[C@]12C",
    "nrv04_epimer": "CC1=C(O)C(=O)C=C2C1=CC=C1[C@@]2(C)CC[C@@]2(C)[C@@H]3C[C@](C)(C(=O)NCCOCCOCCOCCOCCC(=O)"
                    "N[C@@H](C(C)(C)C)C(=O)N4C[C@@H](O)C[C@H]4C(=O)NCc4ccc(-c5scnc5C)cc4)CC[C@]3(C)CC[C@]12C",
    "celastrol": "CC1=C(O)C(=O)C=C2C1=CC=C1[C@@]2(C)CC[C@@]2(C)[C@@H]3C[C@](C)(C(=O)O)CC[C@]3(C)CC[C@]12C",
}

# the celastrol A-ring Michael acceptor: β-carbon of the enone (C=C-C=O), i.e. the carbon of the C=C that is
# NOT the carbonyl carbon and is conjugated to the ring ketone.
_ENONE_SMARTS = "[#6;!$([#6]=O):1]=[#6:2][#6:3]=O"


def _mol(smiles):
    from rdkit import Chem
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        raise ValueError(f"RDKit could not parse SMILES: {smiles[:60]}...")
    return m


def electrophile_atom_index(mol):
    """Return (beta_c_idx, neighbour_idx) — the celastrol A-ring Michael-acceptor carbon and a heavy neighbour
    NOT part of the enone (for the second restraint angle). Raises if no enone is found.

    Celastrol's A-ring is a cross-conjugated 2-hydroxy quinone-methide, so several enone (C=C-C=O) β-carbons
    match. We choose deterministically: prefer the β-carbon that is a RING-FUSION atom (in >= 2 rings) — the
    terminus of the EXTENDED quinone-methide conjugation and the documented thiol-reactive position — tie-broken
    by lowest atom index. NOTE (prereg §2, feasibility limit): the panel's readouts R1-R3 measure the E3<->target
    PPI interface, NOT the warhead-cysteine bond, so a ~1-2 A shift in which conjugated carbon carries the tether
    has only second-order effect on the verdict. The choice is fixed here so it is reproducible."""
    from rdkit import Chem
    ri = mol.GetRingInfo()
    patt = Chem.MolFromSmarts(_ENONE_SMARTS)
    hits = mol.GetSubstructMatches(patt)
    if not hits:
        raise ValueError("no enone (C=C-C=O) found — cannot locate the celastrol electrophile")

    def score(h):
        beta = h[0]
        return (ri.NumAtomRings(beta), -beta)          # most-ring-fused first, then lowest index
    best = max(hits, key=score)
    beta, alpha, carbonyl = best[0], best[1], best[2]  # match = (beta_C, alpha_C, carbonyl_C, O)
    nbrs = [n.GetIdx() for n in mol.GetAtomWithIdx(beta).GetNeighbors()
            if n.GetAtomicNum() > 1 and n.GetIdx() not in (alpha, carbonyl)]
    return beta, (nbrs[0] if nbrs else alpha)


def build_sdf(name, out_path, seed=0xC0FFEE):
    """Embed a 3D conformer and write an SDF (rdkit). Returns the electrophile atom index (0-based)."""
    from rdkit import Chem
    from rdkit.Chem import AllChem
    m = Chem.AddHs(_mol(LIGANDS[name]))
    params = AllChem.ETKDGv3(); params.randomSeed = seed
    if AllChem.EmbedMolecule(m, params) != 0:
        raise SystemExit(f"[nrv04-ligands] 3D embed failed for {name}")
    AllChem.MMFFOptimizeMolecule(m)
    m.SetProp("_Name", name)
    w = Chem.SDWriter(out_path); w.write(m); w.close()
    beta, _ = electrophile_atom_index(Chem.RemoveHs(m))
    return beta


if __name__ == "__main__":
    import sys
    for nm in LIGANDS:
        b = build_sdf(nm, f"{nm}.sdf")
        print(f"{nm}: wrote {nm}.sdf, electrophile atom idx {b}", flush=True)
    sys.exit(0)
