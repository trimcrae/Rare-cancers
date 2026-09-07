"""Metadata-only selection; never accesses trial criteria. Run from repository root."""
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone

OUT = Path('research/autonomy/trial-reference-repair-2026-09-05')
INPUT = Path('research/autonomy/trial-discoverability-2026-09-05/corpus-index.json')
SEED = '20260905'
def selection():
    rows = json.loads(INPUT.read_text())
    strata = []
    for d in ['EMC', 'DSRCT', 'SS']:
        ordinary = {d+'_'+s for s in ['condition','ordinary','eligibility_ordinary','unquoted_ordinary','unquoted_eligibility']}
        molecular = {d+'_molecular',d+'_eligibility_molecular'}
        pools = {s:[] for s in ['ordinary','molecular_only','parent_only']}
        for r in rows:
            if r['study_type'] != 'INTERVENTIONAL' or r['status'] not in ['RECRUITING','NOT_YET_RECRUITING','ENROLLING_BY_INVITATION']:
                continue
            q = set(r['query_ids'])
            s = 'ordinary' if q & ordinary else 'molecular_only' if q & molecular else 'parent_only' if q & {'parent_sarcoma','parent_eligibility_sarcoma'} else None
            if s: pools[s].append(r['nct_id'])
        for s, ids in pools.items():
            ranked = sorted(ids, key=lambda n: (hashlib.sha256(f'{SEED}|{d}|{s}|{n}'.encode()).hexdigest(),n))
            strata.append(dict(diagnosis=d,stratum=s,frame_n=len(ids),frame_ids=sorted(ids),selected_ids=ranked[:4]))
    return dict(seed=SEED,algorithm='Ascending SHA256 of UTF-8 seed|diagnosis|stratum|NCT ID; first min(4,N); no replenishment',input_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(),frame_n=len(rows),strata=strata,challenge_anchors=[dict(nct_id=n,diagnoses=['EMC','DSRCT','SS']) for n in ['NCT05918640','NCT05071209','NCT06571734','NCT05135975','NCT05687136','NCT06094101']])

if __name__ == '__main__':
    result=selection()
    target=OUT/'selection.json'
    if target.exists():
        saved=json.loads(target.read_text()); saved.pop('frozen_at_utc')
        assert saved==result, 'Frozen selection differs'
        print('Frozen metadata selection reproduced exactly')
    else:
        result['frozen_at_utc']=datetime.now(timezone.utc).isoformat()
        target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([{k:v for k,v in s.items() if k!='frame_ids'} for s in result['strata']],indent=2))
