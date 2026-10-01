#!/usr/bin/env python3
import csv,hashlib,io,json,re,subprocess,urllib.parse,urllib.request,zipfile,xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
BASE=Path(__file__).resolve().parents[4]
OUT=BASE/"campaign-output/hagedorn2013-HTML-inspection";OUT.mkdir(parents=True,exist_ok=True)
EXPECTED="321e2baa5ef304351a867592f3cb4337e7b2ad368c5d23ce1ec94cc616550a4c"
paths=list(BASE.rglob("7e762e9767-indexed-000.html"));matched=[p for p in paths if hashlib.sha256(p.read_bytes()).hexdigest()==EXPECTED]
if not matched:raise FileNotFoundError("Restore exact ASO artifact11189519672 from run36917071796; do not treat #SD pages as supplements")
source=matched[0];raw=source.read_bytes()
class Node:
 def __init__(self,tag,attrs,parent=None):self.tag=tag;self.attrs=dict(attrs);self.parent=parent;self.children=[]
 def walk(self):
  yield self
  for c in self.children:
   if isinstance(c,Node):yield from c.walk()
 def text(self):return re.sub(r"\s+"," "," ".join(c.text() if isinstance(c,Node) else c for c in self.children)).strip()
class Parser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.root=Node("ROOT",[]);self.cur=self.root
 def handle_starttag(self,tag,attrs):
  n=Node(tag,attrs,self.cur);self.cur.children.append(n)
  if tag not in {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}:self.cur=n
 def handle_startendtag(self,tag,attrs):self.cur.children.append(Node(tag,attrs,self.cur))
 def handle_endtag(self,tag):
  n=self.cur
  while n.parent is not None:
   if n.tag==tag:self.cur=n.parent;return
   n=n.parent
 def handle_data(self,text):self.cur.children.append(text)
p=Parser();p.feed(raw.decode());nodes=list(p.root.walk())
def nearest_supp(n):
 while n.parent is not None:
  if re.match(r"^SD\d",n.attrs.get("id","")) or re.search(r"supplement|supporting",n.attrs.get("class",""),re.I):return n
  n=n.parent
 return None
tables=[]
for n in nodes:
 if n.tag!="table":continue
 rows=[]
 for tr in n.walk():
  if tr.tag!="tr":continue
  cells=[c.text() for c in tr.children if isinstance(c,Node) and c.tag in {"td","th"}]
  if cells:rows.append(cells)
 wrap=n.parent
 while wrap.parent is not None and not ("table" in wrap.attrs.get("class","") or wrap.attrs.get("id","").startswith("T")):wrap=wrap.parent
 tables.append({"id":n.attrs.get("id"),"parent_id":wrap.attrs.get("id"),"caption_context":wrap.text()[:1500],"rows":rows})
sections=[{"id":n.attrs.get("id"),"text":n.text(),"hrefs":[x.attrs.get("href") for x in n.walk() if x.tag=="a" and x.attrs.get("href")]} for n in nodes if re.match(r"^SD\d",n.attrs.get("id",""))]
all_assets=[];selected={};base_url="https://pmc.ncbi.nlm.nih.gov/articles/PMC3760025/"
for n in nodes:
 if n.tag!="a" or not n.attrs.get("href"):continue
 href=n.attrs["href"];url=urllib.parse.urljoin(base_url,href);label=n.text();supp=nearest_supp(n)
 is_data_file=bool(re.search(r"\.(?:pdf|xlsx?|csv|tsv|txt|docx?|zip)(?:[?#]|$)",href,re.I));is_supp_link=bool(re.search(r"supplement|supporting|suppl",label+" "+href,re.I))
 if not (is_data_file or "/bin/" in href or is_supp_link):continue
 row={"literal_href":href,"resolved_url":url,"label":label,"supplement_section":supp.attrs.get("id") if supp else None};all_assets.append(row)
 if not urllib.parse.urlsplit(url).fragment and (is_data_file or is_supp_link) and (supp is not None or is_supp_link or "/bin/" in href):selected[url]=row
attempts=[];documents=[]
for i,(url,context) in enumerate(sorted(selected.items())):
 if i>=20:raise ValueError("Unexpectedly broad supplement inventory")
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Rare-cancers-primary-source-audit"}),timeout=90) as f:body=f.read();mime=f.headers.get("Content-Type")
  name=Path(urllib.parse.urlsplit(url).path).name or "asset";path=OUT/(str(i)+"-"+name);path.write_bytes(body);receipt={"url":url,"mime":mime,"bytes":len(body),"sha256":hashlib.sha256(body).hexdigest(),"context":context,"path":str(path.relative_to(BASE))};attempts.append(receipt);doc={"receipt":receipt}
  if body.startswith(b"%PDF"):
   from pypdf import PdfReader
   pages=[{"page":j+1,"text":page.extract_text() or ""} for j,page in enumerate(PdfReader(io.BytesIO(body)).pages)];doc.update(format="PDF",pages=pages)
  elif name.lower().endswith((".xls",".xlsx")):
   import pandas as pd
   wb=pd.read_excel(io.BytesIO(body),sheet_name=None,header=None,dtype=str,keep_default_na=False);doc.update(format="spreadsheet",sheets=[{"name":str(k),"rows":df.values.tolist()} for k,df in wb.items()])
  elif name.lower().endswith(".docx") and zipfile.is_zipfile(io.BytesIO(body)):
   with zipfile.ZipFile(io.BytesIO(body)) as z:root=ET.fromstring(z.read("word/document.xml"))
   ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"};doc.update(format="DOCX",paragraphs=["".join(x.text or "" for x in p.findall(".//w:t",ns)) for p in root.findall(".//w:p",ns)])
  elif name.lower().endswith((".csv",".tsv",".txt")):doc.update(format="text",complete_text=body.decode("utf-8-sig",errors="replace"))
  elif "html" in str(mime).lower() or body.lstrip().startswith((b"<!DOCTYPE",b"<html")):doc.update(format="HTML",qualified_data_asset=False,reason="HTML response is not measured supplement rows")
  else:doc.update(format="other",qualified_data_asset=False)
  documents.append(doc)
 except Exception as exc:attempts.append({"url":url,"error":type(exc).__name__+": "+str(exc),"status":getattr(exc,"code",None)})
result={"schema":"exact-PMC3760025-HTML-table-and-asset-inspection/1","input_receipt":{"path":str(source.relative_to(BASE)),"bytes":len(raw),"sha256":EXPECTED,"run_id":36917071796,"job_id":110553641594,"artifact_id":11189519672},"all_main_HTML_tables":tables,"supplement_sections":sections,"all_literal_file_asset_anchors":all_assets,"selected_supplement_asset_count":len(selected),"access_attempts":attempts,"acquired_documents":documents,"limits":["#SD fragments reference source-page sections, not independent files.","Hagedorn2013 reported206 development and23 validation oligos; Dieckmann2018 reported236 is a separate cohort statement until literal rows reconcile.","Sequence/chemistry/toxicity endpoints do not supply measured duplex melting temperatures."]}
(OUT/"exact-PMC3760025-inspection.json").write_text(json.dumps(result,ensure_ascii=False,default=str,indent=2)+"\n");print("ASO2013_HTML_TABLES_ASSETS_BEGIN");print(json.dumps(result,ensure_ascii=False,default=str));print("ASO2013_HTML_TABLES_ASSETS_END")
