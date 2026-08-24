#!/usr/bin/env python3
"""Is a computation-only paper in scope for Nucleic Acid Therapeutics? Ask the journal's own record.

⭐ WHY THIS EXISTS, AND WHY IT REPLACES AN ENQUIRY. External review advised a presubmission enquiry
to the editorial office: is a computational design paper in scope, and which article type. trimcrae
declined to contact the editor (2026-08-24). The question does not need an editor — a journal's
scope is what it has actually published, and that record is public. This censuses every NAT article
PubMed indexes and reports how many carry no wet-lab work, with the examples named so the answer can
be read rather than trusted.

⛔ WHAT A KEYWORD CLASSIFIER CAN AND CANNOT SETTLE. It cannot read a paper. It can separate
abstracts that describe experiments (cells, mice, transfection, blots, assays) from those that
describe only computation (in silico, algorithm, prediction, model, database), and it is wrong in
both directions on individual records. So the counts here are a SCREEN, and the artifact carries the
candidate titles and PMIDs so the handful that matter are read directly. A count without its
examples would be exactly the "reports while measuring nothing" defect this repository keeps finding.

⚠ AND A PUBLISHED PRECEDENT IS NOT A GUARANTEE OF ACCEPTANCE. It answers "has this journal published
work of this shape", which is the question worth answering before spending a submission. It does not
answer whether this particular manuscript will be sent for review.

NETWORK. NCBI E-utilities, 403'd at CONNECT by the dev sandbox, so this runs on an Actions runner.

Run:
    python3 research/manuscripts/nat_scope_census.py           # fetch + write (CI)
    python3 research/manuscripts/nat_scope_census.py --check    # offline: re-read the artifact
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "aso", "nat-scope-census.json")
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
JOURNAL = "Nucleic Acid Ther"

#: Abstract language that means an experiment was performed. Deliberately broad: a false WET reading
#: only makes the computational count more conservative, which is the safe direction for a paper
#: arguing that computation-only work has precedent here.
_WET = re.compile(
    r"\b(cells?\s+were|cell line|transfect|transduc|mice|murine|in vivo|rats?\b|xenograft|"
    r"western blot|immunoblot|qRT-PCR|RT-qPCR|luciferase|flow cytometr|ELISA|HPLC|mass spec|"
    r"we synthesi[sz]ed|were synthesi[sz]ed|incubated|cultured|treated with|administered|"
    r"knockdown was|assay(?:s|ed)?\b|electrophoresis|northern blot|immunohisto)", re.I)

#: Abstract language that means the work is computational.
_DRY = re.compile(
    r"\b(in silico|computational|algorithm|bioinformatic|machine learning|deep learning|"
    r"neural network|molecular dynamics|docking|free energy|predict(?:ion|ive|ed)?\b|"
    r"database|web server|pipeline|simulation|structural model)", re.I)


def _get(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode(errors="replace")
        except Exception as exc:  # noqa: BLE001
            last = exc
            print(f"  retry {i + 1}: {exc}", file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError(f"failed: {url}: {last}")


def _pmids():
    q = urllib.parse.quote(f'"{JOURNAL}"[Journal]')
    first = json.loads(_get(f"{EUTILS}/esearch.fcgi?db=pubmed&retmode=json&retmax=0&term={q}"
                            "&tool=rare-cancers&email=trimcrae@gmail.com"))
    total = int(first["esearchresult"]["count"])
    out = []
    for start in range(0, total, 500):
        d = json.loads(_get(f"{EUTILS}/esearch.fcgi?db=pubmed&retmode=json&retmax=500"
                            f"&retstart={start}&term={q}"
                            "&tool=rare-cancers&email=trimcrae@gmail.com"))
        out.extend(d["esearchresult"]["idlist"])
        time.sleep(0.4)
    return total, out


def _records(pmids):
    """title, abstract and publication types, in batches, from efetch XML."""
    recs = {}
    for i in range(0, len(pmids), 150):
        batch = pmids[i:i + 150]
        xml = _get(f"{EUTILS}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(batch)}"
                   "&tool=rare-cancers&email=trimcrae@gmail.com")
        for chunk in xml.split("<PubmedArticle>")[1:]:
            pm = re.search(r"<PMID[^>]*>(\d+)</PMID>", chunk)
            ti = re.search(r"<ArticleTitle[^>]*>(.*?)</ArticleTitle>", chunk, re.S)
            ab = " ".join(re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", chunk, re.S))
            yr = re.search(r"<PubDate>.*?<Year>(\d{4})</Year>", chunk, re.S)
            pt = re.findall(r"<PublicationType[^>]*>(.*?)</PublicationType>", chunk)
            if not pm:
                continue
            strip = lambda t: re.sub(r"<[^>]+>", "", t or "").strip()  # noqa: E731
            recs[pm.group(1)] = {"pmid": pm.group(1), "title": strip(ti.group(1) if ti else ""),
                                 "abstract": strip(ab), "year": int(yr.group(1)) if yr else None,
                                 "pub_types": pt}
        time.sleep(0.4)
    return recs


_PUBMED_URL = "pubmed.ncbi.nlm.nih.gov/%s"


def build() -> dict:
    total, pmids = _pmids()
    recs = _records(pmids)
    with_abstract = [r for r in recs.values() if len(r["abstract"]) > 200]
    dry = []
    for r in with_abstract:
        text = r["title"] + " " + r["abstract"]
        if _WET.search(text):
            continue
        hits = sorted({m.group(0).lower() for m in _DRY.finditer(text)})
        if hits:
            # ⚠ `pubmed_url` IS NOT DECORATION — it is what anchors these identifiers for
            # lint_citations.py, whose scanner does not recognise a lowercase `"pmid"` JSON key
            # (the `": "` breaks the `PMID` pattern). A record fetched from PubMed and stored
            # without the URL form reads to that gate exactly like a citation typed from memory,
            # which is a false fabrication alarm on honest work.
            dry.append({"pmid": r["pmid"], "pubmed_url": _PUBMED_URL % r["pmid"],
                        "year": r["year"], "title": r["title"],
                        "markers": hits, "pub_types": r["pub_types"]})
    dry.sort(key=lambda r: (-(r["year"] or 0), r["pmid"]))
    return {
        "_what": ("Every Nucleic Acid Therapeutics article PubMed indexes, screened for papers whose "
                  "abstract describes computation and no wet-lab experiment."),
        "_why": ("To answer 'is a computation-only design paper in scope' from the journal's own "
                 "published record rather than by asking its editor."),
        "⛔_this_is_a_screen_not_a_reading": (
            "A keyword classifier cannot read a paper and is wrong in both directions on individual "
            "records. The candidates are listed with their titles and PMIDs so the ones that matter "
            "are read directly; the count alone establishes nothing."),
        "⚠_precedent_is_not_acceptance": (
            "This answers whether the journal has published work of this shape. It does not predict "
            "whether this manuscript is sent for review."),
        "_method": ("esearch over the journal, efetch for title/abstract/publication types. A record "
                    "counts as computation-only when its abstract matches no wet-lab pattern and at "
                    "least one computational pattern. Records with no usable abstract are excluded "
                    "and counted separately."),
        "journal": JOURNAL,
        "n_indexed": total,
        "n_with_abstract": len(with_abstract),
        "n_without_usable_abstract": len(recs) - len(with_abstract),
        "n_computation_only_candidates": len(dry),
        "publication_types_seen": sorted({t for r in recs.values() for t in r["pub_types"]}),
        "candidates": dry,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--check" in argv:
        if not os.path.exists(OUT):
            print("nat-scope-census.json is not built", file=sys.stderr)
            return 1
        d = json.load(open(OUT, encoding="utf-8"))
        print(f"{d['n_computation_only_candidates']} computation-only candidates of "
              f"{d['n_with_abstract']} abstracts, over {d['n_indexed']} indexed articles")
        return 0
    d = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}: {d['n_computation_only_candidates']} computation-only candidates of "
          f"{d['n_with_abstract']} abstracts ({d['n_indexed']} indexed)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
