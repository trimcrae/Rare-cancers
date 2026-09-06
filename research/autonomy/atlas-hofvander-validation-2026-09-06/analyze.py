"""Frozen within-source rank analysis. Default command runs synthetic fixtures only."""
from pathlib import Path
import argparse,csv,json,hashlib,datetime,traceback,math
import numpy as np
from metadata import EMC,PRIMARY,CONTEXT,PANEL,sha
BASE=Path(__file__).parent
def dump(p,x): p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def auc(x,y):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    if len(x)==0 or len(y)==0:return None
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)) or np.any(x<0) or np.any(y<0):raise ValueError('invalid TPM')
    d=x[:,None]-y[None,:]
    return float(np.mean((d>0)+.5*(d==0)))
def mean_complete(v):return float(np.mean(v)) if v and all(x is not None for x in v) else None
def evaluate(rows,values,histologies=PRIMARY,detail=False):
    e=[r for r in rows if r['diagnosis']==EMC];out={}
    for h in histologies:
        c=[r for r in rows if r['diagnosis']==h];cells=[]
        years=sorted({r['sequencing_year'] for r in e+c})
        for year in years:
            a=[r for r in e if r['sequencing_year']==year];b=[r for r in c if r['sequencing_year']==year]
            z=auc([values[r['sample_id']] for r in a],[values[r['sample_id']] for r in b])
            cells.append({'year':year,'n_emc':len(a),'n_comparator':len(b),'pairs':len(a)*len(b),'A':z,'singleton':len(a)==1 or len(b)==1})
        supported=[s for s in cells if s['A'] is not None];den=sum(s['n_emc'] for s in supported)
        for s in cells:s['weight']=s['n_emc']/den if s['A'] is not None and den else 0
        v={'marginal':auc([values[r['sample_id']] for r in e],[values[r['sample_id']] for r in c]),'matched':sum(s['weight']*s['A'] for s in supported) if den else None}
        if detail:
            v.update({'n_emc':len(e),'n_comparator':len(c),'matched_emc':den,'cells':cells,'placements':[{ 'sample_id':r['sample_id'],'year':r['sequencing_year'],'TPM':values[r['sample_id']],'marginal_placement':auc([values[r['sample_id']]],[values[t['sample_id']] for t in c]),'matched_placement':auc([values[r['sample_id']]],[values[t['sample_id']] for t in c if t['sequencing_year']==r['sequencing_year']])} for r in e],'zero_fraction_emc':sum(values[r['sample_id']]==0 for r in e)/len(e) if e else None,'zero_fraction_comparator':sum(values[r['sample_id']]==0 for r in c)/len(c) if c else None})
        out[h]=v
    return {'histologies':out,'summary':{m:mean_complete([out[h][m] for h in histologies]) for m in ['marginal','matched']}}
def deletions(rows,values):
    result={}
    for kind,keys in [('emc',[r['sample_id'] for r in rows if r['diagnosis']==EMC]),('comparator',[r['sample_id'] for r in rows if r['diagnosis'] in PRIMARY]),('year',sorted({r['sequencing_year'] for r in rows if r['diagnosis'] in [EMC]+PRIMARY})),('histology',PRIMARY)]:
        d=[]
        for key in keys:
            remaining=[r for r in rows if (r['sequencing_year']!=key if kind=='year' else r['sample_id']!=key)]
            hs=[h for h in PRIMARY if h!=key] if kind=='histology' else PRIMARY
            ev=evaluate(remaining,values,hs,True)
            d.append({'deleted':key,**ev})
        result[kind]=d
    return result
def decision(est,dels):
    a=est['summary']['marginal'];size=a is not None and a>=.7
    directional=all(est['histologies'][h][m] is not None and est['histologies'][h][m]>.5 for h in PRIMARY for m in ['marginal','matched'])
    robust=all(v['summary'][m] is not None and v['summary'][m]>.5 for kind in ['emc','histology'] for v in dels[kind] for m in ['marginal','matched'])
    return {'marginal_size_pass':size,'each_histology_direction_pass':directional,'required_deletion_pass':robust,'consistent_RNA_rationale':bool(size and directional and robust)}
def bootstrap(rows,values,rng,B=2000):
    groups={}
    for r in rows:
        if r['diagnosis'] in [EMC]+PRIMARY:groups.setdefault((r['diagnosis'],r['sequencing_year']),[]).append(r)
    samples={h:{m:[] for m in ['marginal','matched']} for h in PRIMARY+['summary']}
    for _ in range(B):
        draw=[g[i] for g in groups.values() for i in rng.integers(0,len(g),size=len(g))];ev=evaluate(draw,values)
        for h in samples:
            for m in samples[h]:samples[h][m].append(ev['summary'][m] if h=='summary' else ev['histologies'][h][m])
    return {h:{m:np.percentile(v,[2.5,97.5]).tolist() if all(x is not None for x in v) else None for m,v in ms.items()} for h,ms in samples.items()}
def run(auth,out):
    out.mkdir(parents=True,exist_ok=True);state={'stage':'authorization','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running'};dump(out/'execution.json',state)
    try:
        approval=json.loads(auth.read_text());assert approval['authorized_utc'] and approval['authorized_by']=='coordinator'
        for name in ['protocol.md','metadata-manifest.json','metadata.py','analyze.py']:assert approval['sha256'][name]==sha(BASE/name),name
        manifest=json.loads((BASE/'metadata-manifest.json').read_text());src=Path(manifest['source_location'])
        state['stage']='source_integrity';dump(out/'execution.json',state)
        for name,record in manifest['source_files'].items():assert sha(src/name)==record['sha256'],name
        rows=[r for r in manifest['samples'] if r['eligible']];genes=PANEL+['CHRNA6'];values={}
        state['stage']='authorized_expression_read';dump(out/'execution.json',state)
        with (src/'source_data/tpm_matrix.tsv').open() as f:
            reader=csv.reader(f,delimiter='\t');header=next(reader)[1:]
            for row in reader:
                if row[0] in genes:
                    assert row[0] not in values and len(row)==len(header)+1
                    v=list(map(float,row[1:]));assert all(math.isfinite(x) and x>=0 for x in v)
                    values[row[0]]=dict(zip(header,v))
        assert set(values)==set(genes)
        dump(out/'selected-values.json',values)
        revised=[dict(r,diagnosis=r['revised_diagnosis'] or r['diagnosis']) for r in rows]
        dump(out/'revised-membership-changes.json',[{'sample_id':r['sample_id'],'original':r['diagnosis'],'revised':s['diagnosis']} for r,s in zip(rows,revised) if r['diagnosis']!=s['diagnosis']])
        result={};rng=np.random.default_rng(20260906)
        for gene in genes:
            state['stage']='gene_'+gene;dump(out/'execution.json',state)
            est=evaluate(rows,values[gene],detail=True);dels=deletions(rows,values[gene]);d=decision(est,dels)
            result[gene]={'role':'context_control' if gene=='CHRNA6' else 'address_panel','primary':est,'context':evaluate(rows,values[gene],CONTEXT,True),'bootstrap_pointwise_conditional_95':bootstrap(rows,values[gene],rng),'deletions':dels,'deletion_summary_ranges':{k:{m:[min(v['summary'][m] for v in ds if v['summary'][m] is not None),max(v['summary'][m] for v in ds if v['summary'][m] is not None)] if any(v['summary'][m] is not None for v in ds) else None for m in ['marginal','matched']} for k,ds in dels.items()},'revised_diagnosis_sensitivity':evaluate(revised,values[gene],detail=True),'allocation_rule':d if gene in PANEL else {'not_applied_context_only':True}}
            dump(out/(gene+'.json'),result[gene])
        dump(out/'result.json',{'genes':result,'passing_address_genes':[g for g in PANEL if result[g]['allocation_rule']['consistent_RNA_rationale']],'scope':'single cohort overlap-reduced tissue RNA; no clinical or cell-localization validation','bootstrap_seed':20260906,'bootstrap_replicates':2000,'authorization':approval})
        state['status']='complete'
    except Exception:
        state['status']='failed';state['error']=traceback.format_exc();raise
    finally:
        state['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dump(out/'execution.json',state)
def fixtures():
    assert auc([0,1],[0,2])==.375
    assert auc([0,0],[0,0])==.5
    assert auc([3],[1,2])==1 and auc([1,2],[3])==0
    assert auc([], [1]) is None
    for bad in [-1,float('nan'),float('inf')]:
        try:auc([bad],[1]);raise AssertionError('invalid accepted')
        except ValueError:pass
    def r(s,d,y):return {'sample_id':s,'diagnosis':d,'sequencing_year':y}
    rows=[r('e1',EMC,'1'),r('e2',EMC,'1'),r('e3',EMC,'2')];vals={'e1':10,'e2':10,'e3':0}
    for i,h in enumerate(PRIMARY):
        rows += [r('c'+str(i)+'a',h,'1'),r('c'+str(i)+'b',h,'2')];vals.update({'c'+str(i)+'a':5,'c'+str(i)+'b':5})
    ev=evaluate(rows,vals,detail=True)
    assert abs(ev['summary']['matched']-2/3)<1e-12
    assert all(abs(ev['histologies'][h]['marginal']-2/3)<1e-12 for h in PRIMARY)
    ds=deletions(rows,vals);assert ds['emc'][2]['summary']['matched']==1
    assert not decision(ev,ds)['consistent_RNA_rationale']
    # Equal histology, not comparator count: enlarge a low-effect comparator only.
    rr=[r('e',EMC,'1')];vv={'e':2}
    for i,h in enumerate(PRIMARY):
        for j in range(10 if i==0 else 1):
            sid=f'x{i}_{j}';rr.append(r(sid,h,'1'));vv[sid]=3 if i==0 else 1
    assert abs(evaluate(rr,vv)['summary']['marginal']-2/3)<1e-12
    assert evaluate([r('e',EMC,'1'),r('c',PRIMARY[0],'2')],{'e':2,'c':1},[PRIMARY[0]])['summary']['matched'] is None
    high=dict(vals,e1=20,e2=20,e3=20)
    assert decision(evaluate(rows,high),deletions(rows,high))['consistent_RNA_rationale']
    contrary=dict(high,c0a=30,c0b=30)
    assert not decision(evaluate(rows,contrary),deletions(rows,contrary))['consistent_RNA_rationale']
    b1=bootstrap(rows,vals,np.random.default_rng(9),20);b2=bootstrap(rows,vals,np.random.default_rng(9),20);assert b1==b2
    return {'status':'passed','data':'synthetic only','checks':['half ties','all zero ties','direction reversal','empty undefined','negative/nonfinite rejection','year weights','deletion weight renormalization','failed allocation retained','equal histology unequal counts','unsupported year null','positive allocation and heterogeneity failure','bootstrap reproducibility']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--authorization',type=Path);p.add_argument('--output',type=Path,default=BASE/'results');p.add_argument('--fixture-output',type=Path);a=p.parse_args()
    if a.authorization:run(a.authorization,a.output)
    else:
        x=fixtures();print(json.dumps(x,indent=2))
        if a.fixture_output:dump(a.fixture_output,x)
