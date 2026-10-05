from pathlib import Path
import urllib.request,urllib.parse,hashlib,json,datetime,xml.etree.ElementTree as E
P=Path(__file__).resolve().parent
queries={'direct_assays':'("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" OR "chordoid sarcoma") AND (telomerase OR telomere OR "C-circle" OR "alternative lengthening" OR "ALT-associated")','models':'("extraskeletal myxoid chondrosarcoma" OR EMCS) AND (NCC OR USZ OR organoid OR "cell line" OR explant) AND (telomerase OR telomere OR "TRAP assay" OR "C-circle")'}
routes={'alt-review2018.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5977181/fullTextXML'}
for n,q in queries.items():routes[n+'-metadata.json']='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','pageSize':100,'resultType':'core'})
rec=[]
for name,url in routes.items():
 x={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'file':'raw-cache/'+name,'query':queries.get(name.replace('-metadata.json',''))}
 try:
  with urllib.request.urlopen(url,timeout=20) as f:b=f.read(3*1024*1024+1);x.update(status=f.status,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  if len(b)>3*1024*1024:x['validity']='capped incomplete source, no interpretation'
  else:
   (P/'raw-cache'/name).write_bytes(b)
   if name.endswith('.json'):
    j=json.loads(b);x.update(hitCount=j.get('hitCount'),returned=len(j.get('resultList',{}).get('result',[])));compact=[{k:r.get(k) for k in ['id','pmcid','doi','title','pubYear','pubTypeList']} for r in j.get('resultList',{}).get('result',[])];(P/'raw-cache'/(name.replace('-metadata.json','').upper()+'-METADATA.json')).write_text(json.dumps(compact,indent=2)+'\n');print(name,x['hitCount'],x['returned']);print(json.dumps(compact,indent=2)[:6000])
   else:
    r=E.fromstring(b);out=[]
    for t in r.findall('.//ref'):
     label=t.findtext('label','').strip('. ')
     if label in ['49','53','194']:out.append({'reference':label,'text':' '.join(''.join(t.itertext()).split()),'xml':E.tostring(t,encoding='unicode')})
    (P/'REVIEW-PRIMARY-CITATION-GATE.json').write_text(json.dumps({'review_sha256':x['sha256'],'references':out},indent=2)+'\n');print('PRIMARYREFS',json.dumps(out,indent=2))
    for t in r.findall('.//table-wrap'):
     for tr in t.findall('.//tr'):
      row=[' '.join(''.join(c.itertext()).split()) for c in tr if c.tag in ['td','th']]
      if any('myxoid chondrosarcoma' in c.lower() for c in row):print('COMPILERROW',row)
 except Exception as e:x['error']=str(e)
 rec.append(x)
(P/'SOURCE-SCOUT-RECEIPTS.json').write_text(json.dumps(rec,indent=2)+'\n')
