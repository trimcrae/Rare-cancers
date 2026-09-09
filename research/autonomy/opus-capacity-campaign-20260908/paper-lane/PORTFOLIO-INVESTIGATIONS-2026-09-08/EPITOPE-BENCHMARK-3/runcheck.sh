#!/bin/bash
# usage: runcheck.sh <NN-name> <workdir> <command...>
LANE=/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/EPITOPE-BENCHMARK-3
d="$LANE/checks/$1"; shift; wd="$1"; shift
mkdir -p "$d"
{ printf 'cwd: %s\n' "$wd"; printf '%q ' "$@"; printf '\n'; } > "$d/command.txt"
( cd "$wd" && "$@" ) > "$d/stdout.txt" 2> "$d/stderr.txt"
ec=$?
echo "$ec" > "$d/exit_code.txt"
echo "[$d] exit=$ec"
