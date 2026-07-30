#!/usr/bin/env python3
"""ONE table, one row per GPU leg: name · % complete · ETA · $/ns · running-or-stalled-and-why.

★★ WHY THIS EXISTS (trimcrae, 2026-07-29, third time of asking). The in-flight board was being ASSEMBLED BY
HAND out of a `collect` job log every time it was reported. Three consequences, all of which happened:

  * It drifted in shape between reports, so it could not be compared against the previous one at a glance —
    which is the only thing a progress board is for.
  * It carried whichever columns the writer happened to think of, and one report shipped with the ETA column
    empty ("that's so useless").
  * Every number in it was TYPED. CLAUDE.md §1 is explicit that a figure with two homes is a bug, and a
    hand-copied `%` or `$/ns` is a second home for a number the artifact already owns.

So the board is now DERIVED, from the same reads `collect` already performs, and printed by `collect` itself.
Reporting it becomes copying one block instead of rebuilding a table.

WHAT EACH COLUMN IS, and where it comes from — no column may be invented:

  name      A short human label (`T3 ternary`, `valB r2 ternary`) derived from the unit id via
            `valb_triangle_legs`, which is the ONE home for which morph is T1/T2/T3. Never hardcoded here.
  % done    committed iteration / (warmup_target + prod_target). The targets are NOT re-derived — they are
            parsed from the driver's own `[spot-driver] warmup_target=N ... prod_target=M` log line, because
            the driver computes them from OpenFE settings this process has no stack to evaluate. Reading its
            log is reading the one home; recomputing would be a second one, free to disagree.
  ETA       remaining iterations x a MEASURED s/iter, taken from openmmtools' own "Iteration a/b" +
            "Estimated completion in H:MM:SS" pair in the live log. If that pair is absent the cell is `—`
            and the WHY says so. A planning-rate guess is never substituted: an ETA nobody can trace is the
            column that got called useless.
  $/ns      `inflight_usd_per_ns.row()`, the existing one home for the rate and its multiple of basis.
  state     RUNNING / STALLED / STARTING / NO HOST, and a reason whenever it is not RUNNING.

⛔ THE STALL RULE IS CLAUDE.md §4's, NOT A NEW ONE. "A frozen phase plus an idle GPU across two consecutive
checks is a stall." So STALLED requires the committed census to have failed to advance for >= 2 consecutive
polls AND the host to be past its cold-start grace. Everything else that is merely not-yet-advancing is
STARTING with the reason that explains it — because the failure mode this file must avoid is crying stall at
a leg that is legitimately pulling a 3.35 GB image or minimising 12 replicas, which is precisely the box
`vast_idle_guard` refuses to condemn.

⚠ AND A STALLED ROW MUST CARRY A REAL REASON. trimcrae: *"it better have a good reason if it's going to be
stalled."* `state_of()` therefore REFUSES to return STALLED with an empty why — it raises instead. A stall
nobody can explain is the report that sends someone to re-derive it by hand, which is the whole problem.
"""
from __future__ import annotations

import re

try:                                     # the launcher imports this; tests import it standalone
    import valb_triangle_legs as _tlegs
except Exception:                        # noqa: BLE001 — a missing registry must not break the board
    _tlegs = None

RUNNING, STALLED, STARTING, NO_HOST = "RUNNING", "STALLED", "STARTING", "NO HOST"

# ★★ "WE COULD NOT SEE" IS NOT "IT IS NOT THERE" (measured 2026-07-29, 4:04 PM ET — a false emergency).
# All six legs rendered `NO HOST` at once and read as six simultaneous deaths. They were not: the same
# collect's gates had seen all six hosts three minutes earlier, the summary carried ZERO instance lines and
# ZERO destroy notices, and `collect` had printed `could not list instances: RuntimeError: ...`. The Vast
# instance list was UNREADABLE that pass — a throttle — and `collect` degrades an unreadable list to `mine =
# []`, which the no-host branch then correctly turned into "every enabled unit has no host".
#
# The bug is that the two render IDENTICALLY. A death demands a relaunch and a diagnosis; an unreadable list
# demands nothing but the next poll. CLAUDE.md §4 forbids the reassurance direction ("it's probably just a
# throttle"), and this constant is the other direction: the board must state which of the two it observed
# rather than picking one. `_vast_request` already retries a 403/5xx five times over ~30 s, so by the time
# this fires the read has genuinely failed, and the honest word for the host state is UNKNOWN.
UNKNOWN = "UNKNOWN"

# CLAUDE.md §4: two consecutive checks with no advance. Not tunable per lane — a per-lane threshold is how a
# stall detector gets quietly relaxed until it never fires.
STALL_POLLS = 2

_TARGETS_RE = re.compile(r"warmup_target=(\d+).*?prod_target=(\d+)", re.S)
_ITER_RE = re.compile(r"Iteration (\d+)/(\d+)")
_ETA_RE = re.compile(r"Estimated completion in (\d+):(\d+):([\d.]+)")
# The spot driver's own completed-interval measurement, e.g.
#   [timing] 40 iters in 552s = 13.8s/iter (4.35 iters/min) at iteration 1200/2000
# Only the count and the duration are captured: the `= 13.8s/iter` quotient is rounded to one decimal and
# re-deriving it from the pair is both exact and one home for the arithmetic (CLAUDE.md §1).
_DRIVER_TIMING_RE = re.compile(r"\[timing\]\s+(\d+)\s+iters?\s+in\s+([\d.]+)s")


def parse_targets(log_text):
    """(warmup_target, prod_target) from the driver's own log line, or None. PURE.

    Deliberately a PARSE and not a computation: `rbfe_spot_driver` derives these from OpenFE settings
    (equilibration_length / production_length / the two integrators' timesteps) and this process has no MD
    stack to evaluate them with. Its log line is the one home for what the run actually chose.
    """
    m = _TARGETS_RE.search(log_text or "")
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def measured_s_per_iter(log_text):
    """Seconds per iteration MEASURED by openmmtools on this very host, or None. PURE.

    It prints, for the segment it is running, `Iteration a/b` and `Estimated completion in H:MM:SS`. The
    remaining (b - a) iterations over that duration is a rate this host is actually achieving, on its actual
    card, with its actual system size — strictly better than any table lookup, and it needs no card model.

    Returns None rather than a guess when the pair is absent or degenerate; the caller renders `—`.

    ★★ THE DRIVER'S OWN `[timing]` LINE IS TRIED FIRST, AND ADDING IT FIXED A REAL BLANK COLUMN (measured
    2026-07-29, 6:47 PM ET — trimcrae: "T2 binary should have an ETA").

    WHAT HAPPENED. `calib_lo_to_lo2__binary_vhl` rendered `—` while advancing normally. Its 60-line window,
    verbatim:

        | [timing] 40 iters in 552s = 13.8s/iter (4.35 iters/min) at iteration 1200/2000
        | [barrier] committed checkpoint at iteration 1200/2000
        | --- raw tail ---
        | [barrier] committed checkpoint at iteration 1200/2000
        | INFO:  Iteration 1201/1240

    There is no `Estimated completion` line in it. openmmtools prints that estimate only once it has a few
    iterations of the CURRENT segment behind it, and this host had just crossed the 1200 checkpoint barrier
    and begun a fresh segment at 1201/1240 — so the pair this function required was legitimately incomplete
    for a minute or two at every barrier. The leg's other five siblings happened to be sampled mid-segment
    and priced fine, which is why it read as a property of that one leg.

    A MEASURED RATE WAS SITTING IN THE SAME WINDOW AND WAS BEING DISCARDED. `[timing] 40 iters in 552s` is a
    COMPLETED interval on this host, this card, this system size — strictly better evidence than a
    remaining-time estimate, and it does not vanish at a segment boundary because it describes the interval
    just finished. So it is the primary source and the openmmtools pair is the fallback, which still covers
    the case the driver line cannot: a leg early in warmup that has not yet closed its first interval.
    """
    m = None
    for m in _DRIVER_TIMING_RE.finditer(log_text or ""):
        pass                                 # keep the LAST — the most recently completed interval
    if m:
        n, secs = int(m.group(1)), float(m.group(2))
        if n > 0 and secs > 0:
            return secs / n
    it, eta = _ITER_RE.search(log_text or ""), _ETA_RE.search(log_text or "")
    if not it or not eta:
        return None
    done, total = int(it.group(1)), int(it.group(2))
    remaining = total - done
    if remaining <= 0:
        return None
    secs = int(eta.group(1)) * 3600 + int(eta.group(2)) * 60 + float(eta.group(3))
    return (secs / remaining) if secs > 0 else None


def pct_complete(phase, iteration, targets):
    """0-100, or None if it cannot be known. PURE.

    The scalar from `committed_progress` orders production above warmup; this converts that into a fraction
    of the WHOLE leg, which is the only percentage a reader can act on. A leg in warmup is not "60 % done"
    because it is at warmup 384 of 768 — it is 14 % of 2768 total iterations, and reporting the former is how
    a board promises a result hours before it can arrive.
    """
    if not targets:
        return None
    w, pr = targets
    total = w + pr
    if total <= 0:
        return None
    if phase == "production":
        return min(100.0, 100.0 * (w + iteration) / total)
    if phase == "warmup":
        return min(100.0, 100.0 * iteration / total)
    return 0.0


def eta_seconds(phase, iteration, targets, s_per_iter):
    """Seconds of wall clock remaining for the WHOLE leg, or None. PURE."""
    if not targets or not s_per_iter:
        return None
    w, pr = targets
    done = (w + iteration) if phase == "production" else (iteration if phase == "warmup" else 0)
    remaining = (w + pr) - done
    return remaining * s_per_iter if remaining > 0 else 0.0


def state_of(has_host, advanced, no_advance_polls, cold_start, why_not_running=None,
             pre_first_commit=False, host_list_readable=True, guard_shielding=False):
    """(state, why). PURE.

    ⚠ REFUSES to call a leg STALLED without a reason — see the module docstring. Raising is correct: a board
    that can render an unexplained stall will render one, and the reader then has to go and find out by hand.

    ★★ `pre_first_commit` EXISTS BECAUSE THE FIRST VERSION OF THIS BOARD GOT IT WRONG IN PRODUCTION, on the
    very first run (2026-07-29, 1:05 PM ET). `calib_lo_to_lo2__ternary_vhl` rendered:

        T2 ternary   0.0%  —   $0.00533/ns · 1.56× basis  STALLED  no committed checkpoint yet; host up
                                                                   21 min and the first warmup boundary is
                                                                   one checkpoint interval of MD after the
                                                                   image pull

    — a STALLED verdict whose own reason explains why it is NOT stalled. The cause: the poll counter was
    counting 0 -> 0 -> 0 and calling that "no advance", when a leg that has never reached its first
    checkpoint boundary has nothing to advance FROM. Its host was 21 min old and this lane's measured first
    boundary lands ~30-40 min in, so it was healthy.

    A leg that has never committed is therefore judged against the repo's existing setup grace
    (`watchdog_policy.DEFAULT_SETUP_GRACE_MIN`, 90 min — the same line `vast_idle_guard` uses to decide a
    container is WEDGED rather than slow), NOT against the poll counter and not against the 15-minute
    cold-start floor. Past that grace with still nothing committed it IS a stall, and then the reason is real.
    ★★ `host_list_readable=False` IS CHECKED BEFORE EVERYTHING ELSE, because it is a statement about the
    OBSERVATION and every other branch here is a statement about the LEG. If the provider's instance list
    could not be read, we do not know whether this leg has a host, whether it advanced, or how old its box
    is — so no other verdict in this function is entitled to be rendered. See the `UNKNOWN` constant for the
    4:04 PM ET incident that this exists to stop repeating; like STALLED, it REFUSES an empty reason, because
    "UNKNOWN" with no cause is exactly the cell that sends a reader off to re-derive the board by hand.
    """
    if not host_list_readable:
        why = (why_not_running or "").strip()
        if not why:
            raise ValueError(
                "refusing to render UNKNOWN with no reason: the caller knows WHY the instance list could not "
                "be read (the provider error it caught) and that error is the entire content of this row — "
                "without it the row is indistinguishable from the host death it exists to not be mistaken for")
        return UNKNOWN, why
    if not has_host:
        return NO_HOST, (why_not_running or "no live instance")
    if advanced:
        return RUNNING, ""
    if pre_first_commit:
        return STARTING, (why_not_running or "no first checkpoint yet, and still inside the setup grace")
    if cold_start:
        return STARTING, (why_not_running or "host is inside its cold-start grace — image pull / minimise")
    if guard_shielding:
        # ★★ THE GUARD'S `WATCHING` IS A REFUSAL TO CONDEMN, AND THE BOARD WAS OVERRULING IT WHILE QUOTING
        # IT (measured 2026-07-29, 11:12 PM ET). `valB r2 ternary` rendered:
        #
        #   valB r2 ternary  95.6%  11:58 PM  $0.00551/ns · 1.61× basis  STALLED
        #       WATCHING — quiet but alive: run.log 1 min old, GPU idle, no committed advance —
        #       consistent with a CPU-bound setup phase
        #
        # — a STALLED verdict whose own reason says the leg is alive, which is the exact shape this
        # function exists to refuse. Same defect as the `pre_first_commit` case in production, one path
        # over: the board credits only the guard's `WORKING` as advancement, so a leg the guard is
        # deliberately SHIELDING fell through to the poll counter and tripped it.
        #
        # ⚠ WATCHING IS NOT WORKING, AND THIS DELIBERATELY DOES NOT PROMOTE IT TO `RUNNING`. `WORKING` is
        # positive evidence — the census advanced, or the GPU is busy and the host is writing. `WATCHING`
        # is only the ABSENCE of evidence of death: a fresh run.log and an idle GPU, which is what a
        # CPU-bound resume looks like. STARTING is the honest cell for that — not advancing yet, and here
        # is why.
        #
        # ⚠ AND IT CANNOT MUTE A REAL STALL. WATCHING requires the log to be RECENT; once it goes silent
        # the guard returns WEDGED or CRASH_LOOP, which are destroy verdicts and are not shielding. So the
        # only thing suppressed here is a stall call on a box the guard is actively vouching for, and the
        # guard escalates on its own the moment that stops being true.
        return STARTING, (why_not_running or "the idle guard is shielding this host — quiet but alive")
    if (no_advance_polls or 0) >= STALL_POLLS:
        why = why_not_running or ""
        if not why.strip():
            raise ValueError(
                "refusing to render STALLED with no reason: %d consecutive polls without a committed "
                "advance is the CLAUDE.md §4 stall condition, and a stall the board cannot explain is the "
                "one a human has to go and diagnose by hand — which is what this board exists to prevent."
                % (no_advance_polls or 0))
        return STALLED, why
    return STARTING, (why_not_running or "no committed advance yet this poll (inside one checkpoint interval)")


def short_name(unit_id):
    """A brief label for a unit id. PURE.

    T1/T2/T3 identity comes from `valb_triangle_legs`, never from a table typed here — that module is the one
    home for which morph is which edge, and a second copy would be free to disagree the next time an edge is
    re-scoped.
    """
    uid = str(unit_id or "")
    env = "ternary" if "__ternary" in uid else ("binary" if "__binary" in uid else
                                                ("solvent" if "solvent" in uid else "?"))
    edge = None
    if _tlegs is not None:
        if uid.startswith(_tlegs.T3_KEY + "__"):
            edge = "T3"
        elif uid.startswith(_tlegs.T2_KEY + "__"):
            edge = "T2"
    if edge and "triangle" in uid:
        return f"{edge} {env}"
    m = re.search(r"_r(\d+)_", uid)
    seed = m.group(1) if m else "?"
    if "edge_reps" in uid or "edge" in uid:
        return f"valB r{seed} {env}"
    return f"{uid.split('__')[0]} {env}"


def _fmt_eta(secs, now_epoch=None, tz_offset_h=-4.0):
    """ET 12-hour, per CLAUDE.md. `—` when unknown — never a fabricated time."""
    if secs is None:
        return "—"
    import time
    now = now_epoch if now_epoch is not None else time.time()
    t = time.gmtime(now + secs + tz_offset_h * 3600.0)
    hh = t.tm_hour % 12 or 12
    ampm = "AM" if t.tm_hour < 12 else "PM"
    today = time.gmtime(now + tz_offset_h * 3600.0)
    day = "" if t.tm_mday == today.tm_mday else time.strftime(" %b %-d", t)
    return f"{hh}:{t.tm_min:02d} {ampm}{day}"


def render(rows, now_epoch=None):
    """The whole board as one block of text. PURE (given the rows)."""
    if not rows:
        return "IN-FLIGHT BOARD: no GPU legs.\n"
    head = ("%-18s %7s  %-16s %-26s %-9s %s"
            % ("LEG", "% DONE", "ETA (ET)", "$/ns", "STATE", "WHY (when not running)"))
    out = [head, "-" * len(head)]
    for r in rows:
        pct = "—" if r.get("pct") is None else ("%.1f%%" % r["pct"])
        # 16 wide, because a next-day ETA renders "1:31 AM Jul 30" and a 12-wide column pushed every later
        # cell out of alignment on the very first live board.
        out.append("%-18s %7s  %-16s %-26s %-9s %s"
                   % (r.get("name", "?")[:18], pct,
                      _fmt_eta(r.get("eta_s"), now_epoch=now_epoch),
                      r.get("usd_per_ns") or "—",
                      r.get("state", "?"),
                      r.get("why", "")))
    return "\n".join(out) + "\n"
