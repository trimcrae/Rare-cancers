#!/usr/bin/env python3
"""AUT-PD-145's entry condition 2, MEASURED — may the ceiling `MAX_UNSCORED_OPEN` be pinned yet?

⛔⛔ WHY THIS IS CODE AND NOT A SENTENCE. The condition that gates the held ceiling has been
written in prose three times (AUT-PD-145's `what`, CYC-0073's receipt, the held branch's own
docstring) and computed by hand three times, by three different seats, each re-deriving the method
from the prose: s6 read 253 ledger commits on 2026-08-28 and got 82; CYC-0073-d4ccfde4 read 120 and
got 85; this seat read 9 and got 85. Three hand derivations of one number is the
agreement-in-prose class this repository keeps paying for (AUT-PD-013's fan-out key, AUT-PROP-013's
ids, AUT-PD-037's serialization), and the remedy is always the same: put the predicate in code.

★ WHAT THE CONDITION IS, QUOTED FROM THE ROW RATHER THAN PARAPHRASED: "re-run the same series over
>= 2 h of trunk history that is entirely AFTER this commit; if it is flat or falling, pin the
ceiling at the count measured in the same commit that lands it."

⛔ THIS TOOL DECIDES NOTHING ABOUT THE BAR ITSELF. It reports ADMIT or HOLD and, on ADMIT, the
count to pin. Landing the pin is still a deliberate, mutation-tested edit of
`test_an_unscored_row_is_ranked_by_nothing.py`, recoverable UNMODIFIED from d082c01a78. ⛔ And
`MIN_WINDOW_HOURS` is not a dial to turn: shortening it is the instalment edit AUT-PD-145 has
already refused twice, and `amendment_guard.py` sees this file's own guard suite.

★ "FLAT OR FALLING" IS TESTED STEP BY STEP, NOT END TO END. A window that rises and then falls back
to where it started has the same endpoints as a flat one and is not flat — the rise is a write that
got INTO the population past R5, which is precisely the event this window exists to detect. So
every consecutive delta must be <= 0, not merely the last sample <= the first.

⛔⛔ THE SERIES IS THE TRUNK'S OWN STATES — `--first-parent` — AND NOTHING ELSE. Measured here on
the first real use of this tool, which is also how the bug was found: the plain ancestry range over
the same window returned 17 commits and oscillated 84 -> 85 -> 84 -> 85 inside four minutes, while
`--first-parent` returned 6 and was monotone. The oscillation is not noise and not a rise: a commit
that lived on a side branch carries a ledger missing every OTHER branch's rows, so its count is the
population of a state the trunk never had. Counting those commits invents rises and falls that no
writer ever made, and this window exists to detect exactly one thing — a write that reached the
population past R5. `--first-parent` is what makes the series a sequence of states the trunk was
actually in.

⚠ AND THE WINDOW IS CUT BY TIME, NOT BY ANCESTRY. `git log <sha>..origin/main` is an ancestry
range, so it happily includes commits whose committer timestamp PRECEDES <sha> — they arrived on a
side branch and merged later. Measured here: the range after R5 contained two such commits, at
00:30:35Z and 00:46:57Z against R5's 00:49:39Z, and one of them carried the +1 that made the series
look as though it had risen after R5 when it had not. A window defined as "entirely after this
commit" must therefore filter on the timestamp.

USAGE
    python3 research/autonomy/unscored_ratchet.py              # the entry check
    python3 research/autonomy/unscored_ratchet.py --series     # just the measured series
    python3 research/autonomy/unscored_ratchet.py --json

EXIT CODES
    0  ADMIT — the window is long enough and flat or falling; pin at the reported count
    1  HOLD  — the condition is not met; the reason and, if it is only time, the earliest
              UTC at which it could be
    2  the measurement itself failed (git unreadable, ledger unparseable). Never a verdict.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import admissibility as A  # noqa: E402

LEDGER_PATH = "research/autonomy/research-ledger.json"

#: The commit that landed R5 — `admissibility.refuse_population_growth`, the rule that makes the
#: series able to be flat at all. A historical fact, not a bar: the window must lie entirely after
#: it, because a series measured before R5 says nothing about whether R5 holds.
R5_COMMIT = "ee17c39a22e1a4eeedb8ab432264ad1a4ac1e8e1"

#: AUT-PD-145's entry condition 2, in hours. ⛔ NOT A DIAL. Lowering this to fit the window you
#: happen to have is the instalment edit the row refused on 2026-08-28 and again on 2026-08-29.
MIN_WINDOW_HOURS = 2.0

ADMIT = "ADMIT"
HOLD = "HOLD"


def _parse(iso: str) -> _dt.datetime:
    return _dt.datetime.fromisoformat(iso).astimezone(_dt.timezone.utc)


def _sample(row: dict) -> dict:
    return {"sha": row["sha"], "utc": row["utc"], "n": row["n"]}


def entry_verdict(samples, min_window_hours: float = MIN_WINDOW_HOURS) -> dict:
    """The whole decision, as a pure function of the measured series.

    `samples` is an iterable of `(sha, iso_utc, open_unscored_count)`. Order is not trusted — it is
    sorted by timestamp here, because a caller reading `git log` without `--reverse` would
    otherwise get a series running backwards and every delta sign inverted.
    """
    rows = sorted(({"sha": s, "utc": u, "n": int(n), "_t": _parse(u)} for s, u, n in samples),
                  key=lambda r: r["_t"])
    out = {
        "verdict": HOLD,
        "min_window_hours": min_window_hours,
        "n_samples": len(rows),
        "window_hours": 0.0,
        "first": _sample(rows[0]) if rows else None,
        "last": _sample(rows[-1]) if rows else None,
        "pin": None,
        "rises": [],
        "earliest_satisfiable_utc": None,
        "why": "",
    }
    if len(rows) < 2:
        out["why"] = (f"{len(rows)} sample(s) in the window — a series shorter than two commits "
                      "has no derivative and cannot be flat, falling or rising.")
        if rows:
            out["earliest_satisfiable_utc"] = (
                rows[0]["_t"] + _dt.timedelta(hours=min_window_hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return out

    window = (rows[-1]["_t"] - rows[0]["_t"]).total_seconds() / 3600.0
    out["window_hours"] = round(window, 3)

    rises = []
    for before, after in zip(rows, rows[1:]):
        if after["n"] > before["n"]:
            rises.append({"from_sha": before["sha"], "to_sha": after["sha"], "utc": after["utc"],
                          "delta": after["n"] - before["n"]})
    out["rises"] = rises

    if rises:
        # ⛔ A rise is reported even when the window is also too short: it is the finding that
        # matters (a write reached the population past R5), and hiding it behind "come back later"
        # would send the next cycle away to wait for a clock instead of to read a diff.
        out["why"] = (
            f"the series RISES at {len(rises)} step(s) — {rises[0]['utc']} {rises[0]['delta']:+d} — "
            "so it is neither flat nor falling. A rise after R5 means a write put a row INTO the "
            "open-unscored population, which `admissibility.refuse_population_growth` is supposed "
            "to refuse: read that commit before waiting on any clock.")
        return out

    if window < min_window_hours:
        out["earliest_satisfiable_utc"] = (
            rows[0]["_t"] + _dt.timedelta(hours=min_window_hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
        out["why"] = (
            f"flat or falling across {out['window_hours']} h and {len(rows)} commits, but the "
            f"condition asks for >= {min_window_hours} h of trunk history entirely after "
            f"{R5_COMMIT[:9]}. Nothing is wrong; the window is simply not old enough yet.")
        return out

    out["verdict"] = ADMIT
    out["pin"] = rows[-1]["n"]
    out["why"] = (
        f"flat or falling across {out['window_hours']} h and {len(rows)} trunk commits, all after "
        f"{R5_COMMIT[:9]}. Pin `MAX_UNSCORED_OPEN` at {rows[-1]['n']} — the count measured in the "
        "commit that lands it — and merge the held vacuity test from d082c01a78.")
    return out


def _git(*args: str) -> str:
    proc = subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def series(ref: str = "origin/main", after_commit: str = R5_COMMIT):
    """The open-unscored count at every trunk ledger commit strictly after `after_commit`'s time.

    ⛔ ONE DEFINITION ACROSS THE WHOLE SERIES: `admissibility.is_unscored_open` as it stands in the
    working tree, applied to each commit's committed rows. Reading each commit's own published
    `n_unscored_open` instead would measure when `priority.py --write` last ran, not the population.

    ⛔ `--first-parent`, FOR THE REASON IN THE MODULE DOCSTRING: a side-branch commit's ledger is
    missing every other branch's rows, so its count is a state the trunk was never in. Removing the
    flag invents rises and falls, and this window's whole job is to tell a real rise from none.
    """
    cut = _parse(_git("show", "-s", "--format=%cI", after_commit).strip())
    out = []
    for line in _git("log", "--format=%H %cI", "--reverse", "--first-parent",
                     f"{after_commit}..{ref}", "--", LEDGER_PATH).splitlines():
        if not line.strip():
            continue
        sha, iso = line.split()
        if _parse(iso) <= cut:
            continue  # ancestry, not time — see the module docstring
        data = json.loads(_git("show", f"{sha}:{LEDGER_PATH}"))
        entries = data.get("entries") or []
        out.append((sha, iso, sum(1 for e in entries if A.is_unscored_open(e))))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--ref", default="origin/main")
    parser.add_argument("--after", default=R5_COMMIT)
    parser.add_argument("--series", action="store_true", help="print the series and stop")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        measured = series(args.ref, args.after)
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"MEASUREMENT FAILED: {exc}", file=sys.stderr)
        return 2

    verdict = entry_verdict(measured)
    if args.json:
        print(json.dumps({"series": [{"sha": s, "utc": u, "n": n} for s, u, n in measured],
                          **verdict}, indent=2))
        return 0 if args.series or verdict["verdict"] == ADMIT else 1

    prev = None
    for sha, iso, n in measured:
        delta = "" if prev is None else f" ({n - prev:+d})"
        print(f"{sha[:9]} {iso}  open_unscored={n:4d}{delta}")
        prev = n
    if args.series:
        return 0
    print(f"\n{verdict['verdict']} — {verdict['why']}")
    if verdict["earliest_satisfiable_utc"]:
        print(f"earliest satisfiable: {verdict['earliest_satisfiable_utc']}")
    return 0 if verdict["verdict"] == ADMIT else 1


if __name__ == "__main__":
    raise SystemExit(main())
