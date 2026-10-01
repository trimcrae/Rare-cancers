import base64,csv,hashlib,json,math,re,sys
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
REV="dca75cb3f32b82d54a6f78bf0a6323e5b975aca1";LFS="https://nsssw8k94d.execute-api.us-east-1.amazonaws.com/objects/batch";CAP=64*1024*1024
OUT={"schema":"emc-foundation-public-reanalysis/1","sourceRevision":REV,"startedUtc":datetime.now(timezone.utc).isoformat(),"sources":[],"errors":[]}
def get(url,data=None,headers=None):
    h={"User-Agent":"Rare-cancers-public-reanalysis","Accept":"*/*"};h.update(headers or {})
    with urlopen(Request(url,data=data,headers=h),timeout=60) as r:
        if r.headers.get("Content-Length") and int(r.headers["Content-Length"])>CAP:raise ValueError("file cap exceeded")
        b=r.read(CAP+1)
    if len(b)>CAP:raise ValueError("file cap exceeded")
    return b
def source(name):
    item=json.loads(get("https://api.github.com/repos/cBioPortal/datahub/contents/public/sarcoma_msk_2022/"+name+"?ref="+REV));sha=item["sha"];pointer=base64.b64decode(json.loads(get("https://api.github.com/repos/cBioPortal/datahub/git/blobs/"+sha))["content"])
    if hashlib.sha1(b"blob "+str(len(pointer)).encode()+b"\0"+pointer).hexdigest()!=sha:raise ValueError("Git blob mismatch")
    receipt={"file":name,"blobSha":sha,"pointerBytes":len(pointer)}
    if pointer.startswith(b"version https://git-lfs.github.com/spec/v1"):
        text=pointer.decode();oid=re.search(r"oid sha256:([0-9a-f]{64})",text).group(1);n=int(re.search(r"size ([0-9]+)",text).group(1))
        if n>CAP:raise ValueError("file cap exceeded")
        batch=json.loads(get(LFS,json.dumps({"operation":"download","transfers":["basic"],"objects":[{"oid":oid,"size":n}]}).encode(),{"Content-Type":"application/vnd.git-lfs+json","Accept":"application/vnd.git-lfs+json"}));item=batch["objects"][0]
        if item.get("error"):raise ValueError("public LFS rejected "+name)
        action=item["actions"]["download"];b=get(action["href"],headers=action.get("header",{}))
        if len(b)!=n or hashlib.sha256(b).hexdigest()!=oid:raise ValueError("LFS size/hash mismatch")
        receipt.update({"bytes":n,"sha256":oid,"verifiedLfs":True})
    else:b=pointer;receipt.update({"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"verifiedLfs":None})
    OUT["sources"].append(receipt);return b.decode("utf-8-sig")
def table(t):return list(csv.DictReader((x for x in t.splitlines() if x and not x.startswith("#")),delimiter="\t"))
def missing(v):return v is None or str(v).strip().casefold() in ("","na","n/a","nan","null","unknown","not available")
def sid(r):
    for k in ("SAMPLE_ID","Sample_ID","Sample_Id","Tumor_Sample_Barcode","Tumor_Sample_ID","sampleId","Sample"):
        if not missing(r.get(k)):return r[k]
    return None
def pid(r):return r.get("PATIENT_ID") or r.get("Patient_ID")
def emc(r):return r.get("ONCOTREE_CODE","").upper()=="EMCS" or any(str(v).strip().casefold()=="extraskeletal myxoid chondrosarcoma" for v in r.values())
def wilson(k,n):
    if not n:return None
    z=1.959963984540054;p=k/n;den=1+z*z/n;center=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return {"k":k,"n":n,"fraction":p,"wilson95":[max(0,center-half),min(1,center+half)]}
def fuse_genes(r):return {str(r[k]).upper() for k in r if re.search(r"(Hugo|Gene_Symbol|Gene[12]$|gene[12]$|Site[12]_Gene)",k,re.I) and not missing(r[k])}
try:
    OUT["readme"]=source("README.md");samples=table(source("data_clinical_sample.txt"));patients=table(source("data_clinical_patient.txt"));selected=[r for r in samples if emc(r)];ids={sid(r) for r in selected if sid(r)};pids={pid(r) for r in selected if pid(r)}
    OUT.update({"allSampleRows":len(samples),"allPatientRows":len(patients),"sampleColumns":list(samples[0]) if samples else [],"patientColumns":list(patients[0]) if patients else [],"emcSampleRows":len(selected),"emcUniqueSamples":len(ids),"emcUniquePatients":len(pids),"emcDuplicateSampleIds":len(selected)-len(ids),"emcSampleRowsLiteral":selected,"emcPatientRowsLiteral":[r for r in patients if pid(r) in pids]});OUT["emcSamplesPerPatientHistogram"]=dict(Counter(Counter(pid(r) for r in selected).values()));clinical=[]
    for scope,rows in (("sample",selected),("patient",OUT["emcPatientRowsLiteral"])):
        for k in (list(rows[0]) if rows else []):
            values=[str(r.get(k)) for r in rows if not missing(r.get(k))]
            if any(w in k.upper() for w in ("OS","PFS","DFS","SURV","STATUS","FOLLOW","DEATH","AGE","SEX","STAGE","METAST","GRADE","SITE","PURITY","PANEL","TMB","MSI")):clinical.append({"scope":scope,"field":k,"nonmissingRows":len(values),"uniqueValues":dict(Counter(values)) if len(set(values))<=50 else {"count":len(set(values))}})
    OUT["clinicalCoverage"]=clinical;mutations=table(source("data_mutations.txt"));sv=table(source("data_sv.txt"));mts=[r for r in mutations if sid(r) in ids];svs=[r for r in sv if sid(r) in ids]
    OUT.update({"allMutationRows":len(mutations),"mutationColumns":list(mutations[0]) if mutations else [],"emcMutationRowsLiteral":mts,"allSvRows":len(sv),"svColumns":list(sv[0]) if sv else [],"emcSvRowsLiteral":svs});mapping={sid(r):pid(r) for r in selected};partners=defaultdict(set);nrrows=[]
    for r in svs:
        g=fuse_genes(r)
        if "NR4A3" in g:nrrows.append(r);partners[sid(r)].update(g-{"NR4A3"})
    OUT["nr4a3RowsLiteral"]=nrrows;OUT["explicitNr4a3PartnersBySample"]={k:sorted(v) for k,v in sorted(partners.items())};ppartner=defaultdict(set)
    for k,v in partners.items():ppartner[mapping.get(k)].update(v)
    OUT["explicitNr4a3PartnersByPatient"]={str(k):sorted(v) for k,v in sorted(ppartner.items(),key=lambda x:str(x[0]))};gene_samples=defaultdict(set);gene_patients=defaultdict(set)
    for r in mts:
        g=r.get("Hugo_Symbol")
        if g:gene_samples[g].add(sid(r));gene_patients[g].add(mapping.get(sid(r)))
    OUT["emcObservedMutationFrequency"]=[{"gene":g,"samples":len(gene_samples[g]),"patients":len(gene_patients[g]),"nominalAllEmcPatientFraction":wilson(len(gene_patients[g]),len(pids)),"denominatorCaveat":"Panel coverage and mutation filtering must be checked; not automatically callable prevalence."} for g in sorted(gene_patients,key=lambda g:(-len(gene_patients[g]),g))];OUT["panelLiteral"]=source("data_gene_panel_FoundationOne_476.txt");pmat=table(source("data_gene_panel_matrix.txt"));OUT["panelMatrixColumns"]=list(pmat[0]) if pmat else [];OUT["emcPanelMatrixLiteral"]=[r for r in pmat if sid(r) in ids]
    OUT["interpretationLimits"]=["Foundation Medicine profiling; study name does not mean MSK-IMPACT.","CNA is pending from the author in the pinned README; absent CNA export is not absence of copy-number alterations.","Diagnostic labels alone are not individual molecular verification.","Literal NR4A3 gene-pair rows are interpreted separately from other SV descriptions.","No survival/treatment/causal efficacy analysis is valid without verified endpoints, time origins, clinical covariates and representative sampling."]
except Exception as e:OUT["errors"].append({"type":type(e).__name__,"message":str(e)})
OUT["finishedUtc"]=datetime.now(timezone.utc).isoformat();Path("campaign-output").mkdir(exist_ok=True);Path("campaign-output/clinical-foundation-reanalysis.json").write_text(json.dumps(OUT,indent=2)+"\n");print("EMC_CLINICAL_RESULT_BEGIN");print(json.dumps(OUT,separators=(",",":")));print("EMC_CLINICAL_RESULT_END")
if OUT["errors"]:sys.exit(1)
