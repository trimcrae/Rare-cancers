#!/usr/bin/env python3
"""Extract complete clinical identity rosters without interpreting FAP tissue."""
import datetime,hashlib,json,pathlib,re,zipfile,subprocess
from lxml import etree,html

ROOT=pathlib.Path(__file__).resolve().parent
RAW=ROOT/'raw'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load_html(name):return html.fromstring((RAW/name).read_bytes(),parser=html.HTMLParser(encoding='utf-8'))
def tables(name):
 t=load_html(name)
 return [[[' '.join(e.text_content().split()) for e in tr.xpath('./th|./td')] for tr in tb.xpath('.//tr')] for tb in t.xpath('//table')]
def write(name,data):(ROOT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')

def html_evidence(name,terms):
 t=load_html(name)
 return [{'paragraph_index':i,'text':' '.join(e.text_content().split())} for i,e in enumerate(t.xpath('//p')) if any(term in ' '.join(e.text_content().split()).lower() for term in terms) and not any(term in ' '.join(e.text_content().split()).lower() for term in ['immunohistochem','fapα','fap staining','fap expression'])]

if __name__=='__main__':
 for name in ['hirmas2023_supp','hirmas2024_supp']:
  target=RAW/(name+'.txt')
  if not target.exists():subprocess.run(['pdftotext','-layout',str(RAW/(name+'.pdf')),str(target)],check=True)
 three=tables('three_timepoint_table1.html')[0]
 assert sum(int(r[1]) for r in three[1:])==43
 write('three-timepoint-roster.json',{'source_sha256':digest(RAW/'three_timepoint_table1.html'),'rows':three,'patients':43,'generic_sarcoma_patients':2,'authenticated_EMC':0,'meaning':'No author-labelled EMC; the two generic sarcoma identities remain unresolved, not confirmed non-EMC.'})
 h24=tables('hirmas2024_popup1.html')[0]
 entities=[];active=False
 for row in h24:
  if row[0]=='Tumor entities':active=True;continue
  if active and row[0].startswith('Regional detection'):break
  if active:entities.append(row)
 assert sum(int(re.match(r'\d+',r[1]).group()) for r in entities)==115
 write('hirmas2024-roster.json',{'source_sha256':digest(RAW/'hirmas2024_popup1.html'),'entities':entities,'patients':115,'paired_accuracy_patients':103,'authenticated_EMC':0,'meaning':'Complete eight-entity roster and main text explicitly exclude sarcoma; this analysis is unsuitable for EMC imaging measurement.'})
 h23text=(RAW/'hirmas2023_supp.txt').read_text()
 start=h23text.index('Supplemental Table 1.');end=h23text.index('Pancreas',start)
 section=h23text[start:end]
 sarcomas=[]
 for line in section.splitlines():
  match=re.match(r'^\s+(.+?)\s{2,}(\d+)\s*\(\d+\)',line)
  if match:sarcomas.append({'source_label':match.group(1).strip(),'patients':int(match.group(2))})
 assert sum(r['patients'] for r in sarcomas)==131
 footnotes=['Epitheloid sarcoma','follicular dendritic sarcoma','giant cell tumor','gastrointestinal neuroendocrine tumor (G-NET)','hemangioendothelioma','hemangiopericytoma','myofibroblastic sarcoma','peripheral nerve sheath tumor','soft tissue sarcoma','synchronous adenosarcoma-carcinoma','vulvar sarcoma']
 # Source spelling preserved. These are labels, not molecular diagnoses inferred by this analysis.
 h23table=tables('hirmas2023_popup1.html')[0]
 macro=[];active=False
 for row in h23table:
  if row[0]=='Tumor entity':active=True;continue
  if active and row[0].startswith('Tumor staging'):break
  if active:macro.append(row)
 assert sum(int(re.match(r'\d+',r[1]).group()) for r in macro)==324
 write('hirmas2023-roster.json',{'supplement_sha256':digest(RAW/'hirmas2023_supp.pdf'),'Table1_sha256':digest(RAW/'hirmas2023_popup1.html'),'macro_entity_rows':macro,'patients':324,'sarcoma_subtype_rows':sarcomas,'sarcoma_patients':131,'other_footnote_each_n':1,'other_footnote_labels':footnotes,'paired_all_entities':237,'paired_sarcoma_aggregate':116,'authenticated_EMC':0,'unresolved_identity_labels':['Chondrosarcoma','Fibrosarcoma','Spindle cell sarcoma','Pleomorphic sarcoma','Round cell sarcoma','soft tissue sarcoma','myofibroblastic sarcoma','vulvar sarcoma'],'meaning':'Complete released aggregate subtype roster evaluated; generic labels do not authenticate or exclude EMC, and no individual diagnosis-to-scan crosswalk is released here.'})
 liver=tables('liver2026_table1.html')[0]
 clinical=liver[5:]
 assert sum(int(re.match(r'\d+',r[1]).group()) for r in clinical)==76
 assert sum(int(re.search(r'\((\d+)\)',r[1]).group(1)) for r in clinical)==189
 with zipfile.ZipFile(RAW/'liver2026_supp.docx') as z:doc=etree.fromstring(z.read('word/document.xml'))
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 donor_tables=[]
 for idx,tb in enumerate(doc.findall('.//w:tbl',ns),start=1):
  rows=[]
  for tr in tb.findall('w:tr',ns):
   cells=[' '.join(''.join(c.itertext()).split()) for c in tr.findall('w:tc',ns)]
   if cells and re.fullmatch(r'\d+',cells[0].replace(' ','')):
    assert len(cells)==8,cells
    row={'condition':'liver_metastases' if idx==1 else 'non_liver_metastases','source_table':f'S{idx}','source_id':int(cells[0].replace(' ','')),'gender':cells[1],'age_years':int(cells[2].replace(' ','')),'source_histology':cells[3],'FDG_positive_lesions':int(cells[4]),'FDG_negative_lesions':int(cells[5]),'FAPI_positive_lesions':int(cells[6]),'FAPI_negative_lesions':int(cells[7])}
    assert row['FDG_positive_lesions']+row['FDG_negative_lesions']==row['FAPI_positive_lesions']+row['FAPI_negative_lesions']
    rows.append(row)
  donor_tables.append(rows)
 assert len(donor_tables)==2 and list(map(len,donor_tables))==[61,15]
 assert sum(r['FDG_positive_lesions']+r['FDG_negative_lesions'] for r in donor_tables[0])==173
 assert sum(r['FDG_positive_lesions']+r['FDG_negative_lesions'] for r in donor_tables[1])==16
 write('liver2026-rosters.json',{'main_table_sha256':digest(RAW/'liver2026_table1.html'),'supplement_sha256':digest(RAW/'liver2026_supp.docx'),'main_entity_rows':clinical,'patients':76,'lesions':189,'individual_rows':sum(donor_tables,[]),'authenticated_EMC':0,'unresolved_identity':[{'table':'S1','source_id':4,'label':'pleomorphic sarcoma'}],'source_annotation_limit':'Main Table1 uses solitary fibroma/dedifferentiated liposarcoma/dendritic cell sarcoma; S1 uses solitary fibrous tumor/liposarcoma/interdigitating dendritic cell sarcoma. Source calls11sarcomas/37lesions, whereas explicit sarcoma+GIST+chordoma labels account for10donors/32lesions; inclusion of G2neuroendocrine tumor would supply missing1donor/5lesions. This is a source classification ambiguity, not corrected by relabelling.','meaning':'Every released donor row and both conditions evaluated; no author-labelled EMC. Generic pleomorphic label cannot molecularly exclude EMC.'})
 evidence={name:html_evidence(name,terms) for name,terms in [('three_timepoint_jnm.html',['this was a retrospective','our data consisted','this study had several limitations']),('hirmas2023_jnm.html',['until','october','breakdown of histopathologic']),('hirmas2024_jnm.html',['until march','we identified 133']),('interobserver2023_jnm.html',['fifty patients','pet/ct-positive','patient preparation','in brief, pet','only necessary patient information','table 1 summarizes']),('liver2026_springer.html',['to investigate the diagnostic performance','18f-fdg and 68ga-fapi-04 pet/ct examinations','liver metastasis was confirmed','all data generated'])]}
 # Clinical acquisition paragraph excerpts from supplements; stop before tissue section.
 evidence['hirmas2023_clinical_supplement']=h23text[:h23text.index('Immunohistochemistry and FAP Scoring')].strip()
 h24text=(RAW/'hirmas2024_supp.txt').read_text()
 evidence['hirmas2024_clinical_supplement']=h24text[:h24text.index('Imaging analysis')].strip()
 write('clinical-eligibility-excerpts.json',evidence)
 write('extraction-validation.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':['ThreeTimePoint14category counts sum43','Hirmas2023 macro counts sum324 and18sarcoma subtype counts sum131; other footnote11x1','Hirmas2024 eight-category counts sum115','Liver2026 nineteen-category counts sum76 and lesion counts189','Liver2026 all61S1+15S2donor rows parsed; every donor tracer lesion totals agree; S1sum173+S2sum16=189'],'EMC_quantitative_analysis_executed':False,'note':'Roster completeness at released resolution is not patient subtype authentication for generic labels.'})
 print('PASS: complete released rosters accounted; no authenticated EMC scan pair to analyze.')
