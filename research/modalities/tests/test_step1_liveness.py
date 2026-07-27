"""STEP 1 LIVENESS — the two signals `vast_idle_guard` consumes, and the ways the heartbeat must die.

★ WHY THESE ARE EXECUTION TESTS AND NOT ASSERTIONS ABOUT A STRING. The hazard here is not "does the script
say the right thing", it is a background child interacting with a bash EXIT trap on a container that
provably cannot end itself. This repo has already been wrong once about exactly that class of reasoning —
`kill -9 1` returns 0 and does nothing, which nobody noticed until it was RUN under `unshare -fp
--mount-proc`. So the trap interaction is reproduced the same way, and the heartbeat's lifetime is measured
rather than argued.

THE TWO FAILURE DIRECTIONS, both tested, because they are not symmetric:

  * HEARTBEAT STOPS TOO EARLY -> the guard sees log silence during a legitimately CPU-only phase (stage,
    openff parameterisation of a large hybrid, minimise) and destroys a HEALTHY leg. This is the dangerous
    direction: it is a self-inflicted copy of the incident the guard exists to prevent.
  * HEARTBEAT OUTLIVES THE JOB -> run.log stays fresh forever, the WEDGED clause never fires, and the box
    bills to the age backstop. Strictly worse than having no heartbeat at all.
"""
import os
import shutil
import subprocess
import sys
import time

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import congeneric_fanout_vast as cfv  # noqa: E402
import vast_idle_guard as vig  # noqa: E402


# ---------------------------------------------------------------------------------------------------------
# harness: run the REAL heartbeat text out of `_PREAMBLE`, with $AWS stubbed to a recorder
# ---------------------------------------------------------------------------------------------------------

def _heartbeat_block():
    """The heartbeat definition + its trap, sliced verbatim out of the shipped `_PREAMBLE`.

    Sliced rather than re-typed so the test cannot drift from the script that actually runs — if the block is
    renamed or removed, this raises instead of silently testing nothing."""
    src = cfv._PREAMBLE
    start = src.index("s1f_heartbeat() {")
    end = src.index("trap s1f_stop_heartbeat EXIT") + len("trap s1f_stop_heartbeat EXIT")
    return src[start:end]


def _stub_aws(tmp_path):
    """A fake `aws` that appends one line per invocation. Every PUT the heartbeat makes is therefore
    counted, and its timing is recorded, which is what "the log advances during this phase" means."""
    log = tmp_path / "puts.txt"
    aws = tmp_path / "aws"
    aws.write_text('#!/bin/bash\ndate +%s.%N >> "' + str(log) + '"\nexit 0\n')
    aws.chmod(0o755)
    return str(aws), log


def _run(script, tmp_path, timeout=30, **env):
    e = {**os.environ, "RESULT_S3": "s3://bucket/prefix", **env}
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=timeout, env=e,
                          cwd=str(tmp_path))


# ---------------------------------------------------------------------------------------------------------
# 1. the SHAPES — the guard must find the ternary lane's conventions, not a second one
# ---------------------------------------------------------------------------------------------------------

def test_the_pipeline_emits_both_signals_the_guard_keys_on():
    """Before this change `grep -cE "while true|sleep 120|run\\.log|attempts/"` over the step 1 pipeline
    returned 0 — which is exactly why the guard could not be wired to it."""
    p = cfv._PREAMBLE
    assert "exec > >(tee /tmp/run.log) 2>&1" in p
    assert '"$RESULT_S3/run.log"' in p
    assert "attempts/run-$(date -u +%Y%m%dT%H%M%SZ).log" in p
    assert "s1f_heartbeat" in p


def test_the_archive_key_matches_the_regex_the_guard_actually_parses():
    """A key shape the guard cannot parse is a crash-loop channel that silently counts zero restarts. Pin the
    real strftime output against `vast_idle_guard._ATTEMPT_RE` rather than eyeballing the format string."""
    stamp = subprocess.run(["date", "-u", "+%Y%m%dT%H%M%SZ"], capture_output=True, text=True).stdout.strip()
    key = f"nr4a3-step1-fanout/results/some_unit/attempts/run-{stamp}.log"
    assert vig._ATTEMPT_RE.search("/" + key), key


def test_the_previous_attempt_is_archived_BEFORE_the_first_mark():
    """★ THE ORDERING THE TERNARY LANE PAID FOR. `exec > >(tee /tmp/run.log)` truncates the local log and
    `mark` uploads it, so marking first overwrites the previous attempt's S3 copy with a fresh stub and the
    archive then copies the stub — seventeen 168-byte attempts, 2026-07-26, with the failing log lost."""
    p = cfv._PREAMBLE
    assert p.index("attempts/run-$(date") < p.index("\nmark boot")


def test_mark_refreshes_the_heartbeat_so_a_phase_change_is_never_a_silent_gap():
    p = cfv._PREAMBLE
    mark = p[p.index("mark() {"):p.index("# --- container-start archive")]
    assert '"$RESULT_S3/run.log"' in mark


def test_the_whole_onstart_including_the_heartbeat_is_valid_bash():
    """A syntax error here does not break one unit, it breaks every unit in the fleet at once."""
    from gpu_backend import _vast_onstart, VastBackend
    units = cfv.default_units()
    spec = cfv.build_jobspec(units[0], "some-branch", "some-bucket", 0)
    s = _vast_onstart(spec, VastBackend().self_terminate_cmd())
    r = subprocess.run(["bash", "-n", "-c", s], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


# ---------------------------------------------------------------------------------------------------------
# 2. THE FALSE-POSITIVE SIDE — the heartbeat must cover every phase, including the CPU-only ones
# ---------------------------------------------------------------------------------------------------------

def test_the_heartbeat_keeps_writing_through_a_phase_that_produces_no_output(tmp_path):
    """★ THE DANGEROUS DIRECTION, MEASURED. A step 1 complex leg is legitimately GPU-idle and STDOUT-silent
    for its whole stage/parameterise/minimise stretch — the engine's output goes to /tmp/$L.log, not to
    run.log. If the heartbeat only fired on new text, the guard would see silence and destroy a healthy leg.

    So: run the real heartbeat across a phase that writes NOTHING, and require the PUTs to keep coming."""
    aws, puts = _stub_aws(tmp_path)
    script = f"""
      AWS={aws}
      {_heartbeat_block()}
      sleep 1.1          # a "phase" that emits no output at all
      exit 0
    """
    _run(script, tmp_path, S1F_SYNC_S="0.2")
    n = len(puts.read_text().strip().splitlines())
    assert n >= 4, f"only {n} heartbeat PUTs across a silent phase — the guard would read this as wedged"


def test_every_phase_marker_in_the_real_pipeline_sits_inside_the_heartbeat_window():
    """Coverage as a STRUCTURAL fact over the assembled pipeline, so a phase added later cannot land outside
    the window by accident. `mark boot` is the first marker and it follows the heartbeat start; the trap that
    stops it is armed before that, so nothing between them is uncovered."""
    full = cfv._PREAMBLE + cfv._LEG + cfv._REDUCE
    start = full.index("s1f_heartbeat \"$$\" &")
    marks = [i for i in range(len(full)) if full.startswith("mark ", i) and full[i - 1] in "\n;"]
    assert marks, "no phase markers found — the slice is wrong, not the pipeline"
    assert min(marks) > start, "a phase marker precedes the heartbeat, so that phase is unmonitored"


# ---------------------------------------------------------------------------------------------------------
# 3. THE OTHER SIDE — the heartbeat must not outlive the job, which would DISARM the guard it feeds
# ---------------------------------------------------------------------------------------------------------

def test_the_heartbeat_stops_when_the_pipeline_exits_cleanly(tmp_path):
    aws, puts = _stub_aws(tmp_path)
    script = f"""
      AWS={aws}
      {_heartbeat_block()}
      sleep 0.5
      exit 0
    """
    _run(script, tmp_path, S1F_SYNC_S="0.2")
    n_at_exit = len(puts.read_text().strip().splitlines())
    time.sleep(1.0)
    assert len(puts.read_text().strip().splitlines()) == n_at_exit, \
        "the heartbeat kept PUTting after the pipeline exited — run.log would never go stale and the WEDGED " \
        "clause could never fire"


def test_the_heartbeat_stops_when_the_pipeline_shell_is_SIGKILLED(tmp_path):
    """★★ THE NET THE TRAP CANNOT PROVIDE, AND THE REASON THE LOOP POLLS ITS PARENT.

    SIGKILL runs no trap — it cannot be caught — and `Killed` is exactly what the 2026-07-27 crash-loop
    logged on both stranded legs. If the only stopping mechanism were the EXIT trap, a SIGKILLed pipeline
    would leave an immortal heartbeat keeping run.log fresh forever, which disarms the guard on precisely the
    box that needs it. The loop therefore re-checks `kill -0 $parent` every tick."""
    aws, puts = _stub_aws(tmp_path)
    inner = tmp_path / "pipeline.sh"
    inner.write_text(f"#!/bin/bash\nAWS={aws}\n{_heartbeat_block()}\nsleep 30\n")
    inner.chmod(0o755)

    p = subprocess.Popen(["bash", str(inner)], env={**os.environ, "RESULT_S3": "s3://b/p", "S1F_SYNC_S": "0.2"},
                         cwd=str(tmp_path))
    time.sleep(1.0)
    p.kill()                      # SIGKILL: no trap runs, by definition
    p.wait(timeout=10)
    time.sleep(0.6)               # let the loop notice its parent is gone
    n = len(puts.read_text().strip().splitlines())
    time.sleep(1.2)               # several more sync intervals
    assert len(puts.read_text().strip().splitlines()) == n, \
        "the heartbeat survived a SIGKILL of its pipeline shell — it would keep run.log fresh on a box the " \
        "guard must be able to condemn"


def test_the_heartbeat_has_a_hard_ttl_past_the_units_own_runtime_cap(tmp_path):
    """The third net, for a parent PID reused by an unrelated process. Exercised with a tiny TTL."""
    aws, puts = _stub_aws(tmp_path)
    script = f"""
      AWS={aws}
      {_heartbeat_block()}
      sleep 1.5
      exit 0
    """
    _run(script, tmp_path, S1F_SYNC_S="0.2", S1F_SYNC_TTL_S="0")
    n = len(puts.read_text().strip().splitlines() if puts.exists() else [])
    # <= 1 rather than == 0: the EXIT trap's own final upload always fires and is not the loop. Without the
    # TTL, 1.5 s at a 0.2 s interval would be ~7, so this discriminates.
    assert n <= 1, f"the TTL did not bound the loop ({n} PUTs)"


# ---------------------------------------------------------------------------------------------------------
# 4. THE EXIT-TRAP INTERACTION, reproduced in the topology Vast actually runs
# ---------------------------------------------------------------------------------------------------------

@pytest.mark.skipif(shutil.which("unshare") is None, reason="needs unshare to build the PID namespace")
def test_the_heartbeat_does_not_break_or_outlive_the_onstart_EXIT_trap(tmp_path):
    """★★ THE TEST THE PREVIOUS LANE STOPPED FOR, RUN RATHER THAN REASONED ABOUT.

    Build the exact topology: a PID-namespace init as PID 1, an ONSTART shell that arms `ct_selfstop` as its
    EXIT trap, and a CHILD `bash -c` pipeline that backgrounds the heartbeat — which is precisely the
    composition `_vast_onstart` produces. Two things must hold, and they pull in opposite directions:

      (a) the stray background child must NOT stop the onstart shell exiting and REACHING its trap. bash does
          not wait on background jobs at exit, but that is the kind of claim this repo has been wrong about,
          so it is measured: the trap's own marker must appear in the output.
      (b) the heartbeat must STOP with the job, measured INSIDE the namespace and BEFORE the trap fires —
          because `ct_selfstop`'s `kill -9 -1` would clean up anything left over and thereby hide the bug.
          The observable is the PUT STREAM, not a process count: a first attempt at this test counted
          processes with `pgrep -f s1f_heartbeat` and got 1, which turned out to be pgrep matching the
          harness's own `bash -c` argv (the script text contains the name). The signal the guard consumes is
          run.log's mtime, so the signal the test consumes is the PUTs.
    """
    aws, puts = _stub_aws(tmp_path)
    from gpu_backend import _VAST_SELFSTOP
    # The pipeline goes in a FILE, not inside `bash -c '...'`: the shipped block contains apostrophes in its
    # comments, and quoting them away would mean testing a mangled copy of the thing under test.
    inner = tmp_path / "pipeline.sh"
    inner.write_text(f"#!/bin/bash\nAWS={aws}\n{_heartbeat_block()}\nsleep 0.6\n")
    inner.chmod(0o755)
    script = f"""
      set -o pipefail
      export RESULT_S3=s3://b/p S1F_SYNC_S=0.2 AWS={aws}
      {_VAST_SELFSTOP}
      trap ct_selfstop EXIT
      bash {inner}
      echo ONSTART_COMMAND_RETURNED
      wc -l < {puts} > {tmp_path}/n_at_return
      sleep 1.0                      # five sync intervals with the job gone
      wc -l < {puts} > {tmp_path}/n_after
    """
    r = subprocess.run(["unshare", "-fp", "--mount-proc", "bash", "-c", script],
                       capture_output=True, text=True, timeout=60, cwd=str(tmp_path))
    out = r.stdout + r.stderr
    # (a) the onstart shell got past its child AND ran its EXIT trap
    assert "ONSTART_COMMAND_RETURNED" in out, out
    assert "[selfstop] job exited rc=" in out, out
    # (b) the heartbeat had already stopped, BEFORE `ct_selfstop` could clean up after it
    n0 = int((tmp_path / "n_at_return").read_text().strip())
    n1 = int((tmp_path / "n_after").read_text().strip())
    assert n0 > 0, "the heartbeat never ran inside the namespace — the test proves nothing"
    assert n1 == n0, (f"{n1 - n0} further PUT(s) after the pipeline returned: the heartbeat outlived its job, "
                      f"so run.log would stay fresh forever and the WEDGED clause could never fire")


# ---------------------------------------------------------------------------------------------------------
# 5. THE WIRING — evidence in, verdict out, and the trap that would have disarmed it
# ---------------------------------------------------------------------------------------------------------

def test_the_guard_uses_its_OWN_previous_census_not_the_monitors():
    """★ THE BUG THIS AVOIDS. The autoscale tick runs monitor -> collect, and monitor overwrites
    `_progress_prev.json` with the CURRENT census as its last act. Had the guard read that file, every
    healthy leg would compare against itself, `progress_advanced` would be False fleet-wide, and the one
    clause that overrides every condemnation would be permanently disarmed — a guard that reaps working
    boxes. Pinned by source, because the failure is invisible at runtime until it destroys something."""
    import ast
    import inspect
    src = inspect.getsource(cfv._idle_evidence)
    # CODE, not the docstring/comments — the comment explaining the trap legitimately names the file.
    tree = ast.parse(src)
    ast.get_docstring(tree.body[0]) and setattr(tree.body[0], "body", tree.body[0].body[1:])
    assert "_progress_prev" not in ast.unparse(tree)
    assert cfv._IDLE_PREV_KEY_SUFFIX == "_idle_prev.json"


def test_a_fleet_with_no_run_log_yet_is_never_condemned():
    """The 18 units live when this shipped pulled their code BEFORE the heartbeat existed, so they have no
    run.log at all. That must read as 'no evidence', never as 'silent for a long time'."""
    verdict, why = vig.classify_idle(instance_running=True, container_started=True, gpu_util=0.0,
                                     progress_advanced=False, log_age_min=None, start_ages_min=[],
                                     instance_age_min=120)
    assert not vig.should_destroy(verdict), why


def test_an_idle_gpu_alone_never_condemns_a_box():
    """The inviolable rule. A step 1 complex leg at 0 % GPU with a fresh log is a CPU-bound setup phase."""
    verdict, _ = vig.classify_idle(instance_running=True, container_started=True, gpu_util=0.0,
                                   progress_advanced=False, log_age_min=1.0, start_ages_min=[],
                                   instance_age_min=120)
    assert not vig.should_destroy(verdict)


def test_the_45996071_shape_is_condemned_once_the_signals_exist():
    """The incident this whole change is for: a container crash-looping on a dead credential, `running`,
    0 % GPU, writing nothing. With the two signals in place it is destroyed in ~15 min instead of hours."""
    silent, _ = vig.classify_idle(instance_running=True, container_started=True, gpu_util=0.0,
                                  progress_advanced=False, log_age_min=20.0, start_ages_min=[],
                                  instance_age_min=70)
    assert vig.should_destroy(silent)
    churn, _ = vig.classify_idle(instance_running=True, container_started=True, gpu_util=0.0,
                                 progress_advanced=False, log_age_min=1.0,
                                 start_ages_min=[1.0, 3.0, 6.0], instance_age_min=70)
    assert vig.should_destroy(churn)


def test_measured_progress_overrides_every_condemnation():
    verdict, _ = vig.classify_idle(instance_running=True, container_started=True, gpu_util=0.0,
                                   progress_advanced=True, log_age_min=999.0,
                                   start_ages_min=[1.0, 2.0, 3.0, 4.0], instance_age_min=600)
    assert not vig.should_destroy(verdict)


def test_the_collect_clause_is_reached_only_after_the_cheaper_reaps():
    """Ordering, by source. A box the terminal-state or age clause already condemns must not pay for the
    guard's S3 reads, and — more importantly — the guard must never pre-empt the `result in S3` clause,
    which destroys a FINISHED unit on sight."""
    import inspect
    src = inspect.getsource(cfv.mode_collect)
    assert src.index("result in S3") < src.index("terminal state") < src.index("idle guard:")
