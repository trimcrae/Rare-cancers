"""All four authenticated GSE28866 EMC libraries; exact single-symbol normalized peaks."""
import csv,gzip,hashlib,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SRC=ROOT/'raw-cache/GSE28866_normalized.txt.gz'
GENES='SLC6A2 SLC18A1 SLC18A2 SSTR2 INSM1 CHRNA6 TH DBH DDC'.split()
EMC=['EMC_STT5525','EMC_STT5526','EMC_STT5527','EMC_STT5592']
LINKS={'EMC_STT5525':'GSM715466','EMC_STT5526':'GSM715467','EMC_STT5527':'GSM715470','EMC_STT5592':'GSM715472'}
def main():
 h=hashlib.sha256(SRC.read_bytes()).hexdigest();assert h=='11dae64b2d6b6e77846c3f14971fc9a313da86eb52a4b8b83df96c23eedc0ffd'
 peaks={g:[] for g in GENES};amb=[]
 with gzip.open(SRC,'rt') as f:
  reader=csv.DictReader(f,delimiter='\t');fields=reader.fieldnames;sample_cols=fields[7:]
  assert len(sample_cols)==93 and set(EMC).issubset(sample_cols)
  groups={'EMC':EMC,'Myxoid liposarcoma':[c for c in sample_cols if c.startswith('MLPS_')],'Synovial sarcoma':[c for c in sample_cols if c.startswith('SS_')],'normal_context':[c for c in sample_cols if '_normal_' in c]}
  assert list(map(len,groups.values()))==[4,6,3,27]
  for r in reader:
   g=r['gene_symbol']
   if g in GENES:peaks[g].append({'peak':r['peak'],'hg18_coords':r['hg18_coords'],'classification':r['classification'],'gene_id':r['gene_id'],'gene_symbol':g,'peak_exon_gene_symbol':r['peak_exon_gene_symbol'],'values':{c:float(r[c]) for c in sample_cols}})
   elif any(gene in g.replace(';',',').split(',') for gene in GENES):amb.append({k:r[k] for k in fields[:7]})
 results={}
 for g,rr in peaks.items():
  values={c:sum(r['values'][c] for r in rr) for c in sample_cols} if rr else {}
  distributions={}
  for name,cols in groups.items():
   vv=[values[c] for c in cols] if rr else []
   distributions[name]={'n':len(vv),'min':min(vv),'median':statistics.median(vv),'max':max(vv),'values':{c:values[c] for c in cols}} if vv else {'n':0,'status':'no_exact_single_symbol_peak'}
  results[g]={'exact_symbol_peak_count':len(rr),'peaks':rr,'sum_normalized_peak_distributions':distributions}
 out={'source':{'sha256':h,'bytes':SRC.stat().st_size,'url':'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE28nnn/GSE28866/suppl/GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz'},'EMC_library_mapping':LINKS,'groups':groups,'results':results,'ambiguous_annotations':amb,'limits':['3SEQ normalized peak sums differ from TPM and array intensity; no pooled source estimate.','Exact source gene_symbol mapping retained; no coordinate remap/isoform inference.','A missing exact-symbol peak is not expression absence.','Four EMC specimens, unknown full donor overlaps, normal panel unmatched and incomplete organs; no selectivity or clinical-uptake claim.','RNA quantity is not protein, cell location, MIBG uptake or benefit.']}
 ROOT.joinpath('3SEQ-RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({g:{'peaks':v['exact_symbol_peak_count'],'EMC':v['sum_normalized_peak_distributions']['EMC']} for g,v in results.items() if g in GENES[:3]}))
if __name__=='__main__':main()
