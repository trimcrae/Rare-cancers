import urllib.request,urllib.parse,json,hashlib,datetime,pathlib
p=pathlib.Path(r"C:/Users/mcrae/.codex/private/emc-continuation-20261002/citations-inherited/primary-metadata.json")
doc=json.loads(p.read_text(encoding="utf-8"))
ident="10.1007/s00262-025-04123-y"
url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&query="+urllib.parse.quote('DOI:"'+ident+'"')
with urllib.request.urlopen(url,timeout=25) as f:
 b=f.read(1000000)
 r={"kind":"DOI","requested_identifier":ident,"url":url,"final_url":f.url,"status":f.status,"attempts":[{"n":1,"status":f.status}],"retrieved_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"response_bytes":len(b),"response_sha256":hashlib.sha256(b).hexdigest(),"digest_scope":"HTTP response bytes before parsing; full response not retained"}
m=json.loads(b);rr=m["resultList"]["result"]
r["hit_count"]=m["hitCount"];r["identity_matches"]=len(rr)==1 and rr[0].get("doi","").lower()==ident.lower()
r["metadata"]=[{k:x[k] for k in ["id","source","pmcid","doi","title","pubYear","firstPublicationDate","pubTypeList","journalInfo"] if k in x} for x in rr]
doc["records"].append(r)
for rec in doc["records"]:
 if rec["requested_identifier"]=="10.6019/PXD019643":
  rec["identity_matches"]=rec["metadata"].get("doi","").lower()=="10.6019/pxd019643" and rec["metadata"].get("accession")=="PXD019643"
p.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(r,ensure_ascii=True))

