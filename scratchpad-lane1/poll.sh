#!/bin/bash
RUN=$1
for i in $(seq 1 45); do
  s=$(curl -s "https://api.github.com/repos/trimcrae/Rare-cancers/actions/runs/$RUN" | python3 -c "import sys,json;print(json.load(sys.stdin).get('status'))")
  echo "$(date -u) $s"
  if [ "$s" = completed ]; then echo DONE; break; fi
  sleep 70
done
