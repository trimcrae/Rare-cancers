#!/usr/bin/env python3
import csv,gzip,hashlib,json,math,urllib.request
from collections import Counter,defaultdict
from pathlib import Path
OUT=Path('campaign-output/normal-ligandomics');OUT.mkdir(parents=True,exist_ok=True)
BASE='https://hla-ligand-atlas.org/rel/2020.12/'
QUERIES=['NMPCVQAQY','QQNMPCVQAQY','SYGQQNMPCVQAQYS','DMPCVQAQY']
TARGETS=[('B*15:01','HLA-I'),('A*30:02','HLA-I'),('DRB1*14:01','HLA-II')]
receipts=[]
def download(name):
    url=BASE+name+'.tsv.gz';p=OUT/(name+'.tsv.gz')
    if not p.exists():
        req=urllib.request.Request(url,headers={'User-Agent':'Rare-cancers-public-data-analysis/1'})
        with urllib.request.urlopen(req,timeout=90) as r: payload=r.read(256*1024*1024+1)
        if len(payload)>256*1024*1024: raise RuntimeError('file cap exceeded: '+name)
        p.write_bytes(payload)
    payload=p.read_bytes();receipts.append({'name':name,'url':url,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()})
    def rows():
        opener=gzip.open if payload[:2]==b'\x1f\x8b' else open
        with opener(p,'rt',encoding='utf-8-sig',newline='') as f: yield from csv.DictReader(f,delimiter='\t')
    return rows
readers={n:download(n) for n in ['donors','peptides','sample_hits','aggregated']}
donor_rows=list(readers['donors']());assert donor_rows and {'donor','hla_allele'}<=set(donor_rows[0]),'unexpected donor columns'
donor_alleles=defaultdict(set)
for r in donor_rows: donor_alleles[r['donor']].add(r['hla_allele'].removeprefix('HLA-'))
donors=sorted(donor_alleles);di={d:i for i,d in enumerate(donors)}
all_alleles=sorted(set().union(*donor_alleles.values()));carriers={a:sum(1<<di[d] for d in donors if a in donor_alleles[d]) for a in all_alleles}
peptides={};pep_headers=None
for r in readers['peptides']():
    if pep_headers is None: pep_headers=list(r)
    assert {'peptide_sequence_id','peptide_sequence'}<=set(r)
    k=r['peptide_sequence_id'];s=r['peptide_sequence']
    if k in peptides and peptides[k]!=s: raise AssertionError('conflicting sequence ID')
    peptides[k]=s
qid={k:s for k,s in peptides.items() if s in QUERIES};flags=defaultdict(set);query_aggregate=[];aggregate_n=0;agg_headers=None
for r in readers['aggregated']():
    aggregate_n+=1
    if agg_headers is None: agg_headers=list(r)
    assert {'peptide_sequence_id','peptide_sequence','donor_alleles','hla_class','tissues'}<=set(r)
    k=r['peptide_sequence_id']
    if k in peptides: assert r['peptide_sequence']==peptides[k]
    for item in r['donor_alleles'].split(','):
        if item.startswith('s/'): flags[item[2:].removeprefix('HLA-')].add(k)
    if r['peptide_sequence'] in QUERIES: query_aggregate.append(r)
presence=defaultdict(dict);tissue_presence=defaultdict(dict);units=set();query_hits=[];sh_headers=None;class_counts=Counter();missing_pep=0;sh_n=0
def classes(c):
    if c=='HLA-I': return ['HLA-I']
    if c=='HLA-II': return ['HLA-II']
    if c=='HLA-I+II': return ['HLA-I','HLA-II']
    raise AssertionError('unexpected HLA class '+repr(c))
for r in readers['sample_hits']():
    sh_n+=1
    if sh_headers is None: sh_headers=list(r)
    assert {'peptide_sequence_id','donor','tissue','hla_class'}<=set(r)
    k,d,t=r['peptide_sequence_id'],r['donor'],r['tissue'];assert d in di,'untyped donor'
    if k not in peptides: missing_pep+=1
    bit=1<<di[d]
    for c in classes(r['hla_class']):
        class_counts[c]+=1;units.add((d,t,c));presence[c][k]=presence[c].get(k,0)|bit
        tp=tissue_presence[(c,t)];tp[k]=tp.get(k,0)|bit
    if k in qid: query_hits.append({**r,'peptide_sequence':qid[k]})
assert missing_pep==0,'sample_hits sequences missing from peptides'
def decode(mask): return [d for d in donors if mask&(1<<di[d])]
class_donors={c:set(d for d,t,cl in units if cl==c) for c in presence}
def calibration(a,c,pmap,usable_mask):
    eligible=carriers.get(a,0)&usable_mask;n=eligible.bit_count();masks=[bits&eligible for k,bits in pmap.items() if k in flags.get(a,set()) and bits&eligible];hist=Counter(x.bit_count() for x in masks);curve=[];total=len(masks)
    for m in range(1,n+1):
        denom=math.comb(n,m);miss=sum(count*(math.comb(n-k,m)/denom if n-k>=m else 0.0) for k,count in hist.items());curve.append({'training_donors':m,'expected_fraction_of_full_union_not_detected':miss/total if total else None})
    holdout=[]
    for d in decode(eligible):
        bit=1<<di[d];test=sum(bool(x&bit) for x in masks);lost=sum(x==bit for x in masks);holdout.append({'donor':d,'observed_flagged_peptides':test,'not_detected_in_other_carrier_donors':lost,'fraction':lost/test if test else None})
    den=sum(x['observed_flagged_peptides'] for x in holdout)
    return {'allele':a,'hla_class':c,'eligible_donors':decode(eligible),'n_eligible_donors':n,'n_strong_flagged_peptides_in_carrier_union':total,'donor_breadth_histogram':dict(sorted(hist.items())),'rarefaction':curve,'leave_one_carrier_donor_out':holdout,'pooled_heldout_nonrecovery_fraction':sum(x['not_detected_in_other_carrier_donors'] for x in holdout)/den if den else None}
all_cal=[];tissue_cal=[]
for a in sorted(set(flags)|set(carriers)):
    c='HLA-II' if a.startswith(('DR','DQ','DP')) else 'HLA-I';um=sum(1<<di[d] for d in class_donors.get(c,set()));cal=calibration(a,c,presence.get(c,{}),um)
    if cal['n_eligible_donors']>=2 and cal['n_strong_flagged_peptides_in_carrier_union']: all_cal.append(cal)
    if a in [x[0] for x in TARGETS]:
        for cc,t in sorted(tissue_presence):
            if cc!=c: continue
            tu=sum(1<<di[d] for d,tt,cl in units if tt==t and cl==c);z=calibration(a,c,tissue_presence[(cc,t)],tu)
            if z['n_eligible_donors']>=2 and z['n_strong_flagged_peptides_in_carrier_union']: tissue_cal.append({'tissue':t,**z})
target_results=[]
for a,c in TARGETS:
    carrier_ds=decode(carriers.get(a,0));us=sorted([list(u) for u in units if u[0] in carrier_ds and u[2]==c]);um=sum(1<<di[d] for d in class_donors.get(c,set()));target_results.append({'allele':a,'hla_class':c,'typed_carrier_donors':carrier_ds,'processed_positive_identification_units':us,'n_units':len(us),'calibration':calibration(a,c,presence.get(c,{}),um)})
result={'schema':'benign-hla-coverage-calibration/1','frozen_query_sequences':QUERIES,'source_release':'2020.12','sources':receipts,'headers':{'donors':list(donor_rows[0]),'peptides':pep_headers,'sample_hits':sh_headers,'aggregated':agg_headers},'counts':{'donor_rows':len(donor_rows),'donors':len(donors),'typed_alleles':len(all_alleles),'peptide_ids':len(peptides),'aggregate_rows':aggregate_n,'sample_hit_rows':sh_n,'sample_hit_class_rows':dict(class_counts),'positive_identification_donor_tissue_class_units':len(units),'class_donors':{k:len(v) for k,v in class_donors.items()},'tissues':sorted({t for d,t,c in units})},'queries':[{'sequence':s,'in_processed_peptides':s in peptides.values(),'aggregate_rows':[r for r in query_aggregate if r['peptide_sequence']==s],'sample_hits':[r for r in query_hits if r['peptide_sequence']==s]} for s in QUERIES],'targets':target_results,'all_allele_calibrations':all_cal,'target_tissue_matched_calibrations':tissue_cal,'limits':['sample_hits lists positive identifications, not all attempted assays; empty assays cannot be inferred','s/ allele flags are predictions, not experimentally established restriction','donor/tissue union is not n independent subjects; holdout units are donors','empirical nonrecovery is conditional on peptides seen in the full atlas and does not estimate unseen-peptide prevalence','fusion or isoform sequences omitted from the original search database cannot be treated as measured assay negatives','Original local FDR1% with estimated global peptide FDR4.5%I/3.9%II; singleton nonrecovery includes identification error','no result establishes tumor presentation, immunogenicity, cross-reactivity, or clinical safety']}
(OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n');print('LIGANDOMICS_RESULT_BEGIN');print(json.dumps(result,separators=(',',':')));print('LIGANDOMICS_RESULT_END')
