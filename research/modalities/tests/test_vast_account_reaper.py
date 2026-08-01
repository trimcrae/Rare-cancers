#!/usr/bin/env python3
"""A GUARD NOBODY HAS WATCHED FAIL IS NOT KNOWN TO WORK — the central account reaper, driven through every
branch, including every branch that must NOT destroy.

This module destroys hosts. That makes it the one place in the repo where an untested branch is an
irreversible one, and the reason for this file is measured rather than stylistic: on 2026-08-01 FOUR separate
lane teardown paths were each found to be broken, in four different ways, and every one of them "ran and
exited success" while a box billed.

★★ THE FIVE NEGATIVE CONTROLS ARE THE POINT OF THIS FILE, not an addendum. Each replays a real incident:

    (1) terminal host                -> REAPED.  selcal 46508511 sat `exited` with 0 models while its lane's
                                                 `mode=reap` ran and exited success.
    (2) host mid-work                -> SPARED.  a healthy fan-out leg legitimately runs for many hours.
    (3) `gpu_util: 0.0` but writing  -> SPARED.  BOTH selcal boxes read 0.0 INCLUDING THE WORKING ONE, and on
                                                 2026-07-27 two step-1 boxes read 0.0 while committing real
                                                 production sampling.
    (4) stale census                 -> NOTHING REAPED. The account census was measured 155 min stale earlier
                                                 the same day; a naive check reads that as an empty fleet.
    (5) `done` record older than the
        instance                     -> SPARED.  ternary 46459452, destroyed 2 min 23 s in, mid image-pull,
                                                 because that unit's `leg.json` had said `done` for five days.

Per TESTING.md rule 7 nothing here asserts a population count or a label — every check asserts the PROPERTY
(what was destroyed, and why), so a lane added tomorrow does not turn this file red.
"""
from __future__ import annotations

import ast
import datetime
import json
import pathlib

import pytest

import account_orphan_alarm as AOA
import vast_account_reaper as R

HERE = pathlib.Path(__file__).resolve().parent
MODALITIES = HERE.parent

NOW = R.parse_z("2026-08-01T16:10:00Z")
TERMINAL, TERMINAL_NOTES = R.terminal_states_from_source(str(MODALITIES))

# 2026-08-01T14:09:04Z — one of the real selcal rentals.
START = 1785593344.0


def _inst(iid, label="s1f-01-unit", status="running", cur="running", start=START, **kw):
    d = {"id": iid, "machine_id": 35778, "label": label, "actual_status": status, "cur_state": cur,
         "intended_status": "running", "gpu_name": "RTX 4090", "num_gpus": 1, "gpu_util": 0.0,
         "dph_total": 0.184, "uptime_h": 2.0, "spend_so_far_usd": 0.36, "start_date": start,
         "occupies_slot": True}
    d.update(kw)
    return d


def _census(instances, utc="2026-08-01T16:04:52Z"):
    return {"_what": "test", "utc": utc, "n_instances": len(instances), "instances": instances}


def _plan(census, **kw):
    kw.setdefault("terminal", TERMINAL)
    kw.setdefault("terminal_notes", TERMINAL_NOTES)
    return R.build_plan(census, None, NOW, **kw)


def _ids(rows):
    return [r["instance"] for r in (rows or [])]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the terminal vocabulary is DERIVED, not typed (§1)
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_terminal_set_is_the_union_of_the_two_lane_definitions():
    """§1 — ONE FACT, ONE PLACE. Two lane modules already define what terminal means and neither can be
    imported (one is a function-local, and importing a lane would make the central reaper die whenever a lane
    does). This asserts the AST derivation reproduces BOTH, so a lane that adds a state gets it for free and a
    lane that renames one fails HERE rather than silently narrowing what the reaper can see."""
    src = (MODALITIES / "congeneric_fanout_vast.py").read_text()
    tree = ast.parse(src)
    local = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "_TERMINAL" for t in node.targets):
            local = R._tuple_of_str(node.value)
    assert local, "congeneric_fanout_vast._TERMINAL is no longer a literal tuple — the derivation must move"
    assert set(local) <= TERMINAL

    nrv = ast.parse((MODALITIES / "nrv04_vast_launch.py").read_text())
    other = None
    for node in ast.walk(nrv):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "_TERMINAL_STATES" for t in node.targets):
            other = R._tuple_of_str(node.value)
    assert other, "nrv04_vast_launch._TERMINAL_STATES is no longer a literal tuple"
    assert set(other) <= TERMINAL


def test_terminal_set_agrees_with_the_report_only_alarm():
    """The alarm reports terminal-but-listed; this module DESTROYS on it. If the two ever disagreed, a host
    could be flagged by one and invisible to the other — which is the "we noticed and did not act" gap this
    module closes."""
    assert set(AOA.TERMINAL_STATES) == set(TERMINAL), (
        f"the alarm sees {sorted(AOA.TERMINAL_STATES)} and the reaper sees {sorted(TERMINAL)}; a state in one "
        f"and not the other is a host that gets reported and never cleared, or cleared and never reported")


@pytest.mark.parametrize("early", R.EARLY_STATES)
def test_created_is_never_terminal(early):
    """⚠ AN EARLIER DRAFT HAD `created` IN THE TERMINAL SET AND WOULD HAVE DESTROYED EVERY FRESH RENTAL — a
    reaper that reaps the healthiest event in the system. Neither repo definition contains it."""
    assert early not in TERMINAL
    v = R.classify_instance(_inst(1, status=early, cur=early), terminal=TERMINAL)
    assert v["action"] == R.SPARE


def test_an_unreadable_terminal_definition_disables_rule_1_rather_than_narrowing_it(tmp_path):
    """§4 — an unreadable definition is not an empty one. If the lanes' sources cannot be read, RULE 1 must
    STOP RUNNING and say so, not quietly decide that nothing is terminal."""
    term, notes = R.terminal_states_from_source(str(tmp_path))
    assert term == frozenset()
    assert notes and all("NOT in this union" in n for n in notes)
    plan = R.build_plan(_census([_inst(1, status="exited", cur="exited")]), None, NOW,
                        terminal=term, terminal_notes=notes)
    assert plan["reap"] == []
    assert "RULE 1 IS DISABLED" in plan["rule_1_disabled"]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# CONTROL 1 — a terminal host is reaped
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("status,cur", [("exited", "exited"), ("exited", "running"), ("running", "exited"),
                                        ("stopped", "stopped"), ("offline", "running"), ("error", "error")])
def test_control_1_terminal_host_is_reaped_on_either_field(status, cur):
    """selcal 46508511 sat `exited` with zero models banked and its lane's `mode=reap` ran, exited SUCCESS and
    destroyed nothing. Either status field is sufficient: a half-terminal instance is still an object only the
    control plane can clear, and the cost of being wrong in this direction is zero."""
    plan = _plan(_census([_inst(46508511, status=status, cur=cur)]))
    assert _ids(plan["reap"]) == [46508511]
    assert plan["reap"][0]["rule"] == "RULE-1-TERMINAL"
    assert "CANNOT LOSE WORK BY CONSTRUCTION" in plan["reap"][0]["why"]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# CONTROL 2 — a host mid-work is spared
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_control_2_host_mid_work_is_spared():
    """A live fan-out leg: running, busy GPU, no completion record. Nothing may touch it."""
    plan = _plan(_census([_inst(46514055, label="tvast-5aks-r0", gpu_util=97.0)]))
    assert plan["reap"] == []
    assert _ids(plan["spare"]) == [46514055]


def test_control_2b_age_alone_never_reaps():
    """⛔ NEVER REAP ON AGE. A healthy fan-out leg legitimately runs for many hours; 40 h of uptime is not
    evidence of anything, and a runtime backstop is a LANE's decision, not this module's."""
    plan = _plan(_census([_inst(1, uptime_h=40.0, spend_so_far_usd=7.36,
                                start=START - 40 * 3600)]))
    assert plan["reap"] == []


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# CONTROL 3 — gpu_util 0.0 while writing is spared, and the key is never even read
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_control_3_gpu_util_zero_but_working_is_spared():
    """★★ THE INVIOLABLE RULE. Both selcal boxes read `gpu_util: 0.0` INCLUDING THE ONE THAT WAS WORKING
    CORRECTLY, and on 2026-07-27 two step-1 boxes read 0.0 in the same snapshot in which they committed real
    production sampling. GPU idleness NEVER condemns a box."""
    plan = _plan(_census([_inst(46508454, gpu_util=0.0, uptime_h=1.93)]))
    assert plan["reap"] == []
    assert "gpu_util" in plan["spare"][0]["why"]           # named as a NON-reason, explicitly


def test_control_3b_gpu_util_is_never_read_anywhere_in_the_module():
    """Pinned by AST rather than by care. A future edit that reads the key would turn the one rule
    `vast_idle_guard` calls inviolable into a suggestion, and it would do so silently."""
    tree = ast.parse((MODALITIES / "vast_account_reaper.py").read_text())
    reads = [n for n in ast.walk(tree)
             if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value == "gpu_util"]
    # The docstring/why-strings MENTION it; what is forbidden is using it as a key.
    subscripts = [n for n in ast.walk(tree)
                  if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)
                  and n.slice.value == "gpu_util"]
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get"
             and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value == "gpu_util"]
    assert not subscripts and not calls, (
        "vast_account_reaper reads `gpu_util`. GPU idleness NEVER condemns a box — measured: both selcal "
        "instances read 0.0 including the working one, and two step-1 boxes read 0.0 while committing "
        "production sampling. Remove the read.")
    assert reads, "the module should still DOCUMENT why gpu_util is not read"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# CONTROL 4 — a stale or unreadable census reaps nothing
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_control_4_stale_census_reaps_nothing():
    """The census was measured 155 min stale earlier the same day. For a REAPER the danger is sharper than
    for an alarm: a lane that relaunched inside the gap would have its NEW box judged on its OLD box's
    state."""
    plan = _plan(_census([_inst(1, status="exited", cur="exited")], utc="2026-08-01T13:20:00Z"))
    assert plan["verdict"] == "CENSUS-STALE"
    assert plan["graded"] is False
    assert plan["reap"] is None            # null, NEVER [] — those are opposite facts
    assert plan["n_reap"] is None


@pytest.mark.parametrize("census,err", [
    (None, "not present"),
    ({"utc": "not-a-date", "instances": []}, None),
    ({"utc": "2026-08-01T16:04:52Z"}, None),                      # no instances list
    ({"utc": "2026-08-01T18:04:52Z", "instances": []}, None),     # stamped in the FUTURE
])
def test_control_4b_every_census_absence_is_fail_closed(census, err):
    plan = R.build_plan(census, err, NOW, terminal=TERMINAL, terminal_notes=TERMINAL_NOTES)
    assert plan["graded"] is False and plan["ok"] is False
    assert plan["reap"] is None and plan["spare"] is None
    assert plan["verdict"] in ("CENSUS-UNKNOWN", "CENSUS-STALE")


def test_control_4c_a_fail_closed_plan_is_never_executed_even_when_armed():
    """The guarantee has to hold for anyone who imports `execute`, not only for the CLI."""
    plan = _plan(_census([_inst(1, status="exited")], utc="2026-08-01T13:20:00Z"))
    called = []
    res = R.execute(plan, NOW, armed=True, destroy=lambda i: called.append(i))
    assert called == []
    assert res["destroyed"] == [] and "fail-closed" in res["skipped_why"]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# CONTROL 5 — a `done` record older than the instance spares the host (the 46459452 case)
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_control_5_done_record_older_than_the_instance_spares():
    """★★ THE INCIDENT. Ternary 46459452 was destroyed 2 min 23 s in, mid image-pull, because
    `finished = uid in done` was true — that unit's `leg.json` had said `done` since the ORIGINAL smoke FIVE
    DAYS EARLIER. It produced no `[prune]` line, no manifest, no `run.log`, not even a `status.json`."""
    inst = _inst(46459452, label="tvast-5aks-rerun", start=START)
    five_days_before = START - 5 * 86400
    ok, why = R.record_is_newer_than_instance(five_days_before, inst)
    assert ok is False
    assert "PREVIOUS attempt" in why and "46459452" in why


def test_control_5b_a_record_written_by_this_host_does_attribute():
    inst = _inst(46508454, start=START)
    ok, why = R.record_is_newer_than_instance(START + 1900.0, inst)
    assert ok is True and "THIS rental" in why


@pytest.mark.parametrize("rec,started", [(None, START), (START, None), (START, "nonsense")])
def test_control_5c_every_ambiguity_in_attribution_spares(rec, started):
    """A missing stamp, a missing `start_date`, an unparseable one: none is evidence that the host finished."""
    ok, _ = R.record_is_newer_than_instance(rec, _inst(1, start=started))
    assert ok is False


def test_control_5d_rule_2_cannot_fire_without_positive_banked_evidence():
    """There is no default-reap path. `banked` absent, `banked: False`, or an evidence dict that never says
    True must all SPARE."""
    for banked in (None, {}, {"banked": False, "why": "no artifact under the prefix"},
                   {"banked": None, "why": "the object store could not be listed"}):
        v = R.classify_instance(_inst(1), terminal=TERMINAL, banked=banked)
        assert v["action"] == R.SPARE


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# the ladder — dry-run first, and billed hours latched BEFORE the DELETE
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_dry_run_calls_nothing_and_still_records_what_it_would_do(tmp_path):
    plan = _plan(_census([_inst(46508511, status="exited", cur="exited")]))
    led = tmp_path / "ledger.jsonl"
    res = R.execute(plan, NOW, armed=False, ledger_path=str(led),
                    destroy=lambda i: pytest.fail("dry run must never call destroy"))
    assert res["destroyed"] == [{"instance": 46508511, "rule": "RULE-1-TERMINAL",
                                 "outcome": "WOULD-DESTROY"}]
    rows = [json.loads(l) for l in led.read_text().splitlines()]
    assert [r["outcome"] for r in rows] == ["WOULD-DESTROY"]


def test_billed_hours_are_latched_BEFORE_the_delete():
    """★★ THE ORDERING IS THE POINT. The instance record is the only place billed hours exist and it stops
    existing the moment the DELETE lands. A rental that billed and left no trace has already happened here."""
    plan = _plan(_census([_inst(46508511, status="exited", cur="exited", uptime_h=2.03,
                                spend_so_far_usd=0.374, dph_total=0.184)]))
    order = []
    real_append = R.append_ledger

    def spy_append(path, line):
        order.append(("ledger", line["outcome"], line["billed_hours_at_destroy"],
                      line["spend_so_far_usd_at_destroy"]))
        real_append(path, line)

    R.append_ledger = spy_append
    try:
        R.execute(plan, NOW, armed=True, ledger_path=None,
                  destroy=lambda i: order.append(("DELETE", i)))
    finally:
        R.append_ledger = real_append

    assert order[0][0] == "ledger" and order[0][1] == "DESTROY-ATTEMPTED"
    assert order[0][2] == 2.03 and order[0][3] == 0.374, "billed hours must be latched from the census row"
    assert order[1] == ("DELETE", 46508511)
    assert order[2][0] == "ledger" and order[2][1] == "DESTROYED"


def test_a_failed_destroy_is_recorded_and_does_not_stop_the_rest(tmp_path):
    plan = _plan(_census([_inst(1, status="exited", cur="exited"),
                          _inst(2, status="exited", cur="exited")]))
    led = tmp_path / "l.jsonl"

    def destroy(i):
        if i == 1:
            raise RuntimeError("429 rate limited")

    res = R.execute(plan, NOW, armed=True, ledger_path=str(led), destroy=destroy)
    assert [f["instance"] for f in res["failed"]] == [1]
    assert [d["instance"] for d in res["destroyed"]] == [2]
    outcomes = [json.loads(l)["outcome"] for l in led.read_text().splitlines()]
    assert outcomes == ["DESTROY-ATTEMPTED", "DESTROY-FAILED", "DESTROY-ATTEMPTED", "DESTROYED"]


def test_the_cli_defaults_to_dry_run(monkeypatch, tmp_path):
    """The ladder's first rung must be the DEFAULT, not an opt-in. A reaper whose safe mode needs a flag is
    one flag away from an irreversible accident."""
    monkeypatch.setattr(R, "vast_destroy", lambda i: pytest.fail("the CLI must not destroy without --arm"))
    out = tmp_path / "plan.json"
    rc = R.main(["--root", str(MODALITIES), "--now", "2026-08-01T16:10:00Z", "--json", str(out)])
    assert rc == 0
    doc = json.loads(out.read_text())
    assert doc["mode"] == "DRY-RUN"
    assert doc["execution"]["mode"] == "DRY-RUN"


def test_the_only_destructive_call_is_the_one_named_vast_destroy():
    """AST pin. Every irreversible effect must go through ONE function, so a reviewer has ONE thing to read
    and a test has ONE thing to refuse. A second DELETE path added anywhere in this module fails here."""
    tree = ast.parse((MODALITIES / "vast_account_reaper.py").read_text())
    deletes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for a in node.args:
                if isinstance(a, ast.Constant) and a.value == "DELETE":
                    deletes.append(node)
    assert len(deletes) == 1, "there must be exactly one DELETE call site in this module (`vast_destroy`)"


def test_the_reaper_never_imports_a_lane_module_at_import_time():
    """Same reasoning as the alarm's: a central reaper that dies because one lane's module is broken has the
    failure mode it exists to remove. `gpu_backend` is imported LAZILY inside `vast_destroy` so a plan, a dry
    run and every test run with no key, no network and no boto3."""
    tree = ast.parse((MODALITIES / "vast_account_reaper.py").read_text())
    top = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    names = set()
    for n in top:
        if isinstance(n, ast.Import):
            names |= {a.name for a in n.names}
        elif n.module:
            names.add(n.module)
    banned = {"congeneric_fanout_vast", "nrv04_vast_launch", "ternary_vast_launch", "protfep_vast_launch",
              "gpu_backend", "boto3"}
    assert not (names & banned), f"top-level import of {sorted(names & banned)} — must be lazy or AST-read"
