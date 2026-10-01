#!/usr/bin/env python3
"""Public metadata retrieval for actual measured-data analyses; no credentials."""
import concurrent.futures, hashlib, json, urllib.request
SOURCES = {
 "protein_manifest":"https://api.figshare.com/v2/articles/19345397",
 "ups_mfs_images":"https://www.ebi.ac.uk/biostudies/api/v1/studies/S-BIAD1555",
 "ewing_images":"https://www.ebi.ac.uk/biostudies/api/v1/studies/S-BIAD1597",
 "pediatric_atlas":"https://zenodo.org/api/records/21292448",
 "hofvander_atlas":"https://zenodo.org/api/records/17866629",
 "methylation_files":"https://ftp.ncbi.nlm.nih.gov/geo/series/GSE140nnn/GSE140686/suppl/",
 "methylation_matrix":"https://ftp.ncbi.nlm.nih.gov/geo/series/GSE140nnn/GSE140686/matrix/",
 "normal_ligands":"https://hla-ligand-atlas.org/rel/2020.12/"
}
def inspect(item):
 name,url=item
 rec={"source":name,"url":url}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Rare-cancers-data-analysis/2"}),timeout=60) as response:
   data=response.read(8*1024*1024+1)
   if len(data)>8*1024*1024: raise ValueError("Metadata exceeds8MiB")
   rec.update(http_status=response.status,final_url=response.url,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
  text=data.decode("utf8")
  try: rec["metadata"]=json.loads(text)
  except json.JSONDecodeError: rec["directory_text"]=text[:60000]
  rec["status"]="retrieved"
 except Exception as error: rec.update(status="failed",error=str(error))
 return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 results=list(pool.map(inspect,SOURCES.items()))
print("EMC_ACCESS_PROBE_BEGIN")
print(json.dumps(results,separators=(",",":")))
print("EMC_ACCESS_PROBE_END")
