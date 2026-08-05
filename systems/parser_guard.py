#!/usr/bin/env python3
"""Fail-red guard: every registered parser can still find what it parses. ($0, pure stdlib)

    python3 systems/parser_guard.py

⛔ WHY THIS EXISTS, AND WHY IT LANDS BEFORE ANY DOCUMENT MOVES.

Several parsers in this repository do the honest thing and REPORT their own blindness rather than
returning an empty result — the plan scanner's message says exactly that, and it is right to. But
reporting blindness and FAILING are different, and only the second is visible from CI. The plan scanner
returns `NOT SCANNED — ... The plan is invisible this run.` and the build stays green, so a renamed
heading produces a board with nothing on it that looks exactly like a board with nothing left to do.

That is tolerable while documents sit still. It is not tolerable during a restructure, where headings and
paths move by design and the failure mode — the model silently stops being read — is the one thing that
must not happen quietly. So this guard is a **precondition** for the migration, not a product of it.

WHAT IT IS. A registry of `parser → the thing it must be able to find`, checked INDEPENDENTLY of the
parser itself. It deliberately does not import the parsers: a guard that runs the code it is guarding
inherits that code's failure modes, and the specific failure being guarded against is a parser that
succeeds while finding nothing.

⚠ THIS GUARD IS NOT A SUBSTITUTE FOR THE PARSERS' OWN CHECKS. It answers one question — *could this
parser still locate its input?* — and says nothing about whether the parse was correct.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

MAP = "research/manuscripts/nr4a3-program-map.md"

#: ⭐ MOVED 2026-08-05. THE ORDERED PLAN now lives in the systems model and `work_ledger` reads the
#: generated view, not the roadmap. This guard follows it — a guard still watching the old location
#: would go green on a file that no longer contains the plan, which is the precise failure it exists
#: to prevent, one layer up.
PLAN_DOC = "systems/views/plan.md"


def read(rel):
    path = os.path.join(REPO, rel)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# ───────────────────────── the registered dependencies ─────────────────────────

def check_plan_heading(fail):
    """work_ledger bounds its scan to a `## ... THE ORDERED PLAN ...` heading."""
    text = read(PLAN_DOC)
    if text is None:
        fail("work_ledger", f"the plan document {PLAN_DOC} does not exist",
             "the plan scanner returns NOT SCANNED and exits 0, so the board empties silently")
        return
    section = re.compile(r"^##\s+(.*)$", re.M)
    heads = [m.group(1) for m in section.finditer(text)]
    hit = [h for h in heads if "THE ORDERED PLAN" in h.upper()]
    if not hit:
        fail("work_ledger", f"no '## ... THE ORDERED PLAN ...' heading in {PLAN_DOC}",
             "the scanner reports its own blindness and exits 0 — a plan with nothing left to do and a "
             "plan nobody can read render identically")
        return
    # The heading existing is not enough: the scan is BOUNDED to that section, so a heading that has
    # drifted away from the checkboxes finds a section with no items and reports success.
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines) if section.match(ln) and "THE ORDERED PLAN" in ln.upper())
    end = next((i for i in range(start + 1, len(lines)) if section.match(lines[i])), len(lines))
    item = re.compile(r"^\s*-\s+\*\*`\[([ x~!–-])\]`")
    if not any(item.match(ln) for ln in lines[start:end]):
        fail("work_ledger", "the ORDERED PLAN section exists but contains no checklist items",
             "the scan is bounded to this section, so a heading that has drifted away from the items "
             "returns an empty list that is indistinguishable from a finished plan")


def check_paths(fail):
    """Linters and registries that read named files."""
    reg = [
        ("lint_consistency", "research/manuscripts/pinned-figures.json", "targets"),
        ("lint_claims", None, None),
    ]
    pin = read("research/manuscripts/pinned-figures.json")
    if pin is None:
        fail("lint_consistency", "pinned-figures.json is missing", "the numeric contract stops being checked")
    else:
        d = json.loads(pin)
        for rel in d.get("targets", []):
            if not os.path.exists(os.path.join(REPO, rel)):
                fail("lint_consistency", f"target does not exist: {rel}",
                     "a scanned file that vanishes reduces coverage without reducing the pass rate")
        wanted = set()
        for key in ("derivations", "artifact_figures", "table_completeness", "subset_checks"):
            for row in d.get(key, []):
                wanted.update(row.get("must_appear_in", []))
                if row.get("file"):
                    wanted.add(row["file"])
        for rel in sorted(wanted):
            if not os.path.exists(os.path.join(REPO, rel)):
                fail("lint_consistency", f"must_appear_in path does not exist: {rel}",
                     "a pinned figure whose home is gone is an unenforced contract")

    src = read("research/manuscripts/lint_claims.py")
    if src is None:
        fail("lint_claims", "lint_claims.py is missing", "language discipline stops being enforced")
    else:
        m = re.search(r"^DEFAULT_TARGETS\s*=\s*\[(.*?)^\]", src, re.S | re.M)
        if not m:
            fail("lint_claims", "DEFAULT_TARGETS could not be located",
                 "this guard cannot confirm the linter still has files to scan")
        else:
            # Only quoted strings on their own line are entries. The block carries an explanatory
            # comment quoting verdict text from the file it lints, and a looser match reads those
            # quotes as paths -- which is how this guard reported two nonexistent "targets" on its
            # first run. A guard that cries wolf gets switched off, so it parses the list shape.
            targets = re.findall(r'^\s*"([^"]+)",?\s*$', m.group(1), re.M)
            if not targets:
                fail("lint_claims", "DEFAULT_TARGETS parsed as empty",
                     "an empty target list makes the linter pass over nothing at all")
            for rel in targets:
                if not os.path.exists(os.path.join(REPO, rel)):
                    fail("lint_claims", f"default target does not exist: {rel}",
                         "the linter scans fewer files and still reports success")
            # ⚠ THE PLAN IS LINTED WHEREVER IT LIVES. Moving it out of the roadmap dropped the
            # warning count from 50 to 43 because ~1,580 lines of gate language left the linted set
            # silently. A linter whose SCOPE shrinks while its PASS RATE improves is the worst
            # possible signal, so the coupling is asserted rather than remembered.
            if PLAN_DOC not in targets:
                fail("lint_claims", f"{PLAN_DOC} is not a lint_claims target",
                     "the plan is what the next session steers by; claim language in it would go "
                     "unlinted while the build stayed green and the warning count went DOWN")


def check_scan_triggers(fail):
    """method-watch-triggers evidence homes: where a fired trigger sends the reader."""
    raw = read("research/method-watch-triggers.json")
    if raw is None:
        fail("trigger_scan", "method-watch-triggers.json is missing",
             "the named-capability scan stops running and nothing says so")
        return
    d = json.loads(raw)
    for t in d.get("triggers", []):
        for e in t.get("evidence_home", []):
            rel = e.get("file") if isinstance(e, dict) else None
            if rel and not os.path.exists(os.path.join(REPO, rel)):
                fail("trigger_scan", f"{t['id']} evidence_home does not exist: {rel}",
                     "a fired trigger would point the reader at a file that is gone")


def check_registry(fail):
    for rel, who in [("research/manuscripts/emc-systems-map.json", "emc_systems_map_check"),
                     ("systems/graph/routes.json", "systems_check"),
                     ("systems/graph/strategies.json", "systems_check"),
                     ("systems/graph/blockers.json", "systems_check"),
                     ("systems/graph/technologies.json", "systems_check"),
                     ("systems/graph/forecasts.json", "systems_check")]:
        if not os.path.exists(os.path.join(REPO, rel)):
            fail(who, f"{rel} is missing", "the registry's invariants stop being checked")


CHECKS = [check_plan_heading, check_paths, check_scan_triggers, check_registry]


def main(argv=None):
    problems: list[tuple[str, str, str]] = []

    def fail(parser, what, why):
        problems.append((parser, what, why))

    for c in CHECKS:
        c(fail)

    if not problems:
        print(f"parser_guard: {len(CHECKS)} dependency groups checked · every registered parser can "
              f"still find its input")
        return 0

    for parser, what, why in problems:
        print(f"ERROR [{parser}] {what}")
        print(f"      why this is not a warning: {why}")
    print(f"\nparser_guard: {len(problems)} parser(s) have lost their input.")
    print("A parser that cannot find what it parses must FAIL, not report and continue — that is the "
          "whole reason this guard exists. Repoint the parser in the same commit as the move.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
