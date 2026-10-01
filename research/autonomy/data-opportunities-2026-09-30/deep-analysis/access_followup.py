#!/usr/bin/env python3
import concurrent.futures,gzip,hashlib,json,pathlib,urllib.request
OUT=pathlib.Path("deep-output/access-followup");OUT.mkdir(parents=True,exist_ok=True)
def get(url,cap=8388608):
 with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Rare-cancers-public-analysis/2"}),timeout=90) as r:
  b=r.read(cap+1)
  if len(b)>cap:raise ValueError("response cap")
 return b
urls={
 "biostudies1555_filelist":"https://www.ebi.ac.uk/biostudies/files/S-BIAD1555/IMC/Files_list_STS.json",
 "biostudies1555_api_files":"https://www.ebi.ac.uk/biostudies/api/v1/files/S-BIAD1555/IMC/Files_list_STS.json",
 "biostudies1597_panel1":"https://www.ebi.ac.uk/biostudies/files/S-BIAD1597/EWS_Opal/Panel1.json",
 "biostudies1597_panel2":"https://www.ebi.ac.uk/biostudies/files/S-BIAD1597/EWS_Opal/Panel2.json",
 "biostudies1597_panel3":"https://www.ebi.ac.uk/biostudies/files/S-BIAD1597/EWS_Opal/Panel3.json",
 "protein_readme":"https://ndownloader.figshare.com/files/36155439",
 "protein_mapping":"https://ndownloader.figshare.com/files/34411133",
 "cmp_models":"https://cog.sanger.ac.uk/cmp/download/model_list_20210719.csv",
 "proteomics_primary":"https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9387775/fullTextXML",
 "bangerter_primary":"https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9813045/fullTextXML",
 "hla_primary":"https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8054196/fullTextXML",
 "iwata_primary":"https://link.springer.com/article/10.1007/s13577-025-01250-7",
 "hla_pride_files":"https://www.ebi.ac.uk/pride/ws/archive/v2/files/byProject?accession=PXD019643&pageSize=100&page=0"}
def probe(item):
 name,url=item;r={"name":name,"url":url}
 try:
  b=get(url);(OUT/(name+".source")).write_bytes(b);r.update(status="retrieved",bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  s=b.decode("utf8")
  if name.endswith("primary") and s.lstrip().startswith("<?xml"):
   import xml.etree.ElementTree as E,re
   root=E.fromstring(s);r["primary_paragraphs"]=[" ".join("".join(p.itertext()).split()) for p in root.findall(".//body//p") if re.search("RNA|protein|data|avail|GSE|search|Swiss|off.target|concentrat|replicate|dose", "".join(p.itertext()),re.I)]
   r["supplement_links"]=[e.attrib for e in root.iter() if e.tag in ("media","supplementary-material","ext-link")]
  elif name=="cmp_models":
   import pandas as pd,io
   d=pd.read_csv(io.BytesIO(b));r.update(columns=d.columns.tolist(),rows=len(d),first_rows=d.head(3).fillna("").to_dict("records"))
   for c in d.columns:
    if "cancer" in c.lower() or "tissue" in c.lower():r.setdefault("class_counts",{})[c]=d[c].fillna("").value_counts().to_dict()
  else:
   try:r["metadata"]=json.loads(s)
   except json.JSONDecodeError:r["text"]=s[:200000] if name in ("protein_readme","protein_mapping") else s[:10000]
 except Exception as e:r.update(status="error",error=repr(e))
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:result=list(ex.map(probe,urls.items()))
hdf={"name":"multiomics_hdf5","url":"https://ndownloader.figshare.com/files/34411016"}
try:
 p=OUT/"MultiOmics_DIANN.hdf5";h=hashlib.md5();s=hashlib.sha256();n=0
 with urllib.request.urlopen(hdf["url"],timeout=120) as r,p.open("wb") as f:
  while True:
   b=r.read(1024*1024)
   if not b:break
   n+=len(b)
   if n>246459733:raise ValueError("oversized HDF5")
   h.update(b);s.update(b);f.write(b)
 assert n==246459733 and h.hexdigest()=="eff4e877573f81601c0c3048ea4362e2","HDF5 pin mismatch"
 import h5py,numpy as np
 datasets=[]
 with h5py.File(p,"r") as f:
  def visit(name,obj):
   if isinstance(obj,h5py.Dataset):
    row={"path":name,"shape":list(obj.shape),"dtype":str(obj.dtype)}
    if obj.ndim==1:row["first_values"]=[v.decode() if isinstance(v,bytes) else str(v) for v in obj[:12]]
    datasets.append(row)
  f.visititems(visit)
 hdf.update(status="retrieved",bytes=n,md5=h.hexdigest(),sha256=s.hexdigest(),datasets=datasets)
 try:
  import pandas as pd
  with pd.HDFStore(p,"r") as f:hdf["pandas_keys"]=f.keys()
 except Exception as e:hdf["pandas_inspection_error"]=repr(e)
except Exception as e:hdf.update(status="error",error=repr(e))
result.append(hdf)
(OUT/"results.json").write_text(json.dumps(result,indent=2)+"\n")
print("EMC_ACCESS_FOLLOWUP_BEGIN");print(json.dumps(result,separators=(",",":")));print("EMC_ACCESS_FOLLOWUP_END")
