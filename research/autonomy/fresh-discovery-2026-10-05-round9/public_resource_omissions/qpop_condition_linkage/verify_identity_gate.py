"""Verify QPOP source and categorical eligibility bindings without response values.
Default verifies hashes/records only. --replay-crops requires NY computer-use window.
--write records this initial pre-freeze audit; do not rewrite a frozen audit.
"""
from pathlib import Path
import json,hashlib,datetime,shutil,sys,subprocess,zipfile
from zoneinfo import ZoneInfo
P=Path(__file__).resolve().parent
def j(n):return json.loads((P/n).read_text())
def verify(b,base=P):
 f=Path(b['path']);f=f if f.is_absolute() else base/f
 assert f.stat().st_size==b['bytes'],str(f)
 assert hashlib.sha256(f.read_bytes()).hexdigest()==b['sha256'],str(f)
 return f
checks=[]
def check(n,v,d):
 assert v,n;checks.append({'check':n,'passed':True,'detail':d})
plan=j('PLAN-FROZEN.json');port=j('PORTABILITY.json')
for b in plan['source_bindings']:verify(b)
check('immutable_owner_inputs_exact',True,len(plan['source_bindings']))
for b in port['cache_only_inputs_and_derivatives']:verify(b)
check('cache_derivative_bindings',True,len(port['cache_only_inputs_and_derivatives']))
previous=0
for b in port['prior_freeze_bindings']:
 f=verify(b);fr=json.loads(f.read_text())
 for a in fr.get('artifacts',fr.get('files',[])):
  if isinstance(a,dict) and {'path','bytes','sha256'}<=a.keys():verify(a,f.parent);previous+=1
check('previous_freezes_preserved',True,previous)
roster=j('ALL45-SAMPLE-IDENTITY-ROSTER.json');rows=roster['records']
check('all45_unique_source_labels',len(rows)==45 and len(set(r['sample_id'] for r in rows))==45,45)
counts={k:sum(r['source_Fig1g_category']==k for r in rows) for k in roster['groups']}
check('source_categorical_counts',counts=={'DDLPS':14,'WDLPS':7,'LMS':6,'SFT':4,'GIST':2,'Others':12},counts)
check('boundary_hSC09_WDLPS',next(r for r in rows if r['sample_id']=='hSC09')['source_Fig1g_category']=='WDLPS','Adjudicated against exact annotation and independent review; no drug-rank values')
other={r['sample_id']:r for r in rows if r['source_Fig1g_category']=='Others'}
check('two_named_Other_sources',other['hSC21']['additional_source_identity']=='Hepatic embryonal sarcoma (HES)' and other['hSC51']['additional_source_identity']=='Endometrial stromal sarcoma (ESS)','Source Fig3/Fig5 header identities and primary definitions, not numerical response')
pending={r['sample_id'] for r in rows if r['eligibility'].startswith('Pending')}
check('all10_generic_Other_pending',pending==set(j('SOURCE-STATUS.json')['pending_sample_ids']) and len(pending)==10,'Not source-level confirmed exclusions or authenticated EMC')
check('unit_groups_no_independent_donor_count',len(roster['source_symbol_groups'])==3 and 'No independent-donor count calculated' in roster['other_symbol_limit'],'Exact legend defines three visible groups; unassigned star/06S-L context retained')
check('no_new_values_or_numerical_stage',j('SOURCE-STATUS.json')['new_outcome_values_inspected']==0 and not j('SOURCE-STATUS.json')['new_numerical_stage'],'Source eligibility only')
check('no_promotion_or_exhaustion',not j('DECISION.json')['publication_worthy_finding'] and not j('DECISION.json')['campaign_exhausted'],'NO-GO source-dependent')
check('post_ban_inspection_clock',j('POST-BAN-CLOCK-RECEIPT.json')['actual_utc']=='2026-10-05 14:00:02 UTC','America/New_York10:00:02DST clock before image/OCR')
check('zero_new_network_sources',port['new_network_source_bytes']==0,'Cached originals reused; no new deposit/source retrieval')
check('storage_budget',port['new_retained_raw_and_derivative_bytes']<=port['cap_bytes'] and shutil.disk_usage(P).free>=port['minimum_free_bytes'],{'retained_bytes':port['new_retained_raw_and_derivative_bytes'],'free_bytes':shutil.disk_usage(P).free})
root=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=P,text=True).strip())
tracked=subprocess.check_output(['git','ls-files','--',str(P.relative_to(root)/'source-cache')],cwd=root,text=True).strip()
check('originals_OCR_images_untracked',not tracked,'No full source, image, OCR or matrix Git export')
if '--replay-crops' in sys.argv:
 utc=datetime.datetime.now(datetime.timezone.utc);ny=utc.astimezone(ZoneInfo('America/New_York'))
 if 6<=ny.hour<10:raise RuntimeError('NY06:00–10:00 computer-use ban: image replay prohibited')
 from PIL import Image
 recipes={
 'Fig1-boundary-and-unit-legend-only.png':(1,[(250,700,312,769),(542,655,653,682)],[(620,690),(1110,270)],(1110,980),[(0,0),(0,710)]),
 'Fig1-SFT-pair-labels-only.png':(1,[(423,655,458,769)],[(350,1140)],(350,1140),[(0,0)]),
 'Fig3-case-identity-only.png':(3,[(595,12,663,36),(18,93,65,119)],[(680,240),(470,260)],(680,530),[(0,0),(0,270)]),
 'Fig5-case-histology-only.png':(5,[(44,1,446,25)],[(2010,120)],(2010,120),[(0,0)])}
 # Replay in memory and compare PNG bytes; never include a response panel.
 import io
 for n,(fig,boxes,sizes,total,at) in recipes.items():
  im=Image.open(P/f'source-cache/Fig{fig}-original.jpg');out=Image.new('RGB',total,'white')
  for box,size,pos in zip(boxes,sizes,at):out.paste(im.crop(box).resize(size),pos)
  b=io.BytesIO();out.save(b,format='PNG')
  assert hashlib.sha256(b.getvalue()).hexdigest()==hashlib.sha256((P/'source-cache'/n).read_bytes()).hexdigest(),n
 check('identity_only_crop_replay',True,{'recipes':len(recipes),'actual_utc':utc.isoformat()})
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Immutable input/categorical case/condition/hash and decision checks. No drug-rank, viability, protein or clinical outcome values.','checks':checks,'passed':True,'failures':0}
if '--write' in sys.argv:(P/'AUDIT-RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(checks),'previous_artifacts':previous,'retained_bytes':port['new_retained_raw_and_derivative_bytes']}))
