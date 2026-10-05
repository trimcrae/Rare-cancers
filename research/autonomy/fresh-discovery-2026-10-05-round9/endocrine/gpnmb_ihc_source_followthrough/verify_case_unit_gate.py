#!/usr/bin/env python3
"""Verify exact cached source identity/Methods case units; no outcome cells emitted."""
import argparse,datetime,hashlib,json,pathlib,re,shutil,xml.etree.ElementTree as ET
p=argparse.ArgumentParser()
p.add_argument("--packet",default=str(pathlib.Path(__file__).resolve().parent))
p.add_argument("--pubmed-uterine",default="/workspace/emc-r6-fapi_broader/research/autonomy/fresh-discovery-2026-10-05-round9/functional_new/gpnmb_claim_omission_refresh/raw-cache/two-new-IHC-PubMed-metadata.source")
p.add_argument("--pubmed-ofmt",default="/workspace/emc-r6-fapi_broader/research/autonomy/fresh-discovery-2026-10-05-round9/functional_new/gpnmb_claim_omission_refresh/raw-cache/OFMT-PubMed.source")
p.add_argument("--prior-core",default=str(pathlib.Path(__file__).resolve().parent.parent/"gpnmb_primary_measurement_gate/raw-cache/gpnmb_pathology2025_core.json"))
p.add_argument("--output",required=True)
a=p.parse_args();b=pathlib.Path(a.packet)
checks=[(a.pubmed_uterine,"0bc11b9aeb1c7c109522a08bdf6ea47f38f282711cc46c4ca1a3d2a57e2ead4b"),(a.pubmed_ofmt,"b0e64602e6cdf09a9785692cd925fe0a6d3f5aa4609cd27daa2dac7412080f9f"),(a.prior_core,"f4efda2f41145f32fc59d92760cf4353b19efbc8be76ba023cd137d48b4599e2")]
for f,h in checks:assert hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()==h,f
def article(f,pmid):
 return next(x for x in ET.parse(f).getroot().findall("PubmedArticle") if x.findtext("./MedlineCitation/PMID")==pmid)
def methods(x):
 return " ".join("".join(z.itertext()) for z in x.findall("./MedlineCitation/Article/Abstract/AbstractText") if "METHOD" in (z.get("Label") or z.get("NlmCategory") or "").upper())
u=article(a.pubmed_uterine,"42791032");m=methods(u)
assert "115 uterine mesenchymal tumours" in m
assert re.search(r"nine PEComas",m,re.I)
counts={"PEComa":9}
for k in ["LMS","STUMP","leiomyoma","LG ESS","HG ESS","adenosarcoma","UUS","IMT"]:
 match=re.search(r"\b"+re.escape(k)+r"\s*[,\(\s]*n\s*=\s*(\d+)",m)
 assert match,k
 counts[k]=int(match.group(1))
for k in ["UTROSCT","KAT6B/A::KANSL1","PLAG1","NTRK"]:
 match=re.search(r"(\d+)\s+"+re.escape(k),m)
 assert match,k
 counts[k]=int(match.group(1))
assert sum(counts.values())==115
assert counts["UUS"]==5 and sum(counts[k] for k in ["UTROSCT","KAT6B/A::KANSL1","PLAG1","NTRK"])==7
assert ">75%" in m and "moderate to strong intensity" in m
o=article(a.pubmed_ofmt,"40189028");om=methods(o)
ot="".join(o.find("./MedlineCitation/Article/ArticleTitle").itertext())
assert "13 TFE3-rearranged mesenchymal tumors" in ot
assert "whole-slide" in om and "H-scores" in om
old=json.loads(pathlib.Path(a.prior_core).read_text())["resultList"]["result"][0]
abstract=old.get("abstractText",old.get("abstractString",""))
assert "934 cases" in abstract and "Johns Hopkins" in abstract
access=json.loads((b/"DECLARED-PRIMARY-ACCESS.json").read_text())
assert len(access)==2
assert access[0]["status"]==403 and "403" in access[1]["error"]
assert (b/"raw-cache/uterine42791032-canonical-primary.response").stat().st_size==6180
assert hashlib.sha256((b/"raw-cache/uterine42791032-canonical-primary.response").read_bytes()).hexdigest()=="da4eb19c0dbae92823b94e15905c1bc3a37739b9ee6a1ff1136c1261e2d81bac"
out={"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"PASS source-receipt and case-unit checks only","cases115_by_source_category":counts,"cases115_total":sum(counts.values()),"identity_pending_UUS_plus_rare":12,"study13_total_not_OFMT_denominator":True,"OFMT_subgroup_count":None,"cases934_not_donors":True,"new_requests":2,"actual_denial_stops":True,"new_native_GPNMB_metric_cells_emitted":0,"native_case_counts":None,"source_original_hashes_pass":True,"no_ordinal_RNA_pooling":True,"free_bytes":shutil.disk_usage(b).free,"limits":"No whole-body/native case identity closure, no IHC or RNA estimate, no clone/compartment assumptions."}
pathlib.Path(a.output).write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps({"status":"PASS","cases115":sum(counts.values()),"identity_pending":12,"stain_metrics_emitted":0}))
