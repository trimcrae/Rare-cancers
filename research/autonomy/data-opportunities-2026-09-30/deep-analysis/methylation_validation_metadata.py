#!/usr/bin/env python3
import hashlib,io,json,pathlib,urllib.parse,urllib.request,xml.etree.ElementTree as ET
import openpyxl
OUT=pathlib.Path(__file__).resolve().parent/'outputs'/'methylation-validation';OUT.mkdir(parents=True,exist_ok=True)
def get(url,bound=4_000_000):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Rare-cancers-primary-validation-metadata/1'}),timeout=120) as r:b=r.read(bound+1)
 if len(b)>bound:raise ValueError('source exceeds declared metadata bound')
 return b
url='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7819999/fullTextXML';xml=get(url);tree=ET.fromstring(xml)
base='https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-020-20603-4/MediaObjects/'
workbooks=[]
for node in tree.findall('.//supplementary-material'):
 caption=' '.join(' '.join(node.itertext()).split())
 for element in node.iter():
  for key,href in element.attrib.items():
   if key.endswith('href') and href.lower().endswith('.xlsx'):
    workbooks.append({'caption':caption,'href':href,'url':href if href.startswith('http') else base+urllib.parse.quote(href)})
seen=set();results=[]
for item in workbooks:
 if item['url'] in seen:continue
 seen.add(item['url']);record=dict(item)
 try:
  data=get(item['url']);record.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
  wb=openpyxl.load_workbook(io.BytesIO(data),read_only=True,data_only=True);sheets=[]
  for sheet in wb.worksheets:
   rows=[[v if isinstance(v,(str,int,float,bool)) or v is None else str(v) for v in row] for row in sheet.iter_rows(values_only=True)]
   rows=[r for r in rows if any(v is not None for v in r)]
   sheets.append({'name':sheet.title,'rows':rows,'n_rows':len(rows),'max_columns':max([len(r) for r in rows],default=0)})
  record.update(status='retrieved',sheets=sheets)
 except Exception as error:record.update(status='failed',error=str(error))
 results.append(record)
payload={'primary_xml_url':url,'primary_xml_sha256':hashlib.sha256(xml).hexdigest(),'workbooks':results}
(OUT/'primary-workbooks.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
summary=[]
for record in results:
 out={k:v for k,v in record.items() if k!='sheets'}
 if 'sheets' in record:out['sheets']=[{**{k:v for k,v in s.items() if k!='rows'},'rows':s['rows'] if 400<=s['n_rows']<=600 else s['rows'][:8]} for s in record['sheets']]
 summary.append(out)
print('EMC_METHYLATION_VALIDATION_METADATA_BEGIN');print(json.dumps({'primary_xml_url':url,'primary_xml_sha256':payload['primary_xml_sha256'],'workbooks':summary},separators=(',',':'),ensure_ascii=False));print('EMC_METHYLATION_VALIDATION_METADATA_END')
