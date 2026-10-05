from pathlib import Path
import urllib.request,urllib.parse,json,datetime,hashlib,xml.etree.ElementTree as E
P=Path(__file__).resolve().parent
routes={'umakoshi2023-primary.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9870999/fullTextXML','dancsok-valid-query.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':'Dancsok AND sarcoma AND (immune OR lymphocyte OR macrophage)','format':'json','pageSize':100,'resultType':'core'})}
rec=[]
for name,url in routes.items():
 x={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'file':'raw-cache/'+name}
 try:
  with urllib.request.urlopen(url,timeout=20) as f:b=f.read();x.update(status=f.status,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  (P/'raw-cache'/name).write_bytes(b)
  if name.endswith('json'):
   j=json.loads(b);x.update(hitCount=j.get('hitCount'),returned=len(j.get('resultList',{}).get('result',[])));c=[{k:r.get(k) for k in ['id','pmcid','doi','title','pubYear']} for r in j.get('resultList',{}).get('result',[])];(P/'DANCSOK-VALID-METADATA.json').write_text(json.dumps(c,indent=2)+'\n');print(json.dumps(c,indent=2))
  else:
   r=E.fromstring(b)
   for s in r.findall('.//sec'):
    t=s.find('title')
    if t is not None:print('SECTION',s.attrib,' '.join(''.join(t.itertext()).split()))
   for s in r.findall('.//supplementary-material'):print('SUPPLEMENT',E.tostring(s,encoding='unicode'))
   for s in r.findall('.//ext-link'):
    tx=' '.join(''.join(s.itertext()).split())
    if any(x in tx.lower() for x in ['data','figshare']):print('DATA_LINK',E.tostring(s,encoding='unicode'))
 except Exception as e:x['error']=str(e)
 rec.append(x)
(P/'PRIMARY-RETRIEVAL.json').write_text(json.dumps(rec,indent=2)+'\n')
