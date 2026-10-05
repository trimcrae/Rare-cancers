import concurrent.futures,datetime,hashlib,json,pathlib,shutil,threading,urllib.request,xml.etree.ElementTree as ET
B=pathlib.Path(__file__).resolve().parent;R=B/'raw';L=threading.Lock();CAP=64*1024*1024
IDS=['PMC10094087','PMC5667900','PMC5933935','PMC11713734','PMC10777695']
def fetch(x):
 url='https://www.ebi.ac.uk/europepmc/webservices/rest/'+x+'/fullTextXML';o={'id':x,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-public-source-pilot/1.0'}),timeout=45) as resp:data=resp.read(12*1024*1024+1);o['status']=resp.status
  if len(data)>12*1024*1024:raise RuntimeError('single response stage limit; retain pending')
  with L:
   used=sum(p.stat().st_size for p in B.rglob('*') if p.is_file());assert used+len(data)<CAP and shutil.disk_usage(B).free-len(data)>10*1024**3
   p=R/(x+'.xml');p.write_bytes(data)
  root=ET.fromstring(data);o.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),cache_path='raw/'+p.name)
  excerpts=[]
  for n in root.iter():
   if n.tag in ['p','table','table-wrap','fig']:
    s=' '.join(' '.join(n.itertext()).split())
    if any(a in s.lower() for a in ['hemcss','h-emc','extraskeletal','gp x4','gpx4','rsl3','erastin','ferrostatin']):excerpts.append({'tag':n.tag,'id':n.attrib.get('id'),'text':s})
  (R/(x+'-scoped-paragraphs.json')).write_text(json.dumps(excerpts,indent=2)+'\n')
  o['selected_paragraphs']=len(excerpts);o['supplement_links']=[n.attrib for n in root.iter() if n.tag in ['supplementary-material','ext-link','media'] and ('supp' in str(n.attrib).lower() or 'esm' in str(n.attrib).lower() or n.tag=='supplementary-material')]
  return o
 except Exception as e:o.update(error=type(e).__name__+': '+str(e),disposition='access/parsing unresolved, not absence');return o
if __name__=='__main__':
 out=list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(fetch,IDS));(B/'PRIMARY-RECEIPTS.json').write_text(json.dumps(out,indent=2)+'\n')
 for x in out:print(x['id'],x.get('bytes'),x.get('selected_paragraphs'),x.get('error',''))
