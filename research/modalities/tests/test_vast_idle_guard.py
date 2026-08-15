#!/usr/bin/env python3
"""Guards for the anti-idle reap — the thing that decides whether a rented, `running`, GPU-idle Vast box is
crash-looping or quietly parameterising a 146k-atom system.

TWO FAILURE MODES, AND THE SECOND ONE IS THE EXPENSIVE ONE.
  * MISSING a wedge costs one rental's worth of billed idle — measured at ~53 min / ~$0.35 on 2026-07-27,
    and bounded only by a 22 h runtime backstop.
  * KILLING A HEALTHY LEG costs the whole setup phase AND the rental that has to redo it, and it does so
    silently, because a reaped box looks exactly like a preempted one. So the false-positive tests below are
    the load-bearing ones: `test_a_long_cpu_only_setup_phase_is_never_reaped` is the single most important
    assertion in this file, and every threshold in the module is chosen to keep it true.
"""
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import vast_idle_guard as vig  # noqa: E402


def _ev(**kw):
    """A healthy-ish baseline: `running`, container marked, GPU idle, log fresh, one container start."""
    base = dict(instance_running=True, container_started=True, gpu_util=0.0, progress_advanced=False,
                log_age_min=1.5, start_ages_min=[], instance_age_min=120.0)
    base.update(kw)
    return base


# =============================================================================================================
# THE FALSE-POSITIVE SIDE — these are the assertions that stop this guard costing more than the bug
# =============================================================================================================
def test_a_long_cpu_only_setup_phase_is_never_reaped():
    """★ THE ONE THAT MATTERS. A ternary leg stages (~15 min), then openff/interchange parameterises a
    ~146k-atom solvated hybrid (CPU+RAM bound, tens of minutes), then minimises. Through all of it `gpu_util`
    is 0 and the commit store reads zero, because nothing has committed yet — the exact signature this guard
    is looking for, on a leg that is perfectly healthy. What separates them is that the host is still WRITING:
    the sync loop PUTs run.log every 2 min. Two hours of it must not be touched."""
    for age in (20.0, 45.0, 90.0, 121.0):
        v, why = vig.classify_idle(**_ev(instance_age_min=age, gpu_util=0.0, log_age_min=1.9,
                                         progress_advanced=False))
        assert not vig.should_destroy(v), f"a {age:.0f}-min GPU-idle setup phase was condemned: {v} — {why}"


def test_gpu_idle_alone_can_never_condemn_a_box():
    """The tempting rule — 'GPU idle for N minutes -> destroy' — is the rule this module refuses to
    implement. Sweep the whole utilisation range with every other signal healthy: nothing may be destroyed."""
    for util in (0.0, 0.0001, 1.0, 4.9):
        v, _ = vig.classify_idle(**_ev(gpu_util=util))
        assert not vig.should_destroy(v)


def test_a_single_restart_is_a_resume_not_a_crash_loop():
    """A spot preemption plus the collect nudge legitimately restarts a container, and the leg is SUPPOSED to
    resume from its checkpoint. One (or two) archived attempts must not read as a loop."""
    for starts in ([2.0], [2.0, 9.0]):
        v, _ = vig.classify_idle(**_ev(start_ages_min=starts))
        assert not vig.should_destroy(v)


def test_old_restarts_outside_the_window_do_not_accumulate():
    """`attempts/` is durable and grows over a unit's whole life across days. Counting all of it would make
    every long-lived unit look like a crash-loop; only starts inside the window count."""
    v, _ = vig.classify_idle(**_ev(start_ages_min=[400.0, 900.0, 1500.0, 3000.0]))
    assert not vig.should_destroy(v)


def test_a_measured_advance_overrides_every_other_signal():
    """`watchdog_policy` already encodes this precedence and it is repeated here for the same reason: a
    counter that went UP is direct evidence the GPU did the work, and nothing inferred may overrule it. Hand
    it the worst-looking box imaginable — silent log, restart churn — and an advance still saves it."""
    v, _ = vig.classify_idle(**_ev(progress_advanced=True, log_age_min=600.0,
                                   start_ages_min=[0.5, 1.0, 1.5, 2.0]))
    assert v == vig.WORKING and not vig.should_destroy(v)


def test_a_box_too_young_to_judge_is_left_alone():
    v, _ = vig.classify_idle(**_ev(instance_age_min=4.0, log_age_min=None, container_started=False))
    assert v == vig.COLD_START and not vig.should_destroy(v)


def test_an_unreadable_attempts_listing_is_not_evidence_of_no_restarts():
    """None vs [] is load-bearing: None means the S3 listing failed. Reading it as 'no restarts' would
    silently disable the crash-loop channel; reading it as 'many restarts' would destroy on an S3 blip.
    It must do neither — the clause is skipped and the other channel decides."""
    v, _ = vig.classify_idle(**_ev(start_ages_min=None))
    assert not vig.should_destroy(v)


def test_a_non_running_instance_is_somebody_elses_clause():
    """`collect` already owns stopped boxes (nudge, capacity refusal, stopped-too-long) and frozen image
    pulls. Two clauses acting on one box is how a capacity wait gets destroyed as a wedge."""
    v, _ = vig.classify_idle(**_ev(instance_running=False, log_age_min=999.0))
    assert v == vig.UNKNOWN and not vig.should_destroy(v)


def test_a_container_that_never_started_is_inside_the_cold_start_grace():
    v, _ = vig.classify_idle(**_ev(container_started=False, instance_age_min=30.0, log_age_min=None))
    assert v == vig.COLD_START and not vig.should_destroy(v)


# =============================================================================================================
# THE TRUE-POSITIVE SIDE — each test is one shape actually observed on a billed instance
# =============================================================================================================
def test_the_2026_07_27_dead_credential_wedge_is_caught():
    """THE INCIDENT. An exposed key was rotated at 7:27 AM ET; both 5a-KS containers lost their S3 write path
    mid-leg, crash-looped on `stage cache MISS -> FAILED at staging -> Killed` every 13-30 s, and stayed
    `actual_status: running` with `gpu_util: 0.0` for ~53 min while billing. Nothing was written, so the
    ONLY external signal is the silence: run.log frozen at 7:27."""
    v, why = vig.classify_idle(**_ev(log_age_min=28.0, gpu_util=0.0, start_ages_min=[],
                                     instance_age_min=180.0))
    assert v == vig.WEDGED and vig.should_destroy(v), why
    assert "write path" in why


def test_a_crash_loop_whose_s3_still_works_is_caught_by_restart_churn():
    """The other half of the same failure class, and the reason there are two channels. When the store is
    healthy the log keeps being rewritten — so silence never fires — but every container start archives the
    previous attempt, and the timestamp is in the key. Seventeen 168-byte attempt logs is what this looked
    like on the first 5a-KS smoke (2026-07-26)."""
    v, why = vig.classify_idle(**_ev(log_age_min=0.4, start_ages_min=[0.2, 0.7, 1.4, 2.0, 2.6]))
    assert v == vig.CRASH_LOOP and vig.should_destroy(v), why


def test_the_two_channels_cover_each_others_blind_spot():
    """Stated as a test because it is the whole design: the dead-credential wedge is invisible to the restart
    channel (nothing can be archived) and the live-S3 crash-loop is invisible to the silence channel (the log
    keeps moving). Neither alone is sufficient; both together are."""
    dead_cred = _ev(log_age_min=40.0, start_ages_min=[])           # nothing archived — churn channel blind
    live_loop = _ev(log_age_min=0.3, start_ages_min=[0.1, 0.9, 1.8])  # log fresh — silence channel blind
    assert vig.classify_idle(**dead_cred)[0] == vig.WEDGED
    assert vig.classify_idle(**live_loop)[0] == vig.CRASH_LOOP


def test_a_busy_gpu_does_not_save_a_host_that_can_no_longer_write():
    """★ The one place a high `gpu_util` is NOT a reprieve, and it is deliberate. A host that cannot write
    cannot checkpoint, so those GPU cycles are being computed into a void — the driver aborts at its next
    commit boundary anyway. A healthy leg never reaches this clause because it commits every ~40 iterations,
    far inside one poll, so `progress_advanced` catches it first."""
    v, _ = vig.classify_idle(**_ev(gpu_util=97.0, log_age_min=45.0, progress_advanced=False))
    assert v == vig.WEDGED and vig.should_destroy(v)
    # ...but with the log still moving, the same busy GPU is a reprieve.
    v2, _ = vig.classify_idle(**_ev(gpu_util=97.0, log_age_min=1.0))
    assert v2 == vig.WORKING


def test_a_running_box_that_never_marks_a_phase_is_eventually_condemned():
    """The hole that made the cold-start branch unbounded: if the object store is unreachable from the FIRST
    second of a rental, the phase marker never lands, `container_started` reads False forever and an
    unbounded COLD_START would babysit a crash-looping box all the way to the 22 h runtime backstop.

    Safe against LANE 21's 2 h 57 min image pull for a STRUCTURAL reason rather than a lucky threshold: Vast
    reports `actual_status: loading` during a pull, which the `instance_running` clause excludes outright."""
    v, _ = vig.classify_idle(**_ev(container_started=False, instance_age_min=vig.SETUP_GRACE_MIN + 1,
                                   log_age_min=None))
    assert v == vig.WEDGED and vig.should_destroy(v)
    v2, _ = vig.classify_idle(**_ev(container_started=False, instance_age_min=vig.SETUP_GRACE_MIN - 1,
                                    log_age_min=None))
    assert v2 == vig.COLD_START and not vig.should_destroy(v2)


def test_only_three_verdicts_can_ever_spend_a_destroy():
    """A caller must not invent its own mapping from verdict to action.

    UNIT_FAILED joined the set on 2026-07-27 and is deliberately a THIRD verdict rather than a reuse of
    WEDGED: the two share a remedy and mean opposite things about the host, and printing one as the other
    sent a diagnostic turn after a write path that was working."""
    assert set(vig.DESTROY_VERDICTS) == {vig.CRASH_LOOP, vig.WEDGED, vig.UNIT_FAILED}
    for v in (vig.WORKING, vig.COLD_START, vig.UNKNOWN, vig.WATCHING):
        assert not vig.should_destroy(v)


def test_a_leg_that_recorded_its_own_failure_is_never_reported_as_a_wedged_host():
    """The valB closure triangle, 2026-07-27. Both `calib_lo_to_lo2` legs exited rc=1, uploaded leg.json and
    run.log — successful S3 PUTs are the LAST lines of their logs — and then went quiet because there was
    nothing left to write. The silence clause condemned them as having "lost its write path". Right destroy,
    wrong mechanism, and the wrong mechanism is what a human then goes and investigates."""
    v, why = vig.classify_idle(**_ev(unit_failed=True, log_age_min=vig.LOG_SILENCE_MIN + 25,
                                     progress_advanced=False))
    assert v == vig.UNIT_FAILED and vig.should_destroy(v)
    assert "write path" not in why and "status=failed" in why


def test_a_dead_unit_is_not_held_alive_by_the_cold_start_floor():
    """A rental whose leg is already dead must not buy another hour of grace it can never use."""
    v, _ = vig.classify_idle(**_ev(unit_failed=True, instance_age_min=vig.MIN_INSTANCE_AGE_MIN - 1))
    assert v == vig.UNIT_FAILED


def test_the_reap_is_faster_than_every_backstop_it_replaces():
    """The property the whole exercise exists to buy: minutes, not hours. Compared against the tightest
    pre-existing reap on this lane (the 45-min stopped-box clause) and the one that would actually have
    caught the incident (the 22 h runtime backstop)."""
    import ternary_vast_launch as tv
    assert vig.LOG_SILENCE_MIN < tv.MAX_STOPPED_MIN
    assert vig.LOG_SILENCE_MIN < tv.MAX_INSTANCE_HOURS * 60 / 10


# =============================================================================================================
# EVIDENCE GATHERING — the attempt-archive keys are a durable count of container starts
# =============================================================================================================
class _FakeS3:
    def __init__(self, keys, boom=False):
        self._keys, self._boom = keys, boom

    def get_paginator(self, _op):
        outer = self

        class _P:
            def paginate(self, **kw):
                if outer._boom:
                    raise RuntimeError("AccessDenied")
                yield {"Contents": [{"Key": k} for k in outer._keys]}
        return _P()


def test_start_ages_are_parsed_from_the_key_not_from_s3_metadata():
    """The timestamp is IN the key (`attempts/run-<UTC>.log`), which is what lets one poll decide without
    any history — and which also survives an object being copied or re-uploaded."""
    import calendar
    import time
    now = calendar.timegm(time.strptime("20260727T120000Z", "%Y%m%dT%H%M%SZ"))
    keys = ["p/legs/u/attempts/run-20260727T115800Z.log",     # 2 min ago
            "p/legs/u/attempts/run-20260727T114500Z.log",     # 15 min ago
            "p/legs/u/attempts/run-20260727T100000Z.log",     # 120 min ago
            "p/legs/u/attempts/notes.txt",                    # not a start
            "p/legs/u/attempts/run-garbage.log"]              # unparseable
    ages = vig.start_ages_min(_FakeS3(keys), "b", "p/legs/u/attempts/", now=now)
    assert sorted(round(a) for a in ages) == [2, 15, 120]


def test_an_s3_listing_failure_returns_none_and_not_an_empty_list():
    assert vig.start_ages_min(_FakeS3([], boom=True), "b", "p/") is None
    assert vig.start_ages_min(_FakeS3([]), "b", "p/") == []


# =============================================================================================================
# THE HOST SIDE — what the container can and cannot do, RUN rather than asserted
# =============================================================================================================
@pytest.mark.skipif(not os.path.exists("/usr/bin/unshare") and not os.path.exists("/bin/unshare"),
                    reason="needs unshare to build a private PID namespace")
def test_the_selfstop_chain_cannot_end_a_container():
    """★ THE ROOT CAUSE, REPRODUCED RATHER THAN ARGUED (CLAUDE.md §4 — never a 'probably X').

    `gpu_backend._VAST_SELFSTOP` is an EXIT trap, and CLAUDE.md §6 used to call it a guarantee of no
    idle-GPU billing. Build the exact topology Vast runs — an init process as PID 1 of its own namespace, a
    CHILD shell playing the onstart script — and fire the old chain at it. If PID 1 survives, the container
    survives, and the GPU keeps billing; which is what both 5a-KS instances showed on 2026-07-27, staying
    `actual_status: running` across every read.

    Two independent kernel/POSIX rules make this unavoidable, not a quirk of one image:
      * `man 2 kill`: pid == -1 signals every permitted process "EXCEPT for process 1".
      * a PID-namespace init ignores any signal it has installed no handler for, and SIGKILL cannot be
        handled (SIGNAL_UNKILLABLE) — so `kill -9 1` returns SUCCESS and does nothing, which is precisely
        why the old `||` chain could never notice it had failed.
    """
    script = r"""
      ( while true; do sleep 0.3; done ) &
      bash -c '
        kill -9 1 2>/dev/null; echo "kill -9 1 rc=$?"
        sleep 0.2
        [ -d /proc/1 ] && echo SURVIVED_KILL_1
        kill -9 -1 2>/dev/null
      '
      sleep 0.4
      [ -d /proc/1 ] && echo SURVIVED_KILL_ALL
    """
    # ⚠ SKIP ONLY WHEN THE ENVIRONMENT CANNOT HOST THE EXPERIMENT — NEVER TO QUIET A FAILURE.
    # This test needs an unprivileged PID namespace with its own /proc. The GitHub runner does not provide
    # one (`unshare -fp --mount-proc` returns EMPTY stdout there), so the assertion below was failing for a
    # reason that has nothing to do with the claim being tested, and main stayed red. A red main is not
    # cosmetic — on 2026-07-27 another lane's red assertions took the whole step-1 supervision tick down with
    # them, because the tick gated on pytest before it measured a billing fleet. So an untestable
    # environment must SKIP, with the reason stated, and never fail and never be deleted.
    #
    # ★ THE PROBE IS DELIBERATELY NARROW so it cannot mask a real regression: it asserts only that a
    # namespace can be created AND that PID 1 exists inside it — the preconditions, not the behaviour. If
    # the probe succeeds and the assertions below then fail, that is a GENUINE finding about the self-stop
    # chain and it still turns the build red, which is the whole point of the test.
    probe = subprocess.run(["unshare", "-fp", "--mount-proc", "bash", "-c",
                            "[ -d /proc/1 ] && echo PIDNS_PROBE_OK"],
                           capture_output=True, text=True, timeout=60)
    if "PIDNS_PROBE_OK" not in probe.stdout:
        pytest.skip(
            "unprivileged PID namespaces are not usable in this environment, so the container topology this "
            "test recreates cannot be built here (probe `unshare -fp --mount-proc` -> "
            f"rc={probe.returncode}, stdout={probe.stdout!r}, stderr={probe.stderr.strip()[:200]!r}). "
            "The claim under test is unaffected and is exercised wherever PID namespaces work; this is an "
            "environment limitation, NOT a passing result.")

    out = subprocess.run(["unshare", "-fp", "--mount-proc", "bash", "-c", script],
                         capture_output=True, text=True, timeout=60).stdout
    assert "SURVIVED_KILL_1" in out, out          # kill -9 1 did not end the namespace init
    assert "kill -9 1 rc=0" in out, out           # ...and reported SUCCESS while doing nothing
    assert "SURVIVED_KILL_ALL" in out, out        # kill -9 -1 killed everything else and not PID 1


def test_the_crash_loop_brake_trips_on_churn_and_not_on_a_resume(tmp_path):
    """The in-container brake, EXECUTED. It is the piece that stops a rental re-running a job that keeps
    failing the same way, and its only defence against killing a legitimate resume is that it counts starts
    in a WINDOW rather than latching a flag. So run it: three starts inside the window must hold, and a
    start whose window contains only old entries must run the job."""
    from gpu_backend import _VAST_CRASHLOOP_BRAKE
    starts = tmp_path / "starts"
    body = _VAST_CRASHLOOP_BRAKE.replace("while true; do sleep 3600; done", "exit 42") + "\necho JOB_RAN"
    env = {**os.environ, "CT_STARTS": str(starts), "CT_WIN": "900", "CT_MAX": "3"}

    rcs = [subprocess.run(["bash", "-c", body], capture_output=True, text=True, env=env).returncode
           for _ in range(4)]
    assert rcs == [0, 0, 42, 42], f"brake tripped at the wrong start: {rcs}"

    # A resume hours later: the window contains nothing, so the job runs.
    import time as _t
    starts.write_text("\n".join(str(int(_t.time()) - d) for d in (5000, 4000, 3000)) + "\n")
    r = subprocess.run(["bash", "-c", body], capture_output=True, text=True, env=env)
    assert r.returncode == 0 and "JOB_RAN" in r.stdout, r.stdout


def test_the_onstart_arms_the_brake_before_the_trap_and_the_trap_before_the_job():
    """Order is load-bearing. The brake must decide whether to run the command BEFORE the trap is armed
    (once it is, any exit tries to kill the shell that would make the decision), and the trap must be armed
    before the command so a death on the first line is still covered."""
    from gpu_backend import JobSpec, ResourceSpec, VastBackend, _vast_onstart
    spec = JobSpec(name="u1", command=["bash", "run_ternary_leg.sh"], image="img",
                   resources=ResourceSpec(gpu="rtx4090"), checkpoint_uri="s3://b/ckpt")
    s = _vast_onstart(spec, VastBackend().self_terminate_cmd())
    assert s.index("CRASH-LOOP BRAKE") < s.index("ct_selfstop()") < s.index("trap ct_selfstop EXIT") \
        < s.index("run_ternary_leg.sh")
    assert subprocess.run(["bash", "-n", "-c", s], capture_output=True).returncode == 0


def test_no_surviving_code_claims_the_host_can_stop_its_own_billing():
    """CLAUDE.md §6's 'the auto-teardown wrapper guarantees no idle-GPU billing anywhere' was false, and a
    standing rule asserting a guarantee the code does not provide is worse than no rule. The claim was
    removed from the rule AND from the three docstrings that repeated it; this pins that it stays removed —
    and that `kill -9 1`, which returns 0 while doing nothing, is not silently re-added.

    On 2026-08-15 §6's body moved into the `gpu-compute` skill and CLAUDE.md kept the tripwire that routes
    to it, so this reads the STANDING-RULES CORPUS — the resident file plus the skills it routes to — rather
    than CLAUDE.md alone. Scoping it to one path is what let the split silently empty it: the rule is still
    binding, so the test follows the rule rather than the filename."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[3]
    import gpu_backend
    assert "kill -9 1" not in gpu_backend._VAST_SELFSTOP
    assert "kill -9 1" not in " ".join(gpu_backend.VastBackend().self_terminate_cmd())
    sources = [root / "CLAUDE.md"] + sorted((root / ".claude" / "skills").glob("*/SKILL.md"))
    assert (root / ".claude" / "skills" / "gpu-compute" / "SKILL.md") in sources, \
        "the gpu-compute skill is where §6's compute rules live; if it moved, re-point this test"
    # The old wording may still APPEAR — CLAUDE.md §1 says a corrected claim is registered, not silently
    # dropped, so the retraction quotes it. What must never come back is the claim being ASSERTED, so every
    # surviving occurrence has to sit inside its own retraction.
    claim = "guarantees no idle-GPU billing"
    for path in sources:
        text = path.read_text()
        at = -1
        while (at := text.find(claim, at + 1)) != -1:
            context = text[max(0, at - 300):at]
            assert "previously said" in context and "that was false" in text[at:at + 200], \
                f"{path.name} asserts the host-side teardown guarantee again; it is measurably untrue"
    rules = "\n".join(p.read_text() for p in sources)
    assert "vast_idle_guard" in rules, \
        "the standing rules must still name what actually provides the guarantee now"
