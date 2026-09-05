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
import subprocess
import sys

import cadence

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
LEDGER = HERE / "research-ledger.json"
STATE = HERE / "autonomy-state.json"
RECEIPTS = HERE / "receipts"

# ⚠ sys.path, not a package import — see priority.py's identical comment; this directory is a flat
# set of scripts run as `python3 research/autonomy/<tool>.py` from the repo root.
sys.path.insert(0, str(HERE))
import stuck_clock  # noqa: E402
import bounded_review

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


#: ⛔ The field a session records when the mechanism was ABSENT rather than refused — no
#: `create_session` on this context's tool surface at all. Named here, once, because `session_cap.py`
#: and `health.py` both read it and AUT-PD-017's finding is that a field name agreed in prose between
#: two readers is not agreed at all.
UNAVAILABLE_FIELD = "handoff.mechanism_unavailable"


def mechanism_unavailable_of(receipt: dict) -> str | None:
    """What this session found ABSENT when it went looking for a way to hand off, or None.

    ⛔⛔ A REFUSAL AND AN ABSENCE ARE DIFFERENT FAILURES AND THEY HAVE DIFFERENT REMEDIES
    (AUT-PD-059, measured 2026-08-28; the two incidents are AUT-PD-032 and AUT-PD-045).
    `refusal_of` covers a call that was MADE and rejected — `create_session` exists, the session
    called it, and the platform answered with a lineage-depth ceiling. This covers the stronger
    failure: in a scheduled-Routine session `create_session` is **not present as a tool at all**,
    at lineage depth 1, with no chain to have exhausted. Nothing was refused because nothing could
    be called.

    ★ WHY THE DISTINCTION IS WORTH A SECOND FIELD RATHER THAN A SHARED "blocked" ONE. A depth
    refusal says the loop ran too deep and a successor started nearer the root would work — the
    remedy is a shallower spawn. An absence says the platform never gave THIS LAUNCH SHAPE the
    tool, so spawning shallower changes nothing and the remedy is to stop expecting a handoff here
    and let the driver Routine's next firing be the successor. Recording which one occurred is the
    whole diagnostic value; collapsing them tells a future session to retry something that cannot
    work, or to give up on something that would have.

    ⚠ AND THIS EVIDENCE IS WEAKER THAN A REFUSAL'S, WHICH IS STATED RATHER THAN HIDDEN. A refusal
    can quote the platform's own words, so a reader can tell a real ceiling from an excuse. An
    absence produces no words at all — there is nothing to quote — so the string is necessarily the
    session's own account of a check it says it ran. That asymmetry is exactly why a named absence
    downgrades a health row to UNMEASURED and never to green: it is a reason the reading could not
    be taken, never evidence the rule was obeyed.

    ⛔ AN ABSENT RECORD IS STILL A SKIPPED HANDOFF. Same rule as `refusal_of`, same reason:
    otherwise "the tool wasn't there" becomes a free pass claimable by any session that never
    looked.
    """
    block = receipt.get("handoff")
    if not isinstance(block, dict):
        return None
    v = block.get("mechanism_unavailable")
    return v.strip() if isinstance(v, str) and v.strip() else None


def _read(path: pathlib.Path):
    try:
        return json.loads(path.read_text()), None
    except Exception as exc:                                  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


#: The ref a successor will actually be standing on. Not `HEAD`: the successor's first act is
#: `checkout -B main origin/main`, so a commit this session made and did not push is as invisible to
#: it as one never made. `claim.py` reached the same conclusion for the same reason — "the push is
#: the arbiter" — and reads `origin/main:<path>` too.
TRUNK = "origin/main"

LEDGER_REL = "research/autonomy/research-ledger.json"
STATE_REL = "research/autonomy/autonomy-state.json"
RECEIPTS_REL = "research/autonomy/receipts"


def _git(*args, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True, check=check)


def _committed(rel: str):
    """`(parsed JSON at origin/main:<rel>, None)` or `(None, why it could not be read)`.

    ⛔ NEVER FALLS BACK SILENTLY. A caller that cannot read the trunk gets `None` and a reason it
    must carry into the prompt, because the failure this whole function exists to fix was a
    working-tree read wearing a committed-state label (CLAUDE.md §4: an absent reading is not a
    reading of absence).
    """
    try:
        proc = _git("show", f"{TRUNK}:{rel}", check=False)
        if proc.returncode != 0:
            return None, (proc.stderr or proc.stdout or "").strip() or f"git show exited {proc.returncode}"
        return json.loads(proc.stdout), None
    except Exception as exc:                                  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


def committed_receipts(n: int = RECENT_N) -> tuple[list[str], str | None]:
    """The newest receipt FILENAMES the trunk carries, plus a reason if the trunk was unreadable."""
    try:
        proc = _git("ls-tree", "--name-only", f"{TRUNK}:{RECEIPTS_REL}", check=False)
        if proc.returncode != 0:
            return [], (proc.stderr or "").strip() or f"git ls-tree exited {proc.returncode}"
        names = sorted(x for x in proc.stdout.split() if x.endswith(".json"))
        return names[-n:], None
    except Exception as exc:                                  # noqa: BLE001
        return [], f"{type(exc).__name__}: {exc}"


def unpushed_rows(working: dict | None, trunk: dict | None) -> list[str]:
    """Ledger ids the WORKING TREE holds that `origin/main` does not — filed work about to be lost.

    ⛔⛔ THIS IS THE HALF THAT PREVENTS THE LOSS, AND READING COMMITTED STATE ALONE WOULD HIDE IT
    (AUT-PD-166, measured 2026-08-29). Building the queue from the trunk makes the prompt's
    provenance sentence TRUE; it does nothing whatever for the row that never reached the trunk —
    that row simply stops being mentioned, and a silent omission is a worse failure than a phantom
    pointer because nothing is left to notice.

    ⚠ IDS ONLY, DELIBERATELY, AND THE NARROWNESS IS THE POINT. A row whose CONTENT differs between
    the two is usually `priority.py --write` having re-scored a derived field, which regenerates on
    the successor's own step 3; a row whose ID is absent cannot regenerate from anything. Widening
    this to content drift would fire on almost every handoff and be ignored within a week, which is
    how a guard becomes ceremony.
    """
    if not isinstance(working, dict) or not isinstance(trunk, dict):
        return []
    have = {e.get("id") for e in (trunk.get("entries") or [])}
    return [e.get("id") for e in (working.get("entries") or [])
            if e.get("id") and e.get("id") not in have]


def unpushed_receipt_files() -> list[str]:
    """Receipt filenames on disk that `origin/main` does not carry. Same class as `unpushed_rows`."""
    committed, err = committed_receipts(n=10 ** 6)
    if err:
        return []
    try:
        return sorted(p.name for p in RECEIPTS.glob("*.json") if p.name not in set(committed))
    except Exception:                                         # noqa: BLE001
        return []


def terminal_ids(repo: str | None = None, path: str | None = None) -> frozenset[str]:
    """Ids `stuck_clock.py` currently reports `stalled_needs_human`, or an empty set on ANY failure.

    ⛔⛔ FAIL OPEN, NEVER CLOSED, AND THE DIRECTION IS DELIBERATE (AUT-PROP-029, wiring stuck_clock in).
    stuck_clock derives both clocks by shelling out to `git log`/`git show` on the COMMITTED ledger; a
    missing git binary, an unset identity, a detached worktree or a shallow clone below its own
    censoring threshold must never turn into "hide the highest-scoring row from the successor". A row
    wrongly kept because this read failed costs nothing that was not already true before this function
    existed; a row wrongly HIDDEN because a subprocess errored is a false absence of work — CLAUDE.md
    §4's "an absent reading is not a reading of absence", applied to a queue rather than a status.

    ⚠ CALLED LIVE, NOT FROM A COMMITTED HEALTH BOARD, AND ON PURPOSE. `handoff.py`'s own docstring:
    "every fact here is read from a committed artifact AT BUILD TIME" — a health board is one more
    hop and one more chance to be stale between the ledger this ranks and the verdict about it, and a
    handoff is rare enough (only at a session's cycle cap) that a fresh `git log` walk here costs
    nothing worth optimising away.
    """
    try:
        kwargs = {}
        if repo is not None:
            kwargs["repo"] = repo
        if path is not None:
            kwargs["path"] = path
        return frozenset(clock.entry_id for clock, _ in stuck_clock.terminal_rows(**kwargs))
    except Exception:
        return frozenset()


def top_items(ledger: dict | None, n: int = TOP_N, exclude_ids=None) -> list[dict]:
    """The highest-scoring TAKEABLE entries — the same predicate `queue_is_takeable` uses.

    ⚠ Takeable, not merely high-scoring: handing a successor an item that is owned, blocked or out of
    retry budget wastes its first act on discovering that, which is the cost the ledger exists to
    remove.

    ⛔ `exclude_ids` (AUT-PROP-029) drops a row `stuck_clock.py` reports `stalled_needs_human` — it is
    not queued work any more, it is a human decision (re-scope, hand off, or close it), and handing it
    to a fresh session would spend that session's first act re-discovering exactly the stall the model
    already proved. ⚠ IT DOES NOT TOUCH THE LEDGER OR THIS FUNCTION'S OTHER PREDICATES: a caller that
    passes nothing gets the pre-AUT-PROP-029 behaviour exactly, and the excluded row is still `queued`
    on disk — this filters what is HANDED OVER, never what IS.
    """
    entries = (ledger or {}).get("entries") or []
    exclude = exclude_ids or frozenset()
    takeable = [e for e in entries
                if not e.get("owner")
                and str(e.get("state") or "queued") in {"queued", "blocked"}
                and int(e.get("retry_budget") or 0) > 0
                and e.get("score") is not None
                and not e.get("requires_trimcrae")
                and bounded_review.task_review_decision(e, repo=REPO)["allowed"]
                and e.get("id") not in exclude]
    return sorted(takeable, key=lambda e: -float(e.get("score") or 0))[:n]


def handed_to_trimcrae(ledger=None) -> list[dict]:
    """The rows `_takeable` withholds because they are trimcrae's act, best first.

    Reported rather than dropped silently, for `continuity.py`'s reason: an outward-facing row is a
    question somebody must answer, not a status, and a successor that never learns the row exists
    cannot escalate it. This is `_takeable`'s AUT-PROP-029 exclusion note applied to a second and
    unrelated predicate.
    """
    if ledger is None:
        ledger, _ = _read(LEDGER)
    rows = [e for e in ((ledger or {}).get("entries") or [])
            if e.get("requires_trimcrae")
            and not e.get("owner")
            and str(e.get("state") or "queued") in {"queued", "blocked"}]
    return sorted(rows, key=lambda e: -float(e.get("score") or 0))


def recent_receipts(n: int = RECENT_N) -> list[str]:
    """The newest receipts the SUCCESSOR will find, which is what `origin/main` carries.

    ⛔ SAME DEFECT AS THE QUEUE'S, ONE FILE OVER (AUT-PD-166). A receipt written and not pushed is
    named here and absent from the successor's clone, and the successor is instructed to READ these
    rather than ask what happened — so it spends its first act on a missing file. Falls back to the
    working tree only when the trunk cannot be read at all, which `build` reports in the prompt.
    """
    committed, err = committed_receipts(n)
    if not err:
        return committed
    try:
        return sorted(p.name for p in RECEIPTS.glob("*.json"))[-n:]
    except Exception:                                          # noqa: BLE001
        return []


def build(reason: str = "", ledger=None, state=None, lost=None) -> str:
    """The successor's prompt. Standalone: a fresh session knows nothing about this one.

    ⛔⛔ EVERY FACT HERE IS READ FROM `origin/main`, NOT FROM THE WORKING TREE, AND THAT SENTENCE
    USED TO BE FALSE (AUT-PD-166, measured 2026-08-29). The module docstring above promised
    committed provenance; `build` read `LEDGER` off disk. CYC-0079 filed a row, built its handoff
    before pushing it, and handed CYC-0080 a queue whose TOP ITEM had never existed on the trunk —
    under a heading reading "read from the committed ledger when this prompt was built".

    ⚠ AND THE SUCCESSOR HAD BEEN TOLD THAT SYMPTOM MEANT SOMETHING ELSE. The stale-checkout
    paragraph below describes exactly this symptom and attributes it to a detached HEAD; a
    successor that verifies its HEAD against `origin/main`, as that paragraph instructs, clears the
    named cause and is left holding a symptom the prompt says cannot happen. A warning that names
    one of two causes is a misdiagnosis waiting to be believed, so it now names both.

    ⭐ `lost` is the ids `origin/main` does not carry. Passing it does NOT make the handoff honest —
    `main()` refuses outright unless the caller asked for the escape — it makes a deliberate loss
    legible to the session that inherits it.
    """
    provenance = f"read from `{TRUNK}` when this prompt was built"
    if ledger is None:
        ledger, why = _committed(LEDGER_REL)
        if ledger is None:
            ledger, _ = _read(LEDGER)
            provenance = (f"⚠ read from the BUILDER'S WORKING TREE, not from `{TRUNK}` — the trunk "
                          f"could not be read ({why}). Trust it less than usual and re-score first")
    if state is None:
        state, why = _committed(STATE_REL)
        if state is None:
            state, _ = _read(STATE)

    excluded = terminal_ids()
    items = top_items(ledger, exclude_ids=excluded)
    his = handed_to_trimcrae(ledger)
    queue = "\n".join(
        f"  {e['id']}  score {e.get('score')}  [{e.get('kind')}]  {str(e.get('what') or '')[:150]}"
        for e in items) or "  (the ledger holds nothing takeable — that is itself the finding; see below)"
    if excluded:
        queue += (f"\n  ⛔ EXCLUDED as `stalled_needs_human` (stuck_clock.py --check, AUT-PROP-029): "
                  f"{', '.join(sorted(excluded))} — a human decision, not queued work; do not re-claim "
                  f"it on the strength of its score alone.")
    if his:
        queue += (f"\n  ⛔ WITHHELD as `requires_trimcrae` (AUT-PD-127), NOT because they are "
                  f"unimportant — several outscore everything above: "
                  f"{', '.join(e['id'] for e in his[:10])}"
                  f"{' …' if len(his) > 10 else ''}. Each is an outward-facing or irreversible act "
                  f"reserved for trimcrae by CLAUDE.md §3, so no cycle may take one. ⭐ You may still "
                  f"PREPARE everything one needs and escalate it — `research-loop` §5 — but do not "
                  f"claim it as queued work.")

    if lost:
        queue += (f"\n  ⛔⛔ NOT HANDED OVER AND ALREADY LOST — the builder held {len(lost)} ledger "
                  f"row(s) `{TRUNK}` does not carry, and emitted this prompt anyway: "
                  f"{', '.join(sorted(str(i) for i in lost))}. Their content died with that "
                  f"session's container. ⭐ Do not try to reconstruct them from this line; file what "
                  f"you can re-derive yourself, and treat the ids as free.")

    interval = (state or {}).get("cycle_interval_hours", "?")
    backoff = (state or {}).get("backoff_level", "?")
    width = (state or {}).get("subagent_width", "?")
    cap = (state or {}).get("max_cycles_per_session", "?")
    env = SPAWN["environment_id"]
    src = SPAWN["source_url"]
    rev = SPAWN["source_revision"]
    child_field = CHILD_ID_FIELD
    refused_field = REFUSAL_FIELD
    unavailable_field = UNAVAILABLE_FIELD

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

⛔⛔ AND A STALE CHECKOUT IS ONLY ONE OF THE TWO CAUSES OF THAT SYMPTOM — DO NOT STOP WHEN YOU HAVE
CLEARED IT. Measured 2026-08-29 (AUT-PD-166): CYC-0080 verified its HEAD against `origin/main`,
found them equal, and STILL held a prompt whose top item did not exist, because this generator read
its queue from the builder's working tree while claiming committed provenance. It is fixed here and
the queue above now comes from `{TRUNK}`. ⭐ If you ever again find a named item missing on a HEAD
you have verified, the remedy is NOT to re-check the checkout: run
`git log -8 -- research/autonomy/research-ledger.json` and grep each commit for the id, and if it
has never existed, that is a row somebody filed and did not push — say so rather than reasoning
about your own tree.

Then load the cycle contract and follow it — do not work from this prompt alone:

    the `research-loop` skill, or if you have no Skill tool:  cat .claude/skills/research-loop/SKILL.md

⭐ WHAT IS WAITING, {provenance}. RE-SCORE IT YOURSELF
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

⛔ AND IF YOU CANNOT HAND OFF, RECORD WHICH OF THE TWO WAYS IT FAILED — THEY ARE DIFFERENT FAILURES
WITH DIFFERENT REMEDIES, AND A RECEIPT THAT DOES NOT SAY WHICH IS GRADED AS A SESSION THAT NEVER
TRIED. If `create_session` EXISTS and the platform REFUSES it (a lineage-depth ceiling, for example),
put its answer VERBATIM under `{refused_field}`. If `create_session` is not on your tool surface at
all — the usual case in a scheduled-Routine session — name what you searched for and did not find
under `{unavailable_field}`. ★ THE DISTINCTION IS THE POINT: a refusal means a successor started
nearer the root would work; an absence means spawning cannot help from this launch shape and the
driver Routine's next firing is the successor. Both read as UNMEASURED rather than as your defect;
NEITHER field, or a name you invented instead, reads as RED.

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


def cadence_verdict():
    """`(exit_code, why, payload)` from the cadence gate, read against THIS module's `STATE`.

    ⭐ A NAMED SEAM, ON PURPOSE. It exists so a test about the DIVERGENCE refusal can neutralise the
    CADENCE refusal without either becoming untested — the same hermeticity problem the stuck-clock
    suite hit the same day, where four assertions graded fixed fixtures against a config file the
    budget governor moves. Production keeps the real path; a test patches this one function.
    """
    return cadence.check(state_path=str(STATE))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reason", default="", help="why the handoff is happening")
    ap.add_argument("--json", action="store_true", help="emit {title, prompt} for create_session")
    ap.add_argument("--allow-divergence", action="store_true",
                    help="emit the prompt even though filed ledger rows will not survive the handoff, "
                         "naming them in it. For a builder that genuinely cannot commit — not a way "
                         "past the check.")
    ap.add_argument("--ignore-cadence", action="store_true",
                    help="build the successor even though the cadence gate refuses. For a successor "
                         "genuinely due whose last-cycle stamp is wrong — not a way past the hold.")
    a = ap.parse_args(argv)

    # ⛔⛔ THE REFUSAL, AND IT IS THE POINT OF THIS MODULE'S 2026-08-29 REPAIR (AUT-PD-166). Reading
    # the trunk makes the prompt HONEST; only refusing to build one over unpushed rows makes the
    # work SURVIVE. A handoff is the last act of a session whose container is about to be reclaimed,
    # so this is the final moment anything filed in it can still be saved, and the remedy is one
    # commit. ⚠ It fails OPEN when the trunk is unreadable — `unpushed_rows` returns [] on a None
    # trunk — because a builder that cannot reach git must still be able to hand off; `build` then
    # says so in the prompt rather than claiming committed provenance.
    working, _ = _read(LEDGER)
    trunk, _ = _committed(LEDGER_REL)
    lost = unpushed_rows(working, trunk)
    lost_receipts = unpushed_receipt_files()
    if (lost or lost_receipts) and not a.allow_divergence:
        print("REFUSED: this handoff would discard work the successor can never see.", file=sys.stderr)
        for i in sorted(lost):
            print(f"  ledger row filed in the working tree, absent from {TRUNK}: {i}", file=sys.stderr)
        for f in lost_receipts:
            print(f"  receipt on disk, absent from {TRUNK}: {f}", file=sys.stderr)
        print(f"REMEDY: commit and push them, then build the handoff again. The successor clones "
              f"{TRUNK}; anything not there died with this container. To hand off anyway and record "
              f"the loss in the prompt, re-run with --allow-divergence.", file=sys.stderr)
        return 3

    # ⛔⛔ THE SECOND REFUSAL, AND IT COST $5.39 TO LEARN (CYC-0088, 2026-08-29). A handoff SPAWNS A
    # SESSION, so it is a cadence event as much as a fire from the Routine is — and nothing here
    # checked the cadence. trimcrae's budget hold landed at 11:51Z; CYC-0088 built a handoff at
    # 13:41Z, minutes after its own cycle, and the successor spent $5.39 before it was interrupted.
    # ⚠ THE PROVENANCE WAS NOT THE BUG. `build` reads `origin/main` and did so correctly; the hold
    # simply had not been pushed when it read. What was missing is that a successor created inside
    # the interval breaches the cadence WHATEVER the posture said — the gate belongs on the spawn,
    # not only on the fire, because those are the two ways a cycle starts.
    # ⭐ It fails OPEN exactly where `cadence.check` does: unreadable state, no declared interval, or
    # no prior cycle. A handoff that cannot read the governor must still be possible.
    code, why, _ = cadence_verdict()
    if code != cadence.MAY_START and not a.ignore_cadence:
        print("REFUSED: a handoff creates a session, so it is a cadence event.", file=sys.stderr)
        print(f"  {why}", file=sys.stderr)
        print("REMEDY: end this session without a successor. The Routine fires again on its own "
              "schedule and a fresh session re-reads the ledger — that is the whole recovery "
              "mechanism (architecture §9 property 2), and nothing is lost by not spawning. "
              "⛔ --ignore-cadence exists for a successor that is genuinely due and mis-dated, not "
              "for one that is merely wanted.", file=sys.stderr)
        return 4

    prompt = build(a.reason, lost=lost)
    if a.json:
        ledger = trunk if trunk is not None else working
        top = top_items(ledger, 1, exclude_ids=terminal_ids())
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
