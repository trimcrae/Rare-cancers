#!/usr/bin/env python3
"""The journal article's reference list agrees with the citations in its prose.

⛔ WHY THIS EXISTS. The reference list of the ASO journal article carried a banner reading
"GENERATED FROM THE MANUSCRIPT" and no generator existed anywhere in the repository. Worse, the
gate that looks like it covers this — `submission_citations.py --check` — reads the PREPRINT, and
reported "53 distinct PMID(s), citation numbering is current" while the journal article's 21
references were read by nothing at all. A green gate said nothing about the file it appeared to be
about, which is the "reports while measuring nothing" defect this repository keeps paying for.

Three things are checked, and each is a way the two documents can silently disagree:
  1. every superscript number in the prose resolves to an entry in the list (a dangling citation);
  2. every entry in the list is cited by the prose (a reference to nothing, which reviewers notice);
  3. the PMID a citation names is the PMID its entry carries (the numbering is inherited from the
     extended report, so the numbers are deliberately NOT contiguous and a renumbering slip would
     otherwise point a reader at the wrong paper).
"""
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
ARTICLE = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-journal-article.md")
REFS = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-journal-references.md")

#: `<sup>10,11,13</sup><!--PMID:1794439,9049825,33241214-->` — one superscript may carry several.
_CITE = re.compile(r"<sup>([\d,\s]+)</sup>\s*<!--\s*PMID:\s*([\d,\s]+?)\s*-->")
_ENTRY = re.compile(r"^(\d+)\.\s+(.+)$", re.M)


def _read(path):
    assert os.path.exists(path), f"missing {path}"
    return open(path, encoding="utf-8").read()


def _citations():
    """{number: pmid} as the prose asserts it."""
    out = {}
    for nums, pmids in _CITE.findall(_read(ARTICLE)):
        n = re.findall(r"\d+", nums)
        p = re.findall(r"\d+", pmids)
        assert len(n) == len(p), (
            f"a citation pairs {len(n)} number(s) with {len(p)} PMID(s): {nums!r} / {pmids!r}. "
            "The two lists are positional, so an uneven pair silently mis-attributes every "
            "reference after the mismatch.")
        out.update(zip(n, p))
    return out


def _entries():
    return {n: body for n, body in _ENTRY.findall(_read(REFS))}


def test_every_citation_resolves_to_an_entry():
    missing = sorted(set(_citations()) - set(_entries()), key=int)
    assert not missing, (
        f"{len(missing)} citation(s) in the prose have no entry in the reference list: {missing}. "
        "A reader following the superscript lands on nothing.")


def test_every_entry_is_cited():
    orphans = sorted(set(_entries()) - set(_citations()), key=int)
    assert not orphans, (
        f"{len(orphans)} reference(s) are listed but never cited: {orphans}. Either the prose that "
        "cited them was cut and the entry was left behind, or the citation was dropped by accident.")


def test_each_entry_carries_the_pmid_its_citation_names():
    entries, wrong = _entries(), []
    for num, pmid in sorted(_citations().items(), key=lambda kv: int(kv[0])):
        body = entries.get(num)
        if body and f"PMID: {pmid}" not in body:
            got = re.search(r"PMID:\s*(\d+)", body)
            wrong.append(f"[{num}] prose says PMID {pmid}, entry carries {got.group(1) if got else 'none'}")
    assert not wrong, (
        "the numbering is inherited from the extended report rather than assigned here, so a slip "
        "points the reader at a real paper that is the wrong one:\n  " + "\n  ".join(wrong))


#: ⭐ THE VENUE'S OWN STYLE, AS THE VENUE'S OWN EXAMPLES SHOW IT (2026-08-23). Nucleic Acid
#: Therapeutics: "The journal follows the Sage Vancouver reference style." Its worked examples put
#: the YEAR in parentheses after the authors, name every author after the first as
#: `Initials Surname`, drop the issue number, and run the journal straight into `volume:pages` with
#: no period between them:
#:
#:     Aartsma-Rus A. (2017). FDA approval of nusinersen … Nucleic Acid Ther 27:67–69
#:     Malerba A, L Boldrin and G Dickson. (2011). Long-term systemic administration … 21:293–298.
#:
#: Source of record: research/literature/nat-submission-guidelines-2026-08-23.md.
#: ⚠ WHAT THIS PATTERN DOES NOT CHECK, STATED RATHER THAN IMPLIED: Sage Vancouver also ABBREVIATES
#: the journal name, and the full specification lives on a page linked from the guidelines that no
#: route here can fetch. Abbreviating a journal name means writing an identifier this repository
#: cannot attest, which CLAUDE.md §7 forbids outright — so the names are carried as they were
#: recorded and the gap is declared here rather than papered over with a guess. A copy editor
#: abbreviates journal names; nobody desk-rejects a paper for spelling one out.
#: ⚠ AND THE PMID AND DOI TAILS ARE KEPT, which the venue's examples do not show. They are the
#: provenance of every citation in this repository and `test_each_entry_carries_the_pmid_its_
#: citation_names` above is bound to them; dropping them to match an example would trade a checked
#: fact for a cosmetic one.
_SAGE_VANCOUVER = re.compile(
    r"^\d+\. "                       # the entry number
    r".+?"                           # authors, first as `Surname Initials`
    r"\. \(\d{4}\)\. "               # ". (YEAR). "
    r".+ "                           # title. journal
    r"[A-Z]?\d+:[A-Za-z]*\d[\w–-]*\. "  # volume:pages, no issue number
    r"PMID: \d+\.")


def test_every_entry_is_in_the_style_the_venue_asks_for():
    """⛔ A HAND-ADDED ENTRY IN THE OLD STYLE IS INVISIBLE UNTIL AN EDITOR SEES IT.

    The list is hand-maintained, and the whole of it was converted in one pass on 2026-08-23. The
    next entry will be typed by hand next to twenty-three that already look right, which is exactly
    the condition under which a style silently forks.
    """
    wrong = [n for n, body in sorted(_entries().items(), key=lambda kv: int(kv[0]))
             if not _SAGE_VANCOUVER.match(f"{n}. {body}")]
    assert not wrong, (
        f"{len(wrong)} reference(s) are not in Sage Vancouver form: {wrong}.\n"
        "Expected `N. Surname II, II Surname and II Surname. (YEAR). Title. Journal VOL:PAGES. "
        "PMID: nnn.` — year in parentheses after the authors, every author after the first as "
        "initials-then-surname, no issue number, no period between the journal and the volume. "
        "Nucleic Acid Therapeutics returns a non-conforming manuscript before peer review.")


@pytest.mark.parametrize("path", [ARTICLE, REFS])
def test_the_reference_list_is_not_described_as_generated(path):
    #: The banner said GENERATED FROM THE MANUSCRIPT while nothing generated it. A file that claims
    #: machine provenance is trusted differently from one that admits it is hand-maintained.
    text = _read(path)
    assert "GENERATED FROM THE MANUSCRIPT" not in text, (
        f"{os.path.basename(path)} claims to be generated from the manuscript. No generator writes "
        "it; it is hand-maintained and held by the tests in this file.")


def test_the_printed_pdf_numbers_the_references_as_the_prose_cites_them():
    """⛔ THE SOURCE WAS RIGHT AND THE ARTEFACT WAS WRONG (2026-08-20).

    The reference list inherited the extended report's numbering, so the markdown carried
    1, 2, 6, 7, 8 … 40 and the tests above — which read the markdown — passed. An HTML `<ol>`
    renumbers its items from 1 regardless of the source, so the BUILT PDF printed 1 to 21 and a
    superscript 8 resolved to the eighth printed entry. About two thirds of the citations in the
    typeset article pointed at a real paper that was the wrong one, and nothing in this repository
    read the PDF to notice. Checking a manuscript's source is not checking what a reader receives.
    """
    pdf = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-journal-article.pdf")
    assert os.path.exists(pdf), (
        f"{os.path.basename(pdf)} is not built. It is a committed deposit artefact, so its absence "
        "is a broken tree rather than a reason to pass silently: rebuild with "
        "`build_submission_pdf.py --paper aso-journal`.")
    from pypdf import PdfReader
    pages = PdfReader(pdf).pages
    text = " ".join(" ".join(p.extract_text().split()) for p in pages)
    start = text.rfind("References")
    assert start != -1, "no References section in the built PDF"
    printed = [int(n) for n in re.findall(r"(?:^|\s)(\d{1,3})\. [A-Z]", text[start:])]
    cited = sorted({int(n) for n in _citations()})
    assert printed == cited, (
        f"the PDF prints reference numbers {printed[:8]}… while the prose cites {cited[:8]}…\n"
        "Every citation whose printed position differs from its number sends the reader to a "
        "different paper, which no linter on the markdown can see.")
