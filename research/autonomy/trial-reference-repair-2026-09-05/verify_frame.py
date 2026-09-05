"""Reconstruct corpus metadata from all saved registry query pages; no prior labels used."""
import gzip,hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
SRC=ROOT/'research/autonomy/trial-discoverability-2026-09-05'
def load(p): return json.loads(p.read_text(encoding='utf-8'))
metadata={}; receipts=[]; pages=0
for mp in sorted((SRC/'sources').glob('*/manifest.json')):
    m=load(mp)
    if 'query_id' not in m: continue
    assert m['complete'] is True,mp
    ids=[]
    for a in m['pages']:
        p=SRC/a['file']; b=p.read_bytes(); raw=gzip.decompress(b)
        assert hashlib.sha256(b).hexdigest()==a['stored_sha256'],p
        assert hashlib.sha256(raw).hexdigest()==a['sha256'],p
        doc=json.loads(raw); pages+=1
        assert len(doc['studies'])==a['count']
        for r in doc['studies']:
            ps=r['protocolSection']; n=ps['identificationModule']['nctId']; ids.append(n)
            fields=dict(nct_id=n,status=ps['statusModule']['overallStatus'],study_type=ps['designModule']['studyType'])
            if n not in metadata: metadata[n]={**fields,'query_ids':[]}
            else: assert all(metadata[n][k]==v for k,v in fields.items()),n
            metadata[n]['query_ids'].append(m['query_id'])
    assert len(set(ids))==len(ids)==m['total_count'],mp
    assert sorted(ids)==sorted(m['ids']),mp
    receipts.append(dict(query_id=m['query_id'],records=len(ids),manifest_sha256=hashlib.sha256(mp.read_bytes()).hexdigest()))
index=load(SRC/'corpus-index.json'); assert len(index)==len(metadata)==6182
for r in index:
    x=metadata[r['nct_id']]
    assert r['status']==x['status'] and r['study_type']==x['study_type'],r['nct_id']
    assert sorted(r['query_ids'])==sorted(x['query_ids']),r['nct_id']
result=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),corpus_records=len(index),registry_query_manifests=len(receipts),gzip_pages=pages,all_index_query_memberships_statuses_types_match_raw_sources=True,all_page_and_manifest_counts_hashes_verified=True,queries=receipts)
if '--check' in sys.argv:
    saved=load(OUT/'frame-validation.json')
    assert {k:v for k,v in saved.items() if k!='checked_at_utc'}=={k:v for k,v in result.items() if k!='checked_at_utc'}, 'Frame verification changed'
else:
    (OUT/'frame-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='queries'},indent=2))
