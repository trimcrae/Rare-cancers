"""Local source and eligibility verification; no network calls or assay values."""
from pathlib import Path
import hashlib, json
p=Path(__file__).resolve().parent
h=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
a=json.loads((p/'ACCESS.json').read_text()); plan=json.loads((p/'PLAN.json').read_text()); sets=[]
assert h(p/'PLAN.json')==a['plan_sha256']
assert a['patient_or_matrix_route_calls']==0 and a['noauth_cookies_tokens_redirect_follow']
for r in a['responses']:
 f=p/r['file']; b=f.read_bytes(); assert len(b)==r['bytes'] and h(f)==r['sha256']
 v=json.loads(b); assert isinstance(v,list) and all(isinstance(x,str) for x in v)
 assert len(b)<plan['caps']['bytes_per_response'] and r['http']==200 and not r['at_cap']
 assert r['url']==plan['routes'][r['index']]['exact_url']; sets.append(set(v))
e=json.loads((p/'EVALUATED-LABEL-ELIGIBILITY.json').read_text())
assert [len(x) for x in sets]==[2,9,2,10]
assert sets[3]==sets[0]|sets[1]|sets[2]
assert set.union(*sets)=={r['source_label'] for r in e['rows']} and len(e['rows'])==10
for r in e['rows']: assert r['indexed_routes']==[i for i,s in enumerate(sets) if r['source_label'] in s]
assert sum(len(s) for s in sets)==23 and sum(len(s & {'','Not Reported'}) for s in sets)==6
po=json.loads((p/'PORTABILITY.json').read_text()); assert po['raw_bytes']==sum(r['bytes'] for r in a['responses'])==675
assert po['cumulative_owned_R9_raw_bytes']==53475596 and po['free_bytes_at_finalization']>=po['free_floor_bytes']
m=json.loads((p/'MANIFEST.json').read_text())
for r in m['files']: assert h(p/r['file'])==r['sha256']
for r in m['source_bindings']: assert h(Path(r['path']))==r['sha256']
print(json.dumps({'status':'PASS','raw_responses':4,'raw_bytes':675,'all_label_occurrences':23,'unique_labels':10,'no_network':True,'biological_values_accessed':False}))
