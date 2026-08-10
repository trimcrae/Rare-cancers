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

# ⛔ ONE PREFLIGHT AT A TIME, AND THE LONG GATE STOPS ON ITS OWN (2026-08-10).
#
# MEASURED, not supposed. A session running several subagents in parallel was found with 18 live
# shells and one process burning 83% of a core: `python3 -m pytest research/modalities/tests/`, 16
# minutes in, PPID 1. Its whole tree was orphaned — the subagent that launched it had exited, so
# nobody would ever read its verdict, and the tree it was testing had been edited underneath it. It
# was computing a stale answer for a reader who no longer existed.
#
# THE CHAIN, because only the last link looks like a bug:
#   1. the pytest gate below runs ~7,200 tests serially and takes ~16 minutes on this box;
#   2. 16 minutes exceeds an agent's foreground command budget, so agents background it;
#   3. a backgrounded shell is reparented to init when the agent exits — it does NOT stop;
#   4. N agents each told to "run the gates" therefore leave N detached 16-minute pytest runs
#      competing for 4 cores, which is slower for everyone and reads as a hang.
# No step is wrong alone. The damage is that they compose, unbounded.
#
# Two bounds, in the only two places this file can impose them: a non-blocking lock, so a second
# preflight REFUSES rather than queueing a duplicate; and a hard timeout on the pytest gate, so even
# a leaked run ends by itself.
#
# ⚠ THE REFUSAL EXIT CODE IS 75, NOT 1, AND THAT IS LOAD-BEARING. This script exists because a check
# once "reported while measuring nothing actionable". A skipped run must never read as a pass — and
# must not read as a gate FAILURE either, or a caller cannot tell "someone else is running it" from
# "your code is broken" and will draw the wrong conclusion from a red line. 75 is EX_TEMPFAIL.
# `./scripts/preflight.sh && git commit` stays safe under either reading.
#
# ⛔ OPENED `<>`, NOT `>`, AND THE DIFFERENCE IS THE WHOLE DIAGNOSTIC. `>` truncates on open — so a
# second preflight wiped the holder's pid out of the lock file BEFORE testing the lock, and then read
# back the empty file it had just emptied. The refusal still refused, which is why this survived a
# first test: the guard worked and only its most useful field went missing, intermittently. A
# diagnostic that destroys the evidence it is about to print is worse than one that prints nothing,
# because the blank reads as "no holder" rather than as "I erased it". `<>` opens read-write without
# truncating.
_pf_lock="/tmp/.rare-cancers-preflight.$(pwd -P | cksum | cut -d' ' -f1).lock"
exec {_pf_fd}<>"$_pf_lock"
if ! flock -n "$_pf_fd"; then
  _pf_holder=$(cat "$_pf_lock" 2>/dev/null || true)
  echo "PREFLIGHT ALREADY RUNNING${_pf_holder:+ (pid $_pf_holder)} — refusing to start a second one."
  echo "  The pytest gate takes ~16 minutes; two concurrent runs are slower than one and answer the"
  echo "  same question. Wait for the running one, or re-run when it finishes."
  echo "  Nothing was checked here. This is NOT a pass and NOT a gate failure."
  exit 75
fi
printf '%s' "$$" >"$_pf_lock"

# Ceiling for the pytest gate: generous against the ~16 minutes it takes, tight enough that a leaked
# run cannot hold a core all session. Raise it for a genuinely slower box.
PREFLIGHT_PYTEST_TIMEOUT="${PREFLIGHT_PYTEST_TIMEOUT:-2400}"

# ⛔ AND STOP WHEN THE CALLER GOES AWAY (2026-08-10, added after the SECOND orphan in one session).
#
# The lock above bounds how many preflights run at once. It does nothing about the case that actually
# happened twice: ONE run, orphaned, with nobody left to read it. Measured both times — an agent
# backgrounds this script, the agent exits, the shell wrapper is reparented to init, and pytest keeps
# burning a core computing a verdict for a reader who no longer exists, against a tree that has since
# been edited underneath it. The timeout above caps that at 40 minutes; on a 4-core box shared with
# live work, 40 minutes of a wasted core is still worth not spending.
#
# ⚠ ORPHANING HAS TWO SHAPES AND A GUARD THAT KNOWS ONLY ONE OF THEM IS ABSENT IN THE OTHER. The
# first version of this block watched only the GRANDPARENT, on the reasoning that in both observed
# leaks the shell wrapper survived and so this script's own `$PPID` never changed. That reasoning was
# right about those two leaks and useless in general: tested against a parent that dies immediately,
# the startup lookup of the grandparent returned nothing at all, the block took its own
# "nobody to lose" branch, and NO watchdog started — the guard opted out of precisely the case it
# exists for, silently, and the test only caught it because it watched the process rather than
# trusting the code. So watch both, and never treat an unresolvable ancestor as permission to skip:
#   shape A — wrapper survives, our PPID stays put, the process above it vanishes;
#   shape B — parent dies at once and we are reparented, so our own PPID becomes 1.
_pf_grandparent=$(ps -o ppid= -p "$PPID" 2>/dev/null | tr -d ' ' || true)
case "${_pf_grandparent:-}" in 1|0|"") _pf_grandparent="" ;; esac
if [ "${PREFLIGHT_NO_ORPHAN_GUARD:-0}" != "1" ]; then
  ( while :; do
      sleep 20
      # shape B: our parent went away and init adopted us.
      [ "$(ps -o ppid= -p $$ 2>/dev/null | tr -d ' ')" = "1" ] && break
      # shape A: the process above our parent went away.
      [ -n "$_pf_grandparent" ] && ! kill -0 "$_pf_grandparent" 2>/dev/null && break
    done
    kill -TERM -$$ 2>/dev/null || kill -TERM "$$" 2>/dev/null || true ) &
  _pf_watchdog=$!
  # Never let the watchdog outlive the run it guards — that would be this same leak under a new name.
  trap 'kill "$_pf_watchdog" 2>/dev/null || true' EXIT
fi

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
# ⛔ DERIVED FROM THE LIST, NEVER TYPED (CLAUDE.md rule 1.1: "a total is DERIVED, never typed --
# hand-carried totals drift silently"). This was hard-coded at 50 while the authoritative baseline
# list held 53, so every run printed a drift notice on an otherwise green build -- and a green build
# that always carries a note is a note nobody reads. The list is the source of truth; the count is a
# cross-check on it, so computing one from the other makes the two structurally unable to disagree.
# Superseded, retained: `BASELINE_FAILURES="${PREFLIGHT_BASELINE_FAILURES:-50}"`.
# ⚠ THIS DOES NOT WEAKEN THE GATE. What actually fails a run is a failure NOT NAMED in the list, and
# that check is untouched -- see the `comm -23` below. Deriving the count removes bookkeeping noise;
# it does not raise a ceiling, because the ceiling was never what caught anything.
_baseline_file=research/modalities/tests/sandbox-failure-baseline.txt
BASELINE_FAILURES="${PREFLIGHT_BASELINE_FAILURES:-$(
  grep -v '^#' "$_baseline_file" 2>/dev/null | sed '/^[[:space:]]*$/d' | sort -u | wc -l | tr -d ' '
)}"
BASELINE_FAILURES="${BASELINE_FAILURES:-0}"
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

# ADDED 2026-08-09. The repository's house style -- glyph warnings, bold on the load-bearing clause,
# running commentary about why a rule exists -- is correct in CLAUDE.md, in the roadmap and in the
# artifacts, where the reader is a maintainer being stopped from repeating a mistake. It is wrong in a
# manuscript: a journal reader is not being warned, prose that keeps asserting its own honesty reads as
# advocacy, and the tics are recognisable as machine-written, which costs a paper credibility it has
# otherwise earned. Measured when this gate was added: 81 findings in the one manuscript then listed --
# 25 glyphs, 32 mid-sentence bolds, 14 sentence-shaped headings, bold at 20.1 per 1000 words against a
# limit of 12. Scoped to TARGETS in the linter; memos, plans and findings notes keep the house style.
echo "== manuscript prose style (journal register, not repository register) =="
if python3 research/manuscripts/lint_style.py >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 research/manuscripts/lint_style.py' to see which lines"; rc=1
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
  # ⏱ WRAPPED IN `timeout` (2026-08-10). A leaked, orphaned copy of exactly this command was found
  # holding 83% of a core with nobody left to read it. The lock at the top of this file stops a
  # SECOND one starting; this stops the FIRST one running forever. `|| true` below deliberately
  # swallows the status, so the timeout does not announce itself here — it does not need to. A killed
  # run prints no `N passed` summary, and the count guard immediately below already treats a missing
  # summary as a hard failure. That is the FAIL-ARMED direction: a truncated run goes red on its own.
  timeout "${PREFLIGHT_PYTEST_TIMEOUT}" \
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
  else
    # ⛔ THE GATE NOW DIFFS A LIST, NOT A COUNT, AND THAT CHANGE IS AN INCIDENT FIX (2026-08-08).
    # A count cannot tell a new real failure from a missing module. Measured: a genuine regression
    # (test_lint_citations.py::test_the_ledger_does_not_anchor_itself, broken by a newly committed
    # artifact) took the count 48 -> 49, sat under the baseline of 50, and this gate printed
    # PREFLIGHT OK -- "all dep-related, green in CI", asserted without checking. That tree was pushed
    # and turned `main` red, where CI with full deps reported exactly 1 failure against 7,363 passes.
    #
    # ⚠ THE PREVIOUS VERSION KNEW THIS ABOUT ITSELF. It printed, correctly, "THE NEW FAILURE(S) ARE NOT
    # IDENTIFIED BELOW ... This gate tracks a COUNT, not a list", and that honesty was mistaken for
    # sufficiency -- a limitation stated in prose is still a limitation. It only ever printed when the
    # count was EXCEEDED, so the case that actually bit (a real failure that fits under the ceiling,
    # because a dep failure was fixed or never counted) produced no warning at all.
    # Superseded, retained (CLAUDE.md rule 1.2): the `-gt "$BASELINE_FAILURES"` count comparison and
    # its "excess:" readout. BASELINE_FAILURES is kept only as the cross-check below.
    base=research/modalities/tests/sandbox-failure-baseline.txt
    if [ ! -f "$base" ]; then
      echo "   FAILED: $base is missing. Without it this gate would fall back to trusting a count,"
      echo "           which is the defect it was built to remove. Restore it from git."
      rc=1
    else
      got=$(mktemp); known=$(mktemp)
      grep -E '^FAILED' "$out" | sed 's/^FAILED //; s/ - .*//' | sed 's/[[:space:]]*$//' | sort -u >"$got"
      grep -v '^#' "$base" | sed '/^[[:space:]]*$/d' | sort -u >"$known"
      new=$(comm -23 "$got" "$known"); fixed=$(comm -13 "$got" "$known")
      if [ -n "$new" ]; then
        echo "   FAILED: $(printf '%s\n' "$new" | wc -l | tr -d ' ') failure(s) NOT in the sandbox baseline."
        echo "   ⚠ These are NEW and are named in full -- they are not the known dep gap:"
        printf '%s\n' "$new" | sed 's/^/     /'
        echo "   If one is genuinely a missing-dependency failure, trace it to the module and add it to"
        echo "   $base in the same commit, with the reason. Never add one to silence it."
        rc=1
      else
        echo "   OK ($failed failure(s), every one named in the sandbox baseline as dep-related;"
        echo "       $errored module(s) could not be imported here and are counted separately)"
      fi
      if [ -n "$fixed" ]; then
        # Not a failure: the list is meant to shrink, and a stale entry quietly widens what is tolerated.
        echo "   ⓘ $(printf '%s\n' "$fixed" | wc -l | tr -d ' ') baseline entr(y/ies) no longer fail -- prune them from $base:"
        printf '%s\n' "$fixed" | sed 's/^/     /'
      fi
      # Cross-check the retained count against the list, so the two can never disagree silently.
      if [ "$failed" -gt "$BASELINE_FAILURES" ] && [ -z "$new" ]; then
        echo "   ⓘ $failed failures exceeds the retained count baseline $BASELINE_FAILURES, but every one is"
        echo "     in the list. Lower BASELINE_FAILURES or re-check the list -- they have drifted apart."
      fi
      rm -f "$got" "$known"
    fi
  fi
  rm -f "$out"
fi

if [ "$rc" -ne 0 ]; then
  echo; echo "PREFLIGHT FAILED -- do not commit."
else
  echo; echo "PREFLIGHT OK"
fi
exit "$rc"
