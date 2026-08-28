#!/usr/bin/env bash
# Install the packages this repository's gates need, into the two interpreters that actually run them.
#
# ⛔⛔ WHY THIS EXISTS: `main` WAS RED IN A FRESH SANDBOX, ON A CLEAN TREE, WITH NOTHING WRONG WITH IT
# (measured 2026-08-23, at 6efa7fb == origin/main, no working-tree changes). `./scripts/preflight.sh`
# failed two gates and named twenty-nine tests:
#
#   gate 2  systems model            ModuleNotFoundError: jsonschema
#   gate 12 manuscripts (878 tests)  9 failed + 20 errors, every one a PDF guard wanting
#                                    pdfminer.six / pypdf
#
# Neither was a defect in the repository. `tests.yml` was green on `main` across its last eight runs,
# and installing the packages below — with NO change to any tracked file — took gate 2 to `0 ERROR`
# and gate 12 to `878 passed`. The failures were the environment, reported in the costume of a
# content failure, which is the most expensive kind of red: it sends the next session hunting a bug
# in the manuscripts.
#
# ⚠ THE REPOSITORY ALREADY KNEW AND ROUTED AROUND IT. `preflight.sh` and `affected_tests.py` both
# carry the gap as a fact of life — *"this sandbox lacks numpy, rdkit, boto3, scipy, pymbar and
# netCDF4"* — and `.claude/skills/repo-gates/SKILL.md` records the fix in prose, in a section headed
# "THE SANDBOX DEP GAP IS FIXABLE, AND UNTIL 2026-08-23 NOBODY HAD FIXED IT". Prose in a skill file
# is not a fix: it runs only if a session happens to load that skill and happens to act on it. This
# is the same sentence as a command a hook can run.
#
# ⛔ THE TRAP, AND IT COSTS AN HOUR IF YOU MISS IT: `pytest` IS A `uv` TOOL IN ITS OWN VENV.
# Installing into the system interpreter changes nothing the tests can see — `python3 -c "import
# pdfminer"` succeeds while the identical import inside a test still raises ModuleNotFoundError.
# That is why this installs TWICE, deliberately, rather than once and hoping.
#
# ⚠ AND DO NOT PRUNE `research/modalities/tests/sandbox-failure-baseline.txt` ON THE STRENGTH OF A
# GREEN RUN AFTER THIS. Those entries describe a FRESH sandbox, which is what the next session gets
# before this script has run. The baseline is a statement about the default environment, not yours.
#
# Idempotent; safe to run repeatedly.
#   ./scripts/dev-setup.sh              install (or reinstall) into both interpreters
#   ./scripts/dev-setup.sh --if-needed  exit 0 immediately if both already import everything
#
# ⚠ `--if-needed` IS WHAT A SESSION HOOK RUNS, AND ITS CHECK IS AN IMPORT, NOT A MARKER FILE. A
# stamp saying "setup ran" is a claim about the past; the interpreters are what the gates actually
# consult, so it asks them. CLAUDE.md §4: a populated field is not a measured one.
set -euo pipefail
cd "$(dirname "$0")/.."

# ⛔ TWO INTERPRETERS, TWO LISTS, AND THEY ARE GENUINELY DIFFERENT — MEASURED, NOT TIDIED.
# The first cut installed one list into both and then reported `pypdf` and `pdfplumber` as still
# missing from system python3 after a successful install. The cause is not pip: this image's
# system interpreter carries a distro `cryptography` (41.0.7, /usr/lib/python3/dist-packages) that
# raises `pyo3_runtime.PanicException` on import, and `pypdf` imports it.
#
# ⭐⭐ THE PANIC'S ROOT CAUSE WAS FOUND ON 2026-08-24 AND IT IS NOT THE DISTRO PACKAGE.
# `RUST_BACKTRACE=1 python3 -c "from cryptography.hazmat.bindings._rust import exceptions"` prints
# ONE line above the panic: `ModuleNotFoundError: No module named '_cffi_backend'`. The pyo3 binding
# raises inside a Python call it cannot propagate, so the real error is swallowed and the caller
# sees only `Python API call failed` — which reads like a broken build and is a missing dependency.
# `pip3 install cffi` fixed it, with no distro package touched, and `pypdf` then imported in the
# system interpreter. ⚠ Superseded, retained: the claim that the distro `cryptography` is unusable
# in this interpreter and must be worked around rather than satisfied.
#
# ⛔ AND THE GAP THAT COST THE TIME IS THE PROBE'S, NOT THE PANIC'S. `--if-needed` reported
# "every interpreter the gates use already imports what they need" while
# `build_submission_pdf.py` — which runs in the SYSTEM interpreter and imports pypdf at
# `_postprocess` — could not build a PDF at all. The old comment below said "nothing under
# preflight.sh needs pypdf in that interpreter", which was true of preflight and false of the
# chain script every ASO manuscript edit runs. A probe that omits what the build path imports
# answers a narrower question than the one being asked of it.
#
# SYSTEM: `systems_check.py` needs jsonschema and refuses to run without it (deliberately — it has
# no fallback, because a hand-rolled subset validator silently ignores every keyword it does not
# implement). The other fast gates are pure stdlib plus node.
# ⛔ `pypdf`, `cffi` AND `biopython` ARE HERE BECAUSE `regenerate_aso_chain.sh` RUNS IN THIS
# INTERPRETER (2026-08-24). The list was derived by reading every `python3 …` step the chain
# script runs and grepping those files for a third-party import, rather than by adding modules one
# red run at a time: `build_submission_pdf.py` imports `pypdf`, `junction_aso_thermo.py` imports
# `Bio`. ⚠ `junction_aso_thermo.py` REFUSES rather than falling back when Biopython is absent
# ("a hand-entered table would be indistinguishable from this one"), which is the correct
# behaviour and also means the sandbox gap surfaces as a chain failure, not as a wrong number.
# `cffi` is not imported by name anywhere in this repository — it is what `cryptography`'s rust
# binding needs, and without it `import pypdf` panics. Pinning it by name is how a dependency that
# is only ever reached transitively gets probed at all.
SYSTEM_DEPS=(jsonschema pyyaml pypdf cffi biopython)
# PYTEST: the scientific and PDF stack every test import resolves against.
# ⛔ `pytest-xdist` IS ON THIS LIST FOR A MEASURED REASON, NOT FOR TIDINESS. `preflight.sh` runs the
# suites at `-n <cores> --dist loadfile` when xdist is importable and SERIAL when it is not — and it
# was importable in neither interpreter, so the 2.9x it documents had never once applied here. The
# run that found this took **1090.4 s** for the modalities suite against the 336.9 s that file
# records at `-n 4`.
TEST_DEPS=(pdfminer.six pypdf pdfplumber jsonschema numpy scipy rdkit boto3 netCDF4 pymbar pyyaml
           biopython matplotlib pytest-xdist)

# ⛔ THE PROBE RUNS IN BOTH INTERPRETERS, BECAUSE A GAP IN EITHER ONE IS THE BUG. Probing only the
# system python3 is exactly the mistake that makes the uv-tool trap cost an hour: it answers yes
# while every test still fails on the same import. The tool venv is found by asking `pytest` itself
# where it lives, never by hard-coding a path under ~/.local.
SYSTEM_PROBE="jsonschema yaml pypdf Bio"
TEST_PROBE="pdfminer pypdf pdfplumber jsonschema numpy scipy rdkit boto3 netCDF4 pymbar yaml Bio matplotlib xdist"

_pytest_python() {
  command -v pytest >/dev/null 2>&1 || return 1
  # `pytest` is a console script; its shebang names the interpreter whose site-packages the tests see
  head -1 "$(command -v pytest)" | sed 's/^#!//' | awk '{print $1}'
}

# ⛔⛔ THE INTERPRETER THAT ACTUALLY RUNS THE SUITES IS CHOSEN BY `preflight.sh`, NOT BY THIS SCRIPT,
# AND FOR MONTHS THEY DISAGREED. `preflight.sh` takes `python3 -m pytest` whenever `python3 -c
# "import pytest"` succeeds and only falls back to the bare `pytest` console script when it does not.
# So when pytest is importable in BOTH interpreters — the normal state here — the tests run in the
# SYSTEM one, while every scientific dependency this script installs goes to the uv tool venv, whose
# comment two blocks below asserts the opposite.
#
# ⚠ AND THE `--if-needed` PROBE INHERITED THE SAME BLIND SPOT, WHICH IS WHY THE SessionStart HOOK
# NEVER HEALED IT. It probed `_pytest_python` — the tool venv — found everything importable, and
# reported nothing to do, while `python3` lacked `pymbar`. Measured 2026-08-24: a publication-gate
# `PREFLIGHT_FULL=1` run went red with 11 failures in `test_abfe_diagnostics.py`, all
# `ModuleNotFoundError: No module named 'pymbar'` at `nr4a3_abfe.py:69`; the tool venv had pymbar
# 4.0.3 the whole time. Installing it into `python3` alone took the file to 21 passed. The failures
# had nothing to do with the change under test, which is the expensive part: an unnecessary red on a
# publication gate costs an afternoon of chasing somebody else's lane (CLAUDE.md §6).
#
# So this mirrors preflight's selection rather than guessing at it. Keep the two in step: if that
# `if python3 -c "import pytest"` branch ever changes, this function changes with it.
_preflight_python() {
  if python3 -c "import pytest" >/dev/null 2>&1; then
    command -v python3
  else
    _pytest_python
  fi
}

_missing_in() {   # $1 = interpreter, $2 = module list; echoes what it cannot import
  local py="$1" out=""
  for m in $2; do
    "$py" -c "import $m" >/dev/null 2>&1 || out="$out $m"
  done
  printf '%s' "$out"
}

# --------------------------------------------------------------------------------------------
# ⛔⛔ THE GIT HISTORY IS A DEPENDENCY OF THE GATES TOO, AND A SHALLOW CLONE BREAKS ONE SILENTLY.
#
# Every sandbox is handed a SHALLOW clone, and `research/autonomy/stuck_clock.py` derives both of
# its per-row clocks by walking `git log --follow` over every committed version of the ledger. What
# git cannot see, the clock cannot measure: a row already present in the oldest visible version is
# stamped `stuck_at = horizon` and marked `censored`, a right-censored LOWER BOUND. That is the
# honest behaviour and it stays — but a bound below the clock's own threshold decides nothing, so
# the instrument reports "no row is stalled" while measuring only the clone depth.
#
# ⚠ AND stuck_clock IS ONE OF THREE. `learning_rate.py` refuses to grade a window the horizon
# falls inside, and `out_of_ideas.py` returns `unmeasurable` for a route with no improvement in
# the visible history — both correct, both useless while the horizon is hours deep. Their windows
# are 16 h and 336 h against stuck_clock's 24 h, so the fetch below is sized off the LARGEST,
# not off the one that happened to be diagnosed first.
#
# ⛔ AND IT IS NOT COSMETIC — IT CHANGES WHAT A FRESH SESSION IS HANDED. `handoff.py::terminal_ids()`
# calls `stuck_clock.terminal_rows()` LIVE and fails OPEN, so a censored verdict silently excludes
# nothing. Measured 2026-08-28 in this sandbox, same ledger, three clones side by side:
#
#   session's shallow clone   horizon 3.2 h   142/161 rows censored   0 terminal
#   after the fetch below     horizon 53.4 h    47/160 rows censored   3 terminal
#   a full clone (what CI has) horizon 53.4 h    0/161 rows censored   3 terminal
#
# The three are AUT-010, AUT-049 and AUT-PROP-019, and the shallow run handed AUT-010 — the
# top-scoring row at 190.9 — to the successor as ready work, while the full clone printed
# "⛔ EXCLUDED as `stalled_needs_human`" for exactly those three. CI is unaffected: `autonomy-tick.yml`
# checks out at `fetch-depth: 0`, and its 18:45 UTC run that day named AUT-052 and AUT-049 on the
# board with `0 UNMEASURED`. So the censoring is a SESSION-path defect only, and this is the session
# path's setup script.
#
# ⭐ WHY `--shallow-since` AND NOT `git fetch --unshallow`, WHICH IS WHAT stuck_clock USED TO PRINT.
# The clocks need history that outruns their own longest window, not all of it. Measured the same day, from
# a fresh `--depth 1` clone: `--unshallow` is 1.5 GB and 80 s; the fetch below is +16 MB (107.5 ->
# 124.0 MB, 716 commits) and it produced the IDENTICAL terminal set to that full clone. Wall time
# across five runs was 5-37 s, the spread being contention with sibling seats rather than the fetch;
# a repeat that finds nothing new was 3-9 s. It does not need a checkout: the graft point moves, so
# `git log` from the existing HEAD walks straight through.
#
# ⚠ WHY IT SITS ABOVE THE `--if-needed` EARLY EXIT, AND THIS FILE HAS ALREADY PAID FOR THE LESSON
# ONCE: the ghostscript step was first written BELOW it, so on a sandbox whose interpreters were
# already complete `--if-needed` printed "nothing to do" and never reached it. A dependency the probe
# does not ask about must not sit behind the probe's answer. This step carries its own guard instead.
#
# ⚠ WHAT THIS DOES NOT DO, stated here rather than discovered later:
#   * it never fails the script or the SessionStart hook. A refused fetch (no network, another seat
#     holding `shallow.lock`, a fork without the branch) leaves the clock reporting censored bounds,
#     which is what we would actually know — an absent reading, not a reading of absence.
#   * it does not make the clone non-shallow. `is_shallow()` stays true and every row at the horizon
#     stays flagged `censored`; the horizon simply outruns the readers' windows, which is the
#     condition stuck_clock itself names as the one that makes a bound conclusive.
#   * ⚠ IT CANNOT SATISFY out_of_ideas YET, AND SAYS SO RATHER THAN LOOKING LIKE IT DID. The ledger
#     was created 2026-08-26, so its ENTIRE history is ~53 h against that module's 336 h budget:
#     until the ledger is 14 days old this fetches every session (3-9 s, silent) and out_of_ideas
#     keeps returning `unmeasurable`, which is the honest reading. The guard cannot tell "nothing
#     older exists" from "not fetched yet", and a stamp claiming the past instead of asking git is
#     the alternative this repository has already refused.
#   * two workflows also run this script — `preflight-full-record.yml` and `aso-submission-parts.yml`,
#     both at the checkout default of `fetch-depth: 1` — so they will pay the same one-off fetch.
#     Left in deliberately rather than special-cased on `$CI`: neither reads the clock, so it buys
#     them nothing, but a branch that only ever runs in a sandbox is a branch nothing exercises.
# --------------------------------------------------------------------------------------------

# ⛔ THE MARGIN, NOT THE WINDOW. Every number the window is built from has its own home and is READ
# below, never typed here (CLAUDE.md §1): `stuck_clock.stuck_threshold_hours()`,
# `learning_rate.window_hours()` and `out_of_ideas.budget_days()` — the last itself read from
# `priority-weights.json:age_saturates_days`. This is only the safety factor applied to the LARGEST
# of them, so one deepen overshoots the boundary instead of landing on it.
# ⚠ IT IS 2, NOT 14, AND THAT IS A CORRECTION MADE BEFORE THIS SHIPPED. The first cut sized the
# window off stuck_clock's threshold alone and reached 336 h — which is EXACTLY out_of_ideas' budget,
# so the instrument with the longest memory would have been left sitting on the edge of the horizon
# it needs. Sizing off the max is what lets the factor be small.
LEDGER_HISTORY_MARGIN=2

# ⛔ ONE PROBE FOR EVERY READER OF THE HISTORY, NOT ONE PER READER. Three modules derive verdicts
# from the ledger's git history and each has its own memory; the clone has to satisfy the longest.
# Each import is guarded separately, so a module that is renamed or unimportable narrows the window
# rather than aborting setup — and the answer never falls below what the modules that DID load need.
_ledger_history_need_hours() {
  python3 - <<'NEEDPY' 2>/dev/null || true
import os, sys
sys.path.insert(0, os.path.join("research", "autonomy"))
need = 0.0
try:
    import stuck_clock                       # the stall clock
    need = max(need, float(stuck_clock.stuck_threshold_hours()))
except Exception:
    pass
try:
    import learning_rate                     # is the loop learning? the shortest window
    need = max(need, float(learning_rate.window_hours()))
except Exception:
    pass
try:
    import out_of_ideas                      # THE LONG ONE: age_saturates_days
    need = max(need, float(out_of_ideas.budget_days()) * 24.0)
except Exception:
    pass
print(int(need))
NEEDPY
}

_deepen_ledger_history() {
  command -v git >/dev/null 2>&1 || return 0
  [ "$(git rev-parse --is-shallow-repository 2>/dev/null || echo false)" = "true" ] || return 0

  local need_h
  need_h="$(_ledger_history_need_hours)"
  case "$need_h" in ''|*[!0-9]*) return 0 ;; esac
  [ "$need_h" -gt 0 ] || return 0

  # The horizon is the OLDEST commit git can still see for the ledger — `stuck_clock`'s own
  # `versions[0].when`, asked of git directly rather than restated.
  local oldest
  oldest="$(git log --format=%ct --follow -- research/autonomy/research-ledger.json 2>/dev/null | tail -1)"
  case "$oldest" in ''|*[!0-9]*) return 0 ;; esac

  local age_h=$(( ( $(date -u +%s) - oldest ) / 3600 ))
  if [ "$age_h" -ge "$need_h" ]; then
    return 0            # the bound already outruns every reader's window: nothing left to buy
  fi

  # ⚠ SILENT UNLESS IT MOVED. While the ledger's whole life is shorter than the longest window, the
  # guard above cannot tell "nothing more exists" from "not fetched yet", so this runs each session.
  # The wall times and bytes are in the header block above, which is their one home (CLAUDE.md §1).
  # Announcing a no-op every session is how a step earns a deletion it does not deserve.
  local window_h=$(( need_h * LEDGER_HISTORY_MARGIN ))
  if git fetch --quiet --shallow-since="${window_h} hours ago" origin main 2>/dev/null; then
    local deepened new_age_h
    deepened="$(git log --format=%ct --follow -- research/autonomy/research-ledger.json 2>/dev/null | tail -1)"
    case "$deepened" in ''|*[!0-9]*) return 0 ;; esac
    new_age_h=$(( ( $(date -u +%s) - deepened ) / 3600 ))
    if [ "$new_age_h" -gt "$age_h" ]; then
      echo "dev-setup: deepening the ledger history — the clocks could see back ${age_h} h against a ${need_h} h window; git now reaches ${new_age_h} h."
    fi
  else
    echo "dev-setup: the deepen fetch did not succeed — the ledger clocks will keep reporting censored lower bounds, which is honest, not wrong."
  fi
  return 0
}

_deepen_ledger_history || true

if [ "${1:-}" = "--if-needed" ]; then
  sys_missing="$(_missing_in python3 "$SYSTEM_PROBE")"
  tool_py="$(_pytest_python || true)"
  if [ -z "$tool_py" ] || [ ! -x "$tool_py" ]; then
    tool_missing=" (pytest interpreter not found)"
  else
    tool_missing="$(_missing_in "$tool_py" "$TEST_PROBE")"
  fi
  # The one that decides whether the suites go red. It is usually the system python3, and it is the
  # interpreter the two probes above between them managed not to check against TEST_PROBE.
  run_py="$(_preflight_python || true)"
  if [ -z "$run_py" ] || [ ! -x "$run_py" ]; then
    run_missing=" (no interpreter would run the suites)"
  else
    run_missing="$(_missing_in "$run_py" "$TEST_PROBE")"
  fi
  # ⛔ THE PROBE MUST ASK ABOUT EVERY DEPENDENCY THE SCRIPT INSTALLS, NOT JUST THE PYTHON ONES.
  # Added with the ghostscript step, 2026-08-27, because the first version of that step sat BELOW
  # this early exit — so on a sandbox whose interpreters were already complete, `--if-needed` printed
  # "nothing to do" and returned without ever reaching it. That is this file's own documented failure
  # mode ("a populated field is not a measured one") arriving one layer up: the probe answered a
  # narrower question than the script's job.
  bin_missing=""
  command -v gs >/dev/null 2>&1 || bin_missing=" ghostscript"
  if [ -z "$sys_missing" ] && [ -z "$tool_missing" ] && [ -z "$run_missing" ] && [ -z "$bin_missing" ]; then
    echo "dev-setup: every interpreter the gates use already imports what they need — nothing to do."
    exit 0
  fi
  [ -n "$bin_missing" ] && echo "dev-setup: a system binary the artifact chain needs is missing:$bin_missing"
  [ -n "$sys_missing" ] && echo "dev-setup: system python3 is missing:$sys_missing"
  [ -n "$tool_missing" ] && echo "dev-setup: the pytest tool venv is missing:$tool_missing"
  [ -n "$run_missing" ] && echo "dev-setup: $run_py — the interpreter preflight RUNS THE SUITES in — is missing:$run_missing"
  echo "dev-setup: installing."
fi

echo "== system python3 (systems_check.py, the linters and the node-free gates run here) =="
python3 -m pip install --quiet --disable-pip-version-check "${SYSTEM_DEPS[@]}"

echo "== the pytest tool venv (every test import resolves here, NOT in the system interpreter) =="
if command -v uv >/dev/null 2>&1; then
  uv tool install --force $(printf -- '--with %s ' "${TEST_DEPS[@]}") pytest
else
  # ⛔ NOT A SILENT PASS. Without uv there is no tool venv to install into, and the tests will fail
  # on imports the line above just satisfied — which is exactly the confusing red this script exists
  # to remove, so say so and exit non-zero rather than reporting success.
  echo "   uv is not installed, so the pytest tool venv cannot be provisioned." >&2
  echo "   Install uv, or install pytest into system python3 so that both live in one interpreter." >&2
  exit 1
fi

# ⛔ AND INTO WHICHEVER INTERPRETER PREFLIGHT WILL ACTUALLY USE, WHICH IS USUALLY NOT THE TOOL VENV.
# See `_preflight_python` above for the incident. Installing TEST_DEPS twice is a few seconds of pip
# resolving already-satisfied requirements; NOT installing them is a red publication gate whose 11
# failures name somebody else's lane.
run_py="$(_preflight_python || true)"
tool_py="$(_pytest_python || true)"
if [ -n "$run_py" ] && [ -x "$run_py" ] && [ "$run_py" != "$tool_py" ]; then
  echo
  echo "== $run_py (preflight RUNS THE SUITES here — see _preflight_python) =="
  "$run_py" -m pip install --quiet --disable-pip-version-check "${TEST_DEPS[@]}"
fi

# ⛔ VERIFY IN THE RUNNING INTERPRETER RATHER THAN TRUSTING THE INSTALLS. Every line above can report
# success while the gate still goes red — that is the entire failure this script exists to prevent,
# and it has now happened twice from two different directions (the uv-tool trap, then this one).
if [ -n "$run_py" ] && [ -x "$run_py" ]; then
  still="$(_missing_in "$run_py" "$TEST_PROBE")"
  if [ -n "$still" ]; then
    echo >&2
    echo "   ⛔ $run_py still cannot import:$still" >&2
    echo "   That is the interpreter preflight runs the suites in, so the gates will go red on" >&2
    echo "   imports rather than on the repository. Fix this before reading any test result." >&2
    exit 1
  fi
fi

# ═══════════════════════════════════════════════════════════════════════════════════════════════
# SYSTEM BINARIES THE DERIVED-ARTIFACT CHAIN NEEDS, WHICH ARE NOT PYTHON PACKAGES
# ═══════════════════════════════════════════════════════════════════════════════════════════════
# ⛔ GHOSTSCRIPT, ADDED 2026-08-27. `figures/svg_to_print_formats.py` writes the EPS and CMYK TIFF a
# journal actually uploads, and Ghostscript is the ONLY offline PDF->EPS/TIFF path this image has:
# the tool's own refusal message records that it found no inkscape, no rsvg-convert, no pdftops, no
# cairosvg and no ImageMagick. Without it `regenerate_aso_chain.sh` fails that step, falls back to
# `--check`, and fails that too — so the chain reports "something is stale" and the deliverable a
# reader downloads stays stale.
# ⚠ AND IT WAS NOT IN ANY WORKFLOW EITHER. Measured that day: `grep -rl "svg_to_print_formats\|ghostscript"
# .github/workflows/` returned NOTHING, so unlike the LibreOffice .docx step there was no CI escape
# hatch to route this to — it was simply never regenerated anywhere. It installs from the standard
# archive in about ten seconds, which is the whole reason this line exists rather than a workflow.
if ! command -v gs >/dev/null 2>&1; then
  echo
  echo "== ghostscript (figures/svg_to_print_formats.py: EPS + CMYK TIFF; no other offline path) =="
  if apt-get install -y -qq ghostscript >/dev/null 2>&1 || sudo apt-get install -y -qq ghostscript >/dev/null 2>&1; then
    echo "   installed: $(gs --version 2>/dev/null)"
  else
    # ⚠ NOT FATAL, AND DELIBERATELY SO. Every Python gate above still runs without it; only the
    # print-format step is affected, and it fails loudly with its own apt-get line. A hard exit here
    # would turn a missing figure format into a refusal to set up the sandbox at all.
    echo "   ⚠ could not install ghostscript — figures/svg_to_print_formats.py will refuse and say so" >&2
  fi
fi

echo
echo "DEV SETUP OK — ./scripts/preflight.sh should now measure the repository rather than the sandbox."
