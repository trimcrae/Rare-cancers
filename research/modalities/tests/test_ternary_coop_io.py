"""Unit tests for ternary_coop_io.py — the retained integration boundary (reviewer 2026-07-12, Plan B).

Verifies the schemas/lock/hashes/artifact-manifest, the sign-unit invariant, the mocked end-to-end artifact
validation, and — critically — that a STUB GPU-hour/cost FAILS in execution mode. No MD/GPU."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ternary_coop_io as io  # noqa: E402


def test_schemas_versioned():
    assert io.input_schema()["schema_version"] == io.SCHEMA_VERSION
    assert io.output_schema()["schema_version"] == io.SCHEMA_VERSION


def test_system_hash_deterministic_and_env_sensitive():
    import ternary_coop_prep as prep
    a = prep.assemble_pilot()
    h = {x["leg_id"]: io.system_hash(x) for x in a}
    # deterministic
    assert io.system_hash(a[0]) == io.system_hash(a[0])
    # binary vs ternary of the same pair hash differently (target component differs)
    assert h["nrv04_active_to_epimer__binary_vhl"] != h["nrv04_active_to_epimer__ternary_nr4a1"]


def test_ligand_hash_distinguishes_endpoints():
    assert io.ligand_hash("CCO", "CCN") != io.ligand_hash("CCN", "CCO")
    assert io.ligand_hash(None, None) == io.ligand_hash(None, None)


def test_mock_result_validates_in_execution_mode():
    assert io.validate_result(io.mock_result_for(), mode="execution")["ok"] is True


def test_stub_gpu_hour_fails_in_execution_mode():
    r = io.mock_result_for()
    r["unit_gpu_h_observed"] = 3.0    # a planning STUB
    out = io.validate_result(r, mode="execution")
    assert out["ok"] is False and any("STUB" in x for x in out["failures"])


def test_missing_artifact_fails():
    r = io.mock_result_for()
    r["artifacts"] = r["artifacts"][:-1]
    assert io.validate_result(r)["ok"] is False


def test_too_few_replicas_fails():
    r = io.mock_result_for()
    r["n_replicas"] = 2
    assert io.validate_result(r)["ok"] is False


def test_unfrozen_lock_fails_execution():
    r = io.mock_result_for()
    r["lock"]["protein_ff"] = None
    out = io.validate_result(r, mode="execution")
    assert out["ok"] is False and any("lock" in x for x in out["failures"])


def test_sign_unit_invariant():
    # implied cooperative alpha but a POSITIVE (unfavorable) ddg_coop -> sign disagreement -> fail
    r = io.mock_result_for()
    r["implied_alpha"] = 20.0        # cooperative => dG_coop should be NEGATIVE
    r["ddg_coop_kcal"] = +1.5        # wrong sign
    out = io.validate_result(r)
    assert out["ok"] is False and any("sign/unit" in x for x in out["failures"])
    r["ddg_coop_kcal"] = -1.5        # correct sign
    assert io.validate_result(r)["ok"] is True


def test_non_execution_mode_allows_stub():
    r = io.mock_result_for()
    r["unit_gpu_h_observed"] = 3.0
    # in plan mode the STUB guard does not apply
    assert io.validate_result(r, mode="plan")["ok"] is True
