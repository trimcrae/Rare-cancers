#!/usr/bin/env python3
"""Verify — and repair — the roadmap's `:NNNN` line citations into the paper and the SI.

⛔ WHY THIS EXISTS. The roadmap cites the manuscript and SI by LINE NUMBER, in the form

    *"the quoted phrase"* (`:2200–2203`)

and line numbers drift every time the cited file gains a paragraph above the citation. A verification read
on 2026-08-06 found **every one of 39 such citations stale**, by a systematic +16 to +35 lines into the paper
and +15 to +35 into the SI — i.e. not a typo but the accumulated drift of ordinary edits. Nothing detected
it, because a wrong line number is still a well-formed link: it points somewhere, just not at the sentence.

⭐ THE POINT IS THAT THE QUOTE MAKES IT CHECKABLE. Each citation sits immediately after the phrase it cites,
so the true line can be DERIVED by searching the target for that phrase — the same way a human would check
one, and the reason this defect is fixable in bulk rather than one at a time.

⚠ WHAT THIS DELIBERATELY DOES NOT DO: invent a citation for a quote it cannot find. A phrase that does not
appear in the target is reported as UNRESOLVED and left alone — it may be a paraphrase, or the sentence may
have been rewritten, and silently repointing it at the nearest match is how a citation comes to vouch for
something it does not say.

Usage:
    python3 research/manuscripts/line_citations.py            # check, non-zero exit if any drifted
    python3 research/manuscripts/line_citations.py --fix      # rewrite the drifted ones in place
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = os.path.join(HERE, "nr4a3-program-map.md")
PAPER = os.path.join(HERE, "degrader", "nr4a3-degrader-paper.md")
SI = os.path.join(HERE, "degrader", "nr4a3-degrader-paper-SI.md")

#: A citation: a backticked `:NNNN` or `:NNNN–NNNN`, en dash or hyphen.
CITE = re.compile(r"`:(\d+)(?:[–-](\d+))?`")

#: The quoted phrase this repo uses, `*"…"*`. Non-greedy, and it may span the wrapped line.
QUOTE = re.compile(r'\*"(.+?)"\*', re.S)

#: How far back to look for the quote that a citation belongs to. A citation follows its quote closely;
#: scanning further would start attaching citations to whatever quote happened to appear earlier.
LOOKBACK = 400

#: A citation preceded by "SI" within this many characters targets the SI, not the paper.
SI_HINT = re.compile(r"\bSI\b[^.]{0,80}$")


def _norm(s):
    """Fold the typography apart from the content: smart quotes, dashes, markdown emphasis, whitespace.

    The roadmap quotes the paper through a markdown round-trip, so `**bold**` inside a quoted phrase and a
    straight vs curly apostrophe are noise. Matching on the raw string finds nothing and would report every
    citation UNRESOLVED, which reads as "the checker is broken" rather than "the citation is fine".
    """
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"[*`_]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def _load(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    return lines, [_norm(l) for l in lines]


def _find(needle, norm_lines):
    """1-indexed line of the first line containing `needle`, or None.

    Falls back to a two-line join, because a quoted phrase in the target is frequently wrapped.
    """
    n = _norm(needle)
    if len(n) < 12:                      # too short to identify a line; refuse rather than guess
        return None
    for i, l in enumerate(norm_lines):
        if n in l:
            return i + 1
    for i in range(len(norm_lines) - 1):
        if n in norm_lines[i] + " " + norm_lines[i + 1]:
            return i + 1
    return None


def scan():
    """[(pos, start, end, cited_line, true_line, target, quote)] for every citation carrying a quote."""
    with open(MAP, encoding="utf-8") as fh:
        text = fh.read()
    paper_raw, paper = _load(PAPER)
    si_raw, si = _load(SI)

    out = []
    for m in CITE.finditer(text):
        before = text[max(0, m.start() - LOOKBACK):m.start()]
        quotes = QUOTE.findall(before)
        if not quotes:
            continue
        quote = quotes[-1]
        target = "SI" if SI_HINT.search(before) else "paper"
        true_line = _find(quote, si if target == "SI" else paper)
        out.append({
            "span": (m.start(), m.end()),
            "cited": int(m.group(1)),
            "cited_end": int(m.group(2)) if m.group(2) else None,
            "true": true_line,
            "target": target,
            "quote": quote,
        })
    return text, out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="rewrite drifted citations in place")
    args = ap.parse_args(argv)

    text, cites = scan()
    drifted = [c for c in cites if c["true"] and c["true"] != c["cited"]]
    unresolved = [c for c in cites if not c["true"]]
    ok = [c for c in cites if c["true"] and c["true"] == c["cited"]]

    for c in drifted:
        print(f"  DRIFTED  {c['target']} `:{c['cited']}` -> :{c['true']}   {c['quote'][:64]!r}")
    for c in unresolved:
        print(f"  UNRESOLVED  {c['target']} `:{c['cited']}` — quote not found, LEFT ALONE   "
              f"{c['quote'][:64]!r}")

    if args.fix and drifted:
        # rewrite back-to-front so earlier spans keep their offsets
        for c in sorted(drifted, key=lambda x: -x["span"][0]):
            s, e = c["span"]
            span = str(c["true"]) if c["cited_end"] is None else \
                f"{c['true']}–{c['true'] + (c['cited_end'] - c['cited'])}"
            text = text[:s] + f"`:{span}`" + text[e:]
        with open(MAP, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"\nrewrote {len(drifted)} citation(s)")
        return 0

    print(f"\nline_citations: {len(ok)} correct · {len(drifted)} DRIFTED · {len(unresolved)} unresolved "
          f"({len(cites)} quoted citations)")
    return 1 if drifted else 0


if __name__ == "__main__":
    sys.exit(main())
