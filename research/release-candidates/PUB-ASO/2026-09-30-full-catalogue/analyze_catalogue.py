"""Offline catalogue comparison. Standard library only; never changes older evidence.

Run python analyze_catalogue.py [--output DIRECTORY]. All scientific inputs must
match input-manifest.json. Gap-run enumeration is adapted from the accepted
September 26 evidence/analyze.py best(), without importing its top-level writes.
"""
from collections import defaultdict, Counter
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT.parent / '2026-09-26/evidence'
CONTROL = 'EWSR1_e13__NR4A3_e2'
SUFFIXES = ['', '-noncoding-acceptor', '-taf15intron2', '-ewsr1intron2']


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rows(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def table(path, data):
    assert data, path
    fields = list(dict.fromkeys(k for row in data for k in row))
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for row in data:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                             for k, v in row.items()})


def dump(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def fasta(path):
    result = {}
    for block in path.read_text().split('>')[1:]:
        name, *lines = block.splitlines()
        assert name not in result
        result[name] = ''.join(lines).upper()
    return result


def reverse_complement(sequence):
    return sequence.translate(str.maketrans('ACGT', 'TGCA'))[::-1]


def gap_best(target, corpus):
    """All maximum exact runs covering target positions 6..11, complete windows only."""
    for size in range(16, 5, -1):
        hits = []
        for start in range(6):
            stop = start + size
            if stop > 16 or stop < 11:
                continue
            seed = target[start:stop]
            for ref, seq in corpus.items():
                pos = seq.find(seed)
                while pos >= 0:
                    window_start = pos - start
                    if 0 <= window_start <= len(seq) - 16:
                        window = seq[window_start:window_start + 16]
                        hits.append(dict(reference=ref, normal_start_0based=window_start,
                                         normal_window_5to3=window, target_match_start_0based=start,
                                         gap_spanning_run_bp=size,
                                         mismatch_positions_1based=[i + 1 for i, (a, b) in
                                                                   enumerate(zip(target, window)) if a != b]))
                    pos = seq.find(seed, pos + 1)
        if hits:
            return size, hits
    return 0, []


def gap_seed_extend(target, corpus):
    """Independent check: locate the six gap bases, then extend both directions."""
    longest = 0
    for seq in set(corpus.values()):
        pos = seq.find(target[5:11])
        while pos >= 0:
            window_start = pos - 5
            if window_start >= 0 and window_start + 16 <= len(seq):
                left, right = 5, 11
                while left > 0 and seq[window_start + left - 1] == target[left - 1]:
                    left -= 1
                while right < 16 and seq[window_start + right] == target[right]:
                    right += 1
                longest = max(longest, right - left)
            pos = seq.find(target[5:11], pos + 1)
    return longest


def encode(sequence):
    value = 0
    for base in sequence:
        value = (value << 2) | 'ACGT'.index(base)
    return value


def encoded_hamming(a, b):
    difference = a ^ b
    return ((difference | (difference >> 1)) & 0x55555555).bit_count()


def window_index(corpus):
    aliases = defaultdict(list)
    for ref, seq in corpus.items():
        aliases[seq].append(ref)
    locations = defaultdict(list)
    for seq, refs in aliases.items():
        for start in range(len(seq) - 15):
            locations[seq[start:start + 16]].append((refs, start))
    return locations


def minimum_hamming(target, encoded_windows):
    target_code = encode(target)
    smallest, winners = 17, []
    for window, code in encoded_windows:
        distance = encoded_hamming(target_code, code)
        if distance < smallest:
            smallest, winners = distance, [window]
        elif distance == smallest:
            winners.append(window)
    assert smallest <= 16
    return smallest, winners


def choice(designs, gap_field, distance_field=None):
    minimum = min(r[gap_field] for r in designs)
    chosen = [r for r in designs if r[gap_field] == minimum]
    if distance_field:
        maximum = max(r[distance_field] for r in chosen)
        chosen = [r for r in chosen if r[distance_field] == maximum]
    return chosen


def main(output):
    for item in load(ROOT / 'input-manifest.json'):
        assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']
    plan = load(ROOT / 'analysis-plan.json')
    parents = load(EVIDENCE / 'inputs/emc-construct-inputs.json')['genes']
    old_corpus = fasta(EVIDENCE / 'results/normal-reference-transcripts.fasta')
    assert len(old_corpus) == 77 and len(set(old_corpus.values())) == 71
    corpus = dict(old_corpus)
    corpus['PGR:archived_ENST00000325455_version_unspecified'] = parents['PGR']['cdna']
    expected = load(ROOT / 'sources/PGR-accessions.json')['accessions']
    observed = []
    for entry in (ROOT / 'sources/PGR-curated-RefSeq.gb').read_text().split('//'):
        match = re.search(r'^VERSION\s+(\S+)', entry, re.M)
        if not match:
            continue
        acc = match.group(1)
        assert acc in expected and acc not in observed
        observed.append(acc)
        seq = ''.join(re.findall('[a-zA-Z]+', entry.split('ORIGIN', 1)[1])).upper().replace('U', 'T')
        length = int(re.search(r'^LOCUS\s+\S+\s+(\d+) bp', entry, re.M).group(1))
        assert len(seq) == length
        assert '/gene="PGR"' in entry
        corpus['PGR:' + acc] = seq
    assert sorted(observed) == expected
    assert all(set(seq) <= set('ACGT') for seq in corpus.values()), 'Ambiguous bases require plan amendment'
    baseline7 = {gene: parents[gene]['cdna'] for gene in parents}
    assert set(baseline7) == {'EWSR1', 'TAF15', 'TCF12', 'FUS', 'TFG', 'NR4A3', 'PGR'}
    baseline6 = {k: v for k, v in baseline7.items() if k != 'PGR'}
    assert all(old_corpus[k] == v for k, v in baseline6.items())
    windows = window_index(corpus)
    encoded = [(w, encode(w)) for w in windows]
    cryptic = load(EVIDENCE / 'inputs/nr4a3-intron2-cryptic-exon.json')['resolved_cryptic_exon']['sequence']
    evidence = rows(EVIDENCE / 'results/junction-evidence.tsv')
    prior = {(r['junction'], r['antisense_5to3']): r for r in rows(EVIDENCE / 'results/design-comparisons.tsv')}
    accepted_primary = load(EVIDENCE / 'inputs/aso-parent-gap-pairing.json')['per_design']
    accepted = {(r['junction'], r['antisense_5to3']): r['longest_parent_duplex_bp_through_gap'] for r in accepted_primary}
    design_rows, junction_rows, gap_hits, hamming_hits = [], [], [], []
    expanded_overlap = primary_overlap = 0
    for suffix in SUFFIXES:
        atlas_path = f'inputs/nr4a3-fusion-junction-atlas{suffix}.json'
        atlas = load(EVIDENCE / atlas_path)
        for panel in atlas['panels']:
            label = panel['junction_label']
            donor = parents[panel['donor_symbol']]
            donor_end = donor['exons'][panel['donor_exon_end'] - 1]['cdna_end_exclusive']
            left = donor['cdna'][donor_end - 30:donor_end]
            acceptor_exon = panel['acceptor_exon_start']
            acceptor_start = ''
            if isinstance(acceptor_exon, int):
                acceptor_start = parents['NR4A3']['exons'][acceptor_exon - 1]['cdna_start_0based']
                right = parents['NR4A3']['cdna'][acceptor_start:acceptor_start + 30]
            else:
                right = cryptic[:30]
            support = [r for r in evidence if r['catalogue_junction'] == label]
            classes = sorted({r['evidence_class'] for r in support})
            if label == CONTROL:
                assert not support
                evidence_class = 'annotation_error_control'
            elif 'directly_reported_deposit_sequence' in classes:
                evidence_class = 'deposited_sequence_match'
            elif 'reference_reconstruction_from_reported_coordinates' in classes:
                evidence_class = 'coordinate_based_reference_reconstruction'
            elif support:
                evidence_class = 'construct_description_reference_reconstruction'
            else:
                evidence_class = 'hypothetical_exact_reference_join'
            junction_rows.append(dict(junction=label, atlas=atlas_path, evidence_class=evidence_class,
                control_only=label == CONTROL, support_ids=[r['evidence_id'] for r in support],
                support_classes=classes, source_urls=sorted({r['source_url'] for r in support}),
                source_ambiguities=[r['ambiguity'] for r in support],
                exact_sequence_status=('No direct or resolved exact-source correspondence in accepted evidence; published fusion/exon labels alone do not resolve this reference join.' if not support and label != CONTROL else ''),
                donor=panel['donor_symbol'], donor_archived_transcript=donor['transcript'],
                donor_transcript_version='unspecified in archived construct input', donor_exon_1based=panel['donor_exon_end'],
                donor_cdna_end_exclusive=donor_end, acceptor_archived_transcript=parents['NR4A3']['transcript'],
                acceptor_exon=acceptor_exon, acceptor_cdna_start_0based=acceptor_start,
                junction_RNA_DNA_alphabet_30_plus_30=left + '|' + right))
            assert len(panel['designs']) == 5
            positions = []
            for design in panel['designs']:
                target = design['target_mRNA_5to3']
                aso = design['antisense_5to3']
                donor_bases = 16 - design['junction_offset_in_oligo']
                positions.append(donor_bases)
                assert len(target) == len(aso) == 16 and set(target) <= set('ACGT')
                assert reverse_complement(aso) == target
                assert target == left[-donor_bases:] + right[:16 - donor_bases]
                key = label, aso
                six_baseline = gap_best(target, baseline6)[0]
                if key in accepted:
                    assert six_baseline == accepted[key]
                    primary_overlap += 1
                seven_baseline = gap_best(target, baseline7)[0]
                six_expanded = gap_best(target, old_corpus)[0]
                if key in prior:
                    assert six_expanded == int(prior[key]['expanded_parent_corpus_longest_match_bp'])
                    assert six_baseline == int(prior[key]['legacy_six_parent_longest_gap_spanning_match_bp'])
                    expanded_overlap += 1
                seven_expanded, hits = gap_best(target, corpus)
                assert seven_expanded == gap_seed_extend(target, corpus)
                assert seven_expanded >= six_expanded >= six_baseline
                assert seven_expanded >= seven_baseline >= six_baseline
                distance, hamming_windows = minimum_hamming(target, encoded)
                assert (distance == 0) == (seven_expanded == 16)
                base = dict(design_id=f'{label}:d{donor_bases}', junction=label, donor_bases=donor_bases,
                            acceptor_bases=16-donor_bases, antisense_5to3=aso)
                row = dict(**base, target_RNA_DNA_alphabet_5to3=target,
                    proposed_architecture='16nt 5-LNA/6-DNA/5-LNA', evidence_class=evidence_class,
                    control_only=label == CONTROL,
                    canonical_six_gene_gap_run_bp=six_baseline,
                    canonical_seven_gene_gap_run_bp=seven_baseline,
                    expanded_six_gene_gap_run_bp=six_expanded,
                    expanded_seven_gene_gap_run_bp=seven_expanded,
                    expanded_seven_gene_min_hamming_bp=distance,
                    gap_run_increase_with_isoforms=seven_expanded-seven_baseline,
                    gap_run_increase_with_PGR=seven_expanded-six_expanded,
                    exact_16nt_normal_match=distance == 0)
                design_rows.append(row)
                gap_hits.extend(dict(**base, **hit) for hit in hits)
                for window in hamming_windows:
                    assert sum(a != b for a, b in zip(target, window)) == distance
                    for aliases, start in windows[window]:
                        for ref in aliases:
                            hamming_hits.append(dict(**base, reference=ref, normal_start_0based=start,
                                normal_window_5to3=window, hamming_distance_bp=distance,
                                mismatch_positions_1based=[i + 1 for i, (a, b) in enumerate(zip(target, window)) if a != b]))
            assert sorted(positions) == [6, 7, 8, 9, 10]
    assert len(junction_rows) == plan['scope']['atlas_junctions'] == 44
    assert len(design_rows) == plan['scope']['designs'] == 220
    assert expanded_overlap == 40 and primary_overlap == 190
    assert len({r['design_id'] for r in design_rows}) == 220
    g, h = 'expanded_seven_gene_gap_run_bp', 'expanded_seven_gene_min_hamming_bp'
    for junction in junction_rows:
        group = sorted([r for r in design_rows if r['junction'] == junction['junction']], key=lambda r: r['donor_bases'])
        primary = choice(group, g)
        final = choice(group, g, h)
        canonical = choice(group, 'canonical_seven_gene_gap_run_bp')
        for row in group:
            row['primary_co_winner'] = row in primary
            row['final_co_winner'] = row in final
            row['pareto_alternative'] = not any(
                other[g] <= row[g] and other[h] >= row[h] and
                (other[g] < row[g] or other[h] > row[h]) for other in group)
        junction.update(dict(primary_best_gap_run_bp=primary[0][g],
            primary_co_winner_donor_bases=[r['donor_bases'] for r in primary],
            final_co_winner_donor_bases=[r['donor_bases'] for r in final],
            final_co_winner_ASO_5to3=[r['antisense_5to3'] for r in final],
            final_min_hamming_bp=final[0][h], final_choice_count=len(final),
            pareto_donor_bases=[r['donor_bases'] for r in group if r['pareto_alternative']],
            canonical_primary_co_winner_donor_bases=[r['donor_bases'] for r in canonical],
            primary_choice_set_changed_with_isoforms=set(r['donor_bases'] for r in primary) != set(r['donor_bases'] for r in canonical)))
    output.mkdir(parents=True, exist_ok=True)
    table(output / 'all-designs.tsv', design_rows)
    table(output / 'junction-catalogue.tsv', junction_rows)
    table(output / 'gap-match-locations.tsv', gap_hits)
    table(output / 'nearest-normal-windows.tsv', hamming_hits)
    manifest = [dict(reference=k, gene=k.split(':')[0], length_nt=len(seq), sha256=hashlib.sha256(seq.encode()).hexdigest(),
        source=('sources/PGR-curated-RefSeq.gb' if k.startswith('PGR:N') else
                '../2026-09-26/evidence/inputs/emc-construct-inputs.json' if k.startswith('PGR:archived') else
                '../2026-09-26/evidence/results/normal-reference-transcripts.fasta')) for k, seq in corpus.items()]
    table(output / 'normal-reference-manifest.tsv', manifest)
    (output / 'normal-reference-transcripts.fasta').write_text(''.join('>' + k + '\n' + seq + '\n' for k, seq in corpus.items()), encoding='ascii')
    target_rows = [r for r in design_rows if not r['control_only']]
    targets = [r for r in junction_rows if not r['control_only']]
    summary = dict(junctions_including_control=44, designs_including_control=220,
        noncontrol_junctions=len(targets), noncontrol_designs=len(target_rows),
        evidence_classes=dict(Counter(r['evidence_class'] for r in junction_rows)),
        normal_records=len(corpus), normal_unique_sequences=len(set(corpus.values())),
        normal_genes=sorted(baseline7), unique_normal_16nt_windows=len(windows),
        PGR_added_records=len(corpus)-len(old_corpus), PGR_curated_accessions=expected,
        old_expanded_comparisons_reproduced=expanded_overlap, primary_baseline_comparisons_reproduced=primary_overlap,
        designs_with_longer_gap_run_from_isoforms=sum(r['gap_run_increase_with_isoforms'] > 0 for r in target_rows),
        designs_with_longer_gap_run_from_PGR=sum(r['gap_run_increase_with_PGR'] > 0 for r in target_rows),
        exact_normal_16nt_matches=sum(r['exact_16nt_normal_match'] for r in target_rows),
        junctions_with_changed_primary_choice_set=sum(r['primary_choice_set_changed_with_isoforms'] for r in targets),
        junctions_with_single_final_choice=sum(r['final_choice_count'] == 1 for r in targets),
        junctions_with_tied_final_choices=sum(r['final_choice_count'] > 1 for r in targets),
        junctions_with_primary_ties_broken_by_hamming=sum(len(r['primary_co_winner_donor_bases']) > r['final_choice_count'] for r in targets),
        junctions_with_competing_pareto_alternatives=sum(set(r['pareto_donor_bases']) != set(r['final_co_winner_donor_bases']) for r in targets),
        all_counts_exclude_annotation_control_unless_explicit=True,
        plan_sha256=hashlib.sha256((ROOT / 'analysis-plan.json').read_bytes()).hexdigest(),
        limitation=plan['claim_boundary'])
    dump(output / 'summary.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'results')
    args = parser.parse_args()
    # Bound the local burden during the daily quiet-work window.
    try:
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except (AttributeError, OSError):
        pass
    main(args.output)
