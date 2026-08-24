#!/usr/bin/env python3
"""NLM journal-title abbreviations for the condensed ASO article's reference list.

⭐ WHY. External review of the submission draft, 2026-08-24: the reference style is close to Sage
Vancouver but the journal names are INCONSISTENT — some entries carry the full title in sentence
case ("Human molecular genetics", "Nucleic acids research") and others the NLM abbreviation
("Ann Surg Oncol", "J Pathol"). Sage Vancouver wants the abbreviation throughout. The mixture is an
artefact of the entries having been assembled from two corpora, not a style choice.

⛔ THE ABBREVIATIONS ARE FETCHED, NEVER TYPED. CLAUDE.md §7: never write an identifier from
recollection, and a journal abbreviation is a bibliographic fact like any other — "Folia Histochem
Cytobiol" is not derivable from the full title by rule, and a wrong one is a citation defect that
`lint_citations` cannot see. NCBI ESummary's `source` field IS the NLM title abbreviation; this
script reads it for every PMID the reference list cites and records `fulljournalname` beside it so
the substitution can be checked rather than trusted.

⛔ AND THE REWRITE IS ANCHORED, NEVER PATTERN-GUESSED. A journal title may contain a period
("Drug discovery today. Technologies"), so splitting a reference line on "." mangles it. Each line
is instead matched at its `<volume>:<pages>. PMID: <id>` tail, and the text immediately before that
tail must END WITH a string the fetch actually returned before anything is replaced. An entry whose
current journal string matches neither the fetched full title nor the fetched abbreviation is
REPORTED UNCHANGED rather than rewritten on a guess.

NETWORK. NCBI E-utilities, 403'd at CONNECT by the dev sandbox (CLAUDE.md §6), so the fetch runs on
a GitHub Actions runner and publishes back to the triggering branch. `--apply` is offline and reads
the committed artifact.

Run:
    python3 research/manuscripts/journal_abbreviations.py            # fetch + write artifact (CI)
    python3 research/manuscripts/journal_abbreviations.py --apply    # offline: rewrite the list
    python3 research/manuscripts/journal_abbreviations.py --check    # offline: is the list uniform?
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REFS = os.path.join(HERE, "aso", "fusion-junction-aso-journal-references.md")
OUT = os.path.join(HERE, "aso", "journal-abbreviations.json")

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

#: The tail every entry ends with. Anchoring here rather than on sentence punctuation is what makes
#: a journal title containing a period safe to rewrite.
TAIL = re.compile(r"\s(?P<vol>\d+):(?P<pages>[^\s.]+)\.\s+PMID:\s*(?P<pmid>\d+)")


def entries(text: str):
    """(line_index, line, pmid, journal_span) for every numbered reference entry."""
    out = []
    for i, line in enumerate(text.splitlines()):
        if not re.match(r"^\d+\.\s", line):
            continue
        m = TAIL.search(line)
        if not m:
            out.append((i, line, None, None))
            continue
        out.append((i, line, m.group("pmid"), (0, m.start())))
    return out


def fetch(pmids):
    """ESummary for every PMID at once. `source` is the NLM title abbreviation."""
    url = (f"{EUTILS}?db=pubmed&retmode=json&id={','.join(pmids)}"
           "&tool=rare-cancers&email=trimcrae@gmail.com")
    last = None
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rare-cancers/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read().decode())
            res = d["result"]
            got = {}
            for p in pmids:
                rec = res.get(p)
                if not rec:
                    continue
                got[p] = {"abbreviation": rec.get("source"),
                          "full_title": rec.get("fulljournalname")}
            return got
        except Exception as exc:  # noqa: BLE001
            last = exc
            print(f"  retry {i + 1}: {exc}", file=sys.stderr)
            time.sleep(2 ** i)
    raise RuntimeError(f"esummary failed: {last}")


def build() -> dict:
    text = open(REFS, encoding="utf-8").read()
    rows = entries(text)
    pmids = [p for _, _, p, _ in rows if p]
    got = fetch(pmids)
    missing = [p for p in pmids if p not in got or not got[p].get("abbreviation")]
    return {
        "_what": ("NLM title abbreviation and full title for every journal the condensed ASO "
                  "article cites, read from NCBI ESummary."),
        "_why": ("Sage Vancouver wants abbreviated journal names; the hand-maintained list mixes "
                 "full titles and abbreviations. External review, 2026-08-24."),
        "_provenance": ("ESummary `source` (the NLM title abbreviation) and `fulljournalname`. "
                        "No abbreviation in this file was typed by hand."),
        "⚠_not_a_verification_of_the_reference": (
            "This reads the journal title for a PMID. It says nothing about whether the entry's "
            "authors, title, year, volume or pages are correct."),
        "n_entries": len(rows),
        "n_fetched": len(got),
        "without_fetched_abbreviation": missing,
        "by_pmid": got,
    }


def apply_to_list() -> int:
    """Rewrite each entry's journal name to the fetched abbreviation. Offline."""
    if not os.path.exists(OUT):
        print(f"{os.path.basename(OUT)} is not built — run the CI fetch first", file=sys.stderr)
        return 1
    meta = json.load(open(OUT, encoding="utf-8"))["by_pmid"]
    text = open(REFS, encoding="utf-8").read()
    lines = text.splitlines()
    changed, unchanged, unmatched = 0, 0, []
    for i, line, pmid, span in entries(text):
        if not pmid or pmid not in meta:
            unmatched.append((pmid, "no fetched record"))
            continue
        abbrev = meta[pmid]["abbreviation"]
        full = meta[pmid]["full_title"]
        head = line[span[0]:span[1]]
        # The current journal string must be one the fetch actually returned. Longest first, so a
        # full title that CONTAINS the abbreviation is not half-replaced.
        cands = sorted({c for c in (full, abbrev) if c}, key=len, reverse=True)
        hit = next((c for c in cands if head.lower().endswith(c.lower())), None)
        if hit is None:
            unmatched.append((pmid, f"journal string not recognised: ...{head[-60:]!r}"))
            continue
        if hit == abbrev:
            unchanged += 1
            continue
        lines[i] = head[: len(head) - len(hit)] + abbrev + line[span[1]:]
        changed += 1
    with open(REFS, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"abbreviated {changed} entries; {unchanged} already abbreviated")
    for pmid, why in unmatched:
        print(f"  UNCHANGED {pmid}: {why}", file=sys.stderr)
    return 1 if unmatched else 0


def check() -> int:
    """Every entry's journal string equals the fetched abbreviation."""
    if not os.path.exists(OUT):
        print(f"{os.path.basename(OUT)} is not built", file=sys.stderr)
        return 1
    meta = json.load(open(OUT, encoding="utf-8"))["by_pmid"]
    text = open(REFS, encoding="utf-8").read()
    bad = []
    for _, line, pmid, span in entries(text):
        if not pmid or pmid not in meta:
            continue
        abbrev = meta[pmid]["abbreviation"]
        head = line[span[0]:span[1]]
        if not head.endswith(abbrev):
            bad.append((pmid, abbrev, head[-60:]))
    for pmid, abbrev, tail in bad:
        print(f"  {pmid}: expected journal {abbrev!r}, entry ends ...{tail!r}", file=sys.stderr)
    print(f"{len(bad)} entries not on the NLM abbreviation")
    return 1 if bad else 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--apply" in argv:
        return apply_to_list()
    if "--check" in argv:
        return check()
    d = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {OUT}: {d['n_fetched']} of {d['n_entries']} entries")
    return 1 if d["without_fetched_abbreviation"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
