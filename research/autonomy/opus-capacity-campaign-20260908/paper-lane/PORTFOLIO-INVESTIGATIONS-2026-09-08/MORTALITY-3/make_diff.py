#!/usr/bin/env python3
"""Build the UNAPPLIED unified diff retiring the manuscript's Sec 4.2 generalisation.

Writes only into this lane. The manuscript itself is never modified.
"""
import difflib, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[6]
REL = "research/manuscripts/emc-mortality-mechanisms-paper.md"
src = (ROOT / REL).read_text().splitlines(keepends=True)

OLD = """For ultra-rare cancers generally, the implication is that cause-of-death recording, which costs
nothing at the point of follow-up, determines whether a disease's evidence base can support the
questions its research programme asks.
"""

NEW = """Whether that record is distinctive to this disease, rather than ordinary for a literature written
mostly as case reports, is a separate question, and it can be asked inside the same retrieval. The
128 enumerated papers that are not about this disease contributed 461 death-cue sentences against
this disease's 116. Taken crudely, a strict lexicon fixed in advance names a physiological terminal
event in 4 of the 116 (3.45 per cent) and in 3 of the 461 (0.65 per cent), two-sided Fisher
p = 0.033. That contrast does not survive the difference in what the two sets of papers are. Study
type was classified by a rule written and frozen before any rate was computed: 53 per cent of the
papers about this disease are case reports or case series against 20 per cent of the others, and in
both sets terminal events are named almost only where a death is narrated rather than tabulated.
With study type held fixed, an exact conditional test stratified on the five study types gives
p = 0.70 (Mantel-Haenszel odds ratio 1.78), and direct standardisation moves this disease's rate
from 3.45 to 0.93 per cent on the other papers' mix of study types, and the other papers' rate from
0.65 to 1.86 per cent on this disease's.

This is a null, and it is reported as a null rather than as equality. Within case reports the counts
are 4 events against 2; a genuine two-fold difference in either direction is entirely compatible
with them, so the honest statement is that no contrast is supported, not that none exists. The unit
throughout that comparison is a sentence and not a patient: a matched sentence is not a death and a
death is not a patient, so none of those counts is a count of patients and none assigns a cause to
anyone. Study type was inferred from titles and journal names alone, with no publication-type field
and no full text available for the comparator, by a single unblinded reader; on a seeded 40-paper
hand check the rule agreed overall in 70 per cent of cases (28 of 40), with case-report precision
1.00 (9 of 9) and recall 0.90 (9 of 10).

What follows is a narrower statement than the one this section previously made. Cause-of-death
recording costs nothing at the point of follow-up and determines what this disease's evidence base
can answer, which is the finding above. That this disease's record is distinctively silent by
comparison with other literatures is not shown here, in either direction, and no comparator outside
this single retrieval has been measured.
"""

text = "".join(src)
assert text.count(OLD) == 1, "anchor paragraph not found exactly once"
new_text = text.replace(OLD, NEW)
dst = new_text.splitlines(keepends=True)

diff = difflib.unified_diff(src, dst, fromfile="a/" + REL, tofile="b/" + REL, n=3)
out = pathlib.Path(__file__).with_name("section-4.2-composition-effect.diff")
out.write_text("".join(diff))
print("wrote", out.name, "lines:", len(out.read_text().splitlines()))
