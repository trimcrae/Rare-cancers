#!/usr/bin/env python3
"""Additive correction, using frozen metadata and one official BioSample batch.

Original results/manifest remain unchanged. No expression inference or broad
retrieval. The direct current-provider isolate linkage is distinct from invalid
cross-provider numerical patient matching.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

P = Path(__file__).parent
REF = '6bc942c888a60cf0194f8437ecd92e36f2e5568e'
REMOTE = 'research/autonomy/fresh-discovery-2026-10-04-round6/'
now = datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((P / name).read_text())


def binding(name, disposition='committed observation'):
    return {'path': name, 'bytes': (P / name).stat().st_size,
            'sha256': sha(P / name), 'disposition': disposition}


def write(name, data):
    (P / name).write_text(json.dumps(data, indent=2) + '\n')


receipt = read('BO112-RECONCILIATION-RECEIPT.json')
raw = P / receipt['cache_path']
assert sha(raw) == receipt['sha256'] and raw.stat().st_size == receipt['bytes']
xml = ET.fromstring(raw.read_bytes())
originals = {r.attrib['accession']: r for r in xml.findall('BioSample')}
assert set(originals) == set(receipt['selected_ids']) and len(originals) == 10
attributes = {a: {n.attrib['attribute_name']: ''.join(n.itertext())
                  for n in r.findall('Attributes/Attribute')}
              for a, r in originals.items()}
spatial_ids = ['SAMN53912815', 'SAMN53912816', 'SAMN53912817', 'SAMN53912818']
sc004_ids = ['SAMN53829687', 'SAMN53829688']
for accession in spatial_ids:
    a = attributes[accession]
    assert a['disease'] == 'myxofibrosarcoma'
    assert a['isolate'] == 'BO112-SARC-004' and a['biomaterial_provider'] == 'Kalbasi Lab'
    assert a['sex'] == 'female' and a['collection_date'] == '2021'
for accession in sc004_ids:
    a = attributes[accession]
    assert a['isolate'] == 'BO112-SARC-004' and a['biomaterial_provider'] == 'Kalbasi Lab'
    assert a['sex'] == 'female' and '2021' in a['collection_date']
    assert 'disease' not in a
for accession in ['SAMN53829695', 'SAMN53829696', 'SAMN53829697', 'SAMN53829698']:
    assert 'disease' not in attributes[accession]

frozen = read('BO112-COVERAGE-BY-CONDITION.json')
corrected = []
for r in frozen['rows']:
    accession = r['accession']
    bio = re.findall(r'SAMN\d+', ' '.join(r.get('relation', [])))
    title = ' '.join(r['title'])
    result = {'accession': accession, 'title': title,
              'original_status': r['status'], 'original_reason': r['reason'],
              'GSM_original_sha256': r['source_sha256'], 'biosample_accessions': bio}
    if bio and bio[0] in spatial_ids:
        assert originals[bio[0]].findtext('Description/Title') == title
        result.update({'corrected_status': 'demonstrably unsuitable measurement',
                       'basis': 'Direct exact GSM-linked official BioSample disease=myxofibrosarcoma for every spatial condition.',
                       'source_biosample': bio[0], 'donor_key': 'current Kalbasi BO112-SARC-004'})
    elif bio and bio[0] in sc004_ids:
        result.update({'corrected_status': 'demonstrably unsuitable measurement',
                       'basis': 'Current official BioSamples declare identical full study-isolate BO112-SARC-004 and biomaterial_provider Kalbasi Lab; sex/year consistent with the four explicitly MFS spatial records. This is source-defined within-provider isolate identity, not cross-provider numerical-code transfer.',
                       'source_biosample': bio[0], 'donor_key': 'current Kalbasi BO112-SARC-004',
                       'limitation': 'scRNA BioSamples omit disease. MFS disposition depends on declared current-provider full-isolate identity; it is not independent scRNA pathology/genomic confirmation.'})
    elif accession in ['GSM9376746', 'GSM9376747', 'GSM9376748', 'GSM9376749', 'GSM9376750', 'GSM9376751', 'GSM9376752', 'GSM9376753', 'GSM9376754', 'GSM9376755']:
        result.update({'corrected_status': 'pending accessible analysis',
                       'basis': 'Current source diagnosis unresolved. Do not transfer old-deposit010/011 subtype or adopt unretained RT-only primary search text.',
                       'donor_key': re.search(r'(?:SARC-(\d{3})|RT-(\d{3}))', title).group(0)})
    else:
        result.update({'corrected_status': r['status'],
                       'basis': 'Unchanged direct original GSE279852 source subtype; no transfer to any current deposit.',
                       'donor_key': 'prior deposit:' + title})
    corrected.append(result)
assert len(corrected) == 26 and len({r['accession'] for r in corrected}) == 26
pending = [r for r in corrected if r['corrected_status'] == 'pending accessible analysis']
assert len(pending) == 10 and len({r['donor_key'] for r in pending}) == 6
write('BO112-CORRECTED-CONDITION-DISPOSITIONS.json',
      {'utc': now, 'supersedes_dispositions_only': 'BO112-COVERAGE-BY-CONDITION.json; metadata and originals unchanged',
       'source_receipt': 'BO112-RECONCILIATION-RECEIPT.json', 'rows': corrected,
       'pending_libraries': 10, 'pending_named_current_donors': 6,
       'source_nonEMC_library_conditions': 16, 'authenticated_EMC_conditions': 0,
       'independence': '26libraries are not26donors. Current004 spatial/sc repeats one source-declared isolate; RT001 two fractions one surgical donor. Prior/current donor equivalence and overlap remain unresolved; no pooling.'})

remote = []
for name in ['LEAD-BO112-CROSSWALK-PLAN.json', 'LEAD-BO112-CROSSWALK.json',
             'SPATIAL-INDEPENDENT-CHALLENGE.json', 'spatial_omics/COVERAGE.txt',
             'spatial_omics/RESULTS.txt', 'spatial_omics/MANIFEST.json',
             'spatial_omics/bo112-library-identities.json', 'spatial_omics/metadata-verification.json',
             'spatial_omics/closure-receipts.json', 'spatial_omics/candidate-receipts.json']:
    data = subprocess.check_output(['git', 'show', REF + ':' + REMOTE + name])
    remote.append({'ref': REF, 'path': REMOTE + name,
                   'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                   'disposition': 'read via Git object; raw originals not copied or independently available here'})

original_names = ['REPORT.txt', 'COVERAGE.json', 'DECISION.json', 'MANIFEST.json',
                  'BO112-COVERAGE-BY-CONDITION.json', 'BO112-PUBLISHED-ROSTER-OBSERVATIONS.json',
                  'SELECTED-GEO-ACCESSION-INVENTORY.json']
amendment = {
    'utc': now, 'kind': 'Dated additive source-identity correction; frozen originals preserved',
    'owner': '/root/single_cell', 'base_frozen_commit': '76f77a63daf26764f5651f63b9af135d926c91ab',
    'trigger': 'Independent concurrent R6 source challenge exposed unsupported old/current BO-112 numerical patient-code subtype transfer. Matching424metadata records/fields/hashes did not validate donor identity inference.',
    'original_disposition_references': [binding(n, 'frozen committed record; preserve byte exact') for n in original_names],
    'original_error': 'GSE313859010/011 four library conditions were called source non-EMC by transferring GSE279852 UPS from shared numerical codes;004 current/spatial MFS initially used the same insufficient transfer. Prior BIDMC deposit and current Stanford/Kalbasi source have no authenticated cross-donor table. Original20nonEMC/6pending4donors is superseded.',
    'remote_bindings': remote,
    'corrective_plan': binding('BO112-RECONCILIATION-PLAN.json'),
    'corrective_source': binding(receipt['cache_path'], 'cache-only-not-Git; official BioSample XML10records'),
    'source_receipt': binding('BO112-RECONCILIATION-RECEIPT.json'),
    'direct_observations': binding('BO112-DIRECT-BIOSAMPLE-OBSERVATIONS.json'),
    'corrected_conditions': binding('BO112-CORRECTED-CONDITION-DISPOSITIONS.json'),
    'confirmed': 'All four current spatial004 conditions directly author-labelled myxofibrosarcoma. Two current sc004 conditions declare identical full BO112-SARC-004 isolate and Kalbasi Lab provider; source-defined isolate linkage supports MFS disposition with explicit pathology/genomic limitation.',
    'pending': 'Current010/011/012 paired6libraries plus RT001CD45neg/pos,RT002,RT0034libraries:10conditions/6namedcurrentdonors. Actual processed single-cell measurements remain potentially suitable but diagnosis authentication is unfinished.',
    'RT_limit': 'Own primaryXML route HTTP500 and BioC response ERROR; no usable original primaryXML exists. Remote RT-only UPS assertion uses unretained primary search text. New exact fourRT BioSamples say sarcoma, no disease; do not treat UPS as independently reproduced. RT remains pending.',
    'cross_series_limit': 'Prior GSE279852 direct MFS/LPS/UPS10libraries remain unchanged. No old/current donor equivalence or histology transfer for004/010/011 is inferred. Current004 linkage uses full identical source isolate/provider, not merely digits.',
    'disposition_counts': {'all_library_conditions': 26, 'source_nonEMC_conditions': 16,
                           'pending_conditions': 10, 'pending_current_named_donors': 6,
                           'authenticated_EMC_conditions': 0},
    'scientific_fate': 'Continue shelving; no molecular or imaging result in EMC, no negative biology/absence claim. Search not exhausted; complete suitable public EMC coverage still mandatory before promotion.',
    'other_reconciliation': [
        'Our actual EuropePMC original supplementary ZIP/PDF extraction fills remote scTumor Table1 access gap:all36primarytypes inspected, no EMC/generic sarcoma type. This does not close generic cell-line PRJCA021248/GSE157220 identity or every source/sample correspondence;494/499 and135441/135424 versions remain separate.',
        'Our all59current GSE319124 plus277GSE318841 conditions and26GSE200529 source records remain valid measured-metadata evidence;352experiment/135donor broader crosswalk and pediatric89sample source remain pending.',
        'Remote CASSIS expanded39subtype donor roster/70CITE-seq selection, CellSARCTx primary access and Luthria additional fresh technical-comparison specimen remain actual separate gaps. Our current21GSE243381 library metadata do not replace missing broader GSE243380/S1 fresh specimen crosswalk.',
        'Ngo and prior Subramanian exclusions unchanged/reused; no new cell-state biological pilot or promoted finding.'
    ],
    'reopen': 'Exact authentic EMC source diagnosis/donor/condition evidence, permitted processed measurements, independence/useful contrast and complete relevant coverage; suitable pending evidence blocks promotion.',
    'portability': 'Official XML ignored cache, observations/receipt and exact hashes committed. Remote raw bytes absent here; remote manifest references are not original reproduction. Missing future cache requires permitted exact-URL recovery and source-version comparison.',
    'restrictions': 'No UI/CAPTCHA/private routes/paid/GPU/outreach/publication/PR/push/shared edits; no expression values; no restricted task reopening. Original records unchanged.',
    'owned_processes_running': False,
}
write('BO112-RECONCILIATION-AMENDMENT.json', amendment)
total = sum(f.stat().st_size for f in P.rglob('*') if f.is_file())
free = shutil.disk_usage(P).free
assert total < 64 * 1024 * 1024 and free >= 10 * 1024 * 1024 * 1024
write('BO112-RECONCILIATION-VALIDATION.json',
      {'utc': now, 'official_source_hash_pass': True, 'exact_selected_BioSamples': 10,
       'exact_spatial_GSM_BioSample_disease_matches': 4,
       'current_sc004_declared_provider_isolate_matches': 2,
       'RT_direct_samples_without_disease': 4,
       'condition_count': 26, 'pending_conditions': 10, 'pending_named_current_donors': 6,
       'cross_provider_numeric_subtype_transfers': 0, 'all_original_disposition_record_hashes_preserved': True,
       'storage_bytes': total, 'raw_limit_bytes': 64 * 1024 * 1024, 'free_bytes': free,
       'new_EMC_measurements_authenticated': 0, 'no_biological_negative': True,
       'owned_processes_running': False})
print(json.dumps({'conditions': 26, 'pending': 10, 'pending_donors': 6,
                  'source_nonEMC': 16, 'retained_bytes': total, 'source_bytes': raw.stat().st_size}))
