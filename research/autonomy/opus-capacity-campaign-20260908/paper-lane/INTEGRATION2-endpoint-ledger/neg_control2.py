#!/usr/bin/env python3
"""Negative control: build a DELIBERATELY DEFECTIVE copy of the INTEGRATION2 outputs and run the
real checks over it. The checks must reject it with exit 1.

Nothing outside NEG-CONTROL/ is written. The real outputs are copied, then mutated in the copy.

Six planted defects, one per property the integration claims:
  D1 A's doubt overwritten by C's confidence on one row      -> J5, J6
  D2 the 15,658 B-only observations inner-joined away        -> J3b, J4, J15
  D3 one LABEL_MATCH arm link promoted to SOURCE_CONFIRMED   -> J5
  D4 the two unknowns merged: within-record reporting barred
     by the absent participantFlowModule                     -> J13
  D5 a compatible cross-component status moved into the
     genuine-contradiction register                          -> J14b
  D6 B2's unresolved semantics strengthened to a
     not-a-duplicate claim                                   -> J11
"""
import csv, json, os, shutil

csv.field_size_limit(10 ** 9)
HERE = os.path.dirname(os.path.abspath(__file__))
NC = os.path.join(HERE, 'NEG-CONTROL')
os.makedirs(NC, exist_ok=True)

FILES = ['LEDGER2-integrated-552.tsv', 'COVERAGE2-b-observations.tsv', 'DISPOSITION-MAP2.tsv',
         'CROSS-COMPONENT-STATUS.tsv', 'CONTRADICTIONS-genuine.tsv',
         'INTEGRATION2-CENSUS.json', 'INPUT-MANIFEST2.json']
for f in FILES:
    shutil.copy2(os.path.join(HERE, f), os.path.join(NC, f))


def rd(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def wr(p, rows):
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, list(rows[0].keys()), delimiter='\t')
        w.writeheader(); w.writerows(rows)


L = rd(os.path.join(NC, 'LEDGER2-integrated-552.tsv'))
planted = []

# D1 + D3 + D4 + D6
for r in L:
    if not any(p.startswith('D1') for p in planted) and \
       r['a_proportion_suitability'] == 'UNSUITABLE_FOR_PROPORTION' and \
       r['c_arm_link_state'] == 'SOURCE_CONFIRMED':
        r['a_proportion_suitability'] = 'NOT_REFUTED_BY_THIS_COMPONENT'
        r['integration_state'] = 'NO_COMPONENT_BLOCK_FOUND__NOT_AN_ELIGIBILITY_GRANT'
        planted.append('D1:' + r['integration_row_key'])
    if not any(p.startswith('D3') for p in planted) and r['c_arm_link_state'] == 'LABEL_MATCH':
        r['c_arm_link_state'] = 'SOURCE_CONFIRMED'
        planted.append('D3:' + r['integration_row_key'])
    if not any(p.startswith('D6') for p in planted) and \
       r['b_semantic_duplication_status'] == 'UNRESOLVED__SEMANTIC_CORRESPONDENCE_NOT_ESTABLISHED':
        r['b_semantic_duplication_status'] = 'NOT_A_DUPLICATE'
        planted.append('D6:' + r['integration_row_key'])
for r in L:
    r['within_record_reporting_state'] = 'UNCOMPUTABLE_NO_PARTICIPANT_FLOW_MODULE'
    r['within_record_reporting_barred_by_absent_participant_flow'] = 'YES'
planted.append('D4:all 552 rows')
wr(os.path.join(NC, 'LEDGER2-integrated-552.tsv'), L)

# D2 inner-join the B-only observations away
COV = [c for c in rd(os.path.join(NC, 'COVERAGE2-b-observations.tsv'))
       if c['in_integrated_552'] == 'yes']
wr(os.path.join(NC, 'COVERAGE2-b-observations.tsv'), COV)
planted.append('D2:%d B-only observations dropped' % (16116 - len(COV)))

# D5 move one compatible cross-component status into the genuine-contradiction register
XS = rd(os.path.join(NC, 'CROSS-COMPONENT-STATUS.tsv'))
CN = rd(os.path.join(NC, 'CONTRADICTIONS-genuine.tsv'))
moved = next(x for x in XS if x['code'].startswith('CROSS_COMPONENT_STATUS:'))
CN.append({k: (moved.get(k, '') if k != 'code' else
               'CROSS_COMPONENT_CONTRADICTION:A_NOT_REFUTED_WHILE_C_ARM_WEAK')
           for k in CN[0].keys()})
CN[-1]['integration_row_key'] = moved['integration_row_key']
wr(os.path.join(NC, 'CONTRADICTIONS-genuine.tsv'), CN)
planted.append('D5:' + moved['integration_row_key'])

with open(os.path.join(NC, 'PLANTED-DEFECTS.json'), 'w', encoding='utf-8') as f:
    json.dump({'planted': planted,
               'expected': 'check_integration2.py --dir NEG-CONTROL must exit 1'}, f, indent=1)
print(json.dumps(planted, indent=1))
