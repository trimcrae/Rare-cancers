#!/usr/bin/env python3
"""Harvest the evidence for "what is the field standard for a congeneric RBFE screening ladder".

Runs on a GitHub Actions runner (unrestricted internet); the dev sandbox's egress proxy 403s
publisher/docs domains, so nothing here may be attempted locally and declared unavailable.

Two jobs, both pure stdlib:

1. **Citation verification via Crossref.**  Every DOI this note might cite is resolved against
   ``api.crossref.org``.  Crossref returns the registrant's own metadata, so a DOI that 404s is a
   DOI that does not exist -- which is exactly the fabrication mode the repo's golden rule forbids.
   The harvest records title/authors/year/container/volume/page for each hit and ``MISS`` for each
   miss; the methods note may only cite what came back ``HIT``.

2. **Full-text / documentation capture.**  Fetches the open-access sources (arXiv, LiveCoMS,
   ChemRxiv, OpenFE docs, GitHub raw source) so the claims rest on quotable text rather than on a
   search-result snippet, and greps each one for the replicate/uncertainty vocabulary.

Output: one directory of raw captures plus ``harvest-summary.json``.  Nothing is interpreted here --
interpretation belongs in the methods note, against text a human can re-read.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "Rare-cancers-methods-harvest/1.0 (mailto:trimcrae@gmail.com)"
OUT_DIR = os.environ.get("HARVEST_OUT", "research/modalities/_replicate_standard")

# ---------------------------------------------------------------------------
# 1. DOIs to verify.  These are CANDIDATES -- several are from recollection and are expected to
#    miss.  A miss is a result, not a failure: it means the note must not cite that DOI.
# ---------------------------------------------------------------------------
CANDIDATE_DOIS = {
    # community best practice
    "mey2020_bestpractices": "10.33011/livecoms.2.1.18378",
    "hahn2022_benchmarks": "10.33011/livecoms.4.1.1497",
    # the "single run understates the error" argument
    "coveney2016_pccp": "10.1039/C6CP02349E",
    "bhati2017_ties": "10.1021/acs.jctc.6b00979",
    "bhati2022_largescale": "10.1021/acs.jctc.1c00669",
    "loeffler2018_repro": "10.1021/acs.jctc.8b00544",
    # benchmark campaigns
    "wang2015_fepplus": "10.1021/ja512751q",
    "schindler2020_merck": "10.1021/acs.jcim.0c00900",
    "gapsys2020_chemsci": "10.1039/C9SC03754C",
    "ross2023_maximal": "10.1038/s42004-023-01019-9",
    "kuhn2020_bi": "10.1021/acs.jcim.0c00165",
    "cournia2017_rbfe": "10.1021/acs.jcim.7b00564",
    "cournia2020_rigorous": "10.1021/acs.jcim.0c00116",
    # network / cycle-closure machinery
    "liu2013_lomap": "10.1007/s10822-013-9678-y",
    "xu2019_diffnet": "10.1021/acs.jcim.9b00528",
    "wang2013_fep_rest": "10.1021/ct300911a",
    # openfe / open-source stack
    "gowers2023_openfe": "10.1021/acs.jcim.3c01438",
    "hahn2024_openfe": "10.26434/chemrxiv-2024-6h4vd",
}

# ---------------------------------------------------------------------------
# 2. Crossref free-text searches -- how we find the REAL DOI for a paper whose DOI we do not know
#    (or whose recalled DOI missed above).  Recording the top hits makes the search auditable.
# ---------------------------------------------------------------------------
CROSSREF_QUERIES = [
    "Best Practices for Alchemical Free Energy Calculations",
    "Best practices for constructing preparing and evaluating protein-ligand binding affinity benchmarks",
    "Accurate and Reliable Prediction of Relative Ligand Binding Potency modern free-energy calculation protocol force field",
    "Large-Scale Assessment of Binding Free Energy Calculations in Active Drug Discovery Projects",
    "Large scale relative protein ligand binding affinities using non-equilibrium alchemy",
    "maximal and current accuracy of rigorous protein-ligand binding free energy calculations",
    "Rapid Accurate Precise Reliable Relative Free Energy Prediction Ensemble Based Thermodynamic Integration",
    "Large Scale Study of Ligand-Protein Relative Binding Free Energy Calculations Actionable Predictions",
    "Reproducibility of Free Energy Calculations across Different Molecular Simulation Software Packages",
    "Lead optimization mapper automating free energy calculations for lead optimization",
    "Optimal Measurement Network of Pairwise Differences",
    "Relative Binding Free Energy Calculations in Drug Discovery Recent Advances and Practical Considerations",
    "open free energy consortium industry benchmark relative binding free energy open source",
    "cycle closure correction free energy perturbation map hysteresis",
    "how many repeats independent replicas alchemical binding free energy uncertainty",
]

# ---------------------------------------------------------------------------
# 3. Full text / docs to capture.
# ---------------------------------------------------------------------------
FETCH_URLS = {
    # --- OpenFE documentation (the most directly binding source: we run OpenFE) ---
    "openfe_doc_rhtp": "https://docs.openfree.energy/en/stable/guide/protocols/relativehybridtopology.html",
    "openfe_doc_rhtp_latest": "https://docs.openfree.energy/en/latest/guide/protocols/relativehybridtopology.html",
    "openfe_doc_defining_protocols": "https://docs.openfree.energy/en/stable/guide/setup/defining_protocols.html",
    "openfe_doc_choose_protocol": "https://docs.openfree.energy/en/stable/cookbook/choose_protocol.html",
    "openfe_doc_api_openmm_rfe": "https://docs.openfree.energy/en/stable/reference/api/openmm_rfe.html",
    "openfe_doc_rbfe_tutorial": "https://docs.openfree.energy/en/stable/tutorials/rbfe_python_tutorial.html",
    "openfe_doc_septop": "https://docs.openfree.energy/en/latest/guide/protocols/septop.html",
    "openfe_doc_absolutesolvation": "https://docs.openfree.energy/en/latest/guide/protocols/absolutesolvation.html",
    # --- OpenFE / cinnabar source of truth ---
    "openfe_src_equil_rfe_settings": "https://raw.githubusercontent.com/OpenFreeEnergy/openfe/main/openfe/protocols/openmm_rfe/equil_rfe_settings.py",
    "openfe_src_omm_settings": "https://raw.githubusercontent.com/OpenFreeEnergy/openfe/main/openfe/protocols/openmm_utils/omm_settings.py",
    "openfe_src_equil_rfe_method": "https://raw.githubusercontent.com/OpenFreeEnergy/openfe/main/openfe/protocols/openmm_rfe/equil_rfe_method.py",
    "gufe_src_settings": "https://raw.githubusercontent.com/OpenFreeEnergy/gufe/main/gufe/settings/models.py",
    "cinnabar_readme": "https://raw.githubusercontent.com/OpenFreeEnergy/cinnabar/main/README.md",
    "cinnabar_stats": "https://raw.githubusercontent.com/OpenFreeEnergy/cinnabar/main/cinnabar/stats.py",
    "cinnabar_femap": "https://raw.githubusercontent.com/OpenFreeEnergy/cinnabar/main/cinnabar/femap.py",
    "openfe_benchmarks_readme": "https://raw.githubusercontent.com/OpenFreeEnergy/openfe-benchmarks/main/README.md",
    "openfe_gh_api_rfe_dir": "https://api.github.com/repos/OpenFreeEnergy/openfe/contents/openfe/protocols/openmm_rfe",
    # --- open-access full text ---
    "mey2020_arxiv_abs": "https://arxiv.org/abs/2008.03067",
    "mey2020_livecoms": "https://livecomsjournal.org/index.php/livecoms/article/view/v2i1e18378",
    "hahn2022_livecoms_search": "https://livecomsjournal.org/index.php/livecoms/search/search?query=binding+affinity+benchmarks",
    "gapsys2020_rsc": "https://pubs.rsc.org/en/content/articlehtml/2020/sc/c9sc03754c",
    "ross2023_nature": "https://www.nature.com/articles/s42004-023-01019-9",
    "coveney2016_rsc": "https://pubs.rsc.org/en/content/articlehtml/2016/cp/c6cp02349e",
}

KEYWORDS = [
    "protocol_repeats", "repeats", "replicate", "replica", "independent run",
    "standard error", "standard deviation", "uncertainty", "MBAR", "bootstrap",
    "cycle closure", "hysteresis", "convergence", "n_repeats", "variance",
]


def _get(url: str, timeout: int = 60) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            enc = r.headers.get_content_charset() or "utf-8"
            return r.status, raw.decode(enc, errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, f"<HTTPError {e.code} {e.reason}>"
    except Exception as e:  # noqa: BLE001
        return -1, f"<ERROR {type(e).__name__}: {e}>"


def _strip_html(text: str) -> str:
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = (text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                .replace("&nbsp;", " ").replace("&quot;", '"').replace("&#39;", "'"))
    return re.sub(r"[ \t\r\f\v]+", " ", text)


def _fmt_crossref(msg: dict) -> dict:
    authors = []
    for a in msg.get("author", []) or []:
        fam, given = a.get("family"), a.get("given")
        authors.append(f"{fam}, {given}" if fam and given else (fam or given or a.get("name") or "?"))
    date = (msg.get("issued", {}).get("date-parts") or [[None]])[0]
    return {
        "doi": msg.get("DOI"),
        "title": (msg.get("title") or [None])[0],
        "authors": authors,
        "n_authors": len(authors),
        "year": date[0] if date else None,
        "container": (msg.get("container-title") or [None])[0],
        "volume": msg.get("volume"),
        "issue": msg.get("issue"),
        "page": msg.get("page"),
        "type": msg.get("type"),
        "publisher": msg.get("publisher"),
        "url": msg.get("URL"),
    }


def verify_dois() -> dict:
    out = {}
    for key, doi in CANDIDATE_DOIS.items():
        url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
        code, body = _get(url)
        if code == 200:
            try:
                out[key] = {"status": "HIT", **_fmt_crossref(json.loads(body)["message"])}
            except Exception as e:  # noqa: BLE001
                out[key] = {"status": "PARSE_FAIL", "doi": doi, "error": str(e)}
        else:
            out[key] = {"status": "MISS", "doi": doi, "http": code,
                        "note": "DOI did not resolve at Crossref -- DO NOT CITE"}
        print(f"[doi] {key:32s} {out[key]['status']:10s} {doi}", flush=True)
        time.sleep(0.4)
    return out


def search_crossref() -> dict:
    out = {}
    for q in CROSSREF_QUERIES:
        url = ("https://api.crossref.org/works?rows=5&select=DOI,title,author,issued,"
               "container-title,volume,issue,page,type,publisher,URL&query.bibliographic="
               + urllib.parse.quote(q))
        code, body = _get(url)
        if code == 200:
            try:
                items = json.loads(body)["message"]["items"]
                out[q] = [_fmt_crossref(m) for m in items]
            except Exception as e:  # noqa: BLE001
                out[q] = [{"status": "PARSE_FAIL", "error": str(e)}]
        else:
            out[q] = [{"status": "HTTP_FAIL", "http": code}]
        top = out[q][0].get("title") if out[q] else None
        print(f"[search] {q[:60]:60s} -> {str(top)[:70]}", flush=True)
        time.sleep(0.4)
    return out


def fetch_texts() -> dict:
    raw_dir = os.path.join(OUT_DIR, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    out = {}
    for key, url in FETCH_URLS.items():
        code, body = _get(url)
        ok = code == 200
        text = body if url.endswith((".py", ".md")) or "api.github.com" in url else _strip_html(body)
        if ok:
            with open(os.path.join(raw_dir, f"{key}.txt"), "w", encoding="utf-8") as fh:
                fh.write(f"# SOURCE: {url}\n# HTTP: {code}\n\n{text}")
        hits = {}
        if ok:
            low = text.lower()
            for kw in KEYWORDS:
                n = low.count(kw.lower())
                if n:
                    hits[kw] = n
        out[key] = {"url": url, "http": code, "ok": ok, "chars": len(text) if ok else 0,
                    "keyword_hits": hits}
        print(f"[fetch] {key:34s} HTTP {code:4d} {len(text) if ok else 0:8d} chars", flush=True)
        time.sleep(0.3)
    return out


def grep_context() -> dict:
    """Pull the sentences around each replicate/uncertainty keyword so the note can quote them."""
    raw_dir = os.path.join(OUT_DIR, "raw")
    out = {}
    if not os.path.isdir(raw_dir):
        return out
    pat = re.compile(r"(protocol_repeats|n_repeats|independent repeat|repeats|replicate|cycle closure|"
                     r"hysteresis|standard error|standard deviation)", re.I)
    for fn in sorted(os.listdir(raw_dir)):
        with open(os.path.join(raw_dir, fn), encoding="utf-8") as fh:
            text = fh.read()
        snippets = []
        for m in pat.finditer(text):
            a, b = max(0, m.start() - 400), min(len(text), m.end() + 400)
            snippets.append(re.sub(r"\s+", " ", text[a:b]).strip())
            if len(snippets) >= 40:
                break
        if snippets:
            out[fn] = snippets
    with open(os.path.join(OUT_DIR, "keyword-context.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    return {k: len(v) for k, v in out.items()}


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    summary = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "purpose": ("Evidence base for the congeneric-RBFE replicate/uncertainty field-standard note. "
                    "Crossref HIT/MISS is the fabrication guard: cite only HITs."),
        "doi_verification": verify_dois(),
        "crossref_search": search_crossref(),
        "fetches": fetch_texts(),
    }
    summary["keyword_context_counts"] = grep_context()
    with open(os.path.join(OUT_DIR, "harvest-summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)

    hits = sum(1 for v in summary["doi_verification"].values() if v["status"] == "HIT")
    miss = [k for k, v in summary["doi_verification"].items() if v["status"] != "HIT"]
    okf = sum(1 for v in summary["fetches"].values() if v["ok"])
    print(f"\n[summary] DOIs verified {hits}/{len(CANDIDATE_DOIS)}; unresolved (DO NOT CITE): {miss}")
    print(f"[summary] full-text/doc fetches OK {okf}/{len(FETCH_URLS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
