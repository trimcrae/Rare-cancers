"""THE FOUR CONTROLS FOR THE CROSS-LANE SUPERVISION RESURRECTOR — each one watched to fail, not assumed.

CLAUDE.md §4: a guard nobody has watched fail is not known to work. On 2026-08-01 that rule caught real bugs
in four separate guards in one session, so every branch of `supervisor_resurrect.decide` gets a test that
FAILS if the branch is removed:

    live host, no live watch      -> DISPATCH
    live host, watch alive/queued -> SKIP supervisor_alive        (the double-supervision hazard)
    no live host                  -> SKIP no_live_hosts           (nothing dispatched)
    liveness unreadable           -> SKIP liveness_unreadable     (fails CLOSED, does not spam)

Plus the two that today's incident produced directly:
  * a STALE artifact with a LIVE watch run must NOT dispatch — the false positive measured at 2:25 PM ET;
  * the resurrector may only ever dispatch modes that CANNOT rent (AST-pinned, like the account alarm).
"""
from __future__ import annotations

import ast
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import supervisor_resurrect as SR  # noqa: E402

LANE = "selcal-cofold"


def _report(n_live=1, verdict="UNSUPERVISED-BILLING", top="UNSUPERVISED-BILLING",
            utc="2026-08-01T18:25:00Z"):
    return {"generated_utc": utc, "verdict": top, "ok": False,
            "lanes": [{"lane": LANE, "n_live": n_live, "verdict": verdict}]}


NOW = SR._parse_iso("2026-08-01T18:26:00Z")  # 2:26 PM ET, one minute after the report


def _one(report, live, **kw):
    out = SR.decide(report, live, now=NOW, **kw)
    assert len(out) == len(SR.RESURRECTABLE)
    return {d["lane"]: d for d in out}[LANE]


# ── CONTROL 1 ───────────────────────────────────────────────────────────────────────────────────────────
def test_live_host_no_watch_is_resurrected():
    d = _one(_report(n_live=1), {LANE: 0})
    assert d["action"] == "DISPATCH" and d["dispatch"] is True
    assert d["reason"] == "unsupervised_billing"
    assert d["inputs"]["mode"] == "cofold_watch"
    # The inputs are named IN FULL — an omitted input reads as null downstream (2026-07-27).
    assert set(d["inputs"]) == {"mode", "watch_minutes"}


# ── CONTROL 2 ───────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("live", [1, 2, 7])
def test_live_host_with_a_live_watch_is_never_double_dispatched(live):
    d = _one(_report(n_live=2), {LANE: live})
    assert d["action"] == "SKIP" and d["dispatch"] is False
    assert d["reason"] == "supervisor_alive"


def test_a_stale_artifact_with_a_live_watch_does_not_dispatch():
    """★ THE FALSE POSITIVE MEASURED AT 2:25 PM ET, 2026-08-01, and the reason this module exists in this
    shape. The selcal census was 24 min stale while host 46524315 billed — `UNSUPERVISED-BILLING` — and run
    30711255780's watch loop was alive at 36+ min, having checked out a sha with no `_tick_publish`. A
    resurrector keyed on the verdict, or on artifact freshness, would have put a SECOND supervisor on the
    lane. Liveness comes from the Actions API and nothing else."""
    d = _one(_report(n_live=1, verdict="UNSUPERVISED-BILLING"), {LANE: 1})
    assert d["dispatch"] is False and d["reason"] == "supervisor_alive"


def test_a_fresh_artifact_does_not_protect_a_dead_loop():
    """The mirror: keying on the alarm's verdict would MISS this. A $0 collect tick can leave the census
    perfectly fresh — verdict SUPERVISED — while the watch loop is gone and the host bills on."""
    d = _one(_report(n_live=1, verdict="SUPERVISED", top="ALL-SUPERVISED"), {LANE: 0})
    assert d["action"] == "DISPATCH" and d["reason"] == "unsupervised_billing"


# ── CONTROL 3 ───────────────────────────────────────────────────────────────────────────────────────────
def test_no_hosts_dispatches_nothing():
    d = _one(_report(n_live=0, verdict="IDLE", top="ALL-SUPERVISED"), {LANE: 0})
    assert d["action"] == "SKIP" and d["dispatch"] is False
    assert d["reason"] == "no_live_hosts"


# ── CONTROL 4 ───────────────────────────────────────────────────────────────────────────────────────────
def test_unreadable_liveness_fails_closed():
    d = _one(_report(n_live=3), {LANE: None})
    assert d["action"] == "SKIP" and d["dispatch"] is False
    assert d["reason"] == "liveness_unreadable"


def test_a_lane_missing_from_the_probe_map_is_unreadable_not_zero():
    """An absent key is an ABSENT READING (§4). Reading it as 0 would dispatch on every probe bug."""
    d = _one(_report(n_live=3), {})
    assert d["reason"] == "liveness_unreadable" and d["dispatch"] is False


# ── the unreadable-world cases: never 0, never a dispatch ───────────────────────────────────────────────
@pytest.mark.parametrize("report,expect", [
    (None, "hosts_unreadable"),
    ({}, "hosts_unreadable"),
    ({"generated_utc": "2026-08-01T18:25:00Z", "verdict": "CENSUS-UNKNOWN", "lanes": None},
     "hosts_unreadable"),
    ({"generated_utc": "2026-08-01T18:25:00Z", "verdict": "CENSUS-STALE", "lanes": []}, "hosts_unreadable"),
    ({"generated_utc": "2026-08-01T18:25:00Z", "lanes": [{"lane": LANE, "n_live": None}]},
     "hosts_unreadable"),
    ({"generated_utc": "2026-08-01T18:25:00Z", "lanes": [{"lane": "someone-else", "n_live": 4}]},
     "hosts_unreadable"),
])
def test_an_unreadable_report_never_dispatches(report, expect):
    d = _one(report, {LANE: 0})
    assert d["dispatch"] is False and d["reason"] == expect


def test_lane_hosts_never_returns_zero_for_an_unreadable_lane():
    n, _v, why = SR.lane_hosts({"lanes": [{"lane": LANE}]}, LANE)
    assert n is None and why  # None, NOT 0 — that distinction is the whole §4 rule
    n, _v, _w = SR.lane_hosts(_report(n_live=0), LANE)
    assert n == 0  # a MEASURED zero is a real reading


def test_a_stale_alarm_report_is_not_acted_on():
    """The report is refreshed from every step-1 tick. One older than the threshold means the refresher has
    itself stopped — dispatching off it would be acting on a memory of the account, not a reading."""
    d = _one(_report(n_live=1, utc="2026-08-01T17:00:00Z"), {LANE: 0})
    assert d["dispatch"] is False and d["reason"] == "report_stale"
    assert d["report_age_min"] == 86.0


def test_a_report_with_no_stamp_is_still_graded_on_its_hosts():
    """No stamp is not a stale stamp: `report_age_min` is None, and the host reading still stands on its own.
    (Refusing here would silently retire the watchdog against any report that loses its stamp.)"""
    r = _report(n_live=1)
    r.pop("generated_utc")
    d = _one(r, {LANE: 0})
    assert d["report_age_min"] is None and d["action"] == "DISPATCH"


# ── the registry must describe reality ──────────────────────────────────────────────────────────────────
def test_every_registered_lane_exists_in_the_account_alarm_registry():
    """A lane key that the alarm does not know is a lane whose `n_live` will always be unreadable — the
    watchdog would look armed and grade nothing. Same defect as a declared artifact nothing writes."""
    import account_orphan_alarm as A
    known = {l["key"] for l in A.ACCOUNT_LANES}
    for spec in SR.RESURRECTABLE:
        assert spec["lane"] in known, "%s is not in account_orphan_alarm.ACCOUNT_LANES" % spec["lane"]


def test_every_registered_workflow_file_exists():
    root = os.path.dirname(os.path.dirname(HERE))
    for spec in SR.RESURRECTABLE:
        p = os.path.join(root, ".github", "workflows", spec["workflow"])
        assert os.path.exists(p), "%s does not exist" % p


def test_the_dispatched_mode_is_a_real_choice_in_that_workflow():
    """A dispatch naming a mode the workflow's `choice` input does not offer is rejected by GitHub with a
    422 — silently, from this module's point of view, since it would just log a failed dispatch forever."""
    root = os.path.dirname(os.path.dirname(HERE))
    for spec in SR.RESURRECTABLE:
        text = open(os.path.join(root, ".github", "workflows", spec["workflow"])).read()
        assert spec["mode"] in text, "%s does not offer mode %s" % (spec["workflow"], spec["mode"])


def test_the_dispatched_mode_runs_the_job_the_probe_watches_for():
    """The probe counts a run as a live supervisor only when one of `watch_jobs` is running. If the mode it
    dispatches lands in a DIFFERENT job, the resurrector could never see its own successor and would
    re-dispatch on every tick — a duplicate-supervisor generator wearing a watchdog's name."""
    root = os.path.dirname(os.path.dirname(HERE))
    for spec in SR.RESURRECTABLE:
        text = open(os.path.join(root, ".github", "workflows", spec["workflow"])).read()
        for job in spec["watch_jobs"]:
            # the job's `if:` line must name the mode this module dispatches
            block = text.split("\n  %s:" % job, 1)
            assert len(block) == 2, "no job named %r in %s" % (job, spec["workflow"])
            head = block[1].split("steps:", 1)[0]
            assert spec["mode"] in head, ("%s does not route mode %s into job %r"
                                          % (spec["workflow"], spec["mode"], job))


# ── ★ THE SAFETY PIN: A WATCHDOG THAT CAN BUY IS NOT A WATCHDOG ─────────────────────────────────────────
def test_the_resurrected_mode_cannot_rent():
    """AST-pinned, the same technique that pins `account_orphan_alarm` as report-only. `mode_cofold_watch`
    must not reach any rental path: if resurrecting a lane could buy a host, an Actions API blip would
    become a purchase, and this module dispatches on exactly that kind of blip's opposite."""
    src = open(os.path.join(HERE, "selcal_vast_launch.py")).read()
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "mode_cofold_watch")
    called = {n.func.attr if isinstance(n.func, ast.Attribute) else
              (n.func.id if isinstance(n.func, ast.Name) else None)
              for n in ast.walk(fn) if isinstance(n, ast.Call)}
    for forbidden in ("submit", "mode_launch", "_place", "rent"):
        assert forbidden not in called, "mode_cofold_watch reaches %r — a resurrector must not be able to buy"


def test_the_module_dispatches_only_registered_workflows():
    """`dispatch` takes its target from the registry entry, never from anything read at runtime — so no
    artifact, report or API response can steer this module at a workflow nobody registered."""
    src = open(os.path.join(HERE, "supervisor_resurrect.py")).read()
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "dispatch")
    consts = [n.value for n in ast.walk(fn) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    assert not [c for c in consts if c.endswith(".yml")], "dispatch() hard-codes a workflow file"


# ── the probe's own fail-closed behaviour ───────────────────────────────────────────────────────────────
def test_probe_returns_none_when_the_api_is_unreadable():
    spec = SR.RESURRECTABLE[0]
    assert SR.probe_live_watches(spec, get=lambda _p: None) is None
    assert SR.probe_live_watches(spec, get=lambda _p: {"nope": 1}) is None


def test_probe_counts_only_the_supervision_job():
    """A 25-40 s `cofold_collect` run lands in the `cpu` job. Counting it would let a $0 tick mask a watch
    that is genuinely gone — the staleness mistake, mirrored."""
    spec = SR.RESURRECTABLE[0]

    def get(path):
        if "status=queued" in path:
            return {"workflow_runs": []}
        if "status=in_progress" in path:
            return {"workflow_runs": [{"id": 1}, {"id": 2}]}
        jobs = {"/actions/runs/1/jobs": [{"name": "cpu", "status": "in_progress"},
                                         {"name": "gpu", "status": "completed"}],
                "/actions/runs/2/jobs": [{"name": "gpu", "status": "in_progress"}]}
        return {"jobs": jobs[path]}
    assert SR.probe_live_watches(spec, get=get) == 1


def test_probe_counts_a_queued_run_as_alive():
    """`queued` is alive: the lane's concurrency group is cancel-in-progress:false, so a successor — or a
    hand-dispatched recovery — waits rather than collapsing. Treating it as dead stacks supervisors."""
    spec = SR.RESURRECTABLE[0]
    get = lambda p: {"workflow_runs": [{"id": 9}]} if "status=queued" in p else (  # noqa: E731
        {"workflow_runs": []} if "status=in_progress" in p else {"jobs": []})
    assert SR.probe_live_watches(spec, get=get) == 1


def test_probe_counts_an_unreadable_job_list_as_alive():
    spec = SR.RESURRECTABLE[0]

    def get(path):
        if "status=queued" in path:
            return {"workflow_runs": []}
        if "status=in_progress" in path:
            return {"workflow_runs": [{"id": 5}]}
        return None
    assert SR.probe_live_watches(spec, get=get) == 1


# ── end to end, on disk, with nothing dispatched ────────────────────────────────────────────────────────
def test_main_writes_a_dated_readout_and_dispatches_nothing_on_dry_run(tmp_path, monkeypatch):
    rep = tmp_path / "account-orphan-alarm.json"
    rep.write_text(json.dumps(_report(n_live=1)))
    out = tmp_path / "supervisor-resurrect.json"
    monkeypatch.setattr(SR, "probe_live_watches", lambda spec, token=None, get=None: 0)
    rc = SR.main(["--root", str(tmp_path), "--report", str(rep), "--json", str(out),
                  "--dry-run", "--now", "2026-08-01T18:26:00Z"])
    assert rc == 0
    d = json.loads(out.read_text())
    assert d["generated_et"].endswith("2026") and "ET" in d["generated_et"]
    assert d["decisions"][0]["action"] == "DISPATCH"
    assert d["decisions"][0]["dispatched"] is False  # --dry-run bought nothing and fired nothing


def test_main_survives_a_missing_report(tmp_path, monkeypatch):
    monkeypatch.setattr(SR, "probe_live_watches", lambda spec, token=None, get=None: 0)
    out = tmp_path / "r.json"
    rc = SR.main(["--root", str(tmp_path), "--report", str(tmp_path / "nope.json"),
                  "--json", str(out), "--now", "2026-08-01T18:26:00Z"])
    assert rc == 0
    assert json.loads(out.read_text())["decisions"][0]["dispatch"] is False
