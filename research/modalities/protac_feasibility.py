#!/usr/bin/env python3
"""
PROTAC assembly feasibility for the top NR4A3 warhead scaffolds — the next CPU step of
"design the degrader molecule in-silico." No GPU. Real fragments only (SMILES fetched from
ChEMBL; never hard-coded), so nothing is fabricated.

For each candidate warhead scaffold it (1) maps the **exit-vector handles** (amine/phenol/
carboxylic-acid atoms a linker can conjugate to) and (2) for each standard **E3 ligand**
(CRBN: pomalidomide/lenalidomide/thalidomide; VHL: VH032 if it resolves) x **linker**
(PEG2/PEG4/PEG6/alkyl-C6) predicts the **assembled PROTAC property envelope** (MW, HBA/HBD,
TPSA, rotatable bonds) by an additive/condensation estimate, and flags whether it lands in the
empirically typical PROTAC bRo5 window. This answers, concretely: *can these warheads be built
into a property-space-viable degrader, with which E3/linker, attached where?*

HONEST BOUNDS (in the output): this is an ADDITIVE property estimate, not a bonded SMILES; the
exit vector here is a chemical handle, while the TRUE attachment vector must be the
solvent-exposed position from the docked pose (a GPU/structure step); SAscore of the full
construct is approximated by the hardest fragment. So this is a feasibility/triage map for the
assembly, not a finished molecule.

Needs internet + RDKit -> runs on a GitHub-hosted CPU runner (protac-feasibility.yml).
Output: protac-feasibility.json
"""
import json
import os
import sys
import urllib.parse
import urllib.request

CHEMBL = "https://www.ebi.ac.uk/chembl/api/data"
WARHEADS = ["resveratrol", "chloroquine", "amodiaquine"]      # top developable + handle-bearing
WARHEAD_IDS = ["CHEMBL1873475"]                               # the docking top hit
E3_LIGANDS = ["pomalidomide", "lenalidomide", "thalidomide", "VH032"]  # non-resolving names skipped
# Linkers as real SMILES; descriptors computed with RDKit. (Spacers only; attachment implied.)
LINKERS = {"PEG2": "OCCOCCO", "PEG4": "OCCOCCOCCOCCO", "PEG6": "OCCOCCOCCOCCOCCOCCO",
           "alkyl-C6": "CCCCCC"}
# Empirically typical PROTAC property window (from PROTAC-DB-class compounds; ranges, not hard rules).
PROTAC_WINDOW = {"MW": (700, 1200), "HBA": (8, 16), "HBD": (1, 7), "TPSA": (120, 270),
                 "RotB": (10, 26)}
OUT = os.path.join(os.path.dirname(__file__), "protac-feasibility.json")


def _get(url, timeout=60):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0",
                                                       "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa
            import time
            print(f"  retry {i+1} {url[:80]}: {e}", file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError("failed: " + url)


def smiles_by_name(name):
    try:
        d = json.loads(_get(f"{CHEMBL}/molecule/search?q={urllib.parse.quote(name)}&format=json&limit=1"))
        m = (d.get("molecules") or [None])[0]
        if m:
            s = (m.get("molecule_structures") or {}).get("canonical_smiles")
            if s:
                return m.get("molecule_chembl_id"), s
    except Exception as e:  # noqa
        print(f"  name '{name}': {e}", file=sys.stderr)
    return None


def smiles_by_id(cid):
    try:
        d = json.loads(_get(f"{CHEMBL}/molecule/{cid}?format=json"))
        s = (d.get("molecule_structures") or {}).get("canonical_smiles")
        if s:
            return cid, s
    except Exception as e:  # noqa
        print(f"  id '{cid}': {e}", file=sys.stderr)
    return None


def desc(smiles, rd):
    Chem, Desc, Lip, rdMD = rd
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return None
    return {"MW": Desc.MolWt(m), "HBD": Lip.NumHDonors(m), "HBA": Lip.NumHAcceptors(m),
            "TPSA": Desc.TPSA(m), "RotB": Lip.NumRotatableBonds(m)}


def handles(smiles, rd):
    Chem = rd[0]
    m = Chem.MolFromSmiles(smiles)
    out = []
    for typ, sm in [("amine", "[NX3;H2,H1;!$(N-C=O);!$(N=*)]"),
                    ("phenol", "[OX2H][c]"), ("carboxylic_acid", "[CX3](=O)[OX2H1]")]:
        q = Chem.MolFromSmarts(sm)
        for match in m.GetSubstructMatches(q):
            out.append({"type": typ, "atom_idx": match[0]})
    return out


def in_window(v, lo_hi):
    return lo_hi[0] <= v <= lo_hi[1]


def main():
    from rdkit import Chem
    from rdkit.Chem import Descriptors as Desc, Lipinski as Lip, rdMolDescriptors as rdMD
    rd = (Chem, Desc, Lip, rdMD)

    warheads = []
    for nm in WARHEADS:
        r = smiles_by_name(nm)
        if r:
            warheads.append((nm, r[0], r[1]))
    for cid in WARHEAD_IDS:
        r = smiles_by_id(cid)
        if r:
            warheads.append((cid, r[0], r[1]))

    e3s = []
    for nm in E3_LIGANDS:
        r = smiles_by_name(nm)
        if r:
            e3s.append((nm, r[0], r[1]))
        else:
            print(f"  E3 ligand '{nm}' did not resolve in ChEMBL — skipped", file=sys.stderr)

    linker_desc = {k: desc(v, rd) for k, v in LINKERS.items()}

    warhead_rows = []
    for wname, wid, wsmi in warheads:
        wd = desc(wsmi, rd)
        if not wd:
            continue
        warhead_rows.append({"warhead": wname, "chembl_id": wid, "smiles": wsmi,
                             "exit_vectors": handles(wsmi, rd), **{f"warhead_{k}": round(v, 1)
                                                                   for k, v in wd.items()}})

    combos = []
    for wname, wid, wsmi in warheads:
        wd = desc(wsmi, rd)
        if not wd:
            continue
        for e3name, e3id, e3smi in e3s:
            ed = desc(e3smi, rd)
            if not ed:
                continue
            for lname, ld in linker_desc.items():
                if not ld:
                    continue
                # additive estimate with two condensation losses (~2 * H2O)
                est = {
                    "MW": round(wd["MW"] + ld["MW"] + ed["MW"] - 2 * 18.02, 1),
                    "HBA": wd["HBA"] + ld["HBA"] + ed["HBA"],
                    "HBD": max(0, wd["HBD"] + ed["HBD"] - 1),     # one donor consumed in a bond
                    "TPSA": round(wd["TPSA"] + ld["TPSA"] + ed["TPSA"] - 20, 1),
                    "RotB": wd["RotB"] + ld["RotB"] + ed["RotB"] + 2,
                }
                fits = {k: in_window(est[k], PROTAC_WINDOW[k]) for k in PROTAC_WINDOW}
                combos.append({
                    "warhead": wname, "E3_ligand": e3name, "linker": lname,
                    "est_MW": est["MW"], "est_HBA": est["HBA"], "est_HBD": est["HBD"],
                    "est_TPSA": est["TPSA"], "est_RotB": est["RotB"],
                    "in_protac_window": fits,
                    "window_fit_count": sum(fits.values()),
                })
    combos.sort(key=lambda c: (c["window_fit_count"], -abs(c["est_MW"] - 900)), reverse=True)

    result = {
        "_note": ("PROTAC assembly feasibility for the top NR4A3 warhead scaffolds. Real fragments "
                  "(warheads + E3 ligands fetched from ChEMBL); linkers are standard spacers. The "
                  "assembled properties are an ADDITIVE/condensation ESTIMATE (not a bonded SMILES); "
                  "exit_vectors are chemical handles (the TRUE attachment vector needs the docked pose); "
                  "this is a feasibility/triage map for building the degrader, not a finished molecule."),
        "protac_property_window_used": PROTAC_WINDOW,
        "n_warheads": len(warhead_rows), "n_E3_ligands": len(e3s),
        "E3_ligands_resolved": [e[0] for e in e3s],
        "warheads": warhead_rows,
        "linkers": {k: ({kk: round(vv, 1) for kk, vv in v.items()} if v else None)
                    for k, v in linker_desc.items()},
        "assembly_candidates": combos,
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(f"warheads={len(warhead_rows)} E3={len(e3s)} combos={len(combos)}")
    for w in warhead_rows:
        ev = ", ".join(f"{h['type']}@{h['atom_idx']}" for h in w["exit_vectors"]) or "NONE"
        print(f"  {w['warhead']:<16} exit-vectors: {ev}")
    print("  top assembly candidates (by PROTAC-window fit):")
    for c in combos[:6]:
        print(f"    {c['warhead']:<14}+{c['E3_ligand']:<13}+{c['linker']:<9} "
              f"MW~{c['est_MW']:.0f} RotB~{c['est_RotB']} fit={c['window_fit_count']}/5")


if __name__ == "__main__":
    main()
