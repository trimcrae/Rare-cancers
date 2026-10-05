"""Fixed-panel source projection; streamed originals, no source duplication."""
import collections, csv, datetime, gzip, hashlib, io, json, pathlib, statistics, zipfile
import numpy as np
from scipy.stats import mannwhitneyu

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path('/workspace/Rare-cancers')
PANEL = ['DLL3', 'SEZ6', 'NCAM1']
EMC = 'Extraskeletal myxoid chondrosarcoma'
HISTS = ['Myxoid liposarcoma', 'Low-grade fibromyxoid sarcoma', 'Synovial sarcoma']
LOCKS = {
 'research/autonomy/atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz': '0255cd254762c6184a782d5b9a90aba6e545b6b2206e28f283455df2de4d62fc',
 'research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz': '98c83c8ca23b7052cf0d4d0099a7bf1af6c3c972276038c3a633e2a5349b3c37',
 'research/autonomy/atlas-original-array-source-2026-09-06/original-source-recovery.zip': '855cf60fd09b7206699f7b11053fafb39ceb93209b75ebeae59326cd2e0f66f4',
 'research/autonomy/atlas-hofvander-validation-2026-09-06/metadata-manifest.json': '2dfb58418fdcbd00970602c1b5b06dde10a2d872e90031032c7427e836449db2',
}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def dump(n,x): (HERE/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def a(x,y):
 return float(np.mean(np.asarray(x)[:,None]>np.asarray(y)[None,:])+0.5*np.mean(np.asarray(x)[:,None]==np.asarray(y)[None,:])) if x and y else None
RNG=np.random.default_rng(20261005)
def contrast(x,y,uncertainty=False):
 out={'n_emc':len(x),'n_comparator':len(y),'median_emc':statistics.median(x),'median_comparator':statistics.median(y),'A':a(x,y)}
 if uncertainty:
  xs=np.asarray(x);ys=np.asarray(y); vals=[]
  for _ in range(10000): vals.append(a(RNG.choice(xs,len(xs),replace=True).tolist(),RNG.choice(ys,len(ys),replace=True).tolist()))
  out['bootstrap_A_95CI']=np.quantile(vals,[.025,.975]).tolist()
  ties=len(set(x+y))!=len(x+y)
  test=mannwhitneyu(x,y,alternative='greater',method='asymptotic' if ties else 'exact')
  out['exploratory_one_sided_p']=float(test.pvalue);out['p_method']='asymptotic_tie_corrected' if ties else 'exact'
 out['emc_deletion_A']=[a(x[:i]+x[i+1:],y) for i in range(len(x))]
 return out
def symbolset(s):
 return {t.split(' // ')[1].strip() for t in s.split(' /// ') if len(t.split(' // '))>=2 and t.split(' // ')[1].strip()!='---'}
def main():
 assert sha(HERE/'PLAN.json')=='7963fe3a984518af1d372dc8a6b00ee7ccf4e588948173e1a535aec8d23473af','changed frozen plan'
 inputs=[]
 for n,h in LOCKS.items():
  p=ROOT/n;assert sha(p)==h,n;inputs.append({'path':n,'bytes':p.stat().st_size,'sha256':h,'storage':'existing shared read-only cache/input; no duplicate'})
 meta=json.loads((ROOT/'research/autonomy/atlas-hofvander-validation-2026-09-06/metadata-manifest.json').read_text())['samples']
 byid={r['sample_id']:r for r in meta};assert len(byid)==704
 hv={}
 with gzip.open(ROOT/list(LOCKS)[0],'rt') as f:
  reader=csv.reader(f,delimiter='\t');header=next(reader)[1:];assert set(header)==set(byid) and len(header)==704
  for r in reader:
   if r[0] in PANEL:
    assert r[0] not in hv;hv[r[0]]=dict(zip(header,map(float,r[1:])))
 assert set(hv)==set(PANEL)
 eligible=[r for r in meta if r['eligible']];primary=[r for r in eligible if r['diagnosis']==EMC];all_emc=[r for r in meta if r['diagnosis']==EMC]
 assert len(primary)==9 and len(all_emc)==13
 projections=[];rna={}
 for g,values in hv.items():
  for r in meta: projections.append({'assay':'Hofvander_TPM','gene':g,'feature':g,'sample_id':r['sample_id'],'diagnosis':r['diagnosis'],'value':values[r['sample_id']],'eligible_primary':r['eligible'],'sequencing_year':r['sequencing_year'],'specimen_exception':r['specimen_exception'],'known_overlap':r['known_overlap']})
  ev=[values[r['sample_id']] for r in primary];cs={}
  for hist in HISTS:
   controls=[r for r in eligible if r['diagnosis']==hist];cv=[values[r['sample_id']] for r in controls]
   v=contrast(ev,cv,True);weighted=0;pairs=0;years=[]
   for year in sorted({r['sequencing_year'] for r in primary}):
    e=[values[r['sample_id']] for r in primary if r['sequencing_year']==year];c=[values[r['sample_id']] for r in controls if r['sequencing_year']==year]
    years.append({'year':year,'n_emc':len(e),'n_comparator':len(c),'A':a(e,c)})
    if e and c:weighted+=a(e,c)*len(e)*len(c);pairs+=len(e)*len(c)
   v['year_cells']=years;v['year_matched_A']=weighted/pairs if pairs else None
   v['all13_emc']=contrast([values[r['sample_id']] for r in all_emc],cv)
   cs[hist]=v
  broad=[]
  for hist in sorted({r['diagnosis'] for r in eligible}):
   vs=[values[r['sample_id']] for r in eligible if r['diagnosis']==hist];broad.append({'diagnosis':hist,'n':len(vs),'median':statistics.median(vs),'range':[min(vs),max(vs)],'A_primary_EMC':a(ev,vs)})
  rna[g]={'primary_emc_n':9,'all_emc_n':13,'primary_emc_values':{r['sample_id']:values[r['sample_id']] for r in primary},'primary_median':statistics.median(ev),'primary_range':[min(ev),max(ev)],'n_ge1':sum(x>=1 for x in ev),'n_ge5':sum(x>=5 for x in ev),'primary_contrasts':cs,'all_eligible_category_context':broad,'IUT_p':max(x['exploratory_one_sided_p'] for x in cs.values())}
 order=sorted(PANEL,key=lambda g:rna[g]['IUT_p']);prior=0
 for i,g in enumerate(order):prior=max(prior,min(1,rna[g]['IUT_p']*(len(PANEL)-i)));rna[g]['Holm3_exploratory_IUT_p']=prior
 zpath=ROOT/list(LOCKS)[2]
 with zipfile.ZipFile(zpath) as z:
  roster=json.loads(z.read('sample-rosters.json'));arows=[r for r in roster if r['gse']=='GSE24369'];orows=[r for r in roster if r['gse']=='GSE4303'];assert len(arows)==42 and len(orows)==16
  probes={g:[] for g in PANEL};annotation=[];ambiguous=[]
  with z.open('GPL6244-original-annotation.tsv') as f:
   for r in csv.DictReader(io.TextIOWrapper(f),delimiter='\t'):
    ss=symbolset(r['gene_assignment'])
    if ss.intersection(PANEL):
     record={'platform':'GPL6244','feature':r['ID'],'symbols':sorted(ss),'gene_assignment':r['gene_assignment'],'total_probes':r['total_probes']}
     (annotation if len(ss)==1 else ambiguous).append(record)
     if len(ss)==1:probes[next(iter(ss))].append(r['ID'])
  rev={p:g for g,ps in probes.items() for p in ps};av={g:{r['gsm']:{} for r in arows} for g in PANEL};sid=None;table=False
  with gzip.open(ROOT/list(LOCKS)[1],'rt') as f:
   for line in f:
    line=line.rstrip('\r\n')
    if line.startswith('^SAMPLE = '):sid=line.split(' = ',1)[1];table=False
    elif line=='!sample_table_begin':table=True;columns=None
    elif line=='!sample_table_end':table=False
    elif table:
     row=line.split('\t')
     if columns is None:columns=row;continue
     feature=row[columns.index('ID_REF')]
     if feature in rev:
      assert feature not in av[rev[feature]][sid];av[rev[feature]][sid][feature]=float(row[columns.index('VALUE')])
  cache=json.loads(z.read('accession-symbol-cache.json'));mapping={}
  for source in cache['_precedence_strongest_first']:
   for acc,sym in cache['by_source'][source].items():mapping.setdefault(acc,sym)
  oldprobes={g:[] for g in PANEL};oldmaps=[]
  with z.open('GPL3290-original-annotation.tsv') as f:
   for r in csv.DictReader(io.TextIOWrapper(f),delimiter='\t'):
    accs=[x for x in r['GB_LIST'].replace(';',',').split(',') if x];ss={mapping[x] for x in accs if x in mapping}
    if ss.intersection(PANEL):
     oldmaps.append({'feature':r['ID'],'accessions':accs,'cached_symbols':sorted(ss),'unresolved_accessions':[x for x in accs if x not in mapping],'bridge':'legacy accession cache without original lookup responses; provenance-qualified'})
     if len(ss)==1:oldprobes[next(iter(ss))].append(r['ID'])
  orev={p:g for g,ps in oldprobes.items() for p in ps};ov={g:{r['gsm']:{} for r in orows} for g in PANEL}
  with z.open('GSE4303-GPL3290-source-matrix.gz') as raw:
   with gzip.open(raw,'rt') as f:
    table=False
    for line in f:
     line=line.rstrip('\r\n')
     if line=='!series_matrix_table_begin':table=True;cols=None
     elif line=='!series_matrix_table_end':table=False
     elif table:
      row=next(csv.reader([line],delimiter='\t'))
      if cols is None:cols=row[1:];assert set(cols)=={r['gsm'] for r in orows};continue
      if row[0] in orev:
       for sid,v in zip(cols,row[1:]):ov[orev[row[0]]][sid][row[0]]=None if v in ['null','NA',''] else float(v)
  archive_members=[]
  for n in ['GPL6244-original-annotation.tsv','GPL3290-original-annotation.tsv','sample-rosters.json','accession-symbol-cache.json','GSE4303-GPL3290-source-matrix.gz']:
   with z.open(n) as f:
    h=hashlib.sha256()
    for b in iter(lambda:f.read(1<<20),b''):h.update(b)
   archive_members.append({'zip_member':n,'bytes':z.getinfo(n).file_size,'sha256':h.hexdigest(),'storage':'streamed, not extracted'})
  dump('SOURCE-HASHES.json',{'sources':inputs,'streamed_members':archive_members})
 array={};older={}
 def hist_a(r):
  t=r['title'].lower()
  if 'extraskeletal' in t:return EMC
  if 'low-grade' in t:return 'Low-grade fibromyxoid sarcoma'
  if 'myxofibro' in t:return 'Myxofibrosarcoma'
  if 'desmoid' in t:return 'Desmoid'
  if 'solitary' in t:return 'Solitary fibrous tumor'
  if 'muscle' in t:return 'Pooled normal muscle'
  raise ValueError(t)
 for g in PANEL:
  if probes[g]:
   assert all(set(v)==set(probes[g]) for v in av[g].values())
   values={s:statistics.median(v.values()) for s,v in av[g].items()};cs={}
   for hist in ['Low-grade fibromyxoid sarcoma','Myxofibrosarcoma','Desmoid','Solitary fibrous tumor']:
    es=[r['gsm'] for r in arows if hist_a(r)==EMC];controls=[r['gsm'] for r in arows if hist_a(r)==hist]
    cs[hist]=contrast([values[s] for s in es],[values[s] for s in controls],True)
    cs[hist]['per_cluster_A']={p:a([av[g][s][p] for s in es],[av[g][s][p] for s in controls]) for p in probes[g]}
   array[g]={'features':probes[g],'fixed_aggregation':'median of all uniquely assigned source-era clusters per sample','contrasts':cs,'pooled_muscle':{r['gsm']:values[r['gsm']] for r in arows if hist_a(r)=='Pooled normal muscle'}}
  else:array[g]={'features':[],'status':'no uniquely assigned feature recovered; not expression absence'}
  for r in arows:
   for feature,v in av[g][r['gsm']].items():projections.append({'assay':'GSE24369_RMA_log2','gene':g,'feature':feature,'sample_id':r['gsm'],'diagnosis':hist_a(r),'value':v,'eligible_primary':'not defined','sequencing_year':'','specimen_exception':'','known_overlap':'unresolved'})
  older[g]={'features':oldprobes[g],'status':'observed tumor/reference log2 ratios only; mapping provenance-qualified, donor/reference compatibility unresolved','sample_count':16,'emc_conditions':10,'values':ov[g]}
  for r in orows:
   for feature,v in ov[g][r['gsm']].items():projections.append({'assay':'GSE4303_log2_tumor_reference','gene':g,'feature':feature,'sample_id':r['gsm'],'diagnosis':r['title'],'value':v,'eligible_primary':'not established','sequencing_year':'','specimen_exception':'recurrence if STT2528; patient label mismatch STT3714/STT3696 unresolved','known_overlap':'unresolved'})
 dump('ANNOTATION.json',{'GPL6244_unique':annotation,'GPL6244_ambiguous':ambiguous,'GPL3290_qualified':oldmaps})
 dump('RESULTS.json',{'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'RNA':rna,'array':array,'older_array':older,'limitations':['Exploratory; previous screen rows known before this freeze.','No independent donor count across cohorts; known overlaps excluded only in primary RNA.','RNA is not cell localization, accessible surface antigen, protein or dependency.','Normal muscle pools do not show organ safety; older reference ratios are not abundance replication.','Pending other authentic EMC RNA sources block promotion.']})
 with (HERE/'MEASUREMENTS.tsv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=list(projections[0]),delimiter='\t');writer.writeheader();writer.writerows(projections)
 dump('SPECIMEN-ROSTER.json',{'Hofvander':meta,'GSE24369':arows,'GSE4303':orows,'independence':'Distinct assay specimens, not proven independent patients across studies.'})
 for g in PANEL:
  print(g,'RNA median/range',rna[g]['primary_median'],rna[g]['primary_range'],'RNA A/matched',[(h,round(v['A'],3),round(v['year_matched_A'],3)) for h,v in rna[g]['primary_contrasts'].items()],'array A',[(h,round(v['A'],3)) for h,v in array[g].get('contrasts',{}).items()])
if __name__=='__main__':main()
