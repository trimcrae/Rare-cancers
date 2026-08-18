"""Justified body lines must not blow out further than the accepted baseline.

⛔ WHY THIS IS A CEILING AND NOT A FIX. Three blind screens have flagged inter-word rivers in the
built PDF: justified lines immediately before an unbreakable 16-, 18- or 20-mer are stretched to
roughly three times the normal word gap, because the sequence token that follows cannot be broken.
It cannot be broken on purpose — splitting a printed oligonucleotide across a line break is the
wrong-reagent hazard the whole deposit is built to prevent, and `test_code_spans_never_break_a_
sequence` enforces that separately.

★ TWO CONTENT-SAFE LEVERS WERE TRIED AND NEITHER HELPED (2026-08-19), which is why the defect is
accepted rather than argued away. Measured over body prose only:

    baseline                        1,520 lines, median 3.12 pt, worst 11.02 pt, 20 >2x, 3 >3x
    hyphenate-limit-chars: 5 2 2    identical on every figure — a no-op in this Chromium
    .seq { font-size: 0.94em }      worst 10.95 pt, 22 >2x, 8 >2.5x, 5 >3x — MIXED, neither an
                                    improvement nor a clear regression; narrowing the token
                                    re-wraps paragraphs and relocates the stretch rather than
                                    removing it

⚠ AN EARLIER VERSION OF THIS NOTE CALLED THE SECOND RESULT "STRICTLY WORSE". It was not. That
reading came from an instrument that also measured table lines, whose tight 6.9-9 pt gaps drag the
median down and move every threshold with it. Both levers land within noise of the baseline — a
stronger form of the same conclusion: the cause is the unbreakable token, and nothing that leaves
the token intact shifts it.

★★ THE METRIC IS THE WORST LINE AND THE 2x COUNT, NOT THE 3x COUNT. Six lines cluster between 9.14
and 9.57 pt while 3x the median is 9.36 — so the 3x tally flips between 1 and 5 on rounding alone
and measures the cluster's position, not the typography. A guard whose value swings without the
artefact changing is noise wearing the costume of a threshold.

`hyphens: auto` is already on and the root element already carries `lang="en"` (without it Chromium
declines to hyphenate at all, which would have been the real bug — it was checked, and it is set).

⚠ SO THIS TEST DOES NOT ASSERT THE DEFECT IS GONE. It pins how bad it is allowed to get, so that a
future typographic or content change cannot quietly multiply the blown-out lines the way the
font-size experiment did. A build that IMPROVES on the baseline should tighten these numbers.
"""
from __future__ import annotations

import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
DEPOSIT_PDF = os.path.join(MANUSCRIPTS, "aso",
                           "fusion-junction-aso-research-article-manuscript.pdf")

#: Baseline worst line is 11.02 pt against a 3.12 pt median. 13 pt leaves room for one new sequence
#: citation landing badly without licensing a visibly worse page.
MAX_GAP_PT = 13.0
#: Baseline is 20 lines above 2x the median. 26 is the ceiling on the broader, milder class.
MAX_LINES_ABOVE_2X = 26


def _line_gaps():
    try:
        import pymupdf
    except ImportError:                                     # pragma: no cover - env dependent
        try:
            import fitz as pymupdf
        except ImportError:
            pytest.skip("pymupdf is not installed in this sandbox")
    if not os.path.exists(DEPOSIT_PDF):
        pytest.fail(f"the deposit PDF is missing: {DEPOSIT_PDF}")
    doc = pymupdf.open(DEPOSIT_PDF)
    rows = []
    for pno in range(len(doc)):
        page = doc[pno]
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block["lines"]:
                #: ⛔ BODY PROSE ONLY, BY FONT SIZE. Table and caption lines are set at 6.9-9 pt with
                #: tight gaps; including them pulled the median from 2.92 to 3.20 pt and moved the
                #: 3x threshold by 0.8 pt, which is enough to change the verdict. The defect being
                #: bounded here is justified BODY text before an unbreakable sequence, so the
                #: measurement has to be taken over that population and no other.
                sizes = [sp["size"] for sp in line["spans"] if sp["text"].strip()]
                if not sizes or max(sizes) < 10:
                    continue
                words = [w for w in page.get_text("words", clip=pymupdf.Rect(line["bbox"]))
                         if w[4].strip()]
                if len(words) < 4:
                    continue
                words.sort(key=lambda w: w[0])
                gaps = [words[i + 1][0] - words[i][2] for i in range(len(words) - 1)]
                gaps = [g for g in gaps if g > 0]
                if gaps:
                    rows.append((sum(gaps) / len(gaps), pno + 1,
                                 " ".join(w[4] for w in words)[:70]))
    return rows


def test_justification_does_not_degrade_past_the_accepted_baseline():
    rows = _line_gaps()
    assert rows, "no justified lines were measured — the extraction is broken, not the PDF"
    median = sorted(r[0] for r in rows)[len(rows) // 2]
    over3 = sorted((r for r in rows if r[0] > 3 * median), reverse=True)
    over2 = [r for r in rows if r[0] > 2 * median]

    worst = over3[0] if over3 else max(rows)
    detail = "\n  ".join(f"{g:6.2f} pt  p{p}  {t}" for g, p, t in sorted(rows, reverse=True)[:6])
    assert worst[0] <= MAX_GAP_PT, (
        f"the worst justified body line stretches to {worst[0]:.2f} pt against a median of "
        f"{median:.2f} pt, past the {MAX_GAP_PT} pt ceiling:\n  {detail}\n\n"
        "Do NOT fix this by letting sequence tokens break — that is the wrong-reagent hazard. Two "
        "content-safe levers were measured and neither helped (hyphenate-limit-chars: no effect; a "
        "smaller .seq font: within noise). If a change caused this, revert it.")
    assert len(over2) <= MAX_LINES_ABOVE_2X, (
        f"{len(over2)} body lines exceed 2x the median inter-word gap ({2*median:.2f} pt); the "
        f"measured baseline is 20 and the ceiling is {MAX_LINES_ABOVE_2X}.")
