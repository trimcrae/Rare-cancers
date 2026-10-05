"""Reconstruct complete identity/assay roster; no sequence or IR outcome access."""
import csv
import hashlib
import json
from pathlib import Path
from lxml import etree

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'raw'
expected = json.loads((ROOT / 'ALL23-CURRENT-IDENTITY-ASSAY-ROSTER.json').read_text())
for name, digest in expected['source_hashes'].items():
    assert hashlib.sha256((RAW / name).read_bytes()).hexdigest() == digest
samples = {row.get('accession'): row for row in etree.parse(str(RAW / 'biosample-current-efetch.xml')).xpath('//BioSample')}
runs = list(csv.DictReader((RAW / 'ena-current-runs.tsv').open(), delimiter='\t'))
by_experiment = {row['experiment_accession']: row for row in runs}
packages = etree.parse(str(RAW / 'sra-current-efetch.xml')).xpath('//EXPERIMENT_PACKAGE')
original = {row['experiment']: row for row in expected['all23_source_records']}
assert len(packages) == len(samples) == len(runs) == len(original) == 23
for package in packages:
    experiment = package.find('EXPERIMENT')
    identifier = experiment.get('accession')
    source = by_experiment[identifier]
    observation = original[identifier]
    attributes = {item.get('attribute_name'): item.text for item in samples[source['sample_accession']].xpath('.//Attribute')}
    assert attributes == observation['BioSample_attributes']
    assert attributes['isolate'] == 's_' + source['sample_alias']
    assert [run.get('accession') for run in package.xpath('.//RUN_SET/RUN')] == [observation['run']] == [source['run_accession']]
    assert package.find('SAMPLE').get('accession') == observation['SRA_sample']
    assert experiment.findtext('.//DESIGN_DESCRIPTION') == observation['design'] == 'Stranded Total RNA'
    for key, tag in [('strategy', 'LIBRARY_STRATEGY'), ('selection', 'LIBRARY_SELECTION')]:
        assert experiment.findtext('.//' + tag) == observation[key]
    assert source['library_layout'] == observation['layout'] == 'PAIRED'
    assert int(source['read_count']) == observation['metadata_read_pairs']
    assert int(source['base_count']) == observation['metadata_total_bases']
    assert sum(int(value) for value in source['fastq_bytes'].split(';')) == sum(item['bytes'] for item in observation['FASTQ_source_metadata'])
assert expected['all46_FASTQ_metadata_bytes'] == 46317317021
assert expected['resolved_engineered'] == 8 and expected['unresolved_remaining'] == 15
print('All23 exact library/sample/run and assay fields matched; no native partner/preparation inference or IR outcomes.')
