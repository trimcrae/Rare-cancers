#!/usr/bin/env python3
import concurrent.futures,datetime,hashlib,json,pathlib,urllib.request
P=pathlib.Path(__file__).resolve().parent;C=P/'.cache'
SOURCES={'heterogeneity2022':'PMC9330136','pgr2022':'PMC9489176','kit2018':'PMC6073125','imatinib2021':'PMC8395296','pleural2022':'PMC9527174','regression2025':'PMC12660641','cabozantinib2021':'PMC8776602','trough2022':'PMC9231369'}
def fetch(pair):
 name,acc=pair; urls=[('epmc_xml','https://www.ebi.ac.uk/europepmc/webservices/rest/'+acc+'/fullTextXML'),('bioc_xml','https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/'+acc+'/unicode')];receipts=[]
 for kind,url in urls:
  t=datetime.datetime.now(datetime.timezone.utc).isoformat()
  try:
   with urllib.request.urlopen(url,timeout=35) as r:b=r.read();status=r.status
   f=C/(name+'-'+kind+'.xml');f.write_bytes(b);ok=b'<?xml' in b[:100] or b'<article' in b[:100] or b'<collection' in b[:100]
   receipts.append({'id':name,'pmcid':acc,'utc':t,'url':url,'status':status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'cache_path':str(f.relative_to(P)),'xml_signature':ok})
   if ok and not b'[Error]' in b:break
  except Exception as e:receipts.append({'id':name,'pmcid':acc,'utc':t,'url':url,'error':str(e)})
 return receipts
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:rec=[item for batch in pool.map(fetch,SOURCES.items()) for item in batch]
(P/'SOURCE-RECEIPTS.json').write_text(json.dumps(rec,indent=2)+'\n')
for x in rec:print(x['id'],x.get('status'),x.get('bytes'),x.get('error'))
