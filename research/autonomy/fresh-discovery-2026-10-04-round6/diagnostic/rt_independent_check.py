#!/usr/bin/env python3
"""Independent read-only check of complete Fice source table and Bishop prior art."""
import csv
import hashlib
import json
import pathlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
OWNER = pathlib.Path('/workspace/emc-r6-radiotherapy')
PACKET = OWNER / 'research/autonomy/fresh-discovery-2026-10-04-round6/radiotherapy'
RAW = OWNER / 'source-cache'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def norm(el):
    return ' '.join(''.join(el.itertext()).split())

source = RAW / 'PMC8891938.xml'
root = ET.fromstring(source.read_bytes())
tables = [t for t in root.findall('.//table-wrap') if t.findtext('label') == 'Table 2.']
if not tables:
    tables = [t for t in root.findall('.//table-wrap') if 'Study characteristics' in norm(t)]
assert len(tables) == 1
table = tables[0]
source_headers = [norm(x) for x in table.findall('.//thead/tr')[0]]
rows = []
for tr in table.findall('.//tbody/tr'):
    values = [norm(x) for x in tr]
    assert len(values) == len(source_headers) == 18
    rows.append(dict(zip(source_headers, values)))
assert len(rows) == 15
bycase = {int(r['Case']):r for r in rows}
assert sorted(bycase) == list(range(1,16))
released = list(csv.DictReader((PACKET/'fice2022-all15-patient-measurements.tsv').open(), delimiter='\t'))
assert len(released) == 15
# Independently compare every original printed field by its source header and
# exported position. No owner extraction helper or modified source is used.
for output, original in zip(released, rows):
    assert list(output.values())[:18] == list(original.values())
for output in released:
    if output['surgery_printed'] == 'Y':
        assert 'individual linkage unresolved' in output['margin_evidence']
        assert '13 surgery-Y rows' in output['margin_evidence']
settled_owner = json.loads((PACKET/'measurement-gate-results.json').read_bytes())['fice2022']
assert settled_owner['table_surgery_Y_rows'] == 13
assert settled_owner['table_surgery_N_rows'] == 2
operated = [int(r['Case']) for r in rows if r['Surgery'] == 'Y']
notoperated = [int(r['Case']) for r in rows if r['Surgery'] == 'N']
assert len(operated) == 13 and notoperated == [3,9]
assert bycase[10]['Neoadjuvant Radiation'] == bycase[10]['Adjuvant Radiation'] == 'N'
assert bycase[10]['Local Recurrence'] == bycase[10]['Metastasis'] == 'Y'
assert bycase[11]['Local Recurrence'] == ''
eligible = [r for r in rows if r['Surgery'] == 'Y'
            and 'c' not in r['Local Recurrence'] and 'c' not in r['Metastasis']]
rt = [int(r['Case']) for r in eligible if r['Neoadjuvant Radiation'] == 'Y'
      or r['Adjuvant Radiation'] == 'Y']
no_rt = [int(r['Case']) for r in eligible if int(r['Case']) not in rt]
assert rt == [2,4,11,12,13,14] and no_rt == [1,6,10,15]
paragraphs = [norm(p) for p in root.findall('.//body//p')]
methods = [p for p in paragraphs if 'Three patients elected not to undergo surgical excision' in p]
outcome = [p for p in paragraphs if 'Time to original local recurrence was 11' in p]
assert len(methods) == len(outcome) == 1
assert 'Nine of twelve' in outcome[0]

bishop = RAW/'bishop-bioc.json'
bio = json.loads(bishop.read_bytes())
texts = []
def visit(x):
    if isinstance(x, dict):
        if isinstance(x.get('text'),str):
            texts.append(x['text'])
        for v in x.values():
            if isinstance(v,(dict,list)):visit(v)
    elif isinstance(x,list):
        for v in x:visit(v)
visit(bio)
adjusted = [t for t in texts if 'adjusting for margin status, tumor size, prior treatment' in t]
assert len(adjusted) == 1
assert '5 patients (12%) with local relapse' in adjusted[0]
assert 'HR 12.7, 95% CI 1.4' in adjusted[0]

result = {
 'utc':datetime.now(timezone.utc).isoformat(),
 'reviewer':'Independent Codex diagnostic worker /root/diagnostic, reassigned by lead; not human validation.',
 'scope':'Read-only Fice all-row extraction, contradictory treatment/event and surgery fields; Bishop adjusted association prior art. No source download or efficacy calculation.',
 'bindings':{
   'Fice_original_XML_SHA256':sha(source),
   'Fice_export_TSV_SHA256':sha(PACKET/'fice2022-all15-patient-measurements.tsv'),
   'Bishop_original_BioC_SHA256':sha(bishop),
   'owner_results_at_review_SHA256':sha(PACKET/'measurement-gate-results.json')},
 'Fice':{
   'all_printed_fields_equal_owner_export':True,'cases_checked':15,'printed_fields_per_case':18,
   'printed_surgery_Y_cases':operated,'printed_surgery_N_cases':notoperated,
   'narrative_reports_operations':12,'narrative_reports_nonoperations':3,
   'case10':'Surgery Y, preoperative RT N, adjuvant RT N, subsequent local recurrence Y, metastasis Y.',
   'case11':'Local-recurrence cell is genuinely empty; not a negative measurement.',
   'narrative_outcome':'Recurrence story is introduced as one of nine RT recipients, with four local recurrences and metastasectomy after first recurrence at 11 years.',
   'interpretation':'The treatment/event crosswalk disagrees with Table 2. The operation count is also 12 in narrative versus 13 in Table 2. Neither side is privileged as corrected truth.',
   'table_derived_primary_localized_operated_cases':{'RT':rt,'no_RT':no_rt},
   'margin_limit':'The narrative says all 12 operated patients had negative margins; it cannot be bound to every one of 13 table surgery-Y cases without resolving the discrepancy.',
   'consequence':'A complete descriptive source-suitability audit is reproducible. Individual RT efficacy, event-time, margin-adjusted or causal comparison is unsupported.'},
 'Bishop':{
   'pmid':'31436747','doi':'10.1097/COC.0000000000000590',
   'verified':'Original study reports 5 local failures; 4 after surgery alone and 1 after combined modality treatment. It already adjusted for margin, tumor size and prior treatment.',
   'HR_surgery_alone_vs_combined':12.7,'CI95':[1.4,115.3],'P':0.02,
   'consequence':'Margin adjustment alone is not new. Observational association with five events and a broad interval does not establish causation; no new effect estimate is inferred.'},
 'decision':'Agree with shelving a new RT standalone comparison from these inputs; source inconsistency is not automatically a useful disease-discovery paper.',
 'repair_verification':'Owner applied AMENDMENT-02. Settled results preserve Table 2 surgery 13/2 versus narrative 12/3; all 13 table surgery-Y rows now state individual margin linkage unresolved. Original 270 source fields and the table-derived 10-case subset are unchanged.',
 'reopening':'New accessible authenticated patient-level treatment, margin, first-event/censoring and donor crosswalks permitting a useful unanswered analysis.',
 'running_processes':[]
}
(ROOT/'RT-INDEPENDENT-CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print('Independent check passed: all 270 printed Fice fields; extra surgery-count contradiction verified; Bishop adjusted prior art verified.')
