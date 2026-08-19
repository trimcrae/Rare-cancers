#!/usr/bin/env python3
"""The submission manuscript's citation numbering, asserted rather than promised.

⛔ WHY THIS IS A TEST AND NOT A README LINE. The manuscript's References note used to say the
superscripts were "placeholders pending final numbering". A promise in prose is not a property: for
as long as it stood, superscript 13 pointed at PMID 36780200 for a claim about "a bi-shRNA against
the EWS/FLI1 junction taken into clinical testing", and that paper is a trial of Vigil, a bi-shRNA
against *furin*. Nothing in the repository could be asked the question, so nobody asked it.

⚠ WHAT THESE CAN AND CANNOT CATCH. They check that every superscript carries an identifier, that
the numbering is derived from those identifiers, and that every cited paper has a retrieved record.
They cannot check that a cited paper supports its sentence — the failure that actually happened.
That check is human. These close the second hole: a citation verified once and then renumbered by
hand into the wrong place.
"""
import json
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MAN = os.path.dirname(HERE)
sys.path.insert(0, MAN)

import submission_citations as S  # noqa: E402


def _text():
    #: ⛔ NOT A SKIP (2026-08-19, lane C2). The submission manuscript is committed, so deleting or
    #: renaming it used to switch off every citation-provenance check in this file — the class of
    #: hole the pypdf/pymupdf audit found, where a guard vanishes with its input and reports green.
    if not os.path.exists(S.PAPER):
        pytest.fail(f"the submission manuscript is missing at {S.PAPER}. It is committed; without "
                    "it not one superscript, number or retrieved record in this file is checked.")
    return open(S.PAPER, encoding="utf-8").read()


def test_every_superscript_carries_a_pubmed_identifier():
    """⛔ THE LOAD-BEARING ONE. An unannotated superscript is invisible to the renumbering pass, so
    it keeps whatever number was last typed while everything around it moves."""
    bare = [m.group(1) for m in S.BARE.finditer(_text())]
    assert not bare, (
        f"unannotated superscript(s) {sorted(set(bare))}: add <!--PMID:...--> after each, or the "
        f"renumbering pass will leave them pointing at whatever they happen to say")


def test_the_printed_numbers_are_the_ones_the_identifiers_imply():
    """Numbering is by first appearance — the definition of a numbered reference list. If the file
    says otherwise, the file was hand-edited after the last generate."""
    text = _text()
    cites = S.parse(text)
    assert cites, "no annotated citations found"
    order = S.assign(cites)
    for (_, printed, pmids) in cites:
        expect = S.render_run([order[p] for p in pmids])
        assert printed.strip() == expect, (
            f"superscript reads {printed!r} but its identifiers {pmids} imply {expect!r} — "
            f"re-run submission_citations.py --write rather than editing the number")


def test_one_paper_gets_one_number():
    cites = S.parse(_text())
    order = S.assign(cites)
    assert len(set(order.values())) == len(order)
    assert sorted(order.values()) == list(range(1, len(order) + 1)), "numbering has a gap"


def test_every_cited_paper_has_a_retrieved_bibliographic_record():
    """⛔ A REFERENCE LIST WITH AN INVENTED VOLUME IS WORSE THAN ONE WITH A GAP. This fails rather
    than letting an entry print as '[METADATA NOT RETRIEVED]' unnoticed at submission time."""
    order = S.assign(S.parse(_text()))
    meta = S.load_meta()
    missing = sorted(p for p in order if p not in meta)
    assert not missing, (
        f"no retrieved record for PMID(s) {missing} — fetch them before submission; do not type "
        f"the author list from memory")


def test_the_generated_reference_list_matches_the_manuscript():
    #: ⛔ NOT A SKIP (2026-08-19, lane C2). The generated reference list is a committed artifact
    #: and it is the deposit's own bibliography; "has not been generated" is not a state a checkout
    #: can be in, and skipping on it hid the one check that the committed list and the manuscript
    #: agree about which paper is reference n.
    if not os.path.exists(S.OUT_JSON):
        pytest.fail(f"the generated reference list is missing at {S.OUT_JSON}. It is committed and "
                    "it ships with the submission — re-run submission_citations.py --write.")
    d = json.load(open(S.OUT_JSON))
    order = S.assign(S.parse(_text()))
    assert d["numbering"] == {p: n for p, n in order.items()}, (
        "the committed reference list disagrees with the manuscript — re-run "
        "submission_citations.py --write and commit both")
    assert not d["unannotated_superscripts"]


def test_the_withdrawn_vigil_citation_has_not_come_back():
    """⛔ NAMED, BECAUSE THIS ONE ALREADY HAPPENED. PMID 36780200 is Vigil — an autologous
    tumour-cell therapy expressing a bi-shRNA against *furin* — and it was cited in the submission
    draft as follow-through in patients for a junction-directed EWS/FLI1 agent. EWS/FLI1 appears in
    that paper only as a ctDNA marker. If a future edit reintroduces it, the claim it supports has
    to be re-argued from the paper's actual subject rather than restored."""
    assert "36780200" not in _text(), (
        "PMID 36780200 (Vigil, bi-shRNA against furin) is cited again. It does not support a claim "
        "about a junction-directed EWS/FLI1 agent; see the working record §1a(v).")


def test_render_run_collapses_only_runs_of_three_or_more():
    assert S.render_run([8, 9, 10, 11]) == "8–11"
    assert S.render_run([12]) == "12"
    assert S.render_run([24, 27]) == "24,27"
    assert S.render_run([3, 4]) == "3,4", "a pair reads worse as a range than as two numbers"
    assert S.render_run([1, 2, 3, 7]) == "1–3,7"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))


def test_every_citation_resolves_without_the_literature_cache_branch():
    """⛔ CI IS A PLAIN CHECKOUT, AND THE RECORD LIVED ON A BRANCH IT DOES NOT HAVE (2026-08-13).

    `test_every_cited_paper_has_a_retrieved_bibliographic_record` was RED on `main` for PMID
    7545436 — the Sugimoto nearest-neighbour reference the ASO manuscript's thermodynamics rests on
    — while a complete retrieved record for it sat committed in the generated submission reference
    list the whole time. `load_meta` consulted the working-record corpus, the curated maps and the
    `literature-cache` BRANCH, and not the generated list; so the citation resolved on a developer's
    machine that happened to have fetched that branch and nowhere else.

    ⚠ THE COST OF LEAVING IT IS NOT THE RED BUILD. A citation-integrity check that fails on a lookup
    gap spends the credibility of a real guard on a false alarm, and the next red one gets waved
    through. This asserts the condition CI actually runs under, which the test above cannot: it
    passes on any machine that ever fetched the branch, including the one this was written on.
    """
    order = S.assign(S.parse(_text()))
    real = S._literature_cache
    try:
        S._literature_cache = lambda: {}          # the branch is simply absent, as in CI
        meta = S.load_meta()
    finally:
        S._literature_cache = real
    missing = sorted(p for p in order if p not in meta)
    assert not missing, (
        f"PMID(s) {missing} resolve only via the literature-cache branch, so this check passes "
        f"locally and fails in CI. Commit their retrieved records — do not type them.")


def test_the_check_flag_actually_checks(tmp_path, monkeypatch, capsys):
    """⛔ `--check` used to be a no-op that returned 0.

    The module had exactly two behaviours — `--write`, which repairs the numbering, and a default
    that printed the derived numbering and returned 0. An unrecognised flag fell into the default,
    so `submission_citations.py --check` reported nothing and exited 0 no matter how badly the
    printed superscripts disagreed with the identifiers beside them. A data-integrity review caught
    it on 2026-08-13 by running the flag against a draft whose numbering was, at that moment,
    genuinely broken.

    The test above (`test_the_printed_numbers_are_the_ones_the_identifiers_imply`) would have caught
    the broken draft, and did not fail only because it was never run inside that window. This one
    covers the other half: that the COMMAND a human or a workflow would reach for is not a no-op.
    """
    good = open(S.PAPER, encoding="utf-8").read()
    assert S.main(["--check"]) == 0, "the committed manuscript should pass its own citation check"

    broken = good.replace("<sup>1</sup><!--PMID:8634690-->", "<sup>7</sup><!--PMID:8634690-->", 1)
    assert broken != good, "the fixture superscript is no longer present — pick another"
    p = tmp_path / "paper.md"
    p.write_text(broken, encoding="utf-8")
    monkeypatch.setattr(S, "PAPER", str(p))
    assert S.main(["--check"]) == 1, "a mis-numbered superscript must fail --check, not pass it"
    assert "should be" in capsys.readouterr().err
