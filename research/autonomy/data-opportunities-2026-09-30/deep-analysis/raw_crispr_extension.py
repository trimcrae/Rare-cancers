#!/usr/bin/env python3
import os,re,json,hashlib,urllib.request,time
from pathlib import Path
import numpy as np
import pandas as pd
def run(meta,rna,prot,training,primary,benchmark):
 ROOT=Path(os.environ.get("PROTEOMICS_OUTPUT_DIR","campaign-output/proteomics"));ROOT.mkdir(parents=True,exist_ok=True);CACHE=ROOT/"inputs";CACHE.mkdir(exist_ok=True)
 RECEIPTS=[];secondary=[]
 TARGETS=["CDK7","CDK9","HSP90AA1","HSP90AB1","CDC37","ATR","PRMT5","MTAP","MAT2A","BCL2","BCL2L1","MCL1","ASS1","MDM2","EZH2","SMARCB1","POLQ","PSMB5","BRD4","BRD9","SMARCA2","ALK","ROS1","EGFR","HDAC1","HDAC2","HDAC3","HDAC6","PRKDC","RET"]
 NBOOT=1000;rng=np.random.default_rng(20261001)
 def safe(v):
  if isinstance(v,dict):return {str(k):safe(x) for k,x in v.items()}
  if isinstance(v,(list,tuple)):return [safe(x) for x in v]
  if isinstance(v,np.ndarray):return safe(v.tolist())
  if isinstance(v,np.integer):return int(v)
  if isinstance(v,(np.floating,float)):return float(v) if np.isfinite(v) else None
  if isinstance(v,np.bool_):return bool(v)
  return v
 def write(name,value):(ROOT/name).write_text(json.dumps(safe(value),indent=2,allow_nan=False)+"\n")
 def stage(name):print("CRISPR_PROGRESS "+name,flush=True)
 def req(url):return urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Rare-cancers-public-CRISPR-audit/1"}),timeout=120)
 def symbols(value):return re.sub(r"\s+\(\d+\)$","",str(value))
 def numeric(df):return df.apply(pd.to_numeric,errors="coerce").replace([np.inf,-np.inf],np.nan)
 def download(f):
  path=CACHE/f["name"]
  if not path.exists():
   size=0;temp=path.with_suffix(path.suffix+".part")
   with req(f["download_url"]) as h,temp.open("wb") as w:
    while True:
     block=h.read(4*1024*1024)
     if not block:break
     size+=len(block)
     if size>2*1024**3:raise RuntimeError("public-file cap exceeded")
     w.write(block)
   temp.replace(path)
  md=hashlib.md5();sh=hashlib.sha256()
  with path.open("rb") as h:
   for block in iter(lambda:h.read(4*1024*1024),b""):md.update(block);sh.update(block)
  expected=f.get("computed_md5") or f.get("supplied_md5")
  if expected and md.hexdigest()!=expected:raise ValueError("CRISPR MD5 mismatch")
  if f.get("size") and path.stat().st_size!=f["size"]:raise ValueError("CRISPR size mismatch")
  RECEIPTS.append({"name":f["name"],"fileId":f["id"],"bytes":path.stat().st_size,"md5":md.hexdigest(),"sha256":sh.hexdigest(),"url":f["download_url"]});write("crispr-source-receipts.json",RECEIPTS);stage("retrieved "+f["name"]);return path
 stage("retrieve actual public CRISPR outcomes");api="https://api.figshare.com/v2/articles/22765112"
 with req(api) as h:cb=h.read()
 cm=json.loads(cb);write("depmap23Q2-manifest.json",cm);RECEIPTS.append({"name":"DepMap23Q2_manifest","url":api,"bytes":len(cb),"sha256":hashlib.sha256(cb).hexdigest(),"version":cm.get("version")})
 files={f["name"]:f for f in cm["files"]}
 if not {"CRISPRGeneEffect.csv","Model.csv"}.issubset(files):raise ValueError("Manifest lacks expected endpoints")
 gefile=download(files["CRISPRGeneEffect.csv"]);demeta=download(files["Model.csv"]);dm=pd.read_csv(demeta);geheader=list(pd.read_csv(gefile,nrows=0).columns)
 schema={"geneEffectColumnsPreview":geheader[:8],"geneEffectColumnCount":len(geheader),"ModelColumns":list(dm.columns),"modelPreview":dm.head(3).replace({np.nan:None}).to_dict("records")};write("crispr-source-schema.json",schema);print("CRISPR_SOURCE_SCHEMA "+json.dumps(safe(schema),allow_nan=False),flush=True)
 keys=[c for c in ["ModelID","DepMap_ID","depmap_id","Unnamed: 0"] if c in dm.columns]
 if not keys:raise ValueError("Unknown Model schema; header retained")
 dm=dm.set_index(keys[0]);dm.index=dm.index.astype(str);gene_cols={}
 for gene in TARGETS:
  candidates=[c for c in geheader[1:] if symbols(c)==gene]
  if len(candidates)>1:raise ValueError("Ambiguous CRISPR gene "+gene)
  if candidates:gene_cols[gene]=candidates[0]
 ge=pd.read_csv(gefile,usecols=[geheader[0]]+list(gene_cols.values()),index_col=0);ge.index=ge.index.astype(str)
 if not ge.index.is_unique:raise ValueError("Duplicate raw model ID")
 if len(ge) and not ge.index.str.startswith("ACH-").all():raise ValueError("Nonstable Broad ID")
 ge=numeric(ge).rename(columns={v:k for k,v in gene_cols.items()});pairs=meta[["BROAD_ID","Cell_line","Cancer_type","relatedGroup","isTraining","primarySarcomaTest","disputedEMCLabel"]].copy()
 pairs["rawCRISPRModelPresent"]=pairs.BROAD_ID.isin(ge.index)&pairs.BROAD_ID.isin(dm.index);pairs["ambiguousSourceIdentifier"]=meta["ambiguousSourceIdentifier"].fillna(False).astype(bool);pairs["eligibleIdentifierPair"]=pairs.rawCRISPRModelPresent&~pairs.ambiguousSourceIdentifier;pairs["modernSourceModelName"]=pairs.BROAD_ID.map(dm["CellLineName"]) if "CellLineName" in dm else None;pairs["modernSourcePatientID"]=pairs.BROAD_ID.map(dm["PatientID"]) if "PatientID" in dm else None
 write("crispr-identifier-pairing.json",pairs.reset_index().replace({np.nan:None}).to_dict("records"))
 write("crispr-data-boundary.json",{"source":"DepMap23Q2 Chronos,article22765112","targetColumnMap":gene_cols,"rawDimensions":ge.shape,"pairedModels":int(pairs.rawCRISPRModelPresent.sum()),"eligibleIdentifierPairs":int(pairs.eligibleIdentifierPair.sum()),"pairing":"CMP BROAD_ID to modern ModelID; same cells, not independent cohorts","geneEffectUnits":"Chronos normalized effects,zero nonessential, commonessentials about-1","dependencyThreshold":-.5,"interpretation":"Cancer-cell knockout not pharmacologic efficacy, normal-tissue window, EMCdependency or causal synthetic lethality"})
 ge_sid=pd.DataFrame(index=meta.index)
 for gene in TARGETS:
  if gene in ge:ge_sid[gene]=meta.BROAD_ID.map(ge[gene]).where(pairs.eligibleIdentifierPair)
 pairs_frozen=[(g,g,"cognate abundance") for g in TARGETS]+[("MTAP","PRMT5","locus-expression proxy"),("MTAP","MAT2A","locus-expression proxy"),("SMARCB1","EZH2","SWI/SNF abundance proxy"),("BCL2L1","MCL1","BH3 cross-target"),("MCL1","BCL2L1","BH3 cross-target"),("BCL2","BCL2L1","BH3 cross-target"),("BCL2L1","BCL2","BH3 cross-target")]
 distributions=[]
 for outcome_gene in TARGETS:
  if outcome_gene not in ge_sid:
   secondary.append({"gene":outcome_gene,"outcome":"CRISPR:"+outcome_gene,"kind":"Chronos","status":"gene absent from raw schema"});continue
  yy=ge_sid[outcome_gene];dd=pd.concat([yy.rename("effect"),meta[["relatedGroup","Cancer_type","isTraining","primarySarcomaTest"]]],axis=1).dropna(subset=["effect"]);dd=dd.groupby(["relatedGroup","Cancer_type","isTraining","primarySarcomaTest"],as_index=False).effect.mean()
  for cls,z in dd[dd.primarySarcomaTest].groupby("Cancer_type"):
   d={"gene":outcome_gene,"lineage":cls,"families":len(z),"meanEffect":z.effect.mean(),"medianEffect":z.effect.median(),"effectQ25Q75":z.effect.quantile([.25,.75]).tolist(),"dependentBelowMinusHalf":int((z.effect<-.5).sum()),"scope":"descriptive cancer-cell normalized knockout"}
   if len(z)>=3:
    vals=z.effect.to_numpy();boots=[np.mean(rng.choice(vals,size=len(vals),replace=True)) for _ in range(NBOOT)];d["meanFamilyBootstrapCI95"]=np.quantile(boots,[.025,.975])
   distributions.append(d)
 for predictor,outcome_gene,role in pairs_frozen:
  if outcome_gene not in ge_sid:continue
  rr=benchmark(predictor,ge_sid[outcome_gene],"CRISPR:"+outcome_gene,"Chronos gene effect");rr.update({"sourceRelease":"DepMap23Q2","outcomeGene":outcome_gene,"predictorRole":role,"stateBoundary":"abundance proxy not genomic loss/functional state"});secondary.append(rr)
 modern_columns=[c for c in ["CellLineName","PatientID","OncotreeSubtype","OncotreePrimaryDisease","OncotreeLineage"] if c in dm]
 write("crispr-frozen-modern-context.json",{"schema":"depmap23Q2-frozen-modern-context/1","sourceReceipts":RECEIPTS,"frozenTargets":TARGETS,"geneEffects":ge.reset_index().rename(columns={ge.index.name or "index":"ModelID"}).replace({np.nan:None}).to_dict("records"),"metadata":dm[modern_columns].reset_index().rename(columns={dm.index.name or "index":"ModelID"}).replace({np.nan:None}).to_dict("records"),"units":"Chronos normalized gene effect; cancer-cell knockout, not drug exposure or normal-tissue window"})
 if "BRD9" in ge:
  modern=dm.reindex(ge.index).copy()
  ont=modern.reindex(columns=["OncotreeSubtype","OncotreePrimaryDisease"]).fillna("").astype(str).agg(" ".join,axis=1)
  syn=ont.str.contains("Synovial",case=False,na=False)
  sar=ont.str.contains("Ewing|Osteosarcoma|Rhabdomyosarcoma|Chondrosarcoma|Leiomyosarcoma|Synovial|Fibrosarcoma|Liposarcoma|Epithelioid Sarcoma|Undifferentiated Pleomorphic|Malignant Peripheral",case=False,regex=True,na=False)
  names=modern.get("CellLineName",pd.Series("",index=modern.index)).fillna("").astype(str)
  invalid=names.str.upper().str.replace(r"[^A-Z0-9]","",regex=True).eq("SW982")
  z=pd.DataFrame({"effect":ge["BRD9"],"synovial":syn,"modelName":names,"ModelID":ge.index},index=ge.index)
  pats=modern.get("PatientID",pd.Series("",index=modern.index)).fillna("").astype(str)
  z["family"]=[p if p.startswith("PT-") else j for j,p in zip(z.index,pats)]
  z=z[sar&~invalid].dropna(subset=["effect"])
  mixed=z.groupby("family").synovial.nunique();mixedfamilies=mixed.index[mixed>1]
  z=z[~z.family.isin(mixedfamilies)]
  grouped=z.groupby(["family","synovial"],as_index=False).effect.mean()
  s=grouped.loc[grouped.synovial,"effect"].to_numpy();o=grouped.loc[~grouped.synovial,"effect"].to_numpy()
  control={"gene":"BRD9","control":"Full modern-source nominal synovial versus other named sarcoma","sourceRelease":"DepMap23Q2","synovialFamilyN":len(s),"otherSarcomaFamilyN":len(o),"synovialMean":np.mean(s) if len(s) else None,"otherSarcomaMean":np.mean(o) if len(o) else None,"meanDifference":np.mean(s)-np.mean(o) if len(s) and len(o) else None,"synovialSourceRows":z[z.synovial].reset_index(drop=True).to_dict("records"),"excludedDisputedSW982":modern.loc[invalid].reset_index().to_dict("records"),"excludedMixedSynovialPatientFamilies":list(mixedfamilies),"scope":"Source ontology control; not molecular SS18-fusion verification, a new dependency discovery, or independent EMC evidence","rawControlUnits":"Chronos normalized gene effect; descriptive cancer-cell knockout"}
  if min(len(s),len(o))>=3:
   diffs=[np.mean(rng.choice(s,len(s),replace=True))-np.mean(rng.choice(o,len(o),replace=True)) for _ in range(NBOOT)]
   control["familyBootstrapMeanDifferenceCI95"]=np.quantile(diffs,[.025,.975])
  distributions.append(control)
 write("crispr-class-distributions.json",distributions)
 result={"benchmarks":secondary,"classDistributions":distributions,"sourceReceipts":RECEIPTS,"sourceSchema":schema,"pairingCounts":{"metaModels":len(meta),"rawCRISPRModels":len(ge),"pairedModels":int(pairs.rawCRISPRModelPresent.sum()),"eligibleIdentifierPairs":int(pairs.eligibleIdentifierPair.sum())},"frozenTargets":TARGETS,"frozenPredictorOutcomePairs":pairs_frozen,"executedUTC":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
 write("crispr-execution-summary.json",result);print("CRISPR_RESULT_BEGIN",flush=True);print(json.dumps(safe(result),allow_nan=False),flush=True);print("CRISPR_RESULT_END",flush=True);return result
