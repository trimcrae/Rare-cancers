import urllib.request,urllib.parse,json,hashlib,pathlib,datetime,concurrent.futures,xml.etree.ElementTree as E
P=pathlib.Path(__file__).parent
C=P.parents[3]/'.cache'/'emc-r6-challenge'
C.mkdir(parents=True,exist_ok=True)
sources={'regression2025':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12660641/fullTextXML','massive2018':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6280406/fullTextXML','longterm2020':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7492874/fullTextXML','bsc2016':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4946242/fullTextXML','ultrarare2022':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9780071/fullTextXML','antiHu2018':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5759826/fullTextXML'}
def one(x):
 k,u=x
 try:
  r=urllib.request.urlopen(u,timeout=35);b=r.read(); (C/(k+'.xml')).write_bytes(b)
  root=E.fromstring(b); text='\n'.join(''.join(p.itertext()) for p in root.findall('.//body//p'));(C/(k+'-body.txt')).write_text(text)
  return {'source':k,'url':u,'status':r.status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'date':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 except Exception as e:return {'source':k,'url':u,'error':str(e),'date':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:j=list(e.map(one,sources.items()))
(P/'selected-source-receipts.json').write_text(json.dumps(j,indent=2)+'\n')
for r in j: print(r)
