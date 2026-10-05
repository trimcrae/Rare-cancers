#!/usr/bin/env python3
"""Export only needed primary eligibility rows and exact input receipts."""
import datetime,hashlib,json,pathlib,re,xml.etree.ElementTree as E
BASE=pathlib.Path(__file__).resolve().parent; RAW=BASE/'raw-cache'; ROOT=pathlib.Path('/workspace/Rare-cancers')
def write(n,d): (BASE/n).write_text(json.dumps(d,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def txt(n):return ' '.join(n.itertext()).strip()
out={}
for name,tableid in [('integration2026','Tab1'),('cho2024','Tab1'),('serum2025','cancers-17-00553-t001')]:
 r=E.fromstring((RAW/(name+'.xml')).read_bytes()); tables=r.findall('.//table-wrap')
 t=next((x for x in tables if x.attrib.get('id')==tableid),tables[0])
 rows=[[txt(c) for c in tr] for tr in t.findall('.//tbody/tr')]
 out[name]={'source':bind(RAW/(name+'.xml')),'table_label':txt(t.find('label')),'caption':txt(t.find('caption')),'rows':rows,'table_footnotes':[txt(x) for x in t.findall('table-wrap-foot')],'scope':'complete needed histology/model roster; no compound-response values exported'}
 assert len(rows)=={'integration2026':19,'cho2024':18,'serum2025':8}[name] if name!='serum2025' else True
write('PRIMARY-ROSTERS.json',out)
s=(RAW/'living2026-text.txt').read_text();a=s.index('TA B L E 1      Overview of sarcoma cell cultures.');b=s.index('\f',a)
block=s[a:b]
donors=[
 ('TBB-S-050',['SAR007'],'Osteosarcoma'),('TBB-S-010',['SAR011'],'Synovial sarcoma'),('TBB-S-045',['SAR030'],'Undifferentiated sarcoma, pleomorphic'),('TBB-S-247',['SAR040'],'Osteosarcoma'),('TBB-S-250',['SAR043'],'Carcinosarcoma'),('TBB-S-047',['SAR045'],'Extraskeletal osteosarcoma'),('TBB-S-087',['SAR109'],'Undifferentiated sarcoma, pleomorphic'),('TBB-S-099',['SAR121'],'Undifferentiated sarcoma, pleomorphic'),('TBB-S-058',['SAR156'],'Sarcoma with BCOR genetic alterations'),('TBB-S-044',['SAR183A1','SAR183A2','SAR183A3','SAR183A4','SAR186A1','SAR186A2','SAR186A4','SAR291'],'MPNST'),('TBB-S-155',['SAR187A2','SAR187A3'],'Leiomyosarcoma'),('TBB-S-161',['SAR191'],'Synovial sarcoma'),('TBB-S-028',['SAR295'],'MPNST'),('TBB-S-052',['SAR311','SAR317','SAR357'],'Myxofibrosarcoma'),('TBB-S-229',['SAR313'],'Well-differentiated liposarcoma'),('TBB-S-031',['SAR343'],'Rhabdomyosarcoma'),('TBB-S-342',['SAR433'],'Synovial sarcoma'),('TBB-S-146',['SAR172'],'Giant cell tumour'),('TBB-S-316',['SAR401'],'Carcinosarcoma')]
assert len(donors)==19 and sum(len(x[1]) for x in donors)==29
assert all(c in block for _,cs,_ in donors for c in cs)
write('LIVING-ROSTER.json',{'source':bind(RAW/'living2026.pdf'),'text_derivative':bind(RAW/'living2026-text.txt'),'primary_table1_verbatim':block,'donor_rows':[{'donor':d,'cultures':c,'diagnosis_literal':h,'EMC_eligibility':'unresolved broad label, not authenticated EMC' if 'Undifferentiated sarcoma' in h else 'source diagnosis is a different named entity; unsuitable as EMC observation'} for d,c,h in donors],'commercial_control':{'model':'SW1353','diagnosis_literal':'Chondrosarcoma','donor':'not a new biobank patient','EMC_eligibility':'generic chondrosarcoma unresolved; no EMC inference'},'accountability':{'biobank_cultures':29,'biobank_donors':19,'table1_patient_rows':19,'table1_commercial_rows':1,'broad_UPS_donors':3,'broad_UPS_cultures':3,'other_named_diagnosis_cultures':26,'generic_commercial_controls':1},'overlap':'TBB-S-044 eight regions/stages from one donor; TBB-S-155 two cultures from one donor; TBB-S-052 three metastases at two timepoints from one donor. These are not new EMC observations.'})
r=E.fromstring((RAW/'qpop2025.xml').read_bytes());paras=[txt(x) for x in r.findall('.//p')]
q=[x for x in paras if x.startswith('The phenotypic drug sensitivity data supporting') or x.startswith('Freshly excised tumor samples were digested')]
write('QPOP-ELIGIBILITY.json',{'source':bind(RAW/'qpop2025.xml'),'supplement_zip':bind(RAW/'qpop2025-supp.zip'),'supplement_pdf':bind(RAW/'41698_2025_851_MOESM1_ESM.pdf'),'supplement_text':bind(RAW/'qpop2025-supp-text.txt'),'relevant_primary_excerpts':q,'roster':'45 successful primary samples from51;14 outcome-evaluable patients,27 treatment outcomes; these are distinct denominators, not45 independent donors. Full45 histology-to-assay crosswalk remains unresolved.','supplement_text_observation':'7-page machine-readable text includes supplementary figures and one primer-sequence TableS1. It does not resolve the45-sample EMC identity crosswalk.','graphics':'accessible but pending eligibility review; not visually inspected during active computer-use ban, no absence inferred from machine-text search','functional_raw_data':'available upon reasonable request, not public individual measurements in retrieved text; no outreach attempted','decision':'No attributable EMC response observation or combination inference.'})
paths=[
 'research/autonomy/fresh-discovery-2026-10-04/functional/RESULTS.txt',
 'research/autonomy/fresh-discovery-2026-10-04/functional/COVERAGE.txt',
 'research/autonomy/fresh-discovery-2026-10-04/functional/reused-Bangerter-all40-measured-ordinal-and-complete-source-overlap-final.json',
 'research/autonomy/fresh-discovery-2026-10-04/functional/reused-Iwata-complete221-screen-and24-IC50-literal-measurements-final.json',
 'research/autonomy/fresh-discovery-2026-10-04-round3/functional_discovery/RESULTS.txt',
 'research/autonomy/fresh-discovery-2026-10-04-round3/functional_discovery/COVERAGE.txt',
 'research/autonomy/fresh-discovery-2026-10-04-round3/functional_discovery/civo-source-receipt.json',
 'research/autonomy/fresh-discovery-2026-10-04-round3/proteomics/RESULTS.txt',
 'research/autonomy/fresh-discovery-2026-10-04-round7/functional_models/RESULTS.txt',
 'research/autonomy/fresh-discovery-2026-10-04-round7/functional_models/COVERAGE.txt',
 'research/autonomy/fresh-discovery-2026-10-04-round7/functional_models/precision-supp-receipt.json',
 'research/autonomy/fresh-discovery-2026-10-05-round8/metabolism/RESULTS.txt',
 'research/autonomy/fresh-discovery-2026-10-05-round8/metabolism/COVERAGE.json',
 'research/autonomy/fresh-discovery-2026-10-05-round8/PORTABILITY.json',
 'research/autonomy/fresh-discovery-2026-10-05-round9/ROUND-CONTRACT.json',
 'research/autonomy/fresh-discovery-2026-10-05-round9/SHARED-INPUTS-REUSE.json']
write('REUSED-INPUTS.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':[bind(ROOT/p) for p in paths],'scope':'verified exact existing outputs/decisions, no reanalysis or raw copies; all40USZ/221NCC/24IC50 remain known measurements and DDR/functional/redox/model/source caveats remain in force'})
queries=[]
for name in ['emc-functional','sarcoma-functional-new','historical-functional']:
 d=json.loads((RAW/(name+'.json')).read_text());queries.append({'query':d['request']['queryString'],'hit_count':d['hitCount'],'returned':len(d['resultList']['result']),'source':bind(RAW/(name+'.json')),'scope':'complete discovery metadata returned, not complete primary-paper review'})
write('SEARCH-COVERAGE.json',{'queries':queries,'dates':'API catalogues as of2026-10-05; broad search hits can be full-text references or other NR4A3 diseases, not EMC participants','primary_candidates':'QPOP2025, ex-vivo integration2026, Gijsels living cultures2026, Cho18lines2024, CIVO2020 and serumNMR2025; pan-cancerphosphoproteomics2026 transferred to diagnostic owner before values','excluded_scope':'Interrupted FAP-tissue/glycan/structural-genomics/HLA reviews were not opened; review-only candidates and non-EMC abstracts are source leads, not functional evidence.'})
print('Eligibility extracts complete; no EMC response calculation.')
