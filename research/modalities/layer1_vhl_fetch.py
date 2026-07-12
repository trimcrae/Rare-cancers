#!/usr/bin/env python3
"""Layer-1 VHL calibration panel — primary-source DOSSIER fetcher (prereg §2 Layer-1 blocker).

The ternary-coop preregistration requires a QUANTITATIVE VHL calibration panel (>=6 systems with MEASURED
cooperativity alpha) BEFORE any prospective NR4A ternary ranking, and forbids fabricating alpha/PDB IDs
(nr4a3-ternary-coop-prereg.json → calibration.layer1_vhl_panel.provenance_freeze_blocker). This script gathers
the PRIMARY-SOURCE material to curate that panel from — it does NOT invent numbers and it does NOT itself write
the frozen scored manifest; a human/agent reads the dossier and fills `systems` + flips each `verified` flag
only from what the dossier actually shows.

WHY A CI RUNNER. The dev sandbox's egress proxy 403s RCSB / Europe PMC / NCBI at CONNECT (CLAUDE.md egress
rule), so the network mode runs on a GitHub Actions runner (see .github/workflows/fusion-cpu-extras.yml step
'Layer-1 VHL panel dossier') and publishes the dossier JSON. Pure stdlib (urllib), no pip — matching the
CPU-workflow convention.

WHAT IT GATHERS, per candidate system (the well-known VHL cooperativity literature — Ciulli-lab SMARCA2 series
+ MZ1/BRD4 as the independent transfer control):
  1. RCSB PDB search + entry metadata → CONFIRM the ternary complex exists, its title, and its bound ligands
     (machine-readable, high-confidence).
  2. Europe PMC → resolve the primary paper (PMID/PMCID/DOI, OA status) and retrieve OA full-text XML where
     available, so the MEASURED alpha (usually ITC-derived, in text/tables) can be read + curated.
Output: layer1-vhl-dossier.json = {candidates:[{id, expected_class, pdb:[...], paper:{...}, fulltext_available,
notes}], fetched_at_utc, ...}. The `measured_alpha` field is left NULL by this script on purpose — it is a
CURATION output, never a scrape guess.

OFFLINE. `--plan` prints the exact query targets (no network) so the target list is reviewable/testable in the
sandbox; the CI step runs the default (network) mode.
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.parse

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "layer1-vhl-dossier.json")

# ------------------------------------------------------------------------------------------------------------
# Candidate systems to VERIFY (NOT asserted as final; class labels are the EXPECTED cooperativity class the
# curation must confirm from the retrieved primary source). PDB/paper hints are search SEEDS, confirmed by the
# fetch — never trusted blind. The Ciulli-lab SMARCA2-VHL degrader series + MZ1/BRD4-VHL (independent control).
# ------------------------------------------------------------------------------------------------------------
CANDIDATES = [
    {"id": "mz1_brd4_vhl", "expected_class": "cooperative", "independent_vhl": True, "is_mz1": True,
     "search": {"rcsb_text": "MZ1 BRD4 VHL ternary", "europepmc": "MZ1 BRD4 VHL cooperativity ternary Gadd Ciulli"},
     "note": "independent VHL transfer control; solved cooperative VHL-BRD4 ternary (Gadd et al. 2017 Nat Chem Biol)."},
    {"id": "smarca2_vhl_series", "expected_class": "mixed_panel", "independent_vhl": False, "is_mz1": False,
     "search": {"rcsb_text": "SMARCA2 bromodomain VHL PROTAC ternary",
                "europepmc": "SMARCA2 VHL PROTAC cooperativity ternary Farnaby Ciulli"},
     "note": "the SMARCA2-VHL degrader series spans weak..strong alpha + inactive cis-Hyp stereo controls "
             "(Farnaby et al. 2019 Nat Chem Biol); curation must split it into the >=2 strong / >=2 weak-neg / "
             ">=1 inactive systems the prereg composition requires."},
]

UA = {"User-Agent": "rare-cancers-layer1-vhl-fetch/1.0 (research; contact via repo)"}
TIMEOUT = 30


def _get(url, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read().decode("utf-8", "replace")


def _get_json(url, headers=None):
    return json.loads(_get(url, headers))


# ------------------------------------------------------------------------------------------------------------
# RCSB — search for ternary structures + fetch entry metadata (title + bound ligand comp ids)
# ------------------------------------------------------------------------------------------------------------
def rcsb_search(text, rows=10):
    """RCSB full-text search → list of PDB IDs (best-effort; returns [] on any error so the CI step continues)."""
    q = {"query": {"type": "terminal", "service": "full_text", "parameters": {"value": text}},
         "return_type": "entry",
         "request_options": {"paginate": {"start": 0, "rows": rows},
                             "results_content_type": ["experimental"]}}
    url = "https://search.rcsb.org/rcsbsearch/v2/query?json=" + urllib.parse.quote(json.dumps(q))
    try:
        d = _get_json(url)
        return [hit["identifier"] for hit in d.get("result_set", [])]
    except Exception as e:  # noqa: BLE001
        return {"error": "%s: %s" % (type(e).__name__, e)}


def rcsb_entry(pdb_id):
    """Confirmed entry metadata: title + nonpolymer (ligand) comp ids. Best-effort."""
    try:
        d = _get_json("https://data.rcsb.org/rest/v1/core/entry/%s" % pdb_id)
        title = d.get("struct", {}).get("title")
        ligs = d.get("rcsb_entry_info", {}).get("nonpolymer_bound_components") or []
        return {"pdb_id": pdb_id, "title": title, "ligands": ligs}
    except Exception as e:  # noqa: BLE001
        return {"pdb_id": pdb_id, "error": "%s: %s" % (type(e).__name__, e)}


# ------------------------------------------------------------------------------------------------------------
# Europe PMC — resolve the primary paper + OA full-text availability
# ------------------------------------------------------------------------------------------------------------
def europepmc_search(query, rows=5):
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
           + urllib.parse.quote(query) + "&format=json&pageSize=%d" % rows)
    try:
        d = _get_json(url)
        out = []
        for r in d.get("resultList", {}).get("result", []):
            out.append({"pmid": r.get("pmid"), "pmcid": r.get("pmcid"), "doi": r.get("doi"),
                        "title": r.get("title"), "journal": r.get("journalTitle"), "year": r.get("pubYear"),
                        "is_oa": r.get("isOpenAccess") == "Y", "cited_by": r.get("citedByCount")})
        return out
    except Exception as e:  # noqa: BLE001
        return {"error": "%s: %s" % (type(e).__name__, e)}


def europepmc_fulltext_available(pmcid):
    """Does Europe PMC expose OA full-text XML for this PMCID? (Retrieve a small head to confirm.)"""
    if not pmcid:
        return False
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML" % pmcid
    try:
        txt = _get(url)
        return len(txt) > 500 and "<article" in txt
    except Exception:  # noqa: BLE001
        return False


# ------------------------------------------------------------------------------------------------------------
# driver
# ------------------------------------------------------------------------------------------------------------
def build_dossier():
    import datetime  # local import; argless datetime.now is fine here (CI run, not a resumable workflow)
    out = {"_purpose": "primary-source material to CURATE the Layer-1 VHL cooperativity panel; measured_alpha "
                       "is deliberately NULL — it is a curation output, never a scrape guess",
           "_prereg": "nr4a3-ternary-coop-prereg.json calibration.layer1_vhl_panel",
           "fetched_at_utc": datetime.datetime.utcnow().isoformat() + "Z", "candidates": []}
    for c in CANDIDATES:
        pdb_ids = rcsb_search(c["search"]["rcsb_text"])
        entries = [rcsb_entry(p) for p in (pdb_ids[:6] if isinstance(pdb_ids, list) else [])]
        papers = europepmc_search(c["search"]["europepmc"])
        for p in (papers if isinstance(papers, list) else []):
            p["fulltext_xml_available"] = europepmc_fulltext_available(p.get("pmcid"))
        out["candidates"].append({
            "id": c["id"], "expected_class": c["expected_class"],
            "independent_vhl": c["independent_vhl"], "is_mz1": c["is_mz1"], "note": c["note"],
            "rcsb_search": c["search"]["rcsb_text"], "pdb_hits": pdb_ids, "pdb_entries": entries,
            "europepmc_search": c["search"]["europepmc"], "papers": papers,
            "measured_alpha": None, "verified": False,
            "curation_todo": "read the OA full-text / structure to extract MEASURED alpha per compound; only "
                             "then set measured_alpha + verified and promote into the frozen scored manifest"})
    return out


def plan_targets():
    """Offline: the exact query targets (no network) — reviewable/testable in the sandbox."""
    return {"output": OUT, "candidates": [{"id": c["id"], "expected_class": c["expected_class"],
            "rcsb_text": c["search"]["rcsb_text"], "europepmc": c["search"]["europepmc"],
            "note": c["note"]} for c in CANDIDATES],
            "endpoints": ["RCSB search.rcsbsearch/v2/query", "RCSB data/rest/v1/core/entry/<id>",
                          "EuropePMC rest/search", "EuropePMC rest/<pmcid>/fullTextXML"]}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Layer-1 VHL calibration-panel primary-source dossier fetcher.")
    ap.add_argument("--plan", action="store_true", help="print query targets offline (no network) and exit")
    ap.add_argument("-o", "--out", default=OUT)
    args = ap.parse_args(argv)
    if args.plan:
        print(json.dumps(plan_targets(), indent=2))
        return 0
    dossier = build_dossier()
    with open(args.out, "w") as f:
        json.dump(dossier, f, indent=2)
    n = len(dossier["candidates"])
    print("[layer1-vhl-fetch] wrote %s (%d candidate systems; measured_alpha left NULL for curation)"
          % (args.out, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
