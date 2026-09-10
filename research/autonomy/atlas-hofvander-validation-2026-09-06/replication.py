"""Same-histology cross-cohort ranks. Default is synthetic-only fixtures."""
from pathlib import Path
import argparse,csv,gzip,json,math,datetime,traceback
from metadata import EMC,PANEL,sha
from analyze import evaluate,dump
BASE=Path(__file__).parent
APPROVED=['protocol.md','metadata-manifest.json','metadata.py','analyze.py','amendment-replication-2026-09-06.md','replication-manifest.json','replication_metadata.py','replication.py']
def probability(x,y):
    if not x or not y:return None
    if any(not math.isfinite(v) for v in x+y):raise ValueError('nonfinite released signal')
    return sum((a>b)+.5*(a==b) for a in x for b in y)/(len(x)*len(y))
def sign(a):return None if a is None else ('positive' if a>.5 else 'negative' if a<.5 else 'neutral')
def array_contrast(rows,values,h):
    e=[r['sample_id'] for r in rows if r['diagnosis']==EMC];c=[r['sample_id'] for r in rows if r['diagnosis']==h]
    a=probability([values[s] for s in e],[values[s] for s in c]);d={}
    for label,ids in [('EMC',e),('comparator',c)]:
        d[label]=[]
        for s in ids:
            ev=probability([values[t] for t in e if t!=s],[values[t] for t in c if t!=s])
            d[label].append({'deleted':s,'A':ev,'direction':sign(ev)})
    return {'A':a,'A_minus_half':None if a is None else a-.5,'direction':sign(a),'n_emc':len(e),'n_comparator':len(c),'pairs':len(e)*len(c),'placements':[{'sample_id':s,'value':values[s],'A':probability([values[s]],[values[t] for t in c])} for s in e],'deletions':d,'deletion_ranges':{label:[min(v['A'] for v in ds if v['A'] is not None),max(v['A'] for v in ds if v['A'] is not None)] if any(v['A'] is not None for v in ds) else None for label,ds in d.items()}}
def read_array(path,probes,samples):
    reverse={v:k for k,v in probes.items()};assert len(reverse)==len(probes)
    out={g:{} for g in probes};sample=None;table=False;columns=None
    with gzip.open(path,'rt',encoding='utf-8',errors='strict') as f:
        for line in f:
            line=line.rstrip('\r\n')
            if line.startswith('^SAMPLE = '):sample=line.split(' = ',1)[1];table=False
            elif line=='!sample_table_begin':table=True;columns=None
            elif line=='!sample_table_end':table=False
            elif table:
                row=line.split('\t')
                if columns is None:
                    columns=row;assert 'ID_REF' in columns and 'VALUE' in columns;continue
                probe=row[columns.index('ID_REF')]
                if probe in reverse:
                    assert sample in samples and sample not in out[reverse[probe]],'unknown or duplicate sample/probe'
                    v=float(row[columns.index('VALUE')]);assert math.isfinite(v)
                    out[reverse[probe]][sample]=v
    assert all(set(v)==set(samples) for v in out.values()),'incomplete source sample/probe matrix'
    return out
def run(auth_path,output,original):
    output.mkdir(parents=True,exist_ok=True);state={'status':'running','stage':'authorization','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};dump(output/'execution.json',state)
    try:
        auth=json.loads(auth_path.read_text());assert auth['authorized_by']=='coordinator' and auth['authorized_utc']
        for name in APPROVED:assert sha(BASE/name)==auth['sha256'][name],name
        manifest=json.loads((BASE/'replication-manifest.json').read_text());hm=json.loads((BASE/'metadata-manifest.json').read_text())
        for m in [manifest,hm]:
            for name,v in m['source_files'].items():assert sha(Path(m['source_location'])/name)==v['sha256'],name
        initial=json.loads((original/'result.json').read_text());assert json.loads((original/'execution.json').read_text())['status']=='complete'
        for name in APPROVED[:4]:assert initial['authorization']['sha256'][name]==auth['sha256'][name]
        original_values=json.loads((original/'selected-values.json').read_text());assert set(original_values)==set(PANEL+['CHRNA6'])
        state['stage']='authorized_original_source_values';dump(output/'execution.json',state)
        hv={}
        with (Path(hm['source_location'])/'source_data/tpm_matrix.tsv').open() as f:
            reader=csv.reader(f,delimiter='\t');header=next(reader)[1:]
            for row in reader:
                if row[0] in original_values:hv[row[0]]=dict(zip(header,map(float,row[1:])))
        assert hv==original_values,'Hofvander result source values changed'
        av=read_array(Path(manifest['source_location'])/'GSE24369.soft.gz',manifest['gene_to_probe'],[r['sample_id'] for r in manifest['array_samples']]);dump(output/'array-values.json',av)
        hist=[manifest['primary_replication_histology']]+manifest['secondary_replication_histologies'];result={}
        for g in PANEL+['CHRNA6']:
            contrasts={};rows=manifest['hofvander_samples']
            for h in hist:
                ar=array_contrast(manifest['array_samples'],av[g],h);ho=evaluate(rows,hv[g],[h],True);dels={}
                for label in ['EMC','comparator']:
                    ids=[r['sample_id'] for r in rows if r['diagnosis']==(EMC if label=='EMC' else h)]
                    dels[label]=[{'deleted':s,**evaluate([r for r in rows if r['sample_id']!=s],hv[g],[h],True)} for s in ids]
                directions={'array_marginal':ar['direction'],'hofvander_marginal':sign(ho['summary']['marginal']),'hofvander_matched':sign(ho['summary']['matched'])}
                contrasts[h]={'role':'primary_anchor' if h==hist[0] else 'secondary_context','array':ar,'hofvander':ho,'hofvander_deletions':dels,'directions':directions,'same_marginal_direction':ar['direction']==directions['hofvander_marginal'],'same_matched_direction':ar['direction']==directions['hofvander_matched']}
            result[g]={'role':'context_control' if g=='CHRNA6' else 'address_panel','contrasts':contrasts,'normal_pools_descriptive_values':{r['sample_id']:av[g][r['sample_id']] for r in manifest['array_samples'] if r['unit']=='pooled_normal_RNA'}}
            dump(output/(g+'.json'),result[g])
        dump(output/'result.json',{'genes':result,'authorization':auth,'original_result_sha256':sha(original/'result.json'),'original_values_sha256':sha(original/'selected-values.json'),'scope':'per-histology cohort-specific ranks; no pooled units, new cutoff, organ-safety or efficacy inference'})
        state['status']='complete'
    except Exception:
        state['status']='failed';state['error']=traceback.format_exc();raise
    finally:
        state['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dump(output/'execution.json',state)
def fixtures():
    assert probability([-3,-1],[-2,0])==.25
    assert probability([0,1],[0,2])==.375
    assert probability([], [2]) is None
    assert probability([1,2],[1,2])==.5
    assert probability([1,2],[0,2])==probability([11,12],[10,12])
    rows=[{'sample_id':s,'diagnosis':EMC if s.startswith('e') else 'H'} for s in ['e1','e2','c1','c2']];v={'e1':1,'e2':3,'c1':0,'c2':2}
    r=array_contrast(rows,v,'H');assert r['A']==.75 and r['deletion_ranges']['EMC']==[.5,1.0]
    assert sign(.5)=='neutral' and sign(.49)=='negative' and sign(.51)=='positive' and sign(None) is None
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'fixture.gz'
        def write(s):
            with gzip.open(p,'wt') as f:f.write(s)
        txt='^SAMPLE = A\n!sample_table_begin\nID_REF\tVALUE\np1\t-2.5\n!sample_table_end\n'
        write(txt);assert read_array(p,{'G':'p1'},['A'])=={'G':{'A':-2.5}}
        for bad in [txt+txt,txt.replace('p1','p2'),txt.replace('-2.5','nan')]:
            write(bad)
            try:read_array(p,{'G':'p1'},['A']);raise RuntimeError('bad fixture accepted')
            except AssertionError:pass
    return {'status':'passed','data':'synthetic only','checks':['signed log signal','half ties','empty null','neutral direction','monotonic translation invariance','individual deletion range','SOFT sample-table extraction','duplicate missing nonfinite source rejection']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--authorization',type=Path);p.add_argument('--output',type=Path,default=BASE/'replication-results');p.add_argument('--original-results',type=Path,default=BASE/'results');p.add_argument('--fixture-output',type=Path);a=p.parse_args()
    if a.authorization:run(a.authorization,a.output,a.original_results)
    else:
        x=fixtures();print(json.dumps(x,indent=2))
        if a.fixture_output:dump(a.fixture_output,x)
