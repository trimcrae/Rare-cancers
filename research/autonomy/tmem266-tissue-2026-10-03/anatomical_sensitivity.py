"""Worker-announced post hoc anatomical restriction, not cell localization."""
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,'.cache/python-deps')
import openpyxl,json,csv,gzip,hashlib
from pathlib import Path
R=Path('research/autonomy');P=R/'tmem266-tissue-2026-10-03'
E='Extraskeletal myxoid chondrosarcoma';H=['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma']
source=R/'atlas-hofvander-source-2026-09-06/ccr-25-3740_supplementary_table_s1_suppts1.xlsx'
s=openpyxl.load_workbook(source,read_only=True,data_only=True).active
sr={r[0].split('_')[0]:r for i,r in enumerate(s.values,1) if 3<=i<=706}
manifest=R/'atlas-hofvander-validation-2026-09-06/metadata-manifest.json'
m=[r for r in json.loads(manifest.read_text())['samples'] if r['eligible'] and r['diagnosis'] in [E]+H]
matrix=R/'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz'
with gzip.open(matrix,'rt') as f:
 rd=csv.reader(f,delimiter='\t');hd=next(rd)[1:]
 for r in rd:
  if r[0]=='TMEM266':v=dict(zip(hd,map(float,r[1:])));break
rows=[]
for r in m:
 raw=sr[r['sample_id']];rows.append({'id':r['sample_id'],'histology':r['diagnosis'],'site':raw[7],'depth':raw[9],'purity':raw[18],'gene_TPM':v[r['sample_id']],'sequencing_year':r['sequencing_year']})
sel=[r for r in rows if r['depth']=='D' and 'thigh' in str(r['site']).lower()]
a=[r['gene_TPM'] for r in sel if r['histology']==E];contrasts={}
for h in H:
 b=[r['gene_TPM'] for r in sel if r['histology']==h]
 contrasts[h]={'n_EMC':len(a),'n_comparator':len(b),'A':sum((x>y)+.5*(x==y) for x in a for y in b)/(len(a)*len(b)) if a and b else None}
out={'scope':'Post hoc anatomical restriction only; actual muscle proportion and malignant cell source unresolved. ASCAT purity is not a histological purity estimate.','all_EMC':[r for r in rows if r['histology']==E],'deep_thigh_cases':sel,'contrasts':contrasts,'input_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,manifest,matrix]}}
(P/'anatomical-sensitivity.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'all_EMC':out['all_EMC'],'contrasts':contrasts}))
