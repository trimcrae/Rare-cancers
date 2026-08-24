#!/usr/bin/env bash
# Install CALVADOS at the PINNED commit, with the dependency pin the lane's prespecification records.
#
# ⛔ pandas<3 IS LOAD-BEARING. `calvados.analysis.get_masses` does `masses[0] += 2.` on a pandas
# `.values` view; under pandas 3 that view is non-writeable and the call raises
# `ValueError: assignment destination is read-only`. Reproduced in two lines under pandas 3.0.5 and
# absent under 2.3.3. With the pin the library runs exactly as its authors wrote it.
set -euo pipefail

python -m pip install -q --upgrade pip
python -m pip install -q "openmm>=8.2,<8.5" "MDAnalysis>=2.9,<2.11" "mdtraj>=1.11,<1.12" \
    "pandas<3" numpy biopython Jinja2 tqdm matplotlib PyYAML statsmodels numba scipy pytest

git clone -q "$CALVADOS_REPO" /tmp/CALVADOS
git -C /tmp/CALVADOS checkout -q "$CALVADOS_COMMIT"
GOT="$(git -C /tmp/CALVADOS rev-parse HEAD)"
if [ "$GOT" != "$CALVADOS_COMMIT" ]; then
  echo "::error::CALVADOS checkout is $GOT, not the pinned $CALVADOS_COMMIT"; exit 1
fi
( cd /tmp/CALVADOS && python -m pip install -q . )

python - <<'PY'
import importlib.metadata as md
for p in ("calvados", "openmm", "MDAnalysis", "mdtraj", "numpy", "pandas"):
    print(f"  {p:<12} {md.version(p)}")
PY
# ⚠ Prove the pandas defect is actually absent in THIS environment rather than trusting the pin.
python - <<'PY'
import os, pandas as pd, calvados
p = os.path.join(os.path.dirname(calvados.__file__), "data", "residues.csv")
v = pd.read_csv(p).set_index("three").loc[["ALA", "GLY"], "MW"].values
assert v.flags.writeable, ("the CALVADOS mass array is read-only in this environment — "
                           "get_masses would raise; the pandas pin did not take")
print("  mass-array writeability check: OK")
PY
