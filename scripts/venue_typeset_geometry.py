#!/usr/bin/env python3
"""Measure a journal's TYPESET geometry off its own published PDFs.

⛔ WHY THIS EXISTS. Nucleic Acid Therapeutics levies a mandatory page charge of $90 per printed
page, so "how many printed pages is this manuscript" is a COST question and not a formatting
preference. That number cannot be read anywhere: a journal publishes its SUBMISSION format
(double-spaced, a point size, a reference style) and not its TYPESET design (trim size, column
widths, body point size), because authors do not typeset. journals.sagepub.com also returns 403 to
a real headless browser, so even the submission page is unreadable from CI.

⛔ AND THE OBVIOUS SHORTCUT IS WRONG. Characters-per-page averaged over published articles is not
an estimator of anything: a figure occupies page area and contributes no characters, so the measure
reports a journal's illustration density rather than its layout. What transfers between a published
article and an unpublished one is GEOMETRY — trim size, margins, column count and width, body point
size and leading. Those are applied to our own build so that our own figures and tables occupy
their real area, and the resulting page count is a measurement rather than a ratio.

⚠ THE VERSION OF RECORD IS NOT THE ONLY THING EUROPE PMC SERVES. For many records the open-access
PDF is the ACCEPTED AUTHOR MANUSCRIPT: single-column, double-spaced, in the author's own layout.
Measuring one of those would return the author's geometry under the journal's name, which is the
failure this file exists to avoid. Every PDF is therefore CLASSIFIED before it is used, and a
record that does not look typeset is reported as rejected rather than dropped, so the count of
usable articles is visible instead of implied.

Writes research/literature/venue-typeset-geometry.json. Stdlib plus pdfminer.six, which CI installs.

Usage:
    python3 scripts/venue_typeset_geometry.py
    python3 scripts/venue_typeset_geometry.py --journal "Nucleic Acid Therapeutics" --limit 12
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import statistics
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "research", "literature", "venue-typeset-geometry.json")

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
UA = {"User-Agent": "Mozilla/5.0 (compatible; rare-cancers-research/1.0)"}

#: A typeset research article is multi-column and set solid; an accepted author manuscript is one
#: column and double-spaced. `leading / body size` separates them cleanly and is unit-free, so it
#: does not depend on the trim size the PDF happens to declare.
MAX_TYPESET_LEADING_RATIO = 1.45
MIN_TYPESET_COLUMNS = 2


def _get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return fh.read()


def search(journal, limit):
    """Open-access records in one journal, newest first. No identifier is written from memory."""
    q = f'JOURNAL:"{journal}" AND OPEN_ACCESS:y AND (PUB_TYPE:"research-article" OR SRC:MED)'
    url = (f"{EPMC}/search?query={urllib.parse.quote(q)}&format=json"
           f"&pageSize={limit}&resultType=core&sort=P_PDATE_D%20desc")
    hits = json.loads(_get(url))["resultList"]["result"]
    return [h for h in hits if h.get("pmcid")]


def _pages(pdf_bytes, path):
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LAParams, LTChar, LTTextLineHorizontal
    open(path, "wb").write(pdf_bytes)
    out = []
    for page in extract_pages(path, laparams=LAParams()):
        lines, chars = [], []
        for el in page:
            for line in getattr(el, "_objs", []) if hasattr(el, "_objs") else []:
                if isinstance(line, LTTextLineHorizontal) and line.get_text().strip():
                    lines.append(line)
                    chars += [c.size for c in line if isinstance(c, LTChar)]
        out.append({"media": (page.width, page.height), "lines": lines, "sizes": chars})
    return out


def _mode(values, ndigits=1):
    if not values:
        return None
    counts = collections.Counter(round(v, ndigits) for v in values)
    return counts.most_common(1)[0][0]


def measure(pages):
    """Trim, margins, columns, body point size and leading, over the interior pages only.

    The first page carries a masthead and title block and the last carries the reference tail;
    neither is representative of the body, and including them moves the modal font size.
    """
    body = pages[1:-1] if len(pages) > 2 else pages
    if not body:
        return None
    sizes = [s for p in body for s in p["sizes"]]
    body_size = _mode(sizes)

    # Columns: key off the modal LINE WIDTH, which is the strongest signal a typeset body has.
    # ⛔ Two earlier attempts failed on real input and both failures are kept in mind here.
    # Clustering left edges reported six columns and a negative gutter, because every table cell
    # contributes a dense left edge indistinguishable from a column start. Looking for a vertical
    # whitespace gutter then reported ONE column, because a full-width table's cells tile the whole
    # measure and leave no empty band anywhere on the page. A justified body line, by contrast, is
    # exactly one column wide and there are hundreds of them, so the modal width IS the column
    # width and the left edges OF LINES AT THAT WIDTH are the column starts.
    allx0_all = [l.x0 for p in body for l in p["lines"]]
    allx1_all = [l.x1 for p in body for l in p["lines"]]
    if not allx0_all:
        return None
    block0, block1 = min(allx0_all), max(allx1_all)
    widths = [l.x1 - l.x0 for p in body for l in p["lines"]]
    col_w = _mode(widths, 0)
    #: Lines within a point of the modal width are set to the measure; ragged last lines and table
    #: cells are not, and are what the tolerance excludes.
    at_measure = [l for p in body for l in p["lines"] if abs((l.x1 - l.x0) - col_w) <= 1.0]
    cols = []
    for x in sorted(round(l.x0) for l in at_measure):
        if not cols or x - cols[-1] > col_w / 2:
            cols.append(float(x))
    widths = [col_w] * len(cols)

    # Leading: consecutive baseline gaps inside one column, which excludes column-jump deltas.
    gaps = []
    for p in body:
        for c in cols:
            ys = sorted((l.y0 for l in p["lines"] if abs(l.x0 - c) < 40), reverse=True)
            gaps += [a - b for a, b in zip(ys, ys[1:]) if 0 < a - b < 40]
    leading = _mode(gaps)

    allx0 = [l.x0 for p in body for l in p["lines"]]
    allx1 = [l.x1 for p in body for l in p["lines"]]
    ally0 = [l.y0 for p in body for l in p["lines"]]
    ally1 = [l.y1 for p in body for l in p["lines"]]
    w, h = body[0]["media"]
    return {
        "trim_pt": [round(w, 1), round(h, 1)],
        "trim_mm": [round(w * 25.4 / 72, 1), round(h * 25.4 / 72, 1)],
        "margins_pt": {"left": round(min(allx0), 1), "right": round(w - max(allx1), 1),
                       "bottom": round(min(ally0), 1), "top": round(h - max(ally1), 1)},
        "columns": len(cols),
        "column_x0_pt": [round(c, 1) for c in cols],
        "column_width_pt": [round(v, 1) for v in widths],
        "gutter_pt": (round(cols[1] - cols[0] - widths[0], 1)
                      if len(cols) > 1 and widths else None),
        "body_font_pt": body_size,
        "leading_pt": leading,
        "leading_ratio": round(leading / body_size, 3) if leading and body_size else None,
        "pages_total": len(pages),
    }


def classify(g):
    """Typeset version of record, or an accepted author manuscript wearing the journal's name."""
    if not g or not g.get("leading_ratio"):
        return "unmeasurable"
    if g["columns"] < MIN_TYPESET_COLUMNS:
        return "rejected: single column, reads as an accepted author manuscript"
    if g["leading_ratio"] > MAX_TYPESET_LEADING_RATIO:
        return (f"rejected: leading {g['leading_ratio']}x body size, reads as double-spaced "
                "author manuscript rather than a typeset article")
    return "typeset"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--journal", default="Nucleic Acid Therapeutics")
    ap.add_argument("--limit", type=int, default=12)
    ap.add_argument("--workdir", default="/tmp/venue-typeset")
    a = ap.parse_args()
    os.makedirs(a.workdir, exist_ok=True)

    records, per_article = [], []
    try:
        records = search(a.journal, a.limit)
    except Exception as exc:
        print(f"::error::Europe PMC search failed: {exc}", file=sys.stderr)

    for rec in records:
        pmcid = rec["pmcid"]
        #: ⛔ `{EPMC}/{pmcid}/fullTextPDF` WAS TRIED FIRST AND 404s ON EVERY RECORD (measured
        #: 2026-08-20, 20 of 20). An OPEN_ACCESS:y flag says the article is free to read, not that
        #: Europe PMC serves a PDF of it at a path constructed by hand. The record names its own
        #: full-text locations, so they are read from it rather than assumed.
        urls = [u.get("url") for u in
                (rec.get("fullTextUrlList") or {}).get("fullTextUrl", [])
                if (u.get("documentStyle") == "pdf" and u.get("availability") != "Subscription")]
        urls.append(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextPDF")
        blob, why = None, []
        for u in urls:
            try:
                blob = _get(u)
                if blob[:4] == b"%PDF":
                    break
                why.append(f"{u} served {blob[:16]!r}, not a PDF")
                blob = None
            except Exception as exc:
                why.append(f"{u}: {exc}")
        if blob is None:
            per_article.append({"pmcid": pmcid,
                                "verdict": f"unfetched: {'; '.join(why) or 'no pdf url on the record'}"})
            continue
        try:
            geom = measure(_pages(blob, os.path.join(a.workdir, f"{pmcid}.pdf")))
        except Exception as exc:
            per_article.append({"pmcid": pmcid, "verdict": f"unmeasurable: {exc}"})
            continue
        per_article.append({"pmcid": pmcid, "title": rec.get("title"),
                            "year": rec.get("pubYear"), "verdict": classify(geom),
                            "geometry": geom})

    good = [r for r in per_article if r.get("verdict") == "typeset"]

    def med(path):
        vals = []
        for r in good:
            v = r["geometry"]
            for k in path.split("."):
                v = v[k] if isinstance(v, dict) else v
            if isinstance(v, list):
                v = v[0] if v else None
            if v is not None:
                vals.append(v)
        return round(statistics.median(vals), 1) if vals else None

    doc = {
        "_what": f"The typeset geometry of {a.journal}, measured off its own published PDFs.",
        "_why": ("A page charge makes the printed page count a cost. The journal publishes its "
                 "submission format and not its typeset design, so the design is measured here "
                 "rather than assumed."),
        "⚠_what_this_is_not": ("Not a characters-per-page estimate. A figure occupies page area "
                               "and contributes no characters, so that measure reports "
                               "illustration density rather than layout and does not transfer."),
        "journal": a.journal,
        "records_examined": len(per_article),
        "records_typeset": len(good),
        "⚠_rejected_are_listed_not_dropped": [r for r in per_article
                                              if r.get("verdict") != "typeset"],
        "consensus": None if not good else {
            "trim_pt": med("trim_pt"), "columns": med("columns"),
            "column_width_pt": med("column_width_pt"), "gutter_pt": med("gutter_pt"),
            "body_font_pt": med("body_font_pt"), "leading_pt": med("leading_pt"),
            "margin_left_pt": med("margins_pt.left"), "margin_top_pt": med("margins_pt.top"),
        },
        "per_article": per_article,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"wrote {OUT}: {len(good)} typeset of {len(per_article)} examined")
    if good:
        print(json.dumps(doc["consensus"], indent=1))
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
