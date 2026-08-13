#!/usr/bin/env bash
# PROGRESS monitor for the fanned-out ASO junction screens. Not a liveness ping.
#
# ⛔ THE DISTINCTION IS THE WHOLE POINT (CLAUDE.md §4). "Still in_progress" is a liveness ping and it
# is worth nothing: a job wedged on a BLAST poll that will never return reports exactly the same
# thing as one screening its fourth junction. A PROGRESS check asks whether the work ADVANCED since
# the last look — here, whether each run's current step changed, and how long it has sat where it is.
# Two consecutive checks with no movement on a run that should be cycling through junctions every
# few minutes is a stall, and a stall is a thing to diagnose rather than to wait out.
#
# ⚠ AND THE JOBS API LAGS, WHICH MANUFACTURES FAKE STALLS. It has reported a finished 3-minute step
# as `in_progress` for ~18 minutes. So elapsed-in-step is reported, never asserted on: this prints
# what it sees and flags what has not moved, and a human or the calling agent decides. It does not
# cancel anything.
#
# ⚠ NCBI IS THE SHARED RESOURCE HERE, NOT THE RUNNER. Each job submits at most one BLAST query per
# 3 s (SUBMIT_SPACING_S); six concurrent jobs is therefore ~2 requests/second in aggregate against
# NCBI's URL API from shared GitHub runner IPs. That is the reason this fan-out is six wide and not
# twenty-two: the wall-clock win from more shards is real, and so is the risk of being throttled,
# which would slow every shard at once. If runs start failing at the submit step rather than the
# poll step, throttling is the first hypothesis.
#
#   ./scripts/watch_aso_screens.sh            # one pass
#   ./scripts/watch_aso_screens.sh --loop 6   # every 6 minutes until all runs finish
set -uo pipefail
cd "$(dirname "$0")/.."

REPO=trimcrae/Rare-cancers
STATE=${TMPDIR:-/tmp}/aso-screen-progress.state
IDS_FILE=${ASO_RUN_IDS_FILE:-}

ids() {
  if [ -n "$IDS_FILE" ] && [ -f "$IDS_FILE" ]; then cat "$IDS_FILE"; return; fi
  curl -s "https://api.github.com/repos/$REPO/actions/workflows/aso-offtarget.yml/runs?per_page=12" \
    | python3 -c "
import sys,json
for r in json.load(sys.stdin).get('workflow_runs',[]):
    if r['status'] in ('queued','in_progress'):
        print(r['id'])
"
}

pass() {
  local now active=0 moved=0 stuck=0
  now=$(TZ=America/New_York date '+%-I:%M %p ET')
  printf '\n[%s] ASO screen progress\n' "$now"
  touch "$STATE"
  for id in $(ids); do
    read -r status step elapsed junctions <<<"$(curl -s "https://api.github.com/repos/$REPO/actions/runs/$id/jobs" | python3 -c "
import sys,json,datetime
d=json.load(sys.stdin)
js=d.get('jobs') or []
if not js: print('unknown - - -'); raise SystemExit
j=js[0]; cur='-'; el='-'
for s in j.get('steps',[]):
    if s.get('status')=='in_progress':
        cur=str(s.get('number'))
        t=s.get('started_at')
        if t:
            t=datetime.datetime.fromisoformat(t.replace('Z','+00:00'))
            el=f\"{(datetime.datetime.now(datetime.timezone.utc)-t).total_seconds()/60:.0f}m\"
        break
else:
    done=[s for s in j.get('steps',[]) if s.get('status')=='completed']
    cur=str(len(done))
print(j.get('status','?'), cur, el, '-')
" 2>/dev/null)"
    [ -z "${status:-}" ] && status=unreachable
    active=$((active+1))
    prev=$(grep "^$id " "$STATE" 2>/dev/null | awk '{print $2}')
    mark=""
    if [ "$prev" = "$step" ]; then mark="  ⟲ no step change since last check"; stuck=$((stuck+1))
    elif [ -n "$prev" ]; then mark="  ✓ advanced"; moved=$((moved+1)); fi
    printf '  %s  %-12s step %-4s in-step %-5s%s\n' "$id" "$status" "$step" "$elapsed" "$mark"
    grep -v "^$id " "$STATE" > "$STATE.tmp" 2>/dev/null || true
    echo "$id $step" >> "$STATE.tmp"; mv "$STATE.tmp" "$STATE"
  done
  if [ "$active" = 0 ]; then printf '  no active runs — all six have finished or been cancelled\n'; return 1; fi
  printf '  %d active · %d advanced · %d unchanged since last check\n' "$active" "$moved" "$stuck"
  # ⚠ REPORTED, NOT ACTED ON. See the jobs-API lag note above.
  [ "$stuck" -gt 0 ] && printf '  ⚠ unchanged runs are not proof of a stall — the jobs API lags by up to ~18 min.\n'
  return 0
}

if [ "${1:-}" = "--loop" ]; then
  every=${2:-6}
  while pass; do sleep $((every*60)); done
  printf '\nall runs finished\n'
else
  pass
fi
