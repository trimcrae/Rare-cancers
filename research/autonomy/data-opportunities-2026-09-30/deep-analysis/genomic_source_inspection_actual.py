#!/usr/bin/env python3
import json,hashlib,urllib.request,re,io,html
from pathlib import Path
import pandas as pd
ROOT=Path("campaign-output/genomic-state-controls");ROOT.mkdir(parents=True,exist_ok=True)
GENES=["MTAP","CDKN2A","CDKN2B","SMARCB1","BRCA1","BRCA2","ATM","PALB2","RAD51C","RAD51D"]
def get(url,cap,partial=False):
 req=urllib.request.Request(url,headers={"User-Agent":"Rare-cancers-bounded-genomic-state/1"})
 with urllib.request.urlopen(req,timeout=120) as h:b=h.read(cap if partial else cap+1);status=h.status
 if not partial and len(b)>cap:raise ValueError("Bounded metadata cap exceeded")
 return b,{"url":url,"bytesRead":len(b),"sha256ReadBytes":hashlib.sha256(b).hexdigest(),"httpStatus":status,"partialFileRead":partial}
url="https://api.figshare.com/v2/articles/22765112";b,receipt=get(url,4*1024**2);manifest=json.loads(b);(ROOT/"depmap23Q2-manifest.json").write_bytes(b);files=manifest["files"]
plain=html.unescape(re.sub(r"<[^>]*>"," ",str(manifest.get("description",""))));candidates=[f for f in files if re.search(r"(?:copy.?number|(?:^|_)cn(?:_|gene|\.|$)|CNGene|AbsoluteCN)",f["name"],re.I)]
result={"schema":"depmap23Q2-genomic-source-inspection/1","manifestReceipt":receipt,"articleVersion":manifest.get("version"),"description":plain,"allFiles":[{"id":f["id"],"name":f["name"],"size":f["size"],"download_url":f["download_url"],"md5":f.get("computed_md5") or f.get("supplied_md5")} for f in files],"copyNumberCandidates":[],"documentation":[],"frozenGenomicContextGenes":GENES,"lossUnitsVerified":False}
for f in [x for x in files if re.search("readme|description|documentation",x["name"],re.I) and x["size"]<=1024**2][:5]:
 try:bb,rr=get(f["download_url"],1024**2);result["documentation"].append({"name":f["name"],"receipt":rr,"text":bb.decode("utf-8",errors="replace")})
 except Exception as e:result["documentation"].append({"name":f["name"],"error":str(e)})
for f in candidates[:4]:
 rec={"file":{"id":f["id"],"name":f["name"],"size":f["size"],"download_url":f["download_url"],"md5":f.get("computed_md5") or f.get("supplied_md5")},"scope":"Partial header/schema inspection; full source checksum not yet verified"}
 try:
  bb,rr=get(f["download_url"],2*1024**2,partial=True);rec["readReceipt"]=rr
  if f["name"].lower().endswith(".csv"):
   frame=pd.read_csv(io.BytesIO(bb[:bb.rfind(b"\n")+1]),nrows=3);rec["columnsPreview"]=list(frame.columns[:12]);rec["columnCount"]=len(frame.columns);norm=lambda v:re.sub(r"\s*\([^)]*\)\s*$","",str(v)).strip().upper();selected={g:[c for c in frame if norm(c)==g] for g in GENES};rec["selectedGeneColumns"]=selected;cols=[frame.columns[0]]+[v[0] for v in selected.values() if len(v)==1];rec["selectedRowsPreview"]=json.loads(frame[cols].to_json(orient="records"))
  else:rec["binarySourceRequiresDocumentedParser"]=True
 except Exception as e:rec["error"]=type(e).__name__+": "+str(e)
 result["copyNumberCandidates"].append(rec)
(ROOT/"genomic-source-inspection.json").write_text(json.dumps(result,indent=2)+"\n");print("GENOMIC_SOURCE_INSPECTION_BEGIN");print(json.dumps(result));print("GENOMIC_SOURCE_INSPECTION_END",flush=True)
