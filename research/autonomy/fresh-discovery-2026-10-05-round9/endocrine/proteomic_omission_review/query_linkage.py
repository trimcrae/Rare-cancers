"""Distinct ordinary metadata omission queries, not raw outcome retrieval."""
import pathlib,json,hashlib,datetime,urllib.request,urllib.parse,concurrent.futures
B=pathlib.Path(__file__).parent;C=B/'.cache';C.mkdir(exist_ok=True)
DOI='10.64898/2026.07.08.737171'
def run(job):
 name,url=job;r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'name':name,'url':url,'query_scope':'Metadata only; not complete repository absence evidence'}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-independent-source-linkage/1.0'}),timeout=35) as q:
   raw=q.read(8*1024*1024+1);r.update(http=q.status,content_type=q.headers.get('content-type'),final_url=q.url)
  if len(raw)>8*1024*1024:raise ValueError('metadata cap exceeded')
  p=C/name;p.write_bytes(raw);r.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),cache_only=str(p))
  try:
   d=json.loads(raw)
   if name.startswith('datacite'):r.update(total=d.get('meta',{}).get('total'),returned=len(d.get('data',[])))
   elif name.startswith('zenodo'):r.update(total=d.get('hits',{}).get('total'),returned=len(d.get('hits',{}).get('hits',[])))
   elif name.startswith('crossref'):r.update(primary_url=d.get('message',{}).get('resource',{}).get('primary',{}).get('URL'),links=d.get('message',{}).get('link',[]),related=d.get('message',{}).get('relation',{}))
  except Exception as e:r['JSON_parse_limit']=str(e)
 except Exception as e:r['access_error']=str(e)
 return r
if __name__=='__main__':
 jobs=[
 ('datacite_exact_related.json','https://api.datacite.org/dois?'+urllib.parse.urlencode({'query':'relatedIdentifiers.relatedIdentifier:"'+DOI+'"','page[size]':100})),
 ('datacite_exact_title.json','https://api.datacite.org/dois?'+urllib.parse.urlencode({'query':'titles.title:"Prospective pan-cancer phosphoproteomics at clinical scale"','page[size]':100})),
 ('zenodo_exact_doi.json','https://zenodo.org/api/records?'+urllib.parse.urlencode({'q':'"'+DOI+'"','size':100})),
 ('crossref_exact_doi.json','https://api.crossref.org/works/'+urllib.parse.quote(DOI,safe=''))]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rs=list(ex.map(run,jobs))
 (B/'METADATA-OMISSION-QUERY-RECEIPTS.json').write_text(json.dumps(rs,indent=2)+'\n')
 for r in rs:print(r['name'],r.get('total'),r.get('returned'),r.get('http'),r.get('access_error'),r.get('primary_url'))
