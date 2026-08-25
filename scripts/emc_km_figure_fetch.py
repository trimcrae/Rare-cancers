#!/usr/bin/env python3
"""Retrieve the Kaplan-Meier FIGURE GRAPHICS of the candidate EMC survival series.

WHY A SEPARATE FETCHER
----------------------
`research/literature/emc-ipd-admissibility-2026-08-12.json` closed step 1 with one open question
and named it exactly: *"Look at the four figure graphics and answer one bounded yes/no per curve:
is there a numbers-at-risk row beneath the axis? Obtaining them needs a working route to the OA
package or the publisher's figure assets; the OA service names the package and the HTTPS mirror
for it is still unresolved."*

⛔ THE UNRESOLVED HALF WAS A PROTOCOL, NOT A HOST. That probe rewrote the OA service's `ftp://`
href to `https://` on the same host and got 404 for every path. This script does not rewrite it: it
requests the `ftp://` URL AS GIVEN, which `urllib` speaks natively, and only falls back to guessed
HTTPS mirrors afterwards. Every route is attempted in order and EVERY outcome is recorded, so the
artifact says which route worked rather than only that one did.

THE ROUTE LADDER, cheapest and most faithful first
--------------------------------------------------
  1. `oa.fcgi` -> the OA package `tgz`, fetched over **ftp://**. This is the publisher's own figure
     raster at its original resolution -- the best possible input to a digitizer, because nothing
     has been re-rendered, re-compressed or resampled between the journal and the pixel.
  2. the same record's `pdf` href over ftp://.
  3. HTTPS mirrors of both (kept because when they work they are faster, not because they are
     better).
  4. `europepmc.org/articles/<PMCID>?pdf=render`.
  5. the caller's explicit `pdf_url`, for a publisher-hosted PDF the OA service does not carry.
A PDF is then rasterised page by page with poppler; a tgz is unpacked and its images are taken
directly.

⛔ WHAT IT DOES NOT DO. It does not decide admissibility, it does not read a curve and it does not
say whether a numbers-at-risk row is present. Those are readings of a graphic, and this script's
whole job is to make the graphic exist locally so that a reading is possible at all. Confusing
retrieval with reading is how `numbers_at_risk_in_text_or_table: false` -- a fact about a TEXT
SEARCH -- became quotable as a fact about the papers.

Env:
  KM_TARGETS_JSON   JSON list of {"source_id", "pmcid", optional "pdf_url"}. Defaults to TARGETS.
  KM_OUT_DIR        output directory (default .cache/literature)
  KM_MAX_BYTES      soft cap on total published bytes (default 60 MiB)
  KM_RENDER_DPI     poppler render resolution for PDF pages (default 200)
"""

from __future__ import annotations

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (compatible; rare-cancers-research/1.0; +https://github.com/trimcrae/Rare-cancers)"
OUT_DIR = os.environ.get("KM_OUT_DIR", ".cache/literature")
MAX_BYTES = int(os.environ.get("KM_MAX_BYTES", str(60 * 1024 * 1024)))
DPI = int(os.environ.get("KM_RENDER_DPI", "200"))
# ⭐ RASTERISING ON THE RUNNER IS OPTIONAL, AND USUALLY THE WRONG PLACE TO DO IT. Page PNGs at
# 200 dpi were 36 MB for five papers, against 5.6 MB for the PDFs that produced them — and a
# session that needs a figure will re-render the one page it wants at 600 dpi anyway. Set
# KM_RASTERISE=0 to publish the PDFs only. The runner's job is the part the sandbox cannot do,
# which is reaching the network, not the part it can.
RASTERISE = os.environ.get("KM_RASTERISE", "1") != "0"

# The candidate set is OWNED by research/modalities/emc_ipd_survival.py:CANDIDATE_SOURCES, which
# records why each row is a candidate and what its overlap risk is. Only the rows with a resolved
# PMC identifier can be fetched at all, so only those appear here -- and their absence from this
# list is a statement about REACHABILITY, never about relevance.
TARGETS = [
    {"source_id": "masunaga2025", "pmcid": "PMC12398172"},
    {"source_id": "chiusole2020", "pmcid": "PMC7308468"},
    {"source_id": "martinbroto2020immunosarc1", "pmcid": "PMC7674086"},
    {"source_id": "morioka2016trabectedin", "pmcid": "PMC4946242"},
    {"source_id": "stacchiotti2013anthracycline", "pmcid": "PMC3879193"},
    # Recorded as NOT open access by the OA service on 2026-08-12. Kept so the run re-tests the
    # claim rather than inheriting it -- an access decision made by a publisher can change.
    {"source_id": "drilon2008", "pmcid": "PMC2779719"},
    {"source_id": "bishop2019", "pmcid": "PMC7771031"},
]

IMG_EXT = (".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff")


def _get(url: str, timeout: int = 90) -> tuple[int, str, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA}) if url.startswith("http") else url
    try:
        with urllib.request.urlopen(req, timeout=timeout) as fh:
            body = fh.read()
            ctype = fh.headers.get("Content-Type", "") if hasattr(fh, "headers") else ""
            code = getattr(fh, "status", 200) or 200
            return code, ctype, body
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get("Content-Type", ""), exc.read()[:2000]
    except Exception as exc:  # noqa: BLE001 -- the failure MODE is the datum here
        return 0, f"{type(exc).__name__}: {exc}"[:300], b""


def oa_records(pmcid: str) -> dict:
    """Ask the OA service what it holds. Returns hrefs verbatim -- ftp:// scheme included."""
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmcid}"
    code, ctype, body = _get(url)
    text = body.decode("utf-8", "replace")
    out = {"lookup_url": url, "http": code, "content_type": ctype, "raw": text[:1500],
           "tgz": None, "pdf": None, "error_code": None, "license": None}
    m = re.search(r'<error\s+code="([^"]+)"', text)
    if m:
        out["error_code"] = m.group(1)
    m = re.search(r'license="([^"]*)"', text)
    if m:
        out["license"] = m.group(1)
    for fmt in ("tgz", "pdf"):
        m = re.search(rf'<link\s+format="{fmt}"[^>]*href="([^"]+)"', text)
        if m:
            out[fmt] = m.group(1)
    return out


def resolve_pmcid(pmid: str) -> dict:
    """Ask Europe PMC what PMC identifier, if any, a PMID has, and whether it is open access.

    ⛔ A MISSING PMCID IS A FINDING, NOT AN ERROR. Most of this program's candidate series are
    older or subscription-only; recording "no PMC record" is a statement about REACHABILITY at $0,
    and it is the honest end of the road for that row until somebody pays for a copy.
    """
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search"
           f"?query=EXT_ID:{pmid}%20AND%20SRC:MED&format=json&resultType=core&pageSize=1")
    code, ctype, body = _get(url)
    out = {"query_url": url, "http": code, "pmcid": None, "is_open_access": None,
           "in_epmc": None, "title": None, "journal": None}
    if code != 200:
        out["error"] = f"HTTP {code}"
        return out
    try:
        doc = json.loads(body.decode("utf-8", "replace"))
    except Exception as exc:  # noqa: BLE001
        out["error"] = f"unparseable: {type(exc).__name__}: {exc}"
        return out
    hits = (doc.get("resultList") or {}).get("result") or []
    if not hits:
        out["error"] = "no Europe PMC record for this PMID"
        return out
    rec = hits[0]
    out["pmcid"] = rec.get("pmcid")
    out["is_open_access"] = rec.get("isOpenAccess")
    out["in_epmc"] = rec.get("inEPMC")
    out["title"] = (rec.get("title") or "")[:200]
    out["journal"] = ((rec.get("journalInfo") or {}).get("journal") or {}).get("title")
    return out


def candidate_urls(pmcid: str, oa: dict, pdf_url: str | None) -> list[tuple[str, str]]:
    """(route_name, url) in the order the docstring's ladder describes."""
    urls: list[tuple[str, str]] = []
    if oa.get("tgz"):
        urls.append(("oa_tgz_ftp", oa["tgz"]))
        urls.append(("oa_tgz_https", oa["tgz"].replace("ftp://ftp.ncbi.nlm.nih.gov/",
                                                       "https://ftp.ncbi.nlm.nih.gov/")))
    if oa.get("pdf"):
        urls.append(("oa_pdf_ftp", oa["pdf"]))
        urls.append(("oa_pdf_https", oa["pdf"].replace("ftp://ftp.ncbi.nlm.nih.gov/",
                                                       "https://ftp.ncbi.nlm.nih.gov/")))
    urls.append(("europepmc_pdf_render", f"https://europepmc.org/articles/{pmcid}?pdf=render"))
    if pdf_url:
        urls.append(("caller_pdf_url", pdf_url))
    return urls


def _looks_like(kind: str, ctype: str, body: bytes) -> bool:
    """Classify by MAGIC BYTES, never by the extension in the URL.

    ⛔ On 2026-08-12 `pmc.ncbi.nlm.nih.gov` answered a request for a `.jpg` with HTTP 200 and a
    reCAPTCHA page. A check keyed on the URL would have saved an HTML interstitial under a figure
    filename and reported success.
    """
    if kind == "pdf":
        return body[:5] == b"%PDF-"
    if kind == "tgz":
        return body[:2] == b"\x1f\x8b"
    return False


def harvest_tgz(body: bytes, dest: str, source_id: str) -> list[dict]:
    """Unpack an OA package and keep its image members at original resolution."""
    kept = []
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as tf:
        for member in tf.getmembers():
            if not member.isfile():
                continue
            low = member.name.lower()
            if not low.endswith(IMG_EXT):
                continue
            data = tf.extractfile(member).read()
            name = f"{source_id}__{os.path.basename(member.name)}"
            with open(os.path.join(dest, name), "wb") as fh:
                fh.write(data)
            kept.append({"file": name, "bytes": len(data), "member": member.name})
    return kept


def harvest_pdf(body: bytes, dest: str, source_id: str) -> dict:
    """Rasterise every page, and record which pages name a survival figure in their text.

    ⚠ EVERY page is rendered, and the caption scan only LABELS them. Selecting pages by caption
    text would silently drop a figure whose caption sits on the facing page, which is exactly how
    a two-column journal typesets a full-width figure.
    """
    pdf_path = os.path.join(dest, f"{source_id}.pdf")
    with open(pdf_path, "wb") as fh:
        fh.write(body)
    info = {"pdf": os.path.basename(pdf_path), "pdf_bytes": len(body), "pages": [],
            "poppler": shutil.which("pdftoppm") is not None,
            "rasterised": RASTERISE}
    if not RASTERISE:
        info["note"] = ("PDF published without page rasters (KM_RASTERISE=0). Re-render the page "
                        "you need locally: pdftoppm -r 600 -f <page> -l <page> -png <pdf> <out>.")
        return info
    if not info["poppler"]:
        info["⛔"] = "poppler-utils absent: the PDF was saved but no page was rasterised."
        return info
    prefix = os.path.join(dest, f"{source_id}_page")
    subprocess.run(["pdftoppm", "-r", str(DPI), "-png", pdf_path, prefix],
                   check=False, capture_output=True)
    text_by_page = {}
    if shutil.which("pdftotext"):
        for page in range(1, 60):
            res = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), pdf_path, "-"],
                                 check=False, capture_output=True)
            if res.returncode != 0 or not res.stdout.strip():
                if page > 3:
                    break
                continue
            text_by_page[page] = res.stdout.decode("utf-8", "replace")
    surv = re.compile(r"(kaplan|survival|progression[- ]free|recurrence[- ]free|at risk)", re.I)
    for name in sorted(os.listdir(dest)):
        m = re.match(rf"{re.escape(source_id)}_page-?(\d+)\.png$", name)
        if not m:
            continue
        page = int(m.group(1))
        txt = text_by_page.get(page, "")
        info["pages"].append({
            "file": name, "page": page,
            "bytes": os.path.getsize(os.path.join(dest, name)),
            "mentions_survival_terms": bool(surv.search(txt)),
            "text_head": txt[:300].replace("\n", " ")})
    return info


def main() -> int:
    targets = json.loads(os.environ["KM_TARGETS_JSON"]) if os.environ.get("KM_TARGETS_JSON") \
        else TARGETS
    dest = os.path.join(OUT_DIR)
    os.makedirs(dest, exist_ok=True)
    manifest = {
        "_what": "Figure graphics for the candidate EMC Kaplan-Meier series, with the full route "
                 "ladder tried for each and every outcome recorded.",
        "_not_medical_advice": "Nothing here is medical advice, and nothing here asserts efficacy, "
                               "safety or clinical readiness.",
        "_reading": "A retrieved figure is NOT an admissible curve. Admissibility is decided by "
                    "looking at the graphic for a numbers-at-risk row, which this script does not do.",
        "targets": [],
    }
    total = 0
    for tgt in targets:
        sid = tgt["source_id"]
        pmcid = tgt.get("pmcid")
        rec = {"source_id": sid, "pmcid": pmcid, "routes": [], "assets": None, "route_used": None}
        if not pmcid and tgt.get("pmid"):
            resolved = resolve_pmcid(str(tgt["pmid"]))
            rec["pmid"] = tgt["pmid"]
            rec["pmid_resolution"] = resolved
            pmcid = rec["pmcid"] = resolved.get("pmcid")
            print(f"{sid:32s} pmid={tgt['pmid']} -> pmcid={pmcid} "
                  f"open_access={resolved.get('is_open_access')}")
        if not pmcid:
            rec["⛔"] = ("no PMC identifier: this candidate has no open route at $0. That is a "
                        "reachability statement, not a statement about the paper.")
            manifest["targets"].append(rec)
            continue
        oa = oa_records(pmcid)
        rec["oa_service"] = {k: v for k, v in oa.items() if k != "raw"}
        rec["oa_service_raw"] = oa["raw"]
        for route, url in candidate_urls(pmcid, oa, tgt.get("pdf_url")):
            if total >= MAX_BYTES:
                rec["routes"].append({"route": route, "url": url, "skipped": "byte cap reached"})
                continue
            code, ctype, body = _get(url)
            entry = {"route": route, "url": url, "http": code, "content_type": ctype,
                     "bytes": len(body)}
            if _looks_like("tgz", ctype, body):
                entry["kind"] = "tgz"
                try:
                    kept = harvest_tgz(body, dest, sid)
                    entry["images_extracted"] = len(kept)
                    rec["assets"] = {"kind": "tgz_images", "images": kept}
                    rec["route_used"] = route
                    total += sum(k["bytes"] for k in kept)
                except Exception as exc:  # noqa: BLE001
                    entry["error"] = f"tar open failed: {type(exc).__name__}: {exc}"
            elif _looks_like("pdf", ctype, body):
                entry["kind"] = "pdf"
                rec["assets"] = harvest_pdf(body, dest, sid)
                rec["route_used"] = route
                total += rec["assets"].get("pdf_bytes", 0) + sum(
                    p["bytes"] for p in rec["assets"].get("pages", []))
            else:
                entry["kind"] = "not-a-figure-source"
                entry["head"] = body[:180].decode("utf-8", "replace")
            rec["routes"].append(entry)
            if rec["route_used"]:
                break
        if not rec["route_used"]:
            rec["⛔"] = ("no route returned a figure source. This is a reachability finding about "
                        "THIS run, not a statement that the paper prints no curve.")
        manifest["targets"].append(rec)
        print(f"{sid:32s} {pmcid:14s} route={rec['route_used']}")
    manifest["_totals"] = {
        "targets": len(targets),
        "with_assets": sum(1 for t in manifest["targets"] if t["route_used"]),
        "published_bytes": total,
        "byte_cap": MAX_BYTES,
    }
    with open(os.path.join(dest, "_km_figure_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    print(json.dumps(manifest["_totals"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
