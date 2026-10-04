"""Exploratory alternate-cell-origin check, not a purity/localization validation."""
import csv,gzip,json
import numpy as np
from scipy.stats import rankdata,spearmanr
from antigen_pilot import BASE,SOURCE,MANIFEST,EMC,sha
rp=BASE/'round2-surface-replication.json';ar=json.loads(rp.read_text())
genes=sorted(g for g,r in ar['genes'].items() if r.get('allocated'))
markers=['ACTA1','CKM','MYH1','MYH2','MYH7']; vv={}
rows=[r for r in json.loads(MANIFEST.read_text())['samples'] if r['eligible'] and r['diagnosis']==EMC];ss=[r['sample_id'] for r in rows]
with gzip.open(SOURCE/'tpm_matrix.tsv.gz','rt') as f:
    rd=csv.reader(f,delimiter='\t');head=next(rd)[1:]
    for r in rd:
        if r[0] in genes+markers:
            d=dict(zip(head,map(float,r[1:])));vv[r[0]]=np.array([d[s] for s in ss])
missing=sorted(set(markers)-set(vv));present=[g for g in markers if g in vv]
score=np.mean([rankdata(vv[g]) for g in present],axis=0)
correlations={g:{c:float(spearmanr(vv[g],vv[c]).statistic) for c in present} for g in genes}
for g in genes:correlations[g]['muscle_rank_score']=float(spearmanr(vv[g],score).statistic)
pools=[r['sample_id'] for r in ar['array_samples'] if r['unit']=='pooled_normal_RNA']
eids=[r['sample_id'] for r in ar['array_samples'] if r['diagnosis']==EMC]
normal={g:{'normal_muscle_pooled_RNA':{s:r['values'][s] for s in pools},'EMC':{s:r['values'][s] for s in eids}} for g,r in ar['genes'].items() if 'values' in r}
out={'scope':'Exploratory bulk-RNA alternate-cell-source check. No correlation result can demonstrate cell localization or rule out contamination. Array normal controls are pooled muscleRNA; cannot establish population distributions or clinical specificity.','samples':ss,'missing_markers':missing,'source_TPM':{g:dict(zip(ss,v.tolist())) for g,v in vv.items()},'EMC_Spearman':correlations,'array_normal_muscle_context':normal,'input_sha256':{'replication':sha(rp),'matrix':sha(SOURCE/'tpm_matrix.tsv.gz'),'plan':sha(BASE/'ROUND2-MUSCLE-CONTROL-PLAN.txt')}}
(BASE/'round2-muscle-controls.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'missing':missing,'TMEM266':correlations['TMEM266'],'GPR68':correlations['GPR68'],'TMEM266_array':normal['TMEM266']},indent=2))
