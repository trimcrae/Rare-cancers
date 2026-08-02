#!/usr/bin/env bash
# WHICH TESTS READ THIS WORKFLOW — run before editing any workflow, and run what it prints.
#
# ⛔ WHY THIS EXISTS, and it is a procedural failure rather than a code one. On 2026-08-01 two workflow
# conversions were pushed after running "the test files I could think of", and both went red in CI:
#
#   selectivity-control-vast.yml  -> 3 assertions in test_selcal_launch.py on the removed shell. That file
#                                    is run by the lane's PRE-RENTAL guards step, so the next `launch`
#                                    failed at the guard and five units went un-replaced.
#   gpu-fanout-rep-gcp.yml        -> 4 assertions in test_gcp_fanout_rep.py. Pushed red twice, because the
#                                    three workflow-READING test files had been run and the LANE'S OWN
#                                    had not.
#
# Both were findable in one grep. The tests were not wrong — this repo pins workflow shell deliberately, so
# a workflow edit legitimately trips guards elsewhere — the mistake was choosing which tests to run from
# memory instead of from a search.
#
# ⚠ IT TAKES A MODULE TOO, AND THAT GAP COST A THIRD RED PUSH (2026-08-02). The first version resolved
# WORKFLOWS only. Moving suppression from `selcal_vast_launch.mode_collect` into `selcal_gate` is a MODULE
# change, so the helper had nothing to say about it — and two tests that grepped `mode_collect`'s source for
# `tier_suppressed` went red in CI after a local run of the workflow-resolved set had passed. A helper whose
# scope silently excludes the kind of change you just made is the same defect as a guard that cannot see
# python publishers: it answers confidently about the half it covers.
#
# Usage:
#   research/compute/tests_reading_workflow.sh gpu-ternary-fep-vast.yml     # a workflow
#   research/compute/tests_reading_workflow.sh selcal_gate.py               # a module
#   python3 -m pytest $(research/compute/tests_reading_workflow.sh selcal_gate.py) -q
#
# With no argument, prints the test files for EVERY workflow that has any, one line each.
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1
TESTS=research/modalities/tests

# ⚠ NAME-MATCHING ALONE UNDER-REPORTS, AND A HELPER THAT QUIETLY MISSES FILES IS WORSE THAN NO HELPER.
# `test_inflight_board_lanes.py` and `test_every_lane_remerges_the_board.py` read workflows they never
# NAME: one builds the path from `inflight_board.LANES`, the other globs the whole workflows directory and
# parses every file. Those are exactly the guards a lane conversion trips, so they are added unconditionally
# — a test that reads EVERY workflow reads this one.
_scanners() {
  grep -rl --include='*.py' \
    -e 'workflows.*glob\|glob.*workflows' \
    -e '\.github/workflows' \
    "$TESTS" 2>/dev/null | sort -u
}

_for_one() {
  local wf="${1%.yml}"; wf="${wf%.yaml}"; wf="$(basename "$wf")"
  { grep -rl --include='*.py' -e "$wf\.ya\?ml" -e "\"$wf\"" -e "'$wf'" "$TESTS" 2>/dev/null
    _scanners; } | sort -u
}

# A MODULE's dependents are the tests that import or name it — a different question from a workflow's, and
# asking the wrong one is what let the last regression through.
_for_module() {
  local m="$(basename "${1%.py}")"
  grep -rl --include='*.py' -e "\\b$m\\b" "$TESTS" 2>/dev/null | sort -u
}

if [ $# -ge 1 ]; then
  case "$1" in
    *.py) out="$(_for_module "$1")" ;;
    *)    out="$(_for_one "$1")" ;;
  esac
  if [ -z "$out" ]; then
    # ⚠ EMPTY IS A RESULT, NOT A PASS. Say so, so "no output" is never read as "nothing to run".
    echo "# no test file references $1 — that is itself worth a look before editing it" >&2
    exit 0
  fi
  echo "$out"
  exit 0
fi

for f in .github/workflows/*.yml; do
  n="$(_for_one "$f" | wc -l | tr -d ' ')"
  [ "$n" = 0 ] || printf '%-44s %s\n' "$(basename "$f")" "$n test file(s)"
done
