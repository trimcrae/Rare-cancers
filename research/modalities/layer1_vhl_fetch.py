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
     "search": {"rcsb_text": "MZ1 BRD4 VHL ternary 5T35",
                "europepmc": "MZ1 BRD4 BET VHL structural basis PROTAC ternary cooperativity Gadd 2017 Nature Chemical Biology"},
     "note": "independent VHL transfer control; solved cooperative VHL-BRD4(BD2) ternary, PDB 5T35 (Gadd et al. "
             "2017 Nat Chem Biol). Numeric alpha in that paper's ITC/SI -> archive for reviewer transcription."},
    {"id": "vhl_inactive_stereo_control", "expected_class": "inactive_control", "independent_vhl": False, "is_mz1": False,
     "search": {"rcsb_text": "VHL PROTAC inactive cis hydroxyproline epimer diastereomer",
                "europepmc": "VHL PROTAC inactive cis-hydroxyproline epimer diastereomer negative control ternary cooperativity"},
     "note": "the >=1 inactive stereo control the composition gate needs — a cis-Hyp (VHL-inactive) epimer that "
             "must be predicted non-competent. Archive the primary source; transcribe its status for the panel."},
    {"id": "smarca2_vhl_series", "expected_class": "mixed_panel", "independent_vhl": False, "is_mz1": False,
     "search": {"rcsb_text": "SMARCA2 bromodomain VHL PROTAC ternary",
                "europepmc": "SMARCA2 VHL PROTAC cooperativity ternary Farnaby Ciulli"},
     "note": "the SMARCA2-VHL degrader series spans weak..strong alpha + inactive cis-Hyp stereo controls "
             "(Farnaby et al. 2019 Nat Chem Biol); curation must split it into the >=2 strong / >=2 weak-neg / "
             ">=1 inactive systems the prereg composition requires."},
]

UA = {"User-Agent": "rare-cancers-layer1-vhl-fetch/1.0 (research; contact via repo)"}
TIMEOUT = 30


def _get(url, headers=None, retries=2, backoff=2.0):
    """GET with a small retry (RCSB/EuropePMC intermittently return non-JSON under burst load). Sleeps are fine
    here — this runs on a CI runner, not a resumable workflow."""
    import time
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={**UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt < retries:
                time.sleep(backoff * (attempt + 1))
    raise last


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


def europepmc_fulltext(pmcid):
    """Fetch the OA full-text XML for a PMCID (or None). Returns the raw XML string (may be large)."""
    if not pmcid:
        return None
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML" % pmcid
    try:
        txt = _get(url)
        return txt if (len(txt) > 500 and "<article" in txt) else None
    except Exception:  # noqa: BLE001
        return None


# ------------------------------------------------------------------------------------------------------------
# Supplementary DATA files — the numeric alpha per compound usually lives in a Source-Data xlsx/csv, NOT the
# body XML. Download the Europe PMC supplementaryFiles ZIP and pull cells/lines mentioning cooperativity/alpha
# + the compound labels, so the MEASURED values become curatable. Pure stdlib (zipfile parses xlsx too).
# ------------------------------------------------------------------------------------------------------------
def _xlsx_cell_text(zbytes):
    """Extract all cell strings from an .xlsx (a zip of XML) with stdlib only: sharedStrings + inline values.
    Returns a flat list of non-empty cell texts (order roughly row-major per sheet)."""
    import io
    import re
    import zipfile
    out = []
    try:
        with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
            shared = []
            if "xl/sharedStrings.xml" in z.namelist():
                ss = z.read("xl/sharedStrings.xml").decode("utf-8", "replace")
                shared = [re.sub(r"<[^>]+>", "", m) for m in re.findall(r"<si>(.*?)</si>", ss, flags=re.S)]
            for name in z.namelist():
                if not re.match(r"xl/worksheets/sheet\d+\.xml", name):
                    continue
                sx = z.read(name).decode("utf-8", "replace")
                for cell in re.findall(r"<c\b[^>]*?>.*?</c>|<c\b[^>]*?/>", sx, flags=re.S):
                    tmatch = re.search(r't="([^"]+)"', cell)
                    vmatch = re.search(r"<v>(.*?)</v>", cell, flags=re.S)
                    if not vmatch:
                        continue
                    val = vmatch.group(1)
                    if tmatch and tmatch.group(1) == "s":       # shared-string index
                        try:
                            val = shared[int(val)]
                        except (ValueError, IndexError):
                            pass
                    val = re.sub(r"\s+", " ", val).strip()
                    if val:
                        out.append(val)
    except Exception:  # noqa: BLE001
        return []
    return out


def supplementary_alpha_hits(pmcid, max_hits=60):
    """Download the OA supplementary-files ZIP and return cells/lines that mention cooperativity/alpha OR a
    PROTAC label (P1..P6), from any .xlsx/.csv/.txt/.tsv member — the raw material to curate numeric alpha
    from. Returns {files:[...], hits:[...]} (best-effort; {} on any failure)."""
    if not pmcid:
        return {}
    import io
    import re
    import zipfile
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/%s/supplementaryFiles" % pmcid
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = r.read()
    except Exception as e:  # noqa: BLE001
        return {"error": "%s: %s" % (type(e).__name__, e)}
    files, hits, archived = [], [], []
    want = re.compile(r"(cooperativ|alpha|α|\bP[1-6]\b|Kd|K_d|ternary|binary)", re.I)
    try:
        import hashlib
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for name in z.namelist():
                files.append(name)
                low = name.lower()
                try:
                    raw = z.read(name)
                except Exception:  # noqa: BLE001
                    continue
                if low.endswith(".pdf"):   # archive the SI PDF: checksum + size (the numeric-alpha table locator)
                    archived.append({"file": name, "sha256": hashlib.sha256(raw).hexdigest(),
                                     "bytes": len(raw)})
                cells = []
                if low.endswith(".xlsx"):
                    cells = _xlsx_cell_text(raw)
                elif low.endswith((".csv", ".tsv", ".txt")):
                    cells = [ln.strip() for ln in raw.decode("utf-8", "replace").splitlines() if ln.strip()]
                for cell in cells:
                    if want.search(cell):
                        hits.append({"file": name, "text": cell[:200]})
                        if len(hits) >= max_hits:
                            return {"files": files, "hits": hits, "archived_pdfs": archived}
    except Exception as e:  # noqa: BLE001
        return {"files": files, "error": "%s: %s" % (type(e).__name__, e), "archived_pdfs": archived}
    return {"files": files, "hits": hits, "archived_pdfs": archived}


# cooperativity / ITC terms whose surrounding text carries the MEASURED alpha we must curate
_COOP_TERMS = ("cooperativ", "α", "alpha", " ITC", "isothermal titration",
               "ternary", "K_d", "Kd ", " Kd", "dissociation constant", "positive coopera", "negative coopera")


def extract_tables(xml, max_tables=8, max_len=4000):
    """Pull <table-wrap> regions from full-text XML with cell text preserved row-wise (measured alpha values
    for a PROTAC series live in a table; the generic snippet stripper flattens them). Rows are '|'-joined so
    a curator can read 'P1 | <alpha> | ...'. Capped. Returns [] if no tables."""
    if not xml:
        return []
    import re
    out = []
    for tw in re.findall(r"<table-wrap\b.*?</table-wrap>", xml, flags=re.S | re.I)[:max_tables]:
        label = re.search(r"<label>(.*?)</label>", tw, flags=re.S | re.I)
        caption = re.search(r"<caption>(.*?)</caption>", tw, flags=re.S | re.I)
        rows = []
        for tr in re.findall(r"<tr\b.*?</tr>", tw, flags=re.S | re.I):
            cells = re.findall(r"<t[hd]\b.*?</t[hd]>", tr, flags=re.S | re.I)
            cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip() for c in cells]
            if any(cells):
                rows.append(" | ".join(cells))
        def _strip(m):
            return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip() if m else ""
        block = {"label": _strip(label), "caption": _strip(caption)[:400], "rows": rows}
        out.append(json.dumps(block)[:max_len])
    return out


def cooperativity_snippets(xml, max_snips=40, window=240):
    """Extract short text passages around cooperativity/ITC/alpha mentions from full-text XML (crude tag-strip;
    the goal is human-readable snippets to CURATE measured alpha from, NOT an automated alpha parse). Returns a
    capped list of de-duplicated passages."""
    if not xml:
        return []
    import re
    text = re.sub(r"<[^>]+>", " ", xml)          # strip tags
    text = re.sub(r"\s+", " ", text)
    low = text.lower()
    hits, seen = [], set()
    for term in _COOP_TERMS:
        t = term.lower()
        start = 0
        while True:
            i = low.find(t, start)
            if i < 0:
                break
            a, b = max(0, i - window), min(len(text), i + len(term) + window)
            snip = text[a:b].strip()
            key = snip[:80]
            if key not in seen:
                seen.add(key)
                hits.append(snip)
            start = i + len(term)
            if len(hits) >= max_snips:
                return hits
    return hits


# ------------------------------------------------------------------------------------------------------------
# driver
# ------------------------------------------------------------------------------------------------------------
def build_dossier():
    import datetime  # local import; argless datetime.now is fine here (CI run, not a resumable workflow)
    out = {"_purpose": "primary-source material to CURATE the Layer-1 VHL cooperativity panel; measured_alpha "
                       "is deliberately NULL — it is a curation output, never a scrape guess",
           "_prereg": "nr4a3-ternary-coop-prereg.json calibration.layer1_vhl_panel",
           "fetched_at_utc": datetime.datetime.utcnow().isoformat() + "Z", "candidates": []}
    import time
    for c in CANDIDATES:
        pdb_ids = rcsb_search(c["search"]["rcsb_text"])
        time.sleep(1.0)   # ease RCSB burst limits between candidates (the MZ1 search hit a transient error)
        entries = [rcsb_entry(p) for p in (pdb_ids[:6] if isinstance(pdb_ids, list) else [])]
        papers = europepmc_search(c["search"]["europepmc"])
        for p in (papers if isinstance(papers, list) else []):
            xml = europepmc_fulltext(p.get("pmcid"))
            p["fulltext_xml_available"] = xml is not None
            # pull cooperativity/ITC/alpha snippets + TABLES for curation (only OA full text we can read)
            p["cooperativity_snippets"] = cooperativity_snippets(xml) if xml else []
            p["tables"] = extract_tables(xml) if xml else []
        # supplementary DATA files (Source-Data xlsx/csv) for the top OA full-text papers — where numeric alpha
        # usually lives. Bounded to the first 2 FT papers per candidate to cap runtime/bandwidth.
        ft_papers = [p for p in (papers if isinstance(papers, list) else []) if p.get("fulltext_xml_available")]
        for p in ft_papers[:2]:
            p["supplementary_alpha"] = supplementary_alpha_hits(p.get("pmcid"))
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
