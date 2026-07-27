#!/usr/bin/env python3
"""The ternary lane's LAUNCH-ATTEMPT LEDGER — every dispatched launch and how it ended.

★★ WHY THIS FILE EXISTS (2026-07-27, and it cost a misreport to learn).

At 9:12 AM ET the market gate cleared the valB_mini replicates at 1.261x basis and, per its design,
dispatched the launch itself. The launch ran, re-priced the board 3 m 24 s later, read 2.436x, and exited 1.
It happened again at 9:23 AM. Afterwards the lane's artifacts said this:

  * `ternary-vast-market-hold.json`  -> HOLD          (the launch's own re-price OVERWROTE the gate's CLEAR)
  * `ternary-vast-watch.json`        -> 0 enabled     (nothing armed, because nothing launched)
  * `_last_launch.json` in S3        -> 06:03 UTC     (the launcher never ran, so it never wrote)

Every one of those is ALSO exactly what a plain, uneventful hold looks like. There was no artifact anywhere
saying "a launch was authorised, dispatched, and died", so the state was read as "the gate is holding" — and
reported that way. A gate that clears but cannot execute is worth nothing, and it is worth *less* than
nothing when its failure is indistinguishable from its normal state.

So: a DISTINCT, APPEND-ONLY record, written by CI at the moment of the event rather than by the launcher
(which in the failing case never runs at all), committed to the branch, and printed by `collect` so it lands
in front of the next reader without anyone having to know this file exists.

RULE 1 COMPLIANCE. This ledger stores no threshold and no cost of its own — it copies the numbers out of the
gate readout it is handed, and every one of those is derived by `ternary_vast_launch.market_gate` from
`vast-ladder-repricing.json`. It is a log, not a source of truth.
"""
import argparse
import json
import os
import time

LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ternary-vast-launch-attempts.json")

# Bounded so the file stays readable and its diffs stay reviewable. The interesting record is always the
# most recent one; anything older than the last few dozen attempts is history, not monitoring.
MAX_ATTEMPTS = 60

# The outcomes worth distinguishing. Kept a closed set so a typo cannot invent a state that no reader
# recognises — the whole point of the file is that its states are unambiguous.
# ⚠ EVERY VALUE HERE IS A SINGLE FACT. `rented-nothing` used to read "every offer above the buy line, OR
# creates failed" and that disjunction was a real defect: on 2026-07-27 at 11:10 AM ET it was the ONLY thing
# the ledger said about a launch that had died on a provider 403, so the file could not answer the one
# question it exists to answer — did the price guard work, or is the launcher broken? An outcome that names
# two possibilities names neither. Split, and never re-merged.
OUTCOMES = {
    "dispatched":       "the gate cleared and fired the launch workflow",
    "launched":         "hosts were actually rented",
    "refused-on-price": "the board was read and NOTHING on it was within the buy line — the guard working, "
                        "nothing rented, nothing billing, next tick re-checks",
    "board-unreadable": "the market could not be read at all (provider API/auth/rate-limit) — a FAULT: we "
                        "never learned what the board cost",
    "submit-failed":    "the board was read but the provider refused the rentals — a FAULT",
    "failed":           "the launch died before the rental was attempted (see `reason`)",
}

# The outcomes that mean something is WRONG, as opposed to the market being expensive. Callers use this
# rather than re-deciding per site, so "is this a fault?" has one answer in the repo.
FAULTS = {"board-unreadable", "submit-failed", "failed"}


def _et(utc_struct=None):
    """US Eastern, 12-hour, per CLAUDE.md §1 — because the reader of this ledger is trimcrae, and a UTC
    24-hour stamp is the exact thing that rule exists to stop. EDT = UTC-4.

    Done by shifting the EPOCH and re-formatting in UTC (`calendar.timegm` + `time.gmtime`), never via
    `mktime`/`localtime`, which would silently reinterpret the struct in the RUNNER's timezone and give a
    different answer on a developer box than in CI."""
    import calendar
    shifted = time.gmtime(calendar.timegm(utc_struct or time.gmtime()) - 4 * 3600)
    return "%d:%02d %s ET" % ((shifted.tm_hour % 12) or 12, shifted.tm_min,
                              "AM" if shifted.tm_hour < 12 else "PM")


def load(path=LEDGER):
    try:
        with open(path) as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        d = {}
    d.setdefault("_what", "every dispatched valB/ternary launch attempt and how it ended "
                          "(ternary_launch_ledger.py). NEWEST LAST.")
    d.setdefault("_read_this_when", "the market gate says CLEAR but no host is running. A gate that cleared "
                                    "and a launch that then died look identical in every other artifact.")
    d.setdefault("attempts", [])
    return d


def record(outcome, run_url=None, stage=None, reason=None, gate=None,
           n_requested=None, n_rented=None, path=LEDGER):
    """Append one attempt. Returns the entry written.

    `gate` is a market-gate readout dict (or a path to one); its headline numbers are COPIED so the ledger
    row explains itself without a second lookup — a reader at 3 AM should not have to reconstruct which
    snapshot was in force from commit timestamps, which is precisely what failed here."""
    if outcome not in OUTCOMES:
        raise ValueError("unknown outcome %r; known: %s" % (outcome, ", ".join(sorted(OUTCOMES))))
    if isinstance(gate, str):
        try:
            with open(gate) as fh:
                gate = json.load(fh)
        except (OSError, ValueError):
            gate = None
    now = time.gmtime()
    e = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", now), "et": _et(now),
         "outcome": outcome, "what_that_means": OUTCOMES[outcome]}
    if stage:
        e["stage"] = stage
    if run_url:
        e["run_url"] = run_url
    # ★★ `reason` IS IN THIS LIST BECAUSE LEAVING IT OUT COST AN ANSWER (2026-07-27, 11:10 AM ET).
    # The gate readout handed to that row contained, verbatim:
    #     "could not read the board (RuntimeError: vast API GET /search/asks/ -> 403 ...) —
    #      an unreadable market is not a cheap one"
    # ...which is the complete diagnosis. The ledger copied the NUMBERS and `hold`, and dropped the one
    # field that was prose — so the row recorded `gate_hold: true` with no ratio beside it and a reader had
    # to INFER "the board was unreadable" from the absence of a number. A ledger that requires inference to
    # read is the failure it was built to prevent. Copy the sentence.
    for k in ("ratio_vs_basis", "mean_usd_per_ns", "projected_usd", "max_ratio_vs_basis", "hold", "reason"):
        if isinstance(gate, dict) and k in gate:
            e["gate_" + k] = gate[k]
    if isinstance(gate, dict) and isinstance(gate.get("depth"), dict):
        e["gate_board_depth"] = gate["depth"]
    if n_requested is not None:
        e["n_requested"] = int(n_requested)
    if n_rented is not None:
        e["n_rented"] = int(n_rented)
    if reason:
        e["reason"] = reason[:600]
    d = load(path)
    d["attempts"] = (d["attempts"] + [e])[-MAX_ATTEMPTS:]
    with open(path, "w") as fh:
        json.dump(d, fh, indent=2)
        fh.write("\n")
    return e


def last(path=LEDGER):
    a = load(path)["attempts"]
    return a[-1] if a else None


def summary_line(path=LEDGER):
    """One line for `collect`'s board. A launch attempt nobody reads is the bug this file exists to fix, so
    the ledger is surfaced by the status command everyone already runs rather than by a new one."""
    e = last(path)
    if not e:
        return "[ledger] no launch attempt recorded yet"
    # The verdict word comes FIRST, before the timestamp, because this line is read at a glance in a CI log
    # and "is anything wrong?" is the only question most readers have. ⛔ = go look; ✅/⏸ = nothing to do.
    mark = "⛔ FAULT" if e["outcome"] in FAULTS else ("⏸ held" if e["outcome"] == "refused-on-price" else "✅")
    bits = ["[ledger] %s — last attempt %s (%s): %s" % (mark, e.get("et", "?"), e.get("utc", "?"),
                                                        e["outcome"])]
    if e.get("stage"):
        bits.append("at %s" % e["stage"])
    if e.get("gate_ratio_vs_basis") is not None:
        bits.append("board %.3fx basis" % e["gate_ratio_vs_basis"])
    if e.get("n_requested") is not None:
        bits.append("%s/%s rented" % (e.get("n_rented", 0), e["n_requested"]))
    # The gate's own sentence, which is where an unreadable board actually explains itself. Collapsed to one
    # line because a provider's HTML error page is multi-line and would otherwise break the summary.
    if e.get("gate_reason"):
        bits.append("| board: %s" % " ".join(str(e["gate_reason"]).split())[:220])
    if e.get("reason"):
        bits.append("— %s" % e["reason"])
    return " ".join(bits)


def is_fault(path=LEDGER):
    """True when the most recent attempt failed for a reason that needs a human. A price hold does not."""
    e = last(path)
    return bool(e) and e["outcome"] in FAULTS


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--record", metavar="OUTCOME", choices=sorted(OUTCOMES))
    ap.add_argument("--stage", default=None, help="which step produced this outcome")
    ap.add_argument("--run-url", default=None)
    ap.add_argument("--reason", default=None)
    ap.add_argument("--gate", default=None, help="path to a market-gate readout JSON to copy numbers from")
    ap.add_argument("--n-requested", type=int, default=None)
    ap.add_argument("--n-rented", type=int, default=None)
    ap.add_argument("--path", default=LEDGER)
    ap.add_argument("--print-last", action="store_true")
    a = ap.parse_args(argv)
    if a.record:
        e = record(a.record, run_url=a.run_url, stage=a.stage, reason=a.reason, gate=a.gate,
                   n_requested=a.n_requested, n_rented=a.n_rented, path=a.path)
        print(json.dumps(e, indent=2))
    if a.print_last or not a.record:
        print(summary_line(a.path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
