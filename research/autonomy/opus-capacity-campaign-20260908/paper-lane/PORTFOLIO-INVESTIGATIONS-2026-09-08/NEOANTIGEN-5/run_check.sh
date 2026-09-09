#!/usr/bin/env bash
# Usage: run_check.sh <check-name> <command...>   — records command/stdout/stderr/real exit code.
set -u
LANE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
name="$1"; shift
d="$LANE/checks/$name"; mkdir -p "$d"
printf '%s\n' "$*" > "$d/command.txt"
( cd /home/user/Rare-cancers && "$@" ) > "$d/stdout.txt" 2> "$d/stderr.txt"
rc=$?
printf '%s\n' "$rc" > "$d/exit_code.txt"
echo "[$name] exit=$rc"
exit 0
