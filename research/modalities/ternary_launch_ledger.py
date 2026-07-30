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
import contextlib
import hashlib
import json
import os
import subprocess
import tempfile
import time

LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ternary-vast-launch-attempts.json")

# Bounded so the file stays readable and its diffs stay reviewable. The interesting record is always the
# most recent one; anything older than the last few dozen attempts is history, not monitoring.
#
# ★★ THE CAP TOOK THE WHOLE TERNARY LANE DOWN FOR ~90 MINUTES (measured 2026-07-28, 4:12–6:11 AM ET).
# This module's docstring calls the file APPEND-ONLY and `test_history_is_appended_never_rewritten` pins
# that word — but the write was `(attempts + [e])[-MAX_ATTEMPTS:]`, which is not an append-only log, it is
# a RING BUFFER that silently destroys the oldest row on every write once the file is full. Evidence, all
# from `git log` on the ledger itself:
#
#   commit    UTC       n_attempts   first row kept
#   2a3c7a14  07:08     60           13:13:04Z     <- already at the cap; 9:13 AM ET seed row evicted here
#   6753b36f  08:08     60           13:16:28Z     <- evicted 13:13:04Z. Nobody noticed: not a pinned row.
#   f989a303  08:12     60           13:23:16Z     <- evicted 13:16:28Z, WHICH IS A PINNED ROW -> CI red
#   a81ef65e  10:10     61           13:16:28Z     <- the hand restore, one row OVER the cap
#   f654e104  10:11     60           13:26:36Z     <- next append: 61+1-60 = TWO rows evicted, undoing it
#
# Never a merge, a race or a stale checkout: f989a303 still CONTAINS the 08:08:09Z row written by the
# commit immediately before it, so its base was current. And replaying THIS function's old body over
# 6753b36f's exact blob reproduces f989a303's row list key-for-key — the loss is deterministic, not a race.
# Pinned as behaviour by `test_the_cap_can_never_evict_an_evidence_row`.
#
# THE CAP IS NOT THE DEFECT — a reviewable file is worth having. The defect is that eviction could reach a
# row the repo keeps as EVIDENCE. `_evict` below can now only ever age out ROUTINE rows, and says so in the
# file when it does. The cap is unchanged at 60 (a threshold, and not this fix's to move).
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
    # ★★ THE OUTCOME WHOSE ABSENCE PUT A 2.032x BOARD READING NEXT TO THE WORD `launched` (2026-07-27).
    # Between 12:08 and 12:39 PM ET the gate cleared three times and dispatched three launches. The FIRST
    # rented four hosts; the other two found every unit already running and rented NOTHING. All three were
    # filed as `launched` — "hosts were actually rented" — because the workflow derived the word from the
    # rent step's exit code, and a launch with nothing to do exits 0. The 12:39 row then carried the launch
    # job's advisory board snapshot (2.032x basis, above trimcrae's buy line) beside that word, so the
    # lane's own ledger read as "we bought at 2.032x". Nothing was bought; $0 was spent. A ledger that has
    # to be disbelieved is worse than no ledger, so the zero-rental case gets its own name.
    # ⚠ ONE FACT: not a rental attempt. WHICH units were already satisfied, and how, is in `n_requested`
    # and the receipt — putting it in the MEANING would make this the same "names two possibilities"
    # disjunction that `rented-nothing` was retired for.
    "nothing-to-launch": "no unit needed a host, so no rental was attempted and nothing was spent. Not a "
                         "hold: the market was never consulted.",
    # ★★ NOT `nothing-to-launch`, AND THE DISTINCTION IS THE WHOLE POINT (2026-07-29). The failure breaker
    # withholds a unit that has died on N hosts in a row, which drops the gate's count to zero and used to
    # land on `nothing-to-launch` — "no unit needed a host". A lane stalled on a code fault then read as a
    # lane that had FINISHED, which is CLAUDE.md §6's named prohibition. Also not a price hold: the board is
    # never consulted, so it must not run the hold clock or fire the hold warning, both of which exist for an
    # expensive market rather than a broken unit.
    # ⚠ ONE FACT. The first draft read "a code or data fault another host cannot fix" and tripped
    # test_no_outcome_names_two_possibilities — correctly, and for a deeper reason than the wording: which
    # of those it is has NOT been established, so naming both smuggled a guess about the cause into the one
    # field that must only carry what was observed. What was observed is the repetition.
    "blocked":          "units were withheld after failing on several separate hosts in a row. Nothing "
                        "rented, $0 spent; the lane is STALLED, not finished and not price-held.",
    "refused-on-price": "the board was read and NOTHING on it was within the buy line — the guard working, "
                        "nothing rented, nothing billing, next tick re-checks",
    # ★★ NOT `refused-on-price`, AND CONFLATING THEM IS THE 2026-07-29 MORNING (measured that day).
    # Between 9:25 and 10:01 AM ET the lane rented four hosts — machines 29711, 28164, 12227, 41950 — and
    # every one answered `resources_unavailable` on start while every board read was CHEAP (1.04x, 1.09x,
    # 1.34x basis, all far under the buy line). The lane had exactly two words available for "we rented
    # nothing": a price hold, which was demonstrably false, and a FAULT, which was also false — the launcher
    # worked and the provider answered cleanly. A capacity refusal is neither. It is the market having no
    # SLOT rather than no affordable slot, and its remedy is capacity (wait, or a different provider), not
    # a cheaper board. ⚠ ONE FACT: what was observed is that the hosts declined to start.
    "capacity-refused": "every host we rented answered `resources_unavailable` on start and was destroyed — "
                        "nothing is running, $0 is billing. NOT a price hold: the board was read and cheap.",
    "board-unreadable": "the market could not be read at all (provider API/auth/rate-limit) — a FAULT: we "
                        "never learned what the board cost",
    "submit-failed":    "the board was read but the provider refused the rentals — a FAULT",
    # ★★ THE WORD WHOSE ABSENCE MADE A DOCKER TIMEOUT READ AS A SCIENTIFIC REFUSAL (2026-07-27, 6:01 PM ET).
    # `task=triangle-smoke` (run 30309074338) died inside the step NAMED "ATOM-MAP GATE — the launch cannot
    # rent until the map is proven complete", and the ledger filed it as `failed`, reason "job status
    # failure". Both are true and neither is informative, so the row was read as "the gate measured the map
    # and refused" — when in fact `docker login` had timed out 15.5 s in and the gate never ran at all. The
    # four maps had measured COMPLETE three hours earlier (`valb-triangle-map-preflight.json`, 59/59 heavy
    # atoms on all four legs). A whole diagnostic turn was spent on an edge that was never in question.
    #
    # ⚠ THE TWO CASES ARE OPPOSITES AND MUST NEVER SHARE A WORD. A refusal means the map is genuinely short:
    # a RESULT about that edge, nothing rented, and re-running changes nothing — the remedy is chemistry.
    # A gate that could not RUN means we learned nothing about the map: the remedy is to retry. Filing the
    # first as the second wastes a rung; filing the second as the first is how a green edge gets abandoned.
    # This is the same rule the gate's own shell already states about the stage cache — "could not check"
    # must never read as "checked and fine" — applied to the other direction: "could not check" must never
    # read as "checked and REFUSED".
    #
    # NOT a fault, deliberately, and for the same reason `refused-on-price` is not one: the guard doing its
    # job is not the pipeline breaking. It is decision-relevant, which is a different thing, and the
    # `reason` carries which leg fell how far short.
    "map-gate-refused": "the atom-map pre-flight RAN and measured a SHORT map — the guard working on the "
                        "science, nothing rented, nothing billing. Re-running will not help; the edge "
                        "itself is the finding (see `reason`).",
    "failed":           "the launch died before the rental was attempted (see `reason`)",
}

# The outcomes that mean something is WRONG, as opposed to the market being expensive. Callers use this
# rather than re-deciding per site, so "is this a fault?" has one answer in the repo.
# `map-gate-refused` is excluded on purpose — see its entry above.
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


# =============================================================================================================
# ★★ EVIDENCE ROWS, AND WHY EVICTION MUST NOT BE ABLE TO REACH THEM
# =============================================================================================================
# A row is EVIDENCE when the repo keeps it deliberately rather than as routine telemetry: the four rows
# reconstructed from the 2026-07-27 job logs (the reason this file exists at all — see `_seeded`), and
# anything a human later marks `retain: true`. Those are exactly the rows a test may pin, and therefore
# exactly the rows whose disappearance turns a bookkeeping cap into a lane outage.
#
# ⚠ MARKING IS THE ROW'S OWN PROPERTY, NOT A LIST KEPT SOMEWHERE ELSE (CLAUDE.md §1). A second file naming
# "the rows that matter" would be a copy that drifts; the row carries its own status and the merge preserves
# it, so recovery from any historical blob restores the marking with the data.
def is_evidence(e):
    """True when this row must survive the cap. See the block above."""
    return bool(e.get("retain") or e.get("reconstructed_from_job_log"))


def key(e):
    """The identity of an attempt row: `(utc, outcome, run_url)`.

    This is the established merge rule for this file — the same triple the hand reconciliation of
    2026-07-28 used — and it is what makes two divergent copies of the ledger unionisable instead of
    conflicting. It is deliberately NOT used to deduplicate a freshly recorded event: two attempts can share
    a second, an outcome and a run (the bounded-file test records dozens that do), so a fresh append is
    always an append. Dedup belongs to `merge`, which reconciles two VERSIONS OF THE FILE.
    """
    return (e.get("utc"), e.get("outcome"), e.get("run_url"))


def merge(*attempt_lists):
    """Union rows from several copies of the ledger, keyed on `key`, ordered oldest-first by `utc`.

    First occurrence wins, so a copy that has since been enriched (a `reason` added by a later pass) does
    not lose to a barer duplicate if it is passed first. Order within one `utc` is the order supplied, so a
    lane that recorded several rows inside one second keeps their sequence.
    """
    out, seen = [], set()
    for rows in attempt_lists:
        for e in rows or []:
            k = key(e)
            if k in seen:
                continue
            seen.add(k)
            out.append(e)
    return [e for _, _, e in sorted(((e.get("utc") or "", i, e) for i, e in enumerate(out)),
                                    key=lambda t: (t[0], t[1]))]


def _evict(rows, cap=MAX_ATTEMPTS):
    """Bring `rows` down to `cap` by aging out ROUTINE rows only, oldest first. Returns `(kept, evicted)`.

    ★ AN EVIDENCE ROW IS NEVER EVICTED, EVEN IF THAT LEAVES THE FILE OVER THE CAP. The cap is a
    readability preference; the evidence is the point of the file. When the two conflict the preference
    yields — which is the whole correction of 2026-07-28, where it was the other way round and a
    bookkeeping preference deleted the record it was keeping.

    ★ AND THE NEWEST ROW IS NEVER EVICTED EITHER, for the same reason one level in: a ledger that discards
    the event it was just handed has recorded nothing at all, and would report that nothing happened. The
    old ring buffer got this right only by accident (it sliced from the tail); stated here so it survives.
    """
    rows = list(rows)
    n_drop = len(rows) - cap
    if n_drop <= 0:
        return rows, []
    last_i = len(rows) - 1
    kept, evicted = [], []
    for i, e in enumerate(rows):                     # oldest first
        if n_drop > 0 and i != last_i and not is_evidence(e):
            evicted.append(e)
            n_drop -= 1
        else:
            kept.append(e)
    return kept, evicted


def _note_evictions(d, evicted):
    """Aging out a row is a DELETION, and a deletion this file does not mention is exactly how 90 minutes
    went to diagnosing a diff nobody could account for. Every eviction leaves a running count and the
    high-water mark behind, so the loss is legible in the file rather than only in `git log`."""
    if not evicted:
        return
    prev = d.get("_aged_out") if isinstance(d.get("_aged_out"), dict) else {}
    through = max([e.get("utc") or "" for e in evicted] + [prev.get("through_utc") or ""])
    d["_aged_out"] = {
        "_what": "routine rows the MAX_ATTEMPTS cap has aged out of this file, oldest first. NEVER an "
                 "evidence row (`retain` / `reconstructed_from_job_log`) — those are exempt from the cap. "
                 "Nothing is lost: recover any row from git with "
                 "`ternary_launch_ledger.py --repair` (restores missing evidence) or `git log -p` on this "
                 "file (everything else).",
        "n_total": int(prev.get("n_total") or 0) + len(evicted),
        "through_utc": through,
    }


def _lockfile(path):
    """A stable-inode lock beside no repo file. Keyed by the ledger's absolute path so two processes
    writing the same ledger contend and two writing different ones do not. Lives in the temp dir precisely
    so it can never be `git add`ed by a lane that runs `git add -A`."""
    h = hashlib.sha256(os.path.abspath(path).encode()).hexdigest()[:16]
    return os.path.join(tempfile.gettempdir(), "ternary-launch-ledger-%s.lock" % h)


@contextlib.contextmanager
def _exclusive(path):
    """Hold an exclusive lock for the read-modify-write below.

    ★ WHY THE READ MUST HAPPEN INSIDE THIS. `record` rewrites the WHOLE file from a list it has just read.
    Two processes appending at once would each read the same base, each append their own row, and the
    second write would erase the first one's row — a real concurrent-append race, distinct from (and
    surviving) the cap defect that actually caused the 2026-07-28 outage. Locking the read as well as the
    write is what makes the second writer see the first writer's row and append after it.
    """
    try:
        import fcntl
    except ImportError:                                        # non-POSIX: degrade to unlocked, never fail
        yield
        return
    fh = open(_lockfile(path), "a+")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        finally:
            fh.close()


def _write(path, d):
    """Write via a temp file in the same directory + `os.replace`, so a crash or a concurrent reader can
    never see a half-written ledger — the file is either the old one or the new one."""
    dirname = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(dir=dirname, prefix=".ledger-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(d, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


def record(outcome, run_url=None, stage=None, reason=None, gate=None,
           n_requested=None, n_rented=None, receipt=None, path=LEDGER):
    """Append one attempt. Returns the entry written.

    `gate` is a market-gate readout dict (or a path to one); its headline numbers are COPIED so the ledger
    row explains itself without a second lookup — a reader at 3 AM should not have to reconstruct which
    snapshot was in force from commit timestamps, which is precisely what failed here.

    ⚠ EVERY `gate_*` FIELD IS A PROPERTY OF THE MARKET, NOT OF A PURCHASE. `gate_mean_usd_per_ns` is the mean
    over the n cheapest offers on the board at the instant the snapshot was taken; on a `launched` row it is
    the LAUNCH JOB's own advisory re-read, taken before the rental and never conditioned on it. It is NOT
    what we paid. What we paid is `rented[*].usd_per_ns`, read back from the live instance record — supply it
    via `receipt` (a `ternary-vast-rental-receipt.json` dict or path from `ternary_vast_launch.submit`).

    `receipt` also decides whether `launched` is even a legal word for this row; see below.
    """
    if outcome not in OUTCOMES:
        raise ValueError("unknown outcome %r; known: %s" % (outcome, ", ".join(sorted(OUTCOMES))))
    if isinstance(receipt, str):
        try:
            with open(receipt) as fh:
                receipt = json.load(fh)
        except (OSError, ValueError):
            receipt = None
    if isinstance(receipt, dict):
        if n_requested is None:
            n_requested = receipt.get("n_requested")
        if n_rented is None:
            n_rented = receipt.get("n_rented")
    # ★★ THE INVARIANT THAT MAKES THE 12:39 PM ROW IMPOSSIBLE TO WRITE AGAIN.
    # `launched` means "hosts were actually rented" — so it is a CONTRADICTION when nothing was rented, and
    # a ledger that can contradict its own vocabulary is the defect this file exists to prevent. Corrected
    # here rather than validated at the call site, because the call site is a shell script in a workflow and
    # the whole lesson of 2026-07-27 is that the shell cannot see the rental.
    #
    # Two zero-rental cases, and they must NOT collapse together. Wanting nothing is benign; wanting units
    # and getting none is not, and filing the second as the first is the exact "an outcome that names two
    # possibilities names neither" mistake that `rented-nothing` was retired for. When units WERE wanted the
    # fallback is the FAULT word, never the benign one: the launcher has its own markers for a correct
    # price refusal, so anything reaching here without them is unexplained.
    #
    # ★★ AND `nothing-to-launch` IS WRONG THE MOMENT A UNIT WAS WITHHELD (2026-07-29). `n_requested == 0`
    # has TWO causes and this line used to read only one of them. On the 13:05:24Z tick the receipt carried
    # `n_requested: 0` because one unit was genuinely running and one was withheld by the failure breaker on
    # 51 strikes — and this derivation filed the row as `nothing-to-launch`, "no unit needed a host", over a
    # lane stalled on a unit whose checkpoint sat at warmup/576. That is the SAME §6 prohibition the
    # `blocked` word was added to fix, arriving through a second door: the gate path recorded `blocked`
    # correctly, the launch path recorded `nothing-to-launch` for the identical state. The receipt now names
    # its withheld units, so the word can be derived from the fact instead of from the zero.
    n_withheld = int((receipt or {}).get("n_withheld") or 0) if isinstance(receipt, dict) else 0
    # ★★ AND THE THIRD CAUSE OF A ZERO-RENTAL LAUNCH: EVERY HOST REFUSED TO START (2026-07-29).
    # `submit` classifies each per-unit failure as `fault` / `market` / `capacity`, and only the receipt
    # carries that word out of the process — the workflow step can only see the rent step's exit code and
    # the launcher's annotations, which is exactly the blindness that filed a provider 403 as
    # `rented-nothing` in the first place. When EVERY shortfall is a capacity refusal the row is neither a
    # fault (the launcher and the provider both worked) nor a price hold (the board was cheap), so it gets
    # its own word. Any fault among them still dominates, unchanged: we cannot claim capacity refused us if
    # we never got a clean answer from the provider.
    _failed = [f for f in ((receipt or {}).get("failed") or ()) if isinstance(f, dict)] \
        if isinstance(receipt, dict) else []
    _all_capacity = bool(_failed) and all(f.get("kind") == "capacity" for f in _failed)
    if outcome == "launched" and n_rented is not None and int(n_rented) == 0:
        if n_withheld:
            outcome = "blocked"
        elif _all_capacity:
            outcome = "capacity-refused"
        else:
            outcome = "nothing-to-launch" if not n_requested else "submit-failed"
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
    # ★ THE RATE WE ARE ACTUALLY BEING BILLED, PER HOST — the only figure that answers trimcrae's question
    # ("are we paying over the line?"). Kept beside, and clearly distinct from, the `gate_*` board numbers.
    if isinstance(receipt, dict):
        rented = [r for r in (receipt.get("rented") or []) if isinstance(r, dict)]
        if rented:
            e["rented"] = [{k: r.get(k) for k in ("unit_id", "instance", "machine_id", "gpu",
                                                  "dph_total_usd_h", "usd_per_ns", "x_basis",
                                                  "over_buy_line") if r.get(k) is not None}
                           for r in rented]
            rates = [r["usd_per_ns"] for r in rented if r.get("usd_per_ns") is not None]
            if rates:
                e["rented_max_usd_per_ns"] = max(rates)
                e["rented_any_over_buy_line"] = any(r.get("over_buy_line") for r in rented)
        # Units this launch did NOT rent because they already hold a host, priced the same way. On a
        # zero-rental tick this is the whole of what the lane costs, and without it such a row says nothing
        # about money at all — which is what left a board mean standing in for a purchase.
        # ⛔ THE UNITS THIS TICK REFUSED TO BUY, NAMED IN THE ROW. Without them a `blocked` row says a number
        # and not a unit, and the whole reason `blocked` exists is that a withheld unit must be visible.
        wh = [r for r in (receipt.get("withheld") or []) if isinstance(r, dict)]
        if wh:
            e["n_withheld"] = len(wh)
            e["withheld"] = [{k: r.get(k) for k in ("unit_id", "reason", "n_attempts", "threshold")
                              if r.get(k) is not None} for r in wh]
        live = [r for r in (receipt.get("already_live") or []) if isinstance(r, dict)]
        if live:
            e["already_live"] = [{k: r.get(k) for k in ("unit_id", "instance", "gpu", "usd_per_ns",
                                                        "x_basis", "over_buy_line", "actual_status")
                                  if r.get(k) is not None} for r in live]
    if reason:
        e["reason"] = reason[:600]
    # ★★ THE READ, THE APPEND AND THE WRITE ARE ONE ATOMIC SECTION (2026-07-28).
    # `load` is called HERE, inside the lock, and never earlier — the file on disk at this instant is the
    # base, so a row another process appended a moment ago is already in it and is carried forward. The
    # append itself is a plain append (see `key` for why a fresh event is never deduplicated); the only
    # rows that can leave are routine ones the cap ages out, and that is now recorded rather than silent.
    with _exclusive(path):
        d = load(path)
        d["attempts"], evicted = _evict(d["attempts"] + [e])
        _note_evictions(d, evicted)
        _write(path, d)
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
    #
    # ★ AND A MAP REFUSAL GETS ITS OWN GLYPH, because the other two would both be lies about it (2026-07-27).
    # It is not a FAULT — nothing is broken, the guard measured the map and did its job — but it is emphatically
    # not ✅ either, and it is not ⏸ `held`: a price hold self-heals on the next tick, whereas a short map will
    # be exactly as short an hour later. Rendering it ✅ would be the same glyph as a healthy launch, which is
    # CLAUDE.md §1's rule that a row we are paying and a row the gate refused must never render alike; ⏸ would
    # promise a retry that cannot help. 🔬 = the pipeline is fine and the CHEMISTRY is the finding — go read it.
    # ⛔ AND A CAPACITY REFUSAL GETS ITS OWN GLYPH, for the same §1 reason. ⏸ says "the board was too
    # expensive, wait for a price" — which on 2026-07-29 pointed every reader at a market that was 1.04x
    # basis. 🚫 says the slot, not the price, is what we could not buy.
    mark = ("⛔ FAULT" if e["outcome"] in FAULTS else
            "🔬 MAP REFUSED" if e["outcome"] == "map-gate-refused" else
            "🚫 NO CAPACITY" if e["outcome"] == "capacity-refused" else
            "⏸ held" if e["outcome"] == "refused-on-price" else "✅")
    bits = ["[ledger] %s — last attempt %s (%s): %s" % (mark, e.get("et", "?"), e.get("utc", "?"),
                                                        e["outcome"])]
    if e.get("stage"):
        bits.append("at %s" % e["stage"])
    if e.get("n_requested") is not None:
        bits.append("%s/%s rented" % (e.get("n_rented", 0), e["n_requested"]))
    # ★ WHAT WE PAID COMES BEFORE WHAT THE BOARD COST, AND SAYS WHICH IS WHICH. The old line printed only
    # "board 2.032x basis" next to `launched`, and a reader at a glance takes that for the purchase — it is
    # not, and on the row that prompted this there was no purchase at all. Label both, paid first.
    if e.get("rented_max_usd_per_ns") is not None:
        bits.append("PAID up to $%.6f/ns%s"
                    % (e["rented_max_usd_per_ns"], " ⚠ OVER THE BUY LINE" if e.get("rented_any_over_buy_line")
                       else ""))
    elif e.get("n_rented") == 0:
        bits.append("PAID $0 (nothing rented)")
    if e.get("gate_ratio_vs_basis") is not None:
        bits.append("board(not paid) %.3fx basis" % e["gate_ratio_vs_basis"])
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


# =============================================================================================================
# ★★ RECOVERY — because "it is in git" is only true if something can actually get it back out
# =============================================================================================================
# When the cap ate the pinned row on 2026-07-28 the data was never gone: every version of this file is a blob
# in the repo. What was missing was a way to SAY that, so the restore was done by hand, at 6:10 AM, by reading
# a diff — and the hand restore was itself undone 73 seconds later because it left the file one row over the
# cap. `verify` answers "is an evidence row missing?" and `repair` puts it back by union, from history.
def evidence_from_git(path=LEDGER, max_commits=400):
    """Every EVIDENCE row this ledger has ever held, recovered from its own git history.

    Bounded by `max_commits` so it stays a few seconds even on a long-lived file. Returns `[]` rather than
    raising when git is unavailable or the file is untracked — a recovery tool that explodes outside a
    checkout is a recovery tool nobody runs.
    """
    d = os.path.dirname(os.path.abspath(path)) or "."
    base = os.path.basename(path)

    def _git(*args):
        return subprocess.run(("git", "-C", d) + args, capture_output=True, text=True, timeout=120)

    try:
        r = _git("log", "--format=%H", "-n", str(int(max_commits)), "--", base)
        if r.returncode != 0:
            return []
        shas = [s for s in r.stdout.split() if s]
    except (OSError, subprocess.SubprocessError):
        return []
    rows = []
    for sha in shas:
        try:
            blob = _git("show", "%s:./%s" % (sha, base))
        except (OSError, subprocess.SubprocessError):
            continue
        if blob.returncode != 0:
            continue
        try:
            rows.extend(json.loads(blob.stdout).get("attempts") or [])
        except (ValueError, AttributeError):
            continue
    return [e for e in merge(rows) if is_evidence(e)]


def merge_from(other, path=LEDGER):
    """Union the attempts in `other` (a ledger dict or a path to one) into `path`. Returns rows added.

    ★★ THIS IS WHAT A PUSH RACE SHOULD DO, AND IT IS IDEMPOTENT (2026-07-28). The workflow's retry loop used
    to recover from a lost push by replacing the file with origin's copy and RE-RUNNING `--record`. That
    works, but `record` stamps `utc` from the wall clock, so each retry mints a row with a different key —
    five retries that each half-succeeded could leave five rows for one launch. Unioning our already-written
    row onto origin's current file instead produces exactly one row no matter how many times it runs, and it
    preserves any OTHER local row rather than discarding it with the checkout.
    """
    if isinstance(other, str):
        try:
            with open(other) as fh:
                other = json.load(fh)
        except (OSError, ValueError):
            return []
    incoming = (other or {}).get("attempts") or []
    with _exclusive(path):
        d = load(path)
        have = {key(e) for e in d["attempts"]}
        added = [e for e in incoming if key(e) not in have]
        if added:
            d["attempts"], evicted = _evict(merge(d["attempts"], incoming))
            _note_evictions(d, evicted)
            _write(path, d)
    return added


def verify(path=LEDGER, max_commits=400):
    """Evidence rows this file has held before and is not holding now. Empty list = healthy."""
    have = {key(e) for e in load(path)["attempts"]}
    return [e for e in evidence_from_git(path, max_commits) if key(e) not in have]


def repair(path=LEDGER, max_commits=400):
    """Union any missing evidence rows back in, from history. Returns the rows restored.

    ⚠ EVIDENCE ONLY, DELIBERATELY. Unioning the FULL history back in would undo every legitimate eviction
    and grow the file without bound — the cap exists for a reason. What must never be lost is the evidence,
    and that is exactly what this restores.
    """
    missing = verify(path, max_commits)
    if not missing:
        return []
    with _exclusive(path):
        d = load(path)
        rows = merge(d["attempts"], missing)
        d["attempts"], evicted = _evict(rows)
        _note_evictions(d, evicted)
        _write(path, d)
    return missing


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--record", metavar="OUTCOME", choices=sorted(OUTCOMES))
    ap.add_argument("--stage", default=None, help="which step produced this outcome")
    ap.add_argument("--run-url", default=None)
    ap.add_argument("--reason", default=None)
    ap.add_argument("--gate", default=None, help="path to a market-gate readout JSON to copy numbers from")
    ap.add_argument("--n-requested", type=int, default=None)
    ap.add_argument("--n-rented", type=int, default=None)
    ap.add_argument("--receipt", default=None,
                    help="path to ternary-vast-rental-receipt.json — what was ACTUALLY rented and at what "
                         "rate per host. Supplying it is what lets the outcome word be derived from the "
                         "rental instead of from a step's exit code.")
    ap.add_argument("--path", default=LEDGER)
    ap.add_argument("--print-last", action="store_true")
    # ★ THE TWO COMMANDS THE 2026-07-28 OUTAGE NEEDED AND DID NOT HAVE.
    ap.add_argument("--verify", action="store_true",
                    help="exit 1 if an evidence row this file once held is missing. Read-only.")
    ap.add_argument("--repair", action="store_true",
                    help="restore missing evidence rows from git history by union, and report them.")
    ap.add_argument("--merge-from", default=None, metavar="LEDGER_JSON",
                    help="union another copy of the ledger into --path, keyed on (utc, outcome, run_url). "
                         "Idempotent — this is how a lost push race is recovered without re-recording.")
    a = ap.parse_args(argv)
    rc = 0
    if a.merge_from:
        added = merge_from(a.merge_from, a.path)
        print("[ledger] merge-from %s: %d row(s) added" % (os.path.basename(a.merge_from), len(added)))
    if a.repair:
        restored = repair(a.path)
        if restored:
            # A repair is a real finding, not a chore: something deleted a row the repo keeps on purpose.
            print("::error title=LEDGER EVIDENCE ROW RESTORED::%d evidence row(s) were missing from %s and "
                  "have been restored from git history: %s"
                  % (len(restored), os.path.basename(a.path),
                     ", ".join("%s %s" % (e.get("et"), e.get("outcome")) for e in restored)))
        else:
            print("[ledger] repair: nothing missing — every evidence row this file has held is present")
    if a.verify:
        missing = verify(a.path)
        for e in missing:
            print("::error title=LEDGER EVIDENCE ROW MISSING::%s (%s) %s — this row is marked to be kept and "
                  "is not in the committed ledger. Restore it with: python "
                  "research/modalities/ternary_launch_ledger.py --repair"
                  % (e.get("et"), e.get("utc"), e.get("outcome")))
        if missing:
            rc = 1
        else:
            print("[ledger] verify: %d evidence row(s) present, none missing"
                  % len([e for e in load(a.path)["attempts"] if is_evidence(e)]))
    if a.record:
        e = record(a.record, run_url=a.run_url, stage=a.stage, reason=a.reason, gate=a.gate,
                   n_requested=a.n_requested, n_rented=a.n_rented, receipt=a.receipt, path=a.path)
        print(json.dumps(e, indent=2))
    if a.print_last or not (a.record or a.verify or a.repair or a.merge_from):
        print(summary_line(a.path))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
