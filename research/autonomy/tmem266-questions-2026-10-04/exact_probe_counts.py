"""Exact assay-design lookup in the pre-existing lossy TempO-Seq checkpoint."""
import csv, hashlib, json, math
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
SEQ = 'GTGGTGACCATACACACAGCTGGCTCTGGGACACCGCTGTCACTGCTGGG'
RC = SEQ.translate(str.maketrans('ACGT','TGCA'))[::-1]

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(65536), b''): h.update(block)
    return h.hexdigest()

def main():
    table = ROOT/'research/modalities/emc-fourth-cohort-probe-counts.tsv'
    receipt = ROOT/'research/modalities/emc-fourth-cohort-quant-inputs.json'
    linkage = BASE.parent/'tmem266-tissue-2026-10-03/fish-sensitivity-results.json'
    original = json.loads(receipt.read_text())
    links = {r['run_accession']:r for r in json.loads(linkage.read_text())['run_linkage']}
    matches = []
    with table.open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            if row['probe_sequence'] in {SEQ,RC}: matches.append(row)
    measurements=[]
    for row in matches:
        for key, value in row.items():
            if not key.startswith('SRR'): continue
            run=key.split(':')[0]; meta=original['runs'][run]
            assert meta['stopped_because']=='eof'
            count=int(value); cap=math.ceil(meta['epsilon']*meta['n_reads_read'])
            measurements.append({'run':run,'sample_alias':links[run]['sample_alias'],
                'biosample':links[run]['sample_accession'],
                'orientation':'manufacturer' if row['probe_sequence']==SEQ else 'reverse_complement',
                'persisted_positive':count>0,'stored_count':count,
                'count_lower_bound':count if count>0 else None,
                'conservative_upper_bound':count+cap if count>0 else None,
                'lossy_error_cap':cap,'original_n_reads':meta['n_reads_read'],
                'source_fastq':meta['url'],
                'identity_conflict':run=='SRR35940654'})
    out={'scope':'Detector-oligo product sequence, not a native RNA junction or full transcript',
         'fixed_sequence':SEQ,'reverse_complement':RC,'matched_rows':matches,
         'measurements':measurements,
         'provenance':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in (table,receipt,linkage)],
         'limitation':'Positive counts are lower bounds from historical complete scans, with epsilon*N conservative errors; absent/zero entries are censored, not zero RNA. Original FASTQ bytes are not fetched or reauthenticated here.'}
    (BASE/'exact-probe-counts.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'matches':len(matches),'measurements':measurements},indent=2))

if __name__=='__main__': main()
