"""Stream verified shared Hofvander RNA source; no raw input copies or biological threshold."""
from pathlib import Path
import csv,gzip,hashlib,json,statistics,datetime
ROOT=Path(__file__).resolve().parent
SHARED=Path('/workspace/Rare-cancers/research/autonomy')
MATRIX=SHARED/'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz'
META=SHARED/'atlas-hofvander-validation-2026-09-06/metadata-manifest.json'
GENES='SLC6A2 SLC18A1 SLC18A2 SSTR2 INSM1 CHRNA6 TH DBH DDC'.split()
HIST='MPNST|Schwannoma|Neurofibroma|Myxoid liposarcoma|Low-grade fibromyxoid sarcoma|Synovial sarcoma'.split('|')
EMC='Extraskeletal myxoid chondrosarcoma'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def rank(a,b): return sum((x>y)+.5*(x==y) for x in a for y in b)/(len(a)*len(b)) if a and b else None
def summary(a):return {'n':len(a),'min':min(a),'median':statistics.median(a),'max':max(a),'zero_count':sum(x==0 for x in a)} if a else {'n':0}
def main():
 assert sha(MATRIX)=='0255cd254762c6184a782d5b9a90aba6e545b6b2206e28f283455df2de4d62fc'
 a=json.loads(META.read_text());meta={r['sample_id']:r for r in a['samples']}
 vals={};uncompressed=hashlib.sha256();counts={g:0 for g in GENES}
 with gzip.open(MATRIX,'rb') as f:
  first=f.readline();uncompressed.update(first);header=first.decode().rstrip('\n').split('\t')[1:]
  assert len(header)==704 and set(header)==set(meta)
  for line in f:
   uncompressed.update(line);bits=line.decode().rstrip('\n').split('\t');g=bits[0]
   if g in counts:counts[g]+=1;vals[g]=dict(zip(header,map(float,bits[1:])))
 assert uncompressed.hexdigest()=='b0d665d1bd1d96ace1faf66cc5a4d7ab7e41cb487c8f0f61734f102a1f9a7af3'
 assert all(n==1 for n in counts.values())
 emcs=[r for r in meta.values() if r['diagnosis']==EMC]
 rows=[{**r,'RNA_TPM':{g:vals[g][r['sample_id']] for g in GENES}} for r in emcs]
 contrasts={}
 for g in GENES:
  eg=[vals[g][r['sample_id']] for r in emcs if r['eligible']]
  out={'all_EMC':summary([vals[g][r['sample_id']] for r in emcs]),'primary_nonoverlap_EMC':summary(eg),'comparators':{}}
  for d in HIST:
   cr=[r for r in meta.values() if r['diagnosis']==d and r['primary_lesion']]
   cv=[vals[g][r['sample_id']] for r in cr]
   cells=[]
   for year in sorted(set(r['sequencing_year'] for r in emcs+cr)):
    x=[vals[g][r['sample_id']] for r in emcs if r['eligible'] and r['sequencing_year']==year]
    y=[vals[g][r['sample_id']] for r in cr if r['sequencing_year']==year]
    if x or y:cells.append({'year':year,'n_EMC':len(x),'n_comparator':len(y),'rank_order_A':rank(x,y),'pair_count':len(x)*len(y)})
   weight=sum(c['pair_count'] for c in cells)
   out['comparators'][d]={'distribution':summary(cv),'marginal_rank_order_A':rank(eg,cv),'year_matched_rank_order_A':sum(c['rank_order_A']*c['pair_count'] for c in cells if c['pair_count'])/weight if weight else None,'year_cells':cells,'sample_ids':[r['sample_id'] for r in cr]}
  contrasts[g]=out
 out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_files':{'matrix_compressed':{'path':str(MATRIX),'sha256':sha(MATRIX),'bytes':MATRIX.stat().st_size},'matrix_uncompressed':{'sha256':uncompressed.hexdigest(),'bytes':65407718},'metadata':{'path':str(META),'sha256':sha(META)}},'all_EMC_n':len(rows),'primary_nonoverlap_EMC_n':sum(r['eligible'] for r in rows),'rows':rows,'contrasts':contrasts,'limits':['Bulk RNA is not transporter/receptor protein, location, ligand uptake or drug benefit.','Known historical-overlap and one local-recurrence sample retained descriptively, excluded primary nonoverlap comparison; unknown overlap remains.','Source laboratory sample ids are not proof of no unknown donor overlaps.','Assay-year matching does not remove cell-composition or clinical confounding.','No RNA positivity/uptake threshold; zeros are processed transcript estimates, not protein absence.','No cross-cohort pooling or estimated protein levels.']}
 ROOT.joinpath('RNA-RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'all_EMC':len(rows),'primary_nonoverlap':sum(r['eligible'] for r in rows),'primary_genes':{g:contrasts[g]['all_EMC'] for g in GENES[:3]}}))
if __name__=='__main__':main()
