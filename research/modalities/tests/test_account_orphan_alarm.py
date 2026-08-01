#!/usr/bin/env python3
"""A GUARD NOBODY HAS WATCHED FAIL IS NOT KNOWN TO WORK — the account-keyed alarm, driven through every branch.

`account_orphan_alarm.py` exists because on 2026-08-01 a lane rented two hosts, stopped reporting at
10:14 AM ET, and nothing noticed for 40+ minutes — one of the two hosts had already `exited`. The lane's own
watch job was still `in_progress`, so the supervisor looked alive while producing no ticks.

★★ THE FOUR NEGATIVE CONTROLS ARE THE POINT OF THIS FILE, not an addendum to it. An alarm is only worth
having if it fires on the bad case AND stays quiet on the good one, and the failure being fixed is precisely a
guard that existed and never demonstrated either. So:

    (a) stale lane + host      -> MUST fire, and MUST NAME THE INSTANCE. Today's failure, replayed.
    (b) unclaimed prefix       -> MUST fire. The lane built this morning was invisible exactly here.
    (c) fresh lane + hosts     -> MUST be silent. An alarm that fires on health is one nobody reads.
    (d) unreadable/stale census-> MUST be UNKNOWN, never all-clear. §4: an absent reading is not a reading of
                                  absence, and the census was 155 min stale at one point that same day.

★★ AND THE REPORT-ONLY PROPERTY IS PINNED BY AST, NOT BY CONVENTION. The alarm is meant to run everywhere,
on every lane including ones whose semantics it does not understand, and that is only safe because it cannot
act. A future edit that gives it a destroy call would silently turn a universal watcher into a second
unreviewed control path — the exact shape CLAUDE.md §6 keeps paying for. So `test_report_only_*` walks the
module's syntax tree rather than trusting a docstring.

Per TESTING.md rule 7 nothing here counts lanes or asserts a population: every registry check is parameterised
over whatever `ACCOUNT_LANES` holds, so a lane added tomorrow is covered the moment it is added, and one that
forgets a field fails BY NAME rather than moving a total nobody can grade.
"""
from __future__ import annotations

import ast
import datetime
import importlib
import json
import os
import pathlib

import pytest

import account_orphan_alarm as A

HERE = pathlib.Path(__file__).resolve().parent
MODALITIES = HERE.parent
REPO = MODALITIES.parent.parent

NOW = A.parse_z("2026-08-01T14:54:46Z")


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# fixtures — hand-built census documents, so every branch is reachable with no filesystem and no network
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def _inst(iid, label, status="running", cur="running", **kw):
    d = {"id": iid, "machine_id": 35778, "label": label, "actual_status": status, "cur_state": cur,
         "intended_status": "running", "gpu_name": "RTX 4090", "num_gpus": 1, "gpu_util": 0.0,
         "dph_total": 0.184, "uptime_h": 0.76, "spend_so_far_usd": 0.14, "occupies_slot": True}
    d.update(kw)
    return d


def _census(instances, utc="2026-08-01T14:54:46Z"):
    return {"_what": "test", "utc": utc, "n_instances": len(instances), "instances": instances}


def _reads(**kw):
    """lane key -> (stamp, basis, why_not). Anything unmentioned reads as an unattempted read."""
    out = {s["key"]: (None, None, "not attempted") for s in A.ACCOUNT_LANES}
    out.update(kw)
    return out


def _fresh(minutes_ago):
    return (NOW - datetime.timedelta(minutes=minutes_ago), "in-file stamp (test)", None)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# (a) NEGATIVE CONTROL — a stale lane holding a host MUST fire, and MUST name the instance
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_control_a_stale_lane_with_host_fires_and_names_the_instance():
    """TODAY'S FAILURE, REPLAYED. Two real selcal hosts, one already `exited`, and the lane last reported
    40 minutes ago. Before this module nothing in the repo could reach this conclusion, because the only
    watcher that could have was the lane's own — the thing that had stopped."""
    rep = A.build_report(
        _census([_inst(46508454, "selcal-cofold-selcal-smarca-cofold-v1-smarca2"),
                 _inst(46508511, "selcal-cofold-selcal-smarca-cofold-v1-smarca4",
                       status="exited", cur="stopped", occupies_slot=False)]),
        None, _reads(**{"selcal-cofold": _fresh(40)}), NOW)

    assert rep["ok"] is False, "a lane silent 40 min while holding two hosts must not be graded OK"
    lane = next(l for l in rep["lanes"] if l["lane"] == "selcal-cofold")
    assert lane["verdict"] == "UNSUPERVISED-BILLING"
    assert lane["ok"] is False
    # THE INSTANCE MUST BE NAMED. A verdict that says "a lane is stale" without saying WHICH BOX is one a
    # human cannot act on, and acting is the whole point of noticing.
    assert "46508454" in lane["detail"] and "46508511" in lane["detail"]
    assert {r["instance"] for r in lane["instances"]} == {46508454, 46508511}
    # and the exited one is still surfaced, not filtered out — that is what made it invisible for 40 min
    assert any(r["terminal_but_listed"] for r in lane["instances"])


def test_control_a_fires_on_a_single_host_too():
    """One host is as much unwatched money as two. No quorum, no 'it's only one box' exemption."""
    rep = A.build_report(_census([_inst(1, "selcal-cofold-x")]), None,
                         _reads(**{"selcal-cofold": _fresh(90)}), NOW)
    assert rep["ok"] is False
    assert next(l for l in rep["lanes"] if l["lane"] == "selcal-cofold")["verdict"] == "UNSUPERVISED-BILLING"


def test_control_a_alarm_text_disclaims_having_acted():
    """The alarm must state that it did NOT act. A reader who assumes a guard reaped the box will not reap
    it, and a report-only guard that reads like an actor is worse than no guard at all."""
    rep = A.build_report(_census([_inst(1, "selcal-cofold-x")]), None,
                         _reads(**{"selcal-cofold": _fresh(90)}), NOW)
    d = next(l for l in rep["lanes"] if l["lane"] == "selcal-cofold")["detail"].lower()
    assert "will not" in d and ("destroy" in d or "rent" in d)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# (b) NEGATIVE CONTROL — a host whose prefix matches NO registered lane MUST fire
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_control_b_unclaimed_prefix_is_an_orphan_and_fires():
    """The lane-built-this-morning case. An unregistered lane's hosts do not vanish from the account, so
    forgetting to register one is LOUD here rather than silent — which is the inverse of the failure."""
    rep = A.build_report(_census([_inst(99, "brandnewlane-somejob-seed3")]), None, _reads(), NOW)
    assert rep["ok"] is False
    assert rep["verdict"] == "ORPHAN-HOST"
    assert [o["instance"] for o in rep["orphans"]] == [99]
    assert "brandnewlane-somejob-seed3" in rep["orphan_detail"]
    # it must not be silently absorbed into some lane's host list
    assert all(99 not in {r["instance"] for r in l["instances"]} for l in rep["lanes"])


def test_control_b_orphan_fires_even_when_every_lane_is_healthy():
    """An orphan is not excused by good company. If every registered lane is fresh and one box is unclaimed,
    the run is still not OK — otherwise a healthy fleet hides an abandoned host."""
    rep = A.build_report(
        _census([_inst(1, "selcal-cofold-ok"), _inst(2, "mystery-box")]),
        None, _reads(**{"selcal-cofold": _fresh(2)}), NOW)
    assert rep["ok"] is False
    assert [o["instance"] for o in rep["orphans"]] == [2]


def test_orphan_attribution_prefers_the_longest_prefix():
    """Prefixes are not guaranteed disjoint forever. A short prefix swallowing a longer one's boxes would
    credit a live lane's hosts to a quiet lane — which renders as healthy, the error class this whole module
    exists to stop. Longest-match makes it deterministic regardless of registry order."""
    lanes = [{"key": "short", "label_prefixes": ("ab-",), "fragment": "f.json", "time_keys": ("utc",)},
             {"key": "long", "label_prefixes": ("ab-cd-",), "fragment": "f.json", "time_keys": ("utc",)}]
    assert A.match_lane("ab-cd-thing", lanes)["key"] == "long"
    assert A.match_lane("ab-other", lanes)["key"] == "short"
    assert A.match_lane("zz-thing", lanes) is None
    assert A.match_lane(None, lanes) is None


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# (c) NEGATIVE CONTROL — a FRESH lane holding hosts MUST be silent
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_control_c_fresh_lane_with_hosts_is_silent():
    """The common, healthy case. An alarm that fires here is one nobody reads by tomorrow, and then the next
    real incident is invisible again."""
    rep = A.build_report(
        _census([_inst(46508454, "selcal-cofold-a"), _inst(46508455, "selcal-cofold-b")]),
        None, _reads(**{"selcal-cofold": _fresh(3)}), NOW)
    assert rep["ok"] is True
    assert rep["verdict"] == "ALL-SUPERVISED"
    assert next(l for l in rep["lanes"] if l["lane"] == "selcal-cofold")["verdict"] == "SUPERVISED"


def test_control_c_stale_lane_with_NO_hosts_is_also_silent():
    """THE OTHER HALF OF THE PAIR. A finished or parked lane is silent forever and nothing is billing for it,
    so grading its age would fire permanently on every completed lane. The conjunction is what buys the
    quiet — remove it and this alarm is noise within a day."""
    rep = A.build_report(_census([]), None, _reads(**{"selcal-cofold": _fresh(100000)}), NOW)
    assert rep["ok"] is True
    assert next(l for l in rep["lanes"] if l["lane"] == "selcal-cofold")["verdict"] == "IDLE"


def test_terminal_instance_on_a_FRESH_lane_is_reported_but_does_not_alarm():
    """`exited` is surfaced unconditionally — it was invisible today — but a lane that IS reporting owns its
    own reap, and duplicating that judgement here would be the second control path §6 forbids."""
    rep = A.build_report(
        _census([_inst(7, "selcal-cofold-a", status="exited", cur="stopped", occupies_slot=False)]),
        None, _reads(**{"selcal-cofold": _fresh(2)}), NOW)
    assert rep["ok"] is True
    assert [r["instance"] for r in rep["terminal_but_listed"]] == [7]
    assert "TERMINAL" in next(l for l in rep["lanes"] if l["lane"] == "selcal-cofold")["detail"]


@pytest.mark.parametrize("status,cur", [("exited", "stopped"), ("stopped", "stopped"),
                                        ("offline", "offline"), ("running", "stopped")])
def test_terminal_states_are_detected_from_either_field(status, cur):
    """Today's host read `actual_status: exited` AND `cur_state: stopped`. Requiring both to agree would let
    a half-terminal instance slip through, so either field is sufficient."""
    assert A.instance_row(_inst(1, "x", status=status, cur=cur), None)["terminal_but_listed"] is True


def test_a_running_instance_is_not_flagged_terminal():
    assert A.instance_row(_inst(1, "x"), None)["terminal_but_listed"] is False


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# (d) NEGATIVE CONTROL — an unreadable or stale census is UNKNOWN, never all-clear
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_control_d_unreadable_census_is_unknown_not_all_clear():
    """§4: AN ABSENT READING IS NOT A READING OF ABSENCE. 'I cannot see any instance' and 'there is no
    instance' are opposite facts and a naive check renders them identically."""
    rep = A.build_report(None, "ternary-vast-account-census.json: not present", _reads(), NOW)
    assert rep["ok"] is False
    assert rep["verdict"] == "CENSUS-UNKNOWN"
    assert rep["lanes"] == [] and rep["orphans"] == []


def test_control_d_stale_census_is_unknown_and_grades_nothing():
    """MEASURED TODAY: the census went 155 min stale. A check that graded lanes off it would have reported
    all-clear at the exact moment two hosts were up and unwatched."""
    stale = _census([_inst(1, "selcal-cofold-a")], utc="2026-08-01T12:19:00Z")  # 155 min before NOW
    rep = A.build_report(stale, None, _reads(**{"selcal-cofold": _fresh(2)}), NOW)
    assert rep["ok"] is False
    assert rep["verdict"] == "CENSUS-STALE"
    assert rep["census_age_min"] == pytest.approx(155.8, abs=1.0)
    # NOTHING is graded off a census that is not evidence — not even the lane that looked fine
    assert rep["lanes"] == []


def test_control_d_census_with_no_parseable_utc_is_unknown():
    """A census whose age is unknown cannot be evidence of what the account holds RIGHT NOW."""
    rep = A.build_report({"instances": [], "utc": "not-a-date"}, None, _reads(), NOW)
    assert rep["ok"] is False and rep["verdict"] == "CENSUS-UNKNOWN"


def test_control_d_census_missing_instances_list_is_unknown_not_empty():
    """An unparseable census is not an empty account — the same absent-vs-absence rule one level down."""
    rep = A.build_report({"utc": "2026-08-01T14:54:46Z"}, None, _reads(), NOW)
    assert rep["ok"] is False and rep["verdict"] == "CENSUS-UNKNOWN"


def test_a_lane_whose_freshness_is_unreadable_while_holding_hosts_is_unknown():
    """Fail closed at the LANE level too: 'billing and unwatchable' must never be graded better than
    'billing and stale'."""
    rep = A.build_report(_census([_inst(1, "selcal-cofold-a")]), None, _reads(), NOW)
    lane = next(l for l in rep["lanes"] if l["lane"] == "selcal-cofold")
    assert lane["verdict"] == "LANE-UNKNOWN" and lane["ok"] is False and rep["ok"] is False


def test_a_lane_with_no_fragment_holding_hosts_is_unwatchable_and_loud():
    """A lane that commits no tick artifact at all is stated, not faked — and while it holds hosts that is an
    alarm, because 'I cannot tell' about billing money is worse news than 'it is stale', not better."""
    rep = A.build_report(_census([_inst(1, "protfep-bench-leg3")]), None, _reads(), NOW)
    lane = next(l for l in rep["lanes"] if l["lane"] == "protfep-bench")
    assert lane["verdict"] == "UNWATCHABLE-BILLING" and rep["ok"] is False


def test_a_lane_with_no_fragment_and_no_hosts_is_still_quiet():
    """…but only while it is billing. Idle costs nothing, so it must not fire."""
    rep = A.build_report(_census([]), None, _reads(), NOW)
    assert next(l for l in rep["lanes"] if l["lane"] == "protfep-bench")["verdict"] == "IDLE"
    assert rep["ok"] is True


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# REPORT-ONLY, pinned by AST — the property that makes it safe to run this on every lane
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
_SRC = (MODALITIES / "account_orphan_alarm.py").read_text()
_TREE = ast.parse(_SRC)

#: Verbs and endpoints that would make this an ACTOR. Checked as call targets and as string literals, because
#: a Vast mutation is a URL as often as it is a function name.
_DESTRUCTIVE_CALLS = ("destroy", "destroy_instance", "stop_instance", "reap", "terminate", "delete_instance",
                      "submit", "rent", "bid", "launch", "create_instance", "poweroff", "shutdown", "kill")
_FORBIDDEN_STRINGS = ("/instances/destroy", "destroy_instance", "put_instance", "DELETE",
                      "api.vast.ai", "http://", "https://")


def _called_names(tree):
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                out.add(f.id)
            elif isinstance(f, ast.Attribute):
                out.add(f.attr)
    return out


def test_report_only_no_destructive_call():
    """THE PROPERTY THAT LETS THIS RUN EVERYWHERE. Noticing is safe on a lane whose semantics the watcher does
    not understand; ACTING is not. A future edit adding a destroy path turns a universal watcher into a
    second unreviewed control path, so it is pinned in the syntax tree, not in a docstring."""
    hits = sorted(_called_names(_TREE) & set(_DESTRUCTIVE_CALLS))
    assert not hits, (f"account_orphan_alarm.py calls {hits} — it is REPORT-ONLY by design. Every destructive "
                      f"act belongs in the lanes' own collect paths and in vast_idle_guard.py, which is the "
                      f"one thing CLAUDE.md §6 permits to condemn a box.")


def test_report_only_makes_no_network_call():
    """It must survive the credential outage it is meant to report. No Vast key, no boto3, no HTTP: an alarm
    that dies with the thing it watches is not an alarm."""
    bad = [s for s in _FORBIDDEN_STRINGS
           if any(isinstance(n, ast.Constant) and isinstance(n.value, str) and s in n.value
                  for n in ast.walk(_TREE))]
    assert not bad, f"account_orphan_alarm.py mentions {bad} — it must make no network call"
    imported = {n.module.split(".")[0] for n in ast.walk(_TREE)
                if isinstance(n, ast.ImportFrom) and n.module}
    imported |= {a.name.split(".")[0] for n in ast.walk(_TREE) if isinstance(n, ast.Import) for a in n.names}
    for forbidden in ("boto3", "requests", "urllib", "http", "botocore", "google"):
        assert forbidden not in imported, f"account_orphan_alarm.py imports {forbidden}"


def test_it_imports_nothing_from_any_lane():
    """AN ALARM THAT SHARES A DEPENDENCY WITH THE THING IT WATCHES DIES WITH IT — that is how the 11:37 AM
    tick on 2026-07-27 took its own progress check down. Including `lane_staleness_watch`: this module is the
    backstop for the case where THAT watcher's driver has stalled."""
    imported = {n.module.split(".")[0] for n in ast.walk(_TREE)
                if isinstance(n, ast.ImportFrom) and n.module}
    imported |= {a.name.split(".")[0] for n in ast.walk(_TREE) if isinstance(n, ast.Import) for a in n.names}
    stdlib = {"argparse", "datetime", "json", "os", "re", "subprocess", "sys", "__future__"}
    assert imported <= stdlib, (f"account_orphan_alarm.py imports {sorted(imported - stdlib)} — it must be "
                                f"pure stdlib so it cannot be taken down by the lanes it watches")


def test_gpu_util_is_never_read():
    """`vast_idle_guard`'s INVIOLABLE RULE: GPU IDLENESS NEVER CONDEMNS A BOX. Both of today's selcal
    instances read `gpu_util: 0.0`, including the one that was working. The key sits right there in every
    census record, so the only durable protection is asserting it is never touched."""
    for n in ast.walk(_TREE):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            assert n.value != "gpu_util", "gpu_util must never be READ here — GPU idleness never condemns"
        if isinstance(n, ast.Attribute):
            assert n.attr != "gpu_util"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# registry truthfulness — parameterised, never counted (TESTING.md rule 7)
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("spec", A.ACCOUNT_LANES, ids=lambda s: s["key"])
def test_every_lane_declares_the_fields_a_verdict_needs(spec):
    assert spec.get("key") and spec.get("label") and spec.get("tick_workflow")
    assert spec.get("label_prefixes"), "a lane with no label prefix can never be attributed a host"
    assert all(isinstance(p, str) and p for p in spec["label_prefixes"])
    if spec.get("fragment"):
        assert spec.get("time_keys"), "a fragment with no declared time key can only ever use the weak basis"
        assert spec.get("time_mode") in ("iso", "iso_in_string")
    else:
        # Stated, never faked: a lane with no artifact must SAY why, because that absence is what makes it
        # UNWATCHABLE-BILLING and a reader is owed the reason.
        assert spec.get("no_fragment_why")


@pytest.mark.parametrize("spec", [s for s in A.ACCOUNT_LANES if s.get("fragment")], ids=lambda s: s["key"])
def test_declared_fragments_exist(spec):
    """A DECLARED ARTIFACT THAT NOTHING PRODUCES IS NOT AN ARTIFACT. Same rule, and same reason, as
    `test_lane_registry_contract.py`: on 2026-07-31 a hold artifact was named in three places and had never
    been committed, and the watcher's "not present in the repo" read like a lane being quiet rather than like
    a monitor that was never wired up. Here the consequence is sharper — a fragment that does not exist
    silently demotes a lane to the WEAK git basis, or to LANE-UNKNOWN, forever."""
    assert (MODALITIES / spec["fragment"]).exists(), (
        f"{spec['key']} declares fragment {spec['fragment']!r}, which is not in the repo. Either it is never "
        f"written (then the lane is not gradeable and must declare fragment=None with a reason), or the path "
        f"is wrong.")


@pytest.mark.parametrize("spec", A.ACCOUNT_LANES, ids=lambda s: s["key"])
def test_declared_tick_workflow_exists(spec):
    """A lane pointing a human at a workflow nobody ships is a dead end at the worst moment."""
    assert (REPO / ".github" / "workflows" / spec["tick_workflow"]).exists(), (
        f"{spec['key']} names tick_workflow {spec['tick_workflow']!r}, which does not exist")


@pytest.mark.parametrize("spec", A.ACCOUNT_LANES, ids=lambda s: s["key"])
def test_prefix_matches_the_module_that_actually_mints_it(spec):
    """★★ §1, ONE FACT ONE PLACE — ENFORCED AT TEST TIME SO THE RUNTIME CAN STAY INDEPENDENT.

    The alarm must not import a lane module (see `test_it_imports_nothing_from_any_lane`), but a prefix typed
    here that has drifted from the constant that actually names the boxes would silently produce ORPHAN-HOST
    on a healthy lane, or worse, attribute nothing and call a billing lane IDLE. So the agreement is checked
    HERE, where importing the lane is free and a broken lane module cannot take the alarm down with it."""
    mod_name, _, const = spec["prefix_source"].partition(".")
    try:
        mod = importlib.import_module(mod_name)
    except Exception as e:  # noqa: BLE001 - an unimportable lane must not be silently skipped
        pytest.skip(f"{mod_name} is not importable in this environment ({type(e).__name__}); "
                    f"the prefix agreement for {spec['key']} could not be checked")
    actual = getattr(mod, const, None)
    assert isinstance(actual, str) and actual, f"{spec['prefix_source']} is not a non-empty string"
    assert actual in spec["label_prefixes"], (
        f"{spec['key']} declares prefixes {spec['label_prefixes']} but {spec['prefix_source']} mints "
        f"{actual!r} — a drifted prefix makes a healthy lane look like an orphan, or a billing lane look idle")


def test_lane_keys_are_unique():
    keys = [s["key"] for s in A.ACCOUNT_LANES]
    assert len(keys) == len(set(keys)), "duplicate lane keys would silently drop one lane's hosts"


def test_no_prefix_is_a_prefix_of_another_lanes_prefix_without_longest_match_saving_it():
    """Documented rather than forbidden: overlap is legal because `match_lane` resolves it by longest match.
    This asserts the resolution HOLDS for the registry as it actually stands, so an overlap introduced later
    is caught with the pair named."""
    for a in A.ACCOUNT_LANES:
        for b in A.ACCOUNT_LANES:
            if a["key"] == b["key"]:
                continue
            for pa in a["label_prefixes"]:
                for pb in b["label_prefixes"]:
                    if pa.startswith(pb) or pb.startswith(pa):
                        longer = a if len(pa) > len(pb) else b
                        assert A.match_lane(max(pa, pb, key=len) + "-x", A.ACCOUNT_LANES)["key"] == \
                            longer["key"], f"{a['key']} and {b['key']} overlap and do not resolve cleanly"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# freshness basis — the strong/weak distinction must survive, and must be visible
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_in_file_stamp_is_extracted_from_a_plain_iso_key():
    spec = {"time_keys": ("generated_utc",), "time_mode": "iso"}
    got, why = A.fragment_stamp(spec, {"generated_utc": "2026-08-01T14:41:08Z"})
    assert got == A.parse_z("2026-08-01T14:41:08Z") and why is None


def test_in_file_stamp_is_extracted_from_a_free_text_field():
    """selcal's census has no timestamp KEY — it has `phase`, e.g.
    "done rc=0 2026-08-01T14:41:08Z instance=46508454 attempt=20260801T144027Z". That IS a real tick stamp:
    only a run that executed writes it. Extracting beats the git fallback, which cannot tell a tick from a
    refactor."""
    spec = {"time_keys": ("phase",), "time_mode": "iso_in_string"}
    got, why = A.fragment_stamp(
        spec, {"phase": "done rc=0 2026-08-01T14:41:08Z instance=46508454 attempt=20260801T144027Z"})
    assert got == A.parse_z("2026-08-01T14:41:08Z") and why is None


def test_a_missing_or_unparseable_stamp_returns_a_REASON_not_a_default():
    """Absent is never a legal good value. A stamp that coalesced to the epoch would render an unread lane as
    infinitely stale; one that coalesced to `now` would render it as perfectly fresh. Both are lies."""
    spec = {"time_keys": ("generated_utc",), "time_mode": "iso"}
    got, why = A.fragment_stamp(spec, {"other": 1})
    assert got is None and "absent" in why
    got, why = A.fragment_stamp(spec, {"generated_utc": "garbage"})
    assert got is None and "unparseable" in why
    got, why = A.fragment_stamp(spec, None)
    assert got is None and why


def test_the_weak_git_basis_is_labelled_as_weak_wherever_it_is_used():
    """§4: A POPULATED FIELD IS NOT A MEASURED ONE. The git fallback can only ever make a lane look FRESHER
    than it is, so a verdict resting on it must say so — otherwise a refactor silences the alarm."""
    stamp, basis, why = A.read_lane_freshness(
        str(MODALITIES), {"key": "t", "fragment": "ternary-vast-watch.json", "time_keys": ("nope",),
                          "time_mode": "iso"})
    if stamp is not None:
        assert "WEAKER" in basis and "fresher" in basis


def test_no_git_disables_the_weak_basis_rather_than_silently_using_it():
    stamp, basis, why = A.read_lane_freshness(
        str(MODALITIES), {"key": "t", "fragment": "ternary-vast-watch.json", "time_keys": ("nope",),
                          "time_mode": "iso"}, use_git=False)
    assert stamp is None and "git fallback disabled" in why


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# end-to-end over the REAL committed artifacts — it must actually run here, not just in theory
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_it_runs_against_the_committed_census_and_renders(tmp_path):
    out = tmp_path / "r.json"
    rc = A.main(["--root", str(MODALITIES), "--json", str(out), "--now", "2026-08-01T14:54:46Z"])
    assert rc in (0, 1)
    rep = json.loads(out.read_text())
    assert rep["report_only"] is True
    assert rep["generated_et"].endswith("2026") and " ET " in rep["generated_et"], \
        "CLAUDE.md §1 — every reported time is US Eastern, 12-hour"
    assert A.render(rep)


def test_times_are_reported_in_us_eastern_12_hour():
    """§1, and it is asserted rather than trusted because this is the rule the repo says keeps slipping."""
    t = A.parse_z("2026-08-01T14:54:46Z")
    assert A._et(t) == "10:54 AM ET Aug 1, 2026"
    assert A._et(None) is None
