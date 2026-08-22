"""Every sequence in the deposited PDF must survive a copy-paste, and the PDF must say where the
canonical machine-readable copy is.

⛔ WHY, AND IT IS THE PROCESS GAP RATHER THAN A TYPO. Seven adversarial rounds, a firewalled cold
reader and an adversarial reviewer with artifact access all ran against the MARKDOWN. Not one read
the built PDF — which is the only artifact a depositor uploads and a screener opens. So an entire
defect class was structurally invisible, and the paper was called deposit-ready while it carried one.

MEASURED 2026-08-17 by extracting the text layer of the built manuscript PDF: a sequence in a table
cell arrives as a bare base string with NO `5′-`/`-3′` delimiters, immediately adjacent to a numeric
cell —

    CAGGGCATATCATCAAACCA   3   123   6   189 ...

so whether the sequence and the next column fuse is a property of the READER's extractor, not of the
document. One extractor returned `5′-GGGCATATCATCAAAC3′3 8 123 → 6`: a 16-mer carrying a trailing
digit with its delimiter lost. A reader who pastes that into a synthesis order has bought a molecule
about which nothing in this paper is true, and bioRxiv's own full-text conversion inherits the same
text layer.

⚠ THIS GUARD READS THE PDF, NOT THE MARKDOWN, ON PURPOSE. Checking the source is what missed it. The
markdown was correct at every point; the defect was created by typesetting.

⛔ IT MUST NOT SKIP WHEN ITS EXTRACTOR IS ABSENT. `tests.yml` already states this repository's
position, in the comment on its own install line: "The test CAN run anywhere — it needs no
credentials and touches no network — so the fix is to install the dependency, not to skip the test.
A guard that cannot run is not a guard that passed." `pdfminer.six` is installed in CI for exactly
that reason, and a missing import fails here rather than passing quietly.
"""
import csv
import hashlib
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ASO = os.path.join(REPO, "research", "manuscripts", "aso")

#: BOTH BUILT PDFs, and covering only one of them was itself a gap (found 2026-08-17, by the author
#: asking "on ANY of the PDF formats?"). The submission-format build is what bioRxiv asks for and what
#: a depositor uploads; the journal-format build is tracked, ships with the repository, and prints the
#: SAME orderable sequences through a DIFFERENT typesetting path — two columns, floats placed at first
#: citation, a narrower measure. Two columns is the layout MORE likely to fuse a cell with its
#: neighbour, so guarding only the single-column build guarded the easier case.
#: ⚠ Measured when this was parametrised: both builds were already clean — 155 delimited tokens each,
#: zero fused, zero split, zero undelimited. The gap was in ENFORCEMENT, not in the artifacts, which
#: is the kind of gap that stays invisible until the day something regresses.
#: ⛔ BOTH PAPERS, SINCE ROUND 10. Both keys named the extended report, so neither of the journal
#: article's two built PDFs was read by any delimiter, fusion, split or staleness guard here — the
#: same one-of-a-pair scoping this review has now closed in four separate instruments. The journal
#: builds were clean when this was widened; again the gap was in ENFORCEMENT, not the artifacts.
PDFS = {
    "manuscript": os.path.join(ASO, "fusion-junction-aso-research-article-manuscript.pdf"),
    "journal": os.path.join(ASO, "fusion-junction-aso-research-article.pdf"),
    "journal-article": os.path.join(ASO, "fusion-junction-aso-journal-article.pdf"),
    "journal-article-manuscript": os.path.join(
        ASO, "fusion-junction-aso-journal-article-manuscript.pdf"),
}
#: The markdown each PDF is built from, so a guard can ask "did every sequence the source prints
#: survive typesetting?" instead of comparing against a count someone typed once.
SOURCES = {
    "manuscript": ("fusion-junction-aso-research-article.md",
                   "fusion-junction-aso-submission-tables.md"),
    "journal": ("fusion-junction-aso-research-article.md",
                "fusion-junction-aso-submission-tables.md"),
    "journal-article": ("fusion-junction-aso-journal-article.md",
                        "fusion-junction-aso-journal-tables.md"),
    "journal-article-manuscript": ("fusion-junction-aso-journal-article.md",
                                   "fusion-junction-aso-journal-tables.md"),
}


def _source_texts(pdf_key):
    """The markdown behind `pdf_key`. A named source that is absent is a finding, never a skip."""
    out = []
    for name in SOURCES[pdf_key]:
        path = os.path.join(ASO, name)
        assert os.path.exists(path), f"{name} is a committed source of {pdf_key} and is missing"
        out.append(open(path, encoding="utf-8").read())
    return out


#: The one a depositor uploads, for the checks that are about the deposit rather than the typesetting.
PDF = PDFS["manuscript"]
SEQ_CSV = os.path.join(ASO, "fusion-junction-aso-sequences.csv")


def _extract(path):
    try:
        from pdfminer.high_level import extract_text
    except Exception as exc:  # noqa: BLE001 - a missing extractor is a failure, never a skip
        pytest.fail(
            "pdfminer.six is not importable, so the deposited PDF's text layer is UNCHECKED. "
            "Install it (it is in tests.yml's install line) rather than skipping: a guard that "
            f"cannot run is not a guard that passed. Underlying error: {exc}")
    return extract_text(path)


def _canonical_sequences():
    with open(SEQ_CSV, encoding="utf-8") as fh:
        rows = list(csv.DictReader(ln for ln in fh if not ln.startswith("#")))
    assert rows, f"{SEQ_CSV} carries no rows"
    return {r["sequence"] for r in rows}


#: Everything the deposited PDF is built FROM. If any is newer than the PDF, the PDF is stale and
#: every assertion below is being made about a document that is not the one a depositor would upload.
_SOURCES = (
    os.path.join(ASO, "fusion-junction-aso-research-article.md"),
    os.path.join(ASO, "fusion-junction-aso-submission-tables.md"),
    os.path.join(ASO, "fusion-junction-aso-submission-references.md"),
    SEQ_CSV,
)


def test_the_deposited_pdfs_are_not_stale():
    """⛔ A GUARD THAT PASSES AGAINST A STALE PDF IS WORSE THAN NO GUARD, AND THIS ONE DID.

    Measured 2026-08-17: a rebuild of the manuscript-style PDF failed with a FileNotFoundError while
    the journal-style build succeeded, and every check in this file then went GREEN — against the
    PREVIOUS PDF, still sitting on disk. The document being asserted about was not the document the
    build had just failed to produce. The freshness question has to be asked FIRST and separately,
    because a passing text-layer assertion carries no information about which text layer it read.

    ⛔ AND IT MUST BE ASKED OF CONTENT, NOT OF MTIME. The first version compared timestamps and
    promptly cried wolf: the regeneration chain rewrites its outputs byte-for-byte whether or not
    anything changed, so every chain run pushes their mtimes past the PDFs' and a correct tree reports
    stale. The archive manifest's `--check` had the identical shape earlier the same day. A gate that
    fires on a correct tree trains its reader to rebuild-and-move-on, which is the reflex that would
    carry a genuinely stale PDF into a deposit.
    """
    for style, path in sorted(PDFS.items()):
        assert os.path.exists(path), f"{path} is missing — a built format does not exist."
        stamp_path = path.replace(".pdf", ".build-stamp.json")
        assert os.path.exists(stamp_path), (
            f"the {style}-format PDF has no build stamp, so there is no way to tell what it was "
            "built from. Rebuild it with build_submission_pdf.py, which writes one.")
        with open(stamp_path, encoding="utf-8") as fh:
            built_from = json.load(fh)["built_from"]
        drifted = []
        for rel, want in sorted(built_from.items()):
            src = os.path.join(ASO, os.path.basename(rel))
            if not os.path.exists(src):
                drifted.append(f"{rel} (missing)")
                continue
            got = hashlib.sha256(open(src, "rb").read()).hexdigest()
            if got != want:
                drifted.append(os.path.basename(rel))
        assert not drifted, (
            f"the {style}-format PDF was built from a different version of {drifted}, so it does not "
            "contain the current manuscript and every other check in this file would be asserting "
            "about the wrong document. Rebuild with `python3 "
            f"research/manuscripts/build_submission_pdf.py --paper aso --style {style}`.")


@pytest.fixture(scope="module", params=sorted(PDFS), ids=sorted(PDFS))
def pdf_key(request):
    """Which built PDF the surrounding assertion is running against."""
    return request.param


@pytest.fixture(scope="module")
def pdf_text(pdf_key):
    """Every text-layer assertion runs against EVERY built format."""
    path = PDFS[pdf_key]
    assert os.path.exists(path), (
        f"{path} is missing. Every built format ships; the absence of one is not a reason to skip "
        "the check.")
    return _extract(path)


def test_no_sequence_in_the_pdf_is_fused_to_the_next_column(pdf_text):
    """A base string immediately followed by a digit is the wrong-reagent case.

    ⚠ NESTED SEQUENCES ARE NOT THE DEFECT AND MUST NOT FIRE HERE. `GGGCATATCATCAAAC` is a prefix of
    `GGGCATATCATCAAACC`, so "followed by another base" is legitimate and common. What is never
    legitimate is a base run followed by a DIGIT — no oligonucleotide continues into a number — and
    that is exactly the shape a fused table cell takes.
    """
    seqs = _canonical_sequences()
    assert re.search(r"5[′']-[ACGT]{12,25}-3[′']", pdf_text), (
        "this build's text layer carries no delimited sequence at all, so the search below could "
        "not have found a fused one either. A guard whose corpus is empty is not a guard that "
        "passed.")
    bad = []
    for m in re.finditer(r"[ACGT]{12,}\d", pdf_text):
        run = m.group(0)[:-1]
        # Only report where the run ENDS a canonical sequence: an arbitrary base run bumping a
        # figure axis label is not this defect.
        if any(run.endswith(s) for s in seqs):
            bad.append(pdf_text[max(0, m.start() - 40):m.end() + 10].replace("\n", "⏎"))
    assert not bad, (
        f"{len(bad)} sequence(s) in the deposited PDF run directly into a numeric cell, so a reader "
        "copy-pasting one gets a base string with a trailing digit and orders the wrong molecule:\n"
        + "\n".join("  " + b for b in bad[:6])
        + "\nFix at the table GENERATOR by giving every sequence cell its 5′-/-3′ delimiters, and "
          "re-build the PDF.")


def test_every_sequence_in_the_pdf_carries_its_delimiters(pdf_text):
    """The extractor-INDEPENDENT form of the defect, and the one that actually generalises.

    ⛔ THE FUSION TEST ABOVE IS NECESSARY AND NOT SUFFICIENT, AND SAYING SO IS THE POINT. Measured
    2026-08-17: with `pdfminer` the Table 5 cells separate with newlines and nothing fuses, while
    the extractor that first reported this defect returned `...CAAAC3′3 8 123`. Same PDF, same
    bytes, opposite verdicts — so a guard written against one extractor's behaviour would have gone
    green on a document that corrupts sequences for somebody else's reader.

    What does not depend on the extractor is whether the DOCUMENT bounds the string. A sequence
    printed as `5′-XXXX-3′` is delimited whatever reads it; a bare base run sitting against a
    numeric cell is ambiguous to every reader, and merely happens to be resolved by the newline
    that one library inserts. So the property asserted here is the document's, not the tool's.
    """
    seqs = sorted(_canonical_sequences(), key=len, reverse=True)
    bare, seen = [], set()
    for s in seqs:
        for m in re.finditer(re.escape(s), pdf_text):
            span = (m.start(), m.end())
            # A nested match (a 16-mer inside the 18-mer that contains it) is one printed string,
            # not two, and must not be counted twice or reported as undelimited on its own.
            if any(a <= span[0] and span[1] <= b for a, b in seen):
                continue
            before = pdf_text[max(0, m.start() - 4):m.start()].rstrip()
            after = pdf_text[m.end():m.end() + 4].lstrip()
            if before.endswith(("5′-", "5'-")) or after.startswith(("-3′", "-3'")):
                seen.add(span)
                continue
            bare.append(pdf_text[max(0, m.start() - 30):m.end() + 22].replace("\n", "⏎"))
    assert not bare, (
        f"{len(bare)} sequence occurrence(s) are printed in the deposited PDF WITHOUT their 5′-/-3′ "
        "delimiters, so nothing in the document separates the bases from the cell beside them and "
        "whether they fuse is up to the reader's PDF extractor:\n"
        + "\n".join("  " + b for b in bare[:6])
        + "\nGive every sequence cell its delimiters at the table GENERATOR, then rebuild the PDF.")


def test_no_sequence_is_split_across_a_line_in_the_pdf(pdf_text):
    """Bases broken mid-string are unrecoverable by a reader who cannot see the original."""
    split = re.findall(r"5[′']-[ACGT]{1,19}\s*\n+\s*[ACGT]{1,19}-3[′']", pdf_text)
    assert not split, (
        f"{len(split)} sequence(s) have their BASES broken across a line in the deposited PDF, e.g. "
        f"{split[0]!r}. Set sequences non-breaking at the generator.")


def test_the_pdf_names_the_canonical_machine_readable_sequence_file(pdf_text):
    """The durable fix for a text layer is not needing to read it.

    ⭐ Padding table cells makes today's extractor behave; it does not make a PDF a machine-readable
    record, and the next extractor is not ours to control. The deposit therefore ships the sequences
    in a form that was never typeset — and that is worth nothing if the paper does not tell a reader
    it exists, because the reader who needs it is by definition the one reading the PDF.
    """
    flat = " ".join(pdf_text.split())
    assert "fusion-junction-aso-sequences" in flat, (
        "the deposited PDF never names the canonical machine-readable sequence file "
        "(fusion-junction-aso-sequences.csv / .fasta). A reader with only the PDF has no way to "
        "learn that a copy-paste-safe copy of every sequence travels with the archive.")


def test_every_sequence_the_pdf_prints_is_in_the_canonical_file(pdf_text, pdf_key):
    """The canonical file must be canonical — a sequence in the paper and not in it is a hole.

    ⚠ READ FROM THE PDF, WHICH IS WHAT THE READER HAS. The generator asserts the same contract
    against the markdown at build time; this asserts it survived typesetting, which is the step
    that has now been shown to change what a sequence IS.
    """
    seqs = _canonical_sequences()
    printed = set(re.findall(r"5[′']-([ACGT]{12,25})-3[′']", pdf_text))
    #: ⛔ AND THE SET MUST NOT BE EMPTY, WHICH NOTHING SAID (2026-08-19). `printed - seqs` is empty
    #: when `printed` is empty, so a build that lost every delimiter — the exact regression the two
    #: tests above exist for — would have satisfied this one. MEASURED on both builds: 166 delimited
    #: tokens, 69 distinct, every one of them in the canonical file. The floor is set well under
    #: that, because the number of sequences the paper prints is an editorial decision; what is not
    #: negotiable is that the extractor found some.
    #: ⚠ THE FLOOR IS PER PAPER, BECAUSE THE PAPERS PRINT DIFFERENT NUMBERS OF SEQUENCES. A single
    #: floor of 20 was calibrated on the extended report's 69 and would fail the journal article,
    #: which prints 10 by editorial choice across two tables and its reagent paragraphs — a false
    #: red that would teach a reader to widen the guard rather than read it. Each floor is set well
    #: under that paper's measured count; what is not negotiable is that the extractor found some.
    #: ⛔⛔ AND THE FLOOR IS NOW DERIVED FROM THE SOURCES, NOT TYPED (2026-08-22). It was 8 for the
    #: journal article, calibrated when Table 2 printed two near-twin pairs. Dropping that table to
    #: one pair — an editorial choice made to fit six typeset pages — took the count to 7 and the
    #: guard went red on a build that was perfectly correct. A hardcoded count beside content that
    #: an editor is expected to change is the same staleness this file exists to catch, one level
    #: up: the number went out of date, not the PDF. The sources are read instead, so the guard now
    #: says the stronger thing — every sequence the markdown prints survived typesetting — and
    #: cannot be made red by an editorial decision that is not a defect.
    in_source = set()
    for src in _source_texts(pdf_key):
        in_source |= set(re.findall(r"5[′']-([ACGT]{12,25})-3[′']", src))
    assert in_source, (
        f"no delimited sequence was found in {pdf_key}'s own markdown sources, so this guard has "
        "nothing to compare the PDF against — the delimiters or the source list have moved")
    missing = in_source - printed
    assert not missing, (
        f"{len(missing)} sequence(s) the markdown prints could not be read out of {pdf_key}'s text "
        f"layer: {sorted(missing)}. Either the delimiters are gone — which is what this file exists "
        "to catch — or the extractor is no longer reading the sequence cells.")
    #: ⛔ ONE DELIBERATE EXCEPTION, AND IT IS THE REVERSE-COMPLEMENT TRAP RATHER THAN A HOLE.
    #: Figure 2 draws the TARGET mRNA at the multi-partner seam, because the point of the panel is
    #: where three partners' breakpoints coincide ON THE TRANSCRIPT; the reagent is that strand's
    #: reverse complement and IS in the canonical file. A reader who copies the drawn letters gets
    #: a SENSE-strand oligonucleotide, which is why the panel and its caption both say the rows are
    #: target mRNA (added 2026-08-19). So the sequence is allowed here on two conditions, both
    #: checked: it is exactly the reverse complement of a canonical design, and the document says
    #: in terms that the drawn letters are the target. ⚠ IT IS NEVER ALLOWED SILENTLY — an
    #: unexplained strand and a labelled one must not read alike, which is the whole reason this
    #: guard exists.
    def _rc(x):
        return x.translate(str.maketrans("ACGT", "TGCA"))[::-1]
    labelled = re.search(r"target\s+mRNA", pdf_text, re.I) is not None
    allowed = {q for q in printed - seqs if labelled and _rc(q) in seqs}
    assert not (printed - seqs) or labelled, (
        "a sequence outside the canonical file is printed and nothing in the document says the "
        "drawn letters are target mRNA; an unlabelled reverse complement is a wrong-reagent hazard")
    missing = sorted(printed - seqs - allowed)
    assert not missing, (
        f"{len(missing)} sequence(s) are printed in the deposited PDF and absent from the canonical "
        f"machine-readable file: {missing[:6]}. Re-run "
        "research/manuscripts/aso_sequence_manifest.py, or add the artifact the design comes from "
        "to its source list.")


#: A text page carrying less than this fraction of the document's own median page is stranded: a
#: forced break left a few lines and white space. RELATIVE, not absolute — the first version of this
#: guard used a flat 700 characters, passed a page carrying 1,470 where a full page runs to ~7,900,
#: and so reported a clean document to a screen that had just filed the page as a finding. A flat
#: floor cannot know what a full page is.
_STRANDED_PAGE_FRACTION = 0.45

#: ⛔ WHAT COUNTS AS A DISPLAY ITEM, AND WHY IT IS A RULE COUNT RATHER THAN "ANY DRAWN OBJECT".
#: pdfminer models every drawn primitive as an `LTCurve`, and `LTRect`/`LTLine` are subclasses of
#: it, so "the page carries a curve" is true of any page with a rule under its running head — 37 of
#: the journal build's 47 pages and 42 of the manuscript build's 66. A test exempting those pages
#: exempts most of the document.
#: MEASURED on both builds 2026-08-19, the two populations do not overlap and are not close:
#:   · pages with no grid on them          — 0 to 14 rule primitives (max 14, manuscript p28)
#:   · pages carrying a table grid or an     97 to 820 (min 97, manuscript p50's grid)
#:     SVG figure drawn as rules
#: so any threshold in 15…96 separates them. 40 is taken as the midpoint of that gap rather than
#: either edge, so neither a rule-heavy prose page nor a very small grid decides the test.
_DISPLAY_ITEM_MIN_RULES = 40


def _pages(path):
    """One record per page: number, characters, placed graphics, drawn rules, height, text."""
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer, LTFigure, LTImage, LTCurve
    out = []
    for number, layout in enumerate(extract_pages(path), 1):
        text = "\n".join(el.get_text() for el in layout if isinstance(el, LTTextContainer))
        out.append({
            "number": number,
            "chars": sum(len(el.get_text().strip())
                         for el in layout if isinstance(el, LTTextContainer)),
            "n_placed_graphics": sum(1 for el in layout if isinstance(el, (LTFigure, LTImage))),
            "n_rules": sum(1 for el in layout if isinstance(el, LTCurve)),
            "height": round(layout.height),
            "text": text,
        })
    return out


def _carries_a_display_item(page):
    """True when the page carries an actual float — a placed figure, or a drawn grid.

    ⛔ THIS IS THE CONJUNCT THAT WAS NOT BEING TESTED. Both halves of the exemption below — "the
    page carries no display item of its own" and "the page after it opens one" — were implemented
    against proxies that are true of nearly every page (`isinstance(el, LTCurve)` for the first,
    "the next page holds more than 1,500 characters" for the second), so a blank page in the
    journal-format deposit was guarded by nothing at all.
    """
    return page["n_placed_graphics"] > 0 or page["n_rules"] >= _DISPLAY_ITEM_MIN_RULES


def _next_page_opens_a_display_item(pages, number):
    """True when the page after `number` is where a table or figure block BEGINS.

    A page whose successor opens a display item was truncated by that item's own atomicity, which
    is a property of the item rather than of the pagination. "Opens" rather than "carries" is free
    here: this is only ever asked about a page that carries no display item of its own, so a grid
    on the next page cannot be the continuation of one that started on this one.
    """
    nxt = next((p for p in pages if p["number"] == number + 1), None)
    return bool(nxt) and _carries_a_display_item(nxt)


def _stranded_pages(pages):
    """The decision, as a pure function of the page records, so it can be driven with a
    constructed document instead of only with the one on disk (see the proof below)."""
    import statistics
    median = statistics.median([p["chars"] for p in pages]) or 1
    heights = {p["number"]: p["height"] for p in pages}
    stranded = []
    last = max(p["number"] for p in pages)
    for page in pages:
        number = page["number"]
        if _carries_a_display_item(page) or page["chars"] >= _STRANDED_PAGE_FRACTION * median:
            continue
        #: ⛔ THE FINAL PAGE IS SHORT BECAUSE THE DOCUMENT ENDS, NOT BECAUSE A FLOAT PUSHED IT
        #: (2026-08-19). The journal build's last page carries the tail of the reference list at
        #: 3,183 characters against a 7,402 median, and there is nothing after it that a float
        #: could have displaced — this guard's whole inference is "a float forced a break before
        #: the surrounding prose had filled", and on the last page there is no surrounding prose
        #: left to fill. ⚠ THE EXEMPTION IS THE LAST PAGE AND NOT "a short page near the end":
        #: a genuinely stranded penultimate page is still caught, which the proof below asserts.
        if number == last:
            continue
        #: The page before an orientation change is forced short by page geometry, not by a float
        #: placed badly — a landscape table cannot start halfway down a portrait page.
        if heights.get(number + 1) not in (None, page["height"]):
            continue
        #: ⛔ AND THE PAGE BEFORE AN UNBREAKABLE GRID IS FORCED SHORT THE SAME WAY (2026-08-19).
        #: Manuscript page 42 carries one clause of Table 6's diamond note and nothing else, because
        #: the grid that must follow it is atomic and taller than the space left. THREE fixes were
        #: tried and MEASURED, and this exemption is written only because all three were worse:
        #:   * widows/orphans on the note paragraph        -> page unchanged at 108 characters
        #:   * `break-after: auto` on table captions       -> 1 stranded page became 11
        #:   * `break-inside: auto` on the grid            -> 1 stranded page became 10
        #: Holding the grid atomic is what keeps the other fifty-odd pages full, so the single short
        #: page is the price of that and not a defect this build can remove. A blind screen that
        #: rendered all 58 pages did not report it.
        #: ⚠ NARROW BY CONSTRUCTION: the page must carry no display item of its own AND be followed
        #: by one. A short page that simply runs out of prose is still a failure.
        if _next_page_opens_a_display_item(pages, number):
            continue
        stranded.append((number, page["chars"]))
    return stranded, median


@pytest.mark.parametrize("style", sorted(PDFS))
def test_no_page_of_either_pdf_is_left_stranded(style):
    """⛔ A FORCED PAGE BREAK BEFORE A FLOAT EMPTIED A PAGE MID-RESULTS (2026-08-17).

    Two independent blind screens of the built journal PDF reported page 15: a couple of short
    column fragments at the top and white below, because a landscape float carries
    `break-before: page`. Landscape floats now defer to the end of the section that cites them,
    which removed the worst of it — but a landscape table must still begin on a fresh page, so the
    portrait page before an orientation change legitimately ends early. That one is a property of
    mixed-orientation typesetting, not a defect, and it is exempted BY NAME rather than by lowering
    the bar until everything passes.

    ⚠ MEASURED ON THE BUILT FILE. No source-side check can see a page break.
    """
    pages = _pages(PDFS[style])
    assert pages, f"the {style} PDF has no pages"
    #: ⛔ AND THE EXEMPTIONS MUST NOT SWALLOW THE DOCUMENT. Both were proxies until 2026-08-19 and
    #: between them exempted 42 of the manuscript build's 66 pages and 37 of the journal build's 47
    #: before the size test was ever reached. A display item is now an actual placed figure or a
    #: drawn grid, so the count below is the count of real floats and a regression that starts
    #: exempting prose pages fails here rather than going quiet.
    n_display = sum(1 for p in pages if _carries_a_display_item(p))
    assert 0 < n_display < 0.6 * len(pages), (
        f"{n_display} of the {style} build's {len(pages)} pages read as carrying a display item. "
        "Zero means the detector stopped seeing floats and every short page is now exempt by the "
        "next-page clause; a majority means it is matching prose pages and the guard is vacuous.")
    stranded, median = _stranded_pages(pages)
    assert not stranded, (
        f"the {style}-format PDF leaves {len(stranded)} text page(s) stranded "
        f"(median page {median:.0f} chars): "
        + ", ".join(f"p{n} ({c} chars)" for n, c in stranded)
        + ". A short page with no display item on it, not preceding an orientation change, means a "
          "float forced a break before the surrounding prose had filled.")


def _page(number, chars, *, n_rules=0, n_placed=0, height=842):
    """A page record with everything but the field under test held constant."""
    return {"number": number, "chars": chars, "n_placed_graphics": n_placed,
            "n_rules": n_rules, "height": height, "text": "x" * chars}


def test_the_stranded_page_guard_fails_on_a_page_a_float_did_not_cause():
    """⛔ THE GUARD OF THE GUARD — the defect is CONSTRUCTED and the exemptions are shown to refuse it.

    Both conjuncts of the float exemption were proxies, and both were true of almost every page:

      · "this page carries no display item"  was  `isinstance(el, LTCurve)`, and pdfminer makes
        `LTRect` and `LTLine` subclasses of `LTCurve`, so one rule under a running head exempted the
        page — 42 of 66 manuscript pages and 37 of 47 journal pages;
      · "the next page opens a display item" was  `chars > 1500`, true of 64 of the manuscript
        build's 66 pages and of every page of the journal build.

    So a page emptied by a badly placed float, followed by ordinary prose, was exempt. Below is
    exactly that document: page 2 carries 300 characters against a 6,000-character median, has no
    grid and no placed graphic, and page 3 is a full prose page. It must be reported.
    """
    prose = [_page(1, 6000), _page(2, 300), _page(3, 6000)]
    assert _stranded_pages(prose)[0] == [(2, 300)], (
        "a short prose page between two full prose pages is not being reported — the exemptions "
        "are matching something other than a display item.")
    # the old proxy for the second conjunct, driven with the same document: it exempts the defect
    assert prose[2]["chars"] > 1500, "the retired proxy would have exempted this very page"
    # and the old proxy for the FIRST conjunct: one rule under a running head, still a defect
    assert _stranded_pages([_page(1, 6000), _page(2, 300, n_rules=1), _page(3, 6000)])[0] \
        == [(2, 300)], "a single drawn rule is again reading as a display item"


def test_the_stranded_page_guard_still_exempts_the_two_cases_it_is_meant_to():
    """The other half of the proof: the exemptions must survive, or the fix is just a stricter bar.

    A page short because an atomic grid could not fit under it, and a page short because the next
    page changes orientation, are properties of typesetting rather than defects — and each is
    exempted only on the evidence that names it.
    """
    grid_next = [_page(1, 6000), _page(2, 300), _page(3, 4000, n_rules=400)]
    assert _stranded_pages(grid_next)[0] == [], "the atomic-grid exemption stopped working"
    figure_next = [_page(1, 6000), _page(2, 300), _page(3, 900, n_placed=3)]
    assert _stranded_pages(figure_next)[0] == [], "the placed-figure exemption stopped working"
    landscape = [_page(1, 6000), _page(2, 300), _page(3, 6000, height=595)]
    assert _stranded_pages(landscape)[0] == [], "the orientation-change exemption stopped working"
    # and a page carrying its own grid is never its own defect
    own_grid = [_page(1, 6000), _page(2, 300, n_rules=400), _page(3, 6000)]
    assert _stranded_pages(own_grid)[0] == [], "a page carrying a grid is being called stranded"
