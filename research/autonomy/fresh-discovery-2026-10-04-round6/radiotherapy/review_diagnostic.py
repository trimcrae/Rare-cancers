"""Independent source/novelty review of the frozen diagnostic packet.

Extracts original table rows from separately regenerated primary PDF text and
checks them against the owner observations. The full PDF/text remain cache-only.
No additional source acquisitions or pooled clinical estimates.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
OWNER = Path(os.environ.get('EMC_R6_DIAGNOSTIC_PACKET', '/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-04-round6/diagnostic'))
CACHE = Path(os.environ.get('EMC_R6_RT_CACHE', '/workspace/emc-r6-radiotherapy/source-cache'))

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

observations = json.loads((OWNER / 'OBSERVATIONS.json').read_text())
pdf = OWNER / 'sources/insm1_2018_primary.pdf'
assert digest(pdf) == '06db9d812ed21b6ec3b487bbac17f6fb63a424d8473e7d7aa807ba4cb28bf6d4'
text = (CACHE / 'diagnostic-review-insm1-primary.txt').read_text()
table = text.split('Table 1 INSM1 immunohistochemistry in extraskeletal myxoid chondrosarcoma and its mimics')[1].split('INSM1 positivity was defined')[0]
source_rows = []
for line in table.splitlines():
    match = re.match(r'^\s*(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\(', line)
    if match:
        label, n, a, b, c, d, positive = match.groups()
        if label.startswith('Other mesenchymal tumors'):
            assert list(map(int, (n,a,b,c,d,positive))) == [187,9,1,1,0,11]
            continue
        label = 'EMC' if label == 'Extraskeletal myxoid chondrosarcoma' else label
        if label == 'Miscellaneous tumorsa':
            label = 'Miscellaneous tumors'
        label = label.replace('Poorly-differentiated', 'Poorly differentiated')
        source_rows.append([label,int(n),list(map(int,(a,b,c,d)))])
assert len(source_rows) == 16
assert source_rows == observations['Yoshida2018']['complete_table1_rows']
assert sum(r[1] for r in source_rows[1:]) == 187
assert sum(sum(r[2]) for r in source_rows[1:]) == 11
assert sum(source_rows[0][2]) == 28 and source_rows[0][1] - sum(source_rows[0][2]) == 3

normalized = ' '.join((CACHE / 'diagnostic-review-insm1-primary-flow.txt').read_text().split())
for phrase in ['All 31 tumors were previously confirmed to harbor NR4A3 rearrangement',
               '24 tumors (77%) were positive for EWSR1 rearrangement, while 7 tumors (23%) were negative',
               'One of these resection specimens was previously decalcified by acid',
               'In another case, repeat staining on a preoperative biopsy demonstrated focal INSM1 reactivity',
               'three needle biopsy specimens, with all showing positivity for INSM1',
               'moderate or higher staining in at least 5% of tumor cells was considered positive']:
    assert phrase in normalized, phrase

abstract_path = OWNER / 'sources/insm1_mesenchymal_titleabs.json'
records = json.loads(abstract_path.read_text())['resultList']['result']
lenz = [r for r in records if r.get('id') == '36563884']
assert len(lenz) == 1
abstract = lenz[0]['abstractText']
for phrase in ['Sixteen of 17 EMC cases were stained', '13 INSM1-positive (81%) and 3 INSM1-negative tumors (19%)',
               '1+ in 7 cases (44%), 2+ in 2 cases (13%), 3+ in 2 cases (13%) and 4+ in 2 cases (13%)',
               'weak in 5 cases (31%), moderate in 2 cases (13%) and strong in 6 cases (38%)',
               'more than 25% of tumor cells was present in only 31% of cases',
               'Molecular testing was successfully performed in 12/17 cases']:
    assert phrase in abstract, phrase
assert observations['Lenz2023']['extent_bins_1plus_to4plus'] == [7,2,2,2]
assert observations['Lenz2023']['intensity_weak_moderate_strong'] == [5,2,6]
coverage = json.loads((OWNER / 'COVERAGE.json').read_text())
decision = json.loads((OWNER / 'DECISION.json').read_text())
assert decision['pending_evidence_blocks_promotion'] is True
assert any('Huang' in x['source'] for x in coverage['pending_accessible_analysis'])
assert any('Zhang' in x['source'] for x in coverage['pending_accessible_analysis'])
assert decision['decision'] == 'Shelve the standalone paper'
science_projection = {k:v for k,v in decision.items() if k not in ('independent_review','independent_review_reference')}
report = (OWNER / 'REPORT.txt').read_text()
discovery_path = OWNER / 'sources/emc_diagnostic.json'
discovery = json.loads(discovery_path.read_text())
skull_case = [r for r in discovery['resultList']['result'] if r.get('id') == '42621976'][0]
assert 'immunohistochemical and molecular characterization could not be performed' in skull_case['abstractText']

result = {
    'utc':datetime.now(timezone.utc).isoformat(),
    'reviewer':'Codex /root/radiotherapy, distinct from diagnostic owner',
    'artifact_hashes':{n:digest(OWNER / n) for n in ['REPORT.txt','OBSERVATIONS.json','COVERAGE.json','DECISION.json']},
    'primary_source_pdf_sha256':digest(pdf),
    'separately_regenerated_pdf_text_sha256':digest(CACHE / 'diagnostic-review-insm1-primary.txt'),
    'primary_abstract_cache_sha256':digest(abstract_path),
    'decision_scientific_projection_sha256':sha256(json.dumps(science_projection,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
    'operational_receipt_update':'Final DECISION changes only independent_review and independent_review_reference; all scientific decision/validity/value/reopening/gap flags preserved.',
    'source_checks':{'all16_table_rows_exact':True,'EMC31_with_bins9_2_5_12_and3_negative':True,
                     'all187_mimics_and11_positive':True,'all31_NR4A3_and24vs7_EWSR1':True,
                     'distinct_acid_decalcified_and_repeat_biopsy_cases':True,
                     'three_positive_needle_biopsies_no_new_donors':True,'Lenz16_stains_13positive_original31percent_limit':True},
    'scope':'Focused source/value review of unchanged diagnostic claim; CHRNA6 baseline audit reused, not reacquired.',
    'finding':'Original INSM1 work already reports incomplete positivity, mimic positives and distinct preanalytic/specimen discordance; Lenz already reports threshold-sensitive low broad staining. No new useful paired CHRNA6/INSM1 finding is demonstrated.',
    'small_source_wording_correction':'Repeat biopsy is reported as focal INSM1 reactivity; its individual extent/intensity and crossing the >=5% moderate/strong criterion are not quantified in that discussion. Preserve this uncertainty; do not update the sensitivity denominator.',
    'correction_status':'Owner corrected REPORT and OBSERVATIONS before this final bound receipt; quantitative results and shelving unchanged.',
    'independent_omission_screen':{'cached_source_sha256':digest(discovery_path),'cached_hits_inspected':discovery['hitCount'],
        'comparison':'Independently inspected cached87-hit INSM1 title/abstract query and190-hit EMC diagnostic query for measured-marker/identity eligibility, beyond final owner tables.',
        'additional_hit':'PMID42621976 skull-base generic myxoid chondrosarcoma: source abstract explicitly says IHC and molecular characterization could not be performed; no authentic paired-marker measurement. Not counted as EMC or confirmed non-EMC.',
        'scope_limit':'This is a bounded cached discovery/eligibility challenge, not a fresh full-corpus search or certification of all public coverage.'},
    'strongest_alternative':'Between-study aggregate differences may reflect assay dilution/intensity/extent thresholds, specimen handling and selected cohort/morphology spectrum; none is identified as a biological marker mechanism.',
    'omissions_and_limits':'Huang2023 primary tables/denominator remain pending suitable accessible analysis; Zhang generic chondrosarcoma identities, later variant series, individual paired markers and donor overlap remain unresolved. This review reuses existing omission discovery and does not certify public corpus closure.',
    'decision':'Shelve standalone diagnostic paper on present evidence; no new challenge to an important existing claim demonstrated. Suitable pending sources would block promotion.',
    'reopening':'Authenticated paired per-case marker/handling/molecular/mimic measurements with donor crosswalks supporting a distinct unanswered useful comparison.',
    'computational_status':'All stated source/arithmetic/coverage assertions passed; no pooled sensitivity, efficacy claim or external action.'
}
(HERE / 'DIAGNOSTIC-INDEPENDENT-CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print('Independent original table and Lenz source checks passed; shelving supported.')
