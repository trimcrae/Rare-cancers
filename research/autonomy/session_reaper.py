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
_CYCLE_RECEIPT = re.compile(r"^CYC-\d+\.json$")

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
    ids: set[str] = set()
    for name in out.stdout.split():
        if not _CYCLE_RECEIPT.match(name):
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
        sid = data.get("session_id")
        if isinstance(sid, str):
            # Extract, never compare whole — see _SESSION_ID above.
            ids.update(_SESSION_ID.findall(sid))
        # ⛔ `handoff.child_session_id` IS DELIBERATELY NOT COLLECTED. A child id in a parent's
        # receipt proves the child was CREATED, never that it DELIVERED — and this reaper's whole
        # safety property is "the work is on the trunk". Counting it would archive a spawned session
        # that died before writing anything, which is the one case that must stay visible.
    return ids


def classify(sessions: list[dict], self_id: str | None, ref: str = "HEAD") -> dict:
    """Split the session list into archive / keep, each with a reason.

    Every `keep` carries WHY, because a reaper that silently skips is indistinguishable from a
    reaper that is broken.
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
        else:
            keep.append({
                **row,
                "why": ("idle with NO committed receipt — this is a finding, not litter. A cycle that "
                        "died holding uncommitted work looks exactly like this, and archiving it "
                        "would release the container that still has it."),
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

    verdict = classify(sessions, args.self_id, args.ref)

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
