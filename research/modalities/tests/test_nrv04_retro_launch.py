#!/usr/bin/env python3
"""Offline tests for the NR-V04 retrospective Vast lane (pure JobSpec construction — no Vast, no S3, no GPU).

The load-bearing thing these pin is that a retrospective leg starts from the co-fold model its unit name says
it does. The co-fold model is the unit of independence in the frozen statistics (prereg §4a), so a leg that
globbed a system directory instead of a pinned model prefix would quietly corrupt the model-level means the
verdict is computed from — and nothing downstream would notice.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nrv04_retro_panel as retro       # noqa: E402
import nrv04_vast_launch as launch      # noqa: E402

BUCKET = "test-bucket"


def _spec(arm_id="retro_noncov_nr4a2", model=2, replica=1):
    return launch.build_retro_jobspec(retro.arm_by_id(arm_id), model, replica, "run", "br", BUCKET)


def test_cofold_prefix_is_pinned_to_the_units_model_seed():
    spec = _spec(model=3)
    assert spec.env["COFOLD_PREFIX_S3"] == f"s3://{BUCKET}/{retro.COFOLD_PREFIX}/nr4a2/seed_3/"
    assert spec.env["COFOLD_MODEL_SEED"] == "3"
    assert "-m3-" in spec.name, "the unit name must agree with the model prefix it stages from"


def test_every_authorized_unit_gets_a_distinct_checkpoint_and_result_prefix():
    specs = [launch.build_retro_jobspec(a, m, r, "run", "br", BUCKET) for a, m, r in retro.enumerate_units()]
    assert len(specs) == 24
    assert len({s.checkpoint_uri for s in specs}) == 24, "two units sharing a checkpoint would race"
    assert len({s.env["RESULT_S3"] for s in specs}) == 24


def test_retro_results_do_not_collide_with_the_feasibility_panels_prefix():
    """The feasibility panel's results are a cross-check, not part of this panel — they must not be collected
    into it by a shared prefix."""
    assert launch.RETRO_RESULT_PREFIX != launch.RESULT_PREFIX
    assert _spec().env["RESULT_S3"].startswith(f"s3://{BUCKET}/{launch.RETRO_RESULT_PREFIX}/")


def test_staging_patch_applied_and_pins_exactly_one_cif():
    assert launch._RETRO_PIPELINE != launch._PIPELINE
    assert "assemble_unit" in launch._RETRO_PIPELINE
    assert "leg_by_id" not in launch._RETRO_PIPELINE, "retro units carry no covalent-panel Leg"
    assert "wc -l" in launch._RETRO_PIPELINE, "a second CIF under the pinned prefix must fail, never be guessed"


def test_covalent_flags_only_on_the_nr4a1_arm():
    cov = _spec("retro_cov_nr4a1", 1, 0)
    assert cov.env["COVALENT"] == "1" and cov.env["COV_RESNUM"] == "551"
    for arm_id in ("retro_noncov_nr4a1", "retro_noncov_nr4a2", "retro_noncov_nr4a3"):
        assert _spec(arm_id, 1, 0).env["COVALENT"] == "0"


def test_specs_are_spot_safe_and_resumable():
    spec = _spec()
    assert spec.resources.interruptible is True
    assert spec.resume is True, "a preempted leg must resume from its checkpoint, not restart"
    assert spec.checkpoint_uri


def test_pilot_is_a_paralogue_leg_not_nr4a1(monkeypatch):
    """The pilot's abort information is structural: the assembler has never read an NR4A2/NR4A3 co-fold.
    Piloting NR4A1 would leave the only real staging risk unexercised."""
    monkeypatch.setenv("RETRO_PILOT_ONLY", "1")
    monkeypatch.delenv("RETRO_PILOT_ARM", raising=False)
    units = launch.retro_units_to_run()
    assert len(units) == 1
    arm, model, replica = units[0]
    assert arm.target in ("NR4A2", "NR4A3") and not arm.covalent


def test_full_fanout_is_the_whole_authorized_panel(monkeypatch):
    monkeypatch.setenv("RETRO_PILOT_ONLY", "0")
    assert len(launch.retro_units_to_run()) == 24


def test_arms_differ_only_in_target_and_covalency(monkeypatch):
    """Prereg §2c: identical protocol across arms. The env of two R1 legs at the same model/replica may differ
    only in the fields that identify the arm — any sampling-length or charge drift would be invisible bespoke
    treatment of a paralogue."""
    a = _spec("retro_noncov_nr4a2", 1, 0).env
    b = _spec("retro_noncov_nr4a3", 1, 0).env
    differing = {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
    assert differing <= {"LEG_ID", "TARGET", "ENV_ASSEMBLY", "COFOLD_PREFIX_S3", "RESULT_S3"}
    for shared in ("PROD_NS", "EQUIL_NS", "LIGAND", "COVALENT", "MODE"):
        assert a[shared] == b[shared]


def test_empty_prefix_env_falls_back_instead_of_writing_to_the_bucket_root(monkeypatch):
    """A workflow input that is present-but-empty used to set the prefix to "" via os.environ.get(k, DEFAULT),
    which would send every staged read and every result to the bucket ROOT. `or DEFAULT` is the fix."""
    import importlib
    for var, attr, default in (("NRV04_COFOLD_PREFIX", "COFOLD_PREFIX", "nrv04-covalent-cofold"),
                               ("NRV04_RESULT_PREFIX", "RESULT_PREFIX", "nrv04-covalent-results"),
                               ("NRV04_RETRO_RESULT_PREFIX", "RETRO_RESULT_PREFIX", "nrv04-retro-results")):
        monkeypatch.setenv(var, "")
        mod = importlib.reload(launch)
        assert getattr(mod, attr) == default, f"{var}='' must fall back, not blank the prefix"
        monkeypatch.delenv(var, raising=False)
    importlib.reload(launch)
