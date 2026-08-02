#!/usr/bin/env python3
"""THE SENSITIVITY-CONTROL LANE'S IN-FLIGHT BOARD FRAGMENT — % DONE derived, ETA derived or ABSENT.

★★ WHY THIS EXISTS, and the number that proves it (2026-08-01). `grep -ci selcal inflight-board-all.md` -> 0.
This lane rented hosts all day and appeared on the all-lane board **nowhere**, so it had no derived progress
figure and no derived ETA — and in that vacuum a PROSE estimate ("~3:05 PM ET for 6 models") was quoted in the
ETA column beside genuinely derived numbers and carried forward across six reports without being re-derived.
It was never measured: the only timing anyone had was a FAILURE run in which six seeds died at 7.2 s each on a
missing cysteine, and "~12 min per seed" was invented from nothing. A lane that cannot be seen is a lane whose
numbers get made up.

★ SO THE TWO CELLS OBEY DIFFERENT RULES, deliberately:

  % DONE  is a COUNT and must never be blank while the census is readable. Its numerator is the number of
          (arm, seed) co-folds that have a `_model_0.cif` in S3; its denominator is `len(COFOLD_MODEL_SEEDS)`.
          Both come from things that exist, so there is no state of the world in which this lane can render a
          blank percentage and a filled ETA — which is the shape a prose estimate hides in.

  ETA     is a PROJECTION and is refused until it is earned. `MIN_RATE_INTERVALS` completed arrivals-intervals
          before any rate is quoted; below that the cell reads `ETA UNKNOWN — <reason with the count in it>`,
          exactly as `gcp_fanout_rep.quoted_rate` does. `ETA UNKNOWN` forever would be indistinguishable from
          a broken estimator, so this is a threshold that is REACHED, not a permanent refusal.

★★ AND IT IS LABELLED `⚠ LOWER BOUND`, WHICH IS THE GCP LANE'S OTHER LESSON. Its ETA carries that label
because a warmup rate projected onto production understates. The co-fold's version of the same asymmetry is
sharper and runs the same direction: **the first seed of an arm is not like the others.** It pays for the MSA
search and the model load; seeds 2..6 reuse both. So an interval-based rate, which can only be measured
BETWEEN arrivals, is by construction a rate that has already skipped the expensive part — and projecting it
onto an arm that has not started yet understates that arm's wall clock. Any remaining work on an arm with zero
arrivals therefore makes the whole ETA a LOWER BOUND, and the cell says so rather than being averaged away.

⚠ AND THE SPREAD IS REPORTED, NEVER AVERAGED AWAY. If seeds do not cost the same, the mean is a summary of a
thing that is not summarisable; `spread` (max/min over the window) is printed beside the rate so a reader can
grade the ETA instead of trusting it.

⚠ NO `$/ns` ON ANY ROW OF THIS LANE, AND THAT IS AN HONEST `—`, NOT A MISSING FIELD. A co-fold is structure
INFERENCE — it integrates no dynamics and produces no nanoseconds — so a `$/ns` here would have no denominator
and would be a fabricated figure sitting in the one column CLAUDE.md §1 exists to make gradeable. The cell
names what is actually being spent instead. The lane's MD legs, when they run, are a different rung and carry
a real `$/ns` from `inflight_usd_per_ns`.

A STALE FRAGMENT RENDERS STALE, NOT ABSENT — `inflight_board.merge_board` handles that for every lane and
`stale_rows` blanks the ETA while keeping the %. That convention matters doubly here: this lane's census is
written by a long-running watch loop, and a watch whose commits arrive late is EXACTLY the thing that must not
read as a lane that has stopped (measured today: a 24-minute-stale census over a watch that was alive).

CLI:  python3 selcal_board.py            # publish from S3 (needs AWS credentials)
      python3 selcal_board.py --dry-run  # print the rows, write nothing
"""
from __future__ import annotations

import datetime
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import inflight_board as IB  # noqa: E402
import selcal_panel as SP  # noqa: E402

#: The lane id on the all-lane board. MUST match the `inflight_board.LANES` entry and the alarm's lane key,
#: so the board, the staleness watch and the account alarm all name this lane the same thing.
LANE = "selcal-cofold"

#: ★ THE STATED THRESHOLD FOR "ENOUGH POINTS TO QUOTE A RATE". Same value and same reasoning as
#: `gcp_fanout_rep.MIN_RATE_INTERVALS`, kept as this lane's own constant because it answers a question about
#: THIS lane's units: three completed intervals is the smallest number from which you can see whether a rate
#: is still settling (two to compare, one to confirm). This lane has its own reason to be careful — nobody has
#: ever measured how long a SUCCESSFUL seed takes here. The one timing on record is a failure run whose six
#: seeds each died at 7.2 s, and a rate quoted off that would promise the panel in under a minute.
MIN_RATE_INTERVALS = 3

#: Only the trailing N intervals feed the quoted rate: a whole-run mean keeps a settling transient in the
#: denominator forever, a trailing window forgets it once it is over.
RATE_WINDOW = 5


def _now(now=None):
    return time.time() if now is None else now


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# PURE arithmetic — every cell on the board is derived here and nowhere else
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
def arm_intervals(epochs):
    """Seconds between consecutive co-fold arrivals on one arm, oldest first. PURE.

    N arrivals give N-1 intervals: the first arrival has no predecessor to be measured against, so the time
    it took is simply NOT OBSERVABLE from S3 timestamps alone. Counting it as an interval by pretending the
    arm started when the watch did would manufacture the one number this module refuses to manufacture."""
    e = sorted(float(x) for x in (epochs or ()) if x is not None)
    return [round(b - a, 1) for a, b in zip(e, e[1:])]


def quoted_rate(intervals, min_intervals=MIN_RATE_INTERVALS, window=RATE_WINDOW):
    """{'s_per_model', 'n_intervals', 'n_used', 'spread', 'why'} — or a refusal that NAMES the count. PURE."""
    iv = list(intervals or ())
    n = len(iv)
    if n < min_intervals:
        return {"s_per_model": None, "n_intervals": n, "n_used": 0, "spread": None,
                "why": ("%d completed arrival interval(s); this lane quotes a rate at %d "
                        "(selcal_board.MIN_RATE_INTERVALS). N arrivals give N-1 intervals, so the next "
                        "co-fold to land moves it toward the threshold." % (n, min_intervals))}
    used = iv[-int(window):] if window else iv
    s = sum(used) / len(used)
    return {"s_per_model": round(s, 1), "n_intervals": n, "n_used": len(used),
            "spread": (round(max(used) / min(used), 2) if min(used) > 0 else None),
            "why": ("mean of the trailing %d of %d measured arrival intervals "
                    "(selcal_board.RATE_WINDOW)" % (len(used), n))}


def board_rows(census, arrivals, hosts=(), now=None, seeds=None, unattributed_hosts=0):
    """One row per arm. PURE — `census` and `arrivals` are already-measured readings.

    `census`  as `_cofold_census` returns it: {'per_arm': {arm_id: [seed, ...]}, ...}.
    `arrivals` {arm_id: [epoch, ...]} — when each landed co-fold appeared in S3.
    `hosts`    the live instances wearing this lane's label, as the control plane reported them.
    """
    now = _now(now)
    seeds = list(seeds if seeds is not None else SP.COFOLD_MODEL_SEEDS)
    per_arm = (census or {}).get("per_arm") or {}
    readable = isinstance((census or {}).get("per_arm"), dict)
    by_arm_host = {}
    for h in hosts or ():
        lbl = str(h.get("label") or "")
        for a in SP.ARMS:
            if a.arm_id in lbl or a.cofold_system in lbl:
                by_arm_host.setdefault(a.arm_id, []).append(h)

    # ★ THE RATE IS POOLED ACROSS ARMS, and that is a choice with a reason: the two arms co-fold different
    # systems on different hosts, so neither alone reaches the threshold quickly — but pooling is only honest
    # while the two look alike, so the pooled `spread` is what tells a reader whether it was.
    if arrivals is None:
        # ⚠ NOT THE SAME AS "no intervals yet". `None` means the timestamps were never READ — a fragment
        # built from the committed census alone, with no S3 listing behind it. Saying "0 intervals measured"
        # would imply a measurement that was never attempted (§4), and the next tick would look like
        # progress when nothing had changed.
        rate = {"s_per_model": None, "n_intervals": 0, "n_used": 0, "spread": None,
                "why": ("arrival timestamps were NOT READ for this fragment (built from the committed "
                        "census alone), so no interval exists to measure. This is an unread rate, not a "
                        "rate of zero — a tick with S3 access replaces it.")}
    else:
        pooled = []
        for arm_id in (a.arm_id for a in SP.ARMS):
            pooled += arm_intervals(arrivals.get(arm_id))
        rate = quoted_rate(pooled)

    # An arm with ZERO arrivals has not paid its MSA + model-load cost yet, and no measurable interval
    # includes that cost. Any remaining work there makes the whole projection a floor.
    unstarted = [a.arm_id for a in SP.ARMS
                 if len(per_arm.get(a.arm_id) or ()) == 0 and len(seeds) > 0]

    rows = []
    for a in SP.ARMS:
        got = list(per_arm.get(a.arm_id) or ())
        n_done, n_tot = len(got), len(seeds)
        left = max(0, n_tot - n_done)
        live = by_arm_host.get(a.arm_id) or []
        # ⚠ THE ONE CELL THAT MAY NEVER BE BLANK WHILE THE CENSUS IS READABLE. Not `sequential_pct` — that
        # solves a harder problem (a unit made of ordered stages with per-stage denominators); a co-fold arm
        # is a flat count of models that exist over models wanted, and borrowing the stage machinery would
        # dress a simple count up as an estimate. `n_tot` comes from `COFOLD_MODEL_SEEDS`, so the
        # denominator is known whenever the panel is.
        pct = None if not readable or not n_tot else round(100.0 * n_done / n_tot, 1)
        eta_s, eta_note = None, ""
        if left == 0:
            state = "DONE"
            why = "all %d seeds have a co-fold in S3." % n_tot
        elif rate["s_per_model"] is None:
            state = IB.RUNNING if live else IB.NO_HOST
            eta_note = "ETA UNKNOWN — %s" % rate["why"]
            why = "%d of %d seeds landed. %s" % (n_done, n_tot, eta_note)
        else:
            eta_s = left * rate["s_per_model"]
            floor = bool(unstarted) or a.arm_id in unstarted
            eta_note = ("%s%.1f min/model over %d interval(s)%s"
                        % ("⚠ LOWER BOUND — " if floor else "", rate["s_per_model"] / 60.0,
                           rate["n_used"],
                           (", spread %.2fx — the seeds do NOT cost the same, so the mean is a summary of "
                            "an unsummarisable thing; grade the ETA against the spread, not the mean"
                            % rate["spread"]) if (rate["spread"] or 1) > 1.5 else ""))
            why = ("%d of %d seeds landed; %d to go at %s (%s).%s"
                   % (n_done, n_tot, left, eta_note, rate["why"],
                      (" Arm(s) %s have produced nothing yet: no measurable interval contains the MSA + "
                       "model-load an arm pays once, so this is a FLOOR." % ", ".join(unstarted))
                      if floor else ""))
            state = IB.RUNNING if live else IB.NO_HOST
        if not readable:
            state, pct = IB.UNKNOWN, None
            why = ("the co-fold census is unreadable, so neither the count nor the ETA is measured. An "
                   "absent reading is not a reading of absence (CLAUDE.md §4).")
        if live:
            why += (" Host(s): %s." % ", ".join("%s %s" % (h.get("id"), h.get("actual_status"))
                                                for h in live))
        elif left and readable and not unattributed_hosts:
            why += " No host wearing this arm's label is live."
        elif left and readable:
            # ⚠ NOT "no host". The committed census records instances without their labels, so a host cannot
            # be attributed to an arm from it alone — and "unattributable" must not render as "absent" (§4).
            why += (" %d host(s) are live on this lane but the committed census carries no label, so which "
                    "arm they serve is UNATTRIBUTABLE from this source." % unattributed_hosts)
        # ⚠ DO NOT re-add "and the lane's MD legs carry a real $/ns": they do not, and cannot. This lane's MD
        # rows are UNPRICEABLE in $/ns for a different reason than these co-fold rows — not "no dynamics" but
        # "no benched throughput for endpoint MD at this system size" — and both refusals are honest. A
        # cross-reference that promises a number the neighbouring rows never produce is a rule-1 defect.
        why += (" %d/%d seeds; no $/ns is quoted because a co-fold integrates no dynamics — there is no ns "
                "denominator. The lane's MD rows quote the $/hr they are billed and refuse the conversion "
                "(inflight_board.unpriceable_usd_cell)." % (n_done, n_tot))
        rows.append({
            "name": "%s co-fold" % a.arm_id, "pct": pct,
            # ⚠ `pct_of` STAYS NONE, and that is not an omission. The renderer treats it as a LABEL that
            # REPLACES the percentage, for a row whose progress is measured against something other than the
            # production protocol (`smoke`). This denominator IS the production panel — `COFOLD_MODEL_SEEDS`
            # — so setting it would suppress the one cell that must never be blank.
            "pct_of": None,
            "eta_s": eta_s,
            # ⚠ AN HONEST `—`, KEPT SHORT because this column is sized from its widest cell: a paragraph here
            # stretches the whole board and pushes STATE and WHY out of alignment for every lane. The reason
            # lives in WHY, where a long string costs nothing.
            "usd_per_ns": "— no ns: co-fold is inference, not MD",
            "state": state, "why": why})
    return rows


def banked_leg_minutes(rentals):
    """This lane's OWN measured leg duration, from the rentals that BANKED one -> sorted [minutes].

    ⛔ ONE HOME, AND IT IS NOT HERE. The selection rule and the p90 both live in `lane_staleness_watch`
    (stdlib-only, lane-free, already tested) and are IMPORTED. This wrapper exists only so the board reads
    naturally; it must never grow its own arithmetic, because the same two numbers are quoted in a board
    cell AND in that module's overrun warning — and if they drifted, the board would promise an ETA the
    watcher was simultaneously calling an overrun. The first draft of this function DID re-derive the p90
    inline while its docstring claimed to import it, which is the two-homes bug in miniature.

    ⚠ RENTALS THAT NEVER BANKED ARE EXCLUDED, and that is not a detail. Measured 2026-08-02: 36 of this
    lane's 58 rentals produced no leg (median 13.2 min — hosts that refused, crash-looped or died) against 22
    that finished one (median 41.5). Including the failures drags the median down and the p90 up: a duration
    built mostly from things that never ran.
    """
    import lane_staleness_watch as LSW   # lane -> watcher is acyclic; the watcher imports no lane
    return LSW.banked_leg_minutes(rentals)


def read_banked_leg_minutes(path=None):
    """The above, off `selcal-price-ledger.json`. Never raises: an unreadable ledger means NO measured
    duration, which the row must say rather than silently rendering as "no leg has ever finished"."""
    try:
        import selcal_vast_launch as L
        with open(path or L.PRICE_LEDGER) as fh:
            doc = json.load(fh)
        return banked_leg_minutes((doc or {}).get("rentals"))
    except Exception:  # noqa: BLE001
        return []


def md_rows(handles, hosts=(), landed=None, n_units=None, now=None, leg_minutes=None):
    """One row per MD leg this lane has RENTED. PURE.

    ★★ WHY THIS EXISTS (2026-08-01, ~6 minutes after the lane's first MD leg started billing). This module
    emitted exactly one row per co-fold ARM, because when it was written co-folds were all this lane had —
    its own docstring says so ("the lane's MD legs, when they run, are a different rung"). So the moment the
    first MD host was rented, the board showed two DONE co-fold rows and **nothing at all for the leg that
    was actually spending money**. A billing leg with no board row is the precise failure the whole in-flight
    board exists to prevent, and it is how a fabricated ETA for this lane survived six consecutive reports.

    `handles`  `selcal-handles.json` — [{unit, arm, model, replica, instance, utc}], written at rental.
    `hosts`    live instances as the control plane reported them; `None` means UNREADABLE, not empty.
    `landed`   how many units have a banked result, or None if that was not measured.

    ⚠ THE HANDLES FILE IS A RECORD OF A PURCHASE, NOT OF A RUNNING LEG. A handle whose instance is gone
    means the leg ENDED — landed, preempted or reaped — and the row says exactly that rather than implying
    it is still running (§4: a populated field is not a measured one).
    """
    now = _now(now)
    rows = []
    live_by_id = None if hosts is None else {str(h.get("id")): h for h in (hosts or ())}
    for h in handles or ():
        inst = str(h.get("instance") or "")
        host = None if live_by_id is None else live_by_id.get(inst)
        started = h.get("utc")
        if live_by_id is None:
            state = IB.UNKNOWN
            why = ("the instance list could not be READ this tick, so whether this leg still holds a host "
                   "is unknown. An absent reading is not a reading of absence (CLAUDE.md §4).")
        elif host is not None:
            state = IB.RUNNING
            why = "instance %s %s, rented %s." % (inst, host.get("actual_status") or "?", started)
        else:
            state = "ENDED — no host"
            why = ("instance %s is no longer on the account, so this leg ended — landed, preempted or "
                   "reaped. Rented %s. Which of the three it was is in the lane's collect, not here: this "
                   "row reports host state and must not guess an outcome." % (inst, started))
        # ⚠ NO $/ns IS INVENTED — but the DOLLARS ARE NOT OPTIONAL. `vast_cost_model`'s table benches 84k-atom
        # RBFE and these legs are endpoint MD on a far larger system, so the derived rate genuinely cannot be
        # quoted; that much this row always had right. What it got wrong was writing its own refusal string,
        # which carried no `$/hr` either — so 19 hosts billed with no money anywhere on the board. The one home
        # for "unpriceable, and here is what it costs anyway" is `inflight_board.unpriceable_usd_cell`, which
        # NR-V04 (identical workload, identical reason) already used.
        if host is not None:
            usd = IB.unpriceable_usd_cell(host.get("dph_total"), IB.ENDPOINT_MD_NOT_BENCHED)
        else:
            # No host record to read a rate FROM. Not "free" and not "unknown cost" — the rate this leg was
            # billed at is in the lane's rental ledger, not in a board row about a host that is gone.
            usd = ("— %s; no live host record this tick, so no rate to quote here"
                   % IB.ENDPOINT_MD_NOT_BENCHED)
        # ★★ THE ETA, FROM THIS LANE'S OWN LANDED LEGS — and the sentence this replaces was FALSE.
        # It read "this lane has never run an MD leg to its terminus, so there is no measured s/iter to
        # project from; the first one that lands supplies it", UNCONDITIONALLY. It was true when written
        # (zero legs had landed) and was still being printed after TWENTY-TWO had, because nothing ever
        # re-read it — a hard-coded sentence is not a measurement, and this one asserted a falsehood on a
        # board whose whole job is to say what is happening.
        #
        # ⚠ WHY IT MATTERS BEYOND TIDINESS (measured 2026-08-02, and it cost 4.5 billed hours). With no ETA
        # and no rate, a host running EIGHT TIMES slower per frame than the fleet was indistinguishable on
        # this board from one running normally: the row quotes $/hr, and $/hr cannot show slowness. The one
        # metric that could — cost per unit of work — is genuinely unquotable here (`vast_cost_model` benches
        # 84k-atom RBFE, not endpoint MD), so ELAPSED-AGAINST-MEASURED is the only drift signal this lane can
        # have, and it was sitting unused in the lane's own rental ledger the entire time.
        import lane_staleness_watch as LSW
        mins = read_banked_leg_minutes() if leg_minutes is None else sorted(leg_minutes)
        eta_s, tail = None, ""
        if state is IB.RUNNING and mins and started:
            med = mins[len(mins) // 2]
            p90 = LSW.p90_minutes(mins)   # ⛔ imported, never re-derived — see `banked_leg_minutes`
            age_min = _age_min(started, now)
            if age_min is not None:
                eta_s = max(0.0, (med - age_min)) * 60.0
                # A row past the lane's own p90 says so, with the multiple. NOT a condemnation and nothing
                # reaps on it — a slow leg that is checkpointing is still buying work, which is exactly why
                # destroying one on this signal would be wrong. It is a reason to LOOK (`--mode diag`).
                if age_min > p90:
                    eta_s = None
                    tail = (" ⚠ OVERRUN — up %.0f min against this lane's own measured p90 of %.0f min "
                            "(%.1f×, median %.0f, from %d rental(s) that banked a leg). NOT a condemnation "
                            "and nothing reaps on it: a slow leg that is still checkpointing is still buying "
                            "work. It is a reason to run `--mode diag` and read the host's banked run.log."
                            % (age_min, p90, age_min / p90 if p90 else 0.0, med, len(mins)))
                else:
                    tail = (" ETA from this lane's own measured leg duration: median %.0f min over %d "
                            "rental(s) that banked a leg (p90 %.0f). A PROJECTION off elapsed time, not a "
                            "frame count — the leg's own progress is in its S3 checkpoints, not here."
                            % (med, len(mins), p90))
        if not tail:
            tail = (" ETA UNKNOWN — %s. This lane quotes $/hr and cannot quote $/ns (endpoint MD is not the "
                    "benched workload), so elapsed-against-measured is its only drift signal and it needs a "
                    "landed-leg population to exist."
                    % ("no rental has yet banked a leg, so there is no measured duration to project from"
                       if not mins else
                       "this row has no live host and no rental timestamp to measure elapsed time against"))
        rows.append({
            "name": h.get("unit") or "selcal MD leg",
            "pct": None,
            "pct_of": None if landed is None else ("%d/%d landed" % (landed, n_units or 0)),
            "eta_s": eta_s,
            "usd_per_ns": usd,
            "state": state,
            "why": why + tail,
        })
    return rows


def _age_min(started_iso, now=None):
    """Minutes since an ISO-Z rental stamp, or None if it cannot be read — never a fabricated 0."""
    try:
        t = datetime.datetime.strptime(str(started_iso), "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc)
    except Exception:  # noqa: BLE001
        return None
    return max(0.0, (_now(now) - t.timestamp()) / 60.0)


def note_for(census, rows):
    """The one-line lane note under the heading. Derived from the same census the rows are."""
    per_arm = (census or {}).get("per_arm") or {}
    tot = sum(len(v or ()) for v in per_arm.values())
    want = len(SP.ARMS) * len(SP.COFOLD_MODEL_SEEDS)
    return ("%d of %d (arm, seed) co-folds are in S3. %% DONE is a COUNT of models that exist; the ETA is "
            "refused until %d arrival intervals have been measured (selcal_board.MIN_RATE_INTERVALS) and is "
            "a LOWER BOUND whenever an arm has not started, because no measurable interval includes the MSA "
            "+ model load an arm pays once." % (tot, want, MIN_RATE_INTERVALS))


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# the impure edge
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
def cofold_arrivals(s3, bucket, prefix):
    """{arm_id: [epoch, ...]} — when each landed co-fold's `_model_0.cif` appeared. MEASURED from S3.

    The same object the census counts, read for its timestamp instead of its existence, so the ETA and the
    percentage can never disagree about which models are there."""
    out = {}
    for arm in SP.ARMS:
        got = []
        token, base = None, "%s/%s/" % (prefix.strip("/"), arm.cofold_system)
        while True:
            kw = {"Bucket": bucket, "Prefix": base, "MaxKeys": 1000}
            if token:
                kw["ContinuationToken"] = token
            page = s3.list_objects_v2(**kw)
            for o in page.get("Contents") or []:
                if o["Key"].endswith("_model_0.cif"):
                    got.append(o["LastModified"].timestamp())
            if not page.get("IsTruncated"):
                break
            token = page.get("NextContinuationToken")
        out[arm.arm_id] = sorted(got)
    return out


def read_handles(path=None):
    """`selcal-handles.json`, or [] — never an exception. A board that dies on a missing file renders the
    lane as ABSENT, which is the opposite of what a missing handles file means (no leg has been rented)."""
    try:
        import selcal_vast_launch as L
        with open(path or L.HANDLES) as fh:
            doc = json.load(fh)
        return doc if isinstance(doc, list) else []
    except Exception:  # noqa: BLE001
        return []


def publish(census, arrivals, hosts=(), now=None, root=None, handles=None, landed=None, n_units=None):
    """Write the fragment and regenerate the merged board. The one call the lane's tick makes.

    ⚠ CO-FOLD ROWS **AND** MD ROWS. Until 2026-08-01 this published only the co-fold arms, so the lane's
    first MD rental billed with no row on the board at all — see `md_rows`."""
    rows = board_rows(census, arrivals, hosts=hosts, now=now)
    rows += md_rows(read_handles() if handles is None else handles,
                    hosts=hosts, landed=landed, n_units=n_units, now=now)
    return IB.publish(LANE, rows, now_epoch=_now(now), note=note_for(census, rows), root=root)


def publish_from_census(root=None, census_path=None, now=None):
    """Publish from the COMMITTED census alone — no S3, no credentials, no network.

    A lane that can only render when it holds AWS credentials is a lane that renders as ABSENT in every
    context that does not, which is how it stayed invisible. The percentage survives (the census counts the
    models), the ETA does not (nothing here measured an arrival), and the row says which of the two it is."""
    import selcal_vast_launch as L
    with open(census_path or L.COFOLD_CENSUS) as fh:
        cen = json.load(fh)
    n_hosts = len(cen.get("instances") or [])
    rows = board_rows(cen, None, hosts=(), now=now, unattributed_hosts=n_hosts)
    return IB.publish(LANE, rows, now_epoch=_now(now), note=note_for(cen, rows), root=root)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    dry = "--dry-run" in argv
    if "--from-census" in argv:
        frag, board = publish_from_census()
        print("[selcal-board] wrote %s from the committed census (no S3 read — the ETA cell says so)"
              % os.path.basename(frag), flush=True)
        return 0
    import boto3
    import selcal_vast_launch as L
    bucket = L.BUCKET
    prefix = SP.COFOLD_PREFIX.strip("/")
    s3 = boto3.client("s3")
    census = L._cofold_census(s3, bucket, prefix)
    arrivals = cofold_arrivals(s3, bucket, prefix)
    try:
        _readable, _live, mine = L._live_labels_checked()
    except Exception as e:  # noqa: BLE001
        print("[selcal-board] host board unreadable (%s) — rows will say so" % e, flush=True)
        mine = []
    rows = board_rows(census, arrivals, hosts=mine)
    if dry:
        print(json.dumps({"rows": rows, "note": note_for(census, rows)}, indent=1))
        return 0
    frag, board = publish(census, arrivals, hosts=mine)
    print("[selcal-board] wrote %s and regenerated %s" % (os.path.basename(frag), os.path.basename(board)),
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
