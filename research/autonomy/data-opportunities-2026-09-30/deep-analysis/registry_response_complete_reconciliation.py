#!/usr/bin/env python3
"""Complete archived-response reconciliation; retain every raw match and ambiguity."""
import hashlib,json,math,re
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
BASE="af7211708205b5189d8c537c1ce2a23aa4bea076";CACHE="216bd1b5fb25a56b90ef3cc2373e1fe68322708f";CAP=64*1024*1024
ROOT="https://raw.githubusercontent.com/trimcrae/Rare-cancers/"
PERIODS=("1999_2009","2010_2013","2014_2017","2018_2021","2022_2026")
FILES=[f"ctg_results_bor_{p}" for p in PERIODS]+[f"ctg_placebo_onc_{p}" for p in PERIODS]
CAT={"CR":re.compile(r"^\s*(complete response|complete remission|CR)\b",re.I),"PR":re.compile(r"^\s*(partial response|partial remission|PR)\b",re.I),"SD":re.compile(r"^\s*(stable disease|SD)\b",re.I),"PD":re.compile(r"^\s*(progressive disease|disease progression|PD)\b",re.I)}
R={"schema":"emc-registry-response-complete-reconciliation/2","startedUtc":datetime.now(timezone.utc).isoformat(),"baseCommit":BASE,"cacheCommit":CACHE,"sources":[],"files":[],"errors":[],"interpretation":"Exploratory archived audit. All exact-cell matches and same-key/different-cell candidates retained. Outcome JSON plus NCT/group ID define literal tables; identical copies retain physical occurrences. Denominator differences not automatically errors; rows not unique patients."}
def read(url):
 with urlopen(Request(url,headers={"User-Agent":"Rare-cancers-response-reconciliation"}),timeout=60) as response:
  if response.headers.get("Content-Length") and int(response.headers["Content-Length"])>CAP:raise ValueError("source cap")
  raw=response.read(CAP+1)
 if len(raw)>CAP:raise ValueError("source cap")
 R["sources"].append({"url":url,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()})
 return raw.decode("utf-8-sig")
def number(v):
 try:x=float(v)
 except (TypeError,ValueError):return None
 return int(x) if math.isfinite(x) and x.is_integer() else None
def payload(t):
 i=t.find("="*30);return json.loads(t[t.find("\n",i)+1:] if i>=0 else t)
src=json.loads(read(ROOT+BASE+"/research/manuscripts/endpoint/endpoint-corpus-inputs.json"));arms=src["arms"];index=defaultdict(list)
for i,a in enumerate(arms):index[(a["nct_id"],a["outcome_measure_title"],a["arm_title"],a["evaluable_n"])].append(i)
exact=defaultdict(set);different=defaultdict(set);tables=[];table_index={};occ_seen=defaultdict(set)
for filename in FILES:
 try:
  doc=payload(read(ROOT+CACHE+"/literature/xdisease-ctg-results/"+filename+".txt"))
  R["files"].append({"file":filename,"totalCount":doc.get("totalCount"),"returned":len(doc.get("studies",[]))})
  for si,s in enumerate(doc.get("studies",[])):
   ps=s.get("protocolSection") or {};rs=s.get("resultsSection") or {};nct=(ps.get("identificationModule") or {}).get("nctId")
   for oi,om in enumerate((rs.get("outcomeMeasuresModule") or {}).get("outcomeMeasures") or []):
    omsha=hashlib.sha256(json.dumps(om,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    groups={g.get("id"):g for g in om.get("groups") or []};cells=defaultdict(dict);literal=defaultdict(list);hist=defaultdict(lambda:defaultdict(list))
    for ci,cl in enumerate(om.get("classes") or []):
     for ti,cat in enumerate(cl.get("categories") or []):
      title=cat.get("title") or "";label=next((k for k,rx in CAT.items() if rx.match(title)),None)
      for m in cat.get("measurements") or []:
       gid=m.get("groupId");v=number(m.get("value"))
       literal[gid].append({"classIndex":ci,"classFields":{k:v for k,v in cl.items() if k!="categories"},"categoryIndex":ti,"categoryTitle":title,"recognizedCategory":label,"valueLiteral":m.get("value"),"integerValue":v})
       if label and v is not None:cells[gid][label]=v;hist[gid][label].append(v)
    for gid,c in cells.items():
     if len(c)<4 or sum(c.values())<=0:continue
     title=groups.get(gid,{}).get("title") or "";n=sum(c.values());key=(nct,om.get("title"),title,n)
     if key not in index:continue
     identity=(nct,omsha,gid)
     if identity not in table_index:
      tid=len(tables);table_index[identity]=tid;den=[]
      for d in om.get("denoms") or []:
       for dc in d.get("counts") or []:
        if dc.get("groupId")==gid:den.append({"units":d.get("units"),"valueLiteral":dc.get("value"),"integerValue":number(dc.get("value"))})
      pdset=sorted({x["integerValue"] for x in den if x["integerValue"] is not None and re.fullmatch(r"\s*(participants?|patients?|subjects?)\s*",str(x["units"]),re.I)})
      repeated={k:v for k,v in hist[gid].items() if len(v)>1}
      tables.append({"tableId":tid,"nctId":nct,"outcomeJSONSha256":omsha,"outcomeTitle":om.get("title"),"outcomeType":om.get("type"),"timeFrame":om.get("timeFrame"),"populationDescription":om.get("populationDescription"),"unitOfMeasure":om.get("unitOfMeasure"),"groupId":gid,"groupLiteral":groups.get(gid),"fourCategoryCells":c,"fourCategorySum":n,"postedDenominators":den,"distinctPostedParticipantDenominators":pdset,"sumEqualsSingleParticipantDenominator":n==pdset[0] if len(pdset)==1 else None,"allCategoryMeasurements":literal[gid],"additionalCategories":[x for x in literal[gid] if x["recognizedCategory"] is None],"repeatedRecognizedCategoryValues":repeated,"recognizedCategoryOverwriteDifferent":any(len(set(v))>1 for v in repeated.values()),"sourceOccurrences":[]})
     tid=table_index[identity];occ=(filename,si,oi,gid)
     if occ not in occ_seen[tid]:
      tables[tid]["sourceOccurrences"].append({"sourceFile":filename,"studyIndex":si,"outcomeIndex":oi,"groupId":gid});occ_seen[tid].add(occ)
     for ai in index[key]:(exact if c==arms[ai]["cells"] else different)[ai].add(tid)
 except Exception as e:R["errors"].append({"file":filename,"type":type(e).__name__,"message":str(e)})
R["rows"]=[{"inputRow":i,"compactKey":{"nctId":a["nct_id"],"outcomeTitle":a["outcome_measure_title"],"groupTitle":a["arm_title"],"fourCategorySum":a["evaluable_n"]},"compactCells":a["cells"],"exactTableIds":sorted(exact[i]),"sameKeyDifferentCellTableIds":sorted(different[i]),"mappingStatus":"zero" if not exact[i] else "one" if len(exact[i])==1 else "multiple"} for i,a in enumerate(arms)]
R["literalTables"]=tables;exact_ids=set().union(*exact.values()) if exact else set();t=[tables[i] for i in sorted(exact_ids)]
R["summary"]={"inputRows":len(arms),"matchedInputRows":sum(bool(exact[i]) for i in range(len(arms))),"mappingStatusCounts":dict(Counter(r["mappingStatus"] for r in R["rows"])),"exactDistinctLiteralTables":len(exact_ids),"allCandidateDistinctLiteralTables":len(tables),"exactPhysicalSourceOccurrences":sum(len(x["sourceOccurrences"]) for x in t),"rowsWithSameKeyDifferentCellsCandidate":sum(bool(different[i]) for i in range(len(arms))),"unitOfMeasureCountsOnExactTables":dict(Counter(str(x["unitOfMeasure"]) for x in t)),"participantDenominatorStatusOnExactTables":dict(Counter("one" if len(x["distinctPostedParticipantDenominators"])==1 else "none" if not x["distinctPostedParticipantDenominators"] else "multiple" for x in t)),"exactTablesSumMatchesSingleDenominator":sum(x["sumEqualsSingleParticipantDenominator"] is True for x in t),"exactTablesSumDiffersFromSingleDenominator":sum(x["sumEqualsSingleParticipantDenominator"] is False for x in t),"exactTablesWithAdditionalCategories":sum(bool(x["additionalCategories"]) for x in t),"exactTablesWithPositiveAdditionalIntegerCategories":sum(any(c["integerValue"] is not None and c["integerValue"]>0 for c in x["additionalCategories"]) for x in t),"exactTablesWithRepeatedRecognizedCategoryLabels":sum(bool(x["repeatedRecognizedCategoryValues"]) for x in t),"exactTablesWithDifferentCategoryOverwrite":sum(x["recognizedCategoryOverwriteDifferent"] for x in t),"exactTablesWithTimeframe":sum(bool(x["timeFrame"]) for x in t),"exactTablesWithPopulationDescription":sum(bool(x["populationDescription"]) for x in t)}
R["allInputRowsReconciled"]=not R["errors"] and all(exact[i] for i in range(len(arms)))
R["finishedUtc"]=datetime.now(timezone.utc).isoformat();Path("campaign-output").mkdir(exist_ok=True);Path("campaign-output/registry-response-complete-reconciliation.json").write_text(json.dumps(R,indent=2)+"\n")
print("EMC_REGISTRY_COMPLETE_RESULT_BEGIN");print(json.dumps(R,separators=(",",":")));print("EMC_REGISTRY_COMPLETE_RESULT_END")
