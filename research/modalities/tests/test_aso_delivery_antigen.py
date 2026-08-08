"""Offline tests for the ASO delivery-antigen two-axis scorer.

⛔ THIS MODULE'S FAILURE MODE IS NAMING A CANDIDATE THAT IS NOT THERE. `readiness.md` records
RT-ASO's one missing item as "a named delivery candidate", so a module that emits a name discharges
a register entry and moves a route. Four properties therefore have to be impossible to lose:

  1. **The universe ceiling is REAL.** A verdict computed over antigens the exposure axis cannot
     read would be a claim about genes nobody measured. The scored set must be exactly the
     intersection, and a gene without an exposure reading must be absent from `per_antigen`
     entirely rather than present with a favourable-looking blank.
  2. **An absent reading never becomes a pass.** An unreadable array, a missing HPA row and an
     undefined ratio (a zero comparator median) must each block NAMING, and none may be rendered
     as a low or a high value.
  3. **The naming bar is the strict one.** `can_a_delivery_candidate_be_NAMED` must be true only
     for the tier that clears every instrument that can read the antigen; the residual tiers must
     never leak into it.
  4. **The controls actually run.** A control block that passes because it computed nothing is the
     shape CLAUDE.md §4(b) names, so each control is checked to have read a real value.

Every test runs over the REAL committed artifacts — no fixtures. A hand-written fixture cannot
catch the class of bug that matters here, which is a scorer that disagrees with the data it cites.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aso_delivery_antigen as M  # noqa: E402

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def res():
    return M.derive()


@pytest.fixture(scope="module")
def expo():
    with open(os.path.join(MOD, "gse28866-tumour-vs-normal.json")) as fh:
        return json.load(fh)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 1 — THE UNIVERSE CEILING
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_every_scored_antigen_really_has_a_measured_exposure_reading(res, expo):
    cal = expo["ratio_calibration"]["per_gene"]
    for g in res["per_antigen"]:
        assert cal.get(g, {}).get("emc_over_normal") is not None, (
            f"{g} was scored on the exposure axis with no measured EMC/normal ratio")


def test_no_antigen_is_scored_that_the_exposure_deposit_does_not_carry(res, expo):
    carried = set(expo["per_gene"]["values"])
    assert set(res["per_antigen"]) <= carried


def test_non_surface_products_are_excluded_and_say_why(res):
    excluded = res["instrument_reach"]["joint_universe"]["genes_on_the_exposure_axis_excluded_on_topology"]
    for g in ("VCAN", "BGN", "ENO3", "NR4A3", "PPARG", "PRAME", "SEMA3C"):
        assert g in excluded, f"{g} is not a cell-surface antibody address and must be excluded"
        assert excluded[g], f"{g}'s exclusion carries no stated reason"
        assert g not in res["per_antigen"]


def test_the_universe_ceiling_is_reported_and_is_smaller_than_the_surface_board(res):
    jr = res["instrument_reach"]["joint_universe"]
    assert jr["n"] == len(res["per_antigen"])
    # the whole point: most of the repository's surface antigens cannot be asked the question
    assert jr["n_surface_board_genes_the_exposure_axis_cannot_reach"] > jr["n"]


def test_the_absent_organs_are_named_and_include_normal_soft_tissue(res):
    absent = res["instrument_reach"]["exposure_axis"]["organs_and_tissue_classes_ABSENT_REPO_CURATED"]
    joined = " | ".join(absent).lower()
    for needed in ("nerve", "thyroid", "soft tissue", "brain"):
        assert needed in joined, f"the exposure panel's blind spot list omits {needed}"


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 2 — AN ABSENT READING NEVER BECOMES A PASS
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_an_unreadable_array_is_an_instrument_statement_not_a_low_reading(res):
    seen = False
    for g, row in res["per_antigen"].items():
        for name, inst in row["lineage_axis_vs_comparator_sarcomas"]["per_instrument"].items():
            if inst["state"] == "UNREADABLE":
                seen = True
                assert inst["t"] is None
                assert "NOT a low reading" in inst["_meaning"]
    assert seen, "no unreadable platform in the committed data — this test has lost its subject"


def test_a_missing_hpa_row_blocks_naming_without_being_evidence(res):
    for g, row in res["per_antigen"].items():
        prior = row["exposure_axis_vs_normal_tissue"]["hpa_normal_tissue_prior"]
        if prior["state"] != "ABSENT_FROM_THE_COMMITTED_PRIOR":
            continue
        assert row["joint_verdict"] != "CLEARS_BOTH_AXES_ON_EVERY_INSTRUMENT_THAT_CAN_READ_IT"
        assert "ABSENT READING" in prior["_meaning"]
        assert g not in res["headline"]["antigens_that_clear_both_axes_on_every_instrument_that_can_read_them"]


def test_an_undefined_ratio_is_unreadable_and_never_scores(res, expo):
    """PRAME's normal-organ median is 0.000, so its EMC/normal ratio does not exist. An instrument
    that read that as a perfect exposure score would name a candidate off a division by zero."""
    assert expo["per_gene"]["values"]["PRAME"]["normal_median"] == 0.0
    assert expo["ratio_calibration"]["per_gene"]["PRAME"]["emc_over_normal"] is None
    assert "PRAME" not in res["per_antigen"]
    hard = res["controls"]["hard_control_PRAME_an_undefined_ratio_must_not_score"]
    assert hard["passed"] is True


def test_ratio_state_treats_a_null_ratio_as_unreadable_not_as_zero():
    st = M._ratio_state(None, None)
    assert st["state"] == "UNREADABLE"
    assert "NOT a ratio of zero" in st["_meaning"]


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 3 — THE NAMING BAR
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_naming_requires_the_strict_tier_only(res):
    named = res["headline"]["antigens_that_clear_both_axes_on_every_instrument_that_can_read_them"]
    for g in named:
        assert res["per_antigen"][g]["joint_verdict"] == \
            "CLEARS_BOTH_AXES_ON_EVERY_INSTRUMENT_THAT_CAN_READ_IT"
    assert res["headline"]["can_a_delivery_candidate_be_NAMED"] == bool(named)


def test_the_residual_tiers_are_not_names(res):
    residual = res["headline"]["ranked_residual_clears_the_measured_axes_but_cannot_be_named"]
    named = res["headline"]["antigens_that_clear_both_axes_on_every_instrument_that_can_read_them"]
    assert not (set(residual) & set(named))
    for g in residual:
        assert res["per_antigen"][g]["joint_verdict"].startswith("CLEARS_BOTH_MEASURED_AXES_BUT")


def test_one_instrument_reading_an_antigen_down_refuses_it_outright(res):
    for g, row in res["per_antigen"].items():
        lin = row["lineage_axis_vs_comparator_sarcomas"]
        if lin["n_down"]:
            assert lin["verdict"].startswith("NOT_ELEVATED")
            assert row["joint_verdict"] == "FAILS_THE_LINEAGE_AXIS"


def test_the_committed_artifact_reproduces_from_the_committed_inputs():
    """⛔ A scorer whose artifact no longer derives from its inputs is a stale fact reading as a
    current one — CLAUDE.md §7. `--check` is the guard and this asserts the guard is honest."""
    assert M.main(["--check"]) == 0


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 4 — THE CONTROLS ACTUALLY RAN
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_the_positive_lineage_control_read_real_values(res):
    c = res["controls"]["positive_lineage_control_NR4A3"]
    assert c["sarcoma_median"] == 0.0 and c["emc_median"] is not None and c["emc_median"] > 0
    assert c["GPL6244_t"] is not None and c["passed"] is True


def test_the_transactivation_control_read_real_values(res):
    c = res["controls"]["positive_transactivation_control_ENO3"]
    assert c["GPL6244_t"] and c["GPL3290_t"] and c["emc_over_normal_percentile"]
    assert c["passed"] is True


def test_the_negative_exposure_controls_are_all_below_normal(res):
    c = res["controls"]["negative_exposure_controls"]
    assert set(c["per_gene"]) == {"GPC3", "MSLN", "L1CAM", "CDH17"}
    for g, r in c["per_gene"].items():
        assert r["percentile_of_all_genes"] is not None, g
        assert r["below_normal"] is True, g


def test_the_committed_welch_statistics_still_agree_with_the_committed_per_sample_values(res):
    c = res["controls"]["artifact_self_consistency_recomputed_welch_t"]
    assert c["n_disagreements"] == 0, c["disagreements"]


def test_all_controls_pass(res):
    assert res["controls"]["_pass"] is True


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 5 — THE TWO INSTRUMENT FINDINGS THIS RUN PRODUCED MUST NOT SILENTLY DECAY
# ─────────────────────────────────────────────────────────────────────────────────────────────
def test_the_inert_vital_tissue_override_is_measured_not_asserted(res):
    a = res["hpa_vital_tissue_override_is_inert"]
    assert a["n_antigens_scored_in_the_prior"] > 0
    # the audit must be a READING: if HPA ever returns the field, this flips and the verdict text
    # must flip with it rather than staying frozen at "inert".
    if a["n_with_any_vital_tissue_hit"] == 0:
        assert a["vital_tissue_override_ever_fired"] is False
        assert "INERT" in a["verdict"]
    else:
        assert a["vital_tissue_override_ever_fired"] is True
        assert "INERT" not in a["verdict"]


def test_stage_1_coverage_refuses_the_stronger_claim(res):
    s = res["stage_1_coverage_over_this_universe"]
    assert s["n_universe"] == len(res["per_antigen"])
    # "absent from the outputs" must never be written as "not scanned"
    assert "NOT" in s["⛔_whether_they_were_SCANNED_is_undecidable"]
    for g in s["genes_with_NO_per_gene_row_anywhere_in_stage_1"]:
        assert s["per_gene"][g]["appears_anywhere_in_the_stage_1_artifact"] is False


def test_the_language_discipline_block_is_present_and_binding(res):
    txt = res["_language_discipline"].upper()
    for word in ("EFFICACY", "SAFETY", "THERAPEUTIC WINDOW", "CLINICAL READINESS"):
        assert word in txt
    assert res["_not_preregistered"].startswith("⚠")
