#!/usr/bin/env python3
"""Build INTEGRATION2 — the integrated endpoint curation ledger over the CORRECTED *-v2 components.

Inputs (READ-ONLY, never written):
  CORRECTED-A-denominator-category-v2/corrected-a-v2-rows.tsv          552 rows
  CORRECTED-B-identity-selection-overlap/artifacts/
        LEDGER-response-observations.tsv                            16,116 observations
        (B2 did NOT re-emit the observation ledger; observation-level source facts are v1's)
  CORRECTED-B2-identity-overlap-inference-repair-v2/artifacts/
        RELATED-SETS-encoding-vs-semantics-v2.tsv                    8,740 cohort keys
  CORRECTED-C-arm-attribution-v2/CORRECTED-C-arm-attribution-v2-map.tsv  552 rows
  INTEGRATION-endpoint-ledger/ (v1)                                  comparison only

Writes only into INTEGRATION2-endpoint-ledger/.
No network. No re-run of any job or leaf. No rate, proportion, unique-patient total, capacity
bound, control comparison or agent-independent effect is computed anywhere.
"""
import csv, json, os, hashlib, collections

csv.field_size_limit(10 ** 9)
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
A2_DIR = os.path.join(LANE, "CORRECTED-A-denominator-category-v2")
B1_DIR = os.path.join(LANE, "CORRECTED-B-identity-selection-overlap", "artifacts")
B2_DIR = os.path.join(LANE, "CORRECTED-B2-identity-overlap-inference-repair-v2", "artifacts")
C2_DIR = os.path.join(LANE, "CORRECTED-C-arm-attribution-v2")
V1_DIR = os.path.join(LANE, "INTEGRATION-endpoint-ledger")


def rd(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


A = rd(os.path.join(A2_DIR, "corrected-a-v2-rows.tsv"))
C = rd(os.path.join(C2_DIR, "CORRECTED-C-arm-attribution-v2-map.tsv"))
BOBS = rd(os.path.join(B1_DIR, "LEDGER-response-observations.tsv"))
BSET = rd(os.path.join(B2_DIR, "RELATED-SETS-encoding-vs-semantics-v2.tsv"))
V1LED = rd(os.path.join(V1_DIR, "LEDGER-integrated-552.tsv"))
V1COV = rd(os.path.join(V1_DIR, "COVERAGE-b-observations.tsv"))

# ---------------------------------------------------------------- declared join
# A2 grain : (input_key_nct_id, input_key_om_index, input_key_group_id)   552
# C2 grain : (nct, om_title, group_title, evaluable_n) -- no om_index/group_id  552
# B  grain : obs_id = "<nct>#om<om_index>#<results_group_id>"          16,116
# B2 grain : cohort_key = "<nct>||<results_group_title_norm>"           8,740
c_by_bridge = {}
for r in C:
    c_by_bridge.setdefault((r['nct'], r['om_title'], r['group_title']), []).append(r)
b_by_obs = {r['obs_id']: r for r in BOBS}
set_by_obs = {}
for r in BSET:
    for o in r['observation_ids'].split('|'):
        set_by_obs[o] = r
b_ncts = set(r['nct'] for r in BOBS)
b_oms = set((r['nct'], r['om_index']) for r in BOBS)

# The ONLY arm-link state C2 calls source-evidenced. LABEL_MATCH / PROPOSED / CONTESTED /
# UNKNOWN_IN_THIS_CACHE / UNRESOLVED are weaker and are never promoted here.
C_SOURCE_CONFIRMED = "SOURCE_CONFIRMED"
C_COMPARATOR_SOURCE_SUPPORTED = "COMPARATOR_SUPPORTED_BY_SOURCE_CONFIRMED_ARM_TYPE"

TRUEISH = ('true', 'yes', '1')

rows = []
for a in A:
    nct = a['input_key_nct_id']
    om = str(int(a['input_key_om_index']))
    gid = a['input_key_group_id']
    obs_id = f"{nct}#om{om}#{gid}"
    bridge = (nct, a['om_title'], a['group_title'])
    cs = c_by_bridge.get(bridge, [])
    c = cs[0] if len(cs) == 1 else None
    c_join_state = ("JOINED_UNIQUE" if len(cs) == 1 else
                    "AMBIGUOUS_BRIDGE" if len(cs) > 1 else "ABSENT_FROM_C")
    b = b_by_obs.get(obs_id)
    s = set_by_obs.get(obs_id)
    if b is not None:
        b_join_state = "JOINED_UNIQUE"
    elif nct not in b_ncts:
        b_join_state = "TRIAL_OUTSIDE_B_CORPUS_SCOPE"
    elif (nct, om) not in b_oms:
        b_join_state = "MEASURE_OUTSIDE_B_TITLE_BOUNDARY"
    else:
        b_join_state = "GROUP_ABSENT_IN_B_MEASURE"

    # ------------------------------------------------------ blocking conditions, by axis
    blocking = []
    if a['proportion_suitability'] == 'UNSUITABLE_FOR_PROPORTION':
        blocking.append('AXIS_DENOMINATOR_CATEGORY:A_UNSUITABLE_FOR_PROPORTION')
    if c is None:
        blocking.append('AXIS_ARM_ATTRIBUTION:C_NOT_JOINED')
    else:
        if c['arm_link_state'] != C_SOURCE_CONFIRMED:
            blocking.append('AXIS_ARM_ATTRIBUTION:C_ARM_LINK_NOT_SOURCE_CONFIRMED:' + c['arm_link_state'])
        if c['comparator_role'] != C_COMPARATOR_SOURCE_SUPPORTED:
            blocking.append('AXIS_COMPARATOR_ROLE:C_' + c['comparator_role'])
    if b is None:
        blocking.append('AXIS_COVERAGE:B_NOT_ASSESSED:' + b_join_state)
    else:
        if b['usable_for_proportion'].strip().lower() not in TRUEISH:
            blocking.append('AXIS_OBSERVATION_USABILITY:B_NOT_USABLE_AT_B_SCOPE')
        if s is not None and int(s['n_observations']) > 1:
            blocking.append('AXIS_RECORD_IDENTITY:B_COMPETING_RECORDS_SEMANTIC_CORRESPONDENCE_UNRESOLVED')
            if s['distinction_basis'] == 'TEXT_DERIVED_ONLY':
                blocking.append('AXIS_RECORD_IDENTITY:B_DISTINCTION_TEXT_DERIVED_ONLY')
    # universal, and scoped to ONE axis only (see the two-unknowns separation below)
    blocking.append('AXIS_CROSS_OBSERVATION_DISJOINTNESS:NO_PARTICIPANT_FLOW_MODULE_IN_THIS_CACHE')

    # -------------------------------------------- the two distinct unknowns, kept apart
    # (1) cross-observation disjointness: unverifiable everywhere; limits POOLING and
    #     UNIQUE-PATIENT COUNTING across records.
    disj_state = 'UNVERIFIABLE_IN_THIS_CACHE__NO_PARTICIPANT_FLOW_MODULE'
    disj_scope = 'LIMITS_POOLING_AND_UNIQUE_PATIENT_COUNTING_ACROSS_OBSERVATIONS_ONLY'
    # (2) within-record reporting of the individual source observation: a SEPARATE question,
    #     answered from the record's own fields, never from the absent participantFlowModule.
    if b is None:
        within = 'NOT_ASSESSED_BY_B:' + b_join_state
    elif b['usable_for_proportion'].strip().lower() not in TRUEISH:
        within = 'SOURCE_VALUES_NOT_USABLE_AT_B_SCOPE:' + (b['unusable_reason'] or 'UNSPECIFIED')
    else:
        within = 'SOURCE_VALUES_PRESENT_AT_B_SCOPE'
    if a['proportion_suitability'] == 'UNSUITABLE_FOR_PROPORTION':
        within += '|A_RECORD_STRUCTURE_UNSUITABLE_AT_A_SCOPE'

    # ------------------------------------------------ cross-component status / constraints
    # Compatible statements about DIFFERENT axes. Renamed from v1's "contradiction".
    xstat = []
    if c is not None:
        if a['proportion_suitability'] == 'UNSUITABLE_FOR_PROPORTION' and c['arm_link_state'] == C_SOURCE_CONFIRMED:
            xstat.append('CROSS_COMPONENT_CONSTRAINT:A_UNSUITABLE_WITH_C_ARM_SOURCE_CONFIRMED')
        if a['proportion_suitability'] == 'NOT_REFUTED_BY_THIS_COMPONENT' and c['arm_link_state'] != C_SOURCE_CONFIRMED:
            xstat.append('CROSS_COMPONENT_STATUS:A_NOT_REFUTED_WITH_C_ARM_' + c['arm_link_state'])
    if b is not None:
        if a['proportion_suitability'] == 'NOT_REFUTED_BY_THIS_COMPONENT' and \
           b['usable_for_proportion'].strip().lower() not in TRUEISH:
            xstat.append('CROSS_COMPONENT_STATUS:A_NOT_REFUTED_WITH_B_OBSERVATION_NOT_USABLE_AT_B_SCOPE')
        if s is not None and int(s['n_observations']) > 1 and \
           a['proportion_suitability'] == 'NOT_REFUTED_BY_THIS_COMPONENT':
            xstat.append('CROSS_COMPONENT_STATUS:A_NOT_REFUTED_WITH_B_SET_SEMANTIC_CORRESPONDENCE_UNRESOLVED')
    else:
        xstat.append('COVERAGE_GAP:ROW_NOT_ASSESSED_BY_B')

    # ------------------------------------------------------------- genuine contradictions
    # Reserved strictly for claims that CANNOT both be true of the same object on the same axis.
    contra = []
    if c is not None:
        if c['sole_arm_multi_results_group_flag'] == 'YES':
            contra.append('SOURCE_INTERNAL_CONTRADICTION:SOLE_REGISTERED_ARM_VS_MULTIPLE_RESULTS_GROUPS')
        if c['contested_flags']:
            for t in c['contested_flags'].split('|'):
                if t:
                    contra.append('SOURCE_INTERNAL_CONTRADICTION:C_CONTESTED:' + t)
    if b is not None and b['denominator_value_participants'] != a['reported_denominator_participants']:
        contra.append('CROSS_COMPONENT_CONTRADICTION:A_B_DENOMINATOR_VALUE_DISAGREE')

    substantive = [t for t in blocking
                   if not t.startswith('AXIS_CROSS_OBSERVATION_DISJOINTNESS:')]
    state = 'BLOCKED' if substantive else 'NO_COMPONENT_BLOCK_FOUND__NOT_AN_ELIGIBILITY_GRANT'

    rows.append({
        'integration_row_key': f"{nct}|OM{om}|{gid}",
        'a_row_key': a['row_key'],
        'nct_id': nct, 'om_index': om, 'group_id': gid,
        'obs_id_b_form': obs_id,
        'om_title': a['om_title'], 'group_title': a['group_title'],
        'payload_shard': a['payload_shard'], 'cache_revision': a['cache_revision'],
        # --- component A2, carried verbatim, never overwritten, never strengthened ---
        'a_component': 'CORRECTED-A-denominator-category-v2',
        'a_reported_denominator_participants': a['reported_denominator_participants'],
        'a_denominator_state': a['denominator_state'],
        'a_denominator_provenance': a['denominator_provenance'],
        'a_n_source_categories': a['n_source_categories'],
        'a_n_categories_kept_by_producer': a['n_categories_kept_by_producer'],
        'a_category_preservation_state': a['category_preservation_state'],
        'a_proportion_suitability': a['proportion_suitability'],
        'a_unresolved_reason_codes': a['unresolved_reason_codes'],
        'a_advisory_flag_codes': a['advisory_flag_codes'],
        'a_dropped_response_assessment_category_titles_with_values':
            a['dropped_response_assessment_category_titles_with_values'],
        'a_evaluable_n_minus_reported_denominator': a['evaluable_n_minus_reported_denominator'],
        'a_all_categories_sum_minus_reported_denominator': a['all_categories_sum_minus_reported_denominator'],
        'a_job1_classification_carried': a['job1_classification_carried'],
        'a_leaf_qa_coverage': a['leaf_qa_coverage'],
        # --- component C2 ---
        'c_component': 'CORRECTED-C-arm-attribution-v2',
        'c_join_state': c_join_state,
        'c_join_bridge': 'nct+om_title+group_title (C carries no om_index/group_id)',
        'c_arm_link_state': c['arm_link_state'] if c else '',
        'c_arm_link_relation': c['arm_link_relation'] if c else '',
        'c_arm_link_source': c['arm_link_source'] if c else '',
        'c_arm_link_source_locator': c['arm_link_source_locator'] if c else '',
        'c_bound_arm_label': c['bound_arm_label'] if c else '',
        'c_bound_arm_registered_type_verbatim': c['bound_arm_registered_type_verbatim'] if c else '',
        'c_candidate_arm_labels': c['candidate_arm_labels'] if c else '',
        'c_comparator_role': c['comparator_role'] if c else '',
        'c_comparator_role_basis': c['comparator_role_basis'] if c else '',
        'c_registry_type_statement': c['registry_type_statement'] if c else '',
        'c_registry_type_statement_assumption': c['registry_type_statement_assumption'] if c else '',
        'c_contested_flags': c['contested_flags'] if c else '',
        'c_leaf_claim_state': c['leaf_claim_state'] if c else '',
        'c_leaf_claim_verification': c['leaf_claim_verification'] if c else '',
        'c_sole_arm_multi_results_group_flag': c['sole_arm_multi_results_group_flag'] if c else '',
        'c_arm_set_type_state': c['arm_set_type_state'] if c else '',
        'c_disposition_vs_v1': c['disposition_vs_v1'] if c else '',
        # --- component B (observations v1) + B2 (set semantics) ---
        'b_component_observations': 'CORRECTED-B-identity-selection-overlap (v1 observation ledger, not re-emitted by B2)',
        'b_component_set_semantics': 'CORRECTED-B2-identity-overlap-inference-repair-v2',
        'b_join_state': b_join_state,
        'b_cohort_key': s['cohort_key'] if s else '',
        'b_n_observations_in_cohort_set': s['n_observations'] if s else '',
        'b_sibling_observation_ids': s['observation_ids'] if s else '',
        'b_encoding_identity_status': s['encoding_identity_status'] if s else '',
        'b_semantic_duplication_status': s['semantic_duplication_status'] if s else '',
        'b_semantic_correspondence_evidence': s['semantic_correspondence_evidence'] if s else '',
        'b_distinction_basis': s['distinction_basis'] if s else '',
        'b_distinguishing_field_classes': s['distinguishing_field_classes'] if s else '',
        'b_unresolved_states_v2': s['v2_unresolved_states'] if s else '',
        'b_selection_status': s['selection_status'] if s else '',
        'b_denominator_state': b['denominator_state'] if b else '',
        'b_denominator_value_participants': b['denominator_value_participants'] if b else '',
        'b_reporting_status_state': b['reporting_status_state'] if b else '',
        'b_usable_for_proportion_at_b_scope': b['usable_for_proportion'] if b else '',
        'b_unusable_reason': b['unusable_reason'] if b else '',
        'b_endpoint_constructs': b['endpoint_constructs'] if b else '',
        'b_assessment_criteria': b['assessment_criteria'] if b else '',
        'b_noncollection_statement': b['noncollection_statement'] if b else '',
        # --- the two distinct unknowns, never merged ---
        'cross_observation_disjointness_state': disj_state,
        'cross_observation_disjointness_scope': disj_scope,
        'within_record_reporting_state': within,
        'within_record_reporting_barred_by_absent_participant_flow':
            'NO__ABSENCE_OF_PARTICIPANT_FLOW_IS_NOT_A_WITHIN_RECORD_REPORTING_BAR',
        # --- integration verdicts ---
        'integration_state': state,
        'blocking_conditions': '|'.join(blocking),
        'cross_component_status': '|'.join(xstat) if xstat else 'NONE',
        'contradictions_genuine': '|'.join(contra) if contra else 'NONE',
        'job1_arithmetic_independently_confirmed': 'true',
        'job2_independently_confirmed': 'false',
        'job3_independently_confirmed': 'false',
        'endpoint_manuscript_status': 'PARKED__HOLD_F1_F10_NOT_SATISFIED_BY_THIS_LEDGER',
        'proportion_authorisation': 'NO_PROPORTION_AUTHORISED_IN_THIS_INTEGRATION',
        'rate_derived': 'NOT_DERIVED',
        'unique_patient_total_derived': 'NOT_DERIVED',
        'control_comparison_derived': 'NOT_DERIVED',
        'cross_disease_capacity_bound_derived': 'NOT_DERIVED',
        'agent_independent_effect_derived': 'NOT_DERIVED',
        'source_pointer': a['source_pointer'],
    })

with open(os.path.join(HERE, 'LEDGER2-integrated-552.tsv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, list(rows[0].keys()), delimiter='\t', extrasaction='raise')
    w.writeheader(); w.writerows(rows)

# ------------------------------------------- B-side coverage: every B observation, in-A or not
a_obs = set(r['obs_id_b_form'] for r in rows)
cov = []
for b in BOBS:
    s = set_by_obs.get(b['obs_id'])
    cov.append({
        'obs_id': b['obs_id'], 'nct': b['nct'], 'om_index': b['om_index'],
        'results_group_id': b['results_group_id'],
        'in_integrated_552': 'yes' if b['obs_id'] in a_obs else 'no',
        'coverage_state': ('COVERED_BY_A_AND_C' if b['obs_id'] in a_obs
                           else 'B_ONLY__NO_DENOMINATOR_CATEGORY_OR_ARM_COMPONENT'),
        'cohort_key': s['cohort_key'] if s else '',
        'n_observations_in_cohort_set': s['n_observations'] if s else '',
        'encoding_identity_status': s['encoding_identity_status'] if s else '',
        'semantic_duplication_status': s['semantic_duplication_status'] if s else '',
        'distinction_basis': s['distinction_basis'] if s else '',
        'unresolved_states_v2': s['v2_unresolved_states'] if s else '',
        'denominator_state': b['denominator_state'],
        'denominator_value_participants': b['denominator_value_participants'],
        'reporting_status_state': b['reporting_status_state'],
        'usable_for_proportion_at_b_scope': b['usable_for_proportion'],
        'unusable_reason': b['unusable_reason'],
        'cross_observation_disjointness_state': 'UNVERIFIABLE_IN_THIS_CACHE__NO_PARTICIPANT_FLOW_MODULE',
    })
with open(os.path.join(HERE, 'COVERAGE2-b-observations.tsv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, list(cov[0].keys()), delimiter='\t'); w.writeheader(); w.writerows(cov)

# ------------------------------------------------------------------ disposition map
disp = []
for r in rows:
    disp.append({'component': 'CORRECTED-A-v2', 'component_grain': '(nct_id,om_index,group_id)',
                 'component_record_key': r['a_row_key'], 'integration_row_key': r['integration_row_key'],
                 'disposition': 'CARRIED_INTO_INTEGRATED_LEDGER',
                 'reason': 'A2 is the integration spine; every A2 row is present exactly once. A2 changed no row data value against A1 (its own check D8).'})
    disp.append({'component': 'CORRECTED-C-v2', 'component_grain': '(nct,om_title,group_title,evaluable_n)',
                 'component_record_key': f"{r['nct_id']}|{r['om_title']}|{r['group_title']}",
                 'integration_row_key': r['integration_row_key'],
                 'disposition': 'JOINED_TO_A_ON_TITLE_BRIDGE' if r['c_join_state'] == 'JOINED_UNIQUE' else 'NOT_JOINED:' + r['c_join_state'],
                 'reason': 'C2 carries no om_index/group_id; the (nct,om_title,group_title) bridge is unique on both sides (check J2).'})
    disp.append({'component': 'CORRECTED-B/B2', 'component_grain': 'obs_id=(nct,om_index,results_group_id)',
                 'component_record_key': r['obs_id_b_form'],
                 'integration_row_key': r['integration_row_key'],
                 'disposition': 'JOINED_TO_A_ON_OBSERVATION_KEY' if r['b_join_state'] == 'JOINED_UNIQUE' else 'NOT_PRESENT_IN_B:' + r['b_join_state'],
                 'reason': "B's corpus boundary is job2's response-title regex over 4,235 results trials; A/C's 552 keys come from job1's contract rows. The difference is retained, never inner-joined away."})
for c in cov:
    if c['in_integrated_552'] == 'no':
        disp.append({'component': 'CORRECTED-B/B2', 'component_grain': 'obs_id=(nct,om_index,results_group_id)',
                     'component_record_key': c['obs_id'], 'integration_row_key': '',
                     'disposition': 'B_ONLY__NOT_IN_THE_552_SPINE',
                     'reason': 'No denominator/category component and no arm-attribution component exists for this observation. It is neither resolved nor excluded here.'})
with open(os.path.join(HERE, 'DISPOSITION-MAP2.tsv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, ['component', 'component_grain', 'component_record_key',
                           'integration_row_key', 'disposition', 'reason'], delimiter='\t')
    w.writeheader(); w.writerows(disp)

# --------------------------------- register 1: cross-component status / constraints (compatible)
xs = []
for r in rows:
    if r['cross_component_status'] == 'NONE':
        continue
    for t in r['cross_component_status'].split('|'):
        xs.append({'integration_row_key': r['integration_row_key'], 'code': t,
                   'kind': t.split(':', 1)[0],
                   'axis_a': 'denominator/category structure (component A2)',
                   'axis_c': 'arm attribution and comparator role (component C2)',
                   'axis_b': 'record identity, set semantics and observation usability (B/B2)',
                   'why_not_a_contradiction':
                       'The two statements are about DIFFERENT axes of the same record and can both '
                       'be true at once. A confirmed arm link says nothing about whether the '
                       'denominator/category structure supports a proportion, and an unresolved set '
                       'semantics says nothing about the denominator either.',
                   'a_state': r['a_proportion_suitability'],
                   'a_unresolved_reason_codes': r['a_unresolved_reason_codes'],
                   'c_arm_link_state': r['c_arm_link_state'],
                   'c_comparator_role': r['c_comparator_role'],
                   'b_join_state': r['b_join_state'],
                   'b_semantic_duplication_status': r['b_semantic_duplication_status'],
                   'b_distinction_basis': r['b_distinction_basis'],
                   'resolution': 'BOTH_STATES_STAND__NEITHER_COMPONENT_OVERWRITES_THE_OTHER__ROW_STAYS_BLOCKED',
                   'source_pointer': r['source_pointer']})
with open(os.path.join(HERE, 'CROSS-COMPONENT-STATUS.tsv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, list(xs[0].keys()), delimiter='\t'); w.writeheader(); w.writerows(xs)

# ------------------------------- register 2: genuine contradictions (mutually incompatible only)
cn = []
for r in rows:
    if r['contradictions_genuine'] == 'NONE':
        continue
    for t in r['contradictions_genuine'].split('|'):
        cn.append({'integration_row_key': r['integration_row_key'], 'code': t,
                   'incompatibility':
                       ('The record registers exactly one arm and reports several distinct results '
                        'groups in the same outcome measure. Both cannot be true of one arm set.'
                        if t.endswith('SOLE_REGISTERED_ARM_VS_MULTIPLE_RESULTS_GROUPS') else
                        'Two source fields of the same record state incompatible things about the '
                        'same arm/comparator object; C2 records the conflict without resolving it.'
                        if ':C_CONTESTED:' in t else
                        'Two components read a different participant denominator from the same '
                        'cached record. Only one value can be the reported denominator.'),
                   'a_state': r['a_proportion_suitability'],
                   'a_reported_denominator_participants': r['a_reported_denominator_participants'],
                   'b_denominator_value_participants': r['b_denominator_value_participants'],
                   'c_arm_link_state': r['c_arm_link_state'],
                   'c_contested_flags': r['c_contested_flags'],
                   'c_sole_arm_multi_results_group_flag': r['c_sole_arm_multi_results_group_flag'],
                   'resolution': 'RETAINED_UNRESOLVED__NO_FIELD_IS_DECLARED_WRONG',
                   'source_pointer': r['source_pointer']})
with open(os.path.join(HERE, 'CONTRADICTIONS-genuine.tsv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, list(cn[0].keys()), delimiter='\t'); w.writeheader(); w.writerows(cn)

# --------------------- re-derivation of v1's 562 "contradictions" into the two registers
v1_by_key = {r['integration_row_key']: r for r in V1LED}
rederive = []
v1_code_rows = collections.Counter()
for r in V1LED:
    if r['contradictions_retained'] == 'NONE':
        continue
    for t in r['contradictions_retained'].split('|'):
        v1_code_rows[t] += 1
V1_VERDICT = {
    'A_UNSUITABLE_WHILE_C_ARM_CONFIRMED': (
        'NOT_A_CONTRADICTION__CROSS_COMPONENT_CONSTRAINT',
        'CROSS-COMPONENT-STATUS.tsv',
        'v1 named it a contradiction and then conceded in the same paragraph that both statements '
        'are true about different axes. A confirmed arm on an uncomputable denominator is a '
        'CONSTRAINT, not an incompatibility. Under C2 the confirmed side is also narrower: only '
        'SOURCE_CONFIRMED counts, so the population of this combination changes.'),
    'A_NOT_REFUTED_WHILE_C_ARM_CONFIRMED_TYPE_ONLY': (
        'NOT_A_CONTRADICTION__CROSS_COMPONENT_STATUS', 'CROSS-COMPONENT-STATUS.tsv',
        'An absence of a found A defect and a weak C arm-evidence state are compatible; and '
        'CONFIRMED_TYPE_ONLY no longer exists as a C2 state.'),
    'A_NOT_REFUTED_WHILE_C_ARM_CANDIDATE': (
        'NOT_A_CONTRADICTION__CROSS_COMPONENT_STATUS', 'CROSS-COMPONENT-STATUS.tsv',
        'Compatible statements on different axes; CANDIDATE is superseded by C2 states.'),
    'A_NOT_REFUTED_WHILE_C_ARM_UNKNOWN_IN_THIS_CACHE': (
        'NOT_A_CONTRADICTION__CROSS_COMPONENT_STATUS', 'CROSS-COMPONENT-STATUS.tsv',
        'An unknown is not a claim, so it cannot contradict one.'),
    'A_NOT_REFUTED_WHILE_C_ARM_UNRESOLVED': (
        'NOT_A_CONTRADICTION__CROSS_COMPONENT_STATUS', 'CROSS-COMPONENT-STATUS.tsv',
        'An unresolved state is not a claim, so it cannot contradict one.'),
    'A_NOT_REFUTED_WHILE_B_SET_UNRESOLVED': (
        'NOT_A_CONTRADICTION__CROSS_COMPONENT_STATUS', 'CROSS-COMPONENT-STATUS.tsv',
        'Set-level semantic correspondence and row-level denominator/category structure are '
        'different axes; neither refutes the other.'),
    'ROW_NOT_ASSESSED_BY_B': (
        'NOT_A_CONTRADICTION__COVERAGE_GAP', 'CROSS-COMPONENT-STATUS.tsv (kind COVERAGE_GAP)',
        'Silence from a component whose corpus never covered the row is a coverage gap. It is '
        'neither agreement nor disagreement.'),
    'C_CONTESTED_FLAG_PRESENT': (
        'GENUINE_CONTRADICTION__RETAINED', 'CONTRADICTIONS-genuine.tsv',
        'Two source fields of the same record state incompatible things about the same object. '
        'C2 re-derives the flags, so the row population and count change; the flags are itemised '
        'rather than collapsed into one code.'),
    'C_SOLE_ARM_BUT_MULTIPLE_RESULTS_GROUPS': (
        'GENUINE_CONTRADICTION__RETAINED', 'CONTRADICTIONS-genuine.tsv',
        'One registered arm and several results groups in one measure cannot both hold under any '
        'one-arm reading of that record.'),
    'A_B_DENOMINATOR_VALUE_DISAGREE': (
        'GENUINE_CONTRADICTION__RETAINED', 'CONTRADICTIONS-genuine.tsv',
        'Two readings of one cached denominator that disagree are incompatible. Observed 0 in v1 '
        'and re-tested here; the test stays live.'),
}
v2_code_rows = collections.Counter()
for r in rows:
    for fld in ('cross_component_status', 'contradictions_genuine'):
        if r[fld] == 'NONE':
            continue
        for t in r[fld].split('|'):
            v2_code_rows[t] += 1
for code, n in sorted(v1_code_rows.items()):
    verdict, dest, why = V1_VERDICT[code]
    rederive.append({'v1_contradiction_code': code, 'v1_rows': n, 'v2_verdict': verdict,
                     'v2_register': dest, 'why': why})
with open(os.path.join(HERE, 'CONTRADICTION-REDERIVATION.tsv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, ['v1_contradiction_code', 'v1_rows', 'v2_verdict', 'v2_register', 'why'],
                       delimiter='\t')
    w.writeheader(); w.writerows(rederive)

# -------------------------------------------------------- grain preservation vs the v1 ledger
v1_states = collections.Counter(r['b_join_state'] for r in V1LED)
v2_states = collections.Counter(r['b_join_state'] for r in rows)
grain = {
    'spine_rows': {'v1': len(V1LED), 'v2': len(rows)},
    'b_join_state': {'v1': dict(v1_states), 'v2': dict(v2_states)},
    'b_observations_not_in_spine': {
        'v1': sum(1 for c in V1COV if c['in_integrated_552'] == 'no'),
        'v2': sum(1 for c in cov if c['in_integrated_552'] == 'no')},
    'b_observation_rows': {'v1': len(V1COV), 'v2': len(cov)},
    'spine_row_keys_identical': sorted(r['integration_row_key'] for r in rows) ==
                                sorted(r['integration_row_key'] for r in V1LED),
}

# ------------------------------------------------------------------------------- census
cen = {
    'component': 'INTEGRATION2-endpoint-ledger',
    'supersedes_nothing': 'INTEGRATION-endpoint-ledger/ (v1) is untouched evidence of what v1 '
                          'asserted. This is a new explicitly versioned sibling.',
    'cache_revision': rows[0]['cache_revision'],
    'network_access': 'none',
    'rates_or_proportions_derived': 0,
    'unique_patient_totals_derived': 0,
    'cross_disease_capacity_bounds_derived': 0,
    'control_comparisons_derived': 0,
    'agent_independent_effects_derived': 0,
    'eligibility_subsets_constructed': 0,
    'spine_rows': len(rows),
    'distinct_trials_in_spine': len(set(r['nct_id'] for r in rows)),
    'a_rows_in': len(A), 'c_rows_in': len(C),
    'b_observation_rows_in': len(BOBS), 'b_cohort_keys_in': len(BSET),
    'c_join_state': dict(collections.Counter(r['c_join_state'] for r in rows)),
    'b_join_state': dict(v2_states),
    'b_observations_not_in_spine': sum(1 for c in cov if c['in_integrated_552'] == 'no'),
    'integration_state': dict(collections.Counter(r['integration_state'] for r in rows)),
    'a_proportion_suitability': dict(collections.Counter(r['a_proportion_suitability'] for r in rows)),
    'a_advisory_flag_code_rows': dict(collections.Counter(
        t for r in rows for t in r['a_advisory_flag_codes'].split('|') if t)),
    'c_arm_link_state': dict(collections.Counter(r['c_arm_link_state'] for r in rows)),
    'c_comparator_role': dict(collections.Counter(r['c_comparator_role'] for r in rows)),
    'c_registry_type_statement_assumption': dict(collections.Counter(
        r['c_registry_type_statement_assumption'] for r in rows)),
    'b_encoding_identity_status': dict(collections.Counter(
        r['b_encoding_identity_status'] for r in rows)),
    'b_semantic_duplication_status': dict(collections.Counter(
        r['b_semantic_duplication_status'] for r in rows)),
    'b_distinction_basis': dict(collections.Counter(r['b_distinction_basis'] for r in rows)),
    'blocking_condition_codes': dict(collections.Counter(
        t for r in rows for t in r['blocking_conditions'].split('|'))),
    'cross_component_status_codes': dict(collections.Counter(x['code'] for x in xs)),
    'cross_component_status_rows': sum(1 for r in rows if r['cross_component_status'] != 'NONE'),
    'genuine_contradiction_codes': dict(collections.Counter(c['code'] for c in cn)),
    'genuine_contradiction_rows': sum(1 for r in rows if r['contradictions_genuine'] != 'NONE'),
    'genuine_contradiction_entries': len(cn),
    'within_record_reporting_state': dict(collections.Counter(
        r['within_record_reporting_state'] for r in rows)),
    'cross_observation_disjointness_state': dict(collections.Counter(
        r['cross_observation_disjointness_state'] for r in rows)),
    'confirmation_status': {
        'job1_arithmetic_independently_confirmed': True,
        'job2_independently_confirmed': False,
        'job3_independently_confirmed': False,
        'note': 'Only job 1 arithmetic was independently re-derived (VERIFY-job1-arithmetic.md). '
                'The 552-key spine, the disease attribution and the phase attribution are inherited '
                'from an unconfirmed chain. Correcting A, B and C does not confirm job 2 or job 3.'},
    'endpoint_manuscript_status': 'PARKED',
    'endpoint_hold_findings_preserved': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10'],
    'endpoint_hold_satisfied_by_this_ledger': False,
    'grain_preservation_vs_v1': grain,
    'disposition_map_rows': len(disp),
    'v1_contradiction_rows_rederived': sum(v1_code_rows.values()),
    'v1_contradiction_code_rows': dict(v1_code_rows),
    'v2_register_code_rows': dict(v2_code_rows),
}
with open(os.path.join(HERE, 'INTEGRATION2-CENSUS.json'), 'w', encoding='utf-8') as f:
    json.dump(cen, f, indent=1, sort_keys=True)

# ------------------------------------------------------------------------ input manifest
man = {}
for d, fs in ((A2_DIR, ['corrected-a-v2-rows.tsv', 'corrected-a-v2-checks.json',
                        'corrected-a-v2-summary.json', 'corrected-a-v2-change-map.tsv']),
              (B1_DIR, ['LEDGER-response-observations.tsv', 'RELATED-SETS-unresolved.tsv',
                        'CHECKS.json']),
              (B2_DIR, ['RELATED-SETS-encoding-vs-semantics-v2.tsv', 'CHECKS-v2.json',
                        'RELABEL-SUMMARY-v2.json', 'CHANGE-MAP-v1-to-v2.tsv',
                        'GROUP-RELATIONS-candidate-parent-component-v2.tsv',
                        'ENROLLMENT-EXCESS-CATEGORIES-v2.tsv',
                        'NEGATIVE-CONTROL-wording-only-duplicate.json']),
              (C2_DIR, ['CORRECTED-C-arm-attribution-v2-map.tsv',
                        'CORRECTED-C-arm-attribution-v2-checks.json',
                        'CHANGE-MAP-v1-to-v2.tsv']),
              (V1_DIR, ['LEDGER-integrated-552.tsv', 'COVERAGE-b-observations.tsv',
                        'CONTRADICTIONS.tsv',
                        'INTEGRATION-CENSUS.json', 'INTEGRATION-CHECKS.json',
                        'RUN1-FAILING-checks.log', 'NEG-CONTROL-checks.log',
                        'CHECK-RUN-RECORD.txt'])):
    for fn in fs:
        man[os.path.relpath(os.path.join(d, fn), LANE)] = sha(os.path.join(d, fn))
with open(os.path.join(HERE, 'INPUT-MANIFEST2.json'), 'w', encoding='utf-8') as f:
    json.dump({'note': 'sha256 of every immutable input this integration reads and must not modify. '
                       'The v1 integration files, including its original failing and negative-control '
                       'logs, are listed here so their preservation is checkable (check J14).',
               'input_sha256': man}, f, indent=1, sort_keys=True)

print(json.dumps(cen, indent=1, sort_keys=True))
