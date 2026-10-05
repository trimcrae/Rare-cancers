#!/usr/bin/env python3
"""One dated decisive check of fixed content-adjusted balance, no panel rescue."""
from pathlib import Path
import json, datetime
import numpy as np
P=Path(__file__).parent
rng=np.random.default_rng(28052026)
def analyze(rows,is_emc,score,content,year=None):
    A=np.array([[1,int(is_emc(r))]+content(r) for r in rows],float)
    y=np.array([score(r) for r in rows]);em=np.where(A[:,1]==1)[0];co=np.where(A[:,1]==0)[0]
    beta=np.linalg.lstsq(A,y,rcond=None)[0];boot=[];rankfail=0
    for _ in range(10000):
        inds=np.r_[rng.choice(em,len(em),replace=True),rng.choice(co,len(co),replace=True)]
        if np.linalg.matrix_rank(A[inds])<A.shape[1]:rankfail+=1;continue
        boot.append(float(np.linalg.lstsq(A[inds],y[inds],rcond=None)[0][1]))
    loo=[float(np.linalg.lstsq(np.delete(A,i,axis=0),np.delete(y,i),rcond=None)[0][1]) for i in em]
    out={'N':len(rows),'EMC':len(em),'comparison':len(co),'fixed_content_adjusted_EMC_coefficient':float(beta[1]),
         'stratified_case_bootstrap10000_percentile95CI':list(map(float,np.quantile(boot,[.025,.975]))),
         'bootstrap_rank_failures':rankfail,'leave_one_EMC_out_coefficients':loo,
         'inference':'Case-bootstrap uncertainty, no equivalence or recruitment inference. No patientpooling acrosssources.'}
    if year:
        AY=np.c_[A,[year(r)-2020 for r in rows]]
        out['additional_sequencing_year_EMC_coefficient']=float(np.linalg.lstsq(AY,y,rcond=None)[0][1])
    return out
h=json.loads((P/'HOFVANDER-FIXED-CONTRAST.json').read_text())
rs=[r for r in h['all704_gene_observations'] if r['diagnosis']=='Extraskeletal myxoid chondrosarcoma' or r['diagnosis'] in h['comparators']]
hs=analyze(rs,lambda r:r['diagnosis']=='Extraskeletal myxoid chondrosarcoma',lambda r:r['myeloid_minus_T_ligand_score'],
           lambda r:[r['scores_log2_TPMplus1'][k] for k in ['leukocyte','myeloid_content','T_content']],lambda r:float(r['sequencing_year']))
a=json.loads((P/'GSE24369-FIXED-CONTRAST.json').read_text())
ars=[r for r in a['all42source_observations'] if r['tissue'] in ['Extraskeletal myxoid chondrosarcoma','Low-grade fibromyxoid sarcoma']]
ars_result=analyze(ars,lambda r:r['tissue']=='Extraskeletal myxoid chondrosarcoma',lambda r:r['balance'],
                   lambda r:[r['scores'][k] for k in ['leukocyte','myeloid_content','T_cell_content']])
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plan':'AMENDMENT-02-DECISIVE-VALUE-CHECK.json',
     'Hofvander':hs,'GSE24369':ars_result,'panels_changed':False,'bootstrap_seed':28052026,
     'condition':'Withinarray assay normalizer/probe baseline differs fromTPM. Bothmodelsuseidentical fixedcellcontentgenes, not estimatedcellfractions.'}
(P/'DECISIVE-ROBUSTNESS-RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
