#!/usr/bin/env python3
"""Rank the EMC research backlog by how much each item advances treatment.

The deterministic half of the autonomy loop. No model, no network, stdlib only, $0 — so a
cycle re-scores from scratch every time rather than trusting a score it inherited
(research/manuscripts/program/emc-autonomy-architecture.md §4.2 step 3).

WHAT THIS IS FOR
    `systems/graph/*.json` already records, per route, whether it can still produce a result,
    how its endpoint would reach a patient, what blocks it and what it would cost. Nothing
    reads those fields together and says WHICH ONE TO DO. This does.

WHAT IT IS NOT
    Not a judgement about science. It projects recorded judgements into an order. A wrong
    order is a wrong WEIGHT (research/autonomy/priority-weights.json) or a wrong graph
    record — never a special case added here.

THE THREE RULES THAT ARE CODE, NOT PROSE
    1. A negative/methods write-up may never outrank a live route. Applied as a hard clamp
       AFTER scoring, because weights alone will not hold: the highest-graded route in the
       portfolio today is a write-up of the program's own failure record.
    2. Axis D is never read. It ranks partly on what we hold if the experiment never happens,
       which promotes finished work by construction. It is a human tiebreaker.
    3. `blocked` with no recorded evidence is not filtered out — it is re-emitted as a cheap
       check that re-tests the block, because most blocked rows wait on a $0 observation.

USAGE
    python3 research/autonomy/priority.py                 # ranked table to stdout
    python3 research/autonomy/priority.py --json          # the ledger, to stdout
    python3 research/autonomy/priority.py --write         # seed/refresh research-ledger.json
    python3 research/autonomy/priority.py --explain RT-X  # the arithmetic for one route
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

# ⚠ sys.path, not a package import: this directory is a flat set of scripts run as `python3
# research/autonomy/<tool>.py` from the repo root, and every sibling here resolves the same way.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ids  # noqa: E402
import ledger_io  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
GRAPH = REPO / "systems" / "graph"
WEIGHTS_FILE = HERE / "priority-weights.json"
LEDGER_FILE = HERE / "research-ledger.json"

#: AUT-PD-014. The ceiling `apply_fruitless_attempts` counts down from. Was a literal `3` typed
#: separately into `build_entries`'s default and nowhere else, which is exactly the "one fact, one
#: place" defect CLAUDE.md rule 1 names — `handoff.py:top_items` and `health.py:c_queue_is_takeable`
#: both already read the resulting field (`retry_budget > 0`); neither needed to change, because
#: nothing was ever writing a real number into it.
DEFAULT_RETRY_BUDGET = 3

# Route state values that mean "this route is not itself dead". The route may still be
# blocked or parked — CLAUDE.md §0 is explicit that a blocked row is usually waiting on a
# free check, so blocked is emphatically not dead.
DEAD_WORK_STATES = {"dead"}
OPEN_CLOSURES = {"open", "", None}

# Endpoint outcome_potential values, from systems/graph/publications.json.
LIVE_OUTCOME = "live_positive"
NEGATIVE_OUTCOMES = {"negative_or_methods"}

# ⛔⛔ ROUTE STATUSES THAT MEAN "THERE IS NO STEP A SESSION CAN TAKE ON THIS TODAY" (AUT-PD-075).
# ⚠ THE DEFECT THIS FIXES: the derived row's state was invented here, from `next.blocked_on` alone
# — a field 11 of 77 routes carry — so every other route was born `queued` no matter what the graph
# said about it, and the queue offered rows whose own text says there is nothing to do. Measured on
# the corrected ranking 2026-08-28 by CYC-0053: of 77 derived rows, 39 name a CONCLUSION ("the
# ex-vivo result is banked and needs no further lookup", "Report it as a closed line", "Nothing.
# Cite the closure") or a REGISTRATION waiting on the outside world ("Keep registered for automatic
# re-grade when EMC expression data lands"), and 36 of those 39 were `queued`. That is HALF the
# derived queue, not a handful of rows — AUT-013 was the top-scoring row in the whole ledger.
#
# ⭐ THE DISCRIMINATOR IS A FIELD THE GRAPH ALREADY OWNS, NOT A PHRASE. `state.status` is a closed
# controlled vocabulary defined in systems/CONVENTIONS.md §4.1 and enforced by the route schema:
# `parked` = "failed with today's tools; has a named TECH-* to reopen it", `closed` =
# "conclusively unworkable; carries no TECH-*", `delegated` = "someone else's to answer",
# `superseded` = "replaced by another object, which is named". Each of those, in the vocabulary's
# own words, says the route has no takeable next step. Reading it is a one-line lookup that the
# next re-wording of a `best_next_action` cannot defeat.
# ⛔ THE ALTERNATIVE WAS MATCHING THE ENGLISH ("no further lookup", "closed line", "keep
# registered") AND IT IS REFUSED. It is a grep over prose that a synonym silently defeats — the
# class of guard this repository has already paid for twice (AUT-PD-013's fan-out key,
# AUT-PROP-013's ids: an agreement written in prose that nothing enforced).
#
# ⭐ AND IT FAILS TOWARD OFFERING THE WORK, WHICH IS THE ONLY SAFE DIRECTION HERE. Measured against
# a hand classification of all 77 next-action texts (2026-08-28), with the `next.blocked_on`
# precedence below applied: this set parks 28 rows, 24 of them correctly, 4 of them ACTION rows
# whose route is recorded `parked` while its own next action is a $0 step — AUT-030, AUT-039,
# AUT-061, AUT-076. Wider sets score better on recall and worse here: adding
# `timing.recommendation in {monitor, wait, closed}` lifts recall 0.72 → 0.87 and DOUBLES the false
# parks to 9, hiding live $0 work — CLAUDE.md §0's named failure. A missed row keeps the status
# quo; a false park hides a live route, so precision wins.
# ⛔ THE RESIDUE IS A GRAPH RECORD, NOT A CASE TO ADD HERE. Twelve rows in the class stay `queued`
# because no committed field distinguishes them: RT-CARFILZOMIB is recorded `status: ready`
# (= "nothing blocks it") and `recommendation: pursue_now` while its own next action reads "needs
# no further lookup". Per this module's contract, that is a wrong graph record and it is fixed in
# systems/graph — never by a special case here.
# ⚠ AND `blockers_inherited` / `required_validation[].blocked_by` DO NOT RESCUE THOSE ROWS, tested
# rather than assumed: 13 routes recorded `ready` name a blocker under one of those keys, and they
# include RT-MTAP-PRMT5 ("post the preprint"), the top-scoring live row. Both fields describe the
# route's ultimate VALIDATION, not its next step, so they carry no signal about takeability.
NOT_TAKEABLE_STATUSES = frozenset({"parked", "closed", "delegated", "superseded"})

#: ⛔ AND A PARKED ROW IS NEVER DISPOSED OF. It keeps its id, its score and its `what`; only its
#: state changes, so it stops being OFFERED without being closed. AUT-PD-051's rule: an artifact on
#: the trunk is not the same as the item being finished, and a report is not a closure. Deleting or
#: auto-`done`-ing these rows would take the route's record with them.
PARKED_STATE = "parked"

def _load(name: str) -> Any:
    with (GRAPH / name).open() as fh:
        return json.load(fh)


#: The authority record, read rather than remembered. `publish_bar.py::authority_permits` is the
#: enforcement; this is the same file, consulted for a different question — not "may this post
#: happen?" but "is there a human decision in this row at all?".
AUTHORITY_FILE = HERE / "publication-authority.json"


def _aixiv_grant_covers(endpoint: dict | None) -> bool:
    """Is this endpoint's outward act one the standing aiXiv grant already permits, unattended?

    ⛔⛔ WHY THIS EXISTS, AND IT IS A CORRECTION TO A ROW THIS FUNCTION'S ABSENCE PRODUCED.
    `requires_trimcrae` was never computed. It was hand-typed onto rows once and then carried
    across every re-score by `merge()`'s forward-compat `setdefault` loop, so a judgement made in
    one session became a permanent property of the row that nothing re-examined. Measured
    2026-09-01: thirteen rows carried it, `publish_bar` said the act was impossible on all thirteen,
    and the Stop hook chased them one per stop (AUT-PD-203).

    ⚠ AND IT COST A REAL ESCALATION THE SAME DAY. AUT-073 ("publish the eligibility map") carried
    `requires_trimcrae_why: "§3 is per paper, per act: he must name THIS one for THIS act"`. Its
    endpoint, PUB-STRATEGY-ARCH, is aimed at `preprint` — an aiXiv post, which the standing grant has
    covered since 2026-08-26. The hook fired, a session escalated it, and trimcrae answered:
    *"You don't need my permission to post to aixiv ever. That should be written into your rules.
    This was not a good use of escalation."* ★ CLAUDE.md §3 ALREADY SAID SO, in the bullet added
    after this exact misreading happened once before. **A rule that had already been written twice
    was broken a third time, because it lived in prose and nothing computed it.** This is the
    computation.

    ★ THE ANSWER IS DERIVED FROM TWO COMMITTED ARTIFACTS AND NOTHING ELSE:
      `systems/graph/publications.json` → `target_venue`, and
      `research/autonomy/publication-authority.json` → the aiXiv grant and its deny-list.
    A venue this repository has no standing grant for — a journal, a DOI, a release, an outreach
    package — is untouched and stays his.

    ⛔ FAIL CLOSED, IN THE DIRECTION THAT KEEPS THE ESCALATION. Anything unreadable, any endpoint
    with no venue, any grant that is not live, returns False — which leaves the row exactly as it
    was. This function may only ever REMOVE a false escalation; it can never create one.

    ⚠⚠ AND IT CONTRADICTS A DOCSTRING IN THIS SAME FILE, WHICH IS SAID HERE RATHER THAN LEFT FOR A
    READER TO TRIP OVER. `apply_requires_trimcrae` says the field "is therefore unreachable at
    derive time", on two stated grounds: `build_entries` reads only `systems/graph`, and a route
    legitimately has several next steps of which only one is his act. **Both grounds are about
    setting the field TRUE, and both survive.** Deciding an arbitrary row IS his needs ledger
    context this function does not have — so it never does that. Deciding that a row's endpoint is
    covered by a standing grant needs the graph and the authority file, which is all this reads;
    and the several-next-steps objection is handled by `_names_an_act_beyond_posting`, which is why
    that screen exists rather than the venue test standing alone. ★ The narrower reading is the
    correct one: TRUE is unreachable at derive time, FALSE-by-standing-grant is not.
    """
    if not isinstance(endpoint, dict):
        return False
    if endpoint.get("target_venue") != "preprint":
        return False
    try:
        with AUTHORITY_FILE.open() as fh:
            authority = json.load(fh)
    except (OSError, ValueError):
        return False  # cannot read the grant -> cannot claim it covers anything
    aixiv = authority.get("aixiv")
    if not isinstance(aixiv, dict) or aixiv.get("standing_grant") is not True:
        return False
    scope = aixiv.get("scope")
    if not isinstance(scope, dict):
        return False
    excluded = scope.get("excluded_papers")
    if isinstance(excluded, dict) and endpoint.get("id") in excluded:
        return False  # PUB-ASO is named here, by trimcrae, and stays his
    return True


#: ⛔ THE SECOND-ACT SCREEN, AND IT EXISTS BECAUSE THE FIRST VERSION OF THIS CHANGE WOULD HAVE
#: SWALLOWED A REAL ESCALATION. AUT-046 reads "Post the preprint AND put the MTAP stain in front of
#: a group holding EMC archival material." Its endpoint is aimed at `preprint`, so the venue test
#: above clears it — and the SECOND act, approaching a group, is outreach under trimcrae's name that
#: no grant covers and that he has never delegated. Clearing that row would have deleted a genuine
#: decision on the strength of a venue field that describes only half of it.
#: ★ SO THE VENUE TEST IS NECESSARY AND NOT SUFFICIENT: a row is cleared only if its text names no
#: act beyond posting.
#: ⚠ AND THIS IS A TEXT SCREEN, WHICH IS WEAKER THAN THE VENUE TEST AND IS SAID SO PLAINLY. It reads
#: prose a human wrote, so a second act phrased in words absent from this list slips through. It is
#: used anyway because it fails in the direction that KEEPS an escalation, and because the state it
#: replaces is not "a careful judgement" — it is a field nothing has recomputed since the day it was
#: typed. A row wrongly retained costs one notification; a row wrongly cleared costs a decision that
#: is never made. Those are not symmetric, and the screen is tuned for the cheaper mistake.
_SECOND_ACT = re.compile(
    r"\b(e-?mail|contact|approach|reach out|outreach|collaborat|put .{0,30}in front of|"
    r"journal submission|submit .{0,20}to a journal|zenodo|doi|mint|release|press|"
    r"qeios|correspond|introduce)", re.I)


def _names_an_act_beyond_posting(entry: dict) -> bool:
    """Does this row's own text name an act the aiXiv grant does not reach?"""
    haystack = " ".join(str(entry.get(k) or "") for k in (
        "what", "requires_trimcrae_why", "_requires_trimcrae_why"))
    return bool(_SECOND_ACT.search(haystack))


def load_weights() -> dict:
    with WEIGHTS_FILE.open() as fh:
        return json.load(fh)


def _cost_class(route: dict) -> str:
    """Derive a cost CLASS from the route's recorded next-action cost.

    Never returns or parses a dollar figure into the ledger: research/compute/pricing.md owns
    every cost, and CLAUDE.md rule 1 forbids restating one here. `$0` is the only literal we
    interpret, because "free" is a class, not a price.
    """
    raw = str((route.get("next") or {}).get("cost") or "").strip().lower()
    if raw in {"$0", "0", "free", "$0.00"}:
        return "free"
    if not raw or raw in {"unknown", "unpriced", "-"}:
        return "cheap"  # fail toward doing it; an unpriced item that turns out expensive
        # hits CLAUDE.md §2's halt at spend time, which is the real gate.
    if any(tok in raw for tok in ("gpu", "fleet", "leg", "multi", "k)", "000")):
        return "expensive"
    return "cheap"


def _parked(route: dict) -> bool:
    """Whether this route derives a `parked` row. One predicate, so the state and the two fields
    that explain it can never disagree about which rows are parked."""
    if (route.get("next") or {}).get("blocked_on"):
        return False
    return (route.get("state") or {}).get("status") in NOT_TAKEABLE_STATUSES


def parked_on(route: dict) -> list[str] | None:
    """What the graph says would reopen a route it has already stood down (AUT-PD-075).

    ⭐ NAMING WHAT IT WAITS ON IS THE POINT, not the state string. A row that reads `parked` with
    nothing beside it is the same unanswered question in a new costume (CLAUDE.md §4: a row reading
    UNKNOWN or "will check next cycle" is an unanswered question wearing the costume of a status).
    Both registers are read because they answer different halves and neither is complete alone:
    `timing.revisit_trigger` names the TECH-* whose arrival is being scanned for (schema-REQUIRED
    for any recommendation other than `pursue_now`), and `revival_trigger` names the TR-* result
    that would revive the route. A `closed` route may legitimately have neither, and `None` then
    says so honestly rather than inventing a condition.
    """
    triggers = list((route.get("timing") or {}).get("revisit_trigger") or [])
    triggers += list(route.get("revival_trigger") or [])
    return sorted(set(triggers)) or None


def _blocked_on_human(route: dict) -> bool:
    if (route.get("state") or {}).get("authorization") == "needs_decision":
        return True
    for item in (route.get("next") or {}).get("blocked_on") or []:
        text = str(item).lower()
        if any(tok in text for tok in ("trimcrae", "authoris", "authoriz", "decision", "permission")):
            return True
    return False


def _kind(route: dict, endpoint: dict | None) -> str:
    """Classify the work this route's next step actually is."""
    potential = (endpoint or {}).get("outcome_potential")
    if potential in NEGATIVE_OUTCOMES:
        return "negative"
    status = (route.get("state") or {}).get("status")
    if status == "parked" and route.get("revival_trigger"):
        return "regrade"
    if (route.get("readiness") or {}).get("attainable_today") in {
        "preprint",
        "journal_submission",
        "chemrxiv",
    }:
        return "write"
    if (route.get("required_validation") or []):
        return "experiment"
    return "analysis"


def _blocker_leverage(routes: list[dict]) -> dict[str, int]:
    """How many OTHER routes share at least one blocker with this one."""
    by_blocker: dict[str, set[str]] = {}
    for route in routes:
        for blocker in route.get("blockers_inherited") or []:
            by_blocker.setdefault(blocker, set()).add(route["id"])
    leverage: dict[str, int] = {}
    for route in routes:
        peers: set[str] = set()
        for blocker in route.get("blockers_inherited") or []:
            peers |= by_blocker.get(blocker, set())
        peers.discard(route["id"])
        leverage[route["id"]] = len(peers)
    return leverage


def build_entries(weights: dict | None = None) -> list[dict]:
    """Project systems/graph into scored ledger entries, highest score first."""
    weights = weights or load_weights()
    terms = weights["terms"]
    scale = weights["patient_path_scale"]
    cost_rank = weights["cost_class_rank"]
    cap = weights["blocker_leverage_cap"]

    routes = _load("routes.json")
    endpoints = {p["id"]: p for p in _load("publications.json")}
    leverage = _blocker_leverage(routes)

    entries: list[dict] = []
    for index, route in enumerate(sorted(routes, key=lambda r: r["id"])):
        state = route.get("state") or {}
        endpoint = endpoints.get((route.get("publication") or {}).get("endpoint"))
        kind = _kind(route, endpoint)

        is_live = (
            (endpoint or {}).get("outcome_potential") == LIVE_OUTCOME
            and state.get("work_state") not in DEAD_WORK_STATES
            and route.get("closure_kind") in OPEN_CLOSURES
        )
        patient = scale.get(str((endpoint or {}).get("patient_path")), 0.0)
        pursue = (route.get("timing") or {}).get("recommendation") == "pursue_now"
        tier1 = str((route.get("grade") or {}).get("value") or "").startswith("Tier 1")
        reachable = (route.get("readiness") or {}).get("attainable_today") in {
            "preprint",
            "journal_submission",
            "chemrxiv",
        }
        cost_class = _cost_class(route)
        human = _blocked_on_human(route)
        lever = min(leverage.get(route["id"], 0), cap)

        inputs = {
            "live": bool(is_live),
            "patient_path": (endpoint or {}).get("patient_path"),
            "patient_path_scaled": patient,
            "pursue_now": bool(pursue),
            "tier_one": bool(tier1),
            "endpoint_reachable": bool(reachable),
            "blocker_leverage": lever,
            "cost_class": cost_class,
            "blocked_on_human": bool(human),
            # ⛔ AUT-PD-014: this was HARDCODED and never recomputed — priority-weights.json declares
            # a real weight for this term and nothing ever fed it. It stays 0 HERE on purpose: a
            # freshly-derived row has no access to research-ledger.json's own history
            # (`build_entries` reads only `systems/graph`, per the module docstring), so the true
            # count can only be known once this row's `dispatch_log` — carried across re-scores by
            # `merge()`'s forward-compat `setdefault` loop — has been merged in. The real value is
            # computed post-merge by `apply_fruitless_attempts`, which OVERWRITES this 0 exactly the
            # way `apply_age_factor` overwrites the age term it does not set here either.
            "fruitless_attempts": 0,
        }
        score = (
            terms["live"]["weight"] * inputs["live"]
            + terms["patient_path"]["weight"] * patient
            + terms["pursue_now"]["weight"] * inputs["pursue_now"]
            + terms["tier_one"]["weight"] * inputs["tier_one"]
            + terms["endpoint_reachable"]["weight"] * inputs["endpoint_reachable"]
            + terms["blocker_leverage"]["weight"] * lever
            + terms["cost"]["weight"] * cost_rank[cost_class]
            + terms["blocked_on_human"]["weight"] * inputs["blocked_on_human"]
        )

        entries.append(
            {
                "id": f"AUT-{index + 1:03d}",
                "_derived": True,  # written by the scorer from systems/graph; see merge()
                "what": (route.get("next") or {}).get("best_next_action")
                or f"Decide the next action for {route['id']} — the graph records none.",
                "serves": {
                    "route": route["id"],
                    "publication": (route.get("publication") or {}).get("endpoint"),
                    "strategy": route.get("strategy"),
                },
                "kind": kind,
                # ⛔ THE GRAPH'S OWN `state.status` DECIDES FIRST (AUT-PD-075). Before this, the
                # only input was `next.blocked_on`, so a route the graph records as parked, closed
                # or delegated was still born `queued` and offered as takeable work every cycle.
                # ⛔ AND `next.blocked_on` OUTRANKS THE STATUS, WHICH IS NOT THE ORDER I WROTE
                # FIRST. `state.status` describes the ROUTE; `next.blocked_on` names a blocker on
                # THE NEXT STEP, and clamp 3 turns an unevidenced one into a free re-test
                # (CLAUDE.md §0: a blocked row is usually waiting on a $0 observation). Parking
                # first suppressed that re-test — caught by
                # systems/tests/test_autonomy_priority.py's clamp-3 test on RT-SYNLETH-DEP, the one
                # route that is `parked` AND names a blocker. The $0 re-test of BLK-NO-EMC-DATA is
                # exactly the observation its "keep registered until EMC expression data lands"
                # registration is waiting on, so the specific statement wins over the general one.
                "state": (
                    "blocked" if (route.get("next") or {}).get("blocked_on")
                    else PARKED_STATE if state.get("status") in NOT_TAKEABLE_STATUSES
                    else "queued"
                ),
                # ⛔ ALWAYS WRITTEN, INCLUDING AS None. `merge()` ends with a `setdefault` over every
                # key of the previous row — forward-compat, so an unknown key is never dropped — and
                # a key this function omits on a later run would therefore be RESURRECTED from the
                # stale row. A route that leaves NOT_TAKEABLE_STATUSES must lose this field.
                "parked_on": parked_on(route) if _parked(route) else None,
                "parked_by_graph_status": state.get("status") if _parked(route) else None,
                "owner": None,
                "cost_class": cost_class,
                "cost_points_at": "research/compute/pricing.md",
                "blocked_by": (route.get("next") or {}).get("blocked_on") or None,
                "blocked_evidence": None,
                "retry_budget": DEFAULT_RETRY_BUDGET,
                "attempts": 0,
                "last_evidence_utc": state.get("last_verified"),
                "score": round(score, 2),
                "score_inputs": inputs,
            }
        )

    # ⛔⛔ THE ONE THING THIS PASS MAY DO TO `requires_trimcrae`: TURN IT OFF, NEVER ON.
    # The field is otherwise hand-typed and carried forward for ever by `merge()`'s setdefault
    # loop, so a judgement made once outlives the reason for it. This clears it — and ONLY clears
    # it — where the outward act is one the standing aiXiv grant already permits unattended.
    # ★ Written EXPLICITLY as False so `merge()`'s `entry.setdefault(key, value)` cannot resurrect
    # the stale True from the previous generation of the row. The key is OMITTED in every other
    # case, deliberately, so that a hand-set `requires_trimcrae` on a journal, DOI, release or
    # outreach row survives untouched — see the "ALWAYS WRITTEN, INCLUDING AS None" note above for
    # why the distinction between writing None and omitting the key is load-bearing here.
    # ⛔ THE ANTI-GAMING ANSWER, WRITTEN DOWN RATHER THAN LEFT IMPLICIT (amendment_guard.py): this
    # makes the loop escalate LESS, which is the direction that deserves suspicion. Three things
    # defend it and none of them is convenience. (1) trimcrae asked for it in these words, on
    # 2026-09-01: "You don't need my permission to post to aixiv ever. That should be written into
    # your rules." (2) It is computed from two committed artifacts, so it is falsifiable by reading
    # them rather than by trusting this session. (3) It makes the loop do MORE work, not less — a
    # row it can no longer file as "awaiting trimcrae" is a row it has to finish.
    # ⚠ Keyed on the entry's own `serves.publication` rather than zipped against the route list.
    # A zip would be correct today — `entries` is built in `sorted(routes, key=id)` order — and
    # would silently mis-pair the moment anything filters or reorders either list. This is the
    # cheaper thing to get right once.
    for entry in entries:
        endpoint = endpoints.get((entry.get("serves") or {}).get("publication"))
        if _aixiv_grant_covers(endpoint) and not _names_an_act_beyond_posting(entry):
            entry["requires_trimcrae"] = False
            entry["_requires_trimcrae_why"] = (
                "DERIVED, not judged: this route's endpoint "
                f"{(endpoint or {}).get('id')} is aimed at `preprint`, the standing aiXiv grant in "
                "publication-authority.json covers it, and it is not in that grant's "
                "`excluded_papers`. Posting it needs nobody. ⚠ This says NOTHING about whether the "
                "paper is READY — publish_bar decides that, and it is the loop's own work either "
                "way. If this route ever acquires an act at another venue, that act is his and this "
                "field is not the place to record it."
            )

    entries = apply_clamps(entries, weights)
    entries.sort(key=lambda e: (-e["score"], e["serves"]["route"]))
    return entries


def _score_inputs(entry: dict) -> dict:
    """The row's `score_inputs` dict, created if it is absent OR EXPLICITLY NULL.

    ⛔ `dict.setdefault("score_inputs", {})` IS WRONG HERE AND WAS WRONG IN FOUR PLACES.
    `setdefault` inserts only when the key is ABSENT; a row carrying `"score_inputs": null` has the
    key, so it returns None and the subscript that follows raises
    `TypeError: 'NoneType' object does not support item assignment`. Measured 2026-08-28: exactly
    ONE row in a 265-row ledger (AUT-COV-001) carries an explicit null, and it took out four tests
    in the commit loop — `test_every_committed_derived_score_reproduces_from_its_own_inputs`,
    `test_the_scoring_pipeline_is_a_fixed_point_of_itself`, `test_a_third_application_still_moves_nothing`
    and `test_the_ranker_runs_against_the_committed_ledger` — so NOTHING could be committed until it
    was fixed.
    ⚠ THE ONE-OF-A-PAIR DEFECT, AT FOUR. The read side two lines above the first crash site already
    guarded it correctly (`(e.get("score_inputs") or {})`), which is the tell: the same expression
    written defensively in one place and carelessly in another, in the same function. All four write
    sites shared the careless form and only the first one had been reached, so fixing that line alone
    would have left three latent copies of a bug already proven to stop the repository.
    ★ A row is null rather than absent because a writer emitted the key with no value; that is
    legitimate JSON and this reader's job is to accept it, not to demand the ledger be rewritten.
    """
    got = entry.get("score_inputs")
    if not isinstance(got, dict):
        got = {}
        entry["score_inputs"] = got
    return got


def apply_clamps(entries: list[dict], weights: dict) -> list[dict]:
    """The two rules that weights cannot express. See the module docstring."""
    clamps = weights["clamps"]

    if clamps["negative_never_outranks_live"]["enabled"]:
        live_scores = [e["score"] for e in entries if e["score_inputs"]["live"]]
        if live_scores:
            ceiling = min(live_scores) - 1.0
            for entry in entries:
                if entry["kind"] == "negative" and entry["score"] > ceiling:
                    entry["score_clamped_from"] = entry["score"]
                    entry["score"] = round(ceiling, 2)
                    entry["clamp"] = "negative_never_outranks_live"

    if clamps["blocked_without_evidence_becomes_a_check"]["enabled"]:
        for entry in entries:
            if entry["state"] == "blocked" and not entry["blocked_evidence"]:
                entry["kind"] = "fetch"
                entry["state"] = "queued"
                entry["cost_class"] = "free"
                entry["what"] = (
                    "RE-TEST THE BLOCK before doing anything else — it is recorded without "
                    f"evidence. Blocked on: {entry['blocked_by']}. Original next action: {entry['what']}"
                )
                entry["clamp"] = "blocked_without_evidence_becomes_a_check"

    return entries


# Fields the GRAPH owns: regenerated from systems/graph every re-score, and an edit to them here
# would be overwritten anyway. Everything else on an entry belongs to the SESSION that touched it.
SESSION_OWNED = ("owner", "claimed_utc", "attempts", "retry_budget", "blocked_evidence", "blocked_by",
                 "prerequisite_of")
# States a session sets. `queued`/`blocked`/`parked` are re-derived from the graph; these are not.
# ⛔ AND THAT ORDERING IS THE AUT-PD-051 GUARANTEE: a session that finished a row wrote `done`
# here, and `merge()` lets that WIN over the graph's re-derived `parked`, so a re-score can never
# quietly un-finish work — nor can it finish work by parking it.
SESSION_STATES = {"running", "done", "abandoned"}


#: The states `apply_age_factor` refuses to age, and the states `n_unscored_open` refuses to count.
#: ⛔ ONE HOME (AUT-PD-050). This was an inline literal at a single call site, pinned by
#: `test_the_closed_state_scope_matches_the_states_the_scorer_itself_skips` as a SUBSTRING SEARCH of
#: this file's source — which binds the text, not the value. A second reader of the same fact
#: arrived with `n_unscored_open`, so the fact now has a name; that test now compares the VALUE
#: against `admissibility.CLOSED_STATES`, which a substring search could never have done.
CLOSED_STATES = ("done", "abandoned", "superseded")


def score_rank(entry: dict) -> float:
    """The ASCENDING sort component that orders one row by its score — best (highest) first.

    ⛔⛔ ONE HOME, BECAUSE THE TWO FILES THAT RANK THE QUEUE RANKED A MISSING SCORE DIFFERENTLY
    (AUT-PD-050). `build_ledger` sorted with `-(score if score is not None else -1e9)` — an unscored
    row strictly last. `continuity.ready`, the list a session actually picks work FROM, sorted with
    `-(e.get("score") or 0)` — an unscored row ordered as if it had scored exactly zero, i.e. ABOVE
    every negatively-scored row, and indistinguishable from the two committed rows that really do
    score 0.0. The divergence was latent rather than live (measured 2026-08-28: every ready row
    scored 36.0 to 152.0, so nothing negative was ready that hour) and `apply_fruitless_attempts`
    alone can take a ready row below zero at any time.
    ⚠ THE TIEBREAK IS DELIBERATELY NOT HERE. The ranker breaks ties on route and the ready list on
    id; those are genuinely different questions and folding them together would be inventing a
    shared fact rather than sharing one. What the two must agree on is where a row with NO score
    goes, which is this function and nothing else.
    ⭐ AN UNSCORED ROW SORTS LAST, WHICH IS HONEST AND IS ALSO THE STARVATION: no ranking term can
    move it from there, so the fix for a starved row is a `score`, never a change to this ordering.
    """
    score = entry.get("score")
    return -float(score) if isinstance(score, (int, float)) and not isinstance(score, bool) else 1e9


def _utcnow():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc)


def _parse_utc(value):
    """Lenient ISO-8601 read. An unparseable stamp is treated as ABSENT, which makes the claim stale —
    the safe direction, because the alternative is an immortal claim."""
    import datetime
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        stamp = datetime.datetime.fromisoformat(text)
        return stamp if stamp.tzinfo else stamp.replace(tzinfo=datetime.timezone.utc)
    except Exception:
        return None


def _cycle_interval_hours():
    """The governor owns this figure; read it rather than restating it."""
    try:
        with (HERE / "autonomy-state.json").open() as fh:
            value = json.load(fh).get("cycle_interval_hours")
        return float(value) if value else None
    except Exception:
        return None


def load_existing() -> dict | None:
    try:
        with LEDGER_FILE.open() as fh:
            return json.load(fh)
    except Exception:
        return None


def age_factor(row: dict, weights: dict, today=None) -> float:
    """A BOUNDED wait bonus in [0, 1] — Slurm's age factor, and the bound is the whole point.

    ⛔⛔ WHY THIS EXISTS. The 2026-08-27 `/deep-research` pass tried to refute the claim and could
    not, 3-0: **no verified orchestrator implements any anti-starvation mechanism.** Every shipped
    default is priority-then-FIFO or bare FIFO — no ageing, no quota, no wait-time bound. AlabOS is a
    two-pass stable sort on (submitted_at, priority) and a repo-wide grep for
    `starvation|starve|aging|ageing|fairness|round-robin` returns ZERO hits. ⛔ THIS LEDGER HAD THE
    SAME DEFECT AND THE SAME SYMPTOM: it ranks on score alone, and carried 70+ queued rows with
    several filed weeks earlier and never taken.

    ⭐ SATURATING, NOT UNBOUNDED, AND THAT IS THE DESIGN. Slurm's factor rises linearly to
    `PriorityMaxAge` and then stops. An unbounded age term does not fix a starving queue — it INVERTS
    it into pure FIFO, and a live patient-facing route would sit behind a stale one purely for being
    younger. Read the ceiling from `priority-weights.json`; never restate it here.

    ⚠ FAIR-SHARE WAS DELIBERATELY NOT TAKEN. It arbitrates between competing USERS and there is one
    operator, so it would be ceremony. Take the age term, leave the scheduler.

    ⚠ THE CLOCK IS `last_evidence_utc`, WHICH IS A DATE THE ROW ALREADY CARRIES — not a new field and
    not a git walk on every scoring run. A row with no readable date scores 0.0: unreadable buys
    nothing, the same direction every other cap in this loop fails.
    """
    import datetime as _dt
    sat = ((weights.get("age_saturates_days") or {}).get("value"))
    if not isinstance(sat, (int, float)) or sat <= 0:
        return 0.0
    raw = row.get("last_evidence_utc")
    if not isinstance(raw, str) or not raw.strip():
        return 0.0
    try:
        seen = _dt.date.fromisoformat(raw.strip()[:10])
    except ValueError:
        return 0.0
    now = today or _dt.date.today()
    days = (now - seen).days
    if days <= 0:
        return 0.0
    return min(days / float(sat), 1.0)


def apply_age_factor(entries: list[dict], weights: dict, today=None) -> list[dict]:
    """Add the bounded wait bonus to every OPEN row, echoing the input beside the score.

    ⛔ OPEN ROWS ONLY. Ageing a closed row would raise the score of finished work, which is how a
    ranker starts recommending things that are already done.
    ⭐ AND THE INPUT IS ECHOED into `score_inputs`, because this file's own contract is that every
    term a reader sees is one they can re-derive — a score that moved for a reason nobody can check
    is the thing `_scores_are_not_evidence` warns about.
    """
    import datetime as _dt  # module-local, matching `age_factor`'s own import below
    w = ((weights.get("terms") or {}).get("age") or {}).get("weight")
    if not isinstance(w, (int, float)):
        return entries
    stamp = (today or _dt.date.today()).isoformat()
    for e in entries:
        if (e.get("state") or "queued") in CLOSED_STATES:
            continue
        f = round(age_factor(e, weights, today=today), 4)
        # ⛔⛔ THE SECOND HALF OF THE SAME DEFECT, AND THE ONE THAT WAS ACTIVELY MOVING THE QUEUE
        # (AUT-PROP-036). This was `score = score + w * f`, so on a hand-filed row — whose score
        # `merge()` carries forward — the bonus was added AGAIN on every re-score rather than once
        # per day. Measured across eight consecutive commits in 92 minutes on 2026-08-28:
        # AUT-PROP-036 climbed 158.0 → 158.9 → 159.8 → 160.7 → 161.6 → 162.5 → 163.4 → 164.3 →
        # 165.2 (+0.9 each) while its `age_factor` stayed 0.0714 and its `last_evidence_utc` stayed
        # 2026-08-27. Nothing about the row's evidence changed; only the number did. By then the
        # top 15 rows of the ranked table were all hand-filed process/proposal rows, several already
        # marked "✅ DONE", and the best DERIVED route row was 78 points below them — CLAUDE.md §0's
        # named failure arriving as arithmetic rather than as a judgement.
        # ⭐ APPLY THE DELTA AGAINST WHAT IS ALREADY ON THE ROW. The previously-applied factor is
        # echoed in `score_inputs` and carried by `merge()`; a derived row has none (its inputs are
        # rebuilt each run) so it gets the full term exactly as before. This also makes the term
        # correctly REVERSIBLE: refreshing a row's evidence lowers its age factor, and the bonus now
        # shrinks with it instead of being a ratchet.
        # ⭐ ONE TYPE-CHECKED READ SERVING BOTH THE READ AND THE WRITE BELOW (AUT-PD-152). The old
        # spelling was `(e.get("score_inputs") or {}).get(...)`, which survives a FALSY non-dict
        # (None, "", 0, []) and raises on a truthy one — `'str' object has no attribute 'get'`,
        # found by this fix's own regression test. `or {}` is a falsiness test wearing a type
        # check's clothes; `isinstance` is the type check.
        si = e.get("score_inputs")
        si = si if isinstance(si, dict) else None
        prev = si.get("age_factor") if si is not None else None
        prev = float(prev) if isinstance(prev, (int, float)) and not isinstance(prev, bool) else 0.0
        if not f and not prev:
            continue
        if f:
            # ⛔⛔ `setdefault` RETURNS THE EXISTING VALUE, AND A ROW REALLY DOES CARRY
            # `"score_inputs": null` — so this line was `None["age_factor"] = f` and took the whole
            # loop down. Measured 2026-08-29T00:02Z (AUT-PD-152) on `AUT-COV-001`, filed by CYC-0011
            # and sitting harmlessly on the trunk for days. ⭐ THE TRIGGER WAS THE CALENDAR, NOT A
            # COMMIT: two lines up, `prev` is read defensively (`or {}`) and the guard
            # `if not f and not prev: continue` skipped this row for as long as its age factor
            # rounded to zero. The date rolling to 08-29 made `f` non-zero for the first time, the
            # row reached this write, and `priority.py --write` — step 3 of EVERY cycle — began
            # crashing on state no cycle had touched. ⛔ It deadlocked the loop rather than merely
            # failing: `admissibility.check_write` then refuses every ledger write as
            # `refused_stale_input` (the stored age factors no longer match the date), so a cycle
            # could not re-score AND could not claim, and the two failures each blocked the other's
            # fix. ★ The defensive READ two lines up is the shape this WRITE should always have had;
            # AUT-PD-050 fixed the crashes in this function and this one survived because a null
            # `score_inputs` is a different thing from an absent one.
            if si is None:
                si = {}
                e["score_inputs"] = si
            si["age_factor"] = f
            # ⭐⭐ THE DATE THIS TERM WAS COMPUTED AGAINST, RECORDED BESIDE IT (AUT-PD-198).
            # `age_factor` is a function of `date.today()`, so without this the echoed value is a
            # reading whose basis is not on the record — and `admissibility._stale_age`, which
            # recomputes against TODAY, then refuses every row at UTC midnight. That is not a
            # hypothetical: the block above records the same rule deadlocking the loop, because a
            # cycle could neither re-score nor claim and each failure blocked the other's fix. The
            # trunk went red daily by construction until some cycle happened to re-score.
            # ★ WITH THE BASIS ON THE RECORD, R4 ASKS THE RIGHT QUESTION: not "is this the value
            # today?" but "is this the value its own basis date produces?" — which still catches a
            # hand-edited age term (the number would not match its stated basis) while no longer
            # firing on the passage of time, which is not a defect and never was.
            si["age_factor_as_of"] = stamp
        elif si is not None:
            si.pop("age_factor", None)
            si.pop("age_factor_as_of", None)
        if isinstance(e.get("score"), (int, float)):
            e["score"] = round(e["score"] + w * (f - prev), 1)
    return entries


def merge(generated: list[dict], existing: dict | None) -> list[dict]:
    """Carry the previous ledger's SESSION state onto the freshly derived entries.

    ⛔⛔ WITHOUT THIS, `--write` IS A DATA-LOSS BUG, AND IT WAS ONE. Found by running the first real
    cycle by hand on 2026-08-26 (receipt CYC-0001): step 3 of every cycle re-scores with `--write`,
    which regenerated all 77 entries from the graph and silently destroyed

        - every hand-added entry — though the ledger's own `_role` says a session may add one the
          graph cannot express, so every filed proposal and process_defect would have evaporated;
        - `owner`, so step 4's "claim the item before working" was undone by the NEXT cycle's step 3,
          which is precisely the "work with no owner is indistinguishable from work in progress"
          failure the whole ledger exists to prevent;
        - `attempts`, `retry_budget` and `blocked_evidence` — so a route could be retried forever and
          the scorer's `fruitless_attempts` penalty could never fire.

    ⭐ AND THE IDS WERE POSITIONAL, which is the quieter half. `AUT-{index+1}` over sorted routes
    means adding ONE route to the graph renumbers everything after it, so `AUT-049` written into a
    receipt would later name a DIFFERENT route — a silent rewrite of the historical record. Ids are
    now assigned once per route and persisted here.
    """
    if not existing or not isinstance(existing.get("entries"), list):
        return generated

    prior = existing["entries"]
    # ⛔ ONLY DERIVED ROWS MAY DONATE AN ID. Keying this on ANY prior row with a matching route let a
    # hand-filed entry hand its own id to the graph's row for that route: AUT-PROP-004 ("escalate the
    # corresponding-author emails") had its id taken over by "post the preprint", and the real
    # AUT-PROP-004 vanished. Two rows legitimately serve one route — the work and the thing blocking
    # it — so the route is not an identity.
    by_route = {e["serves"]["route"]: e for e in prior
                if e.get("_derived") and isinstance(e.get("serves"), dict) and e["serves"].get("route")}
    # ⛔⛔ THE ORDINAL IS PARSED BY `ids.parse_entry_id`, NOT BY SPLITTING ON THE LAST DASH.
    # This read `int(id.rsplit("-", 1)[-1])` inside a bare `except ValueError: pass`, which was
    # correct for exactly as long as every ledger id ended in its ordinal. It stopped being correct
    # on 2026-09-01, when `ids.next_entry_id` began appending a session discriminator to stop two
    # concurrent sessions minting the same id (AUT-PD-171): `AUT-PD-204-6b009680` splits to
    # `6b009680`, `int()` raises, and the `except` swallows it — so a discriminated row is INVISIBLE
    # to `used`, and the derived `AUT-NNN` counter stops de-conflicting against it.
    # ⚠ THE FAILURE MODE IS SILENT AND THE `except` IS WHY: nothing goes red, the id set is simply
    # short, and the next derived row is minted onto a number a hand-filed row already holds — where
    # `merge()`'s duplicate check finds it, one step too late to say what caused it. Found by the
    # seat that made the change, in the file it does not own, and handed over rather than reached
    # into. One regex, in `ids`, read by allocator and readers alike.
    used = set()
    for e in prior:
        parsed = ids.parse_entry_id(str(e.get("id", "")))
        if parsed is not None:
            used.add(parsed[1])
    next_id = max(used) + 1 if used else 1

    for entry in generated:
        old_entry = by_route.get(entry["serves"]["route"])
        if old_entry is None:
            while next_id in used:
                next_id += 1
            entry["id"] = f"AUT-{next_id:03d}"
            used.add(next_id)
            continue
        entry["id"] = old_entry["id"]  # stable across graph growth
        for key in SESSION_OWNED:
            if old_entry.get(key) not in (None, 0):
                entry[key] = old_entry[key]
        if old_entry.get("state") in SESSION_STATES:
            entry["state"] = old_entry["state"]
        if str(old_entry.get("last_evidence_utc") or "") > str(entry.get("last_evidence_utc") or ""):
            entry["last_evidence_utc"] = old_entry["last_evidence_utc"]
        for key, value in old_entry.items():  # forward-compat: never drop a key we do not know
            entry.setdefault(key, value)

    # Entries the graph does not produce — proposals, process_defect rows, prerequisites, anything a
    # session filed. ⛔ KEY ON ID ALONE. A first attempt also excluded any prior row whose
    # `serves.route` the graph produces, reasoning that it must be a duplicate; it is not, and that
    # dropped AUT-PROP-002 and AUT-PROP-003 — the hardening round and the blind seat filed as the
    # only path to unblocking the portfolio's top-ranked paper — on their very first re-score.
    # Because ids are now stable per route, a hand-added row can never collide with a derived one,
    # so id is the whole test. A row whose route later leaves the graph is KEPT rather than deleted:
    # retiring an entry is a session's decision with a reason, never a silent side effect of a
    # re-score.
    # ⛔ AND THE DROP IS SCOPED TO `_derived` ROWS, NOT TO THE ID ALONE. This filter exists to discard
    # the PREVIOUS generation of derived rows, which `generated` has just rebuilt. A HAND-FILED row is
    # not a stale copy of anything, so when one carries a derived row's id the id-only test deletes it
    # outright — silently, on a routine re-score, with no error and no trace. That is the AUT-PROP-004
    # incident named above arriving through the other door: there a hand-filed row STOLE a derived id,
    # here it LOSES to one. Scoping by the property (`is this row one the graph produces?`) instead of
    # by the id lets the collision survive into `merged`, where the check below reports it by name.
    derived_ids = {e["id"] for e in generated}
    kept = [e for e in prior if not (e.get("_derived") and e.get("id") in derived_ids)]
    merged = generated + kept

    # ⛔ AND THE DEDUPE ABOVE ONLY EVER GUARDED THE *DERIVED* SPACE. Hand-filed ids (AUT-PROP-*,
    # AUT-PD-*) are TYPED by the filing cycle — nothing mints them and nothing checked them — so two
    # cycles reading the same stale ledger pick the same next number and both write it. Measured
    # 2026-08-27 (CYC-0020): `AUT-PROP-015` named BOTH the PUB-FUSION-PARTNER round-8 item (CYC-0019)
    # and the PUB-ATR gse-series fix (CYC-0018), and `AUT-PD-012` named two unrelated process
    # defects (CYC-0011, CYC-0015). ⚠ THE DAMAGE IS NOT THE COLLISION, IT IS THAT EVERY ID-KEYED
    # OPERATION SILENTLY PICKS ONE: a claim (`owner`/`claimed_utc`), a lease release, a retry-budget
    # decrement and `prerequisite_of` all resolve by id, so a cycle can claim one row and finish the
    # other, and the handoff prompt can point a successor at a row that is not the one it describes.
    # Fail LOUDLY here rather than letting a re-score launder it: this function is the one place
    # every entry passes through.
    seen: dict[str, int] = {}
    for entry in merged:
        seen[entry.get("id", "")] = seen.get(entry.get("id", ""), 0) + 1
    collisions = sorted(i for i, n in seen.items() if n > 1)
    if collisions:
        raise ValueError(
            "duplicate ledger ids: "
            + ", ".join(collisions)
            + " — an id names exactly one item. Rename the LATER-filed row (keep the earlier "
            "filer's claim on the string), record `_renamed_from` on it, and re-run."
        )
    return merged


def route_score_floor(entries: list[dict]) -> dict[str, float]:
    """The lowest score the GRAPH itself puts on each route, read off that route's derived rows.

    ⭐ THE FLOOR IS THE AGGREGATOR, AND THE CHOICE IS CONSERVATIVE ON PURPOSE. A derived row is the
    graph's own enumerated next step for a route, scored by `build_entries` from the route's inputs.
    A hand-filed row on the same route is a step the graph does not express, so its per-step terms
    are UNKNOWN and cannot be computed. Taking the minimum says the only thing the evidence supports:
    this row is worth no more than the least the graph already values on its own route. Taking the
    max, or a mean, would put a number on the row that no derived sibling justifies.
    ⚠ AND THE AGGREGATOR IS CURRENTLY UNEXERCISED, WHICH IS SAID HERE RATHER THAN LEFT TO BE
    DISCOVERED: on the ledger this was written against every route with any derived row has EXACTLY
    ONE, so min, max and mean are the same number today. `test_the_floor_is_the_lowest_sibling`
    binds the rule against a synthetic multi-sibling route, because the committed data cannot.
    ⛔ A ROUTE WITH NO DERIVED ROW GETS NO ENTRY HERE, and that absence must be REPORTED rather than
    filled — `health.py`'s `scores_are_reachable` is what reports it. RT-AUTONOMY is not a route in
    systems/graph, so its rows can never inherit; that is the measured reason this pass cannot flood
    the queue with the loop's own process defects (AUT-PD-143).
    """
    seen: dict[str, float] = {}
    for entry in entries:
        if not entry.get("_derived"):
            continue
        score = entry.get("score")
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            continue
        route = (entry.get("serves") or {}).get("route")
        if not route:
            continue
        if route not in seen or score < seen[route]:
            seen[route] = float(score)
    return seen


#: The `score_inputs` keys that mean "a penalty has ALREADY been charged against this row's score".
#: `apply_route_inheritance` clears them when it replaces the score, because after that replacement
#: the statement they make is false — see its docstring. `age_factor` is deliberately NOT here: it
#: is a term the pass puts back itself, so its echo stays true.
CHARGED_AGAINST_SCORE = ("blocked_with_evidence", "fruitless_attempts", "blocked_on_human")


def apply_route_inheritance(entries: list[dict], weights: dict) -> list[dict]:
    """Give an unscored hand-filed row the floor of its own route, so it can be OFFERED at all.

    ⛔⛔ THE DEFECT (AUT-PD-143, measured 2026-08-28): `build_entries` is the only place a `score` is
    CREATED and it derives rows from systems/graph, while `merge()` carries a hand-filed row forward
    verbatim — so a row filed without a `score` key could never gain one, on any re-score, ever. Four
    readers then treated that absence as "not work": the sort behind a -1e9 sentinel, `_table` (which
    CRASHED on such a row rather than printing it), `health.py`'s `queue_is_takeable`, and
    `handoff.py`'s successor queue. 104 of 277 rows carried no score and 74 of those were OPEN, so a
    third of the ledger had never been offered to any cycle — including live in-silico work on
    RT-SGK1, RT-ALK-HIT, RT-JUNCTION-NEOANTIGEN and RT-PARTNER-STRAT, while the ranked queue's top
    takeable rows were the loop's own process defects. CLAUDE.md §0's named failure arriving as a
    missing dict key rather than as a judgement.

    ★ THE IDIOM IS NOT NEW HERE. `apply_session_penalties`'s rule 2 already ASSIGNS a prerequisite's
    score from its parent's and records `_score_basis` WITHOUT writing `score_inputs`, and
    `admissibility.py` models exactly that shape as UNACCOUNTED rather than as a failure. This pass
    is that idiom applied along `serves.route` instead of along `prerequisite_of`.
    ⛔ IT NEVER FABRICATES `score_inputs`. A full set of zeroed inputs would make an inherited score
    look computed, which is what `test_priority_ranks_the_hand_filed_entries_too` exists to forbid;
    the row carries `_score_basis` in prose instead, exactly as a hand-scored row does.

    ⛔⛔ IT RUNS LAST, AND THE FIRST ATTEMPT RAN IT MID-PIPELINE — THE DIFFERENCE WAS 90 POINTS AND
    IT POINTED THE WRONG WAY (measured this cycle, before either version was committed). Placed
    after `apply_age_factor` and before the penalty passes, the pass reads a derived sibling's
    PRE-PENALTY score, so RT-PARTNER-STRAT's floor read 195.0 while the same row, AUT-049, stands at
    105.0 in the ledger a reader holds. Two consequences, and the second is the serious one:
      1. `_score_basis` would cite a number that appears nowhere in the file it is written into —
         CLAUDE.md §1's one-fact-one-place violated by the very field added to make the score
         checkable.
      2. Five hand-filed rows (AUT-PD-001..004, AUT-PROP-004 — sandbox and trunk process defects)
         would have entered at ~195.9, ABOVE every live research row the pass exists to surface,
         including RT-SGK1 and RT-ALK-HIT at 140.0. The fix would have been §0-NEGATIVE for that
         route: process defects outranking in-silico work is the exact failure this is curing.
    ⭐ So the floor is the sibling's FINISHED score, and the row's own row-specific terms are then
    charged by the passes that own them — never re-implemented here.

    ⭐ HOW THE ROW'S OWN TERMS GET CHARGED, WITHOUT A FOURTH COPY OF THREE FORMULAS. Replacing a
    score invalidates the `score_inputs` flags that say a penalty is already inside it: on the
    committed ledger AUT-PROP-004 carried `blocked_with_evidence: True` beside `score: null`, and
    with a fresh base under that stale flag `apply_session_penalties` REMOVES a 90-point penalty the
    score never contained. So the pass clears `CHARGED_AGAINST_SCORE`, then calls
    `apply_session_penalties`, `apply_fruitless_attempts` and `apply_requires_trimcrae` on the newly
    scored rows ALONE. Each is written as a delta against its echoed input and is therefore a no-op
    on a row that already carries it, which is the property `test_a_score_must_derive_from_its_own_inputs`
    already binds; passing the subset also keeps rule 2's `by_id` from re-resolving the whole ledger.
    ⚠ A row naming a `prerequisite_of` parent is never in that subset — `_resolve` scores it from the
    parent whatever its own score was, and naming a parent is more specific evidence than sharing a
    route.
    ⭐ `age_factor` is the one echoed input the pass keeps and re-adds itself, exactly as `_resolve`
    does for the identical reason (AUT-PD-063): `apply_age_factor` writes the echo even on a row
    whose score is None while adding nothing to the score, so without `_own_age_bonus` the row would
    advertise a term its score does not contain — the one thing `_scores_are_not_evidence` promises
    never happens.

    ⛔ ASSIGNED ONCE, NEVER RE-DERIVED. Only a row whose score is None is touched, so from the next
    re-score on it behaves exactly like a row whose filer typed a number, and every downstream
    flag-guarded penalty stays single-applied. Re-deriving each run would overwrite a base those
    flags say has already been charged, which is the AUT-PD-063 ratchet with a new name.
    """
    terms = weights.get("terms") or {}
    floors = route_score_floor(entries)
    assigned: list[dict] = []
    for entry in entries:
        if entry.get("score") is not None:
            continue
        route = (entry.get("serves") or {}).get("route")
        floor = floors.get(route)
        if floor is None:
            # ⛔ RESIDUE. Not scorable from anything the graph holds, so it gets NO number here — an
            # invented one would be worse than the invisibility it cures (CLAUDE.md §4). `health.py`'s
            # `scores_are_reachable` counts these rows and names what would settle each.
            continue
        inputs = entry.get("score_inputs")
        if isinstance(inputs, dict):
            for flag in CHARGED_AGAINST_SCORE:
                inputs.pop(flag, None)
        entry["score"] = round(floor + _own_age_bonus(entry, terms), 2)
        entry["_score_basis"] = (
            f"inherited from the lowest-scoring derived row on {route} ({floor}) plus this row's own "
            "age bonus, then charged its own penalties — the graph does not express this row, so it "
            "is worth no more than the least the graph already values on the same route (AUT-PD-143)"
        )
        entry["_score_inherited_from_route"] = route
        assigned.append(entry)
    if assigned:
        apply_session_penalties(assigned, weights)
        apply_fruitless_attempts(assigned, weights)
        apply_requires_trimcrae(assigned, weights)
    return entries


def _own_age_bonus(entry: dict, terms: dict) -> float:
    """What `apply_age_factor` has already put into THIS row's score, so an assignment can put it
    back. AUT-PD-063.

    ⚠ READ DEFENSIVELY, LIKE `apply_age_factor`'s OWN READ OF THE SAME NUMBER: a missing or
    malformed weights file must disable the anti-starvation term rather than crash the ranker
    (`test_an_unreadable_saturation_disables_the_term_rather_than_dividing_by_zero`). This is a
    second READER of the weight, not a second copy of it — the value still lives only in
    `priority-weights.json`.
    """
    w = ((terms.get("age") or {}).get("weight"))
    f = (entry.get("score_inputs") or {}).get("age_factor")
    if not isinstance(w, (int, float)) or not isinstance(f, (int, float)) or isinstance(f, bool):
        return 0.0
    return w * f


def apply_session_penalties(entries: list[dict], weights: dict) -> list[dict]:
    """Score adjustments that depend on SESSION state, so they cannot run inside build_entries().

    Two rules, both found by cycle CYC-0001 running for real rather than by reading the code:

    1. ⛔ AN EVIDENCED BLOCK MUST STAND DOWN. The top item was established as blocked, with the
       evidence recorded — and still scored 195 and still sorted first, so the next cycle would have
       re-derived the identical block, and the one after that, every four hours forever. (The
       UNevidenced kind is a different animal and is already handled by its own clamp, which turns it
       into a free re-test — CLAUDE.md §0.)
    2. ⭐ A PREREQUISITE INHERITS WHAT IT UNBLOCKS. An entry naming `prerequisite_of` takes its
       parent's score plus a hair, so it sorts immediately above it. Without this the work that would
       clear a block is invisible to the driver and the blocked item stays blocked indefinitely.
    """
    by_id = {e["id"]: e for e in entries}
    terms = weights["terms"]  # same binding build_entries uses, so every weight is read one way
    penalty = terms["blocked_with_evidence"]["weight"]
    for entry in entries:
        # ⛔ KEYED ON THE EVIDENCE, NOT ON `state`. The state field is re-derived from the graph
        # every re-score, so a session writing state="blocked" saw it reverted to "queued" on the
        # very next run and the penalty never fired — the item stayed at the top of the queue with
        # its own block recorded underneath it. The recorded observation IS the block.
        evidenced = bool(str(entry.get("blocked_evidence") or "").strip())
        # ⛔⛔ IDEMPOTENT, AND IT WAS NOT (AUT-PROP-036, measured 2026-08-28). This was
        # `score = score + penalty` applied on EVERY re-score. For a DERIVED row that is correct —
        # `build_entries` rebuilds its base from `systems/graph` each run, so the term lands on a
        # fresh number. For a HAND-FILED row `merge()` carries the previous `score` forward, by
        # design, because the graph cannot rebuild it — so the penalty compounded. Traced through 25
        # commits of `research-ledger.json`: AUT-PROP-026 went -1344.0 → -2506.8 in one day, -90.0
        # per re-score, while the derived AUT-049 sat unmoved at 117.0 across the same eight runs.
        # That contrast is the observation that discriminates a wrong TERM from a reused BASE.
        # ⭐ THE FLAG IN `score_inputs` IS THE STATE, AND IT IS ALREADY WRITTEN AND ALREADY CARRIED:
        # a derived row's `score_inputs` is rebuilt fresh by `build_entries` (so the flag is absent
        # and the penalty applies), a hand-filed row's is carried by `merge()` (so the flag is
        # present and the penalty is not applied twice). No new field, and the toggle runs BOTH
        # ways — clearing the evidence removes the penalty instead of leaving it baked in forever.
        applied = bool((entry.get("score_inputs") or {}).get("blocked_with_evidence"))
        if evidenced != applied and entry.get("score") is not None:
            entry["score"] = round(entry["score"] + (penalty if evidenced else -penalty), 2)
        if evidenced:
            # ⛔ `setdefault`, BECAUSE A HAND-FILED ENTRY HAS NO SCORE INPUTS AND NEVER DID.
            # `score_inputs` is the DERIVED scorer's audit trail: `build_entries` writes it for
            # the rows it computes from systems/graph, and `merge()` deliberately carries
            # hand-filed rows through untouched (its docstring: "the ledger's own `_role` says a
            # session may add one the graph cannot express"). This line then indexed it on every
            # merged row and `priority.py` DIED — `KeyError: 'score_inputs'` — on the committed
            # ledger, where 47 of 124 entries are hand-filed. ⚠ Measured 2026-08-27 on a clean
            # tree at origin/main, so it was not a working-tree artifact; nothing caught it
            # because no gate ran the ranker (AUT-PD-018, the same day, the same shape).
            # ⭐ AND THE DICT IS CREATED EMPTY RATHER THAN FILLED WITH DEFAULTS. Giving a
            # hand-scored row a full set of zeroed inputs would make it look computed — a
            # populated field that is not a measured one (CLAUDE.md §4) — and the arithmetic
            # printed beside it would be arithmetic nobody did. What goes in is only the flag
            # this function actually observed.
            _score_inputs(entry)["blocked_with_evidence"] = True
        elif applied:
            # The evidence was cleared. Drop the flag with the penalty it accounted for, so the row
            # is again a fixed point of this function rather than carrying a term nothing explains.
            (entry.get("score_inputs") or {}).pop("blocked_with_evidence", None)

    bonus = weights["prerequisite_bonus"]["value"]

    # ⛔⛔ PARENTS FIRST, AND THE ASSIGNED SET IS THE OTHER HALF OF THE FIX (AUT-PROP-036).
    # This loop used to walk `entries` in list order and read `parent["score"]` wherever it found
    # it. Two things then went wrong together on a CHAIN — a prerequisite whose parent is itself a
    # prerequisite, which the committed ledger has four of:
    #   (1) ORDER. A child processed before its parent inherited the parent's PREVIOUS value, so
    #       the chain resolved to a different number depending on where the rows happened to sort.
    #   (2) THE PENALTY ADD-BACK BECAME A LIE. `base = parent.score + 90` is right only while the
    #       parent's score actually CONTAINS one application of the evidenced-block penalty. A row
    #       this loop has just re-assigned holds `grandparent_base + bonus`, which contains none —
    #       yet its `score_inputs.blocked_with_evidence` flag is still set, so +90 was added to a
    #       penalty that was not there. Measured 2026-08-28 on the committed ledger: AUT-PROP-021
    #       and AUT-PROP-022 moved 196.9 → 286.9 and 196.0 → 286.0 on a re-score that changed no
    #       evidence, which would have put two hand-filed rows 90 points clear of every route in
    #       the portfolio.
    # ⭐ RESOLVE DEPTH-FIRST WITH A CYCLE GUARD, and take a re-assigned parent's score as ALREADY
    # pre-penalty. `admissibility.write_verdict` is what caught this: the row was not a fixed point
    # of its own pipeline, which is the whole signature that module exists to name.
    assigned: set[str] = set()
    resolving: set[str] = set()

    def _resolve(entry: dict) -> None:
        eid = entry.get("id")
        parent_id = entry.get("prerequisite_of")
        parent = by_id.get(parent_id) if parent_id else None
        if parent is None or parent.get("score") is None:
            return
        if eid in assigned or eid in resolving:
            return  # already done, or this is a `prerequisite_of` cycle — leave the score alone
        resolving.add(eid)
        if parent.get("prerequisite_of"):
            _resolve(parent)
        resolving.discard(eid)
        # Inherit the parent's PRE-penalty value: the prerequisite is worth what the parent is worth
        # once unblocked, which is the whole reason to do it.
        # ⚠ A hand-filed prerequisite naming a hand-filed parent reaches here with no `score_inputs`
        # on either. `paper-hardening` §8b.2 measured six of eleven list-scoped fixes missing this.
        parent_inputs = parent.get("score_inputs") or {}
        # ⛔⛔ EVERY BLOCKED ROW'S SCORE NOW CARRIES EXACTLY ONE PENALTY, ASSIGNED OR NOT — so this
        # reads the flag and nothing else. It used to read `... and parent_id not in assigned`,
        # because an ASSIGNED parent's freshly-written score genuinely did not contain a penalty:
        # the assignment below overwrote it. That is the half of AUT-PD-063 fixed here — see the
        # re-application four lines down — and once the penalty survives the assignment, exempting
        # assigned parents would subtract a penalty that IS there.
        base = parent["score"] - (penalty if parent_inputs.get("blocked_with_evidence") else 0)
        # ⭐ THE ROW'S OWN AGE SURVIVES THE ASSIGNMENT. `apply_age_factor` runs BEFORE this function
        # (see `build_ledger`) so a parent's wait reaches its child; an assignment that dropped the
        # child's own wait would leave `score_inputs["age_factor"]` advertising a term the printed
        # score does not contain — the one thing `_scores_are_not_evidence` promises never happens.
        entry["score"] = round(base + bonus + _own_age_bonus(entry, terms), 2)
        # ⛔⛔ AND THE ROW THEN ANSWERS FOR ITS OWN BLOCK. AUT-PD-063, measured 2026-08-28: the
        # assignment above is what rule 1 writes to, so a row that is BOTH a prerequisite AND
        # blocked-with-evidence had its -90 silently overwritten while `score_inputs` went on
        # saying `blocked_with_evidence: true`. On the committed ledger that left AUT-PROP-018,
        # -019, -020, -040 and -042 — five rows carrying their own recorded block — at ranks 6, 7,
        # 9, 11 and 12 of a queue rule 1 exists to remove them from, and
        # `test_an_evidenced_block_drops_out_of_the_queue` watched it happen because it checks only
        # the top THREE. Inheriting is what the row is WORTH; the block is what can be DONE about it
        # this cycle. They are different questions and the row answers both.
        if str(entry.get("blocked_evidence") or "").strip():
            entry["score"] = round(entry["score"] + penalty, 2)
        entry["_score_basis"] = f"inherited from {parent_id} (+{bonus}) — it is the work that unblocks it"
        assigned.add(eid)

    for entry in entries:
        _resolve(entry)
    return entries


# ═════════════════════════════════════════════════════════════════════════════════════════════
# AUT-PD-014 — PROGRESS-AWARE RETRY BUDGET, PORTED FROM research/modalities/work_ledger.py
# ═════════════════════════════════════════════════════════════════════════════════════════════
# ⛔⛔ THE DEFECT THIS CLOSES, DIAGNOSED BY A PRIOR CYCLE AND CONFIRMED HERE BEFORE CHANGING
# ANYTHING. Three things were true of this file and of research-ledger.json's schema simultaneously:
#   1. `score_inputs["fruitless_attempts"]` was hardcoded to 0 in `build_entries` — never computed —
#      even though `priority-weights.json` already declares a real weight for it.
#   2. The ledger's `attempts` (a bare int) is incremented in exactly ONE place —
#      `release_stale_claims`, on an EXPIRED LEASE — so it counts sessions that died holding a claim,
#      never sessions that claimed a row, worked it seriously, and released it having learned
#      nothing new. This module's own comment already said as much: "a route could be retried
#      forever and the scorer's fruitless_attempts penalty could never fire."
#   3. Nothing anywhere decremented or enforced `retry_budget`. It was set to a literal `3` in
#      `build_entries` and never moved again, for any row, ever.
#
# ⭐ THE MODEL: research/modalities/work_ledger.py's `Entry.fruitless_attempts()` — a DIFFERENT
# ledger, for GPU/modality work, whose schema already carries this correctly. Its idea, ported
# rather than copied (the two ledgers' schemas differ — that ledger's `attempts` IS already a list
# of per-dispatch records; this one's `attempts` is a bare int with an unrelated meaning, so a NEW
# field is used here rather than repurposing one that already means something else):
#
#     an attempt is FRUITLESS iff the evidence fingerprint it was DISPATCHED against is still the
#     CURRENT fingerprint. Count backwards through the dispatch history and stop at the first
#     attempt whose recorded fingerprint differs — "a dispatch that worked costs nothing."
#
# WHAT "EVIDENCE" MEANS FOR ONE OF THIS LEDGER'S ROWS, stated once so a reader can check the
# arithmetic: `last_evidence_utc` and `blocked_evidence`, concatenated. Those are exactly the two
# fields step 9 of the `research-loop` cycle contract requires a session to write back when it
# OBSERVES something — "set the new state and `last_evidence_utc`... and for a failure the
# *diagnostic*" (which lands in `blocked_evidence`, per `apply_session_penalties`'s own comment:
# "the recorded observation IS the block"). A row whose fingerprint has not moved since it was last
# dispatched has, by construction, produced nothing a reader could point at as new.
#
# THE STAMP HAS TO HAPPEN AT CLAIM TIME, NOT LAZILY LATER. `claim.py`'s `apply_claim()` appends
# `{"utc": <claimed_utc>, "fingerprint_at_dispatch": evidence_fingerprint(entry)}` to a NEW
# `dispatch_log` list field the moment a claim lands — BEFORE any work happens — because the only
# fingerprint that is honest to compare against later is the one the row carried at the instant of
# dispatch. Recomputing it lazily, the next time this module happens to notice the claim, would
# sometimes capture the POST-work fingerprint and call a genuine advance fruitless by construction.
# `dispatch_log` survives every re-score via `merge()`'s forward-compat `setdefault` loop with no
# change needed there — a key `build_entries` never sets on a freshly-derived row is exactly what
# that loop exists to carry forward from the row's own prior committed state.
#
# ⛔⛔ THE HONEST CAVEAT THIS LEDGER ITEM ASKS TO BE PRESERVED, NOT LOST: a progress-aware counter
# WOULD NOT have penalised AUT-PROP-002, which moved `last_evidence_utc` every cycle — its
# fingerprint changes on every real cycle, so its fruitless streak resets to 0 every time, exactly
# as intended. **This defect did not cause the three-cycle stall CYC-0015 found; it is a separate
# governance instrument that was inert, and fixing it here does not retroactively explain that
# stall.** What this DOES fix: a row that is claimed and released, over and over, with nothing new
# ever recorded about it, now decays its own priority and eventually stops being offered as ready
# work — instead of being retried by automation forever, silently, which is the defect actually
# named above.
#
# WHAT THIS DELIBERATELY DOES NOT DO (scoped down, named rather than silently skipped):
#   * `claim.py`'s `SUSPENDED` verdict (a push/merge race exhausting its attempts) is a DIFFERENT
#     terminal state for a different reason and is not touched or conflated with this one.
#   * `claim.py` is NOT taught to refuse claiming a budget-exhausted row. `continuity.py`'s `ready()`
#     already excludes it (see `_retry_budget_spent` there), which is the same "a session should not
#     be OFFERED this row" property, reached through the read side rather than the write side. If a
#     session claims one anyway (by id, deliberately, bypassing `ready()`) that is a human decision
#     this module does not need to prevent.
#   * `research-ledger.json`'s committed content is not migrated. `dispatch_log` is read everywhere
#     as `entry.get("dispatch_log") or []`, so an existing row with no such key behaves exactly as a
#     row that has never been dispatched under the new mechanism — correct, and needs no backfill.


def evidence_fingerprint(entry: dict) -> str:
    """What "the evidence changed" MEANS for one research-ledger.json row. See the module-section
    docstring above for why these two fields and not `attempts`, `owner` or `score`."""
    return f"{entry.get('last_evidence_utc')}|{entry.get('blocked_evidence')}"


def fruitless_attempts_count(entry: dict) -> int:
    """How many of this row's MOST RECENT dispatches produced no new evidence.

    Ported from `research/modalities/work_ledger.py:Entry.fruitless_attempts` — counts backwards
    through `dispatch_log` and stops at the first attempt whose recorded fingerprint differs from
    the row's CURRENT one. A row never dispatched (`dispatch_log` absent or empty) scores 0, never
    an error — the common case, and it must not look penalised for having simply never been tried.
    """
    current = evidence_fingerprint(entry)
    n = 0
    for attempt in reversed(entry.get("dispatch_log") or []):
        if not isinstance(attempt, dict) or attempt.get("fingerprint_at_dispatch") != current:
            break
        n += 1
    return n


def apply_fruitless_attempts(entries: list[dict], weights: dict) -> list[dict]:
    """Feed `priority-weights.json`'s `fruitless_attempts` term from real history, and recompute
    `retry_budget` as the ceiling minus that count — the field `handoff.py:top_items` and
    `health.py:c_queue_is_takeable` already read as `> 0` and were, until now, never given a real
    number to read.

    ⛔ CLOSED ROWS ARE NEVER TOUCHED, mirroring `apply_age_factor`'s
    `test_a_closed_row_never_ages_upward` — a `done`/`abandoned`/`superseded` row's `retry_budget`
    is not this function's business.

    ⭐ THE SCORE TERM IS APPLIED AS A DELTA AGAINST THE PREVIOUSLY-ECHOED INPUT, exactly like
    `apply_age_factor`, and for the identical reason: a DERIVED row's `score_inputs` is rebuilt fresh
    every run by `build_entries` (so `prev` is always 0 there and the full term lands cleanly), while
    a HAND-FILED row's `score` and `score_inputs` are carried forward unchanged by `merge()` — adding
    the full term again on top of an already-applied one would compound it every re-score, which is
    the exact AUT-PROP-036 shape `apply_age_factor`'s own docstring measures in detail.

    ⛔ `retry_budget` IS OVERWRITTEN, NOT DECREMENTED, and that is deliberate: it is set fresh each
    run to `max(0, DEFAULT_RETRY_BUDGET - fruitless_attempts_count(entry))`, a pure function of
    `dispatch_log`. An incrementally-decremented counter could drift from the history it is supposed
    to summarise (double-decrementing on a re-score, or under-decrementing after a lost write);
    recomputing it fresh cannot drift, by construction — the same reasoning `age_factor` and
    `fruitless_attempts` in `score_inputs` already rely on.
    """
    w = ((weights.get("terms") or {}).get("fruitless_attempts") or {}).get("weight")
    for e in entries:
        if (e.get("state") or "queued") in ("done", "abandoned", "superseded"):
            continue
        n = fruitless_attempts_count(e)
        prev = (e.get("score_inputs") or {}).get("fruitless_attempts")
        prev = prev if isinstance(prev, (int, float)) and not isinstance(prev, bool) else 0
        if n or prev:
            _score_inputs(e)["fruitless_attempts"] = n
        if isinstance(w, (int, float)) and isinstance(e.get("score"), (int, float)) and n != prev:
            e["score"] = round(e["score"] + w * (n - prev), 2)
        e["retry_budget"] = max(0, DEFAULT_RETRY_BUDGET - n)
    return entries


def apply_requires_trimcrae(entries: list[dict], weights: dict) -> list[dict]:
    """Feed the `blocked_on_human` term from the ENTRY's own `requires_trimcrae`, not only from
    `systems/graph/routes.json` (AUT-PD-127).

    ⛔⛔ THE DEFECT, MEASURED ON 86098c2 BEFORE ANY CODE WAS CHANGED. Three places answer the one
    question "may a cycle take this row?" and only ONE read the field: `continuity.py`'s
    `_why_not_ready` refuses such a row outright, while this module's `_blocked_on_human` reads
    routes.json alone and `handoff.py`'s `_takeable` did not consider it at all. So the -25 weight
    written for exactly this case — its own `why` in `priority-weights.json` reads "The loop cannot
    advance it this cycle" — appeared in the `score_inputs` of 0 of the 12 rows declaring the field,
    and the re-scored queue's first EIGHT rows were all acts reserved for trimcrae by CLAUDE.md §3
    (AUT-046 199.0 down to AUT-073 172.0), the first takeable row being AUT-025 at 152.0. A fresh
    cycle reading that queue top-down is pointed at eight rows it must refuse before reaching work.

    ⭐ WHY IT IS A POST-MERGE PASS AND NOT A TERM IN `build_entries`, which is where the route half
    of this predicate lives. `build_entries` reads only `systems/graph` (its own docstring says so),
    and `requires_trimcrae` is a property of a LEDGER ROW — a route legitimately has several next
    steps of which only one is his act, and hand-filed rows like AUT-PROP-041 serve no route at all.
    The field is therefore unreachable at derive time, which is the identical constraint
    `apply_fruitless_attempts` documents for `dispatch_log`, and this follows that solution rather
    than inventing a second one.

    ⭐ APPLIED AS A DELTA AGAINST THE PREVIOUSLY-ECHOED INPUT, exactly like `apply_age_factor` and
    `apply_fruitless_attempts`, and for the same reason: a DERIVED row's `score_inputs` is rebuilt
    fresh each run (so `prev` is the route-derived verdict and the term lands once), while a
    HAND-FILED row's score and inputs are carried forward unchanged by `merge()`. The value written
    is the OR of the two sources — a row already blocked on a human via routes.json stays blocked —
    and once True the delta is 0, so the pipeline remains the fixed point
    `test_a_score_must_derive_from_its_own_inputs` asserts it is.

    ⛔ IT PENALISES, IT DOES NOT HIDE. -25 is deliberately not -inf: `priority-weights.json` says the
    row "must stay visible enough to be escalated", and CLAUDE.md §3 trigger 5 depends on a finished
    paper still being findable in the queue. Dropping such rows from the RANKING would break the one
    escalation path that matters; `handoff.py` drops them from what is HANDED to a successor and
    names them instead, which is a different question with a different answer.
    """
    w = ((weights.get("terms") or {}).get("blocked_on_human") or {}).get("weight")
    for e in entries:
        if not e.get("requires_trimcrae"):
            continue
        inputs = _score_inputs(e)
        prev = bool(inputs.get("blocked_on_human"))
        if prev:
            continue
        inputs["blocked_on_human"] = True
        if isinstance(w, (int, float)) and isinstance(e.get("score"), (int, float)):
            e["score"] = round(e["score"] + w, 2)
    return entries


def release_stale_claims(entries: list[dict], weights: dict, interval_h, now=None) -> list[dict]:
    """A claim is a LEASE. Expire it, or one dead cycle parks an item forever.

    ⛔⛔ THIS IS THE STALL THAT ALMOST SHIPPED, AND IT WAS ALREADY HAPPENING WHEN IT WAS FOUND.
    `merge()` carries `owner` across every re-score — correctly, so a claim survives step 3 of the next
    cycle. But nothing ever CLEARED one. CYC-0003 claimed AUT-PROP-002, completed, and left the claim
    standing; the ledger showed it owned by a cycle that no longer existed. The next driver would read
    "someone is working on this", skip the queue's top item, and take something lower — silently, every
    four hours, forever. A cycle KILLED MID-ITEM produces exactly the same state, and that version is
    worse because nothing announces it.

    ⭐ A LEASE MAKES THE FAILURE SELF-HEALING RATHER THAN MERELY DETECTABLE. An alarm on a stuck claim
    would still need a human. An expiry needs nobody.

    ⚠ AN OWNER WITH NO `claimed_utc` IS STALE IMMEDIATELY. It cannot be aged, and an un-releasable claim
    is worse than an item done twice — the work is idempotent, the stall is not. Fail toward releasing.
    """
    now = now or _utcnow()
    periods = weights["claim_lease"]["periods"]
    hours = (interval_h if interval_h else 4.0) * periods
    for entry in entries:
        owner = entry.get("owner")
        if not owner:
            continue
        stamped = _parse_utc(entry.get("claimed_utc"))
        age_h = None if stamped is None else (now - stamped).total_seconds() / 3600.0
        if stamped is not None and age_h < hours:
            continue
        entry["owner"] = None
        entry["claimed_utc"] = None
        if entry.get("state") == "running":
            entry["state"] = "queued"
        entry["attempts"] = int(entry.get("attempts") or 0) + 1
        entry["lease_released"] = (
            f"claim by {owner} released "
            + ("(never stamped with claimed_utc, so it could not be aged)"
               if stamped is None else f"after {age_h:.1f} h, past the {hours:.0f} h lease")
            + ". A claim is a lease, not a deed — see priority-weights.json claim_lease.")
    return entries


def build_ledger() -> dict:
    weights = load_weights()
    existing = load_existing()
    interval_h = _cycle_interval_hours()
    entries = release_stale_claims(merge(build_entries(weights), existing), weights, interval_h)
    # ⭐⭐ AGE RUNS FIRST — A DELIBERATE DECISION, MEASURED 2026-08-28 (AUT-PD-063). Rule 2 of
    # `apply_session_penalties` ASSIGNS a prerequisite's score from what its parent is worth, so
    # anything added to the parent AFTER that assignment is invisible to the child. With age applied
    # last, a starved parent climbed points the only row able to clear it never saw: on the committed
    # ledger AUT-049 aged to +12.0 while AUT-PROP-018 — the single path to it — got only its own
    # +0.86, which drops the prerequisite BELOW the item it unblocks the moment that item's own block
    # penalty stops being erased. You cannot take a blocked row, so raising it buys nothing unless
    # its prerequisite rises with it; ageing first is what makes the wait bonus flow down the chain.
    # ⚠ THE ROW'S OWN AGE IS NOT LOST TO THE ASSIGNMENT — `apply_session_penalties` re-adds it from
    # the `age_factor` echoed in `score_inputs`, so the printed inputs still re-derive the score.
    # ⛔ THE ANTI-STARVATION TERM MUST RUN BEFORE THE SORT, or it is dead
    # code — the defect class this repository has paid for repeatedly (`subagent_width` governed
    # nothing for a fortnight because no code read it; the census lane's exempt flag; the watchdog
    # wired to an env var that does not exist). Its own test asserts this call site exists.
    entries = apply_age_factor(entries, weights)
    entries = apply_session_penalties(entries, weights)
    # ⛔ AUT-PD-014, DELIBERATELY PLACED AFTER `apply_session_penalties` AND NOT ALONGSIDE
    # `apply_age_factor` ABOVE IT, EVEN THOUGH BOTH ARE PER-ROW DECAY TERMS. AUT-PD-063 (immediately
    # above) had to teach `apply_session_penalties`'s prerequisite ASSIGNMENT to explicitly re-add
    # the child's own age bonus and re-apply its own blocked_with_evidence penalty, because that
    # assignment OVERWRITES `entry["score"]` and would otherwise erase a term applied before it ran.
    # Running `apply_fruitless_attempts` before the assignment would reproduce the identical hazard
    # for THIS term the same day it was fixed for the other two, and fixing it would mean editing
    # `_resolve()`'s assignment formula — the exact code AUT-PD-063 just hardened. Running it AFTER
    # instead means it is applied on top of the assignment and nothing after it can overwrite it, at
    # the honest cost that a prerequisite inherits its parent's fruitless-attempts decay one re-score
    # late rather than in the same cycle the parent's decay is computed. Retry-budget exhaustion needs
    # `DEFAULT_RETRY_BUDGET` dispatches to accrue, so a one-cycle lag here is a defensible trade
    # against destabilising machinery fixed the same day this was written — scoped down deliberately,
    # not an oversight.
    entries = apply_fruitless_attempts(entries, weights)
    # ⛔ AUT-PD-127, AND IT MUST RUN BEFORE THE SORT OR IT IS DEAD CODE — the defect class this
    # repository has paid for repeatedly (`subagent_width` governed nothing for a fortnight because
    # no code read it). It is placed alongside `apply_fruitless_attempts` and after
    # `apply_session_penalties` for that function's stated reason: rule 2 of the penalties pass
    # ASSIGNS a prerequisite's score from its parent's, overwriting anything applied before it.
    entries = apply_requires_trimcrae(entries, weights)
    # ⛔ AUT-PD-143 RUNS LAST, AND "LAST" IS A MEASUREMENT, NOT A PREFERENCE — see
    # `apply_route_inheritance`'s docstring for the run that decided it. It reads the DERIVED rows'
    # finished scores, so it must sit downstream of every pass that moves one. ⛔ AND IT IS STILL
    # BEFORE THE SORT, or it is dead code — the defect class this repository has paid for repeatedly
    # (`subagent_width` governed nothing for a fortnight because no code read it). Its own test
    # asserts this call site exists.
    # ⭐ AND IT RUNS BEFORE `score_rank` RATHER THAN CHANGING IT. AUT-PD-050 (immediately upstream)
    # settled that an unscored row sorts LAST and said the fix for a starved row is a `score`,
    # never a change to that ordering. This is that fix: the ordering rule is untouched and the
    # rows simply stop being unscored.
    entries = apply_route_inheritance(entries, weights)
    entries.sort(key=lambda e: (score_rank(e),
                                str(e.get("serves", {}).get("route") or e["id"])))
    return {
        "_schema": "emc-research-ledger/1",
        "_role": (
            "The autonomy loop's work queue. GENERATED by research/autonomy/priority.py from "
            "systems/graph — re-run it rather than hand-editing a score. A session may add an "
            "entry the graph cannot express; it may not edit a `score`. ⛔ AN ENTRY A SESSION ADDS "
            "MUST CARRY A `score` AND A `_score_basis` (or a `prerequisite_of`, which derives one "
            "from the row it unblocks): a row with no score is pinned BELOW every scored row by the "
            "sort and no ranking term can reach it — including the anti-starvation age factor, "
            "which is the one term meant to rescue exactly these rows. See `n_unscored`."
        ),
        "_owner": "research/manuscripts/program/emc-autonomy-architecture.md#3--layer-b--the-queue-and-how-it-ranks-work",
        "_generated_by": "python3 research/autonomy/priority.py --write",
        "_scores_are_not_evidence": (
            "A score orders work; it asserts nothing about the science. Every input is echoed "
            "in score_inputs so a reader can check the arithmetic against the graph."
        ),
        "n_by_kind": _count(entries, "kind"),
        "n_by_state": _count(entries, "state"),
        "n_clamped": sum(1 for e in entries if "clamp" in e),
        # ⛔⛔ AUT-PD-050. `admissibility.py --report` could already grade a row `unscored` and did —
        # 97 of 260 on 2026-08-28 — but that grade was a constant nothing counted anywhere a reader
        # looks, its own report's closing sentence explained `admitted` and `unaccounted` and omitted
        # the LARGEST bucket, and nothing in preflight or CI ran it. The population is therefore a
        # DERIVED number in the artifact itself, beside the other counts, so it cannot go back to
        # being a thing you have to know to go looking for.
        "n_unscored": sum(1 for e in entries if e.get("score") is None),
        "n_unscored_open": sum(1 for e in entries
                               if e.get("score") is None
                               and (e.get("state") or "queued") not in CLOSED_STATES),
        "entries": entries,
    }


def _count(entries: list[dict], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for entry in entries:
        out[str(entry[key])] = out.get(str(entry[key]), 0) + 1
    return dict(sorted(out.items()))


#: How an UNSCORED row renders wherever a score would print. ⛔ NOT `0.0`, AND THAT IS THE WHOLE
#: POINT (AUT-PD-050). `continuity.py` printed `e.get("score", 0)` for these rows, so 91 rows with
#: no score at all rendered as a computed-looking `0.0` in the list the driver reads to pick work —
#: CLAUDE.md §4's "a populated field is not a measured one", in the one view that chooses the work.
NO_SCORE = "unscored"


def _table(entries: list[dict], limit: int) -> str:
    lines = [f"{'score':>7}  {'kind':<10} {'cost':<9} {'route':<28} what"]
    lines.append("-" * 110)
    for entry in entries[:limit]:
        # AUT-PD-046: a row missing `what` (e.g. a freshly-filed proposal nobody has described yet)
        # must degrade the table, never crash the whole --limit view for every other row alongside it.
        # ⚠ `what` is read through `str(... or ...)` rather than `get(key, default)` because a row
        # carrying an explicit `"what": null` is not a row missing the key, and only the first of
        # those two was handled. AUT-PD-143 found this concurrently with AUT-PD-050 below, which
        # owns the account of the same defect on the other three cells — one fact, one place.
        what = str(entry.get("what") or "(no description)").replace("\n", " ")
        if len(what) > 52:
            what = what[:49] + "..."
        # ⛔⛔ AUT-PD-050, AND IT IS AUT-PD-046'S OWN SIBLING LINE — the defect that comment describes,
        # in the same statement, left unfixed because only `what` was missing from the ten rows that
        # prompted it. Measured 2026-08-28 on the committed ledger: 97 of 260 rows carry NO `score`,
        # and `entry['score']:>7.1f` raises `TypeError: unsupported format string passed to
        # NoneType.__format__` on the first one. The sort pins every unscored row to the BOTTOM
        # (`-1e9` in `build_ledger`), so they occupy ranks 164-260 and the default `--limit 20` never
        # reaches them: `--limit 300` — the view a reader uses precisely BECAUSE they are looking for
        # the starved rows — is the invocation that dies. A view that crashes only when pointed at
        # the forgotten work is how the work stays forgotten.
        # ⚠ AND `serves.route` IS THE SAME LINE'S THIRD BARE INDEX, unfixed for the same reason: nine
        # committed rows carry no `serves.route`, and each would have been the NEXT crash the moment
        # the score one was fixed alone (`paper-hardening` §8b.2's one-of-a-pair class).
        score = entry.get("score")
        cell = f"{score:>7.1f}" if isinstance(score, (int, float)) else f"{NO_SCORE:>7}"
        serves = entry.get("serves")
        route = (serves or {}).get("route") or "(no route)"
        lines.append(
            f"{cell}  {str(entry.get('kind') or '?'):<10} {str(entry.get('cost_class') or '?'):<9} "
            f"{route:<28} {what}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true", help="print the ledger as JSON")
    parser.add_argument("--write", action="store_true", help="write research-ledger.json")
    parser.add_argument("--explain", metavar="ROUTE_ID", help="show one route's arithmetic")
    parser.add_argument("--limit", type=int, default=20, help="rows in the table (default 20)")
    args = parser.parse_args(argv)

    ledger = build_ledger()
    entries = ledger["entries"]

    # ⛔⛔ A DUPLICATED ID IS INVISIBLE UNTIL A HUMAN OR A REBASE TRIPS OVER IT (AUT-PROP-013).
    # `AUT-PD-012` was issued twice, by two entirely different process defects, filed by SEQUENTIAL
    # cycles — so this is not a race, the max+1 derivation collides on its own — and it sat on
    # origin/main unnoticed because nothing in the loop ever read a ledger looking for one. Two
    # concurrent sessions did it again the same hour with AUT-PROP-009 and AUT-PROP-010.
    # ⭐ FOUR LINES, HERE, WOULD HAVE CAUGHT ALL THREE AT THE COMMIT THAT CREATED THEM. This is the
    # ledger's own tool: if the ranker will not read a ledger with two rows under one id, the
    # duplicate cannot survive to the next cycle's queue. `research/autonomy/tests` asserts the same
    # property against the committed file, and preflight gate 15 runs it.
    dups = ids.duplicate_ids(entries)
    if dups:
        for bad, n in sorted(dups.items()):
            print(f"⛔ ledger id {bad} is used {n} times — two different items under one identity, "
                  "so a receipt, a claim or an evidence pointer naming it is ambiguous",
                  file=sys.stderr)
        print("Allocate with research/autonomy/ids.py:next_entry_id(); do not renumber by eye.",
              file=sys.stderr)
        return 3

    if args.explain:
        match = [e for e in entries if e["serves"]["route"] == args.explain]
        if not match:
            print(f"no entry serving route {args.explain}", file=sys.stderr)
            return 2
        print(json.dumps(match[0], indent=2))
        return 0

    if args.write:
        # ⛔⛔ AUT-PD-037: this used to be `json.dump(ledger, fh, indent=2)` — `ensure_ascii`
        # defaults to `True`, so this "documented generator" would escape every ⛔ ⭐ ⚠ ★ and
        # em-dash in the file on its next run and rewrite all ~9,000 lines. `ledger_io.write_ledger`
        # is the one place the real, committed serialization is pinned; nothing here may type
        # `indent=`/`ensure_ascii=` again.
        ledger_io.write_ledger(LEDGER_FILE, ledger)
        print(f"wrote {LEDGER_FILE.relative_to(REPO)}: {len(entries)} entries, "
              f"{ledger['n_clamped']} clamped")
        return 0

    if args.json:
        print(json.dumps(ledger, indent=2))
        return 0

    print(_table(entries, args.limit))
    print()
    print(f"{len(entries)} entries · by kind {ledger['n_by_kind']} · {ledger['n_clamped']} clamped "
          f"· {ledger['n_unscored']} UNSCORED ({ledger['n_unscored_open']} of them open), which no "
          f"ranking term can order — see `_role`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
