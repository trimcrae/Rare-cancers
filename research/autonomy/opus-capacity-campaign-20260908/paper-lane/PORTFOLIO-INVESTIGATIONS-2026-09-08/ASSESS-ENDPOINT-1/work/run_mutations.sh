#!/bin/bash
# ASSESS-ENDPOINT-1 control-falsifiability battery.
# Each mutation targets ONE known-answer control of ENDPOINT-1's harness.
# A control that CONTROLS must turn FAIL (and the harness exit 2) under its mutation.
set -u
W="$(cd "$(dirname "$0")" && pwd)"
run() {  # $1=label  $2=sed-expr-on-harness  $3=python-mutation-of-artifacts (or "-")
  local label="$1" sedexpr="$2" datamut="$3"
  rm -rf "$W/mut/run"; mkdir -p "$W/mut/run/artifacts" "$W/mut/run/out"
  cp "$W/mut/artifacts/"* "$W/mut/run/artifacts/"
  if [ "$datamut" != "-" ]; then python3 -c "$datamut" "$W/mut/run/artifacts"; fi
  if [ "$sedexpr" != "-" ]; then sed -e "$sedexpr" "$W/mut/harness_copy.py" > "$W/mut/run/h.py";
  else cp "$W/mut/harness_copy.py" "$W/mut/run/h.py"; fi
  MUT_END="$W/mut/run/artifacts" MUT_LANE="$W/mut/run/out" python3 "$W/mut/run/h.py" > "$W/mut/run/o.txt" 2>&1
  local rc=$?
  echo "=== $label -> harness exit $rc"
  sed -n '/^controls:/,/^$/p' "$W/mut/run/o.txt"
}

run "M0 baseline (no mutation)" "-" "-"
run "M1 break wilson() closed form (z=1.0)" 's|^def wilson(x, n, z=1.959963984540054):|def wilson(x, n, z=1.0):|' "-"
run "M2 break binomial tail (drop last term)" 's|for i in range(k, n + 1))|for i in range(k, n))|' "-"
run "M3 break quantile_type7 (lower order stat)" 's|    return s\[lo\] + (h - lo) \* (s\[hi\] - s\[lo\])|    return float(s[lo])|' "-"
run "M4 corrupt one R2_per_arm_rows gap value" "-" '
import json,sys
p=sys.argv[1]+"/orr-dcr-reread.json"; d=json.load(open(p))
d["R2_per_arm_rows"][5]["gap_pp"]=d["R2_per_arm_rows"][5]["gap_pp"]+9.0
json.dump(d,open(p,"w"))'
run "M5 vacuous mutation control (SD += 0)" 's|    bad\[0\]\["cells"\]\["SD"\] += 40|    bad[0]["cells"]["SD"] += 0|' "-"
run "M6 identity-preserving mutation (SD and denom both +40)" 's|    bad\[0\]\["cells"\]\["SD"\] += 40|    bad[0]["cells"]["SD"] += 40; bad[0]["evaluable_n"] += 40|' "-"
