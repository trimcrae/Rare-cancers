#!/usr/bin/env python3
"""The anonymized build removes identity and changes NOTHING else.

⛔ WHY THIS EXISTS. `build_submission_pdf.py --anonymized` exists because NAT's guidelines
contradict themselves on the review model — "Identity transparency: Single-anonymized" twice, and a
peer-review section declaring "a rigorous double-anonymized reviewing policy" — so both uploads are
built and the form decides. A redaction pass over a finished manuscript has exactly two failure
modes, and they point in opposite directions:

  1. IT LEAVES AN IDENTIFIER IN, and a blinded reviewer learns who wrote the paper.
  2. IT CHANGES A CLAIM, and the version under review states something the author never wrote.

The second is the one nobody would notice. A regex written to take an e-mail address out of a
title block can, on a manuscript that later gains a sentence, take a clause out of a result — and
the anonymized file is not the one anybody proofreads. So the transform's own docstring claims the
two bodies differ only in identity, and CLAUDE.md is explicit that a property asserted in a comment
is not a property. This is where it becomes one.

⚠ WHAT "ONLY IDENTITY" MEANS HERE, PRECISELY. Every line that differs between the two bodies must
be a line a redaction rule declares it touches: the author block, the correspondence-and-ORCID tail
of the affiliation line, the archive DOI, and the author's initials. A diff line anywhere else
fails, whatever it says and however harmless it looks.
"""
from __future__ import annotations

import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, MANUSCRIPTS)

import build_submission_pdf as bsp  # noqa: E402

PAPER = bsp.PAPERS["aso-journal"]

#: ⛔ EVERY STRING THAT NAMES THE AUTHOR OR RESOLVES TO SOMETHING THAT DOES. `zenodo` is here
#: because the deposit record carries the depositor's name, so a DOI a reviewer can resolve is an
#: identifier even though the digits themselves name nobody.
IDENTIFIERS = ("Tristan", "McRae", "T.D.M.", "trimcrae", "orcid", "0000-0002-1823-1451", "zenodo")


@pytest.fixture(scope="module")
def bodies():
    plain, _floats = bsp.assemble(PAPER, "journal")
    anon, applied = bsp.anonymise(plain)
    return plain, anon, applied


def test_every_required_redaction_rule_still_matches_something(bodies):
    """A rule that matches nothing is a silent hole, not a no-op.

    ⚠ SCOPED TO THE REQUIRED RULES, AND THE DISTINCTION IS REAL RATHER THAN A CONCESSION. The
    bare-initials rule is a catch-all behind a specific one that consumes the manuscript's only
    occurrence today; it matching nothing is it working. Demanding a match from it would have left
    exactly two ways out — delete the safety net, or weaken the assertion for every rule — and both
    are worse than naming which rules must bind.
    """
    _plain, _anon, applied = bodies
    matched = {what for what, _n in applied}
    required = [what for _p, _r, what, req in bsp._ANON_RULES if req]
    missing = [what for what in required if what not in matched]
    assert not missing, (
        f"required redaction rule(s) matched nothing: {missing}. The manuscript's front matter or "
        f"Data availability section changed shape and the rule no longer binds. Applied: {applied}")


@pytest.mark.parametrize("identifier", IDENTIFIERS)
def test_no_identifier_survives(bodies, identifier):
    _plain, anon, _applied = bodies
    assert not re.search(re.escape(identifier), anon, re.I), (
        f"{identifier!r} survives into the anonymized body — a blinded reviewer would see it")


def test_the_unblinded_body_still_carries_them(bodies):
    """⛔ THE CONTROL. Without it, a build that emitted an empty document would pass every
    assertion above. Each identifier must be present before redaction for its absence after to
    mean anything."""
    plain, _anon, _applied = bodies
    missing = [i for i in IDENTIFIERS if not re.search(re.escape(i), plain, re.I)]
    assert not missing, (
        f"{missing} are absent from the UNBLINDED manuscript, so the anonymisation tests above "
        "prove nothing about them. Either the manuscript dropped them or this list is stale.")


def test_nothing_but_identity_differs(bodies):
    """Every changed line must be one a rule declares it touches."""
    plain, anon, _applied = bodies
    a, b = plain.splitlines(), anon.splitlines()
    import difflib
    changed = [ln[1:].strip() for ln in difflib.ndiff(a, b)
               if ln.startswith(("-", "+")) and ln[1:].strip()]
    #: A changed line is allowed only where it carries an identifier (the line being removed) or is
    #: the placeholder that replaced one (the line being added).
    allowed = re.compile("|".join(
        [re.escape(i) for i in IDENTIFIERS]
        + [re.escape(bsp._ANON_NOTE), r"^\*\*Author\.\*\*", r"^\*Independent researcher",
           r"the archived deposit cited in the unblinded copy", r"^The sole author is"]), re.I)
    stray = [ln for ln in changed if not allowed.search(ln)]
    assert not stray, (
        "the anonymized build changes lines that carry no identity — a redaction rule is reaching "
        "into the manuscript's content:\n  " + "\n  ".join(stray[:10]))


def test_the_guard_would_catch_a_rule_that_ate_content(bodies):
    """⛔ MUTATION TEST. `test_nothing_but_identity_differs` is only worth having if it fails on a
    rule that removes a sentence, so one is applied here and the assertion is checked directly."""
    plain, _anon, _applied = bodies
    greedy = re.sub(r"(?m)^Both reagents are phosphorothioate.*$", "", plain)
    a, b = plain.splitlines(), greedy.splitlines()
    import difflib
    changed = [ln[1:].strip() for ln in difflib.ndiff(a, b)
               if ln.startswith(("-", "+")) and ln[1:].strip()]
    allowed = re.compile("|".join([re.escape(i) for i in IDENTIFIERS] + [re.escape(bsp._ANON_NOTE)]),
                         re.I)
    assert [ln for ln in changed if not allowed.search(ln)], (
        "a rule that deleted a chemistry sentence produced no disallowed diff line, so the "
        "content guard has no power")


def test_the_pdf_metadata_is_blinded_too():
    """A redacted body under an /Author field naming the author is not an anonymized file."""
    #: ⛔ NO SKIP HERE, AND `test_no_guard_can_silently_not_run.py` IS RIGHT TO REFUSE ONE. The
    #: first cut skipped when the file was absent, which is precisely when the check matters: the
    #: anonymized PDF is a committed artifact that `regenerate_aso_chain.sh` builds on every run,
    #: so its absence is a broken tree, not an environment this guard should stay quiet in.
    out = os.path.join(MANUSCRIPTS, PAPER["out"].replace(".pdf", "-anonymized.pdf"))
    assert os.path.exists(out), (
        f"{os.path.relpath(out, MANUSCRIPTS)} is missing — run "
        "`python3 research/manuscripts/build_submission_pdf.py --paper aso-journal --anonymized` "
        "(the ASO chain does it) and commit the result")
    pypdf = pytest.importorskip("pypdf")
    meta = pypdf.PdfReader(out).metadata or {}
    author = str(meta.get("/Author", ""))
    assert author == "Anonymized for review", f"/Author is {author!r}"
    blob = " ".join(str(v) for v in meta.values())
    leaks = [i for i in IDENTIFIERS if re.search(re.escape(i), blob, re.I)]
    assert not leaks, f"document properties still carry {leaks}"
