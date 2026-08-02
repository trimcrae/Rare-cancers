#!/usr/bin/env python3
"""What molecule was actually co-folded into the NR4A ternaries? ($0 CPU)

⛔ THE PROVENANCE GAP THIS EXISTS TO CLOSE. The paper's §2.5 ternary result rests on a `denovo_401`-PROTAC,
and **the repo does not record which molecule that was.** `nr4a3_ternary_sagemaker.py` forwards it as the
environment variable `PROTAC_SMILES`; `nr4a3_ternary.py` writes the per-paralogue YAMLs to disk but they were
never committed; and `nr4a3-ternary-prep.json`, which would have captured it, holds
`"status": {"sequences": "error: <urlopen error Tunnel connection failed: 403 Forbidden>"}` and an empty
`targets` map. So the one surviving record of the co-folded molecule is **the ligand inside the deposited
model itself**.

★ WHY IT MATTERS RIGHT NOW, beyond bookkeeping. The one thing standing between this program and a testable
NR4A3 selectivity claim that is a GPU spend rather than a wet-lab fact is **replicate models per paralogue**
— Boltz was run without `--diffusion_samples`, so exactly one model exists per arm and reproducibility is
untestable. A replicate run must fold **the same molecule**; folding a different one would produce three new
structures that cannot be compared with the published result, and the difference would be invisible.

★ HOW THE SMILES IS RECOVERED, AND WHEN IT REFUSES. Boltz writes its ligands as non-polymer components; where
the output carries a `_chem_comp_bond` loop the bond orders are **sourced**, and the SMILES is exact. Where it
does not, bond orders would have to be perceived from coordinates, which for a novel PROTAC is a guess — so
this REFUSES rather than emitting a perceived SMILES that would silently become the input to a paid run.

⚠ AND THE THREE ARMS MUST AGREE. All three paralogue ternaries were folded with the SAME degrader, so the
three recovered molecules must be identical. If they are not, either the recovery is unreliable or the three
arms were not folded with one molecule — and both make the published cross-paralogue comparison unsafe. The
agreement check is the evidence that the recovery worked; it is not a formality.
"""
from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))

#: Smallest heavy-atom count that can be a PROTAC rather than an ion or a cryoprotectant. A VHL/CRBN-recruiting
#: degrader is ~50-90 heavy atoms; nothing this size is an accident.
MIN_DEGRADER_HEAVY = 30


def cif_ligand_bonds(path, comp_id):
    """{(atom_id_1, atom_id_2): order} from the model's own `_chem_comp_bond` loop, or (None, why).

    SOURCED, never perceived. The loop is what makes the recovered SMILES exact instead of a guess."""
    import selcal_deepternary_run as RUN
    try:
        text = open(path).read()
    except Exception as e:                                   # noqa: BLE001
        return None, "could not read %s: %s" % (os.path.basename(path), e)
    cols, rows = RUN._cif_loop(text, "_chem_comp_bond.")
    if not cols:
        return None, ("no `_chem_comp_bond` loop in %s — bond orders would have to be perceived from "
                      "coordinates, which for a novel PROTAC is a guess, and a guessed molecule must not "
                      "become the input to a paid run" % os.path.basename(path))
    idx = {c: i for i, c in enumerate(cols)}
    need = ["_chem_comp_bond.comp_id", "_chem_comp_bond.atom_id_1", "_chem_comp_bond.atom_id_2",
            "_chem_comp_bond.value_order"]
    missing = [c for c in need if c not in idx]
    if missing:
        return None, "the bond loop in %s lacks %s" % (os.path.basename(path), ", ".join(missing))
    out = {}
    for r in rows:
        if len(r) <= max(idx[c] for c in need):
            continue
        if comp_id and r[idx[need[0]]].upper() != comp_id.upper():
            continue
        out[(r[idx[need[1]]], r[idx[need[2]]])] = r[idx[need[3]]].upper()
    if not out:
        return None, "no bonds for component %s in %s" % (comp_id, os.path.basename(path))
    return out, None


ORDER = {"SING": 1, "DOUB": 2, "TRIP": 3, "AROM": 12}


def ligand_smiles_from_model(path):
    """(canonical SMILES, detail) for the degrader in one predicted model, or (None, why)."""
    import selcal_cofold_validate as V
    from rdkit import Chem
    from rdkit.Chem import rdchem

    atoms = V.parse_structure(path)
    lig = V.ligand_atoms(atoms, min_heavy=MIN_DEGRADER_HEAVY)
    if not lig:
        return None, {"error": "no non-polymer residue of >=%d heavy atoms in %s"
                               % (MIN_DEGRADER_HEAVY, os.path.basename(path))}
    comp = lig[0].resname
    bonds, berr = cif_ligand_bonds(path, comp)
    if berr:
        return None, {"error": berr, "component": comp, "n_heavy": len(lig)}

    em = Chem.RWMol()
    idx = {}
    for a in lig:
        at = Chem.Atom((a.element or a.name[:1]).capitalize())
        at.SetNoImplicit(False)
        idx[a.name] = em.AddAtom(at)
    used = 0
    for (n1, n2), order in bonds.items():
        if n1 in idx and n2 in idx:
            bt = {1: rdchem.BondType.SINGLE, 2: rdchem.BondType.DOUBLE,
                  3: rdchem.BondType.TRIPLE, 12: rdchem.BondType.AROMATIC}.get(ORDER.get(order, 1))
            em.AddBond(idx[n1], idx[n2], bt)
            used += 1
    mol = em.GetMol()
    try:
        Chem.SanitizeMol(mol)
    except Exception as e:                                   # noqa: BLE001
        return None, {"error": "recovered graph does not sanitize: %s" % e,
                      "component": comp, "n_heavy": len(lig), "n_bonds_used": used}
    smi = Chem.MolToSmiles(Chem.RemoveHs(mol))
    return smi, {"component": comp, "n_heavy": len(lig), "n_bonds_used": used,
                 "n_bonds_in_loop": len(bonds),
                 "_sourced": "bond orders from the model's own _chem_comp_bond loop, never perceived"}


def recover(model_paths):
    """{paralogue: (smiles, detail)} plus the agreement check the recovery's validity rests on."""
    per = {}
    for name, path in sorted(model_paths.items()):
        smi, detail = ligand_smiles_from_model(path)
        per[name] = {"model": os.path.basename(path), "smiles": smi, "detail": detail}
    got = {k: v["smiles"] for k, v in per.items() if v["smiles"]}
    doc = {"_what": "the molecule actually co-folded into this program's NR4A ternaries, recovered from the "
                    "models because the repo does not record it",
           "per_paralogue": per, "n_recovered": len(got), "n_arms": len(model_paths)}
    if not got:
        doc["agree"] = None
        doc["sentence"] = ("REFUSED — no arm's degrader could be recovered with sourced bond orders, so the "
                           "co-folded molecule is UNRECORDED and unrecoverable from these models. A replicate "
                           "run cannot be matched to the published result until it is supplied.")
        return doc
    uniq = sorted(set(got.values()))
    doc["distinct_smiles"] = uniq
    doc["agree"] = bool(len(uniq) == 1 and len(got) == len(model_paths))
    if doc["agree"]:
        doc["protac_smiles"] = uniq[0]
        doc["sentence"] = (
            "RECOVERED and CONSISTENT: all %d paralogue ternaries were folded with the same degrader, "
            "recovered with sourced bond orders as %s. A replicate run can now fold the same molecule, which "
            "is what makes its models comparable with the published one."
            % (len(got), uniq[0]))
    else:
        doc["sentence"] = (
            "REFUSED — the arms do not agree (%d recovered of %d, %d distinct molecule(s)). Either the "
            "recovery is unreliable or the three arms were not folded with one molecule, and both make the "
            "published cross-paralogue comparison unsafe. No SMILES is emitted for a paid run."
            % (len(got), len(model_paths), len(uniq)))
    return doc


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Recover the co-folded PROTAC from the NR4A ternaries ($0).")
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default=os.path.join(HERE, "nr4a-ternary-ligand-provenance.json"))
    args = ap.parse_args(argv)

    import nr4a_ternary_signature as N
    DENY = ("control", "binary", "apo")
    all_cif = sorted(glob.glob(os.path.join(args.root, "**", "*.cif"), recursive=True))
    paths = {}
    for p in (N.FOCUS,) + N.COMPARATORS:
        tok = p.lower()
        hits = [f for f in all_cif
                if tok in os.path.relpath(f, args.root).lower()
                and not any(d in os.path.relpath(f, args.root).lower() for d in DENY)
                and sum(1 for q in (N.FOCUS,) + N.COMPARATORS
                        if q.lower() in os.path.relpath(f, args.root).lower()) == 1]
        m0 = [f for f in hits if f.endswith("_model_0.cif")] or hits
        if len(m0) >= 1:
            paths[p] = m0[0]
    doc = recover(paths)
    doc["_why_it_is_not_in_the_repo"] = (
        "nr4a3_ternary_sagemaker.py forwards the molecule as $PROTAC_SMILES; nr4a3_ternary.py writes the "
        "per-paralogue YAMLs but they were never committed; and nr4a3-ternary-prep.json, which would have "
        "captured it, records a 403 on its sequence fetch and an empty targets map.")
    json.dump(doc, open(args.out, "w"), indent=1)
    for k, v in sorted(doc["per_paralogue"].items()):
        print("  %-7s %-38s %s" % (k, v["model"][:38],
                                   (v["smiles"] or ("REFUSED — %s" % v["detail"].get("error", ""))[:90])),
              flush=True)
    print(doc["sentence"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
