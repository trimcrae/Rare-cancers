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


def test_local_negation_survives_quotes_and_emphasis_around_the_phrase():
    # A prereg's banned-phrase list writes the phrase in quotes or emphasis after the negation:
    #   never "synthesis-ready" ... / no **synthesis-ready** claim
    # The quote must not defeat the scoping (it did, on the NR-V04 retrospective prereg, 2026-07-24).
    for sent in ('Forbidden: never "synthesis-ready" language',
                 "Forbidden: no **synthesis-ready** claim",
                 "Forbidden: never `synthesis-ready`"):
        assert lint_claims._locally_negated(sent, sent.index("synthesis-ready")), sent


def test_local_negation_does_not_leak_across_a_sentence_boundary():
    # Clause-ending punctuation still blocks it: the negation applies to the PREVIOUS sentence.
    sent = "The matrix is not final. It is a synthesis-ready deliverable"
    assert not lint_claims._locally_negated(sent, sent.index("synthesis-ready"))


def test_earned_phrase_rules_use_local_negation():
    for rid in ("R1-synthesis-ready", "R1-selective-hit", "R1-recovered-degradation"):
        rule = next(r for r in lint_claims.RULES if r.rid == rid)
        assert rule.clears_on == "local_negation", rid


# -------------------------------------------------------------------------------------------------
# A document that MANDATES a replacement has to be able to name the phrase it replaces.
#
# THE INCIDENT (2026-08-02). The language-discipline section — which states every R1 rule as a
# substitution, `"selective hit" → **"predicted selective candidate"**` — lived in STRATEGY.md, which
# this linter does not read. The roadmap merge moved it into the roadmap, which this linter DOES
# read, and three R1 rules immediately ERRORed on their own definitions. That is the "a linter that
# flags true statements gets ignored" failure this file's docstring is built around.
# -------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text",
    [
        '- "selective hit" → **"predicted selective candidate"**',
        '- "synthesis-ready matrix" → **"a computationally prioritized candidate matrix"**',
        '- "recovered degradation" → **"produced a surrogate score concordant with the outcome"**',
        '"selective hit" -> "predicted selective candidate"',
    ],
)
def test_a_substitution_rule_naming_a_banned_phrase_is_not_a_claim(tmp_path, text):
    hard = [f for f in _lint(tmp_path, text) if f["severity"] == "ERROR"]
    assert hard == [], f"a substitution rule must not ERROR on its own left-hand side: {text} -> {hard}"


@pytest.mark.parametrize(
    "text",
    [
        # No arrow into a replacement: this is the claim, and it must still fire.
        "Deliverable: a synthesis-ready matrix, not another in-silico lead",
        "The workflow recovered degradation for NR4A1.",
        "Three selective hits emerged from the screen.",
    ],
)
def test_the_substitution_clearing_does_not_excuse_an_assertion(tmp_path, text):
    hard = [f for f in _lint(tmp_path, text) if f["severity"] == "ERROR"]
    assert hard, f"an assertion must still ERROR: {text}"


def test_a_prohibition_that_names_the_phrase_is_cleared_but_the_claim_is_not(tmp_path):
    """Validation requirement 4's own wording: `... — never "recovered degradation."`

    It PROHIBITS the phrase by naming it, and the merge moved that text into a linted file. Only a
    negation sitting immediately before the phrase clears it, so the bare assertion still ERRORs —
    that pair is the whole point of using `local_negation` rather than a blanket disclaimer.
    """
    ok = 'Report only directional concordance with the reported outcome — never "recovered degradation."'
    assert [f for f in _lint(tmp_path, ok) if f["severity"] == "ERROR"] == []
    bad = "The retrospective recovered degradation for NR4A1 and NR4A2."
    assert [f for f in _lint(tmp_path, bad) if f["rule"] == "R1-recovered-degradation"]


def test_R5_ignores_a_zero_dollar_figure_but_not_a_real_one(tmp_path):
    """`$0` is the ABSENCE of a cost, so it can never be the mislabelled projection R5 catches.

    Measured case: the merge moved "(measured 2026-07-28, $0 CPU, `ternary-system-census.yml`)" into a
    linted file and R5 fired on a true statement about free CPU work. A real sub-dollar figure is
    still checked — the narrowing is `$0`, not `$0.xx`.
    """
    free = ("The ternary edge's system identity is answered from the trajectories "
            "(measured 2026-07-28, $0 CPU, ternary-system-census.yml).")
    assert [f for f in _lint(tmp_path, free) if f["rule"] == "R5-measured-edge-cost"] == []
    real = "The ternary edge cost a measured ~$7 per edge."
    assert [f for f in _lint(tmp_path, real) if f["rule"] == "R5-measured-edge-cost"]


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


# =============================================================================================================
# the sensitivity control's NULL must reach a reader who never opens §4
# =============================================================================================================
def _paper():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(here, "..", "..", "manuscripts", "nr4a3-degrader-paper.md")
    if not os.path.exists(p):
        p = os.path.join(here, "..", "..", "..", "research", "manuscripts", "nr4a3-degrader-paper.md")
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def _flat(s):
    """⚠ WHITESPACE-NORMALISED. Prose re-wraps, and an assertion that pins a line break tests the editor's
    column width rather than the document. Caught here immediately: `positive control` fell across a newline
    in §4, so a raw substring check reported the phrase missing from a section that plainly contains it —
    the same lesson `test_nr4a_repanel_prereg_draft._flat` records."""
    return " ".join(s.split())


def _sections(t):
    ab, r1 = t.index("## Abstract"), t.index("## 1. Background")
    res, meth = t.index("## 2. Results"), t.index("## 3. Methods")
    lim = t.index("## 4. Limitations")
    return {"Abstract": t[ab:r1], "Results": t[res:meth], "Limitations": t[lim:]}


def test_the_unvalidated_prediction_scope_statement_reaches_all_three_sections():
    """★★ THE CLAIM THAT WAS ASPIRATIONAL WHEN WRITTEN. §2.12a asserted the consequence was 'carried in the
    language of every selectivity statement in this paper rather than confined to a limitations paragraph' —
    and a grep showed the phrase existed exactly ONCE, inside §2.12a itself. A paper that says where its own
    caveats live is making a checkable claim, so it gets checked.

    Three levels, deliberately, and NOT appended to each individual ΔΔG: this is a scope statement about the
    whole workflow, and repeating it twenty times would dilute rather than strengthen it.
    """
    secs = _sections(_paper())
    for name, body in secs.items():
        assert "unvalidated prediction" in _flat(body).lower(), (
            "the sensitivity control's NULL does not reach §%s — a reader who stops before the limitations "
            "would never learn that no positive control for selectivity detection exists" % name)


def test_the_null_is_reported_with_the_ambiguity_it_cannot_resolve():
    """⛔ A fail does NOT distinguish 'the readout is blunt' from 'this pair is hard'. Reporting the null
    without that clause would let it read as a measured statement about the method, which it is not."""
    flat = _flat(_paper())
    assert "does not distinguish" in flat.lower()
    for token in ("insensitive readout", "narrow structural signal"):
        assert token in flat, token


def test_the_three_failed_controls_are_named_together_not_scattered():
    """The force of the finding is that ALL THREE attempts failed, each for a different reason. Listed
    separately in three sections they read as three caveats; together they read as the conclusion."""
    t = _paper()
    for name, body in (("Abstract", _sections(t)["Abstract"]), ("Limitations", _sections(t)["Limitations"])):
        flat = _flat(body).lower()
        assert "three" in flat, name
        assert "positive control" in flat, name


def test_the_null_does_not_overclaim_against_individual_numbers():
    """⚠ The tempting misreading in the OTHER direction. A null on the control does not retroactively
    invalidate any landed ΔΔG — it removes the evidence that the workflow can resolve a paralogue difference
    at all, which is broader and different. Stating only the first would be alarmism dressed as rigour."""
    lim = _flat(_sections(_paper())["Limitations"])
    assert "not retroactively invalidate" in lim.replace("**", "")
