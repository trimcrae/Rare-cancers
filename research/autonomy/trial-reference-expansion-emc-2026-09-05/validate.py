"""Offline read-only coverage/provenance reproducer; no label inference or semantic adjudication."""
import gzip,json,hashlib,sys,time
from pathlib import Path
from collections import Counter
import assemble
O=Path(__file__).resolve().parent; R=O.parents[2]; S=R/'research/autonomy/trial-discoverability-2026-09-05'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
def ptr(x,p):
    for k in p.strip('/').split('/'):
        k=k.replace('~1','/').replace('~0','~');x=x[int(k)] if isinstance(x,list) else x[k]
    return x
def main():
    started=time.monotonic(); contract=load(O/'contract.json');receipt=load(O/'frame-freeze-receipt.json')
    for p,h in contract['input_hashes'].items():assert sha((R/p).read_bytes())==h,p
    for p,h in receipt['files'].items():assert sha((O/p).read_bytes())==h,p
    index=load(S/'corpus-index.json');idx={p['nct_id']:p for p in index};sel=load(R/'research/autonomy/trial-reference-repair-2026-09-05/selection.json')
    assert sel['input_sha256']==sha((S/'corpus-index.json').read_bytes())
    frame=load(O/'full-frame.json'); fids={p['pair_id'] for p in frame};expected=[]
    for d in ['EMC','DSRCT','SS']:
        ordinary={d+'_'+x for x in ['condition','ordinary','eligibility_ordinary','unquoted_ordinary','unquoted_eligibility']};molecular={d+'_molecular',d+'_eligibility_molecular'}
        for r in index:
            if r['study_type']!='INTERVENTIONAL' or r['status'] not in ['RECRUITING','NOT_YET_RECRUITING','ENROLLING_BY_INVITATION']:continue
            q=set(r['query_ids']);st='ordinary' if q&ordinary else 'molecular_only' if q&molecular else None
            if st:expected.append((d+':'+r['nct_id'],st))
    assert sorted(expected)==sorted((p['pair_id'],p['stratum']) for p in frame)
    for s in sel['strata']:
        if s['stratum'] in ['ordinary','molecular_only']:assert s['frame_ids']==sorted(p['nct_id'] for p in frame if p['diagnosis']==s['diagnosis'] and p['stratum']==s['stratum'])
    assert len(fids)==len(frame)==149
    assert Counter(p['diagnosis'] for p in frame)=={'EMC':58,'DSRCT':39,'SS':52}
    for p in frame:assert p['metadata']==idx[p['nct_id']]
    original=load(R/'research/autonomy/trial-reference-adjudication-2026-09-05/adjudicated-reference.json')['pairs']
    overlap=load(O/'overlap-reference.json');outside=load(O/'outside-frame-reference.json');unjudged=load(O/'unjudged-frame.json')
    assert overlap==[p for p in original if p['pair_id'] in fids]
    assert outside==[p for p in original if p['pair_id'] not in fids]
    oldids={p['pair_id'] for p in overlap};assert len(overlap)==25 and len(outside)==24
    assert unjudged==[p for p in frame if p['pair_id'] not in oldids]
    assert len(unjudged)==124 and len({p['nct_id'] for p in unjudged})==109
    assert Counter(p['diagnosis'] for p in unjudged)=={'EMC':50,'DSRCT':29,'SS':45}
    order=load(O/'work-order.json');ranked=sorted([p['nct_id'] for p in unjudged if p['diagnosis']=='EMC'],key=lambda n:(sha(('20260905|EMC-expansion|'+n).encode()),n))
    assert [p['nct_id'] for p in order]==ranked
    for i,p in enumerate(order):assert p==dict(position=i+1,nct_id=ranked[i],pair_id='EMC:'+ranked[i],order_sha256=sha(('20260905|EMC-expansion|'+ranked[i]).encode()))
    packet=load(O/'source-packet.json');assert set(packet)=={p['nct_id'] for p in frame} and len(packet)==124
    observed={n:[] for n in packet};metadata={};page_docs={};query_count=0;page_count=0
    for mp in sorted((S/'sources').glob('*/manifest.json')):
        m=load(mp);ids=[]
        if 'query_id' in m:assert m['complete'];query_count+=1
        for a in m.get('pages',[]):
            p=S/a['file'];b=p.read_bytes();raw=gzip.decompress(b)
            assert sha(b)==a['stored_sha256'] and sha(raw)==a['sha256'],p
            doc=json.loads(raw);assert len(doc['studies'])==a['count'];page_count+=1
            source=str(p.relative_to(R)).replace('\\','/');page_docs[source]=doc
            for j,r in enumerate(doc['studies']):
                ps=r['protocolSection'];n=ps['identificationModule']['nctId'];ids.append(n)
                if 'query_id' in m:
                    fields=dict(status=ps['statusModule']['overallStatus'],study_type=ps['designModule']['studyType'])
                    if n not in metadata:metadata[n]=dict(**fields,query_ids=[])
                    else:assert all(metadata[n][k]==v for k,v in fields.items())
                    metadata[n]['query_ids'].append(m['query_id'])
                if n in observed:observed[n].append(dict(source=source,source_sha256=sha(b),decoded_sha256=sha(raw),pointer=f'/studies/{j}',manifest=str(mp.relative_to(R)).replace('\\','/'),manifest_sha256=sha(mp.read_bytes()),page_receipt=a,record_sha256=sha(canon(r)),record=r))
        if 'query_id' in m:assert len(ids)==len(set(ids))==m['total_count'] and sorted(ids)==sorted(m['ids'])
    assert set(metadata)==set(idx) and len(idx)==6182
    for n,x in metadata.items():
        assert x['status']==idx[n]['status'] and x['study_type']==idx[n]['study_type']
        assert sorted(x['query_ids'])==sorted(idx[n]['query_ids'])
    for n,x in packet.items():
        assert x['copies']==observed[n],n
        equal=all(c['record']==x['copies'][0]['record'] for c in x['copies'])
        assert x['duplicate_copies_equal']==equal
        assert x['distinct_record_hashes']==sorted({c['record_sha256'] for c in x['copies']})
    labels=load(O/'first-reader-labels.json');lids={p['pair_id'] for p in labels}
    assert len(labels)==len(lids) and not lids&oldids
    assert [p['pair_id'] for p in labels]==[p['pair_id'] for p in order[:len(labels)]]
    valid=set(load(O/'label-protocol.json')['labels']);quotes=0
    for p in labels:
        assert p['label'] in valid and p['state']=='first_reader_pending_independent_verification'
        assert p['clinical_eligibility_established'] is False and p['additional_biomarker_established'] is False
        assert p['cohort_reconciliation'] and p['rationale'] and p['protocol_uncertainty'] and p['extra_biomarker_requirement']
        assert p['complete_saved_modules_read'] and not p['external_protocol_reviewed']
        assert [e['pointer'].split('/')[-1] for e in p['reviewed_modules']]==assemble.MODULES
        for e in p['evidence']:
            doc=page_docs[e['source']];assert sha((R/e['source']).read_bytes())==e['source_sha256']
            s=ptr(doc,e['pointer']);assert s[e['char_start']:e['char_end']]==e['excerpt'];quotes+=1
        for e in p['reviewed_modules']:
            ps=packet[p['nct_id']]['copies'][0]['record']['protocolSection'];m=e['pointer'].split('/')[-1]
            assert (m in ps)==e['module_present'] and sha(canon(ps.get(m)))==e['module_sha256']
        ps=packet[p['nct_id']]['copies'][0]['record']['protocolSection']
        assert p['snapshot_status']==ps['statusModule']['overallStatus'] and p['status_verified_date']==ps['statusModule'].get('statusVerifiedDate')
        assert p['phases']==ps['designModule'].get('phases',[]) and p['registry_primary_purpose']==ps['designModule'].get('designInfo',{}).get('primaryPurpose')
    unfinished=load(O/'unfinished-pairs.json');assert unfinished==[p for p in unjudged if p['pair_id'] not in lids]
    assert lids|oldids|{p['pair_id'] for p in unfinished}==fids
    for name,obj in assemble.results().items():assert load(O/name)==obj,name
    extract=load(O/'source-extraction-receipt.json');assert extract['packet_sha256']==sha((O/'source-packet.json').read_bytes())
    if (O/'reading-log.json').exists():
        reading=load(O/'reading-log.json');assert reading['completed_positions']==list(range(1,len(labels)+1));assert reading['new_criteria_first_display_after_frame_freeze']
    manifest_checked=False
    if '--manifest' in sys.argv:
        manifest=load(O/'output-manifest.json');actual={str(p.relative_to(O)).replace('\\','/') for p in O.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='output-manifest.json'}
        assert actual=={p['path'] for p in manifest['files']}
        for f in manifest['files']:
            b=(O/f['path']).read_bytes();assert len(b)==f['bytes'] and sha(b)==f['sha256'],f['path']
        for p in O.glob('*.md'):
            s=p.read_text(encoding='utf-8');assert s.startswith('---\n');front=s.split('---',2)[1]
            for field in ['id: DOC-','title:','kind:','status: live','date:','last_verified:','purpose:','scope:','audience:']:assert field in front,(p,field)
        manifest_checked=True
    print(json.dumps(dict(passed=True,scope='Mechanical source, coverage, exact preservation and reproduction checks; not independent semantic verification.',frame_pairs=149,frame_trials=124,overlap_preserved=25,outside_frame_preserved=24,new_emc_labels=len(labels),unfinished_pairs=len(unfinished),unfinished_diagnoses=dict(Counter(p['diagnosis'] for p in unfinished)),corpus_records_reproduced=len(metadata),query_manifests=query_count,saved_pages_verified=page_count,source_copies=sum(len(x['copies']) for x in packet.values()),source_copy_differences=[n for n,x in packet.items() if not x['duplicate_copies_equal']],exact_excerpts_verified=quotes,manifest_checked=manifest_checked,elapsed_seconds=time.monotonic()-started),indent=2))
if __name__=='__main__':main()
