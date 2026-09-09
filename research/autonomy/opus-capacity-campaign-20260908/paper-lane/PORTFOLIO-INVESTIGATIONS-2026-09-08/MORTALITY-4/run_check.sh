#!/usr/bin/env bash
# usage: run_check.sh <NN-name> <command...>
d="checks/$1"; shift
mkdir -p "$d"
printf '%s\n' "$*" > "$d/command.txt"
"$@" > "$d/stdout.txt" 2> "$d/stderr.txt"
rc=$?
echo "$rc" > "$d/exit_code.txt"
echo "[$d] exit=$rc"
