#!/usr/bin/env python3
"""Finite ordinary official metadata retrieval. No values, raw sequences or retry."""
import concurrent.futures,datetime,hashlib,json,urllib.request,urllib.parse,shutil
from pathlib import Path
p=Path(__file__).resolve().parent
cache=p/'source-cache';cache.mkdir(exist_ok=True)
assert shutil.disk_usage(p).free>=10737418240
queries=[
 ('CRO-official-home','https://www.cro.it/'),
 ('Crossref-exact-primary-DOI','https://api.crossref.org/works/10.1002/path.5284'),
 ('DataCite-related-primary-DOI','https://api.datacite.org/dois?'+urllib.parse.urlencode({'query':'relatedIdentifiers.relatedIdentifier:"10.1002/path.5284"','page[size]':'100'})),
 ('DataCite-related-published-repository-URL','https://api.datacite.org/dois?'+urllib.parse.urlencode({'query':'relatedIdentifiers.relatedIdentifier:"http://opendocuments.cro.it/cod/handle/item/9167"','page[size]':'100'})),
 ('OpenAIRE-exact-primary-DOI','https://api.openaire.eu/search/publications?'+urllib.parse.urlencode({'doi':'10.1002/path.5284','format':'json','size':'100'}))]
def fetch(item):
 name,url=item;q=cache/name;assert not q.exists(),q
 r={'name':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Official institution/repository-link metadata; no cell/gene/IR values or raw sequence payloads','cap_bytes':2097152}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'EMC-public-source-metadata/1.0'})
  with urllib.request.urlopen(req,timeout=20) as response:
   body=response.read(2097153);r['http']=response.status;r['final_url']=response.url;r['content_type']=response.headers.get('Content-Type')
  if len(body)>2097152:r['status']='response cap exceeded; body not retained; no follow-up stage'
  else:q.write_bytes(body);r.update({'status':'metadata retrieved; not dataset availability','bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'path':'source-cache/'+name})
 except Exception as e:r['status']='access/query failure; no retry';r['error']=str(e)
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:receipts=list(pool.map(fetch,queries))
assert sum(x.stat().st_size for x in cache.iterdir() if x.is_file())<=67108864
out=p/'OFFICIAL-METADATA-RECEIPTS.json';assert not out.exists();out.write_text(json.dumps(receipts,indent=2)+'\n')
for r in receipts:print(json.dumps({k:v for k,v in r.items() if k not in ['scope','url']},ensure_ascii=False))
