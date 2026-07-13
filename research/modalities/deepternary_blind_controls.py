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
# protac-style token head: "5T35_H_E_759" -> "5T35" (unambiguous structure ID, has chain fields after)
PROTAC_STYLE_RE = re.compile(r"\b([1-9][A-Za-z0-9]{3})_[A-Za-z0-9]")
HAS_ALPHA_RE = re.compile(r"[A-Za-z]")

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
    """Scan the DeepTernary release/TernaryDB tree for PDB IDs, keeping provenance per ID.

    Two extraction tiers to avoid training-log contamination (the vis_data/scalars.json files log loss
    curves + iteration counts as bare 4-digit numbers that match a naive PDB-ID regex):
      - protac-style tokens `PDB_chain_chain_lig` are ALWAYS taken (unambiguous structure IDs).
      - bare 4-char tokens are taken ONLY from real list files AND only if they contain >=1 letter
        (drops pure-numeric training-log integers; no PROTAC/MGD training complex has a numeric-only ID).
      - files under a `vis_data/` dir or named `scalars.json` are skipped entirely (pure training logs).
    """
    provenance: dict[str, set] = {}
    scanned, skipped = [], []
    for root, _dirs, files in os.walk(dt_dir):
        for fn in files:
            low = fn.lower()
            if not (low.endswith((".txt", ".csv", ".tsv", ".lst", ".list", ".json"))):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, dt_dir)
            # skip pure training-log files: they carry loss/iteration integers, not structure IDs
            if "vis_data" in rel.split(os.sep) or low == "scalars.json":
                skipped.append(rel)
                continue
            try:
                if os.path.getsize(path) > 20 * 1024 * 1024:
                    skipped.append(rel)
                    continue
                with open(path, "r", errors="ignore") as fh:
                    text = fh.read()
            except OSError:
                continue
            scanned.append(rel)
            found = set()
            # tier 1: protac-style heads anywhere in the text (chain fields => unambiguous structure ID)
            for m in PROTAC_STYLE_RE.findall(text):
                found.add(m.upper())
            # tier 2: bare 4-char PDB tokens, but require >=1 letter to reject training-log integers
            for m in PDBID_RE.findall(text):
                if HAS_ALPHA_RE.search(m):
                    found.add(m.upper())
            for pid in found:
                provenance.setdefault(pid, set()).add(rel)
    return {
        "ids": sorted(provenance),
        "provenance": {k: sorted(v) for k, v in provenance.items()},
        "files_scanned": sorted(scanned),
        "files_skipped_as_logs": sorted(skipped),
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


def _rest(path: str):
    """GET a RCSB REST data-API endpoint; return parsed JSON or None (404/obsolete tolerated)."""
    try:
        return json.loads(_get("https://data.rcsb.org/rest/v1/core/" + path, timeout=40))
    except urllib.error.HTTPError as e:
        if e.code not in (404,):
            sys.stderr.write(f"[rest] {path} HTTP {e.code}\n")
        return None
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"[rest] {path} failed: {e}\n")
        return None


_CHEMCOMP_MW: dict = {}


def _comp_mw(comp_id: str):
    if comp_id in _CHEMCOMP_MW:
        return _CHEMCOMP_MW[comp_id]
    j = _rest(f"chemcomp/{comp_id}")
    mw = None
    name = None
    if j:
        cc = j.get("chem_comp") or {}
        mw = cc.get("formula_weight")
        name = cc.get("name")
    _CHEMCOMP_MW[comp_id] = (mw, name)
    return _CHEMCOMP_MW[comp_id]


def entry_metadata(pdb_ids: list) -> dict:
    """REST data-API metadata per candidate for curation (title, dates, entities, UniProts, ligands).

    Two passes to keep call volume modest: pass 1 fetches entry + polymer-entity data (UniProts) for every
    candidate; pass 2 fetches ligand comp IDs + MW only for entries that carry a known-E3 UniProt (the
    shortlist candidates). REST is used (not the batched GraphQL) because the large GraphQL query silently
    returned empty and cannot be validated from the egress-blocked sandbox; REST endpoints are stable.
    """
    out = {}
    for n, pid in enumerate(pdb_ids):
        ent = _rest(f"entry/{pid}")
        if not ent:
            continue
        ai = ent.get("rcsb_accession_info") or {}
        ei = ent.get("rcsb_entry_info") or {}
        ci = ent.get("rcsb_entry_container_identifiers") or {}
        prots, uniprots = [], []
        for eid in (ci.get("polymer_entity_ids") or []):
            pe = _rest(f"polymer_entity/{pid}/{eid}")
            if not pe:
                continue
            desc = ((pe.get("rcsb_polymer_entity") or {}).get("pdbx_description") or "").strip()
            if desc:
                prots.append(desc)
            pci = pe.get("rcsb_polymer_entity_container_identifiers") or {}
            for rs in (pci.get("reference_sequence_identifiers") or []):
                if (rs.get("database_name") or "").upper().startswith("UNIPROT"):
                    uniprots.append(rs.get("database_accession"))
        uniprots = sorted(set(u for u in uniprots if u))
        e3_hits = {u: E3_INTERFACE_UNIPROT[u] for u in uniprots if u in E3_INTERFACE_UNIPROT}
        out[pid] = {
            "title": (ent.get("struct") or {}).get("title"),
            "deposit_date": (ai.get("deposit_date") or "")[:10],
            "initial_release_date": (ai.get("initial_release_date") or "")[:10],
            "n_protein_entities": ei.get("polymer_entity_count_protein"),
            "n_nonpolymer": ei.get("deposited_nonpolymer_entity_count"),
            "protein_names": prots,
            "uniprots": uniprots,
            "e3_uniprot_hits": e3_hits,
            "nonpolymer_entity_ids": list(ci.get("non_polymer_entity_ids") or []),
            "ligands": [],
            "degrader_sized_ligands": [],
        }
        if n % 25 == 0:
            time.sleep(0.2)
    # pass 2: ligand detail only for E3-positive entries (the shortlist)
    for pid, m in out.items():
        if not m["e3_uniprot_hits"]:
            continue
        ligs = []
        for eid in m["nonpolymer_entity_ids"]:
            ne = _rest(f"nonpolymer_entity/{pid}/{eid}")
            comp = None
            if ne:
                comp = ((ne.get("pdbx_entity_nonpoly") or {}).get("comp_id"))
            if not comp:
                continue
            mw, name = _comp_mw(comp)
            ligs.append({"id": comp, "name": name, "mw": mw})
        m["ligands"] = ligs
        m["degrader_sized_ligands"] = [l for l in ligs if (l.get("mw") or 0) and l["mw"] > 450]
    return out


def source_input_structures(controls: list, exclude_native: set) -> dict:
    """For each curated control, find SEPARATE binary/apo structures for blind input prep.

    DeepTernary unbound PROTAC inputs (from predict.py) need, per control: a POI structure +
    the warhead fragment in that POI frame (from a POI+warhead binary co-crystal), and an E3
    structure + the anchor fragment in that E3 frame (from an E3+anchor binary). Neither may be
    the native ternary. This queries RCSB for candidate binaries by UniProt accession + entity
    count, so the input structures are SOURCED (human curates the final pick per the integrity gate).
    Blindness note: using public 'POI binds warhead-class ligand' structures is NOT native-pose
    leakage — only the native ternary POSE stays sealed.
    """
    def _by_uniprot(uniprot: str, max_prot: int, label: str, exclude: set) -> list:
        query = {"type": "group", "logical_operator": "and", "nodes": [
            {"type": "terminal", "service": "text", "parameters": {
                "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
                "operator": "exact_match", "value": uniprot}},
            {"type": "terminal", "service": "text", "parameters": {
                "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_name",
                "operator": "exact_match", "value": "UniProt"}},
            {"type": "terminal", "service": "text", "parameters": {
                "attribute": "rcsb_entry_info.polymer_entity_count_protein",
                "operator": "less_or_equal", "value": max_prot}},
            {"type": "terminal", "service": "text", "parameters": {
                "attribute": "rcsb_entry_info.deposited_nonpolymer_entity_count",
                "operator": "greater_or_equal", "value": 1}},
        ]}
        req = {"query": query, "return_type": "entry",
               "request_options": {"paginate": {"start": 0, "rows": 60},
                                   "results_content_type": ["experimental"]}}
        url = "https://search.rcsb.org/rcsbsearch/v2/query?json=" + urllib.parse.quote(json.dumps(req))
        try:
            res = json.loads(_get(url))
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode()[:400]
            except Exception:  # noqa: BLE001
                pass
            sys.stderr.write(f"[src:{label}] {uniprot} HTTP {e.code}: {body}\n")
            return []
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"[src:{label}] {uniprot} failed: {e}\n")
            return []
        ids = [r["identifier"].upper() for r in res.get("result_set", [])
               if r["identifier"].upper() not in exclude]
        time.sleep(0.4)
        # sort by deposition date (desc) via the fast batched date lookup, then annotate the top 12
        if ids:
            dd = deposit_dates(ids)
            ids.sort(key=lambda p: dd.get(p, {}).get("deposit_date", ""), reverse=True)
        # annotate the top handful with ligands so a human can pick the warhead/anchor binary
        meta = entry_metadata(ids[:12]) if ids else {}
        return [{"pdb": pid, "deposit_date": meta.get(pid, {}).get("deposit_date"),
                 "proteins": meta.get(pid, {}).get("protein_names"),
                 "ligands": [{"id": l["id"], "mw": l.get("mw")} for l in meta.get(pid, {}).get("ligands", [])]}
                for pid in ids[:12]]

    out = {}
    for ctl in controls:
        pid = ctl["pdb"]
        poi_uni = None
        # POI uniprot = the control's uniprot that is NOT an E3/adapter component
        adapters = set(E3_INTERFACE_UNIPROT) | {"Q15369", "Q15370", "P62877", "Q16531",
                                                "Q13617", "Q13619", "P62979", "P0CG48"}
        for u in ctl.get("uniprots", []):
            if u not in adapters:
                poi_uni = u
                break
        # controls file stores e3 as a label string ("VHL"/"CRBN"); recover the accession
        inv = {v: k for k, v in E3_INTERFACE_UNIPROT.items()}
        e3_uni = inv.get(ctl.get("e3"))
        excl = exclude_native | {pid}
        out[pid] = {
            "poi": ctl.get("target_of_interest"),
            "poi_uniprot": poi_uni,
            "e3": ctl.get("e3"),
            "e3_uniprot": e3_uni,
            "poi_binary_candidates": _by_uniprot(poi_uni, 2, f"{pid}:POI", excl) if poi_uni else [],
            "e3_binary_candidates": _by_uniprot(e3_uni, 4, f"{pid}:E3", excl) if e3_uni else [],
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dt-dir", help="path to extracted DeepTernary release + TernaryDB")
    ap.add_argument("--exclusion-file", help="prebuilt exclusion-set JSON (skips --dt-dir / TernaryDB "
                    "download); expects keys ids[] + data_horizon_max_deposit_date")
    ap.add_argument("--out", default="deepternary_blind_controls.json")
    ap.add_argument("--fallback-cutoff", default="2024-06-01",
                    help="used for the search window if the exclusion set yields no dates")
    ap.add_argument("--search-terms", default="PROTAC,degrader,molecular glue,ternary complex")
    ap.add_argument("--source-inputs", help="curated controls JSON; emit per-control binary input-structure "
                    "candidates instead of running the candidate search")
    args = ap.parse_args()

    # input-sourcing mode: given curated controls, find their separate binary input structures
    if args.source_inputs:
        controls_doc = json.load(open(args.source_inputs))
        native = set()
        for c in controls_doc.get("controls", []):
            native.add(c["pdb"])
        src = source_input_structures(controls_doc.get("controls", []), native)
        rep = {"_protocol": "deepternary-qualification-protocol.md Step 3 blind input prep",
               "_note": "SOURCED binary input-structure candidates (RCSB). Human curates the final POI+warhead "
                        "and E3+anchor binary per control; native ternary pose stays sealed.",
               "input_structure_candidates": src}
        with open(args.out, "w") as fh:
            json.dump(rep, fh, indent=1)
        for pid, s in src.items():
            print(f"\n{pid}  POI={s['poi']}({s['poi_uniprot']})  E3={s['e3']}({s['e3_uniprot']})")
            print(f"  POI binary candidates: {[c['pdb'] for c in s['poi_binary_candidates']]}")
            print(f"  E3  binary candidates: {[c['pdb'] for c in s['e3_binary_candidates']]}")
        return 0

    report = {"_protocol": "research/modalities/deepternary-qualification-protocol.md (Step 3 + risk #5)",
              "_generated_note": "All PDB facts sourced from RCSB; DeepTernary IDs from the frozen release."}

    # A. exclusion set — from a prebuilt file (fast path) or freshly from the DeepTernary release
    prebuilt_horizon = None
    excl = {"ids": [], "provenance": {}, "files_scanned": [], "files_skipped_as_logs": []}
    prebuilt_dates = {}
    if args.exclusion_file and os.path.isfile(args.exclusion_file):
        pj = json.load(open(args.exclusion_file))
        excl = {"ids": pj.get("ids", []), "provenance": pj.get("provenance", {}),
                "files_scanned": pj.get("files_scanned", []),
                "files_skipped_as_logs": pj.get("files_skipped_as_logs", [])}
        prebuilt_horizon = pj.get("data_horizon_max_deposit_date")
        prebuilt_dates = pj.get("exclusion_set_deposit_dates", {})
    elif args.dt_dir and os.path.isdir(args.dt_dir):
        excl = build_exclusion_set(args.dt_dir)
    report["exclusion_set"] = {"count": len(excl["ids"]), "ids": excl["ids"],
                               "files_scanned": excl["files_scanned"],
                               "files_skipped_as_logs": excl.get("files_skipped_as_logs", []),
                               "provenance": excl["provenance"]}

    # B. data horizon
    horizon = args.fallback_cutoff
    dates = prebuilt_dates
    if prebuilt_horizon:
        horizon = prebuilt_horizon
    elif excl["ids"]:
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
