#!/usr/bin/env python3
"""The producer for the publish bar's file-backed clauses — the half that had none.

⛔⛔ WHY THIS FILE EXISTS. `publish_bar.py` is the publication permission. Three of its clauses
read a committed artifact: `hardening-state/<PUB>.json` (clause 1), `preflight-receipts/<sha>.json`
(clause 2) and `review-seats/<PUB>-<sha>.json` (clause 6). ⭐ NEITHER OF THE FIRST TWO DIRECTORIES
HAD EVER EXISTED IN ANY REF — `git log --all` over both returned empty on 2026-08-27 — and
`publish_bar.py` was the only file in the repository that so much as named them. So the bar declared
three clauses that no procedure anywhere produced, and the papers' hardening rounds recorded their
results under ad-hoc `review-seats/` filenames the bar does not read.

That is why the bar sat at 3/6 for PUB-FUSION-PARTNER across CYC-0012, CYC-0013 and CYC-0014: the
three absent clauses are exactly the three that require a PINNED COMMIT, and every one of those
cycles improved the paper's guards, which moves the tree and un-pins it again.

⛔ AND THE RECORD IS DERIVED, NEVER TYPED. Each subcommand refuses to write a record it cannot
support from evidence that already exists on disk. A producer that serialises whatever the caller
asserts would have been worse than none at all: it would put a machine-generated face on a
self-report. CLAUDE.md §4 — an absent reading is not a reading of absence, and a populated field is
not a measured one.

USAGE
    python3 research/autonomy/record_bar_evidence.py preflight --sha <sha> --log <path>
    python3 research/autonomy/record_bar_evidence.py hardening --paper PUB-X --sha <sha> --round N

EXIT CODES
    0  the record was written
    1  refused — the evidence does not support the record (nothing is written)
    2  usage error
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent

HARDENING_DIR = HERE / "hardening-state"
PREFLIGHT_DIR = HERE / "preflight-receipts"
PREFLIGHT_LOG_DIR = HERE / "preflight-logs"
SEATS_DIR = HERE / "review-seats"

#: ⛔ THE SPECIFIC BANNER, AND THE REASON IS A ONE-OF-A-PAIR TRAP. A scoped run's own closing verdict
#: advertises the flag — "PREFLIGHT_FULL=1 before publishing." — so a naive `"PREFLIGHT_FULL=1" in
#: text` test accepts a log from the very run that says it is not the publication run. Measured
#: 2026-08-27 against both logs before this constant was written.
FULL_BANNER = "== pytest (modalities: FULL, PREFLIGHT_FULL=1) =="


def _rel(path: pathlib.Path) -> str:
    """Repo-relative if we can, absolute if we cannot.

    ⚠ THE SAME TRAP `publish_bar._rel` CARRIES, AND IT BIT HERE TOO (CYC-0015). `Path.relative_to`
    RAISES for a path outside the repo, so the success message of a function whose whole job is to
    write a record crashed the moment the directories were pointed anywhere else — caught by the
    producer's own tests before it was committed, which is the argument for writing them.
    """
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def _utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _refuse(why: str) -> int:
    print(f"REFUSED: {why}", file=sys.stderr)
    return 1


def record_preflight(sha: str, log: pathlib.Path) -> int:
    """Clause 2's receipt, derived from the run's own output.

    The receipt carries the log's digest and the log is committed beside it, so `publish_bar.py`
    re-derives the exit code instead of believing this script.
    """
    try:
        text = log.read_text(errors="replace")
    except Exception as exc:
        return _refuse(f"cannot read {log} ({type(exc).__name__})")

    pinned = [ln for ln in text.splitlines() if ln.startswith("PINNED_SHA=")]
    if not pinned:
        return _refuse(f"{log} carries no PINNED_SHA= line, so the tree it ran against is unknown")
    ran_against = pinned[0].split("=", 1)[1].strip()
    if ran_against != sha:
        return _refuse(f"log ran against {ran_against}, not {sha} — a green run against a different "
                       "tree says nothing about the one being posted")
    if FULL_BANNER not in text:
        return _refuse(f"{log} carries no FULL-mode banner; a scoped run cannot clear an "
                       "outward-facing act")

    # ⛔⛔ THE LOG IS COPIED HERE, BEFORE THE PASS/FAIL CHECK — NOT INSIDE THE SUCCESS PATH BELOW.
    # Measured 2026-08-28 (AUT-PROP-018, run 33190817704): a genuine red PREFLIGHT_FULL=1 run hit
    # `_refuse()` on the EXIT= check below and returned before ever reaching the old copy site, so
    # `publish_artifacts.sh` found neither the receipt NOR the log in the tree and printed "nothing
    # to stage" — the ONE diagnostic that would explain the failure was silently discarded, exactly
    # what the caller step's own comment claims cannot happen ("a red run's log is diagnostic
    # evidence, not something to lose ... the log itself still lands on main either way"). By the
    # time this was noticed, the workflow's ephemeral runner and its /tmp were long gone; the only
    # surviving copy was the raw Actions console output, fetched back out through the API. A log
    # that has already passed the PINNED_SHA and FULL_BANNER checks above IS this exact tree's real
    # run, red or green, and belongs on main either way — only the RECEIPT (a claim of success)
    # should ever be conditional on the exit code.
    PREFLIGHT_LOG_DIR.mkdir(parents=True, exist_ok=True)
    kept = PREFLIGHT_LOG_DIR / f"{sha}.log"
    shutil.copyfile(log, kept)

    markers = [ln for ln in text.splitlines() if ln.startswith("EXIT=")]
    if not markers:
        return _refuse(f"{log} has no EXIT= marker — an unterminated log is an abandoned run. "
                       "repo-gates: never trust a backgrounded gate's reported exit code "
                       f"(log preserved at {_rel(kept)})")
    if markers[-1].strip() != "EXIT=0":
        return _refuse(f"{log} terminates in {markers[-1].strip()!r} (log preserved at {_rel(kept)})")

    PREFLIGHT_DIR.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()
    receipt = {
        "_schema": "emc-preflight-receipt/1",
        "_role": "Clause 2 of the publish bar: PREFLIGHT_FULL=1 green on the commit being posted. "
                 "The exit code here is a convenience — the clause re-derives it from `log`.",
        "sha": sha,
        "mode": "FULL",
        "exit": 0,
        "utc": _utcnow(),
        "log": _rel(kept),
        "log_sha256": digest,
    }
    path = PREFLIGHT_DIR / f"{sha}.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"wrote {_rel(path)} (+ {_rel(kept)})")
    return 0


def record_hardening(paper: str, sha: str, round_no: int, note: str | None) -> int:
    """Clause 1's record, derived from the blind seats that actually reviewed this commit.

    ⛔ IT WILL HAPPILY WRITE A NON-CONVERGED RECORD, AND THAT IS THE POINT. A round that ran no seat
    on this commit produces a record with `seats: []`, which clause 1 refuses. Turning the clause's
    verdict from UNVERIFIABLE ("I cannot see") into FAIL ("I looked, and no") is the whole gain: an
    absent reading is not a reading of absence.
    """
    seats, names = [], []
    for path in sorted(SEATS_DIR.glob(f"{paper}-{sha}*.json")):
        try:
            record = json.loads(path.read_text())
        except Exception as exc:
            return _refuse(f"{path.name} is unreadable ({type(exc).__name__}); refusing to write a "
                           "record over evidence this script could not read")
        if record.get("blind") is not True or record.get("reviewed_commit") != sha:
            continue
        seats.append(record)
        names.append(path.name)

    blockers = [item for seat in seats for item in (seat.get("blockers") or [])]
    p1s = [item for seat in seats for item in (seat.get("p1s") or [])]
    HARDENING_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "_schema": "emc-hardening-state/1",
        "_role": "Clause 1 of the publish bar. GENERATED by record_bar_evidence.py from the blind "
                 "seat records that reviewed this exact commit — never hand-written. The bar "
                 "re-derives the tallies from the same seats, so editing this file does not move "
                 "the verdict.",
        "paper": paper,
        "reviewed_commit": sha,
        "last_round": round_no,
        "utc": _utcnow(),
        "seats": names,
        "blockers": blockers,
        "p1s": p1s,
        # Informational review outcome, not permission to publish. P1 maintenance
        # findings have not blocked clause 1 since 2026-08-29. Keeping the retired
        # rule here sent an already-reviewed ASO paper back for more review.
        "converged": bool(names) and not blockers and all(
            seat.get("status") != "open"
            and isinstance(seat.get("blockers"), list)
            and isinstance(seat.get("p1s"), list)
            for seat in seats
        ),
    }
    if note:
        record["note"] = note
    path = HARDENING_DIR / f"{paper}.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")
    verdict = "converged" if record["converged"] else "NOT converged"
    print(f"wrote {_rel(path)}: round {round_no} on {sha[:12]} — {verdict} "
          f"({len(names)} blind review record(s), {len(blockers)} blocker(s), {len(p1s)} P1(s))")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    pre = sub.add_parser("preflight", help="clause 2: record a PREFLIGHT_FULL=1 run")
    pre.add_argument("--sha", required=True)
    pre.add_argument("--log", required=True, type=pathlib.Path)

    hard = sub.add_parser("hardening", help="clause 1: record a hardening round from its seats")
    hard.add_argument("--paper", required=True)
    hard.add_argument("--sha", required=True)
    hard.add_argument("--round", required=True, type=int)
    hard.add_argument("--note")

    args = parser.parse_args(argv)
    if args.command == "preflight":
        return record_preflight(args.sha, args.log)
    return record_hardening(args.paper, args.sha, args.round, args.note)


if __name__ == "__main__":
    raise SystemExit(main())
