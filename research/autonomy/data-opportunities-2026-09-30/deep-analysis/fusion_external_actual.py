import sys,json,gzip,hashlib,datetime,io
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata
CORE=['SEMA3C','PPARG','ENO3']
NATIVE=['BIRC3','CCND1','CDKN2AIP','COX5A','GLS2','ICAM1','LOXL2','MYH7','NOX1','PDP1','SDHA','SKP2','SMPX','TH','VCAM1','VTN']
GENES=CORE+NATIVE
EMC='Extraskeletal myxoid chondrosarcoma'
PRIMARY=['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma']
CONTEXT=['Myxofibrosarcoma','Dermatofibrosarcoma protuberans']
SEED=20261001
B=2000
NNULL=10000
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def auc(x,y):
    if len(x)==0 or len(y)==0:return None
    z=np.asarray(x)[:,None]-np.asarray(y)[None,:]
    return float(np.mean((z>0)+.5*(z==0)))
def contrast(scores,rows,comparators=PRIMARY):
    em=[i for i,r in enumerate(rows) if r['diagnosis']==EMC];per={}
    for name in comparators:
        co=[i for i,r in enumerate(rows) if r['diagnosis']==name]
        years=sorted({rows[i]['sequencing_year'] for i in em+co});cells=[];placements=[]
        for y in years:
            a=[i for i in em if rows[i]['sequencing_year']==y];b=[i for i in co if rows[i]['sequencing_year']==y]
            cells.append({'year':y,'n_emc':len(a),'n_comparator':len(b),'A':auc(scores[a],scores[b])})
            if b:placements.extend(auc([scores[i]],scores[b]) for i in a)
        per[name]={'n_emc':len(em),'n_comparator':len(co),'marginal':auc(scores[em],scores[co]),'year_matched':float(np.mean(placements)) if placements else None,'matched_n_emc':len(placements),'year_cells':cells}
    out={}
    for k in ['marginal','year_matched']:
        v=[per[q][k] for q in comparators];out[k]=float(np.mean(v)) if all(z is not None for z in v) else None
    out['per_histology']=per
    return out
def boot(scores,rows,rng):
    groups={}
    for i,r in enumerate(rows):
        if r['diagnosis'] in [EMC]+PRIMARY:groups.setdefault((r['diagnosis'],r['sequencing_year']),[]).append(i)
    vals={k:[] for k in ['marginal','year_matched']}
    for _ in range(B):
        ids=[int(i) for g in groups.values() for i in rng.choice(g,size=len(g),replace=True)];c=contrast(scores[ids],[rows[i] for i in ids])
        for k in vals:
            if c[k] is not None:vals[k].append(c[k])
    return {k:np.quantile(v,[.025,.975]).tolist() if v else None for k,v in vals.items()}
def deletions(scores,rows):
    out={}
    for kind,keys in [('EMC_patient',[r['sample_id'] for r in rows if r['diagnosis']==EMC]),('sequencing_year',sorted({r['sequencing_year'] for r in rows if r['diagnosis'] in [EMC]+PRIMARY})),('comparator_histology',PRIMARY)]:
        a=[]
        for key in keys:
            ids=[i for i,r in enumerate(rows) if (r['sample_id']!=key if kind=='EMC_patient' else r['sequencing_year']!=key if kind=='sequencing_year' else r['diagnosis']!=key)]
            comp=[x for x in PRIMARY if x!=key] if kind=='comparator_histology' else PRIMARY
            a.append({'deleted':key,**contrast(scores[ids],[rows[i] for i in ids],comp)})
        out[kind]=a
    return out
def bh(v):
    p=np.asarray(v);order=np.argsort(p);q=np.empty(len(p));q[order]=np.minimum.accumulate((p[order]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1]
    return np.minimum(q,1).tolist()
def run(matpath,metapath,outpath):
    assert h(matpath)=='0255cd254762c6184a782d5b9a90aba6e545b6b2206e28f283455df2de4d62fc'
    raw=gzip.decompress(Path(matpath).read_bytes());assert hashlib.sha256(raw).hexdigest()=='b0d665d1bd1d96ace1faf66cc5a4d7ab7e41cb487c8f0f61734f102a1f9a7af3'
    frame=pd.read_csv(io.BytesIO(raw),sep='\t',index_col=0);assert frame.index.is_unique and frame.columns.is_unique
    mb=Path(metapath).read_bytes();assert hashlib.sha1(b'blob '+str(len(mb)).encode()+b'\x00'+mb).hexdigest()=='2998ce73eaca2e86507fa86dd38d924948d28d0c'
    metadata=json.loads(mb);rows=[r for r in metadata['samples'] if r['eligible']]
    assert len({r['patient_group'] for r in rows})==len(rows)
    assert all(r['sample_id'] in frame.columns for r in rows)
    assert set(GENES).issubset(frame.index),sorted(set(GENES)-set(frame.index))
    V=frame[[r['sample_id'] for r in rows]].to_numpy(dtype=float);assert np.isfinite(V).all() and (V>=0).all()
    assert len([r for r in rows if r['diagnosis']==EMC])==9
    rank=rankdata(V,method='average',axis=0)/len(V);symbols=frame.index.astype(str).tolist();lookup={g:i for i,g in enumerate(symbols)};rng=np.random.default_rng(SEED)
    sets={'pooled_19':GENES,'core_3_descriptive_amended_floor':CORE,'native_16':NATIVE};results={}
    for name,members in sets.items():
        scores=rank[[lookup[g] for g in members]].mean(axis=0)
        results[name]={'membership':members,'directions':['UP']*len(members),'scores':dict(zip([r['sample_id'] for r in rows],map(float,scores))),'primary':contrast(scores,rows),'context':contrast(scores,rows,CONTEXT),'bootstrap_conditional_95':boot(scores,rows,rng),'deletions':deletions(scores,rows),'revised_diagnosis':contrast(scores,[dict(r,diagnosis=r['revised_diagnosis'] or r['diagnosis']) for r in rows])}
        wide={};ei=[i for i,r in enumerate(rows) if r['diagnosis']==EMC]
        for d in sorted({r['diagnosis'] for r in rows}-{EMC}):
            ci=[i for i,r in enumerate(rows) if r['diagnosis']==d];wide[d]={'n':len(ci),'A':auc(scores[ei],scores[ci])}
        results[name]['atlas_specificity_descriptive']=wide
    lv=np.log1p(V);summ=np.c_[np.median(lv,axis=1),np.std(lv,axis=1,ddof=1),np.mean(V>0,axis=1)];scale=np.std(summ,axis=0,ddof=1);scale[scale==0]=1
    blocked=set(GENES+['NR4A1','NR4A2','NR4A3','PLAGL1','SGK1','NDRG2','CALD1']+metadata['panel']+metadata['context_control']);bg=np.asarray([i for i,g in enumerate(symbols) if g not in blocked and np.any(V[i]>0)]);pools={}
    for g in GENES:
        dist=np.sum(((summ[bg]-summ[lookup[g]])/scale)**2,axis=1);pools[g]=bg[np.argsort(dist,kind='stable')[:100]]
    nullsets=[]
    for _ in range(NNULL):
        chosen=[]
        for g in GENES:
            available=pools[g][~np.isin(pools[g],chosen)];assert len(available)>0;chosen.append(int(rng.choice(available)))
        nullsets.append(chosen)
    nidx=np.asarray(nullsets);nullscore=np.empty((NNULL,rank.shape[1]),dtype=float)
    for k,ids in enumerate(nidx):nullscore[k]=rank[ids].mean(axis=0)
    nullvals={k:[] for k in ['marginal','year_matched']}
    for scores in nullscore:
        c=contrast(scores,rows)
        for k in nullvals:nullvals[k].append(c[k])
    nullout={}
    for k,vals in nullvals.items():
        vals=np.asarray(vals,dtype=float);obs=results['pooled_19']['primary'][k]
        nullout[k]={'observed':obs,'null_median':float(np.median(vals)),'null_95':np.quantile(vals,[.025,.975]).tolist(),'upper_tail_empirical_p':float((1+np.sum(vals>=obs))/(NNULL+1)),'fraction_null_below_observed':float(np.mean(vals<obs))}
    def mean_abs_corr(ids):
        cor=np.corrcoef(lv[ids]);u=np.triu_indices(len(ids),1);finite=np.isfinite(cor[u]);return float(np.mean(np.abs(cor[u][finite]))) if finite.any() else None
    realcorr=mean_abs_corr([lookup[g] for g in GENES]);nc=[mean_abs_corr(ids) for ids in nidx[:500]];nc=[q for q in nc if q is not None]
    geneout=[];ei=[i for i,r in enumerate(rows) if r['diagnosis']==EMC]
    for g in CORE:
        score=V[lookup[g]]
        for d in PRIMARY+CONTEXT:
            ci=[i for i,r in enumerate(rows) if r['diagnosis']==d];ids=ei+ci;labels=np.asarray([1]*len(ei)+[0]*len(ci));observed=auc(score[ei],score[ci]);pv=[];years=np.asarray([rows[i]['sequencing_year'] for i in ids])
            for _ in range(2000):
                perm=labels.copy()
                for y in sorted(set(years)):
                    mask=np.where(years==y)[0];perm[mask]=rng.permutation(perm[mask])
                pv.append(auc(score[np.asarray(ids)[perm==1]],score[np.asarray(ids)[perm==0]]))
            geneout.append({'gene':g,'comparator':d,'A':observed,'year_matched':contrast(score,rows,[d])['year_matched'],'n_emc':len(ei),'n_comparator':len(ci),'within_year_label_permutation_p_up':float((1+sum(p>=observed for p in pv))/2001)})
    qs=bh([a['within_year_label_permutation_p_up'] for a in geneout])
    for a,q in zip(geneout,qs):a['BH_q_15_comparisons']=q
    data={'schema':'emc-fusion-external-actual/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_sha256':{'matrix_gzip':h(matpath),'matrix_uncompressed':hashlib.sha256(raw).hexdigest(),'metadata':h(metapath)},'matrix_shape':list(frame.shape),'eligible_patients':len(rows),'eligible_EMC_patients':[r['sample_id'] for r in rows if r['diagnosis']==EMC],'excluded_EMC':[r for r in metadata['samples'] if r['diagnosis']==EMC and not r['eligible']],'scoring':'mean within-patient midrank/number-of-genes; all UP; platform-transfer amendment, not original array probe z score','prior_negative':'Existing pooled A+B candidate set reached 39% and 88% of size-matched thresholds on source platforms; not a validated nineteen-gene fusion signature','sets':results,'matched_gene_null':{'replicates':NNULL,'seed':SEED,'matching':'nearest 100 in standardized diagnosis-blinded logTPM median, logTPM variability, detectable fraction; uniform candidate draw without replacement within set','pool_gene_lists':{g:[symbols[i] for i in p] for g,p in pools.items()},'summaries':nullout,'correlation_not_matched':{'candidate_mean_absolute_correlation':realcorr,'first500_null_95':np.quantile(nc,[.025,.975]).tolist(),'first500_null_median':float(np.median(nc))}},'three_core_gene_secondary_family':geneout,'limitations':['Nine patients and four unique EMCs sharing years with primary histology comparators; bootstrap conditional on small supported cells','Overlap-reduced against known prior cohort, not universally independent','Bulk RNA does not establish fusion binding, regulation, protein, cell localization, dependency or treatment effect','No classifier or cutoff tuning; rank amendment changes original assay scale','Gene-null matching is approximate and does not match gene correlation; empirical significance does not establish disease specificity']}
    Path(outpath).parent.mkdir(parents=True,exist_ok=True);Path(outpath).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    print('EMC_FUSION_RESULT_BEGIN');print(json.dumps(data,separators=(',',':')));print('EMC_FUSION_RESULT_END')
if __name__=='__main__':run(*sys.argv[1:4])
