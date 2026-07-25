#!/bin/bash
# Emit a line whenever the job's step-state string changes; exit when the job completes.
JOB=$1
prev=""
for i in $(seq 1 70); do
  cur=$(curl -s "https://api.github.com/repos/trimcrae/Rare-cancers/actions/jobs/$JOB" \
        | python3 "$(dirname "$0")/jobstate.py" 2>/dev/null)
  if [ -z "$cur" ]; then cur="poll-error"; fi
  if [ "$cur" != "$prev" ]; then echo "$cur"; prev="$cur"; fi
  case "$cur" in
    completed*) break ;;
  esac
  sleep 45
done
