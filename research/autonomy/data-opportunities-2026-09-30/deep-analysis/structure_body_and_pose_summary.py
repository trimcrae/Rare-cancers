#!/usr/bin/env python3
import argparse,datetime,hashlib,json,math,pathlib,statistics,urllib.request
P=pathlib.Path
ap=argparse.ArgumentParser();ap.add_argument('--pairs',default='campaign-output/structure-all-pairs.json');ap.add_argument('--output',default='campaign-output/structure-body-and-pose-summary.json');a=ap.parse_args();p=P(a.pairs)
if not p.exists():
 choices=list(P('.').rglob('structure-all-pairs-actual.json'));assert len(choices)==1,[str(x) for x in choices];p=choices[0]
b=p.read_bytes();d=json.loads(b)
while 'result' in d and isinstance(d['result'],dict):d=d['result']
rows=[r for r in d['rows'] if r['pdb']=='9MZA'];assert len(rows)==6;pairs={frozenset(r['chains']):r for r in rows}
def body(one,two):
 def direction(source,target):
  out={'proxy':{k:0 for k in ['contactPoints','contactResidues','hardPoints','softPoints','queryPoints']},'heavyContactResidues4_5A':0,'heavyContactResidues6A':0,'minimumHeavyAtomDistanceA':float('inf'),'proofByChain':[]}
  for s in source:
   profiles=[pairs[frozenset([s,t])]['metrics'][s] for t in target];assert len({x['proxy']['queryPoints'] for x in profiles})==1;active=[x for x in profiles if any(x['proxy'][k] for k in ['contactPoints','hardPoints','softPoints']) or x['heavyContactResidues6A']];assert len(active)<=1,'Cannot derive union when nonzero targets overlap; must return to coordinates';q=active[0] if active else profiles[0]
   for k in out['proxy']:out['proxy'][k]+=q['proxy'][k]
   for k in ['heavyContactResidues4_5A','heavyContactResidues6A']:out[k]+=q[k]
   out['minimumHeavyAtomDistanceA']=min(out['minimumHeavyAtomDistanceA'],*(x['minimumHeavyAtomDistanceA'] for x in profiles));out['proofByChain'].append({'source':s,'nNonzeroTargetProfiles':len(active),'nTargetProfiles':len(profiles)})
  return out
 return {'one':one,'two':two,'forward':direction(one,two),'reverse':direction(two,one),'countOnlyFloor12Pass':min(direction(one,two)['proxy']['contactPoints'],direction(two,one)['proxy']['contactPoints'])>=12}
out={'schema':'structure-body-and-saved-pose-audit/2','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'receipts':[{'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}],'nineMZA':{'depositedAssemblyDefinitions':next(x for x in d['entries'] if x['pdb']=='9MZA')['depositedAssemblyDefinitions'],'allSixPairs':rows,'bodyGroups':[body(['A','C'],['B']),body(['A','C'],['D']),body(['A','C'],['B','D'])],'p300CopyMinimumDistanceA':pairs[frozenset(['B','D'])]['metrics']['B']['minimumHeavyAtomDistanceA'],'proof':'Source-chain identities retained. At most one target per source has any proxy hard/soft/contact point or heavyatom contact within6Å, so union counts equal sole nonzero profile.','limits':['Pooling separate p300 copies changes counted molecular body; no one recruited-copy acceptance.','One TCIP entry; broader transcriptional controls separate.']},'savedPoseCases':[],'errors':[]}
def get(path,blob):
 u='https://raw.githubusercontent.com/trimcrae/Rare-cancers/af7211708205b5189d8c537c1ce2a23aa4bea076/'+path
 with urllib.request.urlopen(u,timeout=90) as f:b=f.read()
 assert hashlib.sha1(('blob '+str(len(b))+'\0').encode()+b).hexdigest()==blob;out['receipts'].append({'url':u,'gitBlob':blob,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)});return json.loads(b)
pro=get('research/modalities/selcal-deepternary-poscontrol.json','d0a98057626e29db6dbf707780a24ec104dc4a81');head=get('research/modalities/selcal-deepternary-headtohead.json','a1cf19266500630a98c9e55d7f0b8d3fda23e748');arm=next(x for x in head['arms'] if x['arm']=='selcal_smarca2')
for label,poses in [('6HAX_B_A_FWZ',pro['poses']),('9DTY_native_SMARCA2_VHL',arm['scored'])]:
 q=sorted(float(x['DockQ']) for x in poses);n=len(q);assert n==16;curves=[]
 for m in [1,2,4,8,16]:
  denom=math.comb(n,m);r={'m':m,'expectedOracleMaximum':sum(v*math.comb(i,m-1)/denom for i,v in enumerate(q) if i>=m-1)}
  for t in [.23,.49,.8]:below=sum(v<t for v in q);r['pOracleAtLeast'+str(t)]=1-(math.comb(below,m)/denom if below>=m else 0)
  curves.append(r)
 out['savedPoseCases'].append({'case':label,'n':n,'mean':statistics.mean(q),'ordinaryMedian':statistics.median(q),'upperMiddleOrderStatistic':q[n//2],'best':max(q),'thresholdCounts':{str(t):sum(x>=t for x in q) for t in [.23,.49,.8]},'finiteSavedSubsetOracleCurves':curves})
out['savedPoseLimits']=['Only32 completed poses in2known-pocket systems.','Oracle uses native-reference scores, not predicted ranking.','Exact finite subset probabilities do not estimate future-seed success.','Rejected SMARCA4 input is not a negative prediction.','Data-horizon membership is not training-list membership.'];P(a.output).parent.mkdir(parents=True,exist_ok=True);P(a.output).write_text(json.dumps(out,indent=2));print('STRUCTURE_BODY_POSE_BEGIN');print(json.dumps(out));print('STRUCTURE_BODY_POSE_END')
