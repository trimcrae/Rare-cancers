#!/usr/bin/env python3
"""Build the proposed source-bound integration ledger from CORRECTED-A / -B / -C.

READ-ONLY over all three components and over every job1/job2/job3 original and leaf file.
Writes only into INTEGRATION-endpoint-ledger/.
No network. No rate, proportion, unique-patient total or comparison is computed anywhere.
"""
import csv, json, os, sys, hashlib, collections

csv.field_size_limit(10 ** 9)
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
A_DIR = os.path.join(LANE, "CORRECTED-A-denominator-category")
B_DIR = os.path.join(LANE, "CORRECTED-B-identity-selection-overlap", "artifacts")
C_DIR = os.path.join(LANE, "CORRECTED-C-arm-attribution")

def rd(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t'))

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

A = rd(os.path.join(A_DIR, "corrected-a-rows.tsv"))
C = rd(os.path.join(C_DIR, "CORRECTED-C-arm-attribution-map.tsv"))
BOBS = rd(os.path.join(B_DIR, "LEDGER-response-observations.tsv"))
BSET = rd(os.path.join(B_DIR, "RELATED-SETS-unresolved.tsv"))

# ---------- declared join ----------
# A grain : (input_key_nct_id, input_key_om_index, input_key_group_id)  -- 552
# C grain : (nct, om_title, group_title, evaluable_n)                   -- 552, NO om_index/group_id
# B grain : obs_id = "<nct>#om<om_index>#<results_group_id>"            -- 16116
# A->C bridge: (nct, om_title, group_title). Verified unique on both sides by check I2.
# A->B bridge: obs_id constructed from A's own key. Partial by construction (check I3).
c_by_bridge = {}
for r in C:
    c_by_bridge.setdefault((r['nct'], r['om_title'], r['group_title']), []).append(r)
b_by_obs = {r['obs_id']: r for r in BOBS}
set_by_obs, set_by_key = {}, {}
for r in BSET:
    set_by_key[r['cohort_key']] = r
    for o in r['observation_ids'].split('|'):
        set_by_obs[o] = r
b_ncts = set(r['nct'] for r in BOBS)
b_oms = set((r['nct'], r['om_index']) for r in BOBS)

ARM_CONFIRMED = {"CONFIRMED"}

rows = []
for a in A:
    nct = a['input_key_nct_id']; om = str(int(a['input_key_om_index'])); gid = a['input_key_group_id']
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

    blocking = []
    if a['proportion_suitability'] == 'UNSUITABLE_FOR_PROPORTION':
        blocking.append('A_DENOMINATOR_OR_CATEGORY_UNSUITABLE')
    if c is None:
        blocking.append('C_NOT_JOINED')
    else:
        if c['arm_link_state'] not in ARM_CONFIRMED:
            blocking.append('C_ARM_LINK_NOT_CONFIRMED:' + c['arm_link_state'])
        if c['control_status'] == 'CONTESTED':
            blocking.append('C_CONTROL_STATUS_CONTESTED')
        elif c['control_status'] == 'UNKNOWN_IN_THIS_CACHE':
            blocking.append('C_CONTROL_STATUS_UNKNOWN_IN_THIS_CACHE')
        elif c['control_status'].endswith('CANDIDATE_GROUP_TEXT_ONLY'):
            blocking.append('C_CONTROL_STATUS_CANDIDATE_ONLY')
    if b is None:
        blocking.append('B_NOT_ASSESSED:' + b_join_state)
    else:
        if b['usable_for_proportion'].strip().lower() not in ('true', 'yes', '1'):
            blocking.append('B_OBSERVATION_NOT_USABLE_FOR_PROPORTION')
        if s is not None and int(s['n_observations']) > 1:
            blocking.append('B_COMPETING_RECORDS_UNRESOLVED')
    # disjointness is unverifiable for every row, by B's own C21 finding
    blocking.append('B_DISJOINTNESS_UNVERIFIABLE_NO_PARTICIPANT_FLOW')

    contradictions = []
    if c is not None:
        if a['proportion_suitability'] == 'UNSUITABLE_FOR_PROPORTION' and c['arm_link_state'] == 'CONFIRMED':
            contradictions.append('A_UNSUITABLE_WHILE_C_ARM_CONFIRMED')
        if a['proportion_suitability'] == 'NOT_REFUTED_BY_THIS_COMPONENT' and c['arm_link_state'] != 'CONFIRMED':
            contradictions.append('A_NOT_REFUTED_WHILE_C_ARM_' + c['arm_link_state'])
        if c['contested_flag']:
            contradictions.append('C_CONTESTED_FLAG_PRESENT')
        if c['sole_arm_multi_results_group_flag'] == 'YES':
            contradictions.append('C_SOLE_ARM_BUT_MULTIPLE_RESULTS_GROUPS')
    if b is not None:
        if a['proportion_suitability'] == 'NOT_REFUTED_BY_THIS_COMPONENT' and \
           b['usable_for_proportion'].strip().lower() not in ('true', 'yes', '1'):
            contradictions.append('A_NOT_REFUTED_WHILE_B_OBSERVATION_UNUSABLE')
        if s is not None and int(s['n_observations']) > 1 and \
           a['proportion_suitability'] == 'NOT_REFUTED_BY_THIS_COMPONENT':
            contradictions.append('A_NOT_REFUTED_WHILE_B_SET_UNRESOLVED')
        if b['denominator_value_participants'] != a['reported_denominator_participants']:
            contradictions.append('A_B_DENOMINATOR_VALUE_DISAGREE')
    else:
        contradictions.append('ROW_NOT_ASSESSED_BY_B')

    substantive = [t for t in blocking if t != 'B_DISJOINTNESS_UNVERIFIABLE_NO_PARTICIPANT_FLOW']
    if not substantive:
        state = 'NO_COMPONENT_BLOCK_FOUND__NOT_AN_ELIGIBILITY_GRANT'
    else:
        state = 'BLOCKED'

    rows.append({
        'integration_row_key': f"{nct}|OM{om}|{gid}",
        'a_row_key': a['row_key'],
        'nct_id': nct, 'om_index': om, 'group_id': gid,
        'obs_id_b_form': obs_id,
        'om_title': a['om_title'], 'group_title': a['group_title'],
        'payload_shard': a['payload_shard'], 'cache_revision': a['cache_revision'],
        # --- component A, carried verbatim, never overwritten ---
        'a_present': 'yes',
        'a_reported_denominator_participants': a['reported_denominator_participants'],
        'a_denominator_state': a['denominator_state'],
        'a_denominator_provenance': a['denominator_provenance'],
        'a_n_source_categories': a['n_source_categories'],
        'a_n_categories_kept_by_producer': a['n_categories_kept_by_producer'],
        'a_category_preservation_state': a['category_preservation_state'],
        'a_proportion_suitability': a['proportion_suitability'],
        'a_unresolved_reason_codes': a['unresolved_reason_codes'],
        'a_advisory_flag_codes': a['advisory_flag_codes'],
        'a_evaluable_n_minus_reported_denominator': a['evaluable_n_minus_reported_denominator'],
        'a_all_categories_sum_minus_reported_denominator': a['all_categories_sum_minus_reported_denominator'],
        'a_job1_classification_carried': a['job1_classification_carried'],
        'a_leaf_qa_coverage': a['leaf_qa_coverage'],
        # --- component C ---
        'c_join_state': c_join_state,
        'c_join_bridge': 'nct+om_title+group_title (C carries no om_index/group_id)',
        'c_arm_link_state': c['arm_link_state'] if c else '',
        'c_arm_link_evidence_code': c['arm_link_evidence_code'] if c else '',
        'c_confirmed_registry_arm_label': c['confirmed_registry_arm_label'] if c else '',
        'c_confirmed_registry_arm_type': c['confirmed_registry_arm_type'] if c else '',
        'c_candidate_registry_arm_labels': c['candidate_registry_arm_labels'] if c else '',
        'c_control_status': c['control_status'] if c else '',
        'c_contested_flag': c['contested_flag'] if c else '',
        'c_sole_arm_multi_results_group_flag': c['sole_arm_multi_results_group_flag'] if c else '',
        'c_arm_set_type_state': c['arm_set_type_state'] if c else '',
        'c_disposition_vs_job3': c['disposition_vs_job3'] if c else '',
        # --- component B ---
        'b_join_state': b_join_state,
        'b_cohort_key': s['cohort_key'] if s else '',
        'b_n_observations_in_cohort_set': s['n_observations'] if s else '',
        'b_sibling_observation_ids': s['observation_ids'] if s else '',
        'b_unresolved_states': s['unresolved_states'] if s else '',
        'b_selection_status': s['selection_status'] if s else '',
        'b_duplicate_encoding_candidate': s['duplicate_encoding_candidate'] if s else '',
        'b_denominator_state': b['denominator_state'] if b else '',
        'b_denominator_value_participants': b['denominator_value_participants'] if b else '',
        'b_reporting_status_state': b['reporting_status_state'] if b else '',
        'b_usable_for_proportion': b['usable_for_proportion'] if b else '',
        'b_unusable_reason': b['unusable_reason'] if b else '',
        'b_endpoint_constructs': b['endpoint_constructs'] if b else '',
        'b_assessment_criteria': b['assessment_criteria'] if b else '',
        'b_noncollection_statement': b['noncollection_statement'] if b else '',
        # --- integration verdicts ---
        'integration_state': state,
        'blocking_conditions': '|'.join(blocking),
        'contradictions_retained': '|'.join(contradictions) if contradictions else 'NONE',
        'job1_arithmetic_independently_confirmed': 'true',
        'job2_independently_confirmed': 'false',
        'job3_independently_confirmed': 'false',
        'rate_derived': 'NOT_DERIVED',
        'unique_patient_total_derived': 'NOT_DERIVED',
        'control_comparison_derived': 'NOT_DERIVED',
        'source_pointer': a['source_pointer'],
    })

LEDGER_COLS = list(rows[0].keys())
with open(os.path.join(HERE, 'LEDGER-integrated-552.tsv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, LEDGER_COLS, delimiter='\t', extrasaction='raise')
    w.writeheader(); w.writerows(rows)

# ---------- B-side coverage: every B observation, in-A or not ----------
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
        'unresolved_states': s['unresolved_states'] if s else '',
        'denominator_state': b['denominator_state'],
        'denominator_value_participants': b['denominator_value_participants'],
        'reporting_status_state': b['reporting_status_state'],
        'usable_for_proportion': b['usable_for_proportion'],
        'unusable_reason': b['unusable_reason'],
    })
with open(os.path.join(HERE, 'COVERAGE-b-observations.tsv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, list(cov[0].keys()), delimiter='\t'); w.writeheader(); w.writerows(cov)

# ---------- disposition map: one row per (component, record) ----------
disp = []
for r in rows:
    disp.append({'component': 'CORRECTED-A', 'component_grain': '(nct_id,om_index,group_id)',
                 'component_record_key': r['a_row_key'], 'integration_row_key': r['integration_row_key'],
                 'disposition': 'CARRIED_INTO_INTEGRATED_LEDGER',
                 'reason': 'A is the integration spine; every A row is present exactly once.'})
    disp.append({'component': 'CORRECTED-C', 'component_grain': '(nct,om_title,group_title,evaluable_n)',
                 'component_record_key': f"{r['nct_id']}|{r['om_title']}|{r['group_title']}",
                 'integration_row_key': r['integration_row_key'],
                 'disposition': 'JOINED_TO_A_ON_TITLE_BRIDGE' if r['c_join_state'] == 'JOINED_UNIQUE' else 'NOT_JOINED:' + r['c_join_state'],
                 'reason': 'C carries no om_index/group_id; the (nct,om_title,group_title) bridge is unique on both sides (check I2).'})
    disp.append({'component': 'CORRECTED-B', 'component_grain': 'obs_id=(nct,om_index,results_group_id)',
                 'component_record_key': r['obs_id_b_form'],
                 'integration_row_key': r['integration_row_key'],
                 'disposition': 'JOINED_TO_A_ON_OBSERVATION_KEY' if r['b_join_state'] == 'JOINED_UNIQUE' else 'NOT_PRESENT_IN_B:' + r['b_join_state'],
                 'reason': "B's corpus boundary is job2's response-title regex over 4,235 results trials; A/C's 552 keys come from job1's contract rows. The difference is retained, never inner-joined away."})
for c in cov:
    if c['in_integrated_552'] == 'no':
        disp.append({'component': 'CORRECTED-B', 'component_grain': 'obs_id=(nct,om_index,results_group_id)',
                     'component_record_key': c['obs_id'], 'integration_row_key': '',
                     'disposition': 'B_ONLY__NOT_IN_THE_552_SPINE',
                     'reason': 'No denominator/category component and no arm-attribution component exists for this observation. It is neither resolved nor excluded here.'})
with open(os.path.join(HERE, 'DISPOSITION-MAP.tsv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, ['component', 'component_grain', 'component_record_key',
                           'integration_row_key', 'disposition', 'reason'], delimiter='\t')
    w.writeheader(); w.writerows(disp)

# ---------- contradictions, retained as contradictions ----------
con = []
for r in rows:
    if r['contradictions_retained'] == 'NONE':
        continue
    for t in r['contradictions_retained'].split('|'):
        con.append({'integration_row_key': r['integration_row_key'], 'contradiction_code': t,
                    'a_state': r['a_proportion_suitability'],
                    'a_unresolved_reason_codes': r['a_unresolved_reason_codes'],
                    'c_arm_link_state': r['c_arm_link_state'], 'c_control_status': r['c_control_status'],
                    'c_contested_flag': r['c_contested_flag'],
                    'b_join_state': r['b_join_state'], 'b_usable_for_proportion': r['b_usable_for_proportion'],
                    'b_unresolved_states': r['b_unresolved_states'],
                    'resolution': 'BOTH_STATES_STAND__NEITHER_COMPONENT_OVERWRITES_THE_OTHER',
                    'source_pointer': r['source_pointer']})
with open(os.path.join(HERE, 'CONTRADICTIONS.tsv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, list(con[0].keys()), delimiter='\t'); w.writeheader(); w.writerows(con)

# ---------- census ----------
cen = {
    'component': 'INTEGRATION-endpoint-ledger',
    'cache_revision': rows[0]['cache_revision'],
    'network_access': 'none',
    'rates_or_proportions_derived': 0,
    'unique_patient_totals_derived': 0,
    'cross_disease_capacity_bounds_derived': 0,
    'control_comparisons_derived': 0,
    'spine_rows': len(rows),
    'a_rows_in': len(A), 'c_rows_in': len(C),
    'b_observation_rows_in': len(BOBS), 'b_cohort_keys_in': len(BSET),
    'c_join_state': dict(collections.Counter(r['c_join_state'] for r in rows)),
    'b_join_state': dict(collections.Counter(r['b_join_state'] for r in rows)),
    'b_observations_not_in_spine': sum(1 for c in cov if c['in_integrated_552'] == 'no'),
    'integration_state': dict(collections.Counter(r['integration_state'] for r in rows)),
    'a_proportion_suitability': dict(collections.Counter(r['a_proportion_suitability'] for r in rows)),
    'c_arm_link_state': dict(collections.Counter(r['c_arm_link_state'] for r in rows)),
    'c_control_status': dict(collections.Counter(r['c_control_status'] for r in rows)),
    'contradiction_codes': dict(collections.Counter(c['contradiction_code'] for c in con)),
    'blocking_condition_codes': dict(collections.Counter(
        t for r in rows for t in r['blocking_conditions'].split('|'))),
    'rows_with_at_least_one_contradiction': sum(1 for r in rows if r['contradictions_retained'] != 'NONE'),
    'confirmation_status': {
        'job1_arithmetic_independently_confirmed': True,
        'job2_independently_confirmed': False,
        'job3_independently_confirmed': False,
        'note': 'Only job 1 arithmetic was independently re-derived (VERIFY-job1-arithmetic.md). '
                'The 552-key spine, the disease attribution and the phase attribution are inherited '
                'from an unconfirmed chain.'},
    'disposition_map_rows': len(disp),
    'contradiction_rows': len(con),
}
with open(os.path.join(HERE, 'INTEGRATION-CENSUS.json'), 'w', encoding='utf-8') as f:
    json.dump(cen, f, indent=1, sort_keys=True)

man = {}
for d, fs in ((A_DIR, ['corrected-a-rows.tsv', 'corrected-a-checks.json', 'corrected-a-summary.json']),
              (B_DIR, ['LEDGER-response-observations.tsv', 'RELATED-SETS-unresolved.tsv', 'CHECKS.json']),
              (C_DIR, ['CORRECTED-C-arm-attribution-map.tsv', 'CORRECTED-C-arm-attribution-checks.json'])):
    for fn in fs:
        man[os.path.relpath(os.path.join(d, fn), LANE)] = sha(os.path.join(d, fn))
with open(os.path.join(HERE, 'INPUT-MANIFEST.json'), 'w', encoding='utf-8') as f:
    json.dump({'note': 'sha256 of the immutable component inputs this integration reads and must not modify',
               'input_sha256': man}, f, indent=1, sort_keys=True)

print(json.dumps(cen, indent=1, sort_keys=True))
