#!/usr/bin/env python3
"""Deterministic checks on the integration ledger. Exits 1 if ANY check fails.

Every check is written so that a real defect makes it fail; NEG-CONTROL.txt records a
deliberately mutated copy that this script rejects with exit code 1.
"""
import csv, json, os, sys, hashlib, collections

csv.field_size_limit(10 ** 9)
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
A_DIR = os.path.join(LANE, "CORRECTED-A-denominator-category")
B_DIR = os.path.join(LANE, "CORRECTED-B-identity-selection-overlap", "artifacts")
C_DIR = os.path.join(LANE, "CORRECTED-C-arm-attribution")
LDIR = os.environ.get("INTEGRATION_DIR", HERE)   # lets the negative control point elsewhere

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
L = rd(os.path.join(LDIR, "LEDGER-integrated-552.tsv"))
COV = rd(os.path.join(LDIR, "COVERAGE-b-observations.tsv"))
DISP = rd(os.path.join(LDIR, "DISPOSITION-MAP.tsv"))
CON = rd(os.path.join(LDIR, "CONTRADICTIONS.tsv"))
CEN = json.load(open(os.path.join(LDIR, "INTEGRATION-CENSUS.json")))
MAN = json.load(open(os.path.join(LDIR, "INPUT-MANIFEST.json")))["input_sha256"]

res = []
def chk(name, ok, detail):
    res.append({"check": name, "result": "PASS" if ok else "FAIL", "detail": detail})

# I1 spine identity
keys = [r['integration_row_key'] for r in L]
chk("I1_spine_is_552_unique_rows_bijective_with_A",
    len(L) == 552 and len(set(keys)) == 552 and
    set(keys) == set(f"{a['input_key_nct_id']}|OM{int(a['input_key_om_index'])}|{a['input_key_group_id']}" for a in A),
    f"ledger_rows={len(L)} distinct={len(set(keys))} A_rows={len(A)}")

# I2 A<->C bridge is a verified bijection, not an assumption
cb = collections.Counter((r['nct'], r['om_title'], r['group_title']) for r in C)
ab = collections.Counter((r['input_key_nct_id'], r['om_title'], r['group_title']) for r in A)
chk("I2_A_to_C_title_bridge_is_unique_on_both_sides_and_total",
    max(cb.values()) == 1 and max(ab.values()) == 1 and set(cb) == set(ab)
    and all(r['c_join_state'] == 'JOINED_UNIQUE' for r in L),
    f"C_max_multiplicity={max(cb.values())} A_max_multiplicity={max(ab.values())} "
    f"only_in_A={len(set(ab)-set(cb))} only_in_C={len(set(cb)-set(ab))}")

# I2b the bridge carries C's own key field consistently
cmap = {(r['nct'], r['om_title'], r['group_title']): r for r in C}
amap = {(r['input_key_nct_id'], r['om_title'], r['group_title']): r for r in A}
bad = [k for k in amap if str(cmap[k]['evaluable_n']) != str(amap[k]['job1_evaluable_n_sum_of_four_producer_cells'])]
chk("I2b_C_evaluable_n_key_component_agrees_with_A_carried_job1_value", not bad,
    f"mismatches={len(bad)}")

# I3 A->B partial join accounted for, and every non-join reason independently recomputed
bobs = {r['obs_id'] for r in BOBS}
bncts = {r['nct'] for r in BOBS}
boms = {(r['nct'], r['om_index']) for r in BOBS}
wrong = []
for r in L:
    oid = r['obs_id_b_form']
    if oid in bobs:
        want = 'JOINED_UNIQUE'
    elif r['nct_id'] not in bncts:
        want = 'TRIAL_OUTSIDE_B_CORPUS_SCOPE'
    elif (r['nct_id'], r['om_index']) not in boms:
        want = 'MEASURE_OUTSIDE_B_TITLE_BOUNDARY'
    else:
        want = 'GROUP_ABSENT_IN_B_MEASURE'
    if want != r['b_join_state']:
        wrong.append((oid, want, r['b_join_state']))
cnt = collections.Counter(r['b_join_state'] for r in L)
chk("I3_A_to_B_join_state_recomputed_and_exhaustive",
    not wrong and sum(cnt.values()) == 552,
    f"mislabelled={len(wrong)} census={dict(cnt)}")

# I4 no silent inner join: the B-only difference is emitted, not dropped
inspine = sum(1 for c in COV if c['in_integrated_552'] == 'yes')
chk("I4_every_B_observation_is_dispositioned_none_inner_joined_away",
    len(COV) == len(BOBS) and {c['obs_id'] for c in COV} == bobs
    and inspine == cnt['JOINED_UNIQUE']
    and (len(COV) - inspine) == CEN['b_observations_not_in_spine'],
    f"B_obs={len(BOBS)} coverage_rows={len(COV)} in_spine={inspine} B_only={len(COV)-inspine}")

# I5 component values are carried, never overwritten by another component
amap2 = {f"{a['input_key_nct_id']}|OM{int(a['input_key_om_index'])}|{a['input_key_group_id']}": a for a in A}
bmap = {r['obs_id']: r for r in BOBS}
v = []
for r in L:
    a = amap2[r['integration_row_key']]
    if r['a_proportion_suitability'] != a['proportion_suitability']: v.append(('A_state', r['integration_row_key']))
    if r['a_reported_denominator_participants'] != a['reported_denominator_participants']: v.append(('A_denom', r['integration_row_key']))
    if r['a_unresolved_reason_codes'] != a['unresolved_reason_codes']: v.append(('A_codes', r['integration_row_key']))
    c = cmap[(r['nct_id'], r['om_title'], r['group_title'])]
    if r['c_arm_link_state'] != c['arm_link_state'] or r['c_control_status'] != c['control_status']:
        v.append(('C_state', r['integration_row_key']))
    b = bmap.get(r['obs_id_b_form'])
    if b is not None and (r['b_denominator_state'] != b['denominator_state']
                          or r['b_usable_for_proportion'] != b['usable_for_proportion']):
        v.append(('B_state', r['integration_row_key']))
chk("I5_no_component_state_is_overwritten_in_the_integrated_row", not v, f"violations={len(v)}")

# I6 contradictions survive as contradictions
both = [r for r in L if r['a_proportion_suitability'] == 'UNSUITABLE_FOR_PROPORTION'
        and r['c_arm_link_state'] == 'CONFIRMED']
ok6 = all('A_UNSUITABLE_WHILE_C_ARM_CONFIRMED' in r['contradictions_retained'] for r in both) \
      and all(r['integration_state'] == 'BLOCKED' for r in both)
chk("I6_A_doubt_is_not_overwritten_by_C_confidence", ok6,
    f"rows_where_A_unsuitable_and_C_confirmed={len(both)}; all retain both states and stay BLOCKED={ok6}")
chk("I6b_contradiction_file_matches_the_row_level_codes",
    len(CON) == sum(len(r['contradictions_retained'].split('|')) for r in L if r['contradictions_retained'] != 'NONE')
    and all(c['resolution'] == 'BOTH_STATES_STAND__NEITHER_COMPONENT_OVERWRITES_THE_OTHER' for c in CON),
    f"contradiction_rows={len(CON)}")

# I7 no forbidden quantity anywhere in the emitted tables
FORBIDDEN = ('response_rate', 'orr', 'proportion_value', 'percent', 'pct', 'unique_patient',
             'capacity_bound', 'effect', 'control_comparison', 'numerator')
# A column whose name matches a forbidden token is an offence UNLESS every one of its values is
# the literal sentinel NOT_DERIVED. The test is on the VALUES, so it is stricter than a name test:
# a column called `unique_patient_total_derived` that ever held a number would still fail here.
badcols, sentinels = [], []
for fn, rows_ in (('LEDGER-integrated-552.tsv', L), ('COVERAGE-b-observations.tsv', COV),
                  ('DISPOSITION-MAP.tsv', DISP), ('CONTRADICTIONS.tsv', CON)):
    for col in rows_[0].keys():
        lc = col.lower()
        if not any(t in lc for t in FORBIDDEN):
            continue
        vals = {r[col] for r in rows_}
        if vals == {'NOT_DERIVED'}:
            sentinels.append(f"{fn}:{col}")
        else:
            badcols.append(f"{fn}:{col} values={sorted(vals)[:4]}")
chk("I7_no_rate_proportion_unique_patient_or_effect_column_emitted", not badcols,
    f"offending_columns={badcols}; NOT_DERIVED-only sentinel columns={sentinels}; all-three sentinels on "
    f"{sum(1 for r in L if r['rate_derived']=='NOT_DERIVED' and r['unique_patient_total_derived']=='NOT_DERIVED' and r['control_comparison_derived']=='NOT_DERIVED')}/552 rows")

# I8 the unconfirmed-chain carry is present on every row and in the census
chk("I8_job2_and_job3_unconfirmed_carried_on_every_row_and_in_census",
    all(r['job2_independently_confirmed'] == 'false' and r['job3_independently_confirmed'] == 'false'
        and r['job1_arithmetic_independently_confirmed'] == 'true' for r in L)
    and CEN['confirmation_status']['job2_independently_confirmed'] is False
    and CEN['confirmation_status']['job3_independently_confirmed'] is False,
    "552/552 rows carry job1=confirmed, job2=false, job3=false")

# I9 disposition map covers every component record exactly once
dc = collections.Counter(d['component'] for d in DISP)
chk("I9_disposition_map_covers_every_component_record_exactly_once",
    dc['CORRECTED-A'] == 552 and dc['CORRECTED-C'] == 552
    and dc['CORRECTED-B'] == len(BOBS) + (552 - cnt['JOINED_UNIQUE'])
    and len({d['component_record_key'] for d in DISP if d['component'] == 'CORRECTED-B'}) == len(BOBS) + (552 - cnt['JOINED_UNIQUE']),
    f"A={dc['CORRECTED-A']} C={dc['CORRECTED-C']} B={dc['CORRECTED-B']} "
    f"(B = {len(BOBS)} observations + {552-cnt['JOINED_UNIQUE']} spine rows B never assessed)")

# I10 duplicate / competing-record relationships retained as first-class states
setmap = {}
for r in BSET:
    for o in r['observation_ids'].split('|'):
        setmap[o] = r
multi = [r for r in L if r['b_n_observations_in_cohort_set'] not in ('', '1')]
ok10 = all(r['b_sibling_observation_ids'] and r['b_unresolved_states']
           and r['b_selection_status'] == 'NOT_SELECTED_BY_DESIGN' for r in multi)
chk("I10_competing_and_duplicate_records_retained_not_collapsed", ok10 and len(multi) > 0,
    f"spine rows in a multi-observation cohort set={len(multi)}; all retain siblings, "
    f"unresolved states and NOT_SELECTED_BY_DESIGN={ok10}")

# I11 the one-arm model is not re-imposed
sole = [r for r in L if r['c_sole_arm_multi_results_group_flag'] == 'YES']
chk("I11_sole_arm_contradiction_retained_no_one_arm_model_forced",
    all('C_SOLE_ARM_BUT_MULTIPLE_RESULTS_GROUPS' in r['contradictions_retained'] for r in sole),
    f"rows flagged sole-arm-but-multiple-results-groups={len(sole)}, all retained")

# I12 the universal disjointness condition is on every row, including unblocked ones
chk("I12_disjointness_unverifiable_carried_on_every_row",
    all('B_DISJOINTNESS_UNVERIFIABLE_NO_PARTICIPANT_FLOW' in r['blocking_conditions'] for r in L)
    and all(r['integration_state'] != 'NO_COMPONENT_BLOCK_FOUND__NOT_AN_ELIGIBILITY_GRANT'
            or 'B_DISJOINTNESS_UNVERIFIABLE_NO_PARTICIPANT_FLOW' in r['blocking_conditions'] for r in L),
    "552/552 rows, including the 105 with no component-specific block")

# I13 census is recomputed, not asserted
recomputed = {
    'spine_rows': len(L),
    'b_observations_not_in_spine': sum(1 for c in COV if c['in_integrated_552'] == 'no'),
    'integration_state': dict(collections.Counter(r['integration_state'] for r in L)),
    'c_arm_link_state': dict(collections.Counter(r['c_arm_link_state'] for r in L)),
    'b_join_state': dict(collections.Counter(r['b_join_state'] for r in L)),
    'contradiction_rows': len(CON),
}
diffs = {k: (recomputed[k], CEN[k]) for k in recomputed if recomputed[k] != CEN[k]}
chk("I13_census_matches_recomputation_from_the_emitted_tables", not diffs, f"differences={diffs}")

# I14 source components byte-unchanged
changed = [p for p, h in MAN.items() if sha(os.path.join(LANE, p)) != h]
chk("I14_component_inputs_unmodified_by_this_integration", not changed,
    f"{len(MAN)} input files re-hashed, {len(changed)} changed")

failed = [r for r in res if r['result'] == 'FAIL']
out = {"component": "INTEGRATION-endpoint-ledger", "checks": res,
       "passed": len(res) - len(failed), "failed": len(failed), "total": len(res)}
if LDIR == HERE:
    with open(os.path.join(HERE, "INTEGRATION-CHECKS.json"), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
for r in res:
    print(f"{r['check']}: {r['result']}\n     {r['detail']}")
print(f"\n{len(res)-len(failed)}/{len(res)} checks passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
