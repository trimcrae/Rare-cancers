#!/bin/bash
# ⛔⛔ THE THIRD ATTEMPT AT "ENDED THE TURN WITH NOTHING RUNNING AND KNOWN WORK LEFT", AND THE FIRST
# ONE THAT IS NOT A CHECKER.
#
# trimcrae, 2026-08-27, on the third occurrence: "Another case of ending with nothing in flight while
# knowing what unblocked work comes next. This is a bug we tried to fix before. Let's try again."
#
# ★ WHY THE FIRST TWO FAILED, WHICH IS THE WHOLE ARGUMENT FOR THIS FILE:
#   v1 `continuity.py` asked "is the work WRITTEN DOWN?", answered yes, and printed a green tick next
#     to the failure. The tick got cited as permission to stop.
#   v2 removed the green state and asked "is the work MOVING?". It answered correctly — 93 items ready
#     — AND THE TURN STILL ENDED. Measured the same day.
# ⛔ So v2's diagnosis was right and its DELIVERY was wrong. A checker only binds if it is consulted
# at the moment of stopping, and that is precisely the moment it does not get consulted: the reply
# has been written, the work feels finished, and running one more command is not part of writing a
# summary. **Both attempts built something to remember. The thing that was missing was something
# that does not need remembering.**
#
# ★★ THIS IS A `Stop` HOOK, WHICH IS THE ONE MECHANISM IN THIS ENVIRONMENT WITH A PROVEN RECORD.
# `~/.claude/stop-hook-git-check.sh` fired at the end of nearly every turn of a very long session and
# was acted on EVERY time, without once being remembered in advance — because the harness runs it, not
# the agent. This file copies that shape deliberately, down to the stderr + `exit 2` convention.
#
# ⚠ IT DOES NOT BLOCK, AND THAT IS A DESIGN DECISION RATHER THAN A LIMITATION. `stop_hook_active`
# makes it fire ONCE per stop; the second stop passes. So it cannot trap a session, cannot stop
# trimcrae reaching the agent, and cannot turn into a wall when the honest answer is "these are
# running" or "this needs you". It makes the state UNAVOIDABLE at the stopping moment, which is all
# the git hook ever did and all it needed to do.
#
# ⛔ WHAT IT DELIBERATELY DOES NOT DO: decide whether the work should continue. It cannot see a
# subagent, a dispatched workflow or a spawned session, and a flag for the agent to declare that
# would be one more self-issued permission slip — the exact shape of the v1 failure. It reports what
# is ready and names it; the agent then either starts it, or says which of the three honest endings
# applies (something IS running, an item is genuinely blocked on a human or the outside world, or the
# list is empty).

set -uo pipefail

input=$(cat 2>/dev/null || echo '{}')

# ⛔ RECURSION GUARD, COPIED FROM THE GIT HOOK AND LOAD-BEARING. Without it the hook re-fires on the
# stop it just caused and the session cannot end at all.
if command -v jq >/dev/null 2>&1; then
  if [[ "$(echo "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)" == "true" ]]; then
    exit 0
  fi
fi

REPO="${CLAUDE_PROJECT_DIR:-/home/user/Rare-cancers}"
CONTINUITY="$REPO/research/autonomy/continuity.py"
[[ -f "$CONTINUITY" ]] || exit 0

# ⚠ A HOOK THAT CANNOT RUN MUST BE SILENT, NOT NOISY. If the interpreter or the ledger is missing,
# saying nothing is right: the alternative is a hook that cries wolf at every turn end and gets
# tuned out, which is how the repository lost the value of several guards already.
out=$(cd "$REPO" && timeout 25 python3 "$CONTINUITY" --check --limit 5 2>/dev/null)
rc=$?
[[ $rc -eq 1 ]] || exit 0

{
  echo "$out"
  echo
  echo "⛔ THE TURN IS ENDING WITH READY WORK AND, AS FAR AS ANYTHING CAN TELL, NOTHING RUNNING."
  echo "   This has now happened three times. Two previous fixes were CHECKERS and both failed —"
  echo "   v1 printed a green tick over the failure, v2 reported it correctly and was not consulted."
  echo "   This is a Stop hook because the harness runs it whether or not anyone remembers to."
  echo
  echo "★ ONE OF THESE IS TRUE, AND THE REPLY SHOULD SAY WHICH:"
  echo "   1. Something IS running that this cannot see — a subagent, a dispatched workflow, a"
  echo "      spawned session. Then say so on the in-flight board and this is a false alarm."
  echo "   2. An item above is genuinely blocked on trimcrae or the outside world. Then say which"
  echo "      and why — CLAUDE.md §0: \"'Blocked' is a claim that needs evidence, and it is usually"
  echo "      wrong.\""
  echo "   3. Neither. Then START ONE — the list is ranked, the top row is the answer, and"
  echo "      research-loop §3 gives the shape (this session, parallel subagents, or a spawn)."
  echo
  echo "⛔ A SCHEDULED ROUTINE IS NOT AN ANSWER. trimcrae, 2026-08-27: \"that's more of a backup to"
  echo "   make sure things never get stale, not a reason to intentionally stall.\" Naming a future"
  echo "   scheduler is a deferral with a citation, not continuation."
  echo
  echo "⚠ This fires ONCE per stop. It will not fire again on the next stop, so it cannot trap the"
  echo "   session — but it also will not ask twice. Answer it now."
} >&2
exit 2
