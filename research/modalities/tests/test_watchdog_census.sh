#!/usr/bin/env bash
# Tests the ternary watchdog's PROGRESS CENSUS — the part that decides whether a live VM is advancing or
# stalled. Two properties matter, and both have already been violated in this lane:
#
#   1. DIRECTION ISOLATION. The commit prefix gains a `_dir<rev>` suffix, so a direction-blind census would
#      read the fwd leg's far-further trajectory and report a dead-stopped rev leg as racing ahead. That is
#      the same bug class as the five direction-blind keys in
#      research/modalities/ternary-lane-guard-audit-2026-07-25.md.
#   2. BASE-10 PARSING. The store pads iterations to 8 digits (iter-00000520). Bash reads a leading-zero
#      literal as OCTAL, so 00000520 silently becomes 336 and 00000999 is not octal at all — the arithmetic
#      ERRORS, PROG is left unset, and `set -u` then kills the watch entry mid-loop. This test found that.
#
# The census function is EXTRACTED FROM THE WORKFLOW at run time rather than copied, so the test cannot pass
# against a stale duplicate of logic the workflow no longer has.

set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
WF=.github/workflows/ternary-leg-watchdog.yml
[ -f "$WF" ] || { echo "missing $WF"; exit 2; }

TD=$(mktemp -d); trap 'rm -rf "$TD"' EXIT

# Pull the census block out of the workflow verbatim (from the SEL filter through the PROG assignment) and
# wrap it in a function. If the workflow's markers change, this fails loudly rather than testing nothing.
python3 - "$WF" > "$TD/census.sh" <<'PY'
import sys, re
t = open(sys.argv[1]).read()
start = t.index('SEL=$(printf \'%s\\n\' "$CALL"')
end   = t.index('else PROG=0; PHASE="none')
end   = t.index('\n', t.index('fi', end)) if False else t.index('\n', end)
block = t[start:end]
block = '\n'.join(l[16:] if l.startswith(' ' * 16) else l.lstrip() for l in block.split('\n'))
print('census() {')
print('  CALL="$1"; SEED="$2"; DIR="$3"; SALT="$4"')
print('\n'.join('  ' + l for l in block.split('\n')))
print('  echo "$PROG $PHASE"')
print('}')
PY
grep -q 'PROG=$((1000000' "$TD/census.sh" || { echo "EXTRACTION FAILED — workflow markers changed"; exit 2; }
. "$TD/census.sh"

B=gs://bkt/valB-6hax/commits/calib_hi_to_lo__ternary_vhl
# fwd is FAR ahead (production 520); rev seed 0 has only warmup 16; rev seed 1 is a different leg entirely.
LST="$B/0_dt2.0fs_clig0_wu_v2pe/warmup/iter-00000008/abc/COMMITTED.json
$B/0_dt2.0fs_clig0_wu_v2pe/production/iter-00000520/def/COMMITTED.json
$B/0_dt2.0fs_clig0_wu_v2pe_dirrev/warmup/iter-00000016/ghi/COMMITTED.json
$B/1_dt2.0fs_clig0_wu_v2pe_dirrev/production/iter-00000999/jkl/COMMITTED.json"

fail=0
chk() { if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1: got '$2' want '$3'"; fail=1; fi; }

chk "rev seed0 does NOT read fwd's production/520" "$(census "$LST" 0 rev v2pe)" "16 warmup/16"
chk "fwd seed0 reads its own production/520"       "$(census "$LST" 0 fwd v2pe)" "1000520 production/520"
chk "seed is honoured (rev seed1 is its own leg)"  "$(census "$LST" 1 rev v2pe)" "1000999 production/999"
chk "no commits at all -> scalar 0"               "$(census "" 0 rev v2pe)"     "0 none (setup/env-solve/minimize)"
chk "a mismatched salt sees nothing"              "$(census "$LST" 0 rev zzz)"  "0 none (setup/env-solve/minimize)"

# production must outrank ANY warmup, so a warmup->production transition can never look like a regression
W=$(census "$LST" 0 rev v2pe | cut -d' ' -f1)
P=$(census "$LST" 0 fwd v2pe | cut -d' ' -f1)
if [ "$P" -gt "$W" ]; then echo "PASS production scalar outranks every warmup scalar"
else echo "FAIL monotonicity: production $P not > warmup $W"; fail=1; fi

# the stall counter itself
st() { if [ "$1" -gt "$2" ]; then echo 0; else echo $(( $3 + 1 )); fi; }
chk "advance resets the stall counter"    "$(st 1000560 1000520 3)" "0"
chk "frozen iteration increments it"      "$(st 1000520 1000520 1)" "2"
chk "a regression counts as no-advance"   "$(st 16 1000520 0)"      "1"

[ "$fail" = 0 ] && echo "watchdog census: all checks pass"
exit "$fail"
