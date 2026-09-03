"""Guards on the publish bar and the anti-gaming amendment guard.

⛔ THESE TWO FILES ARE THE PERMISSION SYSTEM. `publish_bar.py` decides what goes public under
trimcrae's name and ORCID; `amendment_guard.py` is the only thing stopping the loop from editing that
decision when it is inconvenient. A defect in either is not a wrong number — it is a paper published
that should not have been, or a standard quietly lowered.

So the tests here are adversarial by construction: each one tries to get something published or
something loosened, and asserts it was refused.
"""

from __future__ import annotations

import hashlib
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
    # ⛔ THE COUNT WAS TYPED AND WENT STALE, WHICH IS THE ONE-FACT-ONE-PLACE RULE FAILING INSIDE A
    # TEST (2026-08-27). A seventh clause -- `readable_enough_to_review` -- was added to the bar and
    # this line still said six, so CI was red on main for a bar that had GROWN. A test asserting a
    # hand-typed count of something the module already enumerates is a second copy of that fact.
    # ⚠ AND `== len(bar.CLAUSES)` ALONE WOULD BE TAUTOLOGICAL, so it is paired with the clause
    # NAMES: the length catches `evaluate` dropping or merging a row, the names catch a clause being
    # deleted from CLAUSES itself. A clause that silently disappears is the hole this test was
    # written for, and neither assertion finds it alone.
    assert len(result["clauses"]) == len(bar.CLAUSES), (
        "evaluate() returned a different number of rows than the bar declares clauses; a missing "
        "one is a hole")
    assert [c["clause"] for c in result["clauses"]] == [
        "hardening_converged", "preflight_full_green", "claim_ceiling_honoured",
        "identifiers_resolvable", "endpoint_declared", "independent_adversarial_seat",
        "readable_enough_to_review", "deliverable_is_buildable",
    ], ("the bar's clauses changed. That is allowed -- it is how the eighth arrived -- but it is "
        "never a silent change: update this list deliberately, and NEVER drop one to make a red "
        "build green (CLAUDE.md §3: a bar clause may not be loosened by the cycle it blocked).")
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
    broken and refuses everything — which is a different defect, not a safe one.

    ⭐ WHAT THIS TEST HAD TO GROW (CYC-0015) IS ITSELF THE MEASUREMENT. It used to clear all three
    file-backed clauses with three JSON objects of three keys each. Now it has to stand up a blind
    seat that reviewed this exact commit, a preflight log carrying the FULL banner and its own EXIT
    marker, a digest binding the receipt to that log, and a seat bound to the document's bytes. That
    difference is the distance between a self-report and evidence.
    """
    sha = "e" * 40
    hardening, preflight, seats = tmp_path / "h", tmp_path / "p", tmp_path / "s"
    for d in (hardening, preflight, seats):
        d.mkdir()
    monkeypatch.setattr(bar, "HARDENING_DIR", hardening)
    monkeypatch.setattr(bar, "PREFLIGHT_DIR", preflight)
    monkeypatch.setattr(bar, "SEATS_DIR", seats)
    monkeypatch.setattr(bar, "REPO", tmp_path)
    monkeypatch.setattr(bar, "_document_digest", lambda commit, doc: ("f" * 64, None))
    monkeypatch.setattr(bar, "_endpoint", lambda pub: {"document": {"file": "paper.md"}})

    seat_name = f"PUB-X-{sha}.json"
    (seats / seat_name).write_text(json.dumps({
        "blind": True, "verdict": "supported", "reviewed_commit": sha,
        "central_claim": "The fusion partner is a candidate stratification variable, not established.",
        "document_sha256": "f" * 64, "blockers": [], "p1s": []}))
    (hardening / "PUB-X.json").write_text(json.dumps({
        "last_round": 7, "blockers": [], "p1s": [], "reviewed_commit": sha,
        "seats": [seat_name]}))
    body = f"PINNED_SHA={sha}\n{bar.FULL_BANNER}\n878 passed\nEXIT=0\n"
    (tmp_path / "run.log").write_text(body)
    (preflight / f"{sha}.json").write_text(json.dumps({
        "sha": sha, "mode": "FULL", "exit": 0, "utc": "2026-08-26T00:00:00Z",
        "log": "run.log", "log_sha256": hashlib.sha256(body.encode()).hexdigest()}))

    assert bar.clause_1_hardening_converged("PUB-X", sha)["ok"]
    assert bar.clause_2_preflight_full_green("PUB-X", sha)["ok"]
    assert bar.clause_6_independent_adversarial_seat("PUB-X", sha)["ok"]


# ---------------------------------------------------------------- clause 8: is there anything to post

#: `_tree_at`'s fast path only skips materialising a worktree when HEAD is exactly this sha AND the
#: working tree is clean; a dirty tree (the ordinary case while editing) still resolves correctly —
#: `git worktree add --detach` checks out the last COMMIT, never uncommitted changes — so these tests
#: read the real committed `build_submission_pdf.py`, not whatever is on disk right now.
def _committed_head(repo=REPO):
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_deliverable_is_buildable_passes_for_a_registered_manuscript(bar):
    """`build_submission_pdf.PAPERS['aso-journal']['manuscript']` names
    `aso/fusion-junction-aso-journal-article.md`, which is PUB-ASO's own `document.file` with the
    `research/manuscripts/` prefix stripped -- verified directly against the committed renderer
    rather than assumed stable."""
    clause = bar.clause_8_deliverable_is_buildable("PUB-ASO", _committed_head())
    assert clause["verdict"] == bar.PASS, clause["evidence"]


def test_deliverable_is_buildable_fails_for_a_document_no_papers_entry_names(bar, monkeypatch):
    """AUT-PD-213: `publish_bar` returned MAY POST (7/7) for PUB-STRATEGY-ARCH although nothing
    could render its PDF. A document under `research/manuscripts/` that plainly matches no
    `PAPERS` entry reproduces the exact gap without depending on which real papers happen to be
    registered today -- PUB-STRATEGY-ARCH itself may be registered later, which would make a test
    pinned to its id pass for the wrong reason."""
    monkeypatch.setattr(
        bar, "_endpoint",
        lambda pub: {"document": {"file": "research/manuscripts/does/not-exist-in-papers.md"}})
    clause = bar.clause_8_deliverable_is_buildable("PUB-X", _committed_head())
    assert clause["verdict"] == bar.FAIL
    assert "PAPERS" in clause["evidence"]


#: ⭐ ONE FUNCTION, TWO CASES -- `scripts/tier-budgets.json` counts test FUNCTIONS, not parametrized
#: instances, and `systems/tests` sits in the tight commit-loop tier. Two UNVERIFIABLE checks that
#: shared nothing but their assertion were two functions; merged, they are one, at no loss of
#: coverage (the mutation that dropped either branch in publish_bar.py is still caught).
@pytest.mark.parametrize("pub_id,sha", [
    ("PUB-DOES-NOT-EXIST", None),  # no document.file at all
    ("PUB-ASO", "0" * 40),         # a real document, but a sha that resolves to nothing
], ids=["no-document", "unresolvable-sha"])
def test_deliverable_is_buildable_fails_closed_when_it_cannot_be_verified(bar, pub_id, sha):
    clause = bar.clause_8_deliverable_is_buildable(pub_id, sha or _committed_head())
    assert clause["verdict"] == bar.UNVERIFIABLE


def test_a_document_outside_research_manuscripts_cannot_match_any_papers_entry(bar, monkeypatch):
    """Every `PAPERS` entry's `manuscript` is relative to `research/manuscripts/`; a document path
    that is not under that prefix cannot match one by construction, and this must be FAIL (the
    manuscript is a real, readable document with no renderer) rather than UNVERIFIABLE (which
    would read as 'go get more evidence' for a state no evidence can change)."""
    monkeypatch.setattr(bar, "_endpoint", lambda pub: {"document": {"file": "README.md"}})
    clause = bar.clause_8_deliverable_is_buildable("PUB-X", _committed_head())
    assert clause["verdict"] == bar.FAIL


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


# ---------------------------------------------------------------- the self-graded half of the bar
#
# ⛔⛔ CYC-0015 FOUND THAT THREE OF THE BAR'S CLAUSES WERE SELF-REPORTS, AND VERIFIED IT RATHER THAN
# ARGUING IT. Clauses 3-5 are computed — lint_claims, lint_citations, the graph. Clauses 1, 2 and 6
# read a file that the loop itself writes, and each was cleared by a hand-typed JSON object with no
# evidence whatever behind it:
#
#     clause 1  {"blockers": [], "p1s": [], "reviewed_commit": sha, "last_round": 99}  -> PASS
#     clause 2  {"mode": "FULL", "exit": 0, "sha": sha, "utc": "typed by hand"}        -> PASS
#     clause 6  {"blind": true, "reviewed_commit": sha, "verdict": "supported"}        -> PASS
#
# The second one printed `at typed by hand` as its evidence line. This file's own header says these
# tests are adversarial by construction, and this block is the reason that matters: the bar is a
# standing grant to publish under a real person's name and ORCID.


def test_an_empty_hardening_record_with_no_seat_behind_it_is_refused(bar, tmp_path, monkeypatch):
    """⛔ THE VERIFIED DEFECT. Absence of findings is evidence only when somebody looked."""
    monkeypatch.setattr(bar, "HARDENING_DIR", tmp_path)
    monkeypatch.setattr(bar, "SEATS_DIR", tmp_path / "none")
    sha = "a" * 40
    (tmp_path / "PUB-X.json").write_text(json.dumps({
        "blockers": [], "p1s": [], "reviewed_commit": sha, "last_round": 99,
    }))
    clause = bar.clause_1_hardening_converged("PUB-X", sha)
    assert clause["verdict"] == bar.FAIL, "a convergence claim with no seat under it is not a clause"
    assert not clause["ok"]


def test_a_hardening_record_may_not_name_a_seat_that_reviewed_another_commit(bar, tmp_path,
                                                                             monkeypatch):
    """The pin is the whole point: a seat that read an older tree reviewed a different paper."""
    hardening, seats = tmp_path / "h", tmp_path / "s"
    hardening.mkdir(), seats.mkdir()
    monkeypatch.setattr(bar, "HARDENING_DIR", hardening)
    monkeypatch.setattr(bar, "SEATS_DIR", seats)
    sha, older = "a" * 40, "b" * 40
    (seats / f"PUB-X-{sha}-seat-one.json").write_text(json.dumps({
        "blind": True, "reviewed_commit": older, "blockers": [], "p1s": []}))
    (hardening / "PUB-X.json").write_text(json.dumps({
        "blockers": [], "p1s": [], "reviewed_commit": sha, "last_round": 5,
        "seats": [f"PUB-X-{sha}-seat-one.json"]}))
    assert bar.clause_1_hardening_converged("PUB-X", sha)["verdict"] == bar.FAIL


def test_a_hardening_record_may_not_under_report_its_own_seats(bar, tmp_path, monkeypatch):
    """The tallies are the SEATS'. A record that declares zero over a seat holding a blocker is the
    failure mode this clause exists to catch, and it is the one a self-report cannot see."""
    hardening, seats = tmp_path / "h", tmp_path / "s"
    hardening.mkdir(), seats.mkdir()
    monkeypatch.setattr(bar, "HARDENING_DIR", hardening)
    monkeypatch.setattr(bar, "SEATS_DIR", seats)
    sha = "a" * 40
    (seats / f"PUB-X-{sha}-seat-one.json").write_text(json.dumps({
        "blind": True, "reviewed_commit": sha,
        "blockers": [{"id": "B1", "finding": "the central claim is not supported"}], "p1s": []}))
    (hardening / "PUB-X.json").write_text(json.dumps({
        "blockers": [], "p1s": [], "reviewed_commit": sha, "last_round": 5,
        "seats": [f"PUB-X-{sha}-seat-one.json"]}))
    clause = bar.clause_1_hardening_converged("PUB-X", sha)
    assert clause["verdict"] == bar.FAIL
    assert "under-reports" in clause["evidence"]


def test_a_preflight_receipt_with_no_log_is_a_typed_claim(bar, tmp_path, monkeypatch):
    """An exit code nothing can re-derive is a sentence, not a gate result."""
    monkeypatch.setattr(bar, "PREFLIGHT_DIR", tmp_path)
    sha = "c" * 40
    (tmp_path / f"{sha}.json").write_text(json.dumps({
        "sha": sha, "mode": "FULL", "exit": 0, "utc": "typed by hand"}))
    assert bar.clause_2_preflight_full_green("PUB-X", sha)["verdict"] == bar.FAIL


def test_a_scoped_run_log_cannot_clear_the_full_clause(bar, tmp_path, monkeypatch):
    """⛔ A ONE-OF-A-PAIR TRAP, AND THE TEXT BELOW IS THE REAL THING preflight.sh PRINTS. The scoped
    run's own closing verdict ADVERTISES the flag — 'PREFLIGHT_FULL=1 before publishing.' — so a
    naive substring test for `PREFLIGHT_FULL=1` accepts a log from the very run that is telling you
    it is not the publication run."""
    monkeypatch.setattr(bar, "PREFLIGHT_DIR", tmp_path)
    monkeypatch.setattr(bar, "REPO", tmp_path)
    sha = "c" * 40
    scoped = ("PINNED_SHA=" + sha + "\n"
              "PREFLIGHT OK (fast gates + the selector's own contract; NEITHER large suite ran here.\n"
              "             CI runs both on push. PREFLIGHT_TESTS=1 for the manuscripts suite,\n"
              "             PREFLIGHT_MODALITIES=1 for the modalities suite,\n"
              "             PREFLIGHT_FULL=1 before publishing.)\n"
              "EXIT=0\n")
    (tmp_path / "scoped.log").write_text(scoped)
    (tmp_path / f"{sha}.json").write_text(json.dumps({
        "sha": sha, "mode": "FULL", "exit": 0, "utc": "2026-08-27T00:00:00Z",
        "log": "scoped.log",
        "log_sha256": hashlib.sha256(scoped.encode()).hexdigest()}))
    clause = bar.clause_2_preflight_full_green("PUB-X", sha)
    assert clause["verdict"] == bar.FAIL
    assert "banner" in clause["evidence"]


def test_a_preflight_receipt_cannot_be_re_pointed_at_another_run(bar, tmp_path, monkeypatch):
    """The digest binds the receipt to one log. Without it, one green run clears every commit."""
    monkeypatch.setattr(bar, "PREFLIGHT_DIR", tmp_path)
    monkeypatch.setattr(bar, "REPO", tmp_path)
    sha = "c" * 40
    (tmp_path / "run.log").write_text(f"PINNED_SHA={sha}\n{bar.FULL_BANNER}\nEXIT=0\n")
    (tmp_path / f"{sha}.json").write_text(json.dumps({
        "sha": sha, "mode": "FULL", "exit": 0, "utc": "2026-08-27T00:00:00Z",
        "log": "run.log", "log_sha256": "0" * 64}))
    assert bar.clause_2_preflight_full_green("PUB-X", sha)["verdict"] == bar.FAIL


def test_an_unterminated_preflight_log_is_an_abandoned_run(bar, tmp_path, monkeypatch):
    """`repo-gates`: never trust a backgrounded gate's reported exit code — read its own marker. A
    log with no marker is a run that died, and a run that died is not a green one."""
    monkeypatch.setattr(bar, "PREFLIGHT_DIR", tmp_path)
    monkeypatch.setattr(bar, "REPO", tmp_path)
    sha = "c" * 40
    body = f"PINNED_SHA={sha}\n{bar.FULL_BANNER}\n... and then the container went away\n"
    (tmp_path / "run.log").write_text(body)
    (tmp_path / f"{sha}.json").write_text(json.dumps({
        "sha": sha, "mode": "FULL", "exit": 0, "utc": "2026-08-27T00:00:00Z",
        "log": "run.log", "log_sha256": hashlib.sha256(body.encode()).hexdigest()}))
    clause = bar.clause_2_preflight_full_green("PUB-X", sha)
    assert clause["verdict"] == bar.FAIL
    assert "EXIT=" in clause["evidence"]


def test_a_seat_must_be_bound_to_the_text_it_reviewed(bar, tmp_path, monkeypatch):
    """A verdict that names no document could have been written without opening one."""
    monkeypatch.setattr(bar, "SEATS_DIR", tmp_path)
    monkeypatch.setattr(bar, "_document_digest", lambda sha, doc: ("f" * 64, None))
    monkeypatch.setattr(bar, "_endpoint", lambda pub: {"document": {"file": "paper.md"}})
    sha = "d" * 40
    (tmp_path / f"PUB-X-{sha}.json").write_text(json.dumps({
        "blind": True, "verdict": "supported", "reviewed_commit": sha,
        "central_claim": "The fusion partner is a candidate stratification variable, not established.",
    }))
    assert bar.clause_6_independent_adversarial_seat("PUB-X", sha)["verdict"] == bar.FAIL


# ---------------------------------------------------------------- the producer
#
# ⭐ `hardening-state/` AND `preflight-receipts/` HAD NEVER EXISTED IN ANY REF (`git log --all` over
# both returned empty, 2026-08-27), and `publish_bar.py` was the only file in the repository that
# named them. The bar declared three clauses nothing produced. These tests hold the producer to the
# rule that makes it worth having: it derives, it never serialises an assertion.


@pytest.fixture(scope="module")
def producer():
    return _load("record_bar_evidence")


def test_the_producer_refuses_a_run_that_did_not_pass(producer, tmp_path, monkeypatch):
    sha = "a" * 40
    log = tmp_path / "run.log"
    log.write_text(f"PINNED_SHA={sha}\n{producer.FULL_BANNER}\nEXIT=1\n")
    monkeypatch.setattr(producer, "PREFLIGHT_DIR", tmp_path / "receipts")
    monkeypatch.setattr(producer, "PREFLIGHT_LOG_DIR", tmp_path / "logs")
    assert producer.record_preflight(sha, log) == 1
    assert not (tmp_path / "receipts").exists(), "a refusal must write nothing at all"


def test_the_producer_refuses_a_run_against_a_different_tree(producer, tmp_path, monkeypatch):
    log = tmp_path / "run.log"
    log.write_text(f"PINNED_SHA={'b' * 40}\n{producer.FULL_BANNER}\nEXIT=0\n")
    monkeypatch.setattr(producer, "PREFLIGHT_DIR", tmp_path / "receipts")
    monkeypatch.setattr(producer, "PREFLIGHT_LOG_DIR", tmp_path / "logs")
    assert producer.record_preflight("a" * 40, log) == 1


def test_the_producer_refuses_an_unterminated_log(producer, tmp_path, monkeypatch):
    sha = "a" * 40
    log = tmp_path / "run.log"
    log.write_text(f"PINNED_SHA={sha}\n{producer.FULL_BANNER}\nstill going\n")
    monkeypatch.setattr(producer, "PREFLIGHT_DIR", tmp_path / "receipts")
    monkeypatch.setattr(producer, "PREFLIGHT_LOG_DIR", tmp_path / "logs")
    assert producer.record_preflight(sha, log) == 1


def test_the_producer_writes_a_non_converged_record_when_no_seat_ran(producer, tmp_path,
                                                                     monkeypatch):
    """⭐ THE GAIN IS TURNING 'I CANNOT SEE' INTO 'I LOOKED, AND NO'. The record is still written —
    an honest not-converged record is worth more than an absent one, because the bar can grade it."""
    monkeypatch.setattr(producer, "SEATS_DIR", tmp_path / "seats")
    (tmp_path / "seats").mkdir()
    monkeypatch.setattr(producer, "HARDENING_DIR", tmp_path / "hardening")
    assert producer.record_hardening("PUB-X", "a" * 40, 5, None) == 0
    written = json.loads((tmp_path / "hardening" / "PUB-X.json").read_text())
    assert written["seats"] == []
    assert written["converged"] is False


def test_the_producer_carries_a_seats_findings_into_the_record(producer, tmp_path, monkeypatch):
    """It may not quietly drop a blocker: the record's tallies come from the seat files."""
    seats = tmp_path / "seats"
    seats.mkdir()
    sha = "a" * 40
    (seats / f"PUB-X-{sha}-seat-one.json").write_text(json.dumps({
        "blind": True, "reviewed_commit": sha,
        "blockers": [{"id": "B1", "finding": "unsupported"}], "p1s": []}))
    monkeypatch.setattr(producer, "SEATS_DIR", seats)
    monkeypatch.setattr(producer, "HARDENING_DIR", tmp_path / "hardening")
    assert producer.record_hardening("PUB-X", sha, 5, None) == 0
    written = json.loads((tmp_path / "hardening" / "PUB-X.json").read_text())
    assert len(written["blockers"]) == 1
    assert written["converged"] is False


def test_the_producer_ignores_a_seat_that_was_not_blind(producer, tmp_path, monkeypatch):
    seats = tmp_path / "seats"
    seats.mkdir()
    sha = "a" * 40
    (seats / f"PUB-X-{sha}-seat-one.json").write_text(json.dumps({
        "blind": False, "reviewed_commit": sha, "blockers": [], "p1s": []}))
    monkeypatch.setattr(producer, "SEATS_DIR", seats)
    monkeypatch.setattr(producer, "HARDENING_DIR", tmp_path / "hardening")
    producer.record_hardening("PUB-X", sha, 5, None)
    written = json.loads((tmp_path / "hardening" / "PUB-X.json").read_text())
    assert written["seats"] == [], "a seat that was not blind is not independent evidence"
    assert written["converged"] is False
