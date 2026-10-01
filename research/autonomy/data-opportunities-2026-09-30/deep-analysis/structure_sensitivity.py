#!/usr/bin/env python3
from __future__ import annotations
import ast,hashlib,io,json,pathlib,platform,sys,urllib.request
from datetime import datetime,timezone
import numpy as np
from Bio import __version__ as biopython_version
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from scipy.spatial import cKDTree
from scipy.stats import spearmanr
BASE='af7211708205b5189d8c537c1ce2a23aa4bea076';REPO='trimcrae/Rare-cancers';FLOORS=[0,6,10,12,16,20,24]
OUT=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'campaign-output/structure-sensitivity.json')
OUT.parent.mkdir(parents=True,exist_ok=True);CACHE=OUT.parent/'structure-coordinate-inputs';CACHE.mkdir(exist_ok=True)
receipts=[]
def fetch(url,expected_blob=None):
    req=urllib.request.Request(url,headers={'User-Agent':'Rare-cancers-public-coordinate-reanalysis/1'})
    with urllib.request.urlopen(req,timeout=45) as response:data=response.read(16*1024*1024+1)
    if len(data)>16*1024*1024:raise RuntimeError('16 MiB source limit')
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if expected_blob and blob!=expected_blob:raise RuntimeError('pinned blob mismatch: '+url)
    receipts.append({'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'gitBlobSha':blob});return data
rawbase='https://raw.githubusercontent.com/'+REPO+'/'+BASE+'/'
census=json.loads(fetch(rawbase+'research/modalities/nr4a3-induced-interface-census.json','b184a9d23198d7c56a6a69a87d60a2042ba5b67a'))
producer=fetch(rawbase+'research/modalities/nr4a3_induced_interface_census.py','31ec026e05aa336c4e7d4f1f03440306c35aadf2').decode()
constants={}
for node in ast.parse(producer).body:
    if isinstance(node,ast.Assign):
        for target in node.targets:
            if isinstance(target,ast.Name) and target.id in ('AA3','BACKBONE','ENTRY_CLASSES'):constants[target.id]=ast.literal_eval(node.value)
AA3,BACKBONE,CLASSES=constants['AA3'],constants['BACKBONE'],constants['ENTRY_CLASSES']
def at(d,key,i,default=None):
    v=d.get('_atom_site.'+key);return v[i] if v is not None else default
def read_chains(raw):
    d=MMCIF2Dict(io.StringIO(raw.decode('utf-8')));coords,res,atoms={},{},{};first=d.get('_atom_site.pdbx_PDB_model_num',['1'])[0]
    for i,group in enumerate(d['_atom_site.group_PDB']):
        if group!='ATOM' or at(d,'pdbx_PDB_model_num',i,'1')!=first:continue
        if at(d,'label_alt_id',i,'.') not in ('.','?','A'):continue
        if at(d,'type_symbol',i,'').upper() in ('H','D'):continue
        ch=at(d,'auth_asym_id',i,at(d,'label_asym_id',i));seq=at(d,'auth_seq_id',i,at(d,'label_seq_id',i));ins=at(d,'pdbx_PDB_ins_code',i,'.');comp,name=at(d,'label_comp_id',i),at(d,'label_atom_id',i)
        xyz=np.array([float(at(d,k,i)) for k in ('Cartn_x','Cartn_y','Cartn_z')]);key=(str(seq),'' if ins in ('.','?') else ins)
        coords.setdefault(ch,[]).append(xyz);atoms.setdefault(ch,[]).append((key,name,comp,xyz));res.setdefault(ch,{}).setdefault(key,{'comp':comp,'atoms':[]})['atoms'].append((name,xyz))
    return d,{k:np.array(v) for k,v in coords.items()},res,atoms
def probes(res,mode):
    pp,owners=[],[]
    for key,r in res.items():
        if r['comp'] not in AA3:continue
        ca=next((x for name,x in r['atoms'] if name=='CA'),None)
        if ca is None:continue
        pp.append(ca);owners.append(key)
        if mode!='ca':
            if mode=='centroid':
                side=[x for name,x in r['atoms'] if name not in BACKBONE];second=np.mean(side,axis=0) if side else ca
            else:second=next((x for name,x in r['atoms'] if name=='CB'),ca)
            pp.append(second);owners.append(key)
    return np.array(pp),owners
def profile(res,target,mode,lower=3.6,upper=6.0):
    query,owner=probes(res,mode)
    if len(query)==0:raise RuntimeError('missing CA query')
    dd=cKDTree(target).query(query,k=1)[0];shell=(dd>=lower)&(dd<=upper)
    return {'points':int(shell.sum()),'residues':len(set(owner[i] for i in np.flatnonzero(shell))),'hardPoints':int((dd<3).sum()),'softPoints':int(((dd>=3)&(dd<3.6)).sum()),'queryPoints':len(query),'minimumProbeDistanceA':float(dd.min())}
def heavy(source,target,cutoff):
    query=np.array([a[3] for a in source]);tree=cKDTree(target);dd=tree.query(query,k=1)[0];within=dd<=cutoff
    return {'atomsWithin':int(within.sum()),'residuesWithin':len(set(source[i][0] for i in np.flatnonzero(within))),'atomPairs':int(sum(len(v) for v in tree.query_ball_point(query,cutoff))),'minimumAtomDistanceA':float(dd.min())}
rows,entries,errors=[],[],[]
for saved in census['entries']:
    pid=saved['pdb_id']
    try:
        raw=fetch('https://files.rcsb.org/download/'+pid+'.cif');(CACHE/(pid+'.cif')).write_bytes(raw);d,coords,res,atoms=read_chains(raw)
        if d.get('_entry.id',[''])[0].upper()!=pid:raise RuntimeError('entry identity mismatch')
        meta={'pdbId':pid,'title':d.get('_struct.title',[''])[0],'method':d.get('_exptl.method',[]),'resolution':d.get('_refine.ls_d_res_high',[]),'classes':CLASSES.get(pid,{}).get('classes',[]),'nAtoms':int(sum(len(v) for v in coords.values())),'baselineNAtomsModel1':saved['n_atoms_model1']};entries.append(meta)
        spec=CLASSES.get(pid,{});allo={tuple(sorted(p)) for p in spec.get('allosteric_pairs',[])};drop={tuple(sorted(p)) for p in spec.get('exclude_pairs',[])}
        for pair in saved['chain_pairs']:
            a,b=pair['pair'];key=tuple(sorted((a,b)))
            if a not in coords or b not in coords:raise RuntimeError('saved chain absent: '+str((a,b)))
            induced=key not in drop and (bool(pair['ligand_bridged_by']) or key in allo)
            row={'pdbId':pid,'chains':[a,b],'what':pair['what'],'classes':meta['classes'],'induced':induced,'basis':'ligand_bridged_in_saved_census' if pair['ligand_bridged_by'] else ('allosteric_curated' if key in allo else 'contact_only'),'nResiduesWithCA':[len(probes(res[a],'ca')[0]),len(probes(res[b],'ca')[0])],'baselinePoints':[pair['arm_is_'+a]['n_contact_points'],pair['arm_is_'+b]['n_contact_points']],'directions':{}}
            for source,target in ((a,b),(b,a)):
                row['directions'][source]={'proxyCAcentroid':profile(res[source],coords[target],'centroid'),'proxyCACB':profile(res[source],coords[target],'cb'),'proxyCAonly':profile(res[source],coords[target],'ca'),'proxyCentroidNoClashExclusion':profile(res[source],coords[target],'centroid',0,6),'heavy4_5A':heavy(atoms[source],coords[target],4.5),'heavy6A':heavy(atoms[source],coords[target],6)}
            row['freshPoints']=[row['directions'][x]['proxyCAcentroid']['points'] for x in (a,b)];row['matchesBaselinePoints']=row['freshPoints']==row['baselinePoints'];rows.append(row)
    except Exception as exc:errors.append({'pdbId':pid,'error':repr(exc)})
def failures(group,mode,floor):
    by={}
    for r in group:
        vals=[r['directions'][x][mode]['points'] for x in r['chains']];by.setdefault(r['pdbId'],[]).append(min(vals)<floor)
    return {'pairsFailAtLeastOneDirection':sum(sum(v) for v in by.values()),'nPairs':len(group),'entriesAnyCopyFail':sum(any(v) for v in by.values()),'entriesEveryCopyFail':sum(all(v) for v in by.values()),'nEntries':len(by),'byEntry':{k:{'fails':sum(v),'pairs':len(v)} for k,v in by.items()}}
summary={}
for cls in ('degrader_or_glue','tcip','cid_proximity','induced_transcriptional'):
    group=[r for r in rows if r['induced'] and cls in r['classes']];summary[cls]={mode:{str(f):failures(group,mode,f) for f in FLOORS} for mode in ('proxyCAcentroid','proxyCACB','proxyCAonly')}
dg=[r for r in rows if r['induced'] and 'degrader_or_glue' in r['classes']];leave=[]
for pid in sorted(set(r['pdbId'] for r in dg)):
    f=failures([r for r in dg if r['pdbId']!=pid],'proxyCAcentroid',12);leave.append({'omittedEntry':pid,**f,'pairFraction':f['pairsFailAtLeastOneDirection']/f['nPairs'],'entryAnyFraction':f['entriesAnyCopyFail']/f['nEntries']})
def rank(mode,key):
    if len(dg)<3:return None
    value=float(spearmanr([min(r['freshPoints']) for r in dg],[min(r['directions'][c][mode][key] for c in r['chains']) for r in dg]).statistic)
    return {'spearmanRho':value if np.isfinite(value) else None,'scope':'Descriptive ranks among nested selected structural pairs; no p-value or population inference.'}
doc={'schema':'coordinate-interface-sensitivity/1','completedAt':datetime.now(timezone.utc).isoformat(),'sourceCensusCommit':BASE,'sourceCensusBlob':'b184a9d23198d7c56a6a69a87d60a2042ba5b67a','sourceProducerBlob':'31ec026e05aa336c4e7d4f1f03440306c35aadf2','fixedDesign':{'floors':FLOORS,'shellA':[3.6,6.0],'heavyCutoffsA':[4.5,6.0],'firstModelOnly':True,'altloc':['.','?','A'],'hydrogensExcluded':True,'sample':'All 22 entries and saved chain pairs in prior census; no outcome labels.','resampling':'Leave one entire PDB entry out; copies not independent.','coordinates':'Fresh raw mmCIF ATOM records; source bytes saved with SHA-256.'},'software':{'python':platform.python_version(),'numpy':np.__version__,'biopython':biopython_version},'receipts':receipts,'entries':entries,'pairMetrics':rows,'summary':summary,'leaveOneEntryOutDegraderFloor12':leave,'descriptiveRankAgreement':{'heavy4_5AResidues':rank('heavy4_5A','residuesWithin'),'heavy6AResidues':rank('heavy6A','residuesWithin')},'baselineMatch':{'pairs':len(rows),'matching':sum(r['matchesBaselinePoints'] for r in rows),'mismatches':[{'pdbId':r['pdbId'],'chains':r['chains'],'saved':r['baselinePoints'],'fresh':r['freshPoints']} for r in rows if not r['matchesBaselinePoints']]},'errors':errors,'limits':['Convenience sample of deposited complexes, no failed-molecule comparison or activity labels.','Copies, targets and recruiters clustered; no efficacy classifier or recruiter effect.','Only saved contacts evaluated; crystal lattice and absent assembly partners may limit interpretation.','Floor-12 test is count test only; hard/soft gates separately reported, not declared passed.','No affinity, activity, cooperativity, transcription, clinical selectivity or disease-specific claim.']}
OUT.write_text(json.dumps(doc,indent=2)+'\n')
print('STRUCTURE_RESULT_BEGIN');print(json.dumps(doc,separators=(',',':')));print('STRUCTURE_RESULT_END')
if errors:sys.exit(1)
