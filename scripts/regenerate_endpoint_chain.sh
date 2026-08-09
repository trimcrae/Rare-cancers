#!/usr/bin/env bash
# Regenerate the cross-disease endpoint artifacts in DEPENDENCY ORDER, then verify every one.
#
# WHY THIS EXISTS. On 2026-08-09 commit 8af2beae changed endpoint-corpus.json without regenerating
# what reads it, and the staleness was caught by CI -- after a push -- as "EMC evidence artifacts
# reproduce from their generators". Nothing local would have caught it, because the order was held
# together by remembering it. The chain is:
#
#     endpoint_corpus            (reads the literature-cache extraction)
#       -> orr_dcr_reread        (reads the corpus)
#       -> endpoint_regime_map   (reads the corpus)
#       -> placebo_arm_calibration  (reads the corpus AND the regime map)
#       -> endpoint_prior_art_audit (reads its own inputs AND the regime map)
#       -> endpoint_regime_figure   (reads the regime map)
#
# Order matters twice over: placebo_arm_calibration and endpoint_prior_art_audit both read the
# regime map, so regenerating the map after them leaves them stale in a way only --check reveals.
#
# This does NOT run --extract. Extraction needs the literature-cache branch and rewrites the inputs
# cache from ~156 MB of payloads; it is a separate, deliberate act.
set -euo pipefail
cd "$(dirname "$0")/.."

PRODUCERS=(
  endpoint_corpus
  orr_dcr_reread
  endpoint_regime_map
  placebo_arm_calibration
  endpoint_prior_art_audit
  endpoint_regime_figure
)

echo "== regenerating in dependency order =="
for p in "${PRODUCERS[@]}"; do
  printf '   %-28s ' "$p"
  if python3 "research/manuscripts/$p.py" >/dev/null 2>&1; then
    echo "ok"
  else
    echo "FAILED"
    echo "   rerun 'python3 research/manuscripts/$p.py' to see why"
    exit 1
  fi
done

echo "== verifying every artifact re-derives =="
rc=0
for p in "${PRODUCERS[@]}"; do
  printf '   %-28s ' "$p --check"
  if python3 "research/manuscripts/$p.py" --check >/dev/null 2>&1; then
    echo "ok"
  else
    echo "FAILED"
    rc=1
  fi
done

if [ "$rc" -ne 0 ]; then
  echo "CHAIN NOT CLEAN -- an artifact does not re-derive even after regeneration."
  echo "That is a producer bug, not a staleness problem."
  exit 1
fi
echo "CHAIN OK -- all ${#PRODUCERS[@]} artifacts regenerated and verified."
