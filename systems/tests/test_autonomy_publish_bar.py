"""Guards on the publish bar and the anti-gaming amendment guard.

⛔ THESE TWO FILES ARE THE PERMISSION SYSTEM. `publish_bar.py` decides what goes public under
trimcrae's name and ORCID; `amendment_guard.py` is the only thing stopping the loop from editing that
decision when it is inconvenient. A defect in either is not a wrong number — it is a paper published
that should not have been, or a standard quietly lowered.

So the tests here are adversarial by construction: each one tries to get something published or
something loosened, and asserts it was refused.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
AUTONOMY = REPO / "research" / "autonomy"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"autonomy_{name}", AUTONOMY / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def bar():
    return _load("publish_bar")


@pytest.fixture(scope="module")
def guard():
    return _load("amendment_guard")


# ---------------------------------------------------------------- the bar fails closed


def test_a_paper_with_no_evidence_at_all_is_blocked(bar):
    """The default answer is NO. Nothing in the repo has hardening records, preflight receipts or
    blind-seat records yet, so every real endpoint must currently be blocked. If this test ever
    fails, something started passing without evidence being produced."""
    result = bar.evaluate("PUB-ASO", "0" * 40)
    assert result["may_post"] is False
    assert result["n_passed"] < result["n_clauses"]


def test_an_unknown_paper_is_blocked_rather_than_erroring(bar):
    result = bar.evaluate("PUB-DOES-NOT-EXIST", "0" * 40)
    assert result["may_post"] is False


def test_every_clause_reports_pass_fail_or_unverifiable_and_nothing_else(bar):
    result = bar.evaluate("PUB-ASO", "0" * 40)
    assert len(result["clauses"]) == 6, "the bar is six clauses; a missing one is a hole"
    for clause in result["clauses"]:
        assert clause["verdict"] in {bar.PASS, bar.FAIL, bar.UNVERIFIABLE}
        assert clause["ok"] == (clause["verdict"] == bar.PASS), (
            "UNVERIFIABLE must never be treated as ok — an absent reading is not a reading of "
            "absence, and this is the exact line that decides whether silence publishes a paper"
        )
        assert clause["evidence"], "a verdict with no evidence is not checkable"


def test_a_hardening_record_for_a_different_commit_does_not_clear_this_one(bar, tmp_path,
                                                                           monkeypatch):
    """Reviewing a pinned commit is `paper-hardening`'s own rule. A converged record against an
    older tree says the paper WAS fine, not that it is."""
    monkeypatch.setattr(bar, "HARDENING_DIR", tmp_path)
    (tmp_path / "PUB-X.json").write_text(json.dumps({
        "last_round": 4, "blockers": [], "p1s": [], "reviewed_commit": "a" * 40,
    }))
    clause = bar.clause_1_hardening_converged("PUB-X", "b" * 40)
    assert clause["verdict"] == bar.FAIL
    assert not clause["ok"]


def test_a_scoped_preflight_run_cannot_clear_an_outward_facing_act(bar, tmp_path, monkeypatch):
    """`repo-gates`: the default run does not claim any test passes. Accepting it here would make
    PREFLIGHT_FULL ceremonial."""
    monkeypatch.setattr(bar, "PREFLIGHT_DIR", tmp_path)
    sha = "c" * 40
    (tmp_path / f"{sha}.json").write_text(json.dumps({"sha": sha, "mode": "SCOPED", "exit": 0}))
    clause = bar.clause_2_preflight_full_green("PUB-X", sha)
    assert clause["verdict"] == bar.FAIL


def test_a_seat_that_was_not_blind_is_not_independent_evidence(bar, tmp_path, monkeypatch):
    monkeypatch.setattr(bar, "SEATS_DIR", tmp_path)
    sha = "d" * 40
    (tmp_path / f"PUB-X-{sha}.json").write_text(json.dumps({
        "blind": False, "verdict": "supported", "reviewed_commit": sha,
    }))
    clause = bar.clause_6_independent_adversarial_seat("PUB-X", sha)
    assert clause["verdict"] == bar.FAIL


def test_all_six_clauses_passing_is_what_it_takes(bar, tmp_path, monkeypatch):
    """The positive control. Without it, the tests above could all pass on a bar that is simply
    broken and refuses everything — which is a different defect, not a safe one."""
    sha = "e" * 40
    hardening, preflight, seats = tmp_path / "h", tmp_path / "p", tmp_path / "s"
    for d in (hardening, preflight, seats):
        d.mkdir()
    monkeypatch.setattr(bar, "HARDENING_DIR", hardening)
    monkeypatch.setattr(bar, "PREFLIGHT_DIR", preflight)
    monkeypatch.setattr(bar, "SEATS_DIR", seats)
    (hardening / "PUB-X.json").write_text(json.dumps({
        "last_round": 7, "blockers": [], "p1s": [], "reviewed_commit": sha}))
    (preflight / f"{sha}.json").write_text(json.dumps({
        "sha": sha, "mode": "FULL", "exit": 0, "utc": "2026-08-26T00:00:00Z"}))
    (seats / f"PUB-X-{sha}.json").write_text(json.dumps({
        "blind": True, "verdict": "supported", "reviewed_commit": sha}))

    assert bar.clause_1_hardening_converged("PUB-X", sha)["ok"]
    assert bar.clause_2_preflight_full_green("PUB-X", sha)["ok"]
    assert bar.clause_6_independent_adversarial_seat("PUB-X", sha)["ok"]


# ---------------------------------------------------------------- the authority edges


def test_a_journal_is_never_reachable_by_any_bar(bar):
    """`journal.standing_grant` is a constant, not a parameter. If this ever passes, the escalation
    trigger trimcrae relies on has been deleted."""
    assert bar.authority_permits("PUB-ASO", "journal", "submit")["ok"] is False


def test_no_venue_other_than_aixiv_was_granted(bar):
    for venue in ("zenodo", "biorxiv", "qeios", "email"):
        assert bar.authority_permits("PUB-ASO", venue, "submit")["ok"] is False


def test_the_authority_file_records_who_granted_it_and_against_what(bar):
    """A grant with no attribution is not traceable to trimcrae, which CLAUDE.md §3 requires."""
    authority = json.loads((AUTONOMY / "publication-authority.json").read_text())
    aixiv = authority["aixiv"]
    assert "trimcrae" in aixiv["granted_by"]
    assert aixiv["granted_against"], "the backdrop the grant was given against must be recorded"
    assert aixiv["scope"]["max_versions_per_paper"] >= 1
    assert authority["journal"]["standing_grant"] is False


def test_a_missing_authority_file_means_no_authority(bar, tmp_path, monkeypatch):
    monkeypatch.setattr(bar, "AUTHORITY_FILE", tmp_path / "nope.json")
    assert bar.authority_permits("PUB-ASO", "aixiv", "submit")["ok"] is False


# ---------------------------------------------------------------- the anti-gaming guard


def test_governed_paths_are_recognised(guard):
    for path in ("CLAUDE.md", "research/autonomy/priority-weights.json",
                 "research/autonomy/publish_bar.py", "systems/tests/test_autonomy_priority.py",
                 ".claude/skills/research-loop/SKILL.md"):
        assert guard.is_governed(path), f"{path} must be governed"
    for path in ("research/modalities/some_analysis.py", "README.md"):
        assert not guard.is_governed(path), f"{path} should be free to edit without ceremony"


def test_the_deliberate_gaming_attempt_is_refused(guard, monkeypatch):
    """★ THIS IS PHASE 9'S DEFINITION OF DONE, and it is written as an ATTEMPT rather than an
    assertion on purpose: the architecture doc says the check is proved by a deliberate attempt
    being refused, not by a claim that it would be.

    The scenario is the realistic one. A cycle tries to post a paper; the publish bar blocks it;
    the cycle 'fixes' that by editing the bar. That is how a standard gets lowered in practice, and
    it must come back REFUSED.
    """
    receipt = {
        "cycle_id": "CYC-TEST-001",
        "blocked_by": [{"path": "research/autonomy/publish_bar.py",
                        "what": "clause 1 failed: hardening not converged"}],
    }
    monkeypatch.setattr(guard, "changed_paths",
                        lambda _sha: ["research/autonomy/publish_bar.py"])
    result = guard.evaluate(receipt, "HEAD~1")
    assert result["permitted"] is False
    assert result["findings"][0]["verdict"] == "REFUSED"
    assert "blocked" in result["findings"][0]["why"]


def test_the_same_change_by_a_later_cycle_is_allowed_once_declared(guard, monkeypatch):
    """The guard refuses editing under pressure, not the edit itself. If it refused both, the loop
    could never improve its own standards and self-improvement would be a fiction."""
    receipt = {"cycle_id": "CYC-TEST-002", "blocked_by": []}
    monkeypatch.setattr(guard, "changed_paths",
                        lambda _sha: ["research/autonomy/publish_bar.py"])
    monkeypatch.setattr(guard, "declared", lambda _p, _c: True)
    result = guard.evaluate(receipt, "HEAD~1")
    assert result["permitted"] is True
    assert result["findings"][0]["verdict"] == "DECLARED"


def test_an_undeclared_governed_edit_is_caught_even_when_nothing_blocked_the_cycle(guard,
                                                                                  monkeypatch):
    receipt = {"cycle_id": "CYC-TEST-003", "blocked_by": []}
    monkeypatch.setattr(guard, "changed_paths", lambda _sha: ["CLAUDE.md"])
    monkeypatch.setattr(guard, "declared", lambda _p, _c: False)
    result = guard.evaluate(receipt, "HEAD~1")
    assert result["permitted"] is False
    assert result["findings"][0]["verdict"] == "UNDECLARED"


def test_a_free_path_needs_no_declaration(guard, monkeypatch):
    receipt = {"cycle_id": "CYC-TEST-004", "blocked_by": []}
    monkeypatch.setattr(guard, "changed_paths", lambda _sha: ["research/modalities/thing.py"])
    result = guard.evaluate(receipt, "HEAD~1")
    assert result["permitted"] is True
    assert result["governed_paths_touched"] == 0


def test_a_blockage_with_no_path_fails_closed(guard):
    """An unreadable receipt must not clear a cycle. This is the shape the repo has been burned by:
    a plausible-looking record that carries no actual reading."""
    with pytest.raises(RuntimeError):
        guard.blocked_by_paths({"cycle_id": "X", "blocked_by": [12345]})


def test_an_unanswered_self_serving_check_is_not_a_declaration(guard, tmp_path, monkeypatch):
    """§10.5: the field must be ANSWERED. An empty string is the easiest possible way to satisfy a
    logging requirement while telling nobody anything."""
    log = tmp_path / "amendments.jsonl"
    log.write_text(json.dumps({
        "cycle_id": "CYC-X", "path": "CLAUDE.md", "self_serving_check": "  ",
    }) + "\n")
    monkeypatch.setattr(guard, "LOG", log)
    assert guard.declared("CLAUDE.md", "CYC-X") is False

    log.write_text(json.dumps({
        "cycle_id": "CYC-X", "path": "CLAUDE.md",
        "self_serving_check": "no — this tightened a rule against the loop's own convenience",
    }) + "\n")
    assert guard.declared("CLAUDE.md", "CYC-X") is True


def test_the_guard_is_load_bearing_and_not_decorative(guard, monkeypatch):
    """Mutation test. Remove the bar from the governed list and the refusal must disappear — if it
    does not, something else is producing the pass and this suite is blind."""
    receipt = {"cycle_id": "CYC-TEST-005",
               "blocked_by": ["research/autonomy/publish_bar.py"]}
    monkeypatch.setattr(guard, "changed_paths",
                        lambda _sha: ["research/autonomy/publish_bar.py"])
    monkeypatch.setattr(guard, "GOVERNED", ("nothing/at/all",))
    result = guard.evaluate(receipt, "HEAD~1")
    assert result["permitted"] is True, (
        "with publish_bar.py removed from GOVERNED the edit was STILL refused — the refusal is not "
        "coming from the governed list, so the guard is not what this suite thinks it is"
    )


def test_the_amendment_log_integrity_check_runs(guard):
    result = guard.check_log()
    assert isinstance(result["ok"], bool)


def test_both_scripts_run_as_cli_without_crashing():
    """A guard nobody can invoke is a guard that will not be invoked."""
    for args in (["--check-log"],):
        proc = subprocess.run(
            ["python3", str(AUTONOMY / "amendment_guard.py"), *args],
            capture_output=True, text=True, cwd=str(REPO), timeout=120)
        assert proc.returncode in (0, 1), proc.stderr
    proc = subprocess.run(
        ["python3", str(AUTONOMY / "publish_bar.py"), "--paper", "PUB-ASO", "--sha", "0" * 40],
        capture_output=True, text=True, cwd=str(REPO), timeout=300)
    assert proc.returncode == 1, "an evidence-free paper must exit nonzero"
