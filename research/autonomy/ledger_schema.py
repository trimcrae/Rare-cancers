#!/usr/bin/env python3
"""THE ONE PLACE THAT NAMES WHAT A LEDGER ENTRY MAY CALL ITS FIELDS (AUT-PD-030).

⛔⛔ WHY THIS FILE EXISTS. Every row in `research-ledger.json` is hand-authored JSON, and several
readers key off exact field names -- `continuity.py`, `priority.py`, `health.py`, `claim.py`,
`stuck_clock.py`, `handoff.py`, `out_of_ideas.py` and `.claude/hooks/escalation-debt-at-turn-end.sh`
among them. Nothing anywhere held a whitelist, so a one-edit misspelling was indistinguishable from a
new field. AUT-PD-017's sweep found this and left it open; AUT-PD-030 is the residual.

⭐ REPRODUCED BEFORE IT WAS FIXED, ON A SCRATCH COPY OF THE LEDGER (2026-09-01, seat S10-SCHEMA).
A row whose `what` names no outward verb, carrying `require_trimcrae: true` -- ONE deletion away from
`requires_trimcrae` -- was appended to a copy of the committed ledger. Against that copy:

    continuity.ready()                  -> the row is OFFERED AS READY TO RUN         (True)
    continuity.unclassified_outward()   -> the row is NOT FLAGGED                     (False)
    prepush_ledger_guard.py             -> exit 0, no output          (it checks duplicate ids only)
    admissibility.py / health.py        -> not one line naming the row or the key

That is category (c) of AUT-PD-017's own taxonomy -- the failure that reads as GREEN -- on the single
field CLAUDE.md §3 exists to protect. `continuity._why_not_ready()` treats an ABSENT
`requires_trimcrae` as "not his act", and `unclassified_outward()` only rescues the row if its `what`
ALSO matches a regex over publish/submit/deposit/outreach verbs. A misspelling on prose the regex
does not match is silent in both instruments at once.

⛔ AND THE NEAR-MISS CLASS IS NOT HYPOTHETICAL IN THIS FILE. Measured over the 344 committed rows:
`requires_trimcrae_why` (79 rows) and `_requires_trimcrae_why` (87 rows) are the same field under two
spellings, and BOTH `stuck_clock.py` and `out_of_ideas.py` had to hand-code both -- a reader patched
around the drift rather than the drift being fixed. `lease_released`/`_lease_released` are likewise
both live, and AUT-PROP-012 carries BOTH AT ONCE with different text in each. So the vocabulary has
already forked five times; what has not happened yet is a fork onto a name no reader knows.

★★ THE DESIGN QUESTION, ANSWERED RATHER THAN DODGED. A schema that rejects every unknown field breaks
the next legitimate field and gets switched off; a schema that accepts every unknown field catches
nothing. Neither is what the defect is. The defect is a name that LOOKS LIKE a name a reader uses, so
that is what this module measures:

    a key in the vocabulary                                   -> fine
    a key not in the vocabulary, FAR from every governed name -> fine, no registration needed
    a key not in the vocabulary, NEAR a governed name         -> REFUSED, naming the reader it fools

"Near" is four detectors (`near_misses`), all cheap and all stdlib: normalised equality, whole-name
edit distance, leading-token edit distance, and token reordering. The last two exist because pure
edit distance does not reach the ledger row's own worked example -- `owned_by` is FOUR edits from
`owner` and would have sailed through a distance-2 rule; its leading token is one edit away.

⛔ WHAT THIS CANNOT CATCH, STATED SO NOBODY READS THE GATE FOR MORE THAN IT MEASURES.
  1. AN ABSENT FIELD. A row that simply omits `requires_trimcrae` is the DEFAULT (163 of 344 rows)
     and is indistinguishable from a row whose author forgot. That question belongs to
     `continuity.unclassified_outward()`, which answers it with a regex over the row's own prose and
     therefore only partially. A field-name schema cannot help with a name that was never typed.
  2. A TYPO THAT IS ITSELF A REAL FIELD -- writing `evidence` when you meant `blocked_evidence`.
     Both are in the vocabulary; no detector can see the intent.
  3. A TYPO OF A DESCRIPTIVE (unread) FIELD. Deliberate: the detectors fire against GOVERNED names
     only, because a misspelt annotation costs nothing and adding it to the target set would make
     every dated one-off note (`_CORRECTION_2026_09_01`, `_PARKED_2026_09_01`) a maintenance tax on
     the gate for no protection at all.
  4. A WRONG VALUE UNDER A RIGHT NAME, in general. `value_problems()` covers the two fields where a
     wrong value reads as green (`requires_trimcrae`, `state`) and `id_problems()` covers the id
     SHAPE; nothing else is value-checked.

⭐ AND THE SAME DEFECT HAS A VALUE-SHAPED HALF, ADDED THE DAY THE ID FORMAT MOVED (2026-09-01).
`ids.next_entry_id` now mints `AUT-PD-204-6b009680`, a session discriminator appended because two
concurrent sessions provably minted `AUT-PD-204` from one committed ledger. BOTH SHAPES ARE LEGAL and
`id_problems()` accepts both -- by calling `ids.parse_entry_id`, never by writing a second regex,
because a module about one fact having one home may not open a second home for the id format on its
way to saying so. The failure that change exposed is the shape this schema is built to notice: not a
misspelled field name but a VALUE that no longer matches a format something downstream assumes.
`priority.merge()` derived ordinals from `int(id.rsplit("-", 1)[-1])` inside a bare
`except ValueError: pass`, so a discriminated row read its discriminator as its ordinal, threw, was
swallowed, and stopped contributing to the used-ordinal set with nothing printed anywhere.

⚠ THE VOCABULARY IS A REVIEWED SNAPSHOT OF THE COMMITTED LEDGER, NOT A DERIVED SET, and it is
therefore trivially true that the file passes today. The gate is PROSPECTIVE: it is the next typo it
is for. Every one of the 89 committed names was run back through the detectors as if it were unknown
(`tests/test_a_near_miss_field_name_cannot_enter_the_ledger.py::test_no_committed_field_name_is_a_near_miss_of_a_governed_one`)
and none is within reach of a governed name, which is why no hand fix of the ledger was needed first.

★ ADDING A FIELD IS ONE LINE. A new name far from everything needs nothing. A new name that really
does sit beside a governed one -- say a future `blocked_since` -- is added to `DESCRIPTIVE_FIELDS`
(or `GOVERNED_FIELDS`, if code reads it) and the refusal stops. That one line is the point: it makes
adopting a near-name a DELIBERATE act instead of an accident.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "research-ledger.json")

#: ⛔ FIELDS SOME READER KEYS OFF. A near-miss of one of these is what this module refuses; the
#: parenthetical names the reader that a misspelling would fool, so a failure message can say what
#: actually breaks rather than "unknown field".
GOVERNED_FIELDS: dict[str, str] = {
    "id": "every reader; `ids.duplicate_ids` and `prepush_ledger_guard.py`",
    "kind": "priority.py ranking, health.py's kind census",
    "state": "continuity._why_not_ready, priority.py, claim.py, handoff.py, health.py",
    "what": "continuity.unclassified_outward's regex, priority.py, proposal_dedup.py",
    "owner": "claim.py's lease, continuity.py, holder_liveness.py, queue_view.py",
    "claimed_utc": "claim.py's lease clock, stuck_clock.py",
    "serves": "priority.py's route join, health.py, systems_check.py",
    "cost_class": "continuity._why_not_ready, priority.py, admissibility.py",
    "cost_points_at": "priority.py",
    "blocked_by": "continuity._why_not_ready, priority.py, amendment_guard.py",
    "blocked_evidence": "continuity._why_not_ready, health.py, priority.py",
    "retry_budget": "priority.py, handoff.py, health.py",
    "attempts": "priority.py, stuck_clock.py, out_of_ideas.py",
    "last_evidence_utc": "admissibility.py, health.py, priority.py, queue_view.py",
    "filed_by": "stuck_clock.py",
    # ⛔ THE SHARPEST EDGE (AUT-PD-030's own words). continuity.py reads it; the Stop hook
    # `.claude/hooks/escalation-debt-at-turn-end.sh` reads it; a misspelling reads as GREEN in both.
    "requires_trimcrae": "continuity._why_not_ready, escalation-debt-at-turn-end.sh, handoff.py",
    "requires_trimcrae_why": "stuck_clock.PROGRESS_FIELDS, out_of_ideas.py",
    "_requires_trimcrae_why": "stuck_clock.PROGRESS_FIELDS, out_of_ideas.py (the `_` spelling; both "
                              "are live and both readers already carry both)",
    "notified_utc": ".claude/hooks/escalation-debt-at-turn-end.sh -- the falsifiable record that an "
                    "escalation was actually SENT",
    "closes_clause": "continuity.py, out_of_ideas.py, stuck_clock.py",
    "score": "priority.py, continuity.py, admissibility.py, the escalation hook's ranking",
    "score_inputs": "priority.py's derivation, admissibility.py",
    "_score_basis": "priority.py, stuck_clock.TOUCH_FIELDS",
    "_score_correction": "admissibility.py -- the one declared way past a refused score change",
    "_score_inherited_from_route": "priority.py",
    "_score_is_null_why": "out_of_ideas.py",
    "clamp": "priority.py, stuck_clock.TOUCH_FIELDS",
    "parked_on": "priority.py",
    "parked_by_graph_status": "priority.py",
    "prerequisite_of": "priority.py, admissibility.py, out_of_ideas.py",
    "dispatch_log": "claim.py, priority.py",
    "lease_released": "priority.py, queue_view.py, stuck_clock.py",
    # ⚠ A THIRD FORK, AND IT IS ONLY HALF-MITIGATED. `stuck_clock.py:184-185` carries BOTH
    # spellings, so progress is seen either way -- but `queue_view.DELIVERABLE_FIELDS` is
    # `("what", "lease_released")` and knows only the bare one, so a row that records its
    # deliverable here alone is invisible to `already_landed()`. Left in the governed set because it
    # IS read; the honest fix is to collapse the two spellings in the ledger, not to widen a
    # second reader.
    "_lease_released": "stuck_clock.py:185 only -- NOT queue_view.DELIVERABLE_FIELDS. "
                       "AUT-PROP-012 carries BOTH spellings at once, with different text in each",
    "claim_workers": "continuity.py, queue_view.py, out_of_ideas.py",
    "process_defect": "out_of_ideas.py",
    "depends_on_evidence": "stuck_clock.PROGRESS_FIELDS, out_of_ideas.py",
    "outcome": "stuck_clock.PROGRESS_FIELDS, out_of_ideas.py",
    "observed": "stuck_clock.PROGRESS_FIELDS, out_of_ideas.py",
    "superseded_note": "stuck_clock.PROGRESS_FIELDS, out_of_ideas.py",
    "_block_cleared": "stuck_clock.PROGRESS_FIELDS, out_of_ideas.py",
    "_derived": "priority.py, stuck_clock.TOUCH_FIELDS",
    "_renamed_from": "out_of_ideas.py",
    "closed_by": "claim.py, systems_check.py",
    "handoff": "handoff.py, health.py",
}

#: Fields that appear in the committed ledger and that no loop reader keys off: commentary, dated
#: one-offs, and per-row explanation. They are enumerated ONLY so the detectors have the full
#: vocabulary and do not fire on a name that is already in use. Adding one is a one-line, no-argument
#: edit; a misspelling among these costs nothing, which is why they are not detector targets.
DESCRIPTIVE_FIELDS: frozenset[str] = frozenset({
    "CORRECTION", "_CLOSED_2026_09_01", "_CORRECTION_2026_08_31", "_CORRECTION_2026_09_01",
    "_CORRECTION_2026_09_01_live_run", "_CORRECTION_2_2026_09_01", "_NOTIFIED_AND_ANSWERED_2026_09_01",
    "_NOTIFIED_AS_A_GROUP_2026_09_01", "_PARKED_2026_09_01", "_claim_workers_why", "_closed_by",
    "_commit_pointer_correction", "_concurrent_fix_note", "_contested", "_correction",
    "_cycle_row_key", "_id_collision", "_id_note", "_language_discipline",
    "_lease_released_2026_08_31", "_lease_released_by", "_observations", "_refiled_note",
    "_renamed_why", "_resolution", "_route_note", "_stranded_work", "_the_choice_made",
    "_the_id_this_row_does_not_carry", "_what_is_left", "also_worth_fixing", "evidence",
    "evidence_paths", "lesson", "next_action", "open_question_for_trimcrae",
    "why", "why_not_fixed_here", "why_the_restore_is_still_right", "resolution", "result",
    "route", "what_is_actually_lost", "what_was_observed",
})

#: ⛔⛔ NEAR-MISSES THAT ARE ALREADY IN THE COMMITTED LEDGER. Found by running every committed field
#: name back through the detectors as if it were unknown -- which is how a schema built from a
#: snapshot avoids the circularity of blessing whatever it happens to find. These two are REPORTED
#: and do not fail the gate, on `receipt_schema.py`'s precedent: the ledger item that commissioned
#: this module was filed against a checker that HID what it could not read, so burying them in
#: `DESCRIPTIVE_FIELDS` would rebuild that defect one file over.
#:
#: ⚠ THEY ARE NOT COSMETIC. Both are the same fact under two names, with a reader that sees one:
#:   `_closed_by`  3 rows (AUT-068, AUT-PD-129, AUT-PD-146) carry a cycle id here; `claim.py:429`
#:                 reads `closed_by` and nothing else, so those three rows report NO CLOSER while
#:                 the id sits in the row.
#:   `_outcome`    5 rows (AUT-PD-099, AUT-PD-166, AUT-PROP-051/053/054) record the result here;
#:                 `stuck_clock.PROGRESS_FIELDS` and `out_of_ideas.py` both list `outcome` only, so
#:                 an edit to `_outcome` is not progress in the instrument that measures progress.
#: ★ THE FIX IS A LEDGER EDIT (rename the eight rows onto the governed spelling), then deleting this
#: block -- at which point the detectors refuse the drifted spelling for good. It was not made in the
#: same change because `research-ledger.json`'s id allocator collides across concurrent writers
#: (AUT-PD-171) and this module was written during a twelve-seat sprint that forbids touching it.
LIVE_ALIASES: dict[str, str] = {
    "_closed_by": "closed_by",
    "_outcome": "outcome",
}

#: Sub-keys of the two nested blocks a reader descends into. Same rules, same reason: a misspelt
#: `serves.route` unlinks a row from the architecture graph, and a misspelt `score_inputs.age_factor`
#: silently drops a ranking term -- both read as green.
GOVERNED_SUBFIELDS: dict[str, dict[str, str]] = {
    "serves": {
        "route": "priority.py's join to systems/graph/routes.json",
        "publication": "priority.py, systems_check.py",
        "strategy": "priority.py",
    },
    "score_inputs": {
        "age_factor": "priority.py", "age_factor_as_of": "priority.py",
        "fruitless_attempts": "priority.py", "blocked_on_human": "priority.py",
        "live": "priority.py", "cost_class": "priority.py", "patient_path": "priority.py",
        "patient_path_scaled": "priority.py", "pursue_now": "priority.py",
        "tier_one": "priority.py", "endpoint_reachable": "priority.py",
        "blocker_leverage": "priority.py", "blocked_with_evidence": "priority.py",
    },
}

#: Descriptive sub-keys, exactly as `DESCRIPTIVE_FIELDS` above and for the same reason.
DESCRIPTIVE_SUBFIELDS: dict[str, frozenset[str]] = {
    "serves": frozenset({"_route_was", "_route_remap_note"}),
    "score_inputs": frozenset(),
}

#: The `state` vocabulary, measured over the committed ledger. A `state` nothing recognises is not a
#: new state -- it is a row no reader will ever offer, park or close.
STATES: frozenset[str] = frozenset({"queued", "in_progress", "blocked", "parked", "done",
                                    "superseded"})

#: ⭐ THE ID PREFIXES IN USE, measured over the committed ledger on 2026-09-01, with their counts:
#: AUT-PD 199, AUT 81, AUT-PROP 56, AUT-BIX 3, AUT-RT 2, AUT-COV 2, AUT-INC 1. A prefix is a
#: NAMESPACE -- `ids.next_entry_id` counts ordinals within one -- so a misspelt prefix silently opens
#: a private namespace whose ordinals collide with nothing and are seen by nobody. The same
#: `near_misses` detectors are pointed at it, which is the point of having them as a function: the
#: defect this module is about is a name one edit from a name something reads, and a prefix is one.
ID_PREFIXES: dict[str, str] = {
    "AUT": "the original autonomy series",
    "AUT-PD": "process defects",
    "AUT-PROP": "proposals",
    "AUT-BIX": "the bioinformatics-exchange series",
    "AUT-RT": "route-scoped rows",
    "AUT-COV": "coverage rows",
    "AUT-INC": "incident rows",
}

#: ⛔ Edit distance is scaled by name length: one edit in a five-character name is a different word,
#: two edits in a twenty-character name is still a typo. Measured against the committed vocabulary
#: rather than picked -- at these thresholds none of the 89 committed names reaches a governed one.
_SHORT_NAME = 10
_MAX_EDITS_SHORT = 1
_MAX_EDITS_LONG = 2

#: Rule C compares leading tokens and would be noise on two- and three-letter stems.
_MIN_TOKEN_LEN = 4


def _levenshtein(a: str, b: str) -> int:
    """Plain DP edit distance. Stdlib only, and the names here are tens of characters."""
    if a == b:
        return 0
    if not a or not b:
        return len(a) or len(b)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _norm(name: str) -> str:
    """Case and underscores removed -- the form in which `_Requires_Trimcrae` and
    `requires__trimcrae` are visibly the same name as `requires_trimcrae`."""
    return name.replace("_", "").lower()


def _tokens(name: str) -> list[str]:
    return [t for t in name.lower().split("_") if t]


def near_misses(unknown: str, governed: dict[str, str]) -> list[tuple[str, str]]:
    """Every governed name `unknown` is plausibly a misspelling of, with the rule that caught it.

    Four detectors, in the order they were needed:

    A `alias`      normalised equality -- casing, an extra underscore, a leading underscore.
    B `edit`       whole-name edit distance within the length-scaled budget.
    C `stem`       leading tokens exactly one edit apart. ⛔ THIS IS THE ONE THE LEDGER ROW'S OWN
                   EXAMPLE NEEDS: `owned_by` is four edits from `owner` and reachable by no
                   sane distance rule, but `owned` is one edit from `owner`. Exactly one, never
                   zero -- `blocked_by` and `blocked_evidence` are both real and share a stem, so a
                   zero-distance stem rule would refuse every legitimate sibling field.
    D `reorder`    the same tokens in a different order (`trimcrae_requires`).
    """
    hits = []
    un, ut = _norm(unknown), _tokens(unknown)
    for known in governed:
        kn, kt = _norm(known), _tokens(known)
        if un == kn:
            hits.append((known, "alias"))
            continue
        budget = _MAX_EDITS_LONG if max(len(unknown), len(known)) >= _SHORT_NAME else _MAX_EDITS_SHORT
        if _levenshtein(unknown.lower(), known.lower()) <= budget:
            hits.append((known, "edit"))
            continue
        if (ut and kt and len(ut[0]) >= _MIN_TOKEN_LEN and len(kt[0]) >= _MIN_TOKEN_LEN
                and _levenshtein(ut[0], kt[0]) == 1):
            hits.append((known, "stem"))
            continue
        if len(ut) > 1 and sorted(ut) == sorted(kt):
            hits.append((known, "reorder"))
    return hits


def _refusal(row_id: str, where: str, unknown: str, hits: list[tuple[str, str]],
             governed: dict[str, str]) -> str:
    known, rule = hits[0]
    return (f"{row_id}: `{where}{unknown}` is not a known field and is a {rule}-near-miss of "
            f"`{where}{known}`, which is read by {governed[known]}. ⛔ If it is a typo, fix the "
            f"spelling. If it is genuinely a NEW field, register it in ledger_schema.py "
            f"({'GOVERNED_FIELDS' if where == '' else 'GOVERNED_SUBFIELDS'} if code reads it, "
            f"otherwise DESCRIPTIVE_FIELDS) -- one line, and the point of the line is that adopting "
            f"a name this close to a governed one is a decision rather than an accident.")


def field_problems(entry: dict, row_id: str | None = None) -> list[str]:
    """Every near-miss field name in one entry, as a sentence naming the exact edit. [] = clean."""
    rid = row_id or entry.get("id") or "(row with no id)"
    out = []
    for key in entry:
        if key in GOVERNED_FIELDS or key in DESCRIPTIVE_FIELDS or key in LIVE_ALIASES:
            continue
        hits = near_misses(key, GOVERNED_FIELDS)
        if hits:
            out.append(_refusal(rid, "", key, hits, GOVERNED_FIELDS))
    for block, governed in GOVERNED_SUBFIELDS.items():
        value = entry.get(block)
        if not isinstance(value, dict):
            continue
        descriptive = DESCRIPTIVE_SUBFIELDS.get(block, frozenset())
        for key in value:
            if key in governed or key in descriptive:
                continue
            hits = near_misses(key, governed)
            if hits:
                out.append(_refusal(rid, f"{block}.", key, hits, governed))
    return out


def id_problems(entry: dict, require_parseable: bool = True) -> list[str]:
    """The row's `id`, checked as a SHAPE rather than as a string (2026-09-01).

    ⚠ `require_parseable=False` IS FOR THE `write_ledger` PATH AND IS NOT A LOOSENING, measured
    rather than assumed: turning this check on refused seven existing tests at once, all of them
    laying down fixtures with ids like `AUT-X` and `AUT-TEST-APPEND` on a temp path. A fixture id is
    not a ledger id, and there is nothing to protect there -- a REAL writer takes its id from
    `ids.next_entry_id`, which mints a valid one by construction, so the only ids that can reach the
    committed file malformed are hand-authored, and those never pass through `write_ledger` at all.
    The whole-ledger gate (`problems`, run by the preflight-tier test over the committed file) keeps
    the shape check at full strength, which is where it can actually catch something. ⛔ THE PREFIX
    NEAR-MISS IS CHECKED ON BOTH PATHS: that one is the defect this module is about, and a fixture
    has no business inventing a namespace either.

    ⛔⛔ THE SHAPE CHANGED TONIGHT AND A READER THAT ASSUMED THE OLD ONE WAS ALREADY WRONG.
    `ids.next_entry_id` now mints `AUT-PD-204-6b009680` -- a session discriminator appended, because
    two concurrent sessions provably minted `AUT-PD-204` from the same committed ledger. Both shapes
    are legal and this function must accept both. The failure that shape change exposed is the one
    worth naming here: `priority.merge()` derived ordinals from `int(id.rsplit("-", 1)[-1])` inside a
    bare `except ValueError: pass`, so a discriminated row read its DISCRIMINATOR as its ordinal,
    threw, was swallowed, and stopped contributing to the used-ordinal set -- silently.

    ⭐ SO THIS CALLS `ids.parse_entry_id` AND DOES NOT WRITE A SECOND REGEX. A module about one fact
    having one home may not open a second home for the id format on its way to saying so; `ids.py`
    owns `ENTRY_ID`, and if this file carried its own copy the two would drift exactly the way the
    field names did.

    ⛔ AND AN UNIMPORTABLE `ids` FAILS CLOSED WITH THE CAUSE NAMED, never quietly passes: an absent
    reading is not a reading of absence (CLAUDE.md §4).
    """
    rid = entry.get("id")
    if not isinstance(rid, str) or not rid.strip():
        return [f"a row has no usable `id` ({rid!r}). Every reader keys off it and "
                "`ids.duplicate_ids` counts it."]
    try:
        import ids  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - only in a broken tree
        return [f"{rid}: cannot import `ids` to check the id shape ({exc}). Failing closed: this "
                "check reads the id format from its one home rather than re-deriving it."]
    parsed = ids.parse_entry_id(rid)
    if parsed is None:
        if not require_parseable:
            return []
        return [f"{rid}: does not match `ids.ENTRY_ID`. A ledger id is `PREFIX-ORDINAL` or "
                "`PREFIX-ORDINAL-DISCRIMINATOR` (`AUT-PD-030`, `AUT-PD-204-6b009680`) -- both are "
                "legal, and no reader may assume the id ends in its ordinal."]
    prefix, _ordinal, _disc = parsed
    if prefix in ID_PREFIXES:
        return []
    hits = near_misses(prefix, ID_PREFIXES)
    if not hits:
        return []
    known, rule = hits[0]
    return [f"{rid}: the id prefix `{prefix}` is unknown and is a {rule}-near-miss of `{known}` "
            f"({ID_PREFIXES[known]}). A prefix is a NAMESPACE -- `ids.next_entry_id` counts ordinals "
            "within one -- so a misspelt prefix opens a private namespace that collides with nothing "
            "and is read by nobody. If it is genuinely a new series, register it in "
            "`ledger_schema.ID_PREFIXES`."]


def value_problems(entry: dict, row_id: str | None = None) -> list[str]:
    """The two values whose wrong TYPE reads as green. Deliberately not a whole-value schema.

    ⛔ `requires_trimcrae` is checked for a real bool because `continuity._why_not_ready` tests it
    for truthiness: `null`, `0` and `""` all fall through to "ready" exactly as an absent key does,
    so a row that wrote `requires_trimcrae: null` meaning "undecided" is offered as work.
    ⚠ `"false"` is the harmless direction (a non-empty string is truthy, so the row is withheld) and
    is still refused, because a field whose meaning depends on which of two safe-looking spellings
    was typed is the same defect this module exists for.
    """
    rid = row_id or entry.get("id") or "(row with no id)"
    out = []
    if "requires_trimcrae" in entry and not isinstance(entry["requires_trimcrae"], bool):
        out.append(f"{rid}: `requires_trimcrae` = {entry['requires_trimcrae']!r} is not a bool. "
                   "continuity._why_not_ready tests it for TRUTHINESS, so null/0/\"\" read exactly "
                   "like an absent key and the row is offered as ready -- CLAUDE.md §3's protection "
                   "dropped with no warning printed anywhere.")
    state = entry.get("state")
    if state is not None and state not in STATES:
        out.append(f"{rid}: `state` = {state!r} is not one of {sorted(STATES)}. A state no reader "
                   "recognises is a row that can never be offered, parked or closed.")
    return out


def header_problems(ledger: dict) -> list[str]:
    """The ledger header's typed totals against the rows they count (CLAUDE.md §1: a total is
    DERIVED, never typed). `priority.py --write` derives all five; a hand-added row that skips that
    step leaves the file's own summary describing a ledger that no longer exists."""
    entries = ledger.get("entries") or []
    derived = {
        "n_by_kind": {},
        "n_by_state": {},
        "n_clamped": sum(1 for e in entries if e.get("clamp")),
        "n_unscored": sum(1 for e in entries if e.get("score") is None),
        "n_unscored_open": sum(1 for e in entries
                               if e.get("score") is None
                               and e.get("state") not in ("done", "superseded")),
    }
    for e in entries:
        for field, bucket in (("kind", "n_by_kind"), ("state", "n_by_state")):
            key = e.get(field)
            if key is not None:
                derived[bucket][key] = derived[bucket].get(key, 0) + 1
    out = []
    for name, value in derived.items():
        recorded = ledger.get(name)
        if recorded is None:
            continue
        if isinstance(value, dict):
            if dict(sorted((recorded or {}).items())) != dict(sorted(value.items())):
                out.append(f"header `{name}` = {recorded} but the rows count {value}. "
                           "Re-run `python3 research/autonomy/priority.py --write`.")
        elif recorded != value:
            out.append(f"header `{name}` = {recorded} but the rows count {value}. "
                       "Re-run `python3 research/autonomy/priority.py --write`.")
    return out


def problems(ledger: dict) -> list[str]:
    """Every schema failure in a whole ledger document. [] = clean."""
    out = []
    for entry in ledger.get("entries") or []:
        if not isinstance(entry, dict):
            out.append(f"an entry is a {type(entry).__name__}, not an object")
            continue
        out.extend(id_problems(entry))
        out.extend(field_problems(entry))
        out.extend(value_problems(entry))
    out.extend(header_problems(ledger))
    return out


def live_aliases_in(ledger: dict) -> dict[str, list[str]]:
    """Which rows use a `LIVE_ALIASES` spelling, keyed by the drifted name. Reported, never failed --
    and never silent, which is the whole difference from hiding them in `DESCRIPTIVE_FIELDS`."""
    found: dict[str, list[str]] = {}
    for entry in ledger.get("entries") or []:
        if not isinstance(entry, dict):
            continue
        for alias in LIVE_ALIASES:
            if alias in entry:
                found.setdefault(alias, []).append(entry.get("id") or "(row with no id)")
    return found


class SchemaViolation(ValueError):
    """Raised by `ledger_io.write_ledger` when a write would land a near-miss field name."""


def check_write(path: str, data: dict) -> None:
    """The `write_ledger` binding. Raises `SchemaViolation`; never writes anything.

    ⚠ FIELD AND VALUE PROBLEMS ONLY, NOT `header_problems`. A writer that is mid-way through adding
    rows has not re-derived the header yet and must not be refused for it -- `priority.py --write`
    is what fixes that, and it is itself a writer. The header check is the ledger-wide gate's, which
    runs on the committed file where the totals are supposed to be true.
    """
    found = []
    for entry in (data.get("entries") or []):
        if isinstance(entry, dict):
            found.extend(id_problems(entry, require_parseable=False))
            found.extend(field_problems(entry))
            found.extend(value_problems(entry))
    if found:
        raise SchemaViolation(
            f"refusing to write {os.path.basename(path)}: {len(found)} field-name/value problem(s)\n"
            + "\n".join(f"  - {line}" for line in found))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the ledger fails the schema")
    ap.add_argument("--ledger", default=LEDGER)
    args = ap.parse_args(argv)
    try:
        with open(args.ledger, encoding="utf-8") as fh:
            ledger = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"[ledger-schema] cannot read {args.ledger}: {exc} -- failing closed", file=sys.stderr)
        return 1
    found = problems(ledger)
    for line in found:
        print(f"   FAILED {line}")
    for alias, rows in sorted(live_aliases_in(ledger).items()):
        print(f"   drifted-but-committed `{alias}` (= `{LIVE_ALIASES[alias]}`) on {len(rows)} row(s), "
              f"invisible to that field's reader, grandfathered and reported: {', '.join(rows)}")
    n_rows = len(ledger.get("entries") or [])
    print(f"   {n_rows} row(s), {len(GOVERNED_FIELDS)} governed field name(s), {len(found)} problem(s)")
    return 1 if (args.check and found) else 0


if __name__ == "__main__":
    sys.exit(main())
