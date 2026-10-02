import urllib.request,json,hashlib,datetime,pathlib,concurrent.futures,xml.etree.ElementTree as ET
out=pathlib.Path(r"C:/Users/mcrae/.codex/private/emc-continuation-20261002/checkpoint03-aso")
jobs={"construct":("PMC6766969",["construct","E-N","T-N","HEK","cryptic"]),
"models":("PMC9813045",["exon","USZ20","USZ22","DNA sequencing","RNA","fusion"]),
"pfred":("PMC7822268",["off-target","off target","BLAST","antisense","efficacy"]),
"cell_offtarget":("PMC6915909",["microarray","mismatch","pre-mRNA","RNase","complementarity"]),
"specificity":("PMC4114480",["overexpression","off-target","accessib","RNase H1","structure"])}
def read(item):
 name,(pmcid,terms)=item;url="https://www.ebi.ac.uk/europepmc/webservices/rest/"+pmcid+"/fullTextXML"
 r=dict(name=name,url=url,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 try:
  with urllib.request.urlopen(url,timeout=25) as f:b=f.read(2000000);r.update(status=f.status,response_bytes=len(b),response_sha256=hashlib.sha256(b).hexdigest())
  root=ET.fromstring(b);paras=[]
  for sec in root.findall(".//body//sec"):
   title=" ".join(sec.findtext("title","").split())
   for p in sec.findall("./p"):
    text=" ".join("".join(p.itertext()).split())
    if any(t.lower() in text.lower() for t in terms):paras.append(dict(section=title,text=text))
  # Parent nested sections can repeat headings but only direct p extracted.
  selected=paras[:12]
  r.update(read_scope="Selected relevant body paragraphs; no supplement review",body_paragraph_matches=len(paras),
           sections=[p["section"] for p in selected],access="fulltext_xml",pmcid=pmcid)
  return r,selected
 except Exception as e:r.update(status=getattr(e,"code",0),access="failed",error=str(e));return r,[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: results=list(ex.map(read,jobs.items()))
(out/"fulltext-receipts.json").write_text(json.dumps(dict(records=[r for r,ps in results]),indent=2)+"\n")
for r,ps in results:print(json.dumps(dict(receipt=r,paragraphs=ps),ensure_ascii=True))

