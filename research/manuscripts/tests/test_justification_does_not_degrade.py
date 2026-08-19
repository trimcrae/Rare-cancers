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

⛔⛔ AND UNTIL 2026-08-19 IT PINNED NOTHING IN CI, BECAUSE ITS INSTRUMENT WAS NEVER INSTALLED THERE.
The measurement ran through `pymupdf`, which `.github/workflows/tests.yml` does not install — its
pip line is `pytest numpy scipy pymbar rdkit pyyaml boto3 jsonschema biopython pdfminer.six`. So
every CI run took the `pytest.skip("pymupdf is not installed in this sandbox")` branch and reported
a green that measured no page of any PDF. That is the exact fail-quiet shape this repository's own
`test_pdf_text_layer_is_orderable` docstring refuses: "A guard that cannot run is not a guard that
passed." The instrument is now `pdfminer.six`, which CI does install, and a missing import is a
failure rather than a skip.

⚠ CHANGING THE INSTRUMENT MOVED THE READINGS, so the pins below were re-measured rather than
carried across. On one and the same build, the two engines disagree because they group characters
into words differently:

    pymupdf     1,848 lines, median 3.139 pt, 30 over 2x -> 16.23/1000, worst 10.88 pt, 8 over 9 pt
    pdfminer    1,850 lines, median 3.144 pt, 32 over 2x -> 17.30/1000, worst 12.16 pt, 10 over 9 pt

Neither is "right"; they are two instruments. What matters is that the pins and the readings come
from the SAME one, which is why only pdfminer is used now and why the numbers below are its.
"""
from __future__ import annotations

import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
DEPOSIT_PDF = os.path.join(MANUSCRIPTS, "aso",
                           "fusion-junction-aso-research-article-manuscript.pdf")

#: ⛔ WHICH BUILD EVERY NUMBER BELOW WAS MEASURED ON. `build_submission_pdf.py` writes a stamp
#: beside each PDF recording the sha256 of every document it rendered; this is the manuscript hash
#: it held when these ceilings were set. It is recorded rather than asserted — a rebuild is
#: expected and `test_the_deposited_pdfs_are_not_stale` is what enforces currency — but it is the
#: one fact that makes "the current build" a checkable statement six weeks from now.
MEASURED_ON_ARTICLE_SHA256 = "669f7465413911641ab6e73c3d03232ab3d6e3da07313f7046e958b72560d516"

#: Baseline worst line is 11.02 pt against a 3.12 pt median. 13 pt leaves room for one new sequence
#: citation landing badly without licensing a visibly worse page. This one stays ABSOLUTE: a single
#: page with a visible river is a defect however long the paper is.
#:
#: ⚠ HEADROOM IS NOW 0.84 pt, NOT 2 pt, because the instrument changed: pdfminer reads the worst
#: line on this build at 12.16 pt where pymupdf read 10.88. The ceiling is deliberately NOT raised
#: to restore the old-looking margin — the page has not changed, only the ruler, and moving a
#: ceiling to preserve a feeling of headroom is how a threshold stops measuring anything.
MAX_GAP_PT = 13.0

#: ⛔ A RATE, NOT A COUNT (2026-08-19). This was `MAX_LINES_ABOVE_2X = 26` against a baseline of 20
#: lines. A round of substantive corrections grew the body from 1,520 measured lines to 1,721 and
#: the tally went 20 -> 26, landing exactly on the ceiling — so the next legitimate sentence would
#: have failed the build for adding length rather than for degrading typography. An absolute count
#: over a growing document measures two things at once and cannot separate them.
#:
#: ⚠ AND THE CONVERSION IS NOT AN AMNESTY. Normalised, three builds now read 13.2, 15.1 and 16.9
#: blown lines per 1,000 body lines. The rate is rising, it is being recorded rather than absorbed,
#: and the ceiling has been moved twice in one working session — which is a smell, so what is known
#: and what is not is written down here rather than asserted.
#:
#: ⛔ THE OBVIOUS EXPLANATION WAS TESTED AND REFUTED. The hypothesis was that new prose naming
#: sequences, accessions and filenames drives it, each unbreakable token stretching the line before
#: it. Measured on the 16.9 build: of 30 blown lines only 13 carry such a token and 17 do not. So
#: the cause is NOT simply identifier density, and the metric must not be split into an
#: "identifier" class and a "real" class on that basis — that would be loosening the pattern to fit
#: a story the data does not support.
#:
#: ★ WHAT DOES WORK, MEASURED: rewording ONE sentence to drop a redundant backticked junction label
#: took the rate from 18.0 to 16.9. The lever is real, it is per-line, and it is laborious.
#:
#: ⛔⛔ RE-SET DOWNWARD 2026-08-19. The ceiling had been left at 17.5 — "half a point of headroom on
#: 16.9" — while the build it was guarding measured 16.23 (pymupdf) and the baseline it was
#: supposed to defend was 13.2. Against that baseline 17.5 licensed a 33% degradation, and against
#: the build it licensed 8%, and neither of those was a decision anybody took: the ceiling simply
#: outlived the build it was set for. It is now set against the build named above, measured with
#: the instrument that ships in CI: 32 of 1,850 body lines = 17.30 per 1,000, plus one blown line
#: of headroom (0.54 per 1,000 at this document length), rounded to 17.9.
#:
#: ⚠ A NUMBER THAT NEEDS RE-MEASURING WHENEVER THE PDF IS REBUILT. It is a property of a rendered
#: artefact, so it cannot be derived at run time from anything else — the only honest maintenance
#: is to re-measure and re-state it, spending the rewording lever rather than the ceiling.
MAX_BLOWN_LINES_PER_1000 = 17.9

#: ⛔ THE ABSOLUTE COMPANION, AND THE HOLE IT CLOSES. Every threshold above is stated as a multiple
#: of the median gap, so a change that stretches EVERY body line equally moves the median with it
#: and the ratio reports nothing — the page gets visibly looser and the guard stays green. A gap
#: measured in points cannot be defeated that way. 9 pt is roughly three times the current median
#: and is where the eye starts reading a river rather than a word space; on the build named above,
#: 10 of 1,850 lines are over it (5.41 per 1,000), so the ceiling is that plus one line.
MAX_WIDE_GAP_PT = 9.0
MAX_WIDE_LINES_PER_1000 = 6.0

#: A line must have this many words before its inter-word gaps mean anything: two words give one
#: gap, and one gap is the last line of a justified paragraph, which is not stretched at all.
MIN_WORDS_PER_MEASURED_LINE = 4

#: Body prose is set at 10 pt or larger; tables and captions at 6.9-9 pt. See the note in
#: `_line_gaps` for why the population has to be split this way.
MIN_BODY_FONT_PT = 10


def _line_gaps():
    """(mean inter-word gap in pt, page number, first 70 characters) for every body-prose line.

    ⛔ NOT A SKIP IF THE PARSER IS MISSING. `pdfminer.six` is on this repository's CI install line
    precisely so that PDF guards can run there, and the same reasoning applies here: the test needs
    no credentials and no network, so a missing import is something to install, not to skip.
    """
    try:
        from pdfminer.high_level import extract_pages
        from pdfminer.layout import LAParams, LTChar, LTTextContainer, LTTextLine
    except ImportError as exc:                              # pragma: no cover - env dependent
        pytest.fail(
            f"pdfminer.six is not importable ({exc}), so nothing measured this PDF. CI installs it "
            "on purpose — a guard that cannot run is not a guard that passed. Install it rather "
            "than restoring a skip.")
    if not os.path.exists(DEPOSIT_PDF):
        pytest.fail(f"the deposit PDF is missing: {DEPOSIT_PDF}")

    rows = []
    for pno, page in enumerate(extract_pages(DEPOSIT_PDF, laparams=LAParams()), start=1):
        for element in page:
            if not isinstance(element, LTTextContainer):
                continue
            for line in element:
                if not isinstance(line, LTTextLine):
                    continue
                chars = [c for c in line if isinstance(c, LTChar)]
                #: ⛔ BODY PROSE ONLY, BY FONT SIZE. Table and caption lines are set at 6.9-9 pt with
                #: tight gaps; including them pulled the median from 2.92 to 3.20 pt and moved the
                #: 3x threshold by 0.8 pt, which is enough to change the verdict. The defect being
                #: bounded here is justified BODY text before an unbreakable sequence, so the
                #: measurement has to be taken over that population and no other.
                sizes = [c.size for c in chars if c.get_text().strip()]
                if not sizes or max(sizes) < MIN_BODY_FONT_PT:
                    continue
                words, current = [], None
                for char in chars:
                    if char.get_text().isspace():
                        if current:
                            words.append(current)
                            current = None
                    elif current is None:
                        current = [char.x0, char.x1, char.get_text()]
                    else:
                        current[1] = max(current[1], char.x1)
                        current[2] += char.get_text()
                if current:
                    words.append(current)
                if len(words) < MIN_WORDS_PER_MEASURED_LINE:
                    continue
                words.sort(key=lambda w: w[0])
                gaps = [words[i + 1][0] - words[i][1] for i in range(len(words) - 1)]
                gaps = [g for g in gaps if g > 0]
                if gaps:
                    rows.append((sum(gaps) / len(gaps), pno,
                                 " ".join(w[2] for w in words)[:70]))
    return rows


def _check(rows):
    """The verdict, over a list of (gap, page, text) rows — separated from the extraction so the
    defect each ceiling exists to catch can be constructed and shown to trip it."""
    assert rows, "no justified lines were measured — the extraction is broken, not the PDF"
    median = sorted(r[0] for r in rows)[len(rows) // 2]
    over2 = [r for r in rows if r[0] > 2 * median]
    wide = [r for r in rows if r[0] > MAX_WIDE_GAP_PT]
    worst = max(rows)
    detail = "\n  ".join(f"{g:6.2f} pt  p{p}  {t}" for g, p, t in sorted(rows, reverse=True)[:6])

    assert worst[0] <= MAX_GAP_PT, (
        f"the worst justified body line stretches to {worst[0]:.2f} pt against a median of "
        f"{median:.2f} pt, past the {MAX_GAP_PT} pt ceiling:\n  {detail}\n\n"
        "Do NOT fix this by letting sequence tokens break — that is the wrong-reagent hazard. Two "
        "content-safe levers were measured and neither helped (hyphenate-limit-chars: no effect; a "
        "smaller .seq font: within noise). If a change caused this, revert it.")

    rate = 1000 * len(over2) / len(rows)
    assert rate <= MAX_BLOWN_LINES_PER_1000, (
        f"{len(over2)} of {len(rows)} body lines exceed 2x the median inter-word gap "
        f"({2*median:.2f} pt) — {rate:.2f} per 1,000 against a ceiling of "
        f"{MAX_BLOWN_LINES_PER_1000} and a baseline of 13.2. This is a rate, so the paper getting "
        "longer cannot trip it; something made the typography worse. The usual cause is new prose "
        "naming a sequence or an accession, whose unbreakable token stretches the line before it — "
        "moving the token off a line end fixes it, breaking the token never does.")

    wide_rate = 1000 * len(wide) / len(rows)
    assert wide_rate <= MAX_WIDE_LINES_PER_1000, (
        f"{len(wide)} of {len(rows)} body lines carry a mean inter-word gap above "
        f"{MAX_WIDE_GAP_PT} pt — {wide_rate:.2f} per 1,000 against a ceiling of "
        f"{MAX_WIDE_LINES_PER_1000}. This one is measured in POINTS, not in multiples of the "
        "median, so it stays awake when a change loosens every line at once and carries the median "
        f"up with it (the median here is {median:.2f} pt). Check the column width, the font size "
        "and the word-spacing before looking for a new unbreakable token.")
    return {"lines": len(rows), "median": median, "over2": len(over2),
            "rate": rate, "wide": len(wide), "wide_rate": wide_rate, "worst": worst[0]}


def test_justification_does_not_degrade_past_the_accepted_baseline():
    _check(_line_gaps())
