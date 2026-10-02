"""Independent exhaustive-window oracle; fixtures are explicitly synthetic."""
import csv
import gzip
import json
from pathlib import Path
import random
import subprocess
import tempfile


def rows(path):
    return list(csv.DictReader(Path(path).open(), delimiter='\t'))


def oracle(target, records, metric):
    values = []
    for name, sequence in records:
        sequence = sequence.upper().replace('U', 'T')
        for start in range(len(sequence) - 15):
            window = sequence[start:start + 16]
            if set(window) - set('ACGT'):
                continue
            if metric == 'hamming':
                score = sum(a != b for a, b in zip(target, window))
                if score > 3:
                    continue
            else:
                # Enumerate all possible enclosing substrings, unlike engine extension.
                lengths = [stop - left for left in range(6) for stop in range(11, 17)
                           if target[left:stop] == window[left:stop]]
                if not lengths:
                    continue
                score = max(lengths)
            values.append((score, name, start, window))
    if not values:
        return (0 if metric == 'gap' else 4), [], metric == 'gap'
    best = (max if metric == 'gap' else min)(x[0] for x in values)
    return best, [x for x in values if x[0] == best], True


def main(engine):
    rng = random.Random(20261002)
    target = 'ACGTCAGGATCCTAGC'
    queries = [('query0', target), ('same_sequence', target),
               ('nearby', 'TCGTCAGGATCCTAGC'), ('partial_core', 'ACGTCGGGATCCTAGC')]
    records = []
    for n in (0, 1, 2, 3, 4):
        for positions in (list(range(n)), list(range(5, 5 + n)), list(range(16 - n, 16))):
            seq = list(target)
            for p in positions:
                seq[p] = next(b for b in 'ACGT' if b != seq[p])
            records.append((f'EWSR1:mutation{len(records)}', ''.join(seq)))
    records += [('EWSR1:short', target[:15]), ('EWSR1:edge', 'A' + target),
                ('EWSR1:repeat', target + target), ('EWSR1:U', target.replace('T', 'U')),
                ('EWSR1:reverse', target.translate(str.maketrans('ACGT', 'TGCA'))[::-1])]
    records += [(f'EWSR1:N{p}', target[:p] + 'N' + target[p+1:]) for p in range(16)]
    records += [(f'EWSR1:random{i}', ''.join(rng.choices('ACGTN', k=rng.randrange(14, 100)))) for i in range(80)]
    # A line exceeding the gzgets buffer checks input chunk assembly.
    records += [('EWSR1:long_line', 'N' * 65520 + target + 'N' * 32)]
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        q = root / 'queries.tsv'
        q.write_text(''.join(f'{i}\t{s}\n' for i, s in queries))
        raw = ''.join(f'>{i}\n{s}\n' for i, s in records).rstrip('\n')
        # Isolate each mismatch pattern so a perfect hit elsewhere cannot mask it.
        for case_index, record in enumerate(records[:15]):
            isolated = root / 'isolated.fa'
            isolated.write_text('>' + record[0] + '\n' + record[1] + '\n')
            prefix = root / 'isolated'
            subprocess.run([engine, str(q), str(isolated), 'archived', '3', str(prefix)], check=True, capture_output=True)
            for row in rows(str(prefix) + '-summary.tsv'):
                score, hits, exact = oracle(dict(queries)[row['design_id']], [record], row['metric'])
                assert (int(row['value']), int(row['occurrences']), bool(int(row['exact']))) == (score, len(hits), exact), (case_index, row)
        for label, payload in [('plain', raw), ('gzip', raw)]:
            fasta = root / f'{label}.fa'
            if label == 'gzip':
                fasta.write_bytes(gzip.compress(payload.encode()))
            else:
                fasta.write_text(payload)
            prefix = root / label
            subprocess.run([engine, str(q), str(fasta), 'archived', '3', str(prefix)], check=True)
            observed = {(r['design_id'], r['metric']): r for r in rows(str(prefix) + '-summary.tsv')}
            witnesses = rows(str(prefix) + '-witnesses.tsv')
            for ident, sequence in queries:
                for metric in ('gap', 'hamming'):
                    score, hits, exact = oracle(sequence, records, metric)
                    r = observed[ident, metric]
                    assert (int(r['value']), int(r['occurrences']), bool(int(r['exact']))) == (score, len(hits), exact), (ident, metric, r, score, len(hits))
                    expected = [(h[1], str(h[2]), h[3]) for h in hits[:20]]
                    actual = [(h['transcript'], h['start_0based'], h['window_5to3']) for h in witnesses if h['design_id'] == ident and h['metric'] == metric]
                    assert actual == expected, (label, ident, metric, actual, expected)
        # These short records must not be joined across a FASTA boundary.
        boundary = root / 'boundary.fa'
        boundary.write_text('>EWSR1:a\n' + target[:8] + '\n>EWSR1:b\n' + target[8:] + '\n')
        subprocess.run([engine, str(q), str(boundary), 'archived', '3', str(root / 'boundary')], check=True)
        assert all(int(x['occurrences']) == 0 for x in rows(root / 'boundary-summary.tsv'))
        # GENCODE parent/non-parent partition and declared-length validation.
        gc = root / 'gencode.fa'
        gc.write_text(f'>ENST1|ENSG1|-|-|x|EWSR1|16|protein_coding|\n{target}\n>ENST2|ENSG2|-|-|y|OTHER|16|lncRNA|\n{target}\n')
        subprocess.run([engine, str(q), str(gc), 'gencode', '3', str(root / 'gc')], check=True)
        gcrows = rows(root / 'gc-summary.tsv')
        assert {x['stratum'] for x in gcrows} == {'gencode_parent', 'gencode_other'}
        for r in gcrows:
            sequence = dict(queries)[r['design_id']]
            score, hits, exact = oracle(sequence, [('EWSR1:test', target)], r['metric'])
            assert (int(r['value']), int(r['occurrences']), bool(int(r['exact']))) == (score, len(hits), exact)
        gc.write_text(gc.read_text().replace('|16|', '|17|', 1))
        assert subprocess.run([engine, str(q), str(gc), 'gencode', '3', str(root / 'bad')], capture_output=True).returncode != 0
    receipt = {'status': 'passed', 'fixtures': 'synthetic', 'seed': 20261002,
               'query_records': len(queries), 'sequence_records': len(records),
               'oracle': 'every unambiguous complete window; independent substring enumeration and direct mismatch count',
               'checks': ['plain/gzip equivalence', 'counts/extrema/all first20 witnesses', '0..4 mismatches', 'core and flank mismatches', 'duplicate query sequences', 'N windows', 'U normalization', 'reverse orientation retained separately', 'FASTA/chunk boundaries', 'parent partition', 'length mismatch refusal']}
    print(json.dumps(receipt, sort_keys=True))
    return receipt


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
