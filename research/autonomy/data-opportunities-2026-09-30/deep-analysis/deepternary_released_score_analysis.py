#!/usr/bin/env python3
import argparse,collections,datetime,hashlib,json,pathlib,re,statistics,urllib.request
P=pathlib.Path
REF='827821dccca31a5918bd0355e2d6bf70c072b6dd'
REPO='youqingxiaozhua/DeepTernary'
def fetch(path):
 u=f'https://raw.githubusercontent.com/{REPO}/{REF}/{path}'
 with urllib.request.urlopen(u,timeout=90) as h:b=h.read()
 return b,{'url':u,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def readone(name):
 xs=list(P('campaign-output/deepternary-released-files').rglob(name))
 if not xs:xs=[x for x in P('.').rglob(name) if '.git' not in x.parts]
 assert len(xs)==1,(name,[str(x) for x in xs])
 b=xs[0].read_bytes();return b,{'path':str(xs[0]),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def unwrap(d):
 while 'result' in d and isinstance(d['result'],dict):d=d['result']
 return d
def parse(b):
 rows=[]
 for line in b.decode().splitlines():
  if not line.startswith('|'):continue
  c=[x.strip() for x in line.strip('|').split('|')]
  if len(c)!=8:continue
  try:v=[float(c[0]),float(c[1]),float(c[3]),float(c[5]),float(c[7])]
  except ValueError:continue
  if not re.fullmatch(r'\d+/\d+/\d+',c[6]):continue
  rows.append({'predDockQ':v[0],'oracleDockQ':v[1],'firstAcceptablePredictedRank':None if c[2]=='None' else int(c[2]),'bestSmallMoleculeRMSD':v[2],'smallMoleculeRank':int(c[4]),'fractionSmallMoleculeRMSDUnder10':v[3],'legacyHitCounts':[int(x) for x in c[6].split('/')],'legacyHitRate':v[4]})
 return rows
def summary(rows,seeds):
 n=len(rows);out={'n':n,'seedBudget':seeds,'meanPredDockQ':statistics.mean(x['predDockQ'] for x in rows),'meanOracleDockQ':statistics.mean(x['oracleDockQ'] for x in rows),'meanOracleGap':statistics.mean(x['oracleDockQ']-x['predDockQ'] for x in rows),'thresholdCounts':{str(t):{'pred':sum(x['predDockQ']>=t for x in rows),'oracle':sum(x['oracleDockQ']>=t for x in rows)} for t in [.23,.49,.8]}}
 out['rankCoverage']=[{'rankBudget':k,'nAcceptable':sum(x['firstAcceptablePredictedRank'] is not None and x['firstAcceptablePredictedRank']<=k for x in rows)} for k in sorted(set([1,2,5,10,20,seeds])) if k<=seeds]
 for field in ['pdb','authorCluster']:
  g=collections.defaultdict(list)
  for r in rows:g[str(r[field])].append(r)
  out[field+'EqualWeight']={'nGroups':len(g),'meanPredDockQ':statistics.mean(statistics.mean(x['predDockQ'] for x in a) for a in g.values()),'meanAcceptableFraction':statistics.mean(sum(x['predDockQ']>=.23 for x in a)/len(a) for a in g.values()),'groups':{k:{'n':len(a),'meanPredDockQ':statistics.mean(x['predDockQ'] for x in a),'nAcceptable':sum(x['predDockQ']>=.23 for x in a)} for k,a in g.items()}}
 return out
ap=argparse.ArgumentParser();ap.add_argument('--native',default='campaign-output/deepternary-native-geometry.json');ap.add_argument('--output',default='campaign-output/deepternary-released-scores.json');a=ap.parse_args()
np=P(a.native)
if not np.exists():np=next(P('.').rglob('deepternary-native-geometry.json'))
native=unwrap(json.loads(np.read_text()));assert len(native['rows'])==22
out={'schema':'deepternary-released-score-audit/2','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'receipts':[],'errors':[],'limits':['No inference was rerun. Scores are author-released metrics; released prediction coordinates are unavailable.','Row identifiers are absent from score tables. Joining the verified released/pinned list order remains an explicit provenance assumption.','PROTAC40-unbound and molecular-glue1-bound tasks are not a matched performance comparison.','Author clusters are grouping units, not independent efficacy measurements.','Native geometric gate failure is not pharmacological inactivity.']}
pb,pr=readone('result_20240515193524.txt');mb,mr=readone('result_20240515203824.txt');out['receipts'] += [pr,mr]
assert pr['sha256']=='dcf19e2d71ad98055770c2aa40ab6aded039f67fe80954eadb2a5220d9756cf2'
assert mr['sha256']=='16e4c0a3aa866040d55ec6374395974a68d97326203e08b047e766cb3c1d2b16'
pro=parse(pb);mgd=parse(mb);assert len(pro)==22 and len(mgd)==94
lb,lr=fetch('data/PROTAC/protac22.txt');out['receipts'].append(lr);plist=[x.split()[0] for x in lb.decode().splitlines() if x.strip() and not x.startswith('#')];assert plist==[r['case'] for r in native['rows']]
for r,n in zip(pro,native['rows']):
 r.update(case=n['case'],pdb=n['pdb'],authorCluster=n['authorCluster'],nativeMinimumProxyPoints=min(v['proxy']['contactPoints'] for v in n['metrics'].values()));r['nativeFloor12Failure']=r['nativeMinimumProxyPoints']<12
lb,lr=fetch('data/MolecularGlue/test_all.txt');cb,cr=fetch('data/MolecularGlue/test_clusters.json');out['receipts'] += [lr,cr];mlist=[x.split()[0] for x in lb.decode().splitlines() if x.strip() and not x.startswith('#')];assert len(mlist)==94
releasedTests=[x for x in P('campaign-output/deepternary-released-files').rglob('test.txt') if 'MGD' in x.parts];assert len(releasedTests)==1,[str(x) for x in releasedTests];b=releasedTests[0].read_bytes();releasedList=[x.split()[0] for x in b.decode().splitlines() if x.strip() and not x.startswith('#')];assert releasedList==mlist
out['receipts'].append({'path':str(releasedTests[0]),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});clusters=json.loads(cb);assignment={}
for k,v in clusters.items():
 for item in v['items']:assert item not in assignment;assignment[item]=k
for r,c in zip(mgd,mlist):r.update(case=c,pdb=c.split('_')[0],authorCluster=assignment[c])
assert all(r['predDockQ']==r['oracleDockQ'] for r in mgd)
out['protac']={'rows':pro,'summary':summary(pro,40),'floor12DescriptiveGroups':{str(f):{'n':len(g),'meanPredDockQ':statistics.mean(x['predDockQ'] for x in g)} for f in [False,True] if (g:=[r for r in pro if r['nativeFloor12Failure']==f])}}
out['molecularGlue']={'rows':mgd,'summary':summary(mgd,1),'legacyHitVersusDockQDisagreements':[{'case':r['case'],'dockq':r['predDockQ'],'legacyHitCounts':r['legacyHitCounts']} for r in mgd if bool(sum(r['legacyHitCounts']))!=(r['predDockQ']>=.23)]};out['embeddedConfigs']=[]
for p in P('campaign-output/deepternary-released-files').rglob('*.py'):
 if '/checkpoints/' not in str(p):continue
 text=p.read_text(errors='replace')
 if 'test_all.txt' not in text and 'protac22.txt' not in text:continue
 lines=text.splitlines();hits=[{'line':i+1,'text':s} for i,s in enumerate(lines) if re.search(r'protac22\.txt|test_all\.txt|val_interval|max_epochs|train_clusters',s)];out['embeddedConfigs'].append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'lines':hits})
b,r=fetch('predict_cpu.py');out['receipts'].append(r);lines=b.decode().splitlines();out['currentSourceClassifierProvenance']={'sourceGitRef':REF,'lines':[{'line':i+1,'text':s} for i,s in enumerate(lines) if 'def classify_prediction' in s or 'zip(fnat' in s],'limits':['Current source reverses the declared RMSD argument order and is not logically equivalent to canonical CAPRI.','Historical released-table executable identity is unresolved; no historical hit field was repaired.','MGD DockQ/legacy-hit disagreements do not establish that the present-source discrepancies caused them.']}
P(a.output).parent.mkdir(parents=True,exist_ok=True);P(a.output).write_text(json.dumps(out,indent=2));print('DEEPTERNARY_RELEASED_SCORES_BEGIN');print(json.dumps(out));print('DEEPTERNARY_RELEASED_SCORES_END')
