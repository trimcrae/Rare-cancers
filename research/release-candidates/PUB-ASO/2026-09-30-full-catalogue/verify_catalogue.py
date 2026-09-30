"""Independent exhaustive window checks and boundary fixtures; standard library."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import time
import sys

sys.dont_write_bytecode = True
import analyze_catalogue as analysis

ROOT = Path(__file__).resolve().parent


def read_rows(name):
    with (ROOT / 'results' / name).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def direct_run(target, window):
    if any(target[i] != window[i] for i in range(5, 11)):
        return 0
    left, right = 5, 11
    while left > 0 and target[left - 1] == window[left - 1]:
        left -= 1
    while right < 16 and target[right] == window[right]:
        right += 1
    return right - left


def main():
    started = time.perf_counter()
    # Explicit boundaries: a full match, wing/gap mismatch, and an incomplete
    # transcript-end window. The last must not be accepted as a complete site.
    t = 'ACGTCAGTACGATCGA'
    assert analysis.gap_best(t, {'full': t})[0] == 16
    wing = ('T' if t[0] != 'T' else 'A') + t[1:]
    assert analysis.gap_best(t, {'wing': wing})[0] == 15
    gap = t[:8] + ('A' if t[8] != 'A' else 'C') + t[9:]
    assert analysis.gap_best(t, {'gap': gap})[0] == 0
    assert analysis.gap_best(t, {'truncated': t[5:]})[0] == 0
    repeated = analysis.gap_best(t, {'repeats': t + t})[1]
    assert {h['normal_start_0based'] for h in repeated} == {0, 16}
    # Character-wise oracle covers all base substitutions at every position.
    encoding_checks = 0
    for position in range(16):
        for base in 'ACGT':
            changed = t[:position] + base + t[position + 1:]
            assert analysis.encoded_hamming(analysis.encode(t), analysis.encode(changed)) == sum(a != b for a, b in zip(t, changed))
            encoding_checks += 1
    assert analysis.encoded_hamming(analysis.encode('A' * 16), analysis.encode('T' * 16)) == 16
    # Test genuine primary/secondary trade-offs and preserved final ties.
    fixture = [{'g': 7, 'h': 2}, {'g': 8, 'h': 5}, {'g': 7, 'h': 3}, {'g': 7, 'h': 3}]
    assert analysis.choice(fixture, 'g') == [fixture[0], fixture[2], fixture[3]]
    assert analysis.choice(fixture, 'g', 'h') == [fixture[2], fixture[3]]
    corpus = analysis.fasta(ROOT / 'results/normal-reference-transcripts.fasta')
    normal_windows = sorted({seq[i:i+16] for seq in corpus.values() for i in range(len(seq)-15)})
    designs = read_rows('all-designs.tsv')
    nearest = read_rows('nearest-normal-windows.tsv')
    gap_hits = read_rows('gap-match-locations.tsv')
    for row in designs:
        target = row['target_RNA_DNA_alphabet_5to3']
        minimum, longest, winners = 17, 0, set()
        for window in normal_windows:
            longest = max(longest, direct_run(target, window))
            distance = 0
            for i in range(16):
                distance += target[i] != window[i]
                # Safe pruning: additional bases cannot reduce mismatches.
                if distance > minimum:
                    break
            if distance < minimum:
                minimum, winners = distance, {window}
            elif distance == minimum:
                winners.add(window)
        assert minimum == int(row['expanded_seven_gene_min_hamming_bp']), row['design_id']
        assert longest == int(row['expanded_seven_gene_gap_run_bp']), row['design_id']
        recorded = [h for h in nearest if h['design_id'] == row['design_id']]
        assert {h['normal_window_5to3'] for h in recorded} == winners
        # Check every accession/location including identical-sequence aliases.
        expected_locations = {(ref, i) for ref, seq in corpus.items() for i in range(len(seq)-15)
                              if seq[i:i+16] in winners}
        assert {(h['reference'], int(h['normal_start_0based'])) for h in recorded} == expected_locations
        longest_locations = {(ref, int(h['normal_start_0based'])) for h in gap_hits
                             if h['design_id'] == row['design_id'] for ref in [h['reference']]}
        expected_longest = {(ref, i) for ref, seq in corpus.items() for i in range(len(seq)-15)
                            if direct_run(target, seq[i:i+16]) == longest and longest > 0}
        assert longest_locations == expected_longest
    junctions = read_rows('junction-catalogue.tsv')
    assert sum(r['control_only'] == 'True' for r in junctions) == 1
    assert sum(r['control_only'] == 'True' for r in designs) == 5
    for junction in junctions:
        group = [r for r in designs if r['junction'] == junction['junction']]
        metrics = [(int(r['expanded_seven_gene_gap_run_bp']), -int(r['expanded_seven_gene_min_hamming_bp'])) for r in group]
        expected_positions = sorted(int(r['donor_bases']) for r, metric in zip(group, metrics) if metric == min(metrics))
        assert expected_positions == json.loads(junction['final_co_winner_donor_bases'])
        assert len(group) == 5
    receipt = dict(status='PASS', completed_utc=datetime.now(timezone.utc).isoformat(),
        elapsed_seconds=round(time.perf_counter()-started, 3), designs_checked=len(designs),
        unique_normal_windows=len(normal_windows), reference_records=len(corpus),
        exhaustive_independent_checks=['global minimum character-wise Hamming and all tied sequences',
            'gap-run metric on every complete unique window', 'all closest-window accession aliases and locations',
            'all longest-gap-match accession aliases and locations', 'per-junction ranking and all final ties'],
        boundary_fixtures=['full match', 'wing mismatch', 'gap mismatch', 'truncated transcript end',
            'repeated normal sites', 'primary versus secondary preference', 'retained ties'],
        single_substitution_encoding_checks=encoding_checks,
        files={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [ROOT/'analyze_catalogue.py', ROOT/'verify_catalogue.py', ROOT/'analysis-plan.json', ROOT/'input-manifest.json']
            + sorted((ROOT/'results').glob('*.tsv'))})
    analysis.dump(ROOT/'results/verification.json', receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k != 'files'}, indent=2))


if __name__ == '__main__':
    try:
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except (AttributeError, OSError):
        pass
    main()
