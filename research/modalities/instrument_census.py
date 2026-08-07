#!/usr/bin/env python3
"""THE INSTRUMENT CENSUS — every instrument with its known-answer test, its result and its scope, in one
machine-readable artifact GENERATED from the roadmap rather than transcribed from it. ($0, pure stdlib)

⭐ WHY (roadmap §10.1a `Q18`). §3.1's instrument table and §3.2's coverage matrix are the program's only
statements of *what has actually been tested against a known answer*, and they exist as prose in a
5,000-line document. Nothing could count them, so every count of them was narrated: "20 instruments",
"4 requirements with no instrument", "0 requirements standing on an instrument validated in the regime
the claim needs". Each of those is a number a reader has to take on trust, and at least one was already
stale when this was written (see `_derived.counts` against §3.1's own row count).

⛔ THE POINT IS THE HOLES, AND HOLES ARE ONLY COUNTABLE ONCE THE INSTRUMENTS ARE ROWS. `P1` (the
known-answer audit) and `P7` are unwritable without this: their entire claim is *"here is what happened
when a full program was audited instrument-by-instrument"*, which requires the instrument-by-instrument
list to be a table a reader can check rather than a paragraph.

★ GENERATED, NEVER TRANSCRIBED. It parses §3.1 and §3.2 out of `nr4a3-program-map.md`, so it stays true
when the roadmap changes and goes stale visibly (a parse of zero rows is an error, not an empty census)
rather than silently. CLAUDE.md rule 1: the roadmap remains the one home of every grade and every verdict
sentence; this artifact restates none of them, it INDEXES them.

⚠ WHAT THIS DOES NOT DO. It does not grade an instrument, re-word a verdict, or decide whether a result
is good enough. The `verdict_class` below is a CLASSIFICATION OF THE ROADMAP'S OWN STATE STRING by
literal marker, and every row carries `state_verbatim` beside it so a reader can see the string the class
was read from. A classifier that cannot be checked against its input is just another unhomed opinion.

Usage:
    python3 research/modalities/instrument_census.py              # regenerate the JSON + the MD view
    python3 research/modalities/instrument_census.py --check      # fail if the committed copies drift
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAP = os.path.join(ROOT, "research", "manuscripts", "nr4a3-program-map.md")
OUT_JSON = os.path.join(HERE, "instrument-census.json")
OUT_MD = os.path.join(HERE, "instrument-census.md")

INSTRUMENT_HEADER = "| id | instrument | known-answer test | result |"
COVERAGE_HEADER = "| requirement | instruments that serve it |"

#: ⚠ SPLIT ON UNESCAPED PIPES ONLY. `V16`'s cells contain `\|S\|` (absolute-value notation), and a naive
#: `split("|")` turns that one row into nine cells instead of seven -- silently shifting `state` and
#: `serves` by two columns for exactly the instrument whose scope caveat is the subtlest on the page.
CELL = re.compile(r"(?<!\\)\|")

#: Classification of §3.1's `state` cell, tried IN ORDER. First match wins, so the more specific markers
#: come first. Every one of these strings is present verbatim in the roadmap today; a row that matches
#: nothing is reported `UNCLASSIFIED` rather than defaulted, because a default here would quietly turn an
#: unreadable state into a passing one.
STATE_RULES = (
    ("REFUTED",       ("✕ **dead**", "✕ **REFUTED**", "✕ dead")),
    ("NOT_STARTED",   ("○ **not started",)),
    ("NO_KNOWN_ANSWER", ("no known-answer test", "untested as an instrument")),
    ("FAILS",         ("FAILS", "failed as registered")),
    # ⚠ DEFECT_OPEN BEFORE PARKED, AND THE ORDER IS A READING RATHER THAN A PREFERENCE. `V9`'s state cell
    # is "✓ measured — **defect open**, repair 🔒 held **and** ⏸ as framed": the INSTRUMENT was measured
    # and has an open defect; it is the REPAIR that is parked. Classing it PARKED off the ⏸ would say the
    # measurement never happened, which inverts what the row records.
    ("DEFECT_OPEN",   ("defect open",)),
    ("PARKED",        ("⏸",)),
    # ⛔ UNCALIBRATED IS ITS OWN CLASS, NOT A PARTIAL. `V16` ran to completion and returned its
    # PREREGISTERED null; the roadmap's Open decision 13 says it "may be read as a bound and may NOT be
    # reported as calibrated". Folding that into PARTIAL would lose the only distinction that matters
    # about it -- a bound is a result, an ambiguous run is not.
    ("COMPLETE_UNCALIBRATED", ("uncalibrated",)),
    ("PARTIAL",       ("mixed", "INCONCLUSIVE", "DISAGREE", "the decisive arm is ○")),
    ("PASSES",        ("PASSES",)),
)

#: §3.2's `hole?` cell, same discipline. "no usable answer" and "HOLE" are different failures and the
#: roadmap is careful about the difference (a hole means nothing was built; no-usable-answer means
#: something was built and cannot be read), so they are never merged here either.
HOLE_RULES = (
    ("NO_LONGER_A_HOLE_FAILING_INSTRUMENT", ("NO LONGER A HOLE",)),
    ("HOLE",             ("HOLE",)),
    ("EFFECTIVELY_HOLE", ("effectively yes",)),
    ("NO_USABLE_ANSWER", ("no usable answer",)),
    ("UNTESTED_INSTRUMENT", ("untested instrument",)),
    ("NOT_A_BLOCKER",    ("not this paper's blocker",)),
    ("OPEN_DECISION",    ("design decision outstanding",)),
    # ⚠ `R8`'s cell says neither "hole" nor "no usable answer": it says the answer exists but is
    # RANK-ONLY and conditional on another requirement. That is a third state and it is the honest one --
    # collapsing it into NO would report a conditional rank as a clean answer.
    ("RANK_ONLY_CONDITIONAL", ("rank-only",)),
    ("NO",               ("no —", "no --", "no ")),
)

ID_RE = re.compile(r"`?\*{0,2}(V\d+|R\d+)\*{0,2}`?")


def _table_rows(lines, header, want_cols):
    """Data rows of the markdown table under `header`, as lists of stripped cells.

    ⛔ RAISES on a table it cannot find or on a row with the wrong shape. A census that silently returns
    zero rows because a heading was reworded is the failure mode this whole artifact exists to remove --
    it would read as 'no instruments have problems'."""
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith(header))
    except StopIteration:
        raise SystemExit("instrument_census: the roadmap table starting %r is gone. Relocate this "
                         "parser rather than letting the census silently empty." % header)
    out = []
    for l in lines[start + 2:]:
        if not l.startswith("|"):
            break
        cells = [c.strip() for c in CELL.split(l.strip())[1:-1]]
        if len(cells) != want_cols:
            raise SystemExit("instrument_census: %r has %d cells, expected %d -- the table shape moved:\n%s"
                             % (cells[0][:24], len(cells), want_cols, l[:200]))
        out.append(cells)
    if not out:
        raise SystemExit("instrument_census: parsed ZERO rows under %r" % header)
    return out


def _classify(text, rules):
    for name, markers in rules:
        if any(mk in text for mk in markers):
            return name
    return "UNCLASSIFIED"


def _strip_id(cell):
    m = ID_RE.match(cell.strip())
    return m.group(1) if m else cell.strip()


def _ids_in(cell):
    """Every `R*` / `V*` id mentioned in a cell, de-duplicated, in order of appearance."""
    seen, out = set(), []
    for m in re.finditer(r"`(V\d+|R\d+)`", cell):
        if m.group(1) not in seen:
            seen.add(m.group(1))
            out.append(m.group(1))
    return out


def build(map_path=MAP):
    lines = open(map_path, encoding="utf-8").read().split("\n")

    instruments = []
    for cells in _table_rows(lines, INSTRUMENT_HEADER, 7):
        iid, name, test, result, not_supported, state, serves = cells
        iid = _strip_id(iid)
        instruments.append({
            "id": iid,
            "instrument": name,
            "known_answer_test": test,
            # ⛔ THE FIELD THE WHOLE CENSUS TURNS ON. An instrument whose known-answer-test cell SAYS it
            # has none is a different object from one that has a test and failed it, and the two have been
            # collapsed in prose before.
            "has_known_answer_test": not any(
                s in test for s in ("none exists", "**none**", "none —", "none of its own",
                                    "no in-repo known-answer test", "the nulls are the control",
                                    "(a self-check, not a known answer)", "— (no ")),
            "result": result,
            "scope_limit": not_supported,
            "state_verbatim": state,
            "verdict_class": _classify(state, STATE_RULES),
            "serves": _ids_in(serves),
            "serves_verbatim": serves,
        })

    coverage = []
    for cells in _table_rows(lines, COVERAGE_HEADER, 4):
        req, insts, status, hole = cells
        coverage.append({
            "requirement": _strip_id(req),
            "requirement_verbatim": req,
            "instruments": _ids_in(insts),
            "best_available_status": status,
            "hole_verbatim": hole,
            "hole_class": _classify(hole, HOLE_RULES),
        })

    by_class = {}
    for r in instruments:
        by_class.setdefault(r["verdict_class"], []).append(r["id"])
    hole_by_class = {}
    for c in coverage:
        hole_by_class.setdefault(c["hole_class"], []).append(c["requirement"])

    served = {i for c in coverage for i in c["instruments"]}
    orphans = sorted(r["id"] for r in instruments if not r["serves"] and r["id"] not in served)

    census = {
        "_what": ("Every instrument in the program with its known-answer test, its result and its scope, "
                  "plus the requirement-by-instrument coverage matrix -- GENERATED from "
                  "research/manuscripts/nr4a3-program-map.md sections 3.1 and 3.2, never transcribed."),
        "_generated_by": "research/modalities/instrument_census.py",
        "_source": "research/manuscripts/nr4a3-program-map.md (3.1 instrument table, 3.2 R x V coverage)",
        "_rule": ("The roadmap owns every grade and every verdict sentence; this artifact INDEXES them and "
                  "restates none. `verdict_class` and `hole_class` are classifications of the roadmap's own "
                  "state strings by literal marker, and `state_verbatim` / `hole_verbatim` carry the string "
                  "each was read from so the classification can be checked against its input."),
        "_not_a_grade": ("Nothing here decides whether a result is good enough. An UNCLASSIFIED row is an "
                         "unreadable state, not a passing one."),
        "instruments": instruments,
        "coverage": coverage,
        "_derived": {
            "n_instruments": len(instruments),
            "n_with_a_known_answer_test": sum(1 for r in instruments if r["has_known_answer_test"]),
            "n_without_a_known_answer_test": sum(1 for r in instruments if not r["has_known_answer_test"]),
            "instruments_without_a_known_answer_test": [r["id"] for r in instruments
                                                        if not r["has_known_answer_test"]],
            "by_verdict_class": {k: sorted(v, key=lambda s: int(s[1:])) for k, v in sorted(by_class.items())},
            "n_requirements": len(coverage),
            "requirements_by_hole_class": {k: v for k, v in sorted(hole_by_class.items())},
            "instruments_serving_no_requirement": orphans,
            "unclassified_instrument_states": [r["id"] for r in instruments
                                               if r["verdict_class"] == "UNCLASSIFIED"],
            "unclassified_hole_cells": [c["requirement"] for c in coverage
                                        if c["hole_class"] == "UNCLASSIFIED"],
        },
    }
    return census


#: ⛔ EVERY LINK IN A COPIED CELL IS WRITTEN RELATIVE TO THE ROADMAP, AND THE VIEW DOES NOT LIVE THERE.
#: Caught by `systems_check --check` (K2) on the first generated copy: 12 ERRORs, all of the form
#: "instrument-census.md links to `#6a--dead-...` in ITSELF and no heading makes that anchor" -- because a
#: bare `#anchor` copied out of §3.1 resolves against whatever document it lands in. The same applies to
#: `](../modalities/x.json)` (correct from `research/manuscripts/`, one directory too high from here) and
#: to `](other.md)` siblings of the roadmap. So the renderer REBASES, and it does so only in the rendered
#: view -- the JSON keeps the roadmap's text byte-for-byte, because that is the copy a reader diffs.
_MAP_DIR = "research/manuscripts"
_VIEW_DIR = "research/modalities"
_LINK = re.compile(r"\]\(([^)\s]+)\)")


def _rebase_link(target):
    import posixpath
    if target.startswith(("http://", "https://", "mailto:")):
        return target
    if target.startswith("#"):
        return posixpath.relpath(_MAP_DIR, _VIEW_DIR) + "/nr4a3-program-map.md" + target
    path, _, frag = target.partition("#")
    if path.startswith("/"):
        return target
    resolved = posixpath.normpath(posixpath.join(_MAP_DIR, path))
    out = posixpath.relpath(resolved, _VIEW_DIR)
    return out + ("#" + frag if frag else "")


def rebase(text):
    """Rewrite a cell's roadmap-relative links so they resolve from the view's own directory. PURE."""
    return _LINK.sub(lambda m: "](%s)" % _rebase_link(m.group(1)), text)


def render_md(census):
    d = census["_derived"]
    L = []
    L.append("<!-- GENERATED by research/modalities/instrument_census.py -- DO NOT HAND-EDIT. -->")
    L.append("<!-- Regenerate: python3 research/modalities/instrument_census.py -->")
    L.append("# The instrument census")
    L.append("")
    L.append("**Generated from [`nr4a3-program-map.md`](../manuscripts/nr4a3-program-map.md) sections 3.1 "
             "and 3.2. Do not hand-edit; the roadmap is the one home of every verdict.** Machine copy: "
             "[`instrument-census.json`](instrument-census.json).")
    L.append("")
    L.append("Its reason for existing (roadmap §10.1a `Q18`): the program's instrument record was prose, so "
             "every count of it was narrated rather than counted, and the coverage holes could not be "
             "enumerated by anyone who had not read the whole page.")
    L.append("")
    L.append("## Counts — derived from the columns below, not typed")
    L.append("")
    L.append("| quantity | value |")
    L.append("|---|---|")
    L.append("| instruments in §3.1 | **%d** |" % d["n_instruments"])
    L.append("| ⛔ instruments with **no known-answer test of their own** | **%d** — %s |"
             % (d["n_without_a_known_answer_test"],
                ", ".join("`%s`" % i for i in d["instruments_without_a_known_answer_test"]) or "—"))
    L.append("| requirements in the §3.2 matrix | **%d** |" % d["n_requirements"])
    for k, v in d["by_verdict_class"].items():
        L.append("| instruments classed `%s` | **%d** — %s |" % (k, len(v), ", ".join("`%s`" % i for i in v)))
    for k, v in d["requirements_by_hole_class"].items():
        L.append("| requirements classed `%s` | **%d** — %s |" % (k, len(v), ", ".join("`%s`" % i for i in v)))
    L.append("")
    L.append("## Every instrument, its test, its result and its scope")
    L.append("")
    L.append("| id | instrument | known-answer test | has a test? | result | ⚠ scope — what it does NOT "
             "support | state (verbatim) | class | serves |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in census["instruments"]:
        L.append("| **%s** | %s | %s | %s | %s | %s | %s | `%s` | %s |" % (
            r["id"], rebase(r["instrument"]), rebase(r["known_answer_test"]),
            "yes" if r["has_known_answer_test"] else "⛔ **no**",
            rebase(r["result"]), rebase(r["scope_limit"]), rebase(r["state_verbatim"]),
            r["verdict_class"],
            " ".join("`%s`" % s for s in r["serves"]) or "—"))
    L.append("")
    L.append("## Coverage — which requirement rests on which instrument")
    L.append("")
    L.append("| requirement | instruments | best available status | hole? | class |")
    L.append("|---|---|---|---|---|")
    for c in census["coverage"]:
        L.append("| %s | %s | %s | %s | `%s` |" % (
            rebase(c["requirement_verbatim"]), " ".join("`%s`" % i for i in c["instruments"]) or "—",
            rebase(c["best_available_status"]), rebase(c["hole_verbatim"]), c["hole_class"]))
    L.append("")
    return "\n".join(L) + "\n"


def main(argv):
    census = build()
    md = render_md(census)
    js = json.dumps(census, indent=2, ensure_ascii=False) + "\n"
    if "--check" in argv:
        bad = []
        for path, want in ((OUT_JSON, js), (OUT_MD, md)):
            try:
                have = open(path, encoding="utf-8").read()
            except OSError:
                bad.append("%s is MISSING" % os.path.relpath(path, ROOT))
                continue
            if have != want:
                bad.append("%s has DRIFTED from the roadmap -- regenerate it"
                           % os.path.relpath(path, ROOT))
        if bad:
            print("instrument_census --check FAILED:\n  " + "\n  ".join(bad))
            return 1
        print("instrument_census --check: OK (%d instruments, %d requirements)"
              % (census["_derived"]["n_instruments"], census["_derived"]["n_requirements"]))
        return 0
    open(OUT_JSON, "w", encoding="utf-8").write(js)
    open(OUT_MD, "w", encoding="utf-8").write(md)
    print("instrument_census: wrote %d instruments, %d requirements"
          % (census["_derived"]["n_instruments"], census["_derived"]["n_requirements"]))
    print(json.dumps(census["_derived"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
