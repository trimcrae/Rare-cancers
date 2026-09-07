"""Offline, standard-library verification of frozen public GEO metadata.

Expression and platform table bodies are skipped without evaluating their values.
Only a fixed whitelist of descriptive metadata is retained in outputs.
"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import platform
import re
import time

ROOT = Path(__file__).resolve().parent
EXPECTED_HASHES = {
    'sources/GSE6481_family.soft.gz': 'eec1f676f7b05f3115d2b04c926e6085a429350ec6b84a1d637ff27ae8375887',
    'sources/GSE24369_family.soft.gz': '98c83c8ca23b7052cf0d4d0099a7bf1af6c3c972276038c3a633e2a5349b3c37',
    'sources/peerj-21497-article.xml': '2d9a6ee4ed417860867eb954e0b0a4fa3fa3042787f5af3c0a1fea9bb5fbe768',
    'sources/peerj-21497-figure-s6.png': '29932259e722fa46b84f01e2b662bcd58b66a108db669eca5035913eb9d8df03',
}
EXPECTED_COUNTS = {
    'GSE6481': {'Synovial sarcoma':16,'Myxoid liposarcoma':19,'Lipoma':3,
                'Well-differentiated liposarcoma':3,'Dedifferentiated liposarcoma':15,
                'Myxofibrosarcoma':15,'Leiomyosarcoma':6,'Malignant peripheral nerve sheath tumor':3,
                'Fibrosarcoma':4,'Malignant fibrous histiocytoma':21},
    'GSE24369': {'Desmoid fibromatosis tumor':6,'Extraskeletal myxoid chondrosarcoma':6,
                 'Low-grade fibromyxoid sarcoma':17,'Myxofibrosarcoma':6,
                 'Solitary fibrous tumor':5,'Skeletal muscle':2},
}
KEEP = {'Series_title','Series_sample_id','Series_platform_id','Series_pubmed_id','Series_overall_design',
        'Platform_title','Platform_technology','Platform_organism','Platform_data_row_count',
        'Sample_title','Sample_geo_accession','Sample_source_name_ch1','Sample_characteristics_ch1',
        'Sample_platform_id','Sample_description','Sample_channel_count'}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def single(fields, key):
    values = fields.get(key, [])
    require(len(values) == 1, 'Expected exactly one '+key)
    return values[0]

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n', encoding='utf-8')

def metadata_lines(path):
    inside = False
    with gzip.open(path, 'rt', encoding='utf-8', errors='strict') as stream:
        for number, raw in enumerate(stream, 1):
            line = raw.rstrip('\r\n')
            if line.endswith('_table_begin'):
                require(not inside, 'Nested table marker')
                inside = True
                continue
            if line.endswith('_table_end'):
                require(inside, 'Unmatched table end')
                inside = False
                continue
            if not inside:
                yield number, line
    require(not inside, 'Truncated table')

def parse_metadata(path):
    records = []
    current = None
    for line_number, line in metadata_lines(path):
        if line.startswith('^'):
            kind, accession = line[1:].split(' = ', 1)
            current = {'type':kind,'accession':accession,'source_line':line_number,'fields':{}}
            records.append(current)
        elif line.startswith('!') and ' = ' in line and current is not None:
            key, value = line[1:].split(' = ', 1)
            if key in KEEP:
                current['fields'].setdefault(key, []).append(value)
    return records

def alternate_labels(path, accession):
    """Separate direct roster/label scan; does not use parsed record objects."""
    labels, titles, platforms, listed = {}, {}, {}, []
    current = None
    for number, line in metadata_lines(path):
        if line.startswith('^'):
            current = None
            if line.startswith('^SAMPLE = '):
                current = line.split(' = ',1)[1]
                require(current not in labels, 'Duplicate sample in direct scan')
                labels[current] = None
        if line.startswith('!Series_sample_id = '):
            listed.append(line.split(' = ',1)[1])
        if current is None:
            continue
        if line.startswith('!Sample_platform_id = '):
            require(current not in platforms, 'Duplicate direct platform field')
            platforms[current] = line.split(' = ',1)[1]
        if line.startswith('!Sample_title = '):
            require(current not in titles, 'Duplicate direct title field')
            titles[current] = line.split(' = ',1)[1]
            if accession == 'GSE24369':
                match = re.fullmatch(r'(.+) ([0-9]+)', titles[current])
                require(match is not None, 'Unexpected GSE24369 title')
                labels[current] = {'Desmoid fibromatosis':'Desmoid fibromatosis tumor',
                                   'Skeletal muscle pooled RNA':'Skeletal muscle'}.get(match[1],match[1])
        if accession == 'GSE6481' and line.startswith('!Sample_source_name_ch1 = '):
            raw = line.split(' = ',1)[1]
            require(raw.startswith('Soft tissue tumors - '), 'Unexpected GSE6481 source name')
            require(labels[current] is None, 'Duplicate direct diagnostic field')
            labels[current] = raw.removeprefix('Soft tissue tumors - ')
    require(len(listed) == len(set(listed)), 'Duplicate series accession in direct scan')
    require(set(listed) == set(labels) == set(titles) == set(platforms), 'Direct roster mismatch')
    require(all(labels.values()), 'Missing direct diagnostic label')
    return labels, titles, platforms

def verify_geo(accession):
    path = ROOT/'sources'/(accession+'_family.soft.gz')
    records = parse_metadata(path)
    series = [r for r in records if r['type'] == 'SERIES']
    samples = [r for r in records if r['type'] == 'SAMPLE']
    platforms = [r for r in records if r['type'] == 'PLATFORM']
    require(len(series) == 1 and series[0]['accession'] == accession, 'Wrong series')
    ids = [r['accession'] for r in samples]
    listed = series[0]['fields']['Series_sample_id']
    require(len(ids) == len(set(ids)) == len(listed) == len(set(listed)), 'Duplicate/incomplete sample roster')
    require(set(ids) == set(listed), 'Series/sample roster mismatch')
    alternate, titles, alternate_platforms = alternate_labels(path, accession)
    require(set(ids) == set(alternate), 'Independent roster mismatch')
    rows, types, title_numbers = [], Counter(), {}
    for sample in samples:
        fields, gsm = sample['fields'], sample['accession']
        require(single(fields,'Sample_geo_accession') == gsm, 'Sample accession field mismatch')
        title = single(fields,'Sample_title')
        characteristics = fields['Sample_characteristics_ch1']
        prefix = 'Histology:' if accession == 'GSE6481' else 'tissue: '
        matches = [x for x in characteristics if x.startswith(prefix)]
        require(len(matches) == 1, 'Missing/ambiguous diagnostic field')
        diagnosis = matches[0][len(prefix):]
        require(diagnosis == alternate[gsm] and title == titles[gsm], 'Independent label mismatch')
        plat = single(fields,'Sample_platform_id')
        require(plat == alternate_platforms[gsm], 'Independent platform mismatch')
        if accession == 'GSE6481':
            require(single(fields,'Sample_description').split(', ',2)[2] == diagnosis, 'Description/histology mismatch')
        else:
            sample_types = [x for x in characteristics if x.startswith('sample type: ')]
            require(len(characteristics) == 2 and len(sample_types) == 1, 'Unexpected characteristic schema')
            expected_type = 'sample type: pooled RNA' if diagnosis == 'Skeletal muscle' else 'sample type: tumor biopsy'
            require(sample_types[0] == expected_type, 'Tissue/sample-type mismatch')
            types[sample_types[0]] += 1
            title_numbers.setdefault(diagnosis,[]).append(int(title.rsplit(' ',1)[1]))
        rows.append({'gsm':gsm,'source_line':sample['source_line'],'title':title,
                     'diagnosis_field':matches[0],'diagnosis':diagnosis,'platform':plat,
                     'source_name':single(fields,'Sample_source_name_ch1'),
                     'characteristics':[x for x in characteristics if x.startswith(prefix) or x.startswith('sample type: ')]})
    counts = dict(sorted(Counter(r['diagnosis'] for r in rows).items()))
    require(counts == EXPECTED_COUNTS[accession], 'Frozen diagnosis-count mismatch')
    require(Counter(alternate.values()) == Counter(counts), 'Direct diagnostic counts mismatch')
    if accession == 'GSE6481':
        design = single(series[0]['fields'],'Series_overall_design')
        terms = design.split('consisting of ',1)[1].split(' were analyzed',1)[0]
        aggregate = {}
        for term in re.split(', | and ',terms):
            match = re.fullmatch(r'(.+) \(n=(\d+)\)',term)
            require(match is not None and match[1] not in aggregate,'Unexpected series design format')
            aggregate[match[1]] = int(match[2])
        require(aggregate == {k.lower():v for k,v in counts.items()},'Series design/count mismatch')
    else:
        for diagnosis, numbers in title_numbers.items():
            require(sorted(numbers) == list(range(1,counts[diagnosis]+1)), 'Title-number roster mismatch')
    platform_counts = dict(Counter(r['platform'] for r in rows))
    declared_platforms = series[0]['fields']['Series_platform_id']
    require(set(platform_counts) == set(declared_platforms) == {r['accession'] for r in platforms}, 'Platform roster mismatch')
    return {'accession':accession,'sample_count':len(rows),'diagnosis_counts':counts,
            'platform_counts':platform_counts,'sample_type_counts':dict(types),
            'series':series[0],'platforms':platforms,'complete_sample_roster':rows,
            'checks':{'unique_complete_series_roster':True,'independent_label_and_roster_scan':True,
                      'frozen_diagnosis_counts':True,'consistent_platform_roster':True,
                      'all_samples_included':True},
            'expression_values_parsed_or_computed':False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='results', help='Output directory relative to this bundle')
    args = parser.parse_args()
    rel = Path(args.output)
    require(not rel.is_absolute() and '..' not in rel.parts, 'Use a relative output directory inside this bundle')
    require(rel.parts and rel.parts[0] != 'sources', 'Do not write into original sources')
    start, started = time.perf_counter(), datetime.now(timezone.utc).isoformat()
    manifest = json.loads((ROOT/'source-manifest.json').read_text(encoding='utf-8'))
    declared = {x['file']:x for x in manifest['sources']}
    require(set(declared) == set(EXPECTED_HASHES),'Unexpected source manifest roster')
    for relative, expected in EXPECTED_HASHES.items():
        blob = (ROOT/relative).read_bytes()
        require(hashlib.sha256(blob).hexdigest() == expected == declared[relative]['sha256'], 'Source hash mismatch: '+relative)
        require(len(blob) == declared[relative]['bytes'],'Source byte-count mismatch: '+relative)
    results = {acc:verify_geo(acc) for acc in EXPECTED_COUNTS}
    output = ROOT/rel
    output.mkdir(parents=True,exist_ok=True)
    for acc, result in results.items():
        write_json(output/(acc+'-metadata.json'),result)
    summary = {'status':'passed','source_hashes_checked':EXPECTED_HASHES,
               'counts':{k:{'samples':v['sample_count'],'diagnoses':v['diagnosis_counts']} for k,v in results.items()},
               'expression_values_parsed_or_computed':False,
               'scope':'Source integrity, deposited metadata and complete sample rosters.'}
    write_json(output/'verification-summary.json',summary)
    write_json(output/'execution.json',{'status':'passed','exit_code':0,'command':'python -X utf8 -B verify_metadata.py --output '+args.output,
               'python_version':platform.python_version(),'started_utc':started,
               'finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-start,
               'network_access_required':False})
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__ == '__main__':
    main()
