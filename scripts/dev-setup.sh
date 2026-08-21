#!/usr/bin/env bash
# Install the test dependencies preflight needs, into the interpreter preflight actually uses.
#
# ⛔ WHY THIS EXISTS. On a fresh remote container 2026-08-21, `./scripts/preflight.sh` reported
# 6 failures and 10 errors in the manuscripts suite. NONE of them was a regression:
#   * `pytest` was absent from `python3`, so preflight fell through to the bare console script on
#     PATH -- the uv-tool venv its own comments name as the branch that "reports 36 failures that do
#     not exist", because that venv cannot see the repository's dependencies;
#   * `pdfminer.six` was absent, so every text-layer guard on the deposited PDFs failed loudly and
#     correctly ("a guard that cannot run is not a guard that passed") -- 10 of them;
#   * `pypdf` was installed but UNIMPORTABLE: it pulls in Debian's `cryptography` 41.0.7 from
#     /usr/lib/python3/dist-packages, which raises `pyo3_runtime.PanicException` on import. A newer
#     wheel earlier on sys.path fixes it; the Debian copy cannot be uninstalled (no RECORD file).
#
# ⚠ A GATE THAT INVENTS FAILURES IS AS BROKEN AS ONE THAT HIDES THEM, and this one invented sixteen
# on a tree whose only change was a new script and a workflow arm. The next session would have had
# to re-derive all three causes before it could commit anything at all.
#
# The package list is TAKEN FROM `.github/workflows/tests.yml` rather than retyped, so the sandbox
# and CI cannot drift apart silently -- that drift is what makes a local green meaningless.
set -euo pipefail
cd "$(dirname "$0")/.."

deps=$(sed -n 's/^ *- *run: *pip install *//p' .github/workflows/tests.yml | head -1)
[ -n "$deps" ] || { echo "dev-setup: no pip install line found in tests.yml" >&2; exit 1; }

# Fast path: everything importable already, so a session start costs nothing.
if python3 - <<'PY' >/dev/null 2>&1
import importlib
for m in ("pytest", "numpy", "scipy", "yaml", "jsonschema", "Bio",
          "pdfminer", "pypdf", "pdfplumber", "matplotlib", "rdkit", "boto3", "xdist"):
    importlib.import_module(m)
PY
then
  echo "dev-setup: test dependencies already importable"
  exit 0
fi

echo "dev-setup: installing $deps pytest-xdist"
python3 -m pip install --quiet $deps pytest-xdist
# ⛔ --ignore-installed IS LOAD-BEARING: pip refuses to uninstall the Debian-managed copy, and
# without a newer wheel ahead of it on sys.path `import pypdf` panics rather than merely warning.
python3 -m pip install --quiet --ignore-installed --upgrade cryptography

python3 - <<'PY'
import importlib
missing = []
for m in ("pytest", "numpy", "scipy", "yaml", "jsonschema", "Bio",
          "pdfminer", "pypdf", "pdfplumber", "matplotlib", "rdkit", "boto3", "xdist"):
    try:
        importlib.import_module(m)
    except Exception as exc:                      # noqa: BLE001 - reported, never swallowed
        missing.append(f"{m}: {type(exc).__name__}: {exc}")
if missing:
    print("dev-setup: STILL UNIMPORTABLE -- preflight's verdict is not trustworthy until these are "
          "fixed:\n  " + "\n  ".join(missing))
else:
    print("dev-setup: every test dependency imports")
PY
