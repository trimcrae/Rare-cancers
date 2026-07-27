#!/usr/bin/env bash
# A DONE leg must not leave a VM holding the project's only GPU.
#
# WHAT WENT WRONG, measured 2026-07-27 on gcp-ternary-30215419909 (us-central1-a). The leg finished
# ("[barrier] committed checkpoint at iteration 2000/2000", then "[tfep] LEG DONE ... ΔG_morph=-47.79"),
# the startup script's EXIT trap ran, and its delete failed:
#
#   ERROR: (gcloud.compute.instances.delete) Could not fetch resource:
#    - Required 'compute.instances.delete' permission for '.../instances/gcp-ternary-30215419909'
#
# The VM then sat RUNNING and idle, holding GPUS_ALL_REGIONS=1 — which blocks EVERY other GCP GPU job on
# the account — until a human noticed. The watchdog's DONE branch had seen the leg finish (it dispatched
# mode=converge) and had `continue`d without ever looking at the VM list: the reap lived only in the
# CRASHED branch, which a DONE leg can never reach.
#
# HOW THIS TEST WORKS. It EXTRACTS the DONE branch out of watchdog_run.sh at run time and RUNS it against
# a stubbed `gcloud`/`gh` on PATH, so it fails unless a delete is actually issued. A test that asserted on
# the source text would pass on a rewrite that reads correctly and deletes nothing. Verified to
# discriminate by deleting the reap block: case 1 then fails with 0 deletes.

set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
WF=research/modalities/watchdog_run.sh
[ -f "$WF" ] || { echo "missing $WF"; exit 2; }

TD=$(mktemp -d); trap 'rm -rf "$TD"' EXIT
fail=0
chk() { if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1:"; echo "       got  '$2'"; echo "       want '$3'"; fail=1; fi; }

# ---- extract the DONE branch verbatim, from its `if gcloud storage ls "$RESULTS/...` guard to its
# ---- closing `continue`. Markers changing is a loud failure, not a silently-empty test.
python3 - "$WF" > "$TD/done.sh" <<'PY'
import sys, textwrap
t = open(sys.argv[1]).read()
guard = 'if gcloud storage ls "$RESULTS/leg_${LEG}_${DIR}_r${SEED}.json"'
i = t.index(guard); i = t.rfind('\n', 0, i) + 1
j = t.index('\n', t.index('      continue\n', i))
block = textwrap.dedent(t[i:j])
print('done_branch() {')
print('\n'.join('  ' + l for l in block.split('\n')))
print('  fi')          # the extracted slice stops at `continue`, before the branch's own `fi`
print('}')
PY
grep -q 'instances delete' "$TD/done.sh" || { echo "EXTRACTION FAILED — the DONE branch contains no delete (that IS the bug)"; exit 1; }
bash -n "$TD/done.sh" || { echo "EXTRACTION FAILED — extracted block does not parse"; exit 2; }

# ---- stub gcloud: records every `compute instances delete`, answers `storage ls` from $GCS_PRESENT.
mkdir -p "$TD/bin"
cat > "$TD/bin/gcloud" <<'STUB'
#!/usr/bin/env bash
case "$1 $2" in
  "storage ls")
    for k in $GCS_PRESENT; do case "$3" in *"$k"*) exit 0;; esac; done; exit 1 ;;
  "storage cp") exit 0 ;;
  "compute instances")
    case "$3" in
      list)   echo "$STUB_ZONE" ;;
      delete) echo "$4" >> "$DELETED"; [ "${DELETE_RC:-0}" = 0 ] || { echo "ERROR: forced" >&2; exit 1; }; exit 0 ;;
    esac ;;
esac
exit 0
STUB
cat > "$TD/bin/gh" <<'STUB'
#!/usr/bin/env bash
exit 0
STUB
chmod +x "$TD/bin/gcloud" "$TD/bin/gh"
PATH="$TD/bin:$PATH"; export PATH

run_case() {
  DELETED="$TD/deleted"; : > "$DELETED"; export DELETED
  export STUB_ZONE=us-central1-a DELETE_RC="${DELETE_RC:-0}"
  RESULTS=gs://bkt/valB-6hax/results WDIR=gs://bkt/valB-6hax/watchdog
  LEG=calib_hi_to_lo__ternary_vhl SEED=0 DIR=rev SALT=v2pe DT=2.0 WUDT=1.0 UPE=1
  TAG="$LEG dir=$DIR seed=$SEED" WATCH_REF=main ALERT="$TD/alert"; : > "$ALERT"
  VMS="$1" ; NVM=$(printf '%s' "$VMS" | tr -d '[:space:]' | wc -c | tr -dc '0-9'); NVM=${NVM:-0}
  DRY="$2"; GCS_PRESENT="$3"
  export RESULTS WDIR LEG SEED DIR SALT DT WUDT UPE TAG WATCH_REF ALERT VMS NVM DRY GCS_PRESENT
  . "$TD/done.sh"
  done_branch >"$TD/out" 2>&1
  wc -l < "$DELETED" | tr -d ' '
}

# 1. THE REGRESSION ITSELF: leg result present, VM still up -> the VM must be deleted.
chk "done leg + live VM -> VM is deleted" \
    "$(DELETE_RC=0 run_case 'gcp-ternary-30215419909 RUNNING' 0 'leg_calib_hi_to_lo__ternary_vhl_rev_r0.json')" "1"

# 2. no VM alive -> nothing to delete, and the branch must not invent one.
chk "done leg + no VM -> no delete attempted" \
    "$(DELETE_RC=0 run_case '' 0 'leg_calib_hi_to_lo__ternary_vhl_rev_r0.json')" "0"

# 3. dry_run must be honest: report, do not act.
chk "dry_run=1 -> reports but does not delete" \
    "$(DELETE_RC=0 run_case 'gcp-ternary-30215419909 RUNNING' 1 'leg_calib_hi_to_lo__ternary_vhl_rev_r0.json')" "0"

# 4. a FAILED delete must be loud and must name the reason, not print a shrug. This is the property the
#    in-VM trap lacked: "self-delete no-op (already gone / no perm)" covered two opposite outcomes.
DELETE_RC=1 run_case 'gcp-ternary-30215419909 RUNNING' 0 'leg_calib_hi_to_lo__ternary_vhl_rev_r0.json' >/dev/null
if grep -q '::error title=WATCHDOG REAP FAILED' "$TD/out" && grep -q 'DONE-REAP FAILED' "$TD/alert"; then
  echo "PASS a failed reap raises ::error AND trips the alert file"
else
  echo "FAIL a failed reap must raise ::error and trip \$ALERT; got:"; sed 's/^/       /' "$TD/out"; fail=1
fi

# 5. the reap must run BEFORE the converge/reduce dispatch chain, so a finished leg frees the GPU on the
#    same pass it is reduced — not one pass later, and not never if a dispatch fails first.
python3 - "$TD/done.sh" <<'PY' || fail=1
import sys
t = open(sys.argv[1]).read()
d, c = t.index('instances delete'), t.index('mode=converge')
print("PASS reap precedes the converge dispatch" if d < c else "FAIL reap must precede the converge dispatch")
sys.exit(0 if d < c else 1)
PY

exit $fail
