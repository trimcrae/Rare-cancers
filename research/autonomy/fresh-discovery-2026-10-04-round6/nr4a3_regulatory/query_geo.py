"""Primary GEO metadata-only discovery; not an expression or binding analysis."""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlencode
from xml.etree import ElementTree as ET
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parent
queries={
 'geo-fusion':'(NR4A3 OR "EWS-TEC" OR "EWS/NOR1") AND (EWSR1 OR TAF15 OR chondrosarcoma)',
 'geo-emc-regulatory':'"extraskeletal myxoid" AND (ChIP OR ATAC OR knockdown OR silencing OR perturbation)'
}
receipts=[];summaries=[]
for name,q in queries.items():
 url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urlencode({'db':'gds','term':q,'retmax':1000})
 rec={'query':q,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urlopen(Request(url,headers={'User-Agent':'EMCResearchEvidenceCheck/1.0'}),timeout=30) as r:b=r.read(512*1024);rec['status']=r.status
  (ROOT/(name+'.xml')).write_bytes(b);rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  x=ET.fromstring(b);ids=[n.text for n in x.findall('.//IdList/Id')];rec['count']=int(x.findtext('Count'));rec['returned_ids']=ids
  assert len(ids)==rec['count']
  if ids:
   su='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?'+urlencode({'db':'gds','id':','.join(ids)})
   with urlopen(Request(su,headers={'User-Agent':'EMCResearchEvidenceCheck/1.0'}),timeout=30) as r:sb=r.read(2*1024**2);rec['summary_status']=r.status
   (ROOT/(name+'-summary.xml')).write_bytes(sb);rec.update(summary_url=su,summary_bytes=len(sb),summary_sha256=hashlib.sha256(sb).hexdigest())
   for d in ET.fromstring(sb).findall('.//DocSum'):
    row={'uid':d.findtext('Id')}
    for v in d.findall('Item'):
     if v.get('Name') in ['title','summary','Accession','taxon','gdsType','n_samples','GSE']:row[v.get('Name')]=' '.join(v.itertext())
    summaries.append(row)
 except Exception as e:rec['error']=str(e)
 receipts.append(rec)
(ROOT/'geo-retrieval.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
(ROOT/'geo-candidates.json').write_text(json.dumps(summaries,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipts,indent=2));print(json.dumps(summaries,indent=2))
