#!/usr/bin/env python3
"""
Build a journal-format numbered reference list for the fusion-junction ASO manuscript.

WHY THIS EXISTS. The manuscript cites bare inline PMIDs. A journal needs numbered references with
author, title, journal, year, volume and pages. Until 2026-08-09 no fetch product in this repository
carried a journal name at all: `scripts/fetch-paper.mjs` projected `journal: r.journalTitle`, and
Europe PMC nests the field at `journalInfo.journal.title` and returns no flat one, so the key was
always `undefined` and `JSON.stringify` dropped it. The manuscript's References note recorded the
consequence honestly — journal names deliberately absent, because typing one from memory is the exact
failure `lint_citations.py` exists for. The fetcher was fixed; this script consumes the fix.

⛔ EVERY FIELD HERE IS READ FROM A FETCH PRODUCT. Nothing is typed, inferred, completed from
recollection or filled in by pattern. A record that lacks a field emits with that field ABSENT and is
listed in `incomplete`, because a reference list with an invented volume number is worse than one
with a gap: the gap is visible to the author, the invention is not.

⚠ AND A RESOLVED IDENTIFIER IS NOT A VERIFIED CLAIM. This produces citation METADATA — evidence that
a record exists with that title in that journal. It says nothing about whether the paper supports the
sentence it is attached to. That check is human and is not automatable.

Reads:  the manuscript (for which identifiers are actually cited, in order of first appearance)
        every `_index.json` on branch `literature-cache` (for metadata)
Writes: fusion-junction-aso-references.json  — the machine record, one entry per citation
        fusion-junction-aso-references.md    — the numbered list, ready to paste

$0, offline: `git show` against a fetched branch. No network.
"""

import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PAPER = os.path.join(HERE, "fusion-junction-aso-working-record.md")
OUT_JSON = os.path.join(HERE, "fusion-junction-aso-references.json")
OUT_MD = os.path.join(HERE, "fusion-junction-aso-references.md")
BRANCH = "origin/literature-cache"

#: Fields a complete journal reference needs. A record missing any of these is reported, never guessed.
REQUIRED = ("authors", "title", "journal", "year")
NICE = ("volume", "issue", "pages", "doi", "pmcid")


def _git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


def cited_pmids_in_order():
    """PMIDs in order of first appearance in the manuscript body.

    Order matters: a numbered reference list is numbered by first citation, so the order is part of
    the output and must come from the text rather than from a sort.
    """
    text = open(PAPER, encoding="utf-8").read()
    seen, out = set(), []
    for m in re.finditer(r"PMID[: ]\s*(\d{5,9})", text):
        p = m.group(1)
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def harvest_metadata():
    """{pmid: record} over every corpus on `literature-cache`, newest corpus winning.

    ⚠ NEWEST WINS, AND THAT IS DELIBERATE. Corpora fetched before the 2026-08-09 journal fix carry
    no journal name; later ones do. Iterating in listing order and letting a later corpus overwrite
    an earlier one is what upgrades a 2026-07 record to a complete one — but it also means a record
    can change between runs, so the corpus a field came from is recorded per entry.
    """
    ls = _git("ls-tree", "-r", BRANCH, "--name-only")
    if ls.returncode:
        sys.exit(f"cannot read {BRANCH} — run `git fetch origin literature-cache` first")
    meta = {}
    for path in [l for l in ls.stdout.split("\n") if l.endswith("_index.json")]:
        blob = _git("show", f"{BRANCH}:{path}")
        if blob.returncode:
            continue
        try:
            recs = json.loads(blob.stdout)
        except json.JSONDecodeError:
            continue
        if not isinstance(recs, list):
            continue
        corpus = path.rsplit("/", 2)[-2]
        for r in recs:
            p = str(r.get("pmid") or "")
            if not p:
                continue
            cand = {k: r.get(k) for k in REQUIRED + NICE if r.get(k) not in (None, "")}
            cand["_corpus"] = corpus
            prev = meta.get(p)
            # Prefer the record that satisfies more required fields; tie-break to the later corpus.
            if prev is None or sum(k in cand for k in REQUIRED) >= sum(k in prev for k in REQUIRED):
                meta[p] = cand
    return meta


def vancouver(rec):
    """One reference in Vancouver-ish form, from fetched fields only. Absent fields are omitted."""
    bits = []
    if rec.get("authors"):
        bits.append(rec["authors"].rstrip("."))
    if rec.get("title"):
        bits.append(rec["title"].rstrip("."))
    if rec.get("journal"):
        tail = rec["journal"].rstrip(".")
        if rec.get("year"):
            tail += f". {rec['year']}"
        if rec.get("volume"):
            tail += f";{rec['volume']}"
            if rec.get("issue"):
                tail += f"({rec['issue']})"
        if rec.get("pages"):
            tail += f":{rec['pages']}"
        bits.append(tail)
    elif rec.get("year"):
        bits.append(str(rec["year"]))
    return ". ".join(b for b in bits if b) + "."


def main():
    pmids = cited_pmids_in_order()
    meta = harvest_metadata()
    entries, incomplete, unresolved = [], [], []
    for i, p in enumerate(pmids, 1):
        rec = meta.get(p)
        if rec is None:
            unresolved.append(p)
            entries.append({"n": i, "pmid": p, "_status": "NO RETRIEVED RECORD",
                            "_note": "cited in the manuscript and present in no fetch product — "
                                     "either fetch it or remove the citation"})
            continue
        missing = [k for k in REQUIRED if k not in rec]
        e = {"n": i, "pmid": p, **{k: v for k, v in rec.items() if not k.startswith("_")},
             "formatted": vancouver(rec), "_corpus": rec.get("_corpus")}
        if missing:
            e["_missing_fields"] = missing
            incomplete.append({"pmid": p, "missing": missing})
        entries.append(e)

    res = {
        "_what": "Numbered reference list for fusion-junction-aso-working-record.md, in order of first "
                 "citation in the manuscript body.",
        "_generated_by": "research/manuscripts/build_reference_list.py",
        "_provenance": "Every field is read from a Europe PMC fetch product on branch "
                       "literature-cache. No field is typed, inferred or completed from "
                       "recollection; a record missing a field emits without it and is listed in "
                       "`incomplete`.",
        "_what_this_is_not": [
            "NOT verification that any cited paper supports the sentence it is attached to. This is "
            "citation metadata — evidence a record exists with that title in that journal. The "
            "support check is human and is not automated anywhere in this repository.",
            "NOT a stable snapshot: `harvest_metadata` lets a newer corpus override an older one, "
            "so the `_corpus` field per entry is the only record of where a value came from.",
        ],
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_cited": len(pmids),
        "n_complete": len(pmids) - len(incomplete) - len(unresolved),
        "n_incomplete": len(incomplete),
        "n_unresolved": len(unresolved),
        "incomplete": incomplete,
        "unresolved": unresolved,
        "references": entries,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2)

    # ⚠ FRONTMATTER IS NOT DECORATION HERE. `systems_check` gate D4 refuses any tracked markdown in
    # this tree with no declared purpose, scope, audience or freshness, and it refused this file on
    # its first generation. A GENERATED document needs it as much as a hand-written one — arguably
    # more, since a reader has no author to ask.
    lines = ["---",
             "id: DOC-ASO-REFERENCES",
             "title: \"References — fusion-junction ASO manuscript\"",
             "level: L3", "kind: generated", "status: generated",
             "generator: research/manuscripts/build_reference_list.py",
             "purpose: >",
             "  The numbered, journal-format reference list for fusion-junction-aso-working-record.md, in",
             "  order of first citation. Exists because the manuscript cites bare inline PMIDs and a",
             "  journal needs full entries.",
             "scope: >",
             "  Citation METADATA only, every field read from a Europe PMC fetch product. It is not",
             "  evidence that any cited paper supports the sentence it is attached to, and it makes",
             "  no scientific, clinical or efficacy claim of any kind.",
             "audience: [maintainers, external reviewers, autonomous research agents]",
             f"date: {time.strftime('%Y-%m-%d', time.gmtime())}",
             f"last_verified: {time.strftime('%Y-%m-%d', time.gmtime())}",
             "---", "",
             "<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:",
             "     python3 research/manuscripts/build_reference_list.py -->", "",
             "# References — fusion-junction ASO manuscript", "",
             f"*Generated by `build_reference_list.py` from Europe PMC fetch products on "
             f"`literature-cache`. {res['n_complete']} of {res['n_cited']} entries are complete; "
             f"{res['n_incomplete']} lack a required field and {res['n_unresolved']} have no "
             f"retrieved record. Nothing here is typed from recollection — an absent field is left "
             f"absent.*", ""]
    for e in entries:
        if e.get("_status"):
            lines.append(f"{e['n']}. **[NO RETRIEVED RECORD — PMID {e['pmid']}]** — {e['_note']}")
        else:
            flag = f"  ⚠ missing: {', '.join(e['_missing_fields'])}" if e.get("_missing_fields") else ""
            doi = f" doi:{e['doi']}" if e.get("doi") else ""
            lines.append(f"{e['n']}. {e['formatted']} PMID: {e['pmid']}.{doi}{flag}")
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"wrote {OUT_JSON}\nwrote {OUT_MD}", file=sys.stderr)
    print(json.dumps({k: v for k, v in res.items() if k != "references"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
