#!/usr/bin/env python3
"""Negative control: build a DELIBERATELY DEFECTIVE copy of the INTEGRATION3 outputs and run the
real checks over it. The checks must reject it with exit 1.

Nothing outside NEG-CONTROL/ is written. The real outputs are copied, then mutated in the copy.

Nine planted defects. D1-D6 are v2's, carried forward. D7-D9 are new and target exactly the three
things this propagation claims:

  D1 A's doubt overwritten by C's confidence on one row       -> J5, J6
  D2 the 15,658 B-only observations inner-joined away         -> J3b, J4, J15
  D3 one LABEL_MATCH arm link promoted to SOURCE_FIELD_MATCH  -> J5
  D4 the two unknowns merged: within-record reporting barred
     by the absent participantFlowModule                      -> J13
  D5 a demoted tension re-promoted into the genuine register  -> J14, J14b, K19
  D6 B2's unresolved semantics strengthened to a
     not-a-duplicate claim                                    -> J11
  D7 the retired C2 v2 token SOURCE_CONFIRMED restored on an
     arm link -- i.e. the propagation not done                -> J12
  D8 a contested flag silently DROPPED while being demoted --
     i.e. demotion used to lose evidence                      -> J14c, K19, K20
  D9 one row left unblocked on arm attribution -- i.e. the v3
     count complement not propagated                          -> K21
"""
import csv, json, os, shutil

csv.field_size_limit(10 ** 9)
HERE = os.path.dirname(os.path.abspath(__file__))
NC = os.path.join(HERE, 'NEG-CONTROL')
os.makedirs(NC, exist_ok=True)

FILES = ['LEDGER3-integrated-552.tsv', 'COVERAGE3-b-observations.tsv', 'DISPOSITION-MAP3.tsv',
         'CROSS-COMPONENT-STATUS3.tsv', 'CONTRADICTIONS-genuine3.tsv',
         'UNRESOLVED-TENSIONS3.tsv',
         'INTEGRATION3-CENSUS.json', 'INPUT-MANIFEST3.json']
for f in FILES:
    shutil.copy2(os.path.join(HERE, f), os.path.join(NC, f))


def rd(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def wr(p, rows, cols=None):
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, cols or list(rows[0].keys()), delimiter='\t')
        w.writeheader(); w.writerows(rows)


L = rd(os.path.join(NC, 'LEDGER3-integrated-552.tsv'))
planted = []
done = set()

# D1 + D3 + D6 + D7 + D9, each on the first eligible row
for r in L:
    if 'D1' not in done and r['a_proportion_suitability'] == 'UNSUITABLE_FOR_PROPORTION' and \
       r['c_arm_link_state'] == 'SOURCE_FIELD_MATCH':
        r['a_proportion_suitability'] = 'NOT_REFUTED_BY_THIS_COMPONENT'
        r['integration_state'] = 'NO_COMPONENT_BLOCK_FOUND__NOT_AN_ELIGIBILITY_GRANT'
        done.add('D1'); planted.append('D1:' + r['integration_row_key'])
    if 'D3' not in done and r['c_arm_link_state'] == 'LABEL_MATCH':
        r['c_arm_link_state'] = 'SOURCE_FIELD_MATCH'
        done.add('D3'); planted.append('D3:' + r['integration_row_key'])
    elif 'D7' not in done and r['c_arm_link_state'] == 'LABEL_MATCH':
        r['c_arm_link_state'] = 'SOURCE_CONFIRMED'   # retired v2 vocabulary restored
        done.add('D7'); planted.append('D7:' + r['integration_row_key'])
    if 'D6' not in done and \
       r['b_semantic_duplication_status'] == 'UNRESOLVED__SEMANTIC_CORRESPONDENCE_NOT_ESTABLISHED':
        r['b_semantic_duplication_status'] = 'NOT_A_DUPLICATE'
        done.add('D6'); planted.append('D6:' + r['integration_row_key'])
    if 'D9' not in done:
        r['blocking_conditions'] = '|'.join(
            t for t in r['blocking_conditions'].split('|')
            if not t.startswith('AXIS_ARM_ATTRIBUTION:'))
        done.add('D9'); planted.append('D9:' + r['integration_row_key'])

# D8 a contested flag dropped while demoting: blank it on the ledger row AND drop its entry
d8_key = None
for r in L:
    if r['c_contested_flags'].strip():
        d8_key = r['integration_row_key']; r['c_contested_flags'] = ''
        planted.append('D8:' + d8_key); break

# D4 the two unknowns merged, on every row
for r in L:
    r['within_record_reporting_state'] = 'UNCOMPUTABLE_NO_PARTICIPANT_FLOW_MODULE'
    r['within_record_reporting_barred_by_absent_participant_flow'] = 'YES'
planted.append('D4:all 552 rows')
wr(os.path.join(NC, 'LEDGER3-integrated-552.tsv'), L)

# D2 inner-join the B-only observations away
COV = [c for c in rd(os.path.join(NC, 'COVERAGE3-b-observations.tsv'))
       if c['in_integrated_552'] == 'yes']
wr(os.path.join(NC, 'COVERAGE3-b-observations.tsv'), COV)
planted.append('D2:%d B-only observations dropped' % (16116 - len(COV)))

# D5 re-promote a demoted tension into the genuine register; D8 drop the contested tension entries
TN = rd(os.path.join(NC, 'UNRESOLVED-TENSIONS3.tsv'))
TN_COLS = list(TN[0].keys())
promoted = next(t for t in TN if t['tension_kind'] == 'MAPPING')
TN = [t for t in TN if not (t['integration_row_key'] == d8_key and t['tension_kind'] == 'EVIDENCE')]
wr(os.path.join(NC, 'UNRESOLVED-TENSIONS3.tsv'), TN, TN_COLS)

CN_COLS = ['integration_row_key', 'code', 'incompatibility', 'a_state',
           'a_reported_denominator_participants', 'b_denominator_value_participants',
           'c_arm_link_state', 'c_contested_flags', 'c_sole_arm_multi_results_group_flag',
           'resolution', 'source_pointer']
CN = rd(os.path.join(NC, 'CONTRADICTIONS-genuine3.tsv'))
CN.append({k: '' for k in CN_COLS})
CN[-1]['integration_row_key'] = promoted['integration_row_key']
CN[-1]['code'] = 'SOURCE_INTERNAL_CONTRADICTION:SOLE_REGISTERED_ARM_VS_MULTIPLE_RESULTS_GROUPS'
CN[-1]['resolution'] = 'RETAINED_UNRESOLVED__NO_FIELD_IS_DECLARED_WRONG'
wr(os.path.join(NC, 'CONTRADICTIONS-genuine3.tsv'), CN, CN_COLS)
planted.append('D5:' + promoted['integration_row_key'])

with open(os.path.join(NC, 'PLANTED-DEFECTS.json'), 'w', encoding='utf-8') as f:
    json.dump({'planted': sorted(planted),
               'expected': 'check_integration3.py --dir NEG-CONTROL must exit 1'}, f, indent=1)
print(json.dumps(sorted(planted), indent=1))
