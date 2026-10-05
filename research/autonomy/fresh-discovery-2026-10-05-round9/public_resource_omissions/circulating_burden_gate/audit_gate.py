"""Replay source identity/count/hash checks only; never parse biomarker outcomes."""
from pathlib import Path
import json, hashlib, re, shutil, subprocess, zipfile
from datetime import datetime, timezone
from lxml import etree
P=Path(__file__).resolve().parent
checks=[]
def check(name,passed,detail):
 checks.append({'check':name,'passed':bool(passed),'detail':detail})
 if not passed: raise AssertionError(name)
def j(name):return json.loads((P/name).read_text())
def verify(b,base=P):
 f=Path(b['path']);f=f if f.is_absolute() else base/f
 assert f.stat().st_size==b['bytes'],str(f)
 assert hashlib.sha256(f.read_bytes()).hexdigest()==b['sha256'],str(f)
 return f
port=j('PORTABILITY.json')
for b in port['raw_inputs']:verify(b)
check('retained_raw_exact_hashes',True,{'files':len(port['raw_inputs']),'bytes':sum(x['bytes'] for x in port['raw_inputs'])})
for b in j('REUSED-EVIDENCE.json')['reuse_binding']:verify(b)
check('zero_copy_reuse_bindings',True,len(j('REUSED-EVIDENCE.json')['reuse_binding']))
prior_count=0
for b in port['prior_freeze_bindings']:
 f=verify(b)
 freeze=json.loads(f.read_text())
 for a in freeze.get('artifacts',freeze.get('files',[])):
  if isinstance(a,dict) and {'path','bytes','sha256'} <= a.keys():verify(a,f.parent);prior_count+=1
check('prior_freezes_and_frozen_artifacts_preserved',True,{'freeze_files':len(port['prior_freeze_bindings']),'artifact_bindings':prior_count})
for b in j('INDEPENDENT-SCIENCE-REVIEW-STATUS.json')['review_bindings']:verify(b)
check('peer_science_exact_hash_bindings',True,4)
# Management floating Table6: choose only Case and Diagnosis, not grade/outcome cells.
r=etree.parse(str(P/'source-cache/PMC11545914.xml'))
t=next(t for t in r.findall('.//table-wrap') if 'Table 6'==' '.join(t.xpath('./label//text()')))
case_rows=[]
for tr in t.findall('.//tbody/tr'):
 cells=tr.findall('./td')
 case_rows.append({'id':' '.join(cells[0].itertext()),'diagnosis':' '.join(cells[1].itertext())})
expected=j('SOURCE-STATUS.json')['new_sources'][0]['printed_cases']
check('management_five_printed_identity_columns_only',case_rows==expected,case_rows)
check('management_no_denominator_transfer','broader >60 cfDNA / 12 WES' in j('SOURCE-STATUS.json')['new_sources'][0]['status'],'Five cases do not close larger methods universe')
# Actual supplement Table1: read only clinical histology rows; no Table2 statistics.
with zipfile.ZipFile(P/'source-cache/TF2026-actual-published-supplement.docx') as z:
 root=etree.fromstring(z.read('word/document.xml'))
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
t=root.findall('.//w:tbl',ns)[0]
rows=[]
for tr in t.findall('./w:tr',ns):
 cells=tr.findall('./w:tc',ns)
 title=' '.join(cells[0].xpath('.//w:t/text()',namespaces=ns)).strip() if cells else ''
 if title in ['Leiomyosarcoma','Liposarcoma','Undifferentiated   pleomorphic   sarcoma','Synovial  sarcoma','Angiosarcoma','Others']:
  raw=' '.join(cells[1].xpath('.//w:t/text()',namespaces=ns))
  count=int(raw.split('(')[0].replace(' ',''))
  label=' '.join(title.split())
  rows.append((label,count))
expected=j('SOURCE-STATUS.json')['new_sources'][1]['histologies']
check('TF_supplement_clinical_roster',dict(rows)==expected,dict(rows))
check('TF_cohort_reconciliation',sum(dict(rows).values())==192 and dict(rows)['Others']==80,{'cohort':192,'Others':80,'old48':'Preserved only as corrected historical error in AMENDMENT01'})
# Pleural Table2 choose subtype and count only, not survival columns.
r=etree.parse(str(P/'source-cache/PMC12497659.xml'))
t=next(t for t in r.findall('.//table-wrap') if 'TABLE 2'==' '.join(t.xpath('./label//text()')))
others=[]
for tr in t.findall('.//tbody/tr'):
 c=tr.findall('./td')
 if c and ' '.join(c[0].itertext()).strip().lower()=='others':others.append(' '.join(c[1].itertext()))
check('pleural_Other_identity_scope',others==['36 (36)'],{'Other':36,'cohort':98,'remaining_identity':'Unresolved, not excluded'})
# Hsp70 source Table1 entity/stage counts only, never concentration or ROC tables.
r=etree.parse(str(P/'source-cache/PMC13163040.xml'))
t=next(t for t in r.findall('.//table-wrap') if 'Table 1'==' '.join(t.xpath('./label//text()')))
sarcoma=[]
for tr in t.findall('.//tbody/tr'):
 c=tr.findall('./td')
 if c and ' '.join(c[0].itertext()).strip()=='Sarcoma':sarcoma.append([' '.join(x.itertext()).strip() for x in c])
check('Hsp70_generic_sarcoma_stage_scope',sarcoma==[['Sarcoma','8','–','–','8','–']],{'eight_generic_metastatic_samples':True,'EMC_identity':'Unresolved'})
cohort=next(sec for sec in r.findall('.//sec') if 'Analyzed Cohort' in ' '.join(sec.xpath('./title//text()')))
clinical=' '.join(cohort.findall('./p')[0].itertext())
check('Hsp70_pretreatment_population_scope','before implementation of any kind of oncological therapy' in clinical, 'Cross-sectional pretreatment population; no serial patient trace established')
paras=[' '.join(p.itertext()) for p in r.findall('.//p')]
av=[v for v in paras if 'reasonable request' in v]
supp=[v for v in paras if 'Figure S1:' in v and 'Figure S2:' in v]
check('Hsp70_actual_advertised_data_scope',len(av)==1 and len(supp)==1,{'patient_dataset':'Corresponding-author reasonable request','supplement':'Two analytical figures; no advertised patient identity/serial matrix','no_outreach':True})
for n in ['Pending-Tsoi-DataCite','Pending-Bui-DataCite','Pending-Anderson-DataCite']:
 d=json.loads((P/'source-cache'/n).read_text());check('DataCite_exact_related_DOI_'+n,d['meta']['total']==0,'Indexed query scope only, not data/EMC absence')
check('no_new_outcomes_or_numeric_stage',j('SOURCE-STATUS.json')['newly_inspected_case_analyte_outcomes']==0 and not j('SOURCE-STATUS.json')['new_numeric_stage_launched'],'Clinical metadata only; previous R3 results status-only reused')
check('no_promotion_or_exhaustion',not j('DECISION.json')['publication_worthy_finding'] and not j('DECISION.json')['campaign_exhausted'],'Specific pending suitable evidence blocks promotion')
check('budget',port['new_retained_raw_bytes']<=port['soft_cap_bytes'],port['new_retained_raw_bytes'])
check('storage_floor',shutil.disk_usage(P).free>=port['minimum_free_bytes'],shutil.disk_usage(P).free)
root=Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=P,text=True).strip())
tracked=subprocess.check_output(['git','ls-files','--',str(P.relative_to(root)/'source-cache')],cwd=root,text=True).strip()
check('no_tracked_raw_or_catalogues',not tracked,'Raw originals and all three full query catalogues ignored')
result={'utc':datetime.now(timezone.utc).isoformat(),'scope':'Source identity/count/hash/decision boundary checks only; no biomarker case outcomes, no gene values, no restricted mechanisms or images','checks':checks,'passed':True,'failed':0}
(P/'AUDIT-RESULTS.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'passed':True,'checks':len(checks),'prior_artifact_bindings':prior_count,'new_raw_bytes':port['new_retained_raw_bytes'],'free_bytes':shutil.disk_usage(P).free}))
