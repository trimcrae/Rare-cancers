#!/usr/bin/env python3
"""No figure's drawn text may carry markdown emphasis, because SVG renders it verbatim.

⛔ WHY THIS EXISTS. On 2026-08-19 a figure-key relabelling in `aso_gap_length_figure.py` wrote
`"*NR4A3* gap bases"` into an axis key. In prose those asterisks italicise a gene symbol; in an SVG
`<text>` element they are two asterisks, and the deposited figure would have printed them. Every
other figure in this repository sets gene symbols plain for exactly that reason, so the defect was
invisible against the file it was written in and obvious against the convention beside it.

⚠ THIS IS THE CHEAP HALF OF A CLASS. The expensive half — a caption whose claim the drawing does not
support — needs a reader. This catches only the part a string search can: markdown that leaked from
a manuscript-editing habit into a drawing surface that has no markdown.

The scan is over the committed SVGs rather than the generators, because the generator is not what
gets deposited and a label can be assembled from pieces no grep of the source would join.
"""
from __future__ import annotations

import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(os.path.dirname(HERE), "figures")

#: Text nodes only. Attribute values and path data may legitimately contain almost anything.
TEXT_NODE = re.compile(r"<(text|tspan)\b[^>]*>(.*?)</\1>", re.S)

#: Emphasis around a word, a backtick span, or a bracketed link. Bare `*` as a footnote marker or a
#: multiplication sign is legitimate and must not be caught, so the pattern requires a closing mark.
MARKDOWN = [
    (re.compile(r"\*\*[^*\n]+\*\*"), "bold (**...**)"),
    (re.compile(r"(?<!\*)\*[^*\s][^*\n]*\*(?!\*)"), "italic (*...*)"),
    (re.compile(r"_[A-Za-z0-9][^_\n]*_"), "underscore emphasis (_..._)"),
    (re.compile(r"`[^`\n]+`"), "code span (`...`)"),
    (re.compile(r"\[[^\]\n]+\]\([^)\n]*\)"), "link ([...](...))"),
]


#: ⛔ THE EXPECTED SET IS DERIVED, NOT COUNTED TODAY (2026-08-19, lane C2). `if not out: skip`
#: meant a figures directory that had lost its SVGs — a half-finished regeneration, a bad merge —
#: reported PASS for every drawn label in the deposit. The figures the deposit actually has are
#: named by the committed provenance artifact, so the floor moves with the paper rather than with
#: whatever happens to be on disk when the guard runs.
PROVENANCE = os.path.join(FIGS, "aso-figure-provenance.json")


def _expected_aso_figures():
    if not os.path.exists(PROVENANCE):
        pytest.fail(f"the figure provenance artifact is missing at {PROVENANCE}; it is committed, "
                    "and it is what names the figures this guard has to cover.")
    return sorted(json.load(open(PROVENANCE, encoding="utf-8"))["figures"])


def _svgs():
    if not os.path.isdir(FIGS):
        pytest.fail(f"the figures directory is missing at {FIGS}; it is committed, and no drawn "
                    "label in the deposit is checked without it.")
    out = [os.path.join(FIGS, n) for n in sorted(os.listdir(FIGS)) if n.endswith(".svg")]
    missing = [name for name in _expected_aso_figures()
               if os.path.join(FIGS, name + ".svg") not in out]
    if missing:
        pytest.fail(f"the provenance artifact names {missing} but no SVG is on disk for them, so "
                    "their labels are unchecked. Regenerate the figures rather than letting the "
                    "guard shrink to what happens to be present.")
    assert out, "no figure SVG at all — see above; this parametrisation would otherwise be empty"
    return out


@pytest.mark.parametrize("path", _svgs(), ids=os.path.basename)
def test_no_drawn_label_contains_markdown(path):
    body = open(path, encoding="utf-8").read()
    offenders = []
    for _tag, inner in TEXT_NODE.findall(body):
        flat = re.sub(r"<[^>]+>", "", inner)
        for pattern, what in MARKDOWN:
            for hit in pattern.findall(flat):
                offenders.append(f"{what}: {hit!r}")
    assert not offenders, (
        f"{os.path.basename(path)} draws markdown that an SVG renderer prints verbatim — "
        "italicise by convention (plain gene symbols) or with font-style, never with asterisks:\n  "
        + "\n  ".join(offenders))
