#!/usr/bin/env python3
"""Tests for the GENERIC Vast watchdog — the kind registry, and the properties that stop it lying.

The design constraint that outranks every feature here is: AN ENTRY MUST BE UNABLE TO CLAIM COVERAGE IT DOES
NOT HAVE. This repo's most expensive defect class is monitoring that watches nothing — a GCP watchdog sat
unparseable for days so its cron never fired; a gating diagnostic returned success while measuring nothing,
seven separate ways; a collector read keys the driver never wrote and would have returned a confident
"inconclusive" on 24 perfect legs. So the tests that matter most are the REFUSALS, not the happy paths.

The second thing under test is that generalising did not disturb the ternary lane. Its four entries are
watching billed legs, so "byte-identical interpretation" is a property, not a hope.
"""
import copy
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(MOD))
sys.path.insert(0, MOD)

import ternary_vast_watchdog as tvwd  # noqa: E402
import vast_watchdog as vw  # noqa: E402
import watchdog_policy as wp  # noqa: E402
import watchdog_validate as wdv  # noqa: E402

GENERIC_LIST = os.path.join(MOD, "vast-watch.json")
TERNARY_LIST = os.path.join(MOD, "ternary-vast-watch.json")
LANE13_TASK = os.path.join(MOD, "nr4a-paralogue-md-task.json")


def _generic():
    with open(GENERIC_LIST) as fh:
        return json.load(fh)


def _ternary():
    with open(TERNARY_LIST) as fh:
        return json.load(fh)


# ================================================================= ONE POLICY, NOT TWO
def test_the_ternary_watchdog_and_the_generic_engine_share_one_policy_object():
    """Not "the same logic" — the SAME OBJECT. Two monitors that can disagree about whether a leg is dead is
    strictly worse than one, and a copy is exactly how they come to disagree."""
    assert tvwd.classify is wp.classify
    assert vw.classify is wp.classify
    assert tvwd.should_relaunch is wp.should_relaunch is vw.should_relaunch


def test_the_ternary_lanes_grace_and_stall_constants_are_unchanged_by_the_move():
    assert tvwd.SETUP_GRACE_MIN == 90.0
    assert tvwd.STALL_TICKS == 2


# ================================================================= THE REFUSALS
def test_an_unimplemented_kind_is_refused_not_silently_watched():
    """The whole design constraint in one test. A watch list may name a kind; if the running code does not
    implement it, the pass must ABORT with a loud reason rather than skip the entry while the list still
    claims coverage."""
    doc = {
        "_required_run_params_by_kind": {"bioemu": ["unit_id", "kind", "enabled"]},
        "watch": [{"kind": "bioemu", "unit_id": "bioemu-1", "enabled": True}],
    }
    problems = wdv.validate(doc, known_kinds=set(vw.KINDS))
    assert len(problems) == 1
    assert "NOT IMPLEMENTED" in problems[0][2][0]
    # ...and with no registry supplied the standalone validator must not invent an opinion
    assert wdv.validate(doc, known_kinds=None) == []


def test_a_multi_kind_entry_with_no_kind_at_all_is_refused():
    doc = {"_required_run_params_by_kind": {"ternary": ["unit_id"]},
           "watch": [{"unit_id": "x", "enabled": True}]}
    problems = wdv.validate(doc, known_kinds=set(vw.KINDS))
    assert len(problems) == 1 and "kind" in problems[0][2][0]


def test_a_kind_the_engine_implements_but_the_doc_does_not_declare_is_refused():
    """The doc's map and the code's registry must AGREE. A kind implemented but undeclared has no required-key
    list, so nothing would check that its relaunch parameters are present."""
    doc = {"_required_run_params_by_kind": {"ternary": ["unit_id"]},
           "watch": [{"kind": "paralogue_md", "unit_id": "nr4a-pdyn-nr4a1", "enabled": True}]}
    problems = wdv.validate(doc, known_kinds=set(vw.KINDS))
    assert len(problems) == 1 and "not declared" in problems[0][2][0]


def test_an_entry_missing_a_relaunch_parameter_aborts_the_pass():
    # Force the row enabled in the throwaway copy: validate() deliberately skips DISABLED entries, so once a
    # lane completes and its units are disabled this test would assert against an empty problem list and fail
    # for a reason that has nothing to do with what it checks. The required-key contract is a property of the
    # SCHEMA, not of which legs are running. (Same coupling bit the ternary list earlier the same day.)
    doc = _generic()
    doc["watch"][0]["enabled"] = True
    del doc["watch"][0]["metad_ns"]
    problems = wdv.validate(doc, known_kinds=set(vw.KINDS))
    assert problems and "metad_ns" in problems[0][2]


def test_a_smoke_leg_is_refused_because_a_phantom_entry_killed_lane13s_watch():
    """THE INCIDENT THIS ENCODES, with its own log line as the citation.

    2026-07-26T00:28:55Z (8:28 PM ET) LANE 13's long-running watch died with

        ##[error]['nr4a-pdyn-nr4a2-smoke'] made no progress for 8 ticks (24 min) — diagnose, do not relaunch

    while BOTH real legs were demonstrably advancing at 60-69 % GPU utilisation (NR4A1 4.55 -> 4.75 ns,
    NR4A2 3.05 -> 3.25 ns across the same two ticks). The cause is that `leg_names()` synthesises a `-smoke`
    name per target whether or not a smoke leg was ever launched, and a leg that does not exist has a
    progress signature — (None, None, False) — that can never change. A phantom took the monitoring down and
    left two billed legs unwatched. This engine refuses to watch a smoke leg at all rather than inherit it."""
    e = vw.paralogue_entry("NR4A2", git_branch="b")
    e["run_mode"] = "smoke"
    bad = vw.ParalogueMdKind.preflight(e)
    assert bad and "smoke" in bad[0]


def test_a_unit_id_that_is_not_a_real_leg_name_is_refused():
    e = vw.paralogue_entry("NR4A1", git_branch="b")
    e["unit_id"] = "something-else"
    assert vw.ParalogueMdKind.preflight(e)


# ================================================================= THE TERNARY LANE IS UNDISTURBED
def test_the_live_ternary_watch_list_still_validates_exactly_as_before():
    doc = _ternary()
    assert wdv.validate(doc) == []
    # and the new registry argument must not change the verdict on a legacy list
    assert wdv.validate(doc, known_kinds=set(vw.KINDS)) == []


def test_the_ternary_list_is_still_read_by_the_LEGACY_path():
    """A schema migration that silently reinterpreted a live entry would be the worst outcome here. The switch
    into strict multi-kind mode is the PRESENCE of `_required_run_params_by_kind`, and the ternary list does
    not have it — so its entries need no `kind`, and its failure messages keep their (leg_id, direction)
    shape."""
    doc = _ternary()
    assert "_required_run_params_by_kind" not in doc
    assert all("kind" not in e for e in doc["watch"])
    broken = copy.deepcopy(doc)
    # This test is about the legacy (leg_id, direction) failure SHAPE, so it must not depend on which units
    # happen to be running. It first hard-coded watch[0] (broke when the probe completed), then picked the
    # first ENABLED row (broke on 2026-07-26 when the ternary edge landed and the whole lane went disabled,
    # leaving StopIteration). validate() deliberately skips disabled entries, so the fix is to FORCE the row
    # enabled in the throwaway copy rather than to hunt for a live one — the shape is a property of the schema,
    # not of the lane's operational state.
    live = 0
    broken["watch"][live]["enabled"] = True
    del broken["watch"][live]["timestep_fs"]
    problems = wdv.validate(broken, known_kinds=set(vw.KINDS))
    assert problems == [(doc["watch"][live]["leg_id"], doc["watch"][live]["direction"], ["timestep_fs"])]


def test_the_four_live_ternary_entries_are_byte_identical_to_what_shipped():
    """These four units belong to the ternary lane, not to this generalisation, so their exact identities are
    pinned here — a rename or a dropped row should fail loudly.

    `enabled` is deliberately NOT pinned. It is live operational state: a unit is disabled when its leg COMPLETES,
    and the list keeps the row so the finished unit stays on the record. The probe (ΔG_morph 48.1970) and the
    solvent leg (ΔG_morph 47.7982) both landed on 2026-07-26 and were correctly set enabled:false, which turned
    `all(enabled)` into an assertion that the lane must never finish anything. Pinning identities is the real
    invariant; pinning progress makes the suite go red on success."""
    ids = [e["unit_id"] for e in _ternary()["watch"]]
    assert ids == [
        "calib_hi_to_lo__ternary_vhl_r0_dt4.0fs_wu1.0_probe",
        "calib_hi_to_lo__ternary_vhl_r0_dt4.0fs_wu1.0_edge",
        "calib_hi_to_lo__binary_vhl_r0_dt4.0fs_wu1.0_edge",
        "calib_hi_to_lo__solvent_r0_dt4.0fs_wu1.0_edge",
    ]
    # every row still carries the flag (present and boolean) — its VALUE is operational
    assert all(isinstance(e.get("enabled"), bool) for e in _ternary()["watch"])


def test_the_two_watch_lists_are_disjoint():
    """Two relaunchers for one unit is the hazard, not the fix: both would see the same hostless leg and both
    would re-rent it, giving two hosts writing one S3 restart set."""
    a = {e["unit_id"] for e in _generic()["watch"]}
    b = {e["unit_id"] for e in _ternary()["watch"]}
    assert not (a & b), f"a unit is in BOTH watch lists and would be relaunched twice: {sorted(a & b)}"


# ================================================================= THE SCALAR — "alive is not advancing"
def test_the_metad_to_release_reset_never_reads_as_a_regression():
    """THE trap this kind exists to survive. `done_ns` counts biased ns during metadynamics and then STARTS
    AGAIN FROM ZERO for the unbiased release replicas, so the raw counter drops from 60 to 0 at a perfectly
    healthy phase transition. A watchdog scoring done_ns directly would call that no-advance twice and
    stall-alert a good leg."""
    end_of_metad = vw.ParalogueMdKind.score({"phase": "metad", "extra": {"done_ns": 60.0}})[0]
    start_of_release = vw.ParalogueMdKind.score({"phase": "release", "extra": {"done_ns": 0.0}})[0]
    assert start_of_release > end_of_metad
    # and every phase in the job's real order is strictly increasing
    order = ["resume_download", "metad", "release", "package", "done"]
    scalars = [vw.ParalogueMdKind.score({"phase": p, "extra": {"done_ns": 0.0}})[0] for p in order]
    assert scalars == sorted(scalars) and len(set(scalars)) == len(scalars)


def test_ns_within_a_phase_advances_the_scalar():
    a = vw.ParalogueMdKind.score({"phase": "metad", "extra": {"done_ns": 4.55}})[0]
    b = vw.ParalogueMdKind.score({"phase": "metad", "extra": {"done_ns": 4.75}})[0]
    assert b > a, "the observed 4.55 -> 4.75 ns advance must register; 0.2 ns is one heartbeat of real MD"


def test_a_frozen_scalar_is_a_stall_not_running_even_with_a_live_instance():
    """The Vast-specific correction, re-asserted through the generic engine: a rented box can sit up with a
    dead container or an idle GPU and look perfectly healthy."""
    s = vw.ParalogueMdKind.score({"phase": "metad", "extra": {"done_ns": 4.75}})[0]
    v, stall = vw.classify(has_result=False, instance_alive=True, instance_age_min=120,
                           progress_scalar=s, prev_scalar=s, prev_stall=0,
                           stall_ticks=vw.ParalogueMdKind.stall_ticks)
    assert (v, stall) == ("RUNNING", 1)
    v, stall = vw.classify(has_result=False, instance_alive=True, instance_age_min=120,
                           progress_scalar=s, prev_scalar=s, prev_stall=1,
                           stall_ticks=vw.ParalogueMdKind.stall_ticks)
    assert v == "STALLED"


def test_an_unranked_phase_is_refused_rather_than_scored_zero():
    """If the job gains a phase and PHASE_RANK is not updated, the honest answer is "I cannot score this",
    not 0 — which would collapse below every ranked phase and manufacture a SETUP_STALL."""
    scalar, _label, readable, failed, note = vw.ParalogueMdKind.score({"phase": "tica", "extra": {}})
    assert readable is False and failed is False and "does not rank" in note


def test_an_unparseable_done_ns_is_unreadable_not_zero():
    _s, _l, readable, _f, note = vw.ParalogueMdKind.score({"phase": "metad", "extra": {"done_ns": "soon"}})
    assert readable is False and "unparseable" in note


def test_no_marker_yet_is_zero_progress_inside_the_grace_window_not_unreadable():
    """A host pulling a multi-GB image has written nothing yet. That IS zero progress and must sit inside the
    cold-start grace; calling it unreadable would skip the entry and never notice a hung pull."""
    scalar, _l, readable, _f, _n = vw.ParalogueMdKind.score(None)
    assert (scalar, readable) == (0, True)
    assert vw.classify(has_result=False, instance_alive=True, instance_age_min=30, progress_scalar=0,
                       prev_scalar=0, prev_stall=0,
                       setup_grace_min=vw.ParalogueMdKind.setup_grace_min)[0] == "RUNNING"
    assert vw.classify(has_result=False, instance_alive=True, instance_age_min=200, progress_scalar=0,
                       prev_scalar=0, prev_stall=0,
                       setup_grace_min=vw.ParalogueMdKind.setup_grace_min)[0] == "SETUP_STALL"


def test_a_recorded_crash_is_not_a_preemption_and_must_not_relaunch():
    """The job marks metad_failed / release_failed / metad_stalled before returning non-zero. A leg that RAN
    and recorded a reason will fail the same way, and uncapped that buys a full-length rental per attempt.
    A preempted host writes NO record, which is why it correctly reads DIED and resumes."""
    for phase in vw.ParalogueMdKind.FAILED_PHASES:
        _s, _l, readable, failed, _n = vw.ParalogueMdKind.score({"phase": phase, "extra": {"rc": 3}})
        assert readable and failed, phase
        v, _ = vw.classify(has_result=False, has_failed_record=True, instance_alive=False,
                           instance_age_min=0, progress_scalar=0, prev_scalar=0, prev_stall=0)
        assert v == "FAILED"
        assert vw.should_relaunch(v, 0, 6)[0] is False


def test_a_stale_crash_record_does_not_stop_a_live_attempt():
    v, _ = vw.classify(has_result=False, has_failed_record=True, instance_alive=True, instance_age_min=5,
                       progress_scalar=1_004_750, prev_scalar=1_004_000, prev_stall=0)
    assert v == "RUNNING"


# ================================================================= LABEL MATCHING
def test_the_smoke_label_never_matches_the_real_leg():
    """`nr4a-pdyn-nr4a1-smoke` startswith `nr4a-pdyn-nr4a1`, so a prefix test would pair the real leg with a
    finished smoke host and report it as alive. The lane already lost a `target_of()` to this overlap."""
    m = vw.ParalogueMdKind.label_matches
    assert m("nr4a-pdyn-nr4a1", "nr4a-pdyn-nr4a1")
    assert not m("nr4a-pdyn-nr4a1-smoke", "nr4a-pdyn-nr4a1")
    assert not m("nr4a-pdyn-nr4a2", "nr4a-pdyn-nr4a1")
    assert not m(None, "nr4a-pdyn-nr4a1")


# ================================================================= THE RELAUNCH INTERLOCK
def test_a_second_relauncher_in_flight_withholds_the_relaunch():
    withhold, why = vw.relaunch_withheld(1, True, "gpu-nr4a-paralogue-md-vast.yml")
    assert withhold and "in flight" in why


def test_an_unanswerable_interlock_question_withholds_fail_safe():
    """Refusing to relaunch a leg that is already dead costs wall-clock. Relaunching next to another
    relauncher costs the run — two hosts writing one restart set is an interleaved trajectory."""
    withhold, why = vw.relaunch_withheld(None, False, "gpu-nr4a-paralogue-md-vast.yml")
    assert withhold and "could not be queried" in why


def test_an_idle_owner_lets_the_relaunch_through():
    withhold, _ = vw.relaunch_withheld(0, True, "gpu-nr4a-paralogue-md-vast.yml")
    assert withhold is False


def test_only_died_relaunches_and_the_cap_holds():
    assert vw.should_relaunch("DIED", 0, 6)[0] is True
    assert vw.should_relaunch("DIED", 6, 6)[0] is False
    assert vw.should_relaunch("STALLED", 0, 6)[0] is False
    assert vw.should_relaunch("SETUP_STALL", 0, 6)[0] is False
    assert vw.should_relaunch("DIED", "?", 6)[0] is False, "an unparseable counter must refuse, not guess"


# ================================================================= THE SHIPPED LIST IS NOT HAND-TYPED DRIFT
def test_the_shipped_entries_are_exactly_what_the_builder_produces():
    # 17720 joined the exclusion on 2026-07-26: it STARVES the GPU rather than refusing capacity — the same
    # job ran 3.14-3.4 ns/h at 44 % utilisation on its RTX 4080S against 5.5-6.0 ns/h at 75 % on a 4090. An
    # idle GPU, not a busy slower one, so a relaunch must not land back on it. The exclusion is host-selection
    # policy and is allowed to grow; what this test pins is that the shipped list stays BUILDER-PRODUCED
    # rather than hand-typed, and test_the_shipped_entries_carry_what_lane13_ACTUALLY_launched keeps it equal
    # to the task file, so the two relaunchers cannot disagree about where a leg may run.
    # NR4A2 finished 2026-07-26 8:36 AM ET (result artifact in S3) and is `enabled: false` -- kept in the
    # list, not deleted, per the file's own editing convention, so the completed unit stays on the record.
    # What this test pins is that the shipped entries stay BUILDER-PRODUCED rather than hand-typed; the
    # enabled flag is lifecycle and is expected to move.
    # BOTH legs completed 2026-07-26 (NR4A2 8:36 AM, NR4A1 by 3:37 PM) and are `enabled: false`, kept on the
    # record per the file's editing convention. What this pins is that the entries stay BUILDER-PRODUCED
    # rather than hand-typed; `enabled` and `_disabled_why` are lifecycle and are expected to move.
    doc = _generic()
    want = [vw.paralogue_entry("NR4A1", git_branch="claude/max-effort-2dq11l-paralogue",
                               exclude_machines="142143,17720", enabled=False),
            vw.paralogue_entry("NR4A2", git_branch="claude/max-effort-2dq11l-paralogue",
                               exclude_machines="142143,17720", enabled=False)]
    for i in (0, 1):
        want[i]["_disabled_why"] = doc["watch"][i].get("_disabled_why")
    assert doc["watch"] == want


def test_the_declared_required_keys_match_the_implemented_kinds():
    """One fact, one place: the doc's `_required_run_params_by_kind` and the code's registry are the same
    fact. If they can drift, an entry can pass validation while missing something its relaunch needs."""
    doc = _generic()
    assert doc["_required_run_params_by_kind"] == {k: list(v.required_keys)
                                                   for k, v in sorted(vw.KINDS.items())}


def test_the_shipped_entries_carry_what_lane13_ACTUALLY_launched():
    """The guard against the exact failure this lane was warned about: inventing relaunch parameters.
    metad_ns / release_ns / n_rep do NOT key the checkpoint prefix, so a wrong value would resume the right
    trajectory and silently run it to the wrong length. They are read back from LANE 13's own task file."""
    with open(LANE13_TASK) as fh:
        task = json.load(fh)
    for e in _generic()["watch"]:
        assert float(e["metad_ns"]) == float(task["metad_ns"])
        assert float(e["release_ns"]) == float(task["release_ns"])
        assert int(e["n_rep"]) == int(task["n_rep"])
        assert e["exclude_machines"] == task["exclude_machines"]
    assert {e["target"] for e in _generic()["watch"]} == set(task["targets"].split(","))


def test_the_shipped_entry_reproduces_the_launchers_own_leg_identity():
    """The strongest available check short of renting a host: build the JobSpec the relaunch WOULD submit and
    assert the launcher agrees about the leg's name, its result prefix and its run parameters. A relaunch that
    rented a differently-named instance would be invisible to the next pass."""
    import nr4a_paralogue_md_ops as ops
    import nr4a_paralogue_md_vast_launch as L
    for e in _generic()["watch"]:
        spec = L.build_jobspec(e["target"], mode="real", metad_ns=float(e["metad_ns"]),
                               release_ns=float(e["release_ns"]), n_rep=int(e["n_rep"]),
                               git_branch=e["git_branch"], bucket=e["bucket"])
        assert spec.name == e["unit_id"], "the watch list and the launcher disagree about this leg's identity"
        assert spec.image == e["image"]
        assert spec.env["RESULT_S3"] == f"s3://{e['bucket']}/{e['result_prefix']}/{e['unit_id']}"
        assert spec.env["METAD_NS"] == "60" and spec.env["RELEASE_NS"] == "5" and spec.env["N_REP"] == "3"
        assert spec.env["SEED"] == e["seed"] and spec.env["SEGMENT_NS"] == e["segment_ns"]
        assert spec.env["GIT_BRANCH"] == e["git_branch"]
        # and the DONE test reads the key the job actually uploads
        assert ops.result_key(e["unit_id"]) == \
            f"{e['result_prefix']}/{e['unit_id']}/{e['target'].lower()}-pocket-ensemble.tar.gz"


def test_every_shipped_entry_passes_its_kinds_preflight():
    for e in _generic()["watch"]:
        assert vw.KINDS[e["kind"]].preflight(e) == []


# ================================================================= THE ARMING READ-BACK
def test_verify_armed_fails_when_a_unit_went_missing(tmp_path):
    p = tmp_path / "w.json"
    doc = _generic()
    doc["watch"] = []
    p.write_text(json.dumps(doc))
    with pytest.raises(SystemExit):
        vw.verify_armed(["nr4a-pdyn-nr4a1"], str(p))


def test_verify_armed_fails_when_an_entry_is_merely_disabled(tmp_path):
    p = tmp_path / "w.json"
    doc = _generic()
    doc["watch"][0]["enabled"] = False
    p.write_text(json.dumps(doc))
    with pytest.raises(SystemExit):
        vw.verify_armed(["nr4a-pdyn-nr4a1"], str(p))


def test_verify_armed_fails_when_the_list_is_present_but_invalid(tmp_path):
    """Present-and-enabled is not enough: an entry the config guard rejects aborts every pass, which is the
    same as not being watched at all."""
    p = tmp_path / "w.json"
    doc = _generic()
    del doc["watch"][0]["git_branch"]
    p.write_text(json.dumps(doc))
    with pytest.raises(SystemExit):
        vw.verify_armed(["nr4a-pdyn-nr4a1"], str(p))


def test_verify_armed_passes_on_the_shipped_list():
    # Both paralogue legs have completed, so NOTHING is armed — and that is the state verify_armed must
    # report honestly. Its job is to catch a LIVE leg going missing from the list; a finished one must never
    # count as armed, or "covered" would drift to mean "was covered once".
    # SystemExit, not Exception -- it derives from BaseException, and pytest.raises(Exception) would let the
    # refusal sail through as an uncaught error rather than a passing assertion.
    for done_unit in ("nr4a-pdyn-nr4a1", "nr4a-pdyn-nr4a2"):
        with pytest.raises(SystemExit, match="DOES NOT COVER"):
            vw.verify_armed([done_unit], GENERIC_LIST)
    # An empty ask is a legitimate no-op: nothing running, nothing to cover.
    assert vw.verify_armed([], GENERIC_LIST) == []


def test_an_empty_or_missing_list_is_a_legitimate_no_op(tmp_path):
    assert vw.enabled_entries(vw.load_watch(str(tmp_path / "nope.json"))) == []
    assert vw.enabled_entries({"watch": []}) == []
    assert vw.enabled_entries(None) == []


# ================================================================= THE WORKFLOW IS WIRED TO REAL FILES
def test_the_workflow_validates_both_watch_lists_before_acting():
    wf = os.path.join(ROOT, ".github", "workflows", "vast-watchdog.yml")
    text = open(wf).read()
    assert "watchdog_validate.py research/modalities/vast-watch.json" in text
    assert "watchdog_validate.py research/modalities/ternary-vast-watch.json" in text
    assert "tests/test_workflows_parse.py" in text, "the parse gate that stops a cron silently never firing"
    assert "vast_watchdog.py --tick" in text
    assert "vast_watchdog.py --kinds" in text, "print the implemented kinds so coverage is visible in the log"
    assert "VAST WATCHDOG ALIVE" in text, "a green tick must mean 'it ran', not 'it existed'"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))


# ---- KIND: step1_fanout ------------------------------------------------------------------------------------
# The composite scalar is the part that must be right. This kind's census FREEZES legitimately twice per unit
# (MBAR analysis at the end of each leg) and RESTARTS twice (warmup->production, complex->solvent), so a
# scalar that is not phase-dominated would either stall-alert a healthy unit or hide a wedged one.

def test_step1_fanout_scalar_is_monotone_over_a_whole_unit_lifetime():
    K = vw.Step1FanoutKind
    lifetime = [("boot", 0), ("staged", 0),
                ("leg-complex-running", 20), ("leg-complex-running", 2000),
                ("leg-complex-running", 1_002_000),        # warmup -> production, census restarts
                ("leg-complex-done", 0),                   # census frozen through MBAR
                ("leg-solvent-running", 10_000_020),       # solvent leg, census restarts again
                ("leg-solvent-done", 0), ("reduce", 0), ("done", 0)]
    scalars = [K.score(p, c)[0] for p, c in lifetime]
    assert scalars == sorted(scalars), scalars
    assert all(K.score(p, c)[2] for p, c in lifetime)


def test_step1_fanout_refuses_a_phase_it_does_not_rank():
    """A pipeline that gains a marker must make the watchdog REFUSE, not silently score it 0 — collapsing an
    unknown phase to zero manufactures a setup-stall out of a reporting change."""
    scalar, _lab, readable, why = vw.Step1FanoutKind.score("polishing", 5)
    assert scalar == 0 and readable is False and "does not rank" in why


def test_step1_fanout_treats_a_leg_failure_marker_as_a_crash():
    K = vw.Step1FanoutKind
    assert K._failed("leg-complex-FAILED-rc3") and K._failed("leg-solvent-NORESULT")
    assert not K._failed("leg-complex-running") and not K._failed("")
    assert K.score("leg-complex-FAILED-rc3", 0)[2] is True   # readable: a crash is a real reading


def test_step1_fanout_unreadable_census_is_not_zero_progress():
    assert vw.Step1FanoutKind.score("leg-complex-running", -1)[2] is False


def test_step1_fanout_label_is_derived_from_the_frozen_map_not_the_unit_id():
    """The Vast label is `s1f-<idx>-<ligand_b>`, not the unit_id. A prefix or identity match would pair the
    wrong box with the wrong edge, and the watchdog would report another unit's host as this one's."""
    import congeneric_fanout as cf
    units = cf.default_units()
    uid = units[3]["unit_id"]
    assert vw.Step1FanoutKind.label_matches(f"s1f-03-{units[3]['ligand_b']}"[:64], uid)
    assert not vw.Step1FanoutKind.label_matches(uid, uid)
    assert not vw.Step1FanoutKind.label_matches(f"s1f-04-{units[4]['ligand_b']}"[:64], uid)


def test_step1_fanout_preflight_rejects_a_unit_outside_the_frozen_tranche():
    assert vw.Step1FanoutKind.preflight({"unit_id": "not-a-real-unit"})
    import congeneric_fanout as cf
    assert vw.Step1FanoutKind.preflight({"unit_id": cf.default_units()[0]["unit_id"]}) == []
