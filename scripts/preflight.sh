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

# A FULL run must not claim publication evidence while deliberately skipping a suite.
if [ "${PREFLIGHT_FULL:-0}" = "1" ] && [ "${SKIP_TESTS:-0}" = "1" ]; then
  echo "PREFLIGHT REFUSED: PREFLIGHT_FULL=1 and SKIP_TESTS=1 are incompatible." >&2
  exit 2
fi

# ⛔⛔ EVERY GATE BELOW RUNS AGAINST A PRIVATE, EMPTY BYTECODE CACHE — BECAUSE ON 2026-08-27 THIS
# SCRIPT REPORTED TWO FAILING TESTS THAT THE SOURCE ON DISK COULD NOT PRODUCE. `inspect.getsource`
# showed the fixed code; the interpreter executed the OLD bytecode. The mechanism, measured rather
# than guessed:
#
#   research/autonomy/__pycache__/continuity.cpython-311.pyc  written 23:28:57.634
#   research/autonomy/continuity.py                           written 23:28:57.840
#   the .pyc's header recorded source mtime 1787873337, size 21219 — EXACTLY the current source's
#
# CPython validates a cached .pyc by comparing (source mtime in SECONDS, source size). The edit
# landed 0.2 s after the .pyc was written, inside the same second, and happened to leave the file
# the same number of bytes — so both fields matched and the stale bytecode was reused. Clearing the
# caches took that suite from `2 failed, 211 passed` to `213 passed` with no source change.
#
# ⛔ THE DANGEROUS DIRECTION IS THE ONE WE DID NOT GET. A false RED costs an hour. A false GREEN is a
# guard that ran the version of itself that had not yet been broken — this whole script exists to
# stop a check that "reports while measuring nothing actionable", and stale bytecode is that failure
# with no symptom at all. It is also invisible to every gate below: each reads the SOURCE.
#
# ⭐ THE FIX IS ONE LINE AND IT IS THE READ SIDE, NOT THE WRITE SIDE. `PYTHONDONTWRITEBYTECODE=1`
# would only stop THIS run from writing; a cache some other process wrote a second ago would still
# be read. Pointing PYTHONPYCACHEPREFIX at a fresh directory means no .pyc in the tree is visible at
# all, so every gate compiles from the bytes it is about to judge. Modules imported by several gates
# still compile once, inside the run.
# ⚠ Cost, measured 2026-08-27 on `scripts/tests research/autonomy/tests` (213 tests), four runs:
# warm repo cache 32.5 s against 33.1 s and 33.1 s with NO cache reachable at all
# (PYTHONDONTWRITEBYTECODE=1, caches deleted) -- the strictly-worse form, since it recompiles on
# every import where the prefix directory at least caches within the run. **+0.6 s, about 2%.**
# Compilation is CPU, and CPU is free (CLAUDE.md §5).
# ⚠ THE RATIO IS THE FINDING HERE AND IT STANDS; THE ABSOLUTE SECONDS DO NOT. That suite was 213
# tests on 2026-08-27 and is ~800 now, so "32.5 s" no longer describes this gate -- re-read it as
# "+2 % of whatever the gate currently costs", and read the gate's own cost off the block beside the
# PREFLIGHT_TESTS tiering below, which was re-measured 2026-09-01. Recorded because a cost figure
# nothing re-measures is the exact rot AUT-PD-164 was filed about.
PREFLIGHT_PYCACHE="$(mktemp -d)"
export PYTHONPYCACHEPREFIX="$PREFLIGHT_PYCACHE"
trap 'rm -rf "$PREFLIGHT_PYCACHE"' EXIT

# ⛔ AUT-PD-026 — THE CALL BELOW IS RIGHT AND THE MECHANISM THIS COMMENT USED TO NAME WAS WRONG.
# ⚠ Superseded, retained (CLAUDE.md rule 1.2): "AUT-PD-026, 2026-08-27: A FRESH GIT WORKTREE NEVER
# GETS THE SessionStart HOOK, SO dev-setup.sh NEVER RUNS THERE, AND THIS SCRIPT SILENTLY FALLS BACK
# TO AN INCOMPLETE INTERPRETER ... the 2026-08-27 worktree-in/branch-out contract puts every seat in
# exactly the environment the hook cannot reach." That was the SECOND of three guesses on this entry
# and it is disproved: a worktree shares /usr/local/lib/python3.11/dist-packages and /root/.local
# with the main tree and has no venv, no PYTHONPATH and no per-tree pytest config, so there is
# nothing for it to miss. Measured 2026-08-28 in both trees at once: identical `python3`, identical
# `sys.path`, identical pymbar file.
#
# ⭐⭐ THE MEASURED MECHANISM (2026-08-28, CYC-0053): THE INTERPRETER THIS SCRIPT RUNS THE SUITES IN
# IS CHOSEN FROM MUTABLE GLOBAL STATE, AND dev-setup PROVISIONS ONLY THE INTERPRETER THAT STATE
# NAMED AT THE MOMENT dev-setup RAN. Nothing re-asks afterwards, and the answer moves.
#   * The image ships system python3 EMPTY. On a container booted 13:50:37 UTC that day, every
#     dist-info under /usr/local/lib/python3.11/dist-packages carried a post-boot timestamp and the
#     only pre-boot entry was uno.pth (2026-03-31). The baked uv `pytest` tool venv carried plain
#     pytest and nothing scientific (iniconfig/packaging/pluggy/pygments, all 2026-03-31).
#   * dev-setup's `_preflight_python` mirrors the `if python3 -c "import pytest"` branch below. While
#     system python3 has no pytest it answers "the tool venv", so dev-setup's step 3 — TEST_DEPS into
#     the RUN interpreter — is skipped as a correct no-op, and the scientific stack lands only in the
#     tool venv.
#   * ⭐ THE DISCRIMINATING OBSERVATION, same container: the SessionStart dev-setup ran 13:51:07–13:51:16
#     (SYSTEM_DEPS into python3, then `uv tool install --force` into the tool venv) and wrote NOTHING
#     scientific into system python3. That absence is proof its `run_py != tool_py` test was FALSE,
#     i.e. the run interpreter was the tool venv. pytest then entered system python3 at 14:10:58 and
#     pymbar at 14:11:42. For those 44 seconds the branch below resolved to an interpreter holding
#     pytest and no pymbar — the reported condition, in this container, with no worktree involved.
#   * The window is not bounded by that pip run. It lasts as long as system python3 holds pytest and
#     lacks the scientific stack, and several ordinary acts open it: this file's own advice above the
#     `$PYTEST` branch to `python3 -m pip install pytest`, any install that pulls pytest transitively
#     (pytest-xdist does), or one sibling seat installing one package.
#   * ⭐⭐ AND THE WHOLE MECHANISM IS PRESERVED, IN FULL, IN A LOG NOBODY HAD READ: GitHub Actions run
#     33104631542 (2026-08-27 18:41–19:12 UTC, sha 8b3fb54a2c7d5a5562b456103b0c57412ec71de0). That
#     day's `preflight-full-record.yml` ran `./scripts/dev-setup.sh --if-needed || pip install -q
#     pypdf pdfminer.six jsonschema pytest`. dev-setup announced the hole correctly — "the pytest
#     tool venv is missing: (pytest interpreter not found)", "the interpreter preflight RUNS THE
#     SUITES in — is missing: (no interpreter would run the suites)" — and then FAILED, because a
#     vanilla runner has no `uv`. ⛔ The `||` fallback then installed pytest into system python3 AND
#     NOTHING SCIENTIFIC, which is the flip, executed explicitly in one line of YAML. `PREFLIGHT_FULL=1`
#     then reported **53 failed, 7893 passed, 98 skipped**, named in full: 11 in
#     test_abfe_diagnostics.py (pymbar), the rest in test_nr4a3_5bt / test_step1_map_diag /
#     test_short_linker_probe (rdkit), test_slow_cv (numpy/scipy) and test_nrv04_retro_* (boto3).
#     ⭐ THAT RUNNER HAD NO WORKTREE — a detached-HEAD `git checkout` on ubuntu-latest — which is the
#     independent refutation the dev sandbox could not give, and it dates the same day as both seats.
#     ⚠ It also shows the failures are NOT pymbar-specific: pymbar is merely alphabetically first,
#     which is why every report of this defect has been filed under its name.
#   * ⭐ AND IT REPRODUCES ON DEMAND IN TWO SECONDS, WITH A CONTROL, WITHOUT BREAKING THE SANDBOX --
#     put a `pymbar/__init__.py` that raises ModuleNotFoundError on PYTHONPATH and run
#     `research/modalities/tests/test_abfe_diagnostics.py`. Measured 2026-08-28: **11 failed, 10
#     passed** shadowed against **21 passed** unshadowed, the 11 being the same 11 names CI run
#     33104631542 printed, and 11+10=21 being exactly what dev-setup.sh's own header records for
#     2026-08-24 ("11 failures ... installing it into python3 alone took the file to 21 passed").
#     The traceback is verbatim the one every report of this quotes:
#     `nr4a3_abfe.py:69: in _solve_mbar / from pymbar import MBAR / ModuleNotFoundError`.
#     ⛔ Do this rather than uninstalling anything: the interpreters are SHARED with every
#     concurrent seat, so a real uninstall breaks their runs and heals before you can read yours --
#     which is precisely why this defect went undiagnosed from 2026-08-24 to 2026-08-28, across
#     three environments, and attracted three wrong mechanisms in the meantime.
# ⚠ SO THE WORKTREE WAS A CONFOUND, NOT A CAUSE. What the worktree correlates with is WHO ran: seats
# run concurrently and install things, and until the call below existed the SessionStart hook was the
# only thing that re-ran dev-setup — at most once, at session start. Measured on that container:
# dev-setup at 13:51:07–13:51:16, no further write into either interpreter until 14:09:30, and the
# flip at 14:10:58. Twenty minutes in which the chosen interpreter could move and nothing re-asked.
# ⛔ UNKNOWN, and left unknown rather than guessed a fourth time: which process installed pytest into
# system python3 at 14:10:58. The mechanism does not rest on it — `_preflight_python` is a function of
# mutable global state, so ANY writer flips it. `_dep_hint()` below only prints
# after the damage is done — a seat has to notice the hint, read it correctly and act on it, which is
# the class CLAUDE.md §4 exists for ("an absent reading is not a reading of absence").
# ⭐ The call below is what actually closes it, for a reason the old comment did not state: it re-asks
# at the moment the answer is USED, which is the only moment that can be right. `--if-needed` is
# cheap and idempotent (an import check, exit 0 if already satisfied), and `set -euo pipefail`
# (line 49) makes a dev-setup that CANNOT repair the run interpreter abort this script rather than
# let it report a manufactured number.
# Legacy Linux bootstrap is not a Windows dependency installer. The actual gates below
# still run normally and fail for missing dependencies; only Linux package provisioning skips.
case "$(uname -s 2>/dev/null || echo unknown)" in
  MINGW*|MSYS*|CYGWIN*)
    echo "preflight: Windows shell detected; skipping Linux dev-setup. Provision gate dependencies separately."
    ;;
  *)
    if [ -x ./scripts/dev-setup.sh ]; then
      ./scripts/dev-setup.sh --if-needed
    fi
    ;;
esac

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
# ⛔⛔ THE DEFAULT LOOP IS 130.7 s, MEASURED 2026-09-02 FROM ONE TIMESTAMPED DEFAULT RUN OF THIS
# SCRIPT -- gate 13 is 57.1 s of it over 1 030 tests, i.e. 44 %. The numbers above are a snapshot of
# a smaller AND a slower gate; both halves of that moved.
#
#   whole default tier               130.7 s   2026-09-02, this sandbox, 4 cores
#   of which gate 13                  57.1 s   1 030 tests
#
# ⚠ Superseded, retained (CLAUDE.md rule 1.2), and it was CORRECT WHEN TAKEN -- it is the reading
# that named the hot spot the fix removed: "GATE 13 IS NOT HALF THE DEFAULT LOOP -- IT IS 85-94 % OF
# IT ... fast gates 81.3 s (of which the dev-setup/interpreter probe is 15.3 s BEFORE gate 1, and
# citation provenance is 44.4 s) + gate 13 446.3 s quiet box, 2026-08-29, 789 tests / 1 247.8 s under
# twelve-way sprint contention, 2026-09-01" (S6-COMMITLOOP; AUT-PD-164 / AUT-PD-172 / AUT-PD-183).
#
# ⚠ Superseded, retained (CLAUDE.md rule 1.2): "ten fast gates 31.4 s ... + gate 13, the selector
# contract 39.3 s ... the DEFAULT tier is 77.5 s"; "GATE 13 IS NOW HALF THE DEFAULT LOOP ... it is
# **39.3 s of the 77.5 s**, because each of its 55 tests builds the selector's import graph over ~400
# modules and shells out to git ... moving it under PREFLIGHT_TESTS would take the commit loop to
# ~31 s." (The last clause is now ~81 s.)
#
# ⭐ NOTHING REGRESSED -- THE GATE'S SCOPE AND POPULATION GREW, AND THAT WAS MEASURED RATHER THAN
# ASSUMED. On 2026-08-24 this line ran `scripts/tests` ALONE, five files; `research/autonomy/tests`
# was added on 2026-08-27 and went from 0 to 47 files in two days. The five 2026-08-24 files are
# byte-identical today and were re-timed on one machine: **79 tests in 74.4 s** against the recorded
# 55 tests in 39.3 s -- 0.94 s/test now against 0.72 s/test then, on a box carrying eleven other
# seats. Per-test cost did not move; the suite did.
# ⛔ AND THE "one slow file serializes it" HYPOTHESIS IS REFUTED, NOT UNRESOLVED. `tests.yml` already
# passes `--durations=25`; on run 33523366953 the 25 slowest tests of an 11,012-test suite include
# NONE from `scripts/tests` or `research/autonomy/tests`, and the 25th costs 24.09 s.
#
# ⭐⭐ AND MOST OF THIS GATE IS ONE COMMAND, COUNTED RATHER THAN GUESSED. With a counting shim in
# front of `git` on PATH, one run of this gate makes **50 270 git invocations, of which 48 230 --
# 96 % -- are `git show <sha>:research/autonomy/research-ledger.json`** over 371 distinct commits:
# **130 complete walks of the ledger's history in a single gate run**, from
# `research/autonomy/stuck_clock.py::ledger_versions()` (`git log --follow`, then one `git show` per
# commit, each 1.25 MB blob parsed as JSON) reached with its default `repo=REPO`. One walk timed
# directly is **7.5 s for 372 versions**, so that is ~975 CPU-seconds per gate run -- about 55 % of
# the quiet 446 s -- and roughly 60 GB of blob text.
# ⛔ THE CONSEQUENCE IS THE PART TO REMEMBER: **this gate's cost scales with COMMIT COUNT, not with
# test count.** Every ledger commit this loop makes adds one more blob to all 130 walks, of a file
# that is itself growing; the count moved 371 -> 372 inside the twenty minutes it took to measure it.
# So the gate gets slower with no test added, which is exactly the accretion AUT-PD-164 described.
# ⭐⭐ BOTH FIXES LANDED ON 2026-09-02 AND THE COUNT WAS RE-TAKEN WITH THE SAME SHIM. Memoised on
# `(repo, path, HEAD)` and batched into ONE `git cat-file --batch` per walk:
#
#   git calls in one gate-13 run          50 270 -> 3 783
#   of those, `show <sha>:...ledger.json` 48 230 -> 1 140
#   one walk, timed directly                6.71 s -> 2.76 s, output compared element by element
#   gate 13                              446.3 s -> 57.1 s, on 789 -> 1 030 tests
#
# Neither changes an assertion, which is why both are guarded rather than trusted:
# `research/autonomy/tests/test_the_ledger_history_is_read_in_one_git_process.py` asserts the walk
# still equals the per-commit one it replaced (unparseable versions included), that no `git show` is
# spawned per commit, that the batch reader stays in sync across a `missing` rev and frames bodies by
# BYTES, and that an unreadable batch falls back to the slow answer rather than to a SHORT history --
# a shorter history moves the horizon forward and makes stuck rows look younger than they are.
#
# It is left exactly where `main` put it -- reversing another session's deliberate placement inside a
# merge is not this change's business -- and moving it under PREFLIGHT_TESTS is still trimcrae's
# call, now worth ~57 s rather than ~365 s, which is a much weaker trade than it was.
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
  PYTEST_BRANCH="python3 -m pytest (sees the repository's dependencies)"
elif command -v pytest >/dev/null 2>&1; then
  PYTEST="pytest"
  PYTEST_BRANCH="the bare \`pytest\` console script — ⛔ A UV TOOL IN ITS OWN ISOLATED VENV"
else
  PYTEST="python3 -m pytest"
  PYTEST_BRANCH="python3 -m pytest, with NO importable pytest — the run will fail loudly"
fi

# ⛔⛔ SAY WHICH INTERPRETER THIS RUN CHOSE, IN THE FIRST TEN LINES, NOT THE THOUSANDTH.
# Measured 2026-08-27 (AUT-PD-026): two seats independently got `50 failed, 7901 passed` and
# `50 failed, 7933 passed` with `No module named 'pymbar'`, and the only signal that the
# environment was degraded was one `MISSING PACKAGE` line buried inside a gate, a thousand lines
# down. One seat nearly filed it as a live blocker on a whole tier; both faced the temptation to
# add 50 healthy guards to sandbox-failure-baseline.txt and both refused, which is the only reason
# it stayed a fixable defect.
# ⚠ THE SECOND BRANCH IS THE TRAP THIS FILE ALREADY DOCUMENTS at 2026-08-15: a uv tool runs in its
# OWN venv, so `import yaml` fails inside the tests while `python3 -c "import yaml"` succeeds in
# the shell one line earlier. That day it invented 36 failures. A gate that invents failures is as
# broken as one that hides them, and this line is what makes the difference visible before anyone
# spends an afternoon on ghosts.
# ⛔ NOT AN `== ... ==` HEADING, AND THAT IS NOT COSMETIC. `systems_check`'s
# `_preflight_gates()` enumerates gates by splitting on exactly that pattern, and four documents
# hard-code the resulting ordinals -- so writing this banner in the gate style silently made the
# script "run 16 gates" and turned [P1] red on its first execution. A diagnostic line is not a gate.
echo "-- interpreter --"
echo "   pytest: $PYTEST_BRANCH"
# ⚠ `import importlib.util`, NOT `import importlib`. The submodule is not imported by the parent,
# so the bare form raises AttributeError, the probe exits non-zero with EMPTY stdout, and the
# branch below reports "MISSING: unknown" on a perfectly healthy environment. That is exactly what
# this block was written to prevent, and it did it to itself on its first run.
# ⛔⛔ AND THE PROBE ASKS THE INTERPRETER THAT WILL RUN THE TESTS, NOT `python3`.
# ⚠ ONE-OF-A-PAIR (paper-hardening §8b.2), and the sibling sits ~20 lines BELOW: the xdist probe was
# moved onto `$PYTEST` on 2026-08-23 for precisely this trap, and this probe -- immediately above it,
# in the same file, written against the same incident -- was left hard-coding `python3`. When the
# branch above takes the console-script fallback, `$PYTEST` is the uv tool venv and `python3` is a
# DIFFERENT interpreter with a different site-packages, so the banner answered about an interpreter
# no test would import from. Measured 2026-08-28: pymbar resolves to
# /usr/local/lib/python3.11/dist-packages/pymbar/__init__.py under `python3` and to
# /root/.local/share/uv/tools/pytest/lib/python3.11/site-packages/pymbar/__init__.py under the tool
# venv -- two interpreters, two answers, and only one of them is about the run.
# ⭐ MEASURED FALSE-OK, not reasoned (2026-08-28): with `$PYTEST` a console script whose shebang named
# a venv holding none of the seven, the hard-coded form printed `OK  every probed package imports`
# while the resolved form printed all seven MISSING. Same box, same second. A green banner over a run
# that could not import one of them is worse than no banner -- it is the "reports while measuring
# nothing" defect in the line written to prevent it.
# ⛔ Asserted by scripts/tests/test_the_dep_probe_asks_the_interpreter_that_runs_the_tests.py, which
# gate 13 runs on every commit, because this is the third time in this file that a probe and the run
# it describes have drifted apart (pytest 2026-08-15, xdist 2026-08-23, this one).
_PYTEST_PYTHON="$(command -v python3)"
if [ "$PYTEST" = "pytest" ]; then
  # the console script's shebang names the interpreter whose site-packages the tests actually see
  _PYTEST_PYTHON="$(head -1 "$(command -v pytest)" | sed 's/^#!//' | awk '{print $1}')"
fi
if ! _dep_probe="$("$_PYTEST_PYTHON" -c "
import importlib.util, sys
missing = [m for m in ('pytest','numpy','scipy','pymbar','yaml','pdfminer','pypdf')
           if importlib.util.find_spec(m) is None]
print(' '.join(missing))
sys.exit(1 if missing else 0)
" 2>/dev/null)"; then
  echo "   ⛔ MISSING in $_PYTEST_PYTHON -- the interpreter this run's tests import from -- and this"
  echo "      run's failures are SUSPECT until traced: ${_dep_probe:-probe itself failed}"
  echo "      Run ./scripts/dev-setup.sh --if-needed BEFORE believing any failure below."
  echo "      ⛔ Do NOT add these to research/modalities/tests/sandbox-failure-baseline.txt —"
  echo "         that grants a permanent amnesty to guards that are healthy."
else
  echo "   OK   every probed package imports"
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
# ⛔⛔ AND THE PROBE MUST NOT BE A `grep -q` PIPE, BECAUSE `set -o pipefail` TURNS A SUCCESSFUL MATCH
# INTO A FAILURE ROUGHLY HALF THE TIME. ⚠ Superseded, retained (CLAUDE.md rule 1.2):
#     if [ "${PREFLIGHT_SERIAL:-0}" != "1" ] && $PYTEST --version --version 2>/dev/null | grep -q xdist
# ⭐ MEASURED 2026-08-28, and it was caught in the act: this script's own modalities stage was
# observed running `python3 -m pytest research/modalities/tests/ …` with NO `-n`, on a box where
# `python3 -m pytest --version --version` prints `pytest-xdist-3.8.0` twice and `nproc` is 4.
# 60 samples of the exact pipeline under `set -uo pipefail`: **34 of 60 answered NO XDIST, and in
# every one of the 34 it was PYTEST that exited non-zero — `PIPESTATUS=(1 0)`, grep matched every
# single time.** `grep -q` exits the instant it matches, pytest's stdout becomes EPIPE, Python exits
# 1, and `set -euo pipefail` (line 49) reports the pipeline as failed. So the branch answered "no
# xdist" on a machine that has xdist, non-deterministically, at a rate near a coin flip.
# ⛔ THE COST IS THIS FILE'S OWN MEASUREMENT: the modalities suite is 968.9 s serial against 336.9 s
# at `-n 4`. Roughly half of every scoped-or-full modalities run has silently been paying ~11 extra
# minutes since the probe was moved onto `$PYTEST` on 2026-08-23 to fix a DIFFERENT defect — which
# is the third repeat of this file's recurring shape: the answer was about the pipeline, not the run.
# ⭐ THE FIX IS TO NOT PIPE. Capture once, match with `case`; no second process, so nothing can be
# killed early and nothing can race. `|| true` keeps a genuinely broken `$PYTEST` from aborting the
# script here rather than at the gate that needs it, and the empty string then falls through to
# serial, which is the safe direction.
# ⛔ Asserted by scripts/tests/test_the_dep_probe_asks_the_interpreter_that_runs_the_tests.py.
# Keep the slow-test evidence in the durable preflight log, not only in a
# temporary pytest file. This is diagnostic output; all suite verdicts below
# still come from the complete pytest result.
_print_test_profile() {
  awk '/slowest .* durations/ {show=1; print; next} show && /^=/ {exit} show {print}' "$1"
}

PYTEST_PAR=""
_pytest_selftest="$($PYTEST --version --version 2>/dev/null || true)"
if [ "${PREFLIGHT_SERIAL:-0}" != "1" ]; then
  case "$_pytest_selftest" in
    *xdist*)
      _cores=$(nproc 2>/dev/null || echo 1)
      [ "$_cores" -gt 1 ] && PYTEST_PAR="-n $_cores --dist loadfile" || true
      ;;
  esac
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

# ⭐ AND THIS GATE GREW A SECOND AXIS ON 2026-08-27 (AUT-PROP-007), UNDER THE SAME ORDINAL AND THE
# SAME COMMAND. `lint_citations` now also runs `lint_citation_types.py`: provenance asks whether an
# identifier has an ORIGIN, and the type guard asks whether the paper behind it is the KIND of paper
# the sentence says it is. On 2026-08-26 a national-registry cohort and two single-patient case
# reports were cited as "the review literature" -- every identifier real, every one ANCHORED, this
# gate green throughout and correct to be, because origin was never the question. It survived two
# cycles. The discriminator is PubMed's `article_types`, cached offline in
# `research/manuscripts/citation-article-types.json` (attribution and DOI links travel with it).
# ⚠ ONE HEADING ON PURPOSE. Gate ordinals are DERIVED from these `== ... ==` lines by
# `systems_check.check_preflight_gate_list` and hard-coded in four documents besides, so a new
# heading renumbers every gate below it -- the churn this file's generated-artifacts note already
# warns about. Bolting the guard onto a gate that runs in the commit loop AND in CI wires it more
# strongly than a heading of its own would, and the rerun command below is unchanged because it is
# still the right one.
# ⛔ AND THE CITATION LINTER'S NAME IS WRITTEN ABOVE WITHOUT ITS FILE EXTENSION ON PURPOSE, WHICH
# LOOKS LIKE A TYPO AND IS NOT. `systems_check.check_preflight_gate_list` assigns a tool to the FIRST
# gate whose BODY contains that tool's exact filename, and a comment placed above an `echo` belongs
# to the PREVIOUS gate's body -- so naming the file in full in a comment here puts the citation gate
# at ordinal 5 and turns [P1] red against a gate list that is correct. Measured twice while writing
# this block: once in the note above, and once in the note explaining the note. Do not "fix" either.
echo "== citation provenance and publication type (every prose identifier traces to a fetch or to the ledger; every claim of TYPE agrees with PubMed) =="
if python3 research/manuscripts/lint_citations.py; then
  echo "   OK"
else
  echo "   FAILED -- rerun 'python3 research/manuscripts/lint_citations.py' to see which identifier"
  echo "            is unanchored, or which sentence calls a paper something PubMed says it is not"; rc=1
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
# ⭐ ROW ADDED 2026-08-27 (AUT-PROP-009 review), AND IT IS WHAT MAKES THE GUARD A GUARD. CYC-0025
# put a SERIES MISMATCH check inside `atr_hrd_sarcoma_series.py --check` -- it is correct, and
# verified on this reviewer's copy against the real bytes of 325258cb8, the commit that caused the
# incident. But NOTHING RAN IT: `--check` appears nowhere in this script, and the only workflow that
# calls it (`emc-expression-datasets.yml`, gse-series mode) does so as
# `... --check || echo "--check reported drift; non-blocking, but READ IT"`, which swallows the exit
# code by design. The invariant on the real committed artifact was therefore still enforced only by
# `test_the_declared_series_is_the_one_the_committed_artifact_holds` in the modalities suite --
# opt-in locally behind PREFLIGHT_MODALITIES=1, and in CI on push, i.e. AFTER the commit that ships
# the wrong artifact. This row is the one that fires before the mistake is shared, and it costs
# 0.4 s (measured).
# ⭐ THE SECOND ROW IS THE GENERAL HALF. A re-derive check and an artifact-vs-constant check are
# both scoped to ONE module; `single_slot_identity.py --check` walks a REGISTRY of fixed-path
# artifacts and binds each to the identity its producer declares, its caches were fetched for, the
# systems map records, and the manuscripts that declare it as their producer are writing about.
# ⚠ ITS FAILURE IS NOT STALENESS AND THE ROW'S GENERIC REMEDY BELOW IS WRONG FOR IT, exactly as it
# is for the archive manifest; the module prints its own remedy, which AUT-PD-016 is why a reader
# now sees.
# ⭐ THE INSTRUMENT-CENSUS ROW IS AUT-PD-031, AND IT IS THE SAME SHAPE AS THE SERIES-MISMATCH ROW
# ABOVE: a `--check` that already existed, that nothing in the commit loop ran. Measured 2026-08-27 --
# `line_citations.py --fix` repaired the roadmap's 18 drifted line citations, printed "18 rewritten",
# exited 0, and left `instrument-census.json`/`.md`, which embed those same citations verbatim, stale.
# It was found THREE COMMITS LATER by a `PREFLIGHT_MODALITIES=1` run, because the census guard lives in
# the modalities suite -- opt-in locally, and in CI only after the commit that ships the stale copy.
# Trunk was red for hours. This row is the one that fires BEFORE the mistake is shared, and it costs
# 0.032 s (measured 2026-08-28, this sandbox). The fixer now names its downstream copies too; that is
# the other half and it does not replace this one, because a hand edit to the roadmap never runs the
# fixer at all.
# ⭐ THE LAST TWO ROWS ARE THE LITERATURE-ROUTING PAIR, ADDED 2026-08-28, AND THE FIRST OF THEM IS
# THIS GATE'S OWN LESSON REPEATING ITSELF. `trigger_scan.py --check` had existed for weeks, was the
# only thing that could catch a reopening trigger pointing at a renamed route or watching with no
# queries at all -- and NOTHING RAN IT. Measured that morning: it exited 1 with 7 ERROR. Six were
# false (it resolved ids against the manuscript-scoped emc-systems-map.json rather than the
# architecture in systems/graph/, which carries 77 routes to that file's 40); the seventh was real
# and had been hiding behind them -- TRG-CONDENSATE-PARTNER-RESOLUTION was `scan_enabled` with no
# `search` block, so it rendered on every board as a watched row while searching for nothing.
# ⚠ A --check NOBODY RUNS DOES NOT DEGRADE GRACEFULLY: it accumulates false positives, and the
# false positives are what make the real finding unreadable when somebody finally looks.
# ⭐ THE SECOND ROW IS THE HALF THE REPOSITORY HAD NO MECHANISM FOR AT ALL. Two layers FIND
# literature and a third routes a hit into technologies.json for grading; none of them could ask
# whether a captured paper ever reached the artifact whose claim it bears on. PMID 42570981 -- the
# closest human prior art the junction-vaccine route has -- was captured, triaged and cited in two
# manuscripts while research/modalities/vaccine-construct.json, which proposes that exact design
# class, said nothing about it for four days under green gates.
# ⭐ THE THIRD ROW GUARDS THE LLM MATCHER'S COMMITTED OUTPUT (2026-08-28). news_match.py replaces
# the keyword judgement with a model's, which is better at the judgement and worse at being
# reproducible — rerunning it costs an API call and does not return the same answer. So the queue
# is a COMMITTED product, and what this row checks is the part a model cannot be right about by
# luck: that every publication id in it still resolves, that no verdict lacks a reason, and that
# the run recorded WHICH MODEL answered. An unattributed LLM verdict cannot be re-read later.
# ⚠ It passes when no queue is committed yet, because the first one arrives from CI.
# ⛔ NO ROW HERE CITES ANYTHING AUTOMATICALLY. Both verify a decision a human made; the ledger's
# `declined` status exists so that "we looked and it is not owed" stays distinguishable from
# "nobody looked". Measured cost of the pair: under 0.3 s.
# ⛔⛔ THE DEPOSIT-DRIFT ROW WAS ADDED 2026-09-02, AND IT IS HERE BECAUSE THE NUMBER IT GUARDS WENT
# STALE INSIDE ONE COMMIT. The preprint checklist's §3-vii declared "15 paths changed"; it was
# exactly right when written at 19f9d2b41 and wrong at 05c1cac1e -- a commit about THIS SCRIPT's own
# cost, which happened to touch three files that are also deposited (lint_citations.py,
# pinned-figures.json, a .docx build stamp). The real figure was 18. Round 31's citations-and-archive
# seat found it; no gate could have, because the number was typed.
# ★ THE COUNT IS A FUNCTION OF 515 DEPOSITED PATHS, so any commit anywhere in this repository can
# move it -- including one whose author has no idea the archive exists. That is precisely the class
# CLAUDE.md §1 puts under "a total is DERIVED, never typed", and precisely the class this gate
# exists for: "a file marked GENERATED was an instruction to humans backed by nothing".
# ⚠ IT MUST RUN AFTER THE ARCHIVE MANIFEST ROW, WHICH IS WHY IT SITS IMMEDIATELY BELOW IT: it reads
# that manifest's recorded digests, so a stale manifest makes it print a confident WRONG number
# rather than a stale one. Ordering inside this list is the only thing enforcing that.
# ⭐ THE CLAIM-COVERAGE ROW IS AUT-PD-130 AND IT IS THE MOST EXPENSIVE SINGLE ROW IN THIS GATE —
# 1.8 s, measured 2026-09-01 over three runs (1.79 / 1.83 / 1.91 s), against 4.80 s for the sixteen
# pre-existing rows put together (next largest: the archive manifest at 1.48 s). It is here anyway,
# because it is the only row that can catch an edit whose two halves live in different directories:
# `claim-coverage.json` harvests its guard patterns from `research/manuscripts/tests/`, so WIDENING
# A GUARD'S REGEX MOVES `covered` WITH NO MANUSCRIPT BYTE
# TOUCHED. That is not hypothetical — `83aede1` did exactly it, `covered` went 99 -> 101, and `main`
# was red on a clean tree for ~35 minutes, during which every sentence witnessed only by the red
# module scored a false BLIND in the ablation harness.
# ⚠ THE COMPARISON ITSELF IS NOT NEW; ITS PLACEMENT IS. It has existed since 2026-08-22 inside
# `test_claim_coverage_has_not_regressed`, in the manuscripts suite — opt-in locally behind
# PREFLIGHT_TESTS=1, and in CI only after the push that ships the stale artifact. Same shape as the
# series-mismatch and instrument-census rows above: a `--check` that already existed and that nothing
# in the commit loop ran. ⭐ It earned the 1.8 s within its first hour: on 2026-09-01 it caught the
# census going stale TWICE IN TEN MINUTES from concurrent manuscript edits, each time in 1.8 s.
# ⛔ THE FAN-OUT'S SCRATCH LIVES IN A PRIVATE TEMP DIRECTORY, NEVER IN THE TREE. Preflight is the
# gate that checks the tree is clean; a gate writing scratch files into it would be checking its own
# litter. Removed unconditionally after the reporting loop below.
_genout="$(mktemp -d)"
_geni=0
for g in "research/manuscripts/submission_tables.py|submission tables|--check" \
         "research/manuscripts/claim_coverage.py|claim coverage census|--check" \
         "research/manuscripts/submission_citations.py|submission references|--check" \
         "research/manuscripts/submission_metrics.py|submission metrics|--check" \
         "research/manuscripts/aso_sequence_manifest.py|canonical sequence file|--check" \
         "research/manuscripts/aso_journal_tables.py|journal article tables|--check" \
         "research/modalities/aso_offtarget_duplex_energy.py|offtarget duplex energy|--check" \
         "research/manuscripts/submission_packet.py|submission packet|--check" \
         "research/manuscripts/vaccine_path_tables.py|vaccine-path manuscript tables|--check" \
         "research/manuscripts/aso_archive_manifest.py|archive manifest|--check-archive" \
         "research/manuscripts/aso_deposit_drift.py|declared deposit drift|--check" \
         "research/modalities/emc_condensate_report.py|condensate CALVADOS findings|--check" \
         "research/modalities/atr_hrd_sarcoma_series.py|ATR HRD sarcoma series|--check" \
         "research/modalities/single_slot_identity.py|single-slot artifact identity|--check" \
         "research/modalities/instrument_census.py|instrument census|--check" \
         "scripts/trigger_scan.py|reopening-trigger registry join|--check" \
         "scripts/citation_debt.py|literature citation debt|--check" \
         "scripts/news_match.py|news-match queue|--check"; do
  gen="${g%%|*}"; rest="${g#*|}"; label="${rest%%|*}"; mode="${rest##*|}"
  # ⛔⛔ THE ROWS RUN CONCURRENTLY AND ARE READ BACK IN LIST ORDER (2026-09-02). Every row is an
  # independent read-only `--check` against the committed tree — none writes, none reads another's
  # output — and they were nonetheless started one at a time, so the gate cost the SUM of eighteen
  # interpreter starts: 9.2 s of a 131.8 s commit loop, 7 %, on four idle cores.
  # ⭐ THE OUTPUT IS UNCHANGED, WHICH IS THE POINT AND IS WHAT MAKES THIS SAFE TO DO. Each row's
  # exit code and captured text go to a per-row file named by its INDEX, and the reporting loop
  # below walks the list in order — so the log reads identically to the serial version, and the
  # archive-manifest row still reports after the rows it is documented to follow.
  # ⚠ AND THE ORDERING CONSTRAINT THE COMMENT ABOVE RECORDS IS A REPORTING one, not an execution
  # one: the deposit-drift row reads the manifest ARTIFACT ON DISK, which no row here writes —
  # every one of them is a `--check`, and a `--check` that wrote the tree would already be failing
  # `git_tree_is_clean_apart_from_this_manifest`.
  printf '%s\n' "$label" > "$_genout/$_geni.label"
  printf '%s\n' "$gen" > "$_genout/$_geni.gen"
  { python3 "$gen" "$mode" >"$_genout/$_geni.out" 2>&1; echo $? > "$_genout/$_geni.rc"; } &
  _geni=$((_geni + 1))
done
wait || true
_geni=0
while [ -f "$_genout/$_geni.label" ]; do
  label="$(cat "$_genout/$_geni.label")"
  gen="$(cat "$_genout/$_geni.gen")"
  gen_rc="$(cat "$_genout/$_geni.rc" 2>/dev/null || echo 1)"
  gen_out="$(cat "$_genout/$_geni.out" 2>/dev/null || true)"
  if [ "$gen_rc" = "0" ]; then
    echo "   OK   $label"
  else
    # ⛔ THE GENERATOR'S OWN FAILURE TEXT REACHES THE READER AS OF AUT-PD-016 (2026-08-27). The row
    # was once `python3 "$gen" "$mode" >/dev/null 2>&1`, so every producer's diagnosis was discarded
    # and the only remedy a reader ever saw was the generic "rerun and commit the result" below. For
    # the archive manifest that generic advice is ACTIVELY WRONG — it is what regenerates the
    # artifact against the same dirty tree and reproduces the defect — and the generator now says so
    # in a message nobody could read. Capturing instead of discarding is what makes a per-producer
    # remedy possible at all, and the fan-out above keeps every byte of it.
    echo "   STALE $label -- rerun 'python3 $gen' and commit the result"
    # ⚠ AND WHERE THE PRODUCER DISAGREES WITH THAT LINE, THE PRODUCER WINS: it knows which of
    # "stale" and "must not be regenerated here" its own exit code meant. Indented so the block
    # reads as the row's detail rather than as a new gate.
    if [ -n "$gen_out" ]; then
      echo "$gen_out" | sed 's/^/          /' || true
    fi
    gen_fail="$gen_fail $label"; rc=1
  fi
  _geni=$((_geni + 1))
done
rm -rf "$_genout"
[ -n "$gen_fail" ] && echo "   ⛔ a stale generated file ships a claim its own artifacts no longer support:$gen_fail"

# ⛔ THE CYCLE RECEIPT'S FAN-OUT FIELD, CHECKED AT THE MOMENT IT IS WRITTEN (AUT-PD-013, 2026-08-27).
# `health.py`'s `fanout_is_governed` guards `subagent_width` -- the dial the architecture records as
# having failed catastrophically (a 107-agent fan-out: 40 completed, 67 errored, the synthesis lost).
# It reads `subagents.max_concurrent`. Measured over all 22 receipts, the writers used THREE different
# schemas in seventeen of them -- `max_concurrent`, then `concurrent_max`, then `launched` -- so the
# row printed a FALSE ABSENCE for cycles whose fan-out was recorded plainly under another name.
# ⭐ THE PREVENTION HALF HAS TO BE HERE AND NOWHERE ELSE. There is no receipt writer: step 10 of
# `research-loop` says "write the receipt" and every cycle hand-authors the JSON, so the only moment
# anything can check the writer is the commit that lands it. A convention this loop had already got
# right twice, in prose, was lost twice anyway; a gate is what a name shared by two files needs.
# ⚠ IT COSTS NOTHING TO RUN (pure stdlib, one glob over ~22 small files) and it is scoped by a cycle
# NUMBER, not a hand-kept exemption list: receipts before CYC-0023 predate the schema and are
# immutable committed history, so failing them would latch this gate red forever -- the exact defect
# that wedged the autonomy loop the same morning. Their drift is REPORTED, never hidden.
echo "== cycle receipts record the fan-out width the cap is checked against =="
if receipt_out="$(python3 research/autonomy/receipt_schema.py --check 2>&1)"; then
  echo "$receipt_out" | sed 's/^/   /'
  echo "   OK"
else
  echo "$receipt_out" | sed 's/^/   /'
  echo "   FAILED -- a receipt does not record \`subagents.max_concurrent\`, so its fan-out is"
  echo "            invisible to health.py's governed-width row. Fix the receipt, not the checker."
  rc=1
fi

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
  if [ "${PREFLIGHT_FULL:-0}" = "1" ] && [ -n "${PREFLIGHT_PAPER:-}" ]; then
    # ⛔⛔ THE PUBLICATION TIER SCOPED TO THE PAPER BEING PUBLISHED, ADDED 2026-09-02. trimcrae:
    # "10 minutes is still too long for checking 6 pages." Measured on a green FULL run that day,
    # the modalities suite was 423.6 s of a 583 s gate — 72 % — and `affected_tests.select()` for a
    # change to the ASO journal article returns 0 of 429 modality test files. 39 of the 429 name an
    # artifact that paper actually deposits (727 tests); the other 390 are docking, ABFE, GPU-fleet,
    # vaccine and degrader suites, run in full to publish a six-page ASO paper.
    # ★ THE SCOPE IS THE PAPER'S OWN DEPOSIT MANIFEST, so adding a file to the deposit pulls its
    # guards in with nobody remembering to do anything. `paper_scoped_tests.py` carries the
    # derivation and the argument; it returns FULL for any paper it cannot scope.
    # ⛔ ONLY THE MODALITIES SUITE NARROWS. The manuscripts suite, the pure-logic suites and every
    # fast gate still run IN FULL under PREFLIGHT_FULL — a claim in the paper is bound by a
    # manuscripts guard and none of those is dropped. This narrows the one suite whose subject is
    # other routes' science.
    # ⚠ AND IT IS OPT-IN BY NAMING A PAPER. A bare `PREFLIGHT_FULL=1` is unchanged and still runs
    # all 429, so nothing already relying on the FULL tier's meaning is altered underneath it.
    SELECTED="$(python3 research/manuscripts/paper_scoped_tests.py --paper "$PREFLIGHT_PAPER" 2>/dev/null || echo FULL)"
    if [ "$SELECTED" = "FULL" ] || [ -z "$SELECTED" ]; then
      SELECTED=""
      echo "== pytest (modalities: FULL, PREFLIGHT_FULL=1 -- $PREFLIGHT_PAPER could not be scoped) =="
    else
      SEL_STATUS=scoped
      n=$(printf '%s\n' "$SELECTED" | grep -c . || true)
      _modtotal=$(ls research/modalities/tests/test_*.py 2>/dev/null | wc -l)
      # ⛔ THE HEADING NAMES WHAT ACTUALLY RUNS, AND IT WAS WRONG FOR ONE RUN: it said "the
      # manuscripts and pure-logic suites still run in full" after the pure-logic suites had been
      # taken out of this tier in the same edit. That is this file's own recurring defect — a line
      # that reports a check the run did not perform — in the sentence a reader trusts. Derived
      # from the flag now, so it cannot drift from it again.
      echo "== pytest (modalities: FULL, PREFLIGHT_FULL=1 -- scoped to $PREFLIGHT_PAPER's deposit: $n of $_modtotal module(s); the MANUSCRIPTS suite still runs in full, the pure-logic suites do NOT run in a paper tier) =="
    fi
  elif [ "${PREFLIGHT_FULL:-0}" = "1" ]; then
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
    $PYTEST $PYTEST_PAR $SELECTED -q --durations=25 --continue-on-collection-errors >"$out" 2>&1 || true
  elif [ "$SEL_STATUS" = "none" ]; then
    echo "no modality test is affected by this change" >"$out"
  else
    $PYTEST $PYTEST_PAR research/modalities/tests/ -q --durations=25 --continue-on-collection-errors \
        --ignore=research/modalities/tests/test_ternary_endpoint_align.py >"$out" 2>&1 || true
  fi
  failed=$(grep -cE '^FAILED' "$out" || true)
  errored=$(grep -cE '^ERROR ' "$out" || true)
  _print_test_profile "$out"
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
  $PYTEST $PYTEST_PAR research/manuscripts/tests -q --durations=25 --continue-on-collection-errors >"$mout" 2>&1 || true
  _print_test_profile "$mout"
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
#
# ⛔⛔ AND IT HAPPENED AGAIN, IN THE SAME WEEK, TO THE LOOP'S OWN INSTRUMENTS (2026-08-27, found
# while wiring the receipt gate above). `research/autonomy/tests` is run by NEITHER this script nor
# tests.yml -- CI's pytest step names `research/modalities/tests research/manuscripts/tests
# systems/tests scripts/tests` and stops there -- so 53 assertions were unrun by anything:
#   test_continuity_has_no_green_state_recording_can_buy.py  the third fix for "ended the turn with
#     ready work and nothing running", whose whole design is that recording work must never buy a pass
#   test_session_reaper_refuses_to_lose_work.py              pinned after the reaper's first run
#     against real data called three DELIVERED cycles "died holding uncommitted work"
#   test_receipt_schema.py                                   AUT-PD-013's own regression
# ⭐ ALL THREE WERE WRITTEN THE SAME DAY AS GUARDS AGAINST DEFECTS THAT HAD ALREADY HAPPENED, and
# every one of them was a guard nothing ran -- the identical shape as the selector's suite above and
# as `subagent_width` itself, which CLAUDE.md §1 records as governed by nothing for a fortnight.
# They are folded into THIS invocation rather than given a step of their own, deliberately: the
# comment below is about a fix bound to one call site regressing at its sibling, and a second copy of
# this twenty-line decision block is exactly that sibling. 53 tests, 0.09 s.
# ⛔⛔ `systems/tests` WAS WIRED IN ON 2026-09-01 (AUT-PD-191), AND THE REASON IS THE PUBLICATION
# BAR, NOT THE RED TRUNK. preflight's pytest gates were modalities, manuscripts, and this line;
# `systems/tests` appeared in NONE of them, while tests.yml runs all four and is the authority. So
# the local gate and CI disagreed by one whole directory — and that directory had been RED ON `main`
# since 2026-08-29.
# ★ WHAT THAT COST, STATED AS THE THING THAT MATTERS: `publish_bar` clause 2 is "PREFLIGHT_FULL=1
# green on the posted commit", and its receipt is minted by `record_bar_evidence.py preflight` from
# a preflight LOG. Because preflight omitted this directory, a local `PREFLIGHT_FULL=1` could exit 0
# and mint a green clause-2 receipt on a tree whose CI was red — the clause certifying "the whole
# suite passed" on the strength of a run that never executed the failing tests. A gate that quietly
# runs too little is not a faster gate.
# ⚠ IT WAS FILED ON 2026-08-30 AND DELIBERATELY NOT TAKEN THEN, with the right reason: wiring a red
# directory into the commit gate blocks every commit, which is how a gate gets switched off. The
# twelve failures went green first, and only then did this line change.
#
# ⭐⭐ IT RUNS BEHIND `PREFLIGHT_TESTS=1` / `PREFLIGHT_FULL=1`, NOT ON EVERY COMMIT, AND THAT IS THE
# WHOLE FIX RATHER THAN HALF OF IT. `PREFLIGHT_FULL=1` sets `RUN_TESTS`, and FULL is the only tier
# clause 2 ever reads — so the hole above is closed completely by this placement.
# ⚠ THE COST IS WHY IT IS NOT IN THE DEFAULT TIER, MEASURED 2026-09-01 RATHER THAN GUESSED:
# `pytest -n auto systems/tests` is **112 s** for 354 tests (serial it is far worse — 20% in ten
# minutes). The default commit loop is ~78 s, so putting this in it roughly TRIPLES the loop. This
# file's own history says that call is trimcrae's and is not one to make silently inside a merge —
# it is the same sentence that guards moving gate 13 the other way.
# ⛔ AND THE TRADE IS THE ONE ALREADY MADE FOR THE MANUSCRIPTS SUITE: a systems break is now caught
# by CI minutes later and costs one more commit, instead of being caught before the commit. Moving
# it into the default tier is one word — drop the `$SYSTEMS_TESTS` guard below — if he wants that
# instead.
SYSTEMS_TESTS=""
[ "${RUN_TESTS:-0}" = "1" ] && SYSTEMS_TESTS="systems/tests"
# ⛔⛔ OPT-IN AS OF 2026-09-02, ON trimcrae'S DECISION, AND THE MEASUREMENT THAT PUT IT TO HIM.
# He asked "1000 pure logic tests for a 6 page paper seems insane". Measured that day, the framing
# was generous — the real shape is worse:
#
#     gate 13, IN the commit loop      1,119 tests   39.0 s   the loop's OWN machinery
#     research/manuscripts/tests       1,854 tests   63.7 s   the PAPER — and NOT in the commit loop
#
# So every commit verified the loop's leases, receipts, cadence and handoffs — 936 of the 1,119 are
# `research/autonomy/tests` — and verified NOTHING about the manuscript, whose 1,854 guards have
# been opt-in behind PREFLIGHT_TESTS=1 since 2026-08-23. 2,973 tests exist for a 4,695-word paper.
# ★ HIS CHOICE, GIVEN ALL FOUR OPTIONS WITH THEIR COSTS: neither suite in the commit loop. That
# leaves the fast doc and artifact linters — consistency, the systems model, claim strength,
# citation provenance, the generated-artifact checks — at about 37 s, against 131.8 s this morning.
# ⛔ THE COST IS REAL AND IS NOT HIDDEN: a break in either suite is now caught by `tests.yml`
# minutes after the push instead of before it, and costs one more commit. That is the SAME trade
# already taken for the manuscripts suite (2026-08-23) and the modalities suite (2026-08-25), and
# `tests.yml` runs all four directories in full, on every push, with the real dependencies — it is
# the authority and this line never was.
# ⚠ WHAT THIS DOES NOT CHANGE: `PREFLIGHT_FULL=1` still runs everything, so the publication tier —
# the only thing `publish_bar` clause 2 accepts — is untouched. Nothing that reaches an outside
# reader has lost a check.
RUN_SELECTOR_TESTS=0
[ "${PREFLIGHT_TESTS:-0}" = "1" ] && RUN_SELECTOR_TESTS=1
[ "${PREFLIGHT_FULL:-0}" = "1" ] && RUN_SELECTOR_TESTS=1
# ⛔⛔ A PAPER'S PUBLICATION GATE DOES NOT ASK WHETHER THE LOOP'S LEDGER IS WELL-FORMED.
# `research/autonomy/tests` and `scripts/tests` are 1,498 tests about leases, receipts, cadence,
# handoffs, ledger ids and score arithmetic — 58 s of a 224 s paper gate, and NOT ONE of them is
# about the manuscript. ⚠ AND THEY ARE ALSO WHAT KEPT BLOCKING IT: across the eight committed
# PREFLIGHT_FULL logs, ledger bookkeeping failed the PUBLICATION gate in three, twice on
# 2026-09-02 alone, each costing a full re-run. The modalities suite, 72 % of those runs, failed
# in none.
# ★ THE ANSWER IS NOT TO DELETE THE CHECK — it fired three times, so it works, and the churn it
# was reporting is fixed at source in `ledger_io.write_ledger` (the totals are derived now, not
# asked for). It is that whether the LOOP's bookkeeping is tidy has nothing to do with whether a
# PAPER is fit to publish. It gates the COMMIT, which is where it belongs, and `tests.yml` runs it
# in full on every push.
# ⛔ ONLY WITH A PAPER NAMED. A bare `PREFLIGHT_FULL=1` still runs them, so the repository-wide
# publication tier is unchanged and nothing that relies on its meaning is narrowed underneath it.
[ -n "${PREFLIGHT_PAPER:-}" ] && RUN_SELECTOR_TESTS=0
if [ "$RUN_SELECTOR_TESTS" = "0" ]; then
  echo "== pytest (pure-logic suites) == SKIPPED -- PREFLIGHT_TESTS=1 runs them; tests.yml runs all"
  echo "   four directories in full on every push and is the authority (trimcrae, 2026-09-02)."
else
echo "== pytest (pure-logic suites nothing else runs: the selector's contract + the loop's instruments${SYSTEMS_TESTS:+ + the systems model}) =="
sout=$(mktemp)
$PYTEST $PYTEST_PAR scripts/tests research/autonomy/tests $SYSTEMS_TESTS -q --durations=25 --continue-on-collection-errors >"$sout" 2>&1 || true
_print_test_profile "$sout"
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
fi

# ⛔ THE THREE THINGS A PREPRINT SERVER NOW BANS SUBMITTERS OVER (AUT-PROP-032, 2026-08-28).
# A one-year submission ban is applied where there is "incontrovertible evidence" of unverified LLM
# output, and the named triggers are exactly what an unattended drafting loop produces: hallucinated
# references, residual model meta-comments, unremoved placeholder text. ⛔⛔ THE SANCTION ATTACHES TO
# THE AUTHOR'S NAME AND ORCID, not to this repository, and no later commit undoes it. That is why a
# cosmetic-looking string check sits in the commit loop.
# ⚠ THE POLICY IS SEARCH-GRADE HERE AND THE GATE SAYS SO RATHER THAN QUOTING IT. The trigger list
# reached us through a secondary news item (research/method-watch-autonomy-prior-art-2.md §5);
# arxiv.org is refused at this sandbox's egress proxy, so its wording, date and scope are UNKNOWN and
# the module records them as UNKNOWN. What is implemented is the CHECKLIST, not the policy text.
# ⛔ TRIGGER 1 IS GATE 6's AND IS NOT DUPLICATED HERE. `lint_citations.py` already asks whether an
# identifier traces to a fetch product; a second guard over the same corpus would be an overlapping
# wall rather than new coverage. What gate 6 does NOT reach — a reference carrying no identifier at
# all, arXiv ids, the author list and title printed beside an anchored id — is enumerated in the
# module's `UNCOVERED_BY_LINT_CITATIONS` instead of being closed with a weaker check.
# ★★ AND THE SCOPE IS THE DESIGN. Every string this gate looks for appears legitimately, and often,
# in the repository's own working prose — CLAUDE.md, AGENTS.md, the skills, the ledger and the plans
# discuss TODOs, placeholders and model behaviour correctly, and plan files are written as `- [ ]`
# checklists. Measured 2026-08-28, with the shipped rules and the frontmatter exemption both live:
# 132 of the 398 tracked `.md` files that are NOT submission documents match at least one rule, 314
# matches in all, every one honest. (⚠ Superseded, retained: "197 … 275 matches", measured against
# the PROTOTYPE rules before the empty-bracket lookahead was tightened and frontmatter exempted.)
# The linter re-derives this pair on every test run rather than trusting this line. So the gate reads ONLY the
# documents that go out (manuscripts, SIs, tables, references, cover letters), and derives that set
# from four committed artifacts — publications.json, lint_style.TARGETS, build_submission_pdf.PAPERS
# and submission-metrics.json — rather than from a hand-list that drifts.
# ⚠ APPENDED AT THE END ON PURPOSE, AND IT IS THE SAME REASONING THE GENERATED-ARTIFACTS GATE
# RECORDS: a new heading RENUMBERS every gate below it, and gates 13-15's ordinals are written into
# `research/autonomy/ids.py`, `research/autonomy/priority.py` and committed ledger rows that are
# immutable history. Appending moves nothing. This gate is fast (0.6 s measured over five runs) and
# has no ordering requirement, so the only cost of the position is that its message appears at the
# end of the log rather than the middle.
echo "== unverified-output residue in the documents that go out (model meta-comments, placeholders) =="
if residue_out="$(python3 research/manuscripts/lint_submission_residue.py 2>&1)"; then
  echo "$residue_out" | sed 's/^/   /'
  echo "   OK"
else
  echo "$residue_out" | sed 's/^/   /'
  echo "   FAILED -- an outgoing document carries a model meta-comment or an unremoved placeholder."
  echo "            Fix the DOCUMENT. Do not add a row to submission-residue-baseline.json to make"
  echo "            this pass: that file records slots a human decided may stand, and the count is"
  echo "            meant to fall."
  rc=1
fi

# ⛔ THE CYCLE CONTRACT AND THE RECEIPT GATE, CHECKED AGAINST EACH OTHER (AUT-PD-146, 2026-08-29).
# The receipt-schema gate above refuses a receipt missing `ccr_session_id`. ⛔ NAMED, NEVER
# NUMBERED, HERE AND IN THE HEADING BELOW: these headings are numbered BY POSITION, so an ordinal
# typed into a heading is wrong the moment a gate is inserted above it -- and that is this gate's
# own subject.
# The text a cycle actually follows when it
# hand-authors that receipt -- `.claude/skills/research-loop/SKILL.md` §2 step 10 -- did not name the
# field, so a cycle that followed the contract EXACTLY would write a receipt this script rejects
# and learn the requirement from a red build.
# ⚠ MEASURED, NOT ASSUMED: all seven receipts at or after CYC-0070 DO carry the field, so the gap
# has cost no build yet. What it cost is the guarantee -- CYC-0073-d4ccfde4 recorded that it wrote
# the field only because it had opened receipt_schema.py for an unrelated reason, which is
# compliance by luck, and luck is not a mechanism.
# ⭐ A SENTENCE IN THE CONTRACT WOULD HAVE BEEN THE FOURTH SUCH SENTENCE. This repository has lost
# the same writer/reader agreement four times (AUT-PD-013's fan-out key, AUT-PROP-013's ids,
# AUT-PD-037's serialization, this). The checker `contract_check` DERIVES the required set -- it deletes each
# field from receipts the enforcer accepts and re-runs it -- and reds the build when the contract
# does not name every field so derived. It fails closed on a contract it cannot read, and its
# fixtures stop complying the moment receipt_schema grows a requirement, so a new required field
# cannot reach a cycle before the contract does.
# ⛔⛔ APPENDED LAST SO NO ORDINAL MOVED, for the reason the residue gate's own note gives: these
# headings are numbered BY POSITION, and four of those ordinals are referenced by number in
# `research/autonomy/ids.py`, `research/autonomy/priority.py`, committed ledger rows and
# `repo-gates`. Placing this beside the receipt-schema gate, where it belongs by subject, would have
# silently renumbered them and falsified those references -- the same class of defect as the one
# this gate exists to catch. ⚠ It was written that way first, and `systems_check`'s [P1] caught the
# resulting count mismatch inside the same commit.
# ⛔ AND THE TOOL'S FILENAME IS DELIBERATELY NOT SPELLED IN THIS COMMENT, ONLY BELOW THE HEADING.
# `systems_check._preflight_gates` slices the script BY HEADING, so text above a heading belongs
# to the PREVIOUS gate's body -- and `check_preflight_gate_list` maps a tool to the first gate
# whose body contains its filename. ⚠ Measured 2026-08-29: spelling it here made [P1] report
# this gate as running at 16, inside the residue gate. Name the module without `.py` above the
# heading; the real invocation below is what the checker must see.
# ⚠ Pure stdlib, one file read plus a few dozen in-memory schema evaluations; unmeasurable cost.
echo "== the cycle contract names every receipt field the receipt-schema gate requires =="
if contract_out="$(python3 research/autonomy/contract_check.py --check 2>&1)"; then
  echo "$contract_out" | sed 's/^/   /'
  echo "   OK"
else
  echo "$contract_out" | sed 's/^/   /'
  echo "   FAILED -- receipt_schema.py refuses a receipt for a field the cycle contract never names,"
  echo "            so a cycle that follows the contract exactly cannot commit. Fix the CONTRACT"
  echo "            (.claude/skills/research-loop/SKILL.md §2 step 10) -- never the requirement."
  rc=1
fi

# ⛔⛔ WHAT EACH TIER COSTS IS A NUMBER SOMEBODY DECIDED, CHECKED AT THE COMMIT THAT CHANGES IT.
# The gate this row sits in reached 9.7 minutes for a 4,695-word paper purely by accretion: gate 13
# went 789 -> 1,030 -> 1,119 tests in ten days, the modalities suite reached 8,212 and had failed in
# none of the eight committed publication runs, and the repository held 2,973 tests for six pages.
# Every one of those tests was justified by a real incident, and that is precisely why the TOTAL was
# never anybody's decision — it took a human reading the number and saying so.
# ★ THE ROW COSTS ~0.1 s: an AST walk, no pytest, no collection. A budget guard that made the loop
# slower would be self-refuting, and `--collect-only` over the modalities suite is ~20 s.
# ⛔ IT CAPS WHAT THE REPOSITORY ASKS FOR, NOT SECONDS. Wall time varies with the box and with
# contention; a gate that reddened under load is one people learn to re-run, which is worse than no
# gate at all. `scripts/tier-budgets.json` carries each ceiling with the measurement behind it.
echo "== what each test tier costs, against the budget somebody set for it =="
if python3 scripts/tier_budget.py --check; then
  :
else
  echo "   ⛔ a tier is over its budget -- see scripts/tier-budgets.json for how to answer that,"
  echo "      and note that raising the ceiling is the LAST of the three options it lists."
  rc=1
fi

# ⛔⛔ AN `AUT-NNN` NAMES ONE ROUTE FOREVER, AND UNTIL 2026-09-03 IT NAMED WHICHEVER ROUTE LANDED IN
# ITS SLOT (AUT-PD-215). `priority.build_entries()` minted a derived row's id as `AUT-{index+1}` over
# routes sorted by id, so the id was a POSITION. Reproduced against the live graph before anything
# changed: adding ONE route whose id sorts early moved 76 of 77 ids and took AUT-073 -- the
# escalation trimcrae answered on 2026-09-01 -- from RT-TRIAL-REACH to RT-TRABECTEDIN-PPARG.
# ⛔⛔ APPENDED LAST, AND THAT IS NOT COSMETIC — IT IS THIS DEFECT'S OWN LESSON APPLIED TO A
# SECOND RECORD. Drafted at position 13 (beside the other autonomy-record gates, where it reads
# best), it pushed the modalities, manuscripts and pure-logic test gates from 13/14/15 to
# 14/15/16 -- and those three ordinals are written into `research/autonomy/ids.py`,
# `research/autonomy/priority.py`, four prose documents and committed ledger rows. That is a
# positional id silently coming to mean something else, which is the exact defect this gate
# exists to stop, one register over. `systems_check`'s P1 rule caught it in the same run.
# ⭐ THE GATE IS HERE RATHER THAN IN A TEST FOR ONE MEASURED REASON: the commit-loop test tier is
# OPT-IN (`PREFLIGHT_TESTS=1`) and this fires on the commit that ADDS A ROUTE, which is the only
# moment the binding can go wrong. A guard that runs on a flag nobody set on the commit that breaks
# it is a guard that reports the damage afterwards. It costs nothing (pure stdlib, three small JSON
# reads) and it fails closed: an unbound route, a duplicated id, or a ledger row disagreeing with
# the frozen map all red the commit and name `derived_ids.py --extend` as the remedy.
# ⚠ A BINDING WHOSE ROUTE HAS LEFT THE GRAPH IS REPORTED, NOT FAILED -- receipts still name that id,
# so deleting the binding loses the meaning by the other door.
echo "== every route's derived ledger id is frozen, not counted =="
if derived_out="$(python3 research/autonomy/derived_ids.py --check 2>&1)"; then
  echo "$derived_out" | sed 's/^/   /'
  echo "   OK"
else
  echo "$derived_out" | sed 's/^/   /'
  echo "   FAILED -- a derived AUT-NNN does not name the route the record was written against."
  echo "            Run 'python3 research/autonomy/derived_ids.py --extend' for an unbound route;"
  echo "            do NOT hand-edit a binding that already exists."
  rc=1
fi

# The run reached its own verdict, so an exit from here on is the verdict rather than an abort.
_preflight_summary_reached=1

# ⛔⛔ THE LINE `record_bar_evidence.py preflight` REQUIRES, AND WHICH THIS SCRIPT HAS NEVER PRINTED.
# Measured 2026-09-02 on a GREEN PREFLIGHT_FULL run: the recorder refused with "carries no
# PINNED_SHA= line, so the tree it ran against is unknown". `PINNED_SHA=` appears nowhere in this
# file, so clause 2 of the publish bar was UNREACHABLE BY CONSTRUCTION — every green publication run
# there has ever been would have been refused, and the only reason nobody hit it is that the run has
# to be green first, which is rare. Same producer/consumer shape as the receipt field names
# (AUT-PD-013) and `subagent_width`: a name agreed between two files, checked by neither.
# ★ IT NAMES THE COMMIT AND THE TREE'S CLEANLINESS SEPARATELY, because a sha alone would let a run
# over a dirty tree be recorded against the commit it merely started from — the "a green run against
# a different tree says nothing about the one being posted" failure, one level down. A dirty tree
# prints the sha with a `+dirty` suffix, which no `ran_against != sha` comparison can accept.
_pinned_sha="$(git rev-parse HEAD 2>/dev/null || echo UNKNOWN)"
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  _pinned_sha="$_pinned_sha+dirty"
fi
echo "PINNED_SHA=$_pinned_sha"

# ⛔ A GREEN LINE MUST SAY WHAT IT MEASURED. "PREFLIGHT OK" after a run that executed no test reads
# as "the suite passes", which is the exact "reports while measuring nothing" defect this file's
# header was written against -- and it would be a NEW instance of it, created by the change that
# made tests opt-in. So the tier is printed in the verdict, every time.
if [ "$rc" -ne 0 ]; then
  echo; echo "PREFLIGHT FAILED -- do not commit."
elif [ "${PREFLIGHT_FULL:-0}" = "1" ] && [ -n "${PREFLIGHT_PAPER:-}" ]; then
  # This tier omits governance and may narrow modalities. It must neither print the unscoped
  # success banner nor certify the selector hashes, even if every check it actually ran passed.
  echo; echo "PREFLIGHT OK (PAPER=$PREFLIGHT_PAPER: fast gates + manuscripts + modalities; see headings for scope)"
  echo "             Governance suites did NOT run; no unscoped FULL evidence or selector stamp was produced."
elif [ "${PREFLIGHT_FULL:-0}" = "1" ]; then
  # ⛔⛔ A GREEN FULL RUN RE-STAMPS THE SELECTOR RECORD, BECAUSE THE CHORE WAS A TREADMILL.
  # `affected_tests._unvalidated_gatekeepers` compares `preflight.sh` and `affected_tests.py`
  # against `scripts/selector-validation.json`, and only a FULL run may re-stamp it. So editing
  # this file made `test_the_committed_record_matches_the_committed_gatekeepers` red; clearing that
  # needed a green FULL run; and the run was red BECAUSE of that test. Measured three times on
  # 2026-09-02 alone, each costing a full re-run — 9.7 min, and historically 11:46 to 51:28.
  # ★ THE STAMP IS A DERIVED VALUE AND IS NOW DERIVED. A green FULL run is EXACTLY the evidence the
  # record exists to carry, so recording it at that moment is the one place the fact is known; a
  # human being asked to run a second command afterwards is how it went stale for a fortnight
  # (CLAUDE.md §6 carried "both hashes are stale" as an open diagnosis since 2026-08-25).
  # ⛔ IT RUNS AFTER EVERY GATE HAS FINISHED AND ONLY WHEN rc IS 0, so nothing downstream reads a
  # tree this touched, and a RED run still cannot stamp itself green. The write is reported, never
  # silent — a gate that edits the tree must say so or it is the thing it exists to catch.
  if [ -x scripts/record_selector_validation.py ] || [ -f scripts/record_selector_validation.py ]; then
    if python3 scripts/record_selector_validation.py >/dev/null 2>&1; then
      if [ -n "$(git status --porcelain -- scripts/selector-validation.json 2>/dev/null)" ]; then
        echo "   ⭐ selector-validation.json RE-STAMPED by this green FULL run -- commit it with your change."
      fi
    else
      echo "   ⚠ could not re-stamp scripts/selector-validation.json; run"
      echo "     python3 scripts/record_selector_validation.py by hand and commit it."
    fi
  fi
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
  # ⛔⛔ THE VERDICT NAMES WHAT ACTUALLY RAN, AND AS OF 2026-09-02 THAT IS FEWER THINGS. This line
  # read "fast gates + the selector's contract + the loop's instruments" for one commit after gate
  # 13 became opt-in — a green banner claiming a check the run had just skipped, which is this
  # file's own recurring defect ("reports while measuring nothing") in the sentence a reader trusts
  # most. It is DERIVED from the flags now rather than typed, so it cannot drift from them again.
  _ran="fast gates only (doc + artifact linters)"
  [ "$RUN_SELECTOR_TESTS" = "1" ] && _ran="$_ran + the selector's contract + the loop's instruments"
  [ "$RUN_TESTS" = "1" ] && _ran="$_ran + the manuscripts suite"
  [ "${PREFLIGHT_MODALITIES:-0}" = "1" ] || [ "${PREFLIGHT_FULL:-0}" = "1" ] && \
    _ran="$_ran + the modalities suite"
  echo; echo "PREFLIGHT OK ($_ran)"
  echo "             ⛔ NO TEST SUITE THIS RUN DID NOT NAME ABOVE HAS PASSED. tests.yml runs all"
  echo "             four directories in full on every push, with the real dependencies, and is"
  echo "             the authority for anything not listed."
  echo "             PREFLIGHT_TESTS=1 adds the manuscripts suite and the pure-logic ones,"
  echo "             PREFLIGHT_MODALITIES=1 the modalities suite,"
  echo "             PREFLIGHT_FULL=1 everything — the only tier publish_bar clause 2 accepts."
fi
exit "$rc"
