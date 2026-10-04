from pathlib import Path
import xml.etree.ElementTree as E,json,hashlib,datetime
D=Path(__file__).resolve().parent
F=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-functional/research/autonomy/fresh-discovery-2026-10-04-round7/functional_models')
text=lambda e:' '.join(''.join(e.itertext()).split())
r=E.parse(F/'ala2022.xml').getroot()
rows=[[text(c) for c in row] for row in r.findall('.//table-wrap[@id="Tab1"]//tr')]
emc=[row for row in rows if 'EMC' in row]
assert len(emc)==1
p=[text(x) for x in r.findall('.//p')]
key=[s for s in p if ('spontaneous regression' in s.lower() or ('interpretation' in s.lower() and 'pdt' in s.lower()))]
print('EMC row',emc)
for s in key:print('Regression:',s[:2500])
r=E.parse(F/'inbrx2023.xml').getroot()
key2=[text(x) for x in r.findall('.//p') if any(q in text(x) for q in ['CTG-1255','CTG-2383'])]
print('PDX:',key2)
r=E.parse(F/'shared2026.xml').getroot()
key3=[text(x) for x in r.findall('.//p') if 'HEMCSS (CVCL_1238)' in text(x)]
files=['RESULTS.txt','COVERAGE.txt','evaluation.json','ala-source-evaluation.json','disputed-model-evaluation.json','ala2022.xml','inbrx2023.xml','shared2026.xml']
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'Independent read-only source/identity and value challenge; no new retrieval or drug-effect calculation','files':[{'path':str(F/n),'bytes':(F/n).stat().st_size,'sha256':hashlib.sha256((F/n).read_bytes()).hexdigest()} for n in files],'original_emc_row':emc,'regression_paragraphs':key,'original_pdx_identity':key2,'shared_model_identity_paragraph':key3,'judgment':'Agree scoped SHELVE. Single author-labelled EMC tissue observation is real prior published qualitative fluorescence, without fusion confirmation or an EMC-specific controlled PDT response. Technical eggs/grafts are not donors; pooled necrosis and fluorescence do not establish selective vulnerability. The PDXs are conventional chondrosarcoma. HEMCSS is the same identity-disputed resource; STR alone does not resolve histotype. Unresolved source rosters and supplements remain pending, so do not generalize to absence of useful EMC functional evidence.','corrections_required':[],'limits':'Did not repeat full discovery search, inspect every new broad-cohort original, or authenticate the disputed cell line anew. Review is limited to the core published-only EMC observation and the critical model-identity/value claims. Prior platform-denied sources were not accessed.'}
(D/'functional-models-independent-review.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
print('REVIEW_SHA',hashlib.sha256((D/'functional-models-independent-review.json').read_bytes()).hexdigest())
