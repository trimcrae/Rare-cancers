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

# CLAUDE.md §4: two consecutive checks with no advance. Not tunable per lane — a per-lane threshold is how a
# stall detector gets quietly relaxed until it never fires.
STALL_POLLS = 2

_TARGETS_RE = re.compile(r"warmup_target=(\d+).*?prod_target=(\d+)", re.S)
_ITER_RE = re.compile(r"Iteration (\d+)/(\d+)")
_ETA_RE = re.compile(r"Estimated completion in (\d+):(\d+):([\d.]+)")


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
    """
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


def state_of(has_host, advanced, no_advance_polls, cold_start, why_not_running=None):
    """(state, why). PURE.

    ⚠ REFUSES to call a leg STALLED without a reason — see the module docstring. Raising is correct: a board
    that can render an unexplained stall will render one, and the reader then has to go and find out by hand.
    """
    if not has_host:
        return NO_HOST, (why_not_running or "no live instance")
    if advanced:
        return RUNNING, ""
    if cold_start:
        return STARTING, (why_not_running or "host is inside its cold-start grace — image pull / minimise")
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
    head = ("%-18s %7s  %-12s %-26s %-9s %s"
            % ("LEG", "% DONE", "ETA (ET)", "$/ns", "STATE", "WHY (when not running)"))
    out = [head, "-" * len(head)]
    for r in rows:
        pct = "—" if r.get("pct") is None else ("%.1f%%" % r["pct"])
        out.append("%-18s %7s  %-12s %-26s %-9s %s"
                   % (r.get("name", "?")[:18], pct,
                      _fmt_eta(r.get("eta_s"), now_epoch=now_epoch),
                      r.get("usd_per_ns") or "—",
                      r.get("state", "?"),
                      r.get("why", "")))
    return "\n".join(out) + "\n"
