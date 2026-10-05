#!/usr/bin/env python3
"""Validate source identity/count/method and frozen historical bytes; no endpoint analysis."""
import json,pathlib,hashlib,datetime,re,shutil
from lxml import etree
P=pathlib.Path(__file__).resolve().parent
checks=[]
def check(k,ok):
 checks.append({'check':k,'pass':bool(ok)})
def binding(x):
 f=pathlib.Path(x['path']);b=f.read_bytes();return len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256']
def norm(s):return re.sub(r'\s+',' ',s).strip()
sources=json.loads((P/'PRIMARY-SOURCE-RECEIPTS.json').read_text())
for a in sources:check(a['name']+'_source_bytes',binding(a))
for a in json.loads((P/'REUSED-DECISIONS.json').read_text())['historical_records']:check('historical_'+pathlib.Path(a['path']).name,binding(a))
raw=(P/'raw-cache/sjogren2003.xml').read_text()
try:etree.fromstring(raw.encode());valid=True
except etree.XMLSyntaxError:valid=False
check('sjogren2003_error_not_original',not valid and 'No result can be found' in raw)
a=json.loads((P/'SJOGREN-AVAILABILITY-GATE.json').read_text())
check('reused_errorHTML_bytes',binding(a['older_route_reused_zero_copy']))
h=pathlib.Path(a['older_route_reused_zero_copy']['path']).read_text()
check('reused_HTML_challenge_not_article','Checking your browser' in h and 'recaptcha' in h.lower())
r=etree.parse(str(P/'raw-cache/cba1205_2025.xml'))
# Only baseline diagnosis-count rows from Table1; no response/protein result table.
tab=r.xpath('//table-wrap[@id="t1"]')
if not tab: tab=[x for x in r.xpath('//table-wrap') if norm(' '.join(x.xpath('./label/text()'))) == 'TABLE 1']
assert len(tab)==1
rows=[]
for tr in tab[0].xpath('.//tr'):
 cells=[norm(' '.join(td.itertext())) for td in tr.xpath('./td|./th')]
 if cells and cells[0] in [x['source_diagnosis'] for x in json.loads((P/'CBA-BASELINE-ASSAY-GATE.json').read_text())['all_source_baseline_histology_groups']]:rows.append(cells)
a=json.loads((P/'CBA-BASELINE-ASSAY-GATE.json').read_text())
expected=[[x['source_diagnosis'],x['source_patient_count_literal']] for x in a['all_source_baseline_histology_groups']]
check('all15_source_histology_groups',rows==expected)
check('all22_baseline_patients',sum(int(re.match(r'\d+',c[1]).group()) for c in rows)==22)
check('unknown_origin_retained',any(c[0]=='Cancer of unknown origin' and c[1].startswith('1 ') for c in rows))
check('no_explicit_EMC_in_baseline_histology_labels',all('extraskeletal' not in c[0].lower() and 'myxoid chondrosarcoma' not in c[0].lower() for c in rows))
# Whitelisted IHC method paragraph; do not project other full-body tables/values.
pars=[norm(' '.join(q.itertext())) for q in r.xpath('//p')]
ihc=[x for x in pars if x.startswith('Immunohistochemical (IHC) analysis of DLK1 expression')]
check('exact_native_target_assay_method',len(ihc)==1 and all(v in ihc[0] for v in ['formalin','DI','Chiome','Archival tissue','within 28 days']))
# Tissue availability/timing sentence only, not remainder of expression-result paragraph.
check('source_14_of22_old_archival_metadata',all(any(norm(v) in x for x in pars) for v in a['source_tissue_availability_sentences']))
check('ADCT_premise_already_R3', 'NCT06041516' in pathlib.Path('/workspace/Rare-cancers/research/autonomy/fresh-discovery-2026-10-04-round3/dlk1_review/acc2024-relevant-text.json').read_text())
port=json.loads((P/'PORTABILITY.json').read_text())
check('all_cache_bytes_bound',all(binding(x) for x in port['original_cache_only']))
check('raw_softcap',port['new_retained_raw_total_bytes']<=8388608)
check('free_floor',shutil.disk_usage(P).free>=10737418240)
check('no_fresh_outcome_matrix',json.loads((P/'EXPOSURE-AND-SCOPE.json').read_text())['fresh_outcome_matrices_opened'] is False)
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Source bytes, baseline diagnoses/counts, IHC method and archival timing only; no new expression/stain/drug outcomes.','checks':checks,'errors':[x['check'] for x in checks if not x['pass']],'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL'}
(P/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'errors':result['errors']}))
raise SystemExit(bool(result['errors']))
