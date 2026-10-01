import ast,hashlib,io,itertools,json,pathlib,sys,urllib.request
from collections import defaultdict
from datetime import datetime,timezone
import numpy as np
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from scipy.spatial import cKDTree
BASE='https://raw.githubusercontent.com/trimcrae/Rare-cancers/af7211708205b5189d8c537c1ce2a23aa4bea076/';INDIR=pathlib.Path('campaign-output/structure-coordinate-inputs');OUT=pathlib.Path('campaign-output/structure-omitted-pairs.json');OUT.parent.mkdir(parents=True,exist_ok=True);receipts=[]
def get(path,blob):
 with urllib.request.urlopen(urllib.request.Request(BASE+path,headers={'User-Agent':'EMC-all-pair-audit'}),timeout=90) as r:raw=r.read()
 actual=hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()
 if actual!=blob:raise ValueError('pinned source mismatch '+path)
 receipts.append({'url':BASE+path,'gitBlob':blob,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)});return raw
census=json.loads(get('research/modalities/nr4a3-induced-interface-census.json','b184a9d23198d7c56a6a69a87d60a2042ba5b67a'));producer=get('research/modalities/nr4a3_induced_interface_census.py','31ec026e05aa336c4e7d4f1f03440306c35aadf2').decode();constants={}
for node in ast.parse(producer).body:
 if isinstance(node,ast.Assign):
  for t in node.targets:
   if isinstance(t,ast.Name) and t.id in ('AA3','BACKBONE','NOT_A_LIGAND','ENTRY_CLASSES'):constants[t.id]=ast.literal_eval(node.value)
AA3=constants['AA3'];BACKBONE=constants['BACKBONE'];BUFFER=constants['NOT_A_LIGAND'];CLASSES=constants['ENTRY_CLASSES']
def at(d,key,i,default='.'):
 v=d.get(key)
 if v is None:return default
 return v[i] if isinstance(v,list) else v
def parse(raw):
 d=MMCIF2Dict(io.StringIO(raw.decode()));atoms=[];first=at(d,'_atom_site.pdbx_PDB_model_num',0,'1')
 for i in range(len(d['_atom_site.id'])):
  if at(d,'_atom_site.pdbx_PDB_model_num',i,'1')!=first:continue
  if at(d,'_atom_site.label_alt_id',i) not in ('.','?','A'):continue
  if at(d,'_atom_site.type_symbol',i).upper() in ('H','D'):continue
  ch=at(d,'_atom_site.auth_asym_id',i,at(d,'_atom_site.label_asym_id',i));seq=at(d,'_atom_site.auth_seq_id',i,at(d,'_atom_site.label_seq_id',i));ins=at(d,'_atom_site.pdbx_PDB_ins_code',i);ins='' if ins in ('.','?') else ins
  atoms.append({'chain':ch,'seq':seq,'ins':ins,'comp':at(d,'_atom_site.label_comp_id',i),'name':at(d,'_atom_site.label_atom_id',i).strip(chr(34)+chr(39)),'het':at(d,'_atom_site.group_PDB',i)=='HETATM','xyz':np.array([float(at(d,'_atom_site.Cartn_'+axis,i)) for axis in 'xyz'])})
 return d,atoms
def profile(aa,bb):
 residues=defaultdict(list)
 for a in aa:
  if a['comp'] in AA3:residues[(a['seq'],a['ins'],a['comp'])].append(a)
 probes=[];owners=[]
 for key,v in residues.items():
  ca=next((a['xyz'] for a in v if a['name']=='CA'),None)
  if ca is None:continue
  side=[a['xyz'] for a in v if a['name'] not in BACKBONE];probes.extend([ca,np.mean(side,axis=0) if side else ca]);owners.extend([key,key])
 target=np.array([a['xyz'] for a in bb]);tree=cKDTree(target)
 if probes:
  ds=tree.query(np.array(probes),k=1)[0];mask=(ds>=3.6)&(ds<=6.);proxy={'contactPoints':int(mask.sum()),'contactResidues':len({owners[i] for i in np.flatnonzero(mask)}),'hardPoints':int((ds<3.).sum()),'softPoints':int(((ds>=3.)&(ds<3.6)).sum()),'queryPoints':len(probes)}
 else:proxy={'contactPoints':0,'contactResidues':0,'hardPoints':0,'softPoints':0,'queryPoints':0}
 ds=tree.query(np.array([a['xyz'] for a in aa]),k=1)[0]
 return {'proxy':proxy,'minimumHeavyAtomDistanceA':float(ds.min()),'heavyContactResidues4_5A':len({(aa[i]['seq'],aa[i]['ins']) for i in np.flatnonzero(ds<=4.5)}),'heavyContactResidues6A':len({(aa[i]['seq'],aa[i]['ins']) for i in np.flatnonzero(ds<=6.)})}
rows=[];entries=[];errors=[]
for old in census['entries']:
 pid=old['pdb_id'];path=INDIR/(pid+'.cif')
 try:
  raw=path.read_bytes();d,atoms=parse(raw)
  if at(d,'_entry.id',0).upper()!=pid:raise ValueError('entry identity mismatch')
  receipts.append({'input':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()});total=defaultdict(list)
  for a in atoms:
   if not a['het']:total[a['chain']].append(a)
  chains=sorted(ch for ch,aa in total.items() if sum(a['comp'] in AA3 for a in aa)>=max(40,.5*len(aa)));trees={ch:cKDTree(np.array([a['xyz'] for a in total[ch]])) for ch in chains};lig=defaultdict(list)
  for a in atoms:
   if a['het'] and a['comp'] not in AA3 and a['comp'] not in BUFFER:lig[(a['chain'],a['seq'],a['ins'],a['comp'])].append(a['xyz'])
  spans=defaultdict(list)
  for key,pts in lig.items():
   if len(pts)<12:continue
   touched=[ch for ch,tree in trees.items() if int((tree.query(np.array(pts),k=1)[0]<=4.5).sum())>=3]
   for pair in itertools.combinations(touched,2):spans[tuple(sorted(pair))].append({'ligand':key[3],'ligandChain':key[0],'ligandResidue':key[1],'heavyAtoms':len(pts)})
  spec=CLASSES.get(pid,{});allo={tuple(sorted(p)) for p in spec.get('allosteric_pairs',[])};drop={tuple(sorted(p)) for p in spec.get('exclude_pairs',[])};saved={tuple(sorted(p['pair'])) for p in old['chain_pairs']}
  for a,b in itertools.combinations(chains,2):
   pair=(a,b);eligible=pair in spans or pair in allo;metrics={a:profile(total[a],total[b]),b:profile(total[b],total[a])};zero=all(metrics[ch]['proxy']['contactPoints']==0 for ch in pair)
   rows.append({'pdb':pid,'chains':[a,b],'classes':spec.get('classes',[]),'ligandSpanned':pair in spans,'ligands':spans.get(pair,[]),'allostericCurated':pair in allo,'constitutiveExcluded':pair in drop,'inducedEligible':eligible and pair not in drop,'presentInOldSavedPairs':pair in saved,'bothDirectionsZeroProxyContacts':zero,'omittedEligiblePair':eligible and pair not in drop and pair not in saved,'metrics':metrics})
  entries.append({'pdb':pid,'nProteinChains':len(chains),'nAllProteinPairs':len(chains)*(len(chains)-1)//2,'depositedAssemblyDefinitions':{k:v for k,v in d.items() if k.startswith('_pdbx_struct_assembly_gen.')}})
 except Exception as e:errors.append({'pdb':pid,'error':repr(e)})
summary={}
for cls in ['degrader_or_glue','tcip','cid_proximity','induced_transcriptional']:
 group=[r for r in rows if r['inducedEligible'] and cls in r['classes']];by=defaultdict(list)
 for r in group:by[r['pdb']].append(min(r['metrics'][ch]['proxy']['contactPoints'] for ch in r['chains'])<12)
 summary[cls]={'nEligiblePairs':len(group),'nPdb':len(by),'floor12PairFails':sum(sum(v) for v in by.values()),'floor12PdbAnyFail':sum(any(v) for v in by.values()),'floor12PdbEveryFail':sum(all(v) for v in by.values()),'omittedEligiblePairs':[{'pdb':r['pdb'],'chains':r['chains'],'bothDirectionsZero':r['bothDirectionsZeroProxyContacts']} for r in group if r['omittedEligiblePair']]}
doc={'schema':'all-protein-pair-eligibility-audit/2','completedAt':datetime.now(timezone.utc).isoformat(),'receipts':receipts,'entries':entries,'rows':rows,'summary':summary,'errors':errors,'limits':['IndependentMMCIF2Dict parsing of fresh deposited first-model asymmetrical-unit coordinates.','Protein eligibility>=40AAheavyatoms and>=50%ATOM AA; ligands>=12nonbuffer/nonAA HET heavyatoms and>=3within4.5A of each chain.','All pairs counted before zero-contact exclusion; ligand and curated allosteric eligibility visible, constitutive exclusions retained.','Asymmetric-unit ligand spanning does not certify a biological assembly. Deposited assembly instructions are recorded, not transformed or inferred.','No molecular failure/activity labels or efficacy classifier.']}
OUT.write_text(json.dumps(doc,indent=2)+'\n');print('STRUCTURE_OMITTED_BEGIN');print(json.dumps(doc,separators=(',',':')));print('STRUCTURE_OMITTED_END')
if errors:sys.exit(1)
