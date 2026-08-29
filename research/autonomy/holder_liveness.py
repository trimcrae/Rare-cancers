#!/usr/bin/env python3
"""IS THE WORKER HOLDING THIS LEASE STILL ABLE TO BE RUNNING AT ALL?

⛔⛔ MEASURED 2026-08-28T23:30Z (CYC-0072-2e57571a, AUT-PD-150). `session_01SVfJ6HmD2f5u4Z2TPwfTCG`
was SESSION_STATUS_ARCHIVED at 23:17:54Z, its own last summary reading *"landing loop attempt 2/4;
gate re-gating on b94d4bc1c; 4 seats finishing"*. Archiving RELEASES THE CONTAINER, so its four
seats provably could not be running — and they were still holding SEVEN open leases. `continuity.py`
counted those four dead seats plus one live cycle as 5 concurrent workers against a `subagent_width`
of 5, printed AT CAPACITY, and reported 109 rows as *"ready in the ledger and startable by nobody"*.
The whole loop was parked by workers that did not exist.

★ WHY NEITHER EXISTING INSTRUMENT COULD SEE IT, AND THEY FAIL DIFFERENTLY.
  * `stalled_holder.py` joins an open claim against its holder's TRANSCRIPT — a filesystem read, not
    a liveness ping, which is the right shape and the reason that module exists. But a transcript
    lives in the holder's OWN container, and archiving has released it. It requires `--tasks-dir`,
    and for a cross-session holder there is no directory to point it at. The case is not merely
    unmeasured by that design, it is UNMEASURABLE by it.
  * `priority.py:release_stale_claims` does expire leases, but on `claimed_utc` against
    periods × the cycle interval = 8.0 h. `continuity.py --leases` called all seven "within lease"
    at 0.8–1.2 h old, so the clock would not have freed them until ~06:45Z. Seven hours of a parked
    queue is not a race, it is an outage.

⭐ SO THE SIGNAL HAS TO COME FROM OUTSIDE THE FILESYSTEM, AND THIS MODULE DOES NOT GO AND GET IT.
That is deliberate and it is the house pattern, not a limitation worked around: `health.py` takes a
`--gates-verdict` and a `--stall-verdict` rather than reading Actions, and says in as many words that
it "has no network by design". Session status lives in the control plane, which no gate and no hook
can reach. **A driver observes it and hands the observation in; this module only ever arbitrates.**

⛔ IT REPORTS AND NEVER ACTS — `stalled_holder.py`'s rule, ARIS's rule, and the right one. Releasing
another worker's lease is a judgement, and a judgement made by a watchdog is how live work gets
thrown away. Releasing stays a human-or-driver act, and reaping stays `priority.py`'s job so there is
exactly one place a lease is actually released.

⛔⛔ AND IT FAILS CLOSED IN BOTH DIRECTIONS, WHICH IS THE ONLY SAFE DIRECTION HERE.
  * **No verdict for a session ⇒ `UNMEASURED`, never `alive` and never `dead`.** CLAUDE.md §4: an
    absent reading is not a reading of absence. `width_cap()` in `continuity.py` already fails this
    way — an unreadable dial must never buy a pass — and this is the same rule pointed at a holder.
  * **Only an explicitly TERMINAL status licenses the word DEAD.** `TERMINAL_STATUSES` below holds
    exactly the one status this repository has actually OBSERVED terminate a container. It is not
    copied from an API reference nobody here has read, and a status this module does not recognise
    is `UNKNOWN_STATUS`, never dead. Widening that set is a deliberate edit backed by an observation.

⚠ THE OWNER→SESSION MAPPING IS DERIVED, AND ITS FAILURE MODE IS NAMED. A lease owner is
`CYC-0072-2e57571a` or `SEAT-s1-ba841eee`: the trailing 8 characters are `ids.discriminator(...)` of
the worker's `CLAUDE_CODE_SESSION_ID`. Receipts carry BOTH that uuid (`session_id`) and the control
plane's own id (`ccr_session_id`), so the receipts are the join table. A holder whose session never
committed a receipt cannot be resolved — reported `UNRESOLVED`, which is a finding about the loop's
records rather than a verdict about the worker.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "research-ledger.json")
RECEIPTS = os.path.join(HERE, "receipts")

#: Open states, spelled the same way `continuity.py` and `stalled_holder.py` spell them.
OPEN_STATES = {None, "queued", "in_progress"}

#: ⛔ OBSERVED, NOT ENUMERATED. The one status this repository has watched release a container
#: (2026-08-28, session_01SVfJ6HmD2f5u4Z2TPwfTCG). Anything else is UNKNOWN_STATUS and buys nothing.
TERMINAL_STATUSES = {"SESSION_STATUS_ARCHIVED"}

#: A lease owner ends in `-<8 hex-ish chars>`: `ids.discriminator()` of the worker's session uuid.
_DISCRIMINATOR = re.compile(r"-([0-9a-f]{8})$", re.I)

ALIVE, DEAD, UNMEASURED, UNRESOLVED, UNKNOWN_STATUS = (
    "ALIVE", "DEAD", "UNMEASURED", "UNRESOLVED", "UNKNOWN_STATUS")

#: The only verdict that licenses releasing somebody else's lease.
RELEASABLE = {DEAD}


def discriminator_of(owner: str | None) -> str | None:
    """The 8-char session discriminator a lease owner carries, or None if it carries none."""
    m = _DISCRIMINATOR.search(owner or "")
    return m.group(1).lower() if m else None


def receipt_index(receipts_dir: str = RECEIPTS) -> dict[str, str]:
    """`{discriminator: ccr_session_id}`, built from committed receipts — the loop's join table.

    ⚠ A receipt whose `session_id` is prose rather than an id contributes NOTHING rather than a
    wrong row. Cycles really have written prose into that field (`session_reaper.py` was wrong in
    the dangerous direction for exactly this reason), so a value that is not a uuid is skipped.
    """
    out: dict[str, str] = {}
    if not os.path.isdir(receipts_dir):
        return out
    for name in sorted(os.listdir(receipts_dir)):
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(receipts_dir, name), encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            continue
        sid, ccr = d.get("session_id"), d.get("ccr_session_id")
        if not isinstance(sid, str) or not isinstance(ccr, str) or not ccr:
            continue
        m = re.match(r"^([0-9a-f]{8})-[0-9a-f]{4}-", sid, re.I)
        if not m:
            continue
        out.setdefault(m.group(1).lower(), ccr)
    return out


def _leases(ledger_path: str) -> list[tuple[str, str]]:
    try:
        with open(ledger_path, encoding="utf-8") as fh:
            entries = json.load(fh).get("entries", [])
    except (OSError, ValueError):
        return []
    return [(e.get("id"), e.get("owner")) for e in entries
            if e.get("state") in OPEN_STATES and e.get("owner")]


def load_verdict(path: str | None) -> dict[str, str]:
    """`{ccr_session_id: status}` from a driver's observation, or `{}` when none was supplied.

    Accepts `{"sessions": {"session_x": {"session_status": "..."}}}` or the flat
    `{"sessions": {"session_x": "STATUS"}}`, because the first is what `get_session` hands back and
    the second is what a human types.
    """
    if not path:
        return {}
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    sessions = raw.get("sessions", raw) if isinstance(raw, dict) else {}
    out: dict[str, str] = {}
    for sid, v in (sessions or {}).items():
        if isinstance(v, str):
            out[sid] = v
        elif isinstance(v, dict):
            st = v.get("session_status") or v.get("status")
            if isinstance(st, str):
                out[sid] = st
    return out


def arbitrate(verdict_path: str | None = None, ledger_path: str = LEDGER,
              receipts_dir: str = RECEIPTS, me: str | None = None) -> list[dict]:
    """One row per open lease: who holds it, which session that is, and whether it can be running.

    ⛔ `me` is EXCLUDED, for `continuity.own_cycle_owners`' reason: a worker is never blocked by
    itself, and this session's own session is by construction not archived.
    """
    verdict = load_verdict(verdict_path)
    index = receipt_index(receipts_dir)
    rows = []
    for entry_id, owner in _leases(ledger_path):
        if me and owner == me:
            continue
        disc = discriminator_of(owner)
        ccr = index.get(disc) if disc else None
        if ccr is None:
            state, detail = UNRESOLVED, (
                f"no committed receipt carries session_id starting {disc!r} together with a "
                "ccr_session_id, so this owner cannot be mapped to a session")
        elif ccr not in verdict:
            state, detail = UNMEASURED, (
                f"{ccr} was not in the supplied verdict" if verdict else
                "no --verdict was supplied, so nothing was observed about this holder")
        elif verdict[ccr] in TERMINAL_STATUSES:
            state, detail = DEAD, f"{ccr} is {verdict[ccr]} — its container is released"
        else:
            state, detail = (ALIVE if verdict[ccr].startswith("SESSION_STATUS_") else UNKNOWN_STATUS,
                             f"{ccr} is {verdict[ccr]}")
        rows.append({"id": entry_id, "held_by": owner, "discriminator": disc,
                     "ccr_session_id": ccr, "verdict": state, "detail": detail,
                     "releasable": state in RELEASABLE})
    rows.sort(key=lambda r: (not r["releasable"], r["held_by"] or "", r["id"] or ""))
    return rows


def dead_owners(rows: list[dict]) -> set[str]:
    """The holders a caller may discount from a capacity count. Only `DEAD` ever qualifies."""
    return {r["held_by"] for r in rows if r["releasable"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--verdict", metavar="PATH", default=None,
                    help="JSON a driver wrote from the control plane: "
                         '{"sessions": {"session_x": {"session_status": "..."}}}')
    ap.add_argument("--ledger", default=LEDGER)
    ap.add_argument("--receipts", default=RECEIPTS)
    ap.add_argument("--me", default=None, help="your own cycle id; never reported against yourself")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any open lease is held by a provably dead worker")
    args = ap.parse_args(argv)

    rows = arbitrate(args.verdict, args.ledger, args.receipts, args.me)
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        if not rows:
            print("no other worker holds a lease on an open row.")
        for r in rows:
            mark = {DEAD: "⛔ DEAD", ALIVE: "✅ alive", UNMEASURED: "🔎 unmeasured",
                    UNRESOLVED: "🔎 unresolved", UNKNOWN_STATUS: "🔎 unknown-status"}[r["verdict"]]
            print(f"   {mark:18s} {r['id']:12s} held by {r['held_by']}\n"
                  f"        {r['detail']}")
        n_dead = sum(1 for r in rows if r["releasable"])
        n_seen = sum(1 for r in rows if r["verdict"] in (ALIVE, DEAD))
        print(f"\n{len(rows)} lease(s): {n_dead} held by a provably dead worker, "
              f"{len(rows) - n_seen} not observed — and NOT OBSERVED IS NOT ALIVE.")
        if n_dead:
            print("⛔ A DEAD HOLDER'S LEASE IS LITTER: release it (`owner: null`) and the work is\n"
                  "   startable again. THIS MODULE DOES NOT DO THAT — releasing is a judgement, and\n"
                  "   `priority.py` stays the one place a lease is actually released.")
    return 1 if (args.check and any(r["releasable"] for r in rows)) else 0


if __name__ == "__main__":
    sys.exit(main())
