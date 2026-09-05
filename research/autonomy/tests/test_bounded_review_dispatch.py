"""Dispatch spends one frozen review batch; matching evidence and maintenance are reusable."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bounded_review as BR
import continuity
import goal_progress
import handoff
import ready_to_post
import publish_bar
import seat_scratch

SHA = "a" * 40
OLD = "b" * 40


@pytest.fixture
def review(tmp_path, monkeypatch):
    seats = tmp_path / "seats"
    seats.mkdir()
    hard = tmp_path / "hard"
    hard.mkdir()
    state = {"record": None, "history": {}, "matching": False, "ok": False}
    def read(path):
        if path.parent == hard:
            return state["record"], "missing"
        return json.loads(path.read_text()), None
    bar = SimpleNamespace(HARDENING_DIR=hard, SEATS_DIR=seats, _read_json=read,
                          _look_history=lambda p: state["history"],
                          _covers=lambda p, a, b: state["matching"] or a == b,
                          clause_1_hardening_converged=lambda p, s: {
                              "ok": state["ok"], "evidence": "0 blockers, 3 maintenance findings"})
    monkeypatch.setattr(BR, "_bar", lambda repo: bar)
    return tmp_path, seats, state


def test_one_baseline_then_reuse_matching_maintenance_evidence(review):
    root, _, state = review
    assert not BR.review_decision("PUB-X", "HEAD", repo=root)["allowed"]
    assert BR.review_decision("PUB-X", SHA, repo=root)["allowed"]
    state.update(record={"reviewed_commit": OLD}, history={OLD: 2}, matching=True, ok=True)
    result = BR.review_decision("PUB-X", SHA, repo=root)
    assert not result["allowed"] and result["action"] == "reuse_review"
    assert "maintenance" in result["evidence"]


def test_changed_or_failed_review_needs_focused_claims_or_material_reason(review):
    root, _, state = review
    state.update(record={"reviewed_commit": OLD}, history={OLD: 2})
    assert not BR.review_decision("PUB-X", SHA, repo=root)["allowed"]
    request = {"scope": "focused_verification", "changed_claims": ["Result 2"],
               "depends_on": ["arithmetic.json"]}
    assert not BR.review_decision("PUB-X", SHA, request, repo=root)["allowed"]
    (root / "arithmetic.json").write_text('{"recomputed": true}')
    assert BR.review_decision("PUB-X", SHA, request, repo=root)["allowed"]
    request = {"scope": "full_review", "reason": {
        "kind": "material_error", "summary": "independent recomputation contradicts Table 2",
        "evidence": ["arithmetic.json"]}}
    assert BR.review_decision("PUB-X", SHA, request, repo=root)["allowed"]
    request["reason"]["kind"] = "optional_regression_guard"
    assert not BR.review_decision("PUB-X", SHA, request, repo=root)["allowed"]
    request["reason"]["kind"] = "material_error"
    request["reason"]["evidence"] = ["../outside.json"]
    assert not BR.review_decision("PUB-X", SHA, request, repo=root)["allowed"]


def test_frozen_batch_can_finish_but_cannot_expand_or_repeat(review):
    root, seats, state = review
    request = {"scope": "baseline", "lenses": ["claims", "methods"]}
    assert BR.review_decision("PUB-X", SHA, request, repo=root)["allowed"]
    def write(lens):
        (seats / f"PUB-X-{SHA}-seat-{lens}.json").write_text(json.dumps({
            "reviewed_commit": SHA, "lens": lens, "status": "complete",
            "review_request": request}))
    write("claims")
    state["history"] = {SHA: 1}
    assert BR.review_decision("PUB-X", SHA, request, repo=root)["action"] == "resume_batch"
    assert not BR.review_decision("PUB-X", SHA, {**request, "lenses": ["claims", "new"]},
                                  repo=root)["allowed"]
    write("methods")
    assert BR.review_decision("PUB-X", SHA, request, repo=root)["action"] == "budget_spent"


def test_seat_cli_checks_dispatch_and_freezes_the_review_request(tmp_path, monkeypatch):
    request = {"scope": "baseline", "lenses": ["claims", "methods"]}
    request_path = tmp_path / "request.json"
    request_path.write_text(json.dumps(request))
    seats = tmp_path / "seats"
    args = ["--open-seat-record", "--paper", "PUB-X", "--sha", SHA, "--lens", "claims",
            "--seats-dir", str(seats), "--review-request", str(request_path)]
    monkeypatch.setattr(BR, "review_decision", lambda *a, **kw: {
        "allowed": False, "reason": "matching review already complete"})
    assert seat_scratch.main(args) == 1
    assert not seats.exists()
    monkeypatch.setattr(BR, "review_decision", lambda *a, **kw: {"allowed": True})
    assert seat_scratch.main(args) == 0
    path, findings = seat_scratch.close_seat_record(str(seats), "PUB-X", SHA, "claims", {
        "review_request": {**request, "scope": "full_review"}, "blockers": [], "p1s": []})
    assert findings and "CONTRADICTS" in findings[0][0]
    assert json.loads(Path(path).read_text())["review_request"] == request


def test_legacy_and_contract_review_work_share_the_decision(review, monkeypatch):
    root, _, state = review
    state.update(record={"reviewed_commit": OLD}, history={OLD: 2}, matching=True, ok=True)
    assert BR.task_review_decision({"item": "reanalyse expression", "resource": "paper:PUB-X"},
                                   SHA, repo=root)["allowed"]
    legacy = {"what": "Run a hardening round", "kind": "harden",
              "serves": {"publication": "PUB-X"}}
    assert BR.task_review_decision(legacy, SHA, repo=root)["action"] == "reuse_review"
    process = {"kind": "process_defect", "what": "Fix a parser; a hardening round found the defect",
               "closes_clause": {"clause": "hardening_converged", "paper": "PUB-X"}}
    assert BR.task_review_decision(process, SHA, repo=root)["action"] == "not_review"
    monkeypatch.setattr(BR, "task_review_decision", lambda e, **kw: {
        "allowed": e["id"] == "science", "action": "reuse_review", "reason": "already reviewed"})
    row = {"state": "queued", "retry_budget": 1, "score": 10}
    ledger = {"entries": [dict(row, id="review"), dict(row, id="science")]}
    assert [e["id"] for e in handoff.top_items(ledger)] == ["science"]
    assert "bounded review" in continuity._why_not_ready(dict(row, id="review"), None)


def test_ready_notifications_follow_bytes_and_action_not_unrelated_commits(monkeypatch):
    monkeypatch.setattr(publish_bar, "_deliverable_digest_at", lambda p, s: "same")
    queue = {"waiting": {"PUB-X": {"act": "journal_submission"}},
             "notified": {"PUB-X": {"commit": OLD}}}
    ready = {"commit": SHA, "deliverable_digest": "same", "act": "journal_submission"}
    assert ready_to_post._already_notified("PUB-X", ready, queue)
    assert not ready_to_post._already_notified("PUB-X", {**ready, "deliverable_digest": "changed"}, queue)
    assert not ready_to_post._already_notified("PUB-X", {**ready, "act": "qeios_new_version"}, queue)


def test_matching_rollup_reuses_only_the_explicitly_selected_round(tmp_path, monkeypatch):
    hard = tmp_path / "hard"
    hard.mkdir()
    monkeypatch.setattr(publish_bar, "SEATS_DIR", tmp_path)
    monkeypatch.setattr(publish_bar, "HARDENING_DIR", hard)
    monkeypatch.setattr(publish_bar, "_covers", lambda p, a, b: True)
    for sha in (SHA, OLD):
        (tmp_path / f"PUB-X-{sha}.json").write_text(json.dumps({
            "reviewed_commit": sha, "blind": True, "verdict": "supported"}))
    assert publish_bar._rollup_covering("PUB-X", "c" * 40, "missing")[0] is None
    (hard / "PUB-X.json").write_text(json.dumps({"reviewed_commit": OLD}))
    record, _ = publish_bar._rollup_covering("PUB-X", "c" * 40, "missing")
    assert record["reviewed_commit"] == OLD
    # Selection supplies no central claim or digest: the normal acceptance checks still refuse.
    result = publish_bar.clause_6_independent_adversarial_seat("PUB-X", "c" * 40)
    assert not result["ok"] and "central_claim" in result["evidence"]


def test_goal_reader_checks_current_deliverables_or_an_explicit_frozen_target(monkeypatch):
    monkeypatch.setattr(goal_progress, "_head", lambda: SHA)
    monkeypatch.setattr(goal_progress, "_pinned_commit", lambda p: OLD)
    def bar(paper, sha):
        return {"n_passed": 7 if sha == SHA else 8, "n_clauses": 8,
                "clauses": [{"clause": "review", "ok": sha == OLD}]}, None
    monkeypatch.setattr(goal_progress, "_publish_bar", bar)
    condition = {"kind": "publish_bar", "paper": "PUB-X"}
    current = goal_progress.measure({"done_condition": condition})
    assert current["sha"] == SHA and current["status"] == "OPEN"
    frozen = goal_progress.measure({"done_condition": {**condition, "sha": OLD}})
    assert frozen["sha"] == OLD and frozen["status"] == "MET"
