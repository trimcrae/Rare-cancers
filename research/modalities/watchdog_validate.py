#!/usr/bin/env python3
"""Validate ternary-watch.json before the watchdog acts on it.

WHY THIS IS A FILE AND NOT AN INLINE `python3 -c` IN THE WORKFLOW. It was inline first, and its Python lines
sat at column 0 -- which dedents them out of the `run: |` block scalar and makes the whole workflow file
INVALID YAML. GitHub's symptom for an unparseable workflow is a 422 "Workflow does not have 'workflow_dispatch'
trigger", i.e. it reports a *missing trigger* rather than a syntax error, and a `schedule:` cron on an
unparseable file simply never fires. So the guard meant to stop the watchdog acting on bad config instead
stopped the watchdog running at all -- silently. Keeping it in a file makes that impossible and makes the guard
directly unit-testable (tests/test_watchdog_validate.py) instead of reachable only through CI.

WHAT IT CHECKS. Every parameter that KEYS THE SPOT COMMIT PREFIX must be present on each enabled entry, because
the watchdog relaunches a leg from these values alone. The prefix is

    <seed>_dt<timestep_fs>fs_clig0_wu<warmup_timestep_fs>[_<commit_salt>][_dir<direction>]

so an entry missing any of them makes the watchdog "resume" a DIFFERENT trajectory than the one it is watching
-- the direction-blind-key bug class in ternary-lane-guard-audit-2026-07-25.md, which this repo has now hit
five times. Exit 1 (with a GitHub error annotation per offending entry) rather than let the watchdog act.
"""

import json
import sys


def required_params(doc):
    """The params every enabled entry must carry.

    `_required_run_params` supersedes `_prefix_keying_params`: the list outgrew its original name once
    `use_preequil` had to be reproduced. That one is NOT part of the commit prefix, but it selects whether the
    alchemy starts from the plain-MD-relaxed complex (SETUP_VER=v2pe) or the raw one (v1) -- and because
    pre-equilibration only moves coordinates, particle counts are identical, so OpenFE's particle check cannot
    catch a v1 trajectory restored into a v2pe run the way it caught the fwd/rev mismatch. Both names are
    accepted so a copy of this file held by another session keeps working.
    """
    return doc.get("_required_run_params") or doc.get("_prefix_keying_params") or []


def validate(doc):
    """Return a list of (leg_id, direction, [missing keys]) for enabled entries that are incomplete."""
    required = required_params(doc)
    problems = []
    for entry in doc.get("watch", []):
        if not entry.get("enabled"):
            continue
        missing = [k for k in required if k not in entry]
        if missing:
            problems.append((entry.get("leg_id", "?"), entry.get("direction", "?"), missing))
    return problems


def main(argv):
    if len(argv) != 2:
        print("usage: watchdog_validate.py <ternary-watch.json>", file=sys.stderr)
        return 2
    with open(argv[1]) as fh:
        doc = json.load(fh)
    problems = validate(doc)
    for leg, direction, missing in problems:
        print(
            "::error title=WATCHDOG CONFIG INVALID::%s dir=%s is missing prefix-keying param(s) %s "
            "— a relaunch would not reproduce the run it is watching. Refusing to act."
            % (leg, direction, ",".join(missing))
        )
    if not problems:
        n = len([e for e in doc.get("watch", []) if e.get("enabled")])
        print("watch list valid: %d enabled entry/entries carry every required run param" % n)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
