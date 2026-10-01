import ast,hashlib,io,json,pathlib,sys,urllib.request,zipfile
from collections import defaultdict
from datetime import datetime,timezone
import numpy as np
from Bio.PDB import PDBParser
from scipy.spatial import cKDTree
DT='https://raw.githubusercontent.com/youqingxiaozhua/DeepTernary/827821dccca31a5918bd0355e2d6bf70c072b6dd/';ROOT='https://raw.githubusercontent.com/trimcrae/Rare-cancers/af7211708205b5189d8c537c1ce2a23aa4bea076/';OUT=pathlib.Path('campaign-output/deepternary-native-geometry.json');OUT.parent.mkdir(parents=True,exist_ok=True);receipts=[]
def get(base,path,sha):
 with urllib.request.urlopen(urllib.request.Request(base+path,headers={'User-Agent':'EMC-native-geometry'}),timeout=90) as r:raw=r.read()
 if hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()!=sha:raise ValueError('pinned source mismatch '+path)
 receipts.append({'url':base+path,'gitBlob':sha,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)});return raw
cases=get(DT,'data/PROTAC/protac22.txt','94339bff9542c09fd0c44b8ae714e0f57524ba6e').decode().splitlines();clusters=json.loads(get(DT,'data/PROTAC/test_clusters.json','191111dc60a9bca29df2eca28cef3367bf706ec7'));cluster={case:[i for i,c in enumerate(clusters) if case in c['items']] for case in cases}
if any(len(v)!=1 for v in cluster.values()):raise ValueError('ambiguous case-cluster mapping')
raw=get(ROOT,'research/modalities/nr4a3_induced_interface_census.py','31ec026e05aa336c4e7d4f1f03440306c35aadf2');constants={}
for node in ast.parse(raw.decode()).body:
 if isinstance(node,ast.Assign):
  for target in node.targets:
   if isinstance(target,ast.Name) and target.id in ('AA3','BACKBONE'):constants[target.id]=ast.literal_eval(node.value)
AA3=constants['AA3'];BACKBONE=constants['BACKBONE'];helper=pathlib.Path(__file__).with_name('structure_omitted_pairs.py');function=next(n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='profile');namespace={'np':np,'defaultdict':defaultdict,'cKDTree':cKDTree,'AA3':AA3,'BACKBONE':BACKBONE};exec(compile(ast.Module(body=[function],type_ignores=[]),str(helper),'exec'),namespace);profile=namespace['profile'];receipts.append({'metricHelper':str(helper),'sha256':hashlib.sha256(helper.read_bytes()).hexdigest(),'executedFunction':'profile only; job body not imported'})
archive=None;expected='1eb43229480459730f7993f3c22ac42e9a1a5aee60d747088eb35aac4f3d18c3'
for p in pathlib.Path('campaign-output/deepternary-released-files').rglob('*.zip'):
 if p.stat().st_size!=151480895:continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
 if h.hexdigest()==expected:archive=p;break
if archive is None:raise FileNotFoundError('verified151MB output release must be acquired first')
receipts.append({'archive':str(archive),'bytes':151480895,'publisherSha256':expected,'verified':True});parser=PDBParser(QUIET=True);rows=[];errors=[]
with zipfile.ZipFile(archive) as z:
 names=z.namelist()
 for case in cases:
  hits=[n for n in names if n.split('/')[-1]=='gt_complex.pdb' and case in n.split('/')]
  if len(hits)!=1:errors.append({'case':case,'error':'expected one released native reference','matches':hits});continue
  member=hits[0];raw=z.read(member)
  try:
   proteins={}
   for chain in parser.get_structure(case,io.StringIO(raw.decode()))[0]:
    aa=[]
    for res in chain:
     if res.id[0]!=' ' or res.get_resname() not in AA3:continue
     for atom in res.get_unpacked_list():
      if atom.element in ('H','D') or atom.get_altloc() not in (' ','A'):continue
      aa.append({'seq':str(res.id[1]),'ins':res.id[2].strip(),'comp':res.get_resname(),'name':atom.get_name(),'xyz':np.asarray(atom.coord,dtype=float)})
    if len(aa)>=40:proteins[chain.id]=aa
   if len(proteins)!=2:raise ValueError('expected exactly2 protein chains, got '+str(list(proteins)))
   a,b=list(proteins);rows.append({'case':case,'pdb':case.split('_')[0],'authorCluster':cluster[case][0],'member':member,'sha256':hashlib.sha256(raw).hexdigest(),'chains':[a,b],'metrics':{a:profile(proteins[a],proteins[b]),b:profile(proteins[b],proteins[a])}})
  except Exception as e:errors.append({'case':case,'error':repr(e)})
def summary(floor,omit=None):
 group=[r for r in rows if r['authorCluster']!=omit];pdb=defaultdict(list);cl=defaultdict(list)
 for r in group:
  fail=min(r['metrics'][ch]['proxy']['contactPoints'] for ch in r['chains'])<floor;pdb[r['pdb']].append(fail);cl[r['authorCluster']].append(fail)
 return {'nCases':len(group),'casesFail':sum(sum(v) for v in pdb.values()),'nPdb':len(pdb),'pdbAnyCopyFail':sum(any(v) for v in pdb.values()),'pdbEveryCopyFail':sum(all(v) for v in pdb.values()),'nAuthorClusters':len(cl),'clustersAnyCaseFail':sum(any(v) for v in cl.values()),'clustersEveryCaseFail':sum(all(v) for v in cl.values()),'byPdb':{k:{'cases':len(v),'failures':sum(v)} for k,v in pdb.items()}}
doc={'schema':'deepternary-native-contact-floor/2','completedAt':datetime.now(timezone.utc).isoformat(),'receipts':receipts,'nExpectedCases':22,'nExpectedPdb':14,'nExpectedAuthorClusters':7,'rows':rows,'fixedFloorSweep':{str(f):summary(f) for f in [0,6,10,12,16,20,24]},'leaveOneAuthorClusterOutFloor12':[{'omittedCluster':c,**summary(12,c)} for c in sorted({r['authorCluster'] for r in rows})],'errors':errors,'limits':['All author22cases admitted before contacts; no zero-contact selection.','Native solved references, not failed/active molecule or efficacy validation.','Copies and target/recruiter systems nested; entry/cluster summaries descriptive.','Released native PDBs may be preprocessed; not fresh deposited biological-assembly audit.','No prediction rankings, affinity, potency, clinical selectivity or EMC result.']}
OUT.write_text(json.dumps(doc,indent=2)+'\n');print('DEEPTERNARY_NATIVE_GEOMETRY_BEGIN');print(json.dumps(doc,separators=(',',':')));print('DEEPTERNARY_NATIVE_GEOMETRY_END')
if errors:sys.exit(1)
