"""Read-only independent source/arithmetic check of the frozen sibling packet."""
import collections, csv, gzip, hashlib, io, json, pathlib, statistics, zipfile
import numpy as np
import re
import xml.etree.ElementTree as ET
from scipy.stats import rankdata
HERE=pathlib.Path(__file__).resolve().parent
PEER=pathlib.Path('/workspace/emc-r6-fapi_named/research/autonomy/fresh-discovery-2026-10-05-round8/neurosecretory')
ROOT=pathlib.Path('/workspace/Rare-cancers/research/autonomy')
GENES='SLC6A2 SLC18A1 SLC18A2 SSTR2 INSM1 CHRNA6 TH DBH DDC'.split()
EMC='Extraskeletal myxoid chondrosarcoma'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def load(n):return json.loads((PEER/n).read_text())
def A(x,y):
 if not x or not y:return None
 ranks=rankdata(x+y,method='average');return float((sum(ranks[:len(x)])-len(x)*(len(x)+1)/2)/(len(x)*len(y)))
def eq(a,b):assert a==b if isinstance(a,(str,int,list,dict)) else np.isclose(a,b,rtol=1e-12,atol=1e-12),(a,b)
def summary(v):return {'n':len(v),'min':min(v),'median':statistics.median(v),'max':max(v),'zero_count':sum(x==0 for x in v)}
def main():
 assert sha(PEER/'SCIENCE-FREEZE.json')=='3d40abe761af9aa9148db207600c225f3803b9462c67d21cec40c11d9f477fdf'
 freeze=load('SCIENCE-FREEZE.json')
 for n,b in freeze['files'].items():assert sha(PEER/n)==b['sha256'] and (PEER/n).stat().st_size==b['bytes'],n
 rna=load('RNA-RESULTS.json');ar=load('ARRAY-RESULTS.json');seq=load('3SEQ-RESULTS.json');bindings={}
 for r in [rna['source_files']['matrix_compressed'],rna['source_files']['metadata'],ar['source_files']['ZIP'],ar['source_files']['GSE24369']]:
  path=pathlib.Path(r['path']);assert sha(path)==r['sha256'];bindings[str(path)]=r['sha256']
 meta={r['sample_id']:r for r in json.loads((ROOT/'atlas-hofvander-validation-2026-09-06/metadata-manifest.json').read_text())['samples']}
 vals={}
 with gzip.open(ROOT/'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz','rt') as f:
  reader=csv.reader(f,delimiter='\t');cols=next(reader)[1:];assert len(cols)==len(set(cols))==704
  for row in reader:
   if row[0] in GENES:assert row[0] not in vals;vals[row[0]]=dict(zip(cols,map(float,row[1:])))
 assert set(vals)==set(GENES)
 emcs=[r for r in meta.values() if r['diagnosis']==EMC];assert len(emcs)==13 and sum(r['eligible'] for r in emcs)==9
 for row in rna['rows']:
  assert row['sample_id'] in meta and row['diagnosis']==EMC
  for gene,v in row['RNA_TPM'].items():eq(v,vals[gene][row['sample_id']])
 for gene,v in rna['contrasts'].items():
  eq(v['all_EMC'],summary([vals[gene][r['sample_id']] for r in emcs]));ep=[r for r in emcs if r['eligible']];ev=[vals[gene][r['sample_id']] for r in ep]
  eq(v['primary_nonoverlap_EMC'],summary(ev))
  for hist,c in v['comparators'].items():
   ids=[sid for sid,r in meta.items() if r['diagnosis']==hist and r['primary_lesion']];cv=[vals[gene][s] for s in ids]
   eq(c['sample_ids'],ids);eq(c['distribution'],summary(cv));eq(c['marginal_rank_order_A'],A(ev,cv));numer=0;denom=0
   for cell in c['year_cells']:
    x=[vals[gene][r['sample_id']] for r in ep if r['sequencing_year']==cell['year']];y=[vals[gene][sid] for sid in ids if meta[sid]['sequencing_year']==cell['year']]
    av=A(x,y);eq(cell['n_EMC'],len(x));eq(cell['n_comparator'],len(y));eq(cell['pair_count'],len(x)*len(y))
    if av is None:assert cell['rank_order_A'] is None
    else:eq(cell['rank_order_A'],av);numer+=av*len(x)*len(y);denom+=len(x)*len(y)
   eq(c['year_matched_rank_order_A'],numer/denom) if denom else eq(c['year_matched_rank_order_A'],None)
 zipfile_path=ROOT/'atlas-original-array-source-2026-09-06/original-source-recovery.zip';maps={};samples={}
 with zipfile.ZipFile(zipfile_path) as z:
  roster=json.loads(z.read('sample-rosters.json'));bridge={};cache=json.loads(z.read('accession-symbol-cache.json'))
  for tier in cache['_precedence_strongest_first']:
   for acc,symbol in cache['by_source'][tier].items():bridge.setdefault(acc,symbol)
  for platform,n in [('GPL6244','GPL6244-original-annotation.tsv'),('GPL3290','GPL3290-original-annotation.tsv')]:
   m=collections.defaultdict(list)
   with z.open(n) as raw:
    for r in csv.DictReader(io.TextIOWrapper(raw),delimiter='\t'):
     if platform=='GPL6244':symbols={a.split(' // ')[1] for a in r['gene_assignment'].split(' /// ') if len(a.split(' // '))>1}
     else:symbols={bridge[a.strip()] for a in r['GB_LIST'].replace(';',',').split(',') if a.strip() in bridge}
     if len(symbols)==1 and symbols.intersection(GENES):m[next(iter(symbols))].append(r['ID'])
   maps[platform]=dict(m);eq(maps[platform],ar['probe_map'][platform])
  sid=None;table=False;reverse={p:g for g,ps in maps['GPL6244'].items() for p in ps}
  with gzip.open(ROOT/'atlas-primary-provenance-2026-09-06/GSE24369.soft.gz','rt') as f:
   for l in f:
    l=l.rstrip('\r\n')
    if l.startswith('^SAMPLE = '):sid=l.split(' = ',1)[1];samples[sid]={};table=False
    elif l=='!sample_table_begin':table=True;header=None
    elif l=='!sample_table_end':table=False
    elif table:
     row=l.split('\t')
     if header is None:header=row;continue
     if row[0] in reverse:samples[sid][row[0]]=float(row[header.index('VALUE')])
  reverse={p:g for g,ps in maps['GPL3290'].items() for p in ps}
  with z.open('GSE4303-GPL3290-source-matrix.gz') as raw:
   with gzip.open(raw,'rt') as f:
    table=False
    for l in f:
     l=l.rstrip('\r\n')
     if l=='!series_matrix_table_begin':table=True;cols=None
     elif l=='!series_matrix_table_end':table=False
     elif table:
      row=next(csv.reader([l],delimiter='\t'))
      if cols is None:cols=row[1:];samples.update({s:{} for s in cols});continue
      if row[0] in reverse:
       for s,v in zip(cols,row[1:]):
        if v not in ['null','NA','']:samples[s][row[0]]=float(v)
 for ds,rec in ar['datasets'].items():
  platform='GPL6244' if ds=='GSE24369' else 'GPL3290';rr=rec['all_EMC_conditions']+rec['all_comparator_conditions'];assert len(rec['all_EMC_conditions'])==(6 if ds=='GSE24369' else 10)
  for r in rr:
   computed={g:statistics.median([samples[r['gsm']][p] for p in ps if p in samples[r['gsm']]]) for g,ps in maps[platform].items() if any(p in samples[r['gsm']] for p in ps)};eq(r['values'],computed)
  for g,c in rec['contrasts'].items():
   x=[r['values'][g] for r in rec['all_EMC_conditions'] if g in r['values']];y=[r['values'][g] for r in rec['all_comparator_conditions'] if g in r['values']]
   assert c['EMC']['n']==len(x) and c['comparator']['n']==len(y)
   if x and y:eq(c['rank_order_A'],A(x,y))
   else:assert c['rank_order_A'] is None
 seqpath=PEER/'raw-cache/GSE28866_normalized.txt.gz';assert sha(seqpath)==seq['source']['sha256'];bindings[str(seqpath)]=sha(seqpath);peaks=collections.defaultdict(list)
 with gzip.open(seqpath,'rt') as f:
  reader=csv.DictReader(f,delimiter='\t');cols=reader.fieldnames[7:];assert len(cols)==93
  for r in reader:
   if r['gene_symbol'] in GENES:peaks[r['gene_symbol']].append(r)
 for g,v in seq['results'].items():
  assert v['exact_symbol_peak_count']==len(peaks[g]);assert len(v['peaks'])==len(peaks[g])
  for original,projected in zip(peaks[g],v['peaks']):
   eq(projected['peak'],original['peak']);eq(projected['values'],{s:float(original[s]) for s in cols})
  for group,ids in seq['groups'].items():
   if peaks[g]:eq(v['sum_normalized_peak_distributions'][group]['values'],{s:sum(float(r[s]) for r in peaks[g]) for s in ids})
   else:assert v['sum_normalized_peak_distributions'][group]['status']=='no_exact_single_symbol_peak'
 modelzip=ROOT/'tmem266-all-cultures-2026-10-04/archs4-subset.zip';model={};assert sha(modelzip)=='f0bcd17e0c56ec038ea47ee14b7b57700333b46790d2cfb18a555cbf70ea4446'
 with zipfile.ZipFile(modelzip) as z:
  with z.open('matrix.tsv') as f:
   r=csv.reader(io.TextIOWrapper(f),delimiter='\t');cols=next(r)[1:]
   for row in r:
    if row[0] in GENES[:3]:model.setdefault(row[0],[]).append(dict(zip(cols,map(int,row[1:]))))
 context=[]
 for record in load('FOCUSED-SOURCE-EXTRACTS.json'):
  if 'sha256' not in record:continue
  source=record['id'];path=PEER/'raw-cache'/(source+('.xml' if source.startswith('PMC') else '.html'));assert sha(path)==record['sha256']
  if source=='Barresi2025':
   preview=bool(re.search('subscription content',path.read_text(),re.I));assert preview
   context.append({'source':source,'sha256':record['sha256'],'subscription_preview_marker':preview,'status':'Public preview; no detailed assay measurement inferred'})
  else:
   xml=ET.parse(path).getroot();paras=[' '.join(e.itertext()) for e in xml.iter() if e.tag in ['p','table-wrap']]
   pertinent=[t for t in paras if re.search('VMAT2|vesicular monoamine|Nurr1|SLC6A2',t,re.I)]
   context.append({'source':source,'sha256':record['sha256'],'pertinent_paragraph_or_table_count':len(pertinent),'status':'Independent primary-context/source distinctions checked; shared conference/table citation is not an EMC transporter measurement'})
 output={'freeze_sha256':sha(PEER/'SCIENCE-FREEZE.json'),'frozen_files_verified':len(freeze['files']),'source_bindings':bindings,'checks':['All 13 RNA ×9 gene values match raw source, plus 9 primary values and six histology/year comparisons using independent rank-sum formula','All 6/10 EMC array conditions and returned control values/unique probe annotations match original; missing values not zero','All 4 EMC 3SEQ conditions; every retained peak across all 93 source columns exactly matches source; group sums match','9 known-nonoverlap rows are not proven independent donors; RNA/ratios/normalized peaks are distinct assays','Current sources/decisions read only; no retrieval or worker-source mutation'],'additional_model_context_not_in_peer_freeze':{'ARCHS4_shared_sha256':sha(modelzip),'fixed_panel_symbol_rows':model,'limits':'No tissue/protein/uptake inference; USZ23 current transcript annotation pending for this panel. Named authentic model endpoints remain incomplete.'},'arithmetic_status':'passed','scientific_value':'Shelving supported. No transporter uptake/storage, imaging sensitivity or treatment benefit demonstrated. Variable VMAT2 is not a new useful intervention finding; low NET/VMAT1 RNA does not rule out ligand uptake through alternate pathways.','coverage_limit':'Source metadata/full-text gaps and authenticated culture-panel endpoints remain pending; not complete public EMC coverage, no negative-uptake or universal exhaustion claim.','operational_note':'Owner can append bounded accessible model context if useful; original science and shelving decision need not be rescued or relabelled.','primary_context_source_check':context}
 (HERE/'NEUROSECRETORY-INDEPENDENT-REVIEW.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({k:v for k,v in output.items() if k not in ['source_bindings','checks']},indent=2))
if __name__=='__main__':main()
