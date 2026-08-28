#!/usr/bin/env python3
"""WHICH FINISHED LOOP SESSIONS ARE SAFE TO ARCHIVE — the decision, as committed logic.

★★ WHY THIS EXISTS. Every cycle spawns or is spawned as a session, and nothing ever closed one.
Measured 2026-08-27 by trimcrae, who had to ask: of the 40 most recent sessions on the account, 32
were archived by hand, 7 were IDLE — finished cycles nobody closed — and 1 was running. At a 4-hour
cadence that is six new idle rows a day, forever, and the list is the thing a human actually looks
at. A loop that cannot clean up after itself makes its owner the janitor.

⛔⛔ THE ONE RULE THIS FILE IS BUILT AROUND: **ARCHIVING IS ONLY SAFE ONCE THE WORK IS ON `main`.**
Archiving releases the session's container. If that session's work never landed, archiving it turns
a recoverable problem into a lost one, and it does so silently — the row simply stops being there to
notice. So the test is never "is it finished?" but "is its work COMMITTED?", and the evidence is a
receipt reachable from the trunk. This is CLAUDE.md §7's branch-drift rule pointed at cleanup: a
session whose only artifact is on a branch nobody reads is exactly the session you must NOT close.

⚠ AND A SESSION WITH NO RECEIPT IS NOT AUTOMATICALLY GARBAGE. It may be a cycle that died holding
uncommitted work, which is a finding rather than litter. Those are reported as `keep` with a reason,
never archived, so that a human sees them instead of losing them.

⭐ THE SPLIT, AND WHY IT IS THIS WAY. This module does no I/O against the session API — it cannot,
it is plain Python in a repo. The AGENT lists sessions (an MCP call) and passes the result here;
this file decides, from committed evidence, and returns ids. That keeps the judgement reviewable,
testable and mutation-checkable, and keeps the irreversible act (archive) in the agent's hands where
a permission prompt can still reach it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
RECEIPTS = os.path.join(HERE, "receipts")

sys.path.insert(0, HERE)
import ids  # noqa: E402  -- the ONE home for the receipt-id shape; see _CYCLE_RECEIPT_STEM below

#: Statuses that mean the session is doing something. ⛔ NEVER archive one of these — the tool
#: releases the container, so archiving a live cycle kills work in progress. Listed positively
#: (what is alive) rather than negatively (what is dead), because a status string this file has
#: never seen must default to ALIVE: an unknown state is not evidence of finishedness.
ALIVE = {
    "SESSION_STATUS_RUNNING",
    "SESSION_STATUS_WORKING",
    "SESSION_STATUS_STARTING",
    "SESSION_STATUS_PENDING",
}

#: Already closed — nothing to do, and re-archiving is noise.
CLOSED = {"SESSION_STATUS_ARCHIVED"}

#: A loop session announces itself two ways: the tag the handoff sets, and the title the generator
#: writes. ⚠ SCOPED BY PROPERTY, NOT BY A LIST OF IDS — a session created tomorrow is in scope
#: without anybody remembering it (paper-hardening §8b.2: six of eleven list-scoped fixes regressed
#: at a sibling; no predicate-scoped one did).
LOOP_TAG = "emc-research-loop"
LOOP_TITLE = re.compile(r"EMC research loop", re.I)

#: A receipt names the session that wrote it. That is the join between "a row in the session list"
#: and "work that is on main".
#:
#: ⛔⛔ THE RECEIPT-ID SHAPE IS `ids.RECEIPT_ID`'S TO OWN, AND A PRIVATE COPY HERE WENT STALE THE DAY
#: THE SHAPE CHANGED (AUT-PD-129, 2026-08-28). This module used to carry its own
#: `re.compile(r"^CYC-\d+\.json$")`. AUT-PROP-013 then appended a session discriminator to every
#: receipt id -- `CYC-0065-1f1a2449.json` -- precisely so two concurrent cycles sharing an ordinal
#: could not share a file. That regex does not match a discriminated name, so this reaper stopped
#: seeing every receipt written after it: measured over the committed tree, the private pattern
#: matched 24 of 70 receipts where `ids.RECEIPT_ID` matches 69.
#: ⚠ AND THE FAILURE WAS SILENT AND IN THE DANGEROUS DIRECTION. Fewer visible receipts means a
#: smaller `delivered` set, which means a delivered cycle is reported as "died holding uncommitted
#: work" -- CLAUDE.md §4's "an absent reading is not a reading of absence", and the SECOND time this
#: file has produced that exact false finding (see `_SESSION_ID` below, which fixed it at the FIELD
#: level while the FILENAME level was still to break).
#: ★ So the shape is imported, never restated. CLAUDE.md rule 1: one fact, one place.
_CYCLE_RECEIPT_STEM = ids.RECEIPT_ID


def _is_cycle_receipt(name: str) -> bool:
    """Is this committed filename a cycle receipt, in either the bare or the discriminated shape?"""
    return name.endswith(".json") and bool(_CYCLE_RECEIPT_STEM.match(name[:-len(".json")]))


#: ⛔⛔ THE SECOND JOIN, AND IT BREAKS INDEPENDENTLY OF THE FIRST (AUT-PD-129). The session LIST
#: speaks CCR ids (`session_01AbC...`). `session_id` in a receipt no longer does: research-loop §2
#: step 10 was tightened on 2026-08-28 to "read it from the environment; never type it", and
#: `CLAUDE_CODE_SESSION_ID` is a harness UUID. That change was RIGHT for its two readers --
#: `health.py:c_cycles_are_sized` and `session_cap.py` only need cycles of one session to share a
#: value -- and it silently broke this one, which needs the value to be the same id the session list
#: uses. Measured over the committed tree: 12 receipts carry a CCR id, 27 carry a bare UUID, and all
#: eight of the newest are UUIDs. One field, two consumers, two incompatible id spaces.
#: ★ SO THE CCR ID GETS ITS OWN FIELD rather than overloading `session_id` a third way. Receipts
#: record `ccr_session_id`; both fields are read here, so a receipt carrying either still joins.
CCR_ID_FIELDS = ("ccr_session_id", "session_id")

#: ⛔⛔ `session_id` IS NOT ALWAYS AN ID. It is a free-text field and cycles have written prose into
#: it — "session_016z8Nm7cZTaLN4smGWue75c (spawned session, no live user present — started by
#: CYC-0012 at its 2-cycle cap)", "unknown -- fired by the UI-created autonomy Routine", and bare
#: UUIDs for interactive sessions. Measured 2026-08-27 (CYC-0020) by the first run of this reaper,
#: which compared the whole field for equality and therefore reported THREE DELIVERED CYCLES
#: (CYC-0013/0014/0015) as "idle with no committed receipt — a cycle that died holding uncommitted
#: work". ⚠ THAT IS THE DANGEROUS DIRECTION TWICE OVER: it manufactures a finding a human would go
#: chase, and it silently refuses to clean up the very sessions the reaper exists to close. So the
#: id is EXTRACTED from the field rather than assumed to be the field — CLAUDE.md §4's "a populated
#: field is not a measured one", one level down.
_SESSION_ID = re.compile(r"\bsession_[A-Za-z0-9]{6,}\b")


def _is_loop_session(s: dict) -> bool:
    tags = s.get("tags") or []
    if LOOP_TAG in tags:
        return True
    return bool(LOOP_TITLE.search(s.get("title") or ""))


def committed_session_ids(ref: str = "HEAD") -> set[str]:
    """Every session id named by a receipt REACHABLE FROM `ref`.

    ⛔ READ FROM GIT, NOT FROM THE WORKING TREE. A receipt sitting unstaged on disk is precisely the
    case where archiving would lose the work: the file exists, so a naive `os.listdir` would call it
    committed, and the session that still holds it would be closed. `git show` answers the question
    actually being asked — is this on the trunk?
    """
    out = subprocess.run(
        ("git", "ls-tree", "--name-only", f"{ref}:research/autonomy/receipts"),
        cwd=REPO, capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise SystemExit(
            "cannot list committed receipts from git, so no session can be shown to be safe to "
            "archive. Refusing to archive anything rather than guessing — an absent reading is not "
            "a reading of absence (CLAUDE.md §4).\n" + out.stderr.strip()
        )
    found: set[str] = set()
    for name in out.stdout.split():
        if not _is_cycle_receipt(name):
            continue
        blob = subprocess.run(
            ("git", "show", f"{ref}:research/autonomy/receipts/{name}"),
            cwd=REPO, capture_output=True, text=True,
        )
        if blob.returncode != 0:
            continue
        try:
            data = json.loads(blob.stdout)
        except json.JSONDecodeError:
            continue
        for field in CCR_ID_FIELDS:
            sid = data.get(field)
            if isinstance(sid, str):
                # Extract, never compare whole — see _SESSION_ID above.
                found.update(_SESSION_ID.findall(sid))
        # ⛔ `handoff.child_session_id` IS DELIBERATELY NOT COLLECTED. A child id in a parent's
        # receipt proves the child was CREATED, never that it DELIVERED — and this reaper's whole
        # safety property is "the work is on the trunk". Counting it would archive a spawned session
        # that died before writing anything, which is the one case that must stay visible.
    return found


def receipts_that_cannot_join(ref: str = "HEAD") -> int:
    """How many committed receipts name NO CCR session id, and so can never match the session list.

    ⛔⛔ THIS IS WHAT MAKES THE "no committed receipt" VERDICT FALSIFIABLE (AUT-PD-129). Without it
    the reaper cannot tell two very different situations apart, and it reported them identically:

      (a) a cycle really did die before committing its receipt   — a finding a human must chase;
      (b) the cycle delivered, but its receipt records a harness UUID where the session list speaks
          a CCR id, so nothing could ever have matched — an instrument gap, and chasing it wastes
          the reader's time on a session that is fine.

    Reporting (b) as (a) is the failure mode this file's header already records paying for once, and
    a guard that cries wolf is a guard that gets tuned out. So the count is measured and carried into
    the reason string, rather than the verdict being stated more confidently than the evidence.

    ⚠ THE COUNT ALONE IS NOT ENOUGH, AND ON ITS OWN IT LATCHES — see
    `newest_unjoinable_receipt_commit` below, which is what makes the softening expire.
    """
    return len(unjoinable_receipt_names(ref))


def unjoinable_receipt_names(ref: str = "HEAD") -> list[str]:
    """The committed receipt filenames that name NO CCR session id. One scan, one definition.

    ⛔ Both the COUNT and the HORIZON are derived from this list rather than each re-deriving
    "can this receipt join?" — CLAUDE.md rule 1. Two copies of that predicate is the same shape as
    the private filename regex that went stale above.
    """
    out = subprocess.run(
        ("git", "ls-tree", "--name-only", f"{ref}:research/autonomy/receipts"),
        cwd=REPO, capture_output=True, text=True,
    )
    if out.returncode != 0:
        return []
    names: list[str] = []
    for name in out.stdout.split():
        if not _is_cycle_receipt(name):
            continue
        blob = subprocess.run(
            ("git", "show", f"{ref}:research/autonomy/receipts/{name}"),
            cwd=REPO, capture_output=True, text=True,
        )
        if blob.returncode != 0:
            continue
        try:
            data = json.loads(blob.stdout)
        except json.JSONDecodeError:
            continue
        if not any(_SESSION_ID.findall(data.get(f) or "")
                   for f in CCR_ID_FIELDS if isinstance(data.get(f), str)):
            names.append(name)
    return names


def newest_unjoinable_receipt_commit(ref: str = "HEAD") -> str | None:
    """When the newest receipt that can NEVER join reached the trunk. `None` if that is unknown.

    ⛔⛔ WHY A HORIZON AND NOT JUST A COUNT (AUT-PD-124, measured 2026-08-28 on `origin/main`).
    AUT-PD-129 correctly stopped the reaper asserting a death it could not evidence, by softening
    the verdict whenever ANY committed receipt names no CCR id. But that count is taken over
    IMMUTABLE COMMITTED HISTORY and can never fall: measured on the trunk this day, 63 of 76 cycle
    receipts cannot join, and 39 of them name no session id anywhere at all — prose like "unknown --
    fired by the UI-created autonomy Routine" — so nobody can ever recover which session wrote them.
    ★ THE CONSEQUENCE: the softening never expires, so the branch that raises the alarm this whole
    module exists for ("idle with NO committed receipt — this is a finding") became UNREACHABLE in
    production the day it was added. A guard that can never fire again is the latching failure
    `receipt_schema.py` and `preflight.sh` each already record paying for once.

    ★ THE RESOLUTION, AND IT NEEDS NO NEW PINNED CONSTANT. An unjoinable receipt can only excuse a
    session that could have WRITTEN one. A receipt is committed after the session that wrote it
    started, so a session created AFTER the newest unjoinable receipt landed cannot own any of them:
    for that session, "not in `delivered`" really is evidence, and the finding is honest again. The
    horizon is derived from git, so it moves by itself — every receipt written under
    `receipt_schema.FIRST_CCR_GOVERNED_CYCLE` carries a CCR id, so the horizon stops advancing and
    the alarm comes back on for every session created from then on.

    ⚠ FAILS TOWARD SILENCE, NEVER TOWARD A DEATH CLAIM. Unknown horizon, unparseable time, missing
    `created_at` -> the session is treated as one that could own an unjoinable receipt, so the
    verdict stays DEGRADED. Nothing here can archive anything: this only chooses between two `keep`
    reasons.
    """
    names = unjoinable_receipt_names(ref)
    if not names:
        return None
    want = {f"research/autonomy/receipts/{n}" for n in names}
    log = subprocess.run(
        ("git", "log", "--format=%x01%cI", "--name-only", ref, "--",
         "research/autonomy/receipts"),
        cwd=REPO, capture_output=True, text=True,
    )
    if log.returncode != 0:
        return None
    stamp = None
    for line in log.stdout.splitlines():
        # `git log` is newest-first, so the first unjoinable path we meet carries the newest commit
        # that touched one.
        if line.startswith("\x01"):
            stamp = line[1:].strip()
        elif line.strip() in want:
            return stamp
    return None


def _utc(value: str):
    """Parse an RFC3339 stamp, or raise. `Z` is what both git and the session list write."""
    from datetime import datetime, timezone
    dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def could_own_an_unjoinable_receipt(session: dict, horizon_utc: str | None) -> bool:
    """Could THIS session be the author of a receipt that can never join? Conservative by design.

    True unless the session is provably younger than every unjoinable receipt on the trunk. Every
    uncertainty — no horizon, no `created_at`, an unparseable one — answers True, which keeps the
    softer verdict and never manufactures a death.
    """
    if not horizon_utc:
        return True
    created = session.get("created_at")
    if not isinstance(created, str) or not created.strip():
        return True
    try:
        return not (_utc(created) > _utc(horizon_utc))
    except ValueError:
        return True


def classify(sessions: list[dict], self_id: str | None, ref: str = "HEAD",
             unjoinable_receipts: int = 0, join_horizon_utc: str | None = None) -> dict:
    """Split the session list into archive / keep, each with a reason.

    Every `keep` carries WHY, because a reaper that silently skips is indistinguishable from a
    reaper that is broken.

    `unjoinable_receipts` and `join_horizon_utc` are the two halves of one measurement: how many
    committed receipts can never join, and when the newest of them landed. The count decides whether
    the join is degraded AT ALL; the horizon decides whether it is degraded FOR THIS SESSION. Both
    are passed in rather than measured here so the decision stays a pure function of evidence.
    """
    delivered = committed_session_ids(ref)
    archive, keep = [], []

    for s in sessions:
        sid = s.get("id") or ""
        status = s.get("session_status") or ""
        title = (s.get("title") or "")[:60]
        row = {"id": sid, "title": title, "status": status}

        if not sid:
            keep.append({**row, "why": "no id — cannot act on it"})
        elif sid == self_id:
            keep.append({**row, "why": "this is the calling session; a cycle never reaps itself"})
        elif status in CLOSED:
            keep.append({**row, "why": "already archived"})
        elif status in ALIVE or status not in {"SESSION_STATUS_IDLE"}:
            # ⛔ DEFAULT TO ALIVE. Anything not positively known to be idle is left alone, including
            # a status string this file has never seen.
            keep.append({**row, "why": f"not positively idle ({status or 'unknown status'}) — left alone"})
        elif not _is_loop_session(s):
            keep.append({**row, "why": "not a research-loop session; out of this reaper's scope"})
        elif sid in delivered:
            archive.append({**row, "why": "idle, and its receipt is on the trunk"})
        elif unjoinable_receipts and could_own_an_unjoinable_receipt(s, join_horizon_utc):
            # ⛔ THE HONEST VERDICT WHEN THE JOIN ITSELF IS DEGRADED (AUT-PD-129). Some committed
            # receipt names no CCR id at all, so "not in `delivered`" is not evidence this session
            # delivered nothing — it may simply be unmatchable. Still never archived: the safe
            # direction is unchanged, only the claim is weakened to what the evidence supports.
            # ⭐ AND IT IS NOW SCOPED TO THE SESSIONS THE GAP CAN ACTUALLY EXCUSE (AUT-PD-124):
            # unconditional softening never expires, because committed history never gains a CCR id.
            keep.append({
                **row,
                "why": (f"idle, and no committed receipt names it — but {unjoinable_receipts} "
                        "committed receipt(s) record no CCR session id at all, so this join is "
                        "DEGRADED and cannot tell 'died holding work' from 'delivered, unmatchable'. "
                        "Not archived, and not reported as a death. Fix: receipts must carry "
                        "`ccr_session_id`."
                        + (f" (Newest unjoinable receipt committed {join_horizon_utc}; this session "
                           f"was created {s.get('created_at') or 'at an unrecorded time'}, so it "
                           "could be the one that wrote it.)" if join_horizon_utc else "")),
            })
        else:
            keep.append({
                **row,
                "why": ("idle with NO committed receipt — this is a finding, not litter. A cycle that "
                        "died holding uncommitted work looks exactly like this, and archiving it "
                        "would release the container that still has it."
                        + (f" The join is sound FOR THIS SESSION: every committed receipt that cannot "
                           f"name a CCR id landed by {join_horizon_utc}, before this session was "
                           f"created ({s.get('created_at')}), so none of them can be its receipt."
                           if unjoinable_receipts else "")),
            })

    return {"archive": archive, "keep": keep, "committed_session_ids": sorted(delivered)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Decide which finished research-loop sessions are safe to archive. Reads a "
                    "session list on stdin (the JSON the list_sessions tool returns) and writes a "
                    "verdict. Archives nothing itself — the agent does that, so the irreversible "
                    "act stays where a permission prompt can reach it.")
    ap.add_argument("--self-id", help="the calling session's id, which is never reaped")
    ap.add_argument("--ref", default="HEAD", help="git ref whose receipts count as delivered (default HEAD)")
    ap.add_argument("--json", action="store_true", help="emit the verdict as JSON")
    args = ap.parse_args(argv)

    raw = sys.stdin.read().strip()
    if not raw:
        print("no session list on stdin — nothing to classify, and nothing archived.")
        return 0
    data = json.loads(raw)
    # Accept the tool's envelope or a bare list, so a caller need not know which they have.
    if isinstance(data, dict):
        data = data.get("ccr", data)
        sessions = data.get("data") or data.get("sessions") or []
    else:
        sessions = data

    # ⛔ ONE SCAN, TWO NUMBERS. The count and the horizon must describe the SAME set of receipts, or
    # the verdict softens on one measurement and expires on another (AUT-PD-124).
    unjoinable = unjoinable_receipt_names(args.ref)
    verdict = classify(sessions, args.self_id, args.ref,
                       unjoinable_receipts=len(unjoinable),
                       join_horizon_utc=newest_unjoinable_receipt_commit(args.ref))

    if args.json:
        print(json.dumps(verdict, indent=2))
        return 0

    print(f"[reaper] {len(sessions)} session(s) in, "
          f"{len(verdict['archive'])} safe to archive, {len(verdict['keep'])} kept")
    for r in verdict["archive"]:
        print(f"  ARCHIVE  {r['id']}  {r['title']}")
    for r in verdict["keep"]:
        if "already archived" in r["why"] or "out of this reaper's scope" in r["why"]:
            continue  # the boring majority; the interesting keeps are printed below
        print(f"  keep     {r['id']}  {r['title']}\n           └─ {r['why']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
