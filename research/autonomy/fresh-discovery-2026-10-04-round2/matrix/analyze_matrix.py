"""Frozen-panel exploratory ECM transcription pilot; see PLAN.json before results."""
from pathlib import Path
import csv, gzip, json, hashlib, collections
import numpy as np
from scipy.stats import mannwhitneyu, spearmanr

P = Path(__file__).resolve().parent
R = Path('C:/Projects/EMC-Research/research/autonomy')
PLAN = json.loads((P/'PLAN.json').read_text())
M = R/'atlas-hofvander-validation-2026-09-06/metadata-manifest.json'
X = R/'atlas-hofvander-source-2026-09-06/tpm_matrix.tsv.gz'
EMC = 'Extraskeletal myxoid chondrosarcoma'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''):h.update(b)
    return h.hexdigest()

def A(a,b):
    return float(np.mean((a[:,None]>b[None,:])+.5*(a[:,None]==b[None,:])))

def main():
    samples=json.loads(M.read_text())['samples']
    emc=[s for s in samples if s['diagnosis']==EMC]
    primary=[s for s in emc if s['eligible']]
    comparators={h:[s for s in samples if s['diagnosis']==h and s['primary_lesion']] for h in PLAN['primary_comparators']}
    assert len(emc)==13 and len(primary)==9
    values={}
    with gzip.open(X,'rt',encoding='utf-8-sig') as f:
        reader=csv.reader(f,delimiter='\t'); header=next(reader)[1:]
        for row in reader:
            if row[0] not in PLAN['all_extracted_genes']:continue
            assert row[0] not in values
            a=np.array(row[1:],dtype=float)
            assert np.all(np.isfinite(a)) and np.all(a>=0)
            values[row[0]]=dict(zip(header,map(float,a)))
    def v(g, ss):return np.array([values[g][s['sample_id']] for s in ss])
    def compare(g, ss, other):
        a,b=v(g,ss),v(g,other); both=np.r_[a,b]
        mode='exact' if len(set(both))==len(both) else 'asymptotic'
        years=sorted({s['sequencing_year'] for s in ss}&{s['sequencing_year'] for s in other})
        matched=[]
        for y in years:
            aa=[s for s in ss if s['sequencing_year']==y];bb=[s for s in other if s['sequencing_year']==y]
            matched.extend([A(v(g,aa),v(g,bb))]*len(aa))
        return {'n_emc':len(a),'n_comparator':len(b),'A':A(a,b),
                'median_EMC_TPM':float(np.median(a)), 'median_comparator_TPM':float(np.median(b)),
                'log2_median_difference':float(np.median(np.log2(1+a))-np.median(np.log2(1+b))),
                'two_sided_p':float(mannwhitneyu(a,b,alternative='two-sided',method=mode).pvalue),
                'p_method':mode,'same_year_A':float(np.mean(matched)) if matched else None,
                'same_year_EMC_count':len(matched),'shared_years':years,
                'single_EMC_deletion_A':[float(min(A(np.delete(a,i),b) for i in range(len(a)))),float(max(A(np.delete(a,i),b) for i in range(len(a))))]}
    results={}
    for g in PLAN['enzyme_universe']:
        if g not in values:
            results[g]={'missing':True,'intersection_p':1.0};continue
        c={h:compare(g,primary,ss) for h,ss in comparators.items()}
        results[g]={'missing':False,'primary':c,'intersection_p':max(x['two_sided_p'] for x in c.values()),
                    'all12primary':{h:compare(g,[s for s in emc if s['primary_lesion']],ss) for h,ss in comparators.items()},
                    'all13':{h:compare(g,emc,ss) for h,ss in comparators.items()}}
    keys=sorted(results,key=lambda g:results[g]['intersection_p']);n=len(keys)
    qs=np.minimum.accumulate(np.array([results[g]['intersection_p']*n/(i+1) for i,g in enumerate(keys)])[::-1])[::-1]
    for g,q in zip(keys,qs):
        r=results[g];r['BH_q']=min(1.,float(q));r['allocated']=False
        if r['missing']:continue
        c=list(r['primary'].values());up=all(x['A']>=.8 and x['log2_median_difference']>=1 for x in c)
        down=all(x['A']<=.2 and x['log2_median_difference']<=-1 for x in c)
        expressed=all(max(x['median_EMC_TPM'],x['median_comparator_TPM'])>=1 for x in c)
        r['allocated']=bool(q<=.05 and expressed and (up or down))
        r['direction']='higher' if up else 'lower' if down else 'mixed_or_small'
    candidates=[g for g in keys if results[g]['allocated']]
    rng=np.random.default_rng(20261004)
    for g in candidates:
        r=results[g]
        for h,ss in comparators.items():
            a,b=v(g,primary),v(g,ss);boot=[A(rng.choice(a,len(a),replace=True),rng.choice(b,len(b),replace=True)) for _ in range(2000)]
            r['primary'][h]['bootstrap_A95_exploratory']=list(map(float,np.quantile(boot,[.025,.975])))
        r['all13_composition_correlations']={c:{'rho':float(spearmanr(v(g,emc),v(c,emc)).statistic),'n':13} for c in PLAN['prespecified_composition_controls'] if c in values}
    out={'claim_status':'exploratory allocation, not a demonstrated new finding','plan_sha256':sha(P/'PLAN.json'),
         'input_hashes':{str(x):sha(x) for x in (M,X)},'all_EMC_metadata':emc,'primary_EMC_ids':[s['sample_id'] for s in primary],
         'comparator_metadata':comparators,'missing_panel_genes':sorted(set(PLAN['all_extracted_genes'])-set(values)),
         'enzyme_tests':n,'genes':results,'allocated_genes':candidates,'all_panel_values':values,
         'all_source_histology_counts':dict(collections.Counter(s['diagnosis'] for s in samples)),
         'limits':['TPM is bulk RNA, not enzyme activity or GAG measurement','Historical nonoverlap subset is a sensitivity construct, not proof of independence across studies','All13 specimens evaluated; source specimen patient groups do not resolve every possible donor relation','Exploratory allocation and conditional intervals do not establish novelty or correct post-selection uncertainty']}
    (P/'tissue-results.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    with (P/'enzyme-summary.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['gene','q','allocated','direction','EMC_median_TPM','A_MLPS','A_LGFMS','A_MFS'])
        for g in keys:
            z=results[g];c=list(z.get('primary',{}).values());w.writerow([g,z['BH_q'],z['allocated'],z.get('direction'),c[0]['median_EMC_TPM'] if c else None,*[x['A'] for x in c]])
    print(json.dumps({'enzyme_tests':n,'candidates':candidates,'comparators':{h:len(s) for h,s in comparators.items()},'missing':out['missing_panel_genes'],'top_allocation_rows':[{k:results[g].get(k) for k in ('BH_q','direction','allocated')}|{'gene':g} for g in keys[:8]]}))

if __name__=='__main__':main()
