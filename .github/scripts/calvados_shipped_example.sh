#!/usr/bin/env bash
# Reproduce the CALVADOS package's OWN shipped single-IDR example end to end.
#
# ⭐ WHY. Everything else in this lane is our sequences through our wrapper. This is the one step
# that can distinguish "the instrument works and our answer is what it is" from "our wrapper does
# something and nobody checked". It uses the package's example directory unmodified.
set -euo pipefail
mkdir -p shipped_example
cp -a /tmp/CALVADOS/examples/single_IDR/* shipped_example/
cd shipped_example
# Short, because this step tests the PIPELINE, not a scientific quantity. It must produce enough
# frames for the analysis to run at all; it is not compared with any published number, and no
# number from it enters any claim.
python - <<'PY'
import re
src = open("prepare.py").read()
src = src.replace("N_frames = 1010", "N_frames = 120").replace("N_save = 7000", "N_save = 700")
open("prepare.py", "w").write(src)
PY
python prepare.py --name A1SLCD
python A1SLCD/run.py --path A1SLCD
test -s data/conf_prop.csv || { echo "::error::the shipped example produced no conf_prop.csv"; exit 1; }
python - <<'PY'
import csv, json
rows = {r[""]: r for r in csv.DictReader(open("data/conf_prop.csv"))}
nu = float(rows["nu"]["value"])
print("shipped example nu =", nu)
if not (0.30 <= nu <= 0.75):
    raise SystemExit(f"::error::shipped-example nu {nu} outside the physical range — the "
                     f"instrument, not the biology, is what failed")
json.dump({"shipped_example_nu": nu,
           "rows": {k: {kk: vv for kk, vv in v.items()} for k, v in rows.items()},
           "_what_this_is": "a pipeline reproduction of the package's own example, at reduced "
                            "sampling. No claim is made from this number."},
          open("analysis.json", "w"), indent=1)
PY
