"""Reproduce source-linked first-reader artifacts; read-only unless --write (create once)."""
import json, hashlib, sys
from pathlib import Path
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
MODULES=['identificationModule','conditionsModule','descriptionModule','eligibilityModule','armsInterventionsModule','designModule','statusModule']
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(b): return hashlib.sha256(b).hexdigest()
def canon(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def pointer(x,p):
    for k in p.strip('/').split('/'):
        k=k.replace('~1','/').replace('~0','~');x=x[int(k)] if isinstance(x,list) else x[k]
    return x
def results():
    packet=load(OUT/'source-packet.json');order=load(OUT/'work-order.json'); notes=[]
    for p in sorted(OUT.glob('judgments-*.json')):
        for i,r in enumerate(load(p)): notes.append((p,i,r))
    notes.sort(key=lambda v:v[2]['position'])
    assert [r['position'] for _,_,r in notes]==list(range(1,len(notes)+1))
    labels=[]
    for np,ni,note in notes:
        pos=note['position']; w=order[pos-1]; n=w['nct_id']; x=packet[n]
        assert x['duplicate_copies_equal'], 'Differences require explicit per-copy judgment'
        c=x['copies'][0]; ps=c['record']['protocolSection']; base=c['pointer']+'/protocolSection/'
        def ev(path): return dict(source=c['source'],source_sha256=c['source_sha256'],decoded_sha256=c['decoded_sha256'],pointer=base+path)
        quotes=[]
        for path,q in note['quotes']:
            for fix in load(OUT/'source-corrections.json'):
                if fix['position']==pos and fix['old_pointer']==path: path=fix['new_pointer']
            s=pointer(ps,path);assert isinstance(s,str) and q in s,(n,path,q)
            start=s.index(q);quotes.append(dict(**ev(path),excerpt=q,char_start=start,char_end=start+len(q)))
        reviewed=[dict(**ev(m),module_present=m in ps,module_sha256=sha(canon(ps.get(m)))) for m in MODULES]
        labels.append(dict(**{k:v for k,v in note.items() if k!='quotes'},pair_id=w['pair_id'],nct_id=n,diagnosis='EMC',title=ps['identificationModule']['briefTitle'],state='first_reader_pending_independent_verification',source_note=dict(file=np.name,pointer='/'+str(ni),sha256=sha(np.read_bytes())),evidence=quotes,reviewed_modules=reviewed,complete_saved_modules_read=True,external_protocol_reviewed=False,additional_biomarker_established=False,clinical_eligibility_established=False,clinical_benefit_established=False,binary_benchmark_use='not_permitted_before_independent_verification_and_endpoint_definition',snapshot_status=ps['statusModule']['overallStatus'],status_verified_date=ps['statusModule'].get('statusVerifiedDate'),registry_primary_purpose=ps['designModule'].get('designInfo',{}).get('primaryPurpose'),phases=ps['designModule'].get('phases',[]),status_evidence=ev('statusModule'),purpose_phase_evidence=ev('designModule'),recruitment_uncertainty='Saved overall registry status only; sites, phases, cohorts, holds and live slots not independently verified.',other_clinical_constraints='Complete eligibility module retained in source packet; age, organ function, treatment history, anatomy, medications and investigator decisions not assessed for an individual.'))
    done={r['pair_id'] for r in labels}; unfinished=[p for p in load(OUT/'unjudged-frame.json') if p['pair_id'] not in done]
    refpath=ROOT/'research/autonomy/trial-reference-adjudication-2026-09-05/adjudicated-reference.json'; ref=load(refpath)
    overlap={p['pair_id'] for p in load(OUT/'overlap-reference.json')}
    mapping=[dict(pair_id=p['pair_id'],source=str(refpath.relative_to(ROOT)).replace('\\','/'),source_sha256=sha(refpath.read_bytes()),pointer='/pairs/'+str(i),preservation='Exact parsed object including first reader, independent reader, adjudication and original provenance') for i,p in enumerate(ref['pairs']) if p['pair_id'] in overlap]
    return {'first-reader-labels.json':labels,'unfinished-pairs.json':unfinished,'overlap-mapping.json':mapping}
if __name__=='__main__':
    res=results()
    if '--write' in sys.argv:
        assert all(not (OUT/n).exists() for n in res), 'Will not overwrite frozen output'
        for n,x in res.items():
            with (OUT/n).open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
    else:
        for n,x in res.items():assert load(OUT/n)==x,n
    print(json.dumps({n:len(x) for n,x in res.items()}))
