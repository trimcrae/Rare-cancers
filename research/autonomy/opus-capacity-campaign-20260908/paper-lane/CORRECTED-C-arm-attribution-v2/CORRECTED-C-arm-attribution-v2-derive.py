"""CORRECTED-C v2 (arm attribution) -- NEW EXPLICITLY VERSIONED SIBLING producer.

It does NOT overwrite and does NOT re-run Job 3
(`CURATION-endpoint-arm-attribution-derive.py`) or CORRECTED-C v1
(`CORRECTED-C-arm-attribution/CORRECTED-C-arm-attribution-derive.py`).
Both prior maps are read ONLY as prior-state indices for the change map. Their historical
claims stand as made; nothing here rewrites them.

WHY v2 EXISTS -- the defect in v1 that this repairs
---------------------------------------------------
v1 lines 107-130 defined

    CORROBORATION = ('description','interventionnames','bijection','complement','partition',
                     'enumerat','verbatim','reproduced','drug set','elimination')

and returned CONFIRMED when ANY of those tokens occurred anywhere in a leaf's free-text
narrative field. That predicate establishes only WHAT A LEAF NARRATIVE MENTIONED. It does not
establish that a source relation was verified: a narrative reading "description absent" or
"armGroups[*].interventionNames are identical, so no field distinguishes them" satisfies it.
314 rows in the v1 map were CONFIRMED by that token test
(arm_link_evidence_code = LEAF_WITHIN_RECORD_RELATION).

v2 removes the token-matching predicate entirely. NOTHING is confirmed by narrative wording.
Every state is computed from EXACT FIELDS OF THE CACHED SOURCE RECORD, and where the exact
source evidence is not present in this cache the leaf's claim is RETAINED as PROPOSED /
UNVERIFIED together with its locator, never promoted and never silently dropped.

There is no confirmation quota. v1's 503 CONFIRMED is not a target. A substantial fall in
confirmation is the expected and correct consequence of deleting a token test.

WHAT v2 CHANGES, RULE BY RULE
-----------------------------
 1. Leaf narrative tokens can never confirm. `verify_leaf_claim` reads the leaf's claimed arm
    LABEL and checks it against the record's arm labels; the narrative text is carried through
    verbatim as evidence-for-a-human but is never parsed for meaning.
 2. Exact / case-and-whitespace LABEL correspondence is a DISTINCT state (LABEL_MATCH), not
    source-confirmed group-arm identity. SOURCE_CONFIRMED needs two independent exact field
    identities agreeing on one arm, or a unique description-field identity.
 3. The v1 monotonic rule ("a leaf may only strengthen; never downgrade an exact match") is
    withdrawn. Contrary source evidence downgrades: a unique description identity pointing to a
    different arm, a bound arm whose own description says it never enrolled, or placebo/control
    wording against the bound arm's registered type, all yield CONTESTED.
 4. v1's `next((a for a in ai if ...), arm)` arm binding is withdrawn. Every relation reports the
    EXACT NUMBER of compatible candidates; a relation with 2+ candidates binds nothing and is
    UNRESOLVED with all candidates preserved. The first candidate is never selected.
 5. Cardinality (one registered arm) and a uniform registered-arm TYPE are CONDITIONAL type
    statements about the registered arm set, not an unconditional NOT_CONTROL for a results group
    whose membership in that set is unproved. The assumption is written into the machine state
    (`registry_type_statement_assumption`), not only into prose. The token NOT_CONTROL does not
    appear as a state anywhere in this table.
 6. Clinical comparator role and registry arm type are DISTINCT columns. EXPERIMENTAL / OTHER is
    NEVER read as proof that a group has no comparator role; it yields comparator_role =
    NOT_ESTABLISHED_IN_THIS_CACHE, which asserts absence of evidence, not evidence of absence.
    The registered type is carried VERBATIM.
 7. zero registered arms -> UNKNOWN; arm type absent -> UNKNOWN; placebo/control wording against a
    non-comparator bound type -> CONTESTED. These stay four separate machine values.

Scope limits, unchanged from v1: no whole-cache audit, no new source query, no network call, no
re-run of job 3, no response rate, no unique-patient total, no control comparison, no manuscript
edit. The endpoint paper stays parked. `resultsSection.participantFlowModule` and
`armsInterventionsModule.interventions[].armGroupLabels` -- the registry's own explicit join
fields -- are ABSENT from this cache by established fact and are NOT fetched here; their absence
is the reason many rows can only ever be PROPOSED.
"""
import collections, csv, json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(BASE)
CACHE = ("/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/"
         "scratchpad/ctg-cache-216bd1b5")
V1_DIR = os.path.join(LANE, "CORRECTED-C-arm-attribution")
V1_MAP = os.path.join(V1_DIR, "CORRECTED-C-arm-attribution-map.tsv")
JOB3_MAP = os.path.join(LANE, "CURATION-endpoint-arm-attribution-map.tsv")
LEAVES = [(os.path.join(LANE, "LEAF-OUT", "LEAF-QD-group0.tsv"), "join_field", "join_class",
           "recovered_arm_label", "recovered_arm_type"),
          (os.path.join(LANE, "LEAF-OUT", "LEAF-QD-group1.tsv"), "field_used", "verdict",
           "recovered_arm_label", "recovered_armGroupType"),
          (os.path.join(LANE, "LEAF-OUT", "LEAF-QD-group2.tsv"), "join_field", "verdict",
           "recovered_arm_label", "recovered_arm_type"),
          (os.path.join(LANE, "LEAF-OUT", "LEAF-QD-group3.tsv"), "evidence_field", "verdict",
           "recovered_arm_label", "recovered_arm_type")]

BOR = [f"ctg_results_bor_{e}" for e in ("1999_2009","2010_2013","2014_2017","2018_2021","2022_2026")]
PLA = [f"ctg_placebo_onc_{e}" for e in ("1999_2009","2010_2013","2014_2017","2018_2021","2022_2026")]
FILES = BOR + PLA

# ---- Job 3's row-selection logic, reproduced UNCHANGED so the three tables join key-for-key ----
CATEGORY = {"CR": re.compile(r"^\s*(complete response|complete remission|CR)\b", re.I),
            "PR": re.compile(r"^\s*(partial response|partial remission|PR)\b", re.I),
            "SD": re.compile(r"^\s*(stable disease|SD)\b", re.I),
            "PD": re.compile(r"^\s*(progressive disease|disease progression|PD)\b", re.I)}


def payload(name):
    with open(os.path.join(CACHE, name + ".txt"), encoding="utf-8") as fh:
        raw = fh.read()
    return json.loads(raw.split("=" * 70, 1)[1])


def cells_for_groups(om):
    per = collections.defaultdict(dict)
    for cl in om.get("classes") or []:
        for cat in cl.get("categories") or []:
            label = next((k for k, rx in CATEGORY.items() if rx.match(cat.get("title") or "")), None)
            if not label:
                continue
            for meas in cat.get("measurements") or []:
                gid, val = meas.get("groupId"), meas.get("value")
                if gid is None or val is None:
                    continue
                try:
                    f = float(val)
                except (TypeError, ValueError):
                    continue
                if f.is_integer():
                    per[gid][label] = int(f)
    return per


# ---- the ONLY normalisation permitted anywhere in v2: case and whitespace ----------------------
# Punctuation, hyphens, brackets, dosage units and spelling are NOT normalised.
def fold(s):
    return re.sub(r"\s+", "", (s or "")).casefold()


CONTROL_TYPES = {"PLACEBO_COMPARATOR", "SHAM_COMPARATOR", "NO_INTERVENTION", "ACTIVE_COMPARATOR"}
NONCONTROL_TYPES = {"EXPERIMENTAL", "OTHER"}
PLACEBO_TXT = re.compile(r"\bplacebo|\bsham\b|\bvehicle control\b", re.I)
NOINT_TXT = re.compile(r"\bno intervention\b|\bobservation only\b|\bwatchful waiting\b|"
                       r"\buntreated control\b", re.I)
CONTROL_TXT = re.compile(r"\bcontrol\b|\bcomparator\b", re.I)
CONTROL_DESC = re.compile(r"\bcontrol (arm|group|drug)\b|\brandomi[sz]ed to (the )?(control|placebo)\b", re.I)
PLACEBO_SEQUENCE = re.compile(r"[A-Za-z0-9]\s*/\s*placebo", re.I)
# a bound arm whose OWN registered description says it never enrolled contradicts a results group
# that reports evaluable participants. This is contrary SOURCE evidence, not narrative wording.
NOT_ENROLLED_DESC = re.compile(
    r"\bwas not opened for enrollment\b|\bnot opened for enrolment\b|"
    r"\bno participants (were )?(enrolled|randomi[sz]ed)\b|"
    r"\bthis (arm|cohort|group) was not (opened|enrolled)\b|"
    r"\bclosed (prior to|before) enroll?ment\b", re.I)


# ================================================================================================
# 1. EXACT SOURCE-FIELD RELATIONS.  Each returns the FULL candidate index list -- never a pick.
# ================================================================================================
def source_relations(gtitle, gdesc, armgroups):
    """Every relation is an equality between two exact fields of the SAME cached record.

    Field paths (locators):
      results group title       resultsSection.outcomeMeasuresModule.outcomeMeasures[*].groups[*].title
      results group description ...groups[*].description
      registered arm label      protocolSection.armsInterventionsModule.armGroups[i].label
      registered arm descr.     protocolSection.armsInterventionsModule.armGroups[i].description

    Returns {relation_code: [indices]} with the EXACT candidate list for each relation, so a
    caller can require |candidates| == 1 rather than taking the first.
    """
    rel = {}
    gt, gd = gtitle or "", gdesc or ""
    rel["LABEL_BYTE_EXACT"] = [i for i, a in enumerate(armgroups)
                               if gt and (a.get("label") or "") == gt]
    rel["LABEL_CASE_WS_FOLD"] = [i for i, a in enumerate(armgroups)
                                 if fold(gt) and fold(a.get("label")) == fold(gt)]
    rel["DESC_BYTE_EXACT"] = [i for i, a in enumerate(armgroups)
                              if gd and (a.get("description") or "") == gd]
    rel["DESC_CASE_WS_FOLD"] = [i for i, a in enumerate(armgroups)
                                if fold(gd) and fold(a.get("description")) == fold(gd)]
    return rel


def unique_or_none(rel, codes):
    """(index, relation_code, n_candidates, candidate_indices).

    index is not None ONLY when a relation has EXACTLY ONE candidate. Two compatible arms never
    resolve to the first: they resolve to nothing, with both preserved."""
    for c in codes:
        idx = rel.get(c) or []
        if len(idx) == 1:
            return idx[0], c, 1, idx
        if len(idx) > 1:
            return None, c + "_AMBIGUOUS", len(idx), idx
    return None, "", 0, []


# ================================================================================================
# 2. LEAF CLAIMS.  The narrative is NEVER parsed for meaning; only the claimed LABEL is checked.
# ================================================================================================
def verify_leaf_claim(leafrec, armgroups):
    """Check the leaf's claimed arm LABEL against the record's exact arm labels.

    Returns (claim_state, claim_indices, locator). claim_state is one of
      NO_LEAF                            -- no leaf row for this key
      LEAF_CLAIMS_NO_ARM                 -- leaf recovered no arm label
      LEAF_LABEL_RESOLVES_UNIQUELY       -- exactly one registered arm carries that exact label
      LEAF_LABEL_NOT_UNIQUE_IN_RECORD    -- 2+ registered arms carry it: ambiguity is preserved
      LEAF_LABEL_ABSENT_FROM_RECORD      -- contradicted by the record
      LEAF_CLAIMS_MULTIPLE_ARMS          -- an aggregation of arms, which is not an identity
    Resolving a label is NOT confirmation of the group-arm relation: it only says the leaf named
    a real, unique arm. Confirmation still requires a source relation from `source_relations`.
    """
    if not leafrec:
        return "NO_LEAF", [], ""
    raw = (leafrec.get("leaf_arm_label") or "").strip()
    if not raw:
        return "LEAF_CLAIMS_NO_ARM", [], leafrec.get("leaf_locator", "")
    # the four delivered leaves are not uniform: QD-group0 separates multiple recovered arms with
    # "; " while QD-group1/2/3 use "|". BOTH are split, or a multi-arm aggregation would be
    # misread as a single label that is absent from the record (found by inspecting RUN-04 values).
    parts = [p.strip() for p in re.split(r"[;|]", raw) if p.strip()]
    loc = leafrec.get("leaf_locator", "")
    if len(parts) > 1:
        idx = []
        for p in parts:
            idx += [i for i, a in enumerate(armgroups) if (a.get("label") or "") == p]
        return "LEAF_CLAIMS_MULTIPLE_ARMS", sorted(set(idx)), loc
    hit = [i for i, a in enumerate(armgroups) if (a.get("label") or "") == parts[0]]
    if len(hit) == 1:
        return "LEAF_LABEL_RESOLVES_UNIQUELY", hit, loc
    if len(hit) > 1:
        return "LEAF_LABEL_NOT_UNIQUE_IN_RECORD", hit, loc
    fhit = [i for i, a in enumerate(armgroups) if fold(a.get("label")) == fold(parts[0])]
    if len(fhit) == 1:
        return "LEAF_LABEL_RESOLVES_UNIQUELY", fhit, loc
    if len(fhit) > 1:
        return "LEAF_LABEL_NOT_UNIQUE_IN_RECORD", fhit, loc
    return "LEAF_LABEL_ABSENT_FROM_RECORD", [], loc


# ================================================================================================
# 3. THE LINK DECISION.  Pure function of exact source fields + the leaf's claimed label.
# ================================================================================================
def decide_link(gtitle, gdesc, armgroups, leafrec):
    """Returns a dict of machine values. Never reads a leaf narrative for meaning."""
    out = dict(arm_link_state="", arm_link_relation="", arm_link_source="", arm_link_locator="",
               bound_arm_index="", n_candidate_arms=0, candidate_arm_indices="",
               leaf_claim_state="", leaf_claim_locator="", leaf_claim_verification="",
               contested_flags=[])
    n = len(armgroups)
    claim_state, claim_idx, claim_loc = verify_leaf_claim(leafrec, armgroups)
    out["leaf_claim_state"] = claim_state
    out["leaf_claim_locator"] = claim_loc

    if n == 0:
        out.update(arm_link_state="UNKNOWN_IN_THIS_CACHE",
                   arm_link_relation="NO_ARM_GROUPS_REGISTERED_IN_THIS_CACHE",
                   arm_link_source="SOURCE_RECORD",
                   arm_link_locator="protocolSection.armsInterventionsModule.armGroups=[] (absent)")
        out["leaf_claim_verification"] = (
            "NOT_VERIFIABLE_NO_REGISTERED_ARMS" if claim_state != "NO_LEAF" else "")
        return out

    rel = source_relations(gtitle, gdesc, armgroups)
    lab_i, lab_code, lab_n, lab_idx = unique_or_none(rel, ["LABEL_BYTE_EXACT", "LABEL_CASE_WS_FOLD"])
    des_i, des_code, des_n, des_idx = unique_or_none(rel, ["DESC_BYTE_EXACT", "DESC_CASE_WS_FOLD"])
    AG = "protocolSection.armsInterventionsModule.armGroups"

    # ---- contrary source evidence: a unique description identity naming a DIFFERENT arm --------
    if lab_i is not None and des_i is not None and lab_i != des_i:
        out.update(arm_link_state="CONTESTED",
                   arm_link_relation="LABEL_IDENTITY_AND_DESCRIPTION_IDENTITY_DISAGREE",
                   arm_link_source="SOURCE_RECORD", n_candidate_arms=2,
                   candidate_arm_indices="%d|%d" % (lab_i, des_i),
                   arm_link_locator="%s[%d].label==groups[*].title vs %s[%d].description"
                                    "==groups[*].description" % (AG, lab_i, AG, des_i))
        out["contested_flags"].append("LABEL_AND_DESCRIPTION_SOURCE_IDENTITIES_NAME_DIFFERENT_ARMS")
        out["leaf_claim_verification"] = ("LEAF_CLAIM_NOT_ADJUDICATED_SOURCE_FIELDS_CONFLICT"
                                          if claim_state != "NO_LEAF" else "")
        return out

    # ---- two independent exact field identities agreeing on one arm = SOURCE_CONFIRMED ---------
    if lab_i is not None and des_i is not None and lab_i == des_i:
        out.update(arm_link_state="SOURCE_CONFIRMED",
                   arm_link_relation="TWO_INDEPENDENT_FIELD_IDENTITIES:%s+%s" % (lab_code, des_code),
                   arm_link_source="SOURCE_RECORD", bound_arm_index=lab_i, n_candidate_arms=1,
                   candidate_arm_indices=str(lab_i),
                   arm_link_locator="%s[%d].label and %s[%d].description" % (AG, lab_i, AG, lab_i))
    # ---- a unique description-field identity alone is an explicit within-record identity -------
    elif lab_n == 0 and des_i is not None:
        out.update(arm_link_state="SOURCE_CONFIRMED",
                   arm_link_relation="DESCRIPTION_FIELD_IDENTITY:%s" % des_code,
                   arm_link_source="SOURCE_RECORD", bound_arm_index=des_i, n_candidate_arms=1,
                   candidate_arm_indices=str(des_i),
                   arm_link_locator="%s[%d].description" % (AG, des_i))
    # ---- label correspondence ALONE: useful evidence, but not source-confirmed identity --------
    elif lab_i is not None:
        out.update(arm_link_state="LABEL_MATCH",
                   arm_link_relation="LABEL_IDENTITY_ONLY:%s" % lab_code,
                   arm_link_source="SOURCE_RECORD", bound_arm_index=lab_i, n_candidate_arms=1,
                   candidate_arm_indices=str(lab_i),
                   arm_link_locator="%s[%d].label" % (AG, lab_i))
    # ---- ambiguity is preserved; the first candidate is never taken ----------------------------
    elif lab_n > 1:
        out.update(arm_link_state="UNRESOLVED", arm_link_relation=lab_code,
                   arm_link_source="SOURCE_RECORD", n_candidate_arms=lab_n,
                   candidate_arm_indices="|".join(str(i) for i in lab_idx),
                   arm_link_locator="%s[%s].label" % (AG, ",".join(str(i) for i in lab_idx)))
    elif des_n > 1:
        out.update(arm_link_state="UNRESOLVED", arm_link_relation=des_code,
                   arm_link_source="SOURCE_RECORD", n_candidate_arms=des_n,
                   candidate_arm_indices="|".join(str(i) for i in des_idx),
                   arm_link_locator="%s[%s].description" % (AG, ",".join(str(i) for i in des_idx)))
    else:
        # No exact source relation exists in this cache. The leaf claim is RETAINED, unpromoted.
        if claim_state == "LEAF_LABEL_RESOLVES_UNIQUELY":
            out.update(arm_link_state="PROPOSED",
                       arm_link_relation="LEAF_CLAIM_NOT_VERIFIABLE_FROM_EXACT_SOURCE_FIELDS",
                       arm_link_source="DELIVERED_LEAF:" + leafrec["leaf_source"],
                       n_candidate_arms=1, candidate_arm_indices=str(claim_idx[0]),
                       arm_link_locator="%s; candidate %s[%d].label" % (claim_loc, AG, claim_idx[0]))
        elif claim_state in ("LEAF_CLAIMS_MULTIPLE_ARMS", "LEAF_LABEL_NOT_UNIQUE_IN_RECORD"):
            out.update(arm_link_state="UNRESOLVED", arm_link_relation="LEAF_CLAIM_" + claim_state,
                       arm_link_source="DELIVERED_LEAF:" + leafrec["leaf_source"],
                       n_candidate_arms=len(claim_idx),
                       candidate_arm_indices="|".join(str(i) for i in claim_idx),
                       arm_link_locator=claim_loc)
        elif claim_state == "LEAF_LABEL_ABSENT_FROM_RECORD":
            out.update(arm_link_state="CONTESTED",
                       arm_link_relation="LEAF_CLAIMED_ARM_LABEL_ABSENT_FROM_THIS_RECORD",
                       arm_link_source="DELIVERED_LEAF:" + leafrec["leaf_source"],
                       n_candidate_arms=0, arm_link_locator=claim_loc)
            out["contested_flags"].append("LEAF_CLAIMED_ARM_LABEL_NOT_PRESENT_IN_REGISTERED_ARMS")
        else:
            out.update(arm_link_state="UNKNOWN_IN_THIS_CACHE",
                       arm_link_relation="NO_EXACT_SOURCE_RELATION_IN_THIS_CACHE",
                       arm_link_source="SOURCE_RECORD", n_candidate_arms=0,
                       arm_link_locator="%s[*].label/.description compared to groups[*].title/"
                                        ".description; no equality holds" % AG)

    # ---- how the leaf claim stands against whatever the source actually said ------------------
    if claim_state == "NO_LEAF":
        out["leaf_claim_verification"] = ""
    elif out["bound_arm_index"] != "" and claim_idx and out["bound_arm_index"] in claim_idx:
        out["leaf_claim_verification"] = "LEAF_CLAIM_AGREES_WITH_SOURCE_RELATION"
    elif out["bound_arm_index"] != "" and claim_idx:
        out["leaf_claim_verification"] = "LEAF_CLAIM_DISAGREES_WITH_SOURCE_RELATION"
        out["contested_flags"].append("LEAF_CLAIMED_ARM_DIFFERS_FROM_SOURCE_BOUND_ARM")
    elif out["arm_link_state"] == "PROPOSED":
        out["leaf_claim_verification"] = "RETAINED_UNVERIFIED_WITH_LOCATOR"
    else:
        out["leaf_claim_verification"] = "NOT_VERIFIABLE_IN_THIS_CACHE"

    # ---- contrary evidence inside the bound arm's OWN registered description -------------------
    if out["bound_arm_index"] != "":
        bd = armgroups[out["bound_arm_index"]].get("description") or ""
        if NOT_ENROLLED_DESC.search(bd):
            out["contested_flags"].append("BOUND_ARM_REGISTERED_DESCRIPTION_STATES_IT_DID_NOT_ENROL")
            out["arm_link_state"] = "CONTESTED"
            out["arm_link_relation"] = ("CONTRARY_DESCRIPTION:" + out["arm_link_relation"])
    return out


# ================================================================================================
# 4. COMPARATOR ROLE (clinical) and REGISTRY TYPE STATEMENT (registration) -- DISTINCT columns
# ================================================================================================
def decide_comparator(link, gtitle, gdesc, armgroups, arm_set_type_state, types):
    """comparator_role never asserts 'not a control'. A non-comparator registered type yields
    NOT_ESTABLISHED_IN_THIS_CACHE: absence of evidence for a comparator role, not evidence that
    the group had none. The registered type is carried verbatim in a separate column."""
    bound = link["bound_arm_index"]
    btype = (armgroups[bound].get("type") or "") if bound != "" else ""
    seq = bool(PLACEBO_SEQUENCE.search(gtitle or ""))
    t_pla = bool(PLACEBO_TXT.search(gtitle or "") or PLACEBO_TXT.search(gdesc or "")) and not seq
    t_noi = bool(NOINT_TXT.search(gtitle or ""))
    t_ctl = bool(CONTROL_TXT.search(gtitle or "") or CONTROL_DESC.search(gdesc or ""))
    flags = list(link["contested_flags"])
    linked = link["arm_link_state"] in ("SOURCE_CONFIRMED", "LABEL_MATCH") and bound != ""

    # registry type statement -- separate from any clinical role, with its assumption named
    if len(armgroups) == 0:
        stmt, assume = "NO_ARMS_REGISTERED_IN_THIS_CACHE", ""
    elif linked and btype:
        stmt = "BOUND_ARM_REGISTERED_TYPE_IS_%s" % btype
        assume = ("ASSUMES_LABEL_CORRESPONDENCE_IS_ARM_IDENTITY"
                  if link["arm_link_state"] == "LABEL_MATCH" else "")
    elif linked and not btype:
        stmt, assume = "BOUND_ARM_TYPE_ABSENT_IN_THIS_CACHE", ""
    elif arm_set_type_state == "ALL_ARMS_NON_CONTROL_TYPED":
        stmt = "ALL_REGISTERED_ARMS_NON_COMPARATOR_TYPED_CONDITIONAL"
        assume = "ASSUMES_THIS_RESULTS_GROUP_IS_A_SUBSET_OF_THE_REGISTERED_ARM_SET_MEMBERSHIP_UNPROVED"
    elif arm_set_type_state == "ALL_ARMS_CONTROL_TYPED":
        stmt = "ALL_REGISTERED_ARMS_COMPARATOR_TYPED_CONDITIONAL"
        assume = "ASSUMES_THIS_RESULTS_GROUP_IS_A_SUBSET_OF_THE_REGISTERED_ARM_SET_MEMBERSHIP_UNPROVED"
    elif arm_set_type_state == "ARM_TYPE_ABSENT_IN_THIS_CACHE":
        stmt, assume = "ARM_TYPE_ABSENT_IN_THIS_CACHE", ""
    else:
        stmt, assume = "ARM_SET_TYPE_NOT_UNIFORM_NO_TYPE_STATEMENT_POSSIBLE", ""

    # clinical comparator role
    if linked and btype in CONTROL_TYPES:
        if link["arm_link_state"] == "SOURCE_CONFIRMED":
            role = "COMPARATOR_SUPPORTED_BY_SOURCE_CONFIRMED_ARM_TYPE"
            basis = "arm %d bound by %s; registered type %s" % (bound, link["arm_link_relation"], btype)
        else:
            role = "COMPARATOR_PROPOSED_BY_LABEL_MATCHED_ARM_TYPE"
            basis = ("arm %d bound by label correspondence only (%s); registered type %s; the "
                     "group-arm identity is not independently source-confirmed"
                     % (bound, link["arm_link_relation"], btype))
    elif linked and btype in NONCONTROL_TYPES and (t_pla or t_noi):
        role = "CONTESTED"
        basis = ("group record states placebo/no-intervention while the bound registered arm %d "
                 "'%s' is typed %s verbatim; neither field wins and neither is discarded"
                 % (bound, armgroups[bound].get("label") or "", btype))
        flags.append("PLACEBO_OR_NOINT_GROUP_TEXT_VS_NON_COMPARATOR_BOUND_TYPE")
    elif linked and btype in NONCONTROL_TYPES and t_ctl:
        role = "CONTESTED"
        basis = ("group record uses control/comparator wording while the bound registered arm %d "
                 "is typed %s verbatim; registry type does not decide the clinical role"
                 % (bound, btype))
        flags.append("CONTROL_WORDING_VS_NON_COMPARATOR_BOUND_TYPE")
    elif linked and btype in NONCONTROL_TYPES:
        role = "NOT_ESTABLISHED_IN_THIS_CACHE"
        basis = ("bound arm %d registered type %s (verbatim). A registered type of EXPERIMENTAL/"
                 "OTHER is not evidence that this group had no comparator role; no comparator "
                 "evidence exists in this cache either way" % (bound, btype))
    elif linked:
        role = "UNKNOWN_IN_THIS_CACHE"
        basis = "bound arm %d carries no type field in this cache" % bound
    elif link["arm_link_state"] == "CONTESTED":
        role = "CONTESTED"
        basis = "the group-arm link itself is contested: %s" % link["arm_link_relation"]
    elif t_pla:
        role, basis = ("COMPARATOR_PROPOSED_BY_GROUP_TEXT_PLACEBO",
                       "group record states placebo/sham; no source-confirmed registry link")
    elif t_noi:
        role, basis = ("COMPARATOR_PROPOSED_BY_GROUP_TEXT_NO_INTERVENTION",
                       "group record states no-intervention/observation; no source-confirmed link")
    elif t_ctl:
        role, basis = ("COMPARATOR_PROPOSED_BY_GROUP_TEXT_UNSPECIFIED",
                       "group record says control/comparator without naming placebo; no link")
    elif len(armgroups) == 0:
        role, basis = ("UNKNOWN_IN_THIS_CACHE",
                       "zero registered arm groups: comparator role is UNKNOWN, not absent")
    else:
        role, basis = ("UNKNOWN_IN_THIS_CACHE",
                       "no source-confirmed arm link and no comparator wording in the group record")

    if seq:
        flags.append("GROUP_TITLE_IS_A_TREATMENT_SEQUENCE_CONTAINING_A_PLACEBO_TOKEN")
    if role.startswith("COMPARATOR_PROPOSED_BY_GROUP_TEXT_PLACEBO") and not any(
            t in {"PLACEBO_COMPARATOR", "SHAM_COMPARATOR"} for t in types):
        flags.append("PLACEBO_CLAIM_WITHOUT_ANY_PLACEBO_TYPED_ARM_IN_THIS_CACHE")
    return role, basis, stmt, assume, btype, flags


# ================================================================================================
def load_leaves():
    ov = {}
    for path, ffield, vfield, lab, typ in LEAVES:
        src = os.path.basename(path)
        with open(path, encoding="utf-8") as fh:
            for ln, r in enumerate(csv.DictReader(fh, delimiter="\t"), start=2):
                k = (r["nct"], r["om_title"], r["group_title"])
                rec = dict(leaf_source=src, leaf_row=ln, leaf_verdict=r.get(vfield, ""),
                           leaf_locator="LEAF-OUT/%s:line %d" % (src, ln),
                           leaf_narrative=(r.get(ffield) or "").replace("\n", " ")[:400],
                           leaf_arm_label=r.get(lab, "") or "", leaf_arm_type=r.get(typ, "") or "")
                if k in ov and ov[k]["leaf_source"] != src:
                    ov[k]["leaf_duplicate_in"] = src
                else:
                    ov[k] = rec
    return ov


def read_map(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return {(r["nct"], r["om_title"], r["group_title"]): r
                for r in csv.DictReader(fh, delimiter="\t")}


def v2_class(state, role):
    """Four comparable classes, for the change map only. Never written back onto a row."""
    if role == "CONTESTED" or state == "CONTESTED":
        return "CONTESTED"
    if role.startswith("COMPARATOR_SUPPORTED"):
        return "COMPARATOR_SUPPORTED"
    if role.startswith("COMPARATOR_PROPOSED"):
        return "COMPARATOR_PROPOSED"
    if role == "NOT_ESTABLISHED_IN_THIS_CACHE":
        return "NOT_ESTABLISHED"
    return "UNKNOWN"


def v1_class(v):
    if not v:
        return "NONE"
    if v == "CONTESTED":
        return "CONTESTED"
    if v.startswith("NOT_CONTROL"):
        return "NOT_CONTROL_ASSERTED"
    if "CANDIDATE" in v:
        return "COMPARATOR_PROPOSED"
    if v.startswith("CONTROL_"):
        return "COMPARATOR_SUPPORTED"
    return "UNKNOWN"


def main(out_tsv, out_checks):
    leaf = load_leaves()
    v1 = read_map(V1_MAP)
    job3 = read_map(JOB3_MAP)

    rows, seen = [], set()
    for name in FILES:
        era = name.rsplit("_", 2)[-2] + "_" + name.rsplit("_", 1)[-1]
        family = "bor" if name in BOR else "placebo"
        for s in payload(name).get("studies") or []:
            ps, rs = s.get("protocolSection") or {}, s.get("resultsSection") or {}
            nct = (ps.get("identificationModule") or {}).get("nctId")
            ai = (ps.get("armsInterventionsModule") or {}).get("armGroups") or []
            n_arms = len(ai)
            types = [(g.get("type") or "") for g in ai]
            typed = [t for t in types if t]
            arm_set_type_state = (
                "NO_ARMS_REGISTERED_IN_THIS_CACHE" if n_arms == 0 else
                "ARM_TYPE_ABSENT_IN_THIS_CACHE" if not typed else
                "PARTIALLY_TYPED_IN_THIS_CACHE" if len(typed) != n_arms else
                "ALL_ARMS_NON_CONTROL_TYPED" if set(typed) <= NONCONTROL_TYPES else
                "ALL_ARMS_CONTROL_TYPED" if set(typed) <= CONTROL_TYPES else "MIXED_ARM_TYPES")
            for om in (rs.get("outcomeMeasuresModule") or {}).get("outcomeMeasures") or []:
                gmeta = {g.get("id"): g for g in om.get("groups") or []}
                n_results_groups = len(gmeta)
                for gid, cells in cells_for_groups(om).items():
                    if len(cells) < 4:
                        continue
                    n = sum(cells.values())
                    if n <= 0:
                        continue
                    g = gmeta.get(gid) or {}
                    gtitle, omtitle = g.get("title") or "", om.get("title") or ""
                    key = (nct, omtitle, gtitle, n)
                    if key in seen:
                        continue
                    seen.add(key)
                    gdesc = g.get("description") or ""
                    k3 = (nct, omtitle, gtitle)
                    lf = leaf.get(k3)

                    link = decide_link(gtitle, gdesc, ai, lf)
                    role, basis, stmt, assume, btype, flags = decide_comparator(
                        link, gtitle, gdesc, ai, arm_set_type_state, types)
                    b = link["bound_arm_index"]
                    cand_i = [int(x) for x in link["candidate_arm_indices"].split("|") if x != ""]

                    p1 = v1.get(k3) or {}
                    p3 = job3.get(k3) or {}
                    a, bcl = v1_class(p1.get("control_status", "")), v2_class(link["arm_link_state"], role)
                    disp = ("NO_PRIOR_V1_ROW" if not p1 else
                            "UNCHANGED_CLASS:%s" % bcl if a == bcl else
                            "CHANGED_CLASS:%s->%s" % (a, bcl))
                    rows.append(dict(
                        nct=nct, om_title=omtitle, group_title=gtitle, evaluable_n=n, era=era,
                        family=family, n_arms_registered=n_arms,
                        n_results_groups_in_om=n_results_groups,
                        arm_set_type_state=arm_set_type_state,
                        registry_arm_types_in_record_verbatim=" | ".join(types),
                        arm_link_state=link["arm_link_state"],
                        arm_link_relation=link["arm_link_relation"],
                        arm_link_source=link["arm_link_source"],
                        arm_link_source_locator=link["arm_link_locator"],
                        n_candidate_arms=link["n_candidate_arms"],
                        candidate_arm_indices=link["candidate_arm_indices"],
                        candidate_arm_labels=" | ".join((ai[i].get("label") or "") for i in cand_i),
                        candidate_arm_types_verbatim=" | ".join(
                            (ai[i].get("type") or "ARM_TYPE_ABSENT_IN_THIS_CACHE") for i in cand_i),
                        bound_arm_index=("" if b == "" else str(b)),
                        bound_arm_label=("" if b == "" else (ai[b].get("label") or "")),
                        bound_arm_registered_type_verbatim=(
                            "" if b == "" else (btype or "ARM_TYPE_ABSENT_IN_THIS_CACHE")),
                        comparator_role=role, comparator_role_basis=basis,
                        registry_type_statement=stmt,
                        registry_type_statement_assumption=assume,
                        contested_flags=";".join(sorted(set(flags))),
                        leaf_claim_state=link["leaf_claim_state"],
                        leaf_claim_arm_label=(lf["leaf_arm_label"] if lf else ""),
                        leaf_claim_locator=link["leaf_claim_locator"],
                        leaf_claim_verification=link["leaf_claim_verification"],
                        leaf_narrative_verbatim_not_parsed=(lf["leaf_narrative"] if lf else ""),
                        sole_arm_multi_results_group_flag=(
                            "YES" if n_arms == 1 and n_results_groups > 1 else "NO"),
                        v1_arm_link_state=p1.get("arm_link_state", ""),
                        v1_arm_link_evidence_code=p1.get("arm_link_evidence_code", ""),
                        v1_confirmed_registry_arm_label=p1.get("confirmed_registry_arm_label", ""),
                        v1_control_status=p1.get("control_status", ""),
                        job3_control_status=p3.get("control_status", ""),
                        disposition_vs_v1=disp,
                        group_description=gdesc.replace("\n", " ")[:400]))

    cols = list(rows[0].keys())
    with open(out_tsv, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n",
                           quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow({k: str(v).replace("\t", " ").replace("\n", " ") for k, v in r.items()})

    chk, fail = [], 0

    def check(name, ok, detail):
        nonlocal fail
        chk.append(dict(check=name, result="PASS" if ok else "FAIL", detail=detail))
        if not ok:
            fail += 1

    check("row_count_equals_552", len(rows) == 552, "rows=%d" % len(rows))
    newkeys = {(r["nct"], r["om_title"], r["group_title"]) for r in rows}
    check("key_set_identical_to_v1", newkeys == set(v1),
          "only_v2=%d only_v1=%d" % (len(newkeys - set(v1)), len(set(v1) - newkeys)))
    check("key_set_identical_to_job3", newkeys == set(job3),
          "only_v2=%d only_job3=%d" % (len(newkeys - set(job3)), len(set(job3) - newkeys)))

    src = open(__file__, encoding="utf-8").read()
    body = src.split('"""', 2)[2]
    # the pattern is assembled from fragments so that this check's own source line does not
    # contain the token it searches for and therefore cannot match itself (RUN-02 false positive).
    tok = "leaf_" + "narrative"
    corrob = "CORROB" + "ORATION"
    narrative_tested = re.findall(
        r"^(?!\s*#).*" + tok + r".*(?:in |==|!=|search|match|find|startswith|casefold).*$",
        body, re.M)
    check("no_narrative_token_corroboration_predicate_remains",
          corrob not in body and not narrative_tested,
          "v1's token-corroboration tuple is absent from the executable body and no expression "
          "tests the leaf narrative; it is carried verbatim only. suspect_lines=%d"
          % len(narrative_tested))
    check("no_unconditional_NOT_CONTROL_state_in_the_table",
          not any(v.startswith("NOT_CONTROL") for r in rows
                  for v in (r["comparator_role"], r["registry_type_statement"])),
          "comparator_role and registry_type_statement carry no NOT_CONTROL value")
    bad = [r for r in rows if r["registry_type_statement"].endswith("_CONDITIONAL")
           and not r["registry_type_statement_assumption"]]
    check("every_conditional_type_statement_names_its_assumption_in_machine_state", not bad,
          "violations=%d" % len(bad))
    bad = [r for r in rows if r["arm_link_state"] not in ("SOURCE_CONFIRMED", "LABEL_MATCH")
           and r["bound_arm_index"] != ""]
    check("an_arm_is_bound_only_by_SOURCE_CONFIRMED_or_LABEL_MATCH", not bad,
          "violations=%d" % len(bad))
    bad = [r for r in rows if r["bound_arm_index"] != "" and r["n_candidate_arms"] != 1]
    check("a_bound_arm_always_had_exactly_one_candidate", not bad, "violations=%d" % len(bad))
    bad = [r for r in rows if int(r["n_candidate_arms"]) > 1 and r["bound_arm_index"] != ""]
    check("two_or_more_candidates_never_select_the_first", not bad, "violations=%d" % len(bad))
    bad = [r for r in rows if r["arm_link_state"] == "SOURCE_CONFIRMED"
           and not (r["arm_link_relation"].startswith("TWO_INDEPENDENT_FIELD_IDENTITIES")
                    or r["arm_link_relation"].startswith("DESCRIPTION_FIELD_IDENTITY"))]
    check("SOURCE_CONFIRMED_only_from_an_exact_field_identity", not bad, "violations=%d" % len(bad))
    bad = [r for r in rows if r["arm_link_state"] == "PROPOSED" and not r["leaf_claim_locator"]]
    check("every_PROPOSED_row_retains_a_locator", not bad, "violations=%d" % len(bad))
    bad = [r for r in rows if r["leaf_claim_state"] == "LEAF_LABEL_ABSENT_FROM_RECORD"
           and re.search(r"[;|]", r["leaf_claim_arm_label"])]
    check("multi_arm_leaf_claims_are_split_not_read_as_one_absent_label", not bad,
          "violations=%d (both '; ' and '|' separators are split)" % len(bad))
    bad = [r for r in rows if r["n_arms_registered"] == 0
           and (r["comparator_role"] != "UNKNOWN_IN_THIS_CACHE"
                or r["arm_link_state"] != "UNKNOWN_IN_THIS_CACHE")]
    check("zero_arms_stays_UNKNOWN_never_a_role_or_a_link", not bad, "violations=%d" % len(bad))
    bad = [r for r in rows if r["arm_set_type_state"] == "ARM_TYPE_ABSENT_IN_THIS_CACHE"
           and r["registry_type_statement"] not in ("ARM_TYPE_ABSENT_IN_THIS_CACHE",
                                                    "BOUND_ARM_TYPE_ABSENT_IN_THIS_CACHE")]
    check("absent_arm_type_stays_its_own_value", not bad, "violations=%d" % len(bad))
    bad = [r for r in rows if "PLACEBO_OR_NOINT_GROUP_TEXT_VS_NON_COMPARATOR_BOUND_TYPE"
           in r["contested_flags"] and r["comparator_role"] != "CONTESTED"]
    check("placebo_text_vs_type_is_CONTESTED_not_resolved_to_a_side", not bad,
          "violations=%d" % len(bad))
    bad = [r for r in rows if r["bound_arm_index"] != "" and not
           r["bound_arm_registered_type_verbatim"]]
    check("bound_rows_carry_the_registered_type_verbatim", not bad, "violations=%d" % len(bad))
    check("producer_makes_no_network_call",
          not re.search(r"^\s*(import|from)\s+(urllib|requests|httpx|http|socket|subprocess|ssl)\b",
                        src, re.M),
          "imports: " + ", ".join(sorted(set(re.findall(r"^import ([a-z, ]+)$", src, re.M)[0]
                                             .split(", ")))))
    absent = collections.Counter()
    for name in FILES:
        with open(os.path.join(CACHE, name + ".txt"), encoding="utf-8") as fh:
            blob = fh.read()
        absent["participantFlowModule"] += blob.count("participantFlowModule")
        absent["armGroupLabels"] += blob.count("armGroupLabels")
    check("absent_registry_join_modules_stay_absent",
          absent["participantFlowModule"] == 0 and absent["armGroupLabels"] == 0,
          "occurrences across the 12 payloads: %s (0 expected; never fetched)" % dict(absent))

    unresolved = sum(1 for r in rows if r["arm_link_state"] in
                     ("PROPOSED", "UNRESOLVED", "CONTESTED", "UNKNOWN_IN_THIS_CACHE"))
    summary = dict(
        rows=len(rows),
        arm_link_state=dict(collections.Counter(r["arm_link_state"] for r in rows)),
        arm_link_relation=dict(collections.Counter(r["arm_link_relation"] for r in rows)),
        comparator_role=dict(collections.Counter(r["comparator_role"] for r in rows)),
        registry_type_statement=dict(collections.Counter(r["registry_type_statement"] for r in rows)),
        leaf_claim_state=dict(collections.Counter(r["leaf_claim_state"] for r in rows)),
        leaf_claim_verification=dict(collections.Counter(r["leaf_claim_verification"] for r in rows)),
        disposition_vs_v1=dict(collections.Counter(r["disposition_vs_v1"] for r in rows)),
        contested_flag_counts=dict(collections.Counter(
            f for r in rows for f in r["contested_flags"].split(";") if f)),
        not_source_confirmed_rows=unresolved,
        v1_confirmed_by_narrative_token_now=dict(collections.Counter(
            r["arm_link_state"] for r in rows
            if r["v1_arm_link_evidence_code"] == "LEAF_WITHIN_RECORD_RELATION")),
        v1_confirmed_by_label_now=dict(collections.Counter(
            r["arm_link_state"] for r in rows
            if r["v1_arm_link_evidence_code"] in ("LABEL_BYTE_EXACT",
                                                  "LABEL_CASE_AND_WHITESPACE_ONLY"))),
        checks=chk, checks_failed=fail)
    with open(out_checks, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    print(json.dumps(summary, indent=1, sort_keys=True))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
