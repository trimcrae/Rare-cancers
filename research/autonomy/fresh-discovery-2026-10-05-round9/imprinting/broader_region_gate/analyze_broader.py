#!/usr/bin/env python3
"""Bounded primary bisulfite-primer geometry; no methylation values."""
import argparse, csv, gzip, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'sources'
CANDIDATES = {
    'HCC2012_IG1': ['ATTATTGAATTGGGTTTGTTAGTAG', 'CAAAACAACTCAAATCCTTTATAAC'],
    'HCC2012_IG2': ['TAGYGATTTGTTAATTGYGAGTG', 'CRAATCCATTATAACCAATTACAATACCAC'],
    'OS2016_IG1_outer': ['ATGTTAATTATTTTTTGGATAAGAG', 'AATCAAAACAACTCAAATCCTTTA'],
    'OS2016_IG2_outer': ['GTTAAGAGTTTGTGGATTTGTGAGAAATG', 'GTAAAAATGAGGAAAAGGGATAAAATGAG'],
    'OS2016_IG2_inner_R_only': ['CATTATAACCAATTACAATACCACA'],
    'iPSC2022_IG_ASMM': ['AGTTTTATGTTAAGATGTTAATTATTTTTTGGA', 'ACCAAAAAACCTAACAAATCAAAACA'],
}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--output', required=True); a = ap.parse_args()
    reference = json.loads((SOURCES / 'chr14_hg38_DMR_reference.json').read_text())
    original = reference['dna'].upper(); base = reference['start']
    assert reference['genome'] == 'hg38' and reference['chrom'] == 'chr14' and len(original) == 75000
    trans = str.maketrans('ACGTRY', 'TGCAYR')
    result = {}
    for name, primers in CANDIDATES.items():
        placements = []
        for primer in primers:
            hits = []
            for orientation, seq in [('direct', primer), ('reverse_complement', primer.translate(trans)[::-1])]:
                for mode, dna in [('C_to_T', original.replace('C', 'T')), ('G_to_A', original.replace('G', 'A'))]:
                    normalized = seq.replace('C', 'T') if mode == 'C_to_T' else seq.replace('G', 'A')
                    pattern = normalized.replace('Y', '[CT]').replace('R', '[AG]')
                    for hit in re.finditer(pattern, dna):
                        hits.append({'start': base + hit.start(), 'end': base + hit.end(),
                                     'orientation': orientation, 'conversion': mode})
            placements.append({'primer': primer, 'placements': hits})
        complete = len(primers) == 2 and all(len(p['placements']) == 1 for p in placements)
        interval = None
        if complete:
            assert placements[0]['placements'][0]['orientation'] == 'direct'
            assert placements[1]['placements'][0]['orientation'] == 'reverse_complement'
            interval = {'start': min(p['placements'][0]['start'] for p in placements),
                        'end': max(p['placements'][0]['end'] for p in placements)}
        result[name] = {'primers': placements, 'paired_envelope': interval,
                        'status': 'candidate converted-primer envelope only' if complete else 'incomplete mapping; no envelope substitution'}
    arrays = {}
    for platform in ['HM450', 'EPIC']:
        with gzip.open(SOURCES / (platform + '.ordering.tsv.gz'), 'rt') as f: ordering = list(csv.DictReader(f, delimiter='\t'))
        with gzip.open(SOURCES / (platform + '.hg38.coord.tsv.gz'), 'rt') as f: coordinates = list(csv.DictReader(f, delimiter='\t'))
        assert len(ordering) == len(coordinates)
        selected = {}
        for name, region in result.items():
            bounds = region['paired_envelope']
            selected[name] = None if bounds is None else [
                {'Probe_ID': probe['Probe_ID'], 'start': int(coord['CpG_beg']), 'mapQ': int(coord['mapQ'])}
                for probe, coord in zip(ordering, coordinates)
                if coord['CpG_chrm'] == 'chr14' and bounds['start'] <= int(coord['CpG_beg']) < bounds['end']]
        arrays[platform] = {'rows': len(ordering), 'complete_envelope_probes': selected}
    assert result['HCC2012_IG2']['paired_envelope'] == {'start': 100811069, 'end': 100811161}
    for platform in arrays.values():
        for name in ['HCC2012_IG1', 'HCC2012_IG2', 'OS2016_IG1_outer', 'iPSC2022_IG_ASMM']:
            assert platform['complete_envelope_probes'][name] == []
    output = {'method': 'Exact primer-derived C/T or G/A conversion-normalized local sequence matching, both orientations, source IUPAC degeneracy; no mismatch search, guessed coordinate lifts, methylation values or whole-genome specificity claim.',
              'limits': 'Candidate converted-primer envelopes do not establish whole functional CGI/DMR boundaries. Methylation-specific probe CpG sites were not treated as allele or regional output. Unmapped/multi-placed primers prevent envelope acceptance; no hybrid outer/inner PCR-round envelope.',
              'reference': {'genome': 'hg38', 'chrom': 'chr14', 'start': base, 'end': reference['end']},
              'primary_candidates': result, 'arrays': arrays,
              'methylation_values_inspected': False}
    Path(a.output).write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'candidate_regions': len(result), 'complete_pairs': sum(x['paired_envelope'] is not None for x in result.values()), 'values': False}))


if __name__ == '__main__': main()
