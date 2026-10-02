"""Independent full-corpus exact census plus direct verification of saved witnesses."""
import csv
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

HERE = Path(__file__).resolve().parent
RESTORED = HERE / 'verification-artifacts' / 'aso' / 'output'
OUT = HERE / 'verification-output'
GIB = 1024**3


def rows(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def main():
    started = time.monotonic()
    assert shutil.disk_usage(HERE).free >= 11.25*GIB
    OUT.mkdir(exist_ok=False)
    original_bytes = (RESTORED / 'result.json').read_bytes()
    original = json.loads(original_bytes)
    manifest = json.loads((RESTORED / 'manifest.json').read_text())
    for filename in ['result.json', 'gencode-witnesses.tsv', 'gencode-summary.tsv']:
        raw = (RESTORED / filename).read_bytes()
        assert len(raw) == manifest[filename]['bytes']
        assert hashlib.sha256(raw).hexdigest() == manifest[filename]['sha256']
    designs = {r['design_id']: r for r in original['designs']}
    assert len(designs) == 220
    queries = OUT / 'queries.tsv'
    queries.write_text(''.join(k+'\t'+v['target']+'\n' for k,v in designs.items()))
    source = [s for s in original['source_receipts'] if 'gencode.v50.transcripts.fa.gz' in s['url']][0]
    assert source['sha256'] == '5a320f524d73b5793518eb19b118829033713443d0f42af20a67bb31cc06cf56'
    assert source['bytes'] == 183554921
    fasta = OUT / 'gencode.fa.gz'
    digest = hashlib.sha256()
    size = 0
    download_start = time.monotonic()
    with urllib.request.urlopen(source['url'], timeout=45) as response, fasta.open('xb') as dest:
        while True:
            data = response.read(1024*1024)
            if not data:
                break
            size += len(data)
            assert size <= source['bytes'] and time.monotonic()-download_start < 300
            assert shutil.disk_usage(HERE).free >= 10*GIB + len(data)
            digest.update(data)
            dest.write(data)
    assert size == source['bytes'] and digest.hexdigest() == source['sha256']
    engine = OUT / 'verify-exact'
    subprocess.run(['g++','-std=c++17','-O3','-Wall','-Wextra',str(HERE/'verify_transcriptome.cpp'),'-lz','-o',str(engine)], check=True, timeout=120)
    # Independent literal substring counts on explicitly synthetic records.
    sq = OUT/'synthetic-queries.tsv'
    sf = OUT/'synthetic.fa'
    target = 'ACGTCAGGATCCTAGC'
    sq.write_text('a\t'+target+'\nalias\t'+target+'\nnone\tAAAAAAAAAAAAAAAA\n')
    synthetic = [('tx1','EWSR1',target+target),('tx2','OTHER','NN'+target+'N'),
                 ('tx3','OTHER',target[:8]),('tx4','OTHER',target[8:]),
                 ('tx5','OTHER',target.replace('T','U'))]
    sf.write_text(''.join('>'+tx+'|g|-|-|n|'+gene+'|'+str(len(seq))+'|type|\n'+seq+'\n' for tx,gene,seq in synthetic).rstrip('\n'))
    prefix = OUT/'synthetic'
    subprocess.run([str(engine),str(sq),str(sf),str(prefix)],check=True,timeout=60)
    for r in rows(OUT/'synthetic-summary.tsv'):
        needle = target if r['design_id'] in ('a','alias') else 'A'*16
        total=0
        for _, gene, sequence in synthetic:
            if (gene=='EWSR1') != (r['stratum']=='gencode_parent'):
                continue
            normalized=sequence.replace('U','T')
            total+=sum(normalized[p:p+16]==needle for p in range(len(normalized)-15))
        assert int(r['occurrences']) == total
    subprocess.run([str(engine),str(queries),str(fasta),str(OUT/'exact')],check=True,timeout=1200)
    exact = rows(OUT/'exact-summary.tsv')
    assert len(exact) == 440 and len({(r['design_id'],r['stratum']) for r in exact}) == 440
    for r in exact:
        previous = designs[r['design_id']]['strata'][r['stratum']]
        expected = previous['nearest_occurrences'] if previous['min_hamming'] == 0 else 0
        assert int(r['occurrences']) == expected, r
    exact_meta = rows(OUT/'exact-meta.tsv')
    assert len(exact_meta) == 1
    for key,value in exact_meta[0].items():
        if key in original['gencode_corpus']:
            assert int(value) == original['gencode_corpus'][key], (key,value)
    original_witnesses = rows(RESTORED/'gencode-witnesses.tsv')
    independent_witnesses = rows(OUT/'exact-witnesses.tsv')
    summary_rows = rows(RESTORED/'gencode-summary.tsv')
    summary = {(r['design_id'],r['stratum'],r['metric']):r for r in summary_rows}
    assert len(summary_rows)==len(summary)==880
    witness_counts = Counter((w['design_id'],w['stratum'],w['metric']) for w in original_witnesses)
    assert set(witness_counts) <= set(summary)
    for key,r in summary.items():
        assert witness_counts[key]==min(20,int(r['occurrences'])), key
    seen_witnesses=set()
    for w in original_witnesses:
        key=(w['design_id'],w['stratum'],w['metric'])
        assert w['value']==summary[key]['value'] and w['gene'] in summary[key]['genes'].split(';')
        identity=key+(w['transcript'],w['start_0based'])
        assert identity not in seen_witnesses
        seen_witnesses.add(identity)
    independent_counts=Counter((w['design_id'],w['stratum']) for w in independent_witnesses)
    assert set(independent_counts)<= {(r['design_id'],r['stratum']) for r in exact}
    for r in exact:
        assert independent_counts[r['design_id'],r['stratum']]==min(20,int(r['occurrences']))
    wanted = {}
    for kind, collection in [('original',original_witnesses),('independent_exact',independent_witnesses)]:
        for w in collection:
            wanted.setdefault(w['transcript'], []).append((kind,w))
    checked = {'original':0,'independent_exact':0}
    def inspect(header, sequence):
        if not header:
            return
        fields=header.split('|')
        tx,gene=fields[0],fields[5]
        for kind,w in wanted.pop(tx, []):
            start=int(w['start_0based'])
            assert 0 <= start and start+16 <= len(sequence)
            window=sequence[start:start+16]
            assert w['gene']==gene and window==w['window_5to3'] and set(window)<=set('ACGT')
            expected_stratum='gencode_parent' if gene in {'EWSR1','TAF15','TCF12','FUS','TFG','NR4A3','PGR'} else 'gencode_other'
            assert w['stratum']==expected_stratum
            target=designs[w['design_id']]['target']
            if kind=='independent_exact':
                assert target == window
            elif w['metric']=='hamming':
                assert sum(a!=b for a,b in zip(target,window))==int(w['value'])
            else:
                values=[right-left for left in range(6) for right in range(11,17) if target[left:right]==window[left:right]]
                assert values and max(values)==int(w['value'])
            checked[kind]+=1
    header,sequence='',[]
    with gzip.open(fasta,'rt') as stream:
        for line in stream:
            if line.startswith('>'):
                inspect(header,''.join(sequence))
                header,sequence=line[1:].strip(),[]
            else:
                sequence.append(line.strip().upper().replace('U','T'))
        inspect(header,''.join(sequence))
    assert not wanted
    assert checked['original']==len(original_witnesses) and checked['independent_exact']==len(independent_witnesses)
    exact_targets=[r for r in original['designs'] if not r['control'] and r['union_hamming']==0]
    result=dict(schema='aso-independent-exact-and-witness-check/1',status='passed',
                original_result_sha256=hashlib.sha256(original_bytes).hexdigest(),
                original_code_revision='b066a7e7bcffe4892c78f2d9462cc70b4d14945b',source_sha256=digest.hexdigest(),
                algorithm='Independent Aho-Corasick exact-pattern automaton; original engine uses encoded Hamming neighborhoods',
                corpus_metadata=exact_meta[0],design_stratum_exact_counts_compared=len(exact),
                witnesses_directly_verified=checked,exact_target_designs=len(exact_targets),
                exact_target_design_ids=[r['design_id'] for r in exact_targets],
                seconds=time.monotonic()-started,
                limits=['Independent global census validates exact full matches and their counts.',
                        'Direct witness checks validate reported coordinates and scores, not independent maximality of every nonzero distance or gap.',
                        'No tissue expression, accessibility, cleavage, potency or clinical risk estimate.'])
    (OUT/'verification-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('EMC_INDEPENDENT_ASO_BEGIN')
    print(json.dumps(result,indent=2))
    print('EMC_INDEPENDENT_ASO_END')


if __name__=='__main__':
    main()
