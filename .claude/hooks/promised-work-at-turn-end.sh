#!/bin/bash
# ⛔⛔ A TURN THAT ENDS BY DESCRIBING THE NEXT ACTION HAS NOT DONE IT. WRITING THE PLAN IS THE STALL.
#
# trimcrae, 2026-09-01, on the third occurrence in one session: "Did you stall again? If yes, we
# really need something to change in our process so that stops happening."
#
# ★ THE RULE ALREADY EXISTED AND WAS MEASURED BY NOTHING, WHICH IS THIS REPOSITORY'S OWN DIAGNOSIS
# OF WHY RULES FAIL. CLAUDE.md §2 carries the phrasing test — "About to write 'want me to X?' /
# 'I can also X' / 'I could X' and X is self-doable? THE PHRASING IS THE VIOLATION. Delete the offer
# and do X." — and §2's table says a finished sub-task with free steps queued behind is NOT a
# stopping point. Nothing checked. Same shape as `subagent_width` (a governed number no code read
# for a fortnight) and the `notified_utc` requirement (a rule broken three times in one conversation
# while sitting in the file that loads every session).
#
# ⚠ MEASURED THE DAY THIS WAS WRITTEN, three times in one session, and the shape was identical every
# time: finish a diagnosis, write a summary whose last line names the fix, end the turn. The summary
# FEELS like delivery — it is accurate, it is well-organised, and it contains no work.
#   · "Next: regenerate the chain, gate, commit, mint and publish a new archive version"
#   · "Fixing both: the client gets a bounded retry ... and the ledger row gets corrected"
#   · "I'll build the Stop hook that measures it"
# Each was true, each was self-doable, and each cost a round trip that a human had to spend.
#
# ★★ WHAT IT CHECKS, AND WHY THESE THREE CONDITIONS. It refuses the stop only when ALL hold:
#   1. the final message PROMISES work — a future-tense commitment to an action, not a description
#      of one already taken;
#   2. HEAD DID NOT MOVE since the previous stop — nothing was committed this turn;
#   3. NOTHING IS IN FLIGHT — no "In flight:" board with a real row.
# Any one of those failing makes the ending honest: work landed, or work is running and the board
# says so, or the turn genuinely promised nothing.
#
# ⛔ CONDITION 3 IS WHY THIS IS NOT A NAG. `inflight-reporting` requires a board whenever real
# compute is running, and a turn that dispatches a gate and says so is the CORRECT shape — the
# foreground stays free (CLAUDE.md §1) and the harness wakes the session when it lands. This hook
# must never punish that, or it would push sessions toward blocking waits, which is the opposite of
# what §1 asks for.
#
# ⚠ AND IT IS DELIBERATELY NARROW ON CONDITION 1. A guard that reds on true input is one its reader
# learns to loosen (`paper-hardening` §8b.1), and "the model wrote a sentence about the future" is
# far too broad — reporting what a NEXT cycle should do is legitimate and required by the receipt
# contract. So the patterns match a FIRST-PERSON commitment in THIS turn, anchored at a line start
# or after a bullet, and nothing else.
#
# ⛔ WHAT IT CANNOT SEE, STATED SO A GREEN RUN IS NOT MISREAD (CLAUDE.md §4: an absent reading is not
# a reading of absence): whether the promised work was actually the RIGHT work, whether a commit
# that landed was related to the promise, and whether a subagent is running when no board was
# printed. It measures one thing — a promise with no commit and no board behind it.

set -uo pipefail
input=$(cat 2>/dev/null || echo '{}')

# Fires once per stop: the harness sets this when it re-enters after a hook refusal, and a hook that
# can trap a session is worse than no hook.
if command -v jq >/dev/null 2>&1; then
  [[ "$(echo "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)" == "true" ]] && exit 0
fi

REPO="${CLAUDE_PROJECT_DIR:-/home/user/Rare-cancers}"
cd "$REPO" 2>/dev/null || exit 0

STATE_DIR="${REPO}/.git/emc-hooks"
mkdir -p "$STATE_DIR" 2>/dev/null || exit 0
LAST_HEAD_FILE="${STATE_DIR}/promised-work-last-head"

HEAD_NOW=$(git rev-parse HEAD 2>/dev/null) || exit 0
HEAD_PREV=$(cat "$LAST_HEAD_FILE" 2>/dev/null || echo "")
# Record first, so a crash below cannot make the next turn look like it committed nothing.
printf '%s' "$HEAD_NOW" > "$LAST_HEAD_FILE" 2>/dev/null || true

# First run in a container has no baseline. Say nothing rather than guess.
[ -z "$HEAD_PREV" ] && exit 0
# Work landed this turn. Whatever the prose said, something was delivered.
[ "$HEAD_NOW" != "$HEAD_PREV" ] && exit 0

TRANSCRIPT=""
if command -v jq >/dev/null 2>&1; then
  TRANSCRIPT=$(echo "$input" | jq -r '.transcript_path // empty' 2>/dev/null)
fi
[ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ] || exit 0

OUT=$(TRANSCRIPT="$TRANSCRIPT" python3 <<'PYEOF'
import json, os, re, sys

path = os.environ["TRANSCRIPT"]
last = ""
try:
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            msg = ev.get("message") or {}
            if ev.get("type") != "assistant" and msg.get("role") != "assistant":
                continue
            content = msg.get("content")
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text = "\n".join(b.get("text", "") for b in content
                                 if isinstance(b, dict) and b.get("type") == "text")
            else:
                continue
            if text.strip():
                last = text
except Exception:
    sys.exit(0)

if not last.strip():
    sys.exit(0)

# ⭐ CONDITION 3 FIRST — it is the cheapest and it exonerates the correct shape.
# A board with a real row means work is running and the harness will wake the session for it.
board = re.search(r"^\s*\|?\s*In flight\b", last, re.I | re.M) or "In flight:" in last
if board and not re.search(r"nothing in flight", last, re.I):
    sys.exit(0)

# ⛔ CONDITION 1. First-person commitments to work in THIS session, anchored at a line start or
# after a bullet/bold marker. Reporting what a LATER cycle should do is legitimate and is not this.
# ⚠ ANCHORING THESE TOO TIGHTLY IS THE FAILURE MODE, AND THE FIRST DRAFT HAD IT. Written from
# memory of the three stalls, it required `Fixing …:` to END a line and `I'll` to START one; the
# actual messages were "Fixing both: the client gets a bounded retry…" and "The lesson stands. I'll
# build the Stop hook…", and it caught ONE of three. A guard tested only against its author's
# recollection of the defect is a guard fitted to the recollection.
# ★ So the first-person commitment matches ANYWHERE in a sentence — that phrasing is the violation
# wherever it sits (CLAUDE.md §2) — while the bare gerunds stay line-anchored, because "running the
# suite" mid-prose is ordinary description and only "Running X:" as an announcement is a promise.
PATTERNS = [
    r"^\s*(?:[-*>]\s*)?(?:\*\*)?Next(?:\s+steps?)?(?:\*\*)?\s*[:—-]",
    r"\bI(?:'ll|’ll| will| am going to| plan to| intend to)\s+\w",
    r"^\s*(?:[-*>]\s*)?(?:\*\*)?(?:Fixing|Doing|Building|Running|Applying|Committing|Starting|Correcting)\b[^.\n]{0,100}:",
    r"\bnext(?:,| I| step)[^.\n]{0,60}\b(?:I'll|I will|is to)\b",
    r"^\s*(?:[-*>]\s*)?(?:\*\*)?(?:Now|Then|After that)\b[^.\n]{0,60}\b(?:I'll|I will)\b",
]
hits = []
for pat in PATTERNS:
    for m in re.finditer(pat, last, re.I | re.M):
        line = last[m.start():].split("\n", 1)[0].strip()
        if line and line not in hits:
            hits.append(line)

if not hits:
    sys.exit(0)

for h in hits[:3]:
    print("   " + (h[:150] + ("…" if len(h) > 150 else "")))
PYEOF
) || exit 0

[ -z "$OUT" ] && exit 0

{
  echo "⛔⛔ THIS TURN PROMISED WORK, COMMITTED NOTHING, AND HAS NOTHING RUNNING."
  echo
  echo "   HEAD is unchanged since your last stop ($(git rev-parse --short HEAD 2>/dev/null))."
  echo "   No \"In flight\" board with a live row was printed."
  echo "   And your final message says:"
  echo
  echo "$OUT"
  echo
  echo "★ CLAUDE.md §2 — THE PHRASING IS THE VIOLATION. \"About to write 'want me to X?' /"
  echo "   'I can also X' / 'I could X' and X is self-doable? Delete the offer and do X.\""
  echo "   Its table is explicit that finishing one thing with free steps queued behind is NOT a"
  echo "   stopping point, and that a running gate is not either — background it and take the next"
  echo "   task. Writing the plan is the stall; the plan is not the deliverable."
  echo
  echo "★ ONE OF THESE IS TRUE. Do the first that applies, in THIS turn:"
  echo "   1. The work is self-doable. DO IT — then commit, or dispatch it and print the board."
  echo "   2. It is running already. Print the \"In flight\" board, with what will wake you for"
  echo "      each row (inflight-reporting: a row nothing brings you back for is ABANDONED)."
  echo "   3. It is genuinely blocked on a human or an outside system. Then say WHICH, with the"
  echo "      observation that establishes it — CLAUDE.md §0: \"'Blocked' is a claim that needs"
  echo "      evidence, and it is usually wrong.\" ⚠ An inferred outage is not evidence; take the"
  echo "      \$0 reading first."
  echo
  echo "⚠ Fires once per stop, and only when a promise, an unmoved HEAD and an empty board all hold."
} >&2
exit 2
