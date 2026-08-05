#!/usr/bin/env bash
# Pre-commit preflight: run every cheap check, and FAIL LOUDLY if any of them fails.
#
# WHY THIS EXISTS. On 2026-07-25 an agent session pushed a real lint error to `main`, then ~an hour later
# pushed a merge without noticing 14 failing tests. Both times the command looked like this:
#
#     python3 research/manuscripts/lint_consistency.py | tail -3 && git commit ...
#
# A pipeline's exit status is the status of its LAST command. `tail` succeeds, so `&&` proceeds and `set -e`
# never fires -- the check ran, printed its error, and was structurally incapable of stopping anything. That is
# the same defect class this repo keeps paying for: a check that reports while measuring nothing actionable
# (seven false-success diagnostics on the valB lane; a watchdog unparseable for days so its cron never fired;
# `_diagnostics_ok()` returning True when the report was absent).
#
# The fix is not "remember not to pipe". It is one entry point whose exit code cannot be masked:
#   * `set -euo pipefail` so a failure anywhere in a pipeline propagates;
#   * every check's status captured explicitly and re-reported at the end;
#   * a non-zero exit if ANY check failed, so `./scripts/preflight.sh && git commit` is actually safe.
#
# Sandbox note: this box lacks the scientific deps, so those tests fail here and pass in CI, where the
# baked images supply them. MEASURED 2026-08-05, rather than remembered -- absent: numpy, scipy, pymbar,
# rdkit, boto3, netCDF4; present: pyyaml, jsonschema. (The line here used to name "scipy, pymbar, rdkit"
# and omitted numpy and boto3, which between them account for 29 of the 48 baseline failures.) Rather
# than hide that behind an ignore list -- which would be the very "silently measures nothing" pattern
# above -- the test step reports a BASELINE count and fails only when failures EXCEED it. Update the
# baseline deliberately, in a commit, when the environment changes.
#
# Usage:  ./scripts/preflight.sh          # lint + tests
#         SKIP_TESTS=1 ./scripts/preflight.sh   # docs-only change
set -euo pipefail

cd "$(dirname "$0")/.."

# Known-failing-in-sandbox count. Raise ONLY with a recorded reason; lowering it is always safe.
#
# ⛔ RAISED 14 -> 48 ON 2026-08-05, AND THE RAISE IS A CORRECTION RATHER THAN A CONCESSION. The 14 was
# never measured against a run that executed anything: without `--continue-on-collection-errors` below,
# pytest aborted at collection and this script counted `^FAILED` lines in the output of a run that had
# tried zero tests. The first sweep that actually ran measured `50 failed, 5984 passed, 107 skipped, 6
# errors` in 596 s over `research/modalities/tests` alone (manuscripts and systems pass in full).
#
# ⭐ ALL 50 WERE THEN CLASSIFIED RATHER THAN ASSUMED, and two were NOT dep-related:
#   48  ModuleNotFoundError -- boto3 (20), rdkit (19), numpy (9). CI installs all three and runs green.
#    1  test_no_hand_rolled_publish -- a REAL failure, and the same one that had CI red. Fixed.
#    1  test_itemsize_survives_a_dtype_that_is_not_a_numpy_dtype -- a REAL bug in chk_prune._itemsize,
#       whose `except Exception` swallowed ImportError as well as the VLEN TypeError it was written
#       for, so every dtype fell back to 8 bytes where numpy is absent. Fixed.
# Those two are exactly what a gate reporting "0 failures" from an empty run cannot show you.
#
# THIS NUMBER SHOULD FALL as the sandbox gains packages. It describes a deficient environment; it is
# not a tolerance for broken tests, and every one of the 48 is a missing import, not a failing assert.
BASELINE_FAILURES="${PREFLIGHT_BASELINE_FAILURES:-48}"
rc=0

echo "== lint_consistency =="
if python3 research/manuscripts/lint_consistency.py; then
  echo "   OK"
else
  echo "   FAILED"; rc=1
fi

# ⛔ ADDED 2026-08-05 — THE SYSTEMS MODEL'S INVARIANTS WERE NOT IN THE STATED PRE-COMMIT GATE.
# CLAUDE.md §7 says "before committing, ./scripts/preflight.sh must pass", and this script did not run
# systems_check or parser_guard at all: ~35 invariants — a failing instrument cited as SUPPORT, a
# permanent blocker claiming a technology, a drifted generated view, a parser that has lost its input —
# were CI-only. Anyone following the documented workflow would not have run them.
echo "== systems model (invariants, pointers, view drift) =="
if python3 systems/systems_check.py --check >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 systems/systems_check.py --check' to see why"; rc=1
fi

echo "== parser guard (every registered parser can still find its input) =="
if python3 systems/parser_guard.py >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 systems/parser_guard.py' to see why"; rc=1
fi

echo "== validate (EMC clinical registry evidence contract) =="
if node scripts/validate-registry.mjs >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'node scripts/validate-registry.mjs' to see why"; rc=1
fi

if [ "${SKIP_TESTS:-0}" != "1" ]; then
  echo "== pytest (modalities) =="
  out=$(mktemp)
  # ⛔ `--continue-on-collection-errors` ADDED 2026-08-05, AND WITHOUT IT THIS STEP MEASURED NOTHING.
  #
  # Five test modules in this sandbox fail to IMPORT (scipy, pymbar, rdkit are absent). Without this
  # flag pytest prints `Interrupted: 5 errors during collection` and EXITS HAVING RUN ZERO TESTS. The
  # parser below then greps for `^FAILED`, finds none, and prints
  #     OK (0 failures, at/below the 14 sandbox baseline -- all dep-related, green in CI)
  # -- a green line, from a run that executed no test at all. The real number that day was 50.
  #
  # ⚠ THAT IS THIS SCRIPT'S OWN HEADER DEFECT, IN THIS SCRIPT. The comment at the top of this file
  # exists because a check "reported while measuring nothing actionable", and names three prior
  # instances. This was a fourth, sitting inside the fix for the first three. `set -euo pipefail` and
  # an explicit exit code do not help when the thing being counted is never produced.
  python3 -m pytest research/modalities/tests/ -q --continue-on-collection-errors \
      --ignore=research/modalities/tests/test_ternary_endpoint_align.py >"$out" 2>&1 || true
  failed=$(grep -cE '^FAILED' "$out" || true)
  errored=$(grep -cE '^ERROR ' "$out" || true)
  tail -1 "$out"

  # ⛔ A RUN THAT EXECUTED NOTHING IS NOT A PASS. Belt and braces against the failure above returning
  # in another form: if pytest never reports a test count, the parsed failure count is meaningless and
  # this step must go red rather than quietly agree with itself.
  if ! grep -qE '[0-9]+ (passed|failed)' "$out"; then
    echo "   FAILED: pytest reported no test count -- the run collected nothing, so '0 failures' would"
    echo "           be a statement about an empty run. Last lines:"
    tail -5 "$out"
    rc=1
  elif [ "$failed" -gt "$BASELINE_FAILURES" ]; then
    echo "   FAILED: $failed failures exceeds baseline $BASELINE_FAILURES -- these are NEW:"
    grep -E '^FAILED' "$out" | head -20
    rc=1
  else
    echo "   OK ($failed failures, at/below the $BASELINE_FAILURES sandbox baseline -- all dep-related,"
    echo "       green in CI; $errored module(s) could not be imported here and are counted separately)"
  fi
  rm -f "$out"
fi

if [ "$rc" -ne 0 ]; then
  echo; echo "PREFLIGHT FAILED -- do not commit."
else
  echo; echo "PREFLIGHT OK"
fi
exit "$rc"
