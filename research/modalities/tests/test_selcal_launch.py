#!/usr/bin/env python3
"""The sensitivity control's LAUNCHER — the spend guards, in the form that fails when they are removed.

Every test here corresponds to a mistake this program has already paid for. They are not style checks:

  * the buy line must travel ON THE SPEC handed to `submit`, or the lane rents at any price (the NR-V04
    endpoint-MD lane did exactly that until 2026-07-31);
  * the bill must be recorded BEFORE the DELETE, because that is the last moment the instance record exists
    (a rental that billed and left no trace: instance 46459452, overnight);
  * a heartbeat commit must be `--allow-empty`, because THE TIMESTAMP IS THE STALENESS SIGNAL — the
    `git diff --cached --quiet` guard was found in three lanes;
  * the model seed must be PINNED per leg, or the model-level statistics are computed over unknown inputs;
  * a declined tick must leave a durable record, or a silent decline is indistinguishable from a broken
    re-placer (1 h 55 m of unnoticed outage on a sibling lane).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import selcal_panel as SP  # noqa: E402
import selcal_vast_launch as L  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(HERE, "selcal_vast_launch.py")).read()
REPO = os.path.dirname(os.path.dirname(HERE))
WORKFLOW = os.path.join(REPO, ".github", "workflows", "selectivity-control-vast.yml")


# =============================================================================================================
# the buy line
# =============================================================================================================
def test_every_leg_spec_carries_the_approved_buy_line():
    """`rank_offers_by_usd_per_ns` drops every offer above the cap BEFORE selection sees it — including on
    each fallback after a capacity refusal, which is exactly where a launcher that re-checked one chosen
    offer would leak."""
    from inflight_usd_per_ns import APPROVED_USD_PER_NS
    for arm, m, r in SP.enumerate_units()[:4]:
        spec = L.build_leg_jobspec(arm, m, r, "run", "main", "bkt")
        assert spec.resources.max_usd_per_ns == APPROVED_USD_PER_NS


def test_the_cofold_rental_faces_the_same_line():
    """A relaunch is a new purchase — and so is a co-fold. There is no rung of this ladder that rents
    uncapped."""
    from inflight_usd_per_ns import APPROVED_USD_PER_NS
    spec = L.build_cofold_jobspec("main", "bkt")
    assert spec.resources.max_usd_per_ns == APPROVED_USD_PER_NS


def test_the_buy_line_is_never_typed_here():
    """CLAUDE.md §1: the invariant is an ABSOLUTE $/ns and the multiple is DERIVED from it. A literal in this
    file would silently change meaning the next time the throughput table is re-anchored."""
    assert "buy_ceiling_usd_per_ns" in SRC
    assert not re.search(r"max_usd_per_ns\s*=\s*[0-9]", SRC)


def test_the_gate_prices_an_UNCAPPED_spec():
    """A gate must SEE the expensive offers in order to report how far above the line the board sits. The cap
    binds on the spec handed to `submit`; pricing with it on would make a thin board look like an empty one."""
    assert "UNCAPPED" in SRC
    src = SRC[SRC.index("def market_gate"):SRC.index("def _record_gate")]
    assert "endpoint_md_resources()" in src


# =============================================================================================================
# the ledger
# =============================================================================================================
def test_the_bill_is_recorded_BEFORE_the_delete():
    """Ordering, checked in the source rather than asserted in prose: `_ledger_record` must appear before the
    DELETE call inside `mode_reap`, because after the DELETE the instance record is gone."""
    body = SRC[SRC.index("def mode_reap"):SRC.index("def mode_watch")]
    i_ledger = body.index("_ledger_record(inst")
    i_delete = body.index('_vast_request("DELETE"')
    assert i_ledger < i_delete, "the ledger row must be written before the instance is destroyed"


def test_the_ledger_records_uptime_and_rate_not_just_an_id():
    assert '"dph_total"' in SRC and '"uptime_s"' in SRC and '"billed_usd"' in SRC


# =============================================================================================================
# the per-tick gate record
# =============================================================================================================
def test_every_placement_path_writes_a_gate_record():
    """A decline that leaves no record is indistinguishable from a re-placer that never ran."""
    for fn in ("mode_launch", "mode_cofold(", "mode_gate_tick"):
        # ⚠ the trailing "(" on mode_cofold is load-bearing: without it this matched `mode_cofold_dry`,
        # which is a $0 printer, and the test passed while the RENTING path was unchecked.
        body = SRC[SRC.index("def %s" % fn):]
        body = body[:body.index("\ndef ", 10)]
        assert "_record_gate(" in body, "%s can return without recording its decision" % fn


def test_a_nothing_to_buy_tick_still_prices_or_says_why_not():
    """`price=False` is an EVALUATION, not a hold — but it must still be written, or the artifact only ever
    appears when the lane is buying and cannot distinguish 'happy' from 'never ran'."""
    assert "price=False" in SRC
    body = SRC[SRC.index("def market_gate"):SRC.index("def _record_gate")]
    assert '"priced": False' in body and "NOT PRICED" in body


def test_a_hold_reports_board_depth_and_separates_a_filter_diagnosis():
    """`qualifying` far below `offers_returned` is a FILTER diagnosis wearing a price label; the remedies are
    opposite (wait vs widen), so the two must not render alike."""
    body = SRC[SRC.index("def market_gate"):SRC.index("def _record_gate")]
    assert "board_depth" in body
    assert "exclusions_or_spec_not_price" in body
    assert "NOT A PRICE HOLD" in body


# =============================================================================================================
# the panel's own invariants, as the launcher expresses them
# =============================================================================================================
def test_the_leg_pins_its_cofold_model_seed():
    arm = SP.arm_by_id(SP.ARM_B)
    spec = L.build_leg_jobspec(arm, 5, 1, "run", "main", "bkt")
    assert spec.env["COFOLD_PREFIX_S3"].endswith("/seed_5/")
    assert spec.env["COFOLD_MODEL_SEED"] == "5"


def test_the_pipeline_refuses_more_than_one_cofold_cif():
    """Two CIFs under the pinned prefix would mean the seed pin failed and the leg would silently start from
    an unknown model, corrupting the model-level means. Fail, never guess."""
    assert "expected exactly 1 co-fold CIF" in L._MD_PIPELINE


def test_the_pipeline_runs_the_input_audit_and_refuses_a_bad_input():
    assert "cofold_input_audit" in L._MD_PIPELINE
    assert "REFUSING to run" in L._MD_PIPELINE


def test_the_phase_marker_names_the_host_that_wrote_it():
    """A marker that outlives its host reads as a fact about the CURRENT rental and is not."""
    assert "CONTAINER_ID" in L._MD_PIPELINE and "_HOST" in L._MD_PIPELINE
    assert "phase_written_by_current_host" in SRC


def test_the_leg_uses_the_unmodified_driver():
    """A sensitivity control that ran a modified driver would calibrate a readout the program does not use."""
    assert "nrv04_covalent_md.py" in L._MD_PIPELINE
    assert "autoteardown.py" in L._MD_PIPELINE


def test_checkpoints_are_written_per_unit_and_mirrored_continuously():
    arm = SP.ARMS[0]
    spec = L.build_leg_jobspec(arm, 1, 0, "run", "main", "bkt")
    assert spec.resume is True
    assert int(spec.env["CKPT_EVERY_FRAMES"]) > 0
    assert spec.env["RESULT_S3"].endswith(spec.name)          # the driver mirrors checkpoints to RESULT_S3
    assert "s3 sync" in L._COFOLD_PIPELINE                     # co-fold: continuous, not end-of-job


def test_the_smoke_rung_cannot_be_the_last_rung_before_the_fleet():
    """`smoke` green does not authorise `launch`: the smoke skips the heavy MD path, so only a real leg can
    catch an environment fault. The ladder must therefore expose a single-real-leg mode of its own."""
    assert "leg" in L.MODES and "smoke" in L.MODES and "launch" in L.MODES
    assert "GREEN DOES NOT AUTHORISE" in L.__doc__


def test_the_derived_cost_matches_the_authorised_plan():
    """The cost is DERIVED (ladder reprice x the endpoint-MD reference GPU-hours), never typed — and it must
    still land on the figure the options paper authorised for D1/D2.

    ⚠ PRICED ON THE AUTHORISED SHAPE, NOT THE LIVE ONE. What was authorised was a 24-unit panel; excluding a
    measured input fault makes the panel CHEAPER, and letting the authorisation check float down with it
    would mean the ceiling silently re-derives itself to whatever is left — a budget that can only ever be
    satisfied. The live cost is asserted separately, and only that it does not EXCEED the authorisation.
    """
    import selcal_panel as SP
    frozen = L.ladder_cost(len(SP.enumerate_units(include_excluded=True)))
    assert frozen["n_units"] == 24
    assert abs(frozen["plan_usd"] - 3.79) < 0.01
    assert abs(frozen["range_usd"][0] - 1.57) < 0.01 and abs(frozen["range_usd"][1] - 9.54) < 0.01
    live = L.ladder_cost()
    assert live["n_units"] == len(SP.enumerate_units())
    assert live["plan_usd"] <= frozen["plan_usd"] + 1e-9, "the live panel may only ever be cheaper"


# =============================================================================================================
# the workflow
# =============================================================================================================
def test_workflow_parses_and_exposes_the_whole_ladder():
    import yaml
    with open(WORKFLOW) as fh:
        wf = yaml.safe_load(fh)
    opts = set(wf[True]["workflow_dispatch"]["inputs"]["mode"]["options"])
    for rung in ("refs", "selftest", "cofold_dry", "cofold", "stage_test", "smoke", "leg", "launch",
                 "collect", "gate_tick", "reap", "stop"):
        assert rung in opts, "the ladder's %s rung is not dispatchable" % rung


def test_heartbeat_commits_are_allow_empty_and_ungated():
    """⚠ THE LANDMINE, found in three lanes: `git diff --cached --quiet` around a heartbeat commit. The
    TIMESTAMP is the staleness signal, so a tick that changes no bytes must still leave a dated commit."""
    # ⚠ RE-POINTED 2026-08-01, when this step was converted to `publish_artifacts.sh`. This used to assert
    # the literal `git commit --allow-empty` IN THIS FILE, which is a test of the implementation rather than
    # of the rule — and it broke the moment the implementation moved to its one home, blocking a launch that
    # would have re-placed five units. The RULE is unchanged and now lives in the primitive, where
    # `tests/test_publish_does_not_revert_another_jobs_artifact.py::test_the_heartbeat_commit_still_happens…`
    # holds it for every caller at once. What this test still owns is that this workflow USES that home.
    wf = open(WORKFLOW).read()
    executable = "\n".join(ln for ln in wf.splitlines() if not ln.strip().startswith("#"))
    assert executable.count("publish_artifacts.sh") == 2, \
        "both commit steps must publish through the primitive that guarantees the heartbeat commit"
    assert "diff --cached --quiet" not in executable
    prim = open(os.path.join(REPO, "research", "compute", "publish_artifacts.sh")).read()
    assert "git commit -q --allow-empty" in prim, "the primitive must still make the heartbeat unconditional"


def test_the_commit_step_cannot_LOSE_a_tick_to_a_merge_conflict():
    """★★ MEASURED 2026-08-01 (run 30710853581). These artifacts have MORE THAN ONE WRITER: a `cofold_watch`
    tick and a `cofold_collect` tick both wrote selcal-cofold-census.json, `git pull --rebase` hit
    `CONFLICT (content)`, the `|| true` swallowed it, the repo was left mid-rebase and the push printed
    "Everything up-to-date". The tick's REAP READOUT was committed and then silently lost, and a supervision
    job reported failure for a reason that had nothing to do with the fleet it was watching.

    They are regenerated snapshots, so last-writer-wins is the CORRECT rule, not a compromise — reset to the
    remote and lay our copies on top, so no merge can occur at all.

    ⚠ RE-POINTED 2026-08-01. The snapshot/reset/restore/retry this used to assert line-by-line now lives in
    `research/compute/publish_artifacts.sh`, which is the one home for it and is tested directly. Asserting
    the inlined shell here did not make the lane safer — it made the CONVERSION break the lane, because this
    file is run by the pre-rental guards step, so three stale string assertions failed a `launch` and left
    five units un-replaced. The property is the same; the home moved."""
    wf = open(WORKFLOW).read()
    executable = "\n".join(ln for ln in wf.splitlines() if not ln.strip().startswith("#"))
    assert "pull --rebase" not in executable, \
        "a rebase can conflict on a multi-writer snapshot and silently drop the tick"
    assert executable.count("publish_artifacts.sh") == 2, \
        "both commit steps must go through the primitive rather than re-implementing the dance"
    prim = open(os.path.join(REPO, "research", "compute", "publish_artifacts.sh")).read()
    assert "git reset -q --hard FETCH_HEAD" in prim, "rewrite onto upstream, so no merge is possible"
    assert "cp --parents" in prim, "our fresh copies must be snapshotted BEFORE the reset"
    assert "push race on attempt" in prim, "the push must retry, or an ordinary race still drops a tick"


def test_the_workflow_runs_the_guards_before_any_rental():
    wf = open(WORKFLOW).read()
    gpu = wf[wf.index("  gpu:"):]
    assert gpu.index("pytest") < gpu.index("--mode \"$MODE\""), \
        "the guards must run BEFORE the step that rents"


def test_every_artifact_the_workflow_commits_is_one_something_writes():
    """A registry entry naming a file nothing writes is a lie a CI contract test should catch. Same standard
    applied here to the workflow's own commit list."""
    wf = open(WORKFLOW).read()
    declared = set(re.findall(r"research/modalities/(selcal-[a-z0-9-]+\.json)", wf))
    written = {os.path.basename(getattr(L, n)) for n in dir(L)
               if n.isupper() and isinstance(getattr(L, n), str) and getattr(L, n).endswith(".json")}
    written.add("selcal-reference-selectivity.json")           # written by selcal_reference_selectivity.py
    missing = declared - written
    assert not missing, "the workflow commits %s but nothing in the lane writes them" % sorted(missing)


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))


# =============================================================================================================
# the ledger's uptime field — the mistake that printed a six-figure row for an eight-minute box
# =============================================================================================================
def test_rental_uptime_comes_from_start_date_not_duration():
    """⛔ `instance["duration"]` is the HOST MACHINE's uptime. Reading it as the rental's produced a ledger row
    of 2,303,739,360 s and $117,708.76 for a box that lived ~8 minutes. A spend ledger that can print that is
    worse than no ledger, because the number looks authoritative."""
    import time as _t
    now = _t.time()
    inst = {"start_date": now - 600.0, "duration": 2303739360.0}
    assert abs(L.rental_uptime_s(inst, now=now) - 600.0) < 1.0
    assert "duration" not in SRC[SRC.index("def _ledger_record"):SRC.index("def _plan_rate")] or \
        "never `duration`" in SRC


def test_an_unmeasurable_uptime_is_UNKNOWN_not_zero():
    """Defaulting to zero would silently price a real rental at $0 — an absent reading reported as a reading
    of absence, in the one artifact where that is most expensive."""
    assert L.rental_uptime_s({}) is None
    assert L.rental_uptime_s({"start_date": 0}) is None
    body = SRC[SRC.index("def _ledger_record"):SRC.index("def _plan_rate")]
    assert "billed_usd_absent_why" in body and "UNKNOWN, not zero" in body


def test_a_replaced_ledger_row_keeps_its_predecessor():
    """Rule 1.2: never silently drop a superseded number, and a spend ledger is the last place to start."""
    body = SRC[SRC.index("def _ledger_record"):SRC.index("def _plan_rate")]
    assert 'setdefault("corrections"' in body


def test_the_cofold_restores_finished_work_from_S3_before_it_runs():
    """⛔ THE GAP THAT MADE PREEMPTION EXPENSIVE. Every completed (arm, seed) is already durable in S3, but a
    replacement host started from an EMPTY output directory, so the runner's per-seed skip could never fire
    and a preemption cost the whole batch instead of the seed in flight. The restore also recovers the MSA,
    which is the expensive part — a host that died during weight download hands its MSA to its successor."""
    assert "s3 sync \"$RESULT_S3/\" \"$OUTPUT_DIR/\"" in L._COFOLD_PIPELINE
    i_restore = L._COFOLD_PIPELINE.index("s3 sync \"$RESULT_S3/\" \"$OUTPUT_DIR/\"")
    i_run = L._COFOLD_PIPELINE.index("selcal_cofold_run.py")
    assert i_restore < i_run, "the restore must happen BEFORE the runner decides what to skip"


# =============================================================================================================
# ★★ THE REAPER — the incident of 2026-08-01, in the form that fails if it comes back
# =============================================================================================================
# Run 30707211425 (`reap`, 12:01 PM ET) completed SUCCESS, printed `0 destroyed, 2 kept running` and destroyed
# nothing while two hosts billed at $0.184/hr — one of them with all six of its models already durable in S3
# and its own pipeline finished 80 minutes earlier. The reaper had no predicate that could ever fire for a
# co-fold host: `landed and label in done` reduces to `label in done`, and `done` only ever holds MD LEG unit
# names. A guard nobody has watched fail is not known to work, so each control below is a case with a KNOWN
# right answer, and two of them are cases where the right answer is DO NOT REAP.
_SM2 = "selcal-cofold-selcal-smarca-cofold-v1-smarca2"
_SM4 = "selcal-cofold-selcal-smarca-cofold-v1-smarca4"
_BOTH = ("smarca2", "smarca4")


def _inst(label, status="running", iid="1", gpu_util=0.0):
    return {"id": iid, "label": label, "actual_status": status, "gpu_util": gpu_util,
            "dph_total": 0.18402222222222223, "start_date": 1.0}


def _fn(name):
    """The named function's AST node. Tests below assert on CODE, never on the prose beside it — a substring
    scan of the source fails on the very comment that explains why a pattern is banned, which is a test that
    forbids writing down its own reason."""
    import ast
    for node in ast.walk(ast.parse(SRC)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError("no function %r in selcal_vast_launch.py" % name)


def _fn_code(name):
    """The function's executable body, docstring removed."""
    import ast
    node = _fn(name)
    body = node.body[1:] if ast.get_docstring(node) else node.body
    return "\n".join(ast.dump(b) for b in body)


def test_control_a_host_whose_arm_is_DONE_is_reaped():
    """46508454: `running`, `gpu_util 0.0`, six of six models banked. Keeping it buys nothing — it was scoped
    to smarca2 by `SELCAL_SYSTEMS` at launch, so it cannot contribute to the arm that is short."""
    reap, why = L.reap_decision(_inst(_SM2, iid="46508454"), done_units=set(),
                                cofold_complete_systems=("smarca2",), s3_readable=True)
    assert reap is True
    assert "work banked, no remaining role" in why and "smarca2" in why


def test_control_a_host_MID_WORK_with_models_still_to_produce_is_SPARED():
    """The control that matters most: the same instance record, `gpu_util 0.0`, differing ONLY in whether its
    arm's models are in S3. A reaper that destroys this one is worse than the bug it replaced."""
    reap, why = L.reap_decision(_inst(_SM4, iid="46508511"), done_units=set(),
                                cofold_complete_systems=("smarca2",), s3_readable=True)
    assert reap is False
    assert "SPARED" in why and "still owe models" in why


def test_control_a_TERMINAL_host_is_reaped():
    """`exited`/`stopped`/`offline`/`error`: Vast still LISTS and BILLS it and it is not coming back."""
    for status in ("exited", "stopped", "offline", "error"):
        reap, why = L.reap_decision(_inst(_SM4, status=status), done_units=set(),
                                    cofold_complete_systems=(), s3_readable=True)
        assert reap is True, "a %r host must be reaped" % status
        assert "terminal state" in why and status in why


def test_control_an_UNREADABLE_census_reaps_nothing_on_banked_work():
    """An absent reading is not a reading of absence. With no census, neither S3-derived branch may fire —
    not the banked-work one AND not the host-terminus one — however complete the caller claims the arms are."""
    for label in (_SM2, _SM4, "selcal-smarca2-m1-r0"):
        reap, why = L.reap_decision(_inst(label), done_units={label}, cofold_complete_systems=_BOTH,
                                    s3_readable=False, host_phase="done rc=0 x instance=1")
        assert reap is False, "%s must be spared when the census is unreadable" % label
        assert "absent reading is not a reading of absence" in why


def test_an_unreadable_census_still_reaps_a_TERMINAL_host():
    """The one deliberate exception, and the reason is that its evidence never came from S3: an S3 outage is
    exactly when a dead box must not be left billing for hours."""
    reap, why = L.reap_decision(_inst(_SM4, status="exited"), done_units=set(),
                                cofold_complete_systems=(), s3_readable=False)
    assert reap is True and "terminal state" in why


def test_a_host_that_reported_its_own_terminus_is_reaped_even_with_NOTHING_banked():
    """46508511 measured: `done rc=1`, 0 of 6 models, and Vast reporting it `running` again after a restart.
    Nothing is banked, so the banked-work branch cannot fire — and without this branch the box bills forever
    for a run that already returned."""
    reap, why = L.reap_decision(_inst(_SM4, iid="46508511"), done_units=set(), cofold_complete_systems=(),
                                s3_readable=True,
                                host_phase="done rc=1 2026-08-01T15:23:39Z instance=46508511 attempt=x")
    assert reap is True and "host reported its terminus" in why


def test_a_phase_marker_naming_ANOTHER_instance_condemns_nobody():
    """Both arms' co-fold hosts write to the SAME `$RESULT_S3`, so the shared `phase.txt` describes whichever
    wrote last. A marker naming a different box is a fossil, and reaping on it would destroy a live host on
    the strength of its neighbour's death."""
    reap, why = L.reap_decision(_inst(_SM4, iid="46508511"), done_units=set(), cofold_complete_systems=(),
                                s3_readable=True,
                                host_phase="done rc=0 2026-08-01T14:41:08Z instance=46508454 attempt=x")
    assert reap is False and "SPARED" in why


def test_the_reaper_NEVER_reads_gpu_util():
    """⛔ INVIOLABLE (CLAUDE.md §6). Both hosts in the incident read `gpu_util: 0.0`, INCLUDING the one that
    had just produced all six of its models, so idleness cannot tell a finished box from a working one. Only
    a measured absence of banked work / a host-written terminus / a terminal state may condemn."""
    assert "gpu_util" not in _fn_code("reap_decision")
    # ...and behaviourally: two records identical except for gpu_util must decide identically.
    busy = L.reap_decision(_inst(_SM2, gpu_util=99.0), set(), ("smarca2",), True)
    idle = L.reap_decision(_inst(_SM2, gpu_util=0.0), set(), ("smarca2",), True)
    assert busy == idle
    busy = L.reap_decision(_inst(_SM4, gpu_util=99.0), set(), ("smarca2",), True)
    idle = L.reap_decision(_inst(_SM4, gpu_util=0.0), set(), ("smarca2",), True)
    assert busy == idle and idle[0] is False


def test_the_dead_disjunct_that_caused_the_incident_cannot_come_back():
    """`landed and label in done` reduces to `label in done`, and `done` only ever holds MD LEG unit names —
    so the co-fold disjunct was unreachable BY CONSTRUCTION. The invariant is therefore behavioural, not
    textual: a co-fold host must be reapable with an EMPTY `done_units`, which is the only state it can ever
    actually be observed in."""
    reap, _why = L.reap_decision(_inst(_SM2), done_units=set(), cofold_complete_systems=("smarca2",),
                                 s3_readable=True)
    assert reap is True, "a co-fold host must be reapable without ever appearing in the MD leg set"
    body = SRC[SRC.index("def mode_reap"):SRC.index("def mode_watch")]
    assert "reap_decision(" in body, "mode_reap must delegate to the pure, tested classifier"
    assert "_cofold_census(" in body, "the reap must consult the co-fold census, not just the MD leg set"


def test_the_reap_leaves_a_durable_record_of_what_it_SPARED_too():
    """A reaper that only printed is how a run could succeed, destroy nothing and leave no trace — the lane's
    census was silent for 77 minutes and an ACCOUNT-level alarm, not this lane, is what noticed."""
    body = SRC[SRC.index("def mode_reap"):SRC.index("def mode_watch")]
    assert "_write(REAP_READOUT" in body
    assert '"spared"' in body and '"destroyed"' in body and '"s3_census_readable"' in body


def test_a_failed_DELETE_is_loud_because_the_host_is_still_billing():
    body = SRC[SRC.index("def mode_reap"):SRC.index("def mode_watch")]
    assert "SELCAL REAP COULD NOT DESTROY" in body and "destroy_failed" in body


def test_the_cofold_watch_reaps_on_EVERY_tick_not_only_at_completion():
    """The second half of the leak: the reap sat inside `if cen["complete"]`, so a fleet with one arm finished
    and one arm short kept BOTH hosts — the finished arm's box billed 85+ minutes with its work already
    durable. A host scoped to a finished arm cannot contribute to the missing one.

    Asserted on the AST, so the reap must be a statement of the LOOP BODY itself — not merely present
    somewhere in the function, which a call nested back inside the completeness branch would also satisfy."""
    import ast
    loops = [n for n in ast.walk(_fn("mode_cofold_watch")) if isinstance(n, ast.While)]
    assert len(loops) == 1
    tick = [ast.dump(s) for s in loops[0].body]                 # DIRECT statements of the tick, not nested
    assert any("'mode_reap'" in s for s in tick), \
        "the reap must run on EVERY tick, as a statement of the loop body — not inside `if cen['complete']`"
    assert any("'_write'" in s and "COFOLD_CENSUS" in s for s in tick), \
        "every supervision tick must leave a dated census, or a frozen lane reads as a quiet one"


def test_a_supervision_tick_PUBLISHES_not_merely_writes():
    """⛔ THE STALENESS BUG WEARING A DIFFERENT HAT. The workflow's commit step is a separate step, so it runs
    only after the python process exits: a 58-minute watch that faithfully rewrites the census every 3 minutes
    still leaves the lane's census frozen on `main` for 58 minutes — the 77-minute silence of 2026-08-01 with
    a different number on it. A file the outside world cannot see is not a heartbeat."""
    import ast
    for fn in ("mode_cofold_watch", "mode_watch"):
        loops = [n for n in ast.walk(_fn(fn)) if isinstance(n, ast.While)]
        assert len(loops) == 1, fn
        tick = [ast.dump(s) for s in loops[0].body]
        assert any("'_tick_publish'" in s for s in tick), \
            "%s must publish its heartbeat every tick, not only when the job ends" % fn
    body = SRC[SRC.index("def _tick_publish"):SRC.index("def mode_cofold_watch")]
    assert "reset" in body and "--hard" in body, "last writer wins — a snapshot merge describes no instant"
    assert "never raises" in body or "Never raises" in body


def test_a_cofold_label_is_resolved_by_the_NAME_BUILDER_not_by_splitting_on_dashes():
    """The prefix itself contains dashes (`selcal-cofold-selcal-smarca-cofold-v1-smarca2`), so a
    split-on-dash reader mis-assigns the arm — and a mis-assigned arm is a host reaped for work banked
    somewhere else."""
    assert L.cofold_label_systems(_SM2) == ("smarca2",)
    assert L.cofold_label_systems(_SM4) == ("smarca4",)
    assert L.cofold_label_systems("selcal-smarca2-m1-r0") == ()
    assert L.cofold_label_systems("") == ()
    both = L.build_cofold_jobspec("main", "b").name
    assert set(L.cofold_label_systems(both)) == set(_BOTH)


def test_a_BOTH_ARM_cofold_host_is_spared_until_BOTH_arms_are_complete():
    """The `all` host covers two arms; reaping it when one is done would abandon the other mid-flight."""
    both = L.build_cofold_jobspec("main", "b").name
    reap, _why = L.reap_decision(_inst(both), done_units=set(), cofold_complete_systems=("smarca2",),
                                 s3_readable=True)
    assert reap is False
    reap, why = L.reap_decision(_inst(both), done_units=set(), cofold_complete_systems=_BOTH,
                                s3_readable=True)
    assert reap is True and "work banked" in why


def test_a_landed_MD_leg_still_reaps_its_own_host():
    """The branch that already worked must keep working — the fix must not trade one class of leak for
    another."""
    reap, why = L.reap_decision(_inst("selcal-smarca2-m1-r0"), done_units={"selcal-smarca2-m1-r0"},
                                cofold_complete_systems=(), s3_readable=True)
    assert reap is True and "work banked" in why
    reap, _why = L.reap_decision(_inst("selcal-smarca2-m1-r0"), done_units=set(),
                                 cofold_complete_systems=(), s3_readable=True)
    assert reap is False, "an MD host with no landed record is mid-work and must be spared"


def test_stop_all_still_takes_everything():
    reap, why = L.reap_decision(_inst(_SM4), done_units=set(), cofold_complete_systems=(), s3_readable=True,
                                stop_all=True)
    assert reap is True and "stop_all" in why


def test_the_terminal_set_is_imported_rather_than_re_typed():
    """Two sets already existed and disagreed. The union is built from the importable one with the delta
    named, not minted as a third differently-wrong copy (CLAUDE.md rule 1)."""
    from nrv04_vast_launch import _TERMINAL_STATES
    assert set(_TERMINAL_STATES).issubset(set(L._terminal_states()))
    assert "error" in L._terminal_states()
    assert "running" not in L._terminal_states() and "loading" not in L._terminal_states()


def test_the_per_host_phase_marker_exists_because_the_shared_one_is_ambiguous():
    """Both arms write to the same `$RESULT_S3`, so `phase.txt` is a single file they overwrite in turn."""
    assert 'phase-${CONTAINER_ID:-unknown}.txt' in L._COFOLD_PIPELINE
    body = SRC[SRC.index("def _host_phase"):SRC.index("def mode_reap")]
    assert "phase-%s.txt" in body and 'instance=%s' in body


# =============================================================================================================
# ★★ THE CCD CACHE — a truncated download used as if it were complete (measured 2026-08-01)
# =============================================================================================================
# `ValueError: CCD component CYS not found!` killed all six smarca4 seeds in ~7 s each while smarca2's six
# landed. CYS is a canonical amino acid, so this was never a science or a host problem: it was an incomplete
# ~3 GB pull that nothing checked before inference started.
def test_the_ccd_cache_is_verified_by_BOLTZ_OWN_predicate_not_a_re_typed_token_list():
    """A re-spelled set of required components could drift from the one `load_canonicals` actually demands
    and would then certify a cache that still dies. The check calls the failing function itself."""
    import selcal_cofold_run as CR
    src = open(os.path.join(HERE, "selcal_cofold_run.py")).read()
    assert "from boltz.data.mol import load_canonicals" in src
    body = src[src.index("def ccd_cache_integrity"):src.index("def _missing_canonicals")]
    assert "load_canonicals(mol_dir)" in body
    assert callable(CR.ccd_cache_integrity)


def test_an_absent_mols_dir_is_NOT_ok(tmp_path):
    import selcal_cofold_run as CR
    ok, detail = CR.ccd_cache_integrity(str(tmp_path))
    assert ok is False
    assert detail["mol_dir_exists"] is False and detail["why"]


def test_a_cache_that_cannot_be_ASKED_about_is_not_a_clean_cache(tmp_path):
    """Not being able to import Boltz is an ABSENT reading. The expensive mistake is certifying a short cache,
    so the integrity check never returns ok on a cache it could not examine."""
    import selcal_cofold_run as CR
    (tmp_path / "mols").mkdir()
    ok, detail = CR.ccd_cache_integrity(str(tmp_path))     # boltz is not installed in CI
    assert ok is False
    assert detail["state"] in ("unverifiable", "cold", "truncated")


def test_COLD_is_not_TRUNCATED_and_only_TRUNCATED_may_refuse_a_run(tmp_path, monkeypatch):
    """⛔ CONFLATING THEM WOULD BREAK THE VERY FIRST RUN. A cache with no populated `mols/` has simply never
    been fetched — Boltz pulls it lazily inside `predict`, which is the normal cold path and is how this guard
    bootstraps its own S3 cache. The MEASURED failure is the other one: a directory that EXISTS and is SHORT,
    which Boltz never repairs because it only downloads what it thinks is absent."""
    import pytest
    import selcal_cofold_run as CR
    monkeypatch.setattr(CR, "_s3_sync", lambda *a, **k: True)
    # cold -> proceeds
    monkeypatch.setattr(CR, "repair_ccd_cache", lambda c: (False, {"state": "cold", "why": "never fetched"}))
    assert CR.preflight_ccd(str(tmp_path), cache_s3=None)["state"] == "cold"
    # truncated -> refuses
    monkeypatch.setattr(CR, "repair_ccd_cache",
                        lambda c: (False, {"state": "truncated", "why": "CCD component CYS not found!"}))
    with pytest.raises(SystemExit) as e:
        CR.preflight_ccd(str(tmp_path), cache_s3=None)
    assert "re-pull, never a run" in str(e.value)


def test_a_cold_cache_is_never_BANKED_either(tmp_path, monkeypatch):
    """A cache is uploaded because it VERIFIED, never because it is present — a cold or short one banked to
    the shared prefix would poison every future host of this lane."""
    import selcal_cofold_run as CR
    calls = []
    monkeypatch.setattr(CR, "_s3_sync", lambda src, dst, extra=(): calls.append((src, dst)) or True)
    monkeypatch.setattr(CR, "repair_ccd_cache", lambda c: (False, {"state": "cold", "why": "never fetched"}))
    CR.preflight_ccd(str(tmp_path), cache_s3="s3://b/cache/")
    assert not [c for c in calls if c[1].startswith("s3://")], "a cold cache must not be banked: %s" % calls
    calls.clear()
    monkeypatch.setattr(CR, "ccd_cache_integrity", lambda c: (False, {"state": "truncated"}))
    CR.bank_ccd_if_verified(str(tmp_path), "s3://b/cache/")
    assert not calls, "the post-run bank must be gated on verification too"
    monkeypatch.setattr(CR, "ccd_cache_integrity", lambda c: (True, {"state": "ok"}))
    CR.bank_ccd_if_verified(str(tmp_path), "s3://b/cache/")
    assert calls == [(str(tmp_path), "s3://b/cache/")]


def test_the_repair_PURGES_rather_than_asking_again(tmp_path):
    """⛔ Boltz only downloads what it thinks is absent, so a short directory is never fixed by re-asking —
    it stays short forever. That is why the smarca4 host failed identically on its 11:22 AM ET restart."""
    import selcal_cofold_run as CR
    mols = tmp_path / "mols"
    mols.mkdir()
    (mols / "ALA.pkl").write_text("x")
    CR.repair_ccd_cache(str(tmp_path))
    assert not (mols / "ALA.pkl").exists(), "the short mols/ must be purged, not topped up"


def test_a_still_short_cache_REFUSES_TO_RUN_rather_than_burning_six_seeds(tmp_path, monkeypatch):
    """Six seeds failing at ~7 s each, silently, is strictly worse than one loud refusal before the first
    prediction. This is the arm that returned rc=1 with no models and no explanation."""
    import pytest
    import selcal_cofold_run as CR
    monkeypatch.setattr(CR, "repair_ccd_cache",
                        lambda c: (False, {"state": "truncated", "why": "CCD component CYS not found!"}))
    with pytest.raises(SystemExit) as e:
        CR.preflight_ccd(str(tmp_path), cache_s3=None)
    assert "re-pull, never a run" in str(e.value)


def test_the_cache_is_only_BANKED_to_S3_AFTER_the_check_passes(tmp_path, monkeypatch):
    """⚠ THE WHOLE SAFETY ARGUMENT. Uploading a truncated local cache to the shared prefix would poison every
    future host of this lane — turning a one-host accident into a permanent property of the prefix."""
    import pytest
    import selcal_cofold_run as CR
    calls = []
    monkeypatch.setattr(CR, "_s3_sync", lambda src, dst, extra=(): calls.append((src, dst)) or True)
    monkeypatch.setattr(CR, "repair_ccd_cache",
                        lambda c: (False, {"state": "truncated", "why": "CCD component CYS not found!"}))
    with pytest.raises(SystemExit):
        CR.preflight_ccd(str(tmp_path), cache_s3="s3://b/cache/")
    uploads = [c for c in calls if c[1].startswith("s3://")]
    assert not uploads, "a SHORT cache must never be uploaded: %s" % uploads
    assert calls and calls[0][0] == "s3://b/cache/", "the restore must still have been attempted first"
    calls.clear()
    monkeypatch.setattr(CR, "ccd_cache_integrity", lambda c: (True, {"why": ""}))
    CR.preflight_ccd(str(tmp_path), cache_s3="s3://b/cache/")
    assert [c[1] for c in calls] == [str(tmp_path), "s3://b/cache/"], "restore, verify, THEN bank"


def test_the_boltz_cache_lives_outside_the_run_prefix_and_is_keyed_on_the_spec():
    """The co-fold prefix is deliberately FRESH per design freeze; a cache inside it would re-pull ~3 GB on
    every host of every future panel, during exactly the window three of four hosts have died in."""
    from nrv04_vast_launch import BOLTZ_SPEC
    uri = L.boltz_cache_s3("bkt")
    assert uri.startswith("s3://bkt/selcal-boltz-cache/")
    assert SP.COFOLD_PREFIX not in uri
    assert L.boltz_cache_s3("bkt", "boltz==9.9.9") != uri, "a different Boltz must not share a cache layout"
    assert BOLTZ_SPEC


def test_the_cofold_jobspec_hands_the_host_an_explicit_cache_and_its_S3_home():
    """With the default `~/.boltz` the location depends on `$HOME` inside the container, so a check could
    verify a different directory than Boltz reads."""
    spec = L.build_cofold_jobspec("main", "bkt")
    assert spec.env["BOLTZ_CACHE_S3"] == L.boltz_cache_s3("bkt")
    assert "export BOLTZ_CACHE=" in L._COFOLD_PIPELINE
    src = open(os.path.join(HERE, "selcal_cofold_run.py")).read()
    assert '"--cache", cache_dir' in src, "the verified directory must be the one boltz is told to use"


def test_a_RENTAL_arms_its_own_supervisor():
    """★★ A rental is born unsupervised unless something arms the watch, and on 2026-08-01 nothing did: two
    co-fold hosts rented at 10:10 AM ET, the lane's census silent from 11:04 AM ET, and the first thing to
    notice the two idle boxes was an ACCOUNT-level alarm at 12:04 PM ET. It is the WATCH that is armed
    automatically, never the purchase — `self_dispatch`'s rule that a renting rung stays a deliberate
    dispatch is intact, because `cofold_watch`/`watch` rent nothing and reap on every tick."""
    for fn, mode, warn in (("mode_cofold(", "cofold_watch", "SELCAL CO-FOLD UNSUPERVISED"),
                           ("mode_launch", "watch", "SELCAL LEGS UNSUPERVISED")):
        body = SRC[SRC.index("def %s" % fn):]
        body = body[:body.index("\ndef ", 10)]
        assert 'self_dispatch("%s")' % mode in body, "%s must arm its supervisor" % fn
        assert warn in body, "a failed arm must be LOUD — the hosts are already billing"


def test_a_host_only_TOUCHES_its_own_arms_outputs():
    """⛔ smarca2's six models are BANKED and preregistered inputs of every MD leg. A host restoring the whole
    prefix pulls them down, gives them fresh local mtimes, and its continuous sync re-uploads them — churning
    a validated set this rental was never asked to touch. `SELCAL_SYSTEMS` scopes what a host COMPUTES; this
    scopes what it TOUCHES."""
    p = L._COFOLD_PIPELINE
    assert "_SYNC_ARGS+=(--include \"$_s/*\")" in p
    assert p.count('"${_SYNC_ARGS[@]}"') == 3, "restore + continuous upload + final upload must all be scoped"
    i_build = p.index("_SYNC_ARGS=(")
    assert i_build < p.index('s3 sync "$RESULT_S3/" "$OUTPUT_DIR/"'), "scope must be built before the restore"
    src = open(os.path.join(HERE, "selcal_cofold_run.py")).read()
    assert 'cofold-provenance-%s.json' in src, "both arms share $RESULT_S3; provenance must not collide"


def test_the_preflight_runs_BEFORE_the_first_prediction():
    import ast
    src = open(os.path.join(HERE, "selcal_cofold_run.py")).read()
    fn = [n for n in ast.walk(ast.parse(src))
          if isinstance(n, ast.FunctionDef) and n.name == "main"][0]
    dumps = [ast.dump(s) for s in fn.body]
    i_pre = next(i for i, s in enumerate(dumps) if "preflight_ccd" in s)
    i_loop = next(i for i, s in enumerate(dumps) if s.startswith("For("))
    assert i_pre < i_loop, "the CCD preflight must precede the prediction loop, not run inside it"


def test_the_supervisor_re_arms_rather_than_leaving_hosts_unwatched():
    """A watch has a finite window; when it ends the hosts do NOT stop, because a host cannot end its own
    billing — only the control plane can. A watch that simply exits therefore converts a supervised fleet
    into an unsupervised one at a predictable moment."""
    body = SRC[SRC.index("def mode_cofold_watch"):SRC.index("def mode_watch")]
    assert 'self_dispatch("cofold_watch"' in body
    assert "SELCAL SUPERVISION NOT RE-ARMED" in body, \
        "a failed re-arm must be LOUD — a silent one is the unattended-rental leak with extra steps"
    assert 'self_dispatch("stage_test")' in body, "on completion the ladder must advance to the $0 rung"


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ★★ THE WATCH'S EXIT PATHS, EXECUTED — not read (2026-08-01)
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# The test directly above asserts the re-arm exists IN THE SOURCE, and it passed all day while a billing host
# went unwatched — because `self_dispatch("cofold_watch"` really was in the text, on the window-elapsed path,
# while a DIFFERENT path returned 1 without it. A source-text assertion cannot tell two paths apart, and
# believing it is the same mistake as believing the docstring (CLAUDE.md §4: a populated field is not a
# measured one; here, a present string is not an executed branch). So these RUN the loop.
def _watch_env(monkeypatch, *, complete, hosts, readable=True, ticks=1):
    """Drive `mode_cofold_watch` for `ticks` iterations against a scripted control plane. Returns the log."""
    import types
    calls = {"dispatch": [], "reap": [], "log": []}
    seen = {"n": 0}

    class _S3:
        def list_objects_v2(self, **_kw):
            return {"Contents": []}
    monkeypatch.setitem(sys.modules, "boto3", types.SimpleNamespace(client=lambda _n: _S3()))
    monkeypatch.setattr(L, "_cofold_census",
                        lambda *_a, **_k: {"complete": complete, "n_models_per_arm": {}, "per_arm": {}})
    monkeypatch.setattr(L, "mode_reap", lambda *a, **k: calls["reap"].append(k) or 0)
    monkeypatch.setattr(L, "_write", lambda *a, **k: None)
    monkeypatch.setattr(L, "_tick_publish", lambda *a, **k: True)
    monkeypatch.setattr(L, "self_dispatch", lambda m, i=None, **k: calls["dispatch"].append(m) or True)
    monkeypatch.setattr(L, "rental_uptime_s", lambda _i: 60.0)

    def _checked(_key=None):
        seen["n"] += 1
        h = hosts(seen["n"]) if callable(hosts) else hosts
        r = readable(seen["n"]) if callable(readable) else readable
        return r, {}, list(h)
    monkeypatch.setattr(L, "_live_labels_checked", _checked)
    monkeypatch.setattr(L.time, "sleep", lambda _s: None)
    real_print = print
    monkeypatch.setattr("builtins.print", lambda *a, **k: calls["log"].append(" ".join(str(x) for x in a)))
    try:
        rc = L.mode_cofold_watch(bucket="b", minutes=ticks * 0.05, cofold_prefix="p")
    finally:
        monkeypatch.setattr("builtins.print", real_print)
    calls["rc"] = rc
    return calls


def test_control_an_UNREADABLE_host_board_never_ends_a_watch(monkeypatch):
    """⛔ THE §4 BUG. `mine` is empty when the API FAILS as well as when nothing is billing. The old code
    exited — with no re-arm — on the first empty list, so ONE Vast blip retired supervision of a host that
    was still on the meter. An absent reading is not a reading of absence."""
    monkeypatch.setenv("SELCAL_WATCH_GRACE_S", "0")
    c = _watch_env(monkeypatch, complete=False, hosts=[], readable=False, ticks=3)
    assert not any("no co-fold host is alive on two consecutive" in l for l in c["log"])
    assert any("UNREADABLE, not empty" in l for l in c["log"])
    # and when the window ends blind, it re-arms rather than exiting on a board it could not read
    assert "cofold_watch" in c["dispatch"]


def test_control_a_single_no_host_reading_is_a_strike_not_a_verdict(monkeypatch):
    """The race the brief named: `mode_cofold` dispatches this watch the moment it submits, so the first
    looks can legitimately precede the instance appearing. One observation must not end supervision."""
    monkeypatch.setenv("SELCAL_WATCH_GRACE_S", "0")
    c = _watch_env(monkeypatch, complete=False, hosts=lambda n: [] if n == 1 else [{"id": 1}], ticks=3)
    assert any("one strike, not a verdict" in l for l in c["log"])
    assert c["rc"] == 0  # never took the early exit


def test_control_a_repeated_readable_absence_does_end_the_watch(monkeypatch):
    """The guard must still FIRE when it should — a watch that can never exit is its own bug, and with no
    host there is nothing left unwatched."""
    monkeypatch.setenv("SELCAL_WATCH_GRACE_S", "0")
    c = _watch_env(monkeypatch, complete=False, hosts=[], readable=True, ticks=4)
    assert c["rc"] == 1
    assert any("two consecutive READABLE checks" in l for l in c["log"])


def test_control_the_grace_window_covers_the_rental_race(monkeypatch):
    """Inside the grace window a missing host is never even a strike, however many ticks pass."""
    monkeypatch.setenv("SELCAL_WATCH_GRACE_S", "9999")
    c = _watch_env(monkeypatch, complete=False, hosts=[], readable=True, ticks=4)
    assert c["rc"] == 0 and not any("two consecutive READABLE" in l for l in c["log"])


def test_control_completion_with_a_SURVIVING_host_re_arms(monkeypatch):
    """The happy path is the dangerous one: it is taken on every successful panel, and it exits. If the
    stop_all reap did not actually destroy the box, supervision would end on top of a billing host."""
    c = _watch_env(monkeypatch, complete=True, hosts=[{"id": 46524315}], ticks=1)
    assert c["rc"] == 0
    assert "cofold_watch" in c["dispatch"], "a surviving host must keep a supervisor"
    assert "stage_test" in c["dispatch"]


def test_control_completion_with_a_CLEAN_reap_does_not_re_arm(monkeypatch):
    """...and the negative control for it: when the hosts really are gone, a second watch is pure noise and
    a duplicate supervisor is its own hazard."""
    c = _watch_env(monkeypatch, complete=True, hosts=[], ticks=1)
    assert c["rc"] == 0
    assert c["dispatch"] == ["stage_test"], "nothing is billing — exactly one $0 rung should be armed"


def test_live_labels_reports_readability_without_changing_its_callers(monkeypatch):
    """The 2-tuple spelling stays for the launchers (which only ever SKIP on a live host and are unharmed by
    the conflation); only the supervision loop needs the third value."""
    monkeypatch.setattr(L, "_vast_request", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    ok, live, mine = L._live_labels_checked("k")
    assert ok is False and live == {} and mine == []
    assert L._live_labels("k") == ({}, [])
    monkeypatch.setattr(L, "_vast_request",
                        lambda *a, **k: {"instances": [{"label": SP.LABEL_PREFIX + "x",
                                                        "actual_status": "running"}]})
    ok, live, mine = L._live_labels_checked("k")
    assert ok is True and len(mine) == 1


def test_a_container_written_artifact_cannot_lock_the_commit_step_out():
    """⛔ MEASURED, runs 30712764070 / 30712792573 (2026-08-01). `stage_test` runs in the `ternary-fep`
    container, which writes into the bind-mounted `research/modalities` as ROOT; the commit step runs as
    `runner` and died on `cp: cannot create regular file 'research/modalities/selcal-stage-test.json':
    Permission denied`. Under `set -e` that failed the whole step, so the $0 staging shakeout that gates the
    first MD rental could never bank its result — and once that file is TRACKED, `git reset --hard` fails on
    it before the cp is even reached. The normalisation must therefore come FIRST, and must not be able to
    fail the step it protects."""
    wf = open(WORKFLOW).read()
    blocks = wf.split('name: Commit whatever landed')[1:]
    assert len(blocks) == 2, "both the cpu and gpu commit steps must be covered"
    for b in blocks:
        head = b.split('publish_artifacts.sh')[0]
        assert "chown -R" in head, "ownership is not normalised before the commit step touches the files"
        assert "|| true" in head, "the normalisation must not be able to fail the step it protects"
        # ⚠ THE ORDERING IS THE WHOLE POINT and survives the move to the primitive unchanged: the publish
        # resets the working tree, and `git reset --hard` fails on a root-owned TRACKED file before any
        # copy-back is reached. So the chown must precede the publish call, not merely precede the copy.
        assert head.index("chown") < len(head), "chown must precede the publish"
