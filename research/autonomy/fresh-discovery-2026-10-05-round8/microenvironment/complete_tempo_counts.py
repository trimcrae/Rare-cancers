#!/usr/bin/env python3
"""Finite complete TempO-Seq stream. Never retain FASTQs or infer molecules.

Strict full50nt synthetic-probe assignment; half-probe/adapter diagnostics are
recorded but never used to allocate biological counts. The published9500gene
benchmark determines whether this estimator can support the fixed contrast.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv, gzip, hashlib, io, json, time, datetime, urllib.request
import numpy as np
import openpyxl
from scipy.stats import spearmanr

P=Path(__file__).parent
R=Path('/workspace/Rare-cancers/research/autonomy')
RUNS=R/'fresh-discovery-2026-10-04/microenvironment/PRJNA1357027-runs.tsv'
FILTERED=R/'tmem266-tissue-2026-10-03/peerj-source-s009.xlsx'
START=time.monotonic(); LIMIT=45*60


class HashReader:
    def __init__(self,h):self.h=h;self.bytes=0;self.md5=hashlib.md5();self.sha=hashlib.sha256()
    def read(self,n=-1):
        if time.monotonic()-START>LIMIT:raise TimeoutError('Frozen45minstage limit; partial remains pending')
        b=self.h.read(n);self.bytes+=len(b);self.md5.update(b);self.sha.update(b);return b


def timestamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write(name,obj):
    (P/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')


w=openpyxl.load_workbook(P/'raw/HWT2.0-manifest.xlsx',read_only=True,data_only=True)
it=w.active.iter_rows(values_only=True);h=next(it);assert list(h[:5])==['Probe Name','Gene Symbol','Entrez ID','ENSEMBL Gene ID','Probe Sequence']
probes=list(it);w.close();assert len(probes)==22537
lookup=defaultdict(list);left=defaultdict(set);right=defaultdict(set);complement=bytes.maketrans(b'ACGT',b'TGCA')
for i,row in enumerate(probes):
    seq=row[4].encode();assert len(seq)==50
    for sequence,orientation in [(seq,'forward'),(seq.translate(complement)[::-1],'reverse')]:
        lookup[sequence].append((i,orientation));left[sequence[:25]].add(i);right[sequence[-25:]].add(i)
runs=list(csv.DictReader(RUNS.open(),delimiter='\t'));assert len(runs)==12
source_gate=json.loads((P/'TEMPO-SOURCE-GATE.json').read_text());assert len({r['sample_alias'] for r in runs})==12
receipts=[];vectors={}
for run in sorted(runs,key=lambda r:r['sample_alias']):
    sample=run['sample_alias'];url='https://'+run['fastq_ftp'];counts=np.zeros(len(probes),dtype=np.int64)
    receipt={'sample':sample,'run':run['run_accession'],'biosample':run['sample_accession'],'url':url,'utc_start':timestamp(),
             'expected_bytes':int(run['fastq_bytes']),'expected_md5':run['fastq_md5'],'FASTQ_retained_bytes':0,'complete':False}
    total=0;classes=Counter();lengths=Counter();orientations=Counter();adapter_hits=0;hr=None
    try:
        with urllib.request.urlopen(url,timeout=45) as response:
            receipt.update({'HTTP_status':response.status,'final_url':response.url,'content_type':response.headers.get('Content-Type')})
            hr=HashReader(response)
            with gzip.GzipFile(fileobj=hr) as z:
                remainder=b''
                while True:
                    chunk=z.read(8*1024*1024)
                    if not chunk:break
                    lines=(remainder+chunk).split(b'\n');n=((len(lines)-1)//4)*4;remainder=b'\n'.join(lines[n:])
                    assert all(v.startswith(b'@') for v in lines[:n:4])
                    assert all(v.startswith(b'+') for v in lines[2:n:4])
                    seqs=lines[1:n:4];quals=lines[3:n:4];assert all(len(s)==len(q) for s,q in zip(seqs,quals))
                    total+=len(seqs)
                    for seq,number in Counter(seqs).items():
                        lengths[len(seq)]+=number;hit=lookup.get(seq,[])
                        if len(hit)==1:
                            i,ori=hit[0];counts[i]+=number;orientations[ori]+=number;classes['unique_full_probe']+=number
                        elif hit:classes['ambiguous_full_probe']+=number
                        else:
                            L=left.get(seq[:25],set());Q=right.get(seq[-25:],set())
                            if L and Q:classes['different_half_probe_candidates']+=number
                            elif L or Q:classes['one_exact_half']+=number
                            else:classes['neither_exact_half']+=number
                            if b'AGATCGGAAGAGC' in seq:adapter_hits+=number
                assert not remainder,repr(remainder[:80])
        receipt.update({'compressed_bytes':hr.bytes,'compressed_md5':hr.md5.hexdigest(),'compressed_sha256':hr.sha.hexdigest()})
        assert hr.bytes==receipt['expected_bytes'] and hr.md5.hexdigest()==receipt['expected_md5']
        assert sum(classes.values())==total and counts.sum()==classes['unique_full_probe']
        assert lengths=={50:total}
        np.savez_compressed(P/('COUNT-'+sample+'.npz'),counts=counts)
        vectors[sample]=counts
        receipt.update({'complete':True,'count_output':'COUNT-'+sample+'.npz','count_sha256':hashlib.sha256((P/('COUNT-'+sample+'.npz')).read_bytes()).hexdigest()})
    except Exception as e:
        receipt['error']=str(e)
        if hr:receipt.update({'compressed_bytes':hr.bytes,'compressed_md5_partial':hr.md5.hexdigest(),'compressed_sha256_partial':hr.sha.hexdigest()})
    receipt.update({'utc_finish':timestamp(),'reads':total,'classes':dict(classes),'lengths':dict(lengths),'orientation':dict(orientations),
                    'adapter_pattern_hits_among_unassigned':adapter_hits,'elapsed_stage_seconds':time.monotonic()-START})
    receipts.append(receipt);write('COMPLETE-TEMPO-SOURCE-RECEIPTS.json',receipts)
    print(json.dumps({'sample':sample,'complete':receipt['complete'],'reads':total,'assigned_fraction':classes['unique_full_probe']/total if total else None,'elapsed_stage_seconds':time.monotonic()-START,'error':receipt.get('error')}),flush=True)
    if not receipt['complete']:break

if len(vectors)!=12:
    write('TEMPO-CALIBRATION.json',{'utc':timestamp(),'all12_complete':False,'biological_interpretation_allowed':False,
                                  'decision':'All12remainpending accessiblecompleteanalysis; incomplete stage doesnot invalidateassay','completed_samples':list(vectors)})
    raise SystemExit(2)

# Source-control calibration is prespecified; target panel masked from fitting.
w=openpyxl.load_workbook(FILTERED,read_only=True,data_only=True);it=w.active.iter_rows(values_only=True);head=next(it);order=list(head[1:]);published={row[0]:np.array(row[1:],float) for row in it};w.close()
assert len(published)==9500 and set(order)==set(vectors)
genes=defaultdict(list)
for i,row in enumerate(probes):genes[row[1]].append(i)
gene_counts={g:np.array([int(vectors[s][inds].sum()) for s in order]) for g,inds in genes.items()}
depth=np.array([vectors[s].sum() for s in order],float)
logs={g:np.log2(v/depth*1e6+.5) for g,v in gene_counts.items()}
masked=set(sum(json.loads((P/'PLAN.json').read_text())['fixed_panels'].values(),[]))
available=sorted(set(published)&set(logs)-masked);assert len(available)>9000
perlib=[]
for j,sample in enumerate(order):
    pvals=np.array([published[g][j] for g in available]);cvals=np.array([logs[g][j] for g in available])
    perlib.append({'sample':sample,'control_genes':len(available),'Spearman_within_library':float(spearmanr(pvals,cvals).statistic),
                   'control_unassigned_zero_gene_counts':sum(gene_counts[g][j]==0 for g in available)})
variance=np.array([np.var(published[g],ddof=1) for g in available]);cut=np.quantile(variance,.75)
variable=[g for g,v in zip(available,variance) if v>=cut]
correlations=[float(spearmanr(published[g],logs[g]).statistic) for g in variable if np.ptp(logs[g])>0]
adequate=all(x['Spearman_within_library']>=.90 for x in perlib) and float(np.median(correlations))>=.80
out={'utc':timestamp(),'all12_complete':True,'actual_control_genes':len(available),'masked_target_genes':sorted(masked),'per_library':perlib,
     'published_top_variance_control_genes':len(variable),'nonconstant_control_gene_correlations':len(correlations),
     'median_crosssample_Spearman':float(np.median(correlations)),'calibration_passed_frozen_benchmarks':adequate,
     'biological_interpretation_allowed':adequate,'thresholds':'Eachlibrarywithin-geneSpearman>=.90;medianpublished-variablegenecrosssampleSpearman>=.80. Estimatorallocation benchmark, notassayvalidity.',
     'normalization':'Unique-assignedprobePCRreads summedpergene andCPM; log2(CPM+.5). PublishedUQ/global/batchprocessingcancreate differences, no causal inference fromfailedmapping.',
     'elapsed_stage_seconds':time.monotonic()-START}
write('TEMPO-CALIBRATION.json',out)
if adequate:
    target={g:{'probe_count':len(genes[g]),'raw_gene_counts':list(map(int,gene_counts[g])),'sum_probe_log2_CPMplus05':list(map(float,logs[g])),
               'mean_probe_log2_CPMplus05':list(map(float,np.log2(gene_counts[g]/len(genes[g])/depth*1e6+.5)))} for g in sorted(masked)}
    write('TEMPO-FIXED-GENE-OBSERVATIONS.json',{'utc':timestamp(),'sample_order':order,'genes':target,'scope':'PCRprobe counts andsameassaynormalizedmeasurements; notprotein/localization/dependency/outcome','all12_validated_estimator':True})
print(json.dumps({'calibration_passed':adequate,'median_crosssample_Spearman':out['median_crosssample_Spearman'],'perlib_range':[min(r['Spearman_within_library'] for r in perlib),max(r['Spearman_within_library'] for r in perlib)],'elapsed_stage_seconds':time.monotonic()-START}),flush=True)
