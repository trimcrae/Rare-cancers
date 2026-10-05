"""Frozen six FDA target genes, all source tissue/array/3SEQ conditions, read-only originals."""
from pathlib import Path
import csv,gzip,hashlib,io,json,statistics,zipfile,datetime
import numpy as np
from scipy.stats import mannwhitneyu
ROOT=Path(__file__).resolve().parent
BASE=Path('/workspace/Rare-cancers')
GENES=['ERBB2','TACSTD2','NECTIN4','FOLR1','F3','MET']
HIST=['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma']
EMC='Extraskeletal myxoid chondrosarcoma'
LOCKS={'research/autonomy/atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz':'0255cd254762c6184a782d5b9a90aba6e545b6b2206e28f283455df2de4d62fc','research/autonomy/atlas-hofvander-validation-2026-09-06/metadata-manifest.json':'2dfb58418fdcbd00970602c1b5b06dde10a2d872e90031032c7427e836449db2','research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz':'98c83c8ca23b7052cf0d4d0099a7bf1af6c3c972276038c3a633e2a5349b3c37','research/autonomy/atlas-original-array-source-2026-09-06/original-source-recovery.zip':'855cf60fd09b7206699f7b11053fafb39ceb93209b75ebeae59326cd2e0f66f4'}
SEQ=ROOT.parent/'neurosecretory/raw-cache/GSE28866_normalized.txt.gz'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def A(x,y):return sum((a>b)+.5*(a==b) for a in x for b in y)/(len(x)*len(y)) if x and y else None
def stats(x):return {'n':len(x),'min':min(x),'median':statistics.median(x),'max':max(x)} if x else {'n':0}
def main():
 assert sha(ROOT/'PLAN-FROZEN.json')=='c00a4970c111998d62342194aff062513b38041cb92eecf523439d585782bbaf'
 assert sha(ROOT/'FDA-UNIVERSE-FROZEN.json')=='bf76dd9b7f85915fe2c2373df05cc9170d295395017353a703e8b2b73a28e572'
 for n,h in LOCKS.items():assert sha(BASE/n)==h,n
 assert sha(SEQ)=='11dae64b2d6b6e77846c3f14971fc9a313da86eb52a4b8b83df96c23eedc0ffd'
 uni=json.loads((ROOT/'FDA-UNIVERSE-FROZEN.json').read_text());ids={g:uni['official_gene_mapping'][g]['gene_id'] for g in GENES}
 aliases={g:set(uni['official_gene_mapping'][g]['aliases']+[g]) for g in GENES}
 # TF is an ambiguous canonicalothergene, blocked absentsourceID support; onlyPVRL4 rescued in symbol-only sources.
 symbol_only={g:{g}|({'PVRL4'} if g=='NECTIN4' else set()) for g in GENES};rev={s:g for g,ss in symbol_only.items() for s in ss}
 meta=json.loads((BASE/'research/autonomy/atlas-hofvander-validation-2026-09-06/metadata-manifest.json').read_text())['samples'];byid={r['sample_id']:r for r in meta};emcs=[r for r in meta if r['diagnosis']==EMC];primary=[r for r in emcs if r['eligible']];assert len(emcs)==13 and len(primary)==9
 vals={};features={}
 with gzip.open(BASE/'research/autonomy/atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz','rt') as f:
  rows=csv.reader(f,delimiter='\t');header=next(rows)[1:];assert len(header)==704 and set(header)==set(byid)
  for row in rows:
   if row[0] in rev:
    g=rev[row[0]];assert g not in vals,(g,'duplicategene/aliasfeatures');vals[g]=dict(zip(header,map(float,row[1:])));features[g]=row[0]
 assert set(vals)==set(GENES)
 projections=[];rna={};rng=np.random.default_rng(20261005)
 for g in GENES:
  ev=[vals[g][r['sample_id']] for r in primary];cs={}
  for hist in HIST:
   cc=[r for r in meta if r['eligible'] and r['diagnosis']==hist];cv=[vals[g][r['sample_id']] for r in cc];years=[];w=0;tot=0
   for yr in sorted(set(r['sequencing_year'] for r in primary)):
    x=[vals[g][r['sample_id']] for r in primary if r['sequencing_year']==yr];y=[vals[g][r['sample_id']] for r in cc if r['sequencing_year']==yr];v=A(x,y);n=len(x)*len(y)
    years.append({'year':yr,'n_EMC':len(x),'n_comparator':len(y),'A':v,'pair_count':n})
    if n:w+=v*n;tot+=n
   x=np.asarray(ev);y=np.asarray(cv);bootstrap=[]
   for _ in range(10000):
    bx=rng.choice(x,len(x),replace=True);by=rng.choice(y,len(y),replace=True);bootstrap.append(float(np.mean(bx[:,None]>by[None,:])+.5*np.mean(bx[:,None]==by[None,:])))
   p=float(mannwhitneyu(ev,cv,alternative='greater',method='asymptotic' if len(set(ev+cv))!=len(ev+cv) else 'exact').pvalue)
   cs[hist]={'comparator_ids':[r['sample_id'] for r in cc],'EMC':stats(ev),'comparator':stats(cv),'A':A(ev,cv),'year_matched_A':w/tot if tot else None,'year_cells':years,'all13_A':A([vals[g][r['sample_id']] for r in emcs],cv),'primary_deletion_A':[A(ev[:i]+ev[i+1:],cv) for i in range(len(ev))],'conditional_bootstrap95':np.quantile(bootstrap,[.025,.975]).tolist(),'exploratory_one_sided_p':p}
  rna[g]={'feature':features[g],'all13_values':{r['sample_id']:vals[g][r['sample_id']] for r in emcs},'primary9_values':{r['sample_id']:vals[g][r['sample_id']] for r in primary},'primary_distribution':stats(ev),'primary_ge1':sum(v>=1 for v in ev),'primary_ge5':sum(v>=5 for v in ev),'primary_contrasts':cs,'IUT_p':max(v['exploratory_one_sided_p'] for v in cs.values()),'all_source_category_context':{d:stats([vals[g][r['sample_id']] for r in meta if r['eligible'] and r['diagnosis']==d]) for d in sorted(set(r['diagnosis'] for r in meta if r['eligible']))}}
 for r in meta:projections.append({'source':'Hofvander_TPM','sample_id':r['sample_id'],'diagnosis':r['diagnosis'],'year':r['sequencing_year'],'primary_subset':r['eligible'],'condition_flag':r['specimen_exception'],'known_overlap':r['known_overlap'],**{g:vals[g][r['sample_id']] for g in GENES}})
 prev=0
 for i,g in enumerate(sorted(GENES,key=lambda g:rna[g]['IUT_p'])):prev=max(prev,min(1,rna[g]['IUT_p']*(6-i)));rna[g]['Holm6_IUT_exploratory_p']=prev
 maps={g:[] for g in GENES};ann=[];amb=[];oldmaps={g:[] for g in GENES}
 zp=BASE/'research/autonomy/atlas-original-array-source-2026-09-06/original-source-recovery.zip'
 with zipfile.ZipFile(zp) as z:
  roster=json.loads(z.read('sample-rosters.json'));ar=[r for r in roster if r['gse']=='GSE24369'];old=[r for r in roster if r['gse']=='GSE4303'];assert len(ar)==42 and len(old)==16
  with io.TextIOWrapper(z.open('GPL6244-original-annotation.tsv')) as f:
   for r in csv.DictReader(f,delimiter='\t'):
    blocks=[b.split(' // ') for b in r['gene_assignment'].split(' /// ')];syms=set(b[1].strip() for b in blocks if len(b)>1);gids=set(b[4].strip() for b in blocks if len(b)>4 and b[4].strip().isdigit());candidates=[g for g in GENES if g in syms or ids[g] in gids or syms&aliases[g]]
    for g in candidates:
     unambiguous=(gids=={ids[g]} and all(s in aliases[g] or s=='---' for s in syms)) or (not gids and syms=={g})
     entry={'gene':g,'probe':r['ID'],'source_symbols':sorted(syms),'source_gene_ids':sorted(gids),'gene_assignment':r['gene_assignment'],'status':'unique_sourcegene' if unambiguous else 'ambiguous_orconflicting'}
     (ann if unambiguous else amb).append(entry)
     if unambiguous:maps[g].append(r['ID'])
  cache=json.loads(z.read('accession-symbol-cache.json'));bridge={}
  for priority in cache['_precedence_strongest_first']:
   for k,v in cache['by_source'][priority].items():bridge.setdefault(k,v)
  with io.TextIOWrapper(z.open('GPL3290-original-annotation.tsv')) as f:
   for r in csv.DictReader(f,delimiter='\t'):
    accessions=[x.strip() for x in r['GB_LIST'].replace(';',',').split(',') if x.strip()];syms=set(bridge[x] for x in accessions if x in bridge)
    candidates=[g for g in GENES if syms&symbol_only[g]]
    for g in candidates:
     if syms<=symbol_only[g]:oldmaps[g].append(r['ID'])
  oldrev={p:g for g,ps in oldmaps.items() for p in ps};ov={g:{r['gsm']:{} for r in old} for g in GENES}
  with z.open('GSE4303-GPL3290-source-matrix.gz') as raw:
   with gzip.open(raw,'rt') as f:
    table=False;cols=None
    for line in f:
     line=line.rstrip('\r\n')
     if line=='!series_matrix_table_begin':table=True;continue
     if line=='!series_matrix_table_end':break
     if table:
      row=next(csv.reader([line],delimiter='\t'))
      if cols is None:cols=row[1:];continue
      if row[0] in oldrev:
       for sid,v in zip(cols,row[1:]):ov[oldrev[row[0]]][sid][row[0]]=float(v) if v not in ['','NA','null'] else None
 pr={p:g for g,ps in maps.items() for p in ps};av={};sid=None;table=False;head=False
 with gzip.open(BASE/'research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz','rt') as f:
  for l in f:
   l=l.rstrip('\r\n')
   if l.startswith('^SAMPLE = '):sid=l.split(' = ')[1];av[sid]={}
   elif l=='!sample_table_begin':table=True;head=True
   elif l=='!sample_table_end':table=False
   elif table:
    if head:head=False;continue
    b=l.split('\t')
    if b[0] in pr:av[sid][b[0]]=float(b[1])
 array={}
 for g in GENES:
  vv={r['gsm']:statistics.median(av[r['gsm']][p] for p in maps[g] if p in av[r['gsm']]) for r in ar if any(p in av[r['gsm']] for p in maps[g])};ecs=[r for r in ar if 'extraskeletal' in r['title'].lower()];assert len(ecs)==6
  contrasts={}
  for d,needle in [('LGFMS','low-grade'),('MFS','myxofibro'),('desmoid','desmoid'),('SFT','solitary'),('muscle_pools','muscle')]:
   cc=[r for r in ar if needle in r['title'].lower()];x=[vv[r['gsm']] for r in ecs if r['gsm'] in vv];y=[vv[r['gsm']] for r in cc if r['gsm'] in vv];contrasts[d]={'EMC':stats(x),'comparator':stats(y),'A':A(x,y),'comparator_ids':[r['gsm'] for r in cc],'per_probe_A':{p:A([av[r['gsm']][p] for r in ecs if p in av[r['gsm']]],[av[r['gsm']][p] for r in cc if p in av[r['gsm']]]) for p in maps[g]}}
  array[g]={'features':maps[g],'all42_sourcevalues':{r['gsm']:{p:av[r['gsm']].get(p) for p in maps[g]} for r in ar},'all6_EMC_ids':[r['gsm'] for r in ecs],'contrasts':contrasts,'missing_gene_read':'unreadable_notabsence' if not maps[g] else None}
  for r in ar:projections.append({'source':'GSE24369_RMA_log2','sample_id':r['gsm'],'diagnosis':r['title'],'year':'','primary_subset':'not defined','condition_flag':'','known_overlap':'unresolved',**{h:statistics.median(av[r['gsm']][p] for p in maps[h] if p in av[r['gsm']]) if any(p in av[r['gsm']] for p in maps[h]) else '' for h in GENES}}) if g==GENES[0] else None
 # All frozen targets in every4EMC3SEQ condition, all exact canonical/PVRL4 annotation peaks.
 peaks={g:[] for g in GENES}
 with gzip.open(SEQ,'rt') as f:
  reader=csv.DictReader(f,delimiter='\t');cols=reader.fieldnames[7:];groups={'EMC':[c for c in cols if c.startswith('EMC_')],'MLPS':[c for c in cols if c.startswith('MLPS_')],'SS':[c for c in cols if c.startswith('SS_')],'unmatchednormal':[c for c in cols if '_normal_' in c]};assert list(map(len,groups.values()))==[4,6,3,27]
  for r in reader:
   if r['gene_symbol'] in rev:
    g=rev[r['gene_symbol']];peaks[g].append({'annotation':{k:r[k] for k in reader.fieldnames[:7]},'values':{c:float(r[c]) for cc in groups.values() for c in cc}})
 seq={}
 for g,rr in peaks.items():
  vv={c:sum(r['values'][c] for r in rr) for cc in groups.values() for c in cc} if rr else {};seq[g]={'all_peaks':rr,'peak_count':len(rr),'group_sums':{d:{c:vv[c] for c in cc} for d,cc in groups.items()} if rr else {},'unreadable_notabsence':not rr}
 decisions={}
 for g in GENES:
  r=rna[g];app=r['primary_distribution']['median']>=5 and r['primary_ge1']>=8;contrast=all(v['A']>=.8 and v['year_matched_A'] is not None and v['year_matched_A']>=.8 for v in r['primary_contrasts'].values());arr=array[g]['contrasts']['LGFMS']['A'];rep=arr is not None and arr>=.8
  decisions[g]={'appreciable_context_pass':app,'all3_marginal_matched_rank_pass':contrast,'array_LGFMS_replication_pass':rep,'RNA_allocation_rule_pass':app and contrast and rep,'not_protein_or_benefit':True}
 out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plan_sha256':sha(ROOT/'PLAN-FROZEN.json'),'panel':GENES,'shared_source_hashes':LOCKS,'RNA':rna,'array':array,'older_array':{'all16source_roster':old,'features':oldmaps,'all_source_values':ov,'units':'tumor/reference_log2_ratios, historical mapping qualified, no abundance or independentdonor validation'},'3SEQ':seq,'allocation':decisions,'limits':['Primary9 onlyknown-overlap-excluded, notgloballyindependentdonors;all13conditionsretained.','RNA/array/3SEQ/culture scales notpooled;RNA notcelllocalization/protein/ADCbenefit.','WholeGene/TF solubleisoform/normaladmixture means clinicaladdress unresolved.','FOLR1highoutliers knownDavis2017;HER2EMC phaseI condition/cMetIHC sourcepending;no novelty/globalcoverage claim.']}
 ROOT.joinpath('RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');ROOT.joinpath('ANNOTATION.json').write_text(json.dumps({'GPL6244_unique':ann,'GPL6244_rejected':amb,'official_gene_ids':ids,'GPL3290_symbol_only_qualified_features':oldmaps},indent=2)+'\n')
 with ROOT.joinpath('ALL-TISSUE-PROJECTIONS.tsv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(projections[0]),delimiter='\t');w.writeheader();w.writerows(projections)
 print(json.dumps({g:{'median':rna[g]['primary_distribution']['median'],'ge1':rna[g]['primary_ge1'],'A':{h:v['A'] for h,v in rna[g]['primary_contrasts'].items()},'array_LGFMS_A':array[g]['contrasts']['LGFMS']['A'],'allocation':decisions[g]} for g in GENES}))
if __name__=='__main__':main()
