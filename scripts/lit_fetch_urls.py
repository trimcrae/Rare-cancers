#!/usr/bin/env python3
"""Fetch a list of literature URLs from a GitHub-hosted runner (unrestricted egress)
and dump readable text into .cache/literature/ for the publish step.

The dev sandbox egress allowlist only permits github.com, so verbatim-quote
verification of journal/preprint pages has to happen out here. Pure stdlib except
for an optional pypdf import (installed by the workflow) used for PDF targets.
"""
import html
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request

OUT = os.path.join(".cache", "literature")

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

# name -> url. Name becomes the output filename.
TARGETS = {
    # 1. LOMAP origin
    "lomap_escholarship_pdf": "https://escholarship.org/content/qt4ss798kt/qt4ss798kt_noSplash_fa4f02c1a3fd390aee989bdb9f173170.pdf",
    "lomap_springer": "https://link.springer.com/article/10.1007/s10822-013-9678-y",
    "lomap_pmc": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3808540/",

    # 1b. FEP+ / Schrodinger cycle closure
    "wang2015_jacs_landing": "https://pubs.acs.org/doi/10.1021/ja512751q",
    "schrodinger_patent_cycleclosure": "https://patents.google.com/patent/WO2014151310A2/en",
    "schrodinger_patent_us": "https://patents.google.com/patent/US20160055304A1/en",

    # 2/3. precision vs accuracy, hysteresis limitations
    "commschem_maximal_accuracy": "https://www.nature.com/articles/s42004-023-01019-9",
    "scirep_fep_protocol": "https://www.nature.com/articles/s41598-019-53133-1",

    # 4. best-practices documents (the crux: replicates vs cycle closure)
    "livecoms_alchemical_bp": "https://livecomsjournal.org/index.php/livecoms/article/view/v2i1e18378",
    "livecoms_alchemical_bp_pdf": "https://livecomsjournal.org/index.php/livecoms/article/download/v2i1e18378/pdf",
    "mey_bp_arxiv": "https://arxiv.org/abs/2008.03067",
    "mey_bp_arxiv_pdf": "https://arxiv.org/pdf/2008.03067v3",
    "hahn_benchmarks_arxiv": "https://arxiv.org/abs/2105.06222",
    "hahn_benchmarks_arxiv_pdf": "https://arxiv.org/pdf/2105.06222v4",
    "hahn_benchmarks_livecoms": "https://livecomsjournal.org/index.php/livecoms/article/view/v4i1e1497",

    # 4b. OpenFE / cinnabar
    "cinnabar_docs": "https://cinnabar.readthedocs.io/en/latest/",
    "cinnabar_api": "https://cinnabar.readthedocs.io/en/latest/api.html",
    "openfe_docs_analysis": "https://docs.openfree.energy/en/stable/guide/rbfe/index.html",

    # 5. DiffNet / maximum likelihood network estimation
    "diffnet_arxiv": "https://arxiv.org/abs/1906.08599",
    "diffnet_arxiv_pdf": "https://arxiv.org/pdf/1906.08599v2",
    "diffnet_jcim": "https://pubs.acs.org/doi/10.1021/acs.jcim.9b00528",
    "diffnet_jctc_2021": "https://pubs.acs.org/doi/10.1021/acs.jctc.1c00703",

    # 6. replicates / ensemble sampling / reproducibility (the counter-position)
    "coveney_ties_jctc2017": "https://pubs.acs.org/doi/10.1021/acs.jctc.6b00979",
    "loeffler_reproducibility": "https://pubs.acs.org/doi/10.1021/acs.jctc.8b00544",
    "weighted_cycle_closure": "https://pubs.acs.org/doi/10.1021/acs.jcim.2c01076",
}


def strip_html(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?is)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?is)</(p|div|h[1-6]|li|tr|section)>", "\n", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    raw = re.sub(r"[ \t\xa0]+", " ", raw)
    raw = re.sub(r"\n\s*\n\s*\n+", "\n\n", raw)
    return raw.strip()


def pdf_to_text(data: bytes) -> str:
    try:
        import pypdf
    except ImportError:
        return "[pypdf not available]"
    try:
        reader = pypdf.PdfReader(io.BytesIO(data))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:  # noqa: BLE001
        return f"[pdf parse failed: {exc}]"


def fetch(name: str, url: str) -> dict:
    rec = {"name": name, "url": url}
    # Request() is built INSIDE the try: a value that is not a URL raises ValueError
    # from the constructor, and building it outside let ONE bad entry abort the whole
    # corpus run (measured 2026-08-03: a "_readme" prose key in a targets file killed
    # a 14-target fetch before a single request went out). One bad target is now one
    # bad row in the manifest.
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = resp.read()
            rec["status"] = resp.status
            rec["final_url"] = resp.geturl()
            ctype = resp.headers.get("Content-Type", "")
            rec["content_type"] = ctype
    except urllib.error.HTTPError as exc:
        rec["status"] = exc.code
        rec["error"] = f"HTTPError {exc.code}"
        try:
            data = exc.read()
            ctype = exc.headers.get("Content-Type", "")
        except Exception:  # noqa: BLE001
            return rec
    except Exception as exc:  # noqa: BLE001
        rec["status"] = None
        rec["error"] = repr(exc)
        return rec

    if "pdf" in ctype.lower() or data[:5] == b"%PDF-":
        text = pdf_to_text(data)
    else:
        text = strip_html(data.decode("utf-8", errors="replace"))

    rec["chars"] = len(text)
    path = os.path.join(OUT, f"{name}.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"SOURCE URL: {url}\nFINAL URL: {rec.get('final_url')}\n"
                 f"HTTP: {rec.get('status')}\nCONTENT-TYPE: {ctype}\n"
                 + "=" * 70 + "\n" + text)
    return rec


def resolve_targets() -> dict:
    """TARGETS, optionally REPLACED by a JSON {name: url} map named in LIT_TARGETS_FILE.

    Additive by design: the built-in TARGETS list is a fixed corpus tied to specific verification
    tasks, so a new corpus gets its own file rather than editing that dict (which would silently
    change what every future run fetches). LIT_TARGETS_MODE=extend appends instead of replacing.
    """
    path = os.environ.get("LIT_TARGETS_FILE", "").strip()
    if not path:
        return TARGETS
    with open(path, "r", encoding="utf-8") as fh:
        extra = json.load(fh)
    if not isinstance(extra, dict) or not all(isinstance(v, str) for v in extra.values()):
        raise SystemExit(f"{path}: expected a flat JSON object of name -> url")
    # Underscore-prefixed keys are documentation, not targets. Corpus files in this repo
    # carry a "_readme" line saying what the corpus is for and under what constraints it
    # was fetched; that is worth keeping, so the convention is honoured rather than banned.
    extra = {k: v for k, v in extra.items() if not k.startswith("_")}
    if os.environ.get("LIT_TARGETS_MODE", "replace").strip() == "extend":
        return {**TARGETS, **extra}
    return extra


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for name, url in resolve_targets().items():
        rec = fetch(name, url)
        manifest.append(rec)
        print(f"{rec.get('status')}\t{rec.get('chars', 0)}\t{name}\t{url}"
              f"\t{rec.get('error', '')}", flush=True)
    with open(os.path.join(OUT, "_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
