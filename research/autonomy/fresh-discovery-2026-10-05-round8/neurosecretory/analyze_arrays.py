"""Focused original-source array extraction, all EMC rows, exact retained probe annotation."""
from pathlib import Path
import csv,gzip,hashlib,io,json,statistics,zipfile
ROOT=Path(__file__).resolve().parent
BASE=Path('/workspace/Rare-cancers/research/autonomy')
ZIP=BASE/'atlas-original-array-source-2026-09-06/original-source-recovery.zip'
SOFT=BASE/'atlas-primary-provenance-2026-09-06/GSE24369.soft.gz'
GENES='SLC6A2 SLC18A1 SLC18A2 SSTR2 INSM1 CHRNA6 TH DBH DDC'.split()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sumvals(v):return {'n':len(v),'min':min(v),'median':statistics.median(v),'max':max(v)} if v else {'n':0}
def rank(x,y):return sum((a>b)+.5*(a==b) for a in x for b in y)/(len(x)*len(y)) if x and y else None
def main():
 assert sha(ZIP)=='855cf60fd09b7206699f7b11053fafb39ceb93209b75ebeae59326cd2e0f66f4'
 assert sha(SOFT)=='98c83c8ca23b7052cf0d4d0099a7bf1af6c3c972276038c3a633e2a5349b3c37'
 with zipfile.ZipFile(ZIP) as z:
  roster=json.loads(z.read('sample-rosters.json'));maps={'GPL6244':{},'GPL3290':{}};amb=[]
  for name,platform in [('GPL6244-original-annotation.tsv','GPL6244'),('GPL3290-original-annotation.tsv','GPL3290')]:
   if platform=='GPL3290':
    cached=json.loads(z.read('accession-symbol-cache.json'))['by_source'];bridge={}
    for priority in ['remote_lookup','unigene_archive','curated_annotation']:
     bridge.update(cached[priority])
   with io.TextIOWrapper(z.open(name)) as f:
    for r in csv.DictReader(f,delimiter='\t'):
     if platform=='GPL6244':syms=set(x.split(' // ')[1] for x in r['gene_assignment'].split(' /// ') if len(x.split(' // '))>1)
     else:
      syms=set()
      for accession in r.get('GB_LIST','').replace(';',',').split(','):
       v=bridge.get(accession.strip())
       if isinstance(v,str):syms.add(v)
       elif isinstance(v,dict):syms.add(v.get('symbol') or v.get('gene_symbol') or '')
     for g in syms & set(GENES):
      if len(syms-{''})==1:maps[platform].setdefault(g,[]).append(r['ID'])
      else:amb.append({'platform':platform,'probe':r['ID'],'target':g,'symbols':sorted(syms)})
  lookup={probe:g for platform,m in maps.items() for g,probes in m.items() for probe in probes}
  data={};sid=None;in_table=False;head=False
  with gzip.open(SOFT,'rt') as f:
   for line in f:
    line=line.rstrip('\n')
    if line.startswith('^SAMPLE = '):sid=line.split(' = ')[1];data[sid]={}
    elif line=='!sample_table_begin':in_table=True;head=True
    elif line=='!sample_table_end':in_table=False
    elif in_table:
     if head:head=False;continue
     bits=line.split('\t');probe=bits[0]
     if probe in lookup:
      try:data[sid][probe]=float(bits[1])
      except ValueError:pass
  with z.open('GSE4303-GPL3290-source-matrix.gz') as f:
   with gzip.open(f,'rt') as g:
    in_table=False;hdr=None
    for line in g:
     if line.startswith('!series_matrix_table_begin'):in_table=True;continue
     if line.startswith('!series_matrix_table_end'):in_table=False;break
     if in_table:
      bits=next(csv.reader([line],delimiter='\t'))
      if hdr is None:hdr=bits[1:];data.update({k:{} for k in hdr});continue
      if bits[0] in lookup:
       for k,v in zip(hdr,bits[1:]):
        try:data[k][bits[0]]=float(v)
        except ValueError:pass
  result={'source_files':{'ZIP':{'path':str(ZIP),'sha256':sha(ZIP)},'GSE24369':{'path':str(SOFT),'sha256':sha(SOFT)}},'probe_map':maps,'ambiguous_excluded':amb,'datasets':{},'limits':['No arbitrary expression/positivity threshold. Platform values are deposited RMA log2 signals or two-channel ratios, not TPM or uptake.','GPL3290 accession-to-symbol cache provenance reused; not fresh independent annotation.','Gene-specific probe medians summarize only measured probes; unavailable mapping is not transcript absence.','Unknown cross-study donor overlaps prevent a full independence assertion. No pooled source estimate.']}
  for ds,platform in [('GSE24369','GPL6244'),('GSE4303','GPL3290')]:
   rr=[r for r in roster if r['gse']==ds and r['platform']==platform]
   rows=[]
   for r in rr:
    values={g:statistics.median([data.get(r['gsm'],{})[p] for p in probes if p in data.get(r['gsm'],{})]) for g,probes in maps[platform].items() if any(p in data.get(r['gsm'],{}) for p in probes)}
    row={k:r.get(k) for k in ['gsm','title','platform','characteristics_ch1','VALUE_definition']};row.update(values=values,EMC='chondrosarcoma' in r['title'].lower());rows.append(row)
   assert sum(r['EMC'] for r in rows)==(6 if ds=='GSE24369' else 10)
   comp=[r for r in rows if not r['EMC'] and ('fibromyxoid' in r['title'].lower() if ds=='GSE24369' else True)]
   contrasts={}
   for gene in GENES:
    x=[r['values'][gene] for r in rows if r['EMC'] and gene in r['values']];y=[r['values'][gene] for r in comp if gene in r['values']]
    contrasts[gene]={'EMC':sumvals(x),'comparator':sumvals(y),'rank_order_A':rank(x,y),'comparator_definition':'LGFMS all17' if ds=='GSE24369' else 'all6 nonEMC source arms, descriptive heterogeneous context only','probe_count':len(maps[platform].get(gene,[]))}
   result['datasets'][ds]={'all_EMC_conditions':[r for r in rows if r['EMC']],'all_comparator_conditions':comp,'contrasts':contrasts}
  ROOT.joinpath('ARRAY-RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps({ds:{g:v for g,v in a['contrasts'].items() if g in GENES[:3]} for ds,a in result['datasets'].items()}))
if __name__=='__main__':main()
