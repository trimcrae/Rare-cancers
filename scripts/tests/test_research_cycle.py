"""Behavioral checks for selection and duplicate suppression; synthetic inputs."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import types

import pytest

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


def planned_context(tmp_path):
    task, ledger = context(tmp_path)
    task.update(question="Synthetic bounded question", instructions="Use synthetic input only",
                stop_condition="One synthetic output")
    folder = tmp_path / "research/autonomy"
    folder.mkdir(parents=True)
    cycle.runner.write_json(tmp_path / cycle.CONTRACTS, {"tasks": [task]})
    cycle.runner.write_json(folder / "research-ledger.json", ledger)
    cycle.runner.write_json(folder / "codex-handover.json", {"legacy_driver": {"status": "disabled"}})
    (tmp_path / cycle.runner.PROTOCOL).write_text("Synthetic local test; no real model dispatch.\n")
    (tmp_path / ".gitignore").write_text(".cache/\n")
    cycle.runner.git(tmp_path, "add", ".gitignore", "research/autonomy")
    cycle.runner.git(tmp_path, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                     "commit", "-qm", "Synthetic cycle contract")
    destination = tmp_path / ".cache/research-cycle"
    selection = cycle.write_plan(tmp_path, destination)
    return task, destination, selection


def attempted_history(root, selection, status="attempted"):
    folder = root / cycle.HISTORY / "previous"
    folder.mkdir(parents=True)
    cycle.runner.write_json(folder / "cycle.json", {
        "run_id": "previous", "fingerprint": selection["selected"]["fingerprint"],
        "status": status, "artifact_sha256": {}})


def test_no_work_plan_removes_previous_dispatch_files(tmp_path):
    _, destination, selection = planned_context(tmp_path)
    attempted_history(tmp_path, selection)
    assert cycle.write_plan(tmp_path, destination)["selected"] is None
    assert not (destination / "task.txt").exists()
    assert not (destination / "contract.json").exists()
    assert cycle.read(destination / "plan.json")["duplicate_candidates_suppressed"] == 1


@pytest.mark.parametrize("stale", ["verified", "attempted", "base", "prompt", "unbound"])
def test_copied_cycle_dispatch_is_rechecked_before_auth(tmp_path, monkeypatch, stale):
    task, destination, selection = planned_context(tmp_path)
    contract = cycle.read(destination / "contract.json")
    task_text = (destination / "task.txt").read_text(encoding="utf-8")
    if stale in ("verified", "attempted"):
        attempted_history(tmp_path, selection, stale)
        expected = "Reuse|attempted"
    elif stale == "base":
        cycle.runner.git(tmp_path, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                         "commit", "-qm", "unrelated new base", "--allow-empty")
        expected = "plan.*changed|changed.*plan"
    elif stale == "prompt":
        task_text += "\nUnplanned work"
        expected = "prompt|task text"
    else:
        contract.pop("cycle_plan", None)
        expected = "plan"
    cache = cycle.runner.repository(tmp_path)[1]
    with cycle.runner.Coordinator(tmp_path, cache) as ownership:
        ownership.claim("test-owner", "Synthetic isolated fixture")
    monkeypatch.setattr(cycle.runner, "probe_auth", lambda *a: pytest.fail("Authentication reached"))
    with pytest.raises(cycle.runner.Refused, match=expected):
        cycle.runner.launch(tmp_path, cache, "synthetic", cycle.runner.DEFAULTS,
                            task_text, task["resource"], {}, coordinator_id="test-owner",
                            task_contract=contract)
    assert not list(cache.glob("*/receipt.json"))


@pytest.mark.parametrize("failure", ["missing_worktree", "changed_input", "outside_scope", "completed_failed_check"])
def test_failed_worker_is_preserved_as_attempted_without_claiming_valid_output(tmp_path, monkeypatch, failure):
    cache, worker = collected_context(tmp_path, monkeypatch)
    receipt = cycle.read(cache / "receipt.json")
    receipt.update(status="failed", error="Synthetic execution failure")
    if failure == "missing_worktree":
        receipt["worktree"] = str(cache / "never-created")
    elif failure == "changed_input":
        (worker / "input.json").write_text("Synthetic invalid evidence")
    else:
        (worker / "unexpected.txt").write_text("Synthetic disallowed partial output")
    cycle.runner.write_json(cache / "receipt.json", receipt)
    verification = {"run_id": receipt["run_id"], "checks": [],
                    "next_action": "Reconcile retained synthetic failure before another dispatch"}
    if failure == "completed_failed_check":
        receipt["status"] = "completed"
        cycle.runner.write_json(cache / "receipt.json", receipt)
        log = cache / "check.log"
        log.write_text("Synthetic verification rejected unexpected worker output\n")
        verification["checks"] = [{"exit_code": 1, "log": str(log), "log_sha256": cycle.digest(log)}]
    cycle.runner.write_json(cache / "verification.json", verification)
    result = collect_test(tmp_path, cache)
    assert result["status"] == "attempted"
    assert result["artifact_sha256"] == {}
    assert result["time_to_verified_output_seconds"] is None
    assert result["worker_integrity_issues"]
    preserved = tmp_path / cycle.HISTORY / receipt["run_id"]
    assert cycle.read(preserved / "runner-receipt.json") == receipt
    task = cycle.read(cache / "plan.json")["contract"]
    assert cycle.plan(tmp_path, [task], cycle.history(tmp_path),
                      {"entries": [{"id": "AUT-X", "owner": None}]})["selected"] is None


def test_current_bound_plan_executes_one_local_worker_and_then_reuses_output(tmp_path, monkeypatch):
    task, destination, selection = planned_context(tmp_path)
    cache = cycle.runner.repository(tmp_path)[1]
    with cycle.runner.Coordinator(tmp_path, cache) as ownership:
        ownership.claim("test-owner", "Synthetic isolated fixture")
    worker = cache / "synthetic_worker.py"
    worker.write_text(
        "import json, sys\nfrom pathlib import Path\n"
        "sys.stdin.read()\nPath('output.json').write_text('{\"synthetic\": true}')\n"
        "Path(sys.argv[1]).write_text(json.dumps({'status':'completed', 'summary':'Synthetic fixture',"
        "'artifacts':['output.json'], 'checks':[], 'blockers':[], 'follow_up':[]}))\n")
    dispatches = []
    def command(codex, worktree, schema, outcome, config, session=None, read_only=False):
        dispatches.append(str(worktree))
        return [sys.executable, str(worker), str(outcome)]
    monkeypatch.setattr(cycle.runner, "probe_auth", lambda *a: None)
    monkeypatch.setattr(cycle.runner, "command_for", command)
    contract = cycle.read(destination / "contract.json")
    task_text = (destination / "task.txt").read_text(encoding="utf-8")
    receipt_path, receipt = cycle.runner.launch(
        tmp_path, cache, "synthetic", {**cycle.runner.DEFAULTS, "timeout_seconds": 30},
        task_text, task["resource"], dict(os.environ), coordinator_id="test-owner", task_contract=contract)
    assert receipt["status"] == "completed", receipt
    assert len(dispatches) == 1
    output = Path(receipt["worktree"]) / "output.json"
    assert json.loads(output.read_text()) == {"synthetic": True}
    (tmp_path / "output.json").write_bytes(output.read_bytes())
    log = destination / "independent-check.log"
    log.write_text("Independent synthetic fixture JSON read matched expected value\n")
    verification = destination / "verification.json"
    cycle.runner.write_json(verification, {
        "run_id": receipt["run_id"], "checks": [{"exit_code": 0, "log": str(log),
            "log_sha256": cycle.digest(log)}], "artifact_sha256": {"output.json": cycle.digest(output)},
        "next_action": "Reuse the synthetic fixture"})
    result = cycle.collect(tmp_path, cache, "test-owner", destination / "plan.json", receipt_path, verification)
    assert result["status"] == "verified"
    with cycle.runner.Coordinator(tmp_path, cache) as ownership:
        ownership.release_resource("test-owner", task["resource"], "integrated",
                                   tmp_path / cycle.HISTORY / receipt["run_id"] / "cycle.json")
    with pytest.raises(cycle.runner.Refused, match="Reuse"):
        cycle.runner.launch(tmp_path, cache, "synthetic", cycle.runner.DEFAULTS,
                            task_text, task["resource"], {}, coordinator_id="test-owner", task_contract=contract)
    assert len(dispatches) == 1
