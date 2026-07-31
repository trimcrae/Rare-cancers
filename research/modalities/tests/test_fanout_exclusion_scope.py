#!/usr/bin/env python3
"""The step 1 fan-out's own exclusion list: what may persist in it, and what may only bound one wave.

★ WHAT THESE PIN, AND THE MEASUREMENT BEHIND EACH. Across the night of 2026-07-27/28 this lane's excluded
count went 41 -> 45 -> 46 -> 47 -> 49 while authorised submits failed 0 / 1 / 2 / 4 / 2 with
`no rentable verified offer` against boards of 152-189 offers at healthy prices. Two independent causes,
both fixed here:

  1. The 10:05 PM ET clear never reached this lane. It was pointed at
     `nr4a3-step1-fanout/results/_lane_state.json`; this lane's list is `_excluded_machines.json` under
     `machine_ids`. Five minutes after a clear that reported 74 entries removed, the tick filtered 41.
  2. `_record_exclusion` wrote EVERY reason to that permanent list, including the stuck-start condemnation
     whose wording ("create/start race") `vast_machine_blacklist` classifies as perishable and has PROVEN
     wrong three times (53989, 31035, 24573 all ran this lane's container at 94-99 % GPU).

So the rule: a capacity refusal bounds the CURRENT WAVE; only host-scoped evidence persists.
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

import congeneric_fanout_vast as cfv  # noqa: E402
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


class _FakeS3:
    def __init__(self, objs=None):
        self.objs = dict(objs or {})

    def get_object(self, Bucket, Key):
        if Key not in self.objs:
            raise KeyError(Key)
        return {"Body": io.BytesIO(self.objs[Key].encode())}

    def put_object(self, Bucket, Key, Body):
        self.objs[Key] = Body.decode()


def _doc(s3):
    return json.loads(s3.objs.get(cfv._EXCLUDE_KEY, "{}"))


# The exact wording the stuck-start condemnation records, and the one this repo has proven wrong.
CAPACITY_WHY = ("never started: cur_state=stopped with an empty status_msg for 53 min across 2 consecutive "
                "checks (create/start race, not an image pull)")
HOST_WHY = "gpu_util 3% for 2 checks on a plain-RBFE leg (healthy band 70-95%); instance 46095633"


# ============================================================================================================
# A capacity refusal binds one wave and is then forgotten.
# ============================================================================================================
def test_a_capacity_refusal_never_reaches_the_durable_list(monkeypatch):
    monkeypatch.setenv("GITHUB_RUN_ID", "111")
    s3 = _FakeS3()
    assert cfv._record_exclusion(s3, "b", "53989", CAPACITY_WHY, scope="host") is True
    d = _doc(s3)
    assert d["machine_ids"] == [], "a claim about a moment became a permanent entry"
    assert d["capacity_wave"]["machine_ids"] == ["53989"]
    assert d["capacity_wave"]["wave"] == "111"


def test_a_capacity_refusal_is_never_published_cross_lane(monkeypatch):
    """`scope="host"` says WHO the verdict is about; the CLASS says HOW LONG it is true for. Only one of
    those two questions was being asked, so a perishable verdict went into the permanent shared set."""
    monkeypatch.setenv("GITHUB_RUN_ID", "111")
    s3 = _FakeS3()
    cfv._record_exclusion(s3, "b", "53989", CAPACITY_WHY, scope="host")
    assert vmb.load(s3, "b")[0] == []


def test_the_wave_block_binds_the_wave_that_wrote_it(monkeypatch):
    monkeypatch.setenv("GITHUB_RUN_ID", "111")
    s3 = _FakeS3()
    cfv._record_exclusion(s3, "b", "53989", CAPACITY_WHY, scope="host")
    assert "53989" in cfv._load_excluded(s3, "b")[0]


def test_the_wave_block_does_NOT_bind_the_next_wave(monkeypatch):
    """This is the whole fix: 'excluded for the rest of this tick', not 'excluded for ever'."""
    monkeypatch.setenv("GITHUB_RUN_ID", "111")
    s3 = _FakeS3()
    cfv._record_exclusion(s3, "b", "53989", CAPACITY_WHY, scope="host")
    monkeypatch.setenv("GITHUB_RUN_ID", "222")
    assert cfv._load_excluded(s3, "b")[0] == []


def test_no_wave_id_means_the_capacity_block_is_not_recorded_at_all(monkeypatch):
    """Off CI there is no wave to bind to. Under-excluding costs one FREE failed submit; over-excluding
    costs capacity that compounds across lanes and nights, so the safe direction is to drop it."""
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("FANOUT_WAVE_ID", raising=False)
    s3 = _FakeS3()
    assert cfv._record_exclusion(s3, "b", "53989", CAPACITY_WHY, scope="host") is False
    assert _doc(s3) == {}


def test_a_real_host_verdict_still_persists(monkeypatch):
    monkeypatch.setenv("GITHUB_RUN_ID", "111")
    s3 = _FakeS3()
    assert cfv._record_exclusion(s3, "b", "77", HOST_WHY, scope="lane") is True
    assert _doc(s3)["machine_ids"] == ["77"]
    assert cfv._load_excluded(s3, "b")[0] == ["77"]


def test_a_real_host_verdict_at_host_scope_still_shares(monkeypatch):
    monkeypatch.setenv("GITHUB_RUN_ID", "111")
    s3 = _FakeS3()
    cfv._record_exclusion(s3, "b", "77", "container never started, image incompatible", scope="host")
    assert vmb.load(s3, "b")[0] == ["77"]


# ============================================================================================================
# Retiring what the old rule already wrote — a fix that left 49 stale entries in place would ship a correct
# rule and an unchanged outcome.
# ============================================================================================================
def _legacy_doc(pairs, extra_ids=()):
    return json.dumps({"machine_ids": sorted({m for m, _ in pairs} | set(extra_ids)),
                       "history": [{"machine_id": m, "why": w, "utc": "2026-07-27T20:00:00Z"}
                                   for m, w in pairs]})


def test_classify_durable_entries_reads_each_entrys_OWN_reason():
    doc = json.loads(_legacy_doc([("53989", CAPACITY_WHY), ("77", HOST_WHY)], extra_ids=["999"]))
    split = cfv.classify_durable_entries(doc)
    assert split == {"host": ["77"], "capacity": ["53989"], "unjustified": ["999"]}


def test_retire_takes_the_perishable_entries_off_the_durable_list():
    s3 = _FakeS3({cfv._EXCLUDE_KEY: _legacy_doc([("53989", CAPACITY_WHY), ("31035", CAPACITY_WHY),
                                                 ("77", HOST_WHY)], extra_ids=["999"])})
    retired = cfv.retire_perishable_exclusions(s3, "b")
    assert retired == ["31035", "53989", "999"]
    assert _doc(s3)["machine_ids"] == ["77"], "the host-scoped entry must survive"


def test_retire_is_idempotent():
    s3 = _FakeS3({cfv._EXCLUDE_KEY: _legacy_doc([("53989", CAPACITY_WHY), ("77", HOST_WHY)])})
    assert cfv.retire_perishable_exclusions(s3, "b") == ["53989"]
    assert cfv.retire_perishable_exclusions(s3, "b") == []


def test_retire_records_WHY_each_id_went():
    """Never delete state you have not first written down — the history keeps the audit trail."""
    s3 = _FakeS3({cfv._EXCLUDE_KEY: _legacy_doc([("53989", CAPACITY_WHY)], extra_ids=["999"])})
    cfv.retire_perishable_exclusions(s3, "b")
    last = _doc(s3)["history"][-1]
    assert last["action"] == "retire_perishable"
    assert last["retired_capacity"] == ["53989"] and last["retired_unjustified"] == ["999"]


def test_the_launcher_self_heals_before_it_reads_the_list():
    """A repair that needs an operator to remember to run it is not a repair."""
    import ast
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "congeneric_fanout_vast.py")).read()
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "mode_launch")
    names = [n.func.id for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    assert "retire_perishable_exclusions" in names


# ============================================================================================================
# "We could not buy" and "we would not buy" are opposite facts and must not print the same.
# ============================================================================================================
def test_a_starved_board_is_named_as_exclusions_not_price():
    doc = cfv.annotate_exclusions({"board_depth": {"offers_returned": 158, "qualifying": 0}},
                                  excluded=[str(i) for i in range(49)])
    assert doc["hold_cause"] == cfv.HOLD_CAUSE_EXCLUSIONS
    assert doc["n_excluded_machines"] == 49
    assert "NOT A PRICE HOLD" in doc["hold_cause_why"]


def test_the_step1_cause_string_is_the_SAME_one_the_relaunch_gate_uses():
    """Two lanes answering the same question must answer it with the same word, or a reader (and
    `lane_staleness_watch`, which greps for it) sees two unrelated problems."""
    import relaunch_market_gate as rmg
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "relaunch_market_gate.py")).read()
    assert f'"{cfv.HOLD_CAUSE_EXCLUSIONS}"' in src
    assert rmg is not None


def test_a_healthy_board_is_NOT_blamed_on_the_exclusions():
    doc = cfv.annotate_exclusions({"board_depth": {"offers_returned": 158, "qualifying": 148}},
                                  excluded=["1", "2"])
    assert "hold_cause" not in doc


def test_the_excluded_count_is_recorded_even_on_a_healthy_tick():
    """Surfacing it only on failure is how it reached 49 unnoticed. It is in the committed snapshot every
    pass, so a reader watches it grow instead of discovering it."""
    doc = cfv.annotate_exclusions({"board_depth": {"offers_returned": 158, "qualifying": 148}},
                                  excluded=["1", "2"], n_wave_held=9)
    assert doc["n_excluded_machines"] == 2 and doc["excluded_machine_ids"] == ["1", "2"]
    assert doc["n_wave_held_machines"] == 9


def test_hosts_we_already_hold_are_not_counted_as_exclusions():
    """Conflating "we will not rent this machine" with "we are already ON this machine" makes a healthy
    19-wide fan-out read as an over-grown blacklist."""
    doc = cfv.annotate_exclusions({}, excluded=["1"], n_wave_held=9)
    assert doc["n_excluded_machines"] == 1 and doc["n_wave_held_machines"] == 9


def test_exclusions_hold_is_a_named_placement_decision():
    assert "exclusions_hold" in cfv.PLACEMENT_DECISIONS


# ============================================================================================================
# ★★ IS THE MACHINE EVEN THE RIGHT UNIT OF BLAME? (2026-07-29)
#
# Measured by joining this lane's live exclusion list to the committed per-tick census: 15 durable machine
# exclusions were produced by 10 distinct UNITS, and three units account for 8 of them — s1f-13 condemned 3
# machines, s1f-03 condemned 3, s1f-04 condemned 2, every one on the identical `gpu_util 0.0%` wording. The
# ternary lane hit the same shape far more expensively: two units re-rented across 35 and 49 separate hosts.
# A per-unit fault blaming a per-machine blacklist costs one good host per attempt.
# ============================================================================================================
STARVED_WHY = "gpu_util 0.0% for 2 checks on a plain-RBFE leg (healthy band 70-95%); instance {}"


def _condemn(s3, unit, machines):
    for i, m in enumerate(machines):
        cfv._record_exclusion(s3, "b", m, STARVED_WHY.format(46000000 + i), unit=unit)


def test_a_unit_may_condemn_hosts_below_the_threshold():
    """One or two is still a story about hosts — a single unlucky machine can produce two."""
    s3 = _FakeS3()
    _condemn(s3, "s1f-13-cw_ms_free_acid", ["1", "2"])
    assert _doc(s3)["machine_ids"] == ["1", "2"]


def test_a_unit_that_has_condemned_N_hosts_stops_being_evidence_about_hosts():
    s3 = _FakeS3()
    _condemn(s3, "s1f-13-cw_ms_free_acid", ["1", "2", "3"])
    assert _doc(s3)["machine_ids"] == ["1", "2", "3"]
    # the fourth is refused: the common factor is the unit
    assert cfv._record_exclusion(s3, "b", "4", STARVED_WHY.format(9), unit="s1f-13-cw_ms_free_acid") is False
    assert "4" not in _doc(s3)["machine_ids"]


def test_the_guard_is_PER_UNIT_and_does_not_gag_a_different_unit():
    """A real bad host must still be recordable by whoever lands on it next."""
    s3 = _FakeS3()
    _condemn(s3, "s1f-13-cw_ms_free_acid", ["1", "2", "3"])
    assert cfv._record_exclusion(s3, "b", "4", STARVED_WHY.format(9), unit="s1f-03-cw_ev_5alkyne") is True
    assert "4" in _doc(s3)["machine_ids"]


def test_the_threshold_has_ONE_home_shared_with_the_spend_breaker():
    """"How many distinct hosts before the unit is the suspect" is one question. `leg_failure_breaker` stops
    buying the next host; this stops blaming the next machine. Two answers would be a rule 1 violation."""
    import ast
    import leg_failure_breaker as lfb
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "congeneric_fanout_vast.py")).read()
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "_record_exclusion")
    attrs = {n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute)}
    assert "DEFAULT_THRESHOLD" in attrs, "the threshold must be imported, never re-typed"
    assert lfb.DEFAULT_THRESHOLD == 3


def test_wave_scoped_rows_do_not_count_toward_a_units_condemnations():
    """A capacity refusal is not a verdict the unit authored about a host, so it must not push a unit over
    the line and gag its genuine host findings."""
    doc = {"history": [{"machine_id": str(m), "unit": "u", "scope": "wave"} for m in range(9)]}
    assert cfv.unit_condemnations(doc, "u") == set()


def test_the_unit_is_recorded_on_every_durable_row(monkeypatch):
    """Until now the history said WHICH machine and WHY but never WHO, so the question could only be
    answered by joining the committed census. It is answerable from the artifact now."""
    s3 = _FakeS3()
    cfv._record_exclusion(s3, "b", "77", STARVED_WHY.format(1), unit="s1f-13-cw_ms_free_acid")
    assert _doc(s3)["history"][-1]["unit"] == "s1f-13-cw_ms_free_acid"


def test_the_call_sites_actually_pass_the_unit():
    """A guard that is never given the evidence is a guard that never fires."""
    import ast
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "congeneric_fanout_vast.py")).read()
    calls = [n for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "_record_exclusion"]
    assert calls, "no call sites found"
    for c in calls:
        assert any(k.arg == "unit" for k in c.keywords), ast.dump(c)[:200]
