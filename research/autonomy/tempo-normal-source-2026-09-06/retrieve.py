"""Bounded primary public source retrieval; preserves original response bytes."""
import datetime, hashlib, json, pathlib, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent
SOURCES = {
 'GSE119630_family.soft.gz': 'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE119nnn/GSE119630/soft/GSE119630_family.soft.gz',
 'GSE119630_ColonCancerReplicatesMaster.csv.gz': 'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE119nnn/GSE119630/suppl/GSE119630_ColonCancerReplicatesMaster.csv.gz',
 'GSE119630_HumanGeneCountsMaster.csv.gz': 'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE119nnn/GSE119630/suppl/GSE119630_HumanGeneCountsMaster.csv.gz',
 'article.xml': 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6386473/fullTextXML',
}
receipts=[]
for name, url in SOURCES.items():
 r={'file':name,'url':url,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(url, timeout=50) as response:
   data=response.read(); (ROOT/name).write_bytes(data)
   r.update(status=response.status, final_url=response.url, headers=dict(response.headers), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
 except Exception as exc: r['error']=str(exc)
 r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat(); receipts.append(r)
 (ROOT/'retrieval.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(r))
