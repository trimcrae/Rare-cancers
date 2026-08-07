"""Row 27's badge-versus-reality forensic and its regime test, exercised with NO network.

⛔ THE PROPERTY UNDER TEST IS THE ONE ROW 27 EXISTS FOR: a green badge over a job that never ran must
never be readable as a job that ran and found nothing. Every fixture here is synthetic; none is
evidence about any real run.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import row27_ddddg_precheck_status as r27  # noqa: E402


# -------------------------------------------------------------------------------------------------
# The regime test — the half of row 27 that is easy to skip
# -------------------------------------------------------------------------------------------------
def test_no_artifact_is_undetermined_and_explicitly_not_a_negative():
    """⛔ 'the question is still unasked' and 'no benchmark exists' are different findings."""
    art = [{"search": "C01a", "exists": False, "verdict": None},
           {"search": "C01b", "exists": False, "verdict": None}]
    out = r27.regime_test(art, r27.resolution_budget())
    assert out["state"] == "UNDETERMINED"
    assert "NOT the finding that none exists" in out["sentence"]


def test_every_search_refusing_on_evidence_is_a_stop_and_is_named_a_good_outcome():
    art = [{"search": "C01a", "exists": True, "verdict": "STOP_NO_REFERENCE"},
           {"search": "C01b", "exists": True, "verdict": "STOP_NO_REFERENCE"}]
    out = r27.regime_test(art, r27.resolution_budget())
    assert out["state"] == "STOP_NO_REFERENCE"
    assert "refusal on evidence is a better outcome" in out["sentence"]


def test_a_find_does_not_pass_the_regime_test_by_existing():
    """Finding a benchmark is not passing one, and the artifact must say so in the same breath."""
    art = [{"search": "C01a", "exists": True, "verdict": "PROCEED"},
           {"search": "C01b", "exists": True, "verdict": "STOP_NO_REFERENCE"}]
    out = r27.regime_test(art, r27.resolution_budget())
    assert out["state"] == "FOUND_PENDING_REGIME_TEST"
    assert "FINDING A BENCHMARK IS NOT PASSING ONE" in out["sentence"]
    assert "wrong sign" in out["sentence"]


def test_the_regime_test_always_carries_the_no_inheritance_from_v6_statement():
    """C01 inherits NO validation from V6; a reader must not have to know that already."""
    for verdicts in ([None, None], ["STOP_NO_REFERENCE", "STOP_NO_REFERENCE"], ["PROCEED", None]):
        art = [{"search": "C0%d" % i, "exists": v is not None, "verdict": v}
               for i, v in enumerate(verdicts, 1)]
        out = r27.regime_test(art, r27.resolution_budget())
        assert "inherits NO validation from V6" in out["inherits_nothing_from_V6"]
        assert "instrument-options.md §2" in out["inherits_nothing_from_V6"]
        assert "§2.3" in out["claim_ceiling"]


# -------------------------------------------------------------------------------------------------
# The resolution budget is READ, not typed
# -------------------------------------------------------------------------------------------------
def test_the_budget_reads_the_committed_figures_from_their_own_homes():
    """Rule 1: every figure here has one home elsewhere and is loaded from it."""
    b = r27.resolution_budget()
    assert not b.get("error"), b.get("error")
    homes = {r["home"] for r in b["reads"]}
    assert any("valb_failure_propagation.MEASURED" in h for h in homes)
    assert any("S_BEST_CASE_RESOLVABLE_KCAL" in h for h in homes)
    assert any("ddddg_known_answer_search.PREREG" in h for h in homes)


def test_the_wrong_sign_is_carried_with_the_error_magnitude_and_not_separately():
    """⚠ 1.543 kcal/mol alone reads as 'close'. With the sign it reads as 'pointed the other way'."""
    b = r27.resolution_budget()
    row = next(r for r in b["reads"] if "quantity CLASS" in r["quantity"])
    import valb_failure_propagation as vfp
    assert row["value_kcal"] == vfp.MEASURED["abs_error_kcal"]
    assert "WRONG SIGN" in row["⚠"]


def test_v6s_band_is_carried_with_its_within_one_pocket_scope():
    """A band quoted without its scope is how an inheritance gets assumed."""
    b = r27.resolution_budget()
    row = next(r for r in b["reads"] if "V6" in r["quantity"])
    assert "WITHIN ONE POCKET" in row["scope"]


# -------------------------------------------------------------------------------------------------
# The badge forensic's discriminator
# -------------------------------------------------------------------------------------------------
def test_a_zero_duration_skipped_job_is_never_substantive_work():
    """The whole point: a green run whose job was skipped at zero duration proves nothing ran."""
    doc = r27.build(skip_network=True)
    assert doc["badge_forensic"]["runs"] == []
    # And with no network reading, the summary must not claim anything about what ran.
    assert not doc["badge_forensic"]["summary"]


def test_the_module_emits_the_map_edits_verify_map_edits_can_check():
    import verify_map_edits as vme
    doc = r27.build(skip_network=True)
    for edit in doc["map_edits_required"]:
        missing = [f for f in vme.REQUIRED_FIELDS if f not in edit]
        assert not missing, missing


def test_the_routed_map_edits_still_apply_to_the_live_map():
    import verify_map_edits as vme
    with open(vme.DEFAULT_MAP, encoding="utf-8") as fh:
        map_text = fh.read()
    doc = r27.build(skip_network=True)
    for edit in doc["map_edits_required"]:
        row = vme.check_edit(edit, map_text)
        assert row.get("ok"), (row["status"], row.get("detail"))


def test_an_absent_artifact_says_which_ref_it_was_absent_from():
    """CLAUDE.md §7: an artifact on the wrong branch is a stale fact that reads as a current one."""
    rows = r27.artifact_status(root=os.path.join(os.path.dirname(__file__), "_no_such_dir"))
    for r in rows:
        assert r["exists"] is False
        assert "ABSENT READING" in r["_absent_means"]
        assert "which ref" in r["_absent_means"].lower()


# -------------------------------------------------------------------------------------------------
# The timeout finding — row 27's binding blocker, which its own text does not name
# -------------------------------------------------------------------------------------------------
def test_a_nonpositive_duration_counts_as_zero_even_when_completion_precedes_start():
    """⚠ Measured on run 30776566810: a skipped job reported completion one second BEFORE start.

    Exact equality scored that as a real duration — the discriminator failing in the one direction
    that matters, making a job that never ran look like one that did.
    """
    assert r27._nonpositive_duration("2026-08-03T01:20:53Z", "2026-08-03T01:20:52Z") is True
    assert r27._nonpositive_duration("2026-08-03T01:20:53Z", "2026-08-03T01:20:53Z") is True
    assert r27._nonpositive_duration("2026-08-03T01:20:53Z", "2026-08-03T01:22:53Z") is False
    assert r27._nonpositive_duration(None, None) is False


def test_the_declared_timeouts_are_read_from_the_real_workflow_not_typed():
    """Rule 1, and the denominator of the whole finding: 2.00 h means nothing without the ceiling."""
    t = r27.declared_timeouts()
    assert t["error"] is None, t["error"]
    assert t["by_job"].get("c01a"), "c01a must declare a timeout-minutes"
    assert t["by_job"].get("c01b"), "c01b must declare a timeout-minutes"


def test_a_run_reaching_its_declared_timeout_is_named_a_timeout_not_a_cancellation():
    """The Actions API says `cancelled` for both; only the comparison against the ceiling separates
    them, and the two have opposite remedies."""
    timeouts = {"by_job": {"c01a": 350, "c01b": 120}, "_source": "x", "error": None}
    v = r27.timeout_verdict({"longest_observed_run_h": {"c01a": 5.92, "c01b": 2.0}}, timeouts)
    assert v["per_job"]["c01a"]["reached_its_own_timeout"] is True
    assert v["per_job"]["c01b"]["reached_its_own_timeout"] is True
    assert "HIT THE CEILING" in v["per_job"]["c01b"]["reading"]
    assert "MAKE THE SEARCH FIT" in v["⭐_the_finding"]


def test_a_short_cancelled_run_is_not_called_a_timeout():
    """An operator cancellation and a timeout must not render alike."""
    timeouts = {"by_job": {"c01a": 350, "c01b": 120}, "_source": "x", "error": None}
    v = r27.timeout_verdict({"longest_observed_run_h": {"c01a": 0.27, "c01b": 0.06}}, timeouts)
    assert v["per_job"]["c01a"]["reached_its_own_timeout"] is False
    assert v["per_job"]["c01b"]["reached_its_own_timeout"] is False


def test_the_checkpoint_durability_gap_is_measured_from_the_real_workflow():
    """⛔ Checkpoints written and never restored is why the timeout is terminal, not annoying."""
    c = r27.checkpoint_durability()
    assert c["error"] is None, c["error"]
    assert c["writes_checkpoints"] is True
    assert c["has_restore_step"] is False, (
        "if a restore step has been added, this finding is DISCHARGED — update the module rather "
        "than deleting the assertion")
    assert "restarts at stage 1" in c["verdict"]
