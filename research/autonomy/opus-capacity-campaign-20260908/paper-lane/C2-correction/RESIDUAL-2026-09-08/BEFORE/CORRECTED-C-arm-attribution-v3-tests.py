"""Focused VALUE-BASED tests of the v3 rules (the finite root-admitted C2 correction of v2). No counts are asserted anywhere: each test builds a
small record by hand and asserts the machine VALUES the rules produce for it. There is no quota
and no census; these tests would still pass if every real row fell to UNKNOWN.

Scope: the five behaviours the v2 repair exists for, the two withdrawn rules, and the five root
C2 corrections v3 makes -- the count complement (T6), the cleared contested binding and its
comparator propagation (T2a/T2e), the zero-arm contract including comparator wording (T2f), the
transformed-excerpt evidence label (T7, a read-only value test over the four delivered leaves),
and the corrected evidence vocabulary and its identity assumptions (T5a/T5c/T8).
Not in scope: any suite over the 552 rows, any ablation, any amnesty, any source query, any
re-run of jobs 2/3, any new adjudication of a delivered row.
"""
import importlib.util, os, sys, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "v3", os.path.join(HERE, "CORRECTED-C-arm-attribution-v3-derive.py"))
v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v3)


def arm(label, type_="EXPERIMENTAL", desc=""):
    return {"label": label, "type": type_, "description": desc}


def leaf(label, narrative, src="LEAF-QD-group1.tsv", ln=42):
    return dict(leaf_source=src, leaf_row=ln, leaf_verdict="JOIN_RECOVERABLE",
                leaf_locator="LEAF-OUT/%s:line %d" % (src, ln),
                leaf_narrative_excerpt=narrative.replace("\n", " ")[:400],
                leaf_excerpt_original_chars=len(narrative),
                leaf_excerpt_transform=v3.NARRATIVE_TRANSFORM,
                leaf_excerpt_at_400_char_cap=("YES" if len(narrative) > 400 else "NO"),
                leaf_arm_label=label, leaf_arm_type="EXPERIMENTAL")


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
    out = v3.decide_link("Dose Level 1", "", ai, lf)
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
    out = v3.decide_link("Phase II: MBG453", "", ai, None)
    assert out["arm_link_state"] == "CONTESTED", out["arm_link_state"]
    assert out["arm_link_relation"].startswith(
        "CONTRARY_DESCRIPTION_BINDING_CLEARED:LABEL_FIELD_MATCH_ONLY"), out
    assert "BOUND_ARM_REGISTERED_DESCRIPTION_STATES_IT_DID_NOT_ENROL" in out["contested_flags"], out
    # root item 2: the BINDING IS CLEARED. v2 left bound_arm_index set here, violating its own
    # schema and the check "an arm is bound only by SOURCE_FIELD_MATCH or LABEL_MATCH".
    assert out["bound_arm_index"] == "", out
    # and nothing is discarded: candidate, count, contrary evidence and BOTH locators survive
    assert out["downgraded_candidate_arm_index"] == "0", out
    assert out["candidate_arm_indices"] == "0" and out["n_candidate_arms"] == 1, out
    assert out["contrary_description_locator"] == (
        "protocolSection.armsInterventionsModule.armGroups[0].description"), out
    assert out["contrary_description_evidence_excerpt"] == (
        "This arm was not opened for enrollment."), out
    assert "armGroups[0].label" in out["arm_link_locator"], out["arm_link_locator"]
    # comparator propagation: with the binding cleared the row is CONTESTED at the role layer too,
    # the registered type is NOT read through a cleared binding, and no identity is assumed
    role, basis, stmt, assume, btype, flags, role_assume, wording = v3.decide_comparator(
        out, "Phase II: MBG453", "", ai, "ALL_ARMS_NON_CONTROL_TYPED",
        ["EXPERIMENTAL", "EXPERIMENTAL"])
    assert role == "CONTESTED", role
    assert btype == "" and role_assume == "", (btype, role_assume)
    assert stmt == "ALL_REGISTERED_ARMS_NON_COMPARATOR_TYPED_CONDITIONAL", stmt
    assert assume.startswith("ASSUMES_THIS_RESULTS_GROUP_IS_A_SUBSET"), assume
    assert "BOUND_ARM_REGISTERED_DESCRIPTION_STATES_IT_DID_NOT_ENROL" in flags, flags


def t2b():
    # second downgrade shape: the label names arm 0, but the unique description identity in the
    # SAME record names arm 1. Two exact source fields disagree -> CONTESTED, neither discarded.
    ai = [arm("Cohort A", "EXPERIMENTAL", "single agent"),
          arm("Cohort B", "EXPERIMENTAL", "single agent plus chemotherapy")]
    out = v3.decide_link("Cohort A", "single agent plus chemotherapy", ai, None)
    assert out["arm_link_state"] == "CONTESTED", out["arm_link_state"]
    assert out["arm_link_relation"] == "LABEL_FIELD_MATCH_AND_DESCRIPTION_FIELD_MATCH_DISAGREE", out
    assert out["bound_arm_index"] == "", out
    assert out["candidate_arm_indices"] == "0|1", out


def t2c():
    # and the placebo-wording downgrade survives at the comparator layer, unresolved to a side
    ai = [arm("Placebo + Chemo", "EXPERIMENTAL", "placebo plus chemotherapy")]
    link = v3.decide_link("Placebo + Chemo", "Participants received placebo plus chemotherapy.",
                          ai, None)
    role, basis, stmt, assume, btype, flags, role_assume, wording = v3.decide_comparator(
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
    out = v3.decide_link("Arm A", "", ai, None)
    assert out["arm_link_state"] == "UNRESOLVED", out["arm_link_state"]
    assert out["bound_arm_index"] == "", out
    assert out["n_candidate_arms"] == 2, out
    assert out["candidate_arm_indices"] == "0|1", out


def t3b():
    # the same, reached through a leaf claim rather than the label path
    ai = [arm("Arm A", "EXPERIMENTAL", "d1"), arm("Arm A", "EXPERIMENTAL", "d2")]
    out = v3.decide_link("Dose Level 3", "", ai, leaf("Arm A", "bijection over the drug set"))
    assert out["arm_link_state"] == "UNRESOLVED", out["arm_link_state"]
    assert out["arm_link_relation"] == "LEAF_CLAIM_LEAF_LABEL_NOT_UNIQUE_IN_RECORD", out
    assert out["bound_arm_index"] == "", out
    assert out["candidate_arm_indices"] == "0|1", out


def t3d():
    # the delivered leaves use TWO different multi-arm separators ("; " and "|"). Both must be
    # split, or an aggregation of real arms is misread as one label absent from the record.
    ai = [arm("Ph I Monotherapy"), arm("Ph II Monotherapy (Arm A)"), arm("Combination")]
    out = v3.decide_link("Monotherapy 100 ug", "", ai,
                         leaf("Ph I Monotherapy|Ph II Monotherapy (Arm A)", "partition of arms"))
    assert out["leaf_claim_state"] == "LEAF_CLAIMS_MULTIPLE_ARMS", out
    assert out["arm_link_state"] == "UNRESOLVED", out
    assert out["candidate_arm_indices"] == "0|1", out
    out2 = v3.decide_link("Cohorts 1-2", "", ai, leaf("Ph I Monotherapy; Combination", "union"))
    assert out2["leaf_claim_state"] == "LEAF_CLAIMS_MULTIPLE_ARMS", out2
    assert out2["candidate_arm_indices"] == "0|2", out2


def t3c():
    # and the uniqueness helper itself never returns an index for a 2-candidate relation
    rel = {"LABEL_BYTE_EXACT": [3, 7]}
    idx, code, n, cands = v3.unique_or_none(rel, ["LABEL_BYTE_EXACT"])
    assert idx is None and n == 2 and cands == [3, 7], (idx, code, n, cands)


# ------------------------------------------------------------------------------------------
# T4  All-EXPERIMENTAL types WITHOUT proved membership do not confirm a NOT_CONTROL.
# ------------------------------------------------------------------------------------------
def t4a():
    ai = [arm("Arm 1"), arm("Arm 2"), arm("Arm 3")]
    link = v3.decide_link("Overall (all cohorts pooled)", "", ai, None)
    assert link["bound_arm_index"] == "", link      # membership unproved
    role, basis, stmt, assume, btype, flags, role_assume, wording = v3.decide_comparator(
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
    link = v3.decide_link("Stage 2 expansion", "", ai, None)
    role, basis, stmt, assume, btype, flags, role_assume, wording = v3.decide_comparator(
        link, "Stage 2 expansion", "", ai, "ALL_ARMS_NON_CONTROL_TYPED", ["EXPERIMENTAL"])
    assert link["bound_arm_index"] == "", link
    assert role == "UNKNOWN_IN_THIS_CACHE", role
    assert stmt.endswith("_CONDITIONAL") and assume, (stmt, assume)


def t4c():
    # even when an arm IS bound, a non-comparator registered type does not prove absence of a
    # comparator role -- it yields NOT_ESTABLISHED (no evidence), and keeps the type verbatim
    ai = [arm("Arm A", "OTHER", "standard of care")]
    link = v3.decide_link("Arm A", "", ai, None)
    role, basis, stmt, assume, btype, flags, role_assume, wording = v3.decide_comparator(
        link, "Arm A", "", ai, "ALL_ARMS_NON_CONTROL_TYPED", ["OTHER"])
    assert role == "NOT_ESTABLISHED_IN_THIS_CACHE", role
    assert btype == "OTHER" and stmt == "BOUND_ARM_REGISTERED_TYPE_IS_OTHER", (btype, stmt)
    assert assume == "ASSUMES_LABEL_FIELD_CORRESPONDENCE_IS_ARM_IDENTITY_UNPROVED", assume


def t4d():
    # zero registered arms, absent arm type and placebo-vs-type stay three DISTINCT values
    link0 = v3.decide_link("Arm A", "", [], None)
    r0 = v3.decide_comparator(link0, "Arm A", "", [], "NO_ARMS_REGISTERED_IN_THIS_CACHE", [])
    assert link0["arm_link_state"] == "UNKNOWN_IN_THIS_CACHE", link0
    assert r0[0] == "UNKNOWN_IN_THIS_CACHE" and r0[2] == "UNKNOWN_NO_ARMS_REGISTERED_IN_THIS_CACHE", r0
    ai = [arm("Arm A", "", "")]
    link1 = v3.decide_link("Arm A", "", ai, None)
    r1 = v3.decide_comparator(link1, "Arm A", "", ai, "ARM_TYPE_ABSENT_IN_THIS_CACHE", [""])
    assert r1[0] == "UNKNOWN_IN_THIS_CACHE" and r1[2] == "BOUND_ARM_TYPE_ABSENT_IN_THIS_CACHE", r1
    assert r0[2] != r1[2], "zero-arms and absent-type must not collapse to one value"


# ------------------------------------------------------------------------------------------
# T5  An exact source-backed supported relation STAYS properly recorded (the repair does not
#     simply demote everything).
# ------------------------------------------------------------------------------------------
def t5a():
    ai = [arm("Placebo", "PLACEBO_COMPARATOR", "Participants received matching placebo."),
          arm("Drug X", "EXPERIMENTAL", "Participants received Drug X.")]
    link = v3.decide_link("Placebo", "Participants received matching placebo.", ai, None)
    assert link["arm_link_state"] == "SOURCE_FIELD_MATCH", link
    assert link["arm_link_relation"].startswith("TWO_AGREEING_FIELD_MATCHES:"
                                                "LABEL_BYTE_EXACT+DESC_BYTE_EXACT"), link
    assert link["bound_arm_index"] == 0 and link["n_candidate_arms"] == 1, link
    role, basis, stmt, assume, btype, flags, role_assume, wording = v3.decide_comparator(
        link, "Placebo", "Participants received matching placebo.", ai, "MIXED_ARM_TYPES",
        ["PLACEBO_COMPARATOR", "EXPERIMENTAL"])
    assert role == "COMPARATOR_TYPE_INFERRED_VIA_SOURCE_FIELD_MATCH", role
    # v3 (root item 5): the registered type is still carried verbatim, but the row now NAMES the
    # unproved assumption that this results group IS that registered arm. In v2 this assumption
    # was empty for the strongest state, which read as an independent registry confirmation.
    assert btype == "PLACEBO_COMPARATOR", btype
    assert assume == "ASSUMES_TWO_AGREEING_SOURCE_FIELD_MATCHES_ARE_ARM_IDENTITY_UNPROVED", assume
    assert role_assume == assume, (role_assume, assume)
    assert flags == [] or "PLACEBO_CLAIM_WITHOUT" not in ";".join(flags), flags


def t5b():
    # a description-only identity is also a genuine explicit within-record relation, with a path
    ai = [arm("A1", "ACTIVE_COMPARATOR", "Docetaxel 75 mg/m2 every 3 weeks"),
          arm("A2", "EXPERIMENTAL", "Study drug every 3 weeks")]
    link = v3.decide_link("Chemotherapy", "Docetaxel 75 mg/m2 every 3 weeks", ai, None)
    assert link["arm_link_state"] == "SOURCE_FIELD_MATCH", link
    assert link["arm_link_relation"] == "DESCRIPTION_FIELD_MATCH_ONLY:DESC_BYTE_EXACT", link
    assert link["arm_link_locator"] == (
        "protocolSection.armsInterventionsModule.armGroups[0].description"), link


def t5c():
    # case/whitespace-only label correspondence stays LABEL_MATCH, never SOURCE_FIELD_MATCH, and
    # its weaker standing is named in the assumption field rather than hidden
    ai = [arm("Arm  B", "PLACEBO_COMPARATOR", "")]
    link = v3.decide_link("arm b", "", ai, None)
    assert link["arm_link_state"] == "LABEL_MATCH", link
    assert link["arm_link_relation"] == "LABEL_FIELD_MATCH_ONLY:LABEL_CASE_WS_FOLD", link
    role, basis, stmt, assume, btype, flags, role_assume, wording = v3.decide_comparator(
        link, "arm b", "", ai, "ALL_ARMS_CONTROL_TYPED", ["PLACEBO_COMPARATOR"])
    assert role == "COMPARATOR_PROPOSED_BY_LABEL_FIELD_MATCHED_ARM_TYPE", role
    assert assume == "ASSUMES_LABEL_FIELD_CORRESPONDENCE_IS_ARM_IDENTITY_UNPROVED", assume


def t5d():
    # punctuation / dosage-unit differences are NOT normalised into equivalence
    ai = [arm("Cohort 3.2 mg/kg", "EXPERIMENTAL", "")]
    link = v3.decide_link("Cohort 3.2 kg/mg", "", ai, None)
    assert link["arm_link_state"] == "UNKNOWN_IN_THIS_CACHE", link
    assert link["bound_arm_index"] == "", link


def t2e():
    # root item 2, second shape: a leaf claim that AGREED with the binding is not silently kept as
    # agreement after the binding is cleared; the prior verdict is preserved in its own column.
    ai = [arm("Cohort A", "EXPERIMENTAL", "No participants were enrolled in this cohort."),
          arm("Cohort B", "EXPERIMENTAL", "combination")]
    out = v3.decide_link("Cohort A", "", ai, leaf("Cohort A", "join recovered from the label"))
    assert out["arm_link_state"] == "CONTESTED", out
    assert out["bound_arm_index"] == "", out
    assert out["leaf_claim_verification"] == (
        "LEAF_CLAIM_NOT_ADJUDICATED_BOUND_ARM_DESCRIPTION_CONTRARY"), out
    assert out["leaf_claim_verification_before_downgrade"] == (
        "LEAF_CLAIM_AGREES_WITH_SOURCE_RELATION"), out
    assert out["leaf_claim_locator"] == "LEAF-OUT/LEAF-QD-group1.tsv:line 42", out


def t2f():
    # root item 3: ZERO registered arms with explicit comparator wording in the results-group text.
    # v2 evaluated the comparator-text proposal branches BEFORE the zero-arm branch, so this shape
    # could have produced a comparator role with no registered arm to attach it to.
    ai = []
    out = v3.decide_link("Placebo", "Participants received matching placebo.", ai, None)
    assert out["arm_link_state"] == "UNKNOWN_IN_THIS_CACHE", out
    role, basis, stmt, assume, btype, flags, role_assume, wording = v3.decide_comparator(
        out, "Placebo", "Participants received matching placebo.", ai,
        "NO_ARMS_REGISTERED_IN_THIS_CACHE", [])
    # link, registry type statement and comparator role are ALL unknown
    assert role == "UNKNOWN_IN_THIS_CACHE", role
    assert stmt == "UNKNOWN_NO_ARMS_REGISTERED_IN_THIS_CACHE", stmt
    assert stmt.startswith("UNKNOWN_") and out["arm_link_state"].startswith("UNKNOWN"), (stmt, out)
    # the group text is NOT lost: it is preserved as unverified evidence in its separate field
    assert wording == "GROUP_TEXT_PLACEBO_OR_SHAM_WORDING", wording
    assert "not evidence that no comparator existed" in basis, basis
    # and the same wording with control phrasing and a treatment sequence is recorded too
    w2 = v3.decide_comparator(
        v3.decide_link("Drug/placebo control", "", ai, None), "Drug/placebo control", "", ai,
        "NO_ARMS_REGISTERED_IN_THIS_CACHE", [])[7]
    assert "GROUP_TEXT_CONTROL_OR_COMPARATOR_WORDING" in w2, w2
    assert "GROUP_TITLE_TREATMENT_SEQUENCE_CONTAINING_A_PLACEBO_TOKEN" in w2, w2


def t6():
    # root item 1: the complement of an explicitly named state is total minus that state. v2 wrote
    # a hand-listed four-state subset instead and dropped LABEL_MATCH, reporting 362 of 552.
    states = (["SOURCE_FIELD_MATCH"] * 58 + ["LABEL_MATCH"] * 132 + ["PROPOSED"] * 337
              + ["UNRESOLVED"] * 11 + ["CONTESTED"] * 1 + ["UNKNOWN_IN_THIS_CACHE"] * 13)
    p = v3.partition_counts(states)
    assert p["total_rows"] == 552, p
    assert p["rows_in_matched_state"] == 58, p
    assert p["rows_not_in_matched_state"] == 494, p          # NOT 362
    assert p["partition_sums"] is True, p
    assert sum(p["rows_not_in_matched_state_by_state"].values()) == 494, p
    assert p["rows_not_in_matched_state_by_state"]["LABEL_MATCH"] == 132, p
    # the v2 shape, reproduced here only to show the size of the omission -- never used as a state
    v2_shape = sum(1 for x in states if x in
                   ("PROPOSED", "UNRESOLVED", "CONTESTED", "UNKNOWN_IN_THIS_CACHE"))
    assert v2_shape == 362 and p["rows_not_in_matched_state"] - v2_shape == 132, v2_shape
    # and the identity holds for any partition, not just this one
    q = v3.partition_counts(["A", "A", "B"], matched_state="A")
    assert (q["rows_in_matched_state"], q["rows_not_in_matched_state"]) == (2, 1), q
    assert q["partition_sums"] is True, q
    r = v3.partition_counts([], matched_state="A")
    assert r["total_rows"] == 0 and r["rows_not_in_matched_state"] == 0, r


def t7():
    # root item 4: the leaf narrative is a TRANSFORMED EXCERPT, not verbatim text. This reads the
    # four delivered leaves read-only and checks the recorded provenance against the values.
    idx = v3.load_leaves()
    assert idx, "no delivered leaf rows were loaded"
    at_cap = 0
    for k, rec in idx.items():
        assert len(rec["leaf_narrative_excerpt"]) <= 400, (k, len(rec["leaf_narrative_excerpt"]))
        assert "\n" not in rec["leaf_narrative_excerpt"], k
        assert rec["leaf_excerpt_transform"] == v3.NARRATIVE_TRANSFORM, k
        assert rec["leaf_excerpt_at_400_char_cap"] == (
            "YES" if rec["leaf_excerpt_original_chars"] > 400 else "NO"), k
        at_cap += rec["leaf_excerpt_at_400_char_cap"] == "YES"
    for token in ("NEWLINE_TO_SPACE", "CUT_AT_400_CHARS", "TSV_WRITE_NORMALISES",
                  "ORIGINAL_RETRIEVABLE_ONLY_VIA_leaf_claim_locator"):
        assert token in v3.NARRATIVE_TRANSFORM, token
    # observed, not asserted as a rule: no delivered narrative reaches the cap
    assert at_cap == 0, "narratives observed at the 400-char cap: %d" % at_cap
    # the locator that points at the untransformed original is retained
    any_rec = next(iter(idx.values()))
    assert any_rec["leaf_locator"].startswith("LEAF-OUT/"), any_rec["leaf_locator"]


def t8():
    # root item 5: two agreeing text fields of ONE record are not two independent sources, and the
    # comparator type read through that agreement carries its unproved identity assumption.
    ai = [arm("Placebo", "PLACEBO_COMPARATOR", "Participants received matching placebo."),
          arm("Drug X", "EXPERIMENTAL", "Participants received Drug X.")]
    link = v3.decide_link("Placebo", "Participants received matching placebo.", ai, None)
    role, basis, stmt, assume, btype, flags, role_assume, wording = v3.decide_comparator(
        link, "Placebo", "Participants received matching placebo.", ai, "MIXED_ARM_TYPES",
        ["PLACEBO_COMPARATOR", "EXPERIMENTAL"])
    assert "INDEPENDENT" not in link["arm_link_relation"], link["arm_link_relation"]
    assert "CONFIRMED" not in link["arm_link_state"], link["arm_link_state"]
    assert link["arm_link_state"] == "SOURCE_FIELD_MATCH", link
    assert role == "COMPARATOR_TYPE_INFERRED_VIA_SOURCE_FIELD_MATCH", role
    assert role_assume == "ASSUMES_TWO_AGREEING_SOURCE_FIELD_MATCHES_ARE_ARM_IDENTITY_UNPROVED", (
        role_assume)
    assert "not an independently validated clinical comparator" in basis, basis
    # the label-only strength is a DIFFERENT, weaker value with its own assumption
    ai2 = [arm("Placebo", "PLACEBO_COMPARATOR", "some other description")]
    link2 = v3.decide_link("Placebo", "", ai2, None)
    role2, _, _, _, _, _, role_assume2, _ = v3.decide_comparator(
        link2, "Placebo", "", ai2, "ALL_ARMS_CONTROL_TYPED", ["PLACEBO_COMPARATOR"])
    assert link2["arm_link_state"] == "LABEL_MATCH", link2
    assert role2 == "COMPARATOR_PROPOSED_BY_LABEL_FIELD_MATCHED_ARM_TYPE", role2
    assert role_assume2 == "ASSUMES_LABEL_FIELD_CORRESPONDENCE_IS_ARM_IDENTITY_UNPROVED", (
        role_assume2)
    assert role != role2 and role_assume != role_assume2, "the two strengths must not collapse"
    # explicit registry source-join verification is not established anywhere in this table
    assert v3.SOURCE_JOIN_VERIFICATION == (
        "NOT_ESTABLISHED_REGISTRY_JOIN_FIELDS_ABSENT_FROM_THIS_CACHE"), v3.SOURCE_JOIN_VERIFICATION


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
                 ("T5d_dosage_unit_difference_is_not_normalised_into_equivalence", t5d),
                 ("T2e_a_cleared_binding_does_not_leave_a_stale_leaf_agreement", t2e),
                 ("T2f_zero_arms_with_comparator_wording_stays_UNKNOWN_and_keeps_the_wording", t2f),
                 ("T6_complement_of_a_named_state_is_total_minus_that_state_494_not_362", t6),
                 ("T7_leaf_narrative_is_a_labelled_transformed_excerpt_not_verbatim_text", t7),
                 ("T8_agreeing_text_fields_are_not_independent_confirmation_of_identity", t8)]:
    case(name, fn)

width = max(len(n) for _, n, _ in RESULTS)
for res, name, detail in RESULTS:
    print("%-6s %s%s" % (res, name.ljust(width), ("  <- " + detail.strip()) if detail else ""))
bad = [r for r in RESULTS if r[0] != "PASS"]
print("\n%d tests, %d PASS, %d not-PASS (a skipped or deselected test would be neither)"
      % (len(RESULTS), len(RESULTS) - len(bad), len(bad)))
sys.exit(1 if bad else 0)
