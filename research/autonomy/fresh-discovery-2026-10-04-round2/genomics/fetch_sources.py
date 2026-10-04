import json,urllib.request,hashlib,datetime,xml.etree.ElementTree as E
from pathlib import Path
D=Path(__file__).resolve().parent
def fetch(url,name,body=None):
 p=None if body is None else json.dumps(body).encode()
 req=urllib.request.Request(url,data=p,headers={'User-Agent':'EMC-public-evidence-research','Accept':'application/json,application/xml,text/html','Content-Type':'application/json'})
 r={'url':url,'name':name,'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'GET' if body is None else 'POST','body':body}
 try:
  with urllib.request.urlopen(req,timeout=90) as f: raw=f.read(20000000);r['status']=f.status
  r.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest());(D/name).write_bytes(raw)
 except Exception as ex:r['error']=str(ex)
 with (D/'source-receipts.jsonl').open('a') as f:f.write(json.dumps(r)+'\n')
 return r
if __name__=='__main__':
 for url,name in [
 ('https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11874058/fullTextXML','genie-urs.xml'),
 ('https://www.cbioportal.org/api/studies?projection=DETAILED&pageSize=100000','cbio-study-catalog.json'),
 ('https://genie.cbioportal.org/api/studies?projection=DETAILED&pageSize=100000','genie-study-catalog.json')]:print(json.dumps(fetch(url,name)))
