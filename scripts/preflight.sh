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
# tried zero tests. The first sweep that actually ran measured **50 failed** over `research/modalities/tests`
# alone (manuscripts and systems pass in full). That one figure is the whole evidence for the raise.
#
# ⚠ THE REST OF THAT SWEEP'S SUMMARY USED TO BE QUOTED HERE AND HAS BEEN REMOVED, BECAUSE A PASSED COUNT IS
# NOT A FACT ABOUT THIS GATE — IT IS A FACT ABOUT A SUITE THAT GROWS, so it starts going stale the moment it
# is committed and there is no check that would ever catch it. Superseded, retained (CLAUDE.md rule 1.2):
# `5984 passed, 107 skipped, 6 errors` in 596 s. Re-measured ONE DAY LATER, 2026-08-06, on the same command:
# the passed count had already moved by +135 and skipped by +8, and the collection-error count by −1, while
# the failure count this gate actually tracks had not moved at all. Exactly the drift the removal prevents.
# ⛔ SO DO NOT RE-TYPE THE CURRENT POPULATION HERE. This script MEASURES it on every run and prints it:
# `tail -1 "$out"` below emits pytest's own `N failed, M passed, K skipped, E errors` line. THAT printed
# line is the one home of the live count (CLAUDE.md rule 1: a total is derived, never typed).
#
# ⭐ ALL 50 WERE THEN CLASSIFIED RATHER THAN ASSUMED, ON 2026-08-05, and two were NOT dep-related. The split
# below is that day's reading, not a standing property — re-derive it rather than trusting it, by grouping
# the `ModuleNotFoundError` lines in the FAILURES section of this step's own output:
#   48  ModuleNotFoundError -- boto3 (20), rdkit (19), numpy (9). CI installs all three and runs green.
#    1  test_no_hand_rolled_publish -- a REAL failure, and the same one that had CI red. Fixed.
#    1  test_itemsize_survives_a_dtype_that_is_not_a_numpy_dtype -- a REAL bug in chk_prune._itemsize,
#       whose `except Exception` swallowed ImportError as well as the VLEN TypeError it was written
#       for, so every dtype fell back to 8 bytes where numpy is absent. Fixed.
# Those two are exactly what a gate reporting "0 failures" from an empty run cannot show you.
#
# THIS NUMBER SHOULD FALL as the sandbox gains packages. It describes a deficient environment; it is
# not a tolerance for broken tests, and every one is a missing import, not a failing assert.
#
# ⭐ RAISED 48 -> 50 ON 2026-08-07, AND THE RAISE IS MEASURED RATHER THAN CONCEDED. A raise is the
# dangerous direction for this field -- it is how a real regression gets absorbed -- so it was gated on
# a two-sided set comparison, not on a count:
#
#   clean `origin/main` worktree : 50 failed, 6367 passed
#   this branch after the merge  : 50 failed, 6409 passed
#   failing-test-name sets       : IDENTICAL -- both comm(1) directions empty, 50 vs 50
#
# So the branch adds 42 PASSING tests and zero failing ones. The cause of the drift is the suite
# GROWING against a fixed environment: more rdkit/pymbar/boto3-dependent modules land, each adds its
# import failure, and the count rises while nothing breaks. 6120 -> 6409 passing in one day.
#
# ⛔ DO NOT RAISE THIS ON A COUNT COMPARISON. Two counts agreeing proves nothing -- 2 new failures
# masked by 2 fixes reads identically. The check that matters is the NAME SET, and the way to get it is
# a worktree at the merge base (the command is printed by this script when the gate trips). An earlier
# attempt at exactly this comparison on the same day was VACUOUS because it diffed this script's own
# truncated 20-line output against a full 50-line list: a subset can never show "new on branch", so it
# returned a clean verdict it had no power to produce. Compare pytest's full list on both sides.
BASELINE_FAILURES="${PREFLIGHT_BASELINE_FAILURES:-50}"
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

# ⛔ ADDED 2026-08-06, AND IT COST A RED `main` TO NOTICE. This is the SIBLING registry of the gate
# above -- same shape, same "regenerate the view and diff it" discipline, pure stdlib, ~2 s -- and it
# was CI-only while its sibling was here. So a session could run this script, see PREFLIGHT OK, merge,
# and turn `main` red: a new generated view named a cell line whose identity is DISPUTED, and O4 (which
# requires every tracked file naming it to classify the use) fired in CI and nowhere else.
#
# ⚠ The gap was invisible in the worst way: the check that was missing is one of the two that enforce
# MEDICAL INTEGRITY rather than tidiness. A local gate that is green while the strongest evidentiary
# guard in the repository has not run is worse than no local gate, because it is trusted.
echo "== EMC systems map (disputed identities, claim artifacts, view drift) =="
if python3 research/manuscripts/emc_systems_map_check.py --check >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 research/manuscripts/emc_systems_map_check.py --check' to see why"; rc=1
fi

# ⛔ ADDED 2026-08-07, AND IT IS HERE RATHER THAN CI-ONLY BECAUSE THAT MISTAKE WAS MADE TWICE ABOVE.
# An agent drafting a manuscript wrote a PMID from RECOLLECTION -- present in no committed source
# anywhere in this repository -- and it PASSED lint_claims TWICE. Six invented titles and author-lists
# went out in the same pass, caught only by a human-directed audit.
#
# ⚠ lint_claims cannot catch this and is not deficient for failing to: it checks how strongly a claim is
# WORDED (R1-R5: selectivity, efficacy, safety, therapeutic window, clinical readiness). A fabricated
# identifier on a properly-hedged sentence is, to that linter, a perfect sentence. Claim STRENGTH and
# citation PROVENANCE are orthogonal, and no other gate reads an identifier at all -- against a
# repository whose FIRST golden rule is "never fabricate medical facts, stats, citations or patient
# data". This gate closes that and only that.
echo "== citation provenance (every prose identifier traces to a fetch or to the ledger) =="
if python3 research/manuscripts/lint_citations.py >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 research/manuscripts/lint_citations.py' to see which identifier"; rc=1
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
  # Five test modules in this sandbox fail to IMPORT. Without this flag pytest prints
  # `Interrupted: 5 errors during collection` and EXITS HAVING RUN ZERO TESTS. The
  # parser below then greps for `^FAILED`, finds none, and prints
  #     OK (0 failures, at/below the 14 sandbox baseline -- all dep-related, green in CI)
  # -- a green line, from a run that executed no test at all. The real number that day was 50.
  #
  # ⚠ THIS LINE USED TO NAME THE CAUSE — "(scipy, pymbar, rdkit are absent)" — AND THAT WAS THE SAME WRONG
  # TRIPLE THE SANDBOX NOTE AT THE TOP OF THIS FILE ALREADY RECORDS AS CORRECTED. The correction landed up
  # there on 2026-08-05 and was missed HERE, ~85 lines away in the same file: one fact, two places, one of
  # them repeating the error the other had already retired. Measured 2026-08-06, not remembered: all five
  # collection errors are `ModuleNotFoundError: No module named 'numpy'` — not one is scipy, pymbar or rdkit.
  # Superseded, retained (CLAUDE.md rule 1.2): "(scipy, pymbar, rdkit are absent)".
  # ⛔ The cause is deliberately NOT re-typed here now. It is one command, and it answers for today:
  #     python3 -m pytest research/modalities/tests/ -q --collect-only --continue-on-collection-errors \
  #       --ignore=research/modalities/tests/test_ternary_endpoint_align.py 2>&1 | grep ModuleNotFoundError
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
    # ⛔ THIS USED TO SAY "these are NEW:" ABOVE A `head -20` OF *ALL* FAILURES, AND THAT WAS A LIE THE
    # READER COULD NOT DETECT (measured 2026-08-07). With a baseline of 48 and 50 failures, it printed 20
    # lines under a heading claiming every one was a regression, when at most 2 could be and the 20 shown
    # were simply the alphabetically-first. Two sessions in a row chased dep-gap failures believing they
    # had broken something. This script stores no baseline LIST, only a COUNT, so the excess cannot be
    # identified here -- and saying so is strictly better than naming innocents.
    echo "   FAILED: $failed failures exceeds baseline $BASELINE_FAILURES (excess: $((failed - BASELINE_FAILURES)))"
    echo "   ⚠ THE $((failed - BASELINE_FAILURES)) NEW FAILURE(S) ARE NOT IDENTIFIED BELOW. This gate tracks a COUNT, not a"
    echo "     list, so it cannot tell you WHICH failed tests are new. The lines below are the first 20 of"
    echo "     ALL $failed failures, most of which are the known dep gap. To find the real regression, diff"
    echo "     against a clean checkout: git worktree add /tmp/pf-clean HEAD && (cd /tmp/pf-clean && \\"
    echo "     python3 -m pytest research/modalities/tests -q --continue-on-collection-errors)"
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
