#!/usr/bin/env python3
"""Build the prompt for a SUCCESSOR session, from committed state rather than from memory.

⛔⛔ THE GAP THIS CLOSES WAS IN THE ORIGINAL GOAL AND STAYED OPEN FOR A DAY. trimcrae's founding
brief asked for "proper usage of new session creation to manage context"; `research-loop` §3 then
said a full hardening cycle is a SPAWNED SESSION; `health.py`'s `cycles_are_sized` measured when a
session had run too long. Three layers of knowing, and **nothing that actually spawned anything**.
The session that hit the cap wrote "the next cycle should be a fresh session" in its final message
and stopped — a manual step, parked in the middle of a loop whose whole purpose is that no manual
step exists. trimcrae, 2026-08-27: *"You've flagged that a new session needs to start which is
correct. But then you stopped there. We should be automating the creation of new sessions."*

★ WHY THE PROMPT IS GENERATED AND NOT TYPED. A handoff written by the outgoing session is written
from ITS context — the thing that is running out and the reason for handing off at all. Anything it
remembers is exactly what it should not be trusted on. So every fact here is read from a committed
artifact at build time: the queue from `research-ledger.json`, what just happened from the newest
receipts, the posture from `autonomy-state.json`. A fresh session then reads the same files itself
and finds them unchanged, which is CLAUDE.md's "state lives in git, never in context" applied to the
one moment the context is being discarded on purpose.

⚠ AND IT DELIBERATELY CARRIES NO FINDINGS, NO CONCLUSIONS AND NO "WHAT I WAS THINKING". A successor
that inherits the predecessor's reasoning inherits its mistakes with it, and this repository has
already had a wrong seat finding propagate through two cycles because it was passed along as a
summary rather than re-derived. The successor is told WHERE TO LOOK, never WHAT IT WILL FIND.

Usage:
    python3 research/autonomy/handoff.py                  # print the prompt
    python3 research/autonomy/handoff.py --json           # prompt + title, for create_session
    python3 research/autonomy/handoff.py --reason "..."   # why the handoff is happening

⚠ THIS MODULE DOES NOT SPAWN ANYTHING. Creating a session is an MCP call, available to the agent and
not to a script; keeping the DETERMINISTIC half here means the part that can be tested is tested, and
the part that cannot be is one tool call with no judgement left in it.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
LEDGER = HERE / "research-ledger.json"
STATE = HERE / "autonomy-state.json"
RECEIPTS = HERE / "receipts"

#: How many queued items the successor is handed. Enough to choose from; not so many that the prompt
#: becomes a plan the successor follows instead of re-scoring the queue itself, which is step 2 of
#: its own contract.
TOP_N = 5

#: How many recent receipts to name. The successor READS them; they are not summarised here.
RECENT_N = 3

#: ⛔ THE SPAWN TARGET, AND IT IS HERE BECAUSE ITS ABSENCE MADE EVERY HANDOFF A MANUAL STEP AGAIN.
#: `create_session` needs an environment and a source; this module knew neither, so CYC-0017 had to
#: append them BY HAND from its own prompt — copying an operational constant out of the context that
#: is being discarded, which is the one thing a generated handoff exists to prevent. They are read
#: from the loop's own session (`get_session` returns `environment_id` and `session_context.sources`
#: at $0, with no network), and they are constants, not findings: a successor is spawned into the
#: same environment against the same repository, or it is not the same loop.
SPAWN = {
    "environment_id": "env_01AFwLH33U3ZprSgZf2nbV7S",
    "source_url": "https://github.com/trimcrae/Rare-cancers",
    "source_revision": "main",
    "tags": ["emc-research-loop"],
}

#: ⛔ THE RECEIPT FIELD `health.py` ACTUALLY READS. `cycles_are_sized` grades an over-cap session
#: GREEN only if its receipt records `handoff.child_session_id`; a receipt stating the same fact
#: under any other name is invisible to it, so the successor is told the field name rather than left
#: to invent one. Named once, here, and interpolated into the prompt.
CHILD_ID_FIELD = "handoff.child_session_id"


def child_session_id_of(receipt: dict) -> str | None:
    """The handed-off child's session id this receipt records, or None if it records none.

    ⛔ THE ONE PLACE THAT READS `CHILD_ID_FIELD` (AUT-PD-017, generalising AUT-PD-013's fix). Before
    this, `health.py`'s `c_cycles_are_sized` re-derived the same two-level lookup
    (`receipt.get("handoff", {}).get("child_session_id")`) directly in its own source -- the field
    name AND the traversal spelled a second time, agreed with this module only by never being
    touched. That is the exact shape AUT-PD-013 fixed for `subagents.max_concurrent`: a name (and
    here, a path) agreed in prose between a writer and a reader is not agreed at all. Now there is
    one function that knows how to read it, and health.py calls this one instead of re-deriving it.
    """
    block = receipt.get("handoff")
    if not isinstance(block, dict):
        return None
    v = block.get("child_session_id")
    return v.strip() if isinstance(v, str) and v.strip() else None


#: ⛔ The field a session records when the PLATFORM refused the handoff, not when it skipped one.
REFUSAL_FIELD = "handoff.refused_by"


def refusal_of(receipt: dict) -> str | None:
    """The platform's verbatim refusal of this session's handoff attempt, or None.

    ⛔⛔ WHY THIS EXISTS (AUT-PD-032, measured 2026-08-27). `create_session` refuses at a lineage
    depth limit: *"caller session is at lineage depth 8 (limit 8); cannot spawn or re-arm further
    child sessions"*. So the DEEPER a loop has run unattended, the more certainly §3's "hand off the
    same way you were started" fails — and the last generation is the one instructed most
    emphatically to do the impossible.

    ⭐ AND `c_cycles_are_sized` GRADED THAT AS THE SESSION'S DEFECT. Its own comment says a condition
    that cannot be satisfied by doing the right thing "is a stopwatch, not a guard" — which is
    precisely what it became here: the session built the prompt, called the tool, was refused, and
    earned a red row no future cycle could clear.

    ⚠ RECORDING THE REFUSAL IS REQUIRED, AND THAT IS THE WHOLE INTEGRITY OF THIS. An ABSENT refusal
    is still red: otherwise "I could not" becomes a free pass claimable by any session that simply
    did not try. The string must be the platform's own words, so a reader can tell a real ceiling
    from an excuse.
    """
    block = receipt.get("handoff")
    if not isinstance(block, dict):
        return None
    v = block.get("refused_by")
    return v.strip() if isinstance(v, str) and v.strip() else None


def _read(path: pathlib.Path):
    try:
        return json.loads(path.read_text()), None
    except Exception as exc:                                  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


def top_items(ledger: dict | None, n: int = TOP_N) -> list[dict]:
    """The highest-scoring TAKEABLE entries — the same predicate `queue_is_takeable` uses.

    ⚠ Takeable, not merely high-scoring: handing a successor an item that is owned, blocked or out of
    retry budget wastes its first act on discovering that, which is the cost the ledger exists to
    remove.
    """
    entries = (ledger or {}).get("entries") or []
    takeable = [e for e in entries
                if not e.get("owner")
                and str(e.get("state") or "queued") in {"queued", "blocked"}
                and int(e.get("retry_budget") or 0) > 0
                and e.get("score") is not None]
    return sorted(takeable, key=lambda e: -float(e.get("score") or 0))[:n]


def recent_receipts(n: int = RECENT_N) -> list[str]:
    try:
        return sorted(p.name for p in RECEIPTS.glob("*.json"))[-n:]
    except Exception:                                          # noqa: BLE001
        return []


def build(reason: str = "", ledger=None, state=None) -> str:
    """The successor's prompt. Standalone: a fresh session knows nothing about this one."""
    if ledger is None:
        ledger, _ = _read(LEDGER)
    if state is None:
        state, _ = _read(STATE)

    items = top_items(ledger)
    queue = "\n".join(
        f"  {e['id']}  score {e.get('score')}  [{e.get('kind')}]  {str(e.get('what') or '')[:150]}"
        for e in items) or "  (the ledger holds nothing takeable — that is itself the finding; see below)"

    interval = (state or {}).get("cycle_interval_hours", "?")
    backoff = (state or {}).get("backoff_level", "?")
    width = (state or {}).get("subagent_width", "?")
    cap = (state or {}).get("max_cycles_per_session", "?")
    env = SPAWN["environment_id"]
    src = SPAWN["source_url"]
    rev = SPAWN["source_revision"]
    child_field = CHILD_ID_FIELD

    return f"""Run the next cycle of the autonomous EMC research loop. You are a FRESH SESSION,
started deliberately so that this cycle gets a clean context.

WHY YOU EXIST: {reason or "the previous session reached its cycle cap (research-loop §3)."}

Confirm you have the repository AND that you are actually on the trunk, before anything else:

    git -C . fetch -q origin main && git -C . checkout -q -B main origin/main && \
      git -C . rev-parse --short HEAD && git -C . status -sb | head -1

⛔ IF THAT FAILS, SAY SO LOUDLY AS THE FIRST LINE OF YOUR FINAL MESSAGE AND STOP. Do not improvise
around it and do not clone. A session without the repo is the failure that ran every Friday for six
weeks delivering nothing.

⛔⛔ AND CHECK THE SHA AGAINST `git log origin/main -1` BEFORE YOU BELIEVE IT — a session can hold
the repository and still be reading a tree from days ago, which looks EXACTLY like a healthy start.
⚠ Measured 2026-08-27 (CYC-0019), and the command that caused it was the one this generator used to
print: `git pull --rebase -q origin main`. A fired session can begin on a DETACHED HEAD, where that
pull rebases HEAD and leaves the `main` branch where it was; checking out `main` afterwards then
lands on a stale commit and the pull reports success throughout. CYC-0019 spent its first six tool
calls 33 commits behind — its health check read `advancing_live_work` NOT-ADVANCING off three
receipts that were not the last three, its re-score produced a ledger in which the queue's top item
DID NOT EXIST, and the eight most recent receipts were absent from disk. It was caught only by
grepping for an item this prompt had named and finding nothing. `checkout -B main origin/main`
above is unconditional and cannot fail that way.

Then load the cycle contract and follow it — do not work from this prompt alone:

    the `research-loop` skill, or if you have no Skill tool:  cat .claude/skills/research-loop/SKILL.md

⭐ WHAT IS WAITING, read from the committed ledger when this prompt was built. RE-SCORE IT YOURSELF
(`python3 research/autonomy/priority.py --write`) rather than trusting this list — it is a pointer,
not a plan:

{queue}

Posture at handoff, from autonomy-state.json: cycle interval {interval} h, backoff level {backoff},
subagent width {width} (CONCURRENT agents — read it, do not remember it), max cycles per session {cap}.

The last few receipts are {", ".join(recent_receipts()) or "(none)"} in research/autonomy/receipts/.
⛔ READ THEM RATHER THAN ASKING ME WHAT HAPPENED. This prompt deliberately carries no findings and no
conclusions from the previous session: a successor that inherits its predecessor's reasoning inherits
its mistakes, and a wrong review finding has already propagated through two cycles here by being
passed along as a summary instead of re-derived.

⛔ AND YOU INHERIT ITS CAP TOO. You are one session; `research-loop` §3 allows {cap} cycles in it. When
you reach that, HAND OFF THE SAME WAY YOU WERE STARTED — build the prompt with
`python3 research/autonomy/handoff.py --json --reason "..."`, then create the successor with the
claude-code-remote `create_session` tool. That command's JSON carries the `create_session` arguments
under `create_session`: environment {env}, source {src} at revision {rev}. Record the child's id in
your receipt under `{child_field}` — that exact field name is what `health.py`'s `cycles_are_sized`
reads, and a receipt stating the same fact under any other name is invisible to it. A loop that needs
a human to start its next session is not automated; it just has a longer fuse.

⛔ THREE THINGS THAT ARE MEASURED, NOT ADVISORY, AND EACH HAS COST THIS REPOSITORY A RUN: never
background a command with a shell `&` (a hook refuses it — use the tool's own run_in_background,
because `&` orphans the work and nothing ever wakes you); never commit without `./scripts/preflight.sh`
passing on the exact tree you commit; and never trust the harness's reported exit code for a
backgrounded gate — have the command write its own marker (`echo "EXIT=$?" >> log`) and read THAT.
The third is not theoretical: a session has seen the harness report exit code 0 for a preflight whose
own marker said EXIT=1, on the run that caught a red trunk.

⛔ AND VERIFY THE TRUNK YOURSELF RATHER THAN ASSUMING IT: read the Actions result for the current head
of `main` before you take an item. If it is red, `research-loop` §1 says fixing that IS your cycle.
Another cycle may be running concurrently, so expect the ledger to move under you — rebase rather than
force, and check `git log origin/main` before assuming a claim is yours.

Escalate only what the skill's §5 names. Everything else is silent. Your final message is short: what
you took, what changed, and `route_advanced`."""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reason", default="", help="why the handoff is happening")
    ap.add_argument("--json", action="store_true", help="emit {title, prompt} for create_session")
    a = ap.parse_args(argv)

    prompt = build(a.reason)
    if a.json:
        ledger, _ = _read(LEDGER)
        top = top_items(ledger, 1)
        focus = top[0]["id"] if top else "queue empty"
        title = f"EMC research loop — cycle ({focus})"
        # ⭐ THE WHOLE `create_session` CALL, NOT JUST THE PROMPT. The docstring's promise is that
        # the half which cannot be tested is "one tool call with no judgement left in it"; a payload
        # missing the environment and the source left judgement — and hand-copying — in it.
        print(json.dumps({"title": title, "prompt": prompt,
                          "create_session": {"title": title, "prompt": prompt, **SPAWN},
                          "record_child_id_under": CHILD_ID_FIELD},
                         indent=2, ensure_ascii=False))
    else:
        print(prompt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
