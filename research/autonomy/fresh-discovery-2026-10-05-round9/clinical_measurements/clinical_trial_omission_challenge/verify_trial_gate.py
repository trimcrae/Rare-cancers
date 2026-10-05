"""Local source/identity/method/availability replay; no network or assay values."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,datetime,shutil
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
OWNER=Path('/workspace/emc-r6-fapi_broader/research/autonomy/fresh-discovery-2026-10-05-round9/functional_new/clinical_trial_individual_gate')
checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(n,v):
 checks.append({'check':n,'pass':bool(v)})
 if not v:raise AssertionError(n)
check('prospective review plan exact',sha(HERE/'PLAN.json')=='6618151b994189ad3c7c785a25a4a71fa53b960e8255edd97cfbc8389284716b')
check('new clinical primary selection exact',sha(HERE/'SOURCE-SELECTION-FROZEN.json')=='b8c377e19457a0a81ca470ca0f1ea5090720d2a5011e91271319ef84f9f2a9d6')
port=json.loads((HERE/'PORTABILITY.json').read_text())
for r in port['shared_source_inputs']:check('shared unchanged source '+Path(r['path']).name,sha(Path(r['path']))==r['sha256'] and Path(r['path']).stat().st_size==r['bytes'])
metadata=[]
for r in port['shared_source_inputs'][:3]:metadata+=json.loads(Path(r['path']).read_text())['resultList']['result']
check('complete inherited295 metadata records',len(metadata)==295)
check('new source genuine citation exists',any(r.get('id')=='27458288' and r.get('pmcid')=='PMC5321073' and r.get('doi','').lower()=='10.1200/jco.2016.67.6346' for r in metadata))
for r in port['new_raw_sources']:check('new ignored error original exact',sha(HERE/r['file'])==r['sha256'] and (HERE/r['file']).stat().st_size==r['bytes'])
check('6148Bnew error only under cap',port['new_raw_bytes_including_copies']==6148<8388608)
a=json.loads((HERE/'ACCESS-PRIMARY.json').read_text());check('one exactEPMC500 route notarticle',a['attempts']==1 and '500' in a['error'] and not (HERE/'raw-cache/PMC5321073.xml').exists())
a=json.loads((HERE/'ACCESS-ALTERNATE.json').read_text());check('BioC200 notarticle',a['attempts']==1 and a['http']==200 and a['bytes']==6148 and a['status']=='not primary article XML; no eligibility accepted')
raw=HERE/'raw-cache/PMC5321073-BioC.xml';check('standard nonarticle error digest',sha(raw)=='3acc5f4c51ec704cd708d3379196db9f66442a96c9bf275773710e0de0196b52')
try:
 z=E.parse(raw).getroot();accepted=bool(z.findall('.//document')) and bool(z.findall('.//passage'))
except E.ParseError:accepted=False
check('error response no accepted primarydocument',not accepted)
src=Path(port['shared_source_inputs'][3]['path']);x=E.parse(src).getroot();out=json.loads((HERE/'SAMBA102-IDENTITY-ASSAY-SCHEMA-CHALLENGE.json').read_text());t=x.find(".//table-wrap[@id='tbl2']");labels=[]
for ri,tr in enumerate(t.findall('.//tbody/tr')):
 ci=0
 for td in list(tr):
  if td.tag not in ['td','th']:continue
  if ci in [0,2]:
   text=''.join(td.itertext()).strip()
   if text:labels.append((ri,ci,text))
  ci+=int(td.get('colspan','1'))
check('all34diagnosis cells source replay',len(labels)==34 and labels==[(r['row'],r['logical_diagnosis_column'],r['label']) for r in out['all_histology_labels']])
check('all3authorEMC baseline count', ''.join(t.findall('.//tbody/tr')[11].findall('td')[1].itertext()).strip()=='3' and out['author_EMC_patient_count_metadata']==3)
check('generic roundcell/ddCHS labels preserved',all(any(v==s for _,_,v in labels) for s in ['Small round cell sarcoma NOS','Round cell sarcoma with EWSR1–non-ETS fusion','De-differentiated chondrosarcoma']))
check('no individual IDs or independent donor imputation',out['individual_EMC_case_ids'] is None and out['independent_donor_count_across_sources'] is None)
headers=[]
for tt in x.findall('.//table-wrap'):headers.append({'table_id':tt.get('id'),'label':tt.findtext('label'),'headers':[[''.join(c.itertext()) for c in tr.findall('th')+tr.findall('td')] for tr in tt.findall('.//thead/tr')]})
check('allmain schemas match whitelistedtheads',headers==out['table_schema'])
q=x.find(".//table-wrap[@id='tbl4']");names=[];occupied={}
for ri,tr in enumerate(q.findall('.//tbody/tr')):
 used={c for c,n in occupied.items() if n>0};nxt={c:n-1 for c,n in occupied.items() if n>1};ci=0
 for td in list(tr):
  if td.tag not in ['td','th']:continue
  while ci in used:ci+=1
  cs=int(td.get('colspan','1'));rs=int(td.get('rowspan','1'))
  if ci==0:names.append({'row':ri,'diagnosis_column_only':''.join(td.itertext()).strip()})
  for j in range(ci,ci+cs):
   if rs>1:nxt[j]=rs-1
  ci+=cs
 occupied=nxt
check('table4onlytumor fields replay',names==out['table4_tumor_only_labels'] and len(names)==11)
check('noEMC inselectedtable only',not any('myxoid chondrosarcoma' in z['diagnosis_column_only'].lower() for z in names))
m=x.find("./body/sec[@id='sec3']");paras=[''.join(q.itertext()) for q in m.findall('.//p')]
check('selected clinicalmethods exact',out['selected_primary_methods']==[q for q in paras if not q.startswith('For mutational targets')])
check('table4outcomeconditioned selection documented',any(q.startswith(out['table4_selection_method_clause']) for q in paras))
check('request-onlyindividual data actualsource','The data generated in this study are available upon reasonable request from the corresponding author.' in paras)
check('heterogeneous RECISTprotocol clinicalconditions source',any('RECIST (version 1.1) or immune-related RECIST' in q for q in paras))
old=PARENT/'FREEZE.json';check('original clinicalfreeze unchanged',sha(old)=='630b77efcfde36825e4e11c4d5db1a61ce65e62c1d18e01598f28aecaf0f25fa')
for z in json.loads(old.read_text())['files']:check('original clinicalexport '+z['path'],sha(PARENT/z['path'])==z['sha256'])
reuse=json.loads((HERE/'VERIFIED-REUSE.json').read_text());check('availability correction exact',sha(Path(reuse['availability_amendment_freeze']['path']))==reuse['availability_amendment_freeze']['sha256'])
check('all7prior selected sources retained',len(reuse['conditions'])==7)
check('owner final manifest exact',sha(OWNER/'MANIFEST.json')=='3396e214017d3e059b6808b92b62e2e61b4d69645c19f0f006f5eb8c52c2943f')
manifest=json.loads((OWNER/'MANIFEST.json').read_text());check('owner11 final exports',len(manifest['files'])==11)
for z in manifest['files']:check('owner final exact export '+z['file'],sha(OWNER/z['file'])==z['sha256'] and (OWNER/z['file']).stat().st_size==z['bytes'])
coverage=json.loads((OWNER/'ALL-ELIGIBLE-IDENTITY-COVERAGE.json').read_text());check('owner all34 and3EMC metadata',len(coverage['all_histology_labels'])==34 and coverage['author_EMC_case_count']==3)
baseline=[]
for tr in x.find(".//table-wrap[@id='tbl2']").findall('.//tbody/tr'):
 cells=tr.findall('td');label=''.join(cells[0].itertext()).strip();num=''.join(cells[1].itertext()).strip()
 if label:baseline.append((label,num))
 single=''.join(cells[2].itertext()).strip()
 if single:baseline.append((single,'1'))
check('owner all34 baseline label/counts exactly match source',sorted(baseline)==sorted((z['source_histology_label'],z['source_baseline_case_count']) for z in coverage['all_histology_labels']))
check('owner no biomarker outcomes read',coverage['biomarker_outcome_values_read']==0)
report=(OWNER/'REPORT.txt').read_text();check('owner plain report preserves useful value and gaps','no explicit EMC row; this does not establish absence' in report and 'The wider campaign continues' in report and 'No response, survival, mutation or protein-assay values were read' in report)
check('free10GiB',shutil.disk_usage(HERE).free>=10737418240)
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS bounded clinical source/identity/schema/value replay','checks':checks,'checks_count':len(checks),'network_requests_during_verification':0,'assay_or_endpoint_values_read':0,'limits':'Source/metadata/method scope only; public uninspected supplements and participant links remain pending. No independent donors or clinical benefit inferred.'}
(HERE/'VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(checks),'failed':0}))
