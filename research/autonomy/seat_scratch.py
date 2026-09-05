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
import datetime
import json
import os
import pathlib
import re
import sys

# The parent under which per-seat worktrees are created by `research-loop` §3's worktree contract.
DEFAULT_WORKTREE_PARENT = "/home/user/wt"

#: Where a blind seat's record lives. `publish_bar._seat_records` globs this directory, so a record
#: written anywhere else is a record the bar cannot read (`record_bar_evidence.py` header).
SEATS_DIR = str(pathlib.Path(__file__).resolve().parent / "review-seats")

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
# --open-seat-record / --close-seat-record : the record is the seat's FIRST act, not its last.
# ---------------------------------------------------------------------------------------------
#
# ⛔⛔ THE DEFECT (AUT-PROP-006, filed by CYC-0005). That cycle ran two blind seats, ACTED ON BOTH,
# and PERSISTED NEITHER. The manuscript now carries their fixes while `publish_bar`'s convergence
# clause still has nothing to read. ★ THE FAILURE IS ONE-DIRECTIONAL, WHICH IS WHY IT IS WORTH A
# TOOL: the CHANGE survives a context loss and the EVIDENCE FOR IT DOES NOT. A seat that dies on the
# way home costs its own work if it wrote first, and costs the round's whole record if it wrote last
# — the same argument the 2026-09-01 sprint charter makes at §3, from the 107-agent fan-out whose
# 40 successes had to be recovered by hand out of `journal.jsonl`.
#
# ★ SO THE ORDER IS: OPEN, LOOK, CLOSE. `--open-seat-record` writes an honest, EMPTY, `status: open`
# record before the seat reads a line of the paper. `--close-seat-record` merges the findings in and
# marks it complete. `close` REFUSES when no open record exists, so the write-first order is a
# mechanism rather than an instruction.
#
# ⛔⛔ AND THE OPEN RECORD MUST NEVER BE ABLE TO CLEAR THE BAR — THIS IS THE HALF THAT MAKES THE
# PROPOSAL SAFE RATHER THAN A NEW HOLE. An open record is honestly `blind: true` and honestly names
# the commit it is going to read, so every filter in `publish_bar._seat_records` admits it, and a
# seat that DIED would be counted as a look that found nothing. `clause_1_hardening_converged`
# therefore REFUSES on any record at the pinned commit whose `status` is `open`. That coupling is
# not optional: without it, writing the record first would turn every dead seat into a clean one.

_OPEN, _COMPLETE = "open", "complete"


def _utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def seat_record_path(seats_dir: str, paper: str, sha: str, lens: str) -> str:
    """The one filename `publish_bar` counts as an independent look.

    ⛔ THE `-seat-` SEGMENT IS LOAD-BEARING, NOT DECORATION. `publish_bar._is_seat_file` separates a
    seat from a round roll-up on this prefix and nothing else (AUT-PD-193), because the roll-up is
    filed as `{paper}-{sha}.json` and the record's own keys do not discriminate — roll-ups carry a
    `seat` key and some seat files carry `lens` instead. Build the name here, never by hand.
    """
    return os.path.join(seats_dir, f"{paper}-{sha}-seat-{lens}.json")


def open_seat_record(seats_dir: str, paper: str, sha: str, lens: str, *, document: str | None = None,
                     document_sha256: str | None = None, utc: str | None = None,
                     review_request: dict | None = None):
    """Write the empty, honest, `status: open` record. Returns (path, findings)."""
    path = seat_record_path(seats_dir, paper, sha, lens)
    now = utc or _utcnow()
    existing = None
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                existing = json.load(fh)
        except Exception as exc:
            return path, [("UNREADABLE", path,
                           f"a record already exists here and cannot be read ({type(exc).__name__}) "
                           "— refusing to overwrite evidence")]
        # ⛔ A CLOSED RECORD IS EVIDENCE AND IS NOT OVERWRITTEN. Re-opening one would erase a seat's
        # reported findings with an empty shell, which is the one thing worse than losing them:
        # it looks exactly like a seat that found nothing.
        if existing.get("status") != _OPEN:
            return path, [("CLOSED", path,
                           f"a record for {paper} seat {lens!r} at {sha[:12]} already exists and is "
                           f"not open (status={existing.get('status')!r}) — pick a distinct lens "
                           "name rather than overwriting a seat's reported findings")]
        supplied = {"review_request": review_request, "document": document,
                    "document_sha256": document_sha256}
        changed = [key for key, value in supplied.items()
                   if value is not None and value != existing.get(key)]
        if changed:
            return path, [("CONTRADICTS-THE-OPEN-RECORD", path,
                           "reopening would replace the frozen " + ", ".join(sorted(changed)))]

    record = {
        "_schema": "emc-review-seat/1",
        "status": _OPEN,
        "_why_this_exists_before_the_review_does": (
            "AUT-PROP-006. This record is written as the seat's FIRST act, so a seat that dies "
            "leaves evidence that it looked rather than nothing at all. It is EMPTY and says so: "
            "publish_bar.clause_1_hardening_converged REFUSES any round with an open record at the "
            "commit it is grading, because an unfinished look must never be counted as a clean one."
        ),
        "paper": paper,
        "pub_id": paper,
        "reviewed_commit": sha,
        "blind": True,
        "seat": lens,
        "lens": lens,
        "document": document,
        "document_sha256": document_sha256,
        "opened_utc": (existing or {}).get("opened_utc", now),
        "verdict": None,
        "central_claim": None,
        "blockers": [],
        "p1s": [],
    }
    if existing is not None:
        # Resumption keeps the original contract and any interrupted progress.
        record = existing
        record["reopened_utc"] = now
    if review_request is not None:
        record["review_request"] = review_request
    os.makedirs(seats_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2)
        fh.write("\n")
    return path, []


def close_seat_record(seats_dir: str, paper: str, sha: str, lens: str, findings: dict,
                      *, utc: str | None = None):
    """Merge a seat's reported findings into its OPEN record. Returns (path, findings-list).

    ⛔ IT REFUSES WHEN NOTHING WAS OPENED. That refusal IS the write-first rule — an instruction
    nobody can skip is worth more than a step in a contract nobody reads (CLAUDE.md: a rule whose
    trigger nobody computes is a rule that never fires).
    """
    path = seat_record_path(seats_dir, paper, sha, lens)
    if not os.path.exists(path):
        return path, [("NO-OPEN-RECORD", path,
                       "no open record to close — a seat writes its record BEFORE it reads the "
                       "paper (AUT-PROP-006), so that a seat which dies leaves evidence. Run "
                       "--open-seat-record first")]
    try:
        with open(path, "r", encoding="utf-8") as fh:
            record = json.load(fh)
    except Exception as exc:
        return path, [("UNREADABLE", path, f"cannot read the open record ({type(exc).__name__})")]
    if record.get("status") != _OPEN:
        return path, [("NOT-OPEN", path,
                       f"this record is already {record.get('status')!r} — closing it again would "
                       "overwrite a seat's reported findings")]
    # ⛔ THE SEAT MAY NOT RESTATE WHAT THE OPEN RECORD ALREADY FIXED. `reviewed_commit`, `blind` and
    # the lens are the seat's CONTRACT, written before it looked; letting the close overwrite them
    # would let a seat that read another tree relabel itself afterwards, which is exactly the drift
    # `paper-hardening` §3 pins a commit to prevent.
    frozen = ("reviewed_commit", "blind", "seat", "lens", "paper", "pub_id", "opened_utc",
              "review_request")
    contradicted = [k for k in frozen
                    if k in findings and findings[k] != record.get(k)]
    if contradicted:
        return path, [("CONTRADICTS-THE-OPEN-RECORD", path,
                       f"the close would change {', '.join(sorted(contradicted))}, which the open "
                       "record fixed before the seat read anything — a seat cannot relabel which "
                       "commit or lens it was")]
    record.update({k: v for k, v in findings.items() if k not in frozen})
    record["status"] = _COMPLETE
    record["closed_utc"] = utc or _utcnow()
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2)
        fh.write("\n")
    return path, []


def open_seat_records(seats_dir: str, paper: str, sha: str):
    """Every record at this commit still marked open — the driver's read before it believes a round.

    ⛔ AN OPEN RECORD IS A SEAT THAT DIED OR IS STILL RUNNING, AND THE TWO ARE INDISTINGUISHABLE
    FROM HERE. `paper-hardening` §7d: six killed seats were reported as "running" in three separate
    status boards, because a seat that died leaves a board that looks exactly like a seat that is
    thinking. This lists them; it does not grade them.
    """
    out = []
    try:
        names = sorted(os.listdir(seats_dir))
    except OSError as exc:
        return [("MISSING", seats_dir, f"cannot list the seats directory ({type(exc).__name__})")]
    prefix = f"{paper}-{sha}"
    for name in names:
        if not (name.startswith(prefix) and name.endswith(".json")):
            continue
        try:
            with open(os.path.join(seats_dir, name), "r", encoding="utf-8") as fh:
                record = json.load(fh)
        except Exception as exc:
            out.append(("UNREADABLE", name, f"({type(exc).__name__}) — unreadable is not empty"))
            continue
        if isinstance(record, dict) and record.get("status") == _OPEN:
            out.append(("OPEN", name,
                        f"opened {record.get('opened_utc')} and never closed — publish_bar refuses "
                        "a round with an open record, because an unfinished look is not a clean one"))
    return out


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
    # --- the seat record's lifecycle (AUT-PROP-006): open before you look, close when you report.
    ap.add_argument("--open-seat-record", action="store_true",
                    help="write this seat's EMPTY `status: open` record before it reads the paper")
    ap.add_argument("--close-seat-record", action="store_true",
                    help="merge --findings into this seat's open record and mark it complete")
    ap.add_argument("--list-open-seat-records", action="store_true",
                    help="every record at --paper/--sha still open — a seat that died or is running")
    ap.add_argument("--paper", help="publication endpoint id, e.g. PUB-ASO")
    ap.add_argument("--sha", help="the 40-character pinned commit the seat reviews")
    ap.add_argument("--lens", help="this seat's lens, e.g. regression, arithmetic, hostile-referee")
    ap.add_argument("--document", default=None, help="the manuscript path the seat reads")
    ap.add_argument("--document-sha256", default=None, help="that document's digest at --sha")
    ap.add_argument("--findings", metavar="FILE",
                    help="JSON object of the seat's reported findings, for --close-seat-record")
    ap.add_argument("--review-request", metavar="FILE",
                    help="frozen JSON scope/reason and lenses for this bounded review batch")
    ap.add_argument("--seats-dir", default=SEATS_DIR,
                    help=f"directory holding the seat records (default {SEATS_DIR})")
    args = ap.parse_args(argv)

    if args.stamp:
        sys.stdout.write(stamp(args.stamp[0], args.stamp[1]))
        return 0
    if args.open_seat_record or args.close_seat_record:
        missing = [f"--{n}" for n, v in (("paper", args.paper), ("sha", args.sha),
                                         ("lens", args.lens)) if not v]
        if missing:
            ap.error(f"a seat record needs {', '.join(missing)}")
        if args.open_seat_record:
            import bounded_review
            request = {"scope": "baseline", "lenses": [args.lens]}
            if args.review_request:
                try:
                    request = json.loads(pathlib.Path(args.review_request).read_text(encoding="utf-8"))
                except (OSError, ValueError) as exc:
                    return _report([("INVALID-REQUEST", args.review_request, str(exc))], "")
            if not isinstance(request, dict) or args.lens not in request.get("lenses", []):
                return _report([("INVALID-REQUEST", args.lens,
                                 "name this lens in the frozen request's lenses list")], "")
            decision = bounded_review.review_decision(args.paper, args.sha, request)
            if not decision["allowed"]:
                return _report([("BOUNDED-REVIEW", args.paper, decision["reason"])], "")
            path, findings = open_seat_record(
                args.seats_dir, args.paper, args.sha, args.lens,
                document=args.document, document_sha256=args.document_sha256,
                review_request=request)
            return _report(findings, f"opened {path} — now go and read the paper")
        if not args.findings:
            ap.error("--close-seat-record needs --findings FILE")
        try:
            with open(args.findings, "r", encoding="utf-8") as fh:
                reported = json.load(fh)
        except Exception as exc:
            print(f"UNREADABLE: {args.findings}\n    ({type(exc).__name__}) — nothing was closed")
            return 1
        if not isinstance(reported, dict):
            print(f"NOT-AN-OBJECT: {args.findings}\n    a seat's findings are a JSON object")
            return 1
        path, findings = close_seat_record(args.seats_dir, args.paper, args.sha, args.lens, reported)
        return _report(findings, f"closed {path}")
    if args.list_open_seat_records:
        if not (args.paper and args.sha):
            ap.error("--list-open-seat-records needs --paper and --sha")
        return _report(open_seat_records(args.seats_dir, args.paper, args.sha),
                       f"no open seat record for {args.paper} at {args.sha[:12]}")
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
