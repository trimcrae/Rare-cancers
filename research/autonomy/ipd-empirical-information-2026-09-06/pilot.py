"""Empirical values are opened ONLY by explicit --run with reviewed protocol hashes."""
import argparse,csv,hashlib,io,json,math,pathlib,subprocess,tempfile,time,zipfile
HERE=pathlib.Path(__file__).resolve().parent
BASE=pathlib.Path('C:/Users/mcrae/.codex/worktrees/ipd-baselines-20260906/EMC-Research')
RSCRIPT=BASE/'.cache/R-4.6.1/bin/Rscript.exe'
LIB=BASE/'.cache/R-library'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data): path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def logrank(a,b):
    u=v=0.
    for t in sorted({t for t,e in a+b if e}):
        na=sum(x>=t for x,e in a);nb=sum(x>=t for x,e in b);n=na+nb
        da=sum(x==t and e==1 for x,e in a);db=sum(x==t and e==1 for x,e in b);d=da+db
        u+=da-d*na/n
        if n>1:v+=na*nb*d*(n-d)/(n*n*(n-1))
    if v<=0:return {'u':u,'v':v,'z':None,'q':None,'p':None,'reject':None,'evaluable':False}
    z=u/math.sqrt(v)
    return {'u':u,'v':v,'z':z,'q':z*z,'p':math.erfc(abs(z)/math.sqrt(2)),'reject':abs(z)>1.959963984540054,'evaluable':True}
def complete_stopped(attempts,planned):
    done={c['case_id'] for c in attempts}
    return attempts+[dict(c,status='unrun_after_discrepancy',original=None) for c in planned if c['case_id'] not in done]
def release_arm(rows,decimals,density):
    tau=max(t for t,e in rows);s=1.;km=[]
    for t in sorted({t for t,e in rows if e}):
        n=sum(x>=t for x,e in rows);d=sum(x==t and e==1 for x,e in rows)
        s*=1-d/n;km.append([t,round(s,decimals)])
    # Empty event series is represented by flat origin and endpoint.
    coords=[[0.,1.]]+km
    if coords[-1][0]!=tau:coords.append([tau,coords[-1][1]])
    rt=[tau*f for f in ([0.,.5] if density=='sparse' else [0.,.25,.5,.75])]
    return {'time':[x[0] for x in coords],'surv':[x[1] for x in coords],
            'trisk':rt,'nrisk':[sum(t>=r for t,e in rows) for r in rt],
            'n':len(rows),'events':sum(e for t,e in rows)}
def fixture_checks():
    # Analytic tied-event case from retained prior-art counterexample.
    a=[(1.,1),(1.,1)];b=[(2.,0)]
    r=logrank(a,b);assert abs(r['u']-2/3)<1e-12 and abs(r['v']-2/9)<1e-12 and abs(r['q']-2)<1e-12
    rr=logrank(b,a);assert abs(rr['z']+r['z'])<1e-12 and abs(rr['p']-r['p'])<1e-12
    assert logrank([(1,0)],[(2,0)])['p'] is None
    assert logrank([(1,1)],[(1,1)])['evaluable'] is False
    x=release_arm([(1,1),(1,0),(2,1),(3,0)],2,'dense')
    assert x['surv']==[1.,.75,.38,.38] and x['nrisk']==[4,4,2,1]
    assert logrank([(2*t,e) for t,e in a],[(2*t,e) for t,e in b])==r
    near=logrank([(1.,1),(3.,0)],[(1.+1e-10,1),(4.,0)])
    tied=logrank([(1.,1),(3.,0)],[(1.,1),(4.,0)])
    assert abs(near['q']-1/17)<1e-12 and tied['q']==0.
    with tempfile.TemporaryDirectory(dir=HERE) as td:
        path=pathlib.Path(td)/'receipt.json'
        halted=complete_stopped([{'case_id':'one','status':'verification_discrepancy','raw_result':'retained.json'}],[{'case_id':'one'},{'case_id':'two'}])
        save(path,halted);loaded=json.loads(path.read_text())
        assert loaded[0]['raw_result']=='retained.json' and loaded[1]['status']=='unrun_after_discrepancy'
    return {'analytic_ties':True,'arm_swap':True,'zero_variance_undefined':True,'near_ties_distinct':True,'durable_stop_complete_denominator':True,'release_tie_order':True,'time_scale_invariance':True}
def run(args):
    assert args.protocol_sha256==sha(HERE/'protocol.md'),'reviewed protocol hash required'
    assert args.manifest_sha256==sha(HERE/'source-manifest.json'),'reviewed manifest hash required'
    assert args.amendment_sha256==sha(HERE/'amendment-2026-09-06.md'),'reviewed amendment hash required'
    assert args.runtime_amendment_sha256==sha(HERE/'amendment-runtime-2026-09-06.md'),'reviewed runtime amendment hash required'
    manifest=json.loads((HERE/'source-manifest.json').read_text())
    archive=pathlib.Path(manifest['archive']);assert sha(archive)==manifest['archive_sha256']
    out=HERE/'development';out.mkdir(exist_ok=True)
    assert not (out/'attempts.json').exists(),'preserve existing execution; no silent rerun'
    save(out/'execution-freeze.json',{'protocol_sha256':args.protocol_sha256,'manifest_sha256':args.manifest_sha256,'amendment_sha256':args.amendment_sha256,'runtime_amendment_sha256':args.runtime_amendment_sha256,'source_hashes':{p.name:sha(p) for p in HERE.iterdir() if p.suffix in ('.py','.R','.md')},'rscript':str(RSCRIPT),'library':str(LIB),'scope':'development only; no held-out access'})
    started=time.monotonic();attempts=[];planned=[]
    for group in manifest['source_groups']:
        if group['split']!='development':continue
        for curve in group['curves']:
            for seed in (61001,61002,61003):
                for precision in (2,3):
                    for density in ('sparse','dense'):
                        planned.append({'case_id':f"{curve['curve_id']}-{seed}-{precision}-{density}",'source_group':group['source_group'],'curve':curve,'seed':seed,'precision':precision,'density':density})
    save(out/'planned-cases.json',planned)
    with zipfile.ZipFile(archive) as z:
        for group in manifest['source_groups']:
            if group['split']!='development':continue
            for curve in group['curves']:
                rows=[];issue=None
                try:
                    for r in csv.DictReader(io.TextIOWrapper(z.open('RealIPD/IPD/'+curve['curve_id']+'.csv'))):
                        t=float(r['time']);status=float(r['status'])
                        if not math.isfinite(t) or t<=0 or status not in (0.,1.):raise ValueError('invalid/nonpositive time or nonbinary status; no recoding')
                        rows.append((r['id'],t,int(status)))
                    if len(rows)<4:raise ValueError('too few records for two nonempty evaluable pseudoarms')
                except Exception as e: issue=str(e)
                for seed in (61001,61002,61003):
                    ordered=sorted(rows,key=lambda r:hashlib.sha256((str(seed)+'|'+r[0]).encode()).hexdigest())
                    cut=len(ordered)//2;a=[r[1:] for r in ordered[:cut]];b=[r[1:] for r in ordered[cut:]]
                    original=logrank(a,b) if not issue else None
                    for precision in (2,3):
                        for density in ('sparse','dense'):
                            cid=f"{curve['curve_id']}-{seed}-{precision}-{density}"
                            record={'case_id':cid,'source_group':group['source_group'],'curve':curve,'seed':seed,'precision':precision,'density':density,'original':original}
                            if issue:record.update(status='source_failure',error=issue)
                            elif not original['evaluable']:record.update(status='original_unevaluable')
                            elif time.monotonic()-started>1800:record.update(status='unrun_budget')
                            else:
                                rel={'schema':'empirical-numerical-release-v1','a':release_arm(a,precision,density),'b':release_arm(b,precision,density)}
                                inp=out/(cid+'.release.json');result=out/(cid+'.result.json');save(inp,rel)
                                command=[str(RSCRIPT),'--vanilla',str(HERE/'runner.R'),str(LIB),str(inp),str(result)]
                                tick=time.monotonic()
                                try:
                                    cp=subprocess.run(command,capture_output=True,text=True,timeout=60)
                                    (out/(cid+'.log')).write_text(cp.stdout+'\n'+cp.stderr,encoding='utf-8')
                                    record.update(status='returned' if cp.returncode==0 and result.exists() else 'process_failure',returncode=cp.returncode)
                                    if record['status']=='returned':
                                        data=json.loads(result.read_text());record['methods']={}
                                        for method,res in data['methods'].items():
                                            mr={'status':res['status']}
                                            if res['status']=='success':
                                                ipd=res['ipd'];ar=[(r['time'],r['event']) for r in ipd if r['arm']=='a'];br=[(r['time'],r['event']) for r in ipd if r['arm']=='b']
                                                if not ar or not br or any(not math.isfinite(t) or t<0 or e not in (0,1) for t,e in ar+br):raise ArithmeticError('invalid reconstructed records escaped R checks')
                                                calc=logrank(ar,br)
                                                if not calc['evaluable'] or not all(math.isfinite(res[k]) for k in ('logrank_p','logrank_chisq')):raise ArithmeticError('unevaluable/nonfinite result escaped R checks')
                                                if abs(calc['p']-res['logrank_p'])>1e-8 or abs(calc['q']-res['logrank_chisq'])>1e-7*max(1,calc['q']):raise ArithmeticError('independent R/Python discrepancy')
                                                mr.update(statistic=calc,threshold_error=calc['reject']!=original['reject'],flip_direction=('false_reject' if calc['reject'] else 'false_nonreject') if calc['reject']!=original['reject'] else None,sign_flip=calc['z']*original['z']<0)
                                            else:mr['error']=res.get('error')
                                            record['methods'][method]=mr
                                except subprocess.TimeoutExpired:record.update(status='timeout')
                                except ArithmeticError as e:
                                    record.update(status='verification_discrepancy',error=str(e),raw_result=str(result),raw_release=str(inp),elapsed_seconds=time.monotonic()-tick)
                                    attempts.append(record);attempts=complete_stopped(attempts,planned)
                                    save(out/'attempts.json',{'cases':attempts,'stopped_on_discrepancy':True,'elapsed_seconds':time.monotonic()-started,'protocol_sha256':args.protocol_sha256,'amendment_sha256':args.amendment_sha256,'manifest_sha256':args.manifest_sha256})
                                    return {'stopped_on_discrepancy':True,'attempts':len(attempts)}
                                record['elapsed_seconds']=time.monotonic()-tick
                            attempts.append(record);save(out/'attempts.json',{'cases':attempts,'elapsed_seconds':time.monotonic()-started,'protocol_sha256':args.protocol_sha256,'amendment_sha256':args.amendment_sha256,'manifest_sha256':args.manifest_sha256})
                            print(cid,record['status'],flush=True)
    return {'attempts':len(attempts),'elapsed_seconds':time.monotonic()-started}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--protocol-sha256');p.add_argument('--manifest-sha256');p.add_argument('--amendment-sha256');p.add_argument('--runtime-amendment-sha256');args=p.parse_args()
    if args.run:print(json.dumps(run(args)))
    else:print(json.dumps({'fixtures':fixture_checks(),'protocol_sha256':sha(HERE/'protocol.md'),'manifest_sha256':sha(HERE/'source-manifest.json'),'rscript_exists':RSCRIPT.exists(),'library_exists':LIB.exists(),'empirical_outcomes_opened':False}))
