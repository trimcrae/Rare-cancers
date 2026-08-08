#!/usr/bin/env python3
"""Citation PROVENANCE — does every identifier in prose trace to something fetched? ($0, stdlib)

⛔ WHY THIS EXISTS, AND IT IS NOT HYPOTHETICAL (2026-08-07). An agent drafting a manuscript wrote a
citation from RECOLLECTION: a PMID present in **no committed source anywhere in this repository**, on a
sentence attributing the fusion's cloning to a 1995 paper. **It passed `lint_claims.py` twice.** Six
invented titles and author-lists went out in the same pass. They were caught by a human-directed audit of
every identifier against the rest of the tree — by nothing automatic, in a repository whose FIRST golden
rule is "never fabricate medical facts, stats, citations or patient data".

⭐ THE REASON THE EXISTING GUARD CANNOT CATCH IT. `lint_claims.py` checks how strongly a claim is
WORDED — R1–R5 are about selectivity, efficacy, safety, therapeutic window and clinical readiness. A
fabricated PMID attached to a properly-hedged sentence is, to that linter, a perfect sentence. Claim
STRENGTH and citation PROVENANCE are orthogonal, and nothing in preflight's other gates reads an
identifier at all. This closes that, and only that.

⚠ WHAT "PROVENANCE" MEANS HERE, PRECISELY — it is a weaker and more honest test than "is this citation
real", which no offline checker can answer. An identifier is **ANCHORED** when it also appears in a
tracked `.json`/`.jsonl`. That matters because those files are FETCH PRODUCTS and graph records — an
identifier in one got there by a network read, a registry curation or a deliberate graph edit, none of
which a model can do from memory. An identifier that exists ONLY in prose has no such origin: it may be
a perfectly good citation nobody has needed in an artifact yet, or it may be invented, and **this
checker cannot tell those apart.** So it does not try. It requires that the unanchored ones be
ENUMERATED, and it fails on any that is not.

⭐ HENCE A LEDGER, NOT A WALL. On the day it was written 216 identifiers were prose-only. Failing the
build on all 216 would have produced a red gate that the next session turns off, which is worse than no
gate — so those are baselined as `unverified_at_baseline`. **That baseline is not an amnesty; it is the
finding.** It names, for the first time, exactly which citations in this repository nobody has ever
checked. The count is meant to FALL, exactly like `systems_check`'s `last_verified: unverified` count.
⛔ **What is NOT baselined is anything new.** A prose identifier that is neither anchored nor already in
the ledger is an ERROR the moment it is written — which is the case that actually happened.

⚠ AND THE LEDGER IS NOT SELF-SERVICE. Adding an entry by hand records a claim that someone checked it;
`--baseline` refuses to run once the ledger exists, so the only way to grow it is deliberate. Use
`--verify-online` (CI, $0, Europe PMC) to move an entry from `unverified_at_baseline` to `verified` with
the date and the returned title, which is how the count falls honestly rather than by relabelling.

Usage:
  python3 research/manuscripts/lint_citations.py                # check (preflight / CI)
  python3 research/manuscripts/lint_citations.py --baseline     # first-time ledger write, once only
  python3 research/manuscripts/lint_citations.py --report       # counts by kind and status, no exit code
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LEDGER = os.path.join(HERE, "citation-provenance-ledger.json")

#: ⚠ ANCHORED IS ABOUT ORIGIN, NOT ABOUT FILE TYPE. `.json`/`.jsonl` are what fetches, registry
#: curations and graph edits write; prose is what a model types. That asymmetry is the whole test.
ANCHOR_SUFFIXES = (".json", ".jsonl")
PROSE_SUFFIXES = (".md",)

#: ⛔ Each pattern captures the BARE identifier so prose and artifact forms compare equal. A PMID
#: written `PMID: 12345678`, `PMID12345678` and `"pmid": "12345678"` is one identifier, and a checker
#: that treats them as three reports fabrications that are not there and misses the one that is.
#: ⛔ AND A FETCH CORPUS NAMES A PAPER BY URL, NOT BY THE STRING "PMID" (measured 2026-08-08).
#: Every `lit-targets-*.json` in this repo is a {name: url} map — that is what `fetch-literature.yml`
#: consumes — so a retrieved paper appears as `pubmed.ncbi.nlm.nih.gov/40828003`, as an Europe PMC
#: `EXT_ID:40828003`, or as a key like `epmc_core_40828003`, and NEVER as `PMID 40828003`. With only
#: the prefixed form recognised, the anchor scan was blind to the repository's own standard evidence
#: of a fetch: 22 distinct PMIDs were reachable ONLY through a URL inside a tracked artifact and every
#: one of them counted as unanchored.
#: ⚠ THE FAILURE DIRECTION IS THE DANGEROUS ONE — it manufactures FALSE fabrication alarms. A real
#: retrieval is reported in the same words as a citation typed from memory, and §7's warning applies
#: exactly: a gate that goes red on honest work gets switched off, taking the case it exists for with
#: it. Recognising the URL form does NOT loosen the test — a fabricated identifier appears in no
#: tracked artifact in ANY form, which is what `test_a_fabricated_pmid_still_fails` pins.
PATTERNS = {
    #: ⚠ EVERY FORM HERE IS ANCHORED TO A LITERAL CONTEXT — a PubMed host, or Europe PMC's `EXT_ID`.
    #: A bare-digit-run pattern (e.g. `_(\d{6,9})`, which WOULD have matched this corpus's
    #: `epmc_core_40828003` key) was written and then deleted before commit: it matches any 6-9 digit
    #: run after an underscore in any tracked JSON, so it could FALSELY ANCHOR a fabricated PMID that
    #: happened to collide with an unrelated number. That is the one direction this gate must never
    #: move, and a looser pattern buys nothing the two precise ones do not already reach.
    "PMID": (r"\bPMID[:\s]*(\d{6,9})\b",
             r"pubmed\.ncbi\.nlm\.nih\.gov/(\d{6,9})",
             r"\bEXT_ID[:=](\d{6,9})\b"),
    "PMCID": (r"\b(PMC\d{6,9})\b",),
    "DOI": (r"\b(10\.\d{4,9}/[^\s\)\]\},;\"'>]+)",),
    "NCT": (r"\b(NCT\d{8})\b",),
    "GEO": (r"\b(GS[EM]\d{3,7})\b",),
}

#: Trailing punctuation a DOI picks up from prose. Stripped on BOTH sides or the same DOI compares
#: unequal to itself across a sentence break.
#: ⚠ BACKTICK AND ASTERISK WERE MISSING, AND MARKDOWN IS THE PROSE THIS SCANS (measured 2026-08-08).
#: The DOI pattern's character class happily eats them, so `` `10.1002/gcc.23144` `` and
#: **10.1002/gcc.70076.** became identifiers distinct from the bare DOI sitting in the artifact —
#: the same "one identifier read as three" defect the note above says this comparison exists to stop,
#: reintroduced by the strip set rather than by the pattern.
TRAILING = ".,;:)]}\"'`*_"

STATUSES = ("unverified_at_baseline", "verified", "retracted", "known_absent_upstream")


def _tracked():
    r = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True)
    if r.returncode != 0:
        return []
    return r.stdout.split("\n")


def _scan(paths):
    """{kind: {identifier: {files}}} over `paths`."""
    found = collections.defaultdict(lambda: collections.defaultdict(set))
    for rel in paths:
        p = os.path.join(ROOT, rel)
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except (OSError, IsADirectoryError):
            continue
        for kind, pats in PATTERNS.items():
            for pat in pats:
                for m in re.findall(pat, text):
                    ident = m.strip().rstrip(TRAILING)
                    if ident:
                        found[kind][ident].add(rel)
    return found


def survey():
    """(prose, anchors) — identifiers in tracked prose, and identifiers in tracked fetch products."""
    files = _tracked()
    prose = _scan([f for f in files if f.endswith(PROSE_SUFFIXES)])
    # ⛔ THE LEDGER MUST NOT ANCHOR ITSELF, AND IT DID FOR ONE COMMIT (caught 2026-08-07, minutes
    # after the gate merged). The ledger is a `.json` listing every unanchored identifier, so once it
    # existed every one of those 215 ids appeared in a "fetch product" and the unanchored count fell
    # from 215 to 0 — the gate reporting a clean tree it had just finished declaring dirty. The pass
    # condition was unaffected (a new fabrication is in neither the ledger nor an artifact, so it
    # still fails), which is exactly what made it dangerous: the guard kept working while its READOUT
    # went vacuous, and a count of 0 is the one number nobody re-examines.
    ledger_rel = os.path.relpath(LEDGER, ROOT).replace(os.sep, "/")
    anchors = _scan([f for f in files
                     if f.endswith(ANCHOR_SUFFIXES) and f != ledger_rel])
    return prose, anchors


def unanchored(prose, anchors):
    """[(kind, identifier, sorted files)] for every prose identifier with no fetch-product anchor."""
    out = []
    for kind, ids in sorted(prose.items()):
        for ident, files in sorted(ids.items()):
            if ident not in anchors.get(kind, {}):
                out.append((kind, ident, sorted(files)))
    return out


def load_ledger():
    if not os.path.exists(LEDGER):
        return None
    return json.load(open(LEDGER, encoding="utf-8"))


def _key(kind, ident):
    #: ⛔ NORMALISE THE LEDGER'S KEY, DO NOT REWRITE THE LEDGER (2026-08-08). The 2026-08-07 baseline
    #: was captured before `TRAILING` stripped backticks/asterisks, so 35 rows are stored under a
    #: punctuation-laden form (`10.1002/anie.201806037\``). Widening the strip set re-keys the prose
    #: side, orphaning those rows — and an orphaned baseline row does not fail safe: the identifier
    #: reappears as NEW and unanchored, i.e. the gate accuses honest, already-triaged citations of
    #: being fabrications. Normalising here makes the stored form irrelevant, which is what it always
    #: should have been: the ledger records WHO CHECKED an identifier, and that fact cannot depend on
    #: whether the person who logged it happened to include the closing backtick.
    return "%s:%s" % (kind, str(ident).strip().rstrip(TRAILING))


def _norm_stored_key(key):
    """A ledger key as stored -> the same key under today's TRAILING set.

    Rows written before the strip set widened carry the punctuation; splitting on the FIRST colon
    keeps DOIs intact, which contain no colon but do contain slashes and dots.
    """
    kind, _, ident = str(key).partition(":")
    return _key(kind, ident)


def check():
    prose, anchors = survey()
    un = unanchored(prose, anchors)
    led = load_ledger()
    if led is None:
        print("::error::no citation-provenance ledger — run --baseline once to create %s"
              % os.path.relpath(LEDGER, ROOT), file=sys.stderr)
        return 2
    known = {_norm_stored_key(e["key"]) for e in led["entries"]}
    # ⛔ THE ONLY FAILING CASE, AND IT IS THE ONE THAT HAPPENED: a prose identifier that is neither
    # anchored in a fetch product nor already enumerated. Everything baselined stays green so the gate
    # survives; anything NEW must be justified at the moment it is written.
    new = [(k, i, f) for k, i, f in un if _key(k, i) not in known]
    for kind, ident, files in new:
        print("::error::UNANCHORED %s %s — appears only in prose (%s) and is not in the "
              "citation-provenance ledger. Either it is cited by an artifact (add the fetch), or it "
              "needs a ledger entry recording who checked it. A citation typed from memory is the "
              "failure this gate exists for." % (kind, ident, ", ".join(files[:3])), file=sys.stderr)
    # A ledger entry whose identifier has since vanished from prose is stale bookkeeping, not a defect.
    live = {_key(k, i) for k, i, _ in un} | {
        _key(k, i) for k in prose for i in prose[k]}
    stale = [e["key"] for e in led["entries"] if _norm_stored_key(e["key"]) not in live]
    by_status = collections.Counter(e["status"] for e in led["entries"])
    print("lint_citations: %d prose identifier(s), %d unanchored, %d in ledger (%s)%s"
          % (sum(len(v) for v in prose.values()), len(un), len(led["entries"]),
             ", ".join("%s=%d" % (s, n) for s, n in sorted(by_status.items())),
             ", %d stale ledger row(s)" % len(stale) if stale else ""))
    if new:
        print("lint_citations: %d NEW unanchored identifier(s) — see errors above" % len(new),
              file=sys.stderr)
        return 1
    return 0


def baseline():
    if os.path.exists(LEDGER):
        # ⛔ REFUSES TO REGENERATE. If --baseline could be re-run, every future fabrication would be
        # one command away from being blessed, and the gate would launder exactly what it exists to
        # catch. Growing the ledger has to be a deliberate, reviewable edit.
        print("::error::ledger already exists at %s — --baseline is a ONE-TIME operation and will "
              "not overwrite it. To add an entry, edit the file deliberately; to resolve one, use "
              "--verify-online." % os.path.relpath(LEDGER, ROOT), file=sys.stderr)
        return 2
    prose, anchors = survey()
    un = unanchored(prose, anchors)
    doc = {
        "_what": ("Every identifier that appears in this repository's PROSE and in none of its fetch "
                  "products. Written once, on 2026-08-07, after a fabricated PMID reached a manuscript "
                  "and passed lint_claims twice."),
        "_what_an_entry_means": (
            "NOT that the citation is wrong. It means NOTHING IN THIS REPOSITORY CORROBORATES IT — no "
            "fetch, no registry curation, no graph record. Most of these are almost certainly real "
            "citations that no artifact has needed yet. The point is that the list exists and is "
            "finite, so the ones that are not real can be found."),
        "_the_count_is_meant_to_fall": (
            "Same idiom as systems_check's `last_verified: unverified` count. Resolve an entry with "
            "--verify-online (CI, $0, Europe PMC), which records the date and the returned title — "
            "never by relabelling it by hand."),
        "_what_this_does_not_prove": (
            "An ANCHORED identifier is not thereby verified either. It means some artifact carries it, "
            "which is evidence of a fetch, not of correctness — an artifact can record an identifier a "
            "human typed into a curated field. This gate raises the floor; it is not a truth oracle."),
        "statuses": list(STATUSES),
        "entries": [
            {"key": _key(k, i), "kind": k, "id": i, "status": "unverified_at_baseline",
             "files": f, "note": ""}
            for k, i, f in un
        ],
    }
    json.dump(doc, open(LEDGER, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(LEDGER, "a", encoding="utf-8").write("\n")
    print("wrote %s with %d entries" % (os.path.relpath(LEDGER, ROOT), len(doc["entries"])))
    return 0


def report():
    prose, anchors = survey()
    un = unanchored(prose, anchors)
    per = collections.Counter(k for k, _, _ in un)
    print("%-6s %10s %10s %10s" % ("kind", "in prose", "anchored", "unanchored"))
    for kind in PATTERNS:
        n = len(prose.get(kind, {}))
        print("%-6s %10d %10d %10d" % (kind, n, n - per[kind], per[kind]))
    led = load_ledger()
    if led:
        by = collections.Counter(e["status"] for e in led["entries"])
        print("\nledger: %d entries — %s" % (len(led["entries"]),
                                             ", ".join("%s=%d" % kv for kv in sorted(by.items()))))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--baseline", action="store_true", help="one-time ledger write")
    ap.add_argument("--report", action="store_true", help="counts only, always exits 0")
    a = ap.parse_args(argv)
    if a.baseline:
        return baseline()
    if a.report:
        return report()
    return check()


if __name__ == "__main__":
    sys.exit(main())
