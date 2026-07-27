#!/usr/bin/env bash
# A RELAUNCH must reproduce the run it is rescuing — every parameter, including `restrain`.
#
# THE FAILURE MODE, and it is specific to the relaunch path rather than the resume path this lane has already
# been burned by. `restrain=1` adds a flat-bottom pocket restraint: a DIFFERENT HAMILTONIAN that keys the spot
# commit prefix with `_rst`. gpu-ternary-fep-gcp.yml HARD-FAILS before provisioning if the flag and the prefix
# disagree (COMMIT PREFIX LOST THE RESTRAINT) — which is correct, and is exactly what makes a dropped flag
# expensive rather than merely wrong:
#
#   leg dies -> watchdog relaunches WITHOUT restrain=1 -> the launcher's own assertion refuses to provision
#   -> NO leg, NO VM, quota freed, and the watchdog's own log says "RELAUNCHED".
#
# That is a SILENT STALL. The watchdog reports success, the dispatched run fails somewhere else, and the work
# simply never resumes. It reads like an infrastructure blip.
#
# WHY IT NEEDS ITS OWN TEST. Restrained and unrestrained systems are IDENTICAL IN COMPOSITION — same atoms,
# same particle count — so OpenFE's `assert_multistate_system_equality`, the check that has caught every other
# keying bug on this lane, provably cannot fire. And this path only executes on a relaunch, so no happy-path
# test touches it: the sibling test_watchdog_restraint_guards.sh covers the capability handshake and the DONE
# branch's result key, and test_watchdog_done_reaps_vm.sh covers the DONE branch's reap. Nothing exercised the
# DIED branch's dispatch until this file.
#
# METHOD: the relaunch is EXTRACTED from the real watchdog_run.sh and EXECUTED against a stubbed `gh` that
# records its argv. Asserting on the source text would pass on a rewrite that reads correctly and dispatches
# the wrong thing.

set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
WD=research/modalities/watchdog_run.sh
[ -f "$WD" ] || { echo "missing $WD"; exit 2; }

TD=$(mktemp -d); trap 'rm -rf "$TD"' EXIT
fail=0
chk() { if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1:"; echo "       got  '$2'"; echo "       want '$3'"; fail=1; fi; }

# ---- extract the relaunch dispatch, from its `gh workflow run` to the end of its if/else -------------------
python3 - "$WD" > "$TD/relaunch.sh" <<'PY'
import sys, textwrap
t = open(sys.argv[1]).read()
anchor = 'if gh workflow run gpu-ternary-fep-gcp.yml --ref "${WATCH_REF}" \\\n         -f mode=run'
i = t.index(anchor)
i = t.rfind('\n', 0, i) + 1
# the branch ends at its own `fi`, indented 4 spaces
j = t.index('\n    fi\n', i) + len('\n    fi\n')
block = textwrap.dedent(t[i:j])
print('relaunch() {')
print(block)                       # NOT re-indented: this file embeds shell that must stay as-written
print('}')
PY
grep -q 'gh workflow run gpu-ternary-fep-gcp.yml' "$TD/relaunch.sh" \
  || { echo "EXTRACTION FAILED — no relaunch dispatch found in watchdog_run.sh (that IS the bug)"; exit 1; }
bash -n "$TD/relaunch.sh" || { echo "EXTRACTION FAILED — extracted relaunch does not parse"; exit 2; }

# ---- stubs: `gh` records its full argv; `gcloud` swallows the counter write ------------------------------
mkdir -p "$TD/bin"
cat > "$TD/bin/gh" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$GH_ARGV"
exit "${GH_RC:-0}"
STUB
cat > "$TD/bin/gcloud" <<'STUB'
#!/usr/bin/env bash
exit 0
STUB
chmod +x "$TD/bin/gh" "$TD/bin/gcloud"
PATH="$TD/bin:$PATH"; export PATH

dispatch_argv() {   # $1 = value of RST ('' = unset) -> the argv `gh` was called with
  GH_ARGV="$TD/argv"; : > "$GH_ARGV"; export GH_ARGV
  ( set +u
    [ -n "$1" ] && RST="$1"
    LEG=calib_hi_to_lo__binary_vhl; SEED=0; DIR=fwd; SALT=""; DT=2.0; WUDT=""; UPE=0
    CHG=nagl; NWIN=12; TPL=8G1Q; PROV=standard; CNT=0; MAXRL=40
    TAG="$LEG dir=$DIR seed=$SEED"; WATCH_REF=somebranch
    CNTOBJ=gs://bkt/cnt; ALERT="$TD/alert"; : > "$ALERT"
    . "$TD/relaunch.sh"; relaunch ) >"$TD/out" 2>&1
  cat "$GH_ARGV"
}

# ---- 1. THE REGRESSION ITSELF ----------------------------------------------------------------------------
ARGV=$(dispatch_argv 1)
case "$ARGV" in
  *"-f restrain=1"*) echo "PASS a restrained entry relaunches WITH restrain=1" ;;
  *) echo "FAIL a restrained entry relaunched WITHOUT restrain=1 — the launcher would refuse to provision and"
     echo "     the leg would silently never resume. argv: $ARGV"; fail=1 ;;
esac

ARGV0=$(dispatch_argv 0)
case "$ARGV0" in
  *"-f restrain=0"*) echo "PASS an unrestrained entry relaunches with restrain=0" ;;
  *) echo "FAIL an unrestrained entry did not pass restrain=0: $ARGV0"; fail=1 ;;
esac

# An entry from before `restrain` existed must relaunch UNRESTRAINED, not crash and not guess.
ARGVU=$(dispatch_argv '')
case "$ARGVU" in
  *"-f restrain=0"*) echo "PASS an entry with RST unset defaults to restrain=0 (every legacy entry)" ;;
  *) echo "FAIL RST unset did not default to restrain=0: $ARGVU"; fail=1 ;;
esac

# ---- 2. THE RELAUNCH MUST REPRODUCE THE WHOLE RUN, not just the restraint --------------------------------
# `restrain` is only the newest member of this set. The commit prefix is built from seed+dt+clig+wu+salt+dir
# and the SYSTEM from use_preequil, so a relaunch missing any of them resumes a different calculation — the
# defect class of audit sections H / J.2-J.5 / L.1 / L.5 / L.6. Assert the whole set travels, so the next
# parameter added is caught by this test rather than by a wasted GPU-day.
for p in mode=run leg_id= seed= direction= commit_salt= timestep_fs= warmup_timestep_fs= use_preequil= \
         charge_method= n_windows= template_pdb= restrain= provisioning= refuse_if_vm_live=1; do
  case "$ARGV" in
    *"-f $p"*) : ;;
    *) echo "FAIL the relaunch does not pass '$p' — it would not reproduce the run it is rescuing"; fail=1 ;;
  esac
done
echo "PASS (checked) the relaunch carries every run-reproducing parameter"

# ---- 3. The declared requirement and the dispatch must not drift apart ------------------------------------
# ternary-watch.json's `_required_run_params` is what watchdog_validate.py enforces on the CONFIG. If a param
# is required of the config but never actually dispatched, the validation is theatre; if it is dispatched but
# not required, an entry can omit it and the relaunch silently substitutes a default. Both directions are
# checked against the REAL files.
MISSING=$(python3 -c "
import json
req=json.load(open('research/modalities/ternary-watch.json'))['_required_run_params']
argv=open('$TD/argv').read()
print(' '.join(p for p in req if p != 'leg_id' and ('-f %s=' % p) not in argv))
")
chk "every _required_run_params entry is actually dispatched on relaunch" "$MISSING" ""

# ---- 4. A FAILED dispatch must be loud, not counted as a relaunch -----------------------------------------
GH_RC=1 dispatch_argv 1 >/dev/null
if grep -q 'WATCHDOG DISPATCH FAILED' "$TD/out"; then
  echo "PASS a failed dispatch raises ::error"
else
  echo "FAIL a failed dispatch was silent: $(cat "$TD/out")"; fail=1
fi
if grep -q 'DISPATCH FAILED' "$TD/alert"; then
  echo "PASS a failed dispatch trips the alert file (so the job fails and GitHub notifies)"
else
  echo "FAIL a failed dispatch did not trip the alert file"; fail=1
fi

[ "$fail" = 0 ] && echo "watchdog relaunch pass-through: all checks pass"
exit "$fail"
