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
# ⛔⛔ A PARKED CLAIM IS CHECKED FIRST, BECAUSE IT IS THE FAILURE THAT LOOKS MOST LIKE PROGRESS
# (2026-08-27). A seat died on its first message; `ListAgents` reported it `running` for 2 h 36 m;
# the driver relayed that as "in flight" seven times while its claim on AUT-PROP-012 stayed open.
# trimcrae found it, not the loop. ⭐ THE SHAPE IS BORROWED: ARIS (15,294★, MIT) runs
# `tools/watchdog.py` as a SEPARATE process that watches STATE-FILE WRITES rather than pinging for
# liveness, and only ever reports. `research/method-watch-autonomy-prior-art.md` had ranked it hours
# earlier and nobody had read it.
# ⚠ AND IT BELONGS HERE RATHER THAN IN THE DRIVER'S HANDS FOR THE REASON THIS FILE ALREADY EXISTS:
# the driver cannot be the thing that notices the driver has stalled.
# ⛔ DERIVED, NOT READ FROM AN ENV VAR THAT DOES NOT EXIST. `CLAUDE_TASKS_DIR` is UNSET in this
# harness — checked, not assumed — so a branch guarded on it would never have fired, which is the
# unreachable-guard trap this repository hit three times on 2026-08-27 alone (the `--if-needed`
# early exit, the `os.path.exists` guard, and this). `CLAUDE_CODE_SESSION_ID` IS set, and the
# transcripts live at a path derivable from it. If the glob finds nothing the block is silent,
# because a watchdog that cannot see is not a watchdog that reports.
STALLED="$REPO/research/autonomy/stalled_holder.py"
TASKS_DIR=""
for _c in /tmp/claude-*/*/"${CLAUDE_CODE_SESSION_ID:-nope}"/tasks; do
  [[ -d "$_c" ]] && TASKS_DIR="$_c" && break
done
if [[ -f "$STALLED" && -n "$TASKS_DIR" ]]; then
  if held=$(cd "$REPO" && timeout 15 python3 "$STALLED" --tasks-dir "$TASKS_DIR" --check 2>/dev/null); then :; else
    { echo "$held"; echo; } >&2
  fi
fi

out=$(cd "$REPO" && timeout 25 python3 "$CONTINUITY" --check --limit 5 2>/dev/null)
rc=$?
[[ $rc -eq 1 ]] || exit 0

# ⛔⛔ THE FOURTH ANSWER, ADDED 2026-08-28 AFTER THIS HOOK RAN A SESSION NINE CYCLES DEEP.
# The three answers below are exhaustive only for a session that CAN hand off. A session fired by
# the driver Routine, already at `max_cycles_per_session`, whose `create_session` was refused at the
# platform's lineage-depth limit, has no legal answer among them — and the only move that satisfies
# this hook is to start ANOTHER cycle in the same context. Measured: CYC-0033 … CYC-0041, nine
# cycles in one session against a cap of 2, one receipt naming this hook in its own `shape` field.
# ⭐ AND THE LOOP SURVIVES WITHOUT THE HANDOFF: the Routine fires `13 */4 * * *`, so a capped
# session that stops is not stalling — the cron IS the successor. That is why "a scheduled Routine
# is not an answer" stays true below for a session that could still work, and is exactly wrong for
# one that cannot.
# ⛔ EARNED AND FALSIFIABLE, NEVER A FLAG: session_cap.py requires `cap` receipts FROM THIS SESSION
# plus a handoff attempted and blocked in the platform's own words. An absent record is a session
# that did not try and stays red. Every unreadable input answers MUST NOT STOP.
CAP_CHECK="$REPO/research/autonomy/session_cap.py"
if [[ -f "$CAP_CHECK" ]]; then
  if capline=$(cd "$REPO" && timeout 15 python3 "$CAP_CHECK" --check 2>/dev/null); then
    {
      echo "$out"
      echo
      echo "✅ THIS SESSION MAY STOP — and stopping is the CORRECT action, not a deferral."
      echo "   $capline"
      echo
      echo "★ The work above is real and stays queued. What ends here is THIS SESSION, not the loop:"
      echo "   the driver Routine fires on its own schedule and that firing IS the successor. Handing"
      echo "   off early is an optimisation the platform has refused; it was never what keeps the"
      echo "   loop alive."
      echo "⛔ DO NOT START ANOTHER CYCLE HERE. Past the cap a session compacts repeatedly and loses"
      echo "   the verdict — measured once at 23 compactions and a 7.6 MB transcript, and again as"
      echo "   the nine-cycle run this branch exists to end."
    } >&2
    exit 0
  fi
fi

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
  echo "      spawned session. Then say so on the in-flight board — AND CLAIM THE ITEM, so this"
  echo "      stops asking: set \`owner\` and \`claimed_utc\` on its ledger row. ⛔ A LEASE IS NOT A"
  echo "      PERMISSION SLIP — it names WHICH worker holds WHICH item, so it is falsifiable and it"
  echo "      is already how cross-session coordination works. ⚠ Measured 2026-08-27, the second"
  echo "      time this hook fired: two dispatched agents were unclaimed, so their items were still"
  echo "      being offered. A guard that cries wolf is a guard that gets tuned out — which is how"
  echo "      this repository has already lost the value of several. CLAIM AT DISPATCH, in the same"
  echo "      action that spawns the agent."
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
