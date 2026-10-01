"""Bounded public-source retrieval for the EMC data-opportunity campaign.
No credentials, secrets, paid APIs or clinical treatment decisions.
This exploratory retrieval preserves literal source fields; it does not infer
HLA loss, allele presentation or molecular diagnosis from missing values.
"""
import base64, csv, hashlib, io, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

REV = "dca75cb3f32b82d54a6f78bf0a6323e5b975aca1"
ROOT = "https://raw.githubusercontent.com/cBioPortal/datahub/" + REV + "/public/msk_impact_50k_2026/"
LFS_ENDPOINT = "https://nsssw8k94d.execute-api.us-east-1.amazonaws.com/objects/batch"
POINTERS = {
 "data_clinical_sample.txt":"968a9ffaf8ee3e1c7eb0c52b908d8153676433ce",
 "data_clinical_patient.txt":"b9f87799e889ea10600b8f25cc05dd3f0856640a",
 "data_hla_loh.txt":"2af6d43abd0f4ebfd59d15ab9eaf2f7d4be083a0"
}
LIMIT = 64 * 1024 * 1024
result = {"schema":"emc-public-source-retrieval/1","started_utc":datetime.now(timezone.utc).isoformat(),
 "source_revision":REV,"sources":[],"errors":[],
 "scope":"Exploratory source retrieval. Exact diagnostic labels define the subset. No clinical efficacy, antigen presentation, genotype imputation or loss-of-heterozygosity interpretation."}
def download(url, payload=None, extra_headers=None):
    headers={"User-Agent":"EMC-public-secondary-analysis/1"}
    headers.update(extra_headers or {})
    request = Request(url, data=payload, headers=headers)
    with urlopen(request, timeout=90) as response:
        declared=response.headers.get("Content-Length")
        if declared and int(declared)>LIMIT: raise ValueError("source exceeds 64 MiB cap")
        data=response.read(LIMIT+1)
        if len(data)>LIMIT: raise ValueError("source exceeds 64 MiB cap")
    return data
def source(name):
    blob_url="https://api.github.com/repos/cBioPortal/datahub/git/blobs/"+POINTERS[name] if name in POINTERS else None
    pointer=base64.b64decode(json.loads(download(blob_url))["content"]) if blob_url else download(ROOT+name)
    if pointer.startswith(b"version https://git-lfs.github.com/spec/v1"):
        text=pointer.decode("utf-8")
        expected=re.search(r"oid sha256:([0-9a-f]{64})",text).group(1)
        expected_size=int(re.search(r"size ([0-9]+)",text).group(1))
        if expected_size>LIMIT: raise ValueError("LFS source exceeds 64 MiB cap")
        batch=json.loads(download(LFS_ENDPOINT,json.dumps({"operation":"download","transfers":["basic"],"objects":[{"oid":expected,"size":expected_size}]}).encode(),{"Content-Type":"application/vnd.git-lfs+json","Accept":"application/vnd.git-lfs+json"}))
        obj=batch["objects"][0]
        if obj.get("error"): raise ValueError("Public LFS download batch rejected object: "+str(obj["error"].get("message")))
        action=obj["actions"]["download"]
        data=download(action["href"],extra_headers=action.get("header",{}))
        if hashlib.sha256(data).hexdigest()!=expected or len(data)!=expected_size:
            raise ValueError("LFS source hash/size mismatch: "+name)
        result["sources"].append({"file":name,"pointer_url":blob_url,"download_protocol":"custom public LFS basic download","bytes":len(data),
          "sha256":expected,"lfs_hash_and_size_verified":True})
    else:
        data=pointer
        result["sources"].append({"file":name,"url":ROOT+name,"bytes":len(data),
          "sha256":hashlib.sha256(data).hexdigest(),"lfs_hash_and_size_verified":None})
    return data.decode("utf-8-sig")
def table(text):
    return list(csv.DictReader((line for line in text.splitlines() if line and not line.startswith("#")),delimiter="\t"))
def exact_emc(row):
    labels=[str(v).strip().casefold() for v in row.values()]
    return "extraskeletal myxoid chondrosarcoma" in labels or str(row.get("ONCOTREE_CODE","")).strip()=="EMCS"
try:
    study=source("meta_study.txt")
    result["study_metadata"]=study
    samples=table(source("data_clinical_sample.txt"))
    targets=[r for r in samples if exact_emc(r)]
    result["sample_table_rows"]=len(samples)
    result["sample_columns"]=list(samples[0]) if samples else []
    result["diagnostically_labelled_emc_rows"]=len(targets)
    sample_ids={r.get("SAMPLE_ID") for r in targets if r.get("SAMPLE_ID")}
    patient_ids={r.get("PATIENT_ID") for r in targets if r.get("PATIENT_ID")}
    result["unique_sample_ids"]=len(sample_ids)
    result["unique_patient_ids"]=len(patient_ids)
    fields=[k for k in result["sample_columns"] if any(t in k.upper() for t in ["HLA","CANCER","ONCOTREE","SAMPLE_ID","PATIENT_ID","SAMPLE_TYPE","PRIMARY","METAST","FACETS","PURITY","COVERAGE","GENE_PANEL"])]
    result["selected_sample_fields"]=[{k:r.get(k) for k in fields} for r in targets]
    patients=table(source("data_clinical_patient.txt"))
    result["patient_columns"]=list(patients[0]) if patients else []
    patient_fields=[k for k in result["patient_columns"] if k=="PATIENT_ID" or "HLA" in k.upper()]
    matched=[r for r in patients if r.get("PATIENT_ID") in patient_ids]
    result["matched_patient_rows"]=len(matched)
    result["selected_patient_hla_fields"]=[{k:r.get(k) for k in patient_fields} for r in matched]
    result["hla_profile_metadata"]=source("meta_hla_loh.txt")
    matrix=source("data_hla_loh.txt")
    reader=csv.reader((line for line in matrix.splitlines() if line and not line.startswith("#")),delimiter="\t")
    header=next(reader)
    selected=[i for i,v in enumerate(header) if v in sample_ids]
    leading=[i for i,v in enumerate(header) if v in ("ENTITY_STABLE_ID","HLA_GENE")]
    result["hla_matrix_header_prefix"]=header[:6]
    result["hla_matrix_matching_columns"]=[header[i] for i in selected]
    rows=[]
    for row in reader:
        rows.append({header[i]:row[i] if i<len(row) else None for i in leading+selected})
    result["hla_matrix_rows"]=len(rows)
    result["selected_hla_matrix_literal_cells"]=rows
    result["uninterpreted_hla_cell_vocabulary"]=sorted({str(row.get(header[i])) for row in rows for i in selected})
except Exception as error:
    result["errors"].append({"type":type(error).__name__,"message":str(error)})
result["finished_utc"]=datetime.now(timezone.utc).isoformat()
out=Path("campaign-output")
out.mkdir(exist_ok=True)
(out/"public-source-retrieval.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print("EMC_CAMPAIGN_RESULT_BEGIN")
print(json.dumps(result,separators=(",",":")))
print("EMC_CAMPAIGN_RESULT_END")
if result["errors"]: sys.exit(1)
