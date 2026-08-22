#!/usr/bin/env python3
"""Which sentences of the submission does any instrument actually read?

⛔⛔ WHY THIS EXISTS — THE CONVERGENCE DIAGNOSIS (2026-08-22, after round 15).

Fifteen rounds of blind adversarial review, and the BLOCKER count went UP: three distinct in round
14, six in round 15. That is not a paper getting worse. Read the blockers together and they are one
finding:

  r14  Table 2's caption counted rows it no longer had     — no gate read that file
  r14  §5's void figure was deleted, orphaning a claim     — no gate read the dependency
  r14  the paper never stated its own chemistry            — no gate reads absence
  r15  the wrong non-financial interest was declared       — no gate reads Declarations
  r15  both reagents named by donor exon alone             — no gate reads sequence+exon together
  r15  "ten" is a WORD, so no numeric instrument read it   — no gate reads criteria as words
  r15  the title's PREDICATE could be inverted             — no gate reads verbs
  r15  the two reagents swappable against their own table  — no gate joins prose to a table cell

Every one is a surface with ZERO instruments, not a number a guard got wrong. So the blocker rate
was tracking how many new LENSES each round introduced, not how many defects the paper held: a new
seat looks somewhere nobody looked, and finds the first thing there. That process does not converge
by iteration, because there is always another unexamined patch.

★ WHAT CHANGES THE SHAPE: stop sampling surfaces one lens at a time and ENUMERATE them. This script
asks, of every assertive sentence in a manuscript, whether any committed instrument matches it —
pins, the prose-guard patterns, the claim linter. The uncovered set IS the remaining blocker risk,
available all at once instead of one per round.

⚠ WHAT THIS IS NOT. It does not check whether a sentence is TRUE — only whether anything would
notice if it changed. A covered sentence can still be wrong; an uncovered one is simply unwatched.
And matching is approximate by construction: a pattern that matches a sentence may be asserting
about a different part of it. Treat the covered count as an upper bound and the uncovered list as
the finding.
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
TESTS = os.path.join(HERE, "tests")
PINS = os.path.join(HERE, "pinned-figures.json")

PAPERS = {
    "journal-article": os.path.join(HERE, "aso", "fusion-junction-aso-journal-article.md"),
    "journal-tables": os.path.join(HERE, "aso", "fusion-junction-aso-journal-tables.md"),
    "cover-letter": os.path.join(HERE, "aso", "fusion-junction-aso-cover-letter.md"),
}

#: Front matter, HTML comments, headings and table pipes are not prose claims.
_FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_SUP = re.compile(r"<sup>.*?</sup>", re.S)


def _prose(path):
    text = io.open(path, encoding="utf-8").read()
    text = _FRONTMATTER.sub("", text)
    text = _COMMENT.sub("", text)
    text = _SUP.sub("", text)
    keep = [ln for ln in text.splitlines()
            if ln.strip() and not ln.lstrip().startswith(("#", "|", ">", "```"))]
    return re.sub(r"\s+", " ", " ".join(keep))


def sentences(path):
    """Assertive sentences, split on terminal punctuation that is not inside a number or a 5′ tag."""
    flat = _prose(path)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z*‘“])", flat)
    return [s.strip() for s in parts if len(s.split()) >= 6]


def _pin_patterns():
    """Every `context` regex a pin uses, with the document it is pinned to."""
    pins = json.load(io.open(PINS, encoding="utf-8"))["artifact_figures"]
    out = []
    for pin in pins:
        ctx = pin.get("context")
        if not ctx:
            continue
        for home in pin.get("must_appear_in") or []:
            out.append((os.path.basename(home), ctx, f"pin:{pin['id']}"))
    return out


def _test_patterns(document=None):
    """String literals from tests that compile as a regex — from tests that OPEN `document`.

    ⛔⛔ THE DOCUMENT SCOPE IS THE WHOLE POINT, AND ITS ABSENCE MADE THIS SCRIPT LIE (round 16
    seat 4, 2026-08-22). The first version applied EVERY test file's literals to EVERY document, so
    a pattern belonging to a test that only ever opens the journal article could mark a cover-letter
    sentence "covered". Measured on the letter: **27 of 40 reported covered, and 22 of those 27 were
    false positives** — only four test files name that file at all. The census was over-reporting
    the exact quantity it exists to report, and a floor had already been ratcheted onto the wrong
    number.
    ⚠ THE EARLIER COMMENT HERE SAID THE OVER-INCLUSION WAS SAFE because "the finding is the
    UNCOVERED list, so the bias runs against the conclusion". That reasoning was wrong in the
    direction that matters: inflating COVERED shrinks UNCOVERED, which HIDES surfaces. The bias ran
    toward the comfortable answer, which is the one to distrust.
    ★ A test's patterns count for a document only if the test names that document. Crude, and
    exactly right: a guard that never opens a file cannot be binding a sentence in it.
    """
    out = []
    for name in sorted(os.listdir(TESTS)):
        if not (name.startswith("test_") and name.endswith(".py")):
            continue
        try:
            src = io.open(os.path.join(TESTS, name), encoding="utf-8").read()
        except OSError:
            continue
        if document and document not in src:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                s = node.value
                if len(s) < 8 or "\n" in s:
                    continue
                if not re.search(r"[\\(\[]|\\d|\\w|\\s", s):
                    continue
                try:
                    re.compile(s)
                except re.error:
                    continue
                out.append((None, s, f"test:{name}"))
    return out


#: A pattern matching more than this share of a document's sentences is not binding any of them.
#:
#: ⛔⛔ WITHOUT THIS THE SCRIPT REPORTED 100% COVERAGE ON EVERY PAPER, WHICH IS THE DEFECT IT WAS
#: WRITTEN TO FIND (measured 2026-08-22, first run). Harvesting string literals picks up `\s+`,
#: `\d`, `[^.]{0,140}` and their kin — patterns that match every sentence and therefore bind none.
#: A census that counts those as coverage is a gate reporting while measuring nothing, in the very
#: instrument built to detect that. THE SELECTIVITY TEST IS THE MEASUREMENT: a guard earns the word
#: "covers" only by distinguishing the sentence it guards from the ones it does not.
MAX_MATCH_SHARE = 0.10


def census(paper_key):
    path = PAPERS[paper_key]
    base = os.path.basename(path)
    sents = sentences(path)
    pats = [(h, p, w) for h, p, w in _pin_patterns() if h == base] + _test_patterns(base)
    compiled = []
    for _h, p, w in pats:
        try:
            rx = re.compile(p, re.I)
        except re.error:
            continue
        if not sents:
            continue
        share = sum(1 for s in sents if rx.search(s)) / len(sents)
        if share > MAX_MATCH_SHARE:
            continue  # matches everything; binds nothing
        compiled.append((rx, w))
    rows = []
    for s in sents:
        hits = sorted({w for rx, w in compiled if rx.search(s)})
        rows.append({"sentence": s, "has_number": bool(re.search(r"\d", s)),
                     "read_by": hits, "covered": bool(hits)})
    return rows


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    write = "--write" in argv
    report = {"_what": __doc__.strip().splitlines()[0],
              "_generated_by": "research/manuscripts/claim_coverage.py", "papers": {}}
    for key in PAPERS:
        rows = census(key)
        n = len(rows)
        cov = sum(r["covered"] for r in rows)
        num = [r for r in rows if r["has_number"]]
        num_cov = sum(r["covered"] for r in num)
        report["papers"][key] = {
            "sentences": n, "covered": cov,
            "with_a_number": len(num), "with_a_number_covered": num_cov,
            "uncovered_with_a_number": [r["sentence"] for r in num if not r["covered"]],
            "uncovered_without_a_number": [r["sentence"] for r in rows
                                           if not r["covered"] and not r["has_number"]],
        }
        print(f"{key}: {cov}/{n} sentences read by something "
              f"({num_cov}/{len(num)} of those stating a number)")
    if write:
        out = os.path.join(HERE, "aso", "claim-coverage.json")
        io.open(out, "w", encoding="utf-8").write(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
        print(f"wrote {os.path.relpath(out, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
