#!/usr/bin/env bash
# The bounded orphan reap: a VM no ENABLED watch entry covers must still be retired when — and ONLY when —
# its own leg result is already in GCS.
#
# WHAT IT IS FOR. A GCP VM cannot delete itself: the in-VM EXIT trap runs and GCE refuses the call
# (`Required 'compute.instances.delete' permission`, measured 2026-07-27 on gcp-ternary-30215419909;
# research/compute/gcp-gpu-facts.md §6). The only reaper is the watchdog's DONE branch — and that branch is
# inside the loop over ENABLED entries, so `gcp_watch_reap` disabling a landed unit takes the reaper away with
# it. gcp-reap-vms.yml is not a backstop: it has no `schedule:`. So an unwatched detached leg ran to its
# create-time --max-run-duration (72 h on the on-demand branch) holding GPUS_ALL_REGIONS=1.
#
# WHY THIS TEST EXISTS IN THIS FORM. The dangerous direction is not "the sweep failed to reap" — that costs
# one more pass — it is "the sweep reaped something live", which costs hours of MD. So the cases below are
# weighted towards REFUSALS, and every one of them asserts that ZERO deletes were issued. The sweep is
# EXTRACTED from watchdog_run.sh and RUN against a stubbed gcloud, because a test that asserted on source text
# would pass on a rewrite that reads correctly and deletes the wrong box.

set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
WF=research/modalities/watchdog_run.sh
[ -f "$WF" ] || { echo "missing $WF"; exit 2; }

TD=$(mktemp -d); trap 'rm -rf "$TD"' EXIT
fail=0
chk() { if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1:"; echo "       got  '$2'"; echo "       want '$3'"; fail=1; fi; }

# ---- extract orphan_sweep() verbatim: from its definition to the first column-0 '}'.
python3 - "$WF" > "$TD/sweep.sh" <<'PY'
import sys
t = open(sys.argv[1]).read()
i = t.index('orphan_sweep() {')
j = t.index('\n}\n', i) + len('\n}\n')
sys.stdout.write(t[i:j])
PY
grep -q 'instances delete' "$TD/sweep.sh" || { echo "EXTRACTION FAILED — the sweep contains no delete (that IS the bug)"; exit 1; }
bash -n "$TD/sweep.sh" || { echo "EXTRACTION FAILED — extracted block does not parse"; exit 2; }

mkdir -p "$TD/bin"
# ---- stub gcloud. $LABELS_JSON is what `describe --format=json(...)` returns; $RESULT_TS is the result
# ---- object's write time ("" = the object does not exist).
cat > "$TD/bin/gcloud" <<'STUB'
#!/usr/bin/env bash
case "$1 $2" in
  "compute instances")
    case "$3" in
      list)
        # two shapes are asked for: the VM NAME list, and a single VM's zone
        case "$*" in
          *zone.basename*) echo "us-central1-a" ;;
          *) printf '%s\n' $VM_NAMES ;;
        esac ;;
      describe) printf '%s' "$LABELS_JSON" ;;
      delete)   echo "$4" >> "$DELETED"; [ "${DELETE_RC:-0}" = 0 ] || { echo "ERROR: forced" >&2; exit 1; }; exit 0 ;;
    esac ;;
  "storage ls")
    # `ls -l` is the timestamped form the sweep reads: "<size>  <RFC3339>  gs://..."
    # KEY-AWARE on purpose: $RESULT_KEYS lists the object names that EXIST, so a test can put the
    # unrestrained result in the bucket and leave the restrained one out — which is the real bucket's
    # state for the r0 binary arm and the exact way an unkeyed check reaps a leg that never ran.
    K="$3"; [ "$3" = "-l" ] && K="$4"
    [ -z "$RESULT_TS" ] && exit 1
    for want in $RESULT_KEYS; do
      case "$K" in *"$want"*) echo "     42  $RESULT_TS  $K"; exit 0 ;; esac
    done
    exit 1 ;;
esac
exit 0
STUB
chmod +x "$TD/bin/gcloud"
export PATH="$TD/bin:$PATH"

CFG="$TD/watch.json"
RESULTS="gs://bucket/valB-6hax/results"
DRY=0
ALERT="$TD/alert"
export CFG RESULTS DRY ALERT

# an empty watch list -> every VM is an orphan
cat > "$CFG" <<'J'
{"watch": []}
J

labels() {  # leg dir seed rst mode created
  printf '{"labels":{"lane":"ternary","tfep-leg":"%s","tfep-dir":"%s","tfep-seed":"%s","tfep-rst":"%s","tfep-mode":"%s"},"creationTimestamp":"%s"}' "$1" "$2" "$3" "$4" "$5" "$6"
}

run_sweep() {
  : > "$ALERT"; DELETED="$TD/deleted"; : > "$DELETED"; export DELETED
  # shellcheck disable=SC1090
  ( . "$TD/sweep.sh"; orphan_sweep ) > "$TD/out" 2>&1
}
ndel() { wc -l < "$TD/deleted" | tr -d ' '; }

# ============================ 1. THE ONE CASE THAT REAPS ============================
# labelled mode=run VM, its own result object is in GCS, and the VM was created BEFORE that result was
# written -> this VM produced it, there is no sampling left to lose, so it goes.
VM_NAMES="gcp-ternary-111"; export VM_NAMES
RESULT_KEYS="leg_"; export RESULT_KEYS          # every leg_*.json exists
LABELS_JSON=$(labels calib_hi_to_lo__ternary_vhl rev 0 0 run "2026-07-26T10:00:00.000-07:00"); export LABELS_JSON
RESULT_TS="2026-07-27T12:03:00Z"; export RESULT_TS
run_sweep
chk "finished, unwatched leg -> REAPED" "$(ndel)" "1"
grep -q 'REAPED AN ORPHANED FINISHED LEG' "$TD/out" || { echo "FAIL: no reap annotation"; fail=1; }

# ★ AND IT MUST RESOLVE THE RESTRAINT-KEYED RESULT, NOT THE BARE ONE. This is the single most dangerous
# mistake available here: the UNRESTRAINED r0 binary result is ALREADY in the bucket, so a sweep that
# dropped the `_rst` component would read it, call a restrained leg finished that had never started, and
# DELETE A LIVE GPU. Bucket state below is exactly that — bare result present, _rst absent.
RESULT_KEYS="leg_calib_hi_to_lo__binary_vhl_fwd_r0.json"; export RESULT_KEYS
LABELS_JSON=$(labels calib_hi_to_lo__binary_vhl fwd 0 1 run "2026-07-26T10:00:00.000-07:00"); export LABELS_JSON
run_sweep
chk "restrain=1 must NOT be reaped by the UNRESTRAINED result" "$(ndel)" "0"
# ...while restrain=0 on the very same leg, with the very same bucket, IS reaped — proving the refusal
# above came from the key and not from a blanket failure to find anything.
LABELS_JSON=$(labels calib_hi_to_lo__binary_vhl fwd 0 0 run "2026-07-26T10:00:00.000-07:00"); export LABELS_JSON
run_sweep
chk "restrain=0 on the same leg IS reaped (the key is what discriminated)" "$(ndel)" "1"
RESULT_KEYS="leg_"; export RESULT_KEYS

# ============================ 2. EVERY REFUSAL — ZERO DELETES ============================
# (a) VM is NEWER than the result: a different, later run (e.g. force_rerun). Never touched.
LABELS_JSON=$(labels calib_hi_to_lo__ternary_vhl rev 0 0 run "2026-07-27T14:00:00Z"); export LABELS_JSON
RESULT_TS="2026-07-27T12:03:00Z"; export RESULT_TS
run_sweep
chk "VM created AFTER its result -> spared" "$(ndel)" "0"
grep -q 'ORPHAN SPARED' "$TD/out" || { echo "FAIL: no spared annotation"; fail=1; }

# (b) no result object at all: the leg may still be sampling. Loud, but never destructive.
RESULT_TS=""; export RESULT_TS
LABELS_JSON=$(labels calib_hi_to_lo__ternary_vhl rev 0 0 run "2026-07-26T10:00:00.000-07:00"); export LABELS_JSON
run_sweep
chk "result NOT in GCS -> refused, nothing deleted" "$(ndel)" "0"
grep -q 'RESULT NOT IN GCS' "$TD/out" || { echo "FAIL: no refusal annotation"; fail=1; }
grep -q 'ORPHAN VM (no result yet)' "$ALERT" && echo "PASS it trips the alert file (job fails, GitHub notifies)" || { echo "FAIL: alert not tripped"; fail=1; }

# (c) UNLABELLED VM — created before labels existed, or by hand. Age is not evidence; refuse.
LABELS_JSON='{"labels":{},"creationTimestamp":"2026-07-26T10:00:00.000-07:00"}'; export LABELS_JSON
RESULT_TS="2026-07-27T12:03:00Z"; export RESULT_TS
run_sweep
chk "unlabelled VM -> refused, nothing deleted" "$(ndel)" "0"
grep -q 'NOTHING WATCHING IT' "$TD/out" || { echo "FAIL: no orphan annotation"; fail=1; }

# (d) a NON-run mode writes no leg result, so no artifact can prove it is finished. Refuse.
LABELS_JSON=$(labels calib_hi_to_lo__ternary_vhl fwd 0 0 preequil "2026-07-26T10:00:00.000-07:00"); export LABELS_JSON
run_sweep
chk "mode=preequil VM -> refused, nothing deleted" "$(ndel)" "0"
grep -q 'non-run mode' "$TD/out" || { echo "FAIL: no non-run annotation"; fail=1; }

# (e) an UNREADABLE timestamp must fail SAFE. Sparing a zombie costs a pass; reaping a live leg costs hours.
LABELS_JSON=$(labels calib_hi_to_lo__ternary_vhl fwd 0 0 run "not-a-date"); export LABELS_JSON
RESULT_TS="2026-07-27T12:03:00Z"; export RESULT_TS
run_sweep
chk "unreadable VM creation time -> spared" "$(ndel)" "0"

# ============================ 3. IT NEVER RACES THE PER-ENTRY LOOP ============================
# A VM an ENABLED entry already covers is that entry's business. Reaping it here would duplicate the DONE
# branch's decision using different evidence, which is how two guards disagree on a live box.
cat > "$CFG" <<'J'
{"watch": [{"enabled": true, "leg_id": "calib_hi_to_lo__ternary_vhl", "direction": "fwd",
            "seed": "0", "restrain": "0"}]}
J
LABELS_JSON=$(labels calib_hi_to_lo__ternary_vhl fwd 0 0 run "2026-07-26T10:00:00.000-07:00"); export LABELS_JSON
RESULT_TS="2026-07-27T12:03:00Z"; export RESULT_TS
run_sweep
chk "a VM an enabled entry watches -> left to that entry" "$(ndel)" "0"
grep -q 'already watches' "$TD/out" || { echo "FAIL: no hand-off annotation"; fail=1; }

# ...but a DIFFERENT leg, with that same entry enabled, is still an orphan and is still swept.
LABELS_JSON=$(labels calib_hi_to_lo__binary_vhl fwd 0 0 run "2026-07-26T10:00:00.000-07:00"); export LABELS_JSON
run_sweep
chk "an unwatched leg alongside a watched one -> still reaped" "$(ndel)" "1"

# ============================ 4. dry_run NEVER DELETES ============================
DRY=1; export DRY
cat > "$CFG" <<'J'
{"watch": []}
J
LABELS_JSON=$(labels calib_hi_to_lo__ternary_vhl rev 0 0 run "2026-07-26T10:00:00.000-07:00"); export LABELS_JSON
run_sweep
chk "dry_run=1 -> reports, deletes nothing" "$(ndel)" "0"
grep -q 'would DELETE' "$TD/out" || { echo "FAIL: dry_run did not report the candidate"; fail=1; }
DRY=0; export DRY

# ============================ 5. NO VM AT ALL ============================
VM_NAMES=""; export VM_NAMES
run_sweep
chk "no VM up -> clean no-op" "$(ndel)" "0"
[ -s "$ALERT" ] && { echo "FAIL: an empty lane raised an alert"; fail=1; } || echo "PASS an empty lane is silent"

if [ "$fail" = 0 ]; then echo "watchdog orphan sweep: all checks pass"; else echo "watchdog orphan sweep: FAILURES"; fi
exit "$fail"
