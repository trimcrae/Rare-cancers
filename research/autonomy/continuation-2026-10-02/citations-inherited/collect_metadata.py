import urllib.request, urllib.parse, json, hashlib, datetime, concurrent.futures, pathlib
OUT=pathlib.Path(r"C:/Users/mcrae/.codex/private/emc-continuation-20261002/citations-inherited")
OUT.mkdir(exist_ok=True)
dois=["10.1002/aisy.202500778","10.1007/s00262-025-04123-y","10.1038/s41467-025-61272-5","10.1136/jitc-2020-002071","10.1371/journal.pone.0161879","10.21203/rs.3.rs-10374394/v1"]
pmids=["33858848","35705558","35710741","35839778","41895280"]
jobs=[("DOI",d,"https://api.crossref.org/works/"+urllib.parse.quote(d,safe="")) for d in dois]
jobs += [("PMID",p,"https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&query="+urllib.parse.quote("EXT_ID:"+p+" AND SRC:MED")) for p in pmids]
jobs += [("PMCID","PMC8054196","https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&query=PMCID:PMC8054196"),("DOI","10.6019/PXD019643","https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD019643"),("GEO","GSE285944","https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE285944&targ=self&form=text&view=quick")]
def fetch(j):
 kind,ident,url=j
 r={"kind":kind,"requested_identifier":ident,"url":url,"retrieved_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"attempts":[]}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"EMC-bibliographic-verification/1.0"}),timeout=25) as f:
   b=f.read(2000000);r.update(status=f.status,final_url=f.url,response_bytes=len(b),response_sha256=hashlib.sha256(b).hexdigest(),digest_scope="HTTP response bytes before parsing; full response not retained")
  r["attempts"]=[{"n":1,"status":r["status"]}]
  if "crossref" in url:
   m=json.loads(b)["message"];r["identity_matches"]=m["DOI"].lower()==ident.lower()
   r["metadata"]={k:m[k] for k in ["DOI","title","publisher","container-title","type","published","published-online","published-print","URL","relation","update-to"] if k in m}
  elif "europepmc" in url:
   m=json.loads(b);r["hit_count"]=m["hitCount"];rr=m["resultList"]["result"];r["identity_matches"]=len(rr)==1 and rr[0].get("id" if kind=="PMID" else "pmcid")==ident
   r["metadata"]=[{k:x[k] for k in ["id","source","pmcid","doi","title","authorString","pubYear","firstPublicationDate","pubTypeList","isRetracted","journalInfo"] if k in x} for x in rr]
   if kind=="PMID":r["pubmed_url"]="https://pubmed.ncbi.nlm.nih.gov/"+ident+"/"
  elif kind=="GEO":
   s=b.decode();r["identity_matches"]="^SERIES = "+ident in s;r["metadata"]=[l for l in s.splitlines() if l.startswith(("^SERIES","!Series_title","!Series_status","!Series_submission_date","!Series_last_update_date","!Series_pubmed_id","!Series_type","!Series_relation"))]
  else:
   m=json.loads(b);r["identity_matches"]=m.get("accession")=="PXD019643";r["metadata"]={k:m[k] for k in ["accession","title","projectDescription","doi","publicationDate","submissionDate","references"] if k in m}
 except Exception as e:r.update(status=getattr(e,"code",0),error=str(e)[:300],identity_matches=False);r["attempts"]=[{"n":1,"status":r["status"]}]
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: records=list(ex.map(fetch,jobs))
(OUT/"primary-metadata.json").write_text(json.dumps({"schema":"emc-citation-primary-metadata/1","scope":"Bibliographic identity only; does not establish scientific claim. Response hashes cover actual fetched bytes.","records":records},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
for r in records: print(json.dumps({"id":r["requested_identifier"],"status":r["status"],"identity_matches":r["identity_matches"]},ensure_ascii=True))
