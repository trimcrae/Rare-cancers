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


def build_ledger() -> dict:
    entries = build_entries()
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
        what = entry["what"].replace("\n", " ")
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

    if args.explain:
        match = [e for e in entries if e["serves"]["route"] == args.explain]
        if not match:
            print(f"no entry serving route {args.explain}", file=sys.stderr)
            return 2
        print(json.dumps(match[0], indent=2))
        return 0

    if args.write:
        with LEDGER_FILE.open("w") as fh:
            json.dump(ledger, fh, indent=2)
            fh.write("\n")
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
