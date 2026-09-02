"""⛔ A CHECKPOINT WRITTEN AND NEVER RESTORED IS NOT A CHECKPOINT; IT IS A FILE.

Guards for `.github/workflows/nr4a2-bound-ddddg-search.yml`'s checkpoint mechanism, written
2026-09-02 after the 2026-08-07 fix turned out to be one half of a pair.

★ THE MEASURED HISTORY, so a reader does not have to reconstruct it. `c01b` ran 120.6 minutes
against a declared `timeout-minutes: 120` on two independent runs — landing on 7215 s twice to the
second, which no operator cancellation produces — and `c01a` ran 355.2 against 350. The Actions API
labels every one of them `cancelled`, so nothing in the badge says "timeout". On 2026-08-07 an
`actions/cache@v4` restore step was added to both jobs, and `row27-ddddg-precheck-status.json` still
records `has_restore_step: false` because it was generated at 14:29:47Z and the restore landed at
14:37:22Z — the artifact is STALE, not wrong.

⛔⛔ AND THE RESTORE COULD NEVER HAVE WORKED. `actions/cache@v4` saves in a POST step whose
condition is `post-if: "success()"` (read from the action's own `action.yml` at the v4 ref). A job
killed by `timeout-minutes` is CANCELLED, which is not success — and the only runs that reach a
checkpoint worth keeping are exactly the runs that time out. The restore had nothing to restore, by
construction, and the workflow looked repaired.

★ SO THIS FILE ASSERTS THE MECHANISM, NOT THE INTENTION. Each test names the failure it would have
caught, because every one of them is a shape somebody would reintroduce while believing they were
adding caching.
"""
import os

import pytest
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
WF = os.path.join(ROOT, ".github", "workflows", "nr4a2-bound-ddddg-search.yml")

#: GitHub-hosted runners cap a job at this and the value can only be LOWERED, so a fix of the form
#: "raise the timeout" has a ceiling and this is it. Read 2026-09-02 from GitHub's own limits
#: documentation; it is here so a workflow cannot declare a number the platform will ignore.
HOSTED_JOB_CEILING_MIN = 360

CKPT_PATH = "research/modalities/_ddddg_ckpt"


@pytest.fixture(scope="module")
def doc():
    if not os.path.exists(WF):
        pytest.fail(f"{WF} is missing — the workflow this file guards does not exist")
    with open(WF, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _ckpt_jobs(doc):
    out = {}
    for name, job in doc["jobs"].items():
        for st in job.get("steps", []):
            if CKPT_PATH in str((st.get("with") or {}).get("path", "")):
                out.setdefault(name, job)
    return out


def test_the_checkpointing_jobs_are_still_here(doc):
    assert set(_ckpt_jobs(doc)) == {"c01a", "c01b"}, (
        "the set of jobs that checkpoint changed; every test below is scoped to them")


def test_no_job_uses_the_composite_cache_action_whose_save_needs_success(doc):
    """⛔ `actions/cache@v4` saves in a post step with `post-if: success()`. The runs that produce
    a checkpoint worth keeping are the ones that TIME OUT, and a timed-out job is cancelled."""
    offenders = []
    for name, job in doc["jobs"].items():
        for st in job.get("steps", []):
            uses = str(st.get("uses") or "")
            if uses.startswith("actions/cache@") and CKPT_PATH in str(
                    (st.get("with") or {}).get("path", "")):
                offenders.append((name, st.get("name")))
    assert not offenders, (
        "the composite cache action is back on the checkpoint path: %s. Its save is a POST step "
        "gated on success(), so it cannot fire on the timeout it exists for. Use "
        "actions/cache/restore@v4 plus actions/cache/save@v4 with `if: always()`." % offenders)


def test_every_job_that_restores_the_checkpoint_also_saves_it_unconditionally(doc):
    for name, job in _ckpt_jobs(doc).items():
        steps = job["steps"]
        restores = [i for i, s in enumerate(steps)
                    if str(s.get("uses") or "").startswith("actions/cache/restore@")]
        saves = [i for i, s in enumerate(steps)
                 if str(s.get("uses") or "").startswith("actions/cache/save@")]
        assert restores, f"{name}: restores nothing — every dispatch restarts at stage 1"
        assert saves, f"{name}: saves nothing — the restore is decorative"
        for i in saves:
            assert str(steps[i].get("if", "")).strip() == "always()", (
                f"{name}: the checkpoint save is conditional ({steps[i].get('if')!r}). The runs "
                f"worth saving are the ones where an earlier step failed.")
        work = [i for i, st in enumerate(steps)
                if "ddddg_known_answer_search.py" in str(st.get("run") or "")]
        assert work, f"{name}: no search step found"
        assert max(saves) > max(work), (
            f"{name}: the last checkpoint save (step {max(saves)}) runs BEFORE the last search step "
            f"(step {max(work)}), so it banks whatever the restore just put there and nothing the "
            f"run computed")
        assert max(saves) > max(restores), f"{name}: the save precedes the restore"


def test_the_save_key_and_the_restore_prefix_can_actually_meet(doc):
    """A save under a key no later restore-key prefixes is a cache nobody will ever find."""
    for name, job in _ckpt_jobs(doc).items():
        restore = next(s for s in job["steps"]
                       if str(s.get("uses") or "").startswith("actions/cache/restore@"))
        save = next(s for s in job["steps"]
                    if str(s.get("uses") or "").startswith("actions/cache/save@"))
        prefixes = [p.strip() for p in
                    str((restore.get("with") or {}).get("restore-keys", "")).split("\n") if p.strip()]
        assert prefixes, f"{name}: no restore-keys, so the cache hits only on a re-run of the SAME run"
        save_key = str((save.get("with") or {}).get("key", ""))
        assert any(save_key.startswith(p) for p in prefixes), (
            f"{name}: save key {save_key!r} matches none of the restore prefixes {prefixes} — the "
            f"next dispatch will never find what this one banked")


def test_every_search_step_carries_its_own_timeout_below_the_jobs(doc):
    """⛔ THE STEP BUDGETS ARE WHAT MAKE `always()` REACHABLE. A job that exceeds its own
    `timeout-minutes` is CANCELLED and no `if: always()` step of any kind runs — which is exactly
    how three months of dispatches banked nothing. A STEP that overruns merely fails."""
    for name, job in _ckpt_jobs(doc).items():
        job_to = job.get("timeout-minutes")
        assert job_to, f"{name}: no job timeout at all"
        work = [s for s in job["steps"]
                if "ddddg_known_answer_search.py" in str(s.get("run") or "")]
        assert work, f"{name}: no search step found; this test is scoped to the wrong job"
        for s in work:
            to = s.get("timeout-minutes")
            assert to, (f"{name}: search step {s.get('name')!r} has no timeout of its own, so it "
                        f"can run the JOB into cancellation and the checkpoint save never happens")
            assert to < job_to, (f"{name}: step {s.get('name')!r} timeout {to} is not below the "
                                 f"job's {job_to}")
        assert sum(s["timeout-minutes"] for s in work) < job_to, (
            f"{name}: the search steps may together consume {sum(s['timeout-minutes'] for s in work)} "
            f"minutes against a job ceiling of {job_to}, so the last one can still be cancelled "
            f"mid-flight with the save unreached")


def test_no_job_declares_a_timeout_the_platform_will_ignore(doc):
    """A `timeout-minutes` above the hosted-runner ceiling is a number that reads as a fix and is
    not one — the job is killed at the ceiling regardless."""
    for name, job in doc["jobs"].items():
        to = job.get("timeout-minutes")
        if to is None:
            continue
        assert to <= HOSTED_JOB_CEILING_MIN, (
            f"{name}: timeout-minutes {to} exceeds the {HOSTED_JOB_CEILING_MIN}-minute ceiling for "
            f"GitHub-hosted runners; the platform will kill the job at the ceiling and the extra "
            f"minutes are decoration")


def test_the_checkpoint_directory_is_uploaded_whole_so_an_evicted_cache_is_not_a_lost_scan(doc):
    for name, job in _ckpt_jobs(doc).items():
        ups = [s for s in job["steps"]
               if str(s.get("uses") or "").startswith("actions/upload-artifact@")
               and CKPT_PATH in str((s.get("with") or {}).get("path", ""))]
        assert ups, (f"{name}: the checkpoint directory is never uploaded, so an evicted cache "
                     f"leaves no retrievable copy of a partial scan")
        assert any(str(s.get("if", "")).strip() == "always()" for s in ups), (
            f"{name}: the checkpoint upload is conditional; the runs worth uploading are the "
            f"failures")


def test_c01b_was_actually_given_more_room_than_the_run_that_timed_out(doc):
    """120.6 minutes observed against a declared 120 is a LOWER BOUND, so the ceiling had to move
    by much more than the overshoot. A raise sized to the overshoot is a guess, not a fix."""
    to = doc["jobs"]["c01b"]["timeout-minutes"]
    assert to >= 300, (
        f"c01b timeout-minutes is {to}; the search has been MEASURED to exceed 120 twice, and "
        f"nothing measures how much more it needs, so anything near 120 re-buys the same timeout")


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The DETECTOR, not the workflow. `row27_ddddg_precheck_status.checkpoint_durability` printed a
# ✅ verdict over a save that could not fire — the second checker in this repository to put a tick
# over the failure it existed to find. These exercise it against synthetic workflow text.
# ─────────────────────────────────────────────────────────────────────────────────────────────
import sys  # noqa: E402

MOD_DIR = os.path.dirname(HERE)
if MOD_DIR not in sys.path:
    sys.path.insert(0, MOD_DIR)
import row27_ddddg_precheck_status as R  # noqa: E402

_COMPOSITE = """
jobs:
  c01a:
    timeout-minutes: 350
    steps:
      - name: Restore the search checkpoint
        uses: actions/cache@v4
        with:
          path: research/modalities/_ddddg_ckpt
          key: ddddg-x
          restore-keys: |
            ddddg-
      - name: Stage 1
        run: python3 ddddg_known_answer_search.py c01a --stage universe
"""

_SPLIT_BUT_CONDITIONAL = _COMPOSITE.replace("actions/cache@v4", "actions/cache/restore@v4") + """
      - name: Save the search checkpoint
        if: success()
        uses: actions/cache/save@v4
        with:
          path: research/modalities/_ddddg_ckpt
          key: ddddg-x
"""


def _durability(text, tmp_path):
    p = tmp_path / "wf.yml"
    p.write_text(text, encoding="utf-8")
    return R.checkpoint_durability(str(p))


def test_the_detector_refuses_a_composite_cache_whose_save_needs_success(tmp_path):
    """⛔ THE 26-DAY FALSE GREEN. A restore step plus restore-keys was enough to print ✅."""
    out = _durability(_COMPOSITE, tmp_path)
    assert out["has_restore_step"] is True
    assert out["restore_survives_across_dispatches"] is True
    assert out["uses_composite_cache_action"] is True
    assert out["save_can_fire_after_a_timeout"] is False
    assert out["verdict"].startswith("⛔"), out["verdict"]


def test_the_detector_refuses_a_save_that_is_gated_on_success(tmp_path):
    out = _durability(_SPLIT_BUT_CONDITIONAL, tmp_path)
    assert out["has_save_step"] is True
    assert out["save_is_unconditional"] is False
    assert out["save_can_fire_after_a_timeout"] is False
    assert out["verdict"].startswith("⛔"), out["verdict"]


def test_the_detector_passes_the_live_workflow_it_guards():
    out = R.checkpoint_durability(WF)
    assert out["save_can_fire_after_a_timeout"] is True, out
    assert out["search_steps_have_their_own_timeout"] is True, out
    assert not out["verdict"].startswith("⛔"), out["verdict"]
