"""Complete released-row suitability audit, not a clinical effect estimator.

Uses existing openpyxl for primary XLSX supplements; all other code is stdlib.
Raw originals are cache-only. No curve digitization or synthetic patient records.
"""
from datetime import datetime, timezone
from hashlib import sha256
import csv
import io
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import openpyxl

PACKET = Path(__file__).resolve().parent
CACHE = Path(os.environ.get('EMC_R6_RT_CACHE', '/workspace/emc-r6-radiotherapy/source-cache'))
REPO = Path(os.environ.get('EMC_R6_RT_PRIOR_REPO', '/workspace/Rare-cancers'))

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def flat(el):
    return ' '.join(' '.join(el.itertext()).split())

def source_result():
    raw = CACHE / 'PMC8891938.xml'
    root = ET.fromstring(raw.read_bytes())
    table = [t for t in root.findall('.//table-wrap') if 'Study characteristics' in flat(t)][0]
    headers = ['case','age_years','sex','region','size_cm_printed','grade','AJCC','rearrangement_printed','surgery_printed',
               'neoadjuvant_RT_printed','adjuvant_RT_printed','neoadjuvant_CT_printed','adjuvant_CT_printed',
               'local_recurrence_printed','metastasis_printed','concurrent_malignancy_printed','followup_months_printed','status_printed']
    rows = []
    for tr in table.findall('.//tbody/tr'):
        cells = [flat(x) for x in tr if x.tag in ('td','th')]
        assert len(cells) == len(headers), 'Changing primary table shape requires inspection'
        row = dict(zip(headers, cells))
        reasons = []
        if row['surgery_printed'] != 'Y':
            reasons.append('no surgical resection')
        if 'c' in row['metastasis_printed']:
            reasons.append('metastatic at presentation')
        if 'c' in row['local_recurrence_printed']:
            reasons.append('locally recurrent at presentation')
        row['eligible_primary_localized_surgery'] = not reasons
        row['exclusion_reason'] = '; '.join(reasons)
        row['primary_RT_from_table'] = ('Y' in row['neoadjuvant_RT_printed'] or
                                       ('Y' in row['adjuvant_RT_printed'] and 'b' not in row['adjuvant_RT_printed']))
        row['margin_evidence'] = 'individual linkage unresolved: narrative12 negative-margin operations versus Table2 13 surgery-Y rows' if row['surgery_printed'] == 'Y' else 'table surgery-N'
        rows.append(row)
    assert len(rows) == 15 and len({r['case'] for r in rows}) == 15
    out = PACKET / 'fice2022-all15-patient-measurements.tsv'
    with out.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t')
        writer.writeheader(); writer.writerows(rows)
    eligible = [r for r in rows if r['eligible_primary_localized_surgery']]
    summary = {}
    for flag in [True, False]:
        group = [r for r in eligible if r['primary_RT_from_table'] == flag]
        summary['RT' if flag else 'no_RT'] = {
            'cases':[r['case'] for r in group],
            'n':len(group),
            'printed_subsequent_local_recurrence_cases':[r['case'] for r in group if r['local_recurrence_printed'] == 'Y'],
            'printed_no_local_recurrence_cases':[r['case'] for r in group if r['local_recurrence_printed'] == 'N'],
            'unknown_local_recurrence_cases':[r['case'] for r in group if r['local_recurrence_printed'] not in ('N','Y')],
            'followup_range_months':[min(float(r['followup_months_printed']) for r in group), max(float(r['followup_months_printed']) for r in group)],
        }
    paragraphs = [flat(x) for x in root.findall('.//body//p')]
    source_quotes = [x for x in paragraphs if 'Time to original local recurrence was 11 years' in x]
    assert len(source_quotes) == 1
    result = {'source':'Fice2022 DOI10.1177/20363613221079754 PMC8891938', 'source_sha256':digest(raw),
              'all_rows_evaluated':15, 'table_surgery_Y_rows':sum(r['surgery_printed'] == 'Y' for r in rows),
              'table_surgery_N_rows':sum(r['surgery_printed'] == 'N' for r in rows),
              'narrative_surgery_counts':{'operated':12,'not_operated':3,'margin_linkage':'unresolved versus table13/2; no individually assigned negative margins'},
              'eligible_rows':len(eligible), 'excluded':{r['case']:r['exclusion_reason'] for r in rows if not r['eligible_primary_localized_surgery']},
              'groups':summary, 'narrative_quote':source_quotes[0],
              'interpretation':'Table2 case10 has no RT and subsequent local recurrence; source narrative places the sole subsequent recurrence in RT group. Case11 outcome blank. Individual first-event times/treatment dates and narrative-table crosswalk unresolved. No KM, effect estimate or efficacy inference justified.'}
    return result

def supplement_result():
    raw = CACHE / 'spalek-supplementary.zip'
    result = {'source':'Spalek2022 DOI10.1177/17588359211070646 PMC8848098', 'raw_zip_sha256':digest(raw),
              'main_table_EMC_patient_count':2, 'sheets':[], 'EMC_named_rows':[], 'local_failure_roster':[]}
    with zipfile.ZipFile(raw) as archive:
        for name in archive.namelist():
            if not name.endswith('.xlsx'):
                continue
            content = archive.read(name)
            book = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
            for sheet in book:
                rows = list(sheet.iter_rows(values_only=True))
                result['sheets'].append({'file':name,'sha256':sha256(content).hexdigest(),'sheet':sheet.title,'rows':len(rows),'title':str(rows[0][0])})
                for i, row in enumerate(rows, start=1):
                    if any('myxoid chondrosarcoma' in str(x).lower() or 'extraskeletal' in str(x).lower() for x in row):
                        result['EMC_named_rows'].append({'file':name,'sheet':sheet.title,'row':i,'values':list(row)})
                if 'sj-xlsx-11-' in name:
                    for row in rows[2:]:
                        if isinstance(row[0], (int,float)):
                            result['local_failure_roster'].append({'published_number':row[0],'histology':row[1],'indication':row[2], 'site':row[3], 'best_response':row[15]})
    result['interpretation'] = 'MainTable1 authenticates two EMC donors. All supplied XLSX sheets were evaluated; TableS3 exposes local-progressing SRT records, with no EMC-labelled failure. Supplements do not release the two EMC patient/lesion/treatment/follow-up crosswalks. Absence from failure roster cannot estimate EMC control duration or efficacy; all repeated lesions remain donor-dependent.'
    return result

def palliative_result():
    raw = CACHE / 'PMC2834957.xml'
    root = ET.fromstring(raw.read_bytes())
    selected = None
    headers = None
    row_count = 0
    for tr in root.findall('.//table-wrap//tr'):
        cells = [flat(x) for x in tr if x.tag in ('td','th')]
        if cells and cells[0] == 'Pt':
            headers = cells
        if cells and cells[0].isdigit():
            row_count += 1
        if cells and cells[0] == '4':
            selected = cells
    assert row_count == 17 and len(headers) == len(selected) == 9
    row = dict(zip(headers, selected))
    assert row['Pathology'] == 'Myxoid Chondrosarcoma' and row['TTLP'] == '266' and row['TTDP'] == ''
    return {'source':'Palliative RT2010 PMC2834957', 'source_sha256':digest(raw),'all_table_rows_inspected':row_count,
            'eligible_generic_histology_row':row,'time_units':'days','interpretation':'Generic histology identity unresolved;266 is local-progression time and distant-progression cell is blank. Advanced palliative context, no primary surgical-margin comparator.'}

if __name__ == '__main__':
    result = {'utc':datetime.now(timezone.utc).isoformat(),'analysis_scope':'descriptive complete-row measurement gate, not a treatment effect analysis',
              'fice2022':source_result(),'spalek2022':supplement_result(),'palliative2010':palliative_result(),'dependency_openpyxl_version':openpyxl.__version__}
    (PACKET / 'measurement-gate-results.json').write_text(json.dumps(result, indent=2) + '\n')
    print('All15 Fice rows evaluated;',result['fice2022']['eligible_rows'],'eligible; Spalek local-failure roster rows',len(result['spalek2022']['local_failure_roster']))
