#!/usr/bin/env python3
"""Independent source-only GSE9309 identity/method replay; no expression rows."""
import collections
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
PEER = Path('/workspace/emc-r6-single_cell/research/autonomy/fresh-discovery-2026-10-05-round9/rna_processing/gse9309_eligibility_followthrough')
SOURCES = {
    'GSM_metadata': (PEER/'raw/GSE9309-brief-family-metadata.txt', '9edff29cfd886be003931cd151df9424f095e5f5c6192bb4e25b760ab2755a87'),
    'primary': (PEER/'raw/PMC3597597.xml', '7efd9095f45bd24d1ad611c098143e2d41ecf7785eaaa9b2df7f32fe31805208'),
    'owner_roster': (PEER/'GSE9309-SOURCE-IDENTITY-CONDITION-ROSTER.json', '0bce434b7d80a250d4d1ebf99fd858add8e4b34a65516f3316de9c345446bf5f'),
    'owner_plan': (PEER/'PLAN.json', '5cf85ce7346d0828d8d0b956532ab2aa0240595bf756c8e2c0a70f5f84862a7d'),
}
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def text(e):
    return ' '.join(' '.join(e.itertext()).split())

bindings = []
for name, (p, expected) in SOURCES.items():
    actual = sha(p)
    if expected is not None:
        assert actual == expected, (name, actual, expected)
    bindings.append({'name': name, 'path': str(p), 'bytes': p.stat().st_size, 'sha256': actual,
                     'cache_only': name in {'GSM_metadata', 'primary'},
                     'scope': 'Selected source identity, condition, comparator and method fields only'})
raw = {}
current = None
for line in SOURCES['GSM_metadata'][0].read_text().splitlines():
    if line.startswith('^SAMPLE = '):
        current = line.split(' = ', 1)[1]
        raw[current] = {}
    elif current and line.startswith('!Sample_') and ' = ' in line:
        key, value = line.split(' = ', 1)
        raw[current].setdefault(key[len('!Sample_'):], []).append(value)
assert len(raw) == 142
owner = json.loads(SOURCES['owner_roster'][0].read_text())
assert len(owner['rows']) == 142
count = 0
compact_rows = []
for row in owner['rows']:
    original = raw[row['GSM']]
    assert 'GSE9309' in original['series_id']
    for key, values in row['fields'].items():
        selected = original[key]
        if key == 'characteristics_ch1':
            # The owner intentionally omits unrelated breast receptor covariates.
            selected = [v for v in selected if v.startswith(('gender:', 'tissue:'))]
        assert selected == values, (row['GSM'], key)
        count += 1
    assert original['platform_id'] == ['GPL887']
    assert original['source_name_ch2'] == ["Stratagene's human common reference RNA"]
    assert original['label_ch1'] == ['Cy5'] and original['label_ch2'] == ['Cy3']
    assert original['molecule_ch1'] == ['total RNA']
    assert original['growth_protocol_ch1'] == ['The fresh samples used for this study were immediately frozen by liquid nitrogen without any additional growth procedure applied before RNA extraction.']
    compact_rows.append({'GSM': row['GSM'], 'source_title': original['title'][0],
                         'source_diagnosis': original['source_name_ch1'][0],
                         'tissue_condition': [v for v in original.get('characteristics_ch1', []) if v.startswith('tissue:')],
                         'technical_buffer_or_same_tissue_description': original.get('description', []),
                         'declared_series_memberships': original.get('series_id', []),
                         'native_EMC_source_label': False,
                         'disposition': 'Source-named breast diagnosis/normal; no EMC authentication or subtype transfer'})
diagnoses = dict(collections.Counter(v for r in raw.values() for v in r['source_name_ch1']))
expected = {'Infiltrating Ductal Carcinoma (IDC)': 116, 'Infiltrating Lobular Carcinoma (ILC)': 4,
            'Mucinous Carcinoma (MC)': 2, 'Nontumor part (also called normal(N))': 9,
            'Intracystic Papillary Carcinoma (IPC)': 2, 'Metaplastic Carcinoma of Breast (MCB)': 4,
            'Phyllodes Tumor(PT)': 1, 'Atypical Medullary Carcinoma (AMC)': 2,
            'Intraductal Carcinoma (IC)': 2}
assert diagnoses == expected and sum(diagnoses.values()) == 142
tissues = dict(collections.Counter(v for r in raw.values() for v in r.get('characteristics_ch1', []) if v.startswith('tissue:')))
assert tissues == {'tissue: primary tumor': 127, 'tissue: non-tumor part of breast': 9, 'tissue: recurrent tumor': 6}
same_tissue_descriptions = sum('Same tissue as sample' in d for r in raw.values() for d in r.get('description', []))
assert same_tissue_descriptions == 36
series_memberships = dict(collections.Counter(v for r in raw.values() for v in r.get('series_id', [])))
assert series_memberships == {'GSE9309': 142, 'GSE17040': 55, 'GSE17041': 48, 'GSE32641': 22}
primary = ET.parse(SOURCES['primary'][0]).getroot()
methods = [s for s in primary.findall('.//sec') if s.find('title') is not None and text(s.find('title')) == 'Microarray expression data']
assert len(methods) == 1
paragraphs = [text(p) for p in methods[0].findall('p')]
assert len(paragraphs) == 1
method = paragraphs[0]
for value in ['GSE24124', 'GSE17040', 'GSE9309', '181 patients', '25 patients', '2002 to 2005', 'National Taiwan University Hospital']:
    assert value in method
observations = {
    'source_scope': 'Actual complete142 GSE9309 metadata plus selected accession-linked primary methods; source eligibility, not gene/clinical-outcome analysis.',
    'all142_conditions': compact_rows,
    'all_source_diagnosis_counts': diagnoses,
    'all_tissue_condition_counts': tissues,
    'array_not_patient_count': '142 is library/hybridization count.36 descriptions explicitly link the same tissue under buffer variation; exact independent patient/donor map not established here. Do not count36 as36 independent donors or infer donor pairs from numeric title suffixes.',
    'assay': {'platform': 'GPL887/Agilent Human1A(version2) source-linked primary assay',
              'specimen': 'Fresh excised breast primary/recurrent/adjacent-nontumor tissue immediately snap-frozen; no growth before extraction',
              'capture': 'TotalRNA/Trizol+RNeasy; Cy5sample relative to Cy3 Stratagene human common reference RNA, not a matched healthy donor or untreated serial control',
              'condition_semantics': 'Buffer1/Buffer2/same-tissue technical context. Collection protocol is not experimental anticancer treatment or withdrawal. No native EMC perturbation/fidelity assay authenticated.'},
    'primary_method_quote': method,
    'primary_cohort_direction': 'The2013 methods pool181tumor+25nontumor patient material across three distinct accessions. Those patient counts/any diagnoses cannot be transferred to142GSE9309 arrays without an explicit source case/accession map.',
    'explicit_source_overlap': {'declared_GSM_series_membership_counts': series_memberships,
                                'interpretation': '55exactGSM source conditions are also in the primary-cited GSE17040; source arrays cannot be added as independent cohorts. Membership in48GSE17041/22GSE32641 likewise signals public source-record reuse, not new donor identity. This is direct source-record overlap, not proof every pooled clinical patient is mapped or biological outcomes are identical.'},
    'EMC_eligibility': {'author_named_EMC_metadata_rows': 0, 'scope': 'No EMC-labelled/authenticated sample among these142source-named breast arrays. This is not molecular proof of biological absence, exclusion of every pooled-primary case or global publicEMC exhaustion.',
                        'generic_myxo_rule': 'Generic myxoid-chondrosarcoma or sarcoma labels from another primary case/source remain unresolved and cannot be transferred toMC/MCB/PT breast aliases. MC is explicitly mucinous carcinoma here; MCB is explicitly metaplastic carcinoma of breast.'},
    'pending': ['Exact independent donor map and cross-accession overlap for the pooled2013primary cohorts',
                'GSE24124/GSE17040 or other pooled source cases/diagnoses not authenticated by this142library gate',
                'Biological classification beyond author-source diagnoses not newly resolved'],
    'value': 'This source-specific negative eligibility repairs a prior pending branch. It does not discover an EMC phenotype or demonstrate culture failure; no expression data stage follows from breast technical-standardization arrays.',
    'outcomes': {'gene_expression_rows_read': False, 'new_EMC_measurements': False, 'new_original_bytes': 0},
    'source_covariate_exposure': 'Initial independent metadata-key/count inspection displayed aggregate breast receptor characteristic labels (ER/PR/HER) before filtering. No expression matrix, numeric gene effect, clinical endpoint or EMC assay outcome inspected; no fully blind metadata-source claim. These unrelated covariates did not choose the accession, question or feature.',
    'raw_to_owner_field_checks': count,
}
for filename, obj in [('ACTUAL-SOURCE-BINDINGS.json', bindings), ('INDEPENDENT-IDENTITY-ASSAY-OBSERVATIONS.json', observations)]:
    (HERE/filename).write_text(json.dumps(obj, indent=2)+'\n')
print(json.dumps({'status': 'PASS', 'source_hash_bindings': len(bindings), 'predeclared_expected_hashes_checked': 4, 'source_libraries': len(raw),
                  'raw_owner_fields_checked': count, 'same_tissue_technical_descriptions': same_tissue_descriptions,
                  'author_EMC_source_rows': 0, 'expression_or_EMC_outcomes_read': False,
                  'breast_receptor_source_covariate_exposure': True, 'new_original_bytes': 0}))
