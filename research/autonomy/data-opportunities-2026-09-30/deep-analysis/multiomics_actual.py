#!/usr/bin/env python3
"""Frozen sarcoma transfer audit,2026-10-01. CPU,public archivalwhole-cell protein/RNA, no EMCvalidation."""
import os,sys,json,hashlib,urllib.request,time,re,warnings
from pathlib import Path
from collections import defaultdict
import h5py
from urllib.parse import urlencode
import numpy as np
import pandas as pd
from scipy.stats import spearmanr,mannwhitneyu
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression,Ridge
from sklearn.model_selection import GroupKFold
SEED=20261001
PANEL=["CD276","SSTR2","PRAME","FAP","CD248","CSPG4","MSLN","L1CAM","GPC3","ALPP","CDH17"]
CONTROL=["CHRNA6"]
TARGETS=["CDK7","CDK9","HSP90AA1","HSP90AB1","CDC37","ATR","PRMT5","MTAP","MAT2A","BCL2","BCL2L1","MCL1","ASS1","MDM2","EZH2","SMARCB1","POLQ","PSMB5","BRD4"]
TARGETS+=["BRD9","SMARCA2","ALK","ROS1","EGFR","HDAC1","HDAC2","HDAC3","HDAC6","PRKDC","RET"]
ALPHAS=[.01,.1,1.,10.,100.];NBOOT=1000;NPERM=1000
ROOT=Path(os.environ.get("PROTEOMICS_OUTPUT_DIR","campaign-output/proteomics"));ROOT.mkdir(parents=True,exist_ok=True)
CACHE=ROOT/"inputs";CACHE.mkdir(exist_ok=True);RECEIPTS=[];STAGES=[]
def stage(s):
 STAGES.append({"stage":s,"timeUTC":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())})
 print("PROTEOMICS_PROGRESS "+s,flush=True)
def safe(v):
 if isinstance(v,dict):return {str(k):safe(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [safe(x) for x in v]
 if isinstance(v,np.ndarray):return safe(v.tolist())
 if isinstance(v,(np.integer,)):return int(v)
 if isinstance(v,(np.floating,float)):return float(v) if np.isfinite(v) else None
 if isinstance(v,(np.bool_,)):return bool(v)
 return v
def write(name,v):(ROOT/name).write_text(json.dumps(safe(v),indent=2,allow_nan=False)+"\n")
def req(url):return urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Rare-cancers-public-data-audit/1"}),timeout=120)
def get_manifest():
 with req("https://api.figshare.com/v2/articles/19345397") as h:b=h.read()
 m=json.loads(b);write("figshare-manifest.json",m)
 RECEIPTS.append({"name":"Figshare19345397_manifest","bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"articleVersion":m.get("version"),"url":"https://api.figshare.com/v2/articles/19345397"})
 return m
def download(f):
 p=CACHE/f["name"];md=hashlib.md5();sh=hashlib.sha256();size=0
 if not p.exists():
  with req(f["download_url"]) as h,p.with_suffix(p.suffix+".part").open("wb") as w:
   while True:
    b=h.read(4*1024*1024)
    if not b:break
    size+=len(b)
    if size>2*1024**3:raise RuntimeError("Source exceeds2GiB/file cap")
    w.write(b)
  p.with_suffix(p.suffix+".part").replace(p)
 with p.open("rb") as h:
  for b in iter(lambda:h.read(4*1024*1024),b""):md.update(b);sh.update(b)
 size=p.stat().st_size;expected=f.get("computed_md5") or f.get("supplied_md5")
 if expected and md.hexdigest()!=expected:raise ValueError("MD5 mismatch "+f["name"])
 if f.get("size") and size!=f["size"]:raise ValueError("Size mismatch "+f["name"])
 RECEIPTS.append({"name":f["name"],"fileId":f.get("id"),"bytes":size,"md5":md.hexdigest(),"sha256":sh.hexdigest(),"url":f["download_url"]})
 stage("retrieved "+f["name"]);return p
def select(m,name):
 hits=[f for f in m["files"] if f["name"]==name]
 if len(hits)!=1:raise ValueError("Expected one manifest entry for "+name)
 return download(hits[0])
def numeric(d):return d.apply(pd.to_numeric,errors="coerce").replace([np.inf,-np.inf],np.nan)
def mean_by_id(d):return d.groupby(level=0,sort=True).mean()
def symbols(s):return re.sub(r"\s+\(\d+\)$","",str(s))
def fdr(ps):
 ps=np.asarray(ps,dtype=float);ans=np.full(len(ps),np.nan);ok=np.isfinite(ps);vals=ps[ok]
 if len(vals):
  o=np.argsort(vals);tmp=np.minimum.accumulate((vals[o]*len(vals)/(np.arange(len(vals))+1))[::-1])[::-1];restored=np.empty(len(vals));restored[o]=np.minimum(tmp,1);ans[ok]=restored
 return ans
def corr(x,y):
 good=np.isfinite(x)&np.isfinite(y)
 if good.sum()<5 or np.std(x[good])<1e-10 or np.std(y[good])<1e-10:return {"n":int(good.sum()),"rho":None,"p":None}
 z=spearmanr(x[good],y[good]);return {"n":int(good.sum()),"rho":float(z.statistic),"p":float(z.pvalue)}
def pipeline(kind,alpha=1):
 base=LinearRegression() if kind=="single" else Ridge(alpha=alpha)
 return make_pipeline(SimpleImputer(strategy="median",keep_empty_features=True),StandardScaler(),base)
def group_splits(groups,n=5):
 k=min(n,len(np.unique(groups)))
 if k<2:return []
 return list(GroupKFold(n_splits=k).split(np.arange(len(groups)),groups=groups))
def tune(X,y,groups):
 splits=group_splits(groups,3)
 if not splits:return 1.
 scores=[]
 for a in ALPHAS:
  errs=[]
  for tr,va in splits:
   model=pipeline("ridge",a).fit(X[tr],y[tr]);errs.extend(np.abs(y[va]-model.predict(X[va])))
  scores.append(float(np.mean(errs)))
 return ALPHAS[int(np.argmin(scores))]
def nested_choice(xone,X,y,groups):
 splits=group_splits(groups,5)
 if len(splits)<2:return "single",{"reason":"insufficient development lineages"}
 outs={"single":[],"ridge":[],"median":[]};alpha_log=[]
 for tr,va in splits:
  for k,XX in [("single",xone),("ridge",X)]:
   a=tune(XX[tr],y[tr],groups[tr]) if k=="ridge" else 1.;pred=pipeline(k,a).fit(XX[tr],y[tr]).predict(XX[va]);outs[k].extend(np.abs(y[va]-pred))
   if k=="ridge":alpha_log.append(a)
  outs["median"].extend(np.abs(y[va]-np.median(y[tr])))
 maes={k:float(np.mean(v)) for k,v in outs.items()};chosen="single" if maes["single"]<=maes["ridge"] else "ridge"
 return chosen,{"outerGroupedMAE":maes,"outerRidgeAlphas":alpha_log,"selectionRule":"minimum outerMAE,tie tosingle"}
def aggregate_records(records,fixed_support=None):
 if len(records)==0:return None
 rr=pd.DataFrame(records)
 if fixed_support is None:
  good=rr.groupby(['gene','lineage'])['group'].nunique();support=set(good[good>=5].index)
 else:support=set(fixed_support)
 if not support:return None
 present=set(rr.groupby(['gene','lineage']).size().index)
 if not support.issubset(present):return None
 rr=rr.set_index(['gene','lineage']);rr=rr.loc[rr.index.isin(support)].reset_index()
 z=rr.groupby(['gene','lineage'])[['selectedError','singleError','baselineError']].mean()
 return {'strata':len(z),'genes':int(z.index.get_level_values(0).nunique()),'lineages':int(z.index.get_level_values(1).nunique()),'selectedNMAE':float(z.selectedError.mean()),'singleNMAE':float(z.singleError.mean()),'medianBaselineNMAE':float(z.baselineError.mean()),'relativeImprovement':float(1-z.selectedError.mean()/z.baselineError.mean()) if z.baselineError.mean()>0 else None}
def load_measured_growth():
 candidates=[Path(os.environ["PROTEOMICS_MEASURED_GROWTH_SOURCE"])] if os.environ.get("PROTEOMICS_MEASURED_GROWTH_SOURCE") else [Path(__file__).resolve().parent/"results"/"primary-measured-growth-reconciliation.json",ROOT/"primary-measured-growth-reconciliation.json"]
 path=next((p for p in candidates if p.exists()),None)
 if path is None:raise ValueError("Final run requires verified primary measured growth; source file absent")
 b=path.read_bytes();d=json.loads(b)
 if d.get("workbookSHA256")!="9327f665d259ef4d148d3a64e7c76cdeb51dce8dee06768efd6b7d044130e203":raise ValueError("Measured growth workbook pin mismatch")
 if d.get("growthHeader")!="growth" or d.get("sheet")!="Cell line level sample info":raise ValueError("Measured growth column identity mismatch")
 if d.get("sourceDefinitionVerified") is not True or not d.get("sourceDefinition"):raise ValueError("Verify exact primary growth definition before final execution")
 frame=pd.DataFrame(d["records"])
 if not {"model_id","growthValue"}.issubset(frame) or frame.model_id.duplicated().any():raise ValueError("Measured growth identifiers invalid")
 if not frame.model_id.astype(str).str.fullmatch(r"SIDM\d+").all():raise ValueError("Nonstable measured growth identifiers")
 series=pd.to_numeric(frame.set_index("model_id").growthValue,errors="raise");series.index=series.index.astype(str)
 return series,{"sourcePath":str(path),"sourceJSONSHA256":hashlib.sha256(b).hexdigest(),"workbookSHA256":d["workbookSHA256"],"sourceReceipt":d.get("source"),"sourceDefinition":d["sourceDefinition"],"sourceDefinitionVerified":True,"unitsVerified":d.get("unitsVerified",False),"sourceScale":d.get("sourceScale","Published growth column used as released; mapping of exported numerical scale to the primary control ratio is unverified; no extra transformation"),"sourceMeasuredModels":len(series),"transform":"Published growth covariate used as released; no inferred additional log transform"}
def main():
    measured_growth,growth_manifest=load_measured_growth()
    stage("manifest");m=get_manifest()
    def by_id(fid):
     hits=[f for f in m["files"] if f["id"]==fid]
     if len(hits)!=1:raise ValueError("Missing pinned Figshare file "+str(fid))
     return download(hits[0])
    h5p=by_id(34411016)
    if hashlib.sha256(h5p.read_bytes()).hexdigest()!="839818e7333caec11b2717e63aafc0a0fee2186349573819fc9e06b1f377ef52":raise ValueError("Pinned HDF5SHA mismatch")
    pp=by_id(34411151);mp=by_id(34411133);dp=by_id(34355645)
    for p,expected in [(pp,"dc9a209c48425846c341dbb996c878c9"),(mp,"21407e29046d77f42b4f39298ffee7f2"),(dp,"0b4932f7395cc95457eeef435993d122")]:
     if hashlib.md5(p.read_bytes()).hexdigest()!=expected:raise ValueError("Frozen fileMD5 mismatch "+p.name)
    with req("https://cog.sanger.ac.uk/cmp/download/model_list_20210719.csv") as h:cmpb=h.read()
    cp=CACHE/"model_list_20210719.csv";cp.write_bytes(cmpb);RECEIPTS.append({"name":cp.name,"bytes":len(cmpb),"sha256":hashlib.sha256(cmpb).hexdigest(),"url":"https://cog.sanger.ac.uk/cmp/download/model_list_20210719.csv"})
    cmp=pd.read_csv(cp).set_index("model_id");cmp.index=cmp.index.astype(str)
    meta=pd.read_csv(mp,sep="\t").set_index("SIDM");meta.index=meta.index.astype(str);meta.index.name="model_id"
    if not meta.index.is_unique:raise ValueError("Duplicate primary mapping SIDM")
    keep=[c for c in cmp.columns if c not in meta.columns];meta=meta.join(cmp[keep],how="left")
    accessions={"CD276":"Q5ZPR3","SSTR2":"P30874","PRAME":"P78395","FAP":"Q12884","CD248":"Q9HCU0","CSPG4":"Q6UVK1","MSLN":"Q13421","L1CAM":"P32004","GPC3":"P51654","ALPP":"P05187","CDH17":"Q12864","CHRNA6":"Q15825","CDK7":"P50613","CDK9":"P50750","HSP90AA1":"P07900","HSP90AB1":"P08238","CDC37":"Q16543","ATR":"Q13535","PRMT5":"O14744","MTAP":"Q13126","MAT2A":"P31153","BCL2":"P10415","BCL2L1":"Q07817","MCL1":"Q07820","ASS1":"P00966","MDM2":"Q00987","EZH2":"Q15910","SMARCB1":"Q12824","POLQ":"O75417","PSMB5":"P28074","BRD4":"O60885","BRD9":"Q9H8M2","SMARCA2":"P51531","ALK":"Q9UM73","ROS1":"P08922","EGFR":"P00533","HDAC1":"Q13547","HDAC2":"Q92769","HDAC3":"O15379","HDAC6":"Q9UBN7","PRKDC":"P78527","RET":"P07949"}
    uniprot_url="https://rest.uniprot.org/uniprotkb/stream?"+urlencode({"format":"tsv","fields":"accession,id,gene_primary","query":" OR ".join("accession:"+v for v in accessions.values())})
    with req(uniprot_url) as h:ub=h.read()
    up=CACHE/"frozen-uniprot-target-map.tsv";up.write_bytes(ub)
    um=pd.read_csv(up,sep="\t").set_index("Entry")
    RECEIPTS.append({"name":up.name,"bytes":len(ub),"sha256":hashlib.sha256(ub).hexdigest(),"url":uniprot_url})
    for gene,acc in accessions.items():
        if acc not in um.index or gene not in str(um.loc[acc,"Gene Names (primary)"]).split():raise ValueError("Frozen canonical accession not corroborated: "+gene)
    rawprot=pd.read_csv(pp,sep="\t",index_col=0)
    if sum(str(v).startswith("SIDM") for v in rawprot.index)<sum(str(v).startswith("SIDM") for v in rawprot.columns):rawprot=rawprot.T
    rawprot.index=[str(v).split(";")[0] for v in rawprot.index];rawprot=mean_by_id(numeric(rawprot))
    columns_by_acc=defaultdict(list)
    for col in rawprot.columns:
        for token in re.split(r"[;|]",str(col)):
            if token in accessions.values():columns_by_acc[token].append(col)
    prot=pd.DataFrame({g:rawprot[columns_by_acc[a]].mean(axis=1) if columns_by_acc[a] else pd.Series(np.nan,index=rawprot.index) for g,a in accessions.items()})
    def decode(v):return v.decode() if isinstance(v,(bytes,np.bytes_)) else str(v)
    with h5py.File(h5p,"r") as h:
        rna_frames=[]
        for group in h["samples"]:
            if group!="Other":continue
            samples=[decode(x) for x in h["samples"][group][...]];features=[decode(x) for x in h["features"]["transcriptomics"][...]];values=h["data"]["transcriptomics"][group][...]
            if values.shape!=(len(samples),len(features)):raise ValueError("Unexpected RNA HDF5 axis shape")
            intercept=h["intercepts"]["transcriptomics"][group][...].reshape(-1)
            if len(intercept)!=len(features):raise ValueError("Unexpected RNA intercept")
            rna_frames.append(pd.DataFrame(values+intercept,index=samples,columns=features))
        rna=pd.concat(rna_frames).groupby(level=0).mean()
    rna.columns=[symbols(x) for x in rna.columns];rna=rna.T.groupby(level=0).mean().T
    mapping_receipt={"canonicalAccessionMap":accessions,"primaryProteinColumnMap":{g:columns_by_acc[a] for g,a in accessions.items()},"proteinMatrix":"Figshare34411151 canonical accession means; no nondetection imputation","RNA":"HDF5 data/transcriptomics/group +intercepts, notlatentfactors","RNAUnits":"author MOFA-scaled input, Other only; intercept restores centering only, not scaling; global archival preprocessing disclosed","columnPreview":list(rawprot.columns[:10]),"originalProteinDimensions":rawprot.shape}
    write("source-receipts.json",RECEIPTS)
    ids=sorted(set(meta.index)&set(prot.index)&set(rna.index));meta=meta.reindex(ids);prot=prot.reindex(ids);rna=rna.reindex(ids)
    ctype=meta.Cancer_type.fillna("UNKNOWN").astype(str);subtype=meta.get("Cancer_subtype",pd.Series("",index=meta.index)).fillna("").astype(str)
    name=meta.get('Cell_line',pd.Series('',index=meta.index)).fillna('').astype(str)
    norm_name=name.str.upper().str.replace(r'[^A-Z0-9]','',regex=True)
    broad=meta.get('BROAD_ID',pd.Series('',index=meta.index)).fillna('').astype(str)
    meso_context=ctype.eq('Mesothelioma')&subtype.str.contains('Sarcomatoid',case=False,na=False)
    sarcoma=(ctype.str.contains('sarcoma',case=False)|subtype.str.contains('sarcoma',case=False))&~ctype.eq('Mesothelioma')
    disputed=norm_name.eq('HEMCSS')|broad.eq('ACH-001519')|subtype.str.contains('Extraskeletal myxoid',case=False,na=False)
    sarcoma|=disputed;primary=sarcoma&~disputed
    known_label=~ctype.str.strip().str.lower().isin({'','unknown','uncertain','nan','na','n/a','none'})
    ambiguous=broad.eq('ACH-000561')|meta.index.isin(['SIDM00322','SIDM00484'])
    training=~sarcoma&~meso_context&~ambiguous&known_label
    name=meta.get("Cell_line",pd.Series("",index=meta.index)).fillna("").astype(str);normalized=name.str.upper().str.replace(r"[^A-Z0-9]","",regex=True)
    broad=meta.get("BROAD_ID",pd.Series("",index=meta.index)).fillna("").astype(str);patient=meta.get("patient_id",pd.Series("",index=meta.index)).fillna("").astype(str);parent=meta.get("parent_id",pd.Series("",index=meta.index)).fillna("").astype(str)
    links={j:j for j in meta.index}
    def find(j):
        links.setdefault(j,j)
        if links[j]!=j:links[j]=find(links[j])
        return links[j]
    def union(a,b):
        a=find(a);b=find(b)
        if a!=b:links[max(a,b)]=min(a,b)
    for j in meta.index:
        if patient.loc[j].startswith("SIDP"):union(j,"PATIENT:"+patient.loc[j])
        if parent.loc[j].startswith("SIDM"):union(j,parent.loc[j])
        for alias in str(broad.loc[j]).split(";"):
            if re.fullmatch(r"ACH-\d+",alias.strip()):union(j,"BROAD:"+alias.strip())
        if normalized.loc[j]:union(j,"NAME:"+normalized.loc[j])
    meta["relatedGroup"]=[find(j) for j in meta.index]
    held_family=set(meta.loc[sarcoma|meso_context|ambiguous,"relatedGroup"])
    training=~meta.relatedGroup.isin(held_family)&known_label
    meta["heldoutMesotheliomaContext"]=meso_context
    meta["ambiguousSourceIdentifier"]=ambiguous
    write("taxonomy-and-identity-exclusions.json",meta.loc[meso_context|ambiguous|disputed].reset_index().replace({np.nan:None}).to_dict("records"))
    write("excluded-uncertain-training-labels.json",meta.loc[~known_label].reset_index().replace({np.nan:None}).to_dict("records"))
    meta["isTraining"]=training;meta["isSarcoma"]=sarcoma;meta["primarySarcomaTest"]=primary;meta["disputedEMCLabel"]=disputed
    write("sarcoma-model-manifest.json",meta.loc[sarcoma].reset_index().replace({np.nan:None}).to_dict("records"));write("identifier-audit.json",mapping_receipt)
    groupcollisions=meta.groupby("relatedGroup").size();group_lineage_counts=meta.groupby("relatedGroup").Cancer_type.nunique();cross_lineage=group_lineage_counts[group_lineage_counts>1].to_dict()
    frozen={"seed":SEED,"panel":PANEL,"control":CONTROL,"targets":TARGETS,"alphas":ALPHAS,"bootstrapReplicates":NBOOT,"nullPermutations":NPERM,"development":"non-sarcoma; nested Cancer_type groupedCV; globallyprocessed archivalmatrices","test":"sarcoma excluding unresolved EMC-labelled models; nooutcomefiltering","familyRule":"transitive union SIDPpatient,SIDMparent,ACHBroad,normalizedname; entire sarcoma family excluded","minimumPrimaryStratum":5,"minimumPrimaryTrainingPerGene":50,"minimumPrimaryMatchedTestPerGene":5,"minimumDescriptiveTrainingPerGene":10,"minimumDescriptiveMatchedTestPerGene":3,"primaryMacro":"equal gene by Cancer_type strata,n>=5families","scale":"training proteinIQR, trainingmedianbaseline","quantification":"missing remainsmissing, nozeros, measuredproteinconditional","noveltyBoundary":"Original compares RNA/protein andpredictsdrugs/CRISPR. Frozen sarcoma transfer/calibration audit."}
    write("frozen-analysis-manifest.json",frozen);stage("nested non-sarcoma training and held-out evaluation")
    genewise=[];records=[];coverage=[];prediction_models={}
    uncertainty_lineage=meta.groupby("relatedGroup").Cancer_type.agg(lambda z:sorted(set(z.astype(str)))[0]).to_dict()
    available_features=[g for g in PANEL+CONTROL if g in rna.columns];Xall=rna.reindex(columns=available_features);rng=np.random.default_rng(SEED)
    for gene in PANEL+CONTROL:
        row={"gene":gene,"role":"panel" if gene in PANEL else "priorRNAmarkercontrol","rnaAvailable":gene in rna.columns,"proteinAvailable":bool(columns_by_acc[accessions[gene]])}
        y=prot[gene] if gene in prot.columns else pd.Series(np.nan,index=meta.index);x=rna[gene] if gene in rna.columns else pd.Series(np.nan,index=meta.index);test_ids=meta.index[primary]
        row.update({"testModels":len(test_ids),"testQuantifiedProtein":int(y.reindex(test_ids).notna().sum()),"testMatchedRNAProtein":int((y.reindex(test_ids).notna()&x.reindex(test_ids).notna()).sum())})
        for cls,mi in meta.loc[primary].groupby("Cancer_type"):
            j=mi.index;coverage.append({"gene":gene,"lineage":cls,"models":len(j),"families":mi.relatedGroup.nunique(),"proteinQuantified":int(y.reindex(j).notna().sum()),"rnaQuantified":int(x.reindex(j).notna().sum()),"matched":int((y.reindex(j).notna()&x.reindex(j).notna()).sum())})
        miss={}
        for lab,flag in [("development",training),("sarcoma",primary)]:
            measured=x[flag&y.notna()].dropna();unmeasured=x[flag&y.isna()].dropna()
            miss[lab]={"proteinMeasuredN":len(measured),"proteinMissingN":len(unmeasured),"medianRNAProteinMeasured":measured.median(),"medianRNAProteinMissing":unmeasured.median(),"mannWhitneyP":mannwhitneyu(measured,unmeasured,alternative="two-sided").pvalue if min(len(measured),len(unmeasured))>=5 else None}
        row["quantificationMissingness"]=miss;tr=meta.index[training&x.notna()&y.notna()];te=meta.index[primary&x.notna()&y.notna()]
        row["primaryEligible"]=bool(len(tr)>=50 and len(te)>=5)
        if len(tr)<10 or len(te)<3 or gene not in available_features:
            row["status"]="unsupported";row["reason"]="minimum10development/3testnotmet;coverage retained";genewise.append(row);continue
        yy=y.loc[tr].to_numpy();xx=x.loc[tr].to_numpy().reshape(-1,1);XX=Xall.loc[tr].to_numpy();groups=np.asarray([uncertainty_lineage[meta.loc[j,"relatedGroup"]] for j in tr]);scale=np.quantile(yy,.75)-np.quantile(yy,.25)
        if scale<=1e-10:
            row["status"]="unsupported";row["reason"]="trainingproteinIQRzero";genewise.append(row);continue
        chosen,cv=nested_choice(xx,XX,yy,groups);selected_alpha=tune(XX,yy,groups) if chosen=="ridge" else None
        single=pipeline("single").fit(xx,yy);selected=pipeline(chosen,selected_alpha or 1).fit(XX if chosen=="ridge" else xx,yy)
        predsingle=single.predict(x.loc[te].to_numpy().reshape(-1,1));pred=selected.predict(Xall.loc[te].to_numpy() if chosen=="ridge" else x.loc[te].to_numpy().reshape(-1,1))
        frame=pd.DataFrame({"group":meta.loc[te,"relatedGroup"].values,"lineage":ctype.loc[te].values,"observed":y.loc[te].values,"rna":x.loc[te].values,"predicted":pred,"single":predsingle},index=te)
        frame["lineage"]=[uncertainty_lineage[g] for g in frame.group];frame=frame.groupby(["group","lineage"],as_index=False).mean(numeric_only=True)
        base=float(np.median(yy));raw_mae=float(np.mean(np.abs(frame.observed-frame.predicted)));base_mae=float(np.mean(np.abs(frame.observed-base)))
        cal=LinearRegression().fit(frame.predicted.to_numpy().reshape(-1,1),frame.observed) if np.std(frame.predicted)>1e-10 else None
        row.update({"status":"evaluated","developmentN":len(tr),"developmentLineages":len(np.unique(groups)),"testRelatedGroups":len(frame),"trainingProteinIQR":scale,"trainingProteinMedian":base,"selected":chosen,"selectedAlpha":selected_alpha,"developmentCV":cv,"testNMAE":raw_mae/scale,"testMedianBaselineNMAE":base_mae/scale,"relativeImprovement":1-raw_mae/base_mae if base_mae else None,"calibrationSlope":float(cal.coef_[0]) if cal else None,"calibrationIntercept":float(cal.intercept_) if cal else None,"rnaProteinSpearman":corr(frame.rna.to_numpy(),frame.observed.to_numpy()),"predictedProteinSpearman":corr(frame.predicted.to_numpy(),frame.observed.to_numpy()),"trainingProteinQ75":np.quantile(yy,.75),"trainingRNAQ75":np.quantile(x.loc[tr],.75)})
        q=[]
        for cls,df in frame.groupby("lineage"):
            if len(df)<5:continue
            highrna=df.rna>=row["trainingRNAQ75"];highprotein=df.observed>=row["trainingProteinQ75"]
            q.append({"lineage":cls,"n":len(df),"rule":"trainingQ75>=ties","rnaHigh":int(highrna.sum()),"proteinHigh":int(highprotein.sum()),"bothHigh":int((highrna&highprotein).sum()),"agreement":float((highrna==highprotein).mean()),"precisionRNAHigh":float(highprotein[highrna].mean()) if highrna.sum() else None})
        row["upperQuartileConcordance"]=q
        for rec in frame.to_dict("records"):
            rec.update({"gene":gene,"primaryEligible":row["primaryEligible"],"role":row["role"],"scale":scale,"baseline":base,"selectedError":abs(rec["observed"]-rec["predicted"])/scale,"singleError":abs(rec["observed"]-rec["single"])/scale,"baselineError":abs(rec["observed"]-base)/scale});records.append(rec)
        genewise.append(row);stage("evaluated "+gene)
    write("panel-coverage.json",coverage);write("per-gene-transfer.json",genewise);write("heldout-predictions.json",records)
    panel_records=[r for r in records if r["gene"] in PANEL and r["primaryEligible"]]
    # Freeze eligible gene/lineage strata before bootstrap; resampling cannot add unsupported strata.
    supported={(g,l) for (g,l),v in pd.DataFrame(panel_records).groupby(["gene","lineage"]) if v["group"].nunique()>=5} if panel_records else set()
    panel_records=[r for r in panel_records if (r["gene"],r["lineage"]) in supported]
    summary=aggregate_records(panel_records,supported)
    independent=meta.loc[primary].groupby("relatedGroup").Cancer_type.agg(lambda z:sorted(set(z.astype(str)))[0]);cls_groups={c:list(v.index) for c,v in independent.groupby(independent)}
    if summary is not None:
        grouped={g:[r for r in panel_records if r["group"]==g] for g in independent.index};bs=[]
        for _ in range(NBOOT):
            b=[]
            for cls,gs in cls_groups.items():
                for bno,g in enumerate(rng.choice(gs,size=len(gs),replace=True)):
                    for r in grouped.get(g,[]):
                        q=dict(r);q["group"]=str(g)+"#"+str(bno);b.append(q)
            v=aggregate_records(b,supported)
            if v is not None:bs.append(v["relativeImprovement"])
        summary["fixedEligibleStrata"]=sorted([list(x) for x in supported]);summary["bootstrapSkippedMissingEntireStratum"]=NBOOT-len(bs)
        summary["bootstrapRelativeImprovementCI95"]=np.quantile(bs,[.025,.975]) if bs else None;summary["bootstrapSuccessfulReplicates"]=len(bs)
        rr=pd.DataFrame(panel_records);bystratum=[d.to_dict("records") for _,d in rr.groupby(["gene","lineage"])];null=[]
        for _ in range(NPERM):
            perm=[]
            for block in bystratum:
                obs=rng.permutation([r["observed"] for r in block])
                for r,o in zip(block,obs):
                    q=dict(r);q["observed"]=o;q["selectedError"]=abs(o-q["predicted"])/q["scale"];q["singleError"]=abs(o-q["single"])/q["scale"];q["baselineError"]=abs(o-q["baseline"])/q["scale"];perm.append(q)
            z=aggregate_records(perm,supported)
            if z is not None:null.append(z["relativeImprovement"])
        summary["withinLineageProteinPermutationP"]=(1+sum(v>=summary["relativeImprovement"] for v in null))/(1+len(null));summary["withinLineageNullRelativeImprovementCI95"]=np.quantile(null,[.025,.975]) if null else None
    coverage_total={g:float(prot[g].reindex(meta.index[primary]).notna().mean()) if g in prot else 0 for g in PANEL}
    feasibility={"primarySarcomaModels":int(primary.sum()),"relatedGroups":int(meta.loc[primary].relatedGroup.nunique()),"lineages":int(meta.loc[primary].Cancer_type.nunique()),"panelProteinCoverage":coverage_total,"panelGenesWith70PercentCoverage":sum(v>=.7 for v in coverage_total.values()),"planningMinimumMet":bool(meta.loc[primary].relatedGroup.nunique()>=20 and meta.loc[primary].Cancer_type.nunique()>=2 and sum(v>=.7 for v in coverage_total.values())>=6)}
    write("panel-transfer-summary.json",{"feasibility":feasibility,"primary":summary,"crossLineageFamilyExclusionSensitivity":aggregate_records([r for r in panel_records if r["group"] not in cross_lineage]),"unsupportedGenes":[x["gene"] for x in genewise if x["status"]!="evaluated"],"controls":[x for x in genewise if x["gene"] in CONTROL]})
    stage("parse measured drug outcomes");drug=pd.read_csv(dp);source_schema={"columns":list(drug.columns),"shape":drug.shape,"preview":drug.head(3).replace({np.nan:None}).to_dict("records")}
    write("drug-source-schema.json",source_schema);print("DRUG_SOURCE_SCHEMA "+json.dumps(safe(source_schema),allow_nan=False),flush=True)
    required={"model_id","drug_id","drug_name","dataset","ln_IC50"}
    if not required.issubset(drug.columns):raise ValueError("Actual drug schema missing columns: "+str(sorted(required-set(drug.columns))))
    drug=drug[~drug.cell_line_name.eq("LS-1034")].copy() if "cell_line_name" in drug else drug.copy();drug["model_id"]=drug.model_id.astype(str);druggroups=list(drug.groupby(["drug_id","drug_name","dataset"],sort=True));selection=[];wanted=set(TARGETS)
    for key,d in druggroups:
        target_text=" ".join(sorted(set(d.putative_gene_target.dropna().astype(str)))) if "putative_gene_target" in d else "";tokens=set(re.findall(r"[A-Z][A-Z0-9]+",target_text));frozen_hit=sorted(tokens&wanted)
        if frozen_hit:selection.append((key,d,frozen_hit,target_text))
    write("drug-endpoint-manifest.json",[{"drug_id":k[0],"drug_name":k[1],"dataset":k[2],"targets":ts,"sourceTargetAnnotation":tx} for k,d,ts,tx in selection])
    stage("bounded target-outcome transfer/confounding controls");secondary=[];proliferation_genes=["MKI67","PCNA","TOP2A","MCM2","MCM3","MCM4","MCM5","MCM6","MCM7","CDK1","CCNB1"];pg=[g for g in proliferation_genes if g in rna.columns]
    pmean=rna.loc[training,pg].mean();psd=rna.loc[training,pg].std().replace(0,np.nan);proliferation=((rna[pg]-pmean)/psd).mean(axis=1)
    write("proliferation-proxy-manifest.json",{"genes":pg,"centering":"non-sarcoma family-heldout trainingmean/SD","interpretation":"RNA proliferation proxy retained as context, not used as final measured growth"})
    growth_for_adjustment=measured_growth.reindex(meta.index)
    growth_label="Published growth covariate: "+growth_manifest["sourceDefinition"]
    growth_manifest.update({"observedTrainingModels":int(growth_for_adjustment.loc[training].notna().sum()),"trainingModels":int(training.sum()),"observedPrimaryModels":int(growth_for_adjustment.loc[primary].notna().sum()),"primaryModels":int(primary.sum()),"associationMissingness":"Complete cases; no zero or median fill of unknown measured growth","predictiveMissingness":"Development-contained imputation"})
    write("growth-control-manifest.json",growth_manifest)
    print("MEASURED_GROWTH_CONTROL "+json.dumps(safe(growth_manifest),allow_nan=False),flush=True)
    def benchmark(gene,y,label,outcome_kind):
        if gene not in rna or gene not in prot:return {"gene":gene,"outcome":label,"kind":outcome_kind,"status":"nomatchedRNA/protein"}
        d=pd.concat([rna[gene].rename("rna"),prot[gene].rename("protein"),y.rename("outcome")],axis=1).join(meta[["Cancer_type","relatedGroup","primarySarcomaTest","isSarcoma"]])
        growth=growth_for_adjustment;d=d.join(growth.rename("growth")).dropna(subset=["rna","protein","outcome","Cancer_type"]);d["Cancer_type"]=[uncertainty_lineage[g] for g in d.relatedGroup]
        d=d.groupby(["relatedGroup","Cancer_type","primarySarcomaTest","isSarcoma"],as_index=False).mean(numeric_only=True)
        tr=d[d.relatedGroup.isin(set(meta.loc[training,"relatedGroup"]))].copy();te=d[d.primarySarcomaTest].copy()
        rr={"gene":gene,"outcome":label,"kind":outcome_kind,"trainN":len(tr),"testN":len(te),"trainLineages":tr.Cancer_type.nunique(),"testLineages":te.Cancer_type.nunique(),"unadjustedRNAOutcome":corr(te.rna.to_numpy(),te.outcome.to_numpy()),"unadjustedProteinOutcome":corr(te.protein.to_numpy(),te.outcome.to_numpy())}
        adjusted=te.dropna(subset=["growth"]).copy()
        rr.update({"growthObservedTestN":len(adjusted),"growthObservedTrainN":int(tr.growth.notna().sum()),"growthControl":growth_label,"growthAdjustedLineages":int(adjusted.Cancer_type.nunique()),"growthAdjustmentMissingness":"Complete cases for association; development-only imputation for predictive growth variants","adjustedAssociationInference":"Descriptive residual rank association; nominal Spearman p does not incorporate nuisance-fitting uncertainty"})
        if len(adjusted)>=10 and adjusted.Cancer_type.nunique()>=2:
            x=adjusted[["rna","protein","outcome","growth"]].copy();x=x-x.groupby(adjusted.Cancer_type).transform("mean");ctr=np.column_stack([np.ones(len(x)),x.growth.to_numpy()])
            for col in ["rna","protein","outcome"]:
                values=x[col].to_numpy();x[col]=values-ctr@np.linalg.lstsq(ctr,values,rcond=None)[0]
            rr["withinLineageGrowthAdjustedRNAOutcome"]=corr(x.rna.to_numpy(),x.outcome.to_numpy());rr["withinLineageGrowthAdjustedProteinOutcome"]=corr(x.protein.to_numpy(),x.outcome.to_numpy())
        else:rr["adjustedAssociationStatus"]="Insufficient complete-case measured-growth/lineage support"
        rr["primaryEligible"]=bool(len(tr)>=50 and len(te)>=10 and tr.Cancer_type.nunique()>=3)
        if len(tr)<10 or len(te)<3 or tr.Cancer_type.nunique()<2:
            rr["status"]="insufficient matched support fortransfer";return rr
        predictions={}
        for typ,cols in [("rna",["rna"]),("protein",["protein"]),("both",["rna","protein"]),("rnaGrowth",["rna","growth"]),("proteinGrowth",["protein","growth"])]:
            trainX=tr[cols].to_numpy();testX=te[cols].to_numpy();a=tune(trainX,tr.outcome.to_numpy(),tr.Cancer_type.to_numpy());model=pipeline("ridge",a).fit(trainX,tr.outcome);predictions[typ]=model.predict(testX)
        scale=float(np.quantile(tr.outcome,.75)-np.quantile(tr.outcome,.25));base=float(tr.outcome.median())
        if scale<1e-10:rr["status"]="zero trainingoutcomeIQR";return rr
        errs={k:float(np.abs(te.outcome-p).mean()/scale) for k,p in predictions.items()};errs["trainingMedian"]=float(np.abs(te.outcome-base).mean()/scale)
        rr.update({"status":"evaluated","trainingOutcomeIQR":scale,"testNMAE":errs,"proteinOverRNAImprovement":1-errs["protein"]/errs["rna"] if errs["rna"] else None,"proteinOverRNAGrowthImprovement":1-errs["proteinGrowth"]/errs["rnaGrowth"] if errs["rnaGrowth"] else None})
        idxs=[v.index.to_numpy() for _,v in te.reset_index(drop=True).groupby("Cancer_type")];actual=te.outcome.to_numpy();aa=np.abs(actual-predictions["rna"]);bb=np.abs(actual-predictions["protein"]);boot=[]
        for _ in range(NBOOT):
            ix=np.concatenate([rng.choice(ix,size=len(ix),replace=True) for ix in idxs]);denom=aa[ix].mean()
            if denom>0:boot.append(1-bb[ix].mean()/denom)
        rr["proteinOverRNABootstrapCI95"]=np.quantile(boot,[.025,.975]) if boot else None;return rr
    import raw_crispr_extension
    crispr=raw_crispr_extension.run(meta,rna,prot,training,primary,benchmark)
    secondary.extend(crispr["benchmarks"]);RECEIPTS.extend(crispr["sourceReceipts"])
    for key,d,targets,targettext in selection:
        if "ln_IC50" not in d:continue
        response=numeric(d[["ln_IC50"]]).ln_IC50.groupby(d.model_id).mean();predictors=set(targets)
        if "PRMT5" in targets:predictors|={"MTAP","MAT2A"}
        if "EZH2" in targets:predictors|={"SMARCB1"}
        if predictors&{"BCL2","BCL2L1","MCL1"}:predictors|={"BCL2","BCL2L1","MCL1"}
        for gene in sorted(predictors):
            res=benchmark(gene,response.reindex(meta.index),"GDSC:"+str(key),"ln_IC50");res.update({"drug_id":key[0],"drug_name":key[1],"dataset":key[2],"annotatedTarget":targettext,"sourceAnnotatedTargets":targets,"predictorRole":"cognate" if gene in targets else "frozenbranchproxy","multipleTargets":len(targets)>1,"maxScreeningConcentration":pd.to_numeric(d.get("max_screening_conc",pd.Series()),errors="coerce").max()});secondary.append(res)
    for field in ["unadjustedRNAOutcome","unadjustedProteinOutcome","withinLineageGrowthAdjustedRNAOutcome","withinLineageGrowthAdjustedProteinOutcome"]:
        inds=[i for i,r in enumerate(secondary) if r.get(field,{}).get("p") is not None];qs=fdr([secondary[i][field]["p"] for i in inds])
        for i,q in zip(inds,qs):secondary[i][field]["FDRAcrossFrozenEndpointFamily"]=q
    write("target-outcome-benchmarks.json",secondary);specificity=[];atr_names={"AZD6738","VE-822","VE822","Ceralasertib","AZ20","VX-970","Berzosertib"}
    for dataset,ds in drug.groupby("dataset"):
        matrix=ds.pivot_table(index="model_id",columns=["drug_id","drug_name"],values="ln_IC50",aggfunc="mean");reference=matrix.reindex(meta.index[training]);med=reference.median();sc=reference.quantile(.75)-reference.quantile(.25);z=(matrix-med)/sc.replace(0,np.nan)
        controls=[c for c in matrix.columns if str(c[1]) in {"Paclitaxel","Docetaxel","Olaparib","Talazoparib","Doxorubicin","Cisplatin"}];atrcols=[c for c in matrix.columns if str(c[1]) in atr_names]
        for col in atrcols+controls:
            general=z.drop(columns=[col],errors="ignore").median(axis=1);response=matrix[col];d=pd.concat([response.rename("response"),general.rename("general")],axis=1).join(meta[["Cancer_type","primarySarcomaTest","relatedGroup"]]);d=d[d.primarySarcomaTest.fillna(False)].dropna(subset=["response","general","Cancer_type"]);d=d.groupby(["relatedGroup","Cancer_type"],as_index=False).mean(numeric_only=True)
            fet=d.Cancer_type.str.contains("Ewing|Clear Cell|Clear cell|Myxoid Lipo|Low.grade Fibromyx",case=False,regex=True);growth=growth_for_adjustment;bygroup=growth.groupby(meta.relatedGroup).mean();d["growth"]=bygroup.reindex(d.relatedGroup).values
            res={"drug_id":col[0],"drug_name":col[1],"dataset":dataset,"role":"ATR" if col in atrcols else "frozencomparator","n":len(d),"FETHistologyProxyN":int(fet.sum()),"nonFETHistologyProxyN":int((~fet).sum()),"rawMeanContrast":d.loc[fet,"response"].mean()-d.loc[~fet,"response"].mean(),"groupDefinition":"histologyproxyonly,noverifiedFETcalls"}
            complete=d.dropna(subset=["growth"]).copy();complete_fet=fet.loc[complete.index]
            res.update({"growthControl":growth_label,"growthAdjustedN":len(complete),"growthAdjustedFETProxyN":int(complete_fet.sum()),"growthAdjustedOtherProxyN":int((~complete_fet).sum()),"otherDrugNormalization":"Median/IQR computed in non-sarcoma development only","missingGrowthHandling":"Complete cases, not zero or median fill"})
            if min(int(complete_fet.sum()),int((~complete_fet).sum()))>=5:
                X=np.column_stack([np.ones(len(complete)),complete_fet.astype(float),complete.general,complete.growth]);fit=np.linalg.lstsq(X,complete.response,rcond=None)[0];res["generalSensitivityGrowthAdjustedProxyContrast"]=fit[1];res["coefficientUnits"]="Archived lnIC50; lower means greater sensitivity; descriptive histology-proxy association"
            else:res["adjustedStatus"]="Insufficient measured-growth complete-case group support"
            specificity.append(res)
    write("atr-specificity-controls.json",specificity)
    observed={"metadataMatchedModels":len(ids),"nonSarcomaTrainingModels":int(training.sum()),"primarySarcomaModels":int(primary.sum()),"disputedEMCModelsExcludedPrimary":meta.loc[disputed].reset_index().replace({np.nan:None}).to_dict("records"),"sarcomaClasses":meta.loc[primary].Cancer_type.value_counts().to_dict(),"relatedGroupCollisions":groupcollisions[groupcollisions>1].to_dict(),"crossLineageRelatedFamilies":cross_lineage,"crossLineageHandling":"Ambiguous ACH-000561 family excluded from development and primary analyses; all source relations retained for audit","growthControl":growth_manifest,"coverage":feasibility,"panelPrimary":summary,"secondaryEvaluated":sum(r.get("status")=="evaluated" for r in secondary),"secondaryUnsupported":sum(r.get("status")!="evaluated" for r in secondary),"sourceReceipts":RECEIPTS,"stages":STAGES,"perGeneTransfer":genewise,"secondaryBenchmarks":secondary,"atrSpecificityControls":specificity,"primaryCoverageByLineage":coverage,"drugSourceSchema":source_schema,"processingDisclosure":"Original publishedlog2intensity6692protein; Other-groupMOFA-scaledmeasuredRNA+centeringinterceptonly; globalarchivalprocessingdisclosed. Newimputation/scaling/selectiondevelopmentonly. Wholecellnot surface; noverifiedEMC; Published measured growth used for complete-case controls; RNA proliferation proxy retained only as context; noCNA/dependency/genotype/causalwindowclaim.","frozen":frozen}
    reuse_genes=[g for g in PANEL+CONTROL+TARGETS+proliferation_genes if g in rna.columns]
    reuse={"schema":"frozen-sarcoma-matched-measurements/1","sourceReceipts":RECEIPTS,"seed":SEED,"genes":reuse_genes,"metadata":meta.reset_index().replace({np.nan:None}).to_dict("records"),"rna":rna[reuse_genes].reset_index().replace({np.nan:None}).to_dict("records"),"protein":prot.reset_index().replace({np.nan:None}).to_dict("records"),"processingDisclosure":observed["processingDisclosure"]}
    write("matched-measurements-for-followthrough.json",reuse)
    print("PROTEOMICS_MATCHED_MEASUREMENTS_BEGIN",flush=True);print(json.dumps(safe(reuse),allow_nan=False),flush=True);print("PROTEOMICS_MATCHED_MEASUREMENTS_END",flush=True)
    write("execution-summary.json",observed);stage("completed");print("PROTEOMICS_RESULT_BEGIN",flush=True);print(json.dumps(safe(observed),allow_nan=False),flush=True);print("PROTEOMICS_RESULT_END",flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
        write("failure-receipt.json",{"exception":type(e).__name__,"message":str(e),"stages":STAGES,"sources":RECEIPTS});raise
