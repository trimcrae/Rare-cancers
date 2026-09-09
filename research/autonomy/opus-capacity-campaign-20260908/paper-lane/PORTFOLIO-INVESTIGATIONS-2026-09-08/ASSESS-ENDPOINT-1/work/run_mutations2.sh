#!/bin/bash
# Corrected re-run of the three mutations whose sed patterns failed to match in check 03
# (M2/M5/M6). Harness source is mutated on a COPY; artifacts are read unmodified in place;
# the harness's ledger output is redirected to a throwaway dir, never to ENDPOINT-1.
set -u
W=/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/ASSESS-ENDPOINT-1/work
END=/home/user/Rare-cancers/research/manuscripts/endpoint
run() {
  local label="$1" sedexpr="$2"
  rm -rf "$W/mut/run2"; mkdir -p "$W/mut/run2"
  if [ "$sedexpr" != "-" ]; then sed -e "$sedexpr" "$W/mut/harness_copy.py" > "$W/mut/run2/h.py"; else cp "$W/mut/harness_copy.py" "$W/mut/run2/h.py"; fi
  if [ "$sedexpr" != "-" ] && cmp -s "$W/mut/run2/h.py" "$W/mut/harness_copy.py"; then echo "=== $label -> SED DID NOT MATCH (mutation not applied)"; return; fi
  MUT_END="$END" MUT_LANE="$W/mut/run2" python3 "$W/mut/run2/h.py" > "$W/mut/run2/o.txt" 2>&1
  local rc=$?
  echo "=== $label -> harness exit $rc"
  sed -n '/^controls:/,/^$/p' "$W/mut/run2/o.txt"
  rm -f "$W/mut/run2/claim-rederivation-ledger.json"
}
run "M0b baseline (unmutated copy, artifacts read in place)" "-"
run "M2b break binomial tail (drop the last term)" 's|    for i in range(k, n+1):|    for i in range(k, n):|'
run "M5b vacuous mutation control (SD += 0)" 's|^bad\[0\]\["cells"\]\["SD"\] += 40|bad[0]["cells"]["SD"] += 0|'
run "M6b identity-preserving mutation (SD and evaluable_n both +40)" 's|^bad\[0\]\["cells"\]\["SD"\] += 40|bad[0]["cells"]["SD"] += 40; bad[0]["evaluable_n"] += 40|'
rm -rf "$W/mut/run2"
