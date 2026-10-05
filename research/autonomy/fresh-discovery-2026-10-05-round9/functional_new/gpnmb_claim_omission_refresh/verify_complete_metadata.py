"""Replay the frozen metadata-only screening; no network or biological quantities."""
from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent
r=json.loads((p/'COMPLETE-METADATA-ACCESS.json').read_text())
b=(p/'raw-cache/complete-query4.json').read_bytes()
assert hashlib.sha256(b).hexdigest()==r['sha256'] and len(b)==r['bytes']
d=json.loads(b);rows=d['resultList']['result'];assert d['hitCount']==len(rows)==453
old=json.loads((p/'raw-cache/query-4.json').read_text())['resultList']['result']
assert [x['id'] for x in rows[:100]]==[x['id'] for x in old]
counts={'explicit_EMC_LGFMS_title':0,'generic_or_broader_native_candidate_title':0,'other_title_only_no_body_exclusion':0}
selected=[]
for x in rows:
 t=(x.get('title') or '').lower()
 explicit=any(k in t for k in ['extraskeletal myxoid','extra-skeletal myxoid','low-grade fibromyxoid','low grade fibromyxoid','lgfms'])
 potential=(any(k in t for k in ['soft tissue sarcoma','soft-tissue sarcoma','chondrosarcoma','fibromyxoid','mesenchymal tum','multi-cancer','tumor-derived endothelium','tumour-derived endothelium','sarcoma tumor-initiating','targeted expression data','pan-cancer']) or t.strip()=='abstracts')
 key='explicit_EMC_LGFMS_title' if explicit else 'generic_or_broader_native_candidate_title' if potential else 'other_title_only_no_body_exclusion'
 counts[key]+=1
 if explicit or potential:selected.append(x['id'])
frozen=json.loads((p/'COMPLETE-METADATA-ELIGIBILITY-SCREEN.json').read_text())
assert counts==frozen['title_rule_counts']
assert selected==[x['id'] for x in frozen['selected_relevant_metadata_candidates']]
print('PASS: all453 metadata title rules, original100IDs and16 pending source IDs reproduce exactly. No gene outcomes, full bodies or network.')
