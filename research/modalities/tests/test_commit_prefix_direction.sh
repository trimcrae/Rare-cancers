#!/usr/bin/env bash
# The spot commit prefix MUST carry the direction. A rev leg that resumes the forward trajectory is a silent
# wrong answer -- it reports forward sampling as reverse -- and on 2026-07-25 it happened for real.
#
# THE MECHANISM, because it is subtle enough to be reintroduced. The VM startup script is built with an
# UNQUOTED heredoc (`cat > /tmp/startup.sh <<SS`). In an unquoted heredoc, unescaped $VAR is expanded by the
# RUNNER as the script is written; \$VAR survives into the file and is expanded later by the VM. The old code
# did this:
#
#     DIRSUF=""; [ "$DIRECTION" != fwd ] && DIRSUF="_dir$DIRECTION"        # inside the heredoc -> runs on the VM
#     COMMIT_ENV="...wu${WARMUP_TS}${SALT:+_$SALT}${DIRSUF} ..."           # ${DIRSUF} unescaped -> runner expands
#
# so DIRSUF was assigned in the VM's shell and read in the runner's, where it had never been assigned. It
# expanded to empty, the suffix vanished, and nothing errored. Every other component (SEED, TIMESTEP_FS,
# WARMUP_TS, SALT) is a runner-level env: var, which is why DIRSUF was the only one that disappeared.
#
# This test asserts on the WORKFLOW TEXT, because that is where the defect lives -- there is no cheap way to
# run the generator itself, and a review-level "it looks right" is exactly what let this ship.

set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
WF=.github/workflows/gpu-ternary-fep-gcp.yml
[ -f "$WF" ] || { echo "missing $WF"; exit 2; }

fail=0
chk() { if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1: got '$2' want '$3'"; fail=1; fi; }

HD_LINE=$(grep -n 'cat > /tmp/startup.sh <<' "$WF" | head -1 | cut -d: -f1)
chk "the startup heredoc is still found" "$([ -n "$HD_LINE" ] && echo yes)" "yes"

# 1. DIRSUF must be assigned BEFORE the heredoc (runner-side), not inside it (VM-side).
ASSIGN_LINES=$(grep -nE '^[[:space:]]*DIRSUF=' "$WF" | cut -d: -f1)
chk "DIRSUF is assigned exactly once" "$(printf '%s\n' "$ASSIGN_LINES" | sed '/^$/d' | wc -l | tr -d ' ')" "1"
chk "DIRSUF is assigned in the RUNNER (before the heredoc)" \
    "$([ "${ASSIGN_LINES:-999999}" -lt "$HD_LINE" ] && echo before || echo inside)" "before"

# 2. The prefix must be built runner-side and verified.
chk "a full COMMIT_PREFIX is built runner-side" \
    "$(awk -v h="$HD_LINE" 'NR<h && /^[[:space:]]*COMMIT_PREFIX=/{c++} END{print c+0}' "$WF")" "1"
chk "the direction is ASSERTED before provisioning" \
    "$(grep -c 'COMMIT PREFIX LOST THE DIRECTION' "$WF")" "1"

# 3. No part of the prefix may be deferred to a VM-side shell assignment again. Inside the heredoc, the
#    RBFE_SPOT_COMMIT_GCS value must be the finished literal $COMMIT_PREFIX and nothing else.
CE=$(grep -n 'RBFE_SPOT_COMMIT_GCS=' "$WF" | head -1)
CE_TEXT=${CE#*:}
case "$CE_TEXT" in
  *'RBFE_SPOT_COMMIT_GCS=$COMMIT_PREFIX'*) echo "PASS the commit env uses the finished runner-side prefix" ;;
  *) echo "FAIL the commit env rebuilds the prefix inline: $CE_TEXT"; fail=1 ;;
esac
case "$CE_TEXT" in
  *'${DIRSUF}'*|*'$DIRSUF'*) echo "FAIL the commit env still interpolates DIRSUF (the two-shell bug)"; fail=1 ;;
  *) echo "PASS the commit env does not interpolate DIRSUF" ;;
esac

# 4. The echo must print the FULL prefix. The old one stopped at $SEED, so the missing suffix was invisible
#    in the workflow's own log and only showed up in the Python's line.
if grep -q 'spot-safe commit store: \$COMMIT_PREFIX' "$WF"; then
  echo "PASS the log line prints the FULL prefix"
else
  echo "FAIL the log line does not print the full prefix (a truncated echo hid this bug once)"; fail=1
fi

# 5. Behavioural check on the suffix rule itself: fwd stays bare so existing prefixes keep resuming.
sfx() { D="$1"; S=""; [ "$D" != fwd ] && S="_dir$D"; printf '%s' "$S"; }
chk "fwd gets NO suffix (existing prefixes stay byte-identical)" "$(sfx fwd)" ""
chk "rev gets _dirrev"                                          "$(sfx rev)" "_dirrev"

[ "$fail" = 0 ] && echo "commit-prefix direction: all checks pass"
exit "$fail"
