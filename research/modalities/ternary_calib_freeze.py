#!/usr/bin/env python3
"""Freeze the Layer-1 SMARCA2–VHL calibration hi/lo pair for the ternary-coop pilot (valB_mini).

WHAT: fetch the bound-PROTAC chemistry for the two crystallographic SMARCA2–VHL degrader complexes chosen in
`ternary-calib-pair-draft.md` — the HIGH-cooperativity anchor (P1, PDB 9HYN, α_TR-FRET=93) and the LOW /
weakly-negative anchor (P5, PDB 9HYP, α=0.6) — from RCSB, RDKit-validate each SMILES, then compute the
maximum-common-substructure mapping between them to decide whether P1↔P5 is a CLEAN CONGENERIC RBFE edge
(shared VHL-ligand + SMARCA2-warhead scaffold, perturbation confined to the linker/exit vector) or whether we
must fall back to a narrower-Δα but more mappable pair (P1→P4, etc. — the documented contingency).

HONESTY CONTRACT (repo golden rule — no fabricated chemistry): every SMILES + coordinate comes from RCSB; the
measured α values come from the already-primary-source-verified prereg (`nr4a3-ternary-coop-prereg.json →
calibration.layer1_vhl_panel.candidate_systems`, Nat Commun 2025 PMC12480974 Suppl. Table 1). If RCSB does not
return a usable degrader ligand for an entry, the script FREEZES NOTHING and reports exactly what is missing —
the pilot stays `pending_calib_pair_freeze`. Nothing here is invented.

Runs on a CI runner (unrestricted internet; the dev-sandbox egress proxy 403s RCSB). Pure `urllib` for the
network fetch (no pip beyond RDKit, which the runner installs). Emits `ternary-calib-pair-frozen.json`.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PREREG = os.path.join(HERE, "nr4a3-ternary-coop-prereg.json")
OUT = os.path.join(HERE, "ternary-calib-pair-frozen.json")

RCSB_ENTRY = "https://data.rcsb.org/rest/v1/core/entry/{pdb}"
RCSB_NONPOLY = "https://data.rcsb.org/rest/v1/core/nonpolymer_entity/{pdb}/{eid}"
RCSB_CHEMCOMP = "https://data.rcsb.org/rest/v1/core/chemcomp/{ccd}"

# The two anchors chosen in ternary-calib-pair-draft.md (widest same-assay Δα, both crystallographic).
HI = {"panel_id": "smarca2_p1", "pdb": "9HYN", "role": "calib_hi"}
LO = {"panel_id": "smarca2_p5", "pdb": "9HYP", "role": "calib_lo"}

# Common non-degrader heteroatoms/ions/cryoprotectants seen in these structures — never the PROTAC.
_IGNORE_CCD = {
    "HOH", "DOD", "GOL", "EDO", "PEG", "PG4", "PGE", "SO4", "PO4", "CL", "NA", "K", "MG", "CA",
    "ZN", "MN", "ACT", "DMS", "IOD", "BR", "FMT", "TRS", "EPE", "MPD", "IMD", "CIT", "NO3", "FLC",
    "1PE", "P6G", "PE4", "BOG", "MES", "NAG", "BMA",
}


def _get_json(url: str) -> dict | None:
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "rare-cancers-ci"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001 — report, never fabricate
        print(f"[freeze] fetch failed {url}: {e}", flush=True)
        return None


def _measured_alpha(panel_id: str) -> dict:
    """Pull the measured α + provenance for a panel id from the verified prereg (no fabrication)."""
    d = json.load(open(PREREG))
    for c in d["calibration"]["layer1_vhl_panel"].get("candidate_systems", []):
        if c.get("id") == panel_id:
            return {"measured_alpha": c.get("measured_alpha"), "measured_alpha_sd": c.get("measured_alpha_sd"),
                    "measured_class": c.get("measured_class_verified") or c.get("measured_class"),
                    "primary_ref": c.get("primary_ref"), "pdb_in_prereg": c.get("pdb")}
    return {}


def _degrader_ligand(pdb: str) -> dict | None:
    """Resolve the bound PROTAC for an entry = the nonpolymer entity with the largest formula weight that is not
    a common ion/buffer/cryoprotectant. Returns {ccd, smiles, smiles_stereo, name, mw, formula} or None."""
    entry = _get_json(RCSB_ENTRY.format(pdb=pdb))
    if not entry:
        return None
    eids = (entry.get("rcsb_entry_container_identifiers", {}) or {}).get("non_polymer_entity_ids") or []
    if not eids:
        print(f"[freeze] {pdb}: no non-polymer entities reported", flush=True)
        return None
    best = None
    for eid in eids:
        npe = _get_json(RCSB_NONPOLY.format(pdb=pdb, eid=eid))
        if not npe:
            continue
        ccd = ((npe.get("pdbx_entity_nonpoly", {}) or {}).get("comp_id")
               or (npe.get("rcsb_nonpolymer_entity_container_identifiers", {}) or {}).get("nonpolymer_comp_id"))
        if not ccd or ccd.upper() in _IGNORE_CCD:
            continue
        cc = _get_json(RCSB_CHEMCOMP.format(ccd=ccd))
        if not cc:
            continue
        desc = cc.get("rcsb_chem_comp_descriptor", {}) or {}
        smiles = desc.get("SMILES_stereo") or desc.get("SMILES")
        mw = (cc.get("chem_comp", {}) or {}).get("formula_weight")
        name = (cc.get("chem_comp", {}) or {}).get("name")
        formula = (cc.get("chem_comp", {}) or {}).get("formula")
        if not smiles or mw is None:
            continue
        cand = {"ccd": ccd, "smiles": smiles, "smiles_stereo": desc.get("SMILES_stereo"),
                "name": name, "mw": float(mw), "formula": formula}
        if best is None or cand["mw"] > best["mw"]:
            best = cand
    return best


def _rdkit_map(smiles_hi: str, smiles_lo: str, timeout: int = 120) -> dict:
    """RDKit sanity + MCS mapping between the two degraders → congenericity verdict for the RBFE edge.
    `timeout` bounds the MCS search per pair (low for a fast wide sweep; the default is fine for a single pair)."""
    from rdkit import Chem
    from rdkit.Chem import rdFMCS

    mh, ml = Chem.MolFromSmiles(smiles_hi), Chem.MolFromSmiles(smiles_lo)
    if mh is None or ml is None:
        return {"ok": False, "reason": "RDKit could not parse one/both SMILES"}
    nh, nl = mh.GetNumHeavyAtoms(), ml.GetNumHeavyAtoms()
    # Ring-matching + element/bond strictness comparable to a LOMAP/Kartograf pre-check.
    res = rdFMCS.FindMCS([mh, ml], timeout=timeout, matchValences=False,
                         ringMatchesRingOnly=True, completeRingsOnly=True,
                         bondCompare=rdFMCS.BondCompare.CompareOrderExact,
                         atomCompare=rdFMCS.AtomCompare.CompareElements)
    mcs_atoms = res.numAtoms
    # perturbed heavy atoms = atoms outside the shared core on each side (max = the softcore burden the edge asks
    # the alchemical transformation to grow/shrink). A clean single-site/linker edge keeps this small.
    pert_hi, pert_lo = nh - mcs_atoms, nl - mcs_atoms
    frac_shared = mcs_atoms / max(nh, nl) if max(nh, nl) else 0.0
    # Heuristic thresholds (documented, conservative): a mappable congeneric edge shares most of the scaffold and
    # perturbs a modest region. These gate the GO/fallback decision; the real LOMAP/Kartograf mapping in the
    # engine is authoritative — this is the pre-freeze curation check.
    mappable = frac_shared >= 0.6 and max(pert_hi, pert_lo) <= 22
    return {"ok": True, "n_heavy_hi": nh, "n_heavy_lo": nl, "mcs_atoms": mcs_atoms,
            "perturbed_heavy_hi": pert_hi, "perturbed_heavy_lo": pert_lo,
            "frac_scaffold_shared": round(frac_shared, 3), "mcs_smarts": res.smartsString,
            "mappable_congeneric": bool(mappable),
            "threshold": "frac_shared>=0.6 AND max_perturbed_heavy<=22 (curation pre-check; engine LOMAP is authoritative)"}


def freeze() -> dict:
    hi_lig = _degrader_ligand(HI["pdb"])
    lo_lig = _degrader_ligand(LO["pdb"])
    result = {
        "_status": "FROZEN" if (hi_lig and lo_lig) else "INCOMPLETE — freeze nothing (missing RCSB ligand)",
        "_provenance": "SMILES + comp_id from RCSB data API; measured α from verified prereg (PMC12480974).",
        "calib_hi": {**HI, "measured": _measured_alpha(HI["panel_id"]), "ligand": hi_lig,
                     "source": RCSB_ENTRY.format(pdb=HI["pdb"])},
        "calib_lo": {**LO, "measured": _measured_alpha(LO["panel_id"]), "ligand": lo_lig,
                     "source": RCSB_ENTRY.format(pdb=LO["pdb"])},
    }
    if hi_lig and lo_lig:
        mapping = _rdkit_map(hi_lig["smiles"], lo_lig["smiles"])
        result["mapping"] = mapping
        ha, la = result["calib_hi"]["measured"].get("measured_alpha"), result["calib_lo"]["measured"].get("measured_alpha")
        result["delta_alpha"] = {"hi": ha, "lo": la,
                                 "log10_ratio": (round(__import__("math").log10(ha / la), 2)
                                                 if (ha and la and la > 0) else None)}
        result["decision"] = ("GO: P1→P5 is a mappable congeneric edge — freeze it (widest Δα)."
                              if mapping.get("mappable_congeneric")
                              else "FALLBACK: P1↔P5 perturbation too large to map cleanly — fall back to the widest "
                                   "CONGENERIC pair spanning a real class difference (P1→P4 etc.); re-run with that pair.")
    return result


def _all_candidates() -> list:
    """Every verified panel member (id, pdb, measured_alpha, class) from the prereg — the search space for the
    widest MAPPABLE hi/lo edge when the preferred P1→P5 is too large a morph."""
    d = json.load(open(PREREG))
    out = []
    for c in d["calibration"]["layer1_vhl_panel"].get("candidate_systems", []):
        if c.get("verified") and c.get("pdb") and c.get("measured_alpha") is not None:
            out.append({"id": c["id"], "pdb": c["pdb"], "alpha": float(c["measured_alpha"]),
                        "alpha_sd": c.get("measured_alpha_sd"),
                        "class": c.get("measured_class_verified") or c.get("measured_class")})
    return out


def sweep_panel(min_log10_delta: float = 0.7) -> dict:
    """Fetch every panel member's degrader, compute the full pairwise MCS/mappability matrix, and RECOMMEND the
    widest-Δα pair that (a) is a mappable congeneric edge and (b) spans a real cooperativity-class difference
    (|log10 α_hi/α_lo| >= min_log10_delta, ~5×). This is the data-driven fallback the calib-pair draft calls for
    when P1↔P5 cannot map. No chemistry fabricated — a member whose ligand RCSB can't return is skipped + noted."""
    import math

    cands = _all_candidates()
    ligs, missing = {}, []
    for c in cands:
        lig = _degrader_ligand(c["pdb"])
        if lig:
            ligs[c["id"]] = {**c, "ligand": lig}
        else:
            missing.append(c["id"])
    pairs = []
    ids = [c["id"] for c in cands if c["id"] in ligs]
    for i in range(len(ids)):
        for j in range(len(ids)):
            if i == j:
                continue
            hi, lo = ligs[ids[i]], ligs[ids[j]]
            if hi["alpha"] < lo["alpha"]:
                continue  # enumerate each unordered pair once, hi = higher α
            m = _rdkit_map(hi["ligand"]["smiles"], lo["ligand"]["smiles"])
            log10d = (round(math.log10(hi["alpha"] / lo["alpha"]), 2)
                      if lo["alpha"] > 0 else None)
            pairs.append({
                "hi": hi["id"], "hi_pdb": hi["pdb"], "hi_alpha": hi["alpha"],
                "lo": lo["id"], "lo_pdb": lo["pdb"], "lo_alpha": lo["alpha"],
                "log10_delta_alpha": log10d,
                "mappable_congeneric": m.get("mappable_congeneric"),
                "mcs_atoms": m.get("mcs_atoms"), "frac_scaffold_shared": m.get("frac_scaffold_shared"),
                "max_perturbed_heavy": max(m.get("perturbed_heavy_hi", 999), m.get("perturbed_heavy_lo", 999)),
            })
    # eligible = mappable AND a real class gap; rank by Δα width (then by smaller perturbation as tiebreak)
    eligible = [p for p in pairs if p["mappable_congeneric"] and p["log10_delta_alpha"]
                and p["log10_delta_alpha"] >= min_log10_delta]
    eligible.sort(key=lambda p: (-(p["log10_delta_alpha"] or 0), p["max_perturbed_heavy"]))
    rec = eligible[0] if eligible else None
    return {"pairs": sorted(pairs, key=lambda p: -(p["log10_delta_alpha"] or 0)),
            "missing_ligands": missing, "min_log10_delta": min_log10_delta,
            "recommended_pair": rec,
            "recommendation": (
                f"FREEZE {rec['hi']} (α={rec['hi_alpha']}, {rec['hi_pdb']}) → {rec['lo']} "
                f"(α={rec['lo_alpha']}, {rec['lo_pdb']}): widest mappable Δα (log10={rec['log10_delta_alpha']}, "
                f"MCS={rec['mcs_atoms']}, max_perturbed={rec['max_perturbed_heavy']})." if rec else
                "NO mappable panel pair spans a real class gap — the series is not congeneric enough for a clean "
                "RBFE calibration edge; escalate (co-fold/ABFE ternary calib, or a different published series).")}


def main() -> int:
    r = freeze()
    # If the preferred P1→P5 is not a clean congeneric edge, sweep the whole panel for the best mappable pair.
    if r.get("mapping") and not r["mapping"].get("mappable_congeneric"):
        print("[freeze] P1→P5 not mappable — sweeping the full panel for the widest MAPPABLE class-gap pair...",
              flush=True)
        r["panel_sweep"] = sweep_panel()
        rec = r["panel_sweep"].get("recommended_pair")
        if rec:
            r["_status"] = "FROZEN (fallback pair from panel sweep)"
            r["decision"] = r["panel_sweep"]["recommendation"]
    with open(OUT, "w") as f:
        json.dump(r, f, indent=2)
    print(json.dumps(r, indent=2), flush=True)
    print(f"[freeze] wrote {OUT}", flush=True)
    # Non-zero exit if we could not resolve both ligands, so CI surfaces the miss loudly.
    return 0 if (r["calib_hi"]["ligand"] and r["calib_lo"]["ligand"]) else 2


if __name__ == "__main__":
    sys.exit(main())
