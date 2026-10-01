#!/usr/bin/env python3
"""Resolve Foundation export history and primary source before subtype inference."""
import csv,hashlib,io,json,re,zipfile,xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
CAP=512*1024*1024;LFS="https://nsssw8k94d.execute-api.us-east-1.amazonaws.com/objects/batch"
R={"schema":"foundation-primary-provenance-reconciliation/1","startedUtc":datetime.now(timezone.utc).isoformat(),"sources":[],"errors":[]}
OBJECTS={"oldPatient":("0c0883de3f9c998070446dc2bbaad5b1041784ca0429eeefa9089c3390788546",535987),"currentPatient":("3fee9db9a9ef8740f9645e83c365f0df009a252a591cab29580aca013ec7ed9b",536138),"oldSample":("3e9892efa5fbb7c61e2e30ec45f6e3c9bd78c230e0dd37937d6f4e65f673c358",1129472),"currentSample":("ca98900d145c39e74b49f0f2a75d7f339e4e5afc283053bbf67685bb3f5cf83a",1029561)}
def get(url,data=None,headers=None):
 h={"User-Agent":"Rare-cancers-source-reconciliation"};h.update(headers or {})
 with urlopen(Request(url,data=data,headers=h),timeout=120) as r:b=r.read(CAP+1)
 if len(b)>CAP:raise ValueError("source cap")
 return b
def source(key):
 oid,n=OBJECTS[key];q={"operation":"download","transfers":["basic"],"objects":[{"oid":oid,"size":n}]};x=json.loads(get(LFS,json.dumps(q).encode(),{"Content-Type":"application/vnd.git-lfs+json","Accept":"application/vnd.git-lfs+json"}))["objects"][0]
 if x.get("error"):raise ValueError("LFS refusal "+key)
 a=x["actions"]["download"];b=get(a["href"],headers=a.get("header",{}))
 if len(b)!=n or hashlib.sha256(b).hexdigest()!=oid:raise ValueError("LFS integrity")
 R["sources"].append({"key":key,"bytes":n,"sha256":oid,"hashAndSizeVerified":True});return list(csv.DictReader((l for l in b.decode("utf-8-sig").splitlines() if l and not l.startswith("#")),delimiter="\t"))
def txt(e):return " ".join(" ".join(e.itertext()).split()) if e is not None else ""
try:
 data={k:source(k) for k in OBJECTS};cp={x["PATIENT_ID"]:x for x in data["currentPatient"]};op={x["PATIENT_ID"]:x for x in data["oldPatient"]};cs={x["SAMPLE_ID"]:x for x in data["currentSample"]};os={x["SAMPLE_ID"]:x for x in data["oldSample"]}
 ids={k for k,v in cs.items() if any(str(x).casefold()=="extraskeletal myxoid chondrosarcoma" for x in v.values())}
 ordinal_probe=set()
 for k in ids:
  m=re.search(r'(?:^|-)(\d+)$',str(k))
  if m:ordinal_probe.update(int(m.group(1))+o for o in (0,1,2))
 R["currentNominalEmc"]=len(ids);R["oldPatientDiagnosisCounts"]=dict(Counter(op[k].get("FINAL_DIAGNOSIS") for k in ids if k in op));R["oldCurrentPatientDifferences"]=[{"id":k,"old":op.get(k),"current":cp.get(k)} for k in sorted(ids) if op.get(k)!=cp.get(k)];R["oldCurrentSamplePairs"]=[{"id":k,"old":os.get(k),"current":cs.get(k)} for k in sorted(ids)]
 meta=json.loads(get("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A35705558%20AND%20SRC%3AMED&format=json"));hits=meta["resultList"]["result"];R["primaryMetadata"]=hits
 pmc=next(x["pmcid"] for x in hits if x.get("pmcid"));url="https://www.ebi.ac.uk/europepmc/webservices/rest/"+pmc+"/fullTextXML";b=get(url);root=ET.fromstring(b);R["primarySource"]={"url":url,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()};rx=re.compile(r"chondrosarcoma|myxoid|reclass|assign|diagnos|mutation.{0,20}burden|TMB|Foundation|NR4A3|panel",re.I);R["primaryParagraphs"]=[txt(p) for p in root.findall(".//body//p") if rx.search(txt(p))];R["primaryTables"]=[txt(t) for t in root.findall(".//table-wrap")];R["supplementDeclarations"]=[{"tag":e.tag,"attributes":e.attrib,"text":txt(e)} for e in root.iter() if e.tag in ("supplementary-material","media")]
 url="https://www.ebi.ac.uk/europepmc/webservices/rest/"+pmc+"/supplementaryFiles";b=get(url);R["supplementArchive"]={"url":url,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()};z=zipfile.ZipFile(io.BytesIO(b));R["archiveMembers"]=[{"name":e.filename,"bytes":e.file_size} for e in z.infolist()];sheets=[];ns={"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"};rid="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
 cache=Path("campaign-output/source-workbooks");cache.mkdir(parents=True,exist_ok=True)
 genes=("NR4A3","NR4A2","EWSR1","TAF15","RET","ALK","CDKN2A","MTAP")
 for member in z.infolist():
  if not member.filename.lower().endswith(".xlsx") or member.file_size>CAP:continue
  raw=z.read(member);cached=cache/Path(member.filename).name;cached.write_bytes(raw);a=zipfile.ZipFile(io.BytesIO(raw));strings=[]
  if "xl/sharedStrings.xml" in a.namelist():strings=[txt(x) for x in ET.fromstring(a.read("xl/sharedStrings.xml")).findall("s:si",ns)]
  rel={x.attrib["Id"]:x.attrib["Target"] for x in ET.fromstring(a.read("xl/_rels/workbook.xml.rels"))}
  for sheet in ET.fromstring(a.read("xl/workbook.xml")).findall("s:sheets/s:sheet",ns):
   target=rel[sheet.attrib[rid]];path=target.lstrip("/") if target.startswith("/") else "xl/"+target
   if path not in a.namelist():path=path.replace("xl/xl/","xl/")
   first=[];diag=[];selected=[];count=0;gc=Counter();gr=[]
   with a.open(path) as stream:
    for _,elem in ET.iterparse(stream,events=("end",)):
     if elem.tag!="{"+ns["s"]+"}row":continue
     count+=1;row={}
     for c in elem.findall("s:c",ns):
      v=c.find("s:v",ns);val=v.text if v is not None else ""
      if c.attrib.get("t")=="s":val=strings[int(val)] if val else ""
      elif c.attrib.get("t")=="inlineStr":val=txt(c.find("s:is",ns))
      row[c.attrib.get("r")]=val
     if len(first)<10:first.append(row)
     if any("chondrosarcoma" in str(v).casefold() or "NR4A3" in str(v).upper() for v in row.values()):
      if len(diag)<500:diag.append(row)
     present=[g for g in genes if any(str(v).upper()==g for v in row.values())]
     gc.update(present)
     if present and len(gr)<100:gr.append({"genes":present,"row":row})
     if "sample" in sheet.attrib["name"].lower() and count in ordinal_probe:selected.append(row)
     elem.clear()
   sheets.append({"file":member.filename,"cachedPath":str(cached),"fileSha256":hashlib.sha256(raw).hexdigest(),"sheet":sheet.attrib["name"],"rows":count,"firstRows":first,"chondrosarcomaOrNr4a3LiteralRows":diag,"sampleOrdinalProbeRows":selected,"targetLiteralCounts":dict(gc),"targetLiteralExampleRows":gr,"ordinalScope":"Candidate mappings only; IDs may not be source sheet ordinal. No mapping until headers/primary row IDs verified.","alterationScope":"Gene literal is not automatically measured CNA; inspect schema."})
 R["primaryWorkbookSheets"]=sheets
except Exception as e:R["errors"].append({"type":type(e).__name__,"message":str(e)})
R["finishedUtc"]=datetime.now(timezone.utc).isoformat();Path("campaign-output").mkdir(exist_ok=True);Path("campaign-output/foundation-primary-provenance-reconciliation.json").write_text(json.dumps(R,indent=2)+"\n")
print("EMC_FOUNDATION_ORIGIN_RESULT_BEGIN");print(json.dumps(R,separators=(",",":")));print("EMC_FOUNDATION_ORIGIN_RESULT_END")
