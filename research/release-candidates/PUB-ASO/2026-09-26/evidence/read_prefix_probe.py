"""Bounded positive-evidence probe, not a prevalence or negative-detection assay.

Read bounded 16 or 64 MiB prefixes of mate 1 from two attributable Brenca runs.
The final amended analysis uses 64 MiB and includes the cryptic-exon candidates.
Retain prefixes for exact offline replay and all exact 16+16 junction hits.
No whole-file checksum or complete-run coverage is claimed for a prefix.
"""
import argparse, csv, datetime, gzip, hashlib, io, json, pathlib, time, urllib.request, re

ROOT=pathlib.Path(__file__).resolve().parent
INPUTS=ROOT/'inputs'
RC=str.maketrans('ACGTN','TGCAN')
def rc(s): return s.translate(RC)[::-1]
def load(p):return json.loads(p.read_text(encoding='utf-8'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fetch',action='store_true');ap.add_argument('--mib',type=int,choices=[16,64],default=64);args=ap.parse_args()
    parents=load(INPUTS/'emc-construct-inputs.json')['genes']
    nr=parents['NR4A3']; candidates={}
    for file in ['nr4a3-fusion-junction-atlas.json','nr4a3-fusion-junction-atlas-noncoding-acceptor.json','nr4a3-fusion-junction-atlas-taf15intron2.json','nr4a3-fusion-junction-atlas-ewsr1intron2.json']:
        atlas=load(INPUTS/file)
        for panel in atlas['panels']:
            donor=parents[panel['donor_symbol']]
            end=donor['exons'][panel['donor_exon_end']-1]['cdna_end_exclusive']
            if isinstance(panel['acceptor_exon_start'],int):
                start=nr['exons'][panel['acceptor_exon_start']-1]['cdna_start_0based']
                right=nr['cdna'][start:start+16]
            else:
                right=load(INPUTS/'nr4a3-intron2-cryptic-exon.json')['resolved_cryptic_exon']['sequence'][:16]
            seam=donor['cdna'][end-16:end]+right
            candidates[panel['junction_label']]=seam
    patterns=re.compile('|'.join(sorted(set(candidates.values()))))
    metadata=list(csv.DictReader((ROOT/'sources/PRJNA692081-ena.tsv').open(),delimiter='\t'))
    mapping={r['Sample'][1:]:r['Condition'] for r in csv.DictReader((ROOT/'sources/DElite-metadata.csv').open(),delimiter=';')}
    selected=['SRR13435278','SRR13435264']; results=[]
    (ROOT/'reads').mkdir(exist_ok=True)
    for run in selected:
        row=next(r for r in metadata if r['run_accession']==run)
        path=ROOT/'reads'/f'{run}_1.first{args.mib}MiB.fastq.gz.partial'
        url='https://'+row['fastq_ftp'].split(';')[0]
        if not path.exists():
            if not args.fetch:raise FileNotFoundError(path)
            before=time.monotonic()
            req=urllib.request.Request(url,headers={'Range':f'bytes=0-{args.mib*1024*1024-1}'})
            with urllib.request.urlopen(req,timeout=45) as response:
                data=response.read(args.mib*1024*1024)
                receipt=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),url=url,http_status=response.status,content_range=response.headers.get('Content-Range'),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),seconds=round(time.monotonic()-before,2))
            path.write_bytes(data)
            path.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2))
            print('downloaded',run,len(data),flush=True)
        gz=gzip.GzipFile(fileobj=io.BytesIO(path.read_bytes()))
        hits=[]; n=0; ends='';counts={};minqcounts={}
        try:
            while True:
                fields=[gz.readline() for _ in range(4)]
                if not fields[0]:ends='eof';break
                if not all(x.endswith(b'\n') for x in fields):ends='incomplete_record';break
                rid,seq,plus,qual=[x.decode().strip() for x in fields]
                assert rid.startswith('@') and plus.startswith('+') and len(seq)==len(qual)
                n+=1
                for orientation,target,q in [('+',seq,qual),('-',rc(seq),qual[::-1])]:
                    for match in patterns.finditer(target):
                        for label in [lab for lab,seam in candidates.items() if seam==match.group()]:
                            loc=match.start()
                            minq=min(ord(x)-33 for x in q[loc:loc+32])
                            hits.append(dict(read_id=rid,junction=label,orientation=orientation,seam_start_in_oriented_read=loc,min_phred33_across_32nt=minq,sequence=seq,quality=qual))
                            counts[label]=counts.get(label,0)+1
                            if minq>=20:minqcounts[label]=minqcounts.get(label,0)+1
        except (EOFError,gzip.BadGzipFile):ends='intentional_truncated_gzip_prefix'
        gz.close()
        out=ROOT/'reads'/f'{run}-{args.mib}MiB-junction-hits.json';out.write_text(json.dumps(hits,indent=2))
        summary=dict(run=run,sample=row['sample_accession'],sample_alias=row['sample_alias'],condition=mapping[row['sample_alias']],url=url,prefix_bytes=path.stat().st_size,prefix_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),complete_read_records_scanned=n,termination=ends,anchor_bases_each_side=16,candidate_junctions=len(candidates),raw_hit_counts=counts,phred20_hit_counts=minqcounts,unique_read_sequences=len({h['sequence'] for h in hits}),scope=f'first {args.mib} MiB compressed of mate1 only; targeted exact junction presence; no negative inference; not independent molecules',full_file_md5_not_verified=True)
        results.append(summary); print(json.dumps(summary),flush=True)
    (ROOT/f'read-probe-results-{args.mib}MiB.json').write_text(json.dumps(results,indent=2))

if __name__=='__main__':main()
