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
    alchemy starts from the plain-MD-relaxed complex (SETUP_VER=v2pe) or the raw one (v1). Both names are
    accepted so a copy of this file held by another session keeps working.

    CORRECTED 2026-07-25: an earlier version of this docstring said pre-equilibration "only moves coordinates,
    particle counts are identical, so OpenFE's particle check cannot catch a v1 trajectory restored into a v2pe
    run." That was asserted without measuring it and it is FALSE. Measured from the prime markers, the v1 build
    is 146,020 particles and the v2pe build is 141,968 -- the pre-equilibrated complex is RE-SOLVATED, not merely
    relaxed -- so `assert_multistate_system_equality` WOULD reject a cross-restore.

    Reproducing `use_preequil` is still mandatory, for a stronger reason than a missed check: the setup-cache key
    itself carries the version (`..._r0__nagl__v1` vs `..._r0__nagl__v2pe`), so getting it wrong does not merely
    risk a bad resume -- it runs a DIFFERENT SYSTEM. That is exactly what happened on 2026-07-25: four reverse-leg
    attempts silently ran the 146,020-particle v1 system against a forward leg built at 141,968, and every one of
    them died at warmup iteration 1.
    """
    return doc.get("_required_run_params") or doc.get("_prefix_keying_params") or []


def required_params_by_kind(doc):
    """{kind: [required keys]} for a MULTI-KIND watch list, or {} for a legacy single-kind one.

    ADDED 2026-07-26 when the watchdog was generalised past the ternary lane. The presence of this key is what
    switches the validator into strict multi-kind mode, so the ternary list -- which does not have it -- is
    validated by exactly the code path it always was. A schema migration that silently reinterpreted a live
    entry would be the worst possible outcome here: those four entries are watching billed legs right now.
    """
    m = doc.get("_required_run_params_by_kind")
    return m if isinstance(m, dict) else {}


def validate(doc, known_kinds=None):
    """Return a list of (leg_id, direction, [problem strings]) for enabled entries that are incomplete.

    Legacy (single-kind) list: unchanged -- every enabled entry must carry every key in `_required_run_params`.

    Multi-kind list (`_required_run_params_by_kind` present): an enabled entry must ALSO declare a `kind`, that
    kind must appear in the map, and -- when `known_kinds` is supplied by the caller -- the running code must
    actually implement it. THE POINT OF THAT LAST CHECK: an entry naming a kind the engine has never heard of
    would otherwise be skipped with a shrug while the watch list still claimed to cover it. Monitoring that
    watches nothing is this program's most expensive defect class (a GCP watchdog sat unparseable for days; a
    gating diagnostic returned success while measuring nothing seven ways), so an unknown kind is a LOUD
    REFUSAL that aborts the pass, never a silent skip.
    """
    required = required_params(doc)
    by_kind = required_params_by_kind(doc)
    problems = []
    for entry in doc.get("watch", []):
        if not entry.get("enabled"):
            continue
        # Legacy identity tuple, preserved EXACTLY: the ternary list's messages must not change.
        who = (entry.get("leg_id", "?"), entry.get("direction", "?"))
        if by_kind:
            who = (entry.get("unit_id") or entry.get("leg_id") or "?", entry.get("kind") or "?")
            kind = entry.get("kind")
            if not kind:
                problems.append((who[0], who[1], ["kind (this list is multi-kind; an entry with no kind "
                                                  "cannot be relaunched by anything)"]))
                continue
            if kind not in by_kind:
                problems.append((who[0], kind, [f"kind={kind!r} is not declared in "
                                                f"_required_run_params_by_kind {sorted(by_kind)}"]))
                continue
            if known_kinds is not None and kind not in known_kinds:
                problems.append((who[0], kind, [f"kind={kind!r} is NOT IMPLEMENTED by this watchdog "
                                                f"(known: {sorted(known_kinds)}) — refusing to claim coverage "
                                                f"it does not have"]))
                continue
            required = list(by_kind.get(kind) or [])
        missing = [k for k in required if k not in entry]
        if missing:
            problems.append((who[0], who[1], missing))
    return problems


def known_kinds():
    """The job kinds the RUNNING CODE implements, or None if the registry cannot be imported.

    Imported lazily inside the function on purpose: `vast_watchdog` imports THIS module at module level, so a
    top-level import here would be a cycle. Returning None (rather than an empty set) when the import fails
    keeps this file usable standalone -- an empty set would fail every multi-kind entry for the wrong reason.
    """
    try:
        import vast_watchdog  # noqa: PLC0415 — deliberate: see docstring
        return set(vast_watchdog.KINDS)
    except Exception:  # noqa: BLE001
        return None


def main(argv):
    if len(argv) != 2:
        print("usage: watchdog_validate.py <watch-list.json>", file=sys.stderr)
        return 2
    with open(argv[1]) as fh:
        doc = json.load(fh)
    problems = validate(doc, known_kinds=known_kinds())
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
