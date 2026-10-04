#!/usr/bin/env python3
"""Authenticate named clinical-source eligibility; never compute unauthenticated EMC ratios."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,hashlib,zipfile,xml.etree.ElementTree as ET,datetime,subprocess
P=Path(__file__).resolve().parent; C=P/'raw-cache'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data):(P/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
for source in ['kessler','lanzafame','pabst']:
 pdf=C/('pabst-appendix.pdf' if source=='pabst' else source+'-supp.pdf')
 subprocess.run(['pdftotext','-layout',str(pdf),str(pdf.with_suffix('.txt'))],check=True)
# Original histology labels and counts. Preserve reported nomenclature verbatim.
kessler=[('Angiosarcoma',1),('Chordoma',6),('Dedifferentiated chondrosarcoma',1),('Endometrial stromal sarcoma',2),('Ewing Sarcoma',2),('Gastrointestinal stromal tumor',2),('Leiomyosarcoma',4),('Low-grade myofibroblastic sarcoma',1),('Malignant solitary fibrous tumor',2),('Myxoid liposarcoma',3),('Malignant peripheral nerve sheath tumor',1),('Mixed Müllerian tumor',1),('Myxofibrosarcoma',2),('Undifferentiated soft tissue sarcoma (NOS, round cell, UPS)',6),('Undifferentiated bone sarcoma',2),('Osteosarcoma',8),('Rhabdomyosarcoma of the bone',1),('Synovialsarcoma',2)]
# Main Table1 leaf categories other than the56 expanded by SupplementTable3.
lanz_main=[('BS: Osteosarcoma',17),('BS: Chondrosarcoma',17),('BS: Ewing sarcoma',8),('BS: Spindle cell sarcoma',5),('BS: UPS',3),('STS: SFT',22),('STS: UPS',15),('STS: Dedifferentiated liposarcoma',15),('STS: Myxoid liposarcoma',14),('STS: Leiomyosarcoma',14),('STS: Synovial sarcoma',7),('STS: Spindle cell sarcoma',7)]
lanz_sts=[('Myxofibrosarcoma',6),('Clear Cell Sarcoma',4),('Fibrosarcoma',4),('GIST',3),('Angiosarcoma',3),('Low-grade Fibromyxoid sarcoma',3),('Endometrial Stromal Sarcoma',2),('Epitheloid sarcoma',2),('Fibromyxosarcoma',2),('Hemangioendothelioma',2),('Pleomorphic Liposarcoma',2),('Mixed Müllerian Tumor',1),('Follicullar dendritic sarcoma',1),('G-NET/sarcoma',1),('Intimasarcoma',1),('Desmoid fibromatosis',1),('MPNST',1),('Rhabdomyosarcoma',1),('Adenosarcoma',1)]
lanz_bone=[('Chordoma',9),('Rhabdomyosarcoma',6)]
pabst_sts=[('Clear cell sarcoma',1),('Endometrial sarcoma',1),('Fibromyxoid sarcoma',1),('Haemangioendothelioma',2),('Leiomyosarcoma',2),('Liposarcoma',6),('Myxofibrosarcoma',2),('Rhabdomyosarcoma',1),('Solitary fibrous tumour (SFT)',1),('Undifferentiated pleomorphic sarcoma (UPS)',1)]
pabst_bone=[('Chondrosarcoma',2),('Ewing sarcoma',2),('Osteosarcoma',1)]
pabst_remaining=[('Gastrointestinal Stromal Tumours',1),('Other',3),('Unknown',1)]
pabst_macro=[('Breast',7),('Cholangiocarcinoma (intrahepatic)',4),('Colorectal',4),('Endometrial',1),('Oesophageal',4),('Head and Neck',2),('Lymphoma',10),('Multiple Myeloma (free light chain kappa)',2),('Neuroendocrine',3),('Non-small cell lung cancer (NSCLC)',15),('Pancreatic',8),('Prostate',3),('Renal cell carcinoma (RCC)',33),('Sarcoma',28),('Seminoma',2),('Thyroid (follicular subtype)',1),('Unknown primary origin',3),('Urothelial carcinoma',14),('Other*',11)]
pabst_other=[('Anal carcinoma',1),('Metanephric adenoma',1),('M. Ormond',1),('Myxoid renal tumour',1),('Penile cancer',2),('Pseudomyxoma peritonei',2),('Schwannoma',1),('Tonsillar carcinoma',1),('Urachus carcinoma',1)]
assert sum(n for _,n in pabst_macro)==155 and sum(n for _,n in pabst_other)==11
assert sum(n for _,n in kessler)==47
assert sum(n for _,n in lanz_sts)==41 and sum(n for _,n in lanz_bone)==15
assert sum(n for _,n in lanz_main+lanz_sts+lanz_bone)==200
assert sum(n for _,n in pabst_sts)==18 and sum(n for _,n in pabst_bone)==5
assert sum(n for _,n in pabst_sts+pabst_bone+pabst_remaining)==28
# Minimal source excerpts contain clinical identity, reading data and lesion-detection context only.
ks=(C/'kessler-supp.txt').read_text();ls=(C/'lanzafame-supp.txt').read_text();ps=(C/'pabst-appendix.txt').read_text()
excerpts={'Kessler_Table1':ks[:ks.index('Supplemental Table 2.')],'Kessler_Table6':ks[ks.index('Supplemental Table 6.'):ks.index('Supplemental Table 7.')],'Kessler_ClinicalReadingDescriptions':ks[ks.index('Supplemental Spreadsheet 1.'):], 'Lanzafame_Table3':ls[ls.index('Other Soft Tissue Sarcoma (n=41)'):ls.index('Supplemental Table 3:')+len('Supplemental Table 3: Complete list of Other Soft\nTissue Sarcoma (n=41) and Other Bone Sarcoma\n(n=15) histology subentities.')],'Pabst_SarcomaRoster':ps[ps.index(' Sarcoma '):ps.index(' Seminoma ')], 'Pabst_ClinicalFibromyxoidConditions':[line.strip() for line in ps.splitlines() if re.search(r'^\s*[78]\s+Fibromyxoid',line)]}
# Main article sources with limited paragraphs supporting chronology/cohort, not tissue interpretation.
for source,ids in [('kessler',['p-11','p-18']),('lanzafame',['p-6','p-13','p-8']),('kratochwil',['p-7','p-9','p-12','p-14'])]:
 d=json.loads((C/f'{source}-extracted.json').read_text());excerpts[source+'_clinical_main']=[r for r in d['paragraphs'] if r['id'] in ids]
excerpts['Pabst_TableS3_complete']=ps[ps.index('Table S3.'):ps.index('Table S4.')]
excerpts['Pabst_TableS8_clinical_regions']=ps[ps.index('Table S8.'):ps.index('Table S9.')]
excerpts['Lanzafame_MainTable1_html_sha256']=digest(C/'lanzafame-table1.html')
save('SOURCE-EXCERPTS.json',excerpts)
# Check printed roster labels against normalized original extracted text.
def norm(s):return re.sub(r'\s+',' ',s).strip().lower()
for label,n in kessler: assert norm(label) in norm(excerpts['Kessler_Table1']),label
for label,n in lanz_sts+lanz_bone: assert norm(label) in norm(re.sub(r'[0-9]+',' ',excerpts['Lanzafame_Table3'])),label
for label,n in pabst_sts+pabst_bone+pabst_remaining: assert norm(label) in norm(excerpts['Pabst_SarcomaRoster']),label
rosters=[]
def add(source,location,rows,ambiguous):
 for label,n in rows:
  unresolved=label in ambiguous
  rosters.append({'source':source,'location':location,'source_label':label,'reported_donors':n,'individual_donor_ids':'not released in subtype roster','authenticated_EMC':False,'status':'unavailable evidence' if unresolved else 'demonstrably unsuitable measurement','inspection':'Published label is insufficient for EMC identity; subtype/genomic crosswalk unavailable' if unresolved else 'Explicit distinct published histology does not authenticate EMC; not evidence of zero FAPI uptake','condition_evaluation':'No EMC quantitative inference; same-patient scans/regions remain dependent','scope_limit':'Categorical source identity audit, not reclassification of specimens or pathology validation'})
add('Kessler2022','SupplementalTable1',kessler,{'Undifferentiated soft tissue sarcoma (NOS, round cell, UPS)','Undifferentiated bone sarcoma'})
add('Lanzafame2024','MainTable1',lanz_main,{'BS: Chondrosarcoma','BS: Spindle cell sarcoma','STS: Spindle cell sarcoma'})
add('Lanzafame2024','SupplementalTable3 otherSTS41',lanz_sts,{'Fibrosarcoma','Fibromyxosarcoma','G-NET/sarcoma'})
add('Lanzafame2024','SupplementalTable3 otherbone15',lanz_bone,set())
add('Pabst2025','AppendixTableS3 pp5-6 STS18',pabst_sts,{'Endometrial sarcoma','Fibromyxoid sarcoma','Liposarcoma'})
add('Pabst2025','AppendixTableS3 pp5-6 bone5',pabst_bone,{'Chondrosarcoma'})
add('Pabst2025','AppendixTableS3 pp5-6 remaining5',pabst_remaining,{'Other','Unknown'})
save('HISTOLOGY-COVERAGE.json',rosters)
macro=[]
for label,n in pabst_macro:
 unresolved=label in {'Colorectal','Endometrial','Head and Neck','Prostate','Thyroid (follicular subtype)','Unknown primary origin','Other*','Sarcoma'}
 macro.append({'source':'Pabst2025','location':'TableS3 complete155 macrocohort','source_label':label,'donors':n,'status':'unavailable evidence' if unresolved else 'demonstrably unsuitable measurement','consequence':'Generic organ/cancer/category label is not EMC exclusion; primary subtype/identity unresolved or expanded elsewhere' if unresolved else 'Explicit alternate disease class does not authenticate EMC','counting':'Macro categories sum155; sarcoma28 expansion is nested and not additional donors; Other11 footnote nested'})
other=[]
for label,n in pabst_other:
 unresolved=label in {'Myxoid renal tumour','Penile cancer'}
 other.append({'source':'Pabst2025','location':'TableS3 Other11 footnote','source_label':label,'donors':n,'status':'unavailable evidence' if unresolved else 'demonstrably unsuitable measurement','consequence':'Generic myxoid/organ label cannot be excluded as EMC by site alone' if unresolved else 'Explicit alternate published diagnosis does not authenticate EMC','counting':'Nested within Other11 macro category'})
save('PABST-COHORT-COVERAGE.json',{'complete_macro155':macro,'expanded_other11':other,'unknown_primary_origin3':'Unresolved histology, not excluded by organ; TableS8 row23 adverse brain condition retained','myxoid_renal_tumour1':'Unresolved generic myxoid identity, not excluded by renal site; TableS8 row9 adverse primary condition retained'})
# Inspect ALL public Kessler reader/donor IDs and fields; only identity/gate metadata retained.
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};readers=[];by_id={}
for i in range(1,5):
 f=C/f'kessler-reading-{i}.xlsx';z=zipfile.ZipFile(f);strings=[]
 if 'xl/sharedStrings.xml' in z.namelist(): strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
 values=[];header=[]
 for fn in z.namelist():
  if re.match(r'xl/worksheets/sheet\d+\.xml$',fn):
   r=ET.fromstring(z.read(fn))
   for row in r.findall('.//s:sheetData/s:row',ns):
    rv=[]
    for cell in row:
     v=cell.find('s:v',ns);val=v.text if v is not None else ''.join(cell.itertext())
     if cell.get('t')=='s' and val:val=strings[int(val)]
     values.append(val);rv.append(val)
    if row.get('r') in ['1','2','3']:header.append(rv)
 ids=sorted(set(v for v in values if re.match(r'^FAPI_STS_\d+$',v)))
 has_identity=any(re.search(r'(?i)histology|diagnosis|chondrosarcoma|extraskeletal|NR4A3',v or '') for v in values)
 assert not has_identity
 reader=1 if i<3 else 2;tracer='FAPI' if i%2 else 'FDG'
 readers.append({'file':f.name,'source_sha256':digest(f),'reader':reader,'tracer':tracer,'donor_ids':ids,'donor_n':len(ids),'headers':header,'identity_or_date_crosswalk':False,'measurement_level':'regional lesion counts and SUVmax/SUVpeak/SUVmean; lesion-level pairing not provided'})
 for id in ids:by_id.setdefault(id,[]).append(f'reader{reader}_{tracer}')
assert [r['donor_n']for r in readers]==[47,43,47,43]
observations=[{'source':'Kessler2022','id':id,'conditions':conditions,'status':'unavailable evidence','authenticated_EMC':False,'missing':'histology/genomic identity crosswalk, patient scan dates, individual lesion pairing','technical_replication':'two readers of same scans; not independent donors','eligibility_consequence':'Descriptive reading fields inspected; no EMC ratio justified'} for id,conditions in sorted(by_id.items())]
observations += [{'source':'Pabst2025','id':'TableS8 row7','source_diagnosis':'Fibromyxoid sarcoma','condition':'Soft tissue metastasis','source_CT':'27mm','source_MRI':'23mm','source_FAPI_PET_SUVpeak':'No uptake','source_FDG':'not supplied','FAPI_context':'region listed by source as false negative','status':'unavailable evidence','authenticated_EMC':False,'eligibility_consequence':'Generic identity and no donor crosswalk/paired FAPI SUV/date; preserve unfavorable condition without attributing EMC'}, {'source':'Pabst2025','id':'TableS8 row8','source_diagnosis':'Fibromyxoid sarcoma','condition':'Primary tumour','source_FAPI_PET_SUVpeak':'No uptake','source_FDG':'not supplied; FDG local read was a biopsy/surgery trigger','FAPI_context':'region listed by source as false negative','status':'unavailable evidence','authenticated_EMC':False,'eligibility_consequence':'TableS8footnote explicitly confirms rows7/8 are the sameparticipant; one donor, two regions. No EMC authentication or paired SUV/date.'}]
observations += [{'source':'Pabst2025','id':'TableS8 row9','source_diagnosis':'Myxoid renal tumour','condition':'Primary tumour','source_CT':'65mm','source_FAPI_PET_SUVpeak':'No uptake','source_FDG':'not supplied','trigger':'CT local read','status':'unavailable evidence','authenticated_EMC':False,'eligibility_consequence':'Myxoid renal diagnosis is generic; no exclusion by site and no EMC authentication. Retain adverse FAPI clinical condition without substitution of uptake=0.'},{'source':'Pabst2025','id':'TableS8 row23','source_diagnosis':'Cancer of Unknown Origin','condition':'Brain','source_FAPI_PET_SUVpeak':'No uptake','source_FDG':'not supplied','trigger':'CT external read','status':'unavailable evidence','authenticated_EMC':False,'eligibility_consequence':'Unknownprimary macro3 lacks subtype/donor crosswalk. Adverse brain condition not presumed EMC and not omitted.'}]
for o in observations:
 if o.get('id')in ['TableS8 row7','TableS8 row8']:o['donor_overlap']='Known sameparticipant by explicitTableS8footnote; two regions, one donor'
save('KESSLER-READING-IDENTITY-AUDIT.json',readers);save('OBSERVATION-COVERAGE.json',observations)
summary={'analysis_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'question':'Four named clinical FAPI sources','decision':'Shelve the standalone EMC paired FAPI/FDG paper','surviving_demonstrated_new_EMC_findings':[],'authenticated_EMC_donors':0,'computed_EMC_ratios':0,'computed_p_values':0,'recovered_named_supplements':['Kessler2022 SupplementalData and4original clinical reader workbooks','Lanzafame2024 SupplementalData','Pabst2025 original appendix'],'sources':[{'name':'Kessler2022','status':'evaluated','roster_donors':47,'unresolved':'UndifferentiatedSTS6 andbone2 cannot be molecularly/subtype reclassified;47 clinical donorIDs now inspected but no identity/date/individual-lesion crosswalk. Table6 is aggregate regions, not individual observations.','gate':'main range−30 to+7days and no therapy change; unknown patient-specific interval cannot pass<=28days','overlap':'Same NCT04571086/Essen cohort as later Lanzafame; exact overlap not released. R6 broader owner evaluates Hirmas explicit reused47.'},{'name':'Lanzafame2024','status':'evaluated','roster_donors':200,'unresolved':'OtherSTS41/bone15 expanded. GenericCHS17, spindle-cell bone5/STS7, fibrosarcoma4/fibromyxosarcoma2 andG-NET1 remain unresolved. Source diagnostic subtype categories are not donor identities.','gate':'all186 FAPI46 pairedFDG within4wk by main; individual therapy and same-lesion crosswalk unavailable','overlap':'Same ongoing Essen NCT04571086; Methods October2019–2022 vs Results October2020–2022 is source inconsistency, no claim of independent cohorts.'},{'name':'Pabst2025','status':'evaluated','cohort_total_donors':155,'sarcoma_roster_donors':28,'unresolved':'18STS/5bone/1GIST/3Other/1Unknown. Fibromyxoid1/CHS2/other generic labels unresolved. Same-participant fibromyxoid false-negative primary/softtissue-metastasis conditions and generic myxoidrenal/unknownorigin adverse conditions inspected; cannot be treated as EMC. Complete macro155 andOther11 roster accounted; organ/cancer labels, Unknownprimary3/Myxoidrenal1 remain explicit unresolved identities.','gate':'No authenticated EMC individual scan chronology/SUV lesion crosswalk; individual data request-only by R5 reused main.','overlap':'R5 main permits NCT04571086 co-enrolment; public appendix supplies no exact donor crosswalk.'},{'name':'Kratochwil2019','status':'evaluated','roster_donors':80,'unresolved':'Public full article recovered; generic sarcoma group has no supplied detailed histology/donor roster. Detailed EMC identity evidence unavailable in inspected release, not negative uptake.','gate':'FAPI04 main provides no EMC same-lesionFDG paired comparison','overlap':'R5 verified Koerber statement:4previously reported donors, exact crosswalk unavailable.'}],'novelty_value':'Broad sarcoma uptake/aggregate accuracy were already primary published findings. Recovering missing supplements improves evidence reuse, not a new disease discovery. No established EMC imaging claim is challenged by an absence of authenticated entries.','coverage_gap_consequence':'No universal EMC exclusion or exhaustive public-evidence claim. Generic labels/withheld crosswalks and other relevant sources prevent clinical phenotype/population inference and promotion.','reopening_condition':'A permitted public identity-to-scan crosswalk authenticating EMC with suitable independent donor/lesion measurements, <=28-day/no-intervening-therapy chronology and verification. Then evaluate every eligible EMC condition, overlap/contrary findings and prior art before justified analysis.','restrictions':'No tissue FAP analysis, blocked lane takeover, paid work/outreach/publication/browser UI/GPU or shared state/push. TMEM266 shelved.','portable_inputs':'All recovered papers/full extracts/workbooks remain ignored raw-cache. SOURCE-EXCERPTS and derived audits are committed with access hashes. Raw sources recoverable through recorded public URLs if permitted; prior Windows caches remain absent.'}
save('RESULTS.json',summary)
print('eligibility audit complete; rosters47/200/28; readingIDs47/43/47/43; authenticEMC0; ratios0')
