#!/usr/bin/env python3
"""THE STEP 1 LIVENESS SHAKEOUT — does the heartbeat actually reach S3, from the real script? $0, no GPU.

★ WHY A SHAKEOUT AT ALL, AND WHY IT IS NOT OPTIONAL. CLAUDE.md §6: `mode=smoke` -> one real leg -> fleet. The
unit tests in `tests/test_step1_liveness.py` execute the heartbeat with a STUB `aws`, which proves the loop's
timing and its three termination nets but says nothing about whether a real `aws s3 cp` from inside the real
image, against the real bucket, lands an object the guard can then read. Eighteen units are live; shipping an
unshaken guard under them is how a guard reaps a healthy fleet.

★★ AND IT WRITES TO A SCRATCH PREFIX, WHICH IS THE SINGLE MOST IMPORTANT LINE IN THIS FILE. The pipeline's
first act is `mark boot` -> a PUT to `$RESULT_S3/phase.txt`. Pointed at the production prefix that would
overwrite a live unit's phase marker with `boot`, and the monitor would read the fleet as restarted.
`SMOKE_PREFIX` is a distinct prefix with its own unit id, and `_guard_the_prefix` refuses to run if it could
collide — checked BEFORE a single byte is written.

THREE STAGES, in the order the rule asks for, each answering something the previous one cannot:

  smoke   the real `_PREAMBLE` with the network-needing lines stubbed. Does run.log appear in S3, and does
          its LastModified ADVANCE while the pipeline sits in a phase that produces NO output? That is the
          false-positive question — the one where being wrong destroys a healthy leg — and it is measured by
          polling the real object from outside the container while the run is in flight.
  leg     the real `_PREAMBLE` inside the real ONSTART composition (`gpu_backend._vast_onstart`'s ordering:
          crash-loop brake -> ct_selfstop EXIT trap -> the command), run three times. Does
          `attempts/run-<UTC>.log` accumulate one key per container start, in the shape
          `vast_idle_guard._ATTEMPT_RE` parses? And does the brake trip on the third?
  verdict feed that S3 evidence, gathered through the LANE'S OWN helpers, to `classify_idle`. A fresh
          heartbeat must be SPARED and a silent one CONDEMNED — both directions, because a guard that cannot
          condemn anything reports success while measuring nothing.

Usage (inside the parity image, with AWS creds):
    SMOKE_STAGE=smoke   python step1_liveness_smoke.py
    SMOKE_STAGE=leg     python step1_liveness_smoke.py
    SMOKE_STAGE=verdict python step1_liveness_smoke.py
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import congeneric_fanout_vast as cfv  # noqa: E402
import vast_idle_guard as vig  # noqa: E402

OUT = os.path.join(HERE, "step1-liveness-shakeout.json")

PROD_PREFIX = cfv.RESULT_PREFIX          # captured BEFORE the redirect below, so the guard has a real target
SMOKE_PREFIX = os.environ.get("SMOKE_PREFIX", "nr4a3-step1-fanout/liveness-shakeout")
SMOKE_UNIT = os.environ.get("SMOKE_UNIT", "shakeout_unit")
SYNC_S = float(os.environ.get("SMOKE_SYNC_S", "5"))


def _guard_the_prefix():
    """Refuse to run if the scratch namespace could collide with a live unit's artifacts."""
    prod, scratch = PROD_PREFIX.rstrip("/"), SMOKE_PREFIX.rstrip("/")
    if scratch == prod or scratch.startswith(prod + "/"):
        raise SystemExit(f"[s1f-smoke] REFUSING: SMOKE_PREFIX {scratch!r} sits inside the production result "
                         f"namespace {prod!r} — the first `mark boot` would overwrite a live unit's phase "
                         f"marker.")
    if any(u["unit_id"] == SMOKE_UNIT for u in cfv.default_units()):
        raise SystemExit(f"[s1f-smoke] REFUSING: SMOKE_UNIT {SMOKE_UNIT!r} is a REAL fan-out unit.")
    # Point the LANE'S OWN helpers at the scratch namespace, so the verdict stage really does gather evidence
    # the way `mode_collect` gathers it rather than through a parallel reimplementation.
    cfv.RESULT_PREFIX = scratch


def _result_s3():
    return f"s3://{cfv._require_bucket()}/{SMOKE_PREFIX.rstrip('/')}/{SMOKE_UNIT}"


_STUBBED = (
    'curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz',
    "cd Rare-cancers-*/research/modalities",
    '$AWS s3 cp "s3://$BUCKET/$STAGE_PREFIX/" "$IN/" --recursive --only-show-errors',
    'test -s "$IN/ligand/docked_$RECEPTOR.sdf" || { echo "[s1f] FATAL: staged ligand SDF missing"; exit 3; }',
    'test -s "$IN/receptor/$RECEPTOR-opened.pdb" || { echo "[s1f] FATAL: staged receptor PDB missing"; '
    'exit 3; }',
)


def _stub_pipeline(hold_s):
    """`_PREAMBLE` verbatim, with only the network/GB-sized lines replaced by a wait.

    ★ THE PREAMBLE TEXT IS NOT RE-TYPED — it is sliced from the shipped module, so what is shaken out is what
    ships, and a stale stub RAISES rather than silently exercising a different script. What is replaced are
    the repo pull and the staged-tree download; none of them touch the heartbeat, and the silent wait that
    replaces them is the HARDER test, because a phase that emits nothing is exactly what would false-positive.
    """
    p = cfv._PREAMBLE
    for line in _STUBBED:
        if line not in p:
            raise SystemExit(f"[s1f-smoke] _PREAMBLE no longer contains {line!r} — the stub is stale and "
                             f"would shake out the wrong script. Fix the slice, do not loosen it.")
        p = p.replace(line, ": # stubbed for the liveness shakeout")
    return p + (f'\nmark stage-stub\nsleep {hold_s}\n'
                f'mark leg-complex-running\nsleep {hold_s}\nmark done\n')


def _env(extra=None):
    return {**os.environ,
            "RESULT_S3": _result_s3(), "BUCKET": cfv._require_bucket(),
            "STAGE_PREFIX": cfv.STAGE_PREFIX, "RECEPTOR": "nr4a3",
            "S1F_SYNC_S": str(SYNC_S), **(extra or {})}


def _run(script, extra=None, timeout=900):
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=timeout,
                          env=_env(extra))


def _keys(s3, bucket):
    out, tok = [], None
    prefix = f"{SMOKE_PREFIX.rstrip('/')}/{SMOKE_UNIT}/"
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix}
        if tok:
            kw["ContinuationToken"] = tok
        page = s3.list_objects_v2(**kw)
        out += [o["Key"] for o in page.get("Contents", [])]
        if not page.get("IsTruncated"):
            return sorted(out)
        tok = page.get("NextContinuationToken")


def stage_smoke(s3, bucket):
    """★ THE FALSE-POSITIVE TEST. Run the pipeline IN THE BACKGROUND and poll run.log's LastModified from
    outside while it sits in a phase that writes nothing. Distinct mtimes are the proof that a CPU-only phase
    keeps the heartbeat alive; one mtime would mean the guard sees a healthy leg as wedged."""
    hold = max(12.0, SYNC_S * 4)
    key = f"{SMOKE_PREFIX.rstrip('/')}/{SMOKE_UNIT}/run.log"
    p = subprocess.Popen(["bash", "-c", _stub_pipeline(hold)], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, env=_env())
    mtimes, deadline = [], time.time() + 2 * hold + 30
    while p.poll() is None and time.time() < deadline:
        try:
            lm = s3.head_object(Bucket=bucket, Key=key)["LastModified"].isoformat()
            if not mtimes or mtimes[-1] != lm:
                mtimes.append(lm)
        except Exception:  # noqa: BLE001 — not yet written is a normal early state
            pass
        time.sleep(max(1.0, SYNC_S / 2.0))
    out = p.communicate(timeout=120)[0] or ""
    print(out[-4000:], flush=True)
    keys = _keys(s3, bucket)
    return {
        "rc": p.returncode, "sync_s": SYNC_S, "silent_phase_s": hold,
        "run_log_present": any(k.endswith("/run.log") for k in keys),
        "phase_txt_present": any(k.endswith("/phase.txt") for k in keys),
        # THE MEASUREMENT. >= 3 distinct mtimes across two silent phases means the object was re-PUT while
        # the pipeline produced no output at all.
        "distinct_run_log_mtimes_during_the_run": len(mtimes),
        "mtimes": mtimes,
        "advanced_during_a_silent_phase": len(mtimes) >= 3,
        "keys": keys,
    }


def stage_leg(s3, bucket):
    """The real ONSTART composition, three times. The archive must count container starts in a shape the
    guard parses, and the crash-loop brake must trip on the third rather than on a legitimate resume."""
    from gpu_backend import _VAST_CRASHLOOP_BRAKE, _VAST_SELFSTOP
    hold = max(6.0, SYNC_S * 2)
    starts_file = "/tmp/s1f_smoke_starts"
    try:
        os.remove(starts_file)
    except OSError:
        pass
    # The brake HOLDS IDLE forever when it trips — correct on a rental, useless in a test — so that one line
    # becomes an observable exit. Everything else, including the trap and its ordering, is verbatim.
    brake = _VAST_CRASHLOOP_BRAKE.replace("while true; do sleep 3600; done", "echo BRAKE_TRIPPED; exit 0")
    body = "\n".join([brake, _VAST_SELFSTOP, "trap ct_selfstop EXIT", _stub_pipeline(hold)])
    runs = []
    for i in range(3):
        r = _run(body, {"CT_STARTS": starts_file, "CT_WIN": "900", "CT_MAX": "3"})
        runs.append({"n": i + 1, "rc": r.returncode,
                     "brake_tripped": "BRAKE_TRIPPED" in r.stdout,
                     "selfstop_ran": "[selfstop] job exited rc=" in r.stdout,
                     "archived_previous_attempt": "archived the previous attempt" in r.stdout})
        print(f"[s1f-smoke] onstart run {i + 1}: {runs[-1]}", flush=True)
    attempts = [k for k in _keys(s3, bucket) if "/attempts/run-" in k]
    ages = vig.start_ages_min(s3, bucket, f"{SMOKE_PREFIX.rstrip('/')}/{SMOKE_UNIT}/attempts/")
    return {
        "runs": runs,
        "attempt_keys": attempts,
        "every_attempt_key_parses": bool(attempts) and all(
            vig._ATTEMPT_RE.search("/" + k) for k in attempts),
        "start_ages_min": ages,
        "brake_tripped_on_the_third_start_only": [r["brake_tripped"] for r in runs] == [False, False, True],
    }


def stage_verdict(s3, bucket):
    """Both directions, on the evidence actually sitting in S3."""
    age = cfv._log_age_min(s3, bucket, SMOKE_UNIT)
    starts = vig.start_ages_min(s3, bucket, f"{SMOKE_PREFIX.rstrip('/')}/{SMOKE_UNIT}/attempts/")
    live, live_why = vig.classify_idle(instance_running=True, container_started=True, gpu_util=0.0,
                                       progress_advanced=False, log_age_min=age, start_ages_min=[],
                                       instance_age_min=60)
    stale, stale_why = vig.classify_idle(
        instance_running=True, container_started=True, gpu_util=0.0, progress_advanced=False,
        log_age_min=(None if age is None else age + vig.LOG_SILENCE_MIN + 1),
        start_ages_min=[], instance_age_min=60)
    churn, churn_why = vig.classify_idle(instance_running=True, container_started=True, gpu_util=0.0,
                                         progress_advanced=False, log_age_min=age, start_ages_min=starts,
                                         instance_age_min=60)
    return {
        "log_age_min": age, "start_ages_min": starts,
        "fresh_heartbeat": {"verdict": live, "why": live_why, "spared": not vig.should_destroy(live)},
        "if_it_went_silent": {"verdict": stale, "why": stale_why,
                              "condemned": vig.should_destroy(stale)},
        "observed_restart_churn": {"verdict": churn, "why": churn_why,
                                   "condemned": vig.should_destroy(churn)},
        # A guard that only ever spares is a guard that measures nothing. BOTH must hold.
        "both_directions_work": (not vig.should_destroy(live)) and vig.should_destroy(stale),
    }


_STAGES = {"smoke": stage_smoke, "leg": stage_leg, "verdict": stage_verdict}


def main():
    _guard_the_prefix()
    bucket, s3 = cfv._require_bucket(), cfv._s3()
    stage = (os.environ.get("SMOKE_STAGE") or "smoke").strip()
    if stage not in _STAGES:
        raise SystemExit(f"[s1f-smoke] unknown SMOKE_STAGE {stage!r}; expected one of {sorted(_STAGES)}")
    print(f"[s1f-smoke] stage={stage} scratch={_result_s3()} sync={SYNC_S}s", flush=True)
    doc = _STAGES[stage](s3, bucket)

    prev = {}
    if os.path.exists(OUT):
        try:
            prev = json.load(open(OUT))
        except Exception:  # noqa: BLE001
            prev = {}
    prev[stage] = doc
    prev["_what"] = ("step 1 liveness shakeout — smoke -> one real onstart -> guard verdict (CLAUDE.md §6), "
                     "against a SCRATCH S3 prefix that cannot touch a live unit")
    prev["_scratch_prefix"] = _result_s3()
    with open(OUT, "w") as f:
        json.dump(prev, f, indent=2, default=str)
    print(json.dumps(doc, indent=2, default=str), flush=True)
    print(f"[s1f-smoke] wrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
