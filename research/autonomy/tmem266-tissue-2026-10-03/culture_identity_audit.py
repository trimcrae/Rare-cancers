"""Small public source receipts and factual table rows supporting culture identity."""
import urllib.request,xml.etree.ElementTree as ET,zipfile,io,hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
urls={
 'geo':'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM2113301&targ=self&form=text&view=full',
 'supplement':'https://pmc-oa-opendata.s3.amazonaws.com/PMC5072325.1/12864_2016_3161_MOESM3_ESM.docx',
 'article':'https://pmc-oa-opendata.s3.amazonaws.com/PMC5072325.1/PMC5072325.1.xml',
 'ena':'https://www.ebi.ac.uk/ena/portal/api/filereport?accession=SRX1703825&result=read_run&fields=run_accession,experiment_accession,sample_accession,secondary_sample_accession,sample_alias,study_accession&format=tsv'
}
raw={};receipts={}
for k,u in urls.items():
 b=urllib.request.urlopen(u,timeout=45).read();raw[k]=b;receipts[k]={'url':u,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
geo=raw['geo'].decode(errors='replace')
keep=[l for l in geo.splitlines() if any(s in l for s in ['Sample_title','Sample_source_name','Sample_characteristics','Sample_relation'])]
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(io.BytesIO(raw['supplement'])) as z:r=ET.fromstring(z.read('word/document.xml'))
tables=[]
for index,t in enumerate(r.findall('.//w:tbl',ns),1):
 rows=[[' '.join(''.join(c.itertext()).split()) for c in tr.findall('w:tc',ns)] for tr in t.findall('w:tr',ns)]
 hits=[(i,row) for i,row in enumerate(rows) if any(s.lower() in ' '.join(row).lower() for s in ['V1-34','EMC','myxoid','NR4A3'])]
 if hits:tables.append({'table_index':index,'headers':rows[:2],'matching_rows':hits})
result={'source_doi':'10.1186/s12864-016-3161-9','receipts':receipts,'selected_GEO_metadata_lines':keep,'source_tables':tables,'ENA_run_crosswalk':raw['ena'].decode(),'interpretation':'Publication and GEO jointly identify one EMC-derived cell culture with EWSR1::NR4A3 and two sequencing runs. Neither source establishes modern STR identity, malignant-cell fraction or same-cell coexpression of fusion and TMEM266.'}
(BASE/'culture-identity-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'GEO':keep,'tables':tables,'ENA':raw['ena'].decode()},indent=2))
