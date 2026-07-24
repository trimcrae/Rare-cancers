"""Regression tests for the manuscript language-discipline linter.

The linter's whole value rests on ONE property: a regulated word in a *disclaimed*
sentence must PASS. A linter that cries wolf on "makes no efficacy claim" gets ignored,
and an ignored linter is worse than none -- that exact false positive (a naive substring
match reported as "linter FAIL: SI:89 efficacy") is why `lint_claims.py` was written.

So these tests pin both directions: assertive use is caught, disclaimed use is cleared.
"""

import os
import sys

import pytest

_HERE = os.path.abspath(__file__)  # research/modalities/tests/test_lint_claims.py
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))
sys.path.insert(0, os.path.join(REPO, "research", "manuscripts"))

# NOT importorskip: lint_claims is stdlib-only, so a failure to import is a real breakage
# and must fail the suite loudly rather than silently skipping the whole file.
import lint_claims  # noqa: E402


def _lint(tmp_path, text, name="doc.md"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return lint_claims.lint_file(str(p))


def _rules(findings):
    return {f["rule"] for f in findings}


# --------------------------------------------------------------------------
# The regulated set must FIRE on assertion
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text,rule",
    [
        ("The compound shows efficacy in EMC models.", "R2-efficacy"),
        ("The series has a wide therapeutic window.", "R2-therapeutic-window"),
        ("This candidate is clinically ready.", "R2-clinical-readiness"),
        ("The scaffold is safe and effective.", "R2-safe"),
        ("We report proteome-wide selectivity for the lead.", "R2-proteome-wide"),
        ("This is a landmark result for the field.", "R3-landmark"),
        ("We deliver a synthesis-ready matrix of degraders.", "R1-synthesis-ready"),
        ("Three selective hits emerged from the screen.", "R1-selective-hit"),
        ("The workflow recovered degradation for NR4A1.", "R1-recovered-degradation"),
        ("The ternary edge cost a measured ~$7 per edge.", "R5-measured-edge-cost"),
    ],
)
def test_assertive_claim_is_flagged(tmp_path, text, rule):
    assert rule in _rules(_lint(tmp_path, text)), f"{rule} should fire on: {text}"


# --------------------------------------------------------------------------
# ...and must NOT fire when the sentence scopes the claim out.
# These strings are real (or near-real) sentences from the manuscript.
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text",
    [
        "It makes **no efficacy, potency, or therapeutic claim.**",
        "This paper's claimed contribution is the target's computational "
        "druggability/selectivity, not EMC efficacy.",
        "degrader efficacy, like any modality's, is context-dependent and not guaranteed "
        "by target removal alone",
        "it makes the degrader's efficacy claim *quantitative and falsifiable* rather than "
        '"a ternary forms"',
        "The candidate set is explicitly not clinically ready and no therapeutic window is claimed.",
        "Nothing here establishes safety; safety is delegated to a future program.",
        # The endpoint-MD panel IS a completed 15-leg ledger measurement, so this true
        # statement must not be flagged as a mislabelled projection (R5 is scoped to the
        # per-edge alchemical bases, which are the projected ones).
        "it ran end-to-end on Vast.ai community RTX 3090s at a measured ~$0.43 per leg "
        "(~$8 for the full 18-leg panel)",
    ],
)
def test_disclaimed_use_is_cleared(tmp_path, text):
    findings = _lint(tmp_path, text)
    hard = [f for f in findings if f["severity"] == "ERROR"]
    assert hard == [], f"disclaimed sentence must not ERROR: {text} -> {hard}"


# --------------------------------------------------------------------------
# Hard-wrap handling -- the bug that produced the original false positives
# --------------------------------------------------------------------------
def test_disclaimer_carries_across_a_hard_wrapped_line(tmp_path):
    """The manuscript hard-wraps prose, so a claim and its disclaimer land on
    different physical lines. Line-at-a-time scanning severs them."""
    text = (
        "The program has no loss-of-function experiment in any EMC model and therefore no\n"
        "demonstrated efficacy. Therapeutic application additionally assumes NR4A3 dependence.\n"
    )
    hard = [f for f in _lint(tmp_path, text) if f["severity"] == "ERROR"]
    assert hard == [], f"wrapped disclaimer must clear the claim, got {hard}"


def test_paragraph_break_does_not_leak_a_disclaimer(tmp_path):
    """A disclaimer in a *different* paragraph must NOT clear a later assertion."""
    text = "We make no efficacy claim.\n\nThe compound shows efficacy in EMC models.\n"
    assert "R2-efficacy" in _rules(_lint(tmp_path, text))


# --------------------------------------------------------------------------
# Non-prose contexts are not claims
# --------------------------------------------------------------------------
def test_code_fence_is_not_scanned(tmp_path):
    text = "```\nefficacy = compute_efficacy()  # landmark\n```\n"
    assert _lint(tmp_path, text) == []


def test_reference_title_is_not_the_papers_own_claim(tmp_path):
    """Quoting a cited work's title that contains a regulated phrase is not a claim."""
    text = "[Neosubstrate basis of the del(5q) therapeutic window.]\n"
    assert _lint(tmp_path, text) == []


# --------------------------------------------------------------------------
# Severity contract
# --------------------------------------------------------------------------
def test_exit_code_is_driven_by_errors_not_warns(tmp_path):
    warn_only = tmp_path / "w.md"
    warn_only.write_text("The endpoint tier confirms tri-paralogue engagement.\n", encoding="utf-8")
    findings = lint_claims.lint_file(str(warn_only))
    assert findings and all(f["severity"] == "WARN" for f in findings)
    assert lint_claims.main([str(warn_only)]) == 0
    assert lint_claims.main(["--warn-as-error", str(warn_only)]) == 1


def test_shipped_manuscript_has_no_errors():
    """The real paper + SI must stay ERROR-clean. This is the gate that matters."""
    assert lint_claims.main([]) == 0, "manuscript/SI has language-discipline ERRORs"


# --------------------------------------------------------- local-negation clearing (R1)
def test_local_negation_clears_disclaimed_earned_phrase():
    # "present it as a research hypothesis, NOT among synthesis-ready degrader claims"
    # correctly disclaims the phrase and must pass.
    assert lint_claims._locally_negated("present it as a hypothesis, NOT among synthesis-ready claims",
                               "present it as a hypothesis, NOT among ".__len__())


def test_local_negation_does_not_clear_an_assertion_that_merely_contains_not():
    # "a synthesis-ready matrix, not another in-silico lead" ASSERTS the phrase; the "not"
    # negates something else downstream. Sentence-level disclaimer detection cleared this
    # one wrongly, which is why the earned-phrase rules use local negation instead.
    sent = "Deliverable: a synthesis-ready matrix, not another in-silico lead"
    assert not lint_claims._locally_negated(sent, sent.index("synthesis-ready"))


def test_earned_phrase_rules_use_local_negation():
    for rid in ("R1-synthesis-ready", "R1-selective-hit"):
        rule = next(r for r in lint_claims.RULES if r.rid == rid)
        assert rule.clears_on == "local_negation", rid


def test_strategy_and_plan_docs_are_clean_of_banned_phrases():
    import os
    targets = ["research/manuscripts/nr4a3-congeneric-rbfe-plan.md",
               "research/manuscripts/nr4a3-degrader-strategy-ternary-first.md",
               "research/compute/access-allocation-request.md"]
    errs = []
    for t in targets:
        p = os.path.join(lint_claims.REPO, t)
        if os.path.exists(p):
            errs += [f for f in lint_claims.lint_file(p) if f["severity"] == "ERROR"]
    assert not errs, errs
