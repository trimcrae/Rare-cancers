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

═══════════════════════════════════════════════════════════════════════════════════════════════════════════
★★ EVERY BILLING LANE, NOT JUST THE TERNARY ONE (2026-07-31) — AND WHERE THE MERGED BOARD IS WRITTEN
═══════════════════════════════════════════════════════════════════════════════════════════════════════════

THE GAP. Until this section existed, `inflight_board` was imported by exactly ONE caller
(`ternary_vast_launch.py`), so the board covered the ternary lane and showed NOTHING for the NR-V04
retrospective panel or the step 1 congeneric fan-out — both of which rent GPUs on their own launchers. "A row
for every leg" was therefore false, and a board that silently omits a whole billing lane is worse than no
board: it reads as complete. Same defect class as the missing NO_HOST rows above, one level up — a lane that
does not appear looks like a lane that has nothing running.

⛔ WHY THE MERGED BOARD IS **NOT** `inflight-board.md`, WHICH IS THE FIRST THING A READER WILL ASK.
`inflight-board.md` has exactly ONE writer — `gpu-ternary-fep-vast.yml task=collect` — and that step rewrites
the file WHOLESALE from the ternary lane's rows on every collect. It cannot know another lane's rows and it
does not merge. So putting all-lane rows at that path would have them silently truncated back to one lane
every few minutes, which is the exact "reads as complete" failure this section exists to end, with the added
cruelty that rows would VANISH and reappear. A merged file therefore has to live at a path no lane's collect
owns. Hence:

  research/modalities/inflight-board.md      the TERNARY lane's fragment. Unchanged, still written by that
                                             lane's collect, still that lane's one home.
  research/modalities/inflight-board.d/*.json every other lane's fragment, one file per lane, written ONLY
                                             by that lane's own launcher.
  research/modalities/inflight-board-all.md   THE BOARD. Derived from all of the above; no lane's rows live
                                             here, so nothing is lost when it is overwritten.

⚠ THE WRITE RACE IS RESOLVED BY OWNERSHIP, NOT BY LOCKING. Two writers never touch the same path: each lane
writes ONLY its own fragment. The merged file is 100 % derived from those fragments, so it is a CACHE and
never a home — whichever lane regenerates it last regenerates every lane's section from whatever fragments
exist at that moment, and a concurrent overwrite loses nothing. There is no ordering requirement, no lock,
and no lane can erase another lane's rows, because no lane ever writes another lane's rows.

⚠ A LANE THAT HAS NOT REPORTED MUST GO STALE, NOT VANISH — both halves matter. `merge_board` iterates the
LANE REGISTRY, not the fragments it happens to find, so a lane that has never published still renders a
section saying so. A lane whose fragment is older than `stale_after_min()` renders its section under a loud
banner and — for the lanes whose fragments are structured — with the ETA column dropped, because a
projection from a rate nobody has re-measured is the "promise nothing can keep" case above. The staleness
line is IMPORTED, not typed: it is `vast_idle_guard.LOG_SILENCE_MIN`, the repo's existing "this long with no
write and we stop believing it" line. A lane's fragment IS its heartbeat; the analogy is exact, so it uses
the same number rather than inventing a second one.

⚠ THE TERNARY SECTION IS INCLUDED VERBATIM, and that is deliberate. Its rows' one home is the block its own
collect rendered; re-parsing that block into cells and re-rendering them would be a second derivation, free
to disagree the next time a cell format changes. Rule 1 says point at it, so the merge transcludes it.
"""
from __future__ import annotations

import json
import os
import re
import time

try:                                     # the launcher imports this; tests import it standalone
    import valb_triangle_legs as _tlegs
except Exception:                        # noqa: BLE001 — a missing registry must not break the board
    _tlegs = None

RUNNING, STALLED, STARTING, NO_HOST = "RUNNING", "STALLED", "STARTING", "NO HOST"

# A sentinel, not `None`: `None` is a REAL value here meaning "the record was read and `is_bid`
# was absent" -> UNKNOWN tier. "Caller did not pass the argument at all" has to stay
# distinguishable from it, or every legacy call site would start printing `[tier?]` on rows where
# no tier claim is being made.
_MISSING = object()

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
# The SAME driver line carries the checkpoint interval each phase RESOLVED to — `warmup_target=1600 (ci=64)
# prod_target=2000 (ci=40)`. That is the authoritative value: `rbfe_spot_checkpoint` fixes the interval when
# the .nc is created and `effective_interval` reads it back from the committed file, so the ENV request can
# differ from what is running. Parsing it here means the measure-on-arrival guard tests the grid the leg is
# ACTUALLY on rather than the one the mode asks for.
_CKPT_IV_RE = re.compile(r"warmup_target=\d+\s*\(ci=(\d+)\).*?prod_target=\d+\s*\(ci=(\d+)\)", re.S)
_ITER_RE = re.compile(r"Iteration (\d+)/(\d+)")
_ETA_RE = re.compile(r"Estimated completion in (\d+):(\d+):([\d.]+)")
# The spot driver's own completed-interval measurement, e.g.
#   [timing] 40 iters in 552s = 13.8s/iter (4.35 iters/min) at iteration 1200/2000
# Only the count and the duration are captured: the `= 13.8s/iter` quotient is rounded to one decimal and
# re-deriving it from the pair is both exact and one home for the arithmetic (CLAUDE.md §1).
_DRIVER_TIMING_RE = re.compile(r"\[timing\]\s+(\d+)\s+iters?\s+in\s+([\d.]+)s")
# The endpoint-MD driver's own frame census, in the two shapes `nrv04_covalent_md` prints it:
#   "[nrv04-md] checkpoint @ frame 340/1000 -> S3"      /  "... at frame 340/1000 (spot-preemption safe)"
#   "[nrv04-md] production throughput: ... 1000/1000 frames, ..."
_MD_FRAME_RE = re.compile(r"frame\s+(\d+)\s*/\s*(\d+)|(\d+)\s*/\s*(\d+)\s+frames")

# ── the multi-lane registry ────────────────────────────────────────────────────────────────────────────────
# ⚠ `merge_board` iterates THIS, never the set of fragment files it happens to find. A lane that has never
# published, or whose CI has not run since the map changed, must render a section that SAYS so — a lane that
# is simply absent from the output is indistinguishable from a lane with nothing running, which is the
# "reads as complete" failure the whole multi-lane section of the docstring exists to end.
TERNARY, FANOUT, NRV04_RETRO = "ternary", "step1-fanout", "nrv04-retro"
#: The free GCP L4. A lane on a SEPARATE LEDGER (CLAUDE.md §6: trial credit is never summed into realized or
#: ladder spend), which is exactly why it must still appear here — a lane nobody can see is a lane nobody
#: notices has stopped, and this one sat idle ~15 h on 2026-07-31 because its watch entries had gone
#: `enabled: false` on landing and nothing queued new work. Its rows carry `—` for `$/ns`: no ladder dollar
#: is spent, so there is no ratio to quote, and the L4 list price is NOT a go-forward basis (pricing.md).
GCP_S1F_REP = "gcp-s1f-rep"

#: lane id -> (heading, what it rents, which launcher publishes it). Kept as data so a fourth lane is one
#: entry plus a `write_fragment` call, and cannot be added by editing the renderer.
#: ⚠ HEADINGS CARRY NO COUNTS. `NRV04_RETRO`'s used to read "18 endpoint-MD legs" and went stale the moment
#: AMENDMENT 4 reduced the panel to 16 — while the body two lines below it, derived from
#: `enumerate_units()`, correctly said "of 16". One fact, one home (§1): the count belongs to the writer
#: that derives it, never to a heading typed once and never revisited.
LANES = (
    (TERNARY, "TERNARY / RUNG 5a-KS — calibrator, triangle and valB replicate legs",
     "ternary_vast_launch.py task=collect"),
    (FANOUT, "STEP 1 FAN-OUT — the cmpd19 congeneric RBFE map (one unit = complex + solvent legs)",
     "congeneric_fanout_vast.py MONITOR=1"),
    (NRV04_RETRO, "NR-V04 RETROSPECTIVE (Arm E / R1) — endpoint-MD legs",
     "nrv04_vast_launch.py RETRO_COLLECT=1"),
    (GCP_S1F_REP, "GCP L4 — step-1 fan-out replicate (free trial credit)",
     # `tick`, not `board`: the workflow's unattended entry point changed when the lane became
     # self-feeding (2026-08-01), and this string is what a reader runs to reproduce the rows. `board`
     # still works and still writes the fragment, so nothing was broken — which is exactly why it would
     # have gone stale unnoticed. A publisher name nobody can run is the same defect as a declared
     # artifact nothing writes, one field over.
     "gcp_fanout_rep.py tick"),
)

#: The ternary lane's fragment: the file its own collect writes wholesale. NOT the merged board — see the
#: docstring for why a merged file cannot live at a path a single-lane writer owns.
TERNARY_BOARD_MD = "inflight-board.md"
#: Where every other lane drops its own fragment. One writer per file, so there is no race to resolve.
FRAGMENT_DIR = "inflight-board.d"
#: THE BOARD. Derived from the two above; no lane's rows live here, so an overwrite loses nothing.
MERGED_BOARD_MD = "inflight-board-all.md"

_TERNARY_BLOCK_RE = re.compile(r"^---- TVAST-BOARD ----$(.*?)^---- END TVAST-BOARD ----$",
                               re.S | re.M)
_TERNARY_STAMP_RE = re.compile(r"Generated\s+(\d{1,2}:\d{2}\s+[AP]M)\s+ET\s+\w{3}\s+(\w{3}\s+\d{1,2},\s+\d{4})")

#: US Eastern, the only timezone this repo reports in (CLAUDE.md §1). EDT = UTC−4.
ET_OFFSET_H = -4.0


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


def committed_intervals(log_text):
    """(warmup_ci, prod_ci) the running leg RESOLVED to, from the driver's own line, or None. PURE.

    Not the mode's configured value: the interval is fixed when the .nc is created, so a leg resumed from an
    older checkpoint runs the OLD grid whatever the env now says (`rbfe_spot_checkpoint.effective_interval`).
    A guard that tested the requested grid would mis-time every resumed leg."""
    m = _CKPT_IV_RE.search(log_text or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def interval_for_phase(log_text, phase):
    """The checkpoint interval in force for `phase` on this host, or None. PURE."""
    iv = committed_intervals(log_text)
    if not iv:
        return None
    return iv[1] if str(phase or "").startswith("prod") else iv[0]


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


def parse_md_frames(log_text):
    """(done, total) FRAMES from an endpoint-MD driver's own log, or None. PURE.

    ★ THE NR-V04 LANE'S EQUIVALENT OF `parse_targets` + the committed census in ONE line, because that lane's
    driver prints both together and its `run.log` is synced to S3 every 45 s (`nrv04_vast_launch._PIPELINE`
    tees the driver's stdout and a background loop PUTs it), so the line is durable and live:

        [nrv04-md] checkpoint @ frame 340/1000 -> S3
        [nrv04-md] RESUMED from checkpoint at frame 340/1000 (spot-preemption safe)
        [nrv04-md] production throughput: 118.4 ns/day (5.0000 ns in 3650.2s active, 1000/1000 frames, ...)

    Both shapes are read and the LAST match wins — the most recent statement the driver made about itself.
    Returning None rather than a frame count guessed from wall clock is the same refusal `parse_targets`
    makes: these legs are plain endpoint MD, and nothing else in the object store knows how many frames they
    were asked for.
    """
    m = None
    for m in _MD_FRAME_RE.finditer(log_text or ""):
        pass                                  # keep the LAST — the driver's most recent statement
    if not m:
        return None
    done, total = (m.group(1), m.group(2)) if m.group(1) is not None else (m.group(3), m.group(4))
    done, total = int(done), int(total)
    return (done, total) if total > 0 else None


def sequential_done(stages, stage_key, done_in_stage):
    """Units of work finished across an ORDERED sequence of stages, or None if the stage is not one of them.

    PURE, and the one home for the arithmetic every lane's `% done` needs. A lane's progress scalar always
    says "I am `done_in_stage` into stage X of an ordered list"; the only percentage a reader can act on is
    against the WHOLE unit, so the prior stages' targets are added in. `stages` is [(key, target), ...] in
    execution order — ternary passes [("warmup", w), ("production", p)], the fan-out passes its four
    (leg, phase) pairs, an endpoint-MD leg passes one.
    """
    prior = 0
    for key, target in (stages or ()):
        if key == stage_key:
            return prior + max(0, int(done_in_stage or 0))
        prior += max(0, int(target or 0))
    return None


def sequential_pct(stages, stage_key, done_in_stage):
    """0-100 of the WHOLE unit, or None if the denominator is unknown. PURE.

    A stage this sequence does not contain (a leg that has not started, a phase marker we do not recognise)
    is 0 %, never None: "no work done yet" is knowable, whereas "no targets" is not, and collapsing the two
    would let a board render `—` for a leg that is simply at the beginning.
    """
    total = sum(max(0, int(t or 0)) for _, t in (stages or ()))
    if not stages or total <= 0:
        return None
    done = sequential_done(stages, stage_key, done_in_stage)
    if done is None:
        return 0.0
    return min(100.0, 100.0 * done / total)


def sequential_remaining(stages, stage_key, done_in_stage):
    """Units of work left in the WHOLE unit, or None if the denominator is unknown. PURE."""
    total = sum(max(0, int(t or 0)) for _, t in (stages or ()))
    if not stages or total <= 0:
        return None
    done = sequential_done(stages, stage_key, done_in_stage)
    return max(0.0, float(total - (done or 0)))


def pct_complete(phase, iteration, targets):
    """0-100, or None if it cannot be known. PURE.

    The scalar from `committed_progress` orders production above warmup; this converts that into a fraction
    of the WHOLE leg, which is the only percentage a reader can act on. A leg in warmup is not "60 % done"
    because it is at warmup 384 of 768 — it is 14 % of 2768 total iterations, and reporting the former is how
    a board promises a result hours before it can arrive.

    Delegates to `sequential_pct` so the ternary lane and every other lane share ONE implementation of the
    arithmetic (CLAUDE.md rule 1); this function is the ternary lane's two-stage spelling of it.
    """
    if not targets:
        return None
    w, pr = targets
    return sequential_pct((("warmup", w), ("production", pr)), phase, iteration)


def eta_seconds(phase, iteration, targets, s_per_iter):
    """Seconds of wall clock remaining for the WHOLE leg, or None. PURE."""
    if not targets or not s_per_iter:
        return None
    w, pr = targets
    rem = sequential_remaining((("warmup", w), ("production", pr)), phase, iteration)
    return None if rem is None else rem * s_per_iter


def advance_counters(prev_state, census):
    """The board's own poll bookkeeping for the CLAUDE.md §4 two-consecutive-checks rule. PURE.

    `census` and the returned state are {unit: {"stage": str, "iteration": int|None, "utc": str}}; the return
    adds `no_advance_polls`. Two things it deliberately does NOT do:

    ⚠ AN UNREADABLE READING IS NEVER A NON-ADVANCE. `iteration is None` means the object store did not
    answer, and counting that as "did not move" manufactures a stall out of a network blip — the identical
    rule `congeneric_fanout_vast.committed_progress` states for its negative scalar. The previous entry is
    CARRIED unchanged, so the next real reading still compares against the last real one.

    ⚠ A STAGE CHANGE RESETS THE COUNTER. Iteration numbers restart at a leg or phase boundary, so comparing
    across one would read a fresh warmup as a regression and then as a stall.

    ★ WHY THIS IS THE BOARD'S OWN STATE AND NOT A LANE'S PROGRESS FILE. `congeneric_fanout_vast._idle_evidence`
    documents the trap: the fan-out's monitor OVERWRITES `_progress_prev.json` with the current census as its
    last act, so anything else reading that file compares a pass against itself and every leg looks frozen.
    One owner, one file — the board keeps its own.
    """
    out = {}
    for unit, cur in (census or {}).items():
        prev = (prev_state or {}).get(unit) or {}
        it = cur.get("iteration")
        if it is None:
            out[unit] = dict(prev) if prev else {**cur, "no_advance_polls": 0}
            continue
        n = int(prev.get("no_advance_polls") or 0)
        if prev.get("iteration") is None or prev.get("stage") != cur.get("stage") or it > prev["iteration"]:
            n = 0
        else:
            n += 1
        out[unit] = {**cur, "no_advance_polls": n}
    return out


def advanced_since_last_poll(prev_entry, cur_entry):
    """Did this unit's own durable census MOVE since the previous board poll? PURE.

    ⚠ A FIRST CENSUS IS NOT EVIDENCE OF ADVANCE. With no previous reading there is nothing to have moved
    from, so this is False and the caller's row renders STARTING with a reason — never RUNNING, which would
    be the board asserting a box is working on the strength of having looked at it once.

    ⚠ AND AN UNREADABLE READING IS NOT A REGRESSION. `iteration is None` means the store did not answer;
    `advance_counters` carries the counter for exactly that case, and this returns False without claiming
    anything either way.
    """
    if not prev_entry or not cur_entry:
        return False
    a, b = prev_entry.get("iteration"), cur_entry.get("iteration")
    if a is None or b is None:
        return False
    return cur_entry.get("stage") != prev_entry.get("stage") or b > a


def gpu_is_busy(gpu_util):
    """Is this GPU reading POSITIVE evidence of work? IMPORTED from the guard, never typed. PURE.

    ★★ WHY THE BOARD NEEDS THIS AT ALL (the ternary lane's 1:43 PM ET lesson, 2026-07-29, in this lane's
    shape). A committed census ticks at CHECKPOINT BOUNDARIES — the fan-out commits every 20 warmup / 40
    production iterations, roughly every 5-10 minutes — while a supervising agent may poll every 3. So "did
    not advance since the last poll" is the ORDINARY state of a perfectly healthy leg, and a stall rule
    keyed on that alone will cry stall at legs that are working. The guard's own positive-evidence rule is
    the fix and it is already the authority this board defers to elsewhere: `vast_idle_guard.GPU_BUSY_PCT`,
    at or above which the GPU is doing work.

    ⚠ ONE DIRECTION ONLY, exactly as the guard uses it. A busy GPU SAVES a row from the poll counter; a low
    or absent reading never condemns one — `None` means "the host is not telling us", which is a different
    fact from "the GPU is idle" and only the second would be evidence of anything.
    """
    if gpu_util is None:
        return False
    try:
        import vast_idle_guard as _vig
        busy = float(_vig.GPU_BUSY_PCT)
    except Exception:  # noqa: BLE001 — keep this module importable with no lane code present
        busy = float(os.environ.get("VAST_IDLE_GPU_BUSY_PCT") or "5")
    try:
        return float(gpu_util) >= busy
    except (TypeError, ValueError):
        return False


def measured_rate_per_h(prev_entry, cur_entry):
    """Progress-scalar units per HOUR, MEASURED between two board polls of the same stage, or None. PURE.

    ★ THIS IS A MEASUREMENT, NOT A PLANNING RATE, and that is the whole reason the ETA column is allowed to
    exist. Both readings come from OUR OWN durable object store, on this host, for this workload — the same
    argument `congeneric_fanout_vast._iter_rate` makes for preferring it over `gpu_util` or a card constant.
    When it cannot be computed the caller renders `—`; substituting a table lookup is what made the ETA
    column "so useless" the first time.
    """
    if not prev_entry or not cur_entry:
        return None
    if prev_entry.get("stage") != cur_entry.get("stage"):
        return None
    a, b = prev_entry.get("iteration"), cur_entry.get("iteration")
    if a is None or b is None or b <= a:
        return None
    hours = _hours_between(prev_entry.get("utc"), cur_entry.get("utc"))
    if not hours or hours <= 0:
        return None
    return (b - a) / hours


def _hours_between(utc_a, utc_b):
    """Hours between two `%Y-%m-%dT%H:%M:%SZ` stamps, or None if either is unusable. PURE."""
    try:
        import calendar
        ta = calendar.timegm(time.strptime(str(utc_a), "%Y-%m-%dT%H:%M:%SZ"))
        tb = calendar.timegm(time.strptime(str(utc_b), "%Y-%m-%dT%H:%M:%SZ"))
    except (TypeError, ValueError):
        return None
    return (tb - ta) / 3600.0


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
    # ★★ THE FALLBACK MUST CARRY WHAT DISTINGUISHES THE UNITS, AND IT DID NOT (2026-07-31).
    # It returned `f"{uid.split('__')[0]} {env}"`, so all FOUR RUNG 5a-KS units — which differ only in the
    # paralogue (`nr4a1` vs `nr4a3`) and the replicate (`r0` vs `r1`) — rendered as the single string
    # `5aks_d0_to_d ternary`. Both discriminators were dropped, on a lane where the whole experiment IS the
    # nr4a1/nr4a3 comparison.
    #
    # The cost was real and it was paid the same day: reading that board, two legs the idle guard had
    # condemned were reported as "both on the nr4a3 arm", which made an arm-specific hang the leading
    # hypothesis. The machine-written `5aks-market-hold.json` snapshots say the two were `nr4a1_r1` and
    # `nr4a3_r0` — one from EACH arm — and that host losses ran 7 to 7 across the arms. An hour of diagnosis
    # went at a pattern the renderer had invented.
    #
    # (`render()` also truncated the column to 18 characters, which collapsed them a second time. Both had to
    # go; a shortener that drops the discriminator cannot be rescued by a wider column.)
    m2 = re.search(r"__(?:ternary|binary|solvent)_([A-Za-z0-9]+)_r(\d+)", uid)
    if m2:
        return f"{uid.split('__')[0]} {env} {m2.group(1)} r{m2.group(2)}"
    if seed != "?":
        return f"{uid.split('__')[0]} {env} r{seed}"
    return f"{uid.split('__')[0]} {env}"


def _fmt_eta_at(epoch, now_epoch=None, tz_offset_h=ET_OFFSET_H):
    """An ABSOLUTE completion epoch as ET 12-hour, per CLAUDE.md. `—` when unknown — never fabricated.

    Absolute rather than relative because a row read out of a FRAGMENT was computed at some earlier poll: a
    "seconds remaining" recorded then would silently re-project itself forward every time the board is
    merged, which is a promise nobody measured. The epoch a lane predicted is a fact about that lane's poll
    and stays true whatever time it is read.
    """
    if epoch is None:
        return "—"
    now = now_epoch if now_epoch is not None else time.time()
    t = time.gmtime(epoch + tz_offset_h * 3600.0)
    hh = t.tm_hour % 12 or 12
    ampm = "AM" if t.tm_hour < 12 else "PM"
    today = time.gmtime(now + tz_offset_h * 3600.0)
    day = "" if t.tm_mday == today.tm_mday else time.strftime(" %b %-d", t)
    return f"{hh}:{t.tm_min:02d} {ampm}{day}"


def _fmt_eta(secs, now_epoch=None, tz_offset_h=ET_OFFSET_H):
    """ET 12-hour, per CLAUDE.md. `—` when unknown — never a fabricated time."""
    if secs is None:
        return "—"
    now = now_epoch if now_epoch is not None else time.time()
    return _fmt_eta_at(now + secs, now_epoch=now, tz_offset_h=tz_offset_h)


def et_stamp(epoch=None, tz_offset_h=ET_OFFSET_H):
    """`7:04 AM ET Fri Jul 31, 2026` — the one time format this repo reports in (CLAUDE.md §1)."""
    t = time.gmtime((time.time() if epoch is None else epoch) + tz_offset_h * 3600.0)
    hh = t.tm_hour % 12 or 12
    ampm = "AM" if t.tm_hour < 12 else "PM"
    return "%d:%02d %s ET %s" % (hh, t.tm_min, ampm, time.strftime("%a %b %-d, %Y", t))


def render(rows, now_epoch=None):
    """The whole board as one block of text. PURE (given the rows).

    A row states its ETA either as `eta_s` (seconds from now — the in-process caller that just measured a
    rate) or as `eta_epoch` (an absolute completion time — a row read back out of a fragment). One formatter
    serves both; see `_fmt_eta_at` for why a stored ETA must not be relative.
    """
    if not rows:
        return "IN-FLIGHT BOARD: no GPU legs.\n"
    # ★ ETA IS THE SECOND COLUMN (trimcrae, 2026-07-31). It is the cell a reader acts on — "when does this
    # land" is the question a progress board exists to answer — so it sits beside the name rather than
    # third behind a percentage. % DONE follows, because it is how you SANITY-CHECK the ETA, not a
    # substitute for it.
    #
    # ⚠ AND THERE IS DELIBERATELY NO "REFUSED" COLUMN. A refusal is not a different quantity from a
    # purchase, it is the same $/ns with a different disposition, and `inflight_usd_per_ns.row()` already
    # renders that distinction inside the cell (`⚠ PAYING OVER THE …× LINE` vs `⛔ REFUSED at … — $0
    # spent`). A separate column would be a second home for a fact that already has one, and the two would
    # be free to disagree — which is exactly how a row we declined came to read like a row we were buying.
    # The $/ns column is sized FROM THE ROWS, not to a constant. A refusal renders `⛔ REFUSED at
    # $0.007282/ns · 2.13× basis — $0 spent`, roughly twice the width of a paying cell, and against a fixed
    # 26 it overflowed and pushed STATE and WHY out of alignment — making the refused row the least legible
    # one on the board, which is precisely backwards. A widest-cell width self-corrects as the strings
    # change and cannot drift out of step with them.
    w = max([len("$/ns")] + [len(str(r.get("usd_per_ns") or "—")) for r in rows])
    # ★★ THE LEG COLUMN IS SIZED FROM THE ROWS TOO, AND FOR A HARDER REASON THAN ALIGNMENT (2026-07-31).
    # It was a fixed 18 with a `[:18]` truncation, and RUNG 5a-KS's four unit ids share a 20-character prefix:
    # `5aks_d0_to_d__ternary_nr4a1_r0…` / `…nr4a3_r0…` / `…nr4a3_r1…`. So all four rows rendered as the
    # identical string `5aks_d0_to_d terna` — the arm and the replicate, the ONLY things that tell the four
    # legs apart, were exactly what the truncation removed.
    #
    # That is not cosmetic and it did real damage the same day: reading that board, two condemned legs were
    # reported as "both on the nr4a3 arm", which made an arm-specific hang the leading hypothesis. The
    # committed `5aks-market-hold.json` snapshots — machine-written, untruncated — say the two were
    # `nr4a1_r1` and `nr4a3_r0`, one from EACH arm, and that host losses ran 7 to 7 across the arms all day.
    # An hour of diagnosis was aimed at a pattern that the board had manufactured.
    #
    # Same principle as CLAUDE.md §1's "a row we are paying and a row the gate refused must never render
    # alike": rows that are DIFFERENT must not render the SAME. A width taken from the actual names cannot
    # collide, and it self-corrects when the next mode's ids are longer still.
    # Minimum 18 = the OLD fixed width, kept so short-named lanes render exactly as before; the max is
    # what removes the truncation. Never below 18, or a one-word name collapses the header spacing the
    # column separator is parsed from.
    lw = max([18] + [len(str(r.get("name") or "?")) for r in rows])
    fmt = "%-" + str(lw) + "s %-16s %7s  %-" + str(w) + "s %-9s %s"
    head = fmt % ("LEG", "ETA (ET)", "% DONE", "$/ns", "STATE", "WHY (when not running)")
    out = [head, "-" * len(head)]
    for r in rows:
        pct = "—" if r.get("pct") is None else ("%.1f%%" % r["pct"])
        # ★★ A PERCENTAGE OF THE WRONG PROTOCOL MUST NOT RENDER AS A PERCENTAGE (2026-07-31).
        # The NR-V04 retro board showed SIXTEEN rows at `100.0%` for legs that are not landed legs at all:
        # their census came from a `mode=smoke` run.log, which reaches `frame 5/5` in ~4-20 s, so the
        # arithmetic was right and the DENOMINATOR was a different experiment. A banner above the table said
        # so, but `100.0%` is exactly the cell that gets quoted out of the table it stands in — and this repo
        # has already had one frozen gate come within a single leg of emitting a verdict off smoke records
        # (CLAUDE.md §4b). So a row whose progress is measured against something other than the production
        # protocol renders that LABEL in the cell instead of a number: `smoke`, never `100.0%`.
        # The lane decides — it is the only thing that knows which protocol produced the census — and the
        # renderer merely refuses to print a bare percentage without one. Same shape as the `$/ns` cell's
        # refusal to convert an unbenched workload: an UNKNOWN is visibly absent, a substitution is not.
        if r.get("pct_of"):
            pct = str(r["pct_of"])[:7]
        eta = (_fmt_eta(r.get("eta_s"), now_epoch=now_epoch) if r.get("eta_s") is not None
               else _fmt_eta_at(r.get("eta_epoch"), now_epoch=now_epoch))
        # 16 wide, because a next-day ETA renders "1:31 AM Jul 30" and a 12-wide column pushed every later
        # cell out of alignment on the very first live board.
        out.append(fmt
                   % (r.get("name", "?"), eta, pct,
                      r.get("usd_per_ns") or "—",
                      r.get("state", "?"),
                      r.get("why", "")))
    return "\n".join(out) + "\n"


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# THE $/ns CELL — one home for it, and one honest way to decline to compute it
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

def planning_usd_per_ref_gpu_h(root=None):
    """The planning $/reference-GPU-hour, READ from the ladder repricing artifact — never typed.

    CLAUDE.md §1: the ladder repricing JSON is that number's one home. None if unreadable, and the caller
    then renders `—` rather than a rate nobody can trace.
    """
    # ⚠ THE MODULE'S OWN DIRECTORY, NOT `_root()`. `_root()` is where the board is WRITTEN and is redirected
    # under test; the repricing artifact is a committed repo INPUT and lives beside this file whatever the
    # output directory is. Reading it through the redirect made every priced row unpriceable under pytest.
    try:
        with open(os.path.join(root or os.path.dirname(os.path.abspath(__file__)),
                               "vast-ladder-repricing.json")) as fh:
            return float(json.load(fh)["plan_usd_per_reference_gpu_h"])
    except Exception:  # noqa: BLE001
        return None


def usd_per_ns_cell(gpu_name, dph_total, stance=None, rate_basis=None, root=None, is_bid=_MISSING):
    """One row's `$/ns` cell, or None. Delegates ENTIRELY to `inflight_usd_per_ns.row()`.

    That module is the one home for the rate, its multiple of the ladder basis, and — load-bearing since
    CLAUDE.md §1's 2026-07-27 ruling — the distinction between `⚠ PAYING OVER THE …× LINE` (money going out)
    and `⛔ REFUSED at …` (the gate declined; `$0 spent`). A board that renders those alike makes a working
    guard look broken, so this function never formats a rate itself: it passes the stance through and returns
    what that module produced.
    """
    import inflight_usd_per_ns as _ifn
    rate = planning_usd_per_ref_gpu_h(root)
    if rate is None or gpu_name is None or dph_total is None:
        return None
    kw = {}
    if stance is not None:
        kw["stance"] = stance
    if rate_basis is not None:
        kw["rate_basis"] = rate_basis
    # ★ THE TIER RIDES THE SAME PATH AS THE STANCE, and is derived by that module rather than here
    # (trimcrae, 2026-07-31: "Update the status table to show on demand / interruptible too."). `is_bid` is
    # the Vast instance record's own field — already in `vast_rate_forensics._FIELDS`, so the collect pass
    # has it in hand and nothing new is requested from the API.
    # ⚠ `is_bid` ABSENT MUST RENDER AS UNKNOWN, NOT AS BID. A caller that never read the record passes None
    # and gets `[tier?]`; only an explicit False renders `[ON-DEMAND]`. `tier_of` is what encodes that, so
    # the "absent is not bid" rule has one home and cannot be re-decided by a truthiness test here.
    if is_bid is not _MISSING:
        kw["tier"] = _ifn.tier_of(is_bid)
    try:
        return _ifn.row(gpu_name, float(dph_total), rate, **kw).get("cell")
    except Exception:  # noqa: BLE001
        return None


def unpriceable_usd_cell(dph_total, workload):
    """The `$/ns` cell for a GPU row whose ns/h is NOT MEASURABLE. Never a fabricated rate.

    ★★ WHY A LANE MAY BE UNPRICEABLE IN $/ns AND MUST SAY SO. `vast_cost_model.MEASURED_NS_PER_DAY_84K` is
    "THE ONLY THROUGHPUT TABLE" and it is a table of **84k-atom RBFE** throughput. The NR-V04 retrospective
    legs are plain endpoint MD on a different system; running their `$/hr` through that table would produce a
    confident-looking number describing a workload nobody benched — the exact failure `card_of` was tightened
    to prevent one level down, where a substituted throughput was called "worse than being unpriceable".

    So the cell carries the rate we ARE paying (which is measured) and refuses the conversion out loud. It
    can never be mistaken for a priced row: it leads with `—` and names the missing measurement.
    """
    hr = "" if dph_total is None else ("$%.4f/hr " % float(dph_total))
    return f"— {hr}(no measured ns/h: {workload})"


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# FRAGMENTS AND THE MERGED BOARD — see the module docstring for why the merged file is a separate path
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════

def _root():
    """Where the fragments and the merged board live: this directory, unless redirected.

    ★★ `INFLIGHT_BOARD_DIR` EXISTS FOR ONE REASON — NO TEST MAY WRITE A BOARD INTO THE WORKING TREE
    (measured 2026-07-31, and it is the same defect `conftest._isolate_ternary_rental_receipt` was written
    for). `tests/test_monitor_survives_unreadable_board.py` drives `mode_monitor` against a MOCKED object
    store, so publishing from that path left a fragment carrying invented units and a fabricated `0 of 19
    landed` note sitting in `research/modalities/`, ready for the next `git add -A`. A board is an evidence
    artifact about money being spent; one assembled from a mock must never be able to reach a branch.
    """
    return os.environ.get("INFLIGHT_BOARD_DIR") or os.path.dirname(os.path.abspath(__file__))


def stale_after_min():
    """Minutes after which a lane's fragment stops being a statement about NOW. IMPORTED, never typed.

    `vast_idle_guard.LOG_SILENCE_MIN` is the repo's existing "this long with no write and we stop believing
    it" line, written for a host's `run.log`. A lane's fragment is exactly that object one level up — the
    periodic write that proves the SUPERVISOR is alive — so the analogy is exact and it uses the same number
    rather than inventing a second one that could drift away from it.

    ⚠ A LANE GOING STALE IS A REAL FINDING, NOT NOISE. CLAUDE.md §6 records that this repo's schedules are
    throttled and that an agent has been dispatching the ticks by hand, so a lane that stops reporting while
    it is billing is precisely the condition that must be visible. The board says it rather than quietly
    ageing the rows.
    """
    try:
        import vast_idle_guard as _vig
        return float(_vig.LOG_SILENCE_MIN)
    except Exception:  # noqa: BLE001 — keep this module importable with no lane code present
        return float(os.environ.get("VAST_IDLE_LOG_SILENCE_MIN") or "15")


def fragment_path(lane, root=None):
    """The ONE file this lane may write. No other lane writes it, which is the whole race resolution."""
    return os.path.join(root or _root(), FRAGMENT_DIR, f"{lane}.json")


def build_fragment(lane, rows, now_epoch=None, note=None):
    """The fragment DOCUMENT for one lane. PURE.

    Relative ETAs are converted to ABSOLUTE completion epochs here, at the moment they were measured — see
    `_fmt_eta_at`. Everything else is carried through untouched: a fragment is a record of what the lane
    observed, not a second place to compute anything.
    """
    now = time.time() if now_epoch is None else now_epoch
    out = []
    for r in rows or ():
        r = dict(r)
        if r.get("eta_s") is not None:
            r["eta_epoch"] = now + float(r.pop("eta_s"))
        out.append(r)
    return {"_what": "One lane's rows for the all-lane in-flight board. Written ONLY by this lane; merged, "
                     "never edited, by inflight_board.merge_board().",
            "lane": lane, "generated_epoch": now, "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                                                time.gmtime(now)),
            "generated_et": et_stamp(now), "note": note, "rows": out}


def write_fragment(lane, rows, now_epoch=None, note=None, root=None):
    """Publish this lane's fragment. Returns the path written."""
    path = fragment_path(lane, root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(build_fragment(lane, rows, now_epoch=now_epoch, note=note), fh, indent=2)
        fh.write("\n")
    return path


def read_fragment(lane, root=None):
    """This lane's fragment, or None. A malformed fragment reads as ABSENT, never as empty rows."""
    try:
        with open(fragment_path(lane, root)) as fh:
            doc = json.load(fh)
        return doc if isinstance(doc, dict) and doc.get("lane") == lane else None
    except Exception:  # noqa: BLE001
        return None


def read_ternary_fragment(root=None):
    """(block_text, generated_epoch, error) for the ternary lane's own board file.

    Its rows are TRANSCLUDED verbatim rather than re-parsed into cells: the block its collect rendered is
    their one home, and a second derivation here would be free to disagree the next time a cell changes
    (CLAUDE.md rule 1 — point at it). The `Generated … ET` line that file already carries is the lane's
    as-of stamp, so no extra artifact is needed to date it.
    """
    path = os.path.join(root or _root(), TERNARY_BOARD_MD)
    try:
        with open(path) as fh:
            text = fh.read()
    except OSError as e:
        return None, None, f"{TERNARY_BOARD_MD} is not readable ({e})"
    m = _TERNARY_BLOCK_RE.search(text)
    if not m:
        return None, None, (f"{TERNARY_BOARD_MD} carries no ---- TVAST-BOARD ---- block; that lane's collect "
                            f"is the only thing that writes one")
    block = m.group(1).strip("\n")
    stamp = _TERNARY_STAMP_RE.search(text)
    epoch = None
    if stamp:
        try:
            import calendar
            t = time.strptime(f"{stamp.group(1)} {stamp.group(2)}", "%I:%M %p %b %d, %Y")
            epoch = calendar.timegm(t) - ET_OFFSET_H * 3600.0
        except ValueError:
            epoch = None
    err = None if epoch is not None else (f"could not date {TERNARY_BOARD_MD} — its `Generated … ET` line is "
                                          f"missing or unparseable, so this section cannot be graded for "
                                          f"staleness")
    return block, epoch, err


def stale_rows(rows, age_min):
    """Rows re-stated as what they are: a PAST report, not a current reading. PURE.

    `%` survives — a committed checkpoint does not un-happen — and so does the `$/ns` that was being billed,
    because both are facts about the moment the lane observed them. The ETA does NOT: projecting a completion
    time from a rate nobody has re-measured is the "promise nothing can keep" case this board already refuses
    for a destroyed host. The STATE becomes UNKNOWN with the original verdict quoted inside the WHY, so no
    information is lost and none of it is passed off as current.
    """
    out = []
    for r in rows or ():
        r = dict(r)
        was = "%s%s" % (r.get("state", "?"), (" — " + r["why"]) if r.get("why") else "")
        r["eta_epoch"], r["eta_s"] = None, None
        r["state"] = UNKNOWN
        r["why"] = ("lane last reported %.0f min ago — this row is THAT report, not a current reading; "
                    "it then read: %s" % (age_min, was))
        out.append(r)
    return out


def merge_board(now_epoch=None, root=None):
    """THE BOARD: every lane, one renderer, one file. Returns the whole markdown document.

    Iterates `LANES` rather than the fragments on disk, so a lane that has never published still renders a
    section that says so — see the module docstring for why a missing lane is the failure this exists to end.
    """
    now = time.time() if now_epoch is None else now_epoch
    limit = stale_after_min()
    out = [
        "<!-- GENERATED by inflight_board.merge_board(). Do not edit by hand: every lane's tick regenerates",
        "     it from the per-lane fragments. Source of every cell: inflight_board.py. -->",
        "# In-flight board — ALL LANES",
        "",
        f"Merged {et_stamp(now)}. One row per GPU leg, for every lane that can bill.",
        "",
        f"> ⚠ `{TERNARY_BOARD_MD}` IS ONE LANE ONLY. Its single writer (`gpu-ternary-fep-vast.yml`",
        f"> `task=collect`) rewrites it wholesale from the ternary lane's rows, so it can never carry another",
        f"> lane. **This** file is the all-lane board. Each lane writes only its own fragment",
        f"> (`{FRAGMENT_DIR}/<lane>.json`, or the file above for the ternary lane) and nothing else, so no",
        f"> two writers share a path and no lane can erase another's rows.",
        "",
        f"> A lane whose fragment is older than {limit:g} min renders STALE rather than vanishing — the line is",
        "> `vast_idle_guard.LOG_SILENCE_MIN`, imported, because a lane's fragment is its heartbeat.",
        "",
    ]
    for lane, heading, writer in LANES:
        out.append(f"## {heading}")
        out.append("")
        if lane == TERNARY:
            block, epoch, err = read_ternary_fragment(root)
            age = None if epoch is None else max(0.0, (now - epoch) / 60.0)
            if block is None:
                out += _absent_lane_section(lane, writer, err, now)
                continue
            if age is None:
                out.append(f"_As of: UNKNOWN — {err}. Written by `{writer}`._")
            elif age > limit:
                out.append(f"_As of {et_stamp(epoch)} — **{age:.0f} min ago, STALE (> {limit:g} min)**. The "
                           f"rows below are that report, not a current reading, and the ETA column was "
                           f"computed then and has not been re-measured. Written by `{writer}`._")
            else:
                out.append(f"_As of {et_stamp(epoch)} ({age:.0f} min ago). Written by `{writer}`._")
            out += ["", "```", block, "```", ""]
            continue
        doc = read_fragment(lane, root)
        if not doc:
            out += _absent_lane_section(
                lane, writer,
                f"no fragment at `{FRAGMENT_DIR}/{lane}.json` — this lane has never published one, or its "
                f"last publish did not reach this checkout", now)
            continue
        epoch = float(doc.get("generated_epoch") or 0.0)
        age = max(0.0, (now - epoch) / 60.0)
        rows = doc.get("rows") or []
        note = (" " + doc["note"]) if doc.get("note") else ""
        if age > limit:
            out.append(f"_As of {et_stamp(epoch)} — **{age:.0f} min ago, STALE (> {limit:g} min)**. Written "
                       f"by `{writer}`.{note}_")
            rows = stale_rows(rows, age)
        else:
            out.append(f"_As of {et_stamp(epoch)} ({age:.0f} min ago). Written by `{writer}`.{note}_")
        out += ["", "```", render(rows, now_epoch=now).rstrip("\n"), "```", ""]
    return "\n".join(out) + "\n"


def _absent_lane_section(lane, writer, why, now):
    """A lane with nothing to read renders a ROW saying so — never an empty section and never no section.

    An absent lane and an idle lane are opposite facts: one means "nothing is running", the other means "we
    cannot see whether anything is running", and this board's whole history is of those two rendering alike.
    """
    row = [{"name": lane, "pct": None, "eta_s": None, "usd_per_ns": None, "state": UNKNOWN,
            "why": f"{why}. Published by `{writer}`."}]
    return ["_As of: NEVER — this lane has published nothing this checkout can see._", "",
            "```", render(row, now_epoch=now).rstrip("\n"), "```", ""]


def write_merged_board(now_epoch=None, root=None):
    """Regenerate the all-lane board from every fragment. Returns the path written.

    Safe to call from any lane at any time: the file is derived in full from the fragments, so two lanes
    racing to write it produce the same content up to their own fragment's freshness, and neither can drop
    the other's rows.
    """
    path = os.path.join(root or _root(), MERGED_BOARD_MD)
    text = merge_board(now_epoch=now_epoch, root=root)
    with open(path, "w") as fh:
        fh.write(text)
    return path


def publish(lane, rows, now_epoch=None, note=None, root=None):
    """Write this lane's fragment AND regenerate the merged board. The one call a lane's collect makes."""
    frag = write_fragment(lane, rows, now_epoch=now_epoch, note=note, root=root)
    board = write_merged_board(now_epoch=now_epoch, root=root)
    return frag, board


def main(argv):
    """`python3 inflight_board.py [--write]` — print the all-lane board; `--write` also regenerates the file.

    Costs nothing, needs no credentials and touches no provider: everything it reads is already committed.
    """
    write = "--write" in argv[1:]
    print(merge_board(), end="")
    if write:
        print(f"\n[board] wrote {write_merged_board()}")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv))
