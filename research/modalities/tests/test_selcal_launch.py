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
WORKFLOW = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                        ".github", "workflows", "selectivity-control-vast.yml")


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


def test_the_ledger_records_duration_and_rate_not_just_an_id():
    assert '"dph_total"' in SRC and '"duration_s"' in SRC and '"billed_usd"' in SRC


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
    still land on the figure the options paper authorised for D1/D2."""
    c = L.ladder_cost()
    assert c["n_units"] == 24
    assert abs(c["plan_usd"] - 3.79) < 0.01
    assert abs(c["range_usd"][0] - 1.57) < 0.01 and abs(c["range_usd"][1] - 9.54) < 0.01


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
    wf = open(WORKFLOW).read()
    assert "git commit --allow-empty" in wf
    # COMMENTS ARE STRIPPED FIRST. The workflow DOCUMENTS this landmine in a comment, and a naive substring
    # check would fail on the warning against the very thing it is warning about — a test that forbids
    # writing down why the rule exists.
    executable = "\n".join(ln for ln in wf.splitlines() if not ln.strip().startswith("#"))
    assert "diff --cached --quiet" not in executable


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
