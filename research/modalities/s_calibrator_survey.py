#!/usr/bin/env python3
"""Which paralogue pairs could carry an S-CALIBRATOR — screened on whether a REAL structure exists on BOTH arms.

★ WHY THIS EXISTS. STRATEGY Open decision 9 (2026-07-30) concluded that `S` — the flagship kill-switch — has
never had a known-answer calibrator, and that the binding constraint on choosing one is **which arm is REAL**,
not what is already staged. The reason is specific: valB_mini's miss is an ENDPOINT-STATE error, and a
known-answer accuracy test does NOT telescope such an error the way a cycle does. On SMARCA2-vs-SMARCA4 as the
repo currently stages it, 8G1Q is a *SMARCA4* structure with the BD sequence substituted to SMARCA2 and
relaxed — so a homology-model error would sit on ONE arm and not cancel, and a failure could not be told apart
from "the S-class quantity does not work." A pair with a solved structure on both arms removes that ambiguity
outright.

★ WHAT THIS SCREENS, AND WHAT IT DELIBERATELY DOES NOT. It answers the STRUCTURAL half, entirely from fetched
RCSB data: for each candidate paralogue pair, does a deposited structure exist for each arm, and is any of them
a TERNARY complex (target + an E3 component)? That is the half that is decidable without a literature claim.

⛔ IT DOES NOT SUPPLY SELECTIVITY MAGNITUDES, AND MUST NOT BE READ AS DOING SO. A calibrator needs a measured,
primary-source selectivity value, and STRATEGY Open decision 7 now binds it: the accuracy band may not be wider
than the signal being calibrated, and the null-rejection rate must be stated up front. No such number is typed
here from memory — every candidate is emitted with `selectivity_kcal: null` and
`needs_primary_source_verification: true`, and the repo's medical-integrity rule means it stays that way until
a primary source is read and cited. A pair that passes the structural screen is a CANDIDATE, not a choice.

★ NO PDB ID IS TYPED. Every accession in the output is returned by the RCSB search API against a GENE NAME, so
the survey cannot invent a structure that does not exist. The candidate list carries only gene-name pairs —
statements about which proteins are paralogues, which is not a claim this file needs to source from the network.

Pure stdlib. Network: RCSB only (search.rcsb.org + data.rcsb.org). The dev sandbox's egress proxy refuses
both, so this runs in CI (CLAUDE.md §6).
"""
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "s-calibrator-survey.json")

SEARCH = "https://search.rcsb.org/rcsbsearch/v2/query"
DATA = "https://data.rcsb.org/rest/v1/core/entry/"

# E3/CRL components whose presence in an entry makes it a TERNARY (or at least E3-bound) structure rather than
# a bare target complex. Gene names, matched against the entry's own polymer-entity gene names.
E3_MARKERS = {"VHL", "CRBN", "DDB1", "ELOB", "ELOC", "TCEB1", "TCEB2", "CUL2", "CUL4A", "RBX1",
              "BIRC2", "DCAF1", "DCAF15", "DCAF16", "KEAP1", "FEM1B", "RNF114", "MDM2"}

# ---------------------------------------------------------------------------------------------------------
# CANDIDATES -- paralogue pairs for which a selective degrader or ligand is reported in the literature.
# Gene names only. The claim being made here is ONLY that these are paralogues and that selectivity has been
# reported for the pair; the magnitude is left to primary-source verification, and the structures are fetched.
# ---------------------------------------------------------------------------------------------------------
CANDIDATES = [
    {"pair": ("SMARCA2", "SMARCA4"), "why": "the repo's incumbent; VHL PROTACs with reported SMARCA2 preference"},
    {"pair": ("BRD4", "BRD2"), "why": "BET family; VHL PROTACs with reported intra-family preference"},
    {"pair": ("BRD4", "BRD3"), "why": "BET family, second pairing"},
    {"pair": ("CDK4", "CDK6"), "why": "close kinase paralogues with reported selective degraders"},
    {"pair": ("IKZF1", "IKZF3"), "why": "CRBN molecular-glue neosubstrates with reported differential degradation"},
    {"pair": ("MAPK14", "MAPK11"), "why": "p38 alpha vs beta; selective degraders reported"},
    {"pair": ("FKBP12", "FKBP51"), "why": "FKBP family; selective ligands reported"},
    {"pair": ("WEE1", "PKMYT1"), "why": "related kinases with selective chemistry reported"},
    {"pair": ("CDK9", "CDK7"), "why": "transcriptional CDKs with reported selective degraders"},
    {"pair": ("HDAC1", "HDAC2"), "why": "class-I HDAC paralogues, reported selective chemistry"},
]


def _post(url, payload, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return json.load(fh)


def _get(url, timeout=60):
    with urllib.request.urlopen(url, timeout=timeout) as fh:
        return json.load(fh)


def search_by_gene(gene, limit=50):
    """PDB entry IDs whose polymer entities carry this gene name. IDs come from RCSB, never from memory."""
    q = {
        "query": {"type": "terminal", "service": "text",
                  "parameters": {"attribute": "rcsb_polymer_entity.rcsb_gene_name.value",
                                 "operator": "exact_match", "value": gene}},
        "return_type": "entry",
        "request_options": {"paginate": {"start": 0, "rows": limit},
                            "results_content_type": ["experimental"]},
    }
    try:
        r = _post(SEARCH, q)
    except urllib.error.HTTPError as e:
        if e.code == 204:                      # RCSB returns 204 for "no hits"
            return []
        raise
    return [h["identifier"] for h in r.get("result_set", [])]


def entry_genes_and_resolution(pdb_id):
    """Gene names present in an entry, plus its resolution. Used to decide whether an entry is TERNARY."""
    try:
        e = _get(DATA + pdb_id)
    except Exception:
        return set(), None
    res = None
    r = (e.get("rcsb_entry_info") or {}).get("resolution_combined")
    if isinstance(r, list) and r:
        res = r[0]
    genes = set()
    for eid in (e.get("rcsb_entry_container_identifiers") or {}).get("polymer_entity_ids", []):
        try:
            pe = _get("https://data.rcsb.org/rest/v1/core/polymer_entity/%s/%s" % (pdb_id, eid))
        except Exception:
            continue
        for g in (pe.get("rcsb_gene_name") or []):
            if g.get("value"):
                genes.add(g["value"].upper())
    return genes, res


def screen_arm(gene, max_entries=25):
    """One paralogue arm: how many deposited structures, and how many are E3-bound (ternary)."""
    ids = search_by_gene(gene)
    ternary, best_res, ternary_ids = 0, None, []
    for pid in ids[:max_entries]:
        genes, res = entry_genes_and_resolution(pid)
        if genes & E3_MARKERS:
            ternary += 1
            ternary_ids.append({"pdb_id": pid, "resolution_A": res,
                                "e3_components": sorted(genes & E3_MARKERS)})
            if res is not None and (best_res is None or res < best_res):
                best_res = res
    return {"gene": gene, "n_structures": len(ids), "n_inspected": min(len(ids), max_entries),
            "n_ternary": ternary, "best_ternary_resolution_A": best_res,
            "ternary_entries": ternary_ids[:8],
            "_n_structures_is_a_floor_if_truncated": len(ids) >= 50}


def survey(candidates=None):
    rows = []
    for c in (candidates or CANDIDATES):
        a, b = c["pair"]
        arm_a, arm_b = screen_arm(a), screen_arm(b)
        both_real = arm_a["n_ternary"] > 0 and arm_b["n_ternary"] > 0
        rows.append({
            "pair": [a, b],
            "why_a_candidate": c["why"],
            "arm_a": arm_a,
            "arm_b": arm_b,
            "ternary_structure_on_BOTH_arms": both_real,
            "verdict": ("SYMMETRIC — a solved ternary exists on both arms, so neither arm needs a homology "
                        "substitution and a model error cannot sit on one side only"
                        if both_real else
                        "ASYMMETRIC or ABSENT — at least one arm has no deposited ternary, so that arm would "
                        "have to be modelled and a model error would NOT cancel"),
            "selectivity_kcal": None,
            "needs_primary_source_verification": True,
            "_selectivity_note": ("NOT SUPPLIED BY THIS SURVEY. A calibrator needs a measured, primary-source "
                                 "selectivity value, and STRATEGY Open decision 7 binds it: the accuracy band "
                                 "may not be wider than the signal, and the null-rejection rate must be stated "
                                 "up front. Passing the structural screen makes a pair a CANDIDATE, not a "
                                 "choice."),
        })
    rows.sort(key=lambda r: (not r["ternary_structure_on_BOTH_arms"],
                             -(r["arm_a"]["n_ternary"] + r["arm_b"]["n_ternary"])))
    return {
        "_what": ("structural screen for an S-calibrator: which paralogue pairs have a deposited TERNARY "
                  "structure on BOTH arms, so that a homology-model error cannot sit on one arm only"),
        "_why": ("STRATEGY Open decision 9 — the system must be chosen on WHICH ARM IS REAL, not on what is "
                 "already staged, because a known-answer accuracy test does not telescope an endpoint-state "
                 "error the way a cycle does"),
        "_no_pdb_id_is_typed": "every accession is returned by the RCSB search API against a gene name",
        "_does_not_supply_selectivity": True,
        "_binding_constraint_from_decision_7": ("no accuracy band wider than the signal being calibrated; "
                                                "state the null-rejection rate up front"),
        "e3_markers_used": sorted(E3_MARKERS),
        "candidates": rows,
        "n_symmetric": sum(1 for r in rows if r["ternary_structure_on_BOTH_arms"]),
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    rep = survey()
    if "--write" in argv:
        with open(OUT, "w") as fh:
            json.dump(rep, fh, indent=1)
            fh.write("\n")
        print("wrote %s" % OUT)
    print("[S-CALIBRATOR SURVEY] %d of %d candidate pairs have a ternary structure on BOTH arms"
          % (rep["n_symmetric"], len(rep["candidates"])))
    for r in rep["candidates"]:
        print("  %-18s both_arms=%-5s  A: %d struct/%d ternary   B: %d struct/%d ternary"
              % ("/".join(r["pair"]), r["ternary_structure_on_BOTH_arms"],
                 r["arm_a"]["n_structures"], r["arm_a"]["n_ternary"],
                 r["arm_b"]["n_structures"], r["arm_b"]["n_ternary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
