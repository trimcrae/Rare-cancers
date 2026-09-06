"""Independent audit. No worker functions imported. Only ten development ZIP members opened."""
import bisect,collections,csv,datetime,hashlib,io,json,math,pathlib,sys,time,zipfile
P=pathlib.Path('C:/Users/mcrae/.codex/worktrees/ipd-empirical-information-20260906/EMC-Research/research/autonomy/ipd-empirical-information-2026-09-06')
OUT=pathlib.Path(__file__).parent
START=time.monotonic(); ERR=[]; HASHES={}; MAX=collections.defaultdict(float)
def read(p):
 b=p.read_bytes();HASHES[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(b)
def check(x,msg):
 if not x:ERR.append(msg)
def close(a,b,msg):
 if a is None or b is None:check(a==b,msg);return
 delta=abs(a-b);MAX[msg.split(':')[0]]=max(MAX[msg.split(':')[0]],delta)
 check(delta<=1e-9*max(1,abs(a),abs(b)),msg+f' {a} != {b}')
def stat(a,b):
 # One pooled exit table, decreasing risk totals; censor exits follow events at each exact time.
 tab=collections.defaultdict(lambda:[0,0,0,0])
 for g,rows in enumerate((a,b)):
  for t,e in rows:
   if not math.isfinite(t) or t<0 or e not in (0,1):raise ValueError('invalid row')
   tab[t][g]+=1;tab[t][2+g]+=e
 risk=[len(a),len(b)]; us=[];vs=[]
 for t,(xa,xb,da,db) in sorted(tab.items()):
  n=sum(risk);d=da+db
  if d:
   us.append(da-d*risk[0]/n)
   if n>1:vs.append(d*(n-d)/(n-1)*(risk[0]/n)*(risk[1]/n))
  risk[0]-=xa;risk[1]-=xb
 u=math.fsum(us);v=math.fsum(vs)
 if not v>0:return dict(u=u,v=v,z=None,q=None,p=None,reject=None,evaluable=False)
 z=u/math.sqrt(v);p=math.erfc(abs(z)/math.sqrt(2))
 return dict(u=u,v=v,z=z,q=z*z,p=p,reject=p<.05,evaluable=True)
def release(rows,dec,density):
 exits=collections.Counter(t for t,e in rows);events=collections.Counter(t for t,e in rows if e)
 n=len(rows);remaining=n;s=1.;tx=[0.];sy=[1.]
 for t in sorted(exits):
  if events[t]:s*= (remaining-events[t])/remaining;tx.append(t);sy.append(round(s,dec))
  remaining-=exits[t]
 tau=max(exits)
 if tx[-1]!=tau:tx.append(tau);sy.append(sy[-1])
 ts=sorted(t for t,e in rows); rt=[tau*f for f in ([0,.5] if density=='sparse' else [0,.25,.5,.75])]
 return dict(time=tx,surv=sy,trisk=rt,nrisk=[n-bisect.bisect_left(ts,t) for t in rt],n=n,events=sum(events.values()))
def same_release(a,b,tag):
 for k in a:
  if isinstance(a[k],list):
   check(len(a[k])==len(b[k]),tag+k+' length')
   for i,(x,y) in enumerate(zip(a[k],b[k])):close(x,y,'release:'+tag+k+str(i))
  else:close(a[k],b[k],'release:'+tag+k)
# Independent analytic checks, including true ties and zero variance.
check(abs(stat([(1,1),(1,1)],[(2,0)])['q']-2)<1e-12,'fixture tied')
check(abs(stat([(1,1),(3,0)],[(1+1e-10,1),(4,0)])['q']-1/17)<1e-12,'fixture near ties')
check(not stat([(1,0)],[(2,0)])['evaluable'],'fixture zero variance')
auth=read(P/'authorization.json');freeze=read(P/'development/execution-freeze.json');manifest=read(P/'source-manifest.json')
for name,digest in auth['hashes'].items():check(hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,'approved hash '+name)
for name,digest in freeze['source_hashes'].items():
 actual=hashlib.sha256((P/name).read_bytes()).hexdigest();HASHES[str(P/name)]=actual;check(actual==digest,'execution-frozen hash '+name)
archive=pathlib.Path(manifest['archive']);check(hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['archive_sha256'],'archive digest')
planned=read(P/'development/planned-cases.json');attempts=read(P/'development/attempts.json');cases=attempts['cases']
groups=[g for g in manifest['source_groups'] if g['split']=='development'];check(len(groups)==10,'ten development groups');check(sum(g['split']=='reserved_unopened' for g in manifest['source_groups'])==11,'eleven reserved groups')
expected=[];truth={};arms={};opened=[];seen=set()
with zipfile.ZipFile(archive) as z:
 for g in groups:
  for c in g['curves']:
   member='RealIPD/IPD/'+c['curve_id']+'.csv';opened.append(member)
   rr=list(csv.DictReader(io.TextIOWrapper(z.open(member))))
   ids={r['id'] for r in rr};check(len(ids)==len(rr),'unique IDs '+member);check(not ids&seen,'development ID overlap '+member);seen|=ids
   idhash=hashlib.sha256('\n'.join(sorted(ids)).encode()).hexdigest()
   check(idhash==g['identifier_union_sha256'],'development identifier union digest '+member)
   for seed in (61001,61002,61003):
    ranked=sorted(rr,key=lambda r:hashlib.sha256(f"{seed}|{r['id']}".encode()).digest())
    chunks=[ranked[:len(ranked)//2],ranked[len(ranked)//2:]]
    ab=[[(float(r['time']),int(float(r['status']))) for r in part] for part in chunks]
    check(all(float(r['status']) in (0.,1.) and math.isfinite(float(r['time'])) and float(r['time'])>0 for r in rr),'valid development source '+member)
    key=(c['curve_id'],seed);arms[key]=ab;truth[key]=stat(*ab)
    for prec in (2,3):
     for density in ('sparse','dense'):expected.append(dict(case_id=f"{c['curve_id']}-{seed}-{prec}-{density}",source_group=g['source_group'],curve=c,seed=seed,precision=prec,density=density))
check(expected==planned,'planned Cartesian product/order');check(len(expected)==120,'120 planned')
check(len({c['case_id'] for c in cases})==len(cases),'unique attempted IDs')
expected_by={c['case_id']:c for c in expected};computed=[];recon_count=0;packages=collections.Counter()
for c in cases:
 cid=c['case_id'];check(cid in expected_by,'unexpected case '+cid)
 for k,v in expected_by[cid].items():check(c[k]==v,'case metadata '+cid+k)
 key=(c['curve']['curve_id'],c['seed']);orig=truth[key]
 for k in orig:
  if isinstance(orig[k],bool):check(orig[k]==c['original'][k],'original flag '+cid+k)
  else:close(orig[k],c['original'][k],'original_'+k+':'+cid)
 cc=dict(case_id=cid,group=c['source_group'],original=orig,methods={});computed.append(cc)
 if c['status']!='returned':continue
 released=read(P/'development'/f'{cid}.release.json');result=read(P/'development'/f'{cid}.result.json')
 for label,rows in zip(('a','b'),arms[key]):
  same_release(release(rows,c['precision'],c['density']),released[label],cid+label)
  same_release(released[label],result['inputs'][label],cid+label+'R')
 for m,res in result['methods'].items():
  check(res['status']==c['methods'][m]['status'],'method status '+cid+m)
  packages[str(result['package_versions'])]+=1
  if res['status']!='success':continue
  aa=[(r['time'],r['event']) for r in res['ipd'] if r['arm']=='a'];bb=[(r['time'],r['event']) for r in res['ipd'] if r['arm']=='b']
  check(bool(aa) and bool(bb),'nonempty reconstructed arms '+cid+m)
  calc=stat(aa,bb);check(calc['evaluable'],'evaluable reconstructed '+cid+m);recon_count+=1
  for k in ('u','v','z','q','p'):close(calc[k],c['methods'][m]['statistic'][k],'reconstructed_'+k+':'+cid+m)
  close(calc['q'],res['logrank_chisq'],'R_Q:'+cid+m);close(calc['p'],res['logrank_p'],'R_p:'+cid+m)
  err=calc['reject']!=orig['reject'];flip=('false_reject' if calc['reject'] else 'false_nonreject') if err else None
  check(err==c['methods'][m]['threshold_error'],'error classification '+cid+m);check(flip==c['methods'][m]['flip_direction'],'flip direction '+cid+m)
  check((calc['z']*orig['z']<0)==c['methods'][m]['sign_flip'],'sign flip '+cid+m)
  cc['methods'][m]=dict(z=calc['z'],error=err,reject=calc['reject'])
common=[c for c in computed if len(c['methods'])==2]
def chosen(rows,aug):
 def score(c):
  zi=c['methods']['IPDfromKM']['z'];zc=c['methods']['CIFresolve']['z']
  return abs(abs(zi)-1.959963984540054)-(abs(zi-zc) if aug else 0)
 return sorted(rows,key=lambda c:(-score(c),c['case_id']))[:int(.75*len(rows))]
def err_ids(rows):return [c['case_id'] for c in rows if c['methods']['IPDfromKM']['error']]
ms=chosen(common,False);ds=chosen(common,True);me=err_ids(ms);de=err_ids(ds)
gains={g['source_group']:sum(c['group']==g['source_group'] and c['methods']['IPDfromKM']['error'] for c in ms)-sum(c['group']==g['source_group'] and c['methods']['IPDfromKM']['error'] for c in ds) for g in groups}
loo={g['source_group']:len(err_ids(chosen([c for c in common if c['group']!=g['source_group']],False)))-len(err_ids(chosen([c for c in common if c['group']!=g['source_group']],True))) for g in groups}
ie=[c for c in computed if c['methods'].get('IPDfromKM',{}).get('error')]
complete=len(cases)==120 and {c['case_id'] for c in cases}==set(expected_by) and not any(c['status'].startswith('unrun') or c['status']=='verification_discrepancy' for c in cases)
gate=dict(complete_planned_execution=complete,at_least_8_incumbent_errors=len(ie)>=8,at_least_3_error_sources=len({c['group'] for c in ie})>=3,dual_success_at_least_80pct=len(common)>=96,primary_gain_at_least_2=len(me)-len(de)>=2,primary_relative_gain_at_least_20pct=len(me)>0 and (len(me)-len(de))/len(me)>=.2,gain_at_least_2_sources=sum(v>0 for v in gains.values())>=2,no_leave_one_source_out_reversal=all(v>=0 for v in loo.values()))
summary_checked=False
if complete and (P/'development/summary.json').exists():
 sm=read(P/'development/summary.json');summary_checked=True
 check(gate==sm['continuation_checks'],'summary gate');check(all(gate.values())==sm['continue_to_held_out'],'summary continuation')
 check(len(common)==sm['dual_success_cases'],'summary dual success');check(sm['attempted_cases']==120,'summary attempted')
 for rule,selected,errs in [('margin',ms,me),('margin_minus_disagreement',ds,de)]:
  s=sm['primary_common_success']['0.75'][rule];check(len(selected)==s['retained'],'summary retained '+rule);check(errs==s['error_cases'],'summary primary error IDs '+rule)
 check(gains=={r['source_group']:r['gain'] for r in sm['source_primary_gains']},'summary source gains')
 check(loo=={r['excluded_source']:r['gain'] for r in sm['leave_one_source_out']},'summary LOO')
report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),independent_method='pooled event/exit contingency table with decrementing risks, math.fsum; no worker imports; exact float ties',opened_development_members=opened,reserved_outcome_members_opened=[],source_groups=len(groups),original_assignments=len(truth),planned_cases=len(expected),persisted_cases=len(cases),complete_execution=complete,returned_reconstructions_verified=recon_count,dual_success=len(common),original_reject_assignments=sum(v['reject'] for v in truth.values()),incumbent_errors=len(ie),incumbent_error_sources=sorted({c['group'] for c in ie}),retained=len(ms),margin_error_ids=me,augmented_error_ids=de,source_gains=gains,leave_one_source_out_gains=loo,gate=gate,continue_to_held_out=all(gate.values()),summary_checked=summary_checked,max_absolute_differences=dict(MAX),discrepancies=ERR,elapsed_seconds=time.monotonic()-START,scope='Independent development arithmetic/provenance verification; not clinical validity, manuscript or ultra review')
(OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
HASHES[str(pathlib.Path(__file__))]=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
(OUT/'file-manifest.json').write_text(json.dumps(HASHES,indent=2)+'\n')
print(json.dumps(report,indent=2));sys.exit(1 if ERR else 0)

