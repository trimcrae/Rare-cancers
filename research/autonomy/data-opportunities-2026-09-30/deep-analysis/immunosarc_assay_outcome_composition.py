import csv,hashlib,io,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
from urllib.request import Request,urlopen
REV='b71c3373bc182f9c647a6f7bc1fbd641d24db917';BASE='https://raw.githubusercontent.com/mskcc/ImmunoSarc/'+REV+'/';O=Path('campaign-output/immunosarc-outcome-composition');O.mkdir(parents=True,exist_ok=True)
R=dict(schema='immunosarc-assay-outcome-composition/1',sourceRevision=REV,sources=[],errors=[],limits=['Public S01 NCT03282344 is not IMMUNOSARC1 and contains no EMC','Availability on treatment or paired availability is future-defined, with histology/clinical selection','Descriptive KM/RMST/response composition, not causal bias correction or informative-missingness identification','RNA score availability is not complete raw RNA count access; CD8 quartile availability is not complete numeric IHC access','No treatment efficacy comparison or subgroup benefit'])
def get(path,sha):
 with urlopen(Request(BASE+path,headers={'User-Agent':'Rare-cancers-assay-outcome-audit'}),timeout=60) as x:b=x.read(16*1024*1024+1)
 if len(b)>16*1024*1024:raise ValueError('16MiB cap')
 git=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest();assert git==sha,(path,git,sha);R['sources'].append(dict(path=path,url=BASE+path,bytes=len(b),gitBlobSHA=git,sha256=hashlib.sha256(b).hexdigest()));(O/Path(path).name).write_bytes(b);return b.decode('utf-8-sig')
def table(s):return list(csv.DictReader(io.StringIO(s),delimiter='\t'))
def numeric(x):
 try:v=float(x);return v if math.isfinite(v) else None
 except (TypeError,ValueError):return None
def km(v):
 assert v;risk=len(v);s=1.;med=None;steps=[]
 for t in sorted({x['time'] for x in v}):
  d=sum(x['time']==t and x['event'] for x in v);c=sum(x['time']==t and not x['event'] for x in v)
  if d:s*=1-d/risk
  if med is None and s<=.5:med=t
  steps.append(dict(time=t,atRisk=risk,events=d,censors=c,survival=s));risk-=d+c
 return dict(n=len(v),events=sum(x['event'] for x in v),medianDays=med,steps=steps,lastObserved=max(x['time'] for x in v))
def rmst(q,tau):
 assert tau<=q['lastObserved'];last=0.;s=1.;area=0.
 for z in q['steps']:
  t=min(tau,z['time']);area+=(t-last)*s;last=t
  if z['time']>=tau:return area
  s=z['survival']
 return area+(tau-last)*s
def composition(ids,patients):
 q=[patients[k] for k in sorted(ids,key=int)];v=[dict(time=x['canonicalPFSDays'],event=x['PFSevent']) for x in q];a=km(v);tau=168.;return dict(n=len(q),subjectIDs=sorted(ids,key=int),cohortCounts=dict(Counter(x['Cohort'] for x in q)),responseCounts=dict(Counter(x['BestResponse'] for x in q)),KM=a,RMSTtauDays=tau,RMSTDays=rmst(a,tau))
try:
 ps=table(get('Figures/data/PatientSourceData.txt','8e65abf4208c2e6d9b96d8271752bfde4c85f443'));ss=table(get('Figures/data/SampleSourceData.txt','c3d9ee850299eb8930788468c87754b58d5a67f8'));r=get('Figures/Figure2.R','d706a9e8241f7b1aedea82917907429981337be1');assert re.search(r'PFSCensor\s*==\s*1',r);R['eventCoding']='PFSCensor==1 directly verified in pinned Figure2.R; not inferred from variable name';assert len(ps)==77 and len(ss)==133
 patients={str(x['Subject']):dict(x) for x in ps};assert len(patients)==77;assert all(x['Cohort'].lower().find('extraskeletal myxoid')<0 for x in ps);corrections=[]
 for k,x in patients.items():
  t=numeric(x['PFS.days']);assert t is not None and t>=0;e=numeric(x['PFSCensor']);assert e in (0,1);t2=float(round(t)) if abs(t-round(t))<1e-9 else t
  if t2!=t:corrections.append(dict(subject=k,literal=x['PFS.days'],normalized=t2,absoluteDifference=abs(t2-t)))
  x.update(canonicalPFSDays=t2,PFSevent=e==1)
 allids=set(patients);by=defaultdict(list)
 for x in ss:
  k=str(x['Subject']);assert k in patients;assert x['Cohort']==patients[k]['Cohort'] and x['BestResponse']==patients[k]['BestResponse'];t=numeric(x['PFS.days']);e=numeric(x['PFSCensor']);assert t is not None and abs(t-patients[k]['canonicalPFSDays'])<1e-8 and e==float(patients[k]['PFSCensor']);by[(k,x['SampleTimepoint'])].append(x)
 R['sourceDimensions']=dict(clinicalRows=len(ps),uniqueSubjects=len(patients),missingPatientIDs=sum(str(x['PatientID']).upper() in ('','NA','N/A','NAN') for x in ps),sampleRows=len(ss),timepointRows=dict(Counter(x['SampleTimepoint'] for x in ss)),sampleSubjects=len({x['Subject'] for x in ss}),duplicateSubjectTimepoints=[dict(subject=k[0],timepoint=k[1],rows=len(v)) for k,v in by.items() if len(v)>1]);R['floatingDayCorrections']=corrections;R['availabilityAnalyses']=[]
 immune=['T-cell','T-cell (CD8)','NK cell','B-cell','Macrophage/Monocyte','Myeloid dendritic cell','Neutrophil','Endothelial cell','Cancer-associated fibroblast']
 assert all((numeric(x['T-cell (CD8)']) is not None)==all(numeric(x[c]) is not None for c in immune) for x in ss)
 R['immuneScoreSentinelDefinition']='Finite T-cell(CD8) availability matches all9finite scores in every133source rows, verified exactly'
 for measure,column in [('RNAImmuneScore','T-cell (CD8)'),('CD8IHCQuartile','CD8.IHCquart')]:
  base={x['Subject'] for x in ss if x['SampleTimepoint']=='Baseline' and numeric(x[column]) is not None};on={x['Subject'] for x in ss if x['SampleTimepoint']=='On-Treatment' and numeric(x[column]) is not None}
  for kind,ids in [('baseline',base),('on',on),('paired',base&on)]:R['availabilityAnalyses'].append(dict(measure=measure,literalColumn=column,kind=kind,available=composition(ids,patients),unavailable=composition(allids-ids,patients)))
 actual={(x['measure'],x['kind']):x['available']['n'] for x in R['availabilityAnalyses']};assert actual=={('RNAImmuneScore','baseline'):41,('RNAImmuneScore','on'):38,('RNAImmuneScore','paired'):31,('CD8IHCQuartile','baseline'):47,('CD8IHCQuartile','on'):32,('CD8IHCQuartile','paired'):23};R['allClinicalPFS']=composition(allids,patients);R['patientLiteralAndCanonicalRows']=list(patients.values())
except Exception as e:R['errors'].append(dict(type=type(e).__name__,message=str(e)))
(O/'immunosarc-assay-outcome-composition.json').write_text(json.dumps(R,indent=2)+'\n');print('IMMUNOSARC_OUTCOME_COMPOSITION_BEGIN');print(json.dumps(R,separators=(',',':')));print('IMMUNOSARC_OUTCOME_COMPOSITION_END')
if R['errors']:raise SystemExit(1)
