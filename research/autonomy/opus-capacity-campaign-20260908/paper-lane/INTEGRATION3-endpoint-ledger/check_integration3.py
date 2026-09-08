#!/usr/bin/env python3
"""Deterministic checks over INTEGRATION3, the C2-v3 propagation. Exit 1 if any check fails.

Every check recomputes its quantity from the emitted tables and the component inputs. A check that
cannot recompute its quantity FAILS; it never passes by absence.

Usage:  python3 check_integration3.py [--dir <ledger dir>]
"""
import csv, json, os, sys, hashlib, collections

csv.field_size_limit(10 ** 9)
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
TARGET = HERE
if '--dir' in sys.argv:
    TARGET = os.path.abspath(sys.argv[sys.argv.index('--dir') + 1])

A2_DIR = os.path.join(LANE, "CORRECTED-A-denominator-category-v2")
B1_DIR = os.path.join(LANE, "CORRECTED-B-identity-selection-overlap", "artifacts")
B2_DIR = os.path.join(LANE, "CORRECTED-B2-identity-overlap-inference-repair-v2", "artifacts")
C2_DIR = os.path.join(LANE, "C2-correction")
V1_DIR = os.path.join(LANE, "INTEGRATION-endpoint-ledger")
V2_DIR = os.path.join(LANE, "INTEGRATION2-endpoint-ledger")


def rd(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


L = rd(os.path.join(TARGET, 'LEDGER3-integrated-552.tsv'))
COV = rd(os.path.join(TARGET, 'COVERAGE3-b-observations.tsv'))
DISP = rd(os.path.join(TARGET, 'DISPOSITION-MAP3.tsv'))
XS = rd(os.path.join(TARGET, 'CROSS-COMPONENT-STATUS3.tsv'))
CN = rd(os.path.join(TARGET, 'CONTRADICTIONS-genuine3.tsv'))
TN = rd(os.path.join(TARGET, 'UNRESOLVED-TENSIONS3.tsv'))
CEN = json.load(open(os.path.join(TARGET, 'INTEGRATION3-CENSUS.json')))
MAN = json.load(open(os.path.join(TARGET, 'INPUT-MANIFEST3.json')))['input_sha256']

A = rd(os.path.join(A2_DIR, 'corrected-a-v2-rows.tsv'))
C = rd(os.path.join(C2_DIR, 'CORRECTED-C-arm-attribution-v3-map.tsv'))
BOBS = rd(os.path.join(B1_DIR, 'LEDGER-response-observations.tsv'))
BSET = rd(os.path.join(B2_DIR, 'RELATED-SETS-encoding-vs-semantics-v2.tsv'))
V1LED = rd(os.path.join(V1_DIR, 'LEDGER-integrated-552.tsv'))
V2LED = rd(os.path.join(V2_DIR, 'LEDGER2-integrated-552.tsv'))
V2CN = rd(os.path.join(V2_DIR, 'CONTRADICTIONS-genuine.tsv'))

res = []


def chk(name, ok, detail):
    res.append({'check': name, 'result': 'PASS' if ok else 'FAIL', 'detail': detail})


# ---- J0 the B v1 observation ledger and the B2 set file are the correct pairing --------------
BSET_V1 = rd(os.path.join(B1_DIR, 'RELATED-SETS-unresolved.tsv'))
v1_map = {r['cohort_key']: r['observation_ids'] for r in BSET_V1}
v2_map = {r['cohort_key']: r['observation_ids'] for r in BSET}
chk('J0_B2_set_file_has_the_same_cohort_keys_and_membership_as_the_B_v1_observation_ledger',
    v1_map == v2_map and len(v2_map) == 8740,
    f'v1_keys={len(v1_map)} v2_keys={len(v2_map)} '
    f'symmetric_difference={len(set(v1_map) ^ set(v2_map))} '
    f'membership_strings_differing={sum(1 for k in v2_map if v1_map.get(k) != v2_map[k])}')

# ---- J1 spine identity and grain preservation -------------------------------------------------
keys = [r['integration_row_key'] for r in L]
chk('J1_spine_is_552_unique_rows_bijective_with_A2',
    len(L) == 552 and len(set(keys)) == 552 and len(A) == 552,
    f'ledger_rows={len(L)} distinct={len(set(keys))} A2_rows={len(A)}')

chk('J1b_spine_row_key_set_identical_to_the_v1_integration',
    sorted(keys) == sorted(r['integration_row_key'] for r in V1LED),
    f'v2_keys={len(set(keys))} v1_keys={len(set(r["integration_row_key"] for r in V1LED))} '
    f'symmetric_difference={len(set(keys) ^ set(r["integration_row_key"] for r in V1LED))}')

# ---- J2 A<->C bridge ---------------------------------------------------------------------------
cb = collections.Counter((r['nct'], r['om_title'], r['group_title']) for r in C)
ab = collections.Counter((r['input_key_nct_id'], r['om_title'], r['group_title']) for r in A)
chk('J2_A_to_C_title_bridge_is_unique_on_both_sides_and_total',
    (cb and ab and max(cb.values()) == 1 and max(ab.values()) == 1 and
     set(cb) == set(ab)),
    f'C_max_multiplicity={max(cb.values())} A_max_multiplicity={max(ab.values())} '
    f'only_in_A={len(set(ab) - set(cb))} only_in_C={len(set(cb) - set(ab))}')

c_by = {(r['nct'], r['om_title'], r['group_title']): r for r in C}
mism = sum(1 for a in A
           if c_by[(a['input_key_nct_id'], a['om_title'], a['group_title'])]['evaluable_n']
           != a['job1_evaluable_n_sum_of_four_producer_cells'])
chk('J2b_C2_evaluable_n_key_component_agrees_with_A2_carried_job1_value',
    mism == 0, f'mismatches={mism}')

# ---- J3 A<->B join recomputed ------------------------------------------------------------------
b_by_obs = {r['obs_id'] for r in BOBS}
b_ncts = set(r['nct'] for r in BOBS)
b_oms = set((r['nct'], r['om_index']) for r in BOBS)
bad, cens = 0, collections.Counter()
for r in L:
    obs = r['obs_id_b_form']
    if obs in b_by_obs:
        want = 'JOINED_UNIQUE'
    elif r['nct_id'] not in b_ncts:
        want = 'TRIAL_OUTSIDE_B_CORPUS_SCOPE'
    elif (r['nct_id'], r['om_index']) not in b_oms:
        want = 'MEASURE_OUTSIDE_B_TITLE_BOUNDARY'
    else:
        want = 'GROUP_ABSENT_IN_B_MEASURE'
    cens[want] += 1
    if want != r['b_join_state']:
        bad += 1
chk('J3_A_to_B_join_state_recomputed_and_exhaustive', bad == 0,
    f'mislabelled={bad} census={dict(cens)}')

chk('J3b_covered_grains_preserved_552_458_94_15658',
    len(L) == 552 and cens['JOINED_UNIQUE'] == 458 and
    (cens['TRIAL_OUTSIDE_B_CORPUS_SCOPE'] + cens['MEASURE_OUTSIDE_B_TITLE_BOUNDARY'] +
     cens['GROUP_ABSENT_IN_B_MEASURE']) == 94 and
    sum(1 for c in COV if c['in_integrated_552'] == 'no') == 15658,
    f'spine={len(L)} joined={cens["JOINED_UNIQUE"]} not_assessed={94 if (cens["TRIAL_OUTSIDE_B_CORPUS_SCOPE"] + cens["MEASURE_OUTSIDE_B_TITLE_BOUNDARY"] + cens["GROUP_ABSENT_IN_B_MEASURE"]) == 94 else (cens["TRIAL_OUTSIDE_B_CORPUS_SCOPE"] + cens["MEASURE_OUTSIDE_B_TITLE_BOUNDARY"] + cens["GROUP_ABSENT_IN_B_MEASURE"])} b_only={sum(1 for c in COV if c["in_integrated_552"] == "no")}')

# ---- J4 nothing inner-joined away --------------------------------------------------------------
chk('J4_every_B_observation_is_dispositioned_none_inner_joined_away',
    len(COV) == len(BOBS) == 16116 and
    len(set(c['obs_id'] for c in COV)) == len(BOBS),
    f'B_obs={len(BOBS)} coverage_rows={len(COV)} '
    f'in_spine={sum(1 for c in COV if c["in_integrated_552"] == "yes")} '
    f'B_only={sum(1 for c in COV if c["in_integrated_552"] == "no")}')

# ---- J5 component states carried verbatim, never overwritten -----------------------------------
a_by = {(r['input_key_nct_id'], str(int(r['input_key_om_index'])), r['input_key_group_id']): r for r in A}
bo_by = {r['obs_id']: r for r in BOBS}
set_by_obs = {}
for r in BSET:
    for o in r['observation_ids'].split('|'):
        set_by_obs[o] = r
viol = []
for r in L:
    a = a_by[(r['nct_id'], r['om_index'], r['group_id'])]
    if (r['a_proportion_suitability'] != a['proportion_suitability'] or
            r['a_unresolved_reason_codes'] != a['unresolved_reason_codes'] or
            r['a_advisory_flag_codes'] != a['advisory_flag_codes'] or
            r['a_reported_denominator_participants'] != a['reported_denominator_participants']):
        viol.append(('A', r['integration_row_key']))
    c = c_by[(r['nct_id'], r['om_title'], r['group_title'])]
    if (r['c_arm_link_state'] != c['arm_link_state'] or
            r['c_comparator_role'] != c['comparator_role'] or
            r['c_registry_type_statement'] != c['registry_type_statement'] or
            r['c_registry_type_statement_assumption'] != c['registry_type_statement_assumption'] or
            r['c_contested_flags'] != c['contested_flags']):
        viol.append(('C', r['integration_row_key']))
    s = set_by_obs.get(r['obs_id_b_form'])
    if s is not None and (r['b_semantic_duplication_status'] != s['semantic_duplication_status'] or
                          r['b_encoding_identity_status'] != s['encoding_identity_status'] or
                          r['b_distinction_basis'] != s['distinction_basis'] or
                          r['b_selection_status'] != s['selection_status']):
        viol.append(('B2', r['integration_row_key']))
chk('J5_component_states_arrive_verbatim_and_no_component_overwrites_another',
    not viol, f'violations={len(viol)} first={viol[:3]}')

# ---- J6 A doubt is not overwritten by C confidence ---------------------------------------------
both = [r for r in L if r['a_proportion_suitability'] == 'UNSUITABLE_FOR_PROPORTION'
        and r['c_arm_link_state'] == 'SOURCE_FIELD_MATCH']
chk('J6_A_doubt_is_not_overwritten_by_C_confidence',
    all(r['integration_state'] == 'BLOCKED' and
        'AXIS_DENOMINATOR_CATEGORY:A_UNSUITABLE_FOR_PROPORTION' in r['blocking_conditions'] and
        'CROSS_COMPONENT_CONSTRAINT:A_UNSUITABLE_WITH_C_ARM_SOURCE_FIELD_MATCH' in r['cross_component_status']
        for r in both),
    f'rows_A_unsuitable_and_C_arm_source_field_match={len(both)}; all retain both states and stay BLOCKED')

# ---- J7 no forbidden derived quantity ----------------------------------------------------------
FORBIDDEN_SUBSTR = ('rate_value', 'proportion_value', 'response_rate', 'percent',
                    'unique_patient_count', 'pooled_n', 'capacity_bound', 'effect_size',
                    'odds_ratio', 'risk_ratio', 'control_vs')
# short tokens that would false-positive as substrings (e.g. 'orr' inside 'correspondence') are
# matched as whole underscore-separated words instead
FORBIDDEN_WORDS = ('orr', 'rr', 'pct', 'pfs', 'n_responders', 'responders')
SENTINELS = ['rate_derived', 'unique_patient_total_derived', 'control_comparison_derived',
             'cross_disease_capacity_bound_derived', 'agent_independent_effect_derived']
offending = [c for c in L[0].keys()
             if (any(t in c.lower() for t in FORBIDDEN_SUBSTR)
                 or any(w in c.lower().split('_') for w in FORBIDDEN_WORDS))
             and c not in SENTINELS]
bad_sent = [(c, r['integration_row_key']) for r in L for c in SENTINELS if r[c] != 'NOT_DERIVED']
# value-level: no cell anywhere in the ledger may hold a bare decimal fraction or a percentage
import re as _re
_num = _re.compile(r'^\s*(?:0?\.\d+|\d+(?:\.\d+)?\s*%)\s*$')
numeric_cells = [(r['integration_row_key'], c) for r in L for c in L[0].keys() if _num.match(r[c] or '')]
chk('J7_no_rate_proportion_unique_patient_capacity_or_effect_value_emitted',
    not offending and not bad_sent and not numeric_cells,
    f'offending_columns={offending}; proportion-shaped cells={len(numeric_cells)}; '
    f'sentinel columns={SENTINELS} all NOT_DERIVED on '
    f'{len(L) - len(set(k for _, k in bad_sent))}/{len(L)} rows')

# ---- J8 unconfirmed chain carried --------------------------------------------------------------
n8 = sum(1 for r in L if r['job1_arithmetic_independently_confirmed'] == 'true'
         and r['job2_independently_confirmed'] == 'false'
         and r['job3_independently_confirmed'] == 'false')
chk('J8_job2_and_job3_unconfirmed_carried_on_every_row', n8 == len(L),
    f'{n8}/{len(L)} rows carry job1=confirmed job2=false job3=false')

# ---- J9 disposition map completeness -----------------------------------------------------------
dc = collections.Counter(d['component'] for d in DISP)
chk('J9_disposition_map_covers_every_component_record_exactly_once',
    dc['CORRECTED-A-v2'] == 552 and dc['CORRECTED-C-v3'] == 552 and
    dc['CORRECTED-B/B2'] == 16116 + 94 and
    len(set((d['component'], d['component_record_key']) for d in DISP)) == len(DISP),
    f'A={dc["CORRECTED-A-v2"]} C={dc["CORRECTED-C-v3"]} B={dc["CORRECTED-B/B2"]} '
    f'(B = 16116 observations + 94 spine rows B never assessed)')

# ---- J10 competing sets retained, not collapsed, not resolved ----------------------------------
comp = [r for r in L if r['b_n_observations_in_cohort_set'] not in ('', '1')]
chk('J10_competing_sets_retained_unresolved_and_never_selected',
    all(r['b_semantic_duplication_status'] == 'UNRESOLVED__SEMANTIC_CORRESPONDENCE_NOT_ESTABLISHED'
        and r['b_selection_status'] == 'NOT_SELECTED_BY_DESIGN'
        and r['b_sibling_observation_ids'] for r in comp),
    f'spine rows in a multi-observation cohort set={len(comp)}; corpus-wide competing sets='
    f'{sum(1 for r in BSET if int(r["n_observations"]) > 1)}')

# ---- J11 B2 scope: non-identical ENCODING only, never semantic non-duplication -----------------
FORBIDDEN_SEM = ('DUPLICATE_ENCODINGS_DO_NOT_OCCUR', 'SEMANTICALLY_DISTINCT',
                 'DISTINCT_OUTCOME_CONFIRMED', 'NOT_A_DUPLICATE', 'SEMANTIC_DUPLICATION_EXCLUDED',
                 'NON_DUPLICATE_CONFIRMED')
hits = []
for path in ('LEDGER3-integrated-552.tsv', 'COVERAGE3-b-observations.tsv',
             'CROSS-COMPONENT-STATUS3.tsv', 'CONTRADICTIONS-genuine3.tsv',
             'UNRESOLVED-TENSIONS3.tsv',
             'DISPOSITION-MAP3.tsv', 'INTEGRATION3-CENSUS.json'):
    txt = open(os.path.join(TARGET, path), encoding='utf-8').read()
    for t in FORBIDDEN_SEM:
        if t in txt:
            hits.append((path, t))
sem = collections.Counter(r['b_semantic_duplication_status'] for r in L if r['b_semantic_duplication_status'])
chk('J11_B2_non_identical_encoding_scope_propagated_without_semantic_nonduplication_claim',
    not hits and sem.get('SEMANTICALLY_RESOLVED', 0) == 0,
    f'forbidden_semantic_tokens={hits}; spine semantic_duplication_status census={dict(sem)}')

# ---- J12 no state is stronger than the component that produced it ------------------------------
retired = ('NOT_CONTROL_BY_ARM_SET_TYPE_INVARIANT', 'NOT_CONTROL_CONFIRMED', 'NOT_CONTROL',
           'CONFIRMED_TYPE_ONLY', 'RESPONSE_BEARING_CATEGORY_DROPPED_BY_PRODUCER',
           'DUPLICATE_ENCODING_CANDIDATE',
           # retired by the C2 v2 -> v3 correction; none may survive the propagation
           'SOURCE_CONFIRMED', 'COMPARATOR_SUPPORTED_BY_SOURCE_CONFIRMED_ARM_TYPE',
           'COMPARATOR_PROPOSED_BY_LABEL_MATCHED_ARM_TYPE',
           'ASSUMES_LABEL_CORRESPONDENCE_IS_ARM_IDENTITY')
CHANGE_MAP_COLS = {'c_disposition_vs_v1'}
state_cols = [c for c in L[0].keys() if c not in CHANGE_MAP_COLS]
present = sorted({t for r in L for c in state_cols for t in retired if t in (r[c] or '')})
# the retired NOT_CONTROL vocabulary may appear ONLY as C2's historical change-map token
cm_bad = [r['integration_row_key'] for r in L
          if 'NOT_CONTROL' in r['c_disposition_vs_v1']
          and not r['c_disposition_vs_v1'].startswith('CHANGED_CLASS:NOT_CONTROL_ASSERTED->')]
present += [f'CHANGE_MAP_MISUSE:{k}' for k in cm_bad[:3]]
allowed_arm = {'SOURCE_FIELD_MATCH', 'LABEL_MATCH', 'PROPOSED', 'CONTESTED',
               'UNKNOWN_IN_THIS_CACHE', 'UNRESOLVED'}
arm_ok = set(r['c_arm_link_state'] for r in L) <= allowed_arm
chk('J12_no_retired_or_strengthened_state_appears_in_the_ledger',
    not present and arm_ok,
    f'retired_tokens_present={present}; arm_link_states={sorted(set(r["c_arm_link_state"] for r in L))}')

# ---- J13 the two unknowns are separated --------------------------------------------------------
d_ok = all(r['cross_observation_disjointness_state'] ==
           'UNVERIFIABLE_IN_THIS_CACHE__NO_PARTICIPANT_FLOW_MODULE' and
           r['cross_observation_disjointness_scope'] ==
           'LIMITS_POOLING_AND_UNIQUE_PATIENT_COUNTING_ACROSS_OBSERVATIONS_ONLY' and
           r['within_record_reporting_barred_by_absent_participant_flow'] ==
           'NO__ABSENCE_OF_PARTICIPANT_FLOW_IS_NOT_A_WITHIN_RECORD_REPORTING_BAR'
           for r in L)
# no within-record state may cite participant flow, and no disjointness code may appear as a
# within-record reason
leak = [r['integration_row_key'] for r in L
        if 'PARTICIPANT_FLOW' in r['within_record_reporting_state'].upper()
        or 'DISJOINT' in r['within_record_reporting_state'].upper()]
axis_leak = [r['integration_row_key'] for r in L
             if r['blocking_conditions'].count('AXIS_CROSS_OBSERVATION_DISJOINTNESS:') != 1]
chk('J13_cross_observation_disjointness_and_within_record_reporting_are_separate_unknowns',
    d_ok and not leak and not axis_leak,
    f'all_rows_carry_both_axes={d_ok} within_record_states_citing_participant_flow={len(leak)} '
    f'rows_without_exactly_one_disjointness_condition={len(axis_leak)}')

chk('J13b_no_proportion_is_authorised_anywhere_in_this_integration',
    all(r['proportion_authorisation'] == 'NO_PROPORTION_AUTHORISED_IN_THIS_INTEGRATION' for r in L)
    and CEN['rates_or_proportions_derived'] == 0,
    f'rows={len(L)} census_rates_or_proportions_derived={CEN["rates_or_proportions_derived"]}')

# ---- J14 register discipline: genuine vs tension, after the demotion ---------------------------
# ONLY the A<->B denominator family survives the admission test in v3. Nothing derived from an
# unproved mapping or from a text/token inference may sit in the genuine register.
ALLOWED_GENUINE = ('CROSS_COMPONENT_CONTRADICTION:A_B_DENOMINATOR_VALUE_DISAGREE',)
bad_g = [c['code'] for c in CN if c['code'] not in ALLOWED_GENUINE]
bad_x = [x['code'] for x in XS if 'CONTRADICTION' in x['code']]
# the demoted register must not call itself a contradiction anywhere in its own codes
bad_t = [t['code'] for t in TN if 'CONTRADICTION' in t['code']]
bad_tp = [t['code'] for t in TN
          if not t['code'].startswith(('UNRESOLVED_MAPPING_TENSION:', 'UNRESOLVED_EVIDENCE_TENSION:'))]
chk('J14_contradiction_is_reserved_for_incompatible_claims_only',
    not bad_g and not bad_x and not bad_t and not bad_tp,
    f'genuine_entries={len(CN)} genuine_rows={len(set(c["integration_row_key"] for c in CN))} '
    f'tension_entries={len(TN)} tension_rows={len(set(t["integration_row_key"] for t in TN))} '
    f'cross_component_entries={len(XS)} miscategorised_genuine={bad_g[:3]} '
    f'contradiction_words_in_status_register={bad_x[:3]} '
    f'contradiction_words_in_tension_codes={bad_t[:3]} mis-prefixed_tensions={bad_tp[:3]}')

# recompute BOTH registers from the components, independently of the builder
want_g = collections.Counter()
want_t = collections.Counter()
for r in L:
    c = c_by[(r['nct_id'], r['om_title'], r['group_title'])]
    if c['sole_arm_multi_results_group_flag'] == 'YES':
        want_t[r['integration_row_key']] += 1
    if c['contested_flags']:
        want_t[r['integration_row_key']] += len([t for t in c['contested_flags'].split('|') if t])
    b = bo_by.get(r['obs_id_b_form'])
    a = a_by[(r['nct_id'], r['om_index'], r['group_id'])]
    if b is not None and b['denominator_value_participants'] != a['reported_denominator_participants']:
        want_g[r['integration_row_key']] += 1
got_g = collections.Counter(c['integration_row_key'] for c in CN)
got_t = collections.Counter(t['integration_row_key'] for t in TN)
chk('J14b_genuine_contradiction_register_recomputed_from_the_components',
    want_g == got_g,
    f'recomputed_rows={len(want_g)} register_rows={len(got_g)} '
    f'entries={sum(want_g.values())} disagreements={len(set(want_g.items()) ^ set(got_g.items()))}')
chk('J14c_demoted_tension_register_recomputed_from_the_components',
    want_t == got_t,
    f'recomputed_rows={len(want_t)} register_rows={len(got_t)} '
    f'entries={sum(want_t.values())} disagreements={len(set(want_t.items()) ^ set(got_t.items()))}')

# ---- K19 the demotion LOST NOTHING: every v2 genuine entry is present here, in a register ------
v2_keys = collections.Counter(c['integration_row_key'] for c in V2CN)
here_keys = got_g + got_t
chk('K19_every_v2_genuine_entry_survives_the_demotion_in_one_register_or_the_other',
    v2_keys == here_keys,
    f'v2_entries={sum(v2_keys.values())} v3_entries={sum(here_keys.values())} '
    f'(genuine={sum(got_g.values())} tension={sum(got_t.values())}) '
    f'row_disagreements={len(set(v2_keys.items()) ^ set(here_keys.items()))}')

# ---- K20 the underlying source flags are preserved verbatim, not thinned by the demotion -------
flag_pairs = {
    'sole_arm_YES': (sum(1 for r in C if r['sole_arm_multi_results_group_flag'] == 'YES'),
                     sum(1 for r in L if r['c_sole_arm_multi_results_group_flag'] == 'YES')),
    'rows_with_contested_flags': (sum(1 for r in C if r['contested_flags'].strip()),
                                  sum(1 for r in L if r['c_contested_flags'].strip())),
    'contested_flag_tokens': (sum(len([t for t in r['contested_flags'].split('|') if t]) for r in C),
                              sum(len([t for t in r['c_contested_flags'].split('|') if t]) for r in L)),
}
chk('K20_demotion_changed_the_register_not_the_flags',
    all(a == b for a, b in flag_pairs.values()),
    '; '.join(f'{k}: c2_v3={a} ledger={b}' for k, (a, b) in flag_pairs.items()))

# ---- K21 the v3 count complement: no row is left unblocked on arm attribution -------------------
no_join = [r['integration_row_key'] for r in L
           if 'AXIS_ARM_ATTRIBUTION:C_REGISTRY_SOURCE_JOIN_NOT_ESTABLISHED' not in r['blocking_conditions']]
join_states = set(r['source_join_verification'] for r in C)
chk('K21_v3_registry_join_is_unverified_on_every_row_so_arm_attribution_has_no_confirmed_complement',
    not no_join and join_states == {'NOT_ESTABLISHED_REGISTRY_JOIN_FIELDS_ABSENT_FROM_THIS_CACHE'},
    f'rows_without_the_universal_join_block={len(no_join)} c2_v3_join_states={sorted(join_states)}')

# ---- K22 the withdrawal is recorded, and v2 is intact ------------------------------------------
w = CEN.get('withdrawn_v2_assertions', {})
v2_files_in_manifest = [p for p in MAN if p.startswith('INTEGRATION2-endpoint-ledger/')]
chk('K22_v2_counts_are_withdrawn_as_assertions_and_preserved_as_history',
    w.get('v2_genuine_contradiction_entries_claimed') == 91 and
    w.get('v2_v1_rows_called_genuine_claimed') == 90 and
    w.get('v3_status_of_those_counts') == 'WITHDRAWN_AS_ASSERTIONS__PRESERVED_AS_HISTORY' and
    len(v2_files_in_manifest) >= 8 and os.path.isdir(V2_DIR),
    f'census records the withdrawn 91/91/90; v2 files hashed in the manifest={len(v2_files_in_manifest)}; '
    f'v2 directory present={os.path.isdir(V2_DIR)}')

# ---- J15 census matches recomputation ----------------------------------------------------------
recomp = {
    'spine_rows': len(L),
    'b_observations_not_in_spine': sum(1 for c in COV if c['in_integrated_552'] == 'no'),
    'integration_state': dict(collections.Counter(r['integration_state'] for r in L)),
    'c_arm_link_state': dict(collections.Counter(r['c_arm_link_state'] for r in L)),
    'c_comparator_role': dict(collections.Counter(r['c_comparator_role'] for r in L)),
    'b_join_state': dict(collections.Counter(r['b_join_state'] for r in L)),
    'a_proportion_suitability': dict(collections.Counter(r['a_proportion_suitability'] for r in L)),
    'genuine_contradiction_entries': len(CN),
    'unresolved_tension_entries': len(TN),
    'unresolved_tension_rows': sum(1 for r in L if r['unresolved_tensions'] != 'NONE'),
    'unresolved_tension_kinds': dict(collections.Counter(t['tension_kind'] for t in TN)),
    'cross_component_status_rows': sum(1 for r in L if r['cross_component_status'] != 'NONE'),
    'disposition_map_rows': len(DISP),
}
diff = {k: (v, CEN.get(k)) for k, v in recomp.items() if CEN.get(k) != v}
chk('J15_census_matches_recomputation_from_the_emitted_tables', not diff, f'differences={diff}')

# ---- J16 inputs, and the whole v1 integration, unmodified --------------------------------------
changed = [p for p, h in MAN.items() if sha(os.path.join(LANE, p)) != h]
chk('J16_component_inputs_and_the_entire_v1_integration_are_unmodified',
    not changed, f'{len(MAN)} input files re-hashed, {len(changed)} changed: {changed[:3]}')

v1_logs = ['RUN1-FAILING-checks.log', 'NEG-CONTROL-checks.log', 'CHECK-RUN-RECORD.txt']
missing = [f for f in v1_logs if not os.path.exists(os.path.join(V1_DIR, f))]
chk('J16b_v1_original_failing_and_negative_control_logs_still_present_and_hashed',
    not missing and all(os.path.relpath(os.path.join(V1_DIR, f), LANE) in MAN for f in v1_logs),
    f'v1 logs present={[f for f in v1_logs if f not in missing]} missing={missing}')

v2_files = ['LEDGER2-integrated-552.tsv', 'CONTRADICTIONS-genuine.tsv',
            'CONTRADICTION-REDERIVATION.tsv', 'INTEGRATION2-CENSUS.json',
            'INTEGRATION2-CHECKS.json', 'CHECK-RUN-RECORD.txt']
v2_missing = [f for f in v2_files if not os.path.exists(os.path.join(V2_DIR, f))]
chk('J16c_v2_including_its_now_withdrawn_genuine_register_is_present_hashed_and_unmodified',
    not v2_missing and all(os.path.relpath(os.path.join(V2_DIR, f), LANE) in MAN for f in v2_files),
    f'v2 files present={len(v2_files) - len(v2_missing)}/{len(v2_files)} missing={v2_missing}; '
    f'withdrawing a count must not alter one byte of v2')

# ---- J17 endpoint hold preserved ---------------------------------------------------------------
hold = open(os.path.join(LANE, 'HOLD-endpoint-extraction-validity.md'), encoding='utf-8').read()
present_f = [f'F{i}' for i in range(1, 11)
             if (f'**F{i}**' in hold or f'**F{i} ' in hold)]
chk('J17_endpoint_hold_and_its_ten_findings_preserved_and_not_satisfied_here',
    len(present_f) == 10 and CEN['endpoint_hold_satisfied_by_this_ledger'] is False and
    CEN['endpoint_manuscript_status'] == 'PARKED' and
    all(r['endpoint_manuscript_status'].startswith('PARKED') for r in L),
    f'findings_found_in_hold={len(present_f)}/10 census_status={CEN["endpoint_manuscript_status"]} '
    f'hold_satisfied={CEN["endpoint_hold_satisfied_by_this_ledger"]}')

# ---- J18 no eligibility subset was constructed --------------------------------------------------
resid = [r for r in L if r['integration_state'] != 'BLOCKED']
subset_files = [f for f in os.listdir(TARGET)
                if 'ELIGIBLE' in f.upper() or 'ANALYSABLE' in f.upper() or 'SELECTED' in f.upper()]
chk('J18_no_scientific_eligibility_subset_is_constructed_or_emitted',
    not subset_files and CEN['eligibility_subsets_constructed'] == 0 and
    all(r['integration_state'] == 'NO_COMPONENT_BLOCK_FOUND__NOT_AN_ELIGIBILITY_GRANT'
        for r in resid) and
    all('AXIS_CROSS_OBSERVATION_DISJOINTNESS:' in r['blocking_conditions'] for r in resid),
    f'rows_without_a_component_specific_block={len(resid)} (named NOT_AN_ELIGIBILITY_GRANT, all '
    f'still carrying the universal disjointness condition); subset_files={subset_files}')

out = {'component': 'INTEGRATION3-endpoint-ledger', 'target_dir': os.path.basename(TARGET),
       'checks': res,
       'passed': sum(1 for r in res if r['result'] == 'PASS'),
       'failed': sum(1 for r in res if r['result'] == 'FAIL'),
       'total': len(res)}
with open(os.path.join(TARGET, 'INTEGRATION3-CHECKS.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1)
for r in res:
    print(f"{r['result']}  {r['check']}  {r['detail']}")
print(f"passed={out['passed']} failed={out['failed']} total={out['total']}")
sys.exit(1 if out['failed'] else 0)
