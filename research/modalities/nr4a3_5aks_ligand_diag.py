#!/usr/bin/env python3
"""RUNG 5a-KS — why did the NR4A1 leg's endpoint verification fail when NR4A3's passed?

THE OBSERVATION TO EXPLAIN (2026-07-26, both legs, same construct, same staged SMILES):

    NR4A3 arm : n_mapped 111, n_dummy_B  0, graph_identical TRUE  -> ok
    NR4A1 arm : n_mapped  80, n_dummy_B 31, graph_identical FALSE -> ABORT at preequil

`ternary_preequil._load_ligands` takes the SDF's two records verbatim as ligA/ligB, and this rung writes ONE
pose twice, so the two records are the same molecule by construction. Identical inputs cannot legitimately
give a 111/0 map on one leg and an 80/31 map on the other — so either the two legs' `ligands.sdf` are NOT in
fact chemically identical, or the perception of one of them is unstable.

The failure report named the difference: `smiles_in` carries the indole in a NON-aromatic Kekulé form
(`[H]C1=C(...)c2...N1[H]`) while `smiles_out` carries a properly aromatic one (`...c([H])n3[H]`). That is an
AROMATICITY PERCEPTION difference in the warhead's indole, nothing to do with the aza-scan.

WHAT THIS SCRIPT DOES, and why it is the discriminating measurement rather than another hypothesis: it reads
BOTH legs' staged `ligands.sdf` and, for each record, reports the canonical SMILES with and without
stereochemistry, the aromatic-atom count, the bond-order histogram and the per-record atom count. If the two
legs' records differ, the defect is in STAGING and the fix is upstream of the GPU. If they are identical and
the maps still differ, the defect is in PERCEPTION at read time and the fix is to write the SDF in a form
that cannot be re-perceived differently.

$0, CPU, and it must run inside `triskit23/ternary-fep` because the RDKit that reads the SDF here has to be
the one the leg reads it with — a different RDKit could perceive the same file differently, which is the very
thing under investigation.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def describe(mol, Chem):
    """Everything about a record that could differ between two legs and change a LOMAP map."""
    from rdkit import Chem as _C
    flat = _C.Mol(mol)
    _C.RemoveStereochemistry(flat)
    bond_hist = {}
    for b in mol.GetBonds():
        k = str(b.GetBondType())
        bond_hist[k] = bond_hist.get(k, 0) + 1
    return {
        "n_atoms": mol.GetNumAtoms(),
        "n_heavy": mol.GetNumHeavyAtoms(),
        "n_aromatic_atoms": sum(1 for a in mol.GetAtoms() if a.GetIsAromatic()),
        "n_aromatic_bonds": sum(1 for b in mol.GetBonds() if b.GetIsAromatic()),
        "bond_types": dict(sorted(bond_hist.items())),
        "canonical_smiles": _C.MolToSmiles(_C.RemoveHs(_C.Mol(mol))),
        "canonical_no_stereo": _C.MolToSmiles(_C.RemoveHs(flat)),
        "formula": __import__("rdkit.Chem.rdMolDescriptors", fromlist=["x"]).CalcMolFormula(mol),
    }


def main():
    from rdkit import Chem
    from rdkit import RDLogger
    RDLogger.DisableLog("rdApp.*")

    root = os.environ.get("STAGED_ROOT", "/tmp/5aks_legs_in")
    out = {}
    for leg_dir in sorted(glob.glob(os.path.join(root, "*", "ligands.sdf"))):
        leg = os.path.basename(os.path.dirname(leg_dir))
        recs = [m for m in Chem.SDMolSupplier(leg_dir, removeHs=False) if m is not None]
        out[leg] = {
            "sdf_bytes": os.path.getsize(leg_dir),
            "n_records": len(recs),
            "records": [{"name": (m.GetProp("_Name") if m.HasProp("_Name") else "?"),
                         **describe(m, Chem)} for m in recs],
        }
    print(json.dumps(out, indent=1), flush=True)

    legs = sorted(out)
    print("\n================ COMPARISON ================", flush=True)
    if len(legs) < 2:
        print(f"  only {len(legs)} leg(s) staged under {root} — cannot compare", flush=True)
        return 1

    a, b = out[legs[0]], out[legs[1]]
    # (1) do the two legs describe the same molecule at all?
    for i, (ra, rb) in enumerate(zip(a["records"], b["records"])):
        same_flat = ra["canonical_no_stereo"] == rb["canonical_no_stereo"]
        same_arom = ra["n_aromatic_atoms"] == rb["n_aromatic_atoms"]
        print(f"  record {i} ({ra['name']} vs {rb['name']}): constitution_same={same_flat} "
              f"aromatic_atoms {ra['n_aromatic_atoms']} vs {rb['n_aromatic_atoms']} "
              f"(same={same_arom})", flush=True)
        if not same_flat:
            print(f"    {legs[0]}: {ra['canonical_no_stereo']}", flush=True)
            print(f"    {legs[1]}: {rb['canonical_no_stereo']}", flush=True)

    # (2) within ONE leg, are the two records identical? They must be — this rung writes one pose twice.
    for leg in legs:
        r = out[leg]["records"]
        if len(r) == 2:
            ok = r[0]["canonical_no_stereo"] == r[1]["canonical_no_stereo"]
            print(f"  {leg}: its two records are the same molecule = {ok} "
                  f"(aromatic atoms {r[0]['n_aromatic_atoms']} / {r[1]['n_aromatic_atoms']})", flush=True)

    print("\n  READING: if constitution differs BETWEEN legs, the defect is in STAGING (fix upstream of the "
          "GPU).\n  If the legs agree here but the engine still built different maps, the defect is in "
          "PERCEPTION at\n  read time, and the SDF must be written so it cannot be re-perceived differently.",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
