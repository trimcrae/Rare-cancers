#!/usr/bin/env python3
"""Session-independent watchdog for the VAST ternary lane.

WHY IT HAD TO BE WRITTEN RATHER THAN REUSED
-------------------------------------------
`.github/workflows/ternary-leg-watchdog.yml` already watches ternary legs — but only GCP ones. Every one of
its three questions is GCP-specific: it authenticates by WIF, reads state from GCS, asks "is a
`gcp-ternary-*` VM up?", and its only recovery is to re-dispatch `gpu-ternary-fep-gcp.yml`. Pointing a Vast
leg at it would produce a watchdog that silently watches nothing — the exact failure class this program has
been bitten by repeatedly (a check that reports success while measuring nothing). Under the 2026-07-25
all-runs-on-Vast directive that gap applies to every GPU run the program makes from here, so it is closed
here rather than worked around.

THE THREE QUESTIONS, mirrored from the GCP watchdog:
    result artifact in S3                -> DONE     (disable the entry)
    an instance for this unit alive AND ADVANCING -> RUNNING  (emit progress)
    neither                              -> DIED     (relaunch; resumes from the last committed checkpoint)

TWO THINGS THE GCP VERSION HAS NO ANALOGUE FOR
----------------------------------------------
1. **"Alive" is not "advancing" on Vast.** A rented instance can sit up with a dead container or an idle
   GPU and look perfectly healthy. So RUNNING requires the COMMITTED ITERATION COUNT to have gone up since
   the previous tick, not merely that an instance exists. The commit store is the only durable evidence
   that the science advanced, and unlike the instance it survives a preemption.
2. **A capacity refusal is not a preemption.** If a start comes back
   `{"success": false, "error": "resources_unavailable"}` the machine has no free GPU and no bid fixes it
   (verified 2026-07-25: +26% to the value ceiling changed nothing). The answer is to destroy, add the
   machine to the exclusion set, and pick a different host — never to wait, never to raise the bid. A host
   that never starts has infinite realised $/ns, which the ranking cannot see, so without the exclusion it
   keeps winning selection and keeps failing. That policy already exists in
   `ternary_vast_launch.collect` + `ResourceSpec.exclude_machine_ids`; this module DELEGATES to it rather
   than writing a second policy that can disagree.

SAFETY PROPERTIES CARRIED OVER FROM THE GCP WATCHDOG
  - a per-UTC-day relaunch counter per entry, capping runaway re-dispatch;
  - a no-op on an empty or all-disabled watch list;
  - all state in the repo (the watch list) and S3 (progress + counters), so it survives container restarts
    with no agent awake;
  - outcomes emitted as ::notice::/::error:: annotations, readable from the check-runs API without opening
    a log, and any alert also fails the job so GitHub's own workflow-failure notification fires.

STATE LAYOUT (S3, under the lane prefix)
    watchdog/progress-<unit_id>.json     {"scalar": int, "stall": int, "utc": str}
    watchdog/relaunch-<YYYYMMDD>-<unit_id>.txt
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ternary_vast_launch as tv  # noqa: E402
import watchdog_validate as wdv  # noqa: E402
from gpu_backend import _vast_request  # noqa: E402

# THE DECISION POLICY LIVES IN watchdog_policy AND IS RE-EXPORTED HERE, UNCHANGED.
# It was written here and it was right, but not one clause of it is ternary-specific — every clause takes its
# evidence as an argument. Generalising the watchdog to non-ternary Vast jobs (vast_watchdog.py) therefore
# meant either importing this policy or writing a second copy, and two monitors that can disagree about
# whether a leg is dead is strictly worse than one. `from ... import` rather than a wrapper so that
# `ternary_vast_watchdog.classify` IS `watchdog_policy.classify` — there is nothing to drift.
from watchdog_policy import (  # noqa: E402,F401  (re-exported: callers + tests use these)
    classify, container_started_from_phase, should_relaunch)
import watchdog_policy as _wp  # noqa: E402

WATCH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ternary-vast-watch.json")

# =============================================================================================================
# ★★ WHICH PHASES CAN COMMIT AN FEP ITERATION AT ALL — and why the answer has to be written down
# (LANE 21, 2026-07-27, after a SETUP_STALL alert sent two readers after the wrong cause in three hours).
#
# `committed_progress` counts objects under `commits/<uid>/{warmup,production}/iter-N/`. Those are written by
# the sampler inside `run_ternary_leg.sh`, which the driver invokes ONLY after `mark md-running`. So for the
# whole of start / cloned / staging / preequil the committed-iteration counter is ZERO **by construction** —
# not because nothing is happening, but because nothing that happens in those phases is an FEP iteration.
#
# The 9:17 PM ET pass read `scalar=0 age=146min` and emitted "Setup is hung, not slow: check the CUDA probe,
# the charge cache, minimise steps and GPU utilisation." Every one of those was wrong. The container was
# running a full 0.5 ns pre-equilibration on CUDA (~26 min per cycle) and aborting at the END of it — real
# work, real GPU spend, and a counter that cannot see any of it. The hint list actively pointed away from the
# only available explanation.
#
# This is the same shape as the defect fixed in `vast_watchdog` the same night: a verdict computed from a
# counter that cannot answer the question being asked. There it was unit-scoped vs instance-scoped; here it
# is FEP-iteration-scoped vs phase-scoped. **`scalar == 0` is evidence of "nothing happening" only inside a
# phase that commits iterations.** So the phase is consulted BEFORE any hint text is written.
#
# Kept as data rather than prose because it must track `ternary_vast_launch`'s `mark` calls; the test suite
# asserts this map against the marks that module actually emits, so adding a phase without classifying it
# fails CI rather than silently producing a confident wrong hint.
# =============================================================================================================
# Phases before the sampler exists. A zero counter here is CORRECT and expected.
NON_COMMITTING_PHASES = ("start", "cloned", "staging", "preequil")
# The only phase that can move the committed-iteration counter.
COMMITTING_PHASES = ("md-running",)
# After the MD has finished; the deliverable path, not a sampling phase.
TERMINAL_PHASES = ("md-done", "done")
# The log uploader (`mark`, plus a 2-min sync loop) pushes run.log continuously. A log materially older than
# that interval means the UPLOADER stopped, which is a different and worse fact than "this phase is long".
LOG_STALE_MIN = 8.0

# Grace before "zero committed iterations" is called a stall rather than a slow start. A cold unit does
# stage (~15 min) -> pre-equilibrate (~10 min) -> solvate+parameterise the ~146k-atom hybrid (~8-40 min)
# -> minimise 12 replicas, all before its first commit. 90 min is comfortably past a healthy cold start and
# far short of an hour wasted on a hang. Same value, same TVAST_* env override, now sourced from the policy
# module so the ternary lane and the generic engine cannot drift apart on it.
SETUP_GRACE_MIN = _wp.DEFAULT_SETUP_GRACE_MIN
# Consecutive no-advance ticks before a frozen counter is a stall. At a 15-min cron and a 40-iteration
# production commit interval (~10 min of MD at 4 fs), 2 ticks is one missed interval, not noise.
STALL_TICKS = _wp.DEFAULT_STALL_TICKS


def phase_head(phase_text):
    """The bare phase name out of a `<phase> <ISO8601Z>` marker. '' when there is no marker at all."""
    return (phase_text or "").strip().split()[0] if (phase_text or "").strip() else ""


def setup_stall_diagnosis(*, phase_text, marker_age_min, log_age_min, log_lines,
                          container_started, instance_age_min, grace_min=None):
    """(headline, hints) for a SETUP_STALL — the CAUSE, not a list of guesses. PURE, hence unit-tested.

    ★ THE RULE THIS ENCODES: a zero committed-iteration counter only means "nothing is happening" inside a
    phase that commits iterations. Three cases, and the old alert emitted the third one's hint list for all
    of them — which is how a healthy-but-long pre-equilibration was reported as a hung CUDA probe.

      1. NO CONTAINER YET — the phase marker predates this rental (or there is none). The box is pulling its
         image or failing to start it, and nothing inside the leg is wrong. Verified elsewhere on this
         account at 2 h 57 min for a 2.91 GiB image, so this is not a corner case.
      2. IN A NON-COMMITTING PHASE — stage / pre-equilibrate / clone. Real work, real GPU, zero FEP
         iterations BY CONSTRUCTION. The progress signal here is the phase marker's age and the log's own
         mtime, and the alert says so instead of naming the sampler's failure modes.
      3. IN A COMMITTING PHASE AND NOT COMMITTING — `md-running` with the counter still at zero past the
         grace. This is the ONLY case the historical hint text ever fitted, and it keeps it.

    Log staleness is reported in every case because it separates the two things that look identical from
    outside: a phase that is legitimately long (log fresh, work ongoing) from a container that has wedged or
    died with its uploader (log stale). `gpu_util` is deliberately not consulted — LANE 17 established it
    reads `None` on this lane while a box is demonstrably advancing, so it can only mislead.
    """
    grace = SETUP_GRACE_MIN if grace_min is None else grace_min
    head = phase_head(phase_text)
    tail = " | ".join(str(x) for x in (log_lines or [])[-4:])[:600] or "(no run.log in S3 yet)"

    def _age(v, what):
        return f"{what} {v:.0f} min ago" if isinstance(v, (int, float)) else f"{what} unknown"

    freshness = _age(log_age_min, "run.log last written")
    if isinstance(log_age_min, (int, float)) and log_age_min > LOG_STALE_MIN:
        freshness += (f" — STALE (>{LOG_STALE_MIN:.0f} min). The driver pushes the log continuously, so a "
                      f"stale log means the CONTAINER or its uploader stopped, not that a phase is slow")
    elif isinstance(log_age_min, (int, float)):
        freshness += " — fresh, so the container is alive and writing"

    if not container_started:
        return ("THE CONTAINER ON THIS INSTANCE HAS NEVER RUN",
                f"the phase marker {head or '(absent)'!r} predates this rental, so it was written by a "
                f"previous host — this box has not executed one instruction and there is nothing wrong "
                f"inside the leg. It is pulling its image or failing to start it (a 2.91 GiB pull has taken "
                f"2 h 57 min on this account). Check the Vast instance's actual_status/status_msg, not the "
                f"leg. Do NOT diagnose the CUDA probe, the charge cache or minimise steps.")

    if head in NON_COMMITTING_PHASES:
        return (f"NOT STALLED ON THE COUNTER — phase {head!r} COMMITS NO FEP ITERATIONS BY CONSTRUCTION",
                f"`scalar=0` is the CORRECT reading here and is not evidence of a hang: the committed-"
                f"iteration store is only written by the sampler, which starts at `md-running`. This leg is "
                f"still in {head!r} after {instance_age_min:.0f} min (grace {grace:.0f} min). The progress "
                f"signal for THIS phase is the marker's age and the log, not the counter: "
                f"{_age(marker_age_min, 'phase marker written')}; {freshness}. Read the log tail below and "
                f"ask whether {head!r} is advancing or repeating — a 0.5 ns pre-equilibration is ~26 min per "
                f"cycle and a leg that aborts at the END of one looks exactly like this. Ignore the CUDA "
                f"probe and the charge cache unless the log names them. Log: {tail}")

    if head in TERMINAL_PHASES:
        return (f"PAST THE MD — phase {head!r} with no committed iteration",
                f"the leg reached {head!r}, which is the deliverable path, yet nothing was ever committed. "
                f"That is an MD that produced no checkpoint at all, so look at the leg record and the log "
                f"tail rather than at setup: {freshness}. Log: {tail}")

    if head in COMMITTING_PHASES:
        return (f"IN {head!r}, WHICH DOES COMMIT, AND HAS COMMITTED NOTHING",
                f"the sampler is the thing that is not producing, so setup really is the suspect here: "
                f"check the CUDA probe, the charge cache, the minimise step count and whether a warmup NaN "
                f"aborted before the first checkpoint interval. {_age(marker_age_min, 'phase marker written')}; "
                f"{freshness}. Log: {tail}")

    return (f"UNRECOGNISED PHASE {head!r}" if head else "NO PHASE MARKER, BUT THE CONTAINER APPEARS STARTED",
            f"this engine does not classify {head!r} as committing or non-committing, so it will NOT guess "
            f"at a cause — adding a `mark` to ternary_vast_launch without classifying it here is what this "
            f"branch catches. {_age(marker_age_min, 'phase marker written')}; {freshness}. Log: {tail}")


def enabled_entries(doc):
    """The entries this pass should act on. PURE. An absent/!dict/empty list is a legitimate no-op."""
    if not isinstance(doc, dict):
        return []
    return [w for w in (doc.get("watch") or []) if isinstance(w, dict) and w.get("enabled")]


def watch_entry(leg_id, seed, direction, mode, timestep_fs, warmup_timestep_fs,
                git_branch=None, max_relaunches_per_day=8, enabled=True):
    """One watch-list entry. PURE. Carries every parameter a relaunch needs, so the watchdog INVENTS
    NOTHING — it re-dispatches exactly what was launched.

    `git_branch` is in here for a reason that is easy to miss: the watchdog runs on a SCHEDULE, and a
    schedule only fires from the default branch, so `github.ref_name` inside it is `main`. A unit launched
    from a feature branch would therefore be relaunched onto a host that pulls MAIN's code — different code,
    silently, on a resumed checkpoint. Recording the branch the unit was launched from and replaying it is
    the difference between "resume this leg" and "run something else under this leg's name".
    """
    return {
        "unit_id": tv.unit_id(leg_id, seed, direction, timestep_fs, warmup_timestep_fs, mode),
        "leg_id": leg_id, "seed": int(seed), "direction": direction, "mode": mode,
        "timestep_fs": str(timestep_fs), "warmup_timestep_fs": str(warmup_timestep_fs),
        "git_branch": git_branch or os.environ.get("GIT_BRANCH") or "main",
        "max_relaunches_per_day": int(max_relaunches_per_day),
        "enabled": bool(enabled),
    }


# =============================================================================================================
# I/O
# =============================================================================================================
def load_watch(path=None):
    p = path or WATCH_FILE
    try:
        with open(p) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"watch": []}


def save_watch(doc, path=None):
    with open(path or WATCH_FILE, "w") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")


def arm(mode, path=None, timestep_fs=None, warmup_timestep_fs=None):
    """Register (or re-enable) every unit of `mode` in the watch list. Idempotent.

    Called by the launch job immediately after renting, because the watch list is the ONLY input the cron
    watchdog reads — a launch that does not register its units is a launch nobody is watching.
    """
    dt = str(timestep_fs or os.environ.get("TVAST_TIMESTEP_FS") or tv.DEFAULT_TIMESTEP_FS)
    wdt = str(warmup_timestep_fs or os.environ.get("TVAST_WARMUP_TIMESTEP_FS")
              or tv.DEFAULT_WARMUP_TIMESTEP_FS)
    doc = load_watch(path)
    doc.setdefault("watch", [])
    by_id = {w.get("unit_id"): w for w in doc["watch"] if isinstance(w, dict)}
    added = 0
    for (leg, seed, direction) in tv.units_for(mode):
        e = watch_entry(leg, seed, direction, mode, dt, wdt)
        if e["unit_id"] in by_id:
            by_id[e["unit_id"]]["enabled"] = True
        else:
            doc["watch"].append(e)
            added += 1
    # Do NOT rewrite the file's `_`-prefixed documentation or `_prefix_keying_params` here: arming is an
    # append, and a launch job silently replacing the config guard's required-key list with whatever this
    # version of the code happened to think is exactly how a guard stops guarding.
    save_watch(doc, path)
    problems = wdv.validate(doc)
    if problems:
        raise SystemExit("[arm] REFUSING to write a watch list the config guard rejects: %r. The entry the "
                         "launch just armed would make a relaunch resume a different trajectory." % problems)
    print(f"[arm] mode={mode} dt={dt} warmup_dt={wdt}: {added} new entr(ies), "
          f"{len(enabled_entries(doc))} enabled in total")
    return doc


def verify_armed(mode, path=None, timestep_fs=None, warmup_timestep_fs=None):
    """Assert that every unit of `mode` is present AND enabled in the watch list. Raises otherwise.

    WHY A SEPARATE READ-BACK, when `arm()` just wrote the file. Because the failure this catches is not
    arm() misbehaving — it is the file being changed AFTERWARDS by something that had no idea a leg was
    running. That happened on 2026-07-25: the launch job armed the probe and committed it, and a later edit
    to the same file (adding the config-guard schema) rewrote `"watch"` to `[]` and pushed. The watchdog's
    only input then said there was nothing to watch, while a billed GPU leg ran unwatched — and it would
    have reported "idle" with a green tick.

    The config guard cannot catch this: an EMPTY list is a legitimate state (nothing running), so it must
    stay a no-op. Only something that knows which units were just launched can tell "nothing to watch" from
    "the thing I am watching went missing". That is this function, and it belongs in the launch path.
    """
    dt = str(timestep_fs or os.environ.get("TVAST_TIMESTEP_FS") or tv.DEFAULT_TIMESTEP_FS)
    wdt = str(warmup_timestep_fs or os.environ.get("TVAST_WARMUP_TIMESTEP_FS")
              or tv.DEFAULT_WARMUP_TIMESTEP_FS)
    doc = load_watch(path)
    armed = {w.get("unit_id") for w in enabled_entries(doc)}
    want = {tv.unit_id(l, s, d, dt, wdt, mode) for (l, s, d) in tv.units_for(mode)}
    missing = sorted(want - armed)
    if missing:
        raise SystemExit(
            "[verify-armed] THE WATCH LIST DOES NOT COVER THE UNITS JUST LAUNCHED: %s. A leg is billing "
            "with nothing watching it. Re-run --arm %s and commit before walking away." % (missing, mode))
    print("[verify-armed] %s: all %d unit(s) present and enabled in the watch list" % (mode, len(want)))
    return sorted(want)


def _s3():
    import boto3
    return boto3.client("s3")


def _read_json_key(bucket, key, default=None):
    try:
        return json.loads(_s3().get_object(Bucket=bucket, Key=key)["Body"].read().decode())
    except Exception:  # noqa: BLE001 — absent state is a legitimate first pass
        return default


def _write_json_key(bucket, key, doc):
    try:
        _s3().put_object(Bucket=bucket, Key=key, Body=json.dumps(doc, indent=2).encode())
        return True
    except Exception as e:  # noqa: BLE001
        print(f"::warning::watchdog state write failed for {key}: {type(e).__name__}: {e}")
        return False


def _annotate(level, title, msg):
    print(f"::{level} title={title}::{msg}")


def tick(path=None, dry_run=False, bucket=None, prefix=None, ref=None):
    """One watchdog pass over the enabled entries. Returns the number of alerts raised."""
    b = bucket or tv.DEFAULT_BUCKET
    p = (prefix or tv.RESULT_PREFIX).rstrip("/")
    doc = load_watch(path)
    # CONFIG GUARD, reusing the module Lane 3 extracted rather than re-implementing it. An entry missing a
    # prefix-keying parameter would make a relaunch resume a DIFFERENT trajectory than the one being watched.
    # It lives in a FILE, not inline in the workflow, for a reason worth repeating: the GCP watchdog's guard
    # was an inline `python3 -c` whose lines sat at column 0, which dedented them out of the `run: |` block
    # and made the whole workflow unparseable — and GitHub's symptom for that is a 422 about a MISSING
    # TRIGGER, while a `schedule:` cron on an unparseable file simply never fires. The guard meant to stop the
    # watchdog acting on bad config stopped the watchdog running at all, silently.
    problems = wdv.validate(doc)
    for leg, direction, missing in problems:
        _annotate("error", "TVAST WATCHDOG CONFIG INVALID",
                  f"{leg} dir={direction} is missing prefix-keying param(s) {','.join(missing)} — a relaunch "
                  f"would resume a DIFFERENT commit prefix. Refusing to act.")
    if problems:
        return len(problems)
    entries = enabled_entries(doc)
    print(f"enabled watch entries: {len(entries)} (dry_run={dry_run})")
    if not entries:
        _annotate("notice", "TVAST WATCHDOG idle",
                  "No enabled entries in ternary-vast-watch.json — nothing to watch.")
        return 0

    recs = tv.leg_records(b, p)
    key = os.environ.get("VAST_API_KEY")
    insts = []
    if key:
        try:
            insts = [i for i in _vast_request("GET", "/instances/", key).get("instances", [])
                     if (i.get("label") or "").startswith(tv.LABEL_PREFIX)]
        except Exception as e:  # noqa: BLE001
            # Without the instance list we cannot tell DIED from RUNNING, and guessing DIED would relaunch
            # on top of a live leg — two hosts on one commit prefix. Refuse the pass instead.
            _annotate("error", "TVAST WATCHDOG BLIND",
                      f"could not list Vast instances ({type(e).__name__}: {e}) — refusing to act this "
                      f"pass rather than risk relaunching on top of a live leg.")
            return 1
    else:
        _annotate("error", "TVAST WATCHDOG BLIND",
                  "VAST_API_KEY absent — cannot tell a live leg from a dead one; taking no action.")
        return 1

    alerts = 0
    day = time.strftime("%Y%m%d", time.gmtime())
    for e in entries:
        uid = e["unit_id"]
        print(f"=============== {uid} ===============")
        rec = recs.get(uid) or {}
        has_result = rec.get("status") == "done"
        has_failed = rec.get("status") == "failed"

        inst = next((i for i in insts if tv.label_matches_unit(i.get("label"), uid)), None)
        age_min = 0.0
        if inst:
            try:
                age_min = (time.time() - float(inst.get("start_date") or time.time())) / 60.0
            except (TypeError, ValueError):
                age_min = 0.0

        phase, it, scalar = tv.committed_progress(uid, b, p)
        if scalar < 0:
            # A listing failure is NOT zero progress; treating it as zero would manufacture a SETUP_STALL.
            _annotate("warning", "TVAST WATCHDOG progress unreadable",
                      f"{uid} — could not list the commit store this pass; leaving the counters alone.")
            continue

        # THE PHASE MARKER AND THE LOG, read on every pass and not only when something looks wrong. They are
        # what turn `scalar=0` from an ambiguous number into an answerable question: the counter is only
        # meaningful inside a phase that commits, and `phase_and_log` is the only thing that knows which
        # phase the leg is actually in. Failure here must never abort the entry — an unreadable marker is a
        # missing diagnosis, not a missing verdict.
        try:
            marker, marker_age, log_lines, log_age = tv.phase_and_log(uid, b, p)
        except Exception as ex:  # noqa: BLE001
            marker, marker_age, log_lines, log_age = None, None, [], None
            print(f"[diag] phase/log unreadable for {uid}: {type(ex).__name__}: {ex}")
        started = container_started_from_phase(marker, inst)

        pkey = f"{p}/watchdog/progress-{uid}.json"
        prev = _read_json_key(b, pkey, {}) or {}
        verdict, stall = classify(
            has_result=has_result, has_failed_record=has_failed,
            instance_alive=inst is not None, instance_age_min=age_min,
            container_started=started,
            progress_scalar=scalar, prev_scalar=int(prev.get("scalar") or 0),
            prev_stall=int(prev.get("stall") or 0))
        pstr = f"{phase}/{it}" if phase else "none (stage/pre-equil/setup/minimise)"
        print(f"verdict={verdict} progress={pstr} scalar={scalar} prev={prev.get('scalar')} "
              f"stall={stall} instance={inst.get('id') if inst else None} age={age_min:.0f}min")
        if inst is not None:
            print(f"  phase_marker={marker!r} marker_age="
                  f"{f'{marker_age:.0f}min' if marker_age is not None else 'n/a'} log_age="
                  f"{f'{log_age:.0f}min' if log_age is not None else 'n/a'} container_started={started}")
        if not dry_run:
            _write_json_key(b, pkey, {"scalar": scalar, "stall": stall,
                                      "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                      "phase": pstr, "verdict": verdict})

        if verdict == "DONE":
            _annotate("notice", "TVAST WATCHDOG DONE",
                      f"{uid} — leg.json is in S3 (dG_morph={rec.get('dg_morph_kcal')}, "
                      f"NaN={rec.get('nan_seen')}). Set enabled=false for this entry.")
            continue
        if verdict == "FAILED":
            alerts += 1
            tail = (rec.get("log_tail") or [])[-3:]
            _annotate("error", "TVAST WATCHDOG LEG FAILED",
                      f"{uid} — the leg RAN and recorded status=failed (rc={rec.get('rc')}, "
                      f"NaN_seen={rec.get('nan_seen')}) at {rec.get('updated_utc')}. NOT relaunching: it "
                      f"would fail the same way and, uncapped, would buy a full-length rental per attempt. "
                      f"Diagnose, then clear the record or disable the entry. Last log lines: {tail}")
            continue
        if verdict == "RUNNING":
            _annotate("notice", "TVAST WATCHDOG RUNNING",
                      f"{uid} — advancing at {pstr} on instance {inst.get('id')} "
                      f"({inst.get('gpu_name')}, up {age_min:.0f} min). Leaving it alone.")
            continue
        if verdict == "SETUP_STALL":
            alerts += 1
            # THE ALERT CARRIES ITS OWN DIAGNOSIS. It used to carry a guess list — "check the CUDA probe,
            # the charge cache, minimise steps and GPU utilisation" — emitted identically whatever the leg
            # was actually doing, and on 2026-07-27 every item on it was wrong for the leg it fired on. The
            # refusal to auto-relaunch is unchanged and deliberate; only the explanation is now derived.
            headline, hints = setup_stall_diagnosis(
                phase_text=marker, marker_age_min=marker_age, log_age_min=log_age, log_lines=log_lines,
                container_started=started, instance_age_min=age_min)
            _annotate("error", "TVAST WATCHDOG SETUP STALL",
                      f"{uid} — instance {inst.get('id')} up {age_min:.0f} min with ZERO committed FEP "
                      f"iterations (grace {SETUP_GRACE_MIN:.0f} min). {headline}. {hints} NOT relaunching "
                      f"— a relaunch would hit the same thing and pay for it again.")
            continue
        if verdict == "STALLED":
            alerts += 1
            # STALLED implies scalar > 0, so this leg HAS committed and is therefore in a committing phase —
            # the guess list genuinely fits here, which is why it survives. What is added is the log's own
            # freshness, because "the sampler is wedged" and "the container died with its uploader" present
            # identically through a frozen counter and are fixed differently.
            stale = (isinstance(log_age, (int, float)) and log_age > LOG_STALE_MIN)
            _annotate("error", "TVAST WATCHDOG STALLED",
                      f"{uid} — instance {inst.get('id')} is up but the committed iteration has been "
                      f"frozen at {pstr} for {stall} consecutive passes. The MD is not advancing. Phase "
                      f"marker {phase_head(marker)!r}; run.log last written "
                      f"{f'{log_age:.0f} min ago' if log_age is not None else 'unknown'}"
                      + (" — STALE, so suspect the container/uploader rather than the sampler"
                         if stale else " — fresh, so the container is alive and the sampler is the suspect")
                      + f". NOT relaunching — diagnose (NaN, run log) before spending more.")
            continue

        # DIED: no result, no instance. Relaunch, capped.
        ckey = f"{p}/watchdog/relaunch-{day}-{uid}.json"
        cnt = int((_read_json_key(b, ckey, {}) or {}).get("count") or 0)
        ok, why = should_relaunch(verdict, cnt, e.get("max_relaunches_per_day", 8))
        if not ok:
            alerts += 1
            _annotate("error", "TVAST WATCHDOG CAPPED",
                      f"{uid} — died again but {why}. NOT relaunching; needs a human.")
            continue
        if dry_run:
            _annotate("notice", "TVAST WATCHDOG would-relaunch",
                      f"{uid} — died (no result, no instance), {why}. dry_run=1 so taking no action.")
            continue
        print(f"relaunching {uid} ({why}) — resumes from the last committed checkpoint")
        try:
            # DELEGATE to the launcher. It already skips finished/in-flight units, excludes blocked
            # machines, spreads one unit per machine, and keys the commit prefix by dt — so a relaunch
            # resumes rather than restarts, and cannot double-book a live unit.
            # ★ THE ENTRY'S OWN git_branch, NOT THE RUNNER'S. This argument was missing, and its absence made
            # the watch list's most carefully documented field decorative: `build_jobspec` fell back to
            # `os.environ["GIT_BRANCH"]`, which this workflow sets from `github.ref_name` — and a `schedule:`
            # only fires from the DEFAULT branch, so every cron relaunch pulled **main's** code onto a
            # feature branch's checkpoint. The entry records the branch precisely so that cannot happen.
            handles = tv.submit(mode=e["mode"], timestep_fs=e["timestep_fs"],
                                warmup_timestep_fs=e["warmup_timestep_fs"],
                                git_branch=e.get("git_branch"),
                                legs=[(e["leg_id"], e["seed"], e["direction"])])
            if handles:
                _write_json_key(b, ckey, {"count": cnt + 1, "unit_id": uid,
                                          "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
                _annotate("notice", "TVAST WATCHDOG RELAUNCHED",
                          f"{uid} — was dead (no result, no instance); rented instance "
                          f"{handles[0].get('instance')} on machine {handles[0].get('machine_id')}, "
                          f"{why}. Resumes from the last committed checkpoint.")
            else:
                alerts += 1
                _annotate("error", "TVAST WATCHDOG RELAUNCH PRODUCED NOTHING",
                          f"{uid} — died and the relaunch rented no host (no rentable offer, or every "
                          f"candidate machine is on the blocked list). Needs a human.")
        except Exception as ex:  # noqa: BLE001 — one entry must not abandon the others
            alerts += 1
            _annotate("error", "TVAST WATCHDOG RELAUNCH FAILED",
                      f"{uid} — died AND the relaunch raised {type(ex).__name__}: {ex}. Needs a human.")
    print(f"watchdog pass complete; {alerts} alert(s)")
    return alerts


def main(argv=None):
    ap = argparse.ArgumentParser(description="Session-independent watchdog for the Vast ternary lane")
    ap.add_argument("--arm", metavar="MODE", help="register every unit of MODE in the watch list")
    ap.add_argument("--tick", action="store_true", help="run one watchdog pass")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--disable", metavar="UNIT_ID", help="set enabled=false for one entry")
    ap.add_argument("--verify-armed", metavar="MODE",
                    help="assert every unit of MODE is present and enabled in the watch list; exit non-zero "
                         "otherwise. Run it in the launch path, AFTER the commit.")
    a = ap.parse_args(argv)
    if a.verify_armed:
        verify_armed(a.verify_armed)
        return 0
    if a.arm:
        arm(a.arm)
        return 0
    if a.disable:
        doc = load_watch()
        for w in doc.get("watch", []):
            if w.get("unit_id") == a.disable:
                w["enabled"] = False
        save_watch(doc)
        print(f"[disable] {a.disable}")
        return 0
    alerts = tick(dry_run=a.dry_run)
    # A non-zero exit makes GitHub send its own workflow-failure notification — the alert path that does
    # not depend on an agent, a session, or anyone thinking to open a log. RUNNING/DONE stay green.
    return 1 if alerts else 0


if __name__ == "__main__":
    raise SystemExit(main())
