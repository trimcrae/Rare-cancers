"""Post-discovery, predeclared context/sensitivity checks; no independent validation."""
import csv,gzip,json,collections
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from antigen_pilot import BASE,ROOT,SOURCE,MANIFEST,EMC,HIST,auc,sha

def contrast(e,b,er,br):
    years=sorted({r['sequencing_year'] for r in er}&{r['sequencing_year'] for r in br})
    cells=[]
    for y in years:
        a=e[[r['sequencing_year']==y for r in er]];c=b[[r['sequencing_year']==y for r in br]]
        cells.append({'year':y,'ne':len(a),'nc':len(c),'A':auc(a,c)})
    n=sum(c['ne'] for c in cells)
    return {'n_EMC':len(e),'n_comparator':len(b),'A':auc(e,b),'matched_n_EMC':n,'matched_A':sum(c['ne']*c['A'] for c in cells)/n if n else None,'cells':cells}

def main():
    fr=BASE/'round2-surface-hits-frozen.json';rp=BASE/'round2-surface-replication.json'
    genes=sorted(r['gene'] for r in json.loads(fr.read_text())['hits'])
    replicated=sorted(g for g,r in json.loads(rp.read_text())['genes'].items() if r.get('allocated'))
    controls=['PTPRC','LST1','FCER1G','AIF1','COL1A1','COL1A2','DCN','PECAM1','VWF']
    rows=[r for r in json.loads(MANIFEST.read_text())['samples'] if r['eligible']]
    group=collections.defaultdict(list)
    for r in rows:group[r['diagnosis']].append(r)
    group={h:rs for h,rs in group.items() if len(rs)>=5}
    needed=set(genes+controls);vv={}
    with gzip.open(SOURCE/'tpm_matrix.tsv.gz','rt') as f:
        rd=csv.reader(f,delimiter='\t');head=next(rd)[1:]
        for r in rd:
            if r[0] in needed:vv[r[0]]=dict(zip(head,map(float,r[1:])))
    assert set(vv)==needed
    vec=lambda g,rr:np.array([vv[g][r['sample_id']] for r in rr])
    er=group[EMC];context=[];sens={}
    for g in genes:
        e=vec(g,er)
        for h,rr in sorted(group.items()):
            if h==EMC:continue
            c=contrast(e,vec(g,rr),er,rr)
            context.append({'gene':g,'histology':h,'n':len(rr),'median_TPM':float(np.median(vec(g,rr))),**{k:v for k,v in c.items() if k!='cells'}})
    dst=BASE/'round2-surface-context.tsv'
    with dst.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(context[0]),delimiter='\t');w.writeheader();w.writerows(context)
    rng=np.random.default_rng(20261003)
    boot={}
    for h in [EMC]+HIST:
        rr=group[h]; ix=[]
        for y in sorted({r['sequencing_year'] for r in rr}):
            ii=np.array([i for i,r in enumerate(rr) if r['sequencing_year']==y])
            ix.append(rng.choice(ii,size=(2000,len(ii)),replace=True))
        boot[h]=np.concatenate(ix,axis=1)
    for g in replicated:
        e=vec(g,er);r={'EMC_values':{s['sample_id']:vv[g][s['sample_id']] for s in er},'contrasts':{}}
        eb=e[boot[EMC]]
        r['conditional_bootstrap_95_median_TPM']=np.quantile(np.median(eb,axis=1),[.025,.975]).tolist()
        for h in HIST:
            br=group[h];b=vec(g,br);base=contrast(e,b,er,br)
            patient=[];years=[]
            for i,s in enumerate(er):patient.append({'omitted':s['sample_id'],**contrast(np.delete(e,i),b,[v for j,v in enumerate(er) if j!=i],br)})
            for y in sorted({v['sequencing_year'] for v in er+br}):
                ner=[v for v in er if v['sequencing_year']!=y];nbr=[v for v in br if v['sequencing_year']!=y]
                years.append({'omitted':y,**contrast(vec(g,ner),vec(g,nbr),ner,nbr)})
            bb=b[boot[h]];au=((eb[:,:,None]>bb[:,None,:])+.5*(eb[:,:,None]==bb[:,None,:])).mean(axis=(1,2))
            matched=np.zeros(2000);den=0
            ey=np.array([v['sequencing_year'] for v in er])[boot[EMC]];by=np.array([v['sequencing_year'] for v in br])[boot[h]]
            for c in base['cells']:
                a=eb[ey==c['year']].reshape(2000,c['ne']);d=bb[by==c['year']].reshape(2000,c['nc'])
                aa=((a[:,:,None]>d[:,None,:])+.5*(a[:,:,None]==d[:,None,:])).mean(axis=(1,2));matched+=aa*c['ne'];den+=c['ne']
            r['contrasts'][h]={'base':base,'single_EMC_deletions':patient,'year_deletions':years,'conditional_bootstrap_95_A':np.quantile(au,[.025,.975]).tolist(),'conditional_bootstrap_95_matched_A':np.quantile(matched/den,[.025,.975]).tolist()}
        r['EMC_bulk_control_spearman']={c:{'rho':float(spearmanr(e,vec(c,er)).statistic),'p_unadjusted_exploratory':float(spearmanr(e,vec(c,er)).pvalue)} for c in controls}
        sens[g]=r
    out={'scope':'Exploratory checks in reused discovery cohort; not independent evidence. Bootstrap conditional on observed histology/year and cannot expose unobserved overlap or remove batch/confounding. At complete sample separation bootstrap intervals can degenerate at1 and must not be interpreted as certainty. Correlations of9bulk samples cannot identify cell oforigin.','eligible_n':len(rows),'eligible_histologies_ge5':{h:len(rr) for h,rr in sorted(group.items())},'seed':20261003,'bootstrap_replicates':2000,'genes':sens,'hashes':{str(p.relative_to(ROOT)):sha(p) for p in [fr,rp,MANIFEST,SOURCE/'tpm_matrix.tsv.gz',Path(__file__),BASE/'ROUND2-SENSITIVITY-PLAN.txt',dst]}}
    (BASE/'round2-surface-sensitivity.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    focus=['GPR68','ABHD2','TMEM266']
    print(json.dumps({'n':len(rows),'histologies':len(group),'focus':{g:{'median_CI':sens[g]['conditional_bootstrap_95_median_TPM'],'comparisons':{h:{'A_CI':z['conditional_bootstrap_95_A'],'matched_CI':z['conditional_bootstrap_95_matched_A'],'patient_A_min':min(x['A'] for x in z['single_EMC_deletions']),'year_A_min':min(x['A'] for x in z['year_deletions'])} for h,z in sens[g]['contrasts'].items()},'control_rho':{c:z['rho'] for c,z in sens[g]['EMC_bulk_control_spearman'].items()},'context_lowest_A':sorted([r for r in context if r['gene']==g],key=lambda r:r['A'])[:5]} for g in focus}},indent=2))

if __name__=='__main__':main()
