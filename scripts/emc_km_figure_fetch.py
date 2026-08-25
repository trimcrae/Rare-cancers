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
# ⭐ THE LAST RUNG, AND IT IS NOT A PAYWALL ROUTE. Three of the nine remaining candidate series are
# FREE TO READ -- Unpaywall grades seer270_2022 gold and huang2023 and japan2003 bronze -- and all
# three answer plain urllib with HTTP 403. That is publisher bot protection keyed on TLS fingerprint
# and header order, which the escape-hatch skill records as clearing under a real headless Chromium
# and under nothing else: no User-Agent string and no amount of retrying touches it.
# ⛔ IT IS ONLY EVER POINTED AT A URL UNPAYWALL HAS ALREADY GRADED AS OPEN ACCESS. A subscription
# article a browser cannot read without a login stays unreachable, and recording it as unreachable
# is the finding.
USE_BROWSER = os.environ.get("KM_BROWSER", "0") == "1"

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

REGISTRY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "research", "data", "emc-clinical-registry.json")


def registry_ids(source_id: str) -> dict:
    """The DOI, PMID and PMC id the registry holds for a citation key.

    ⛔⛔ THIS EXISTS BECAUSE A CALLER-TYPED IDENTIFIER IS AN IDENTIFIER FROM RECOLLECTION, AND ON
    2026-08-25 THREE OF NINE WERE WRONG. A dispatch was composed by reading DOIs off a truncated
    terminal dump: `10.1097/coc.0000000000000992` for a registry value ending 0988,
    `10.1016/j.anndiagpath.2016.04.007` for one ending .004, and
    `10.1016/S1470-2045(19)30276-7` for `(19)30319-5`. CLAUDE.md §7 says never write an identifier
    from recollection; a rule that has to be remembered at the moment of composing a JSON blob is
    not a guard, so the guard is here instead.

    ⚠ AND A WRONG DOI DOES NOT FAIL LOUDLY. Unpaywall answers a nonexistent DOI with "no free copy",
    which is indistinguishable from the true answer for a genuinely paywalled paper — so the error
    would have been recorded as a reachability FINDING about three real papers.

    A caller may still pass an identifier explicitly; if it CONTRADICTS the registry the target is
    refused rather than resolved one way or the other.
    """
    out = {"doi": None, "pmid": None, "pmcid": None, "found": False}
    try:
        with open(REGISTRY, encoding="utf-8") as fh:
            doc = json.load(fh)
    except Exception as exc:  # noqa: BLE001
        out["error"] = f"registry unreadable: {type(exc).__name__}: {exc}"
        return out
    cits = doc.get("citations") or (doc.get("registry") or {}).get("citations") or {}
    rec = cits.get(source_id)
    if not rec:
        out["error"] = f"no registry citation for source_id {source_id!r}"
        return out
    out["found"] = True
    for k in ("doi", "pmid", "pmcid"):
        if rec.get(k):
            out[k] = str(rec[k])
    return out


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


# ⛔ AN EMAIL IS REQUIRED BY UNPAYWALL AND IT MUST NOT BE A PERSON'S. The repository's own bot
# address identifies the caller for rate-limiting, which is all the API asks for, and sends nobody's
# personal address to a third-party service.
UNPAYWALL_CONTACT = "41898282+github-actions[bot]@users.noreply.github.com"


def unpaywall(doi: str) -> dict:
    """Is there a FREE copy of this DOI anywhere, and where?

    ⭐ WHY THIS RUNG EXISTS. Europe PMC answering `isOpenAccess: N` means "not open access HERE",
    which is a fact about one index. Turning that into "unreachable at $0" is the inference this
    program keeps making and should not: a paper can be free on the publisher's own site, in an
    institutional repository, or as an author manuscript, and none of those is a PMC record.
    Unpaywall answers the question that was actually being asked.
    """
    url = f"https://api.unpaywall.org/v2/{doi}?email={UNPAYWALL_CONTACT}"
    code, _ctype, body = _get(url)
    out = {"query_url": url.split("?")[0], "http": code, "is_oa": None,
           "oa_status": None, "best_url_for_pdf": None, "best_host_type": None, "licence": None}
    if code != 200:
        out["error"] = f"HTTP {code}"
        return out
    try:
        doc = json.loads(body.decode("utf-8", "replace"))
    except Exception as exc:  # noqa: BLE001
        out["error"] = f"unparseable: {type(exc).__name__}: {exc}"
        return out
    out["is_oa"] = doc.get("is_oa")
    out["oa_status"] = doc.get("oa_status")
    best = doc.get("best_oa_location") or {}
    out["best_url_for_pdf"] = best.get("url_for_pdf") or best.get("url")
    out["best_url"] = best.get("url")
    out["best_host_type"] = best.get("host_type")
    out["licence"] = best.get("license")
    out["n_oa_locations"] = len(doc.get("oa_locations") or [])
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
    if pmcid:
        urls.append(("europepmc_pdf_render", f"https://europepmc.org/articles/{pmcid}?pdf=render"))
    if pdf_url:
        urls.append(("caller_pdf_url", pdf_url))
    return urls


def browser_get(url: str, referer: str | None = None) -> tuple[int, str, bytes]:
    """Fetch through a real Chromium, so the request carries a browser's TLS fingerprint.

    The article landing page is visited FIRST when one is known, because several publishers gate the
    PDF on a cookie the landing page sets; the PDF is then requested through the same browser
    context so it carries that cookie and that fingerprint.
    """
    try:
        from playwright.sync_api import sync_playwright  # noqa: PLC0415 -- optional by design
    except Exception as exc:  # noqa: BLE001
        return 0, f"playwright unavailable: {type(exc).__name__}: {exc}", b""
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
            ctx = browser.new_context(
                user_agent=("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like "
                            "Gecko) Chrome/124.0.0.0 Safari/537.36"),
                accept_downloads=True)
            if referer:
                try:
                    page = ctx.new_page()
                    page.goto(referer, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(1500)
                    page.close()
                except Exception:  # noqa: BLE001 -- the landing page is a courtesy, not the fetch
                    pass
            resp = ctx.request.get(url, timeout=90000)
            body = resp.body()
            code = resp.status
            ctype = resp.headers.get("content-type", "")
            browser.close()
            return code, ctype, body
    except Exception as exc:  # noqa: BLE001
        return 0, f"{type(exc).__name__}: {exc}"[:300], b""


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


def run_target(tgt: dict, dest: str, budget_left: int) -> tuple[dict, int]:
    """Resolve, fetch and harvest ONE candidate. Returns (record, bytes published)."""
    sid = tgt["source_id"]
    reg = registry_ids(sid)
    conflicts = [k for k in ("doi", "pmid", "pmcid")
                 if tgt.get(k) and reg.get(k) and str(tgt[k]) != reg[k]]
    if conflicts:
        print(f"{sid:32s} REFUSED: identifier conflicts with the registry ({conflicts})")
        return {
            "source_id": sid, "routes": [], "assets": None, "route_used": None,
            "⛔_refused": ("caller-supplied identifier contradicts the registry: "
                          + "; ".join(f"{k}: caller {tgt[k]!r} vs registry {reg[k]!r}"
                                      for k in conflicts)
                          + ". Refused rather than resolved -- one of the two is wrong and this "
                            "script cannot tell which."),
            "registry_ids": reg}, 0
    if reg.get("found"):
        for k in ("doi", "pmid", "pmcid"):
            if reg.get(k) and not tgt.get(k):
                tgt = dict(tgt, **{k: reg[k]})

    pmcid = tgt.get("pmcid")
    rec = {"source_id": sid, "pmcid": pmcid, "routes": [], "assets": None, "route_used": None,
           "registry_ids": reg,
           "identifiers_used": {k: tgt.get(k) for k in ("doi", "pmid", "pmcid")},
           "identifier_source": "registry" if reg.get("found") else "caller"}

    if not pmcid and tgt.get("pmid"):
        resolved = resolve_pmcid(str(tgt["pmid"]))
        rec["pmid_resolution"] = resolved
        pmcid = rec["pmcid"] = resolved.get("pmcid")
        print(f"{sid:32s} pmid={tgt['pmid']} -> pmcid={pmcid} "
              f"open_access={resolved.get('is_open_access')}")
    if not pmcid and tgt.get("doi"):
        # ⭐ NOT IN PMC IS NOT THE SAME AS NOT FREE. Ask the question that was meant.
        up = unpaywall(tgt["doi"])
        rec["unpaywall"] = up
        print(f"{sid:32s} doi={tgt['doi']} -> is_oa={up.get('is_oa')} "
              f"status={up.get('oa_status')} host={up.get('best_host_type')}")
        if up.get("best_url_for_pdf"):
            tgt = dict(tgt, pdf_url=up["best_url_for_pdf"],
                       landing_url=up.get("best_url") or None)
    if not pmcid and not tgt.get("pdf_url"):
        rec["⛔"] = ("no PMC identifier and no free copy located: this candidate has no open route "
                    "at $0. That is a reachability statement, not a statement about the paper.")
        return rec, 0

    oa = oa_records(pmcid) if pmcid else {"lookup_url": None, "skipped": "no PMC id"}
    rec["oa_service"] = {k: v for k, v in oa.items() if k != "raw"}
    # ⚠ `oa` is a STUB when there is no PMC id, so every read of it must tolerate a missing key.
    rec["oa_service_raw"] = oa.get("raw")

    spent = 0
    for route, url in candidate_urls(pmcid or "", oa, tgt.get("pdf_url")):
        if spent >= budget_left:
            rec["routes"].append({"route": route, "url": url, "skipped": "byte cap reached"})
            continue
        code, ctype, body = _get(url)
        entry = {"route": route, "url": url, "http": code, "content_type": ctype,
                 "bytes": len(body)}
        if (USE_BROWSER and route == "caller_pdf_url" and not _looks_like("pdf", ctype, body)):
            # the plain fetch was refused; retry the SAME url through a real browser
            b_code, b_ctype, b_body = browser_get(url, referer=tgt.get("landing_url"))
            entry["browser_retry"] = {"http": b_code, "content_type": b_ctype,
                                      "bytes": len(b_body)}
            if _looks_like("pdf", b_ctype, b_body):
                code, ctype, body = b_code, b_ctype, b_body
                entry["route"] = route = "caller_pdf_url_via_browser"
        if _looks_like("tgz", ctype, body):
            entry["kind"] = "tgz"
            try:
                kept = harvest_tgz(body, dest, sid)
                entry["images_extracted"] = len(kept)
                rec["assets"] = {"kind": "tgz_images", "images": kept}
                rec["route_used"] = route
                spent += sum(k["bytes"] for k in kept)
            except Exception as exc:  # noqa: BLE001
                entry["error"] = f"tar open failed: {type(exc).__name__}: {exc}"
        elif _looks_like("pdf", ctype, body):
            entry["kind"] = "pdf"
            rec["assets"] = harvest_pdf(body, dest, sid)
            rec["route_used"] = route
            spent += rec["assets"].get("pdf_bytes", 0) + sum(
                p["bytes"] for p in rec["assets"].get("pages", []))
        else:
            entry["kind"] = "not-a-figure-source"
            entry["head"] = body[:180].decode("utf-8", "replace")
        rec["routes"].append(entry)
        if rec["route_used"]:
            break
    if not rec["route_used"]:
        rec["⛔"] = ("no route returned a figure source. This is a reachability finding about THIS "
                    "run, not a statement that the paper prints no curve.")
    print(f"{sid:32s} {str(pmcid):14s} route={rec['route_used']}")
    return rec, spent


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
        # ⛔ ONE BAD TARGET MUST NOT DISCARD THE WHOLE RUN. Round 3 crashed on its first pmcid-less
        # row AFTER its Unpaywall lookup had already answered: the finding existed, was printed to
        # the log, and was thrown away because nothing caught the exception. That is the same lesson
        # the publish step records from the other direction -- never let one failure discard a
        # retrieval that already happened.
        try:
            rec, spent = run_target(tgt, dest, MAX_BYTES - total)
            total += spent
        except Exception as exc:  # noqa: BLE001
            rec = {"source_id": tgt.get("source_id"), "routes": [], "assets": None,
                   "route_used": None,
                   "⛔_crashed": f"{type(exc).__name__}: {exc}",
                   "⚠": "this target raised; the other targets in this run are unaffected"}
            print(f"{tgt.get('source_id')}: CRASHED {type(exc).__name__}: {exc}")
        manifest["targets"].append(rec)
    manifest["_totals"] = {
        "targets": len(targets),
        "with_assets": sum(1 for t in manifest["targets"] if t.get("route_used")),
        "crashed": sum(1 for t in manifest["targets"] if t.get("⛔_crashed")),
        "published_bytes": total,
        "byte_cap": MAX_BYTES,
    }
    with open(os.path.join(dest, "_km_figure_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    print(json.dumps(manifest["_totals"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
