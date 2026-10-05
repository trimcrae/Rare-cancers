#!/usr/bin/env python3
"""All source-compatible additional controls for the unchanged fixed panel."""
from pathlib import Path
from collections import defaultdict
import csv,gzip,hashlib,json,datetime
import numpy as np
from scipy.stats import mannwhitneyu,t
P=Path(__file__).parent
SOURCE=Path('/workspace/emc-r6-fapi_named/research/autonomy/fresh-discovery-2026-10-05-round8/neurosecretory/raw-cache/GSE28866_normalized.txt.gz')
panels=json.loads((P/'PLAN.json').read_text())['fixed_panels'];genes=sorted(set(sum(panels.values(),[])))
peaks=defaultdict(list);conflicts=[]
with gzip.open(SOURCE,'rt') as f:
    reader=csv.DictReader(f,delimiter='\t');samples=reader.fieldnames[7:];assert len(samples)==93
    for row in reader:
        g=row['gene_symbol']
        if g not in genes:continue
        if row['classification']!='coding':continue
        if row['peak_exon_gene_symbol'] and row['peak_exon_gene_symbol']!=g:
            conflicts.append({k:row[k] for k in reader.fieldnames[:7]});continue
        vals=np.array([float(row[s]) for s in samples]);assert np.isfinite(vals).all() and (vals>=0).all()
        peaks[g].append((dict((k,row[k]) for k in reader.fieldnames[:7]),vals))
missing=sorted(set(genes)-set(peaks));obs=[]
sumvals={g:sum(v*v for _,v in rows) for g,rows in peaks.items()}
means={g:v/len(peaks[g]) for g,v in sumvals.items()}
for j,s in enumerate(samples):
    obs.append({'sample':s,'source_condition':'Archived tissue3SEQ; author diagnosis from column labels; no new fusion/donor linkage',
                'fixed_gene_squared_peak_sum':{g:float(v[j]) for g,v in sumvals.items()},
                'fixed_gene_squared_peak_mean':{g:float(v[j]) for g,v in means.items()}})
def effect(a,b):
    u=mannwhitneyu(a,b,alternative='two-sided')
    return {'n_EMC':len(a),'n_comparator_libraries':len(b),'A_probability_EMC_greater':float(u.statistic/(len(a)*len(b))),
            'median_difference':float(np.median(a)-np.median(b)),'two_sided_MWU_p_exploratory':float(u.pvalue)}
contrasts={}
if all(g in sumvals for g in panels['myeloid_recruitment']+panels['T_cell_recruitment']):
    scores={k:np.mean([np.log2(sumvals[g]+1) for g in gs],axis=0) for k,gs in panels.items() if all(g in sumvals for g in gs)}
    balance=scores['myeloid_recruitment']-scores['T_cell_recruitment']
    emc=[i for i,s in enumerate(samples) if s.startswith('EMC_')];closest=[i for i,s in enumerate(samples) if s.startswith(('MLPS_','SS_'))]
    assert len(emc)==4 and len(closest)==9
    contrasts['all4_EMC_vs_fixed6MLPS3SS']=effect(balance[emc],balance[closest])
    tumour_groups=sorted({s.split('_STT')[0] for s in samples[:66]}-{'EMC'})
    assert len(tumour_groups)==16
    for prefix in tumour_groups:
        inds=[i for i,s in enumerate(samples) if s.startswith(prefix+'_')]
        contrasts[prefix]=effect(balance[emc],balance[inds])
    meanbalance=np.mean([np.log2(means[g]+1) for g in panels['myeloid_recruitment']],axis=0)-np.mean([np.log2(means[g]+1) for g in panels['T_cell_recruitment']],axis=0)
    contrasts['mean_per_peak_sensitivity_4_vs9']=effect(meanbalance[emc],meanbalance[closest])
    for j,r in enumerate(obs):
        r['fixed_scores_log2_squared_peak_sum_plus1']={k:float(v[j]) for k,v in scores.items()}
        r['myeloid_minus_T_ligand_score']=float(balance[j]);r['mean_per_peak_ligand_balance']=float(meanbalance[j])
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(SOURCE),'bytes':SOURCE.stat().st_size,'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
     'source_units':'Released square-root depth-normalized3prime peakdensity; squared to source density then summed/meanpercodingpeak. Not TPM/molecules/cell fractions.',
     'method_frozen_in':'AMENDMENT-04-ADDITIONAL-SOURCE-CONTROLS.json','peaks':{g:[p for p,_ in rows] for g,rows in peaks.items()},'conflicting_exon_annotation_peaks':conflicts,
     'missing_suitable_fixed_panel_genes':missing,'all93library_observations':obs,'contrasts':contrasts,
     'decision':'Unchangedsix-ligand contrast evaluated descriptively; full13gene content-adjusted model remains pending without CD3G, no marker substitution' if contrasts else 'Incomplete ligandpanel: no score formed, missingfiltered/codingpeak is not biologicalabsence; partial measurements retained and completecontrast pending',
     'coverage':'All4EMC/all93 matrixlibraries;64tumours plus2technicalduplicate libraries and27unmatchednormalorgans. No duplicate is a newdonor. SixadditionalbreastcelllineRNAseq GEOrecords do notoccur in this93library3SEQmatrix, notEMC.',
     'limits':'Source authorEMC identity, unprovedfusion/cross-studyoverlap; no absolutecrossplatform pooling, gene-dependentpeak capture/length bias, normal-safety, localization, recruitment or outcome inference. Otherhistologies are descriptivecontext, cannotrescuefailedfixedcontrast.'}
(P/'GSE28866-FIXED-PANEL-OBSERVATIONS.json').write_text(json.dumps(out,indent=2)+'\n')

# Post-result complete array comparator diagnostic. All source rows unchanged.
array=json.loads((P/'GSE24369-FIXED-CONTRAST.json').read_text());rows=array['all42source_observations']
emc=[r for r in rows if r['tissue']=='Extraskeletal myxoid chondrosarcoma'];assert len(emc)==6
groups={name:[r for r in rows if r['tissue']==name] for name in ['Low grade fibromyxoid sarcoma','Myxofibrosarcoma','Solitary fibrous tumor','Desmoid fibromatosis tumor','Skeletal muscle']}
# Preserve source labels; accommodate original source's exact LGFMS hyphenation.
groups={name:[r for r in rows if r['tissue']==name] for name in sorted({r['tissue'] for r in rows if r not in emc})}
assert sorted(map(len,groups.values()))==[2,5,6,6,17]
allmalignant=[r for name,rs in groups.items() if name not in ['Desmoid fibromatosis tumor','Skeletal muscle'] for r in rs];assert len(allmalignant)==28
adjusted={}
for name,controls in [('all28_malignant',allmalignant)]+list(groups.items()):
    sel=emc+controls
    X=np.array([[1,int(i<len(emc)),r['scores']['leukocyte'],r['scores']['myeloid_content'],r['scores']['T_cell_content']] for i,r in enumerate(sel)])
    y=np.array([r['balance'] for r in sel]);b=np.linalg.lstsq(X,y,rcond=None)[0];rank=np.linalg.matrix_rank(X);df=len(y)-rank
    se=float(np.sqrt(np.linalg.pinv(X.T@X)[1,1]*np.sum((y-X@b)**2)/df));interval=float(t.ppf(.975,df))*se
    adjusted[name]={'n_EMC':6,'n_controls':len(controls),'EMC_coefficient':float(b[1]),'SE_descriptive':se,'t95CI_descriptive':[float(b[1]-interval),float(b[1]+interval)],'rank':int(rank),'df':int(df),'condition_number':float(np.linalg.cond(X))}
(P/'GSE24369-ADDITIONAL-CONTROL-DIAGNOSTICS.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_sha256':hashlib.sha256((P/'GSE24369-FIXED-CONTRAST.json').read_bytes()).hexdigest(),'purpose':'Explicitlypost-result unchangedfixedpanel diagnostic; all19ancillarysourceobservations andall28malignantcontrols. No favorable selection/confirmation, wide smallgroup uncertainty retained. Pooledmuscle referencesare not twoindependent normaldonors.','adjusted':adjusted,'all42_source_rows_accounted':True},indent=2)+'\n')
print(json.dumps({'GSE28866_missing':missing,'suitable_peaks':{g:len(v) for g,v in peaks.items()},'contrasts':contrasts},indent=2))
print(json.dumps({'array_adjusted_diagnostics':adjusted},indent=2))
