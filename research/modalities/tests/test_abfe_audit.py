"""Tests for the hardened ABFE audit (reviewer §7): the direct production-dispatcher regression, the semantic
per-leg checks, and the immutable-manifest pure helpers. All pass WITHOUT boto3/pymbar (synthetic fixtures +
monkeypatch); the S3-touching code is exercised only in CI."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import abfe_audit          # noqa: E402
import abfe_manifest       # noqa: E402
import nr4a3_abfe as abfe  # noqa: E402


# ----------------------------------------------------------------------------------------------------------
# 3. DIRECT DISPATCHER TEST — the key regression. Proves the PRODUCTION run path (run_shard) launches every
#    schedule-defined window, not the frozen N_WINDOWS=12. Runs NO MD: run_window + _prepare_or_load_reference
#    are stubbed, so only the dispatcher's window-iteration logic is exercised.
# ----------------------------------------------------------------------------------------------------------
def _stub_dispatcher(monkeypatch, tmp_path):
    called = []

    def fake_run_window(reference_system, positions, alchemical_atoms, window_index=None, **kw):
        called.append(window_index)
        return 0

    def fake_prepare(out_dir, leg, *a, **k):
        return {"system": object(), "positions": [], "alchemical_atoms": [0],
                "n_receptor_atoms": 0, "n_ligand_atoms": 1, "pose_index": 0}

    monkeypatch.setattr(abfe, "run_window", fake_run_window)
    monkeypatch.setattr(abfe, "_prepare_or_load_reference", fake_prepare)
    return called


def test_dispatcher_runs_all_16_windows_under_dense(monkeypatch, tmp_path):
    called = _stub_dispatcher(monkeypatch, tmp_path)
    monkeypatch.setenv("ABFE_LAMBDA_SCHEDULE", "dense")
    abfe.run_shard("solvent", "lig.sdf", str(tmp_path), window_end=None)
    assert called == list(range(16)), (
        f"dispatcher launched windows {called}; the dense production run MUST iterate all 16 schedule windows, "
        f"not the frozen N_WINDOWS={abfe.N_WINDOWS}")


def test_dispatcher_runs_all_12_windows_under_standard(monkeypatch, tmp_path):
    called = _stub_dispatcher(monkeypatch, tmp_path)
    monkeypatch.delenv("ABFE_LAMBDA_SCHEDULE", raising=False)
    abfe.run_shard("solvent", "lig.sdf", str(tmp_path), window_end=None)
    assert called == list(range(12)), f"standard run must iterate all 12 windows, got {called}"


def test_dispatcher_meta_records_active_schedule_window_count(monkeypatch, tmp_path):
    # the dispatcher also writes meta.n_windows from the ACTIVE schedule (16 under dense) — cross-check.
    import json
    _stub_dispatcher(monkeypatch, tmp_path)
    monkeypatch.setenv("ABFE_LAMBDA_SCHEDULE", "dense")
    abfe.run_shard("solvent", "lig.sdf", str(tmp_path), window_end=None)
    meta = json.load(open(os.path.join(str(tmp_path), "meta.json")))
    assert meta["n_windows"] == 16


# ----------------------------------------------------------------------------------------------------------
# 2. SEMANTIC CHECKS — pure, synthetic inputs (no S3).
# ----------------------------------------------------------------------------------------------------------
def _std_len():
    return len(list(zip(abfe.LAMBDA_ELEC, abfe.LAMBDA_STERICS)))       # 12


def _dense_len():
    return len(list(zip(abfe.LAMBDA_ELEC_DENSE, abfe.LAMBDA_STERICS_DENSE)))   # 16


def test_semantic_ok_on_clean_standard_leg():
    n = _std_len()
    meta = {"leg": "complex", "receptor": "nr4a3", "n_windows": n, "lambda_schedule": "standard"}
    raw = [10] * n
    uniq = [10] * n
    sem = abfe_audit.semantic_checks("nr4a3-abfe/ckpt/complex-nr4a3/nr4a3/complex/",
                                     n_window_files=n, n_contiguous=n, u_length=n,
                                     meta=meta, raw_counts=raw, uniq_counts=uniq)
    assert sem["semantic_ok"] is True
    assert sem["schedule_claimed"] == "standard"
    assert sem["lambda_length_match"] is True
    assert sem["endpoints_ok"] is True
    assert sem["leg_identity_consistent"] is True
    assert sem["target_identity_consistent"] is True
    assert sem["duplication_flagged"] is False


def test_semantic_catches_window_count_vs_schedule_length_mismatch():
    # the 2026-07-11 bug signature: 12 window files but u evaluated at 16 states (dense) → semantic FAIL
    sem = abfe_audit.semantic_checks("nr4a3-abfe/ckpt/complex-nr4a2/nr4a2/complex/",
                                     n_window_files=12, n_contiguous=12, u_length=16,
                                     meta={"leg": "complex", "n_windows": 12},
                                     raw_counts=[5] * 12, uniq_counts=[5] * 12)
    # u_length=16 → inferred 'dense' (len 16); 12 files != 16 → hard mismatch
    assert sem["schedule_claimed"] == "dense"
    assert sem["lambda_length_match"] is False
    assert sem["semantic_ok"] is False
    assert any("!= claimed" in f for f in sem["semantic_findings"])


def test_semantic_verifies_recorded_lambda_value_and_order():
    dense = list(zip(abfe.LAMBDA_ELEC_DENSE, abfe.LAMBDA_STERICS_DENSE))
    n = len(dense)
    good = {"leg": "complex", "receptor": "nr4a2", "n_windows": n, "lambda_schedule": "dense",
            "lambda": [list(x) for x in dense]}
    sem = abfe_audit.semantic_checks("nr4a3-abfe/ckpt/complex-nr4a2/", n, n, n, good, [7] * n, [7] * n)
    assert sem["lambda_value_order_match"] is True and sem["semantic_ok"] is True
    # now scramble the order → must be caught
    bad_order = [list(x) for x in dense]
    bad_order[1], bad_order[2] = bad_order[2], bad_order[1]
    bad = dict(good, **{"lambda": bad_order})
    sem2 = abfe_audit.semantic_checks("nr4a3-abfe/ckpt/complex-nr4a2/", n, n, n, bad, [7] * n, [7] * n)
    assert sem2["lambda_value_order_match"] is False and sem2["semantic_ok"] is False


def test_semantic_flags_sample_duplication_dedup_ratio():
    n = _std_len()
    meta = {"leg": "solvent", "n_windows": n, "lambda_schedule": "standard"}
    raw = [20] * n
    uniq = [10] * n            # 2.0 dedup ratio → duplicated records (checkpoint/resume) → flag
    sem = abfe_audit.semantic_checks("nr4a3-abfe/ckpt/solvent/", n, n, n, meta, raw, uniq)
    assert sem["duplication_flagged"] is True
    assert sem["max_dedup_ratio"] == 2.0
    assert sem["semantic_ok"] is False


def test_semantic_flags_leg_and_target_mismatch():
    n = _std_len()
    # meta says complex/nr4a1 but the path says solvent — hard identity contradiction
    meta = {"leg": "complex", "receptor": "nr4a1", "n_windows": n, "lambda_schedule": "standard"}
    sem = abfe_audit.semantic_checks("nr4a3-abfe/ckpt/solvent/", n, n, n, meta, [5] * n, [5] * n)
    assert sem["leg_identity_consistent"] is False
    assert sem["semantic_ok"] is False


def test_semantic_missing_metadata_is_warning_not_hard_fail():
    # a real current-format leg: meta lacks schedule name + per-window λ + target. Those are WARNINGS (recorded
    # in findings) but do NOT by themselves fail the leg (only a definite contradiction does).
    n = _std_len()
    meta = {"leg": "solvent", "n_windows": n}                       # no lambda_schedule / lambda / receptor
    sem = abfe_audit.semantic_checks("nr4a3-abfe/ckpt/solvent/", n, n, n, meta, [8] * n, [8] * n)
    assert sem["schedule_source"] == "inferred-from-window-count"
    assert sem["lambda_value_order_match"] is None                 # not recorded → not verifiable
    assert sem["target_identity_present"] is False
    assert sem["semantic_ok"] is True                              # no hard contradiction
    assert any("not recorded" in f for f in sem["semantic_findings"])


def test_semantic_endpoints_flag_for_unknown_schedule():
    # a window count matching neither 12 nor 16 → unknown schedule → can't confirm endpoints, semantic_ok True
    # (no contradiction) but a finding is recorded.
    sem = abfe_audit.semantic_checks("nr4a3-abfe/ckpt/complex-nr4a3/", 9, 9, 9, {"leg": "complex"},
                                     [3] * 9, [3] * 9)
    assert sem["schedule_claimed"] == "unknown"
    assert sem["endpoints_ok"] is None
    assert any("neither standard" in f for f in sem["semantic_findings"])


def test_prefix_token_helpers():
    assert abfe_audit._leg_token_from_prefix("nr4a3-abfe/ckpt/complex-nr4a2/nr4a2/complex/") == "complex"
    assert abfe_audit._leg_token_from_prefix("nr4a3-abfe/ckpt/solvent/") == "solvent"
    assert abfe_audit._target_token_from_prefix("nr4a3-abfe/ckpt/complex-nr4a2/nr4a2/complex/") == "nr4a2"
    assert abfe_audit._target_token_from_prefix("nr4a3-abfe/ckpt/solvent/") is None


# ----------------------------------------------------------------------------------------------------------
# 4. MANIFEST — pure hashing / merge helpers (no boto3), synthetic bytes.
# ----------------------------------------------------------------------------------------------------------
def test_sha256_bytes_and_stream_agree():
    import hashlib
    data = b"the quick brown fox" * 100
    assert abfe_manifest.sha256_bytes(data) == hashlib.sha256(data).hexdigest()
    # streaming in arbitrary chunks yields the same digest + correct total size
    chunks = [data[i:i + 7] for i in range(0, len(data), 7)]
    digest, size = abfe_manifest.sha256_stream(chunks)
    assert digest == hashlib.sha256(data).hexdigest()
    assert size == len(data)


def test_sha256_stream_skips_empty_chunks():
    import hashlib
    parts = [b"abc", b"", b"def", b""]
    digest, size = abfe_manifest.sha256_stream(parts)
    assert digest == hashlib.sha256(b"abcdef").hexdigest()
    assert size == 6


def test_merge_leg_records_order_independent_fingerprint():
    r1 = {"key": "leg/window_00.jsonl", "version_id": "v1", "sha256": "aaa", "size": 3}
    r2 = {"key": "leg/window_01.jsonl", "version_id": "v2", "sha256": "bbb", "size": 3}
    a = abfe_manifest.merge_leg_records([r1, r2])
    b = abfe_manifest.merge_leg_records([r2, r1])
    assert a["content_fingerprint"] == b["content_fingerprint"]     # listing order must not matter
    assert a["n_objects"] == 2
    assert a["versioning_disabled"] is False


def test_merge_leg_records_flags_disabled_versioning():
    recs = [{"key": "leg/meta.json", "version_id": "null", "sha256": "ccc", "size": 5},
            {"key": "leg/window_00.jsonl", "version_id": "v9", "sha256": "ddd", "size": 5}]
    merged = abfe_manifest.merge_leg_records(recs)
    assert merged["versioning_disabled"] is True


def test_build_manifest_doc_placeholders_are_explicit_todos():
    legs = {"nr4a3-abfe/ckpt/solvent/": {"n_objects": 1, "content_fingerprint": "x",
                                         "versioning_disabled": False, "objects": [],
                                         "provenance": {"leg": "solvent"}}}
    doc = abfe_manifest.build_manifest_doc("sagemaker-us-east-2-123", legs)
    ph = doc["runtime_provenance_placeholders"]
    # every runtime-only field is an explicit TODO, never a fabricated value
    assert all(str(v).startswith("TODO") for v in ph.values())
    assert "forcefield_versions" in ph and "container_image_digest" in ph
    assert doc["versioning_disabled_anywhere"] is False
    assert doc["schema"] == "abfe-manifest/v1"


def test_leg_provenance_reads_meta_and_placeholders_ancestry():
    prov = abfe_manifest._leg_provenance({"leg": "complex", "receptor": "nr4a2", "seed": 1,
                                          "n_windows": 16, "lambda_schedule": "dense"})
    assert prov["leg"] == "complex" and prov["receptor"] == "nr4a2" and prov["n_windows"] == 16
    assert str(prov["checkpoint_ancestry"]).startswith("TODO")      # not recorded → explicit placeholder
    assert prov["meta_present"] is True
