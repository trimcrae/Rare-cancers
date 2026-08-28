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

# Route state values that mean "this route is not itself dead". The route may still be
# blocked or parked — CLAUDE.md §0 is explicit that a blocked row is usually waiting on a
# free check, so blocked is emphatically not dead.
DEAD_WORK_STATES = {"dead"}
OPEN_CLOSURES = {"open", "", None}

# Endpoint outcome_potential values, from systems/graph/publications.json.
LIVE_OUTCOME = "live_positive"
NEGATIVE_OUTCOMES = {"negative_or_methods"}


def _load(name: str) -> Any:
    with (GRAPH / name).open() as fh:
        return json.load(fh)


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
                "state": "blocked" if (route.get("next") or {}).get("blocked_on") else "queued",
                "owner": None,
                "cost_class": cost_class,
                "cost_points_at": "research/compute/pricing.md",
                "blocked_by": (route.get("next") or {}).get("blocked_on") or None,
                "blocked_evidence": None,
                "retry_budget": 3,
                "attempts": 0,
                "last_evidence_utc": state.get("last_verified"),
                "score": round(score, 2),
                "score_inputs": inputs,
            }
        )

    entries = apply_clamps(entries, weights)
    entries.sort(key=lambda e: (-e["score"], e["serves"]["route"]))
    return entries


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
# States a session sets. `queued`/`blocked` are re-derived from the graph; these are not.
SESSION_STATES = {"running", "done", "abandoned"}


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
    used = set()
    for e in prior:
        try:
            used.add(int(str(e.get("id", "")).rsplit("-", 1)[-1]))
        except ValueError:
            pass
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
        if str(entry.get("blocked_evidence") or "").strip():
            if entry.get("score") is not None:
                entry["score"] = round(entry["score"] + penalty, 2)
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
                entry.setdefault("score_inputs", {})["blocked_with_evidence"] = True

    bonus = weights["prerequisite_bonus"]["value"]
    for entry in entries:
        parent_id = entry.get("prerequisite_of")
        parent = by_id.get(parent_id) if parent_id else None
        if parent is None or parent.get("score") is None:
            continue
        # Inherit the parent's PRE-penalty value: the prerequisite is worth what the parent is worth
        # once unblocked, which is the whole reason to do it.
        # ⚠ THE SIBLING OF THE LINE ABOVE, AND IT WOULD HAVE BEEN THE NEXT CRASH: a hand-filed
        # prerequisite naming a hand-filed parent reaches here with no `score_inputs` on either.
        # `paper-hardening` §8b.2 measured six of eleven list-scoped fixes missing exactly this.
        parent_inputs = parent.get("score_inputs") or {}
        base = parent["score"] - (penalty if parent_inputs.get("blocked_with_evidence") else 0)
        entry["score"] = round(base + bonus, 2)
        entry["_score_basis"] = f"inherited from {parent_id} (+{bonus}) — it is the work that unblocks it"
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
    entries = apply_session_penalties(entries, weights)
    entries.sort(key=lambda e: (-(e.get("score") if e.get("score") is not None else -1e9),
                                str(e.get("serves", {}).get("route") or e["id"])))
    return {
        "_schema": "emc-research-ledger/1",
        "_role": (
            "The autonomy loop's work queue. GENERATED by research/autonomy/priority.py from "
            "systems/graph — re-run it rather than hand-editing a score. A session may add an "
            "entry the graph cannot express; it may not edit a `score`."
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
        "entries": entries,
    }


def _count(entries: list[dict], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for entry in entries:
        out[str(entry[key])] = out.get(str(entry[key]), 0) + 1
    return dict(sorted(out.items()))


def _table(entries: list[dict], limit: int) -> str:
    lines = [f"{'score':>7}  {'kind':<10} {'cost':<9} {'route':<28} what"]
    lines.append("-" * 110)
    for entry in entries[:limit]:
        # AUT-PD-046: a row missing `what` (e.g. a freshly-filed proposal nobody has described yet)
        # must degrade the table, never crash the whole --limit view for every other row alongside it.
        what = entry.get("what", "(no description)").replace("\n", " ")
        if len(what) > 52:
            what = what[:49] + "..."
        lines.append(
            f"{entry['score']:>7.1f}  {entry['kind']:<10} {entry['cost_class']:<9} "
            f"{entry['serves']['route']:<28} {what}"
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
    print(f"{len(entries)} entries · by kind {ledger['n_by_kind']} · {ledger['n_clamped']} clamped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
