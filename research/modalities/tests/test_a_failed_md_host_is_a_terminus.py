"""A FAILURE IS A TERMINUS TOO — the branch whose absence billed 4.5 hours for nothing.

★★ THE INCIDENT, 2026-08-02. Three `selcal-` hosts sat `actual_status: running` at `gpu_util: 0.0` producing
nothing: `selcal-smarca4-m2-r0` for 275 min at $0.1819/hr, `-m3-r0` for 122 min at $0.2207/hr, `-m3-r1` for
40 min at $0.0711/hr. The lane's own reaper printed `SPARED — no landed leg in S3 and no host-written
terminus` on every one of ~120 consecutive ticks, and recorded `host_phase: null` every time.

The hosts were never silent. `-m3-r0` and `-m3-r1` were writing `[audit] REFUSING to run: two heavy atoms in
DIFFERENT residues sit 0.693 A apart` on a loop — 12 attempt logs across FIVE machines — into a file nothing
read. `host_phase: null` was not a reading of absence; it was the ABSENCE OF A READING, because
`_host_phase` searches the CO-FOLD prefix and an MD leg writes `<RESULT_PREFIX>/<unit>/phase.txt`.

Three safety nets, none of which covered this lane:
  1. the container's crash-loop brake fired, then parked and deferred to "the CI idle guard" — which no
     caller runs over `selcal-` hosts;
  2. the reaper's terminus branch could not fire for an MD host even in principle;
  3. the resulting `null` rendered as a reassuring sentence.

So these tests pin the PROPERTY (a host that has written terminal-failure evidence gets destroyed) and the
two scoping rules that keep it honest, not the shape of any one string.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import selcal_vast_launch as L  # noqa: E402
import selcal_panel as SP  # noqa: E402

REFUSAL = ("[stage] {\"target_chain\": \"A\"}\n"
           "[audit] REFUSING to run: two heavy atoms in DIFFERENT residues sit 0.693 A apart, below the "
           "1.00 A floor.\n")
BRAKE = "[selfstop] CRASH-LOOP BRAKE: 3 container starts in 900s. This rental keeps restarting\n"


def _inst(label="selcal-smarca4-m3-r1", status="running", iid="46555738"):
    return {"id": iid, "label": label, "actual_status": status, "dph_total": 0.07}


# =============================================================================================================
# the markers are QUOTED FROM THEIR EMITTERS, not invented
# =============================================================================================================
def test_the_refusal_marker_is_the_string_the_stager_actually_raises():
    """⛔ A marker that drifts from the code that emits it is a guard that silently stops firing — and looks
    identical to a guard with nothing to find. Pin it against the emitter, in the same repo."""
    src = open(os.path.join(MOD, "selcal_vast_launch.py")).read()
    assert "raise SystemExit('%s ' + audit['why'])" % L.AUDIT_REFUSAL_MARK in src or \
           "raise SystemExit('%s' + " % L.AUDIT_REFUSAL_MARK in src or \
           L.AUDIT_REFUSAL_MARK in src.split("def md_failure_terminus")[0], \
        "AUDIT_REFUSAL_MARK does not appear in the staging heredoc that is supposed to emit it"


def test_the_brake_marker_is_the_string_gpu_backend_actually_echoes():
    import gpu_backend
    assert L.CRASH_LOOP_MARK.replace("[selfstop] ", "") in gpu_backend._VAST_CRASHLOOP_BRAKE
    assert "[selfstop] " in gpu_backend._VAST_CRASHLOOP_BRAKE


# =============================================================================================================
# the pure decision
# =============================================================================================================
def test_an_audit_refusal_is_a_terminus():
    t, why = L.md_failure_terminus(REFUSAL, "cloned instance=46555738", "46555738")
    assert t == "input_audit_refused"
    assert "static" in why.lower() or "STATIC" in why


def test_an_audit_refusal_condemns_WITHOUT_an_instance_match():
    """★ THE SCOPING RULE THAT MATTERS. The fault is a property of the CO-FOLD, not the rental: it reproduced
    byte-identically on five machines. Requiring the log to name this instance would spare each fresh host in
    turn — which is precisely the loop that burned five rentals on one unit."""
    t, _ = L.md_failure_terminus(REFUSAL, phase="", instance_id="99999999")
    assert t == "input_audit_refused"
    t2, _ = L.md_failure_terminus(REFUSAL, phase="cloned instance=11111111", instance_id="99999999")
    assert t2 == "input_audit_refused"


def test_a_crash_loop_brake_condemns_ONLY_the_rental_that_wrote_it():
    """★ THE OPPOSITE SCOPING, and conflating the two would be a real bug: a previous host's brake sits in the
    inherited per-unit log, and must not condemn the fresh rental that has not failed yet."""
    t, _ = L.md_failure_terminus(BRAKE, "cloned instance=46555738", "46555738")
    assert t == "crash_loop_brake"
    stale, _ = L.md_failure_terminus(BRAKE, "cloned instance=46539178", "46555738")
    assert stale is None, "a brake from a PREVIOUS instance must be a fossil, not a verdict"


def test_a_working_host_is_never_condemned():
    for log in ("", "[stage] ok\n[audit] {\"ok\": true}\n", "minimize 1200/4000\n", None):
        assert L.md_failure_terminus(log, "md-running instance=46555738", "46555738")[0] is None


def test_gpu_idleness_is_not_an_input_to_this_decision():
    """⛔ CLAUDE.md §6, INVIOLABLE. All three hosts in the incident read `gpu_util: 0.0` — and so does a
    legitimately CPU-bound staging phase. What condemns is positive host-written evidence, never idleness."""
    # ⚠ THE DOCSTRING IS STRIPPED FIRST, and that is not a loosening: the docstring NAMES `gpu_util` on
    # purpose, to record that all three hosts read 0.0. The claim is about what the CODE consults, so
    # grepping the prose would forbid explaining the rule in the one place a reader will look for it.
    import ast
    src = open(os.path.join(MOD, "selcal_vast_launch.py")).read()
    fn = next(n for n in ast.parse(src).body
              if isinstance(n, ast.FunctionDef) and n.name == "md_failure_terminus")
    fn.body = fn.body[1:] if (fn.body and isinstance(fn.body[0], ast.Expr)
                              and isinstance(fn.body[0].value, ast.Constant)) else fn.body
    assert "gpu_util" not in ast.unparse(fn)


# =============================================================================================================
# the branch, in reap_decision
# =============================================================================================================
def test_reap_decision_destroys_a_host_with_a_failure_terminus():
    reap, why = L.reap_decision(_inst(), done_units=set(), cofold_complete_systems=(), s3_readable=True,
                                md_terminus="input_audit_refused — the audit refused")
    assert reap is True
    assert "FAILURE terminus" in why


def test_without_the_terminus_the_same_host_is_spared_exactly_as_before():
    """The regression baseline: this is the sentence the incident printed ~120 times. It must still be what
    happens when there is genuinely no evidence — the fix adds a branch, it does not lower the bar."""
    reap, why = L.reap_decision(_inst(), done_units=set(), cofold_complete_systems=(), s3_readable=True)
    assert reap is False
    assert "no landed leg in S3 and no host-written terminus" in why


def test_banked_work_still_wins_over_a_stale_failure_terminus():
    """★ ORDERING. A unit whose leg is banked must be reaped AS BANKED WORK, not as a failure — the earlier
    attempt's refusal can still be sitting in the per-unit log after a later attempt succeeded, and reporting
    a landed leg's host as a failure would put a false cause in the ledger."""
    reap, why = L.reap_decision(_inst(), done_units={"selcal-smarca4-m3-r1"}, cofold_complete_systems=(),
                                s3_readable=True, md_terminus="input_audit_refused — x")
    assert reap is True
    assert "work banked" in why and "FAILURE" not in why


def test_an_unreadable_census_still_reaps_nothing_on_a_terminus():
    """`s3_readable=False` short-circuits before every S3-derived branch, and the terminus is S3-derived."""
    reap, why = L.reap_decision(_inst(), done_units=set(), cofold_complete_systems=(), s3_readable=False,
                                md_terminus="input_audit_refused — x")
    assert reap is False and "could not be read" in why


def test_a_terminal_state_still_wins_first():
    reap, why = L.reap_decision(_inst(status="exited"), set(), (), True, md_terminus="crash_loop_brake — x")
    assert reap is True and "terminal state" in why


# =============================================================================================================
# the reaper actually asks the question
# =============================================================================================================
def test_mode_reap_reads_the_MD_phase_path_and_not_only_the_cofold_one():
    """⛔ THE ACTUAL DEFECT. `_host_phase` looks under the CO-FOLD prefix only, so for an MD host it returned
    "" forever. If this wiring is removed, every test above passes and the incident recurs — the pure
    function would simply never be handed anything."""
    src = open(os.path.join(MOD, "selcal_vast_launch.py")).read()
    body = src[src.index("def mode_reap("):]
    body = body[:body.index("\ndef ", 10)]
    assert "_md_leg_terminus(" in body, "mode_reap never computes the MD failure terminus"
    assert "md_terminus=" in body, "…and never passes it to reap_decision"
    assert body.index("_md_leg_terminus(") < body.index("reap_decision("), "it must be computed first"


def test_the_terminus_is_recorded_in_the_artifact():
    """A reaper with no artifact is indistinguishable from a reaper that never ran — and a reap whose CAUSE is
    not recorded is indistinguishable from a guess."""
    src = open(os.path.join(MOD, "selcal_vast_launch.py")).read()
    body = src[src.index("def mode_reap("):]
    body = body[:body.index("\ndef ", 10)]
    assert '"md_terminus"' in body


def test_the_lookup_is_scoped_to_MD_labels():
    """A co-fold host has no `<RESULT_PREFIX>/<label>/`, so asking would only ever return an absent reading."""
    src = open(os.path.join(MOD, "selcal_vast_launch.py")).read()
    body = src[src.index("def mode_reap("):]
    body = body[:body.index("\ndef ", 10)]
    assert "cofold_label_systems(" in body.split("_md_leg_terminus(")[0]


# =============================================================================================================
# the exclusion this produced
# =============================================================================================================
def test_smarca4_model_3_is_excluded_on_MEASURED_evidence():
    ex, why = SP.excluded_cofold("selcal_smarca4", 3)
    assert ex is True
    for token in ("0.693", "A:LYS71:O", "E:SER38:O", "cofold_input_audit", "OUTCOME-BLIND"):
        assert token in why, token
    assert "5" in why or "FIVE" in why, "the multi-host reproduction is the argument against 'bad rental'"


def test_the_exclusion_did_not_quietly_take_the_other_unlanded_unit_with_it():
    """★★ THE DISCIPLINE THAT MAKES THIS NOT A RETUNE. `m2-r0` was ALSO unlanded and ALSO burning — and it
    audited CLEAN at 1.2994 A while its replica m2-r1 landed. Excluding what happens to be unfinished is
    outcome-shaped; excluding what a static audit REFUSED is not. m2 must still be in the panel."""
    assert SP.excluded_cofold("selcal_smarca4", 2)[0] is False
    assert SP.excluded_cofold("selcal_smarca2", 3)[0] is False, "the fault was smarca4's co-fold, not seed 3"
    names = {SP.unit_name(a, m, r) for a, m, r in SP.enumerate_units()}
    assert "selcal-smarca4-m2-r0" in names
    assert "selcal-smarca4-m3-r0" not in names and "selcal-smarca4-m3-r1" not in names


def test_the_panel_can_still_be_SCORED_after_the_exclusion():
    """⛔ THE CLAUSE THE CRITERION FROZE IN ADVANCE: 'at least 4 conforming co-fold models in EACH arm … after
    any measured input-fault exclusion'. If this fails, the exclusion has silently destroyed the panel and the
    honest outcome is INDETERMINATE, not a quiet re-shape."""
    from math import comb
    per_arm: dict = {}
    for a, m, _r in SP.enumerate_units():
        per_arm.setdefault(a.arm_id, set()).add(m)
    for arm, models in per_arm.items():
        assert len(models) >= SP.MIN_MODELS_PER_ARM, f"{arm} fell below the frozen floor: {sorted(models)}"
    na, nb = (len(per_arm["selcal_smarca2"]), len(per_arm["selcal_smarca4"]))
    assert 1.0 / comb(na + nb, na) <= SP.ALPHA, "the exact reference set can no longer reach alpha"


def test_the_replacement_loop_can_no_longer_re_buy_the_excluded_unit():
    """The 5-rental loop closes HERE, not in the reaper: `enumerate_units` is what the watch diffs against
    `done` to decide what still needs a host."""
    src = open(os.path.join(MOD, "selcal_vast_launch.py")).read()
    body = src[src.index("def mode_watch("):]
    body = body[:body.index("\ndef ", 10)]
    assert "SP.enumerate_units()" in body


# =============================================================================================================
# the refusal must BANK, which is what made this diagnosis hard
# =============================================================================================================
def test_the_input_audit_artifact_is_uploaded_before_the_refusal_can_end_the_script():
    """⛔ MEASURED: `input_audit.json` was absent in S3 for BOTH failing units, because its upload sat below a
    heredoc that `raise SystemExit` had already made fatal under `set -e`. The one artifact naming the cause
    was the one thing never banked, so the diagnosis had to come from container stdout that dies with the
    rental."""
    src = open(os.path.join(MOD, "selcal_vast_launch.py")).read()
    assert "|| RC_AUDIT=$?" in src, "the heredoc's failure must be CAUGHT, not left to end the shell"
    up = src.index('input_audit.json" "$RESULT_S3/input_audit.json"')
    assert src.index("|| RC_AUDIT=$?") < up, "the rc must be captured before the upload"
    assert up < src.index('exit "$RC_AUDIT"'), "the upload must happen BEFORE the script re-raises"


def test_set_e_is_actually_in_force_so_that_reasoning_holds():
    """The fix above is only correct if `set -e` is really on; if it were ever removed, `|| RC_AUDIT=$?` is
    harmless but the COMMENT explaining it would be wrong, and a wrong comment outlives a wrong line."""
    src = open(os.path.join(MOD, "selcal_vast_launch.py")).read()
    assert "set -eo pipefail" in src


@pytest.mark.parametrize("unit", ["selcal-smarca4-m3-r0", "selcal-smarca4-m3-r1"])
def test_the_two_dead_units_are_gone_from_the_expected_panel(unit):
    assert unit not in {SP.unit_name(a, m, r) for a, m, r in SP.enumerate_units()}
    assert unit in {SP.unit_name(a, m, r) for a, m, r in SP.enumerate_units(include_excluded=True)}, \
        "…but still reachable with include_excluded, so the record of what was dropped survives"
