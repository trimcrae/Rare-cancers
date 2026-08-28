"""Regression tests for lint_style.py's HTML-comment handling.

Round 11 (AUT-PROP-039/CYC-0032) added an exemption so a decorative glyph or other house-register
tic sitting INSIDE an `<!-- ... -->` comment (maintainer bookkeeping that never renders in the
typeset PDF) does not trip the gate. Round 12 seat 1 found that the exemption was implemented by
dropping the WHOLE LINE whenever it contained a same-line-closed comment, not just the comment
span -- and the ASO journal article's citation markers (`<sup>1</sup><!--PMID:...-->`) sit
mid-sentence on ~24 lines, so real prose sharing those lines went uninspected. Verified by mutation
on a scratch copy of the live article: inserting a decorative glyph and a second-person "your" into
the prose sharing a comment-bearing line passed `lint_style.py` clean, while the identical mutation
on a comment-free line was caught.

These tests pin both directions: content INSIDE a comment must stay exempt (round 11's own goal),
and content OUTSIDE a comment -- even sharing its line -- must not.
"""

import os
import sys
import tempfile

import pytest

_HERE = os.path.abspath(__file__)  # research/modalities/tests/test_lint_style.py
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))
sys.path.insert(0, os.path.join(REPO, "research", "manuscripts"))

# NOT importorskip: lint_style is stdlib-only, so a failure to import is a real breakage.
import lint_style  # noqa: E402


def _lint(body):
    """Write `body` as a minimal manuscript (title + body) and return lint_style's findings."""
    text = "# A Title\n\n" + body + "\n"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
        fh.write(text)
        path = fh.name
    try:
        result = lint_style.lint_file(path)
    finally:
        os.unlink(path)
    assert result is not None
    return result["findings"]


def _kinds(findings):
    return {kind for (_lineno, _sev, kind, _msg) in findings}


def test_a_glyph_inside_a_same_line_comment_stays_exempt():
    # This is round 11's own case: the glyph never renders, so it must not fire.
    findings = _lint("Ordinary prose.<!--⛔ maintainer note--> More ordinary prose.")
    assert "glyph" not in _kinds(findings)


def test_a_glyph_outside_a_same_line_comment_is_still_caught():
    # The regression: real prose sharing a comment-bearing line must still be inspected.
    findings = _lint("Ordinary prose ⭐ with a glyph.<!--PMID:1234--> and more prose.")
    assert "glyph" in _kinds(findings)


def test_second_person_outside_a_same_line_comment_is_still_caught():
    findings = _lint("A result holds.<!--PMID:1234--> As you can see, it replicates.")
    assert "second-person" in _kinds(findings)


def test_prose_after_a_same_line_comment_is_still_inspected():
    # The exact shape in the ASO article: a citation marker mid-sentence, ordinary prose after it.
    findings = _lint(
        "The fusion is common,<sup>1</sup><!--PMID:1234--> with a second gene ⛔ rare."
    )
    assert "glyph" in _kinds(findings)


def test_a_genuinely_multiline_comment_is_still_fully_skipped():
    findings = _lint(
        "Clean prose before.\n"
        "<!-- a maintainer note\n"
        "spanning several lines ⛔ with a glyph -->\n"
        "Clean prose after."
    )
    assert "glyph" not in _kinds(findings)


def test_a_comment_only_line_produces_no_entry_but_does_not_swallow_neighbours():
    findings = _lint(
        "Clean prose before.\n"
        "<!-- ⛔ decorative only -->\n"
        "Clean prose ⭐ after, with a glyph."
    )
    assert "glyph" in _kinds(findings)


# ⛔ NO TEST HERE NAMES A REAL SUBMISSION DOCUMENT PATH, ON PURPOSE. The journal article is guarded
# from research/manuscripts/tests/, which preflight runs unscoped -- scripts/tests/test_affected_
# tests.py::test_the_selector_reports_a_documents_guard_truthfully pins that no MODALITY test names
# it, so a static reference to that path here (even to assert "stays clean") would make the selector
# report a modality guard that does not belong to this suite. The corpus-wide, no-regression check
# this fix needs is already run by `./scripts/preflight.sh`'s own lint_style.py pass, which lints all
# 14 real TARGETS including the article, SI, tables and references directly.
