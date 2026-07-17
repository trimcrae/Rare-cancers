#!/usr/bin/env python3
"""Search RCSB for a genuinely CONGENERIC VHL-PROTAC pair with measured cooperativity — the valB_mini calib edge.

WHY: the curated SMARCA2/BRD4-VHL cooperativity panel (nr4a3-ternary-coop-prereg.json) is NOT congeneric — every
hi/lo pair perturbs 32-47 heavy atoms (ternary_calib_freeze.py panel_sweep), so no clean relative-FEP
calibration edge exists in it. Per trimcrae (2026-07-17), before any GPU spend, cast a wider net: enumerate ALL
VHL ternary-PROTAC crystal structures in the PDB, MCS-cluster their bound degraders, and surface the pairs that
ARE congeneric (shared scaffold, a SMALL linker/exit-vector perturbation LOMAP can map) — then cross-reference
which have published cooperativity so a graded alpha-ranking calibration edge can be frozen.

WHAT it does (free CPU on a CI runner; the dev-sandbox egress proxy 403s RCSB):
  1. RCSB Search API → every PDB entry whose polymer references VHL (UniProt P40337).
  2. For each, resolve the bound PROTAC (largest non-ion/buffer nonpolymer; reuses ternary_calib_freeze).
  3. RDKit MCS over ALL pairs → flag CONGENERIC pairs (tight: frac_scaffold_shared>=0.75 AND
     max_perturbed_heavy<=12 — a real RBFE edge, far tighter than the panel_sweep GO check).
  4. Cross-reference measured cooperativity: annotate any pair whose BOTH PDBs already carry a verified alpha in
     the prereg; the rest are flagged `needs_alpha_litfetch` (structure is congeneric, cooperativity TBV).

HONESTY: pure RCSB + RDKit; no chemistry or alpha fabricated. A congeneric structural pair without a verified
alpha is reported as a CANDIDATE needing a primary-source cooperativity fetch, never as a frozen calib edge.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

import ternary_calib_freeze as tcf

HERE = os.path.dirname(os.path.abspath(__file__))
PREREG = os.path.join(HERE, "nr4a3-ternary-coop-prereg.json")
OUT = os.path.join(HERE, "ternary-calib-congeneric-search.json")

RCSB_SEARCH = "https://search.rcsb.org/rcsbsearch/v2/query"
VHL_UNIPROT = "P40337"

# tight congeneric gate for a CLEAN relative-FEP edge (much tighter than the panel_sweep GO check)
FRAC_MIN = 0.75
PERTURB_MAX = 12
MAX_ENTRIES = int(os.environ.get("CALIB_SEARCH_MAX_ENTRIES", "150"))


def _rcsb_vhl_entries() -> list:
    """Every PDB entry ID whose polymer references VHL (UniProt P40337)."""
    query = {
        "query": {
            "type": "group", "logical_operator": "and", "nodes": [
                {"type": "terminal", "service": "text", "parameters": {
                    "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
                    "operator": "exact_match", "value": VHL_UNIPROT}},
                {"type": "terminal", "service": "text", "parameters": {
                    "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_name",
                    "operator": "exact_match", "value": "UniProt"}},
            ],
        },
        "return_type": "entry",
        "request_options": {"paginate": {"start": 0, "rows": MAX_ENTRIES}, "results_verbosity": "minimal"},
    }
    req = urllib.request.Request(RCSB_SEARCH, data=json.dumps(query).encode(),
                                headers={"Content-Type": "application/json", "User-Agent": "rare-cancers-ci"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001
        print(f"[search] RCSB search failed: {e}", flush=True)
        return []
    total = d.get("total_count")
    ids = [m["identifier"] for m in d.get("result_set", [])]
    if total and total > len(ids):
        print(f"[search] NOTE: RCSB reports {total} VHL entries; fetched {len(ids)} (cap {MAX_ENTRIES}). "
              f"Raise CALIB_SEARCH_MAX_ENTRIES to widen.", flush=True)
    return ids


def _prereg_alpha_by_pdb() -> dict:
    d = json.load(open(PREREG))
    out = {}
    for c in d["calibration"]["layer1_vhl_panel"].get("candidate_systems", []):
        if c.get("pdb") and c.get("measured_alpha") is not None:
            out[c["pdb"].upper()] = {"id": c["id"], "alpha": c["measured_alpha"],
                                     "verified": bool(c.get("verified"))}
    return out


def search() -> dict:
    import math

    entries = _rcsb_vhl_entries()
    print(f"[search] {len(entries)} VHL entries to resolve degraders for", flush=True)
    ligs, no_lig = {}, []
    for pdb in entries:
        lig = tcf._degrader_ligand(pdb)
        # keep only genuine PROTAC-scale ligands (>=600 Da) — filters VHL peptides / apo / fragment entries
        if lig and lig.get("mw", 0) >= 600:
            ligs[pdb.upper()] = lig
        else:
            no_lig.append(pdb)
    print(f"[search] {len(ligs)} entries carry a PROTAC-scale degrader", flush=True)

    alpha = _prereg_alpha_by_pdb()
    pdbs = sorted(ligs)

    # Precompute heavy-atom counts once so we can CHEAPLY prune pairs before the (expensive) MCS: since
    # max_perturbed_heavy >= |n_heavy_a - n_heavy_b|, any pair whose atom counts differ by more than PERTURB_MAX
    # cannot pass the congeneric gate — skip its MCS entirely. (This is what blew the 20-min budget: 2080 pairs ×
    # a 120 s MCS timeout. The prune leaves only plausibly-congeneric pairs, and we cap each MCS at 8 s.)
    from rdkit import Chem, DataStructs
    from rdkit.Chem import rdFingerprintGenerator
    _mfp = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    nheavy, fp = {}, {}
    for p in pdbs:
        mm = Chem.MolFromSmiles(ligs[p]["smiles"])
        if mm is not None:
            nheavy[p] = mm.GetNumHeavyAtoms()
            fp[p] = _mfp.GetFingerprint(mm)
    n_pruned = 0
    congeneric = []
    for i in range(len(pdbs)):
        for j in range(i + 1, len(pdbs)):
            pa, pb = pdbs[i], pdbs[j]
            # cheap prunes before the expensive MCS: (a) atom counts too far apart to be a <=PERTURB_MAX edge;
            # (b) low Morgan-Tanimoto → not congeneric (a real single-site/linker edge stays highly similar).
            if pa in nheavy and pb in nheavy and abs(nheavy[pa] - nheavy[pb]) > PERTURB_MAX:
                n_pruned += 1
                continue
            if pa in fp and pb in fp and DataStructs.TanimotoSimilarity(fp[pa], fp[pb]) < 0.5:
                n_pruned += 1
                continue
            m = tcf._rdkit_map(ligs[pa]["smiles"], ligs[pb]["smiles"], timeout=8)
            if not m.get("ok"):
                continue
            frac = m.get("frac_scaffold_shared", 0)
            pert = max(m.get("perturbed_heavy_hi", 999), m.get("perturbed_heavy_lo", 999))
            if frac >= FRAC_MIN and pert <= PERTURB_MAX:
                aa, ab = alpha.get(pa), alpha.get(pb)
                both_alpha = bool(aa and ab)
                log10d = (round(abs(math.log10(aa["alpha"] / ab["alpha"])), 2)
                          if (both_alpha and aa["alpha"] > 0 and ab["alpha"] > 0) else None)
                congeneric.append({
                    "pdb_a": pa, "ccd_a": ligs[pa]["ccd"], "pdb_b": pb, "ccd_b": ligs[pb]["ccd"],
                    "mcs_atoms": m["mcs_atoms"], "frac_scaffold_shared": frac, "max_perturbed_heavy": pert,
                    "alpha_a": aa, "alpha_b": ab,
                    "both_have_measured_alpha": both_alpha, "log10_delta_alpha": log10d,
                    "status": ("CANDIDATE_CALIB_EDGE (congeneric + both alphas)" if both_alpha
                               else "congeneric_structural_pair (needs_alpha_litfetch)"),
                })
    congeneric.sort(key=lambda p: (not p["both_have_measured_alpha"],
                                   -(p["log10_delta_alpha"] or 0), p["max_perturbed_heavy"]))
    ready = [p for p in congeneric if p["both_have_measured_alpha"] and (p["log10_delta_alpha"] or 0) >= 0.7]
    return {
        "_provenance": "RCSB Search API (VHL UniProt P40337) + RCSB chemcomp SMILES + RDKit MCS. No alpha fabricated.",
        "gate": {"frac_scaffold_shared_min": FRAC_MIN, "max_perturbed_heavy": PERTURB_MAX,
                 "note": "tight CLEAN-RBFE-edge gate; far tighter than the panel_sweep GO check"},
        "n_vhl_entries": len(entries), "n_with_degrader": len(ligs),
        "n_pairs_pruned_by_atomcount": n_pruned,
        "congeneric_pairs": congeneric,
        "ready_calib_edges": ready,
        "recommendation": (
            f"FREEZE the congeneric pair {ready[0]['pdb_a']}({ready[0]['ccd_a']})→{ready[0]['pdb_b']}"
            f"({ready[0]['ccd_b']}): congeneric (frac={ready[0]['frac_scaffold_shared']}, "
            f"perturbed<={ready[0]['max_perturbed_heavy']}) AND both carry measured alpha spanning a class gap "
            f"(log10Δα={ready[0]['log10_delta_alpha']})." if ready else
            "NO ready congeneric+alpha edge in the PDB VHL set. Congeneric STRUCTURAL pairs (if any below) need a "
            "primary-source cooperativity fetch; if none, the noncovalent VHL ternary known-answer must come from "
            "an active→epimer control or an absolute-cooperativity calc (escalate)."),
    }


def main() -> int:
    r = search()
    with open(OUT, "w") as f:
        json.dump(r, f, indent=2)
    print(json.dumps(r, indent=2), flush=True)
    print(f"[search] wrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
