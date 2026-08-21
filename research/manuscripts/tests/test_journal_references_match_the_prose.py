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


@pytest.mark.parametrize("path", [ARTICLE, REFS])
def test_the_reference_list_is_not_described_as_generated(path):
    #: The banner said GENERATED FROM THE MANUSCRIPT while nothing generated it. A file that claims
    #: machine provenance is trusted differently from one that admits it is hand-maintained.
    text = _read(path)
    assert "GENERATED FROM THE MANUSCRIPT" not in text, (
        f"{os.path.basename(path)} claims to be generated from the manuscript. No generator writes "
        "it; it is hand-maintained and held by the tests in this file.")
