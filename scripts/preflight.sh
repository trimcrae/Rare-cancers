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
# ⭐ SANDBOX NOTE, CORRECTED 2026-08-23: THE DEPS ARE INSTALLABLE AND NOW INSTALLED BY A SCRIPT.
# `./scripts/dev-setup.sh` provisions both interpreters and a SessionStart hook runs it
# `--if-needed`, so a fresh box no longer fails these tests: the run that fixed it went from
# 9 failed + 20 errors to **878 passed** on the manuscripts suite and 7,859 passed on modalities,
# with no tracked file touched. The baseline machinery below stays exactly as it is, because it
# describes the environment a session gets BEFORE that hook has run — and if the hook is ever
# absent or fails, this is again the only thing standing between a dep gap and a false green.
# ⚠ Superseded, retained (CLAUDE.md rule 1.2): "this box lacks the scientific deps, so those tests
# fail here and pass in CI, where the baked images supply them." MEASURED 2026-08-05, rather than remembered -- absent: numpy, scipy, pymbar,
# rdkit, boto3, netCDF4; present: pyyaml, jsonschema. (The line here used to name "scipy, pymbar, rdkit"
# and omitted numpy and boto3, which between them account for 29 of the 48 baseline failures.) Rather
# than hide that behind an ignore list -- which would be the very "silently measures nothing" pattern
# above -- the test step reports a BASELINE count and fails only when failures EXCEED it. Update the
# baseline deliberately, in a commit, when the environment changes.
#
# Usage:  ./scripts/preflight.sh                      # the commit loop: the ten fast gates
#         PREFLIGHT_TESTS=1 ./scripts/preflight.sh    # + the manuscripts suite (~4 min)
#         PREFLIGHT_MODALITIES=1 ./scripts/preflight.sh  # + the modalities suite (~8 min), ALONE
#   ⚠ Superseded, retained: "PREFLIGHT_MODALITIES=1 PREFLIGHT_TESTS=1 …  # + the modalities suite
#     too (~8 min more)". That spelling was the ONLY place in the repository that described the two
#     flags as needing each other, and it matched the code — which is how the coupling survived: the
#     modalities stage was nested inside the PREFLIGHT_TESTS block, so the modalities flag was an
#     AND and did nothing on its own. Fixed 2026-08-26; the two flags are independent and either
#     may be given alone. Evidence and the reasoning: the note beside the outer gate.
#   ⚠ Superseded, retained: "+ both suites, modalities scoped to the change". PREFLIGHT_TESTS no
#     longer implies modalities — see the note beside RUN_MODALITIES — and "scoped to the change"
#     had not been true for days: the selector was answering FULL on every run.
#         PREFLIGHT_FULL=1 ./scripts/preflight.sh     # + everything, unscoped -- PUBLICATION ONLY
#         SKIP_TESTS=1 ./scripts/preflight.sh         # retired spelling of the default; still honoured
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
# ⛔ DERIVED FROM THE LIST, NEVER TYPED (CLAUDE.md rule 1.1: "a total is DERIVED, never typed --
# hand-carried totals drift silently"). This was hard-coded at 50 while the authoritative baseline
# list held 53, so every run printed a drift notice on an otherwise green build -- and a green build
# that always carries a note is a note nobody reads. The list is the source of truth; the count is a
# cross-check on it, so computing one from the other makes the two structurally unable to disagree.
# Superseded, retained: `BASELINE_FAILURES="${PREFLIGHT_BASELINE_FAILURES:-50}"`.
# ⚠ THIS DOES NOT WEAKEN THE GATE. What actually fails a run is a failure NOT NAMED in the list, and
# that check is untouched -- see the `comm -23` below. Deriving the count removes bookkeeping noise;
# it does not raise a ceiling, because the ceiling was never what caught anything.
# ⛔⛔ THE TRAP GOES HERE, ABOVE EVERY LINE THAT CAN ABORT — AND THE FIRST VERSION DID NOT (2026-08-23).
# It was installed after the baseline count, which is the line that actually died, so it reported
# nothing on the very failure it was written for. Verified by re-introducing that failure: trap
# below the assignment -> 0 bytes of output; trap above it -> the message. A `set -e` abort during
# setup otherwise produces ZERO stdout and ZERO stderr, which reads as "nothing ran" and is
# indistinguishable from a killed process — the exact ambiguity that makes a silent gate dangerous.
# ⛔⛔ AND IT MUST COVER THE WHOLE RUN, NOT JUST SETUP (2026-08-23). An unguarded `grep` in a pipeline
# aborted this script AFTER the modality suite reported 7,804 passing and zero failures, so every
# gate below that line never ran and the only evidence was `PF_EXIT=1` with no message. That is the
# same shape as the 2026-08-12 incident recorded at the `comm` block, and it is worse than a failing
# check: a failing check names itself, while this one leaves a green-looking log and an exit code
# nobody reads. `_preflight_summary_reached` is set only where the run prints its own verdict, so
# any exit before that is reported here with the line that caused it.
_preflight_reached_first_check=0
_preflight_summary_reached=0
_preflight_died() {
  if [ "$_preflight_summary_reached" = 1 ]; then
    return
  fi
  if [ "$_preflight_reached_first_check" = 0 ]; then
    echo "PREFLIGHT ABORTED DURING SETUP at ${BASH_SOURCE[0]}:${1} -- NO CHECK RAN." >&2
    echo "  A clean working tree proves nothing here: the gate never started." >&2
  else
    echo "PREFLIGHT ABORTED MID-RUN at ${BASH_SOURCE[0]}:${1}, before its summary." >&2
    echo "  ⛔ EVERY GATE BELOW THAT LINE NEVER RAN. The checks that printed OK above are the only" >&2
    echo "     ones that executed; this is NOT a pass, and the usual cause is a command whose" >&2
    echo "     non-zero exit propagates under 'set -euo pipefail' -- a grep matching nothing is the" >&2
    echo "     one that has done it twice." >&2
  fi
}
trap '_preflight_died $LINENO' ERR

_baseline_file=research/modalities/tests/sandbox-failure-baseline.txt
# ⛔⛔ `|| true` IS LOAD-BEARING: AN EMPTY BASELINE KILLED THIS SCRIPT SILENTLY (2026-08-23).
# `grep -v '^#'` exits 1 when it selects NOTHING, which is exactly what happens once every entry has
# been pruned -- and pruning to empty is the end state a PREFLIGHT_FULL=1 run advises you toward, so
# this was waiting for whoever finished the job. Under `pipefail` the pipeline then exits 1, and
# under `set -e` the assignment aborts the script BEFORE THE FIRST echo: zero stdout, zero stderr,
# exit 1. A gate that fails with no output is the "reports while measuring nothing" defect this
# file's own header was written about, in the file itself.
BASELINE_FAILURES="${PREFLIGHT_BASELINE_FAILURES:-$(
  { grep -v '^#' "$_baseline_file" 2>/dev/null || true; } |
    sed '/^[[:space:]]*$/d' | sort -u | wc -l | tr -d ' '
)}"
BASELINE_FAILURES="${BASELINE_FAILURES:-0}"
rc=0
_preflight_reached_first_check=1

# ⭐⭐ THE TEST SUITES LEFT THE DEFAULT COMMIT LOOP ON 2026-08-23 (trimcrae: *"change the rules so
# that it's not constantly running and blocking things"*), AND THE NUMBERS ARE WHY.
#
#   ten fast gates                    31.4 s
#   + gate 13, the selector contract   39.3 s   <- added by `main` after this was measured; it runs
#                                                  unconditionally, so the DEFAULT tier is 77.5 s
#   + manuscripts suite              176.1 s   <- 878 tests, run in full on EVERY commit
#   + modalities suite                 ~0 s    <- already scoped; a typical change selects nothing
#
# So the gate was ~85 % one step, and that step ran identically whether the change was a manuscript
# rewrite or nothing at all: the measurement that opened this was a run on a CLEAN TREE at
# origin/main, which still executed all 878.
#
# ⚠ AND GATE 13 IS NOW HALF THE DEFAULT LOOP, WHICH IS WORTH SOMEBODY'S DECISION RATHER THAN MY
# SILENT ONE. It was added on `main` on the reasoning that it is "a fast, offline, pure-logic suite";
# measured here it is **39.3 s of the 77.5 s**, because each of its 55 tests builds the selector's
# import graph over ~400 modules and shells out to git. It is left exactly where `main` put it --
# reversing another session's deliberate placement inside a merge is not this change's business --
# but the "fast" in that note is not what the clock says, and moving it under PREFLIGHT_TESTS would
# take the commit loop to ~31 s.
#
# ⛔ AND SCOPING IT WAS TRIED FIRST, PROPERLY, AND THE MEASUREMENT KILLED IT. A selector for this
# suite was built and validated against ground truth — all 50 guards traced in their own processes
# to record every file each one really reads — and it reached ZERO under-selection. It still could
# not help: these guards bind to directory scans and to paths read out of committed artifacts, so
# 28 of 50 are unscopeable on their own terms and the floor stayed at 132.5 s of 176.1 s. A 25 %
# saving is not worth a new selector's failure surface, so it was reverted rather than shipped. The
# honest finding is that this suite is not scopeable, not that nobody had tried.
#
# ⚠ THIS IS THE 2026-08-12 ARGUMENT, APPLIED TO THE STEP IT ORIGINALLY SPARED. That day's note says
# it in full, about the other suite: *"the expensive copy is the WEAKER one … tests.yml runs
# `on: push` WITH those dependencies installed, so the version of this suite that means something
# runs in CI on every push regardless"*, and CLAUDE.md §6 draws the conclusion — **"Watch CI; do not
# pre-run it locally."** CI is the authority and it runs both suites in full on every push.
#
# ⛔⛔ AND HERE IS WHAT THIS COSTS, STATED PLAINLY RATHER THAN GLOSSED. Gate 12 was put in the commit
# loop on 2026-08-12 for a real reason, recorded below: *"a citation guard that only fires after the
# push is a citation guard that fires after the mistake is shared."* That reason does not evaporate
# — it is now paid. What makes it payable is the distinction CLAUDE.md §6 draws between rigour of
# CONTENT, which never relaxes, and ceremony of GATING, which scales with who reads the result: a
# push to this repository is read by CI and by the next session, both of which see the failure and
# fix it with another commit. **Publication is unchanged and still requires PREFLIGHT_FULL=1.**
# ⚠ If you are about to commit a manuscript, its SI, a citation or a deposit artifact,
# `PREFLIGHT_TESTS=1` is one word and 176 s. Spend it there; that is what the flag is for.
# ⛔⛔ RESOLVED OUTSIDE THE TEST TIER, AND THAT IS A BUG FIX, NOT A TIDY-UP (2026-08-24).
# These two were assigned INSIDE the `if` that runs the suites, while the scripts-selector gate near
# the end of this file uses `$PYTEST` unconditionally. Under `set -u` that is an unbound variable
# the moment the suites do not run. ⚠ MEASURED ON `main` BEFORE THIS BRANCH TOUCHED IT:
# `SKIP_TESTS=1 ./scripts/preflight.sh` dies with `PYTEST: unbound variable` at that gate. It was
# latent there because skipping was the unusual path; making the fast tier the DEFAULT would have
# fired it on every single run, so the merge that changes the default is the merge that owes the fix.
# ⛔ HOW PYTEST IS INVOKED, AND WHY IT IS NOT `python3 -m pytest` (measured 2026-08-15).
# Both test steps below called `python3 -m pytest` and BOTH reported "No module named pytest" in
# this sandbox, which the count guard correctly turned into a hard FAILED -- so preflight could
# not be run at all, and the only ways past it were to skip tests or to mask the exit code. The
# cause is not a missing pytest: `pytest --version` answers 9.0.2. It is installed as a **uv
# tool**, in an isolated venv under /root/.local/share/uv/tools/pytest, whose interpreter is not
# the `python3` on PATH -- so the console script works and `-m` cannot. Resolved once, here, and
# exported, rather than at each call site: a per-call fallback is how one of the two steps ends up
# fixed and the other silently left behind. If neither form exists, PYTEST stays as `python3 -m
# pytest` so the run still FAILS loudly with the same message rather than skipping quietly --
# never resolve this to `true` or to a no-op.
#
# ⛔ THE ORDER OF THESE TWO BRANCHES IS LOAD-BEARING, AND THE CONSOLE-SCRIPT FALLBACK IS A TRAP
# (measured 2026-08-15, the same day, an hour after the block above was written). Resolving to the
# bare `pytest` on PATH made the gate report **36 failures that do not exist**: that pytest was a
# uv TOOL, and a uv tool runs in its OWN isolated venv, so `import yaml` failed inside the tests
# while `python3 -c "import yaml"` succeeded in the shell one line earlier. Every one of the 36 was
# a ModuleNotFoundError for a package the repository actually has. They were proved spurious the
# expensive way -- a worktree at origin/main, the same eight files, two-sided `comm` on the failure
# NAME SETS: 39 on main, 39 on branch, both directions EMPTY.
# ⚠ SO A GREEN `python3 -c "import pytest"` IS NOT MERELY THE PREFERRED BRANCH, IT IS THE ONLY ONE
# THAT SEES THE REPOSITORY'S DEPENDENCIES. The fix when the first branch is false is to
# `python3 -m pip install pytest`, NOT to fall through -- the fallback exists so the gate can still
# run somewhere degraded, and its failures must be read as suspect until traced. A gate that
# invents failures is as broken as one that hides them: this one nearly got 36 healthy tests
# written into the sandbox baseline as permanent known-failures, which would have masked a real
# regression in any of them forever.
if python3 -c "import pytest" >/dev/null 2>&1; then
  PYTEST="python3 -m pytest"
elif command -v pytest >/dev/null 2>&1; then
  PYTEST="pytest"
else
  PYTEST="python3 -m pytest"
fi

# ⛔ THE GATE WAS SINGLE-THREADED ON A FOUR-CORE BOX, AND THAT COST 16 MINUTES A RUN.
# Measured 2026-08-17 on this tree: the modalities suite is 968.9s serial and 336.9s at `-n 4
# --dist loadfile`, a 2.9x saving, with the verdict IDENTICAL -- 14 failed, 7,756 passed, 58
# skipped both ways, the same 14 tests by name, every one already in sandbox-failure-baseline.txt,
# and the working tree clean afterwards.
# ⚠ `--dist loadfile` IS LOAD-BEARING, NOT A TUNING CHOICE. Several tests regenerate a committed
# artifact and then assert against it; distributing by TEST rather than by FILE would let two
# workers race the same file and produce failures that are real-looking and untrue. Keeping every
# test in a file on one worker preserves the within-file ordering those tests rely on. The clean
# tree after the parallel run is the evidence that no regeneration raced.
# ⛔ IF XDIST IS ABSENT, RUN SERIAL. A missing plugin must slow the gate down, never skip it.
# ⛔⛔ THE PROBE ASKED THE WRONG INTERPRETER, AND THE 2.9x SPEEDUP HAD BEEN OFF THE WHOLE TIME
# (measured 2026-08-23). This tested `python3 -c "import xdist"` while the tests run under $PYTEST,
# which in this sandbox is a uv TOOL in its own venv — the identical trap the block above this one
# documents at length for pytest itself, repeated 20 lines later for its plugin. Evidence: neither
# interpreter had xdist at all, so the branch was correctly false; but once installed it would have
# gone into the tool venv and this line would STILL have said no. Measured cost of the miss on the
# run that found it: the modalities suite took **1090.4 s serial** where this file's own note
# records 336.9 s at `-n 4`. ⭐ So the probe now runs under the same interpreter as the tests, via
# pytest's own plugin list — the one answer that cannot disagree with what the run will do.
PYTEST_PAR=""
if [ "${PREFLIGHT_SERIAL:-0}" != "1" ] && $PYTEST --version --version 2>/dev/null | grep -q xdist; then
  _cores=$(nproc 2>/dev/null || echo 1)
  [ "$_cores" -gt 1 ] && PYTEST_PAR="-n $_cores --dist loadfile"
fi


RUN_TESTS=0
[ "${PREFLIGHT_TESTS:-0}" = "1" ] && RUN_TESTS=1
[ "${PREFLIGHT_FULL:-0}" = "1" ] && RUN_TESTS=1

# ⭐⭐ THE MODALITIES SUITE IS OFF IN THE COMMIT LOOP AS OF 2026-08-25 (trimcrae: "Just turn off
# modalities completely if it's that big an issue"). `PREFLIGHT_MODALITIES=1` runs it; so does
# PREFLIGHT_FULL=1.
#
# ⛔ MEASURED, NOT ESTIMATED. Four runs that day: modalities 481-535 s against manuscripts 225-255 s,
# the fast gates ~31 s and the selector's own suite ~55 s. Modalities was about 62% of a 13.5-minute
# gate, and EVERY run of it was the full 7,924 tests.
#
# ⛔ AND IT WAS FULL FOR A REASON NOBODY CHOSE. `affected_tests.py` fails safe: if the selector or
# this script differ from the content `scripts/selector-validation.json` says a FULL run validated,
# it answers FULL. Both hashes are stale — preflight.sh changed 2026-08-23, affected_tests.py
# arrived by merge 2026-08-24 — and the ONLY thing that re-stamps that record is a PREFLIGHT_FULL=1
# run, which CLAUDE.md §6 reserves for publication. So the tripwire could only be cleared by an act
# that is meant to be rare, and until then every commit paid eight minutes to re-run docking, ABFE
# and GPU-fleet tests that a manuscript edit cannot reach.
# ⚠ That diagnosis is UNCHANGED BY THIS FLAG and is not fixed by it. Re-stamping the record is a
# separate decision; this only stops the commit loop paying for it.
#
# ⛔⛔ WHAT THIS COSTS, STATED PLAINLY: a modality break is no longer caught before the commit. It is
# caught by `tests.yml`, which runs BOTH suites in full on every push with the real dependencies and
# is the authority — the same trade this repository already made for the manuscripts suite on
# 2026-08-23. Minutes later rather than never, and one more commit to fix it.
RUN_MODALITIES=0
[ "${PREFLIGHT_MODALITIES:-0}" = "1" ] && RUN_MODALITIES=1
[ "${PREFLIGHT_FULL:-0}" = "1" ] && RUN_MODALITIES=1
# ⚠ RETIRED SPELLING, HONOURED ON PURPOSE. `SKIP_TESTS=1` was how a docs-only change opted out when
# tests were the default. It is now the default, so the variable can only ever mean "and I still
# do not want them" -- which is already true. Kept so an old command line or a stale note does not
# fail; it is deliberately not an error.
[ "${SKIP_TESTS:-0}" = "1" ] && RUN_TESTS=0

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
# ⛔ A GATE THAT FAILS ON A MISSING IMPORT MUST SAY SO, BECAUSE THE RED LOOKS IDENTICAL OTHERWISE
# (2026-08-23). `main` came up red on a CLEAN TREE at origin/main: this gate wanting `jsonschema`
# and 29 manuscript guards wanting pdfminer/pypdf, while CI was green on the same commit. The
# script reported "FAILED -- rerun to see why", which is true and sends the next session hunting a
# defect in the systems model. Naming the cause is not a weakening: the gate still FAILS, and it
# must — a check that cannot run has not passed. It just stops misattributing.
_dep_hint() {
  echo "   ⭐ that is a MISSING PACKAGE, not a defect in the repository — run ./scripts/dev-setup.sh"
  echo "     (a SessionStart hook runs it with --if-needed; if you are seeing this, it did not)"
}
echo "== systems model (invariants, pointers, view drift) =="
_sc=$(mktemp)
if python3 systems/systems_check.py --check >"$_sc" 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 systems/systems_check.py --check' to see why"; rc=1
  { grep -qE "No module named|needs .jsonschema." "$_sc" && _dep_hint; } || true
fi
rm -f "$_sc"

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
# ⛔⛔ lint_claims RUNS HERE NOW, AND ROUND 9 IS WHY (2026-08-22). It was CI-only by design, on the
# reading that CI would catch it. What actually happened: a manuscript repair introduced a word that
# fires R2, preflight went green, the commit shipped, and CI failed at this step -- which SKIPS the
# 26 steps behind it, so citation provenance, prose style and every manuscript test went unrun on
# that commit too. A gate whose failure blinds the rest of the suite belongs in the commit loop.
echo "== claim strength (R1-R5: selectivity, efficacy, safety, window, readiness) =="
if python3 research/manuscripts/lint_claims.py >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 research/manuscripts/lint_claims.py' to see which claim"; rc=1
fi

# ⚠ AND lint_changed_prose, WHICH RAN NOWHERE AT ALL -- not in preflight, not in tests.yml. It is the
# only instrument that watches for a qualifier being dropped from a claim by an edit, which is the
# defect class that produced most of rounds 9-11's findings. It reports warnings rather than errors,
# so it cannot fail the build; printing them is the whole point.
echo "== changed prose (a qualifier dropped by an edit) =="
python3 research/manuscripts/lint_changed_prose.py || true

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

# ⚠ ADVISORY ON PURPOSE — IT PRINTS, IT NEVER SETS rc. trimcrae, 2026-08-27: "Good prose is going to
# come from better writing style rather than metrics. Though the metrics could be a decent screening
# layer." Gating the commit loop on a readability number would instruct this loop to shorten sentences
# by any means available, and the cheapest means is deleting the difficult truth. The HARD half lives
# where it belongs: publish_bar clause 7, which blocks an outgoing version — not a commit — on a
# sentence past the ceiling or a fall in caution.
echo "== readability screen (ADVISORY: where to look, not whether the prose is good) =="
python3 research/manuscripts/lint_readability.py --report 2>/dev/null | tail -n +1 | sed 's/^/   /' || true

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

# ⛔ A FILE MARKED "GENERATED" WAS AN INSTRUCTION TO HUMANS BACKED BY NOTHING (added 2026-08-16).
# Four deposit artifacts are produced by generators and carry GENERATED banners, and no gate ever
# re-derived any of them. Round 7 measured THREE of the four stale at once: the archive manifest 78
# commits behind HEAD (so the recorded manuscript hash described a pre-restructure file), and
# submission-metrics.json under-counting by 263 main words while every other deposit document
# defers to it as "the one home" for those counts. Both had been wrong for weeks under nine green
# gates, because "is this file current?" was a question nothing could ask.
# ⚠ THE MANIFEST ALREADY HAD A --check MODE AND NO GATE RAN IT. Two of the others were given one in
# the same pass that added this block; the fourth (submission_packet.py) still has none and is
# named as unverified by scripts/regenerate_aso_chain.sh rather than silently assumed current.
# ⚠ POSITION IS LOAD-BEARING, AND NOT FOR A TECHNICAL REASON. This gate was first inserted BEFORE
# the parser guard, which pushed the registry validator from gate 7 to gate 8 -- and four documents
# (README.md, CONTRIBUTING.md, systems/POLICY-evidence.md and .claude/skills/repo-gates/SKILL.md)
# state its ordinal in prose. systems_check's P1 rule caught all four immediately, which is the
# one-fact-one-place rule doing its job on a change that looked purely additive. Appending here
# leaves every existing ordinal untouched; it still runs before the test steps, which is all this
# gate's placement actually requires. ⛔ Insert a new gate ABOVE this line and you will move an
# ordinal that four documents hard-code.
echo "== generated deposit artifacts reproduce from their generators =="
gen_fail=""
# ⛔ THE MANIFEST TAKES `--check-archive`, NOT `--check`, AND THE DIFFERENCE IS NOT COSMETIC.
# `aso_archive_manifest.py` stamps `git_revision`, which advances on EVERY commit — including
# commits touching no archived file — so `--check` is red the instant you commit the manifest you
# just regenerated. Measured 2026-08-17: PREFLIGHT_FULL=1 failed on exactly that, one commit after
# the manifest was regenerated and committed. The generator's own header had predicted it in words
# and said not to wire `--check` into preflight; this gate did anyway.
# ⚠ THE FIX IS NOT TO DROP THE MANIFEST FROM THE GATE. A cry-wolf gate gets relaxed, and the
# relaxation that suggests itself is removing the row — which is how a REAL hash-list staleness
# would then go unwatched. `--check-archive` compares everything except the two repository-state
# fields, so it still fails when the inventory, the hashes or the promises move, and no longer
# fails because a commit happened. The strict `--check` remains the pre-deposit check.
for g in "research/manuscripts/submission_tables.py|submission tables|--check" \
         "research/manuscripts/submission_citations.py|submission references|--check" \
         "research/manuscripts/submission_metrics.py|submission metrics|--check" \
         "research/manuscripts/aso_sequence_manifest.py|canonical sequence file|--check" \
         "research/manuscripts/aso_journal_tables.py|journal article tables|--check" \
         "research/modalities/aso_offtarget_duplex_energy.py|offtarget duplex energy|--check" \
         "research/manuscripts/submission_packet.py|submission packet|--check" \
         "research/manuscripts/vaccine_path_tables.py|vaccine-path manuscript tables|--check" \
         "research/manuscripts/aso_archive_manifest.py|archive manifest|--check-archive" \
         "research/modalities/emc_condensate_report.py|condensate CALVADOS findings|--check"; do
  gen="${g%%|*}"; rest="${g#*|}"; label="${rest%%|*}"; mode="${rest##*|}"
  # ⛔ THE GENERATOR'S OWN FAILURE TEXT REACHES THE READER AS OF AUT-PD-016 (2026-08-27). This line
  # was `python3 "$gen" "$mode" >/dev/null 2>&1`, so every producer's diagnosis was discarded and
  # the only remedy a reader ever saw was the generic "rerun and commit the result" below. For the
  # archive manifest that generic advice is ACTIVELY WRONG — it is what regenerates the artifact
  # against the same dirty tree and reproduces the defect — and the generator now says so in a
  # message nobody could read. Capturing instead of discarding is what makes a per-producer remedy
  # possible at all, and it costs one variable.
  if gen_out="$(python3 "$gen" "$mode" 2>&1)"; then
    echo "   OK   $label"
  else
    echo "   STALE $label -- rerun 'python3 $gen' and commit the result"
    # ⚠ AND WHERE THE PRODUCER DISAGREES WITH THAT LINE, THE PRODUCER WINS: it knows which of
    # "stale" and "must not be regenerated here" its own exit code meant. Indented so the block
    # reads as the row's detail rather than as a new gate.
    if [ -n "$gen_out" ]; then
      echo "$gen_out" | sed 's/^/          /' || true
    fi
    gen_fail="$gen_fail $label"; rc=1
  fi
done
[ -n "$gen_fail" ] && echo "   ⛔ a stale generated file ships a claim its own artifacts no longer support:$gen_fail"

if [ "$RUN_TESTS" = "1" ] || [ "$RUN_MODALITIES" = "1" ]; then
  # ⚠ EACH STAGE IS GATED ON ITS OWN FLAG, AND THIS OUTER TEST IS AN `OR` FOR THAT REASON.
  # ⛔ MEASURED 2026-08-26 — `PREFLIGHT_MODALITIES=1` WAS INERT ON ITS OWN, FOR A FULL DAY.
  # This outer condition read `[ "$RUN_TESTS" = "1" ]` alone while the modalities stage sat nested
  # inside it, so the modalities flag was an AND with `PREFLIGHT_TESTS` rather than a flag. A run
  # with `PREFLIGHT_MODALITIES=1` and nothing else was byte-identical in structure to a run with no
  # flag at all: zero modality tests executed, and the verdict line printed
  # `PREFLIGHT_MODALITIES=1 for the modalities suite` — offering, as the remedy, the flag that was
  # already set. `PREFLIGHT_FULL=1` sets BOTH, which is why publication was never affected and why
  # nothing caught this.
  # ⚠ THE DOCS AND THE CODE DISAGREED AND THE DOCS WERE THE MAJORITY: CLAUDE.md §6
  # ("`PREFLIGHT_MODALITIES=1` the modalities one"), the note beside RUN_MODALITIES below
  # ("`PREFLIGHT_MODALITIES=1` runs it"), and this script's own verdict line all describe one
  # independent flag; only the usage header's `PREFLIGHT_MODALITIES=1 PREFLIGHT_TESTS=1` example
  # matched the code, and that example is the fossil of the coupling 2026-08-25 removed when it
  # took modalities OUT of `PREFLIGHT_TESTS`. Requiring TESTS to reach MODALITIES is that same
  # coupling in the other direction, so the code is what was wrong.
  # ⚠ Superseded, retained: "ONLY THE MODALITIES STAGE IS GATED HERE. The first cut put
  # `RUN_MODALITIES` on the OUTER block and silently took the manuscripts suite out with it —
  # measured immediately: a run that printed PREFLIGHT OK having executed neither suite." That
  # incident was real and its lesson stands — the manuscripts suite must not ride on the modalities
  # flag — but the fix over-corrected into an AND. The property actually wanted is that each stage
  # answers to its own flag and neither can silence the other, which is what is now written.
if [ "$RUN_MODALITIES" = "1" ]; then
  # ⭐ CHANGE-SCOPED BY DEFAULT, FULL ON DEMAND (trimcrae, 2026-08-12: the suite was the bottleneck,
  # and "only the ones affected by the changes" plus "not on every push, manually before
  # publication").
  #
  # MEASURED, which is why this changed: the modalities step was **745.9 s of a ~15-minute gate**,
  # 87 % of preflight, while the seven doc / systems-model / medical-integrity gates above cost
  # about a minute between them — and those are the ones that have actually caught things here.
  #
  # ⚠ AND THE EXPENSIVE COPY IS THE WEAKER ONE. This sandbox lacks numpy, rdkit, boto3, scipy,
  # pymbar and netCDF4, so 48 of these tests fail as missing imports and five modules do not import
  # at all. `tests.yml` runs `on: push` WITH those dependencies installed, so the version of this
  # suite that means something runs in CI on every push regardless. Twelve local minutes bought a
  # degraded rerun of a check that was about to run properly.
  #
  # ⛔ THE SELECTOR FAILS TO FULL, AND THAT IS THE WHOLE SAFETY ARGUMENT. A changed conftest, a
  # changed test helper, an unparseable source, a git that does not answer, or an edit to the
  # selector or to this script all return FULL rather than a subset — because a gate that quietly
  # runs too little is the "reports while measuring nothing" defect this file was written against,
  # not a faster gate. `scripts/tests/test_affected_tests.py` asserts each of those directions.
  #
  # ⛔ BEFORE ANYTHING OUTWARD-FACING — a preprint, a submission, a release, a DOI — run
  #     PREFLIGHT_FULL=1 ./scripts/preflight.sh
  # Scoping is for the commit loop. It is not a claim that the rest of the suite passes.

  # ⛔ THE SELECTOR IS ASKED ONCE, AND ITS THREE ANSWERS ARE KEPT APART (measured 2026-08-16).
  # This block used to call `affected_tests.py` here, discard the result, and call it AGAIN below to
  # decide whether an empty selection meant "nothing affected". That conflated two opposite answers:
  #   "" from a selector that RAN and found nothing   -> correctly green, run nothing
  #   "" from a selector that DIED before printing    -> must run everything
  # The first call caught the second case safely (`|| echo FULL`) and the second call then threw that
  # away, because a dead selector's stdout is also empty. MEASURED CONSEQUENCE: an editorial pass
  # broke 11 tests in `test_aso_submission_numbers.py` -- all 35 pass at c131f5a30, 11 fail after --
  # and preflight printed "FULL -- the change could not be scoped" IMMEDIATELY followed by "no
  # modality test is affected by this change" and exited 0, having run zero modality tests. Four
  # commits were made against that green.
  # ⚠ This is the header defect of this very file, for the fifth time: a gate that reports while
  # measuring nothing. The rule it violates is the one the block below already states -- an empty
  # selection is a real answer -- but only when the selector actually answered.
  SELECTED=""
  SEL_STATUS=full
  if [ "${PREFLIGHT_FULL:-0}" = "1" ]; then
    echo "== pytest (modalities: FULL, PREFLIGHT_FULL=1) =="
  elif SELECTED="$(python3 scripts/affected_tests.py 2>/dev/null)"; then
    if [ "$SELECTED" = "FULL" ]; then
      SELECTED=""
      echo "== pytest (modalities: FULL -- the selector asked for the full suite) =="
    elif [ -z "$SELECTED" ]; then
      SEL_STATUS=none
      echo "== pytest (modalities: none -- the selector ran and this change affects no module) =="
    else
      SEL_STATUS=scoped
      n=$(printf '%s\n' "$SELECTED" | grep -c . || true)
      echo "== pytest (modalities: $n module(s) affected by this change; PREFLIGHT_FULL=1 for all) =="
    fi
  else
    SELECTED=""
    echo "== pytest (modalities: FULL -- the selector FAILED, so nothing is assumed) =="
  fi
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
  #     $PYTEST $PYTEST_PAR research/modalities/tests/ -q --collect-only --continue-on-collection-errors \
  #       --ignore=research/modalities/tests/test_ternary_endpoint_align.py 2>&1 | grep ModuleNotFoundError
  #
  # ⚠ THAT IS THIS SCRIPT'S OWN HEADER DEFECT, IN THIS SCRIPT. The comment at the top of this file
  # exists because a check "reported while measuring nothing actionable", and names three prior
  # instances. This was a fourth, sitting inside the fix for the first three. `set -euo pipefail` and
  # an explicit exit code do not help when the thing being counted is never produced.
  # ⚠ AN EMPTY SELECTION IS A REAL ANSWER — "this change touches no modality test" — and pytest
  # exits 5 on "no tests ran", which must not read as a failure. It is handled below.
  # ⛔ BRANCH ON SEL_STATUS, NEVER ON EMPTINESS, AND NEVER RE-ASK THE SELECTOR. `$SELECTED` is empty
  # for BOTH "nothing affected" and "run everything"; only SEL_STATUS distinguishes them, and it was
  # decided once, above, where the selector's exit code was still in hand.
  if [ "$SEL_STATUS" = "scoped" ]; then
    # shellcheck disable=SC2086
    $PYTEST $PYTEST_PAR $SELECTED -q --continue-on-collection-errors >"$out" 2>&1 || true
  elif [ "$SEL_STATUS" = "none" ]; then
    echo "no modality test is affected by this change" >"$out"
  else
    $PYTEST $PYTEST_PAR research/modalities/tests/ -q --continue-on-collection-errors \
        --ignore=research/modalities/tests/test_ternary_endpoint_align.py >"$out" 2>&1 || true
  fi
  failed=$(grep -cE '^FAILED' "$out" || true)
  errored=$(grep -cE '^ERROR ' "$out" || true)
  tail -1 "$out"

  # ⛔ A RUN THAT EXECUTED NOTHING IS NOT A PASS. Belt and braces against the failure above returning
  # in another form: if pytest never reports a test count, the parsed failure count is meaningless and
  # this step must go red rather than quietly agree with itself.
  if grep -q '^no modality test is affected by this change$' "$out"; then
    echo "   OK (no modality test is affected; CI runs the full suite on push)"
  elif ! grep -qE '[0-9]+ (passed|failed)' "$out"; then
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
      # ⛔ `|| true` BECAUSE grep EXITS 1 ON NO MATCH AND THIS SCRIPT RUNS `set -euo pipefail`
      # (2026-08-12). No match here means ZERO test failures — the good case — so the pipeline
      # returned 1 and `set -e` killed preflight at exactly the moment everything passed. The
      # damage was not the non-zero exit: gate 9, the manuscript tests, sits BELOW this line and
      # therefore never ran locally at all, while the script's own header comment warns about this
      # precise interaction. A gate that is skipped in silence is the failure mode CLAUDE.md §7
      # records; here the skip was caused by the suite being green.
      grep -E '^FAILED' "$out" | sed 's/^FAILED //; s/ - .*//' | sed 's/[[:space:]]*$//' \
        | sort -u >"$got" || true
      # ⛔⛔ THE SAME `|| true`, AND IT WAS MISSING ON THIS LINE ONLY (2026-08-23). The comment
      # directly above records the 2026-08-12 incident in which an unguarded `grep` in a pipeline
      # "killed preflight at exactly the moment everything passed" — and the fix was applied to one
      # of the pair. This line greps the BASELINE, which exits 1 when the file holds no entries, so
      # once the list was legitimately pruned to empty the script aborted here: 7,804 modality tests
      # passing, zero failures, and every gate BELOW this line silently never ran. One-of-a-pair,
      # inside the fix for the defect it repeats.
      { grep -v '^#' "$base" || true; } | sed '/^[[:space:]]*$/d' | sort -u >"$known"
      new=$(comm -23 "$got" "$known"); fixed=$(comm -13 "$got" "$known")
      # ⛔⛔ THE THIRD SITE OF THE 2026-08-26 FALSE-GREEN DEFECT, AND THE ONE WITH THE MOST TO LOSE.
      # This gate diffs a LIST built from `^FAILED` lines. If those lines are absent while the run
      # really did fail — the state observed that day, in which a preflight printed OK over its own
      # `1 failed, 1209 passed, 3 skipped, 4 errors` — then `$got` is EMPTY, `$new` is empty, and this
      # block reports a clean diff. The list-based design fixed the 2026-08-08 count defect and
      # inherited a different blind spot: an empty list is indistinguishable from a green run.
      # ⚠ Cause still UNKNOWN — five hypotheses tested and refuted (see the manuscripts block). This
      # is a cross-check between two signals that can each fail separately, not a root-cause fix.
      _osum=$(tail -1 "$out")
      _ocount=$({ printf '%s\n' "$_osum" | grep -oE '[0-9]+ (failed|errors?)' || true; } | awk '{s+=$1} END {print s+0}')
      _olisted=$(wc -l <"$got" | tr -d ' ')
      if [ "$_ocount" -gt 0 ] && [ "$_olisted" -eq 0 ]; then
        echo "   FAILED: the summary reports $_ocount failure(s)/error(s) and the parsed list is EMPTY,"
        echo "           so the baseline diff below would compare nothing and report clean. This is the"
        echo "           2026-08-26 false-green state; capture the run's FULL output before rerunning."
        tail -5 "$out"
        rc=1
      fi
      if [ -n "$new" ]; then
        echo "   FAILED: $(printf '%s\n' "$new" | wc -l | tr -d ' ') failure(s) NOT in the sandbox baseline."
        echo "   ⚠ These are NEW and are named in full -- they are not the known dep gap:"
        printf '%s\n' "$new" | sed 's/^/     /'
        echo "   If one is genuinely a missing-dependency failure, trace it to the module and add it to"
        echo "   $base in the same commit, with the reason. Never add one to silence it."
        { grep -q "ModuleNotFoundError" "$out" && _dep_hint; } || true
        rc=1
      else
        echo "   OK ($failed failure(s), every one named in the sandbox baseline as dep-related;"
        echo "       $errored module(s) could not be imported here and are counted separately)"
      fi
      # ⛔ A SUBSET CANNOT SAY A BASELINE ENTRY IS FIXED, AND SAYING SO WOULD BE THE WORST KIND OF
      # WRONG (2026-08-12, with the change-scoped run above). `fixed` is comm(1) over the baseline
      # minus THIS RUN's failures — so a scoped run, which never executed most of the suite, would
      # report every unrun entry as "no longer fails, prune it". Acting on that would delete the
      # baseline wholesale and the next full run would go red against nothing. The list is only
      # meaningful when the run that produced it covered the same population, so it is printed only
      # for a full run; for a scoped one the pruning question is simply not asked.
      if [ -n "$fixed" ] && [ -z "$SELECTED" ]; then
        # Not a failure: the list is meant to shrink, and a stale entry quietly widens what is tolerated.
        echo "   ⓘ $(printf '%s\n' "$fixed" | wc -l | tr -d ' ') baseline entr(y/ies) no longer fail -- prune them from $base:"
        printf '%s\n' "$fixed" | sed 's/^/     /'
      elif [ -n "$SELECTED" ]; then
        echo "   ⓘ scoped run — the baseline-pruning check is skipped (a subset cannot speak for"
        echo "     tests it did not execute). Run PREFLIGHT_FULL=1 to re-derive it."
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
fi   # end of the modalities stage

if [ "$RUN_TESTS" = "1" ]; then
  # ⚠ EXPLICIT, because the outer block above is now an OR. Under `PREFLIGHT_MODALITIES=1` alone
  # this stage must NOT run — that is the 2026-08-12 incident's lesson kept intact — and under
  # `PREFLIGHT_TESTS=1` alone it must, which is what it always did.

  # ⛔ GATE 9: THE MANUSCRIPT TESTS, WHICH THIS SCRIPT DID NOT RUN UNTIL 2026-08-12.
  #
  # CI has run `research/manuscripts/tests` since 2026-08-03 and preflight never did, so a session
  # could read PREFLIGHT OK and push a manuscript guard failure — the exact shape of the 2026-08-06
  # incident recorded in CLAUDE.md §7, where gate 3 was CI-only and a disputed cell line reached
  # `main` behind a green local run. What made this worth closing today rather than noting: the
  # newest guard here is `test_submission_citations.py`, and citation integrity is the repository's
  # FIRST golden rule. A citation guard that only fires after the push is a citation guard that
  # fires after the mistake is shared.
  #
  # ⚠ RUN SEPARATELY, NOT FOLDED INTO THE INVOCATION ABOVE. That one diffs its failures against
  # `sandbox-failure-baseline.txt`, whose entries are all modalities test IDs; widening its scope
  # would silently change what the baseline is a baseline OF. These have no dep gap in this sandbox
  # — 151 passed, 0 failed, measured the day this gate was added — so the bar here is simply zero.
  echo "== pytest (manuscripts: endpoints, systems map, pooling, submission citations) =="
  mout=$(mktemp)
  $PYTEST $PYTEST_PAR research/manuscripts/tests -q --continue-on-collection-errors >"$mout" 2>&1 || true
  tail -1 "$mout"
  # ⛔⛔ READ THE COUNT, NOT ONLY THE `^FAILED` LINES — MEASURED 2026-08-26, IN THIS FILE'S OWN LOG.
  # A preflight run printed `PREFLIGHT OK` while THIS step's own `tail -1` said
  #     1 failed, 1209 passed, 3 skipped, 4 errors in 721.19s
  # because the `^(FAILED|ERROR )` grep below found nothing to match. The gate had the truth in hand,
  # printed it to the log, and then decided on a different signal.
  # ⚠ THE MECHANISM IS UNKNOWN AND IS RECORDED AS UNKNOWN. Five hypotheses were tested against real
  # runs and every one was REFUTED: xdist suppressing the summary (it does not, `-n 4 --dist loadfile`
  # emits them), an OOM-killed worker (emits them), colour codes breaking the `^` anchor (plausible in
  # principle, but the log carries zero escape sequences), a pytest config or conftest changing
  # reporting (neither exists in this repo), and collection errors from half-written files (emit
  # `ERROR ` lines normally). So this is NOT a fix derived from a root cause — it is a fix derived
  # from the observation that the count and the lines can DISAGREE, which is all that is needed.
  # ⭐ THE COUNT IS THE MORE TRUSTWORTHY SIGNAL because pytest always emits it and this script already
  # prints it. The lines are kept as an INDEPENDENT second signal, and either one alone turns the step
  # red. Two signals that can each fail separately are the whole point (CLAUDE.md §4).
  # ⛔ AND A DISAGREEMENT BETWEEN THEM IS ITSELF REPORTED, LOUDLY, rather than resolved silently: the
  # unexplained state above IS a disagreement, so the next occurrence must arrive with its evidence
  # attached instead of being absorbed by whichever signal happened to fire.
  # ⚠ Counted from the SUMMARY LINE ONLY, never the whole file — "3 failed" inside a traceback or a
  # test's own name would otherwise manufacture a failure, which is the red-on-true-input hazard that
  # gets a gate switched off (`paper-hardening` §8b.1).
  # ⛔ `|| true` INSIDE THE BRACES, NOT AFTER THE PIPELINE. grep exits 1 on NO MATCH, which here
  # means ZERO failures — the GOOD case — and `set -euo pipefail` propagates that, killing the run
  # at the instant everything passed. This file already records the same shape twice (2026-08-12,
  # 2026-08-23) and it was reintroduced HERE on 2026-08-26 inside the fix for the false-green
  # defect, then caught by the abort banner: `PREFLIGHT ABORTED MID-RUN at :790`, every gate below
  # it unrun. ⚠ A guard added to a gate is a change to the gate and inherits every trap the gate
  # has — including the ones its own comments warn about 200 lines up.
  _msum=$(tail -1 "$mout")
  _mcount=$({ printf '%s\n' "$_msum" | grep -oE '[0-9]+ (failed|errors?)' || true; } | awk '{s+=$1} END {print s+0}')
  _mlines=$(grep -cE '^(FAILED|ERROR )' "$mout" || true)
  if ! grep -qE '[0-9]+ (passed|failed)' "$mout"; then
    echo "   FAILED: pytest reported no test count -- the run collected nothing."
    tail -5 "$mout"; rc=1
  elif [ "$_mcount" -gt 0 ] && [ "$_mlines" -eq 0 ]; then
    echo "   FAILED: the summary reports $_mcount failure(s)/error(s) and NOT ONE is named by a"
    echo "           '^FAILED'/'^ERROR ' line. That disagreement is the 2026-08-26 false-green state"
    echo "           and its cause is still unknown -- capture this run's FULL output before rerunning,"
    echo "           because '$mout' is deleted below and only 'tail -1' reaches the log."
    tail -5 "$mout"; rc=1
  elif [ "$_mcount" -gt 0 ] || [ "$_mlines" -gt 0 ]; then
    echo "   FAILED:"; { grep -E '^(FAILED|ERROR )' "$mout" || true; } | sed 's/^/     /'
    # ⛔ `|| true` ON THE HINT TOO, FOR THE REASON THE LINE ABOVE CARRIES IT. `grep -q X && f` is a
    # single AND-list: when grep finds nothing it returns 1, the list returns 1, and `set -e` kills
    # the run at the moment there was nothing to report. That is the empty-baseline death this file
    # was just fixed for twice; a new call site must not reintroduce its shape.
    { grep -q "ModuleNotFoundError" "$mout" && _dep_hint; } || true
    rc=1
  else
    echo "   OK"
  fi
  rm -f "$mout"
fi   # end of the manuscripts stage

fi   # end of the "either large suite was asked for" block

# ⛔⛔ THE SELECTOR'S OWN TESTS RAN NOWHERE (2026-08-22, round 14 seat 4). This script cites
# scripts/tests/test_affected_tests.py as the evidence for the selector's safety contract -- "the
# selector fails to FULL, and that is the entire safety argument" -- and neither this script nor
# tests.yml ever executed that directory. There is no pytest.ini or testpaths either, so nothing
# collected it by accident. Nineteen assertions about the gate that decides what this script runs,
# asserted by nobody. It is a fast, offline, pure-logic suite; it runs every time now.
echo "== pytest (scripts: the test selector's own contract) =="
sout=$(mktemp)
$PYTEST $PYTEST_PAR scripts/tests -q --continue-on-collection-errors >"$sout" 2>&1 || true
tail -1 "$sout"
# ⛔ SAME TWO-SIGNAL DECISION AS THE MANUSCRIPTS BLOCK ABOVE, AND IT IS HERE FOR THE REASON THAT
# BLOCK'S COMMENT GIVES: a fix bound to one call site regresses at its sibling (`paper-hardening`
# §8b.2 — measured over 33 mutations, six of eleven list-scoped fixes missed a sibling, and in three
# of those the missed sibling was named in the fix's own comment). This file has already paid for
# that shape twice: the modalities block's careful count-based parser was written in 2026-08-05 and
# the manuscripts block, added later, was still deciding on `grep -q` alone on 2026-08-26.
_ssum=$(tail -1 "$sout")
_scount=$({ printf '%s\n' "$_ssum" | grep -oE '[0-9]+ (failed|errors?)' || true; } | awk '{s+=$1} END {print s+0}')
_slines=$(grep -cE '^(FAILED|ERROR )' "$sout" || true)
if ! grep -qE '[0-9]+ (passed|failed)' "$sout"; then
  echo "   FAILED: pytest reported no test count -- the run collected nothing."
  tail -5 "$sout"; rc=1
elif [ "$_scount" -gt 0 ] && [ "$_slines" -eq 0 ]; then
  echo "   FAILED: the summary reports $_scount failure(s)/error(s) and NOT ONE is named by a"
  echo "           '^FAILED'/'^ERROR ' line -- the 2026-08-26 false-green state, cause still unknown."
  tail -5 "$sout"; rc=1
elif [ "$_scount" -gt 0 ] || [ "$_slines" -gt 0 ]; then
  echo "   FAILED:"; { grep -E '^(FAILED|ERROR )' "$sout" || true; } | sed 's/^/     /'
  rc=1
else
  echo "   OK"
fi
rm -f "$sout"

# The run reached its own verdict, so an exit from here on is the verdict rather than an abort.
_preflight_summary_reached=1

# ⛔ A GREEN LINE MUST SAY WHAT IT MEASURED. "PREFLIGHT OK" after a run that executed no test reads
# as "the suite passes", which is the exact "reports while measuring nothing" defect this file's
# header was written against -- and it would be a NEW instance of it, created by the change that
# made tests opt-in. So the tier is printed in the verdict, every time.
if [ "$rc" -ne 0 ]; then
  echo; echo "PREFLIGHT FAILED -- do not commit."
elif [ "${PREFLIGHT_FULL:-0}" = "1" ]; then
  echo; echo "PREFLIGHT OK (FULL: every gate, both suites unscoped)"
elif [ "$RUN_TESTS" = "1" ]; then
  # ⚠ THIS LINE USED TO SAY "modalities scoped to this change" AND THAT WAS SOMETIMES A LIE — caught
  # on its first real run, which printed it after the selector had asked for the FULL suite (the
  # working tree held an edit to preflight.sh, which is ALWAYS_FULL). The gate heading above already
  # states which mode ran and is derived from the selector; a summary line must not re-assert it
  # from an assumption. One fact, one place.
  if [ "$RUN_MODALITIES" = "1" ]; then
    echo; echo "PREFLIGHT OK (fast gates + manuscripts + modalities -- see the modalities heading"
    echo "             above for its scope)"
  else
    echo; echo "PREFLIGHT OK (fast gates + the manuscripts suite; the MODALITIES suite did NOT run."
    echo "             PREFLIGHT_MODALITIES=1 adds it. CI runs both on push.)"
  fi
elif [ "$RUN_MODALITIES" = "1" ]; then
  # ⛔ THIS BRANCH DID NOT EXIST UNTIL 2026-08-26, AND ITS ABSENCE WAS HALF THE INERT-FLAG DEFECT.
  # `PREFLIGHT_MODALITIES=1` alone fell through to the `else` below, which prints "NEITHER large
  # suite ran here" and then offers `PREFLIGHT_MODALITIES=1` as the remedy -- advice to set the flag
  # that was already set. Now that the flag actually runs the suite, the verdict has to be able to
  # say so without claiming the manuscripts suite ran too.
  echo; echo "PREFLIGHT OK (fast gates + the modalities suite -- see its heading above for scope."
  echo "             The MANUSCRIPTS suite did NOT run; PREFLIGHT_TESTS=1 adds it.)"
else
  # ⚠ "no test ran here" WAS WRONG THE MOMENT THIS BRANCH REBASED, AND IT IS THE FAILURE THIS BLOCK
  # EXISTS TO PREVENT. `main` added gate 13 -- the selector's own contract -- and runs it OUTSIDE
  # the tier, so 55 tests DO run in the default loop. A verdict line that names what it measured is
  # worth having only if it is re-derived when the gates move; this one is now written from what
  # actually ran rather than from what the tier was designed to run.
  echo; echo "PREFLIGHT OK (fast gates + the selector's own contract; NEITHER large suite ran here."
  echo "             CI runs both on push. PREFLIGHT_TESTS=1 for the manuscripts suite,"
  echo "             PREFLIGHT_MODALITIES=1 for the modalities suite,"
  echo "             PREFLIGHT_FULL=1 before publishing.)"
fi
exit "$rc"
