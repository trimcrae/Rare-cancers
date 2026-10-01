#!/usr/bin/env python3
import argparse,datetime,hashlib,io,json,pathlib
P=pathlib.Path
ap=argparse.ArgumentParser();ap.add_argument('--output',default='campaign-output/deepternary-extra-native-control.json');a=ap.parse_args();choices=[]
for p in P(__file__).parent.glob('*.py'):
 if p.name==P(__file__).name:continue
 t=p.read_text()
 if 'archive=None;expected=' in t and 'def profile' not in t:choices.append((p,t))
assert len(choices)==1,[str(x[0]) for x in choices];source,text=choices[0];ns={'__file__':str(source),'__name__':'_native_control_setup'};exec(compile(text.split('archive=None;expected=',1)[0],str(source),'exec'),ns);roots=P('campaign-output/deepternary-released-files');files=[p for p in roots.rglob('gt_complex.pdb') if '7PI4_A_D_7QB' in p.parts];assert len(files)==1,[str(x) for x in files];p=files[0];raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert len(raw)==274445 and sha=='0bd6afb5ca28eb42367d1b1fb42d6fcb5fe0a8fcf224d91cae4a8f530d8c988b';AA3=ns['AA3'];np=ns['np'];parser=ns['PDBParser'](QUIET=True);chains={}
for ch in parser.get_structure('7PI4_extra',io.StringIO(raw.decode()))[0]:
 atoms=[]
 for res in ch:
  if res.id[0]!=' ' or res.get_resname() not in AA3:continue
  for atom in res.get_unpacked_list():
   if atom.element in ('H','D') or atom.get_altloc() not in (' ','A'):continue
   atoms.append({'seq':str(res.id[1]),'ins':res.id[2].strip(),'comp':res.get_resname(),'name':atom.get_name(),'xyz':np.asarray(atom.coord,dtype=float)})
 if len(atoms)>=40:chains[ch.id]=atoms
assert len(chains)==2,list(chains);x,y=list(chains);metrics={x:ns['profile'](chains[x],chains[y]),y:ns['profile'](chains[y],chains[x])};minimum=min(v['proxy']['contactPoints'] for v in metrics.values());out={'schema':'deepternary-extra-released-native-control/1','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'case':'7PI4_A_D_7QB','source':{'path':str(p),'bytes':len(raw),'sha256':sha},'metricSetup':{'path':str(source),'sha256':hashlib.sha256(text.encode()).hexdigest(),'onlyPrefixExecuted':True},'receipts':ns['receipts'],'chains':[x,y],'metrics':metrics,'fixedFloorFailures':{str(f):minimum<f for f in [0,6,10,12,16,20,24]},'limits':['Additional released preprocessed control outside frozen22score list.','Do not append to22case14entry7cluster denominators.','No predictions, new inference, potency or biologicalassembly reconstruction.']};P(a.output).parent.mkdir(parents=True,exist_ok=True);P(a.output).write_text(json.dumps(out,indent=2));print('DEEPTERNARY_EXTRA_NATIVE_BEGIN');print(json.dumps(out));print('DEEPTERNARY_EXTRA_NATIVE_END')
