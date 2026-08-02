"""The step-3 preregistration DRAFT cannot be mistaken for a frozen one, and cannot go stale silently.

★★ WHY A DRAFT PREREGISTRATION NEEDS A GUARD AT ALL. This repo's whole claim to preregistration rests on
documents that were demonstrably fixed before their data. A draft sitting in the same directory, in the same
format, is the one thing that could erode that: read six months later, "DRAFT" is a word in a header and
`PASS_CRITERION`-shaped prose is prose. So the draft's unfrozen status is asserted mechanically, and the
fields that are deliberately unfilled are asserted to be STILL unfilled — because the failure mode is not
someone forging a freeze, it is someone quietly deleting a `⬜ TO BE FILLED` marker and leaving nothing.

It is written BEFORE the verdict it is gated on, deliberately: a prereg drafted after seeing that result
cannot be shown not to have been tuned to it.
"""
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
DRAFT = os.path.join(MOD, "nr4a-repanel-prereg-DRAFT.md")

MARKER = "⬜ TO BE FILLED"


def _text():
    with open(DRAFT, encoding="utf-8") as fh:
        return fh.read()


def _flat():
    """⚠ WHITESPACE-NORMALISED. Prose re-wraps; an assertion that pins a line break tests the editor's
    column width, not the document. (Tonight's recurring lesson, applied before it bit again.)"""
    return " ".join(_text().split())


def test_the_draft_declares_itself_unfrozen_and_unrunnable():
    t = _text()
    assert "NOT FROZEN" in t and "NOT IN FORCE" in t
    assert "NOTHING MAY BE RUN AGAINST IT" in t
    assert t.lstrip().startswith("# NR4A1/2/3 RE-PANEL"), "the status must be at the very top, not buried"
    head = t[:1600]
    assert "NOT FROZEN" in head, "a reader must hit the status before any design content"


def test_the_filename_still_says_draft():
    """The freeze is a separate dated commit that RENAMES the file. While it is named -DRAFT it is a draft,
    and that is deliberately impossible to get wrong by editing prose alone."""
    assert DRAFT.endswith("-DRAFT.md")


def test_every_unfilled_field_is_still_marked():
    """⚠ THE REAL FAILURE MODE. Nobody forges a freeze stamp; somebody deletes a marker and leaves a blank,
    and the document then reads as complete. Each marker must be followed by a description of what fills it
    and where that value is DERIVED — a marker with no derivation named is a wish, not a placeholder."""
    t = _text()
    # Only the FIELD markers, not the status block's prose ABOUT them — the two are different claims and
    # counting the explanation as a placeholder would let every real one be deleted while the test passed.
    markers = [ln.strip() for ln in t.splitlines()
               if ln.lstrip().startswith("- **" + MARKER)]
    # ⚠ A FLOOR THAT TRACKS REALITY. Three markers (σ, exact power, what-it-cannot-detect) were FILLED from
    # derivations on 2026-08-02, so the floor came down to match. Lowering it is only legitimate alongside
    # the values that replaced them — which `test_the_power_section_is_derived_not_promised` now requires.
    assert len(markers) >= 3, f"expected the unfilled fields to still be marked, found {len(markers)}"
    for ln in markers:
        assert "—" in ln, f"marker names no field: {ln!r}"


def test_the_freeze_conditions_are_enumerated_and_include_the_verdict():
    t = _text()
    assert "tier: PASS" in t
    assert "retired unrun" in t.lower() or "retired UNRUN" in t
    for cond in ("selcal-verdict.json", "TO BE FILLED", "trimcrae", "loses `-DRAFT`"):
        assert cond in t, cond


def test_no_leg_count_and_no_dollar_figure_is_typed_into_the_prereg():
    """⛔ CLAUDE.md §1. Step 3's shape and price are DERIVED by `recommended_sequence`; a copy here would go
    stale silently and then be quoted in a paper. The document must POINT."""
    t = _text()
    body = "\n".join(ln for ln in t.splitlines() if not ln.strip().startswith(">"))
    # The measured supervision-leak figures are quoted deliberately and cited; everything else must not be.
    allowed = {"$25.83", "$1.57"}
    found = set(re.findall(r"\$\s?[\d,]+(?:\.\d+)?", body))
    assert found <= allowed, f"undeclared dollar figures typed into the prereg: {sorted(found - allowed)}"
    assert "NR4A_REPANEL_SHAPE" in t and "recommended_sequence" in t


def test_the_endpoint_is_E1_and_the_reason_for_not_re_choosing_is_recorded():
    """Keeping E1 is a DECISION, not an omission: choosing whichever endpoint separated best on the landed
    panel and then testing on new models is endpoint-shopping, the retune this program forbids."""
    t = _text()
    assert "E1, unchanged" in t or "**E1, unchanged**" in t
    assert "endpoint-shopping" in t
    assert "promoted none" in t, "step 1 reported E2/E3/E4 and promoted none — that is the licence to keep E1"
    assert "reported alongside E1" in t, "reporting E2-E4 is an inherited preregistered obligation"


def test_the_covalency_confound_is_stated_as_a_limit_no_n_removes():
    """The system is covalency-confounded (Cys551 unique to NR4A1), so a positive result is directional
    concordance, never an attribution to ternary geometry. Stating it AFTER the run would be a caveat;
    stating it here makes it a design constraint."""
    t = _text()
    assert "Cys551" in t and "covalency-confounded" in t
    assert "no `n` removes it" in _flat()


def test_it_is_not_framed_as_an_extension_of_the_retrospective_prereg():
    """§4d may not be invoked on a wrong-sign result, and the retrospective returned DISCORDANT."""
    t = _text()
    assert "NOT an extension" in t or "NOT AN EXTENSION" in t.upper()
    assert "4d" in t


def test_the_16_landed_legs_decision_is_OPEN_and_declared():
    """The options paper requires the re-use question to be declared IN ADVANCE. The draft must ask it, take
    a position, and record the argument against that position — not decide it silently."""
    t = _text()
    sec = t[t.index("THE ONE OPEN DECISION"):]
    assert "DO NOT re-use" in sec, "the draft must state a position"
    assert "Against" in sec, "and record the strongest argument against it"
    assert "before the freeze" in sec.lower()


def test_the_admissibility_rule_is_by_proportion_not_a_copied_integer():
    """`nrv04_retro_gate` uses 1 for arms of 6; `selcal_panel` deliberately uses 2 for arms of 12 and records
    why copying the integer across is a stricter rule arrived at by accident."""
    t = _text()
    assert "PROPORTION" in t
    assert "MAX_FAILED_LEGS_PER_ARM" in t
    assert not re.search(r"allowance[^\n]*=\s*\d", t), "the allowance must not be a typed integer yet"


def test_power_is_not_claimed_from_the_normal_approximation():
    """Measured: at the delta the approximation calls 80 % power, the exact rule delivered 0.64-0.74 on the
    prior panel — and 0.757 at THIS design. No power claim may be sourced from the approximation."""
    t = _text()
    assert "No power claim in this document may be sourced from the approximation" in t
    assert "0.64" in t and "optimism" in t.lower()
    assert "0.757" in t, "the exact value at this design must be stated, not just the approximation's claim"


def test_the_power_section_is_derived_not_promised():
    """The σ and the exact power table must carry real numbers from the named derivations."""
    t = _text()
    assert "1.0278" in t and "which_sigma" in t
    assert "power_primary" in t and "power_pairwise" in t
    assert "n_sims = 2000" in t, "a Monte-Carlo power figure must state its own uncertainty"


def test_the_design_states_what_it_CANNOT_detect_against_the_OBSERVED_effect():
    """★★ THE FINDING THAT MOST CHANGES WHAT STEP 3 MEANS. At this shape the exact power against the
    separations this program has already measured is ~0.16 (pairwise, δ=0.4124 Å) and ~0.13 (primary,
    δ=0.2825 Å) — so a null would be returned roughly five times in six even if the effect is real at the
    observed size. Fixed BEFORE the run, because it decides what a null is allowed to mean."""
    t = _text()
    assert "0.4124" in t and "0.159" in t
    assert "0.2825" in t and "0.130" in t
    assert '"δ ≳ 1.5 Å", not "δ > 0"' in t, "the restricted null must be stated explicitly"
    assert "uninformative" in t


def test_the_underpowered_finding_is_a_live_decision_not_a_caveat():
    """Three responses are recorded with a recommendation, so the shape is chosen deliberately rather than
    inherited. A finding this size buried as a limitation would be the paper writing around it."""
    t = _text()
    sec = t[t.index("CANNOT DETECT"):]
    assert "live design question, not a caveat" in sec
    for opt in ("Run as shaped", "Re-shape to a powered design", "Do not run step 3"):
        assert opt in sec, opt
    assert "Recommended" in sec


def test_no_interim_analysis_is_carried_forward():
    t = _text()
    assert "No interim analysis" in t or "no interim analysis" in t
    assert "suppress the tier" in t


@pytest.mark.parametrize("tier_word", ["null", "wrong-sign", "INDETERMINATE"])
def test_every_outcome_is_pre_licensed(tier_word):
    """What each outcome licenses is written BEFORE the run, so none can be re-narrated afterwards."""
    t = _text()
    assert tier_word.lower() in t.lower()


def test_supervision_is_a_precondition():
    """The NR-V04 ledger recorded $25.83 leaked against $1.57 of compute. A panel cheap to compute and
    expensive to supervise has not been costed."""
    t = _text()
    assert "leaked_usd" in t and "25.83" in t
    assert "precondition" in t.lower()


def test_the_power_figures_are_declared_UPPER_BOUNDS():
    """⚠ `power_primary`'s own docstring says it does NOT apply leave-one-model-out — LOMO sat outside the
    conjunction on the panel it was written for. §4 of this prereg REQUIRES LOMO survival, and adding a
    condition can only lower the pass probability. So every figure is an upper bound, and the already-bleak
    power against the observed effect is bleaker still. Stated as a DIRECTION, not an estimate: quantifying
    it needs a LOMO-aware simulator, and an unmeasured correction is not a number."""
    t = _text()
    assert "UPPER BOUND" in t.upper()
    assert "leave-one-model-out" in t or "LOMO" in t
    assert "at or below" in t
    assert "an unmeasured correction is not a number" in t


# =============================================================================================================
# the retirement — 2026-08-02, step 2 returned NULL
# =============================================================================================================
def test_the_draft_is_RETIRED_because_step_2_did_not_PASS():
    """★★ The freeze conditions required `tier: PASS`. Step 2 returned NULL, so §7's own rule applies: this
    document is RETIRED UNRUN, not amended. The retirement is asserted against the LIVE verdict rather than
    against prose, so the two can never drift apart — if a future step 2 ever passes, this test is what makes
    someone revisit the retirement deliberately instead of the banner quietly outliving its cause."""
    import json
    v = json.load(open(os.path.join(MOD, "selcal-verdict.json")))
    t = _text()
    if v.get("tier") == "PASS":
        assert "RETIRED UNRUN" not in t.upper()[:2000], \
            "step 2 PASSES, so this document must no longer be marked retired"
        return
    assert "RETIRED UNRUN" in t.upper(), (
        "step 2 returned %r, which is not PASS, so this document must be marked RETIRED UNRUN at the top"
        % v.get("tier"))
    head = t[:2200]
    assert "RETIRED UNRUN" in head.upper(), "the retirement must precede any design content"
    assert "not amended" in head.lower() or "NOT AMENDED" in head, \
        "§7's rule is retire-not-amend; the banner must say which happened"


def test_the_retirement_KEEPS_the_document_rather_than_gutting_it():
    """⚠ The value of a prereg written before its verdict is that it PROVES the design was not tuned to the
    result. Deleting or hollowing it on retirement destroys exactly that evidence, so the design content and
    the power finding must survive the retirement intact."""
    t = _text()
    assert len(t) > 8000, "the retired draft has been gutted; its whole evidentiary value is being complete"
    for kept in ("0.159", "0.130", "1.0278", "power_primary", "NR4A_REPANEL_SHAPE"):
        assert kept in t, f"{kept} did not survive the retirement"
    assert "before" in t[:2200].lower(), "the banner must say the design predates the verdict that killed it"


def test_the_retirement_points_at_the_verdict_that_caused_it():
    t = _text()
    assert "selcal-verdict.json" in t
    assert "0.7468" in t, "the retirement must quote the p-value that triggered it, not just assert a tier"
