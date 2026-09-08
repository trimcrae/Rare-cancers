#!/bin/sh
# Preserve one attempt: exact expanded command, stdout, stderr and the REAL exit code.
# Usage: run-check.sh <RUN-NAME> <command...>   (no pipes; $? is the command's own status)
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
NAME="$1"; shift
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT="$DIR/CHECKS-RUNS/$NAME-$STAMP"
mkdir -p "$OUT"
printf '%s\n' "cwd: $DIR" > "$OUT/cmd.txt"
printf 'CMD: %s\n' "$*" >> "$OUT/cmd.txt"
cd "$DIR" || exit 99
"$@" > "$OUT/stdout.txt" 2> "$OUT/stderr.txt"
RC=$?
printf '%d\n' "$RC" > "$OUT/exit.txt"
printf 'exit: %d\n' "$RC" >> "$OUT/cmd.txt"
echo "$OUT EXIT=$RC"
exit "$RC"
