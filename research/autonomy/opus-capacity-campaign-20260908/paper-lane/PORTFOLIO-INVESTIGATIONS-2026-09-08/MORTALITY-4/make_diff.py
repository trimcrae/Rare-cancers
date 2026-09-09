#!/usr/bin/env python3
"""Build the UNAPPLIED unified diff for section 6 of
research/manuscripts/emc-mortality-mechanisms-paper.md.

It replaces the final sentence of the Conclusion, which restates in softer, number-free form the
same generalisation MORTALITY-3's section 4.2 diff withdraws, with a version scoped to this disease
plus one sentence that reports the comparator result as the null it is.

This script NEVER writes to the manuscript. It reads it, asserts its anchor occurs exactly once,
and writes only section-6-conclusion-scope.diff inside this lane.
"""
import difflib, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[6]
REL = "research/manuscripts/emc-mortality-mechanisms-paper.md"
SRC = ROOT / REL
OUT = pathlib.Path(__file__).with_name("section-6-conclusion-scope.diff")

OLD = """those deaths occur at approximately background rate. The survival available to antitumour therapy is
6.7 percentage points in localised disease and 31.0 in metastatic disease at three years. Research
prioritisation in this disease should reflect that difference, and cause-of-death recording should be
treated as a measurement that determines what its evidence base can answer.
"""

NEW = """those deaths occur at approximately background rate. The survival available to antitumour therapy is
6.7 percentage points in localised disease and 31.0 in metastatic disease at three years. Research
prioritisation in this disease should reflect that difference, and in this disease cause-of-death
recording should be treated as a measurement that determines what its own evidence base can answer.
Whether this disease's record is more silent than other literatures' is not established here. The one
comparator available inside the same retrieval supports no contrast in either direction once study
type is held fixed, and that is a null rather than a demonstration of equality: it rests on 4 flagged
sentences against 2 within case reports, with a sentence and not a patient as the unit, which is too
little to establish sameness as well as too little to establish a difference.
"""


def main():
    text = SRC.read_text()
    n = text.count(OLD)
    if n != 1:
        print(f"ABORT: anchor occurs {n} times, expected exactly 1", file=sys.stderr)
        return 2
    new_text = text.replace(OLD, NEW)
    diff = difflib.unified_diff(text.splitlines(True), new_text.splitlines(True),
                                fromfile=f"a/{REL}", tofile=f"b/{REL}", n=3)
    d = "".join(diff)
    OUT.write_text(d)
    sys.stdout.write(d)
    print(f"\n[wrote {OUT.name}; manuscript NOT modified]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
