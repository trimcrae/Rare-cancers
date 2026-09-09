#!/usr/bin/env bash
# usage: run_check.sh <check-dir-name> <command...>
# Records command, stdout, stderr and the REAL exit code (no pipes in the measured command).
set -u
LANE="/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/NEOANTIGEN-7"
name="$1"; shift
d="$LANE/checks/$name"; mkdir -p "$d"
printf '%s\n' "$*" > "$d/command.txt"
cd /home/user/Rare-cancers
"$@" > "$d/stdout.txt" 2> "$d/stderr.txt"
rc=$?
printf '%s\n' "$rc" > "$d/exit_code.txt"
echo "check $name exit $rc"
exit 0
