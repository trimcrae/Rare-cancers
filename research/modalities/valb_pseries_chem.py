#!/usr/bin/env python3
"""The $0 blocker on the valB rescope: is the Ciulli P-series actually a mappable congeneric series?

Every edge in `valb-rescope-design.json` is a CANDIDATE until this returns, because an edge LOMAP/Kartograf
cannot map does not converge at any price, and a charge-changing edge needs a different and much more expensive
treatment. The prereg records `ligand_ccd: null` for all five systems, so the chemistry has never been fetched.

What this does, in order, and what it refuses to do:
  1. Fetch each PDB entry from RCSB and read its title + polymer entity names — this CONFIRMS the entries are
     SMARCA2 (not SMARCA4) VHL ternaries rather than assuming it. The current valB edge's whole homology-model
     limitation exists because 8G1Q is SMARCA4, so this is not a formality.
  2. Fetch the nonpolymer (ligand) components and keep the PROTAC-sized one — >=40 heavy atoms excludes buffer,
     ions and cryoprotectants. If an entry has zero or several such ligands, it is REPORTED, not guessed at.
  3. Pull each ligand's canonical SMILES from the RCSB chemical-component endpoint.
  4. With RDKit (present in triskit23/ternary-fep, along with lomap2 and kartograf — the same mapper the
     production edge would use, at version parity): pairwise MCS, perturbed heavy-atom count, and FORMAL CHARGE
     CHANGE for every candidate edge.

NOTHING is fabricated. A ligand whose SMILES cannot be fetched is reported as unfetched; congenericity is a
computed MCS result or it is absent. Alpha values are NOT touched here — they live in the prereg, already
primary-source verified, and this module never re-derives them.

Pure stdlib for the fetch (RDKit optional, and its absence degrades to "structures fetched, mapping not run").
The dev sandbox's egress proxy 403s RCSB at CONNECT, so this runs on a CI runner.
"""
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TIMEOUT = 45
MIN_PROTAC_HEAVY = 40          # a PROTAC is ~55-75 heavy atoms; buffers/ions/cryoprotectants are far smaller


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Rare-cancers/valb-rescope (research)"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.load(r)


def entry_dossier(pdb_id):
    """Title, polymer entity names, and the PROTAC-sized ligand for one PDB entry."""
    rec = {"pdb_id": pdb_id}
    try:
        e = _get("https://data.rcsb.org/rest/v1/core/entry/%s" % pdb_id)
    except Exception as ex:  # noqa: BLE001
        rec["error"] = "entry fetch failed: %s: %s" % (type(ex).__name__, ex)
        return rec
    rec["title"] = (e.get("struct") or {}).get("title")
    rec["resolution_A"] = ((e.get("rcsb_entry_info") or {}).get("resolution_combined") or [None])[0]
    rec["comp_ids"] = list((e.get("rcsb_entry_container_identifiers") or {}).get("non_polymer_entity_ids") or [])
    # Polymer names decide the SMARCA2-vs-SMARCA4 question, so read them rather than trusting the panel label.
    names = []
    for pid in ((e.get("rcsb_entry_container_identifiers") or {}).get("polymer_entity_ids") or []):
        try:
            pe = _get("https://data.rcsb.org/rest/v1/core/polymer_entity/%s/%s" % (pdb_id, pid))
            nm = (pe.get("rcsb_polymer_entity") or {}).get("pdbx_description")
            if nm:
                names.append(nm)
        except Exception:  # noqa: BLE001
            pass
    rec["polymer_entities"] = names
    joined = " ".join(names).lower()
    rec["mentions_smarca2"] = "smarca2" in joined or "brm" in joined
    rec["mentions_smarca4"] = "smarca4" in joined or "brg1" in joined
    rec["mentions_vhl"] = "hippel" in joined or "vhl" in joined
    # nonpolymer components -> the PROTAC
    cands = []
    for nid in rec["comp_ids"]:
        try:
            ne = _get("https://data.rcsb.org/rest/v1/core/nonpolymer_entity/%s/%s" % (pdb_id, nid))
            ccds = ((ne.get("pdbx_entity_nonpoly") or {}).get("comp_id"))
            if not ccds:
                continue
            ch = _get("https://data.rcsb.org/rest/v1/core/chemcomp/%s" % ccds)
            info = ch.get("chem_comp") or {}
            desc = ch.get("rcsb_chem_comp_descriptor") or {}
            smi = desc.get("smiles") or desc.get("smilesstereo")
            if smi is None:
                for d in (ch.get("pdbx_chem_comp_descriptor") or []):
                    if str(d.get("type", "")).upper() == "SMILES_CANONICAL":
                        smi = d.get("descriptor")
                        break
            heavy = info.get("pdbx_formal_charge") is not None and None
            nheavy = (ch.get("rcsb_chem_comp_info") or {}).get("atom_count_heavy")
            cands.append({"ccd": ccds, "name": info.get("name"), "formula": info.get("formula"),
                          "n_heavy": nheavy, "formal_charge": info.get("pdbx_formal_charge"),
                          "smiles": smi})
            del heavy
        except Exception as ex:  # noqa: BLE001
            cands.append({"nonpolymer_entity_id": nid, "error": "%s: %s" % (type(ex).__name__, ex)})
    rec["nonpolymer_components"] = cands
    big = [c for c in cands if (c.get("n_heavy") or 0) >= MIN_PROTAC_HEAVY]
    if len(big) == 1:
        rec["protac"] = big[0]
        rec["protac_status"] = "ok"
    else:
        rec["protac"] = None
        rec["protac_status"] = ("%d components have >=%d heavy atoms — the PROTAC is not uniquely identified, "
                                "so none is chosen" % (len(big), MIN_PROTAC_HEAVY))
    return rec


def pairwise_mapping(dossiers):
    """RDKit MCS between every pair of identified PROTACs: perturbed heavy atoms and formal-charge change."""
    try:
        from rdkit import Chem, RDLogger
        from rdkit.Chem import rdFMCS
        RDLogger.DisableLog("rdApp.*")
    except Exception as e:  # noqa: BLE001
        return {"status": "rdkit unavailable (%s) — structures fetched, mapping NOT run" % e}
    mols = {}
    for k, d in dossiers.items():
        smi = ((d.get("protac") or {}).get("smiles"))
        if not smi:
            continue
        m = Chem.MolFromSmiles(smi)
        if m is not None:
            mols[k] = m
    out = {"n_molecules_parsed": len(mols), "pairs": []}
    ks = sorted(mols)
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            ma, mb = mols[a], mols[b]
            res = rdFMCS.FindMCS([ma, mb], timeout=60, ringMatchesRingOnly=True, completeRingsOnly=True)
            nm = res.numAtoms if res and not res.canceled else 0
            ha, hb = ma.GetNumHeavyAtoms(), mb.GetNumHeavyAtoms()
            perturbed = ha + hb - 2 * nm
            qa = Chem.GetFormalCharge(ma)
            qb = Chem.GetFormalCharge(mb)
            out["pairs"].append({
                "edge": "%s -> %s" % (a, b),
                "heavy_a": ha, "heavy_b": hb, "mcs_atoms": nm,
                "perturbed_heavy_atoms": perturbed,
                "formal_charge_a": qa, "formal_charge_b": qb, "charge_change": qb - qa,
                "mcs_smarts": (res.smartsString if res else None),
                "verdict": ("CHARGE-CHANGING — needs a different and much more expensive treatment; not a "
                            "candidate for this calibrator" if qa != qb else
                            "mappable congeneric edge (%d perturbed heavy atoms)" % perturbed if perturbed <= 20
                            else "LARGE perturbation (%d heavy atoms) — expect poor overlap; prefer an "
                                 "intermediate hop" % perturbed),
            })
    out["pairs"].sort(key=lambda p: p["perturbed_heavy_atoms"])
    return out


def main():
    panel = json.load(open(os.path.join(HERE, "nr4a3-ternary-coop-prereg.json")))
    systems = [s for s in panel["calibration"]["layer1_vhl_panel"].get("candidate_systems", [])
               if s.get("pdb") and s.get("id", "").startswith("smarca2_p")]
    dossiers = {}
    for s in systems:
        print("[chem] fetching %s (%s)" % (s["id"], s["pdb"]), flush=True)
        dossiers[s["id"]] = entry_dossier(s["pdb"])
        dossiers[s["id"]]["prereg_alpha"] = s.get("measured_alpha")
    report = {
        "_what": "P-series ligand chemistry + pairwise mappability — the $0 blocker on the valB calibrator "
                 "rescope (valb-calibrator-rescope-2026-07-25.md section 5)",
        "_provenance": "RCSB REST (entry / polymer_entity / nonpolymer_entity / chemcomp). No SMILES, alpha or "
                       "identity is invented; an unfetched ligand is reported as unfetched.",
        "_alpha_note": "alpha values are carried through from the prereg, where they are primary-source "
                       "verified. This module never re-derives one.",
        "entries": dossiers,
        "identity_check": {k: {"smarca2": v.get("mentions_smarca2"), "smarca4": v.get("mentions_smarca4"),
                               "vhl": v.get("mentions_vhl"), "title": v.get("title"),
                               "resolution_A": v.get("resolution_A")}
                           for k, v in dossiers.items()},
        "mapping": pairwise_mapping(dossiers),
    }
    out = os.path.join(HERE, "valb-pseries-chem.json")
    json.dump(report, open(out, "w"), indent=2)
    print(json.dumps(report["identity_check"], indent=2))
    print(json.dumps(report["mapping"], indent=2)[:4000])
    print("[chem] wrote %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
