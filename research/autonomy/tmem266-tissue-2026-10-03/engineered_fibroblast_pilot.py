"""Supporting engineered-model evidence only; no fusion-negative controls."""
import urllib.request,zipfile,io,csv,hashlib,json,statistics
from pathlib import Path
BASE=Path(__file__).resolve().parent
u='https://pmc-oa-opendata.s3.amazonaws.com/PMC11614847.1/DataSheet2.zip'
b=urllib.request.urlopen(u,timeout=45).read();z=zipfile.ZipFile(io.BytesIO(b))
assert hashlib.sha256(b).hexdigest()=='f91e7432900dfce82caa24beb826fdbd7bed37ef934470243aee6823c6ecb383'
raw=z.read('Supplementary_File_2/counts_file..csv');meta=z.read('Supplementary_File_2/metadata_file.csv')
cond={r['Sample']:r['Condition'] for r in csv.DictReader(io.StringIO(meta.decode()),delimiter=';')}
rd=csv.reader(io.StringIO(raw.decode()),delimiter=';');head=next(rd)
tot=[0]*len(head[1:]);targets={};n=0
ids={'ENSG00000169758':'TMEM266','ENSG00000111640':'GAPDH','ENSG00000119508':'NR4A3'}
for r in rd:
 v=list(map(float,r[1:]));n+=1;tot=[a+c for a,c in zip(tot,v)]
 if r[0].split('.')[0] in ids:targets[ids[r[0].split('.')[0]]]=v
assert n==57714 and len(head[1:])==8 and cond['S318']=='TN' and cond['S363']=='EN'
out={'source':u,'source_doi':'10.3389/fgene.2024.1440994','zip_sha256':hashlib.sha256(b).hexdigest(),'counts_sha256':hashlib.sha256(raw).hexdigest(),'metadata_sha256':hashlib.sha256(meta).hexdigest(),'n_gene_rows':n,'samples':[{'sample':s,'condition':cond[s],'library_gene_count_sum':tot[i],**{g:{'raw_count':v[i],'CPM_gene_count_sum':v[i]/tot[i]*1e6} for g,v in targets.items()}} for i,s in enumerate(head[1:])]}
out['summary']={c:{'n':sum(cond[s]==c for s in head[1:]),'TMEM266_nonzero':sum(v>0 for i,v in enumerate(targets['TMEM266']) if cond[head[i+1]]==c),'TMEM266_atleast10':sum(v>=10 for i,v in enumerate(targets['TMEM266']) if cond[head[i+1]]==c),'median_TMEM266_CPM':statistics.median(v/tot[i]*1e6 for i,v in enumerate(targets['TMEM266']) if cond[head[i+1]]==c)} for c in ['EN','TN']}
out['scope']='Oncogene-transformed tBJ/ER fibroblasts engineered with EN/TN, not patient-derived EMC tissue. No fusion-negative control, induction/dependency or localization inference. CPM uses this matrix column sum, not TPM or the FFPE scale.'
(BASE/'engineered-fibroblast-results.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'summary':out['summary'],'samples':[{k:v for k,v in s.items() if k in ['sample','condition','TMEM266']} for s in out['samples']]},indent=2))
