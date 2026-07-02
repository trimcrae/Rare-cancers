#!/usr/bin/env python3
"""
In-silico developability / ADMET-lite profile of the lead NR4A3 binder (ledger F1-F5).

WHY. The paper had potency (MM-GBSA, FEP-queued) and selectivity work, but NO developability read —
the first thing a medicinal chemist or reviewer asks: is the molecule drug-like, is it flagged by
structural-alert filters, is it synthesizable? These are free (RDKit, CPU-seconds) and were simply
absent. This computes them honestly for the lead.

SCOPE HONESTY. denovo_401 is the *binder / warhead* (a small neutral molecule), NOT yet an assembled
PROTAC (no CRBN ligand + linker attached — that is ledger E4, the exit-vector step). So we report:
  (1) the exact profile of the binder as-is, and
  (2) a PROJECTED full-PROTAC physchem envelope (binder + a canonical CRBN ligand + a short linker),
      clearly flagged as an estimate, to show where the eventual degrader lands in beyond-Ro5 space.
Nothing is fabricated; the projection is labelled a projection.

No internet needed (pure RDKit) -> runs locally or in CI. Output: nr4a3-developability.json.
"""

import json
import os
import sys

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "nr4a-developability.json")

# The lead binder (from fep_species.LEADS; the generated stereochemistry). denovo_111 withdrawn.
LEAD = {"name": "denovo_401", "smiles": "COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1"}
# Canonical CRBN ligand for the projection (pomalidomide) + a modest PEG2-type linker fragment.
CRBN_LIGAND = {"name": "pomalidomide", "smiles": "O=C1CCC(N2C(=O)c3cccc(N)c3C2=O)C1=O"}
LINKER_ESTIMATE = {"name": "PEG2-ish linker", "approx_mw": 130.0, "approx_clogp": -0.6,
                   "approx_hbd": 1, "approx_hba": 4, "approx_rotbonds": 6}


def _props(smiles):
    from rdkit import Chem
    from rdkit.Chem import Crippen, Descriptors, Lipinski, QED, rdMolDescriptors
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return {"_status": "unparseable SMILES", "smiles": smiles}
    p = {
        "smiles": Chem.MolToSmiles(m),
        "mw": round(Descriptors.MolWt(m), 1),
        "heavy_atoms": m.GetNumHeavyAtoms(),
        "clogp": round(Crippen.MolLogP(m), 2),
        "tpsa": round(rdMolDescriptors.CalcTPSA(m), 1),
        "hbd": Lipinski.NumHDonors(m),
        "hba": Lipinski.NumHAcceptors(m),
        "rot_bonds": Lipinski.NumRotatableBonds(m),
        "aromatic_rings": rdMolDescriptors.CalcNumAromaticRings(m),
        "fsp3": round(rdMolDescriptors.CalcFractionCSP3(m), 2),
        "qed": round(QED.qed(m), 3),
        "n_stereocenters": len(Chem.FindMolChiralCenters(m, useLegacyImplementation=False,
                                                         includeUnassigned=True)),
    }
    # Rule-of-5 / Veber for a small molecule (NOTE: PROTACs are expected to violate Ro5 — that is normal).
    p["lipinski_violations"] = sum([p["mw"] > 500, p["clogp"] > 5, p["hbd"] > 5, p["hba"] > 10])
    p["veber_pass"] = bool(p["rot_bonds"] <= 10 and p["tpsa"] <= 140)
    return p


def _sa_score(smiles):
    """Synthetic accessibility (Ertl-Schuffenhauer SA score, 1=easy..10=hard). Optional contrib module."""
    try:
        from rdkit import Chem
        from rdkit.Chem import RDConfig
        sys.path.append(os.path.join(RDConfig.RDContribDir, "SA_Score"))
        import sascorer  # noqa: E402
        m = Chem.MolFromSmiles(smiles)
        return round(sascorer.calculateScore(m), 2) if m else None
    except Exception as e:  # noqa: BLE001
        print(f"  SA score unavailable: {e}", file=sys.stderr)
        return None


def _structural_alerts(smiles):
    """PAINS + BRENK structural-alert hits via RDKit FilterCatalog."""
    try:
        from rdkit import Chem
        from rdkit.Chem import FilterCatalog
        from rdkit.Chem.FilterCatalog import FilterCatalogParams
        m = Chem.MolFromSmiles(smiles)
        hits = {}
        for name, cat in [("PAINS", FilterCatalogParams.FilterCatalogs.PAINS),
                          ("BRENK", FilterCatalogParams.FilterCatalogs.BRENK)]:
            params = FilterCatalogParams()
            params.AddCatalog(cat)
            fc = FilterCatalog.FilterCatalog(params)
            matches = fc.GetMatches(m)
            hits[name] = [h.GetDescription() for h in matches]
        return hits
    except Exception as e:  # noqa: BLE001
        print(f"  structural-alert scan unavailable: {e}", file=sys.stderr)
        return {"_status": f"unavailable: {e}"}


def _projected_protac(binder, crbn):
    """Rough full-PROTAC physchem envelope: additive over binder + CRBN ligand + linker (minus ~2 H2O
    for the two amide/ester couplings). Clearly a PROJECTION, not a built molecule."""
    if "_status" in binder or "_status" in crbn:
        return {"_status": "cannot project (component unparsed)"}
    lk = LINKER_ESTIMATE
    return {
        "_status": "PROJECTION — additive estimate over binder + pomalidomide + a short linker, "
                   "NOT an assembled/optimized PROTAC. Real values require the exit-vector build (E4).",
        "proj_mw": round(binder["mw"] + crbn["mw"] + lk["approx_mw"] - 36.0, 0),
        "proj_clogp": round(binder["clogp"] + crbn["clogp"] + lk["approx_clogp"], 1),
        "proj_hbd": binder["hbd"] + crbn["hbd"] + lk["approx_hbd"],
        "proj_hba": binder["hba"] + crbn["hba"] + lk["approx_hba"],
        "proj_rot_bonds": binder["rot_bonds"] + crbn["rot_bonds"] + lk["approx_rotbonds"],
        "beyond_ro5_note": "Expected to sit in beyond-Rule-of-5 space (MW ~600-750, high rot-bond) — "
                           "NORMAL and expected for a PROTAC; the point is to quantify where it lands, "
                           "not to force Ro5 compliance.",
    }


def main():
    binder = _props(LEAD["smiles"])
    binder["sa_score"] = _sa_score(LEAD["smiles"])
    binder["structural_alerts"] = _structural_alerts(LEAD["smiles"])
    crbn = _props(CRBN_LIGAND["smiles"])

    result = {
        "_title": "In-silico developability / ADMET-lite — lead NR4A3 binder (ledger F1-F5)",
        "_source": "RDKit (descriptors, QED, FilterCatalog PAINS/BRENK, Ertl-Schuffenhauer SA score)",
        "_scope": "denovo_401 is the BINDER/warhead, not an assembled PROTAC. Binder profile is exact; "
                  "the full-PROTAC line is an explicit projection pending linker assembly (E4).",
        "lead_binder": {"name": LEAD["name"], **binder},
        "crbn_ligand_ref": {"name": CRBN_LIGAND["name"], **crbn},
        "projected_full_protac": _projected_protac(binder, crbn),
        "interpretation": {
            "binder_druglikeness": (
                f"QED {binder.get('qed')}, {binder.get('lipinski_violations')} Ro5 violation(s), "
                f"Veber {'pass' if binder.get('veber_pass') else 'fail'}, SA {binder.get('sa_score')} "
                f"(1=easy..10=hard)."),
            "alerts": ("PAINS/BRENK hits listed under lead_binder.structural_alerts — empty lists = "
                       "clean on those catalogs."),
        },
    }
    json.dump(result, open(OUT, "w"), indent=2)
    print("wrote", OUT, file=sys.stderr)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
