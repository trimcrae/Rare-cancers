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
# raises `pyo3_runtime.PanicException` on import, and `pypdf` imports it. Nothing under
# `preflight.sh` needs pypdf in that interpreter — the PDF guards are TESTS, and tests import from
# the pytest venv, which carries its own working cryptography. So the fix is to ask each
# interpreter only for what it actually runs, rather than to fight the distro package.
#
# SYSTEM: `systems_check.py` needs jsonschema and refuses to run without it (deliberately — it has
# no fallback, because a hand-rolled subset validator silently ignores every keyword it does not
# implement). The other fast gates are pure stdlib plus node.
SYSTEM_DEPS=(jsonschema pyyaml)
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
SYSTEM_PROBE="jsonschema yaml"
TEST_PROBE="pdfminer pypdf pdfplumber jsonschema numpy scipy rdkit boto3 netCDF4 pymbar yaml Bio matplotlib xdist"

_pytest_python() {
  command -v pytest >/dev/null 2>&1 || return 1
  # `pytest` is a console script; its shebang names the interpreter whose site-packages the tests see
  head -1 "$(command -v pytest)" | sed 's/^#!//' | awk '{print $1}'
}

_missing_in() {   # $1 = interpreter, $2 = module list; echoes what it cannot import
  local py="$1" out=""
  for m in $2; do
    "$py" -c "import $m" >/dev/null 2>&1 || out="$out $m"
  done
  printf '%s' "$out"
}

if [ "${1:-}" = "--if-needed" ]; then
  sys_missing="$(_missing_in python3 "$SYSTEM_PROBE")"
  tool_py="$(_pytest_python || true)"
  if [ -z "$tool_py" ] || [ ! -x "$tool_py" ]; then
    tool_missing=" (pytest interpreter not found)"
  else
    tool_missing="$(_missing_in "$tool_py" "$TEST_PROBE")"
  fi
  if [ -z "$sys_missing" ] && [ -z "$tool_missing" ]; then
    echo "dev-setup: both interpreters already import everything the gates need — nothing to do."
    exit 0
  fi
  [ -n "$sys_missing" ] && echo "dev-setup: system python3 is missing:$sys_missing"
  [ -n "$tool_missing" ] && echo "dev-setup: the pytest interpreter is missing:$tool_missing"
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

echo
echo "DEV SETUP OK — ./scripts/preflight.sh should now measure the repository rather than the sandbox."
