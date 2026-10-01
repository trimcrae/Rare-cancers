#!/usr/bin/env python3
"""Finite released relative-CN and damaging/hotspot call controls; no EMC validation."""
import os,re,json,time,hashlib,urllib.request
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import spearmanr
HERE=Path(__file__).resolve().parent;ROOT=Path("campaign-output/genomic-state-controls");ROOT.mkdir(parents=True,exist_ok=True);CACHE=ROOT/"inputs";CACHE.mkdir(exist_ok=True)
MARKERS=["MTAP","CDKN2A","CDKN2B","SMARCB1","BRCA1","BRCA2","ATM","PALB2","RAD51C","RAD51D","TP53"]
PAIRS=[(g,y,"locus-copy/damaging-call context") for g in MARKERS[:3] for y in ["PRMT5","MAT2A"]]+[("SMARCB1","EZH2","SWI/SNF copy/damaging-call context")]+[(g,"POLQ","repair-gene copy/damaging-call context") for g in MARKERS[4:10]]
PAIRS += [("TP53","MDM2","p53 reported damaging/hotspot-call context")]
PAIRS += [(g,y,"frozen generic-fitness reference") for g in MARKERS for y in ["PSMB5","HSP90AA1"]]
RATIO_THRESHOLDS=[.1,.2];NBOOT=1000;rng=np.random.default_rng(20261001);receipts=[]
def safe(v):
 if isinstance(v,dict):return {str(k):safe(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [safe(x) for x in v]
 if isinstance(v,np.ndarray):return safe(v.tolist())
 if isinstance(v,np.integer):return int(v)
 if isinstance(v,(float,np.floating)):return float(v) if np.isfinite(v) else None
 if isinstance(v,np.bool_):return bool(v)
 return v
def write(name,value):(ROOT/name).write_text(json.dumps(safe(value),indent=2,allow_nan=False)+"\n")
def req(url):return urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Rare-cancers-finite-genomic-controls/1"}),timeout=120)
def fetch(f):
 p=CACHE/f["name"]
 if not p.exists():
  temp=p.with_suffix(p.suffix+".part");n=0
  with req(f["download_url"]) as h,temp.open("wb") as w:
   for b in iter(lambda:h.read(4*1024**2),b""):
    n+=len(b)
    if n>1024**3:raise ValueError("Frozen1GiB input cap")
    w.write(b)
  temp.replace(p)
 md=hashlib.md5();sh=hashlib.sha256()
 with p.open("rb") as h:
  for b in iter(lambda:h.read(4*1024**2),b""):md.update(b);sh.update(b)
 if p.stat().st_size!=f["size"] or md.hexdigest()!=(f.get("computed_md5") or f.get("supplied_md5")):raise ValueError("Source size/MD5")
 receipts.append({"name":f["name"],"fileID":f["id"],"url":f["download_url"],"bytes":p.stat().st_size,"md5":md.hexdigest(),"sha256":sh.hexdigest()});write("genomic-source-receipts.json",receipts);print("GENOMIC_PROGRESS retrieved "+f["name"],flush=True);return p
def matrix(f):
 p=fetch(f);header=list(pd.read_csv(p,nrows=0).columns);norm=lambda v:re.sub(r"\s*\([^)]*\)\s*$","",str(v)).strip().upper();mapping={g:[c for c in header[1:] if norm(c)==g] for g in MARKERS};schema={"name":f["name"],"indexHeader":header[0],"columnCount":len(header),"selectedGeneColumns":mapping};write(f["name"]+".schema.json",schema);print("GENOMIC_SOURCE_SCHEMA "+json.dumps(schema),flush=True)
 if any(len(v)>1 for v in mapping.values()):raise ValueError("Ambiguous selected gene")
 selected={g:v[0] for g,v in mapping.items() if v};d=pd.read_csv(p,usecols=[header[0]]+list(selected.values()),index_col=0).rename(columns={v:k for k,v in selected.items()});d.index=d.index.astype(str)
 if not d.index.is_unique or not d.index.str.fullmatch(r"ACH-\d+").all():raise ValueError("Unique released ModelID required")
 return d.apply(pd.to_numeric,errors="coerce").replace([np.inf,-np.inf],np.nan),schema
def corr(x,y):
 ok=np.isfinite(x)&np.isfinite(y);x=np.asarray(x)[ok];y=np.asarray(y)[ok]
 if len(x)<10 or np.std(x)<1e-12 or np.std(y)<1e-12:return {"n":len(x),"rho":None,"p":None}
 r,p=spearmanr(x,y);return {"n":len(x),"rho":r,"p":p}
def fdr(p):
 p=np.asarray(p,float);order=np.argsort(p);q=np.minimum.accumulate((p[order]*len(p)/np.arange(1,len(p)+1))[::-1])[::-1];z=np.empty(len(p));z[order]=np.minimum(q,1);return z
def contrast(families,col):
 z=families[families[col].isin(["proxy-positive","proxy-negative"])].dropna(subset=["effect"]);a=z[z[col].eq("proxy-positive")];b=z[z[col].eq("proxy-negative")];ans={"positiveFamilies":len(a),"negativeFamilies":len(b),"unknownOrMixedFamilies":len(families)-len(z),"positiveMean":a.effect.mean(),"negativeMean":b.effect.mean(),"rawMeanDifference":a.effect.mean()-b.effect.mean(),"withinSharedDiseaseClasses":[]}
 if min(len(a),len(b))>=3:
  strata=[(s,v.effect.to_numpy()) for (c,s),v in z.groupby(["disease",col])];boots=[]
  for _ in range(NBOOT):
   va=np.concatenate([rng.choice(v,len(v),replace=True) for s,v in strata if s=="proxy-positive"]);vb=np.concatenate([rng.choice(v,len(v),replace=True) for s,v in strata if s=="proxy-negative"]);boots.append(va.mean()-vb.mean())
  ans["conditionalDiseaseStateFamilyBootstrapCI95"]=np.quantile(boots,[.025,.975])
 differences=[];blocks=[]
 for cls,v in z.groupby("disease"):
  aa=v.loc[v[col].eq("proxy-positive"),"effect"].to_numpy();bb=v.loc[v[col].eq("proxy-negative"),"effect"].to_numpy()
  if min(len(aa),len(bb))>=3:differences.append(aa.mean()-bb.mean());blocks.append((aa,bb));ans["withinSharedDiseaseClasses"].append({"disease":cls,"positiveN":len(aa),"negativeN":len(bb),"meanDifference":aa.mean()-bb.mean()})
 if blocks:
  ans["equalDiseaseMacroMeanDifference"]=np.mean(differences);boots=[np.mean([rng.choice(a,len(a),replace=True).mean()-rng.choice(b,len(b),replace=True).mean() for a,b in blocks]) for _ in range(NBOOT)];ans["equalDiseaseMacroCI95"]=np.quantile(boots,[.025,.975])
 else:ans["diseaseAdjustedStatus"]="No disease has3 observed families in both proxy groups"
 return ans
paths=[Path(os.environ["GENOMIC_CRISPR_SOURCE"])] if os.environ.get("GENOMIC_CRISPR_SOURCE") else [Path("campaign-output/proteomics/crispr-frozen-modern-context.json"),HERE/"results"/"crispr-frozen-modern-context.json"]+list(Path("restored-artifacts").rglob("crispr-frozen-modern-context.json"));source=next((p for p in paths if p.exists()),None)
if source is None:raise ValueError("Restore actual final-core modern context")
sb=source.read_bytes();context=json.loads(sb)
if not any(r.get("sha256")=="d1633bfa0bf4719e72e564f15d9bcda7fddbbd3dac2a8a3aebf4898ac9f56f00" for r in context["sourceReceipts"]):raise ValueError("Frozen GeneEffect source pin")
ge=pd.DataFrame(context["geneEffects"]).set_index("ModelID");meta=pd.DataFrame(context["metadata"]).set_index("ModelID").reindex(ge.index)
if not ge.index.is_unique or not meta.index.is_unique:raise ValueError("Duplicate modern keys")
pats=meta.PatientID.fillna("").astype(str);meta["family"]=[p if p.startswith("PT-") else j for j,p in zip(meta.index,pats)];meta["disease"]=meta.OncotreePrimaryDisease.fillna("UNANNOTATED").astype(str);ont=meta.reindex(columns=["OncotreeSubtype","OncotreePrimaryDisease"]).fillna("").astype(str).agg(" ".join,axis=1);meta["nominalSarcoma"]=ont.str.contains("sarcoma",case=False,na=False);names=meta.CellLineName.fillna("").str.upper().str.replace(r"[^A-Z0-9]","",regex=True);meta.loc[names.isin(["SW982","HEMCSS"]),"nominalSarcoma"]=False
with req("https://api.figshare.com/v2/articles/22765112") as h:mb=h.read()
manifest=json.loads(mb);write("genomic-manifest.json",manifest);receipts.append({"name":"DepMap23Q2_manifest","url":"https://api.figshare.com/v2/articles/22765112","bytes":len(mb),"sha256":hashlib.sha256(mb).hexdigest(),"version":manifest.get("version")});files={f["name"]:f for f in manifest["files"]}
for name,fileid,md5 in [("OmicsCNGene.csv",40448840,"32b989ce2d1c1f897fed114961b919ab"),("OmicsSomaticMutationsMatrixDamaging.csv",40449647,None),("OmicsSomaticMutationsMatrixHotspot.csv",40449650,None)]:
 if name not in files or files[name]["id"]!=fileid:raise ValueError("Pinned genomic source absent")
 if md5 and (files[name].get("computed_md5") or files[name].get("supplied_md5"))!=md5:raise ValueError("CN pin")
cn,cschema=matrix(files["OmicsCNGene.csv"]);mutation,mschema=matrix(files["OmicsSomaticMutationsMatrixDamaging.csv"]);hotspot,hschema=matrix(files["OmicsSomaticMutationsMatrixHotspot.csv"]);coverage=[];records=[]
for marker in MARKERS:
 coverage.append({"gene":marker,"relativeCNSourceModels":int(cn[marker].notna().sum()) if marker in cn else 0,"pairedRelativeCNModels":int(cn.reindex(ge.index)[marker].notna().sum()) if marker in cn else 0,"invalidNegativeRelativeCNSourceRows":int((cn[marker]<0).sum()) if marker in cn else 0,"damagingSourceModels":int(mutation[marker].notna().sum()) if marker in mutation else 0,"unexpectedDamagingSourceValues":sorted([float(x) for x in mutation[marker].dropna().unique() if x not in [0,1,2]]) if marker in mutation else [],"pairedDamagingCodeCounts":mutation.reindex(ge.index)[marker].value_counts(dropna=False).to_dict() if marker in mutation else {}})
for marker,outcome,role in PAIRS:
 result={"marker":marker,"outcome":outcome,"role":role,"status":"missing source feature"}
 if marker not in cn or outcome not in ge:records.append(result);continue
 raw=pd.DataFrame({"cnReleased":cn[marker].reindex(ge.index),"effect":pd.to_numeric(ge[outcome],errors="coerce"),"damaging":mutation[marker].reindex(ge.index) if marker in mutation else np.nan,"hotspot":hotspot[marker].reindex(ge.index) if marker in hotspot else np.nan}).join(meta[["family","disease","nominalSarcoma"]]);raw.loc[raw.cnReleased<0,"cnReleased"]=np.nan;raw.loc[~raw.damaging.isin([0,1,2]),"damaging"]=np.nan;raw.loc[~raw.hotspot.isin([0,1,2]),"hotspot"]=np.nan;raw["relativeRatio"]=np.exp2(raw.cnReleased)-1;families=[]
 for family,v in raw.groupby("family"):
  entry={"family":family,"disease":v.disease.iloc[0] if v.disease.nunique()==1 else "MIXED_DISEASE_FAMILY","effect":v.effect.mean(),"cnReleased":v.cnReleased.mean(),"damaging":v.damaging.mean(),"nominalSarcoma":bool(v.nominalSarcoma.all())}
  for threshold in RATIO_THRESHOLDS:
   x=v.relativeRatio;entry["relativeRatioBelow"+str(threshold)]="unknown" if x.isna().any() else "proxy-positive" if (x<threshold).all() else "proxy-negative" if (x>=threshold).all() else "mixed"
  x=v.damaging;entry["reportedDamagingState"]="unknown" if x.isna().any() else "proxy-positive" if (x>0).all() else "proxy-negative" if (x==0).all() else "mixed"
  if marker=="TP53":
   positive=(v.damaging>0)|(v.hotspot>0);negative=v.damaging.eq(0)&v.hotspot.eq(0);entry["reportedTP53VariantState"]="proxy-positive" if positive.all() else "proxy-negative" if negative.all() else "unknown" if not (positive|negative).all() else "mixed"
  families.append(entry)
 z=pd.DataFrame(families);result.update({"status":"evaluated","modelPairsWithCNAndEffect":int(raw[["cnReleased","effect"]].notna().all(axis=1).sum()),"familyRows":len(z),"relativeCNRankAssociation":corr(z.cnReleased.to_numpy(),z.effect.to_numpy()),"damagingCodedRankAssociation":corr(z.damaging.to_numpy(),z.effect.to_numpy()),"proxyContrasts":{},"nominalSarcomaContrasts":{}});complete=z.dropna(subset=["cnReleased","effect"]);eligible=complete.disease.value_counts();complete=complete[complete.disease.isin(eligible[eligible>=3].index)]
 if len(complete)>=10 and complete.disease.nunique()>=2:
  residual=complete[["cnReleased","effect"]]-complete.groupby("disease")[["cnReleased","effect"]].transform("mean");result["withinDiseaseRelativeCNResidualAssociation"]=corr(residual.cnReleased.to_numpy(),residual.effect.to_numpy())
 for col in ["relativeRatioBelow0.1","relativeRatioBelow0.2","reportedDamagingState"]+(["reportedTP53VariantState"] if marker=="TP53" else []):result["proxyContrasts"][col]=contrast(z,col);result["nominalSarcomaContrasts"][col]=contrast(z[z.nominalSarcoma],col)
 records.append(result)
for field in ["relativeCNRankAssociation","damagingCodedRankAssociation","withinDiseaseRelativeCNResidualAssociation"]:
 inds=[i for i,r in enumerate(records) if r.get(field,{}).get("p") is not None]
 for i,q in zip(inds,fdr([records[i][field]["p"] for i in inds])):records[i][field]["descriptiveBHAcross36FrozenPairs"]=q
result={"schema":"finite-genomic-state-knockout-controls/1","executedUTC":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"modernContextSource":{"path":str(source),"sha256":hashlib.sha256(sb).hexdigest(),"sourceReceipts":context["sourceReceipts"]},"sourceReceipts":receipts,"sourceSchemas":[cschema,mschema,hschema],"sourceModels":len(ge),"patientFamilies":meta.family.nunique(),"frozenPairs":PAIRS,"coverage":coverage,"benchmarks":records,"sourceScale":{"relativeCopyNumber":"README23Q2: log2(CN ratio+1); inverse2**v-1; not absolute copies","relativeLossProxyThresholds":RATIO_THRESHOLDS,"thresholdDisclosure":"Analyst sensitivities after3row schema preview before full values; not official deletions/preregistered","damagingCalls":"README23Q2:0 no reported damaging,1 summed AF<=.95,2 AF>.95; not validated biallelicloss","p53ReportedVariantProxy":"Damaging/hotspot code1/2 reported variant proxy; both observed0 qualifies no-reported-call control, not provenWT","absoluteCopySource":"OmicsAbsoluteCNGene absent from actual article22765112v4","pipelinePin":"broadinstitute/depmap_omics23Q2:f72c809107775f38e404fe48f5efa5d6fd3a78e8"},"limitations":["Cancer-cell knockouts, not clinical efficacy/normalwindow/MTAcooperativeinhibitor response","No verified EMC or EMCprevalence","CN/damaging proxies not functional loss/HRD/biallelic/WT","Genotype/lineage correlation and Chronoscopycorrection limit causal interpretation","Missing retained; relatedmodel state conflicts excluded from categorical contrasts","Intervals conditional on disease/state family counts, not simultaneous","Residualnominal inference does not include nuisance estimation; BH descriptive"]};write("genomic-state-controls-execution-summary.json",result);print("GENOMIC_STATE_RESULT_BEGIN");print(json.dumps(safe(result),allow_nan=False));print("GENOMIC_STATE_RESULT_END",flush=True)
