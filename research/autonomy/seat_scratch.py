#!/usr/bin/env python3
"""The shared scratchpad has many writers and no owner — this is the instrument that says so.

⛔⛔ THE DEFECT (AUT-PD-055, measured twice independently on 2026-08-28). Every concurrent seat is
handed the SAME scratchpad directory. A seat wrote `scratchpad/mutate.py`; a sibling wrote its own
`scratchpad/mutate.py` over it; the first seat's next run executed the sibling's file and reported
`4 caught / 4` **against a module in ANOTHER WORKTREE**, in a log that read exactly like a clean run
of its own. It was caught only because a human noticed the module name was wrong. That is CLAUDE.md
§4 verbatim — *a plausible-looking record is more dangerous than an empty one* — and the record it
produced was fabricated in substance while looking finished.

⛔ THE PRIOR FIX WAS REAL AND DID NOT REACH THIS. AUT-PD-027 (2026-08-27) put the convention in
`research-loop` §3: *write every log to `scratchpad/<seat-name>/`.* Two gaps, both measured above:
it says **logs**, and the file that collided was a **script**; and it was prose, checked by nothing,
which this repository's own history says is a rule that decays.

★ THE TWO CHECKS ARE THE TWO HALVES OF THE MEASURED INCIDENT AND THEY FAIL DIFFERENTLY.

  `--audit-root DIR`   the COLLISION SURFACE. The convention is that the scratchpad root holds
                       DIRECTORIES ONLY — one per writer — and that every file inside a writer's
                       directory carries that writer's name as its prefix. A regular file at the
                       root is a path two writers can both take, which is the overwrite; a file
                       inside a directory without the owning prefix loses its owner the moment it is
                       copied, quoted or moved, which is how a log becomes unattributable.

  `--verify-log FILE`  the PROVENANCE. A seat stamps `SEAT=` and `WORKTREE=` at the head of its log
                       (see `--stamp`), and this reads the body back for absolute paths under the
                       worktree parent that do NOT live under the declared worktree. That is the
                       fabricated half of the incident: the run touched a module belonging to a
                       sibling, and the log said so in plain text that nobody was reading.

⛔ AN UNSTAMPED LOG IS `UNSTAMPED`, NEVER `OK`. CLAUDE.md §4: an absent reading is not a reading of
absence. A log this tool cannot attribute is reported as unattributable, because the alternative —
grading a missing stamp as a pass — is the exact grading error that lets a shared file through.

⚠ WHAT THIS DOES NOT CATCH, STATED HERE RATHER THAN DISCOVERED LATER:
  * a run whose foreign paths are RELATIVE. A script that `chdir`s into a sibling worktree and
    prints `manuscripts/foo.md` leaves nothing for `--verify-log` to bind to. The measured incident
    printed an absolute module path; a near neighbour of it would not.
  * two writers colliding on a path OUTSIDE the audited root (a bare `/tmp/x`, an env-var directory,
    a home-directory file). The audit sees one tree.
  * a seat that stamps a WORKTREE it is not actually using — the stamp is a declaration, not a
    measurement, and this tool checks the log against the declaration, not against the process.
  * a seat writing deliberately into a SIBLING's directory under the sibling's prefix.
  * it is an AFTER-THE-FACT reading. It does not prevent the overwrite; it makes the overwrite
    visible before the result is believed. That is the whole of the claim.

⛔ AND IT IS DELIBERATELY NOT WIRED INTO `preflight.sh`. Preflight is offline, deterministic and
scoped to the repository; the scratchpad is per-session mutable state outside the tree, so a gate
reading it would go red or green on facts no commit contains. This is a tool a seat runs before it
reports and a driver runs before it believes a seat — named in the seat prompt by `research-loop`
§3, which owns the convention. Its own logic is asserted by
`research/autonomy/tests/test_a_seats_log_is_provably_its_own.py`, which gate 13 runs every commit.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

# The parent under which per-seat worktrees are created by `research-loop` §3's worktree contract.
DEFAULT_WORKTREE_PARENT = "/home/user/wt"

_STAMP_SCAN_LINES = 20
_SEAT_RE = re.compile(r"^SEAT=(\S+)\s*$")
_WORKTREE_RE = re.compile(r"^WORKTREE=(\S+)\s*$")


# ---------------------------------------------------------------------------------------------
# --stamp : the one line a seat puts at the head of every log it will later quote.
# ---------------------------------------------------------------------------------------------

def stamp(seat: str, worktree: str) -> str:
    """The header. Two fields, both required, both read back by `verify_log`."""
    return f"SEAT={seat}\nWORKTREE={os.path.abspath(worktree)}\n"


# ---------------------------------------------------------------------------------------------
# --audit-root : the collision surface.
# ---------------------------------------------------------------------------------------------

def audit_root(root: str):
    """Findings for a shared scratchpad root. Empty list == the convention holds.

    ⛔ A regular file directly at the root is UNOWNED: nothing about its name says which writer may
    write it, so every writer may. `mutate.py` was exactly this file.
    """
    findings = []
    if not os.path.isdir(root):
        return [("MISSING", root, "the audited root does not exist")]

    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if os.path.isdir(path):
            # ⚠ THE PREFIX IS THE DIRECTORY'S OWNER TOKEN, NOT ITS WHOLE NAME. Measured on this
            # tool's own first run: `s55-scratchpad/s55-blast-radius.log` is exactly what the seat
            # prompt asks for, and demanding the full directory name called it a violation. A gate
            # that reds on true input is worse than one that greens on false input
            # (`paper-hardening` §8b.1) — the first thing anyone does to it is loosen it.
            owner = name.split("-", 1)[0]
            for inner in sorted(os.listdir(path)):
                if os.path.isdir(os.path.join(path, inner)):
                    continue
                if not (inner.startswith(name) or inner.startswith(owner)):
                    findings.append((
                        "UNPREFIXED", os.path.join(path, inner),
                        f"inside {name}/ but carries neither {name!r} nor {owner!r} — it loses its "
                        f"owner the moment it is copied, quoted or moved",
                    ))
        else:
            findings.append((
                "UNOWNED", path,
                "a regular file at the shared root — any concurrent writer may take this same path",
            ))
    return findings


# ---------------------------------------------------------------------------------------------
# --verify-log : the provenance half.
# ---------------------------------------------------------------------------------------------

def read_stamp(text: str):
    """(seat, worktree) from the header, or (None, None) if either field is absent."""
    seat = worktree = None
    for line in text.splitlines()[:_STAMP_SCAN_LINES]:
        m = _SEAT_RE.match(line)
        if m and seat is None:
            seat = m.group(1)
        m = _WORKTREE_RE.match(line)
        if m and worktree is None:
            worktree = m.group(1)
    return seat, worktree


def foreign_paths(text: str, worktree: str, parent: str):
    """Absolute paths under `parent` that are not under `worktree`, in first-seen order.

    ⛔ The discriminating observation from the measured incident: the log NAMED a module under a
    sibling's worktree while claiming to be that seat's own run.
    """
    own = os.path.abspath(worktree).rstrip("/") + "/"
    pat = re.compile(re.escape(parent.rstrip("/")) + r"/[A-Za-z0-9._/-]+")
    seen, out = set(), []
    for hit in pat.findall(text):
        if hit.startswith(own) or hit.rstrip("/") == own.rstrip("/"):
            continue
        if hit not in seen:
            seen.add(hit)
            out.append(hit)
    return out


def verify_log(path: str, parent: str = DEFAULT_WORKTREE_PARENT, expect_seat: str | None = None):
    """Findings for one log. Empty list == the log is attributable and touched only its own tree."""
    if not os.path.isfile(path):
        return [("MISSING", path, "no such log")]
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()

    seat, worktree = read_stamp(text)
    if seat is None or worktree is None:
        return [("UNSTAMPED", path,
                 "no SEAT=/WORKTREE= header — this log cannot be attributed to the run that made it")]

    findings = []
    owner = expect_seat if expect_seat is not None else os.path.basename(os.path.dirname(os.path.abspath(path)))
    if owner and seat != owner:
        findings.append((
            "MISATTRIBUTED", path,
            f"stamped SEAT={seat} but it sits in {owner}/ — one of the two is wrong",
        ))
    for hit in foreign_paths(text, worktree, parent):
        findings.append((
            "FOREIGN", path,
            f"names {hit}, which is outside the stamped WORKTREE={worktree}",
        ))
    return findings


# ---------------------------------------------------------------------------------------------

def _report(findings, ok_msg: str) -> int:
    if not findings:
        print(f"OK — {ok_msg}")
        return 0
    for kind, where, why in findings:
        print(f"{kind}: {where}\n    {why}")
    print(f"\n{len(findings)} finding(s). See research/autonomy/seat_scratch.py's header for what "
          f"this does NOT catch — a clean run here is not proof the result is the seat's own.")
    return 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--audit-root", metavar="DIR",
                    help="audit a shared scratchpad root for paths two writers can both take")
    ap.add_argument("--verify-log", metavar="FILE",
                    help="check one log's SEAT=/WORKTREE= stamp against the paths it names")
    ap.add_argument("--stamp", nargs=2, metavar=("SEAT", "WORKTREE"),
                    help="print the two-line header a seat writes at the top of every log")
    ap.add_argument("--worktree-parent", default=DEFAULT_WORKTREE_PARENT,
                    help=f"parent of the per-seat worktrees (default {DEFAULT_WORKTREE_PARENT})")
    ap.add_argument("--seat", default=None,
                    help="expected seat id for --verify-log (default: the log's parent directory)")
    args = ap.parse_args(argv)

    if args.stamp:
        sys.stdout.write(stamp(args.stamp[0], args.stamp[1]))
        return 0
    if args.audit_root:
        return _report(audit_root(args.audit_root),
                       f"every writer under {args.audit_root} owns a directory and prefixes its files")
    if args.verify_log:
        return _report(verify_log(args.verify_log, args.worktree_parent, args.seat),
                       f"{args.verify_log} is stamped and names no path outside its own worktree")
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
