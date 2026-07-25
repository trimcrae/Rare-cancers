#!/bin/sh
# LANE 10 poller — corrected RUNG-5a basin search.
RUN=${1:-30178697504}
i=0
while [ $i -lt 70 ]; do
  i=$((i+1))
  s=$(curl -s "https://api.github.com/repos/trimcrae/Rare-cancers/actions/runs/$RUN" | python3 -c "import sys,json;print(json.load(sys.stdin).get('status'))" 2>/dev/null)
  echo "$(date -u +%H:%M) $s"
  if [ "$s" = completed ]; then echo DONE; break; fi
  sleep 70
done
