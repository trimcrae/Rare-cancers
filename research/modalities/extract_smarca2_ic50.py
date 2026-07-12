#!/usr/bin/env python3
"""Extract the SMARCA2-VHL cooperativity / IC50 table from the paper's SI PDF (reviewer 2026-07-12 Req 1).

The per-PROTAC alpha_TR-FRET + binary/ternary IC50 components + replicate/uncertainty metadata live in
Supplementary Table 1 of the SI PDF (Nat Commun 2025, PMC12480974) — not in the OA body XML. The dev sandbox
has no PDF library, but a GitHub Actions runner does: this runs there (pip install pdfplumber), downloads the
Europe PMC supplementaryFiles ZIP, VERIFIES the SI PDF checksum against the archived value, extracts every
table + cooperativity/IC50 text region, and writes smarca2-ic50-extract.json for curation. No fabrication —
it dumps what the PDF actually contains; a human/agent then transcribes P1-P4 into the frozen JSON.

Run via a CI step that does `pip install pdfplumber` (see fusion-cpu-extras.yml).
"""
import hashlib
import io
import json
import os
import re
import urllib.request
import zipfile

PMCID = "PMC12480974"
# archived checksums (from layer1_vhl_fetch supplementary_alpha.archived_pdfs) — verify before trusting
KNOWN_SHA = {
    "41467_2025_63713_MOESM1_ESM.pdf": "b9c875de73437a0ce53f7da7a19903e918de6efa7178b371709c7e853278bd57",
    "41467_2025_63713_MOESM9_ESM.pdf": "bf15443cf3bc8657003661bb621864cf42c6e3b8aef82f1ae0298b621e9cdc5f",
}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smarca2-ic50-extract.json")
UA = {"User-Agent": "rare-cancers-ic50-extract/1.0 (research)"}
WANT = re.compile(r"(cooperativ|alpha|α|IC50|IC₅₀|P[1-6]\b|Kd|ternary|binary|nM)", re.I)


def _download_supp_zip(pmcid):
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/%s/supplementaryFiles" % pmcid
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def _tables_from_pdf(raw, source):
    """Every table (as row lists) + cooperativity/IC50 text regions from a PDF, via pdfplumber."""
    import pdfplumber
    tables, text_hits = [], []
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for pno, page in enumerate(pdf.pages, 1):
            for t in (page.extract_tables() or []):
                rows = [[(c or "").strip() for c in row] for row in t]
                flat = " ".join(c for row in rows for c in row)
                if WANT.search(flat):        # keep only tables that mention cooperativity/IC50/P1-P5
                    tables.append({"source": source, "page": pno, "rows": rows})
            txt = page.extract_text() or ""
            for m in re.finditer(r"[^\n]*(?:cooperativ|IC50|IC₅₀)[^\n]*", txt, re.I):
                s = m.group(0).strip()
                if re.search(r"\d", s):
                    text_hits.append({"source": source, "page": pno, "line": s[:300]})
    return tables, text_hits


def main():
    out = {"_purpose": "SI-PDF table/text extraction for SMARCA2-VHL alpha_TR-FRET + binary/ternary IC50 "
                       "components (reviewer 2026-07-12 Req 1). Curate P1-P4 into the frozen JSON from THIS.",
           "pmcid": PMCID, "pdfs": [], "tables": [], "text_hits": []}
    try:
        data = _download_supp_zip(PMCID)
    except Exception as e:  # noqa: BLE001
        out["error"] = "supp download failed: %s: %s" % (type(e).__name__, e)
        json.dump(out, open(OUT, "w"), indent=2)
        print(out["error"]); return 1
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            if not name.lower().endswith(".pdf"):
                continue
            raw = z.read(name)
            sha = hashlib.sha256(raw).hexdigest()
            checksum_ok = (name not in KNOWN_SHA) or (sha == KNOWN_SHA[name])
            rec = {"file": name, "sha256": sha, "bytes": len(raw), "checksum_ok": checksum_ok}
            out["pdfs"].append(rec)
            if not checksum_ok:
                rec["skipped"] = "checksum MISMATCH vs archived — not parsed"
                continue
            try:
                tables, hits = _tables_from_pdf(raw, name)
                out["tables"].extend(tables)
                out["text_hits"].extend(hits)
                rec["n_tables"] = len(tables); rec["n_text_hits"] = len(hits)
            except Exception as e:  # noqa: BLE001
                rec["parse_error"] = "%s: %s" % (type(e).__name__, e)
    json.dump(out, open(OUT, "w"), indent=2)
    print("[ic50-extract] %s: %d pdf(s), %d cooperativity/IC50 tables, %d text hits -> %s"
          % (PMCID, len(out["pdfs"]), len(out["tables"]), len(out["text_hits"]), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
