import concurrent.futures,datetime,hashlib,json,pathlib,urllib.request,xml.etree.ElementTree as ET
B=pathlib.Path(__file__).resolve().parent
IDS=['PMC5667900','PMC5933935','PMC10777695']
def get(x):
 url='https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/'+x+'/unicode';r={'id':x,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reason':'EuropePMC fullTextXML first response HTTP500; alternate ordinary public text API, no identical request repeat'}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-public-source-pilot/1.0'}),timeout=40) as z:blob=z.read(8*1024*1024+1);r['status']=z.status
  assert len(blob)<=8*1024*1024;p=B/'raw'/(x+'-bioc.xml');p.write_bytes(blob);r.update(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),cache_path='raw/'+p.name);root=ET.fromstring(blob);r['passages']=len(root.findall('.//passage'))
  return r
 except Exception as e:r.update(error=type(e).__name__+': '+str(e),disposition='unavailable/source-gap at attempted route, not no-EMC evidence');return r
out=list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(get,IDS));(B/'ALTERNATE-PRIMARY-RECEIPTS.json').write_text(json.dumps(out,indent=2)+'\n')
for r in out:print(r['id'],r.get('bytes'),r.get('passages'),r.get('error',''))
