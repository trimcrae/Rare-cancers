from pathlib import Path
import urllib.request,hashlib,json,datetime,xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).resolve().parent
sources={
'bostongene-sitc2024.pdf':'https://bostongene.com/assets/SITC_2024_Comprehensive_molecular_profiling_management_patients_with_diverse_sarcoma_RGB.pdf',
'galitskiy2025-elsevier.xml':'https://api.elsevier.com/content/article/PII:S092375342501230X?httpAccept=text/xml',
'vienna2017-elsevier.xml':'https://api.elsevier.com/content/article/PII:S0923753420387561?httpAccept=text/xml',
'rosenbaum2026.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13014529/fullTextXML',
'rosenbaum2026.html':'https://pmc.ncbi.nlm.nih.gov/articles/PMC13014529/',
}
def fetch(item):
 name,url=item;out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'filename':name}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30)as response:
   data=response.read(12*1024*1024+1);assert len(data)<=12*1024*1024;out.update(status=response.status,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),final_url=response.url);(P/name).write_bytes(data)
 except Exception as e:out.update(error=str(e))
 return out
with ThreadPoolExecutor(max_workers=5)as ex:out=list(ex.map(fetch,sources.items()))
(P/'fetch-immune-followup-receipts.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps([{k:v for k,v in row.items()if k in ['filename','status','bytes','error']}for row in out]))
