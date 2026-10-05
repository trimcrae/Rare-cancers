"""Read-only reproduction of source identity/condition gates; no network or assay values."""
from pathlib import Path
import json,hashlib,collections,shutil,xml.etree.ElementTree as E,zipfile,io,datetime
HERE=Path(__file__).resolve().parent
OWNER=Path('/workspace/emc-r6-fapi_broader/research/autonomy/fresh-discovery-2026-10-05-round9/functional_new/broader_native_assay_followthrough')
CHALLENGE=Path('/workspace/emc-r6-challenge/research/autonomy/fresh-discovery-2026-10-05-round9/imprinting/dynamic_native_assays_challenge')
checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(n,v):
 checks.append({'check':n,'pass':bool(v)})
 if not v:raise AssertionError(n)
def parse(f):
 rows=[];r=None
 for line in f.read_text().splitlines():
  if line.startswith('^SAMPLE = '):r={'gsm':line.split(' = ',1)[1],'chars':{}};rows.append(r)
  elif r is not None and line.startswith('!Sample_') and ' = ' in line:
   k,v=line.split(' = ',1)
   if k=='!Sample_characteristics_ch1':
    key,val=v.split(': ',1) if ': ' in v else (v,'');r['chars'][key]=val
   elif k in ['!Sample_title','!Sample_source_name_ch1','!Sample_organism_ch1']:r[k.removeprefix('!Sample_')]=v
 return rows
check('prospective reviewer plan preserved',sha(HERE/'PLAN.json')=='4f1e72b6bf317b84e8ad4d3c0ba747e13d58a569cd4ffb11c272e3963676725a')
c=CHALLENGE/'raw-cache/geo-broader-dynamic-series-metadata.json';check('actual shared catalogue exact',sha(c)=='932cae6c1baeaf8c2884b0ef8d4395017f00909f7da1df2977e9026b0e658c75')
x=json.loads(c.read_text())['result'];check('all53 source metadata records',len(x['uids'])==53 and len(set(x['uids']))==53)
port=json.loads((HERE/'PORTABILITY.json').read_text())
for r in port['raw_files']:check('retained exact raw '+r['file'],sha(HERE/r['file'])==r['sha256'] and (HERE/r['file']).stat().st_size==r['bytes'])
check('source budget includes all copies',sum(r['bytes'] for r in port['raw_files'])==port['new_raw_bytes_including_copies']<8388608)
rows=parse(HERE/'raw-cache/GSE140819-all-GSM-brief.txt');check('all40 unique source libraries',len(rows)==40 and len({r['gsm'] for r in rows})==40)
check('all40 catalogue IDs agree with official sample source',set(r['gsm'] for r in rows)==set(r['accession'] for r in x['200140819']['samples']))
q=json.loads((HERE/'GSE140819-ALL-CONDITION-ELIGIBILITY.json').read_text());out=q['rows'];check('all40 exported rows match source',[(r['gsm'],r['title'],r['source_entity_label'],r['declared_sample_type']) for r in out]==[(r['gsm'],r['title'],r['source_name_ch1'],r['chars']['sample type']) for r in rows])
check('all source entity counts agree',dict(collections.Counter(r['source_name_ch1'] for r in rows))==q['source_label_counts']=={'lung cancer':5,'neuroblastoma':10,'MBC':10,'glioma':2,'CLL':2,'ovarian':5,'melanoma':2,'sarcoma':4})
check('all19 generic clinical/organ/sarcoma identities stay pending',sum(r['status'].startswith('pending') for r in out)==19 and all(r['status'].startswith('pending') for r in out if r['source_entity_label'] in ['MBC','ovarian','sarcoma']))
check('all4 generic sarcoma preparations retained',[(r['gsm'],r['declared_sample_type']) for r in out if r['source_entity_label']=='sarcoma']==[('GSM4186992','HTAPP-951-SMP-4652 TST-V2'),('GSM4186993','HTAPP-951-SMP-4652 TST-V3'),('GSM4186994','HTAPP-951-SMP-4652 CST-V3'),('GSM4186995','HTAPP-975-SMP-4771 TST-V3')])
check('no independent donor imputation',all(r['donor_identity'] is None for r in out))
geo=(HERE/'raw-cache/GSE140819-series-brief.txt').read_text().splitlines();design=' '.join(l.split(' = ',1)[1] for l in geo if l.startswith('!Series_overall_design = '))
check('NSCLC title/class source matching',all(r['title'].startswith('NSCLC') for r in rows if r['source_name_ch1']=='lung cancer') and 'non-small cell lung carcinoma' in design)
check('primary-vs-deposit unit discrepancy preserved','23 tumors, from 22 patients spanning 39 sample preparations' in design and len(rows)==40)
check('controlled raw access recorded','controlled access' in design and 'DUOS-000111' in design)
primary=E.parse(HERE/'raw-cache/PMC7220853.xml').getroot();method=primary.find("./body/sec[@id='Sec13']/sec")
methodrec=json.loads((HERE/'PRIMARY-METHODS-AND-VALUE.json').read_text())
for r in methodrec['selected_method_sections_only']:
 s=method.find("sec[@id='"+r['section_id']+"']");check('exact permitted primary methods '+r['section_id'],s is not None and s.findtext('title')==r['title'] and [''.join(z.itertext()) for z in s.findall('p')]==r['methods'])
check('human sample methods confirm neuroblastoma O-PDX identity',any('neuroblastoma O-PDX' in t for r in methodrec['selected_method_sections_only'] for t in r['methods']))
check('generic sarcoma methods not subtype authentication',any('sarcoma (IRB protocol 17-104)' in t for r in methodrec['selected_method_sections_only'] for t in r['methods']))
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(HERE/'raw-cache/41591_2020_844_MOESM2_ESM.xlsx') as z:
 ss=E.fromstring(z.read('xl/sharedStrings.xml'));strings=[''.join(s.itertext()) for s in ss.findall('m:si',ns)]
 w=E.fromstring(z.read('xl/worksheets/sheet1.xml'));head=w.find('m:sheetData/m:row',ns)
 headers=[strings[int(c.findtext('m:v',namespaces=ns))] for c in head.findall('m:c',ns) if c.get('t')=='s']
check('supplement is geneset schema not patient roster',headers==['genesets','geneset.names','geneset.descriptions'])
f=OWNER/'raw-cache/GSE135323-allGSM-brief.txt';check('shared other source exact',sha(f)=='5d04ebf70dde5d677bca4ed030f1d3dcbeaeaec9feb65d4acf6b63efde50df1e')
r=parse(f);o=json.loads((OWNER/'GSE135323-ASSAY-CONDITION-MAP.json').read_text());check('owner other source map exact',sha(OWNER/'GSE135323-ASSAY-CONDITION-MAP.json')=='30eac394687f76bdd2852ed69498e3c81ecc6da0e966d1d43a125e394d9376c6')
check('all132 independent row replay',len(r)==len(o['all_condition_rows'])==132 and [(a['gsm'],a['title'],a['source_name_ch1'],a['chars'].get('cell type'),a['chars'].get('exposure'),a['chars'].get('treatment concentration')) for a in r]==[(a['gsm'],a['title'],a['source_name'],a['declared_cell_type'],a['declared_exposure'],a['declared_treatment_concentration']) for a in o['all_condition_rows']])
check('source-defined Ewing/osteoblast groups include reference inputs',dict(collections.Counter(a['source_name_ch1'] for a in r))==o['source_group_counts']=={"Ewing's Sarcoma Cells 2D":57,"TE-Tumor, 3D Osteoblasts and Ewing's Sarcoma":60,'TE-Bone, 3D Osteoblasts':15})
check('all reference and blank libraries preserved',set(a['title'] for a in o['all_condition_rows'] if a['technical_input_label'])==set(o['reference_or_blank_record_titles']) and len(o['reference_or_blank_record_titles'])==3)
check('TempO-seq method directly named in source',any('TempO' in l for l in f.read_text().splitlines() if l.startswith('!Sample_extract_protocol_ch1 = ')))
check('verified all30 GSE98824 reuse exact',sha(CHALLENGE/'EVALUATED-BROADER-SOURCE.json')=='8c02c91c8362e1846930d530a4ff9e1bf5974340b9b3249e7571dfb47816f32d')
check('GSE98824 original source exact',sha(CHALLENGE/'raw-cache/GSE98824-source-metadata.txt')=='e2ba04bc6c994fa36aa3f04f7764a92e857ff5902da3b47185fd8f3014e59490')
previous=HERE.parent/'phosphoproteomic_manifest_review/dated_backend_index_review/diagnosis_eligibility_review';check('preceding scientific freeze immutable',sha(previous/'FREEZE.json')=='e5b4486b2fb6109371e8356cb4b575cf69d5dabf1001f3ac1936e0575cd3a1e3')
for a in json.loads((previous/'FREEZE.json').read_text())['bindings']:check('preceding exact export '+a['file'],sha(previous/a['file'])==a['sha256'])
check('owner final manifest exact',sha(OWNER/'MANIFEST.json')=='915a1b9cfa2ce86249115ca5a5f99762d8e1eb90adea115787751accc5d40333')
manifest=json.loads((OWNER/'MANIFEST.json').read_text());check('owner16 frozen exports',len(manifest['files'])==16)
for z in manifest['files']:check('owner frozen export '+z['file'],sha(OWNER/z['file'])==z['sha256'] and (OWNER/z['file']).stat().st_size==z['bytes'])
for z in manifest['borrowed_peer_source_receipts']:check('owner exact borrowed source '+Path(z['path']).name,sha(Path(z['path']))==z['sha256'])
cover=json.loads((OWNER/'COVERAGE.json').read_text());check('owner50 other source conditions remain pending',any(z['source']=='Remaining50 catalogue entries' and 'pending' in z['status'] for z in cover['reconciled']))
g=json.loads((OWNER/'GSE140819-IDENTITY-CONDITION-COVERAGE.json').read_text());check('owner all40 row projection matches independent source',[(z['gsm'],z['title'],z['source_label'],z['declared_preparation']) for z in g['all40_preparation_rows']]==[(z['gsm'],z['title'],z['source_name_ch1'],z['chars']['sample type']) for z in rows])
check('owner40 and19 pending counts',len(g['all40_preparation_rows'])==40 and g['identity_pending_preparations']==19 and g['source_annotated_named_different_entity_preparations']==21)
check('owner scientific value no numerical stage',json.loads((OWNER/'DECISION.json').read_text())['new_biological_values_accessed']==0 and 'NO-GO' in json.loads((OWNER/'DECISION.json').read_text())['decision'])
check('free10GiB',shutil.disk_usage(HERE).free>=10737418240)
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS scoped source/method/identity replay','checks':checks,'checks_count':len(checks),'reviewer_network_calls_during_verification':0,'biological_outcome_values_inspected':0,'limits':'All records checked at declared source metadata/method scope. Generic labels, unpublished crosswalks and other underlying catalogue series remain pending. Not a biological result or complete-source closure.'}
(HERE/'VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(checks),'failed':0}))
