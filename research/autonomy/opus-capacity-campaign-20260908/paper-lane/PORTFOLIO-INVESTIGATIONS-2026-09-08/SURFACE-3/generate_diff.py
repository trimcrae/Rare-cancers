#!/usr/bin/env python3
"""SURFACE-3: build an UNAPPLIED unified diff correcting category (a) claims -- prose that
asserts a normal-tissue/vital-tissue FILTER operated -- to state that the vital-tissue screen
produced no input and vital-tissue status is UNKNOWN.  Superseded wording is preserved verbatim
in a dated correction note, never erased.  No file outside this lane is written."""
import difflib, os, sys

ROOT = os.path.abspath(__file__)
for _ in range(7):
    ROOT = os.path.dirname(ROOT)
DATE = "2026-09-09"

EDITS = [
    # (path, old_exact, new)
    ("research/manuscripts/surface-targets/emc-surface-target-outreach.md",
     'selectivity test and a hard normal-tissue-window filter, most "obvious" candidates fall away — the field-default\n'
     '**B7-H3 is not selective** in the data, and CD56/CDH11/others carry specific normal-tissue liabilities. The two\n',
     'selectivity test and a normal-tissue **category** annotation, most "obvious" candidates fall away — the\n'
     'field-default **B7-H3 is not selective** in the data, and CD56/CDH11/others carry blood-category normal-tissue\n'
     'liability labels. ⚠ The annotation\'s vital-tissue screen **produced no input and never ran**: the quantitative\n'
     'per-tissue nTPM field is null for all 45 classified records, so the vital-tissue status of every antigen here is\n'
     '**UNKNOWN** — neither absent nor present, and no window is filtered on it. The two\n'
     '\n'
     '⛔ *Superseded, retained (' + DATE + '): this sentence read "with a rigorous selectivity test and a hard\n'
     'normal-tissue-window filter, most \\"obvious\\" candidates fall away — the field-default **B7-H3 is not selective**\n'
     'in the data, and CD56/CDH11/others carry specific normal-tissue liabilities." "Hard filter" asserted a\n'
     'vital-tissue exclusion that the screen never performed.*\n'
     '\n'),

    ("research/manuscripts/surface-targets/emc-surface-target-outreach.md",
     'self-critical: with a rigorous selectivity test and a hard normal-tissue-window filter, most candidates fall\n'
     'away — the field-default **B7-H3 is not selective**, and CD56/CDH11 carry normal-tissue liabilities. The leads\n',
     'self-critical: with a rigorous selectivity test and a normal-tissue **category** annotation, most candidates fall\n'
     'away — the field-default **B7-H3 is not selective**, and CD56/CDH11 carry blood-category liability labels.\n'
     '⚠ The annotation\'s vital-tissue screen produced no input and never ran (per-tissue nTPM null on all 45\n'
     'classified records), so vital-tissue status is **UNKNOWN** for every antigen named here. The leads\n'
     '\n'
     '⛔ *Superseded, retained (' + DATE + '): this sentence read "with a rigorous selectivity test and a hard\n'
     'normal-tissue-window filter, most candidates fall away — the field-default **B7-H3 is not selective**, and\n'
     'CD56/CDH11 carry normal-tissue liabilities."*\n'
     '\n'),

    ("research/manuscripts/surface-targets/emc-surface-target-redteam.md",
     'enrichment by ≤ 0.13 log2TPM, no sign flips); (2) a hard normal-tissue\n'
     'window under which **most candidates are liabilities**, so the analysis mainly refines priorities and flags\n'
     'dangers rather than declaring winners; and (3) a grounded SSTR2/DOTATATE neuroendocrine hypothesis the first\n',
     'enrichment by ≤ 0.13 log2TPM, no sign flips); (2) a normal-tissue **category annotation** under which **most\n'
     'candidates carry liability labels** — labels set by the blood-cell branch alone, because the vital-tissue\n'
     'branch produced no input and never ran (per-tissue nTPM null on all 45 classified records), leaving every\n'
     'antigen\'s vital-tissue status **UNKNOWN** — so the analysis mainly refines priorities and flags\n'
     'annotation-level dangers rather than declaring winners; and (3) a grounded SSTR2/DOTATATE neuroendocrine hypothesis the first\n'),

    ("research/manuscripts/README.md",
     '  rigorous selectivity + a hard normal-tissue window show **B7-H3 is not selective** and the selective\n'
     '  candidates carry window liabilities, so the honest result refines priorities and nominates a neuroendocrine\n',
     '  rigorous selectivity + a normal-tissue **category annotation** show **B7-H3 is not selective** and the\n'
     '  selective candidates carry window liability **labels** — set by the blood-cell branch alone, since the\n'
     '  vital-tissue screen produced no input and never ran, leaving vital-tissue status **UNKNOWN** for every\n'
     '  classified record — so the honest result refines priorities and nominates a neuroendocrine\n'),
]

chunks = []
by_file = {}
for path, old, new in EDITS:
    by_file.setdefault(path, []).append((old, new))

ok = True
for path, edits in by_file.items():
    full = os.path.join(ROOT, path)
    src = open(full, encoding="utf-8").read()
    dst = src
    for old, new in edits:
        if dst.count(old) != 1:
            sys.stderr.write("ANCHOR NOT UNIQUE (%d) in %s:\n%r\n" % (dst.count(old), path, old[:80]))
            ok = False
            continue
        dst = dst.replace(old, new)
    d = difflib.unified_diff(src.splitlines(True), dst.splitlines(True),
                             fromfile="a/" + path, tofile="b/" + path, n=3)
    chunks.append("diff --git a/%s b/%s\n" % (path, path) + "".join(d))

if not ok:
    sys.exit(2)
out = "".join(chunks)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "UNAPPLIED-vital-tissue-unknown.diff"), "w", encoding="utf-8").write(out)
sys.stdout.write(out)
