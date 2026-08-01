"""The stuck-run guard cancels ONLY what is provably safe to cancel.

The measured incident is in `stuck_run_guard`'s docstring. What this file pins is the boundary, because the
guard cancels things: `total_count == 0` is the entire safety argument, and every test here exists to stop
that argument being widened by a later edit that "also handles" queued jobs or slow runners.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
if MOD not in sys.path:
    sys.path.insert(0, MOD)

import stuck_run_guard as G  # noqa: E402


NOW = 1785708000.0  # a fixed clock; `_age_min` takes it injected so no test depends on wall time


def _run(status="pending", age_min=30.0, rid=1, anchor=NOW, wf=555):
    """`anchor=NOW` for the pure predicate tests (which inject the same clock); `anchor=None` for the scan
    tests, which go through `scan` and therefore read the real clock."""
    import time
    base = time.time() if anchor is None else anchor
    created = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(base - age_min * 60))
    return {"id": rid, "status": status, "created_at": created, "workflow_id": wf,
            "name": "ENDPOINT-MD SENSITIVITY CONTROL"}


# =============================================================================================================
# the predicate
# =============================================================================================================
def test_the_measured_incident_is_wedged():
    """Run 30720583406: pending, 0 jobs, 19 minutes."""
    assert G.is_wedged(_run(age_min=19.0), 0, now=NOW) is True


def test_a_run_with_jobs_is_never_wedged_however_old():
    """⛔ THE SAFETY BOUNDARY. A job waiting for a runner is real work; a slow runner is not a stuck lock.

    This is the assertion that must survive every future edit. `total_count == 0` is why cancelling is
    provably lossless — a run with even one job may have rented a host."""
    for jobs in (1, 2, 17):
        assert G.is_wedged(_run(age_min=600.0), jobs, now=NOW) is False


def test_queued_is_not_pending():
    """`queued` means GitHub accepted it and is finding a runner — the normal path, not a wedge."""
    assert G.is_wedged(_run(status="queued", age_min=99.0), 0, now=NOW) is False
    assert G.is_wedged(_run(status="in_progress", age_min=99.0), 0, now=NOW) is False
    assert G.is_wedged(_run(status="completed", age_min=99.0), 0, now=NOW) is False


def test_a_young_pending_run_is_left_alone():
    """Job creation normally takes seconds; the threshold only avoids racing it."""
    assert G.is_wedged(_run(age_min=0.5), 0, now=NOW) is False
    assert G.is_wedged(_run(age_min=9.9), 0, now=NOW, after_min=10) is False
    assert G.is_wedged(_run(age_min=10.1), 0, now=NOW, after_min=10) is True


def test_a_run_with_no_timestamp_is_left_alone():
    """An absent reading is not a reading of absence (CLAUDE.md §4) — and never grounds to cancel."""
    assert G.is_wedged({"id": 1, "status": "pending", "created_at": ""}, 0, now=NOW) is False


# =============================================================================================================
# the scan, with the network stubbed
# =============================================================================================================
class _Api:
    """Replaces `_get`. Records every call so the test can assert what was and was not cancelled."""

    def __init__(self, runs, jobs, fail_jobs_for=(), fail_cancel_for=(), fail_list=False,
                 in_progress=(), fail_in_progress=False):
        self.runs, self.jobs = runs, jobs
        self.fail_jobs_for, self.fail_cancel_for, self.fail_list = fail_jobs_for, fail_cancel_for, fail_list
        # workflow_ids with a run in progress — the "may be legitimately queued behind it" spare
        self.in_progress, self.fail_in_progress = in_progress, fail_in_progress
        self.cancelled = []

    def __call__(self, url, token=None, method="GET"):
        import urllib.error
        if url.endswith("/cancel"):
            rid = int(url.rsplit("/", 2)[-2])
            if rid in self.fail_cancel_for:
                raise urllib.error.URLError("cancel refused")
            self.cancelled.append(rid)
            return {}
        if "status=pending" in url:
            if self.fail_list:
                raise urllib.error.URLError("api down")
            return {"workflow_runs": self.runs}
        if "status=in_progress" in url:
            if self.fail_in_progress:
                raise urllib.error.URLError("api down")
            return {"workflow_runs": [{"workflow_id": w} for w in self.in_progress]}
        rid = int(url.rsplit("/", 2)[-2])
        if rid in self.fail_jobs_for:
            raise urllib.error.URLError("jobs unreadable")
        return {"total_count": self.jobs.get(rid, 0)}


@pytest.fixture()
def patched(monkeypatch, tmp_path):
    monkeypatch.setattr(G, "ARTIFACT", str(tmp_path / "stuck-run-guard.json"))

    def _install(api):
        monkeypatch.setattr(G, "_get", api)
        return api
    return _install


def test_the_wedged_run_is_cancelled_and_the_healthy_one_is_not(patched):
    api = patched(_Api(runs=[_run(rid=30720583406, age_min=19.0, anchor=None), _run(rid=999, age_min=2.0, anchor=None)],
                       jobs={30720583406: 0, 999: 0}))
    rec = G.scan(token="t")
    assert api.cancelled == [30720583406]
    assert rec["cancelled"][0]["run"] == 30720583406
    assert any(s["run"] == 999 for s in rec["spared"])


def test_a_pending_run_that_has_jobs_is_spared_with_a_reason(patched):
    api = patched(_Api(runs=[_run(rid=7, age_min=90.0, anchor=None)], jobs={7: 3}))
    rec = G.scan(token="t")
    assert api.cancelled == []
    assert "not a stuck lock" in rec["spared"][0]["why"]


def test_an_unreadable_job_count_never_cancels(patched):
    """⚠ CLAUDE.md §4. Not being able to READ the job count is not a reading of zero jobs — and zero jobs is
    the whole safety argument, so an unreadable count must spare."""
    api = patched(_Api(runs=[_run(rid=7, age_min=90.0, anchor=None)], jobs={}, fail_jobs_for=(7,)))
    rec = G.scan(token="t")
    assert api.cancelled == []
    assert "UNREADABLE" in rec["spared"][0]["why"]


def test_an_unreadable_run_list_is_recorded_as_unreadable_not_as_clean(patched):
    patched(_Api(runs=[], jobs={}, fail_list=True))
    rec = G.scan(token="t")
    assert rec["readable"] is False and "error" in rec
    assert rec["cancelled"] == []


def test_a_failed_cancel_is_surfaced_not_swallowed(patched):
    """A wedge we could not clear still blocks re-placement; it must not read like a clean tick."""
    patched(_Api(runs=[_run(rid=7, age_min=90.0, anchor=None)], jobs={7: 0}, fail_cancel_for=(7,)))
    rec = G.scan(token="t")
    assert rec["cancelled"] == [] and rec["cancel_failed"][0]["run"] == 7


def test_the_artifact_is_written_even_when_nothing_was_cancelled(patched, tmp_path):
    """A guard with no artifact is indistinguishable from a guard that never ran."""
    patched(_Api(runs=[], jobs={}))
    G.scan(token="t")
    rec = json.loads((tmp_path / "stuck-run-guard.json").read_text())
    assert rec["cancelled"] == [] and rec["readable"] is True and rec["utc"].endswith("Z")


def test_dry_run_cancels_nothing(patched):
    api = patched(_Api(runs=[_run(rid=7, age_min=90.0, anchor=None)], jobs={7: 0}))
    G.scan(token="t", cancel=False)
    assert api.cancelled == []


def test_the_module_is_pure_stdlib():
    """It watches the supervision layer, so it must not be takeable down by the supervision layer — the same
    isolation `account_orphan_alarm` keeps."""
    import inspect
    src = inspect.getsource(G)
    for banned in ("import boto3", "import requests", "import yaml", "import numpy"):
        assert banned not in src, banned


# =============================================================================================================
# ⛔ THE SPARE THAT MATTERS: a queued supervision re-arm must never be cancelled
# =============================================================================================================
def test_a_pending_run_is_SPARED_when_its_own_workflow_is_already_running(patched):
    """★★ CAUGHT BEFORE THE FIRST LIVE TICK. A `watch` queued behind a running `watch` has ZERO jobs — it is
    waiting precisely because it has not been allowed to start. Cancelling it would kill the re-arm of a
    supervision loop and leave a fleet billing unwatched: the worst outcome in this repo, and strictly worse
    than the wedge this module clears."""
    api = patched(_Api(runs=[_run(rid=7, age_min=90.0, anchor=None, wf=555)], jobs={7: 0},
                       in_progress=(555,)))
    rec = G.scan(token="t")
    assert api.cancelled == [], "a run queued behind its own running sibling was cancelled"
    assert any("may be" in s["why"] and "queued behind" in s["why"] for s in rec["spared"])


def test_it_is_still_REPORTED_even_when_it_cannot_be_cancelled(patched):
    """A wedge nobody can see is the outage. The cancel is only how some get cleared automatically."""
    patched(_Api(runs=[_run(rid=7, age_min=90.0, anchor=None, wf=555)], jobs={7: 0}, in_progress=(555,)))
    rec = G.scan(token="t")
    assert [w["run"] for w in rec["wedged"]] == [7]


def test_a_different_workflow_running_does_not_protect_it(patched):
    """The spare is scoped to the SAME workflow — only that one can share a concurrency group."""
    api = patched(_Api(runs=[_run(rid=7, age_min=90.0, anchor=None, wf=555)], jobs={7: 0},
                       in_progress=(999,)))
    G.scan(token="t")
    assert api.cancelled == [7]


def test_an_unreadable_in_progress_list_spares_everything(patched):
    """§4: if we cannot tell whether a sibling is running, we do not get to assume none is."""
    api = patched(_Api(runs=[_run(rid=7, age_min=90.0, anchor=None, wf=555)], jobs={7: 0},
                       fail_in_progress=True))
    rec = G.scan(token="t")
    assert api.cancelled == []
    assert rec["in_progress_readable"] is False
    assert [w["run"] for w in rec["wedged"]] == [7], "still reported, just not cancelled"
