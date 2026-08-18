#!/usr/bin/env python3
"""Check the sentences a commit CHANGED, not the whole manuscript.

⛔ WHY THIS EXISTS, AND IT IS MEASURED. Across review rounds 15 and 16 of the fusion-junction ASO
paper, the defects stopped coming from the original text and started coming from the REPAIRS:

    round 15   2 of 7 findings were introduced by round 14's fixes
    round 16   4 of 4 findings were introduced by rounds 13-15's fixes
    then       a pre-build review of those 4 fixes found 5 further problems IN THEM, one a
               claim the manuscript refutes 300 lines away

An agent scoped to the diff found all four; a whole-document reader had walked past them twice. That
is the argument for this file: the changed lines are where the defects are, and they are the lines a
reviewer is least likely to re-read because they were just repaired.

★ WHAT IT CHECKS, all of it mechanical and none of it a matter of taste:

  1. CROSS-REFERENCES RESOLVE. Every "§x.y", "Table n", "Figure n" and "Box 1" introduced by the diff
     must name something that exists. Round 15 found a pointer promising what its target denied; this
     catches the cheaper failure of a pointer naming nothing at all.
  2. PAIRED NUMERIC LISTS ARE BOUND IN A POSSIBLE ORDER. Inside an N-mer, a paired run of L leaves
     exactly N - L positions unpaired, so the two lists run in OPPOSITE directions. Writing both
     ascending inverts the mapping - which is exactly how "eleven or twelve ... four or five" got in.
  3. NEW UNIVERSALS OVER COUNTED NOUNS ARE REPORTED. A repair that closes a gap by widening a claim
     is the single most common defect this paper has produced. These are WARNINGS, not errors: a
     universal can be perfectly true, and the point is to force one deliberate look at each new one.

⚠ WHAT IT DOES NOT DO. It cannot tell whether a resolvable pointer's target actually SAYS what the
pointer promises, or whether a new claim is true. Those need a reader. This is the cheap pass that
runs every time, so the expensive reader spends its attention on what is left.

    python3 research/manuscripts/lint_changed_prose.py                 # working tree vs HEAD
    python3 research/manuscripts/lint_changed_prose.py HEAD~3..HEAD    # an explicit range
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DEFAULT_TARGETS = [
    "research/manuscripts/aso/fusion-junction-aso-research-article.md",
    "research/manuscripts/submission_tables.py",
]

WORD2NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
}
_NUMWORD = "|".join(WORD2NUM)

_RUN_LIST = re.compile(
    rf"(?:run of|runs of)\s+((?:{_NUMWORD}|\d+)(?:\s+or\s+(?:{_NUMWORD}|\d+))*)\s+base pairs?"
    rf"|((?:{_NUMWORD}|\d+)(?:-\s*or\s+|\s+or\s+)(?:{_NUMWORD}|\d+))-?\s*base-pair", re.I)
_GAP_LIST = re.compile(
    rf"(?:leaves|carries|leaving|carrying)\s+((?:{_NUMWORD}|\d+)(?:\s+or\s+(?:{_NUMWORD}|\d+))*)"
    rf"\s+(?:positions? unpaired|mismatch(?:es)?|unpaired positions?)", re.I)
_NMER = re.compile(r"\b(\d+)-mer\b")

_COUNTED_NOUNS = ("counts?", "screens?", "designs?", "reagents?", "junctions?", "criteri(?:on|a)",
                  "rules?", "duplex(?:es)?", "sites?", "near-matches", "geometr(?:y|ies)",
                  "thresholds?", "registers?", "parents?", "tall(?:y|ies)")
_GOVERNS = re.compile(
    rf"\b(every|all|each|any|none of|no other|the only|only one)\b[\w\s,'’-]{{0,25}}?"
    rf"\b(?:{'|'.join(_COUNTED_NOUNS)})\b", re.I)


def _git(*args):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True).stdout


def added_hunks(rev_range, targets):
    """[(path, joined_text)] — one entry per contiguous run of ADDED lines, joined into prose.

    ⛔ JOINED, NOT PER-LINE, AND THAT IS THE WHOLE POINT. The manuscript is hard-wrapped at about
    100 columns, so a single sentence routinely spans two or three source lines. The first version
    of this file matched per line and therefore could not see the very defect it was written for:
    "…leaves five or four" sat on one line and "positions unpaired respectively" on the next, so the
    paired-list check never fired. It was caught by testing the linter against the known defect
    rather than by reading it. A checker whose unit of analysis is smaller than a sentence cannot
    check sentences.
    """
    #: ⛔ -U2, NOT -U0, AND CONTEXT LINES ARE KEPT. Second measured failure of this instrument: with
    #: -U0 the diff holds only the modified line, so a sentence whose tail sits on the FOLLOWING
    #: unchanged line is still cut in half. The injected test defect — "…leaves four or five" with
    #: "positions unpaired respectively" wrapped onto the next line — survived the first two versions
    #: of this function for exactly that reason. The unit of analysis has to be the changed
    #: NEIGHBOURHOOD; a hunk is analysed only if it actually contains an addition.
    args = ["diff", "-U2"]
    if rev_range:
        args.append(rev_range)
    args += ["--", *targets]
    out, path, hunks = _git(*args), None, []
    current, touched = [], False
    def _flush():
        if current and touched:
            hunks.append((path, " ".join(current)))
        current.clear()
    for line in out.splitlines():
        if line.startswith("+++ b/"):
            _flush(); touched = False
            path = line[6:]
        elif line.startswith("@@"):
            _flush(); touched = False
        elif line.startswith("+") and not line.startswith("+++"):
            current.append(line[1:].strip()); touched = True
        elif line.startswith(" "):
            current.append(line[1:].strip())
    _flush()
    return hunks


def _known_anchors(article):
    text = open(article, encoding="utf-8").read()
    sections = set(re.findall(r"^#{2,3}\s+(\d+(?:\.\d+)?)\s*·", text, re.M))
    tables = set(re.findall(r"\*\*Table (\d+)\.", text))
    figures = set(re.findall(r"\*\*(?:Supplementary )?Figure (S?\d+)\.", text))
    tables |= set(re.findall(r"\*\*Table (\d+)\.",
                             open(os.path.join(HERE, "aso",
                                               "fusion-junction-aso-submission-tables.md"),
                                  encoding="utf-8").read()))
    return sections, tables, figures


def _to_int(tok):
    tok = tok.strip().lower()
    return WORD2NUM.get(tok, int(tok) if tok.isdigit() else None)


def _split_list(blob):
    return [_to_int(p) for p in re.split(r"\s*(?:-\s*)?or\s+", blob) if _to_int(p) is not None]


def main(argv):
    rev_range = argv[1] if len(argv) > 1 else None
    targets = DEFAULT_TARGETS
    article = os.path.join(REPO, DEFAULT_TARGETS[0])
    sections, tables, figures = _known_anchors(article)

    rows = added_hunks(rev_range, targets)
    errors, warnings = [], []

    for path, line in rows:
        base = os.path.basename(path)

        for ref in re.findall(r"§(\d+(?:\.\d+)?)", line):
            if ref not in sections:
                errors.append(f"{base}: §{ref} names no section — {line.strip()[:110]}")
        for ref in re.findall(r"\bTable (\d+)", line):
            if ref not in tables:
                errors.append(f"{base}: Table {ref} does not exist — {line.strip()[:110]}")
        for ref in re.findall(r"\bFigure (S?\d+)", line):
            if ref not in figures:
                errors.append(f"{base}: Figure {ref} does not exist — {line.strip()[:110]}")

        nmer, run, gap = _NMER.search(line), _RUN_LIST.search(line), _GAP_LIST.search(line)
        if nmer and run and gap:
            n = int(nmer.group(1))
            runs = _split_list(run.group(1) or run.group(2) or "")
            gaps = _split_list(gap.group(1) or "")
            if runs and gaps and len(runs) == len(gaps):
                bad = [(a, b) for a, b in zip(runs, gaps) if a + b != n]
                if bad:
                    errors.append(
                        f"{base}: paired lists bound in an impossible order — "
                        + " and ".join(f"{a}+{b}={a + b}" for a, b in bad)
                        + f" (each must total {n}) — {line.strip()[:110]}")

        m = _GOVERNS.search(line)
        if m:
            warnings.append(f"{base}: new universal '{m.group(0).strip()}' — {line.strip()[:110]}")

    print(f"lint_changed_prose: {len(rows)} changed passage(s) over "
          f"{rev_range or 'the working tree'}")
    for w in warnings:
        print(f"  ⚠ WARN  {w}")
    for e in errors:
        print(f"  ⛔ ERROR {e}")
    if warnings:
        print(f"\n{len(warnings)} new universal claim(s) over counted nouns. Each may be true; "
              "check each against the section or table it is about before shipping. A repair that "
              "closes a gap by widening a claim is this paper's most common self-inflicted defect.")
    if errors:
        print(f"\n{len(errors)} ERROR(s): a changed line names something that does not exist, or "
              "binds a numeric pair in an order the arithmetic forbids.")
        return 1
    print("   OK" if not warnings else "   OK (warnings above are for a human to clear)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
