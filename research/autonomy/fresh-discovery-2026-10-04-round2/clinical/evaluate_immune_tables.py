"""Authenticate all released Rosenbaum2026 table rows and all EMC entries."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as E,json,hashlib,datetime
P=Path(__file__).resolve().parent;ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};out={};hashes={}
for f in P.glob('rosenbaum-*suppts*.docx'):
 with zipfile.ZipFile(f)as z:r=E.fromstring(z.read('word/document.xml'))
 rows=[[' '.join(''.join(c.itertext()).split())for c in row.findall('w:tc',ns)]for row in r.findall('.//w:tr',ns)];out[f.name]=rows;hashes[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
hits={k:[r for r in rows if any('extraskeletal myxoid chondrosarcoma'in c.lower()for c in r)]for k,rows in out.items()}
s1=next(k for k in hits if '_s1_'in k);s3=next(k for k in hits if '_s3_'in k)
assert hits[s1]==[['Extraskeletal myxoid chondrosarcoma','Other fusion+ STS','1']]
assert hits[s3]==[['Depleted','No','Extraskeletal myxoid chondrosarcoma','1']]
(P/'rosenbaum-tables-extracted.json').write_text(json.dumps(out,indent=2)+'\n')
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_hashes':hashes,'all_EMC_rows':hits,'interpretation':'One reported EMC in bloodhistologytable and one immune-depleted/noresponse EMC in RNAtable; no individualidentifier makes matching independently verifiable. Published case-level finding, not newresponsepredictor. Other myxoid, bonechondrosarcoma andextraskeletalosteosarcoma rows excluded by explicitdiagnosis.','gaps':['No patient-to-regimen/NR4A3/flowimmunotype/H&E crosswalk inS1–S3','dbGaPMSK192RNA controlled; not retrieved','Additionalfigures, originaltrials andStanfordGSE213065 suitableevidence remain pending if advancing claim','Galitskiy2025 response/biomarkerdata unrecovered; vendorcaseform not submitted','No exhaustiveclinicalICBcorpusclaim'],'failed_download_warning':'NIHMS2150030-supplement-1..8 initialfiles are1816/1817-byte browserchallengeHTML, notPDF/DOCX. ActualS1–S3 publisherfiles recovered separately viaFigshare; initial HTTP200doesnotconstitute successfulsourceevaluation.'}
(P/'immune-table-evaluation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'tables':len(out),'row_counts':{k:len(v)for k,v in out.items()},'EMC_rows':hits}))
