"""Independent value-masked primary-sequence and coherent array-coordinate review."""
import csv
import datetime
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import re
from lxml import etree

OUT = Path(__file__).resolve().parent
INPUT = Path('/workspace/emc-r6-challenge/research/autonomy/fresh-discovery-2026-10-05-round9/imprinting')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


gate = json.loads((INPUT / 'ASSAY-GATE.json').read_text())
verified_sources = []
for relative, expected in gate['all_sources'].items():
    path = INPUT / relative
    assert path.stat().st_size == expected['bytes']
    assert digest(path) == expected['sha256']
    verified_sources.append(relative)

reference = json.loads((INPUT / 'sources/chr14_hg38_DMR_reference.json').read_text())
sequence = reference['dna'].upper()
base = reference['start']
assert reference['genome'] == 'hg38' and reference['chrom'] == 'chr14'
assert len(sequence) == 75000
printed = (INPUT / 'sources/human_imprint_DMR_suppS1.txt').read_text()
source_rows = {}
for line in printed.splitlines():
    if any(key in line for key in ['IG‐DMR', 'MEG3‐US', 'MEG3 ']):
        fields = re.findall(r'\S+', line)
        if len(fields) >= 6 and fields[1] == '14' and fields[3].startswith(('CCT', 'GGA', 'GCC')):
            source_rows[fields[0]] = fields
regions = {'IG-DMR': 'IG‐DMR', 'MEG3-US': 'MEG3‐US', 'MEG3-promoter': 'MEG3'}
mapped = {}
for name, label in regions.items():
    fields = source_rows[label]
    placements = []
    for primer in fields[3:5]:
        reverse = primer.translate(str.maketrans('ACGT', 'TGCA'))[::-1]
        matches = [(base + match.start(), base + match.end(), orientation)
                   for query, orientation in [(primer, 'direct'), (reverse, 'reverse_complement')]
                   for match in re.finditer(re.escape(query), sequence)]
        assert len(matches) == 1
        placements.append({'sequence': primer, 'start': matches[0][0], 'end': matches[0][1], 'orientation': matches[0][2]})
    start = min(row['start'] for row in placements)
    end = max(row['end'] for row in placements)
    assert (start, end) == (gate['intervals'][name]['start'], gate['intervals'][name]['end'])
    mapped[name] = {'start': start, 'end': end, 'placements': placements}

platforms = {}
for platform in ['HM450', 'EPIC']:
    selected = {name: [] for name in mapped}
    seen = set()
    rows = 0
    with gzip.open(INPUT / f'sources/{platform}.ordering.tsv.gz', 'rt') as ordered_handle, gzip.open(INPUT / f'sources/{platform}.hg38.coord.tsv.gz', 'rt') as coordinate_handle:
        ordered = csv.DictReader(ordered_handle, delimiter='\t')
        coordinates = csv.DictReader(coordinate_handle, delimiter='\t')
        for identity, coordinate in itertools.zip_longest(ordered, coordinates):
            assert identity is not None and coordinate is not None
            identifier = identity['Probe_ID']
            assert identifier not in seen
            seen.add(identifier)
            rows += 1
            if coordinate['CpG_chrm'] != 'chr14':
                continue
            position = int(coordinate['CpG_beg'])
            for name, region in mapped.items():
                if region['start'] <= position < region['end']:
                    assert sequence[position - base:position - base + 2] == 'CG'
                    selected[name].append({'Probe_ID': identifier, 'position': position,
                                           'strand': coordinate['strand'], 'mapQ': int(coordinate['mapQ'])})
    assert selected == gate['platforms'][platform]['region_probes']
    assert rows == gate['platforms'][platform]['coordinate_rows']
    platforms[platform] = {'all_rows': rows, 'selected': selected}

primary = etree.parse(str(INPUT / 'sources/PMC3038880.xml'))
coordinate_rows = []
for row in primary.xpath('//table-wrap[@id="T1"]//tr'):
    text = ' '.join(row.itertext())
    if text.startswith(('IG-DMR ', 'MEG3-US ', 'MEG3 ')):
        # Only genomic-location fields are exported; published normal methylation is irrelevant.
        coordinate_rows.append({'region': text.split()[0], 'chr': text.split()[1], 'location': text.split()[2]})
coverage = json.loads((INPUT / 'COVERAGE.json').read_text())
assert len(coverage['all_GSE140686_EMC']) == 10
assert len(coverage['all_fixed_primary_FFPE_control_inventory']) == 62
result = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'source_checks': {'all_original_sources_hashed': len(verified_sources), 'mismatches': 0},
          'primer_mapping': mapped, 'platforms': platforms, 'primary_main_table_locations': coordinate_rows,
          'all_metadata_counts': {'EMC': 10, 'comparison_inventory': 62},
          'Case21': coverage['Case21'],
          'limits': ['Independent replay matches exact primary genomic-sequence envelopes and all selected probe identities.',
                     'Sequence uniqueness is local to a75kb official reference; original corresponding genomic sequences are not a new PCR design.',
                     'Zero IG-envelope probes does not establish no broader IG-DMR/adjacent measurement. Human broader primary interval definition remains pending.',
                     'Probe coordinates/mapQ alone do not authenticate SNP/cross-reactivity, biological methylation or allelic imprinting.',
                     'Postfreeze added sources are excluded from original20-source binding; no byte-level equality is claimed for owner current inventory.'],
          'methylation_values_inspected': False, 'raw_copies_downloads': 0}
(OUT / 'COORDINATE-REPLAY.json').write_text(json.dumps(result, indent=2) + '\n')
print('20 original hashes; six primary sequences; all1352980 coordinate rows and selected identities matched; no methylation values.')
