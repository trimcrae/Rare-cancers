#!/usr/bin/env python3
"""AN ADMISSION GATE FOR THE ONE PIECE OF EVIDENCE THE LOOP USES TO CHOOSE ITS OWN NEXT ACTION.

WHAT THIS ANSWERS
-----------------
Ledger item AUT-PROP-036, grounded in `research/method-watch-autonomy-prior-art-2.md` §4.4
(PUBMED 10.1038/s41467-024-55655-3 Polybot, 10.1038/s41467-023-37139-y AlphaFlow): *a result must
pass an explicit validity predicate, written down IN ADVANCE, before it is allowed to steer the next
decision.* AlphaFlow enumerates the signature of a dead run before the campaign starts and terminates
in-line rather than letting a dead run's numbers reach the evidence base.

`scripts/emc_km_admissibility.py` already made that conversion for ONE domain — a computed quality
floor a digitized Kaplan-Meier curve must clear before AUT-034 admits it. This file makes it for a
SECOND: **the autonomy loop's own scoring evidence.**

THE EVIDENCE TYPE, NAMED NARROWLY ON PURPOSE
--------------------------------------------
A ledger row's `score_inputs` block, and the `score` that block is supposed to be the audit trail
for. `research-ledger.json` says of itself, in `_scores_are_not_evidence`:

    "A score orders work; it asserts nothing about the science. Every input is echoed in
     score_inputs so a reader can check the arithmetic against the graph."

⛔ **NOTHING CHECKED THAT ARITHMETIC.** The promise was prose, and prose in this repository is a
convention that decays (AUT-PD-013's fan-out key; AUT-PD-037's serialization). This module is the
check, and `ledger_io.write_ledger` runs it before any writer is allowed to change a row's score.

THE SIGNATURE OF AN INADMISSIBLE BLOCK, WRITTEN DOWN IN ADVANCE
---------------------------------------------------------------
Every rule below is evaluated from committed artifacts only — the row, `priority-weights.json`, and
the ledger as it stood before the write. None of them consults a session's memory.

  R1 `refused_unreadable`   the block is present but cannot be read as arithmetic: not a dict, or a
                            term whose type the sum cannot consume (a string where a number is
                            required, a cost_class the rank table does not name). ⛔ FAILS CLOSED —
                            an unreadable derivation is INADMISSIBLE, never "fine". CLAUDE.md §4: an
                            absent reading is not a reading of absence.
  R2 `refused_underivable`  the block carries every term the scorer writes, and the pinned weights
                            do not reproduce the row's `score`. The number was typed or inherited,
                            not derived — CLAUDE.md rule 1(1), *a total is DERIVED, never typed.*
  R3 `refused_accumulated`  the row's `score` moved between the ledger on disk and the ledger being
                            written, by an amount the change in its own echoed inputs cannot
                            explain. ⭐ THIS IS THE ONE THAT FIRED ON REAL DATA — see below.
  R4 `refused_stale_input`  the block echoes an `age_factor` that disagrees with `priority.age_factor`
                            recomputed from that row's own `last_evidence_utc`. The input on the
                            record is not the input in force, so the arithmetic beside it is
                            arithmetic nobody did.

And two gradings that are deliberately NOT `admitted`:

  `unaccounted`  a row carries a `score` with no derivation on the record at all (a hand-filed
                 proposal). ⛔ REPORTED AS UNMEASURED, NOT AS A PASS. CLAUDE.md §4: a populated
                 field is not a measured one. R3 still governs every subsequent change to it, which
                 is the whole reason the grade is separate from `admitted` rather than folded into
                 it.
  `unscored`     `score` is None. There is no number to adjudicate.

THE THRESHOLD, AND WHY IT IS NOT A PREFERENCE
----------------------------------------------
`TOLERANCE = 0.05`. The scorer emits scores through `round(x, 2)` in `build_entries` and
`apply_session_penalties` and through `round(x, 1)` in `apply_age_factor`, so **the coarsest quantum
the pipeline itself can emit is 0.1** and half of it is 0.05. The tolerance therefore absorbs
IEEE-754 summation error (~1e-13 here) and nothing else: a discrepancy of one full rounding quantum
is REFUSED. It is read off the `round()` calls in `priority.py`, not chosen.

⛔ **A WALL-CLOCK `N` MINUTES WAS THE OBVIOUS CANDIDATE AND IT IS THE WRONG INSTRUMENT HERE, MEASURED
RATHER THAN ASSUMED.** The proposal offers "an environment reading older than N minutes relative to
when it was filed". Tested against the committed ledger on 2026-08-28: the age term is a bounded
anti-starvation bonus that *rises with age on purpose* (`priority-weights.json:age_saturates_days`,
14 days), so `last_evidence_utc` being old is the thing the score is SUPPOSED to reward. Any N over
that field grades the calendar, not the evidence — at N = one cycle interval (4 h,
`autonomy-state.json`) it refuses 103 of 103 rows carrying an age term, and at N = 14 days it
refuses the rows the scorer most wants to promote. R4 replaces it with a CONTENT test that needs no
N: recompute the echoed input and compare. That is the form the workflow engines converged on
independently (`method-watch-autonomy-prior-art-2.md` §9: Nextflow's task hash covers code and
environment, not just data, and its resume check is two-part — the hash must match AND the output
must still be there).

WHAT IT REFUSED ON THE REAL CORPUS (2026-08-28, `origin/main` at e49c167)
-------------------------------------------------------------------------
⭐ R3 fired, and on a defect that was live and moving while it was measured. Traced through 25
commits of `research-ledger.json` with `git show`:

    AUT-PROP-036  158.0 → 158.9 → 159.8 → 160.7 → 161.6 → 162.5 → 163.4 → 164.3 → 165.2
                  +0.9 per re-score, EIGHT re-scores in 92 minutes, while its `score_inputs`
                  age_factor stayed pinned at 0.0714 and its `last_evidence_utc` stayed 2026-08-27.
    AUT-PROP-026  -1344.0 → -2506.8 over the same window, -90.0 (later -89.1) per re-score.
    AUT-049       105.0 → 117.0, then 117.0 at every subsequent re-score. Unmoved.

⛔ THE MECHANISM, WITH THE OBSERVATION THAT DISCRIMINATES IT. `apply_session_penalties` and
`apply_age_factor` were ADDITIVE mutations — `entry["score"] = entry["score"] + term` — and
`merge()` carries a hand-filed row's previous `score` forward untouched, by design, because the
graph cannot rebuild it. A DERIVED row's base is rebuilt from `systems/graph` every run, so the term
lands on a fresh base and the row is a fixed point of its own pipeline (AUT-049, unmoved across
eight runs). A HAND-FILED row's base is last run's output, so every term compounds. That is the
whole of the defect and AUT-049 sitting still is the observation that proves it is not the terms
being wrong but the base being reused.

⛔ AND IT HAD ALREADY CORRUPTED THE WORK QUEUE. On the corpus measured, the top 15 rows of
`priority.py`'s table were all hand-filed process/proposal rows at 195.5-199.0 — several of them
already marked "✅ DONE" — while the highest-scoring DERIVED route row, AUT-049, sat at 117.0. That
is CLAUDE.md §0's named failure ("do not default to documenting dead ones") arriving as arithmetic
rather than as a judgement call.

`priority.py`'s two terms are idempotent as of this commit, so the accumulation stops. ⚠ **THE
NUMBERS ALREADY ACCUMULATED ARE NOT REPAIRED HERE** — repairing them means editing
`research-ledger.json`, which is a separate owner's act; the residue is reported by `--report`
and filed as a ledger row rather than silently rewritten.

AND WHAT IT REFUSED IN `research/autonomy/receipts/` — NOTHING, WITH THE REASON
------------------------------------------------------------------------------
⛔ **NOT BECAUSE THE RECEIPTS ARE CLEAN. BECAUSE NONE OF THEM CARRIES A BLOCK THIS GATE CAN READ.**
Measured over all 52 committed receipts on 2026-08-28: **0 record a `score_inputs` block**, so the
predicate has nothing to adjudicate and refuses nothing. That is a coverage statement, and reporting
it as a pass would be the false-absence failure `receipt_schema.py` was itself filed against.
`--receipts` prints the number rather than a verdict.

⭐ 27 of the 52 quote a score in PROSE ("the queue's top-scored item (195.0)", "top of the re-scored
ledger at 195.5"), which is a real factual claim with a checkable referent, and extending the gate
to them was tried and REFUSED on measurement. A regex extractor over the corpus, checked against
`git show <receipt's commit>:research-ledger.json`, produced 29 (id, score) pairs of which 17 looked
like mismatches; inspecting all 17 by hand found **16 to be extractor artifacts** — it had matched
the digits of a NEIGHBOURING ledger id (`AUT-PD-020` read as the score "20", `AUT-PROP-029` followed
by `AUT-PD-030` read as "030") — and the seventeenth, CYC-0001 quoting AUT-049 at 195.0 against a
committed 105.0, is explained by that cycle's own `blocked_with_evidence` fix landing between
reading the queue and writing the receipt. **A false-positive rate that high makes a gate whose
first maintenance act is to loosen it** (`paper-hardening` §8b.1: a gate that reds on true input is
worse than one that greens on false input), so the prose route is recorded here as measured and not
taken. The machine-readable route is the one to open, and it costs a receipt writer one field.

WHAT THIS DOES NOT CATCH, STATED HERE RATHER THAN DISCOVERED LATER
-------------------------------------------------------------------
  * **The first score a hand-filed row is given.** It is typed by the filing cycle against a prose
    `_score_basis` and there is nothing to re-derive it from. It is graded `unaccounted`, and only
    its subsequent MOVEMENT is governed. A wrong number filed once stays wrong.
  * **Whether the graph the derived block was computed from was itself right.** R2 checks the
    arithmetic, not the reading. A wrong `patient_path` in `systems/graph` reproduces perfectly.
  * **A receipt's prose claims.** Receipts quote scores in free text ("the queue's top-scored item
    (195.0)"); this module reads JSON fields, not sentences. See `--receipts`, which reports that
    coverage gap as a number instead of leaving it implied.
  * ⚠ **SUPERSEDED 2026-08-28 (AUT-PD-041's re-score).** `apply_fruitless_attempts` was wired into
    `priority.py`'s pipeline, exactly as predicted above — and it went red on the very first
    non-derived row it moved (`refused_accumulated` on AUT-PD-041, -8.00 unexplained). Both
    `expected_score` (R2) and `_explained_delta` (R3) now carry the `fruitless_attempts` term,
    applied last, at 2 dp, matching `priority.py:apply_fruitless_attempts`'s own place at the end of
    `build_ledger`'s pipeline and its own rounding. This paragraph is kept as the record of the
    prediction that came true, not as current behaviour.
  * **A row deleted outright.** The delta rules see rows present in both states and rows added; a
    disappearance is `ids.py`/`merge()`'s territory.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
LEDGER = os.path.join(HERE, "research-ledger.json")
WEIGHTS = os.path.join(HERE, "priority-weights.json")
RECEIPT_DIR = os.path.join(HERE, "receipts")

#: ⛔ READ OFF `priority.py`'s OWN `round()` CALLS, NEVER CHOSEN. The pipeline emits through
#: `round(x, 2)` and `round(x, 1)`; the coarsest quantum it can emit is 0.1 and this is half of it.
#: Float summation error on these magnitudes is ~1e-13, so the band admits noise and nothing else.
TOLERANCE = 0.05

#: The terms `priority.build_entries` writes into `score_inputs` for a row it derives from
#: `systems/graph`. A block carrying all of them is one R2 can adjudicate exactly.
DERIVED_TERMS = (
    "live", "patient_path_scaled", "pursue_now", "tier_one", "endpoint_reachable",
    "blocker_leverage", "cost_class", "blocked_on_human",
)

#: States `priority.apply_age_factor` refuses to age. R4 is scoped to the same set, because a closed
#: row's echoed `age_factor` is frozen BY DESIGN and grading it stale would red a row on a rule that
#: no action can clear — the latching failure `receipt_schema.py` already paid for.
CLOSED_STATES = {"done", "abandoned", "superseded"}

#: ⛔ THE ONE DECLARED WAY A SCORE MAY MOVE WITHOUT ARITHMETIC BEHIND IT, AND IT IS NOT A BYPASS
#: FLAG. A writer correcting a score by hand must record WHY on the row, and the value must DIFFER
#: from the one already there — so the field cannot be left in place as a standing licence. It is
#: CLAUDE.md rule 1(2), corrections go on the record, expressed as a precondition of the write.
CORRECTION_KEY = "_score_correction"

ADMITTED = "admitted"
UNSCORED = "unscored"
UNACCOUNTED = "unaccounted"
REFUSED_UNREADABLE = "refused_unreadable"
REFUSED_UNDERIVABLE = "refused_underivable"
REFUSED_ACCUMULATED = "refused_accumulated"
REFUSED_STALE_INPUT = "refused_stale_input"
REFUSED_UNSCORED_NEW = "refused_unscored_new"

REFUSALS = (REFUSED_UNREADABLE, REFUSED_UNDERIVABLE, REFUSED_ACCUMULATED, REFUSED_STALE_INPUT,
            REFUSED_UNSCORED_NEW)


class InadmissibleWrite(Exception):
    """Raised at the write path when a ledger write would change a score nothing can account for."""


def _priority():
    """Imported lazily: `priority` imports `ledger_io`, and `ledger_io` calls into this module."""
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import priority  # noqa: PLC0415
    return priority


def load_weights(path: str = WEIGHTS) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------------------------
# The arithmetic, re-derived from the row's own echoed inputs.
# ---------------------------------------------------------------------------------------------

def _num(value):
    """A real number, or None. ⛔ `bool` is deliberately NOT a number here except where a term is
    declared boolean — a `True` silently worth 1.0 in a numeric slot is a populated field passing
    for a measured one."""
    if isinstance(value, bool):
        return None
    return float(value) if isinstance(value, (int, float)) else None


def derived_score(inputs: dict, weights: dict):
    """The base score `priority.build_entries` computes, re-derived from the echoed inputs.

    Returns `(value, None)` or `(None, why_unreadable)`. ⛔ Never raises and never guesses: a term
    it cannot read makes the whole block unreadable, which R1 refuses.
    """
    terms = weights["terms"]
    rank = weights["cost_class_rank"]
    total = 0.0
    for key, term in (("live", "live"), ("pursue_now", "pursue_now"), ("tier_one", "tier_one"),
                      ("endpoint_reachable", "endpoint_reachable"),
                      ("blocked_on_human", "blocked_on_human")):
        value = inputs.get(key)
        if not isinstance(value, bool):
            return None, f"`{key}` is {value!r}, not a boolean the scorer could have written"
        total += terms[term]["weight"] * value
    scaled = _num(inputs.get("patient_path_scaled"))
    if scaled is None:
        return None, f"`patient_path_scaled` is {inputs.get('patient_path_scaled')!r}, not a number"
    total += terms["patient_path"]["weight"] * scaled
    lever = _num(inputs.get("blocker_leverage"))
    if lever is None:
        return None, f"`blocker_leverage` is {inputs.get('blocker_leverage')!r}, not a number"
    total += terms["blocker_leverage"]["weight"] * lever
    cost_class = inputs.get("cost_class")
    if cost_class not in rank:
        return None, (f"`cost_class` is {cost_class!r}, which `priority-weights.json"
                      f":cost_class_rank` does not name")
    total += terms["cost"]["weight"] * rank[cost_class]
    return round(total, 2), None


def expected_score(row: dict, weights: dict):
    """The full pipeline value for a row whose block carries every derived term.

    Mirrors `priority.py`'s order exactly — base, then the evidenced-block penalty at 2 dp, then the
    age term at 1 dp — because that order is what produces the committed numbers.
    """
    inputs = row.get("score_inputs") or {}
    base, why = derived_score(inputs, weights)
    if base is None:
        return None, why
    if inputs.get("blocked_with_evidence"):
        base = round(base + weights["terms"]["blocked_with_evidence"]["weight"], 2)
    age = inputs.get("age_factor")
    if age:
        factor = _num(age)
        if factor is None:
            return None, f"`age_factor` is {age!r}, not a number"
        base = round(base + weights["terms"]["age"]["weight"] * factor, 1)
    # ⛔ ORDER IS THE CONTRACT, NOT A PREFERENCE. `priority.py` applies this immediately after the
    # age term and before the penalties; this function must mirror that sequence, because the
    # committed numbers are the product of the rounding at each step and a different order produces
    # a different last digit on rows nobody touched.
    recurring = inputs.get("recurring_cost_factor")
    if recurring:
        factor = _num(recurring)
        if factor is None:
            return None, f"`recurring_cost_factor` is {recurring!r}, not a number"
        base = round(base + weights["terms"]["recurring_cost"]["weight"] * factor, 1)
    fruitless = inputs.get("fruitless_attempts")
    if fruitless:
        n = _num(fruitless)
        if n is None:
            return None, f"`fruitless_attempts` is {fruitless!r}, not a number"
        base = round(base + weights["terms"]["fruitless_attempts"]["weight"] * n, 2)
    return base, None


def _has_full_block(inputs) -> bool:
    return isinstance(inputs, dict) and all(k in inputs for k in DERIVED_TERMS)


# ---------------------------------------------------------------------------------------------
# The static half: R1, R2, R4. Evaluated on one row against committed artifacts alone.
# ---------------------------------------------------------------------------------------------

def verdict(row: dict, weights: dict, today=None):
    """`(verdict, why)` for one ledger row. `why` is empty only for `admitted`/`unscored`."""
    inputs = row.get("score_inputs")
    if inputs is not None and not isinstance(inputs, dict):
        return REFUSED_UNREADABLE, (f"`score_inputs` is {type(inputs).__name__}, not an object — "
                                    "the derivation cannot be read, so it is not admitted")

    if isinstance(inputs, dict) and "age_factor" in inputs:
        stale = _stale_age(row, inputs, weights, today)
        if stale:
            return REFUSED_STALE_INPUT, stale

    if isinstance(inputs, dict) and "recurring_cost_factor" in inputs:
        stale = _stale_recurring_cost(row, inputs, weights, today)
        if stale:
            return REFUSED_STALE_INPUT, stale

    score = row.get("score")
    if score is None:
        return UNSCORED, ""
    if _num(score) is None:
        return REFUSED_UNREADABLE, f"`score` is {score!r}, not a number"

    if not _has_full_block(inputs):
        return UNACCOUNTED, (
            "carries a score with no derived `score_inputs` block behind it — a hand-filed number "
            "nothing can re-derive. Reported as UNMEASURED, not as a pass; every subsequent change "
            "to it is governed by the write-path delta rule.")

    want, why = expected_score(row, weights)
    if want is None:
        return REFUSED_UNREADABLE, why
    if abs(float(score) - want) > TOLERANCE:
        return REFUSED_UNDERIVABLE, (
            f"score {score} but its own `score_inputs` and `priority-weights.json` give {want} "
            f"(off by {float(score) - want:+.2f}, tolerance ±{TOLERANCE}) — the number was typed or "
            "inherited, not derived")
    return ADMITTED, ""


def _stale_age(row: dict, inputs: dict, weights: dict, today=None):
    """R4. Empty string when the echoed age term is the one in force."""
    if str(row.get("state") or "").strip() in CLOSED_STATES:
        return ""
    echoed = _num(inputs.get("age_factor"))
    if echoed is None:
        return f"`age_factor` is {inputs.get('age_factor')!r}, not a number"
    # ⭐⭐ RECOMPUTE AGAINST THE TERM'S OWN BASIS DATE WHEN IT HAS ONE (AUT-PD-198).
    # `priority.age_factor` is a function of the calendar day, so comparing an echoed value against
    # TODAY made every scored open row inadmissible at UTC midnight — a red trunk daily, by
    # construction, until some cycle happened to re-score. `priority.apply_age_factor` now stamps
    # `age_factor_as_of` beside the value, so the question becomes "is this the value its own basis
    # date produces?" instead of "is this the value today?".
    # ⛔ THIS DOES NOT WEAKEN R4, AND THE DISTINCTION IS THE WHOLE POINT. A hand-edited age term
    # still fails, because the number would not match the basis date stated next to it; only the
    # passage of time stops firing, and elapsed time was never evidence of a fabricated score. The
    # ageing itself is unaffected — `priority.py --write` is what advances a row's age term, and it
    # always was; R4 is a consistency check, not the clock.
    # ⚠ A ROW WITH NO BASIS DATE FALLS BACK TO TODAY, exactly as before, so nothing is grandfathered
    # into silence: rows written before this change keep failing until one `--write` stamps them,
    # which is one command and is the same command that fixed it by hand every previous morning.
    as_of = inputs.get("age_factor_as_of")
    basis = None
    if isinstance(as_of, str):
        try:
            basis = _dt.date.fromisoformat(as_of.strip())
        except ValueError:
            return (f"`score_inputs.age_factor_as_of` is {as_of!r}, which is not an ISO date — the "
                    "basis of the age term cannot be read, so the term beside it cannot be checked")
    live = round(_priority().age_factor(row, weights, today=basis or today), 4)
    if abs(echoed - live) > 1e-4:
        return (f"`score_inputs.age_factor` is {echoed}, but recomputing it from this row's own "
                f"`last_evidence_utc`={row.get('last_evidence_utc')!r} gives {live} — the input on "
                "the record is not the input in force")
    return ""


# ---------------------------------------------------------------------------------------------
# The delta half: R3. This is what the write path enforces.
# ---------------------------------------------------------------------------------------------

def _stale_recurring_cost(row: dict, inputs: dict, weights: dict, today=None):
    """R4, for the accrued-debt term. Empty string when the echoed value is the one in force.

    ⛔⛔ THIS IS THE ONLY THING STANDING BETWEEN THE TERM AND ITS OBVIOUS ABUSE. Every other input
    in a `score_inputs` block is a flag or a graph-derived value; `recurring_cost_factor` is worth
    up to 90 points and is computed from a magnitude a filer types. Without a recomputation, a row
    could carry a hand-written `recurring_cost_factor: 1.0` with no `recurring_cost` block at all
    and take the queue — the score-typing this whole module exists to refuse, at the largest weight
    in the file after `live`.
    ⭐ SO IT IS RECOMPUTED FROM THE ROW'S OWN BLOCK, against the basis date the row itself records
    (AUT-PD-198: a term that is a function of the calendar must be graded against its own stated
    basis, or the trunk goes red at UTC midnight by construction rather than by anybody's mistake).
    A row whose block is missing or unreadable recomputes to 0.0, so a non-zero echo over a missing
    block is exactly what this catches.
    ⚠ Scoped to open rows for `_stale_age`'s reason: a closed row's echo is frozen BY DESIGN and
    grading it stale would red a finished row on a rule about live ones.
    """
    if (row.get("state") or "queued") in CLOSED_STATES:
        return ""
    echoed = _num(inputs.get("recurring_cost_factor"))
    if echoed is None:
        return (f"`recurring_cost_factor` is {inputs.get('recurring_cost_factor')!r}, not a number")
    as_of = inputs.get("recurring_cost_as_of")
    basis = None
    if isinstance(as_of, str) and as_of.strip():
        try:
            basis = _dt.date.fromisoformat(as_of.strip()[:10])
        except ValueError:
            return (f"`score_inputs.recurring_cost_as_of` is {as_of!r}, which is not an ISO date — "
                    "the echoed debt has no basis to be checked against")
    else:
        return ("`score_inputs.recurring_cost_factor` is echoed with no `recurring_cost_as_of` "
                "beside it, so there is no date to recompute it against. A term worth up to 90 "
                "points may not be unfalsifiable.")
    live, _echo = _priority().recurring_cost_factor(row, weights, today=basis or today)
    if abs(live - echoed) > 1e-9:
        return (f"`score_inputs.recurring_cost_factor` is {echoed}, but recomputing it from this "
                f"row's own `recurring_cost` block against its stated basis {basis} gives {live}. "
                "Either the block was edited without re-scoring, or the factor was typed.")
    return ""


def _explained_delta(before: dict, after: dict, weights: dict) -> float:
    """How much of a score move the row's own echoed terms account for."""
    terms = weights["terms"]
    b = before.get("score_inputs") or {}
    a = after.get("score_inputs") or {}
    delta = 0.0
    delta += terms["age"]["weight"] * ((_num(a.get("age_factor")) or 0.0)
                                       - (_num(b.get("age_factor")) or 0.0))
    delta += terms["blocked_with_evidence"]["weight"] * (bool(a.get("blocked_with_evidence"))
                                                         - bool(b.get("blocked_with_evidence")))
    delta += terms["fruitless_attempts"]["weight"] * ((_num(a.get("fruitless_attempts")) or 0.0)
                                                       - (_num(b.get("fruitless_attempts")) or 0.0))
    # ⚠ AUT-PD-127, AND IT IS THE SAME EVENT THIS MODULE'S DOCSTRING ALREADY RECORDS ONE TERM EARLIER.
    # `apply_requires_trimcrae` was wired into `priority.py`'s pipeline and went red on the first
    # non-derived row it moved (`refused_accumulated` on AUT-PROP-041, -25.00 unexplained), exactly as
    # `apply_fruitless_attempts` did on AUT-PD-041. `derived_score` has always carried
    # `blocked_on_human`; only this delta half had never seen it move, because until now nothing moved
    # it after merge. ⛔ THIS DOES NOT LOOSEN R3: a score that moves with NO matching input change is
    # refused exactly as before, and a `blocked_on_human` flip with no matching score move is now
    # caught where previously it was invisible. The boolean shape mirrors `blocked_with_evidence`
    # immediately above, which is the same kind of term.
    delta += terms["blocked_on_human"]["weight"] * (bool(a.get("blocked_on_human"))
                                                     - bool(b.get("blocked_on_human")))
    # ⛔⛔ THE SAME EVENT, A THIRD TIME, AND THIS LINE IS WHY IT DID NOT HAPPEN AGAIN. Wiring a term
    # into `priority.py`'s pipeline without teaching THIS function about it makes the first row it
    # moves `refused_accumulated` — measured for `apply_fruitless_attempts` (AUT-PD-041) and again
    # for `apply_requires_trimcrae` (AUT-PD-127). `apply_recurring_cost` moves hand-filed rows by up
    # to 90 points, so it would have refused every ledger write the moment one row accrued a debt,
    # deadlocking the loop exactly as AUT-PD-152 did.
    # ⛔ AND THE TERM IS DEFAULTED PER-ROW, NOT PER-LEDGER: a row with no `recurring_cost` block
    # reads 0.0 on both sides and contributes nothing, so this is invisible to every row that does
    # not use it.
    delta += terms["recurring_cost"]["weight"] * ((_num(a.get("recurring_cost_factor")) or 0.0)
                                                  - (_num(b.get("recurring_cost_factor")) or 0.0))
    return delta


def write_verdict(before: dict, after: dict, weights: dict):
    """`(verdict, why)` for one row's CHANGE. `before` is the row as committed, `after` as written.

    ⛔ Scoped to rows R2 cannot adjudicate. A derived row's base is rebuilt from `systems/graph`
    every run, so a graph edit legitimately moves it — and R2 already checks that row against its
    own inputs exactly, which is strictly stronger than any delta rule could be. Every row is
    adjudicated by exactly one rule, chosen by whether its recorded inputs suffice to reproduce it.
    """
    if _has_full_block(after.get("score_inputs")):
        return ADMITTED, ""
    old, new = _num(before.get("score")), _num(after.get("score"))
    if old is None or new is None:
        return ADMITTED, ""
    moved = new - old
    if abs(moved) <= TOLERANCE:
        return ADMITTED, ""

    note = after.get(CORRECTION_KEY)
    if isinstance(note, str) and note.strip() and note != before.get(CORRECTION_KEY):
        return ADMITTED, ""

    if after.get("prerequisite_of"):
        # A prerequisite's score is recomputed from its parent every run
        # (`priority.apply_session_penalties`), so its own inputs never account for the move. The
        # parent is the derivation; the delta rule has nothing to say and says so.
        return ADMITTED, ""

    explained = _explained_delta(before, after, weights)
    residual = moved - explained
    if abs(residual) <= TOLERANCE:
        return ADMITTED, ""
    return REFUSED_ACCUMULATED, (
        f"score moved {old} → {new} ({moved:+.2f}) but its echoed inputs account for only "
        f"{explained:+.2f}, leaving {residual:+.2f} unexplained (tolerance ±{TOLERANCE}). A score "
        f"that moves for a reason nobody can check is an accumulation, not a derivation. Either "
        f"re-derive it, or record why on the row as `{CORRECTION_KEY}`.")


# ---------------------------------------------------------------------------------------------
# R5. The ratchet: the open-unscored population may only SHRINK.
# ---------------------------------------------------------------------------------------------

def is_unscored_open(row: dict) -> bool:
    """Is this row a member of the population `priority.py` publishes as `n_unscored_open`?

    ⛔ AN UNSCORED ROW IS ORDERED BY NOTHING (AUT-PD-050). `priority.score_rank` pins a missing
    score below every scored row, so no ranking term can reach it — the anti-starvation age factor
    included, which is the one term meant to rescue exactly these rows. A row filed without a
    number is therefore not "ranked low"; it is outside the ranking, and it stays there.

    ⚠ THE THREE EXEMPTIONS ARE THE FILING CONTRACT ALREADY WRITTEN IN `research-ledger.json`'s
    `_role`, not new policy: a row carries a `score` (with a `_score_basis`), or a
    `prerequisite_of` naming the row it unblocks — which derives one from that parent every run —
    or it is CLOSED, and a closed row is never offered to a session and never ranked.

    ⚠ THIS PREDICATE AND `priority.py`'s COUNTER MUST AGREE, AND ONE TEST HOLDS THEM TOGETHER.
    The counter does not test `prerequisite_of`, because no unscored row has ever carried one — a
    prerequisite is scored from its parent. `test_the_unscored_population_can_only_shrink.py`
    asserts the two agree on the committed ledger, so the day that stops being true it is a red
    build rather than a silent divergence between the gate and the number it is pinned to.
    """
    if not isinstance(row, dict):
        return False
    if _num(row.get("score")) is not None:
        return False
    if row.get("prerequisite_of"):
        return False
    return str(row.get("state") or "queued").strip() not in CLOSED_STATES


def refuse_population_growth(old: "dict | None", new: dict) -> str:
    """R5. Empty string unless this write puts a row INTO the open-unscored population.

    ⭐⭐ A RATCHET, NOT A CEILING, AND THAT IS THE WHOLE DESIGN. Refusing every unscored row would
    red the trunk on its first use: 85 open rows carry no score today, and a gate that cannot be
    satisfied by the tree it guards is an outage. So membership is GRANDFATHERED and only ENTRY is
    refused — the set can shrink freely and can never grow, which is what makes a pinned ceiling
    reachable instead of merely enforced (AUT-PD-145's entry condition 1).

    ⛔ ENTRY HAS THREE DOORS AND THIS CLOSES ALL THREE, because closing one is the one-of-a-pair
    defect class `paper-hardening` names. A row can be APPENDED unscored; a committed row's
    `score` can be REMOVED; and a committed unscored row that was CLOSED — and so exempt — can be
    REOPENED. All three end with one more row nothing can rank, so all three are the same finding
    and none of them is a special case of the others.
    """
    if not is_unscored_open(new):
        return ""
    if old is None:
        return ("appended with no `score` and no `prerequisite_of`. An unscored row is pinned below "
                "every scored row by `priority.score_rank` and no ranking term can reach it, the "
                "anti-starvation age factor included — so this row would be filed already starving. "
                "File it with a `score` and a `_score_basis`, or with a `prerequisite_of` naming "
                "the row it unblocks. See research-ledger.json `_role`.")
    if not is_unscored_open(old):
        if _num(old.get("score")) is not None:
            return (f"its committed `score` ({old.get('score')!r}) is removed by this write, which "
                    "moves the row out of the ranking entirely. A score that is wrong is "
                    "re-derived, never deleted.")
        return ("it was exempt on the trunk and this write ends that exemption while the row still "
                "carries no `score` — reopening a closed row, or clearing its `prerequisite_of`, "
                "puts it into the population nothing can rank. Give it a score in the same write.")
    return ""


# ---------------------------------------------------------------------------------------------
# The gate itself.
# ---------------------------------------------------------------------------------------------

def refuse_inadmissible_write(before: dict | None, after: dict, weights: dict, today=None):
    """Findings that must block the write. Empty list == admit.

    ⛔ FAILS CLOSED IN BOTH DIRECTIONS THAT MATTER. `before=None` means there is genuinely no
    committed ledger yet (a first write), and only the static rules apply; a committed ledger that
    exists and cannot be PARSED is a different thing entirely and the caller refuses it there,
    because a baseline we cannot read is not a baseline of nothing.
    """
    findings = []
    rows = after.get("entries")
    if not isinstance(rows, list):
        return [("REFUSED", "<ledger>", "`entries` is not a list — nothing here can be adjudicated")]

    prior = {}
    if before is not None:
        for row in before.get("entries") or []:
            if isinstance(row, dict) and row.get("id"):
                prior[row["id"]] = row

    for row in rows:
        if not isinstance(row, dict):
            findings.append(("REFUSED", "<row>", f"a row is {type(row).__name__}, not an object"))
            continue
        rid = row.get("id") or "<unnamed>"
        kind, why = verdict(row, weights, today=today)
        if kind in REFUSALS:
            findings.append((kind, rid, why))
            continue
        old = prior.get(rid)
        # R5 runs only with a real baseline. `before is None` means there is no committed ledger to
        # compare against, so EVERY row reads as newly appended and the rule would refuse the whole
        # file — the one case where it must stay silent rather than fail closed, because it cannot
        # tell growth from the population it is meant to grandfather.
        if before is not None:
            why = refuse_population_growth(old, row)
            if why:
                findings.append((REFUSED_UNSCORED_NEW, rid, why))
                continue
        if old is None:
            continue
        kind, why = write_verdict(old, row, weights)
        if kind in REFUSALS:
            findings.append((kind, rid, why))
    return findings


def check_write(path: str, data: dict, weights: dict | None = None, today=None) -> None:
    """The write-path gate. Raises `InadmissibleWrite` rather than letting the write land."""
    weights = weights or load_weights()
    before = None
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                before = json.load(fh)
        except Exception as exc:  # noqa: BLE001
            raise InadmissibleWrite(
                f"the ledger already at {path} cannot be parsed ({exc}), so no score change in this "
                "write can be checked against it. An unreadable baseline is not a baseline of "
                "nothing — fix or restore the file before writing over it.") from exc
    findings = refuse_inadmissible_write(before, data, weights, today=today)
    if findings:
        lines = "\n".join(f"  {kind}  {rid}\n      {why}" for kind, rid, why in findings)
        raise InadmissibleWrite(
            f"{len(findings)} inadmissible score change(s) in this ledger write:\n{lines}\n"
            "research/autonomy/admissibility.py names the signature each one tripped.")


# ---------------------------------------------------------------------------------------------
# Reporting.
# ---------------------------------------------------------------------------------------------

def audit(ledger: dict, weights: dict, today=None):
    out = []
    for row in ledger.get("entries") or []:
        if not isinstance(row, dict):
            continue
        kind, why = verdict(row, weights, today=today)
        out.append((row.get("id") or "<unnamed>", kind, why))
    return out


def receipt_coverage(receipt_dir: str = RECEIPT_DIR):
    """What this gate can and cannot say about the committed cycle receipts.

    ⛔ REPORTS THE COVERAGE GAP AS A NUMBER RATHER THAN LEAVING IT IMPLIED. This gate reads a JSON
    `score_inputs` block; a receipt records its claims as free prose, and the scores it quotes sit
    inside sentences. Saying "the receipts are clean" would be reading absence as evidence.
    """
    total = adjudicable = quoting = 0
    quoting_ids = []
    for path in sorted(glob.glob(os.path.join(receipt_dir, "*.json"))):
        total += 1
        raw = open(path, encoding="utf-8").read()
        try:
            data = json.loads(raw)
        except Exception:  # noqa: BLE001
            continue
        if "score_inputs" in raw:
            adjudicable += 1
        if "score" in raw.lower():
            quoting += 1
            quoting_ids.append(data.get("cycle_id") or os.path.basename(path))
    return {"receipts": total, "carrying_a_score_inputs_block": adjudicable,
            "mentioning_a_score_in_prose": quoting, "prose_mentions": quoting_ids}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", action="store_true",
                    help="grade every row of the committed ledger and print the counts")
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if any committed row trips a refusal signature")
    ap.add_argument("--receipts", action="store_true",
                    help="what this gate can and cannot adjudicate in research/autonomy/receipts/")
    ap.add_argument("--ledger", default=LEDGER)
    args = ap.parse_args(argv)

    if args.receipts:
        print(json.dumps(receipt_coverage(), indent=2))
        return 0

    weights = load_weights()
    with open(args.ledger, encoding="utf-8") as fh:
        ledger = json.load(fh)
    rows = audit(ledger, weights)

    counts: dict[str, int] = {}
    for _, kind, _why in rows:
        counts[kind] = counts.get(kind, 0) + 1

    if args.report or args.check:
        for rid, kind, why in rows:
            if kind in REFUSALS:
                print(f"{kind}  {rid}\n    {why}")
    print(json.dumps(counts, indent=2, sort_keys=True))
    # ⛔⛔ THE CLOSING SENTENCE EXPLAINED TWO GRADES AND OMITTED THE LARGEST ONE (AUT-PD-050). On
    # 2026-08-28 this report printed `{"admitted": 77, "unaccounted": 86, "unscored": 97}` and then
    # a sentence that named `admitted` and `unaccounted` only — so the biggest bucket in the loop's
    # own scoring audit was a number with no reading attached, and the reading it needed is that an
    # unscored row cannot be RANKED at all. Every grade this reporter can emit is now explained.
    # ⚠ THE REMEDY IS UNCONDITIONAL AND THE COUNT IS NOT (seat s6). Written first with both halves
    # behind `if counts.get(UNSCORED)`, this told a reader how to clear the population only while
    # the population existed — so the guard asserting the reader is told would have gone RED on the
    # day the defect was finally cleared, which is a test that punishes its own success.
    print(f"{len(rows)} rows graded. `admitted` means the arithmetic checks out; `unaccounted` "
          "means there is no arithmetic to check and is NOT a pass; `unscored` means there is no "
          "NUMBER — the row is pinned below every scored row by `priority.build_ledger`'s sort and "
          "no ranking term can reach it, the anti-starvation age factor included. A hand-filed "
          "entry is HAND-SCORED, not unscorable: file it with a `score` and a `_score_basis`, or "
          "with a `prerequisite_of` naming the row it unblocks. See research-ledger.json `_role`.")
    if counts.get(UNSCORED):
        print(f"⛔ {counts[UNSCORED]} row(s) are UNSCORED and no ranking term can order them.")
    if args.check:
        return 1 if any(k in REFUSALS for _, k, _w in rows) else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
