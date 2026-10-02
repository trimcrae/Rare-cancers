import urllib.request,urllib.parse,json,hashlib,datetime,pathlib,concurrent.futures,xml.etree.ElementTree as ET
out=pathlib.Path(r"C:/Users/mcrae/.codex/private/emc-continuation-20261002/checkpoint03-aso");out.mkdir(exist_ok=True)
queries={"fusion":"EXT_ID:8634690 AND SRC:MED","construct":"EXT_ID:31020999 AND SRC:MED","models":"EXT_ID:36316541 AND SRC:MED","junction_aso":"EXT_ID:1794439 AND SRC:MED","pfred":'DOI:"10.1371/journal.pone.0238753"',"cell_offtarget":"PMCID:PMC6915909","specificity":'DOI:"10.1371/journal.pone.0101752"'}
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"EMC-source-integration/1"}),timeout=25) as f:
  b=f.read(2000000);return b,dict(url=url,final_url=f.url,status=f.status,response_bytes=len(b),response_sha256=hashlib.sha256(b).hexdigest(),retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
def fetch(item):
 name,q=item;url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&query="+urllib.parse.quote(q)
 try:
  b,r=get(url);d=json.loads(b);rs=d["resultList"]["result"]
  r.update(name=name,query=q,hit_count=d["hitCount"],metadata=[{k:x[k] for k in ["id","pmcid","doi","title","authorString","pubYear","firstPublicationDate","journalInfo","pubTypeList","abstractText"] if k in x} for x in rs])
  return r
 except Exception as e:return dict(name=name,url=url,status=getattr(e,"code",0),error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:records=list(e.map(fetch,queries.items()))
(out/"primary-metadata.json").write_text(json.dumps(dict(scope="Targeted primary bibliographic retrieval, not a comprehensive review",records=records),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
for r in records:print(json.dumps(r,ensure_ascii=True))

