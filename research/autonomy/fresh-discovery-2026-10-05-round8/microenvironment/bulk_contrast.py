#!/usr/bin/env python3
"""Fixed ligand-balance contrast, read shared original sources in place."""
from pathlib import Path
import csv, gzip, json, hashlib, datetime
import numpy as np
from scipy.stats import mannwhitneyu, spearmanr

P = Path(__file__).parent
R = Path('/workspace/Rare-cancers/research/autonomy')
MATRIX = R / 'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz'
META = R / 'atlas-hofvander-validation-2026-09-06/metadata-manifest.json'
PANELS = {'myeloid_ligand':['CCL2','CSF1'],
          'T_ligand':['CXCL9','CXCL10','CXCL11','CCL5'],
          'myeloid_content':['LST1','AIF1','FCER1G'],
          'T_content':['CD3D','CD3E','CD3G'], 'leukocyte':['PTPRC']}
GENES = set(sum(PANELS.values(), []))
COMPS = ['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma']
EMC = 'Extraskeletal myxoid chondrosarcoma'


def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()


def effect(a,b):
    u=mannwhitneyu(a,b,alternative='two-sided',method='auto')
    A=float(u.statistic/(len(a)*len(b)))
    return {'n_EMC':len(a),'n_comparator':len(b),
            'probability_EMC_gt_comparator':A,
            'median_EMC':float(np.median(a)), 'median_comparator':float(np.median(b)),
            'median_difference':float(np.median(a)-np.median(b)),
            'two_sided_MWU_p_exploratory':float(u.pvalue)}


meta=json.loads(META.read_text())['samples']
lookup={r['sample_id']:r for r in meta}
data={}
with gzip.open(MATRIX,'rt') as h:
    reader=csv.reader(h,delimiter='\t');header=next(reader)[1:]
    for row in reader:
        if row[0] in GENES:
            assert row[0] not in data, 'duplicated gene symbol; resolve annotation before interpretation'
            data[row[0]]=np.array(list(map(float,row[1:])))
assert GENES == set(data), sorted(GENES-set(data))
assert len(header)==704 and set(header)==set(lookup)
values=np.array([data[g] for g in sorted(GENES)])
assert np.isfinite(values).all() and (values>=0).all()
scores={k:np.mean([np.log2(data[g]+1) for g in genes],axis=0) for k,genes in PANELS.items()}
balance=scores['myeloid_ligand']-scores['T_ligand']
rows=[]
for i,s in enumerate(header):
    m=lookup[s]
    rows.append({'sample':s,'diagnosis':m['deposited_diagnosis'],
                 'patient_group':m['patient_group'], 'sequencing_year':m['sequencing_year'],
                 'specimen_exception':m['specimen_exception'],'known_overlap':m['known_overlap'],
                 'genes_TPM':{g:float(data[g][i]) for g in sorted(GENES)},
                 'scores_log2_TPMplus1':{k:float(v[i]) for k,v in scores.items()},
                 'myeloid_minus_T_ligand_score':float(balance[i])})
emc=[i for i,s in enumerate(header) if lookup[s]['deposited_diagnosis']==EMC]
comp=[i for i,s in enumerate(header) if lookup[s]['deposited_diagnosis'] in COMPS]
assert len(emc)==13 and len({lookup[header[i]]['patient_group'] for i in emc})==13
contrasts={'all13_vs_fixed46':effect(balance[emc],balance[comp])}
for d in COMPS:
    inds=[i for i in comp if lookup[header[i]]['deposited_diagnosis']==d]
    contrasts['vs_'+d]=effect(balance[emc],balance[inds])
for name,inds in [('primary12',[i for i in emc if not lookup[header[i]]['specimen_exception']]),
                  ('unoverlapped_primary9',[i for i in emc if not lookup[header[i]]['specimen_exception'] and not lookup[header[i]]['known_overlap']])]:
    contrasts[name]=effect(balance[inds],balance[comp])
contrasts['all13_vs_fixed46']['leave_one_EMC_out_A']=[effect(balance[[i for i in emc if i!=omit]],balance[comp])['probability_EMC_gt_comparator'] for omit in emc]

selected=emc+comp
X=np.array([[1,int(i in emc),scores['leukocyte'][i],scores['myeloid_content'][i],scores['T_content'][i]] for i in selected])
y=balance[selected]
b=np.linalg.lstsq(X,y,rcond=None)[0]
res=y-X@b
df=len(y)-np.linalg.matrix_rank(X)
cov=(res@res)/df*np.linalg.pinv(X.T@X)
se=float(np.sqrt(cov[1,1]))
adjusted={'method':'OLSdescriptive; fixed globalleukocyte/myeloid/Tcell panels, no causal cell-source attribution',
          'EMC_coefficient':float(b[1]),'standard_error':se,'normal_approx95CI':[float(b[1]-1.96*se),float(b[1]+1.96*se)],
          'N':len(y),'matrix_rank':int(np.linalg.matrix_rank(X)), 'design_condition_number':float(np.linalg.cond(X))}
correlations={k:{'rho':float(spearmanr(balance[emc],v[emc]).statistic),'p_exploratory':float(spearmanr(balance[emc],v[emc]).pvalue)} for k,v in scores.items() if k in ['leukocyte','myeloid_content','T_content']}
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'scope':'One frozen fixed ligand transcript balance; all13sourceEMCsamples and all46fixedclosesthistologycomparators; no gene search/selection',
     'inputs':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'storage':'shared read-only source; not copied'} for p in [MATRIX,META]],
     'panels':PANELS, 'comparators':COMPS,'all704_gene_observations':rows,
     'contrasts':contrasts,'adjusted':adjusted,'withinEMC_content_correlations':correlations,
     'limitations':'Bulk RNA ligand score is neither recruitment nor tumorcell secretion; independentarray/complete12TempOanalysis and publishedprotein/sourcecoverage remain necessary.13 includes oneLR and3knownpriorarrayoverlaps, not all independentexternalvalidation donors.'}
(P/'HOFVANDER-FIXED-CONTRAST.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'contrasts':contrasts,'adjusted':adjusted,'withinEMC_content_correlations':correlations},indent=2))
