"""Bounded public-source retrieval only; no forms, credentials or outreach."""
from pathlib import Path
import urllib.request,urllib.error,hashlib,json,datetime
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).resolve().parent
sources={
'galitskiy2025.html':'https://www.annalsofoncology.org/article/S0923-7534(25)01230-X/fulltext',
'galitskiy2025-crossref.json':'https://api.crossref.org/works/10.1016%2Fj.annonc.2025.08.310',
'bostongene-publications.html':'https://www.bostongene.com/news-and-publications/publications',
'bostongene-patient-resource.html':'https://www.bostongene.com/sign-up-for-your-free-copy?file=report%2FBostonGene-patient-case-extraskeletal-myxoid-chondrosarcoma_%5B09.22.2026%5D.pdf',
'immunosarc2020.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7674086/fullTextXML',
'vienna2016-crossref.json':'https://api.crossref.org/works?query.title=Pembrolizumab%20Named%20patient%20use%20Medical%20University%20Vienna&rows=3',
'matrix-willems2008.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:18315599&resultType=core&format=json',
'immunosarc2025.html':'https://ascopubs.org/doi/10.1200/JCO.2025.43.16_suppl.11513',
'immune-nct03277924.json':'https://clinicaltrials.gov/api/v2/studies/NCT03277924',
}
def fetch(item):
 name,url=item;out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'filename':name}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-public-research/1.0'}),timeout=35)as response:
   data=response.read(10*1024*1024+1);assert len(data)<=10*1024*1024
   out.update(status=response.status,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),final_url=response.url);(P/name).write_bytes(data)
 except Exception as e:out.update(error=str(e))
 return out
with ThreadPoolExecutor(max_workers=5)as ex:out=list(ex.map(fetch,sources.items()))
(P/'fetch-immune-receipts.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps([{k:v for k,v in row.items()if k in ['filename','status','bytes','error']}for row in out]))
