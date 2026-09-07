"""Create-once metadata freeze, then exact saved-source extraction. No labels inferred."""
import json, hashlib, gzip
from pathlib import Path
from datetime import datetime, timezone
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SRC=ROOT/'research/autonomy/trial-discoverability-2026-09-05'
SEL=ROOT/'research/autonomy/trial-reference-repair-2026-09-05/selection.json'
REF=ROOT/'research/autonomy/trial-reference-adjudication-2026-09-05/adjudicated-reference.json'
def sha(b): return hashlib.sha256(b).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def write(name,obj):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as f: f.write(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def now(): return datetime.now(timezone.utc).isoformat()
selection=load(SEL); index=load(SRC/'corpus-index.json'); reference=load(REF)
byid={r['nct_id']:r for r in index}; old={p['pair_id']:p for p in reference['pairs']}
frame=[]
for s in selection['strata']:
    if s['stratum'] not in ['ordinary','molecular_only']: continue
    d=s['diagnosis']; ordinary={d+'_'+x for x in ['condition','ordinary','eligibility_ordinary','unquoted_ordinary','unquoted_eligibility']}; molecular={d+'_molecular',d+'_eligibility_molecular'}
    expected=[]
    for r in index:
        if r['study_type']!='INTERVENTIONAL' or r['status'] not in ['RECRUITING','NOT_YET_RECRUITING','ENROLLING_BY_INVITATION']: continue
        q=set(r['query_ids']); st='ordinary' if q&ordinary else 'molecular_only' if q&molecular else None
        if st==s['stratum']: expected.append(r['nct_id'])
    assert sorted(expected)==s['frame_ids']
    for n in s['frame_ids']:
        pid=d+':'+n
        frame.append(dict(pair_id=pid,diagnosis=d,nct_id=n,stratum=s['stratum'],metadata=byid[n],reference_state='reused_adjudicated' if pid in old else 'unjudged'))
frame.sort(key=lambda p:p['pair_id']); ids={p['pair_id'] for p in frame}
overlap=[p for p in reference['pairs'] if p['pair_id'] in ids]; outside=[p for p in reference['pairs'] if p['pair_id'] not in ids]
unjudged=[p for p in frame if p['reference_state']=='unjudged']
order=sorted([p['nct_id'] for p in unjudged if p['diagnosis']=='EMC'],key=lambda n:(sha(('20260905|EMC-expansion|'+n).encode()),n))
assert len(frame)==149 and len(overlap)==25 and len(outside)==24 and len(unjudged)==124 and len(order)==50
assert len({p['nct_id'] for p in frame})==124 and len({p['nct_id'] for p in unjudged})==109
contract=dict(frozen_utc=now(),base='95dbbe7a0f243452bc689fb22db00fb13417d9f5',reservation_confirmed_utc='2026-09-05T19:33:41.876267Z',scientific_started_utc='2026-09-05T19:43:07Z',scientific_budget_seconds=1800,scope='Full 149-pair ordinary-or-molecular frame; this round first reads 50 remaining EMC pairs only.',endpoint='Source-based disease/cohort scope, never individual eligibility, clinical benefit, live slots, global recall or retrieval performance.',stop='50 source judgments or honest timed prefix; independent verification required before performance evaluation.',no_prior_provisional_labels=True,input_hashes={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [SEL,SRC/'corpus-index.json',REF]})
protocol=dict(frozen_utc=now(),labels={
'explicit_diagnosis_compatible':'EMC explicitly admitted by saved disease/cohort scope.',
'defining_fusion_compatible':'Exact defining EMC fusion/variant admitted; variant matching required.',
'fusion_class_compatible':'Matching EMC variant belongs to an admitted fusion class; not all NR4A3 fusions are FET fusions.',
'broad_tumor_compatible':'Open solid-tumor/sarcoma scope without a narrower conflicting histology limit; additional molecular gates stay orthogonal.',
'explicit_exclusion':'Express exclusion or clearly closed incompatible positive disease list; record which.',
'insufficient_evidence':'Unresolved disease/cohort applicability including nononcology acronym hits; never automatic negative.'},rules=['Read complete eligibility, description, arms/cohorts, design/purpose/phases, conditions and status before labeling.','Reconcile all cohorts/phases; distinguish open examples from closed lists.','Required additional biomarker is unestablished, never inferred from EMC or a hypothetical future alteration.','Keep enrollment holds, missing external protocols, non-treatment purpose and snapshot status explicit.','Preserve 25 adjudicated overlaps with all original provenance unchanged; 24 outside-frame reference pairs stay separate.','No patient-specific judgments, ranking, model fitting or retrieval evaluation.','New labels require separate independent verification/adjudication.'],work_order='Ascending SHA256 of UTF-8 20260905|EMC-expansion|NCTID, NCT ID tie-breaker. Work order, not prevalence sample.')
write('contract.json',contract);write('label-protocol.json',protocol);write('full-frame.json',frame);write('overlap-reference.json',overlap);write('outside-frame-reference.json',outside);write('unjudged-frame.json',unjudged)
write('work-order.json',[dict(position=i+1,nct_id=n,pair_id='EMC:'+n,order_sha256=sha(('20260905|EMC-expansion|'+n).encode())) for i,n in enumerate(order)])
write('frame-freeze-receipt.json',dict(frozen_utc=now(),criteria_displayed=False,files={p.name:sha(p.read_bytes()) for p in sorted(OUT.glob('*.json'))}))
# Only after metadata/protocol freeze: inspect saved raw registry pages programmatically.
needed={p['nct_id'] for p in frame}; packet={n:dict(nct_id=n,copies=[]) for n in sorted(needed)}; pages=[]
for mp in sorted((SRC/'sources').glob('*/manifest.json')):
    m=load(mp)
    for a in m.get('pages',[]):
        p=SRC/a['file']; b=p.read_bytes(); raw=gzip.decompress(b)
        assert sha(b)==a['stored_sha256'] and sha(raw)==a['sha256']
        doc=json.loads(raw)
        for i,r in enumerate(doc['studies']):
            n=r['protocolSection']['identificationModule']['nctId']
            if n not in needed: continue
            packet[n]['copies'].append(dict(source=str(p.relative_to(ROOT)).replace('\\','/'),source_sha256=sha(b),decoded_sha256=sha(raw),pointer=f'/studies/{i}',manifest=str(mp.relative_to(ROOT)).replace('\\','/'),manifest_sha256=sha(mp.read_bytes()),page_receipt=a,record_sha256=sha(json.dumps(r,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()),record=r))
for n,x in packet.items():
    assert x['copies'],n
    x['duplicate_copies_equal']=all(c['record']==x['copies'][0]['record'] for c in x['copies'])
    x['distinct_record_hashes']=sorted({c['record_sha256'] for c in x['copies']})
write('source-packet.json',packet)
write('source-extraction-receipt.json',dict(created_utc=now(),records=len(packet),copies=sum(len(x['copies']) for x in packet.values()),differences=[n for n,x in packet.items() if not x['duplicate_copies_equal']],packet_sha256=sha((OUT/'source-packet.json').read_bytes())))
print(json.dumps(dict(frame=len(frame),overlap=len(overlap),outside=len(outside),unjudged=len(unjudged),emc=len(order),sources=len(packet),differences=[n for n,x in packet.items() if not x['duplicate_copies_equal']],order=order)))
