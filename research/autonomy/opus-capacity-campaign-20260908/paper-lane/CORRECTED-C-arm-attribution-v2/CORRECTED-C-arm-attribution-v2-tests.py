"""Focused VALUE-BASED tests of the v2 rules. No counts are asserted anywhere: each test builds a
small record by hand and asserts the machine VALUES the rules produce for it. There is no quota
and no census; these tests would still pass if every real row fell to UNKNOWN.

Scope: the five behaviours the repair exists for, plus the two withdrawn rules.
Not in scope: any suite over the 552 rows, any ablation, any amnesty, any source query.
"""
import importlib.util, os, sys, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "v2", os.path.join(HERE, "CORRECTED-C-arm-attribution-v2-derive.py"))
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)


def arm(label, type_="EXPERIMENTAL", desc=""):
    return {"label": label, "type": type_, "description": desc}


def leaf(label, narrative, src="LEAF-QD-group1.tsv", ln=42):
    return dict(leaf_source=src, leaf_row=ln, leaf_verdict="JOIN_RECOVERABLE",
                leaf_locator="LEAF-OUT/%s:line %d" % (src, ln),
                leaf_narrative=narrative, leaf_arm_label=label, leaf_arm_type="EXPERIMENTAL")


RESULTS = []


def case(name, fn):
    try:
        fn()
        RESULTS.append(("PASS", name, ""))
    except AssertionError as e:
        RESULTS.append(("FAIL", name, str(e) or "assertion failed"))
    except Exception:
        RESULTS.append(("ERROR", name, traceback.format_exc(limit=3)))


# ------------------------------------------------------------------------------------------
# T1  A narrative token WITHOUT actual corroboration cannot confirm.
#     The narrative literally contains 'description', 'interventionNames', 'verbatim' and
#     'elimination' -- four of v1's ten CORROBORATION tokens -- while SAYING THE OPPOSITE.
#     v1 returned CONFIRMED + LEAF_WITHIN_RECORD_RELATION for exactly this shape.
# ------------------------------------------------------------------------------------------
def t1():
    ai = [arm("Arm A", "EXPERIMENTAL", "Cohort one"), arm("Arm B", "EXPERIMENTAL", "Cohort two")]
    lf = leaf("Arm A",
              "the group description is absent and armGroups[*].interventionNames are identical, "
              "so no verbatim field supports elimination of either arm")
    out = v2.decide_link("Dose Level 1", "", ai, lf)
    assert out["arm_link_state"] == "PROPOSED", out["arm_link_state"]
    assert out["arm_link_relation"] == "LEAF_CLAIM_NOT_VERIFIABLE_FROM_EXACT_SOURCE_FIELDS", out
    assert out["leaf_claim_verification"] == "RETAINED_UNVERIFIED_WITH_LOCATOR", out
    assert "LEAF-QD-group1.tsv:line 42" in out["arm_link_locator"], out["arm_link_locator"]
    # and the claim itself is not thrown away: the candidate arm is preserved
    assert out["candidate_arm_indices"] == "0", out


# ------------------------------------------------------------------------------------------
# T2  A contradictory description CAN downgrade a label correspondence.
#     v1's monotonic rule ("never downgrade an exact match") is withdrawn: here the group title
#     equals armGroups[0].label byte-for-byte, but armGroups[0]'s own registered description
#     says the arm never enrolled, while the results group reports evaluable participants.
# ------------------------------------------------------------------------------------------
def t2a():
    ai = [arm("Phase II: MBG453", "EXPERIMENTAL",
              "This arm was not opened for enrollment."),
          arm("Phase II: MBG453 + PDR001", "EXPERIMENTAL", "combination")]
    out = v2.decide_link("Phase II: MBG453", "", ai, None)
    assert out["arm_link_state"] == "CONTESTED", out["arm_link_state"]
    assert out["arm_link_relation"].startswith("CONTRARY_DESCRIPTION:LABEL_IDENTITY_ONLY"), out
    assert "BOUND_ARM_REGISTERED_DESCRIPTION_STATES_IT_DID_NOT_ENROL" in out["contested_flags"], out


def t2b():
    # second downgrade shape: the label names arm 0, but the unique description identity in the
    # SAME record names arm 1. Two exact source fields disagree -> CONTESTED, neither discarded.
    ai = [arm("Cohort A", "EXPERIMENTAL", "single agent"),
          arm("Cohort B", "EXPERIMENTAL", "single agent plus chemotherapy")]
    out = v2.decide_link("Cohort A", "single agent plus chemotherapy", ai, None)
    assert out["arm_link_state"] == "CONTESTED", out["arm_link_state"]
    assert out["arm_link_relation"] == "LABEL_IDENTITY_AND_DESCRIPTION_IDENTITY_DISAGREE", out
    assert out["bound_arm_index"] == "", out
    assert out["candidate_arm_indices"] == "0|1", out


def t2c():
    # and the placebo-wording downgrade survives at the comparator layer, unresolved to a side
    ai = [arm("Placebo + Chemo", "EXPERIMENTAL", "placebo plus chemotherapy")]
    link = v2.decide_link("Placebo + Chemo", "Participants received placebo plus chemotherapy.",
                          ai, None)
    role, basis, stmt, assume, btype, flags = v2.decide_comparator(
        link, "Placebo + Chemo", "Participants received placebo plus chemotherapy.", ai,
        "ALL_ARMS_NON_CONTROL_TYPED", ["EXPERIMENTAL"])
    assert role == "CONTESTED", role
    assert "PLACEBO_OR_NOINT_GROUP_TEXT_VS_NON_COMPARATOR_BOUND_TYPE" in flags, flags
    assert btype == "EXPERIMENTAL", btype   # registry type kept verbatim, not overwritten


# ------------------------------------------------------------------------------------------
# T3  Duplicate candidates CANNOT select the first.
#     v1 bound with next((a for a in ai if a.label == claimed), arm) -- first hit wins.
# ------------------------------------------------------------------------------------------
def t3a():
    ai = [arm("Arm A", "EXPERIMENTAL", "d1"), arm("Arm A", "PLACEBO_COMPARATOR", "d2")]
    out = v2.decide_link("Arm A", "", ai, None)
    assert out["arm_link_state"] == "UNRESOLVED", out["arm_link_state"]
    assert out["bound_arm_index"] == "", out
    assert out["n_candidate_arms"] == 2, out
    assert out["candidate_arm_indices"] == "0|1", out


def t3b():
    # the same, reached through a leaf claim rather than the label path
    ai = [arm("Arm A", "EXPERIMENTAL", "d1"), arm("Arm A", "EXPERIMENTAL", "d2")]
    out = v2.decide_link("Dose Level 3", "", ai, leaf("Arm A", "bijection over the drug set"))
    assert out["arm_link_state"] == "UNRESOLVED", out["arm_link_state"]
    assert out["arm_link_relation"] == "LEAF_CLAIM_LEAF_LABEL_NOT_UNIQUE_IN_RECORD", out
    assert out["bound_arm_index"] == "", out
    assert out["candidate_arm_indices"] == "0|1", out


def t3d():
    # the delivered leaves use TWO different multi-arm separators ("; " and "|"). Both must be
    # split, or an aggregation of real arms is misread as one label absent from the record.
    ai = [arm("Ph I Monotherapy"), arm("Ph II Monotherapy (Arm A)"), arm("Combination")]
    out = v2.decide_link("Monotherapy 100 ug", "", ai,
                         leaf("Ph I Monotherapy|Ph II Monotherapy (Arm A)", "partition of arms"))
    assert out["leaf_claim_state"] == "LEAF_CLAIMS_MULTIPLE_ARMS", out
    assert out["arm_link_state"] == "UNRESOLVED", out
    assert out["candidate_arm_indices"] == "0|1", out
    out2 = v2.decide_link("Cohorts 1-2", "", ai, leaf("Ph I Monotherapy; Combination", "union"))
    assert out2["leaf_claim_state"] == "LEAF_CLAIMS_MULTIPLE_ARMS", out2
    assert out2["candidate_arm_indices"] == "0|2", out2


def t3c():
    # and the uniqueness helper itself never returns an index for a 2-candidate relation
    rel = {"LABEL_BYTE_EXACT": [3, 7]}
    idx, code, n, cands = v2.unique_or_none(rel, ["LABEL_BYTE_EXACT"])
    assert idx is None and n == 2 and cands == [3, 7], (idx, code, n, cands)


# ------------------------------------------------------------------------------------------
# T4  All-EXPERIMENTAL types WITHOUT proved membership do not confirm a NOT_CONTROL.
# ------------------------------------------------------------------------------------------
def t4a():
    ai = [arm("Arm 1"), arm("Arm 2"), arm("Arm 3")]
    link = v2.decide_link("Overall (all cohorts pooled)", "", ai, None)
    assert link["bound_arm_index"] == "", link      # membership unproved
    role, basis, stmt, assume, btype, flags = v2.decide_comparator(
        link, "Overall (all cohorts pooled)", "", ai, "ALL_ARMS_NON_CONTROL_TYPED",
        ["EXPERIMENTAL"] * 3)
    assert role == "UNKNOWN_IN_THIS_CACHE", role
    assert not role.startswith("NOT_CONTROL"), role
    assert stmt == "ALL_REGISTERED_ARMS_NON_COMPARATOR_TYPED_CONDITIONAL", stmt
    assert stmt.endswith("_CONDITIONAL"), stmt
    # the assumption is in the MACHINE state, not only in prose
    assert assume == ("ASSUMES_THIS_RESULTS_GROUP_IS_A_SUBSET_OF_THE_REGISTERED_ARM_SET"
                      "_MEMBERSHIP_UNPROVED"), assume


def t4b():
    # cardinality alone (one registered arm) is likewise conditional, never NOT_CONTROL
    ai = [arm("Everolimus")]
    link = v2.decide_link("Stage 2 expansion", "", ai, None)
    role, basis, stmt, assume, btype, flags = v2.decide_comparator(
        link, "Stage 2 expansion", "", ai, "ALL_ARMS_NON_CONTROL_TYPED", ["EXPERIMENTAL"])
    assert link["bound_arm_index"] == "", link
    assert role == "UNKNOWN_IN_THIS_CACHE", role
    assert stmt.endswith("_CONDITIONAL") and assume, (stmt, assume)


def t4c():
    # even when an arm IS bound, a non-comparator registered type does not prove absence of a
    # comparator role -- it yields NOT_ESTABLISHED (no evidence), and keeps the type verbatim
    ai = [arm("Arm A", "OTHER", "standard of care")]
    link = v2.decide_link("Arm A", "", ai, None)
    role, basis, stmt, assume, btype, flags = v2.decide_comparator(
        link, "Arm A", "", ai, "ALL_ARMS_NON_CONTROL_TYPED", ["OTHER"])
    assert role == "NOT_ESTABLISHED_IN_THIS_CACHE", role
    assert btype == "OTHER" and stmt == "BOUND_ARM_REGISTERED_TYPE_IS_OTHER", (btype, stmt)
    assert assume == "ASSUMES_LABEL_CORRESPONDENCE_IS_ARM_IDENTITY", assume


def t4d():
    # zero registered arms, absent arm type and placebo-vs-type stay three DISTINCT values
    link0 = v2.decide_link("Arm A", "", [], None)
    r0 = v2.decide_comparator(link0, "Arm A", "", [], "NO_ARMS_REGISTERED_IN_THIS_CACHE", [])
    assert link0["arm_link_state"] == "UNKNOWN_IN_THIS_CACHE", link0
    assert r0[0] == "UNKNOWN_IN_THIS_CACHE" and r0[2] == "NO_ARMS_REGISTERED_IN_THIS_CACHE", r0
    ai = [arm("Arm A", "", "")]
    link1 = v2.decide_link("Arm A", "", ai, None)
    r1 = v2.decide_comparator(link1, "Arm A", "", ai, "ARM_TYPE_ABSENT_IN_THIS_CACHE", [""])
    assert r1[0] == "UNKNOWN_IN_THIS_CACHE" and r1[2] == "BOUND_ARM_TYPE_ABSENT_IN_THIS_CACHE", r1
    assert r0[2] != r1[2], "zero-arms and absent-type must not collapse to one value"


# ------------------------------------------------------------------------------------------
# T5  An exact source-backed supported relation STAYS properly recorded (the repair does not
#     simply demote everything).
# ------------------------------------------------------------------------------------------
def t5a():
    ai = [arm("Placebo", "PLACEBO_COMPARATOR", "Participants received matching placebo."),
          arm("Drug X", "EXPERIMENTAL", "Participants received Drug X.")]
    link = v2.decide_link("Placebo", "Participants received matching placebo.", ai, None)
    assert link["arm_link_state"] == "SOURCE_CONFIRMED", link
    assert link["arm_link_relation"].startswith("TWO_INDEPENDENT_FIELD_IDENTITIES:"
                                                "LABEL_BYTE_EXACT+DESC_BYTE_EXACT"), link
    assert link["bound_arm_index"] == 0 and link["n_candidate_arms"] == 1, link
    role, basis, stmt, assume, btype, flags = v2.decide_comparator(
        link, "Placebo", "Participants received matching placebo.", ai, "MIXED_ARM_TYPES",
        ["PLACEBO_COMPARATOR", "EXPERIMENTAL"])
    assert role == "COMPARATOR_SUPPORTED_BY_SOURCE_CONFIRMED_ARM_TYPE", role
    assert btype == "PLACEBO_COMPARATOR" and assume == "", (btype, assume)
    assert flags == [] or "PLACEBO_CLAIM_WITHOUT" not in ";".join(flags), flags


def t5b():
    # a description-only identity is also a genuine explicit within-record relation, with a path
    ai = [arm("A1", "ACTIVE_COMPARATOR", "Docetaxel 75 mg/m2 every 3 weeks"),
          arm("A2", "EXPERIMENTAL", "Study drug every 3 weeks")]
    link = v2.decide_link("Chemotherapy", "Docetaxel 75 mg/m2 every 3 weeks", ai, None)
    assert link["arm_link_state"] == "SOURCE_CONFIRMED", link
    assert link["arm_link_relation"] == "DESCRIPTION_FIELD_IDENTITY:DESC_BYTE_EXACT", link
    assert link["arm_link_locator"] == (
        "protocolSection.armsInterventionsModule.armGroups[0].description"), link


def t5c():
    # case/whitespace-only label correspondence stays LABEL_MATCH, never SOURCE_CONFIRMED, and
    # its weaker standing is named in the assumption field rather than hidden
    ai = [arm("Arm  B", "PLACEBO_COMPARATOR", "")]
    link = v2.decide_link("arm b", "", ai, None)
    assert link["arm_link_state"] == "LABEL_MATCH", link
    assert link["arm_link_relation"] == "LABEL_IDENTITY_ONLY:LABEL_CASE_WS_FOLD", link
    role, basis, stmt, assume, btype, flags = v2.decide_comparator(
        link, "arm b", "", ai, "ALL_ARMS_CONTROL_TYPED", ["PLACEBO_COMPARATOR"])
    assert role == "COMPARATOR_PROPOSED_BY_LABEL_MATCHED_ARM_TYPE", role
    assert assume == "ASSUMES_LABEL_CORRESPONDENCE_IS_ARM_IDENTITY", assume


def t5d():
    # punctuation / dosage-unit differences are NOT normalised into equivalence
    ai = [arm("Cohort 3.2 mg/kg", "EXPERIMENTAL", "")]
    link = v2.decide_link("Cohort 3.2 kg/mg", "", ai, None)
    assert link["arm_link_state"] == "UNKNOWN_IN_THIS_CACHE", link
    assert link["bound_arm_index"] == "", link


for name, fn in [("T1_narrative_token_without_corroboration_cannot_confirm", t1),
                 ("T2a_contrary_arm_description_downgrades_a_byte_exact_label_match", t2a),
                 ("T2b_label_and_description_identities_disagree_is_CONTESTED", t2b),
                 ("T2c_placebo_wording_vs_registered_type_stays_CONTESTED", t2c),
                 ("T3a_two_identical_labels_do_not_select_the_first", t3a),
                 ("T3b_leaf_claimed_label_matching_two_arms_does_not_select_the_first", t3b),
                 ("T3c_unique_or_none_returns_no_index_for_two_candidates", t3c),
                 ("T3d_both_leaf_multi_arm_separators_are_split_not_read_as_one_label", t3d),
                 ("T4a_all_EXPERIMENTAL_without_membership_does_not_confirm_NOT_CONTROL", t4a),
                 ("T4b_cardinality_alone_is_a_conditional_type_statement", t4b),
                 ("T4c_bound_non_comparator_type_is_NOT_ESTABLISHED_not_proof_of_absence", t4c),
                 ("T4d_zero_arms_absent_type_and_contested_stay_distinct_values", t4d),
                 ("T5a_exact_source_backed_supported_relation_stays_recorded", t5a),
                 ("T5b_description_only_identity_is_confirmed_with_a_field_path", t5b),
                 ("T5c_case_whitespace_label_match_stays_LABEL_MATCH_with_its_assumption", t5c),
                 ("T5d_dosage_unit_difference_is_not_normalised_into_equivalence", t5d)]:
    case(name, fn)

width = max(len(n) for _, n, _ in RESULTS)
for res, name, detail in RESULTS:
    print("%-6s %s%s" % (res, name.ljust(width), ("  <- " + detail.strip()) if detail else ""))
bad = [r for r in RESULTS if r[0] != "PASS"]
print("\n%d tests, %d PASS, %d not-PASS (a skipped or deselected test would be neither)"
      % (len(RESULTS), len(RESULTS) - len(bad), len(bad)))
sys.exit(1 if bad else 0)
