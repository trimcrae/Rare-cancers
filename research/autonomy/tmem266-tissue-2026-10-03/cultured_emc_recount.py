"""Published culture pilot; two technical runs, one biological sample; no spatial inference."""
import urllib.request as U,gzip,csv,io,re,json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent
PREFIX='https://duffel.rail.bio/recount3/human/'
receipts=[]
def get(path):
 x=U.urlopen(PREFIX+path,timeout=45).read()
 receipts.append({'url':PREFIX+path,'bytes':len(x),'sha256':hashlib.sha256(x).hexdigest()})
 return gzip.decompress(x).decode()
a=get('annotations/gene_sums/human.gene_sums.G026.gtf.gz')
c=get('data_sources/sra/gene_sums/67/SRP073267/sra.gene_sums.SRP073267.G026.gz')
q=get('data_sources/sra/metadata/67/SRP073267/sra.recount_qc.SRP073267.MD.gz')
runs=['SRR3380704','SRR3380705']
wanted={'TMEM266','ACTB','RPLP0','VIM','NR4A3','ACTA1','CKM','MYH1','MYH2','MYH7'};ann={}
for line in a.splitlines():
 if line.startswith('#'):continue
 f=line.split('\t');d=dict(re.findall(r'(\w+) "([^"]*)"',f[8]))
 if d.get('gene_name') in wanted:ann[d['gene_id']]={'name':d['gene_name'],'gtf':line}
qc={v['external_id']:v for v in csv.DictReader(io.StringIO(q),delimiter='\t')}
rows=csv.DictReader((line for line in c.splitlines() if not line.startswith('#')),delimiter='\t')
results={};n=0
for x in rows:
 n+=1
 if x['gene_id'] in ann:
  name=ann[x['gene_id']]['name'];assert name not in results
  results[name]={'gene_id':x['gene_id'],'annotation':ann[x['gene_id']],'runs':{r:{'coverage_bp_sum':int(x[r]),'auc_all_reads_all_bases':float(qc[r]['bc_auc.all_reads_all_bases']),'coverage_scaled_to_40M_AUC':int(x[r])*4e7/float(qc[r]['bc_auc.all_reads_all_bases'])} for r in runs}}
assert set(results)==wanted and n==63856
assert [results['TMEM266']['runs'][r]['coverage_bp_sum'] for r in runs]==[1333,1694]
source='https://raw.githubusercontent.com/LieberInstitute/recount3/master/R/transform_counts.R'
formula=U.urlopen(source,timeout=45).read()
receipts.append({'url':source,'bytes':len(formula),'sha256':hashlib.sha256(formula).hexdigest()})
out={'source_doi':'10.1186/s12864-016-3161-9','sample':'GSM2113301 / V1-34 / SRX1703825 / SAMN04851121','biological_samples':1,'technical_runs':runs,'gene_features':n,'project_run_columns':len(rows.fieldnames)-1,'receipts':receipts,'genes':results,'qc_selected_runs':{r:qc[r] for r in runs},'normalization':'gene coverage * 40000000 / bc_auc.all_reads_all_bases; a coverage scaling, not TPM, integer reads or transcript molecules. Do not directly compare with original tissue TPM or FFPE log2CPM.','scope':'Low assigned coverage in a published EMC-derived EWSR1::NR4A3-positive culture. No locus breadth, full-length transcript, modern STR identity, purity, protein or intact-tumor cell localization established. Both runs are technical observations of one sample. MYH1/MYH2 signals prevent declaring muscle-program absence.'}
(BASE/'cultured-emc-recount-results.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'gene_features':n,'sample':out['sample'],'TMEM266':results['TMEM266'],'MYH1':results['MYH1']},indent=2))
