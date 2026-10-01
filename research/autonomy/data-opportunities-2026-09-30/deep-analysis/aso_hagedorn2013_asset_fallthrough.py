import concurrent.futures,hashlib,json,subprocess,urllib.request,shutil,io
from datetime import datetime,timezone
from pathlib import Path
BASE=Path(__file__).resolve().parents[4];OUT=BASE/"campaign-output/hagedorn2013-bounded-asset-fallthrough";OUT.mkdir(parents=True,exist_ok=True)
FILES=["Supp_Table1.pdf","Supp_Fig1.pdf","Supp_Table2.pdf","Supp_Table3.pdf","Supp_Table4.pdf","Supp_Table5.pdf","Supp_Table6.pdf"]
HOSTS=[("canonical_PMC","https://pmc.ncbi.nlm.nih.gov/articles/PMC3760025/bin/"),("legacy_NCBI","https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3760025/bin/"),("EuropePMC_public_article","https://europepmc.org/articles/PMC3760025/bin/")]
def inspect(filename):
 attempts=[];document=None
 for route,prefix in HOSTS:
  url=prefix+filename
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Rare-cancers-public-primary-data-audit","Accept":"application/pdf"}),timeout=45) as response:raw=response.read();status=response.status;mime=response.headers.get("Content-Type");final_url=response.url
   receipt={"url":url,"route":route,"status":status,"final_url":final_url,"content_type":mime,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"qualified_PDF":raw.startswith(b"%PDF")};(OUT/(route+"-"+filename)).write_bytes(raw)
   if not raw.startswith(b"%PDF"):receipt["non_PDF_response_prefix"]=raw[:800].decode("utf-8","replace")
   attempts.append(receipt)
   if raw.startswith(b"%PDF"):
    path=OUT/(route+"-"+filename);text=path.with_suffix(".txt")
    if shutil.which("pdftotext"):subprocess.run(["pdftotext","-layout",str(path),str(text)],check=True);literal=text.read_text()
    else:
     from pypdf import PdfReader
     literal="\f".join(p.extract_text(extraction_mode="layout") or "" for p in PdfReader(io.BytesIO(raw)).pages);text.write_text(literal)
    document={"filename":filename,"receipt":receipt,"complete_text":literal,"pages":literal.count("\f"),"endpoint_qualification":"Literal published sequence/chemistry/toxicity table; no inferred measured Tm."};break
  except Exception as exc:attempts.append({"url":url,"route":route,"error_type":type(exc).__name__,"error":str(exc),"status":getattr(exc,"code",None)})
 return {"literal_filename":filename,"attempts":attempts,"qualified_document":document}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(inspect,FILES))
output={"schema":"exact-Hagedorn2013-seven-assets-bounded-public-fallthrough/1","executed_utc":datetime.now(timezone.utc).isoformat(),"primary_identity":{"PMID":"23952551","PMCID":"PMC3760025","DOI":"10.1089/nat.2013.0436"},"verified_asset_inventory_source":{"run_id":36921168639,"job_id":110567359946,"original_HTML_sha256":"321e2baa5ef304351a867592f3cb4337e7b2ad368c5d23ce1ec94cc616550a4c"},"filename_results":results,"qualified_PDF_count":sum(x["qualified_document"] is not None for x in results),"limits":["Three bounded public URL layouts for seven literal filenames; no guessed filenames, fragment/main-page copies or authentication bypass.","Non-PDF and error responses are access receipts, not measured rows or assay negatives.","206 development and23 validation oligos are distinct reported2013 cohorts;236 cited elsewhere is not assumed to have acquired rows.","Do not infer modified-duplex Tm from toxicity endpoints."]}
(OUT/"exact-seven-assets-bounded-fallthrough.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n");print("ASO2013_SEVEN_ASSET_FALLTHROUGH_BEGIN");print(json.dumps(output,ensure_ascii=False));print("ASO2013_SEVEN_ASSET_FALLTHROUGH_END")
