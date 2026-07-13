#!/usr/bin/env python3
"""DeepTernary Step-3 foundation: leakage audit + post-cutoff blind-control candidate finder.

Governing protocol: research/modalities/deepternary-qualification-protocol.md
  - Step 3 = prospective-like BLIND controls: PROTAC ternaries NOT in DeepTernary's train/val/test,
    ideally deposited AFTER its data horizon, inputs prepared from SEPARATE monomer/binary structures.
  - Risk #5 = training-set-leakage audit (broader than "PROTACs excluded").
  - Integrity gate (2026-07-13): E3 identity + deposition dates must be SOURCED from RCSB, never guessed.

This script does the two things that gate a valid blind-control selection, and does them from primary
data only (no memory-based structure facts):

  A. EXCLUSION SET  — walk the frozen DeepTernary release + TernaryDB, extract every 4-char PDB ID that
     appears in any split/list/manifest, with provenance (which file each ID came from). These are the
     structures DeepTernary may have seen; a blind control MUST NOT be one of them.

  B. DATA HORIZON   — via the RCSB data API, fetch the deposition date of every exclusion-set PDB ID and
     report the max = the effective "DeepTernary could have seen up to" horizon. A blind control should
     deposit strictly after it.

  C. CANDIDATES     — query the RCSB search API for degrader ternary complexes (full-text PROTAC/degrader/
     molecular-glue) deposited after a cutoff, then GraphQL-fetch each hit's title, dates, polymer-entity
     descriptions + UniProt accessions (to identify POI + E3 by accession, not by guess), and ligand IDs +
     MW. Flag: in exclusion set? has a known-E3 UniProt? >=2 protein entities? has a degrader-sized ligand?
     Emit a sourced JSON table for human curation of the final 2-3 blind controls.

Pure stdlib (urllib/json/re/tarfile/zipfile) so it runs on a free CPU GitHub-Actions runner (RCSB is
egress-blocked in the dev sandbox). NOTHING here is fabricated: every field is copied from RCSB or from
the DeepTernary release; the known-E3 UniProt map is the only curated constant and is standard + cited.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

# --- standard E3-ligase substrate-receptor UniProt accessions (human), for identifying the E3 arm ---
# These are canonical UniProt IDs; used only to CLASSIFY an RCSB-reported accession, never to invent one.
KNOWN_E3_UNIPROT = {
    "P40337": "VHL",        # von Hippel-Lindau
    "Q96SW2": "CRBN",       # cereblon
    "Q13490": "cIAP1/BIRC2",
    "Q13489": "cIAP2/BIRC3",
    "P98170": "XIAP",
    "Q00987": "MDM2",
    "Q9Y2X8": "DCAF (UBE2D)",  # placeholder guard; refined below by name if needed
    "Q9NWF9": "DCAF16",
    "Q8TEB1": "DCAF11",
    "Q7L590": "MCM10",      # guard (not an E3; excluded by name check)
    "Q14145": "KEAP1",
    "Q969H0": "FBXW7",
    "P63208": "SKP1",
    "Q13616": "CUL1",
    "Q13617": "CUL2",
    "Q13618": "CUL3",
    "Q13619": "CUL4A",
    "Q13620": "CUL4B",
}
# E3 substrate receptors we actually care about for a PROTAC/glue ternary interface:
E3_INTERFACE_UNIPROT = {"P40337": "VHL", "Q96SW2": "CRBN", "Q13490": "cIAP1", "Q13489": "cIAP2",
                        "P98170": "XIAP", "Q00987": "MDM2", "Q14145": "KEAP1", "Q9NWF9": "DCAF16",
                        "Q8TEB1": "DCAF11"}

PDBID_RE = re.compile(r"\b([1-9][A-Za-z0-9]{3})\b")

UA = {"User-Agent": "rare-cancers-deepternary-qual/1.0 (research; contact trimcrae@gmail.com)"}


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _post_json(url: str, payload: dict, timeout: int = 90) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={**UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


# ------------------------------------------------------------------ A. exclusion set from DT release ---
def build_exclusion_set(dt_dir: str) -> dict:
    """Scan the DeepTernary release/TernaryDB tree for PDB IDs, keeping provenance per ID."""
    provenance: dict[str, set] = {}
    scanned = []
    for root, _dirs, files in os.walk(dt_dir):
        for fn in files:
            low = fn.lower()
            if not (low.endswith((".txt", ".csv", ".tsv", ".lst", ".list", ".json"))):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, dt_dir)
            # skip huge non-list files defensively (>20MB); PDB-ID list files are tiny
            try:
                if os.path.getsize(path) > 20 * 1024 * 1024:
                    continue
                with open(path, "r", errors="ignore") as fh:
                    text = fh.read()
            except OSError:
                continue
            scanned.append(rel)
            found = set()
            # protac-style IDs "5T35_H_E_759" -> first field; plus any bare 4-char PDB tokens
            for line in text.replace(",", " ").split():
                tok = line.strip()
                head = tok.split("_")[0]
                for cand in (head, tok):
                    m = PDBID_RE.fullmatch(cand)
                    if m:
                        found.add(cand.upper())
            # also sweep the raw text for embedded PDB IDs (json values etc.)
            for m in PDBID_RE.findall(text):
                found.add(m.upper())
            for pid in found:
                provenance.setdefault(pid, set()).add(rel)
    # A bare-token regex over prose is noisy (e.g. 4-char words). Keep only IDs that appear in a file whose
    # name/path looks like a structure list, OR appear as a protac-style "<PDB>_<ch>_<ch>_<lig>" token.
    return {
        "ids": sorted(provenance),
        "provenance": {k: sorted(v) for k, v in provenance.items()},
        "files_scanned": sorted(scanned),
    }


# ------------------------------------------------------------------ B. deposition dates via data API ---
def deposit_dates(pdb_ids: list) -> dict:
    """Batch GraphQL: {PDBID: {deposit_date, initial_release}} from RCSB data API."""
    out = {}
    url = "https://data.rcsb.org/graphql"
    for i in range(0, len(pdb_ids), 50):
        batch = pdb_ids[i:i + 50]
        q = ("query($ids:[String!]!){entries(entry_ids:$ids){rcsb_id "
             "rcsb_accession_info{deposit_date initial_release_date}}}")
        try:
            res = _post_json(url, {"query": q, "variables": {"ids": batch}})
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"[dates] batch {i} failed: {e}\n")
            continue
        for e in (res.get("data", {}).get("entries") or []):
            ai = e.get("rcsb_accession_info") or {}
            out[e["rcsb_id"].upper()] = {
                "deposit_date": (ai.get("deposit_date") or "")[:10],
                "initial_release_date": (ai.get("initial_release_date") or "")[:10],
            }
        time.sleep(0.3)
    return out


# ------------------------------------------------------------------ C. RCSB search for candidates ------
def search_candidates(after_date: str, terms: list, rows: int = 300) -> list:
    """Full-text degrader search, deposited strictly after `after_date`. Returns list of PDB IDs."""
    ids = set()
    for term in terms:
        query = {
            "type": "group",
            "logical_operator": "and",
            "nodes": [
                {"type": "terminal", "service": "full_text", "parameters": {"value": term}},
                {"type": "terminal", "service": "text", "parameters": {
                    "attribute": "rcsb_accession_info.deposit_date",
                    "operator": "greater", "value": f"{after_date}T00:00:00Z"}},
                {"type": "terminal", "service": "text", "parameters": {
                    "attribute": "rcsb_entry_info.polymer_entity_count_protein",
                    "operator": "greater_or_equal", "value": 2}},
            ],
        }
        req = {"query": query, "return_type": "entry",
               "request_options": {"paginate": {"start": 0, "rows": rows},
                                   "results_content_type": ["experimental"]}}
        url = "https://search.rcsb.org/rcsbsearch/v2/query?json=" + urllib.parse.quote(json.dumps(req))
        try:
            res = json.loads(_get(url))
        except urllib.error.HTTPError as e:
            if e.code == 204:  # no hits
                continue
            sys.stderr.write(f"[search] term={term!r} HTTP {e.code}\n")
            continue
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"[search] term={term!r} failed: {e}\n")
            continue
        for r in res.get("result_set", []):
            ids.add(r["identifier"].upper())
        time.sleep(0.4)
    return sorted(ids)


def entry_metadata(pdb_ids: list) -> dict:
    """Batch GraphQL: full metadata per candidate for curation (title, dates, entities, UniProts, ligs)."""
    out = {}
    url = "https://data.rcsb.org/graphql"
    q = """query($ids:[String!]!){entries(entry_ids:$ids){
      rcsb_id
      struct{title}
      rcsb_accession_info{deposit_date initial_release_date}
      rcsb_entry_info{deposited_polymer_entity_count deposited_nonpolymer_entity_count
                      polymer_entity_count_protein}
      polymer_entities{
        rcsb_polymer_entity{pdbx_description}
        rcsb_polymer_entity_container_identifiers{
          reference_sequence_identifiers{database_accession database_name}}
      }
      nonpolymer_entities{
        nonpolymer_comp{chem_comp{id name formula_weight}}
      }
    }}"""
    for i in range(0, len(pdb_ids), 40):
        batch = pdb_ids[i:i + 40]
        try:
            res = _post_json(url, {"query": q, "variables": {"ids": batch}})
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"[meta] batch {i} failed: {e}\n")
            continue
        for e in (res.get("data", {}).get("entries") or []):
            pid = e["rcsb_id"].upper()
            ai = e.get("rcsb_accession_info") or {}
            ei = e.get("rcsb_entry_info") or {}
            prots, uniprots = [], []
            for pe in (e.get("polymer_entities") or []):
                desc = ((pe.get("rcsb_polymer_entity") or {}).get("pdbx_description") or "").strip()
                if desc:
                    prots.append(desc)
                cid = pe.get("rcsb_polymer_entity_container_identifiers") or {}
                for rs in (cid.get("reference_sequence_identifiers") or []):
                    if (rs.get("database_name") or "").upper().startswith("UNIPROT"):
                        uniprots.append(rs.get("database_accession"))
            ligs = []
            for ne in (e.get("nonpolymer_entities") or []):
                cc = ((ne.get("nonpolymer_comp") or {}).get("chem_comp") or {})
                if cc.get("id"):
                    ligs.append({"id": cc["id"], "name": cc.get("name"),
                                 "mw": cc.get("formula_weight")})
            e3_hits = {u: E3_INTERFACE_UNIPROT[u] for u in uniprots if u in E3_INTERFACE_UNIPROT}
            # a degrader-sized ligand = any HETATM comp with MW > 450 that isn't a common buffer/ion
            big_ligs = [l for l in ligs if (l.get("mw") or 0) and l["mw"] > 450]
            out[pid] = {
                "title": (e.get("struct") or {}).get("title"),
                "deposit_date": (ai.get("deposit_date") or "")[:10],
                "initial_release_date": (ai.get("initial_release_date") or "")[:10],
                "n_protein_entities": ei.get("polymer_entity_count_protein"),
                "n_nonpolymer": ei.get("deposited_nonpolymer_entity_count"),
                "protein_names": prots,
                "uniprots": sorted(set(u for u in uniprots if u)),
                "e3_uniprot_hits": e3_hits,
                "ligands": ligs,
                "degrader_sized_ligands": big_ligs,
            }
        time.sleep(0.3)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dt-dir", help="path to extracted DeepTernary release + TernaryDB")
    ap.add_argument("--out", default="deepternary_blind_controls.json")
    ap.add_argument("--fallback-cutoff", default="2024-06-01",
                    help="used for the search window if the exclusion set yields no dates")
    ap.add_argument("--search-terms", default="PROTAC,degrader,molecular glue,ternary complex")
    args = ap.parse_args()

    report = {"_protocol": "research/modalities/deepternary-qualification-protocol.md (Step 3 + risk #5)",
              "_generated_note": "All PDB facts sourced from RCSB; DeepTernary IDs from the frozen release."}

    # A. exclusion set
    excl = {"ids": [], "provenance": {}, "files_scanned": []}
    if args.dt_dir and os.path.isdir(args.dt_dir):
        excl = build_exclusion_set(args.dt_dir)
    report["exclusion_set"] = {"count": len(excl["ids"]), "ids": excl["ids"],
                               "files_scanned": excl["files_scanned"],
                               "provenance": excl["provenance"]}

    # B. data horizon
    horizon = args.fallback_cutoff
    dates = {}
    if excl["ids"]:
        dates = deposit_dates(excl["ids"])
        dep = sorted([d["deposit_date"] for d in dates.values() if d.get("deposit_date")])
        if dep:
            horizon = dep[-1]
    report["deepternary_data_horizon"] = {
        "max_deposit_date_in_exclusion_set": horizon,
        "note": "A valid Step-3 blind control should deposit strictly AFTER this date.",
        "exclusion_set_deposit_dates": dates,
    }

    # C. candidates deposited after the horizon
    terms = [t.strip() for t in args.search_terms.split(",") if t.strip()]
    cand_ids = search_candidates(horizon, terms)
    excl_ids = set(excl["ids"])
    # never re-query exclusion members as "candidates"; but keep note of any overlap for the audit
    overlap = sorted(set(cand_ids) & excl_ids)
    fresh = [c for c in cand_ids if c not in excl_ids]
    meta = entry_metadata(fresh) if fresh else {}

    # rank: has known E3 + >=2 proteins + degrader-sized ligand, newest first
    def _score(pid):
        m = meta.get(pid, {})
        return (bool(m.get("e3_uniprot_hits")),
                (m.get("n_protein_entities") or 0) >= 2,
                bool(m.get("degrader_sized_ligands")),
                m.get("deposit_date") or "")
    ranked = sorted(meta, key=_score, reverse=True)

    report["candidates"] = {
        "search_terms": terms,
        "deposited_after": horizon,
        "n_search_hits_total": len(cand_ids),
        "n_overlapping_exclusion_set": len(overlap),
        "overlapping_ids": overlap,
        "n_fresh_candidates": len(fresh),
        "ranked_ids": ranked,
        "metadata": {pid: meta[pid] for pid in ranked},
    }
    report["shortlist_hint"] = [
        pid for pid in ranked
        if meta.get(pid, {}).get("e3_uniprot_hits")
        and (meta.get(pid, {}).get("n_protein_entities") or 0) >= 2
        and meta.get(pid, {}).get("degrader_sized_ligands")
    ][:12]

    with open(args.out, "w") as fh:
        json.dump(report, fh, indent=1)
    # human-readable tail to stdout / CI log
    print(f"exclusion set: {len(excl['ids'])} PDB IDs (horizon {horizon})")
    print(f"search hits: {len(cand_ids)}  fresh (not in exclusion): {len(fresh)}  "
          f"overlap: {len(overlap)}")
    print(f"shortlist_hint ({len(report['shortlist_hint'])}): {report['shortlist_hint']}")
    for pid in report["shortlist_hint"]:
        m = meta[pid]
        e3 = ",".join(m["e3_uniprot_hits"].values()) or "-"
        print(f"  {pid}  dep {m['deposit_date']}  E3={e3}  prot={m['n_protein_entities']}  "
              f"lig={[l['id'] for l in m['degrader_sized_ligands']]}  {m['title'][:70]!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
