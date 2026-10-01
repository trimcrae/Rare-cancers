"""Finite public primary-source verification, exploratory campaign amendment.
Stdlib only; public downloads; no secrets, uploads, paid services or GPU.
"""
import csv, hashlib, io, json, sys, zipfile
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
LIMIT=64*1024*1024
out={"schema":"primary-source-verification/1","started_utc":datetime.now(timezone.utc).isoformat(),"sources":[],"papers":[],"errors":[]}
def get(url):
 with urlopen(Request(url,headers={"User-Agent":"EMC-secondary-source-audit/1"}),timeout=35) as r:
  data=r.read(LIMIT+1)
  if len(data)>LIMIT: raise ValueError("source exceeds64MiB")
 out["sources"].append({"url":url,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()})
 return data
for pmid,pmc in [("33479225",None),("41895280",None),("", "PMC13374579")]:
 record={"pmid":pmid,"requested_pmc":pmc}
 try:
  if pmid:
   search=json.loads(get("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urlencode({"query":"EXT_ID:"+pmid+" AND SRC:MED","format":"json","resultType":"core"})))
   hits=search.get("resultList",{}).get("result",[])
   if len(hits)!=1: raise ValueError("expected one primary PMID search result")
   record["primary_record"]=hits[0]
   pmc=hits[0].get("pmcid")
  if pmc:
   raw=get("https://www.ebi.ac.uk/europepmc/webservices/rest/"+pmc+"/fullTextXML")
   root=ET.fromstring(raw)
   record["pmc"]=pmc
   record["article_title"]=" ".join(root.find(".//article-title").itertext()) if root.find(".//article-title") is not None else None
   record["abstracts"]=[" ".join(p.itertext()) for p in root.findall(".//abstract")]
   record["body_paragraphs"]=[" ".join(p.itertext()) for p in root.findall("./body//p")]
   record["table_texts"]=[" ".join(p.itertext()) for p in root.findall(".//table-wrap")]
   record["related_article_attributes"]=[x.attrib for x in root.findall(".//related-article")]
   record["supplement_links"]=[{"tag":x.tag,"attrs":x.attrib,"text":" ".join(x.itertext())} for x in root.findall(".//supplementary-material")]
  else: record["fulltext_status"]="No PMC identifier in exact primary record"
 except Exception as e: record["retrieval_error"]={"type":type(e).__name__,"message":str(e)}
 out["papers"].append(record)
try:
 url="https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-020-20603-4/MediaObjects/41467_2020_20603_MOESM4_ESM.xlsx"
 raw=get(url); z=zipfile.ZipFile(io.BytesIO(raw)); ns={"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
 strings=[]
 if "xl/sharedStrings.xml" in z.namelist():
  strings=["".join(x.itertext()) for x in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("s:si",ns)]
 sheets=[]
 for path in z.namelist():
  if path.startswith("xl/worksheets/sheet") and path.endswith(".xml"):
   root=ET.fromstring(z.read(path));rows=[]
   for row in root.findall(".//s:sheetData/s:row",ns):
    cells=[]
    for c in row.findall("s:c",ns):
     v=c.find("s:v",ns);t=c.attrib.get("t")
     value=v.text if v is not None else ""
     if t=="s": value=strings[int(value)] if value else ""
     if t=="inlineStr":value="".join(c.find("s:is",ns).itertext())
     cells.append({"ref":c.attrib.get("r"),"value":value})
    rows.append(cells)
   sheets.append({"path":path,"rows":rows})
 out["methylation_primary_workbook"]={"url":url,"sha256":hashlib.sha256(raw).hexdigest(),"sheets":sheets}
except Exception as e: out["errors"].append({"resource":"methylation_primary_workbook","type":type(e).__name__,"message":str(e)})
out["finished_utc"]=datetime.now(timezone.utc).isoformat()
print("EMC_PRIMARY_RESULT_BEGIN")
print(json.dumps(out,separators=(",",":")))
print("EMC_PRIMARY_RESULT_END")
# An inaccessible source remains a documented blocker, not proof of its absence.
