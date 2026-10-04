from pathlib import Path
from datetime import datetime, timezone
import urllib.request, json, hashlib, xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
BASE=Path(__file__).resolve().parent
SOURCES={
 'drilon2008':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC2779719/fullTextXML',
 'chiusole2020':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7308468/fullTextXML',
 'agaram2014':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1016/j.humpath.2014.01.007&format=json',
 'suemitsu2025':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1002/gcc.70076&format=json',
 'masunaga2025':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12398172/fullTextXML',
 'choi2014':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=TITLE:extraskeletal%20AND%20AUTH_FIRST:Yun&format=json',
}
def fetch(item):
 key,url=item;rec={'key':key,'url':url,'utc':datetime.now(timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(url,timeout=45) as response:
   data=response.read(4_000_000);rec.update(status=response.status,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
  ext='.json' if data[:1]==b'{' else '.xml';(BASE/(key+ext)).write_bytes(data)
  if ext=='.xml':
   root=ET.fromstring(data)
   out={'tables':[{'id':x.get('id'),'text':' | '.join(' '.join(y.itertext()) for y in x.findall('.//tr'))} for x in root.findall('.//table-wrap')], 'sections':[{'title':x.findtext('title'),'text':' '.join(x.itertext())} for x in root.findall('.//body/sec')], 'supplements':[' '.join(x.itertext()) for x in root.findall('.//supplementary-material')]}
   (BASE/(key+'-extracted.json')).write_text(json.dumps(out,indent=2),encoding='utf8')
 except Exception as e:rec['error']=str(e)
 return rec
if __name__=='__main__':
 receipts=list(ThreadPoolExecutor(max_workers=3).map(fetch,SOURCES.items()))
 (BASE/'fetch-receipts.json').write_text(json.dumps(receipts,indent=2))
 print(json.dumps(receipts,indent=2))
