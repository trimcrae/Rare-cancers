#!/usr/bin/env python3
"""The anti-gaming guard — a bar may not be changed by the cycle that the bar just blocked.

⛔⛔ WHY THIS FILE IS THE PRICE OF THE WIDE GRANT. On 2026-08-26 trimcrae gave the loop free rein to
edit the repository, merge to `main` unattended, manage its own triggers and change its own process
(architecture §10.1, decisions D5-D7). That is survivable for exactly one reason: **improving the
mechanism and making your own success easier are both edits, and this script can tell them apart.**

    THE TEST:  does this change make it easier for the loop to report success?

The loop already writes down what blocked each cycle (the receipt) and git already records what each
cycle changed (the diff). A cycle that does BOTH — blocked by a standard, then edits that standard —
is the failure mode, and it is the one that ends with a paper published because the bar moved rather
than because the work got better. **A later cycle may make the identical change**, declared; what is
refused is making it under pressure, with the obstacle still in front of you.

TWO CLASSES OF PATH (architecture §10.4):

    GOVERNED   the weights, the publish bar, the authority file, CLAUDE.md, AGENTS.md, the health
               conditions, any test. Editing one is allowed unattended but must be DECLARED in
               amendments.jsonl, and is refused outright if that cycle was blocked by it.
    FREE       everything else. Fix a bug, add a check, refactor, correct a doc, retime a Routine.
               No ceremony — this is the bulk of self-improvement and slowing it down helps nobody.

⛔ FAIL CLOSED ON THE CLASSIFIER, NOT ON THE EDIT. If this script cannot tell which class a path is
in, it treats it as GOVERNED. A misfiled governed edit is an annoyance; a misfiled free edit is the
whole guard failing silently.

USAGE
    python3 research/autonomy/amendment_guard.py --receipt <path> --diff-from <sha>
    python3 research/autonomy/amendment_guard.py --check-log      # amendments.jsonl integrity

EXIT CODES
    0  the change is permitted (declared where required)
    1  REFUSED — a governed path was edited by the cycle it blocked, or a declaration is missing
    2  usage error
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
LOG = HERE / "amendments.jsonl"

# Paths whose edit changes what "doing well" MEANS. Globs, matched against repo-relative paths.
# ⛔ Adding a path here is safe. REMOVING one is itself a governed act — it is how a future cycle
# would quietly widen what it may edit without declaring anything.
GOVERNED = (
    "research/autonomy/priority-weights.json",
    # ⭐⭐ THE CODE THAT APPLIES THE WEIGHTS, AND THE GATE THAT ADMITS A SCORE, ADDED 2026-09-01
    # (AUT-PD-198). The one-of-a-pair shape this repository keeps paying for: `priority-weights.json`
    # was governed and `priority.py` was not, so the NUMBERS could not be changed quietly while the
    # ARITHMETIC that consumes them could. `admissibility.py` decides whether a score is admissible
    # at all — R1-R4 — and was likewise free.
    # ⚠ FOUND BY WALKING THROUGH THE HOLE. CYC-0090 changed R4's firing condition in
    # admissibility.py and added a field in priority.py, ran this guard, and got
    # "PERMITTED — 0 governed path(s) touched". A change to what the ranker picks and to what counts
    # as a legitimate score is exactly what "a bar may not be changed by the cycle it blocked" is
    # about, and neither file was in scope.
    # ⛔ THIS IS A TIGHTENING AND ONLY A TIGHTENING. It adds two paths and removes none, so every
    # future edit here — including by the cycle that wrote this line — must be declared with its
    # self_serving_check answered. Declared in amendments.jsonl for CYC-0090-d7df5340.
    "research/autonomy/priority.py",
    "research/autonomy/admissibility.py",
    "research/autonomy/publish_bar.py",
    "research/autonomy/publication-authority.json",
    "research/autonomy/amendment_guard.py",
    "research/autonomy/health.py",
    "research/autonomy/venue-fit-weights.json",
    "CLAUDE.md",
    "AGENTS.md",
    "research/manuscripts/program/emc-autonomy-architecture.md",
    "**/test_*.py",
    "**/tests/**",
    ".claude/skills/**",
    # ⭐⭐ AND `.claude/hooks/**`, ADDED 2026-09-02 — THE ONE-OF-A-PAIR SHAPE AGAIN, IN THE SAME
    # TUPLE THAT ALREADY RECORDS IT TWICE. `.claude/skills/**` was governed and `.claude/hooks/**`
    # was not, so a SKILL — instructions a session may or may not load — could not be changed
    # quietly, while a STOP HOOK, which the harness runs whether or not anyone remembers to, could.
    # The hooks are the only bars in this repository that fire without being invoked; CLAUDE.md §7
    # calls `merge-debt-at-turn-end.sh` the enforcement of a rule that "lived in prose and was
    # measured by nothing", and §3 says the same of `escalation-debt-at-turn-end.sh`. A bar changed
    # by the session it fires at is exactly what this file exists to catch, and two sessions have
    # now declared hook edits here VOLUNTARILY (S35-DRIFTGUARD, and the merge-debt edit of
    # 2026-09-02) on the reasoning that the guard should have required it. It now does.
    # ⛔ THIS IS A TIGHTENING AND ONLY A TIGHTENING: it adds one glob and removes none, so the very
    # edit that introduced it — two hooks patched the same hour, in the session those hooks fire at
    # — is itself governed and declared in amendments.jsonl with its self_serving_check answered.
    ".claude/hooks/**",
)


def is_governed(path: str) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in GOVERNED)


def changed_paths(from_sha: str) -> list[str]:
    """Every path this cycle touched, tracked or not.

    ⛔ `git diff` ALONE NEVER LISTS UNTRACKED FILES, STAGED OR NOT (AUT-PD-156, 2026-08-29). A
    brand-new file under a GOVERNED glob — a new `**/tests/**` file, a new file that happened to be
    named `CLAUDE.md` — was invisible to this guard until `git add`-ed at least once. Measured
    2026-08-29 (CYC-0074): three new files including one matching `**/tests/**` were completely
    absent from `git diff --name-only <sha> --` and appeared only after staging. That means a quiet
    new governed file could reach a commit unrefused, caught only by the accident of the session
    remembering to `git add` before its own final check — not by the guard itself.
    So `git status --porcelain --untracked-files=all` is unioned in: it reports a brand-new file
    whether or not it has ever been staged, which is exactly the gap `git diff` cannot close.
    """
    tracked = subprocess.run(
        ["git", "diff", "--name-only", from_sha, "--"],
        capture_output=True, text=True, cwd=str(REPO),
    )
    if tracked.returncode != 0:
        # Cannot read the diff -> cannot clear the change. Fail closed.
        raise RuntimeError(f"git diff failed against {from_sha}: {tracked.stderr.strip()}")

    untracked_proc = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        capture_output=True, text=True, cwd=str(REPO),
    )
    if untracked_proc.returncode != 0:
        # Same fail-closed rule as above: cannot read the status -> cannot clear the change.
        raise RuntimeError(f"git status failed: {untracked_proc.stderr.strip()}")
    # Porcelain status lines are "XY path" (or "XY orig -> new" for a rename); an untracked file's
    # status is always "?? path". Anything else here is already covered by the tracked diff above.
    untracked = [line[3:] for line in untracked_proc.stdout.splitlines() if line.startswith("?? ")]

    out = [line for line in tracked.stdout.splitlines() if line.strip()]
    out.extend(p for p in untracked if p not in out)
    return out


def blocked_by_paths(receipt: dict) -> list[str]:
    """Which governed paths stood in this cycle's way.

    The receipt records blockages as `blocked_by[]`, each naming the path of the thing that refused
    it — a failed clause names publish_bar.py, a red health condition names health.py, a refused
    score names priority-weights.json. A receipt that records a blockage WITHOUT a path is not
    exculpatory: it is unreadable, and unreadable fails closed.
    """
    out: list[str] = []
    for entry in receipt.get("blocked_by") or []:
        if isinstance(entry, str):
            out.append(entry)
        elif isinstance(entry, dict) and entry.get("path"):
            out.append(entry["path"])
        else:
            raise RuntimeError(f"receipt has a blockage with no path: {entry!r}")
    return out


def declared(path: str, cycle_id: str) -> bool:
    """Was this edit appended to the amendment log by this cycle?"""
    if not LOG.exists():
        return False
    for line in LOG.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("path") == path and record.get("cycle_id") == cycle_id:
            # An unanswered self_serving_check is not a declaration. §10.5.
            return bool(str(record.get("self_serving_check") or "").strip())
    return False


def evaluate(receipt: dict, from_sha: str) -> dict:
    cycle_id = receipt.get("cycle_id") or "<no cycle_id>"
    blocked = set(blocked_by_paths(receipt))
    findings = []
    for path in changed_paths(from_sha):
        if not is_governed(path):
            continue
        if path in blocked:
            findings.append({
                "path": path,
                "verdict": "REFUSED",
                "why": (
                    f"cycle {cycle_id} was blocked by {path} and then edited it. A bar may not be "
                    "changed by the cycle it blocked. File this as a proposal and escalate; a "
                    "later cycle may make the same change, declared."
                ),
            })
        elif not declared(path, cycle_id):
            findings.append({
                "path": path,
                "verdict": "UNDECLARED",
                "why": (
                    f"{path} changes what 'doing well' means and is not in amendments.jsonl for "
                    f"cycle {cycle_id} with an ANSWERED self_serving_check. The loop may change "
                    "anything; it may not change anything quietly."
                ),
            })
        else:
            findings.append({"path": path, "verdict": "DECLARED", "why": "logged and permitted"})

    refused = [f for f in findings if f["verdict"] != "DECLARED"]
    return {
        "cycle_id": cycle_id,
        "from_sha": from_sha,
        "governed_paths_touched": len(findings),
        "findings": findings,
        "permitted": not refused,
    }


def check_log() -> dict:
    """The log is append-only. A rewritten history is the tell that the guard was worked around."""
    problems = []
    if not LOG.exists():
        return {"ok": True, "n": 0, "problems": ["log absent (no amendments yet)"]}
    records = []
    for i, line in enumerate(LOG.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            problems.append(f"line {i} is not valid JSON — the log must stay machine-readable")
    for record in records:
        for field in ("cycle_id", "utc", "path", "what_changed", "why", "self_serving_check"):
            if not str(record.get(field) or "").strip():
                problems.append(f"{record.get('path')!r}: {field} is empty — §10.5 requires it "
                                "ANSWERED, and an unanswered check is a red health condition")
    return {"ok": not problems, "n": len(records), "problems": problems}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--receipt", help="path to this cycle's receipt JSON")
    parser.add_argument("--diff-from", help="base sha to diff the cycle's changes against")
    parser.add_argument("--check-log", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.check_log:
        result = check_log()
        print(json.dumps(result, indent=2) if args.json else
              f"amendments.jsonl: {result['n']} record(s), "
              f"{'OK' if result['ok'] else 'PROBLEMS: ' + '; '.join(result['problems'])}")
        return 0 if result["ok"] else 1

    if not (args.receipt and args.diff_from):
        parser.error("give --receipt and --diff-from, or --check-log")

    receipt = json.loads(pathlib.Path(args.receipt).read_text())
    result = evaluate(receipt, args.diff_from)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for finding in result["findings"]:
            print(f"[{finding['verdict']:>10}] {finding['path']}\n            {finding['why']}")
        print(f"\n{'PERMITTED' if result['permitted'] else 'REFUSED'} — "
              f"{result['governed_paths_touched']} governed path(s) touched")
    return 0 if result["permitted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
