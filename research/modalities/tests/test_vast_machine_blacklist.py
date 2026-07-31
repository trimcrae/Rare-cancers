#!/usr/bin/env python3
"""The shared Vast machine-exclusion set: what may go in it, and how it is emptied.

A wrong permanent entry is an unrecoverable capacity loss that compounds across lanes, while re-discovering
a genuinely bad host is nearly free — a failed SUBMIT costs no rental and no billing. These tests pin that
asymmetry into the module.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

import vast_machine_blacklist as vmb  # noqa: E402


# ⛔⛔ THESE TESTS PIN THE **RETIRED** DURABLE EXCLUSION LIST, DELIBERATELY (2026-07-31).
# trimcrae retired it that day — *"You've gotta just stop doing the blacklist. It seems like it only ever
# bites us in the ass and clearing it always makes things better."* — and `vast_machine_blacklist` now reads
# and writes NOTHING unless `VAST_DURABLE_EXCLUSIONS=1`. The machinery below (capacity-vs-host classification,
# wave scoping, the per-unit condemnation guard, clear/snapshot/retire) is kept and kept TESTED rather than
# deleted, because the retirement is a switch and a switch that flips back into untested code is a trap. The
# behaviour that is now live by default is pinned separately, in `test_blacklist_retired.py`.
@pytest.fixture(autouse=True)
def _durable_exclusions_on(monkeypatch):
    monkeypatch.setenv("VAST_DURABLE_EXCLUSIONS", "1")



# ============================================================================================================
# "Clear it out, and don't add anything back unless you have a real reason" (trimcrae, 2026-07-27).
#
# The set had grown to 48 permanent entries and blocked 2 of 2 authorised placements against a 189-offer
# board where price was fine. The cause was storing a MOMENT as if it were a property of the host.
# ============================================================================================================
def test_a_capacity_refusal_is_classified_as_perishable():
    for why in ("resources_unavailable on start (instance 46056372, RTX 5090)",
                "machine has no free GPU",
                "CAPACITY refusal"):
        assert vmb.classify_reason(why) == vmb.CLASS_CAPACITY, why


def test_a_container_failure_is_classified_as_durable():
    for why in ("container never started", "image pull failed", "crash-loop on start",
                "CUDA_ERROR_UNSUPPORTED_PTX_VERSION"):
        assert vmb.classify_reason(why) == vmb.CLASS_HOST, why


def test_capacity_is_checked_before_the_never_started_markers():
    # `resources_unavailable` matches NEVER_STARTED_MARKERS too. If that were checked first, the perishable
    # class would be filed as durable — which is exactly how the set grew.
    why = "resources_unavailable on start"
    assert vmb.is_never_started_reason(why) is True      # still true, and still used by withdraw()
    assert vmb.classify_reason(why) == vmb.CLASS_CAPACITY


class _FakeS3:
    def __init__(self, objs=None):
        self.objs = dict(objs or {})

    def get_object(self, Bucket, Key):
        if Key not in self.objs:
            raise KeyError(Key)
        return {"Body": io.BytesIO(self.objs[Key].encode())}

    def put_object(self, Bucket, Key, Body):
        self.objs[Key] = Body.decode()


def test_publish_REFUSES_a_capacity_reason():
    s3 = _FakeS3()
    assert vmb.publish(s3, "b", "12345", "resources_unavailable on start", "ternary") is False
    ids, _ = vmb.load(s3, "b")
    assert ids == []


def test_publish_still_accepts_a_real_host_reason():
    s3 = _FakeS3()
    assert vmb.publish(s3, "b", "12345", "container never started", "ternary") is True
    ids, doc = vmb.load(s3, "b")
    assert ids == ["12345"]
    assert doc["history"][-1]["reason_class"] == vmb.CLASS_HOST


def test_clear_all_empties_the_set_but_keeps_the_history():
    s3 = _FakeS3()
    vmb.publish(s3, "b", "1", "container never started", "ternary")
    vmb.publish(s3, "b", "2", "crash-loop on start", "step1")
    removed = vmb.clear_all(s3, "b", "trimcrae 2026-07-27: too strict, blocking placements")
    assert sorted(removed) == ["1", "2"]
    ids, doc = vmb.load(s3, "b")
    assert ids == []
    # The clear is an EVENT in the record, not a gap.
    assert doc["history"][-1]["reason_class"] == "clear"
    assert sorted(doc["history"][-1]["cleared_machine_ids"]) == ["1", "2"]


def test_snapshot_captures_everything_needed_to_reconstruct():
    s3 = _FakeS3()
    vmb.publish(s3, "b", "1", "container never started", "ternary")
    snap = vmb.snapshot(s3, "b")
    assert snap["n_machine_ids"] == 1 and snap["machine_ids"] == ["1"]
    assert snap["history"] and snap["history_entries_by_reason_class"]


def test_clearing_only_the_shared_set_is_not_enough():
    # blocked_machine_ids() unions lane-local with shared, so a lane keeps excluding until its own list goes.
    s3 = _FakeS3({"pfx/_lane_state.json": json.dumps({"_blocked_machines": ["7", "8"]})})
    removed = vmb.clear_lane_state(s3, "b", "pfx/_lane_state.json")
    assert sorted(removed) == ["7", "8"]
    assert json.loads(s3.objs["pfx/_lane_state.json"])["_blocked_machines"] == []


def test_clear_refuses_without_a_snapshot():
    assert vmb.main(["--clear", "because"]) == 2


def test_the_create_start_race_verdict_is_perishable_because_it_has_been_wrong():
    """53989, 31035 and 24573 were condemned on exactly this wording and every one had run our container at
    94-99 % GPU. A verdict that has demonstrably flipped must not create a permanent entry."""
    why = ("never started: cur_state=stopped with an empty status_msg for 53 min across 2 consecutive "
           "checks (create/start race, not an image pull)")
    assert vmb.classify_reason(why) == vmb.CLASS_CAPACITY
    s3 = _FakeS3()
    assert vmb.publish(s3, "b", "53989", why, "step1_fanout") is False


def test_the_cli_actually_reads_its_command_line(monkeypatch, tmp_path):
    """`parse_args([])` ignores every flag. That made --clear a silent no-op that reported success twice."""
    import sys as _sys
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "vast_machine_blacklist.py")).read()
    assert "parse_args([] if argv is None else argv)" not in src
    assert "sys.argv[1:] if argv is None else argv" in src

    # And end to end: with argv=None the parser must see the real process argv.
    out = tmp_path / "snap.json"
    monkeypatch.setattr(_sys, "argv", ["vast_machine_blacklist.py", "--clear", "x"])
    assert vmb.main() == 2          # --clear without --snapshot is refused, proving the flag was parsed


def test_nothing_is_defined_after_the_main_guard():
    """`raise SystemExit(main())` runs at import-as-script time, so a def BELOW it never exists when the
    module is executed — only when it is imported. That is why the unit tests all passed while the real CLI
    died on `NameError: name 'snapshot' is not defined` (2026-07-27). Import-only tests cannot see this.
    """
    import ast
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "vast_machine_blacklist.py")).read()
    tree = ast.parse(src)
    guards = [i for i, n in enumerate(tree.body)
              if isinstance(n, ast.If) and "__main__" in ast.dump(n.test)]
    assert guards, "no __main__ guard found"
    after = [n.name for n in tree.body[guards[-1] + 1:]
             if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
    assert after == [], f"defined after the __main__ guard and therefore invisible to the CLI: {after}"


def test_the_cli_runs_as_a_SCRIPT_not_just_as_an_import(tmp_path):
    """Exercise the real entry point the workflow uses. --clear without --snapshot must exit 2, which proves
    the module got far enough to parse flags rather than dying on a NameError."""
    import subprocess
    mod = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "vast_machine_blacklist.py")
    r = subprocess.run([sys.executable, mod, "--clear", "x"], capture_output=True, text=True)
    assert r.returncode == 2, f"rc={r.returncode} stdout={r.stdout[-400:]} stderr={r.stderr[-400:]}"
    assert "NameError" not in r.stderr


def test_the_lane_local_exclusion_list_is_wave_scoped_not_cumulative():
    """`sorted(prior | blocked)` made the lane's own list grow forever, and it is populated ONLY by the
    resources_unavailable branch — the perishable class. Clearing the shared set without this would have
    regrown the same 40-machine filter within a day."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "ternary_vast_launch.py")).read()
    assert 'new_state["_blocked_machines"] = sorted(prior | blocked)' not in src
    assert 'new_state["_blocked_machines"] = sorted(blocked)' in src


# ============================================================================================================
# ★★ THE LAUNDERING ROUTE (found 2026-07-28). `publish` refuses CLASS_CAPACITY — and `backfill` walked
# around it by synthesising its own reason string, which classified as CLASS_HOST. 32 of the 41 entries in
# the committed pre-clear snapshot are that exact synthetic string. These tests pin the door shut.
# ============================================================================================================
def test_backfill_REFUSES_to_run_without_the_original_reason():
    s3 = _FakeS3()
    try:
        vmb.backfill(s3, "b", ["1", "2"], lane="rung5a_ks")
    except TypeError as e:
        assert "why" in str(e)
    else:
        raise AssertionError("backfill accepted a call with no recorded reason — that is the laundering")


def test_backfill_cannot_promote_a_capacity_refusal():
    """The whole set of ids on a wave-scoped `_blocked_machines` is the perishable class. Handed to backfill
    WITH ITS REAL REASON, publish's classifier sees it and refuses — which is the behaviour that was being
    bypassed."""
    s3 = _FakeS3()
    added = vmb.backfill(s3, "b", ["53989", "31035"], lane="rung5a_ks",
                         why="resources_unavailable on start")
    assert added == []
    assert vmb.load(s3, "b")[0] == []


def test_backfill_still_promotes_a_genuine_host_verdict():
    s3 = _FakeS3()
    added = vmb.backfill(s3, "b", ["1", "2"], lane="rung5a_ks",
                         why={"1": "container never started", "2": "crash-loop on start"})
    assert sorted(added) == ["1", "2"]


def test_the_synthetic_backfill_label_would_have_classified_as_durable():
    """The measurement behind the fix: this is the string backfill used to invent, and it is why the guard
    never fired. Kept as a test so nobody re-introduces a label like it."""
    assert vmb.classify_reason("backfilled from rung5a_ks's refuse-to-start list") == vmb.CLASS_HOST


def test_the_ternary_lane_no_longer_backfills_on_every_read():
    """AST, not a substring: the comment block that explains the removal necessarily QUOTES the old call,
    and a grep-based test would fail on the explanation rather than on the code."""
    import ast
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "ternary_vast_launch.py")).read()
    calls = [n for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "backfill"]
    assert calls == [], "the per-read backfill is the regrowth route; it must stay removed"


# ============================================================================================================
# The clear that reported success against a key the fan-out has never written.
# ============================================================================================================
def test_clear_lane_state_handles_the_fanouts_machine_ids_shape():
    s3 = _FakeS3({"nr4a3-step1-fanout/results/_excluded_machines.json":
                  json.dumps({"machine_ids": ["8914", "68109"], "history": []})})
    removed = vmb.clear_lane_state(s3, "b", "nr4a3-step1-fanout/results/_excluded_machines.json")
    assert sorted(removed) == ["68109", "8914"]
    assert json.loads(s3.objs["nr4a3-step1-fanout/results/_excluded_machines.json"])["machine_ids"] == []


def test_a_missing_lane_key_is_reported_as_missing_not_as_clean(capsys):
    """"nothing to clear" and "you are pointed at the wrong file" must not print the same. On 2026-07-27 the
    second printed as the first and 41 machines survived a clear that reported 74 entries removed."""
    s3 = _FakeS3()
    assert vmb.clear_lane_state(s3, "b", "nr4a3-step1-fanout/results/_lane_state.json") == []
    out = capsys.readouterr().out
    assert "NO SUCH DOCUMENT" in out and "wrong one" in out


def test_the_clear_workflow_points_at_the_fanouts_REAL_key():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    wf = open(os.path.join(root, ".github", "workflows", "gpu-ternary-fep-vast.yml")).read()
    assert '--lane-state "nr4a3-step1-fanout/results/_excluded_machines.json"' in wf
    # the flag form only — the comment above it names the wrong key on purpose, as the record of the miss
    assert '--lane-state "nr4a3-step1-fanout/results/_lane_state.json"' not in wf


# ============================================================================================================
# A snapshot is a record, not a buffer.
# ============================================================================================================
def test_snapshot_refuses_to_overwrite_an_existing_record(tmp_path, monkeypatch):
    p = tmp_path / "vast-blacklist-snapshot-before-clear.json"
    p.write_text('{"n_machine_ids": 41}')
    import sys as _sys
    monkeypatch.setattr(_sys, "argv", ["vast_machine_blacklist.py", "--snapshot", str(p)])
    assert vmb.main() == 2
    assert json.loads(p.read_text())["n_machine_ids"] == 41, "the pre-clear record was clobbered"


def test_the_committed_pre_clear_record_is_still_intact():
    """The irreplaceable artifact this whole guard exists for: 41 machines, {'host': 9, 'capacity': 32}."""
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "vast-blacklist-snapshot-before-clear.json")
    doc = json.load(open(p))
    assert doc["n_machine_ids"] == 41
    assert doc["history_entries_by_reason_class"] == {"host": 9, "capacity": 32}


# ============================================================================================================
# ★ THE ENTRIES THE GUARD WAS ADDED TOO LATE FOR. Measured live 7:16 AM ET 2026-07-28, hours after the set
# was cleared to zero: the shared set held four machines and its own history classes three of them as
# capacity refusals — one of them written NINETY SECONDS earlier by the backfill, from the ternary lane's
# wave-scoped list. Closing the door does not empty the room.
# ============================================================================================================
def test_retire_perishable_removes_a_capacity_entry_the_guard_would_refuse_today():
    s3 = _FakeS3()
    vmb.publish(s3, "b", "28908", "container never started: 163 min from rental", "step1_fanout")
    # written the way a pre-guard build (or backfill's synthetic label) got them in
    ids, doc = vmb.load(s3, "b")
    doc["machine_ids"] = sorted(set(ids) | {"46427", "8914"})
    doc["history"] += [
        {"machine_id": "46427", "why": "never started: cur_state=stopped with an empty status_msg for 94 "
                                       "min across 2 consecutive checks (create/start race, not an image "
                                       "pull)", "lane": "step1_fanout"},
        {"machine_id": "8914", "why": "resources_unavailable on start (instance 46089664)",
         "lane": "rung5a_ks"}]
    s3.objs[vmb.SHARED_KEY] = json.dumps(doc)

    assert sorted(vmb.retire_perishable(s3, "b")) == ["46427", "8914"]
    assert vmb.load(s3, "b")[0] == ["28908"], "the genuine host verdict must survive"


def test_retire_perishable_is_idempotent():
    s3 = _FakeS3()
    vmb.publish(s3, "b", "1", "container never started", "ternary")
    assert vmb.retire_perishable(s3, "b") == []


def test_retire_perishable_records_what_it_removed():
    s3 = _FakeS3({vmb.SHARED_KEY: json.dumps({
        "machine_ids": ["8914"],
        "history": [{"machine_id": "8914", "why": "resources_unavailable on start", "lane": "rung5a_ks"}]})})
    vmb.retire_perishable(s3, "b")
    last = json.loads(s3.objs[vmb.SHARED_KEY])["history"][-1]
    assert last["action"] == "retire_perishable" and last["retired_machine_ids"] == ["8914"]


def test_retire_perishable_leaves_an_entry_it_cannot_read_a_reason_for():
    """Unlike this lane's own list, the shared set's history is complete by construction — publish always
    writes it — so a shared entry with no reason is a surprise, not a legacy. Leave it and let a human look;
    the cross-lane set is the one where being wrong is most expensive in both directions."""
    s3 = _FakeS3({vmb.SHARED_KEY: json.dumps({"machine_ids": ["999"], "history": []})})
    assert vmb.retire_perishable(s3, "b") == []


def test_project_retire_is_read_only_and_reports_the_union():
    """The verification path that costs $0: the retire lives in a LAUNCH tick, and a launch tick rents GPUs.
    This computes the same answer from the same classification with zero writes."""
    s3 = _FakeS3({
        vmb.SHARED_KEY: json.dumps({
            "machine_ids": ["8914", "28908"],
            "history": [{"machine_id": "8914", "why": "resources_unavailable on start"},
                        {"machine_id": "28908", "why": "container never started: 163 min from rental"}]}),
        "lane/_excluded_machines.json": json.dumps({
            "machine_ids": ["8914", "77", "999"],
            "history": [{"machine_id": "8914", "why": "resources_unavailable on start"},
                        {"machine_id": "77", "why": "gpu_util 0.0% for 2 checks on a plain-RBFE leg"}]}),
    })
    before = json.dumps(s3.objs, sort_keys=True)
    proj = vmb.project_retire(s3, "b", ["lane/_excluded_machines.json"])
    assert json.dumps(s3.objs, sort_keys=True) == before, "a dry run must not write"
    # union today = {8914, 28908, 77, 999}; after = {28908, 77}
    assert proj["_total_union"] == {"before": 4, "after": 2, "_what": proj["_total_union"]["_what"]}
    assert proj["lane/_excluded_machines.json"]["would_retire"] == ["8914", "999"]
    assert proj[vmb.SHARED_KEY]["would_retire"] == ["8914"]


def test_project_retire_keeps_an_unjustified_entry_in_the_SHARED_set():
    """Asymmetric on purpose, and it matches the live code: a lane's own list sheds reasonless entries, the
    cross-lane set does not, because publish() always writes history so a gap there is a surprise."""
    s3 = _FakeS3({vmb.SHARED_KEY: json.dumps({"machine_ids": ["999"], "history": []})})
    assert vmb.project_retire(s3, "b")[vmb.SHARED_KEY]["would_retire"] == []
