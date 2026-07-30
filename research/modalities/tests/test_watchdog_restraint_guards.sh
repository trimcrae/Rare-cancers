#!/usr/bin/env bash
# A watchdog that cannot honour its watch list must REFUSE, not improvise.
#
# THE FAILURE BEING PREVENTED. `restrain=1` adds a flat-bottom pocket restraint — a DIFFERENT HAMILTONIAN —
# and it keys both the spot commit prefix (`_rst`) and the leg result file. A watchdog that drops that key
# resolves `leg_<leg>_<dir>_r<seed>.json`, which FOR THE r0 BINARY ARM ALREADY EXISTS from the unrestrained
# run. It would then report a green DONE for a leg that never ran, chain converge+reduce off a stale file,
# and leave the running VM holding GPUS_ALL_REGIONS=1 — the whole project's only GPU — while billing expiring
# credit. A success that measured the wrong thing, which is this repo's signature defect.
#
# TWO GUARDS, DEFENDING TWO DIFFERENT CAUSES, both tested here against the REAL files:
#
#   1. CAPABILITY HANDSHAKE (stale code, new config). ternary-watch.json declares
#      `_requires_watchdog_features`; watchdog_run.sh declares WATCHDOG_FEATURES and refuses if it cannot
#      supply everything the config asks for.
#      SCOPE, stated honestly: `actions/checkout@v4` in ternary-leg-watchdog.yml takes NO `ref`, so the script
#      and the config normally travel together and cannot diverge. The real paths are a SELECTIVE MERGE that
#      forwards the JSON without the script, and the divergent private copies this repo already documents
#      (ternary-watch.json's `_required_keys_are_enforced` note warns another session may hold an older
#      watchdog_validate.py). It CANNOT protect against a watchdog older than the handshake itself — such a
#      copy never reads the key. It closes the window from here forward, which is all a handshake can do.
#
#   2. RESULT-KEY ASSERTION (future edit, current code). Independent of any version skew: if an entry declares
#      restrain=1, the key this pass actually resolved must carry `_rst`. It asserts the PROPERTY, not the
#      spelling, so it fires inside the very code that has the bug, before any DONE verdict or reap.
#
# METHOD: both guards are EXTRACTED from the real watchdog_run.sh and executed. Restating them here would
# prove only that the copy agrees with itself.

set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
WD=research/modalities/watchdog_run.sh
CFGREAL=research/modalities/ternary-watch.json
for f in "$WD" "$CFGREAL"; do [ -f "$f" ] || { echo "missing $f"; exit 2; }; done

TD=$(mktemp -d); trap 'rm -rf "$TD"' EXIT
fail=0
chk() { if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1:"; echo "       got  '$2'"; echo "       want '$3'"; fail=1; fi; }

# ---- GUARD 1: the capability handshake, extracted and run against synthetic configs -----------------------
python3 - "$WD" > "$TD/handshake.sh" <<'PY'
import sys
t = open(sys.argv[1]).read()
start = t.index('WATCHDOG_FEATURES=')
end   = t.index('\nfi\n', t.index('WATCHDOG TOO OLD FOR THIS CONFIG', start)) + len('\nfi\n')
print('handshake() {')
print(t[start:end])          # NOT re-indented — see the note above the key-guard extraction
print('}')
PY
grep -q 'WATCHDOG TOO OLD FOR THIS CONFIG' "$TD/handshake.sh" \
  || { echo "EXTRACTION FAILED — no handshake refusal in watchdog_run.sh (that IS the bug)"; exit 1; }
bash -n "$TD/handshake.sh" || { echo "EXTRACTION FAILED — extracted handshake does not parse"; exit 2; }

run_handshake() {  # $1 = JSON text -> "<exit> <sawerror>"
  printf '%s' "$1" > "$TD/cfg.json"
  ( set +u; CFG="$TD/cfg.json"; . "$TD/handshake.sh"; handshake ) >"$TD/hs.out" 2>&1
  rc=$?
  if grep -q 'WATCHDOG TOO OLD' "$TD/hs.out"; then e=1; else e=0; fi
  echo "$rc $e"
}

chk "a config requiring nothing is accepted" \
    "$(run_handshake '{"watch":[]}')" "0 0"
chk "a config requiring the feature this script HAS is accepted" \
    "$(run_handshake '{"_requires_watchdog_features":["restraint_keyed_result_v1"],"watch":[]}')" "0 0"
chk "a config requiring an UNKNOWN feature is REFUSED loudly (exit 1 + ::error)" \
    "$(run_handshake '{"_requires_watchdog_features":["some_future_thing"],"watch":[]}')" "1 1"
chk "one unknown feature among known ones still refuses" \
    "$(run_handshake '{"_requires_watchdog_features":["restraint_keyed_result_v1","some_future_thing"],"watch":[]}')" "1 1"

# The live config must actually declare the requirement, or guard 1 protects nothing in practice.
chk "the REAL ternary-watch.json declares its watchdog feature requirement" \
    "$(python3 -c "
import json;d=json.load(open('$CFGREAL'))
print('restraint_keyed_result_v1' in (d.get('_requires_watchdog_features') or []))")" "True"

# ...and it must be declared BECAUSE a restrained entry exists — a requirement nobody needs is noise.
#
# ⚠ COUNTS EVERY ENTRY, ENABLED OR NOT — and that is the fix for a real outage, not a loosening.
# This filtered on `if w.get('enabled')`. Landed units are now auto-disabled the moment their result is in
# (gcp_watch_reap), so when the restrained binary leg landed at 5:33 PM ET on 2026-07-28 the last enabled
# restrain=1 entry vanished and this went False. It is the FIRST step in the pytest job, so its failure
# SKIPPED the actual `pytest research/modalities/tests` step — the repo's own test gate stopped executing and
# stayed dead for 9+ commits while every merge reported green on a suite that never ran.
#
# The intent survives intact: a `_requires_watchdog_features` declaration that NO entry has ever needed is
# still noise and still fails. What changed is that a FINISHED restrained entry keeps justifying it — the
# file declares what it may ask of the watchdog, a disabled entry can be re-enabled, and the dangerous
# direction (an entry needing a feature the watchdog LACKS) is Guard 1, which is untouched and still fires.
chk "the real config has at least one restrain=1 entry justifying it (enabled or landed)" \
    "$(python3 -c "
import json;d=json.load(open('$CFGREAL'))
print(any(w.get('restrain')=='1' for w in d['watch']))")" "True"

# ---- GUARD 2: the result-key assertion, extracted and run --------------------------------------------------
# NB the extracted text is NOT re-indented. Re-indenting a shell block is usually harmless, but this file
# embeds `python3 -c` and Python is indentation-sensitive — the first cut of this test added two spaces to
# every line and the handshake died with IndentationError, i.e. the test broke the thing it was measuring.
# watchdog_run.sh now keeps its embedded python on one line for that reason; not re-indenting here is the
# other half of the same lesson.
python3 - "$WD" > "$TD/keyguard.sh" <<'PY'
import sys, textwrap
t = open(sys.argv[1]).read()
start = t.index('    RESULT_KEY="$RESULTS/leg_')
end   = t.index('\n    fi\n', t.index('WATCHDOG RESULT KEY LOST THE RESTRAINT', start)) + len('\n    fi\n')
block = textwrap.dedent(t[start:end])
print('keyguard() {')
print(block)
print('}')
PY
grep -q 'WATCHDOG RESULT KEY LOST THE RESTRAINT' "$TD/keyguard.sh" \
  || { echo "EXTRACTION FAILED — no result-key assertion in watchdog_run.sh (that IS the bug)"; exit 1; }
bash -n "$TD/keyguard.sh" || { echo "EXTRACTION FAILED — extracted key guard does not parse"; exit 2; }

# `continue` is correct in the real per-entry loop but is a no-op warning inside a bare function, so the
# property under test is the REFUSAL ANNOUNCEMENT, not control flow. Control flow is covered where it really
# runs, by test_watchdog_done_reaps_vm.sh, which extracts the whole DONE decision including this guard.
run_keyguard() {  # $1=RST $2=RSTTAG -> 1 if it announced a refusal, else 0
  ( set +u
    RST="$1"; RSTTAG="$2"
    RESULTS=gs://bkt/results; LEG=calib_hi_to_lo__binary_vhl; DIR=fwd; SEED=0
    TAG="$LEG dir=$DIR seed=$SEED"
    . "$TD/keyguard.sh"; keyguard ) >"$TD/kg.out" 2>&1
  if grep -q 'RESULT KEY LOST THE RESTRAINT' "$TD/kg.out"; then echo 1; else echo 0; fi
}

chk "restrain=1 with the _rst key -> no complaint"        "$(run_keyguard 1 _rst)" "0"
chk "restrain=1 WITHOUT the _rst key -> REFUSES loudly"   "$(run_keyguard 1 '')"   "1"
chk "restrain=0 with no key -> no complaint (unchanged)"  "$(run_keyguard 0 '')"   "0"
chk "restrain unset -> no complaint (every legacy entry)" "$(run_keyguard '' '')"  "0"

[ "$fail" = 0 ] && echo "watchdog restraint guards: all checks pass"
exit "$fail"
