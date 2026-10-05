#!/usr/bin/env python3
"""Reproduce the prospective, value-masked human DMR annotation gate."""
import argparse
import csv
import datetime
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REGIONS = {
    'IG-DMR': ('CCTACCACTGAACTGGGTTTGCCAGT', 'CTGAAATTCTGCAGTAGGAATTGC'),
    'MEG3-US': ('GGAGCATCCCACCTGAGGCCTGGGGCTCCC', 'GCAAGCTCCACAGGCTGTAAAGGGGGTGTT'),
    'MEG3-promoter': ('GCCAGGCAGGGTGAATTCAGGCACAATGTGTG', 'AACTGGTTCCCAGATGTAAGCCAGAGGCTGTC'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reverse_complement(seq):
    return seq.translate(str.maketrans('ACGT', 'TGCA'))[::-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    seq_source = ROOT / 'sources/chr14_hg38_DMR_reference.json'
    ref = json.loads(seq_source.read_text())
    dna, base = ref['dna'].upper(), ref['start']
    assert ref['genome'] == 'hg38' and ref['chrom'] == 'chr14'
    assert len(dna) == ref['end'] - base == 75000
    original = (ROOT / 'sources/human_imprint_DMR_suppS1.txt').read_text()
    intervals = {}
    for name, primers in REGIONS.items():
        hits = []
        for primer in primers:
            assert primer in original, 'Primer is not in original supplementary table.'
            current = []
            for orientation, query in [('direct', primer), ('reverse_complement', reverse_complement(primer))]:
                offset = dna.find(query)
                while offset >= 0:
                    current.append({'start': base + offset, 'end': base + offset + len(primer),
                                    'orientation': orientation, 'sequence': primer})
                    offset = dna.find(query, offset + 1)
            assert len(current) == 1, (name, current)
            hits += current
        intervals[name] = {'chr': 'chr14', 'start': min(x['start'] for x in hits),
                           'end': max(x['end'] for x in hits), 'primers': hits,
                           'definition': 'Envelope of uniquely mapped original genomic F/R sequences, 0-based half-open; not the entire biological DMR or a PCR design.'}
    platforms = {}
    for platform in ['HM450', 'EPIC']:
        with gzip.open(ROOT / ('sources/' + platform + '.ordering.tsv.gz'), 'rt') as handle:
            ordering = list(csv.DictReader(handle, delimiter='\t'))
        with gzip.open(ROOT / ('sources/' + platform + '.hg38.coord.tsv.gz'), 'rt') as handle:
            coordinates = list(csv.DictReader(handle, delimiter='\t'))
        assert len(ordering) == len(coordinates)
        assert len({x['Probe_ID'] for x in ordering}) == len(ordering)
        selections = {}
        for name, interval in intervals.items():
            selected = []
            for probe, coordinate in zip(ordering, coordinates):
                if coordinate['CpG_chrm'] != interval['chr']:
                    continue
                position = int(coordinate['CpG_beg'])
                if interval['start'] <= position < interval['end']:
                    assert dna[position - base:position - base + 2] == 'CG'
                    selected.append({'Probe_ID': probe['Probe_ID'], 'position': position,
                                     'strand': coordinate['strand'], 'mapQ': int(coordinate['mapQ'])})
            selections[name] = selected
        midpoint = (intervals['IG-DMR']['start'] + intervals['IG-DMR']['end']) // 2
        nearest = sorted(({'Probe_ID': probe['Probe_ID'], 'position': int(coordinate['CpG_beg']),
                           'distance_to_envelope_midpoint': abs(int(coordinate['CpG_beg']) - midpoint),
                           'mapQ': int(coordinate['mapQ'])}
                          for probe, coordinate in zip(ordering, coordinates)
                          if coordinate['CpG_chrm'] == 'chr14'),
                         key=lambda x: x['distance_to_envelope_midpoint'])[:5]
        platforms[platform] = {'ordering_rows': len(ordering), 'coordinate_rows': len(coordinates),
                               'region_probes': selections, 'nearest_IG_probes': nearest}
    assert [platforms[x]['ordering_rows'] for x in ['HM450', 'EPIC']] == [486427, 866553]
    for platform in platforms.values():
        assert not platform['region_probes']['IG-DMR']
        assert len(platform['region_probes']['MEG3-US']) == 3
        assert len(platform['region_probes']['MEG3-promoter']) == 3
    sources = {str(path.relative_to(ROOT)): {'sha256': sha(path), 'bytes': path.stat().st_size,
                                            'cache_only': True}
               for path in sorted((ROOT / 'sources').iterdir()) if path.is_file()}
    result = {'schema': 'emc-r9-value-masked-DMR-assay-gate/1',
              'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'human_primary': 'PMC3038880 Supplementary Table1 genomic sequences',
              'reference': {k: ref[k] for k in ['genome', 'chrom', 'start', 'end']},
              'intervals': intervals, 'platforms': platforms,
              'mapping_limits': ['Uniqueness is established within the retrieved 75kb chr14 reference segment, not by genome-wide primer specificity testing.',
                                 'Original printed location, main table and assay-coordinate table disagree for IG-DMR; no guessed assembly or outcome-dependent coordinate extension is used.',
                                 'Zero probes concerns this exact primary-sequence envelope. It is not absence of probes from the whole locus or absence of EMC methylation.',
                                 'Nearby EPIC probes outside the envelope cannot replace it without a new primary-supported assay contract; mapQ is reported rather than treated as full probe-quality authentication.',
                                 'MEG3 probes have position/sequence checks, but SNP/cross-reactivity masks, preprocessing portability and biological values were not evaluated after the joint gate failed.'],
              'all_sources': sources,
              'methylation_values_inspected': False,
              'decision': 'SHELVE original joint IG+MEG3 array contrast; suitable independent regional measurements remain pending.'}
    Path(args.output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'arrays': {k: v['ordering_rows'] for k, v in platforms.items()},
                      'IG_probes': {k: len(v['region_probes']['IG-DMR']) for k, v in platforms.items()},
                      'sources': len(sources), 'retained_new_raw_bytes': sum(x['bytes'] for x in sources.values()),
                      'values_inspected': False}))


if __name__ == '__main__':
    main()
