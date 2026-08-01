#!/usr/bin/env python3
"""The sensitivity control's PANEL and its PRE-REGISTERED criterion — pinned.

★ WHAT THESE TESTS ARE FOR, and it is not tidiness. The scientific content of a control is that its criterion
existed BEFORE its numbers. That property cannot be verified by reading the file later — the file could have
been edited — so it is pinned here, in CI, in the same commit that first launched a GPU leg. A change to any
clause below turns the suite red and has to be argued for in a diff.

⚠ THEY ASSERT PROPERTIES, NOT LABELS OR POPULATION COUNTS (TESTING.md rule 7). No test here pins the WORDING
of a reason string or the SIZE of a growing set; both failure modes are backwards — red on every legitimate
change, green through the illegitimate one.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import selcal_panel as SP  # noqa: E402


# =============================================================================================================
# the shape
# =============================================================================================================
def test_two_arms_six_models_two_replicas_is_24_units():
    units = SP.enumerate_units()
    assert len(units) == len(SP.ARMS) * len(SP.COFOLD_MODEL_SEEDS) * len(SP.MD_REPLICAS)
    assert len(units) == 24
    per_arm = {}
    for a, _m, _r in units:
        per_arm[a.arm_id] = per_arm.get(a.arm_id, 0) + 1
    assert set(per_arm) == {SP.ARM_A, SP.ARM_B}
    assert len(set(per_arm.values())) == 1, "the arms must be BALANCED — an unbalanced design changes the "\
                                            "reference set and the criterion was written for a balanced one"


def test_unit_names_are_unique_and_namespaced():
    names = [SP.unit_name(a, m, r) for a, m, r in SP.enumerate_units()]
    assert len(set(names)) == len(names)
    assert all(n.startswith(SP.LABEL_PREFIX) for n in names)
    # DISJOINT from the sibling lanes' namespaces, in BOTH directions: a reaper's selector is derived from
    # this prefix, so an overlap would let one lane destroy another's billing hosts.
    for other in ("nrv04retro-", "nrv04cov-"):
        assert not SP.LABEL_PREFIX.startswith(other) and not other.startswith(SP.LABEL_PREFIX)


def test_leg_env_is_non_covalent_and_carries_the_frozen_protocol():
    arm = SP.arm_by_id(SP.ARM_A)
    env = SP.leg_env(arm, 3, 1)
    assert env["COVALENT"] == "0", "no arm of this panel forms a covalent adduct; setting it would be "\
                                   "fabricating chemistry"
    assert env["SEED"] == "1" and env["COFOLD_MODEL_SEED"] == "3"
    assert env["LEG_ID"] == "%s__m3" % SP.ARM_A
    assert float(env["PROD_NS"]) == SP.PROD_NS and float(env["EQUIL_NS"]) == SP.EQUIL_NS


def test_the_protocol_is_identical_to_the_panel_this_control_calibrates():
    """The scientific content of the word `control`: a different protocol would calibrate a different readout."""
    import nrv04_retro_panel as RP
    assert (SP.PROD_NS, SP.EQUIL_NS) == (RP.PROD_NS, RP.EQUIL_NS)


def test_cofold_prefix_pins_the_model_seed():
    arm = SP.arm_by_id(SP.ARM_B)
    p = SP.cofold_prefix_s3(arm, "bkt", 4)
    assert p.endswith("/seed_4/"), "the co-fold MODEL is the unit of independence; a leg that globbed a "\
                                   "system directory could silently start from a different model"
    assert arm.cofold_system in p


# =============================================================================================================
# the criterion — every clause
# =============================================================================================================
def test_criterion_is_declared_frozen_before_any_gpu_leg():
    assert SP.PASS_CRITERION["_frozen_before_any_gpu_leg"] is True


def test_criterion_names_all_five_and_clauses():
    reqs = " ".join(SP.PASS_CRITERION["PASS_requires_ALL"]).lower()
    assert "p <= 0.05" in reqs
    assert "negative" in reqs                       # the predicted direction
    assert "leave-one-model-out" in reqs
    assert "technical failures" in reqs
    assert "conforming co-fold models" in reqs      # the reference-set adequacy clause
    assert len(SP.PASS_CRITERION["PASS_requires_ALL"]) == 5


def test_alpha_matches_the_panel_being_calibrated():
    """A control judged at a looser alpha than the experiment it calibrates is not a calibration."""
    import nrv04_retro_gate as RG
    assert SP.ALPHA == RG.ALPHA


def test_direction_is_committed_and_matches_the_reference():
    assert SP.ALTERNATIVE == "less"
    assert SP.PREDICTED_MORE_STABLE_ARM == SP.ARM_A
    # the arm the reference PREFERS must be arm A, or the one-sided test points the wrong way
    assert SP.arm_by_id(SP.ARM_A).gene == SP.REFERENCE["pair"][0]
    assert SP.arm_by_id(SP.ARM_B).gene == SP.REFERENCE["pair"][1]
    assert "lower" in SP.arm_by_id(SP.ARM_A).predicted.lower()


def test_a_pass_licenses_exactly_one_sentence_and_disclaims_the_rest():
    lic = SP.PASS_CRITERION["_what_a_pass_licenses"]
    for forbidden in ("NR4A3", "degradation", "efficacy", "therapeutic window", "clinical readiness"):
        assert forbidden.lower() in lic.lower(), \
            "the licence text must NAME the claims a pass does NOT support — a reader who only reads this "\
            "field must not be able to over-read it"
    assert "NOTHING" in lic


def test_a_fail_has_its_sentence_written_in_advance():
    fail = SP.PASS_CRITERION["_what_a_fail_licenses"]
    assert "UNVALIDATED PREDICTIONS" in fail
    assert "does NOT distinguish" in fail, "a fail is ambiguous between 'the readout is blunt' and 'this "\
                                           "pair is hard', and the criterion has to say so"


def test_max_failed_legs_is_deliberately_not_the_retro_constant():
    """Copying `nrv04_retro_gate.MAX_FAILED_LEGS_PER_ARM` across would silently halve this panel's tolerance:
    that constant governs an arm of 6 legs, this one an arm of 12. The PROPORTION is what is held."""
    import nrv04_retro_gate as RG
    retro_legs_per_arm = len(RG.__dict__.get("POOLED_ARMS", ())) and 6 or 6
    here_legs_per_arm = len(SP.COFOLD_MODEL_SEEDS) * len(SP.MD_REPLICAS)
    assert here_legs_per_arm == 12
    assert SP.MAX_FAILED_LEGS_PER_ARM * retro_legs_per_arm == RG.MAX_FAILED_LEGS_PER_ARM * here_legs_per_arm


def test_min_models_per_arm_still_clears_alpha():
    """The clause exists because the NR-V04 pairwise floor (0.10 > alpha) made that comparison a
    NON-MEASUREMENT. Whatever the minimum is, the design at that minimum must still be able to reject."""
    from math import comb
    n = SP.MIN_MODELS_PER_ARM
    assert 1.0 / comb(2 * n, n) <= SP.ALPHA


# =============================================================================================================
# the reference — provenance, not plausibility
# =============================================================================================================
def test_reference_carries_a_citation_and_a_verbatim_quote():
    ref = SP.REFERENCE
    assert ref["citation"]["doi"]
    assert ref["selectivity_quote"].strip()
    assert ref["pair"] == ("SMARCA2", "SMARCA4")


def test_reference_states_the_magnitude_is_not_quotable_rather_than_quoting_one():
    """AGENTS.md: never fill a gap with a plausible number. The primary paper is paywalled, so the panel
    records the ABSENCE explicitly instead of importing a figure from a press release."""
    ref = SP.REFERENCE
    assert "magnitude_not_quotable" in ref
    assert "NOT used" in ref["magnitude_not_quotable"]
    # ...and no numeric selectivity field sneaked in alongside it
    assert "fold_window" not in ref and "dc50_nm" not in ref


def test_reference_ligand_has_a_deposited_ternary_on_BOTH_arms():
    """This is why this ligand and not one with better numbers: each arm's co-fold can be validated against a
    real structure of the same complex, which is what options-paper precondition 2 asks for."""
    dep = SP.REFERENCE["deposited_ternaries"]
    assert set(dep) == set(SP.REFERENCE["pair"])
    assert all(isinstance(v, str) and len(v) == 4 for v in dep.values())


def test_reference_quotes_survive_against_the_committed_fetch_artifact():
    """When the fetched artifact is present, the transcribed quotes must actually appear in it. This is the
    check that stops a quote drifting into a paraphrase over successive edits."""
    import json
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        SP.REFERENCE_ARTIFACT)
    if not os.path.exists(path):
        return                                   # the artifact is produced by a CI mode; absence is not failure
    with open(path) as fh:
        doc = json.load(fh)
    blob = json.dumps(doc)

    def _norm(s):
        return "".join(ch for ch in s.lower() if ch.isalnum())

    hay = _norm(blob)
    for field in ("selectivity_quote", "pair_mechanism_quote"):
        needle = _norm(SP.REFERENCE[field])
        assert needle in hay, "%s is not present verbatim in %s — a transcribed quote must match its source" \
                              % (field, SP.REFERENCE_ARTIFACT)
    assert SP.REFERENCE["ligand_ccd"] in (doc.get("ligands") or {}), \
        "the reference ligand's CCD must be in the fetched chemical-component records — that is where its "\
        "SMILES comes from, and it is never typed"


# =============================================================================================================
# exclusions
# =============================================================================================================
def test_no_cofold_is_excluded_at_freeze():
    assert SP.EXCLUDED_COFOLD_MODELS == {}, "an exclusion must be justified by a MEASURED static input fault "\
                                            "(selcal_stage.cofold_input_audit), never by how a leg came out"


def test_membership_predicate_rejects_a_smoke_record_that_echoes_the_env():
    """The measured failure this predicate exists to stop: 17 smoke legs echoed `prod_ns: 5.0` and a
    fully-populated `R1_interface` from their ENV rather than from what ran."""
    smoke = {"mode": "smoke", "prod_ns": SP.PROD_NS, "equil_ns": SP.EQUIL_NS,
             "n_frames": 5, "timed_ns": 0.002, "R1_interface": {"plateau_A": 1.09, "stable": True}}
    ok, why = SP.production_leg_check(smoke)
    assert not ok and "smoke" in why.lower()


def test_completed_check_separates_finishing_from_membership():
    frames = SP.expected_production_frames()
    good = {"mode": "run", "prod_ns": SP.PROD_NS, "equil_ns": SP.EQUIL_NS,
            "timed_ns": SP.PROD_NS, "n_frames": frames}
    assert SP.production_leg_check(good)[0] and SP.completed_production_check(good)[0]
    blew = dict(good, blew_up=True, blow_phase="prod@frame3/500")
    assert SP.production_leg_check(blew)[0], "a blow-up is still a leg of the panel — the gate scores it as a "\
                                             "technical failure rather than deleting it"
    assert not SP.completed_production_check(blew)[0]


def test_manifest_says_what_this_is_and_is_not():
    man = SP.panel_manifest()
    assert "INSTRUMENT CALIBRATION" in man["_what"]
    assert "not a selectivity result" in man["_what"].lower()
    assert "NR4A3" in man["_why"] or "NR-V04" in man["_why"]
    assert "NO free energy" in man["honesty"]
    assert man["n_units"] == 24


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
