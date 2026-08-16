#!/usr/bin/env python3
"""What a manuscript contains that must survive an edit — and what a given edit actually lost.

⭐ WHY THIS EXISTS. Five review rounds have run against the fusion-junction ASO paper and every one
had a remit that could only ADD: find what is wrong, state it more carefully, disclose the bound.
None was ever asked what the paper does not need. The measured result is a main text that went from
10,905 words to 18,427 in two days, with each addition individually defensible and nothing ever
removed — a ratchet, not a process.

The reason nobody cut is that cutting was unsafe. A reviewer can verify an addition by reading it; to
verify a DELETION you have to know what the paper contained before, in full, and check that nothing
load-bearing went with the prose. Round 4 did exactly that by hand for one pass — it diffed every
numeral and every 5'-...-3' sequence against HEAD and reported "numbers present before and absent
after: one, `1997,` -> `1997.`". That was the right instrument and it was never made reusable.

This is that instrument, generalised. It lets an editorial pass delete aggressively, because what a
deletion costs is measured rather than feared.

⛔ WHAT IT IS NOT. It does not judge whether a cut was WISE — only whether it was LOSSLESS on the
things this repository treats as load-bearing:

    numbers      every numeral carrying scientific weight, with the sentence it sat in
    sequences    every 5'-...-3' oligonucleotide, which must never vanish silently
    citations    every PMID, since a dropped citation is a dropped provenance
    hedges       every scope-limiting construction, because the failure mode of a SHORTENING pass is
                 dropping the qualifier and keeping the claim -- the exact inverse of the failure
                 mode every previous round was guarding against, and far more dangerous

⚠ A LOSS IS NOT AUTOMATICALLY A DEFECT. Cutting a duplicated caveat removes a hedge and improves the
paper; cutting the only statement of a bound removes the same kind of token and damages it. This tool
reports; a human or a reviewing agent decides. What it forbids is losing something WITHOUT NOTICING,
which is the only outcome that has no defence.

Usage
-----
    python3 research/manuscripts/manuscript_inventory.py <file>                 # inventory one file
    python3 research/manuscripts/manuscript_inventory.py <file> --against <ref> # what changed vs a git ref
    python3 research/manuscripts/manuscript_inventory.py <file> --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

# ⚠ Section numbers, reference superscripts, years and list markers are excluded deliberately: they
# move whenever a paper is reorganised, which is exactly what an editorial pass is for, and flagging
# them would bury the losses that matter under noise.
_SUPERSCRIPT = re.compile(r"<sup>[\d,–\-]+</sup>")
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_SECTION_REF = re.compile(r"§\s*[\d.]+")
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")

_NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?\s*%?")
_SEQUENCE = re.compile(r"5[′']-[ACGTUacgtu]+-3[′']")
_PMID = re.compile(r"PMID:\s*(\d+)")

# Scope-limiting constructions. The point is not lint-style pattern matching -- it is that a
# shortening pass which drops these while keeping the sentence turns a bounded claim into a bare one.
_HEDGES = (
    "not established", "no retrieved", "not measured", "is a floor", "lower bound",
    "upper bound", "cannot", "does not establish", "is not a claim", "not a statement about safety",
    "stated threshold", "not a measurement", "would falsify", "no evidence", "unquantified",
    "not attempted", "is not evidence", "rather than measured", "by construction",
)


def _strip(text: str) -> str:
    text = _COMMENT.sub(" ", text)
    text = _SUPERSCRIPT.sub(" ", text)
    text = _SECTION_REF.sub(" ", text)
    return text


def inventory(text: str) -> dict:
    body = _strip(text)
    flat = " ".join(body.split())
    numbers: dict[str, int] = {}
    for m in _NUMBER.finditer(flat):
        tok = m.group(0).strip()
        if _YEAR.fullmatch(tok.replace(",", "")):
            continue
        if len(tok.rstrip("%").replace(",", "").replace(".", "")) == 0:
            continue
        numbers[tok] = numbers.get(tok, 0) + 1
    return {
        "numbers": numbers,
        "sequences": sorted(set(_SEQUENCE.findall(text))),
        "pmids": sorted(set(_PMID.findall(text))),
        "hedges": {h: flat.lower().count(h) for h in _HEDGES if h in flat.lower()},
        "words": len(flat.split()),
        "headings": [l.strip() for l in text.splitlines() if l.startswith("#")],
    }


def _at_ref(path: str, ref: str) -> str:
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True, check=True).stdout.strip()
    rel = os.path.relpath(os.path.abspath(path), root)
    return subprocess.run(["git", "show", f"{ref}:{rel}"],
                          capture_output=True, text=True, check=True).stdout


def compare(old: dict, new: dict) -> dict:
    lost_numbers = {k: v for k, v in old["numbers"].items()
                    if new["numbers"].get(k, 0) < v}
    return {
        "words_before": old["words"],
        "words_after": new["words"],
        "words_delta": new["words"] - old["words"],
        "numbers_lost": {k: {"before": old["numbers"][k], "after": new["numbers"].get(k, 0)}
                         for k in lost_numbers},
        "sequences_lost": [s for s in old["sequences"] if s not in new["sequences"]],
        "pmids_lost": [p for p in old["pmids"] if p not in new["pmids"]],
        "hedges_lost": {h: {"before": c, "after": new["hedges"].get(h, 0)}
                        for h, c in old["hedges"].items() if new["hedges"].get(h, 0) < c},
        "headings_removed": [h for h in old["headings"] if h not in new["headings"]],
        "headings_added": [h for h in new["headings"] if h not in old["headings"]],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--against", help="git ref to compare against (e.g. HEAD, main, a SHA)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as fh:
        new = inventory(fh.read())

    if not args.against:
        out = {k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in new.items()}
        print(json.dumps(out, indent=1) if args.json else
              "\n".join(f"{k:>12}: {v}" for k, v in out.items()))
        return 0

    delta = compare(inventory(_at_ref(args.file, args.against)), new)
    if args.json:
        print(json.dumps(delta, indent=1))
        return 0

    print(f"words {delta['words_before']} -> {delta['words_after']} "
          f"({delta['words_delta']:+d})\n")
    for label, key in (("SEQUENCES LOST", "sequences_lost"),
                       ("PMIDs LOST", "pmids_lost"),
                       ("HEADINGS REMOVED", "headings_removed")):
        if delta[key]:
            print(f"⛔ {label} ({len(delta[key])}):")
            for item in delta[key]:
                print(f"     {item}")
            print()
    if delta["hedges_lost"]:
        print(f"⚠ HEDGES REDUCED ({len(delta['hedges_lost'])}) — a shortening pass that drops the "
              f"qualifier and keeps the claim is the failure mode here:")
        for h, c in sorted(delta["hedges_lost"].items()):
            print(f"     {h!r}: {c['before']} -> {c['after']}")
        print()
    if delta["numbers_lost"]:
        print(f"⚠ NUMBERS NO LONGER PRESENT ({len(delta['numbers_lost'])}) — each is either a cut "
              f"worth making or a result dropped by accident; this tool does not know which:")
        for n, c in sorted(delta["numbers_lost"].items(),
                           key=lambda kv: -kv[1]["before"])[:40]:
            print(f"     {n:>12}: {c['before']} -> {c['after']}")
        if len(delta["numbers_lost"]) > 40:
            print(f"     … and {len(delta['numbers_lost']) - 40} more")
    if not any(delta[k] for k in ("sequences_lost", "pmids_lost", "hedges_lost", "numbers_lost")):
        print("✅ nothing load-bearing lost: no sequence, citation, hedge or number went missing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
