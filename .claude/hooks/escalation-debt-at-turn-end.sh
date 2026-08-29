#!/bin/bash
# ⛔⛔ A DECISION PARKED IN AN UNMONITORED SESSION HAS NOT BEEN ESCALATED. IT HAS BEEN LOST.
#
# trimcrae, 2026-08-29, on a turn that ended with "still only yours: AUT-044": "It makes it seem
# like you're expecting a response from me in a session. If you need my attention for a decision
# that you are truly incapable of making yourself, it needs to be a real notification and not in an
# unmonitored session. That's a process that needs codifying if it doesn't already exist."
#
# ★ IT DID ALREADY EXIST, AND THAT IS THE POINT. CLAUDE.md §3: "📱 Notify in the SAME TURN (trimcrae
# routes these elsewhere and is often away): ALWAYS PushNotification ... and unless there is nothing
# to decide, AskUserQuestion." The rule was written, correct, and measured by nothing — so a session
# could name an item as his three times in one conversation, never send anything, and look diligent
# while doing it. Same failure class as the merge-to-main rule the sibling hook now enforces.
#
# ⚠ MEASURED THE SAME DAY: FOURTEEN ledger rows carry `requires_trimcrae: true`, not one. The
# highest (AUT-046, 174.0) outranks every item the loop's own workers were taking, and one
# (AUT-PROP-041) is on a CLOCK — the Vancouver standard consultation closes 2026-10-16. A decision
# that expires unnoticed is the worst shape this failure takes, because nothing goes red when the
# date passes; the row simply stops mattering.
#
# ★★ WHAT IT CHECKS, AND WHY THIS IS A RECORD RATHER THAN A FLAG. Each `requires_trimcrae` row must
# carry `notified_utc` — when it was last actually put in front of him. That is a FALSIFIABLE
# statement about an outbound act, not a self-issued "I intend to tell him": it names a date that
# either happened or did not, and a row still open long after its last notice is still failing.
# ⛔ Writing `notified_utc` without sending anything is not a loophole, it is a false record — the
# same status as a fabricated receipt or an invented in-flight row, and it fails for the same reason.
#
# ⛔⛔ IT SURFACES ONE DECISION, NOT THE BACKLOG (trimcrae, 2026-08-29: *"We can't possibly address
# all of them at once so only notify me when there's a decision that's actually ready to be acted
# on, both in terms of priority and bandwidth"*). ⚠ The first version of this hook printed all
# fourteen and told the session to send them. That is the same defect one layer up: a guard that
# dumps a backlog gets tuned out, and this repository has already lost the value of several guards
# exactly that way. His attention is the scarce resource the hook is spending, so it spends ONE
# unit: the single highest-ranked undelivered decision. The rest stay recorded and invisible until
# that one is answered — which is what "bandwidth" means operationally.
# ★ AND THE FILTER IS PRIORITY-ORDERED, NOT AGE-ORDERED: the top row by score is the one worth his
# attention now, and a stale low-scoring row does not jump the queue by having waited.
#
# ⛔ WHY A `Stop` HOOK. Two checkers have already failed at this class in this repository (one
# printed a green tick over the failure, one was never consulted), and the stopping moment is
# exactly when nobody runs one more command. The harness runs a Stop hook whether or not anyone
# remembers to. Fires once per stop, so it cannot trap a session.

set -uo pipefail
input=$(cat 2>/dev/null || echo '{}')
if command -v jq >/dev/null 2>&1; then
  [[ "$(echo "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)" == "true" ]] && exit 0
fi

REPO="${CLAUDE_PROJECT_DIR:-/home/user/Rare-cancers}"
cd "$REPO" 2>/dev/null || exit 0
# ⛔⛔ READ THE TRUNK, NOT THE WORKING TREE — MEASURED 2026-08-29, BY THIS HOOK FAILING THAT WAY ON
# ITS FIRST DAY. It reported FOURTEEN decisions parked on trimcrae that had ALREADY been cleared on
# `main` by another session; the reporting session simply held a stale local copy. A guard that
# invents escalations is worse than none — it spends his attention on decisions nobody needs made,
# which is the exact currency this hook exists to protect. The ledger is shared state written by
# many concurrent sessions, so the only honest reading of "what is still open" is the pushed one.
# ⚠ Falls back to the working tree only when origin/main is unreadable, and says nothing either way
# rather than guessing.
LEDGER_JSON=$(git show origin/main:research/autonomy/research-ledger.json 2>/dev/null)
if [ -z "$LEDGER_JSON" ]; then
  [ -f "research/autonomy/research-ledger.json" ] || exit 0
  LEDGER_JSON=$(cat research/autonomy/research-ledger.json)
fi

OUT=$(printf '%s' "$LEDGER_JSON" | python3 - <<'PYEOF'
import json, sys, datetime
STALE_DAYS = 7
try:
    rows = json.load(sys.stdin)
except Exception:
    sys.exit(0)
rows = rows if isinstance(rows, list) else (rows.get("entries") or [])
now = datetime.datetime.now(datetime.timezone.utc)

# ⭐ A DATED DECISION OUTRANKS A HIGHER-SCORING ONE ONCE IT IS INSIDE ITS LEAD TIME (trimcrae,
# 2026-08-29, choosing "hard-fail the gate as the date nears"). Score ordering is the right default
# and the wrong one here: a row that expires cannot wait for a busier row to clear, and nothing goes
# red when the date passes — the row just quietly stops mattering, which is the worst shape this
# failure takes. `expires_utc` makes the deadline machine-readable; EXPIRY_LEAD_DAYS is when it
# starts shouting.
EXPIRY_LEAD_DAYS = 45
never, stale, dated = [], [], []
for e in rows:
    if not isinstance(e, dict) or not e.get("requires_trimcrae"):
        continue
    if e.get("closed_utc") or e.get("status") in ("closed", "done"):
        continue
    n = e.get("notified_utc")
    row = (e.get("score") or 0, e.get("id", "?"), str(e.get("what") or "")[:88])
    exp = e.get("expires_utc")
    if exp:
        try:
            left = (datetime.datetime.fromisoformat(str(exp).replace("Z", "+00:00")) - now).days
            if left <= EXPIRY_LEAD_DAYS:
                dated.append((left, e.get("id", "?"), str(e.get("what") or "")[:88], exp))
        except Exception:
            pass
    if not n:
        never.append(row); continue
    try:
        age = (now - datetime.datetime.fromisoformat(str(n).replace("Z", "+00:00"))).days
    except Exception:
        never.append(row); continue
    if age >= STALE_DAYS:
        stale.append(row + (age,))

# ⛔ ONE AT A TIME, AND AN OUTSTANDING ONE SUPPRESSES THE REST. If something has already been put
# to him and is still open, sending a second competes with the first for the same attention. The
# queue is not lost — it is recorded in the ledger and it will surface as each is answered.
if dated:
    left, i, w, exp = sorted(dated)[0]
    when = "has EXPIRED" if left < 0 else f"expires in {left} day(s)"
    print(f"⛔⛔ A DATED decision {when} ({exp}) and outranks everything else:\n"
          f"   {i}  {w}\n"
          f"   Send this one, whatever its score. A decision that lapses is not deferred, it is void,"
          f" and nothing else goes red when the date passes.")
    sys.exit(0)
if stale:
    s, i, w, a = sorted(stale, reverse=True)[0]
    print(f"⚠ A decision has been with trimcrae {a} days and is still open — do NOT send another "
          f"until it resolves.\n   [{s:.1f}] {i}  {w}\n"
          f"   {len(never)} more are recorded and deliberately NOT being surfaced yet.")
    sys.exit(0)
if not never:
    sys.exit(0)

s, i, w = sorted(never, reverse=True)[0]
print(f"⛔ ONE decision is ready for trimcrae and has never been sent:\n"
      f"   [{s:.1f}] {i}  {w}\n"
      f"   ({len(never)-1} others are parked and are deliberately NOT listed — his bandwidth is the "
      f"scarce resource, and the top row is the only one worth spending it on now.)")
PYEOF
)
[ -z "$OUT" ] && exit 0

{
  echo "$OUT"
  echo
  echo "⛔⛔ NAMING ONE OF THESE IN A REPLY IS NOT ESCALATING IT. He routes notifications elsewhere"
  echo "   and is often away; a decision that lives only in session text is a decision he never"
  echo "   sees. CLAUDE.md §3: notify in the SAME TURN — ALWAYS PushNotification (status: proactive,"
  echo "   one line, <200 chars, no markdown), AND AskUserQuestion unless there is nothing to decide."
  echo
  echo "★ DO THIS NOW, IN THIS TURN:"
  echo "   1. Send THAT ONE — PushNotification, plus AskUserQuestion if there is a real fork."
  echo "      Do not bundle the others in with it; they are suppressed on purpose."
  echo "   2. Stamp \`notified_utc\` on that row, and push. That is what makes the claim"
  echo "      falsifiable and what stops this firing again."
  echo "   ⛔ Stamping a row you did NOT send is a false record, not a workaround — the same status"
  echo "      as a fabricated receipt."
  echo
  echo "⚠ Skip ONLY if trimcrae is chatting right now (§3's one exemption) — and if so, put the"
  echo "   decision in THIS reply as a real question, not as a closing remark he has to notice."
  echo
  echo "⚠ Fires once per stop."
} >&2
exit 2
