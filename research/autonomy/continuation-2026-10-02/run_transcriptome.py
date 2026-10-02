"""Bounded public-reference extension; original catalogue and inputs stay frozen."""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request
import unittest
from datetime import datetime, timezone
import test_scan
import interval_ranking
import test_interval_ranking

HERE = Path(__file__).resolve().parent
OUT = HERE / 'output'
INPUT = HERE / 'inputs'
SOURCE_REF = 'a916dab2979e27f930b417243f021b6c2b2ca371'
SOURCE_BASE = ('https://raw.githubusercontent.com/trimcrae/Rare-cancers/' + SOURCE_REF +
               '/research/release-candidates/PUB-ASO/2026-09-30-full-catalogue/results/')
FASTA_URL = 'https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/gencode.v50.transcripts.fa.gz'
FASTA_MD5 = '4d5bd41b247480e12c0b370490f52ddd'
FASTA_BYTES = 183554921
CAP = 1024 ** 3
GIB = 1024 ** 3
RECEIPTS = []


def fetch(url, path, *, git_blob=None, expected_md5=None, expected_bytes=None):
    if path.exists():
        raise ValueError('Refuse to replace source capture: ' + str(path))
    request = urllib.request.Request(url, headers={'User-Agent': 'EMC-computational-research/1.0'})
    start = time.monotonic()
    sha = hashlib.sha256()
    md5 = hashlib.md5()
    size = 0
    with urllib.request.urlopen(request, timeout=45) as response, path.open('xb') as dest:
        if response.status != 200:
            raise ValueError('Source HTTP status ' + str(response.status))
        declared = int(response.headers.get('Content-Length', 0))
        if declared > CAP or (expected_bytes and declared and declared != expected_bytes):
            raise ValueError('Unexpected source Content-Length')
        headers = {k: response.headers.get(k) for k in ('Content-Length', 'Last-Modified', 'ETag')}
        final_url = response.url
        while True:
            data = response.read(1024 * 1024)
            if not data:
                break
            size += len(data)
            if size > CAP or time.monotonic() - start > 600 or shutil.disk_usage(INPUT).free < 10 * GIB + len(data):
                raise ValueError('Source size, deadline or free-space limit')
            sha.update(data)
            md5.update(data)
            dest.write(data)
    if expected_bytes and size != expected_bytes:
        raise ValueError('Source byte count mismatch')
    if expected_md5 and md5.hexdigest() != expected_md5:
        raise ValueError('Pinned provider MD5 mismatch')
    if git_blob:
        raw = path.read_bytes()
        actual = hashlib.sha1(('blob ' + str(len(raw)) + '\0').encode() + raw).hexdigest()
        if actual != git_blob:
            raise ValueError('Frozen Git blob mismatch')
    RECEIPTS.append(dict(url=url, final_url=final_url, bytes=size, sha256=sha.hexdigest(),
                         md5=md5.hexdigest(), git_blob=git_blob, headers=headers,
                         retrieved_utc=datetime.now(timezone.utc).isoformat()))


def read_tsv(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def scanner(engine, queries, fasta, kind, prefix):
    start = time.monotonic()
    subprocess.run([str(engine), str(queries), str(fasta), kind, '3', str(prefix)],
                   check=True, timeout=2400)
    data = read_tsv(Path(str(prefix) + '-summary.tsv'))
    expected = 220 * 2 * (2 if kind == 'gencode' else 1)
    if len(data) != expected or len({(r['design_id'], r['stratum'], r['metric']) for r in data}) != expected:
        raise ValueError('Incomplete or duplicate scanner summary')
    meta_rows = read_tsv(Path(str(prefix) + '-meta.tsv'))
    if len(meta_rows) != 1:
        raise ValueError('Incomplete scanner metadata')
    meta = {k: int(v) for k, v in meta_rows[0].items()}
    assert meta['query_count'] == 220 and meta['radius'] == 3
    return data, dict(meta, seconds=time.monotonic() - start)


def main():
    start = time.monotonic()
    if shutil.disk_usage(HERE).free < 11.25 * GIB:
        raise RuntimeError('Require source/output budget plus at least10GiB headroom')
    OUT.mkdir(exist_ok=False)
    INPUT.mkdir(exist_ok=False)
    engine = OUT / 'scan'
    subprocess.run(['g++', '-std=c++17', '-O3', '-Wall', '-Wextra', str(HERE / 'scan_transcriptome.cpp'), '-lz', '-o', str(engine)], check=True, timeout=120)
    oracle = test_scan.main(str(engine))
    interval_suite = unittest.defaultTestLoader.loadTestsFromModule(test_interval_ranking)
    interval_result = unittest.TextTestRunner(verbosity=1).run(interval_suite)
    if not interval_result.wasSuccessful():
        raise ValueError('Interval arithmetic/ranking checks failed')
    interval_checks = dict(tests=interval_result.testsRun, status='passed', fixtures='synthetic')
    (OUT / 'oracle.json').write_text(json.dumps(oracle, indent=2) + '\n')
    fetch(SOURCE_BASE + 'all-designs.tsv', INPUT / 'all-designs.tsv', git_blob='ee3b2300ab06851780789f0ea2f990231fb61270')
    fetch(SOURCE_BASE + 'normal-reference-transcripts.fasta', INPUT / 'parents.fasta', git_blob='5a978cdb1f345f72abd68bab29c983a52c34e5cf')
    designs = read_tsv(INPUT / 'all-designs.tsv')
    assert len(designs) == 220 and len({r['design_id'] for r in designs}) == 220
    assert sum(r['control_only'] == 'False' for r in designs) == 215
    for r in designs:
        target = r['target_RNA_DNA_alphabet_5to3']
        assert len(target) == 16 and set(target) <= set('ACGT')
        assert r['antisense_5to3'].translate(str.maketrans('ACGT', 'TGCA'))[::-1] == target
    queries = INPUT / 'queries.tsv'
    queries.write_text(''.join(r['design_id'] + '\t' + r['target_RNA_DNA_alphabet_5to3'] + '\n' for r in designs))
    baseline, baseline_meta = scanner(engine, queries, INPUT / 'parents.fasta', 'archived', OUT / 'archive')
    assert baseline_meta['records'] == 85 and baseline_meta['ambiguous_windows'] == 0
    index = {(r['design_id'], r['stratum'], r['metric']): r for r in baseline}
    for r in designs:
        g = index[r['design_id'], 'archived_parent', 'gap']
        h = index[r['design_id'], 'archived_parent', 'hamming']
        assert int(g['value']) == int(r['expanded_seven_gene_gap_run_bp']), r['design_id']
        old_h = int(r['expanded_seven_gene_min_hamming_bp'])
        assert (int(h['value']) == old_h and h['exact'] == '1') if old_h <= 3 else (h['value'] == '4' and h['exact'] == '0')
    # Only download/run the larger new corpus after both independent checks pass.
    fetch(FASTA_URL, INPUT / 'gencode.fa.gz', expected_md5=FASTA_MD5, expected_bytes=FASTA_BYTES)
    extended, extended_meta = scanner(engine, queries, INPUT / 'gencode.fa.gz', 'gencode', OUT / 'gencode')
    assert extended_meta['records'] > 100000 and extended_meta['parent_records'] > 0 and extended_meta['other_records'] > 0
    index.update({(r['design_id'], r['stratum'], r['metric']): r for r in extended})
    result_rows = []
    for r in designs:
        strata = {}
        for s in ('archived_parent', 'gencode_parent', 'gencode_other'):
            g, h = index[r['design_id'], s, 'gap'], index[r['design_id'], s, 'hamming']
            strata[s] = dict(max_complete_core_run=int(g['value']), gap_occurrences=int(g['occurrences']),
                             min_hamming=int(h['value']) if h['exact'] == '1' else None,
                             min_hamming_lower_bound=int(h['value']), hamming_exact=h['exact'] == '1',
                             nearest_occurrences=int(h['occurrences']), gap_genes=g['genes'].split(';') if g['genes'] else [],
                             nearest_genes=h['genes'].split(';') if h['genes'] else [])
        union_gap = max(x['max_complete_core_run'] for x in strata.values())
        exact_h = [x['min_hamming'] for x in strata.values() if x['hamming_exact']]
        union_low, union_upper, union_h = interval_ranking.union_distance(int(r['expanded_seven_gene_min_hamming_bp']), exact_h)
        assert union_gap >= int(r['expanded_seven_gene_gap_run_bp'])
        assert union_h is None or union_h <= int(r['expanded_seven_gene_min_hamming_bp'])
        result_rows.append(dict(design_id=r['design_id'], junction=r['junction'], donor_bases=int(r['donor_bases']),
                                control=r['control_only'] == 'True', evidence_class=r['evidence_class'],
                                target=r['target_RNA_DNA_alphabet_5to3'], antisense=r['antisense_5to3'],
                                archive_gap=int(r['expanded_seven_gene_gap_run_bp']), archive_hamming=int(r['expanded_seven_gene_min_hamming_bp']),
                                archive_primary=r['primary_co_winner'] == 'True', archive_final=r['final_co_winner'] == 'True',
                                strata=strata, union_gap=union_gap, union_hamming=union_h,
                                union_hamming_lower_bound=union_low, union_hamming_upper_bound=union_upper))
    groups = defaultdict(list)
    for r in result_rows:
        groups[r['junction']].append(r)
    rankings = []
    for name, rs in groups.items():
        assert len(rs) == 5
        primary = [r for r in rs if r['union_gap'] == min(x['union_gap'] for x in rs)]
        secondary_resolved, final_ids = interval_ranking.rank_primary_intervals(primary)
        final = [r for r in primary if r['design_id'] in final_ids]
        old_primary = sorted(r['donor_bases'] for r in rs if r['archive_primary'])
        old_final = sorted(r['donor_bases'] for r in rs if r['archive_final'])
        new_primary = sorted(r['donor_bases'] for r in primary)
        new_final = sorted(r['donor_bases'] for r in final)
        rankings.append(dict(junction=name, control=rs[0]['control'], evidence_class=rs[0]['evidence_class'],
                             archive_primary=old_primary, archive_final=old_final, union_primary=new_primary,
                             union_final=new_final if secondary_resolved else None, secondary_resolved=secondary_resolved,
                             primary_changed=old_primary != new_primary,
                             final_changed=(old_final != new_final) if secondary_resolved else None))
    target_rows = [r for r in result_rows if not r['control']]
    target_rankings = [r for r in rankings if not r['control']]
    result = dict(schema='aso-transcriptome-extension/1', status='executed', source_ref=SOURCE_REF,
                  elapsed_seconds=time.monotonic()-start, oracle=oracle, interval_checks=interval_checks,
                  archived_baseline_check='All220 exact gap values and bounded Hamming values agree',
                  source_receipts=RECEIPTS, archive_corpus=baseline_meta, gencode_corpus=extended_meta,
                  summary=dict(targets=215, junctions=43, annotation_error_controls=5,
                               designs_with_longer_gap=sum(r['union_gap'] > r['archive_gap'] for r in target_rows),
                               designs_with_smaller_hamming=sum(r['union_hamming'] is not None and r['union_hamming'] < r['archive_hamming'] for r in target_rows),
                               exact_full_matches=sum(r['union_hamming'] == 0 for r in target_rows),
                               censored_minima=sum(r['union_hamming'] is None for r in target_rows),
                               primary_choice_changes=sum(r['primary_changed'] for r in target_rankings),
                               final_choice_changes=sum(r['final_changed'] is True for r in target_rankings),
                               unresolved_secondary_junctions=sum(not r['secondary_resolved'] for r in target_rankings)),
                  designs=result_rows, rankings=rankings,
                  limits=['Mature annotated reference RNA, not tissue expression or unspliced pre-mRNA.',
                          'Counts are record-window occurrences including aliases/haplotypes, not independent samples.',
                          'Gap zero means no perfect complete-six-base-core match, not absence of complementarity.',
                          'Hamming null is interval [4,archived exact distance]; archive distance4 proves union exact4 when no<=3 hit.',
                          'All normal-parent/other-gene matches retained; no intended fusion reference was added.',
                          'No cleavage, delivery, accessibility, chemical-pattern or safety validation.'])
    (OUT / 'result.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    manifest = {p.name:dict(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in OUT.iterdir() if p.is_file() and p.name != 'scan'}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('EMC_ASO_RESULT_BEGIN')
    print(json.dumps(result, indent=2, allow_nan=False))
    print('EMC_ASO_RESULT_END')


if __name__ == '__main__':
    main()
