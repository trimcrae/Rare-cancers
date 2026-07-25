#!/usr/bin/env python3
"""No variable may be ASSIGNED inside the VM startup heredoc and then EXPANDED BY THE RUNNER.

THE BUG THIS GATES. gpu-ternary-fep-gcp.yml builds the VM startup script with an UNQUOTED heredoc
(`cat > /tmp/startup.sh <<SS`). In an unquoted heredoc:

    $VAR    -> expanded by the RUNNER, as the script is written
    \\$VAR   -> survives into the file, expanded later by the VM

So a variable assigned *inside* the heredoc lives in the VM's shell, and referencing it *unescaped* asks the
RUNNER for a value it never had. The reference silently becomes the empty string. On 2026-07-25 that happened
to DIRSUF: the direction suffix vanished from the spot commit prefix and a REVERSE leg restored the FORWARD
leg's trajectory. It failed only because OpenFE checks particle counts; had they matched it would have reported
forward sampling as reverse. Full write-up: ternary-lane-guard-audit-2026-07-25.md section H.

Notably the file ALREADY documented this exact trap, for STAGE_CACHE:

    # NOTE the backslash escapes: \\$STAGE_CACHE must be evaluated ON THE VM.

so DIRSUF was a lapse against a written-down hazard sitting a few dozen lines away. A prose warning is not a
guard. This is the guard.

Two forms are deliberately NOT flagged, because they are correct:
  * `env FOO=$FOO cmd ...` -- a subprocess environment prefix, not a shell assignment read later. The runner
    expanding $FOO from its OWN env is the intent.
  * a name that is also a runner-level `env:` key on the step -- the runner genuinely has that value.
"""

import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
WORKFLOWS = [
    os.path.join(ROOT, ".github", "workflows", "gpu-ternary-fep-gcp.yml"),
]

HEREDOC_RE = re.compile(r"cat\s*>\s*(\S+)\s*<<(\w+)\s*$")
# an assignment at the start of a statement -- NOT preceded by `env` or another VAR=... (a subprocess prefix)
ASSIGN_RE = re.compile(r"(?:^|;|\bthen\b|\bdo\b|&&|\|\|)\s*([A-Za-z_][A-Za-z0-9_]*)=")
RUNNER_REF_RE = re.compile(r"(?<!\\)\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?")
ENV_KEY_RE = re.compile(r"^\s{6,}([A-Z_][A-Z0-9_]*):\s")


def env_keys(lines):
    """Runner-level env: keys declared on the step — the runner really does hold these."""
    return {m.group(1) for m in (ENV_KEY_RE.match(l) for l in lines) if m}


def strip_comment(line):
    """Drop a trailing/whole-line shell comment. The DIRSUF scan's only false positives were prose inside
    comments (including the STAGE_CACHE warning itself), so comments must not count as references."""
    out, quote = [], None
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            continue
        if ch == "#":
            break
        out.append(ch)
    return "".join(out)


def scan(path):
    lines = open(path).read().split("\n")
    envs = env_keys(lines)
    problems = []
    i = 0
    while i < len(lines):
        m = HEREDOC_RE.search(lines[i])
        if not m:
            i += 1
            continue
        term = m.group(2)
        quoted = m.group(0).rstrip().endswith(("'%s'" % term, '"%s"' % term))
        start = i + 1
        end = start
        while end < len(lines) and lines[end].strip() != term:
            end += 1
        body = lines[start:end]
        if not quoted:
            assigned = set()
            for l in body:
                code = strip_comment(l)
                # skip `env FOO=... BAR=... cmd` subprocess prefixes entirely
                if re.search(r"\benv\s+[A-Za-z_][A-Za-z0-9_]*=", code):
                    code = re.sub(r"\benv\s+(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s*)+", " ", code)
                for a in ASSIGN_RE.finditer(code):
                    assigned.add(a.group(1))
            for n, l in enumerate(body, start=start + 1):
                code = strip_comment(l)
                for ref in RUNNER_REF_RE.finditer(code):
                    v = ref.group(1)
                    if v in assigned and v not in envs:
                        problems.append((v, n, l.strip()[:120]))
        i = end + 1
    return problems


def main():
    failed = 0
    for path in WORKFLOWS:
        name = os.path.basename(path)
        if not os.path.isfile(path):
            print("SKIP %s (not found)" % name)
            continue
        problems = scan(path)
        if problems:
            failed += 1
            print("FAIL %s: variable(s) assigned INSIDE the unquoted heredoc but expanded by the RUNNER — the "
                  "reference silently becomes empty (this is the DIRSUF bug that made a rev leg resume the fwd "
                  "trajectory):" % name)
            for v, n, text in problems:
                print("      %s at line %d: %s" % (v, n, text))
            print("      Fix: compute it in the RUNNER before the heredoc, or escape the use as \\$%s."
                  % problems[0][0])
        else:
            print("PASS %s: no variable is both VM-assigned and runner-expanded" % name)
    return 1 if failed else 0


def test_no_two_shell_variable_in_startup_heredoc():
    assert main() == 0, "a heredoc variable is assigned on the VM and expanded by the runner"


if __name__ == "__main__":
    sys.exit(main())
