"""Behavioral checks for selection and duplicate suppression; synthetic inputs."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import types

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import research_cycle as cycle


def context(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=Test", "-c",
                    "user.email=test@example.invalid", "commit", "-qm", "base", "--allow-empty"], check=True)
    (tmp_path / "input.json").write_text('{"synthetic": true}')
    subprocess.run(["git", "-C", str(tmp_path), "add", "input.json"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=Test", "-c",
                    "user.email=test@example.invalid", "commit", "-qm", "input"], check=True)
    task = {"id": "test", "kind": "science", "resource": "paper:TEST", "ledger_ids": ["AUT-X"],
            "inputs": ["input.json"], "outputs": ["output.json"], "effort_minutes": 20,
            "assessment": {n: {"rating": 2, "basis": "synthetic test judgement"}
                           for n in ("clinical_relevance", "answerability", "validation", "information_gain")}}
    return task, {"entries": [{"id": "AUT-X", "owner": None}]}


def test_verified_work_is_reused_but_changed_input_is_new_work(tmp_path):
    task, ledger = context(tmp_path)
    (tmp_path / "output.json").write_text("{}")
    fp, _ = cycle.fingerprint(tmp_path, task)
    prior = [{"fingerprint": fp, "run_id": "past", "status": "verified",
              "artifact_sha256": {"output.json": cycle.digest(tmp_path / "output.json")}}]
    result = cycle.plan(tmp_path, [task], prior, ledger)
    assert result["selected"] is None
    assert result["duplicate_candidates_suppressed"] == 1
    (tmp_path / "input.json").write_text('{"synthetic": "changed"}')
    import pytest
    with pytest.raises(cycle.runner.Refused, match="differs from HEAD"):
        cycle.plan(tmp_path, [task], prior, ledger)
    subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=Test", "-c",
                    "user.email=test@example.invalid", "commit", "-qam", "changed input"], check=True)
    assert cycle.plan(tmp_path, [task], prior, ledger)["selected"]


def test_changed_completed_artifact_needs_reconciliation_not_redispatch(tmp_path):
    task, ledger = context(tmp_path)
    fp, _ = cycle.fingerprint(tmp_path, task)
    prior = [{"fingerprint": fp, "run_id": "past", "status": "verified",
              "artifact_sha256": {"output.json": "missing"}}]
    result = cycle.plan(tmp_path, [task], prior, ledger)
    assert result["selected"] is None
    assert "reconcile" in result["decisions"][0]["reason"]


def test_failed_same_input_does_not_create_automatic_retry_loop(tmp_path):
    task, ledger = context(tmp_path)
    fp, _ = cycle.fingerprint(tmp_path, task)
    prior = [{"fingerprint": fp, "run_id": "failed", "status": "attempted"}]
    assert cycle.plan(tmp_path, [task], prior, ledger)["selected"] is None
    task["effort_minutes"] = 10
    task["assessment"]["information_gain"]["rating"] = 3
    assert cycle.plan(tmp_path, [task], prior, ledger)["selected"] is None


def test_owner_and_missing_evidence_block_selection(tmp_path):
    task, ledger = context(tmp_path)
    ledger["entries"][0]["owner"] = "another writer"
    assert cycle.plan(tmp_path, [task], [], ledger)["selected"] is None
    ledger["entries"][0]["owner"] = None
    (tmp_path / "input.json").unlink()
    assert cycle.plan(tmp_path, [task], [], ledger)["selected"] is None


def test_maintenance_requires_measurement_and_cannot_displace_science(tmp_path):
    task, ledger = context(tmp_path)
    repair = copy.deepcopy(task)
    repair.update(id="repair", kind="maintenance", effort_minutes=1)
    assert cycle.plan(tmp_path, [repair], [], ledger)["selected"] is None
    repair["observed_friction"] = {"evidence": "input.json", "measurement": "synthetic timing"}
    assert cycle.plan(tmp_path, [repair, task], [], ledger)["selected"]["task_id"] == "test"
    assert cycle.plan(tmp_path, [repair], [{"kind": "maintenance"}], ledger)["selected"] is None


def test_paths_cannot_escape_root(tmp_path):
    import pytest
    with pytest.raises(cycle.runner.Refused):
        cycle.within(tmp_path, "../outside.json")


def collected_context(tmp_path, monkeypatch):
    task, ledger = context(tmp_path)
    selected = cycle.plan(tmp_path, [task], [], ledger)
    selected.update(contract=task, task_sha256="task-digest")
    cache = tmp_path / ".cache"
    cache.mkdir()
    worker = cache / "worker"
    subprocess.run(["git", "-C", str(tmp_path), "worktree", "add", "--detach", str(worker),
                    selected["base_commit"]], check=True, capture_output=True)
    for root in (tmp_path, worker):
        (root / "output.json").write_text('{"synthetic_result": true}')
    log = cache / "check.log"
    log.write_text("Synthetic independent check passed\n")
    receipt = {"run_id": "test-run", "base_commit": selected["base_commit"], "resource": task["resource"],
               "task_sha256": "task-digest", "worktree": str(worker), "status": "completed", "rounds": [],
               "elapsed_seconds": 1.0, "model": "synthetic", "limits": {"max_dispatches": 1}}
    verification = {"run_id": "test-run", "checks": [{"exit_code": 0, "log": str(log),
                       "log_sha256": cycle.digest(log)}],
                    "artifact_sha256": {"output.json": cycle.digest(tmp_path / "output.json")},
                    "next_action": "Synthetic test complete"}
    for name, value in (("plan", selected), ("receipt", receipt), ("verification", verification)):
        (cache / f"{name}.json").write_text(json.dumps(value))
    class Ownership:
        def __init__(self, *args): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def require(self, owner): assert owner == "test-owner"
    monkeypatch.setitem(sys.modules, "local_ownership", types.SimpleNamespace(Coordinator=Ownership))
    return cache, worker


def collect_test(tmp_path, cache):
    return cycle.collect(tmp_path, cache, "test-owner", cache / "plan.json", cache / "receipt.json",
                         cache / "verification.json")


def test_collection_requires_verified_integrated_bytes_and_preserves_logs(tmp_path, monkeypatch):
    cache, worker = collected_context(tmp_path, monkeypatch)
    result = collect_test(tmp_path, cache)
    assert result["status"] == "verified"
    assert (tmp_path / cycle.HISTORY / "test-run/check-1.log").read_bytes() == (cache / "check.log").read_bytes()
    assert cycle.history(tmp_path)[0]["run_id"] == "test-run"


def test_tampered_log_does_not_create_success_or_partial_history(tmp_path, monkeypatch):
    import pytest
    cache, worker = collected_context(tmp_path, monkeypatch)
    (cache / "check.log").write_text("changed")
    with pytest.raises(cycle.runner.Refused, match="hash-matching"):
        collect_test(tmp_path, cache)
    assert cycle.history(tmp_path) == []


def test_worker_scope_and_integrated_output_mismatch_are_refused(tmp_path, monkeypatch):
    import pytest
    cache, worker = collected_context(tmp_path, monkeypatch)
    (worker / "unexpected.txt").write_text("unapproved process edit")
    with pytest.raises(cycle.runner.Refused, match="outside its bounded"):
        collect_test(tmp_path, cache)
    (worker / "unexpected.txt").unlink()
    (tmp_path / "output.json").write_text("different integrated data")
    with pytest.raises(cycle.runner.Refused, match="byte-for-byte"):
        collect_test(tmp_path, cache)


def test_changed_worker_input_cannot_be_attested_as_selected_evidence(tmp_path, monkeypatch):
    import pytest
    cache, worker = collected_context(tmp_path, monkeypatch)
    (worker / "input.json").write_text("different evidence")
    with pytest.raises(cycle.runner.Refused, match="Worker inputs differ"):
        collect_test(tmp_path, cache)
