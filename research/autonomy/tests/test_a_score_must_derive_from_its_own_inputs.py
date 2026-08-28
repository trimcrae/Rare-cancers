#!/usr/bin/env python3
"""A score that steers the loop must be a DERIVATION of its own recorded inputs (AUT-PROP-036).

⛔⛔ THE DEFECT THIS SUITE WAS WRITTEN AGAINST, MEASURED BEFORE ANY CODE WAS CHANGED.
`research-ledger.json` promises, in its own `_scores_are_not_evidence` field, that "every input is
echoed in score_inputs so a reader can check the arithmetic against the graph." Nothing checked that
arithmetic, and on 2026-08-28 the arithmetic was wrong and moving. Traced with `git show` across 25
commits of the committed ledger:

    AUT-PROP-036  158.0 → 158.9 → 159.8 → 160.7 → 161.6 → 162.5 → 163.4 → 164.3 → 165.2
                  +0.9 on every re-score, EIGHT re-scores in 92 minutes, while its echoed
                  `age_factor` stayed 0.0714 and its `last_evidence_utc` stayed 2026-08-27.
    AUT-PROP-026  -1344.0 → -2506.8 in one day, -90.0 per re-score.
    AUT-049       105.0 → 117.0, then 117.0 at every subsequent re-score.

⭐ AUT-049 SITTING STILL IS THE OBSERVATION THAT DISCRIMINATES THE CAUSE. `apply_session_penalties`
and `apply_age_factor` were additive mutations. A DERIVED row's base is rebuilt from `systems/graph`
every run, so the term landed on a fresh number and the row was a fixed point of its own pipeline. A
HAND-FILED row's base is last run's output, carried by `merge()` because the graph cannot rebuild
it — so both terms compounded. The terms were never wrong; the base was reused.

⛔ AND IT HAD ALREADY INVERTED THE WORK QUEUE. On that corpus the top 15 rows of `priority.py`'s
ranked table were all hand-filed process/proposal rows at 195.5-199.0, several already marked
"✅ DONE", while the best DERIVED route row sat 78 points below them.

WHAT EACH TEST HOLDS DOWN
  1-4   the predicate's four refusal signatures fire, and fail CLOSED — an unreadable derivation is
        INADMISSIBLE, and a hand-filed number with no derivation is `unaccounted`, never `admitted`.
  5-7   the write path REFUSES rather than writing, including when the baseline it would have to
        compare against cannot be read. A gate that admits what it cannot check is not a gate.
  8     the declared correction is one-shot by construction and cannot become a standing licence.
  9-10  the fixed-point property itself: `priority.py`'s pipeline applied twice moves nothing. This
        is the regression test for the accumulation, and it is the one that would go red first if
        either term were ever made additive again.
  11    the tolerance is the pipeline's own rounding quantum, not a preference.
  12    the receipt corpus's coverage is reported as a NUMBER. `--receipts` says how many receipts
        carry an adjudicable block (zero) rather than reporting the corpus clean, because an absent
        reading is not a reading of absence.
"""

from __future__ import annotations

import copy
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(AUTONOMY))
sys.path.insert(0, AUTONOMY)

import admissibility as A  # noqa: E402
import ledger_io  # noqa: E402
import priority  # noqa: E402

LEDGER = os.path.join(AUTONOMY, "research-ledger.json")


@pytest.fixture(scope="module")
def weights():
    return A.load_weights()


@pytest.fixture(scope="module")
def committed():
    with open(LEDGER, encoding="utf-8") as fh:
        return json.load(fh)


def _derived_row(committed):
    """The first committed row carrying a full derived block — real data, never a fixture I made."""
    for row in committed["entries"]:
        if A._has_full_block(row.get("score_inputs")) and isinstance(row.get("score"), (int, float)):
            return copy.deepcopy(row)
    pytest.skip("no derived row in the committed ledger")


# 1 ------------------------------------------------------------------------------------------
def test_every_committed_derived_score_reproduces_from_its_own_inputs(committed, weights):
    """The promise in `_scores_are_not_evidence`, checked instead of trusted."""
    bad = [(r["id"], A.verdict(r, weights))
           for r in committed["entries"]
           if A._has_full_block(r.get("score_inputs")) and A.verdict(r, weights)[0] != A.ADMITTED]
    assert not bad, f"derived rows whose arithmetic does not check out: {bad}"


# 2 ------------------------------------------------------------------------------------------
def test_a_typed_score_is_refused_at_one_rounding_quantum(committed, weights):
    """⛔ The tolerance must not swallow a real discrepancy. 0.1 is the coarsest value the pipeline
    can emit (`round(x, 1)` in `apply_age_factor`), so one quantum off is REFUSED."""
    row = _derived_row(committed)
    row["score"] = round(row["score"] + 0.1, 2)
    kind, why = A.verdict(row, weights)
    assert kind == A.REFUSED_UNDERIVABLE, (kind, why)
    assert "typed or inherited" in why


def test_float_noise_is_not_refused(committed, weights):
    row = _derived_row(committed)
    row["score"] = row["score"] + 1e-9
    assert A.verdict(row, weights)[0] == A.ADMITTED


# 3 ------------------------------------------------------------------------------------------
@pytest.mark.parametrize("mutate", [
    lambda r: r["score_inputs"].update(cost_class="gratis"),
    lambda r: r["score_inputs"].update(patient_path_scaled="high"),
    lambda r: r["score_inputs"].update(live="yes"),
    lambda r: r["score_inputs"].update(blocker_leverage=None),
    lambda r: r.update(score_inputs=["live", True]),
    lambda r: r.update(score="195.5"),
])
def test_an_unreadable_derivation_is_inadmissible_never_fine(committed, weights, mutate):
    """⛔ FAIL CLOSED. CLAUDE.md §4: an absent reading is not a reading of absence, and a populated
    field is not a measured one. Every one of these is a block that LOOKS filled in."""
    row = _derived_row(committed)
    mutate(row)
    assert A.verdict(row, weights)[0] == A.REFUSED_UNREADABLE


# 4 ------------------------------------------------------------------------------------------
def test_a_hand_filed_score_is_unaccounted_and_that_is_not_a_pass(committed, weights):
    hand = [r for r in committed["entries"]
            if r.get("score") is not None and not A._has_full_block(r.get("score_inputs"))]
    assert hand, "the committed ledger has no hand-filed scored rows — this test is measuring nothing"
    for row in hand:
        kind, _why = A.verdict(row, weights)
        assert kind != A.ADMITTED, f"{row['id']} was admitted with no derivation behind it"
        assert kind in (A.UNACCOUNTED,) + A.REFUSALS


# 5 ------------------------------------------------------------------------------------------
def test_a_score_that_moves_for_no_recorded_reason_is_refused(weights):
    """The accumulation signature, in the exact shape measured on AUT-PROP-036."""
    before = {"id": "X", "score": 158.0, "score_inputs": {"age_factor": 0.0714}}
    after = {"id": "X", "score": 158.9, "score_inputs": {"age_factor": 0.0714}}
    kind, why = A.write_verdict(before, after, weights)
    assert kind == A.REFUSED_ACCUMULATED, (kind, why)
    assert "+0.90" in why and "unexplained" in why


def test_a_move_the_echoed_age_term_accounts_for_is_admitted(weights):
    w = weights["terms"]["age"]["weight"]
    before = {"id": "X", "score": 158.0, "score_inputs": {"age_factor": 0.0}}
    after = {"id": "X", "score": round(158.0 + w * 0.0714, 1), "score_inputs": {"age_factor": 0.0714}}
    assert A.write_verdict(before, after, weights)[0] == A.ADMITTED


def test_a_move_the_evidenced_block_penalty_accounts_for_is_admitted(weights):
    p = weights["terms"]["blocked_with_evidence"]["weight"]
    before = {"id": "X", "score": 195.5, "score_inputs": {}}
    after = {"id": "X", "score": round(195.5 + p, 2), "score_inputs": {"blocked_with_evidence": True}}
    assert A.write_verdict(before, after, weights)[0] == A.ADMITTED


# 6 ------------------------------------------------------------------------------------------
def test_a_stale_echoed_age_factor_is_refused(weights):
    """R4. The echoed input must be the input in force — no wall-clock `N` anywhere in the rule."""
    row = {"id": "X", "state": "queued", "score": 100.0, "last_evidence_utc": "2026-08-01",
           "score_inputs": {"age_factor": 0.0714}}
    kind, why = A.verdict(row, weights, today=__import__("datetime").date(2026, 8, 28))
    assert kind == A.REFUSED_STALE_INPUT, (kind, why)
    assert "not the input in force" in why


@pytest.mark.parametrize("state", ["done", "abandoned", "superseded"])
def test_a_closed_rows_frozen_age_factor_is_not_graded_stale(weights, state):
    """⛔ THE SCOPE IS READ OFF `apply_age_factor`, NOT CHOSEN. It refuses to age a closed row, so a
    closed row's echoed factor is frozen BY DESIGN; grading it stale would red a row that no future
    action could clear — the latching failure `receipt_schema.py` already paid for once.

    ⚠ THE STATES ARE SPELLED OUT HERE RATHER THAN ITERATED FROM `A.CLOSED_STATES`. Mutation M10
    emptied that constant and this test went on passing — a loop over an empty set asserts nothing,
    which is the vacuous-guard failure `paper-hardening` §8b names. Naming them makes emptying the
    constant a red build."""
    row = {"id": "X", "state": state, "score": 100.0, "last_evidence_utc": "2026-08-01",
           "score_inputs": {"age_factor": 0.0714}}
    assert A.verdict(row, weights,
                     today=__import__("datetime").date(2026, 8, 28))[0] != A.REFUSED_STALE_INPUT


def test_the_closed_state_scope_matches_the_states_the_scorer_itself_skips():
    """One fact, one place: if `apply_age_factor` ever ages a state this module exempts, the two
    disagree and the exemption becomes a hole rather than a scope."""
    source = open(os.path.join(AUTONOMY, "priority.py"), encoding="utf-8").read()
    assert '("done", "abandoned", "superseded")' in source, (
        "apply_age_factor's skip list moved — re-derive admissibility.CLOSED_STATES from it")
    assert A.CLOSED_STATES == {"done", "abandoned", "superseded"}


# 7 ------------------------------------------------------------------------------------------
def test_the_write_path_refuses_and_leaves_the_file_untouched(tmp_path, weights):
    path = tmp_path / "research-ledger.json"
    good = {"_schema": "emc-research-ledger/1",
            "entries": [{"id": "X", "score": 158.0, "score_inputs": {"age_factor": 0.0714},
                         "state": "queued", "last_evidence_utc": "2026-08-27"}]}
    ledger_io.write_ledger(path, good, check=False)
    original = path.read_text(encoding="utf-8")

    bad = copy.deepcopy(good)
    bad["entries"][0]["score"] = 158.9
    with pytest.raises(A.InadmissibleWrite) as exc:
        ledger_io.write_ledger(path, bad)
    assert "X" in str(exc.value)
    assert path.read_text(encoding="utf-8") == original, "a refused write still touched the file"


def test_an_unreadable_baseline_refuses_the_write(tmp_path):
    """⛔ A baseline we cannot read is NOT a baseline of nothing."""
    path = tmp_path / "research-ledger.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(A.InadmissibleWrite):
        ledger_io.write_ledger(path, {"entries": []})


def test_a_genuine_first_write_is_allowed(tmp_path):
    path = tmp_path / "research-ledger.json"
    ledger_io.write_ledger(path, {"_schema": "emc-research-ledger/1", "entries": []})
    assert json.loads(path.read_text(encoding="utf-8"))["entries"] == []


# 8 ------------------------------------------------------------------------------------------
def test_a_declared_correction_is_admitted_once_and_cannot_become_a_licence(weights):
    before = {"id": "X", "score": 158.0, "score_inputs": {}}
    after = {"id": "X", "score": 100.0, "score_inputs": {},
             A.CORRECTION_KEY: "removing the residue AUT-PROP-036 measured"}
    assert A.write_verdict(before, after, weights)[0] == A.ADMITTED

    # ⛔ The SAME note left in place on a later move is not a second correction.
    later = copy.deepcopy(after)
    later["score"] = 50.0
    assert A.write_verdict(after, later, weights)[0] == A.REFUSED_ACCUMULATED
    for empty in ("", "   ", None, 7):
        blank = copy.deepcopy(after)
        blank[A.CORRECTION_KEY] = empty
        assert A.write_verdict(before, blank, weights)[0] == A.REFUSED_ACCUMULATED


# 9 ------------------------------------------------------------------------------------------
def test_the_scoring_pipeline_is_a_fixed_point_of_itself():
    """⭐ THE REGRESSION TEST FOR THE ACCUMULATION. Score the real graph and ledger, then score the
    RESULT again. Nothing may move: a derivation applied twice gives the same answer, an
    accumulation does not. Before the fix this moved 13 rows, by up to 89.1."""
    w = priority.load_weights()
    first = priority.build_ledger()
    def _again(state):
        entries = priority.merge(priority.build_entries(w), state)
        entries = priority.apply_age_factor(entries, w)
        entries = priority.apply_session_penalties(entries, w)
        entries = priority.apply_fruitless_attempts(entries, w)
        entries = priority.apply_requires_trimcrae(entries, w)
        return {"entries": entries}
    second = _again(first)
    was = {e["id"]: e.get("score") for e in first["entries"]}
    now = {e["id"]: e.get("score") for e in second["entries"]}
    moved = {k: (was[k], now[k]) for k in was if was.get(k) != now.get(k)}
    assert not moved, f"the pipeline is not a fixed point of itself: {moved}"


def test_a_third_application_still_moves_nothing():
    """Two applications could coincide by luck; three cannot."""
    w = priority.load_weights()
    state = priority.build_ledger()
    scores = []
    for _ in range(3):
        entries = priority.merge(priority.build_entries(w), state)
        entries = priority.apply_age_factor(entries, w)
        entries = priority.apply_session_penalties(entries, w)
        entries = priority.apply_fruitless_attempts(entries, w)
        entries = priority.apply_requires_trimcrae(entries, w)
        state = {"entries": entries}
        scores.append({e["id"]: e.get("score") for e in entries})
    assert scores[0] == scores[1] == scores[2]


# 9b -----------------------------------------------------------------------------------------
def test_the_hand_copied_pipeline_matches_the_real_one():
    """⛔ TESTS 9 AND 9a RE-LIST `build_ledger`'s POST-MERGE STAGES BY HAND, AND A HAND COPY DRIFTS.

    Measured 2026-08-28 (AUT-PD-127): `apply_requires_trimcrae` was added to `build_ledger` and NOT
    to those two helpers, so test 9 went red reporting eleven rows as an accumulation. It was not an
    accumulation — the two pipelines had simply diverged, and the "fixed point" being asserted was
    between `build_ledger` and a DIFFERENT pipeline that happened to be one stage shorter. A red
    test that names the wrong cause is worse than a missing one: the obvious repair is to weaken
    test 9, which would have retired the regression guard for the real accumulation it exists to
    catch (AUT-PROP-036, -90.0 per re-score).

    ⭐ SO THE COPY IS CHECKED AGAINST THE ORIGINAL RATHER THAN TRUSTED. Adding a stage to
    `build_ledger` and forgetting the helpers now fails HERE, naming the stage, instead of failing
    there as a phantom accumulation.
    """
    import re
    src = open(os.path.join(AUTONOMY, "priority.py")).read()
    real = re.findall(r"entries = (apply_\w+)\(", src.split("def build_ledger()", 1)[1])
    assert real, "no apply_* stages found in build_ledger — the parse is wrong, not the code"

    mine = open(os.path.abspath(__file__)).read()
    for helper in ("def test_the_scoring_pipeline_is_a_fixed_point_of_itself",
                   "def test_a_third_application_still_moves_nothing"):
        body = mine.split(helper, 1)[1].split("\ndef ", 1)[0]
        copied = re.findall(r"entries = priority\.(apply_\w+)\(", body)
        assert copied == real, (
            f"{helper} applies {copied}, build_ledger applies {real} — "
            f"missing: {[s for s in real if s not in copied]}")


# 10 -----------------------------------------------------------------------------------------
def test_the_evidenced_block_penalty_toggles_both_ways():
    """⛔ Clearing the evidence must REMOVE the penalty, not leave it baked in. A one-way term is
    how the row stops being a fixed point in the other direction."""
    w = priority.load_weights()
    p = w["terms"]["blocked_with_evidence"]["weight"]
    row = {"id": "X", "score": 100.0, "blocked_evidence": "measured it", "score_inputs": {}}
    priority.apply_session_penalties([row], w)
    assert row["score"] == round(100.0 + p, 2)
    assert row["score_inputs"]["blocked_with_evidence"] is True
    priority.apply_session_penalties([row], w)
    assert row["score"] == round(100.0 + p, 2), "the penalty was applied twice"
    row["blocked_evidence"] = None
    priority.apply_session_penalties([row], w)
    assert row["score"] == 100.0
    assert "blocked_with_evidence" not in row["score_inputs"]


def test_the_age_term_shrinks_when_the_evidence_is_refreshed():
    """A ratchet is not a derivation: a lower age factor must lower the bonus."""
    import datetime
    w = priority.load_weights()
    row = {"id": "X", "score": 100.0, "state": "queued", "last_evidence_utc": "2026-08-01"}
    priority.apply_age_factor([row], w, today=datetime.date(2026, 8, 28))
    aged = row["score"]
    assert aged > 100.0
    row["last_evidence_utc"] = "2026-08-28"
    priority.apply_age_factor([row], w, today=datetime.date(2026, 8, 28))
    assert row["score"] == 100.0
    assert "age_factor" not in (row.get("score_inputs") or {})


def test_a_prerequisite_chain_resolves_to_the_same_scores_in_any_row_order():
    """⛔⛔ THE ORDER-DEPENDENCE THE ADMISSION GATE FOUND (AUT-PROP-036). `apply_session_penalties`
    used to walk `entries` in list order and read `parent["score"]` wherever it landed, so a
    prerequisite whose parent is ITSELF a prerequisite inherited whichever value happened to be
    there — and added back a 90-point penalty its parent's freshly-assigned score did not contain.
    Measured on the committed ledger: AUT-PROP-021 and AUT-PROP-022 moved 196.9 → 286.9 and
    196.0 → 286.0 on a re-score that changed no evidence.

    ⚠ This test exists because the fixed-point tests did NOT catch it (mutation M11 survived them):
    once a chain has resolved, re-running from the resolved state reproduces it. The defect is
    visible only from a STALE parent score, which is what a real re-score always starts from."""
    w = priority.load_weights()
    bonus = w["prerequisite_bonus"]["value"]

    def rows():
        return {
            "G": {"id": "G", "score": 195.0, "score_inputs": {}},
            "P": {"id": "P", "score": 999.0, "prerequisite_of": "G",
                  "score_inputs": {"blocked_with_evidence": True}},
            "C": {"id": "C", "score": 999.0, "prerequisite_of": "P",
                  "score_inputs": {"blocked_with_evidence": True}},
        }

    results = []
    for order in (["C", "P", "G"], ["G", "P", "C"], ["P", "C", "G"]):
        table = rows()
        priority.apply_session_penalties([table[k] for k in order], w)
        results.append({k: table[k]["score"] for k in ("G", "P", "C")})

    assert results[0] == results[1] == results[2], f"the chain is order-dependent: {results}"
    assert results[0]["P"] == round(195.0 + bonus, 2)
    assert results[0]["C"] == round(195.0 + 2 * bonus, 2), (
        "a child of a freshly-assigned prerequisite must not have its parent's evidenced-block "
        f"penalty added back — got {results[0]['C']}")


# 11 -----------------------------------------------------------------------------------------
def test_the_tolerance_is_the_pipelines_own_rounding_quantum():
    """⛔ NOT A PREFERENCE. `priority.py` emits through `round(x, 1)` at its coarsest, so the
    smallest real difference it can express is 0.1 and the band is half of it."""
    source = open(os.path.join(AUTONOMY, "priority.py"), encoding="utf-8").read()
    assert ", 1)" in source, "apply_age_factor no longer rounds to 1 dp — re-derive TOLERANCE"
    assert A.TOLERANCE == 0.05


# 12 -----------------------------------------------------------------------------------------
def test_the_receipt_corpus_coverage_is_reported_as_a_number_not_as_clean():
    """⛔ An absent reading is not a reading of absence. This gate reads a JSON `score_inputs`
    block; a receipt records its claims as prose. Saying nothing was refused there without saying
    how many receipts were even adjudicable would be the false-absence failure `receipt_schema.py`
    was filed against."""
    cov = A.receipt_coverage()
    assert cov["receipts"] > 0, "no receipts found — the reporter is measuring nothing"
    assert "carrying_a_score_inputs_block" in cov
    assert cov["carrying_a_score_inputs_block"] <= cov["receipts"]
