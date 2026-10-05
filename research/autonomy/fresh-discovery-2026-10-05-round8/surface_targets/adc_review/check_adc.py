"""Independent frozen ADC packet projection from original read-only input bytes.

Run --peer PATH --freeze NAME [--freeze-sha SHA]. No network or source writes.
The owner script is not imported. Source thresholds remain the frozen plan's.
"""
import argparse, collections, csv, gzip, hashlib, io, json, pathlib, statistics, zipfile
import numpy as np
from scipy.stats import rankdata, mannwhitneyu
HERE=pathlib.Path(__file__).resolve().parent
ROOT=pathlib.Path('/workspace/Rare-cancers')
GENES=['ERBB2','TACSTD2','NECTIN4','FOLR1','F3','MET']
IDS={'ERBB2':'2064','TACSTD2':'4070','NECTIN4':'81607','FOLR1':'2348','F3':'2152','MET':'4233'}
ALIASES={g:g for g in GENES}|{'PVRL4':'NECTIN4'}
EMC='Extraskeletal myxoid chondrosarcoma'
HISTS=['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma']
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def A(x,y):
 if not x or not y:return None
 rank=rankdata(x+y,method='average')
 return float((sum(rank[:len(x)])-len(x)*(len(x)+1)/2)/(len(x)*len(y)))
def eq(x,y,label):
 if isinstance(x,(int,float)) and isinstance(y,(int,float)):assert np.isclose(x,y,rtol=1e-11,atol=1e-12),(label,x,y)
 else:assert x==y,(label,x,y)
def dist(v):return {'n':len(v),'min':min(v),'median':statistics.median(v),'max':max(v)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--peer',type=pathlib.Path,required=True);ap.add_argument('--freeze',default='SCIENCE-FREEZE.json');ap.add_argument('--freeze-sha');args=ap.parse_args();peer=args.peer
 if args.freeze_sha:assert sha(peer/args.freeze)==args.freeze_sha
 freeze=json.loads((peer/args.freeze).read_text());bindings={}
 entries=freeze['files'].items() if isinstance(freeze['files'],dict) else [(r['path'],r) for r in freeze['files']]
 for n,r in entries:
  h=r['sha256'] if isinstance(r,dict) else r
  assert sha(peer/n)==h,n
  if isinstance(r,dict) and 'bytes' in r:assert (peer/n).stat().st_size==r['bytes']
  bindings[n]=h
 result=json.loads((peer/'RESULTS.json').read_text());assert result['panel']==GENES
 assert result['plan_sha256']==sha(peer/'PLAN-FROZEN.json')=='c00a4970c111998d62342194aff062513b38041cb92eecf523439d585782bbaf'
 original={}
 for n,h in result['shared_source_hashes'].items():assert sha(ROOT/n)==h,n;original[n]=h
 meta=json.loads((ROOT/'research/autonomy/atlas-hofvander-validation-2026-09-06/metadata-manifest.json').read_text())['samples'];byid={r['sample_id']:r for r in meta};assert len(byid)==704
 rna={};features={}
 with gzip.open(ROOT/'research/autonomy/atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz','rt') as f:
  reader=csv.reader(f,delimiter='\t');cols=next(reader)[1:];assert len(cols)==704 and set(cols)==set(byid)
  for row in reader:
   if row[0] in ALIASES:
    g=ALIASES[row[0]];assert g not in rna;rna[g]=dict(zip(cols,map(float,row[1:])));features[g]=row[0]
 assert set(rna)==set(GENES)
 ep=[r for r in meta if r['eligible'] and r['diagnosis']==EMC];all_emc=[r for r in meta if r['diagnosis']==EMC];assert len(ep)==9 and len(all_emc)==13
 pvals={};compact={}
 for g in GENES:
  rr=result['RNA'][g];ev=[rna[g][r['sample_id']] for r in ep]
  eq(rr['feature'],features[g],g+'source feature');eq(rr['primary9_values'],{r['sample_id']:rna[g][r['sample_id']] for r in ep},g+'primary9');eq(rr['all13_values'],{r['sample_id']:rna[g][r['sample_id']] for r in all_emc},g+'all13')
  eq(rr['primary_distribution'],dist(ev),g+'distribution');eq(rr['primary_ge1'],sum(v>=1 for v in ev),g+'ge1');eq(rr['primary_ge5'],sum(v>=5 for v in ev),g+'ge5')
  p=[];cc={}
  for hist in HISTS:
   cr=rr['primary_contrasts'][hist];ids=[r['sample_id'] for r in meta if r['eligible'] and r['diagnosis']==hist];cv=[rna[g][s] for s in ids];eq(cr['comparator_ids'],ids,g+hist+'ids');eq(cr['EMC'],dist(ev),g+hist+'emc');eq(cr['comparator'],dist(cv),g+hist+'control');eq(cr['A'],A(ev,cv),g+hist+'A');eq(cr['all13_A'],A([rna[g][r['sample_id']] for r in all_emc],cv),g+hist+'all13')
   for i,dele in enumerate(cr['primary_deletion_A']):eq(dele,A(ev[:i]+ev[i+1:],cv),g+hist+'deletion')
   numer=0;denom=0
   for cell in cr['year_cells']:
    x=[rna[g][r['sample_id']] for r in ep if r['sequencing_year']==cell['year']];y=[rna[g][s] for s in ids if byid[s]['sequencing_year']==cell['year']]
    eq(cell['n_EMC'],len(x),'year EMC');eq(cell['n_comparator'],len(y),'year comp');eq(cell['pair_count'],len(x)*len(y),'year pairs');eq(cell['A'],A(x,y),'year A')
    if x and y:numer+=A(x,y)*len(x)*len(y);denom+=len(x)*len(y)
   eq(cr['year_matched_A'],numer/denom if denom else None,g+hist+'matched')
   pv=float(mannwhitneyu(ev,cv,alternative='greater',method='asymptotic' if len(set(ev+cv))<len(ev)+len(cv) else 'exact').pvalue);eq(pv,cr['exploratory_one_sided_p'],g+hist+'p');p.append(pv)
   lo,hi=cr['conditional_bootstrap95'];assert 0<=lo<=hi<=1
   cc[hist]={'n':len(cv),'A':A(ev,cv),'matched_A':cr['year_matched_A'],'bootstrap95_owner':cr['conditional_bootstrap95']}
  pvals[g]=max(p);eq(rr['IUT_p'],pvals[g],g+'IUT')
  compact[g]={'primary_TPM':dist(ev),'n_ge1':sum(v>=1 for v in ev),'RNA_contrasts':cc}
 order=sorted(GENES,key=lambda g:pvals[g]);prev=0
 for i,g in enumerate(order):prev=max(prev,min(1,pvals[g]*(len(GENES)-i)));eq(result['RNA'][g]['Holm6_IUT_exploratory_p'],prev,g+'Holm6')
 # Every projected RNA condition, including unfavorable source histologies.
 tsv=list(csv.DictReader((peer/'ALL-TISSUE-PROJECTIONS.tsv').open(),delimiter='\t'));rna_rows=[r for r in tsv if r['source']=='Hofvander_TPM'];assert len(rna_rows)==704
 for r in rna_rows:
  eq(r['diagnosis'],byid[r['sample_id']]['diagnosis'],'TSV identity')
  for g in GENES:eq(float(r[g]),rna[g][r['sample_id']],g+'TSV')
 annotation=json.loads((peer/'ANNOTATION.json').read_text());m624=collections.defaultdict(list);m329=collections.defaultdict(list);old_values=collections.defaultdict(dict);zip_path=ROOT/'research/autonomy/atlas-original-array-source-2026-09-06/original-source-recovery.zip'
 with zipfile.ZipFile(zip_path) as z:
  roster=json.loads(z.read('sample-rosters.json'));cache=json.loads(z.read('accession-symbol-cache.json'));bridge={}
  for tier in cache['_precedence_strongest_first']:
   for a,s in cache['by_source'][tier].items():bridge.setdefault(a,s)
  with z.open('GPL6244-original-annotation.tsv') as f:
   for r in csv.DictReader(io.TextIOWrapper(f),delimiter='\t'):
    entries=[a.split(' // ') for a in r['gene_assignment'].split(' /// ')];symbols={ALIASES.get(a[1],a[1]) for a in entries if len(a)>1 and a[1]!='---'};source_ids={a[4] for a in entries if len(a)>4 and a[4]!='---'}
    if len(symbols)==1:
     g=next(iter(symbols))
     if g in GENES and source_ids=={IDS[g]}:m624[g].append(r['ID'])
  for g in GENES:eq(m624[g],result['array'][g]['features'],g+'all6244features')
  with z.open('GPL3290-original-annotation.tsv') as f:
   for r in csv.DictReader(io.TextIOWrapper(f),delimiter='\t'):
    ss={ALIASES.get(bridge[a.strip()],bridge[a.strip()]) for a in r['GB_LIST'].replace(';',',').split(',') if a.strip() in bridge}
    if len(ss)==1 and next(iter(ss)) in GENES:m329[next(iter(ss))].append(r['ID'])
  with z.open('GSE4303-GPL3290-source-matrix.gz') as raw:
   with gzip.open(raw,'rt') as f:
    active=False
    for line in f:
     line=line.rstrip('\r\n')
     if line=='!series_matrix_table_begin':active=True;columns=None
     elif line=='!series_matrix_table_end':active=False
     elif active:
      r=next(csv.reader([line],delimiter='\t'))
      if columns is None:columns=r[1:];continue
      if any(r[0] in ps for ps in m329.values()):old_values[r[0]]={s:None if v in ['null','NA',''] else float(v) for s,v in zip(columns,r[1:])}
 reverse={pr:g for g,prs in m624.items() for pr in prs};array_values=collections.defaultdict(dict)
 with gzip.open(ROOT/'research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz','rt') as f:
  active=False
  for line in f:
   line=line.rstrip('\r\n')
   if line.startswith('^SAMPLE = '):sid=line.split(' = ',1)[1];active=False
   elif line=='!sample_table_begin':active=True;header=None
   elif line=='!sample_table_end':active=False
   elif active:
    r=line.split('\t')
    if header is None:header=r;continue
    if r[0] in reverse:array_values[sid][r[0]]=float(r[header.index('VALUE')])
 ar=[r for r in roster if r['gse']=='GSE24369'];assert len(ar)==42;old_roster=[r for r in roster if r['gse']=='GSE4303'];assert len(old_roster)==16
 emcs=[r['gsm'] for r in ar if r['title'].startswith(EMC)];assert len(emcs)==6
 groups={'LGFMS':'Low-grade fibromyxoid sarcoma','MFS':'Myxofibrosarcoma','desmoid':'Desmoid fibromatosis','SFT':'Solitary fibrous tumor','muscle_pools':'Skeletal muscle pooled RNA'}
 for g in GENES:
  own=result['array'][g];eq(own['all6_EMC_ids'],emcs,g+'6arrayids')
  expected={r['gsm']:{p:array_values[r['gsm']][p] for p in m624[g]} for r in ar};eq(own['all42_sourcevalues'],expected,g+'42rawarray')
  ev=[statistics.median(list(expected[s].values())) for s in emcs]
  for label,cr in own['contrasts'].items():
   ids=cr['comparator_ids'];eq(ids,[r['gsm'] for r in ar if r['title'].startswith(groups[label])],g+label+'sourceids');assert all(s in expected for s in ids);cv=[statistics.median(list(expected[s].values())) for s in ids];eq(cr['A'],A(ev,cv),g+label+'arrayA');eq(cr['EMC'],dist(ev),g+label+'arrayEMC');eq(cr['comparator'],dist(cv),g+label+'arraycomp')
  compact[g]['array_LGFMS_A']=own['contrasts']['LGFMS']['A']
 # All old source features/conditions, including nulls.
 eq(result['older_array']['all16source_roster'],old_roster,'all16oldroster')
 for g in GENES:
  eq(result['older_array']['features'][g],m329[g],g+'all3290features')
  expected={r['gsm']:{pr:old_values[pr][r['gsm']] for pr in m329[g]} for r in old_roster}
  eq(result['older_array']['all_source_values'][g],expected,g+'old16')
 # All four EMC 3SEQ observations and prespecified controls/normal conditions.
 seqpath=peer.parent/'neurosecretory/raw-cache/GSE28866_normalized.txt.gz';assert sha(seqpath)=='11dae64b2d6b6e77846c3f14971fc9a313da86eb52a4b8b83df96c23eedc0ffd';original[str(seqpath)]=sha(seqpath);peaks=collections.defaultdict(list)
 with gzip.open(seqpath,'rt') as f:
  reader=csv.DictReader(f,delimiter='\t');columns=reader.fieldnames[7:];assert len(columns)==93
  for r in reader:
   if r['gene_symbol'] in ALIASES:peaks[ALIASES[r['gene_symbol']]].append(r)
 seq_groups={'EMC':[c for c in columns if c.startswith('EMC_')],'MLPS':[c for c in columns if c.startswith('MLPS_')],'SS':[c for c in columns if c.startswith('SS_')],'unmatchednormal':[c for c in columns if 'normal' in c.lower()]}
 assert {g:len(v) for g,v in seq_groups.items()}=={'EMC':4,'MLPS':6,'SS':3,'unmatchednormal':27}
 seq_selected=set(c for vv in seq_groups.values() for c in vv)
 for g in GENES:
  own=result['3SEQ'][g];eq(own['peak_count'],len(peaks[g]),g+'allpeaks');assert len(own['all_peaks'])==len(peaks[g])
  for s,pj in zip(peaks[g],own['all_peaks']):
   eq(s['peak'],pj['annotation']['peak'],g+'peakid');eq(set(pj['values']),seq_selected,g+'all declared source columns')
   for col,v in pj['values'].items():eq(float(s[col]),v,g+col+'peak')
  for group,rec in own['group_sums'].items():
   if peaks[g]:
    eq(set(rec),set(seq_groups[group]),g+group+'all group conditions')
    for col,v in rec.items():eq(sum(float(s[col]) for s in peaks[g]),v,g+group+'sum')
    if group=='EMC':assert len(rec)==4
  appreciable=compact[g]['primary_TPM']['median']>=5 and compact[g]['n_ge1']>=8
  rank=all(c['A']>=.8 and (c['matched_A'] is None or c['matched_A']>=.8) for c in compact[g]['RNA_contrasts'].values())
  array_pass=compact[g]['array_LGFMS_A']>=.8
  eq(result['allocation'][g]['appreciable_context_pass'],appreciable,g+'appreciable');eq(result['allocation'][g]['all3_marginal_matched_rank_pass'],rank,g+'rankpass');eq(result['allocation'][g]['array_LGFMS_replication_pass'],array_pass,g+'arraypass');eq(result['allocation'][g]['RNA_allocation_rule_pass'],appreciable and rank and array_pass,g+'rule')
  compact[g]['frozen_allocation_pass']=appreciable and rank and array_pass
 out={'schema':'emc-independent-ADC-arithmetic-review/1','peer_freeze':args.freeze,'peer_freeze_sha256':sha(peer/args.freeze),'peer_file_bindings':bindings,'original_input_bindings':original,'source_checked_counts':{'RNA_columns':704,'RNA_EMC_conditions':13,'RNA_primary_known_nonoverlap_rows':9,'array_conditions':42,'array_EMC_conditions':6,'older_array_conditions':16,'older_array_EMC_conditions':10,'3SEQ_source_columns':93,'3SEQ_EMC_conditions':4,'3SEQ_MLPS_controls':6,'3SEQ_SS_controls':3,'3SEQ_unmatched_normal_conditions':27,'genes':6},'results':compact,'arithmetic_status':'passed','uncertainty_scope':'Independently verified all raw values, source identities/annotation, rank-sum A, year weighting, all13/deletion sensitivity, Mann-Whitney/IUT/Holm6 and fixed allocation gates. Owner bootstrap intervals bounds checked; bootstrap draws not independently regenerated in this check. Confidence intervals remain cohort-conditional and donor independence unresolved.','models':'Model final source/readout validation is recorded separately, not implied by this tissue arithmetic check.','value':'No fixed candidate passes the prospectively frozen useful RNA contrast. Neither low expression nor failed specificity establishes absence of accessible protein or ADC benefit. Existing broad-screen/primary published findings limit novelty; failed invented panel alone is not a useful negative paper.','coverage':'Pending/unavailable primary case-linked protein/trial and other public EMC expression sources remain visible; no full-public-EMC completeness or exhaustion claim.'}
 (HERE/'ARITHMETIC-REVIEW.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'arithmetic_status':out['arithmetic_status'],'freeze_sha256':out['peer_freeze_sha256'],'frozen_files':len(bindings),'allocation_passes':sum(r['frozen_allocation_pass'] for r in compact.values())}))
if __name__=='__main__':main()
