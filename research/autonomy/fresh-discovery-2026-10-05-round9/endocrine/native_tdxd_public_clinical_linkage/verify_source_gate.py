#!/usr/bin/env python3
"""Reproduce only source identity/schema/availability; never emit patient outcome cells."""
import argparse,datetime,hashlib,json,re,pathlib,shutil,xml.etree.ElementTree as ET
p=argparse.ArgumentParser()
p.add_argument("--packet",default=str(pathlib.Path(__file__).resolve().parent))
p.add_argument("--primary",default="/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round8/surface_targets/adc_review/source-cache/PMC8292921-BioC.xml")
p.add_argument("--output",required=True)
a=p.parse_args();b=pathlib.Path(a.packet)
def receipt(path):
 x=pathlib.Path(path);raw=x.read_bytes()
 return {"path":str(x),"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
expected={"NCT02564900-official.json":"2fc137ba58ffe64458d7aa9c5520b8c85e570a9ddd668ef7146604406b4dae3d","EMA-official.pdf":"48392101d45d7a12a982ce1ea12bec150eaf2c508a3a095504560cd2f4ff5107","FDA-official.pdf":"00d62cc98b5a795035bede9e40afabc97d833de91cb734b92a0b925cb67f670d","PMDA-official.pdf":"12c0cdcf11e81edcf2243a20864746900e4e015e2670ce9b6f88ef6dcfee5000"}
rs=[receipt(b/"raw-cache"/k) for k in expected]
for rr in rs:
 assert rr["sha256"]==expected[pathlib.Path(rr["path"]).name],rr["path"]
primary=receipt(a.primary)
assert primary["sha256"]=="57713e89b601f89d257fbdfa62912e53d116c9cf190093d1fed278ccb0851c9e"
r=ET.parse(a.primary).getroot()
registration=[]
for x in r.findall(".//passage"):
 section=next((i.text for i in x.findall("infon") if i.get("key")=="section_type"),None)
 if section!="METHODS":continue
 t=x.findtext("text") or ""
 for clause in re.split(r"(?<=[.!?])\s+",t):
  if "NCT02564900" in clause:registration.append(clause)
assert len(registration)==1 and "152978" in registration[0]
d=json.loads((b/"raw-cache/NCT02564900-official.json").read_text())
assert d["protocolSection"]["identificationModule"]["nctId"]=="NCT02564900"
assert d["protocolSection"]["identificationModule"]["orgStudyIdInfo"]["id"]=="DS8201-A-J101"
emc=[];ids=[]
def inspect(x,path=""):
 if isinstance(x,dict):
  for k,v in x.items():
   q=path+"/"+k
   if re.search(r"(patient|participant|subject).*(id|number)|^(subjectId|patientId|participantId)$",k,re.I):ids.append(q)
   if isinstance(v,str) and re.search("extraskeletal|chondrosarcoma",v,re.I):emc.append(q)
   elif isinstance(v,(dict,list)):inspect(v,q)
 elif isinstance(x,list):
  for i,v in enumerate(x):inspect(v,path+"/"+str(i))
inspect(d)
assert len(emc)==14 and all(x.endswith("/description") for x in emc)
assert not ids
measures=d["resultsSection"]["outcomeMeasuresModule"]["outcomeMeasures"]
assert len(measures)==12
assert all(g["title"].startswith("Dose ") for m in measures for g in m.get("groups",[]))
ipd=d["protocolSection"]["ipdSharingStatementModule"]
assert ipd["ipdSharing"]=="YES" and "request" in ipd["description"].lower() and "CSR" in ipd["infoTypes"]
report_terms={}
for n in ["EMA","FDA","PMDA"]:
 tx=(b/f"raw-cache/{n}-official-text.txt").read_text()
 report_terms[n]={term:len(re.findall(term,tx,re.I)) for term in ["extraskeletal","myxoide? chondrosarcoma","chondrosarcoma","骨外性","粘液型軟骨肉腫"]}
 assert all(v==0 for v in report_terms[n].values())
out={"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"PASS","scope":"four exact new official primary receipts plus retained article study registration, all registry result schema and disease mention paths; exact regulatory text identity audit, not full manuscript/figure/case review","primary":primary,"official_source_receipts":rs,"primary_registration":registration,"registry_EMC_description_occurrences":len(emc),"unique_native_EMC_cases_supported_by_description":1,"occurrences_are_not_donors":True,"registry_patient_identifier_key_paths":ids,"registry_result_measure_count":len(measures),"all_results_arm_group_level":True,"IPD_CSR_request_only":True,"regulatory_text_native_identity_term_counts":report_terms,"native_patient_assay_response_values_emitted":0,"numerical_empirical_analysis":None,"absence_of_tokens_is_not_absence_of_case":True,"free_bytes":shutil.disk_usage(b).free}
pathlib.Path(a.output).write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps({"status":"PASS","registry_measures":len(measures),"description_mentions":len(emc),"case_values_emitted":0}))

