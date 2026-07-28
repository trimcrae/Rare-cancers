#!/usr/bin/env python3
"""P(a `stopped` Vast box ever comes back) — MEASURED from this repo's own committed per-tick census.

★★ WHY THIS EXISTS. `ternary_vast_launch.MAX_STOPPED_MIN` (and `protfep_vast_launch`'s copy) has been 45
minutes since 2026-07-25 with **no derivation anywhere in the code**. It looks like the duration of one
incident — the +26 % bid raise that left a box queued `stopped` for 45 min across ~13 start attempts — which
is a sample size of one, promoted to a constant.

That was tolerable while the constant only decided when to reap a box nobody wanted. It is not tolerable now:
`teardown_decision.decide()` uses the SAME constant as the backstop on how long a **capacity-refused** box is
HELD when no replacement clears the buy line, and there the economics are explicit and lopsided:

  * HOLDING costs storage only — `teardown_decision.storage_usd_h_for(disk_gb)`; at the disks the live lanes
    request that is ~$0.016/hr (ternary, 60 GB) and ~$0.022/hr (step 1 fan-out, 80 GB).
  * DESTROYING forfeits the staged disk and forces a replacement to redo the cold start — staging, hybrid
    build and minimisation billed on the new GPU before one FEP iteration commits, worth ~$0.10-0.28.

Break-even on those two lines alone is **6-17 hours**, not 45 minutes. But that comparison is only half the
decision, because the saving is not certain: it is collected ONLY if the held box actually resumes. The
missing input is exactly **P(resume)**, and nobody had measured it. This module measures it.

★ THE DATA IS ALREADY IN THE REPO, AND IT IS THE RIGHT DATA. `step1-fanout-progress.json` is rewritten and
committed at the START of every autoscale tick and carries, per live instance, its `id`, `machine_id`,
`cur_state`, `status`, `status_msg` and `age_min`. Every commit of that file is therefore a timestamped
census of the fleet, and git has kept all of them. Walking the file's history reconstructs a per-instance
state trajectory at tick resolution with no new instrumentation, no API call and no dollar — the same
"gitmine" trick `vast_board_volatility_gitmine` uses for prices.

⚠ THE CENSORING IS THE WHOLE DIFFICULTY, AND IT MUST BE REPORTED, NOT HIDDEN. Our own code destroys a
stopped box — at `MAX_STOPPED_MIN`, or after `STUCK_START_STRIKES` consecutive stuck-start checks. So the
observation window on any stopped episode is bounded by the very constant we are trying to derive, and a
naive "0 of N resumed" would be circular: we never LET most of them resume. Every episode therefore carries
`censored` (it ended because the box left the census, not because we watched it come back) and the headline
splits the two. An honest reading of a fully-censored sample is *"the data cannot support an estimate"*, and
this module says so rather than inventing one — which is the ruling that governs the constant.

USAGE (pure stdlib, $0, no network, no AWS):
    python3 research/modalities/vast_stopped_resume_measure.py            # print the report
    python3 research/modalities/vast_stopped_resume_measure.py --json PATH
"""
from __future__ import annotations

import json
import os
import subprocess

# The committed per-tick censuses this miner understands. Each is a JSON doc with a fleet timestamp and a
# list of per-instance rows; the readers below know each shape. Adding a lane means adding a reader, not
# changing the analysis.
CENSUS_FILES = ("research/modalities/step1-fanout-progress.json",)

# A state that means "this box is not executing". Vast reports `exited` in `status` and `stopped` in
# `cur_state` for the same box, and the fan-out's census carries both, so the trajectory is built from
# `cur_state` (the control-plane's own field) and `status` is kept only for the record.
STOPPED_STATES = ("stopped", "exited", "created")
RUNNING_STATES = ("running",)


def _git(args, repo=None):
    return subprocess.run(["git"] + list(args), cwd=repo or _repo_root(), capture_output=True, text=True,
                          check=False).stdout


def _repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=here, capture_output=True, text=True,
                         check=False).stdout.strip()
    return out or os.path.abspath(os.path.join(here, "..", ".."))


def _iso_to_epoch(s):
    """Seconds since epoch from an ISO-8601 UTC stamp. PURE. None if unparseable."""
    if not s:
        return None
    import datetime
    txt = str(s).strip().replace("Z", "+00:00")
    try:
        dt = datetime.datetime.fromisoformat(txt)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.timestamp()


def observations(repo=None, files=CENSUS_FILES):
    """Every (utc, instance) row across every committed revision of the census files. PURE-ish (reads git).

    Keyed and de-duplicated on (instance_id, tick_utc): the same census can be committed more than once (a
    rebase, a re-push), and counting a tick twice would fabricate a longer stopped episode than happened.
    """
    seen, rows = set(), []
    for path in files:
        revs = [ln for ln in _git(["log", "--all", "--format=%H", "--", path], repo).splitlines() if ln]
        for rev in revs:
            blob = _git(["show", f"{rev}:{path}"], repo)
            if not blob.strip():
                continue
            try:
                doc = json.loads(blob)
            except Exception:  # noqa: BLE001 — a half-written census in history is not an error here
                continue
            tick = doc.get("_generated_utc") or doc.get("utc")
            t = _iso_to_epoch(tick)
            if t is None:
                continue
            for inst in (doc.get("instances") or []):
                iid = inst.get("id")
                if iid is None:
                    continue
                k = (str(iid), round(t))
                if k in seen:
                    continue
                seen.add(k)
                rows.append({
                    "instance": str(iid), "machine_id": str(inst.get("machine_id")),
                    "utc": tick, "t": t,
                    "cur_state": (inst.get("cur_state") or "").lower(),
                    "status": (inst.get("status") or "").lower(),
                    "status_msg": (inst.get("status_msg") or "")[:120],
                    "age_min": inst.get("age_min"),
                    "source": path,
                })
    rows.sort(key=lambda r: (r["instance"], r["t"]))
    return rows


def episodes(rows):
    """Maximal runs of consecutive `stopped` observations, one dict per episode. PURE.

    An episode carries:
      * `preceded_by_running` — had we ever seen this box EXECUTING before it stopped? That splits the two
        populations that must never be pooled: a **never-started** box (the capacity/create-race class this
        constant governs) and a **paused-after-running** box (an outbid or preempted leg, which
        `bid-strategy.md` F3 already records as routinely resuming — and which our reaper once wrongly
        destroyed).
      * `resumed` — a LATER observation of the same instance in a running state. Positive evidence only.
      * `censored` — the episode's last stopped observation is the last time we ever saw the box. It did not
        resume *in our window*; we do not know what it did next, because we (or Vast) removed it.
      * `observed_min` — wall-clock across the episode's own observations. It is a LOWER BOUND on how long
        the box was stopped, since the census only samples at tick cadence.
    """
    by_inst = {}
    for r in rows:
        by_inst.setdefault(r["instance"], []).append(r)
    out = []
    for iid, obs in by_inst.items():
        obs.sort(key=lambda r: r["t"])
        i, seen_running = 0, False
        while i < len(obs):
            if obs[i]["cur_state"] in RUNNING_STATES:
                seen_running = True
                i += 1
                continue
            if obs[i]["cur_state"] not in STOPPED_STATES:
                i += 1
                continue
            j = i
            while j + 1 < len(obs) and obs[j + 1]["cur_state"] in STOPPED_STATES:
                j += 1
            after = obs[j + 1:]
            resumed = any(o["cur_state"] in RUNNING_STATES for o in after)
            first_resume = next((o for o in after if o["cur_state"] in RUNNING_STATES), None)
            out.append({
                "instance": iid, "machine_id": obs[i]["machine_id"],
                "first_stopped_utc": obs[i]["utc"], "last_stopped_utc": obs[j]["utc"],
                "n_observations": j - i + 1,
                "observed_min": round((obs[j]["t"] - obs[i]["t"]) / 60.0, 1),
                "preceded_by_running": seen_running,
                "resumed": resumed,
                "min_to_resume": (round((first_resume["t"] - obs[i]["t"]) / 60.0, 1)
                                  if first_resume else None),
                "censored": (not resumed) and j == len(obs) - 1,
                "status_msg": obs[i]["status_msg"],
                "age_min_at_first_stop": obs[i]["age_min"],
            })
            i = j + 1
    out.sort(key=lambda e: (e["first_stopped_utc"], e["instance"]))
    return out


def kaplan_meier(eps):
    """P(resumed by t) against stopped-minutes, censoring-corrected. PURE. Returns [(t, p, at_risk), ...].

    ★ WHY A SURVIVAL ESTIMATOR AND NOT A RATIO. `resumed / episodes` is a LOWER bound and a badly biased
    one: our own reaper removes most stopped boxes long before they could come back, so every teardown
    enters the denominator as a silent "did not resume" when in truth we never looked. Kaplan-Meier is the
    standard handling — a censored episode leaves the at-risk set at its own censoring time instead of
    counting as a failure — and it is the ONLY way this sample can say anything about the region past
    45 minutes, which is precisely the region the constant lives in.

    ⚠ READ THE `at_risk` COLUMN. The estimate is only as good as the number of boxes still under
    observation, and this sample thins hard in the tail; `recommended_hold_min` therefore refuses to
    extrapolate past the largest time actually observed.
    """
    events = ([(e["min_to_resume"], "resume") for e in eps
               if e["resumed"] and e["min_to_resume"] is not None]
              + [(e["observed_min"], "censored") for e in eps if e["censored"]])
    events.sort(key=lambda x: (x[0], x[1] != "resume"))
    surv, at_risk, curve = 1.0, len(events), []
    for t, kind in events:
        if kind == "resume" and at_risk > 0:
            surv *= (1.0 - 1.0 / at_risk)
            curve.append((round(float(t), 1), round(1.0 - surv, 4), at_risk))
        at_risk -= 1
    return curve


def p_resume_by(curve, minutes):
    """P(resumed by `minutes`) off a Kaplan-Meier curve. PURE. 0.0 before the first event."""
    p = 0.0
    for t, val, _n in curve:
        if t <= minutes:
            p = val
    return p


def summarise(eps):
    """Headline P(resume) by population, with the censoring stated. PURE.

    ⚠ THE DENOMINATOR IS THE ARGUMENT, AND ONE OBVIOUS DENOMINATOR IS A TRAP. `resumed / all episodes` is a
    LOWER BOUND, not P(resume): most episodes end because WE destroyed the box, and a destroyed box cannot
    resume. The complementary "resumed / episodes we watched to a conclusion" is worse — it is identically
    1.0 by construction here, because an episode that neither resumed nor was censored does not exist (a box
    stops being observed exactly when it stops existing). Quoting that as a probability would be a
    fabricated all-clear, so it is not reported at all; the censoring-corrected `kaplan_meier` curve is.
    """
    def _cut(sel):
        n = len(sel)
        res = [e for e in sel if e["resumed"]]
        cens = [e for e in sel if e["censored"]]
        times = sorted(e["min_to_resume"] for e in res if e["min_to_resume"] is not None)
        curve = kaplan_meier(sel)
        return {
            "n_episodes": n,
            "n_resumed": len(res),
            "n_censored": len(cens),
            "p_resume_lower_bound": (round(len(res) / n, 4) if n else None),
            "_p_resume_lower_bound_means": "resumed / ALL episodes. A lower bound only: the censored "
                                           "episodes did not fail to resume, we stopped watching them.",
            "km_p_resume_by_45min": round(p_resume_by(curve, 45), 4),
            "km_p_resume_by_90min": round(p_resume_by(curve, 90), 4),
            "km_curve": curve,
            "min_to_resume": {"n": len(times), "min": (times[0] if times else None),
                              "median": (times[len(times) // 2] if times else None),
                              "max": (times[-1] if times else None)},
            "observed_stopped_min_p50": (sorted(e["observed_min"] for e in sel)[n // 2] if n else None),
            "observed_stopped_min_max": (max((e["observed_min"] for e in sel), default=None)),
        }

    never = [e for e in eps if not e["preceded_by_running"]]
    paused = [e for e in eps if e["preceded_by_running"]]
    return {
        "all": _cut(eps),
        "never_started": _cut(never),
        "paused_after_running": _cut(paused),
    }


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ THE CONSTANT, DERIVED. `MAX_STOPPED_MIN` was 45 with no derivation in the code — it is the duration of
# ONE incident (2026-07-25: a +26 % bid raise left a box queued `stopped` for 45 min across ~13 start
# attempts), i.e. n=1 promoted to a policy. Everything below replaces that with the measurement.
#
# THE RULE, and it is deliberately conservative in the one direction that costs money:
#   * A hold may run as long as the LONGEST RESUME WE HAVE ACTUALLY SEEN, plus one census tick so that a box
#     resuming at the latest observed time is still observed resuming rather than reaped one tick early.
#   * It may NOT be extrapolated past that. Beyond the largest observed time the sample is empty and the
#     storage bill is unbounded — this is the same refusal as "no TTL without a measurement", pointed the
#     other way.
#   * It may not be set at all from a sample too small to mean anything (`MIN_OBSERVED_RESUMES`), in which
#     case the honest answer is "the data cannot support an estimate, leave the constant alone".
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
MIN_OBSERVED_RESUMES = 5

# What a teardown actually costs, and it is the number the hold is bought against: the replacement must redo
# the cold start — stage, parameterise/solvate the hybrid, minimise — all billed on a fresh GPU before one
# FEP iteration commits. Its one home is `teardown_decision.__doc__`; the LOW end is used here on purpose,
# so the recommendation is the one that survives the least favourable reading of the saving.
COLD_START_USD_LOW = 0.10


def census_gap_min(rows):
    """Median wall-clock between consecutive censuses. PURE. The resolution of every time in this module."""
    ts = sorted({r["t"] for r in rows})
    gaps = [(b - a) / 60.0 for a, b in zip(ts, ts[1:]) if 0 < (b - a) / 60.0 < 180]
    if not gaps:
        return None
    return round(sorted(gaps)[len(gaps) // 2], 1)


def recommended_hold_min(doc):
    """The hold backstop in minutes, DERIVED from the measurement. PURE. None when the data cannot say.

    Reads only the `never_started` population: that is the capacity/create-race class this constant governs.
    A `paused_after_running` box is the outbid case, which `bid-strategy.md` F3 already rules on separately.
    """
    never = [e for e in (doc.get("episodes") or []) if not e.get("preceded_by_running")]
    observed = [e["min_to_resume"] for e in never if e.get("resumed") and e.get("min_to_resume") is not None]
    if len(observed) < MIN_OBSERVED_RESUMES:
        return None
    gap = doc.get("census_gap_min") or 0.0
    raw = max(observed) + float(gap)
    return int(5 * -(-raw // 5))          # up to the next 5 min, so the number is quotable


def economics(doc, hold_min, disk_gb, from_min=45.0, cold_start_usd=COLD_START_USD_LOW):
    """Is extending the hold from `from_min` to `hold_min` worth its storage? PURE.

    Cost is certain and small (storage, billed stopped or running); the saving is probabilistic (only a box
    that RESUMES collects it). So the comparison is storage x extra hours against ΔP(resume) x cold start.
    """
    import teardown_decision as tdd
    curve = kaplan_meier([e for e in (doc.get("episodes") or []) if not e.get("preceded_by_running")])
    d_p = p_resume_by(curve, hold_min) - p_resume_by(curve, from_min)
    extra_h = max(0.0, (float(hold_min) - float(from_min)) / 60.0)
    cost = tdd.storage_usd_h_for(disk_gb) * extra_h
    gain = d_p * float(cold_start_usd)
    return {
        "disk_gb": disk_gb, "from_min": from_min, "to_min": hold_min,
        "extra_hours": round(extra_h, 3),
        "storage_usd_h": round(tdd.storage_usd_h_for(disk_gb), 5),
        "extra_storage_usd": round(cost, 5),
        "delta_p_resume": round(d_p, 4),
        "cold_start_usd_assumed": cold_start_usd,
        "expected_saving_usd": round(gain, 5),
        "worth_it": gain >= cost,
        "margin_x": (round(gain / cost, 2) if cost else None),
    }


_ARTIFACT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vast-stopped-resume.json")


def hold_minutes(default=45.0):
    """`MAX_STOPPED_MIN` for the launchers — the derived figure, or `default` if it cannot be derived.

    ★ THIS IS THE ONE HOME OF THE HOLD LENGTH (rule 1). The launchers point here; they do not carry their
    own number. Reading a committed artifact rather than re-mining git keeps module import free and keeps
    the figure reproducible — regenerate with `--json research/modalities/vast-stopped-resume.json` and the
    constant moves with the evidence.

    Falls back rather than raising: a launcher must never fail to import because a measurement file moved.
    """
    try:
        with open(_ARTIFACT) as fh:
            doc = json.load(fh)
        v = doc.get("recommended_hold_min")
        return float(v) if v else float(default)
    except Exception:  # noqa: BLE001 — an absent measurement is "no derivation available", not an error
        return float(default)


def report(repo=None, files=CENSUS_FILES):
    rows = observations(repo, files)
    eps = episodes(rows)
    summ = summarise(eps)
    doc = {
        "_what": "P(a stopped Vast box ever resumes), measured from every committed revision of this repo's "
                 "per-tick fleet census. The derivation behind MAX_STOPPED_MIN / the teardown_decision "
                 "hold backstop.",
        "_method": "git log --all over the census files -> per-instance cur_state trajectory at tick "
                   "resolution -> maximal stopped episodes -> did a later tick show the SAME instance "
                   "running? Censoring is explicit: our own reaper removes most stopped boxes.",
        "_censoring_warning": "p_resume_over_all_episodes is a LOWER BOUND. Episodes marked `censored` "
                              "ended because the box left the census (we destroyed it, or Vast did), not "
                              "because we watched it fail to resume.",
        "sources": list(files),
        "n_observations": len(rows),
        "n_instances": len({r["instance"] for r in rows}),
        "window_utc": [rows[0]["utc"], rows[-1]["utc"]] if rows else [None, None],
        "census_gap_min": census_gap_min(rows),
        "summary": summ,
        "episodes": eps,
    }
    doc["recommended_hold_min"] = recommended_hold_min(doc)
    doc["_recommended_hold_min_rule"] = (
        "the LONGEST time-to-resume actually observed among never-started boxes, plus one median census "
        f"tick, rounded up to 5 min. Never extrapolated past the observed maximum, and not set at all from "
        f"fewer than {MIN_OBSERVED_RESUMES} observed resumes (then it is None and the constant is left "
        "alone). Derivation: vast_stopped_resume_measure.recommended_hold_min.")
    if doc["recommended_hold_min"]:
        try:
            doc["economics"] = {f"{gb}GB": economics(doc, doc["recommended_hold_min"], gb)
                                for gb in (60, 80)}
        except Exception as e:  # noqa: BLE001 — the measurement stands with or without the costing
            doc["economics"] = {"error": f"{type(e).__name__}: {e}"}
    return doc


def render(doc):
    s = doc["summary"]
    L = [f"[resume] {doc['n_observations']} observations of {doc['n_instances']} instances across the "
         f"committed census history"]
    for name in ("all", "never_started", "paused_after_running"):
        c = s[name]
        L.append(f"[resume] {name:22s} episodes={c['n_episodes']:4d} resumed={c['n_resumed']:3d} "
                 f"censored={c['n_censored']:3d} P(resume)>={c['p_resume_lower_bound']} "
                 f"KM@45min={c['km_p_resume_by_45min']} KM@90min={c['km_p_resume_by_90min']} "
                 f"min_to_resume={c['min_to_resume']}")
    L.append(f"[resume] census tick gap (median) {doc.get('census_gap_min')} min")
    rec = doc.get("recommended_hold_min")
    L.append(f"[resume] DERIVED hold backstop: {rec} min"
             if rec else "[resume] DERIVED hold backstop: NONE — the data cannot support an estimate; "
                         "leave MAX_STOPPED_MIN alone")
    for k, e in (doc.get("economics") or {}).items():
        if isinstance(e, dict) and "worth_it" in e:
            L.append(f"[resume]   {k}: extending {e['from_min']:.0f}->{e['to_min']:.0f} min costs "
                     f"${e['extra_storage_usd']} of storage and buys ΔP(resume)={e['delta_p_resume']} x "
                     f"${e['cold_start_usd_assumed']} cold start = ${e['expected_saving_usd']} "
                     f"-> {'WORTH IT' if e['worth_it'] else 'NOT worth it'} ({e['margin_x']}x)")
    return "\n".join(L)


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", default=None, help="write the full measurement here")
    ap.add_argument("--repo", default=None)
    a = ap.parse_args(argv)
    doc = report(a.repo)
    print(render(doc))
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(doc, fh, indent=2)
            fh.write("\n")
        print(f"[resume] -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
