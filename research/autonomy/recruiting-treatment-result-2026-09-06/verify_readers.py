from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def pointer(obj,path):
 assert path.startswith('/')
 for token in path[1:].split('/'):
  key=token.replace('~1','/').replace('~0','~');obj=obj[int(key)] if isinstance(obj,list) else obj[key]
 return obj
manifest=read(ROOT/'research/autonomy/recruiting-treatment-difference-2026-09-06/coordinator/packet-manifest.json')
groups={r['case_id']:r for r in manifest['membership_and_provenance']}
expected={'one':'90434d6ee59a06bec195e4368faaf3238c456a52be0a8bd812e69daa22407d36','two':'8d851c61805c0043850f87138d01dbc2fbd26f95f0f1bd58daff80741bd500f8'}
reports={};judgments={}
for suffix in ('one','two'):
 base=ROOT/f'research/autonomy/recruiting-treatment-reader-{suffix}-2026-09-06'
 raw=(base/'freeze-receipt.json').read_bytes();assert sha(raw)==expected[suffix];receipt=json.loads(raw)
 if suffix=='one':
  ins=receipt['input_sha256'];outs={str(base/k):v for k,v in receipt['output_sha256'].items()};assert not receipt['comparison_performed']
 else:
  ins={x['file']:x['sha256'] for x in receipt['input_hashes']};outs={str(ROOT/x['file']):x['sha256'] for x in receipt['output_hashes']};assert not receipt['comparison_seen']
 for rel,h in ins.items():assert sha((ROOT/rel).read_bytes())==h,rel
 for rel,h in outs.items():assert sha(Path(rel).read_bytes())==h,rel
 cases=read(base/'independent-labels.json')['cases'];evidence=read(base/'source-evidence.json')['cases']
 byid={c['case_id']:c for c in cases};byev={c['case_id']:c for c in evidence}
 assert len(cases)==len(byid)==8 and set(byid)==set(groups)==set(byev)
 excerpts=0
 for c in cases:
  cid=c['case_id'];assert c['nct_id']==groups[cid]['nct_id'];assert c['source_raw_sha256']==groups[cid]['selected_raw_sha256']
  assert c['bounds']=={'positive':[1,1],'negative':[0,0],'unresolved':[0,1]}[c['label']]
  assert c['evidence']==byev[cid]['evidence']
  for e in c['evidence']:
   f=ROOT/e['file'];assert f.resolve().is_relative_to((ROOT/'research/autonomy/recruiting-treatment-difference-2026-09-06/reader/records').resolve())
   obj=read(f);assert obj['protocolSection']['identificationModule']['nctId']==c['nct_id']
   ptr=e.get('pointer',e.get('json_pointer'));value=pointer(obj,ptr)
   assert isinstance(value,str) and e['excerpt'] and e['excerpt'] in value,(cid,ptr)
   excerpts+=1
 entrants=[c for c in cases if groups[c['case_id']]['group']=='entrant'];displaced=[c for c in cases if groups[c['case_id']]['group']=='displaced']
 assert len(entrants)==len(displaced)==4
 bound=[sum(c['bounds'][0] for c in entrants)-sum(c['bounds'][1] for c in displaced),sum(c['bounds'][1] for c in entrants)-sum(c['bounds'][0] for c in displaced)]
 reports[suffix]={'input_hashes':len(ins),'output_hashes':len(outs),'exact_excerpts':excerpts,'entrant_positive':sum(c['label']=='positive' for c in entrants),'displaced_positive':sum(c['label']=='positive' for c in displaced),'delta_bounds':bound,'labels':[{'case_id':c['case_id'],'nct_id':c['nct_id'],'label':c['label'],'bounds':c['bounds'],'group':groups[c['case_id']]['group']} for c in cases]}
 judgments[suffix]=byid
agreements=[k for k in groups if judgments['one'][k]['bounds']==judgments['two'][k]['bounds']]
result={'status':'passed','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'readers':reports,'agreements':len(agreements),'total':8,'scope':'Independent frozen input/output hashes, exact source pointers and excerpts, complete memberships and deterministic difference arithmetic. Semantic validity requires separate source review.'}
(HERE/'reader-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({**{k:v for k,v in result.items() if k!='readers'},'readers':{k:{a:b for a,b in v.items() if a!='labels'} for k,v in reports.items()}}))
