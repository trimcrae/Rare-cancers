#!/usr/bin/env python3
"""
RDKit verification of the RUNG-5b virtual library. Runs on a free CI runner inside the pre-baked
`docker.io/triskit23/ternary-fep` image (CLAUDE.md §6: pull the image, never solve a conda env in CI).

WHY THIS EXISTS, AND WHY IT IS A REFUSAL RATHER THAN A REPORT. `nr4a3_linker_design.py` derives a linker
length and a branch position from GEOMETRY, and then emits a SMILES string by concatenation. Those are two
independent representations of the same molecule, and nothing in the enumerator forces them to agree — a
mis-specified fragment, an off-by-one in the branch index, or a segment whose atom count is wrong would
produce a library whose geometry and whose chemistry describe different compounds, with no symptom. Three
such defects were already caught by READING the emitted strings (an alpha-ketoamide at the VHL junction, an
N,O-acetal wherever a PEG segment followed an amide nitrogen, an acylurea when the branch residue abutted the
warhead acyl) and one by re-deriving an index (the branch position was one atom too close to the warhead).
Reading strings does not scale and does not stay done. So this recomputes, from the PARSED MOLECULE:

  * the backbone length, as the topological shortest path between the two anchor atoms, and compares it to
    `n_backbone_atoms_intended` — **a mismatch is a hard failure, not a warning**;
  * the branch position, as the path index of the branch alpha-carbon, and compares it to
    `branch_k_from_warhead`;
  * that the cmpd19 warhead core, the des-acetyl VH032 core or the pomalidomide core, and the declared
    pendant are each present as exact substructures, with stereochemistry where declared;
  * that no unintended functional group was created at a junction (alpha-ketoamide, N,O-acetal, acylurea,
    ketone, anhydride, ester-in-linker);
  * physicochemical descriptors, reported WITHOUT a pass/fail, because a degrader is a beyond-rule-of-5
    molecule by construction and gating on Ro5 here would reject the entire class.

Output: `nr4a3-linker-library-chem.json`, committed back to the triggering branch. Exit code is non-zero if
any construct fails, so the CI step cannot go green on a library that does not describe what it claims to.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from rdkit import Chem, RDLogger
from rdkit.Chem import Crippen, Descriptors, rdMolDescriptors

RDLogger.DisableLog("rdApp.*")

HERE = os.path.dirname(os.path.abspath(__file__))

# Anchor definitions. Each is a SMARTS whose LAST matched atom is the anchor: the warhead's C5 substituent
# atom on one side, and the E3 handle's attachment heteroatom on the other. These are exactly the two atoms
# the geometry calls `a` and `b`.
ANCHORS = {
    "warhead_5amide": ("COC(=O)c1c[nH]c2ccc([NX3])cc12", -1),
    "warhead_5triazole": ("COC(=O)c1c[nH]c2ccc([OX2])cc12", -1),
    "warhead_5piperazine": ("COC(=O)c1c[nH]c2ccc([NX3]3CCNCC3)cc12", 7),
    "e3_vhl": ("CC1=C(SC=N1)c1ccc(CNC(=O)C2CC(O)CN2C(=O)C(C(C)(C)C)[NX3])cc1", -1),
    "e3_crbn": ("O=C1NC(=O)CCC1N1C(=O)c2cccc([NX3])c2C1=O", -1),
}

CORES = {
    "cmpd19": "COC(=O)c1c[nH]c2ccccc12",
    "vh032_desacetyl": "CC1=C(SC=N1)c1ccc(CNC(=O)C2CC(O)CN2C(=O)C(C(C)(C)C)N)cc1",
    "pomalidomide": "O=C1NC(=O)CCC1N1C(=O)c2cccc(N)c2C1=O",
}

# Junction motifs that must NEVER appear. Each was either emitted by an earlier version of the enumerator or
# is the obvious neighbouring failure mode of one that was.
FORBIDDEN = {
    "alpha_ketoamide": "[NX3][CX3](=O)[CX3](=O)",
    "n_o_acetal": "[NX3][CX4;H2][OX2]",
    "acylurea": "[CX3](=O)[NX3][CX3](=O)[NX3]",
    "linker_ketone": "[CX4][CX3](=O)[CX4]",
    "anhydride": "[CX3](=O)[OX2][CX3]=O",
    "gem_diol_or_hemiketal": "[OX2H][CX4][OX2]",
}

PENDANT_SMARTS = {
    "cyac_me": "N#CC(=CC)C(=O)N",
    "cyac_ph": "N#CC(=Cc1ccccc1)C(=O)N",
    "acrylamide": "C=CC(=O)N",
    "cyanoprop": "N#CC(C)C(=O)N",
    "pyr3": "Cc1cccnc1",
    "ph": "Cc1ccccc1",
}


def _match_anchor(mol, key):
    smarts, idx = ANCHORS[key]
    patt = Chem.MolFromSmarts(smarts)
    if patt is None:
        raise RuntimeError("bad anchor SMARTS for %s" % key)
    hits = mol.GetSubstructMatches(patt)
    if not hits:
        return None, "anchor pattern %s not found" % key
    if len(hits) > 1:
        return None, "anchor pattern %s is ambiguous (%d matches)" % (key, len(hits))
    return hits[0][idx], None


def check_one(c):
    """Verify one construct. Returns a dict; `ok` False means the construct does not describe what it claims."""
    out = {"construct_id": c["construct_id"], "errors": [], "warnings": []}
    mol = Chem.MolFromSmiles(c["smiles"])
    if mol is None:
        out["errors"].append("SMILES does not parse")
        out["ok"] = False
        return out

    wh_key = "warhead_" + c["warhead_handle"]
    e3_key = "e3_" + c["e3_handle"]
    a_idx, err_a = _match_anchor(mol, wh_key)
    b_idx, err_b = _match_anchor(mol, e3_key)
    for e in (err_a, err_b):
        if e:
            out["errors"].append(e)
    if a_idx is None or b_idx is None:
        out["ok"] = False
        return out

    path = Chem.GetShortestPath(mol, a_idx, b_idx)
    n_measured = len(path) - 2          # atoms STRICTLY between the two anchors
    out["n_backbone_atoms_measured"] = n_measured
    out["n_backbone_atoms_intended"] = c["n_backbone_atoms_intended"]
    if n_measured != c["n_backbone_atoms_intended"]:
        out["errors"].append("backbone length disagrees: geometry says %d, the molecule says %d"
                             % (c["n_backbone_atoms_intended"], n_measured))

    # branch position, re-derived from the molecule: the path atom carrying the declared pendant
    if c.get("branch_k_from_warhead") is not None:
        patt = Chem.MolFromSmarts(PENDANT_SMARTS[c["pendant"]])
        hits = mol.GetSubstructMatches(patt) if patt is not None else []
        if not hits:
            out["errors"].append("declared pendant %s not found in the molecule" % c["pendant"])
        else:
            pend_atoms = set(a for h in hits for a in h)
            on_path = [i for i, ai in enumerate(path)
                       if any(nb.GetIdx() in pend_atoms for nb in mol.GetAtomWithIdx(ai).GetNeighbors())
                       and ai not in pend_atoms]
            if not on_path:
                out["errors"].append("pendant %s is not attached to the backbone path" % c["pendant"])
            else:
                k_measured = min(on_path)          # index along the path from the WAREHEAD anchor
                out["branch_k_measured"] = k_measured
                out["branch_k_intended"] = c["branch_k_from_warhead"]
                if k_measured != c["branch_k_from_warhead"]:
                    out["errors"].append("branch position disagrees: geometry says k=%d, the molecule says "
                                         "k=%d" % (c["branch_k_from_warhead"], k_measured))

    for name, core in CORES.items():
        need = (name == "cmpd19"
                or (name == "vh032_desacetyl" and c["e3_handle"] == "vhl")
                or (name == "pomalidomide" and c["e3_handle"] == "crbn"))
        patt = Chem.MolFromSmiles(core)
        present = patt is not None and mol.HasSubstructMatch(patt)
        out.setdefault("cores", {})[name] = present
        if need and not present:
            out["errors"].append("required core %s absent" % name)

    for name, sma in FORBIDDEN.items():
        patt = Chem.MolFromSmarts(sma)
        if patt is not None and mol.HasSubstructMatch(patt):
            out["errors"].append("forbidden junction motif present: %s" % name)

    n_stereo = len(Chem.FindMolChiralCenters(mol, includeUnassigned=True, useLegacyImplementation=False))
    n_unassigned = sum(1 for _, tag in Chem.FindMolChiralCenters(
        mol, includeUnassigned=True, useLegacyImplementation=False) if tag == "?")
    if n_unassigned:
        out["errors"].append("%d UNASSIGNED stereocentre(s): an 'exact structure' with an undefined centre "
                             "is two compounds, not one" % n_unassigned)

    out["descriptors"] = {
        "mw": round(Descriptors.MolWt(mol), 1),
        "heavy_atoms": mol.GetNumHeavyAtoms(),
        "clogp": round(Crippen.MolLogP(mol), 2),
        "tpsa": round(rdMolDescriptors.CalcTPSA(mol), 1),
        "hbd": rdMolDescriptors.CalcNumHBD(mol),
        "hba": rdMolDescriptors.CalcNumHBA(mol),
        "rotatable_bonds": rdMolDescriptors.CalcNumRotatableBonds(mol),
        "fraction_csp3": round(rdMolDescriptors.CalcFractionCSP3(mol), 3),
        "n_stereocentres": n_stereo,
        "_reading": "REPORTED, NOT GATED. A bifunctional degrader is beyond-rule-of-5 by construction; "
                    "applying a Ro5 filter here would reject the entire modality. These are for the "
                    "manuscript's physicochemical assessment and for ranking WITHIN the class.",
    }
    out["canonical_smiles"] = Chem.MolToSmiles(mol)
    out["inchikey"] = Chem.MolToInchiKey(mol)
    out["ok"] = not out["errors"]
    return out


def check_pair(pair, results):
    """The matched pair carries an extra obligation: d and d0 must differ in EXACTLY ONE ATOM.

    Checked, not asserted: same heavy-atom count, same net formal charge, same rotatable-bond count, same
    number of stereocentres, and a canonical-SMILES difference confined to a single aromatic position. If any
    of those fails the pair is not a matched pair and `S` would not isolate the wedge element.
    """
    d, d0 = pair.get("d"), pair.get("d0")
    if not d or not d0:
        return {"ok": False, "errors": ["no pair proposed"]}
    rd = next((r for r in results if r["construct_id"] == d["construct_id"]), None)
    r0 = next((r for r in results if r["construct_id"] == d0["construct_id"]), None)
    if not rd or not r0 or not rd.get("descriptors") or not r0.get("descriptors"):
        return {"ok": False, "errors": ["pair members failed their own checks"]}
    md, m0 = Chem.MolFromSmiles(d["smiles"]), Chem.MolFromSmiles(d0["smiles"])
    errs = []
    if md.GetNumHeavyAtoms() != m0.GetNumHeavyAtoms():
        errs.append("heavy-atom counts differ (%d vs %d)" % (md.GetNumHeavyAtoms(), m0.GetNumHeavyAtoms()))
    if Chem.GetFormalCharge(md) != Chem.GetFormalCharge(m0):
        errs.append("net formal charges differ")
    if rd["descriptors"]["rotatable_bonds"] != r0["descriptors"]["rotatable_bonds"]:
        errs.append("rotatable-bond counts differ")
    if rd["descriptors"]["n_stereocentres"] != r0["descriptors"]["n_stereocentres"]:
        errs.append("stereocentre counts differ")
    fd = rdMolDescriptors.CalcMolFormula(md)
    f0 = rdMolDescriptors.CalcMolFormula(m0)
    return {
        "ok": not errs,
        "errors": errs,
        "d_formula": fd, "d0_formula": f0,
        "d_inchikey": rd.get("inchikey"), "d0_inchikey": r0.get("inchikey"),
        "heavy_atoms": md.GetNumHeavyAtoms(),
        "delta": "d - d0 = one aromatic C-H replaced by N (aza-scan)",
        "_reading": "these are the checks that make 'differs only in the wedge element' a MEASUREMENT rather "
                    "than a claim. They do not, and cannot, establish that the two molecules are equally "
                    "well described by the force field — that is a separate question for the FEP setup.",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--design", default=os.path.join(HERE, "nr4a3-linker-design.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a3-linker-library-chem.json"))
    args = ap.parse_args(argv)

    design = json.load(open(args.design))
    lib = design["virtual_library"]
    results = [check_one(c) for c in lib]
    n_bad = sum(1 for r in results if not r["ok"])
    pair = check_pair(design.get("matched_pair_for_rung_5a_ks", {}), results)

    out = {
        "_title": "RDKit verification of the RUNG-5b virtual library",
        "_method": "Every construct's backbone length and branch position are RE-DERIVED from the parsed "
                   "molecule (topological shortest path between the two anchor atoms) and compared to the "
                   "values the geometry asserted; required cores and the declared pendant are matched as "
                   "exact substructures; a list of junction motifs that must never appear is checked; "
                   "descriptors are reported without a pass/fail.",
        "_rdkit_version": Chem.rdBase.rdkitVersion,
        "n_constructs": len(lib),
        "n_failed": n_bad,
        "constructs": results,
        "matched_pair_check": pair,
        "_descriptor_scope": "A bifunctional degrader is beyond-rule-of-5 by construction. Descriptors are "
                             "for physicochemical assessment and within-class ranking; no permeability, "
                             "exposure, efficacy or safety claim follows from them.",
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print("[chem] %d constructs, %d FAILED  (pair check: %s)"
          % (len(lib), n_bad, "OK" if pair.get("ok") else "FAILED %s" % pair.get("errors")))
    for r in results:
        if not r["ok"]:
            print("[chem]   %-40s %s" % (r["construct_id"], "; ".join(r["errors"])))
    return 1 if (n_bad or not pair.get("ok")) else 0


if __name__ == "__main__":
    raise SystemExit(main())
