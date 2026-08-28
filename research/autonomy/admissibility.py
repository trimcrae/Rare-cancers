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

REFUSALS = (REFUSED_UNREADABLE, REFUSED_UNDERIVABLE, REFUSED_ACCUMULATED, REFUSED_STALE_INPUT)


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
    live = round(_priority().age_factor(row, weights, today=today), 4)
    if abs(echoed - live) > 1e-4:
        return (f"`score_inputs.age_factor` is {echoed}, but recomputing it from this row's own "
                f"`last_evidence_utc`={row.get('last_evidence_utc')!r} gives {live} — the input on "
                "the record is not the input in force")
    return ""


# ---------------------------------------------------------------------------------------------
# The delta half: R3. This is what the write path enforces.
# ---------------------------------------------------------------------------------------------

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
    print(f"{len(rows)} rows graded. `admitted` means the arithmetic checks out; `unaccounted` "
          "means there is no arithmetic to check and is NOT a pass.")
    if args.check:
        return 1 if any(k in REFUSALS for _, k, _w in rows) else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
