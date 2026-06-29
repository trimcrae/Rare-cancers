#!/usr/bin/env python3
"""
Cheminformatic characterization of the NR4A3 warhead-screen hits — the CPU half of
"design the degrader molecule in-silico." No GPU. No wet lab. Real molecules only.

For each compound the warhead screen actually docked (the same ChEMBL NR4A-relevant set as
nr4a3_dock.py, plus the reported top hit CHEMBL1873475), this computes a drug-likeness /
synthesizability / liability / PROTAC-handle profile with RDKit:
  - physicochemistry: MW, cLogP, HBD, HBA, TPSA, rotatable bonds, aromatic rings, fraction Csp3
  - drug-likeness: QED, Lipinski Ro5 violations, Veber pass, beyond-Ro5 flag (PROTAC-relevant)
  - synthesizability: SAscore (RDKit Contrib SA_Score; ~1 easy .. 10 hard)
  - structural-alert liabilities: PAINS and BRENK catalog hits (count + which)
  - PROTAC attachment handles: counts of amine / phenol / carboxylic-acid groups a linker
    could conjugate to (the exit-vector chemistry for warhead->linker->E3 assembly)

SMILES are fetched live from ChEMBL (never hard-coded; names that don't resolve are skipped),
so this needs internet + RDKit -> runs on a GitHub-hosted CPU runner (warhead-chem-profile.yml);
output is published to the modalities-cache branch. Triage only; not a validated lead.

Output: warhead-chem-profile.json
"""
import json
import os
import sys
import urllib.parse
import urllib.request

CHEMBL = "https://www.ebi.ac.uk/chembl/api/data"
# Same NR4A-relevant set the docking screen used (nr4a3_dock.LIGAND_NAMES) + the reported top hit.
LIGAND_NAMES = ["celastrol", "cytosporone B", "amodiaquine", "chloroquine",
                "piperlongumine", "resveratrol"]
EXTRA_IDS = ["CHEMBL1873475"]                       # top NR4A3-favoured hit from the warhead screen
OUT = os.path.join(os.path.dirname(__file__), "warhead-chem-profile.json")


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
        d = json.loads(_get(f"{CHEMBL}/molecule/search?q={urllib.parse.quote(name)}"
                            f"&format=json&limit=1"))
        mols = d.get("molecules", [])
        if mols:
            s = (mols[0].get("molecule_structures") or {}).get("canonical_smiles")
            if s:
                return mols[0].get("molecule_chembl_id"), s
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


def profile(smiles, rdkit):
    Chem, Desc, Crippen, Lip, QED, rdMD, FilterCatalog, FilterCatalogParams, sascorer = rdkit
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return {"error": "unparseable SMILES"}
    mw = Desc.MolWt(m); logp = Crippen.MolLogP(m)
    hbd = Lip.NumHDonors(m); hba = Lip.NumHAcceptors(m)
    tpsa = Desc.TPSA(m); rotb = Lip.NumRotatableBonds(m)
    ro5 = sum([mw > 500, logp > 5, hbd > 5, hba > 10])
    # structural alerts
    def alerts(catalog_enum):
        p = FilterCatalogParams(); p.AddCatalog(catalog_enum)
        cat = FilterCatalog(p)
        return [e.GetDescription() for e in cat.GetMatches(m)]
    pains = alerts(FilterCatalogParams.FilterCatalogs.PAINS)
    brenk = alerts(FilterCatalogParams.FilterCatalogs.BRENK)
    # PROTAC attachment handles (where a linker could be conjugated)
    def n(sm):
        q = Chem.MolFromSmarts(sm)
        return len(m.GetSubstructMatches(q)) if q else 0
    amine = n("[NX3;H2,H1;!$(N-C=O);!$(N=*)]")
    phenol = n("[OX2H][c]")
    cooh = n("[CX3](=O)[OX2H1]")
    try:
        sa = round(sascorer.calculateScore(m), 2)
    except Exception:  # noqa
        sa = None
    # stability/reactivity structural alerts (beyond PAINS/BRENK) — the developability gate the de-novo
    # red-team added after artifacts (carbamic acid, peroxide, ...) topped the funnel
    try:
        import structural_alerts as _sa
        liabilities = _sa.find_liabilities(m, Chem)
    except Exception:  # noqa — never let the alert step break profiling
        liabilities = []
    return {
        "MW": round(mw, 1), "cLogP": round(logp, 2), "HBD": hbd, "HBA": hba,
        "TPSA": round(tpsa, 1), "RotB": rotb, "FractionCsp3": round(rdMD.CalcFractionCSP3(m), 2),
        "aromatic_rings": rdMD.CalcNumAromaticRings(m),
        "QED": round(QED.qed(m), 3), "SAscore": sa,
        "Ro5_violations": ro5, "beyond_Ro5": ro5 >= 2,
        "veber_pass": (rotb <= 10 and tpsa <= 140),
        "PAINS_alerts": pains, "BRENK_alert_count": len(brenk),
        "structural_liabilities": liabilities,
        "protac_handles": {"amine": amine, "phenol": phenol, "carboxylic_acid": cooh,
                           "total": amine + phenol + cooh},
    }


def main():
    # import RDKit lazily so the file imports/compiles without it (it runs on the CI runner)
    from rdkit import Chem
    from rdkit.Chem import Descriptors as Desc, Crippen, Lipinski as Lip, QED, rdMolDescriptors as rdMD
    from rdkit.Chem import RDConfig
    from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams
    sys.path.append(os.path.join(RDConfig.RDContribDir, "SA_Score"))
    import sascorer
    rdkit = (Chem, Desc, Crippen, Lip, QED, rdMD, FilterCatalog, FilterCatalogParams, sascorer)

    mols = []
    for nm in LIGAND_NAMES:
        r = smiles_by_name(nm)
        if r:
            mols.append((nm, r[0], r[1]))
    for cid in EXTRA_IDS:
        r = smiles_by_id(cid)
        if r:
            mols.append((cid, r[0], r[1]))

    rows = []
    for label, cid, smi in mols:
        p = profile(smi, rdkit)
        rows.append({"label": label, "chembl_id": cid, "smiles": smi, **p})

    ok = [r for r in rows if "error" not in r]
    # a transparent triage score: drug-like + synthesizable + clean + has a handle
    def promise(r):
        if "error" in r:
            return -1
        return round(r["QED"]
                     - 0.1 * (r["SAscore"] or 6)
                     - 0.15 * len(r["PAINS_alerts"])
                     - 0.05 * r["BRENK_alert_count"]
                     + (0.1 if r["protac_handles"]["total"] > 0 else -0.2), 3)
    for r in rows:
        r["warhead_promise"] = promise(r)
    rows.sort(key=lambda r: r["warhead_promise"], reverse=True)

    result = {
        "_note": ("Cheminformatic triage of the NR4A3 warhead-screen hits (RDKit; SMILES live from "
                  "ChEMBL). Drug-likeness/synthesizability/alerts/PROTAC-handle profile to prioritise "
                  "which docked chemotypes are worth advancing into a PROTAC. Triage only — docking "
                  "gave the binding prior (confounded), this gives the developability/synthesizability "
                  "prior; neither is affinity or a validated lead."),
        "n_profiled": len(ok),
        "ranking_note": "warhead_promise = QED - 0.1*SAscore - 0.15*PAINS - 0.05*BRENK +/- handle",
        "compounds": rows,
    }
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, file=sys.stderr)
    for r in rows:
        if "error" in r:
            print(f"  {r['label']:<18} {r.get('error')}"); continue
        print(f"  {r['label']:<18} QED={r['QED']:.2f} SA={r['SAscore']} MW={r['MW']:.0f} "
              f"cLogP={r['cLogP']:.1f} PAINS={len(r['PAINS_alerts'])} handles={r['protac_handles']['total']} "
              f"promise={r['warhead_promise']}")


if __name__ == "__main__":
    main()
