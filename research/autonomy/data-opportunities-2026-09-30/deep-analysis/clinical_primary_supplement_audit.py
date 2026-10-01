import hashlib,io,json,re,zipfile,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
CAP=64*1024*1024;MEMBER=32*1024*1024
R={"schema":"emc-clinical-primary-and-supplement-audit/1","startedUtc":datetime.now(timezone.utc).isoformat(),"sources":[],"errors":[]}
STUDIES=[("IMMUNOSARC1","PMC7674086",True),("PEERJ","PMC13374579",True),("MORTALITY","PMC12398172",True),("TRABECTEDIN","PMC4946242",False),("ANTHRACYCLINE","PMC3879193",False),("CHIUSOLE","PMC7308468",False),("PROTEOMICS","PMC9387775",True),("ASO_KAMOLA","PMC4605310",True),("ASO_HAGEDORN_TOX","PMC4797265",True),("ASO_HAGEDORN_PANEL","PMC5725219",True),("ASO_TOEHOLD","PMC10693639",True)]
NS={"x":"http://schemas.openxmlformats.org/spreadsheetml/2006/main","r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
def get(url):
    with urlopen(Request(url,headers={"User-Agent":"Rare-cancers-public-clinical-audit"}),timeout=60) as response:
        if response.headers.get("Content-Length") and int(response.headers["Content-Length"])>CAP:raise ValueError("file cap")
        b=response.read(CAP+1)
    if len(b)>CAP:raise ValueError("file cap")
    return b
def text(e):return " ".join(" ".join(e.itertext()).split())
def xlsx(b,keep_rows=False):
    z=zipfile.ZipFile(io.BytesIO(b));strings=[]
    if "xl/sharedStrings.xml" in z.namelist():strings=[text(e) for e in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("x:si",NS)]
    wb=ET.fromstring(z.read("xl/workbook.xml"));rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"));rels={e.attrib["Id"]:e.attrib["Target"] for e in rel};sheets=[]
    for sh in wb.findall("x:sheets/x:sheet",NS):
        target=rels[sh.attrib["{"+NS["r"]+"}id"]];path=target.lstrip("/") if target.startswith("/") else "xl/"+target
        if path not in z.namelist():path=path.replace("xl/xl/","xl/")
        rows=[]
        for rr in ET.fromstring(z.read(path)).findall("x:sheetData/x:row",NS):
            row={}
            for c in rr.findall("x:c",NS):
                v=c.find("x:v",NS);value=v.text if v is not None else ""
                if c.attrib.get("t")=="s":value=strings[int(value)] if value else ""
                elif c.attrib.get("t")=="inlineStr":
                    elem=c.find("x:is",NS);value=text(elem) if elem is not None else ""
                row[c.attrib.get("r","")]=value
            rows.append(row)
        sheet={"name":sh.attrib["name"],"rows":len(rows),"firstRows":rows[:6],"headers":list(rows[0].values()) if rows else []}
        if keep_rows and len(rows)<=2000:sheet["literalRows"]=rows
        gene_candidates={"CSPG4","SEMA3C","PPARG","ENO3","NR4A3","TYMS","PRAME","FAP","SSTR2","GPC3","CHRNA6","CD8A","CD8B","CD3D","CD3E","CD19","MS4A1","CD79A","PDCD1","CD274","FOXP3","IL7R","NKG7","LST1","COL1A1"};selected=[];numeric_columns={}
        for row in rows[1:]:
            cells=list(row.items());vals=[str(v).strip().upper() for _,v in cells]
            if any(v in gene_candidates for v in vals):selected.append(row)
            for key,val in cells:
                col=re.sub("[0-9]","",key)
                try:n=float(val)
                except (TypeError,ValueError):continue
                numeric_columns.setdefault(col,[]).append(n)
        sheet["selectedLiteralGeneRows"]=selected;sheet["numericColumnSummaries"]={k:{"n":len(v),"min":min(v),"max":max(v),"mean":sum(v)/len(v),"sd":(sum((a-sum(v)/len(v))**2 for a in v)/(len(v)-1))**0.5 if len(v)>1 else None} for k,v in numeric_columns.items()};sheets.append(sheet)
    return sheets
for name,pmc,supp in STUDIES:
    study={"id":name,"pmcid":pmc,"supplementStatus":None}
    try:
        url="https://www.ebi.ac.uk/europepmc/webservices/rest/"+pmc+"/fullTextXML";b=get(url);root=ET.fromstring(b);study["primarySource"]={"url":url,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()};paragraphs=[text(e) for e in root.findall(".//body//p")];rx=re.compile(r"(extraskeletal|NR4A3|TAF15|EWSR1|myxoid|died|death|follow.up|public|available|accession|clinical.{0,40}data|GEO|survival|prognos|overfit|C.index|subject.{0,15}[2345]|GSE\d|E-MTAB|off.target|gapmer|mismatch|growth rate|doubling|normalized|scale views)",re.I);study["matchedPrimaryParagraphs"]=[p for p in paragraphs if rx.search(p)]
        study["tables"]=[{"id":e.attrib.get("id"),"label":text(e.find("label")) if e.find("label") is not None else None,"text":text(e),"rows":[[text(c) for c in tr if c.tag in ("td","th")] for tr in e.findall(".//tr")]} for e in root.findall(".//table-wrap")];study["supplementDeclarations"]=[{"tag":e.tag,"attributes":e.attrib,"text":text(e)} for e in root.iter() if e.tag in ("supplementary-material","ext-link","media") and (e.tag!="ext-link" or any(w in str(e.attrib).lower() for w in ("geo","ncbi","zenodo","github","figshare","xls","supp")))]
        if supp:
            surl="https://www.ebi.ac.uk/europepmc/webservices/rest/"+pmc+"/supplementaryFiles";raw=get(surl);study["supplementArchive"]={"url":surl,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()};archive=zipfile.ZipFile(io.BytesIO(raw));study["supplementStatus"]="downloaded_valid_zip";study["archiveMembers"]=[{"name":e.filename,"bytes":e.file_size} for e in archive.infolist()];parsed=[]
            for member in archive.infolist():
                if member.file_size>MEMBER:continue
                filename=member.filename.lower()
                if not filename.endswith((".xlsx",".docx",".csv",".tsv",".txt")):continue
                data=archive.read(member);item={"file":member.filename,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}
                if filename.endswith(".xlsx"):item["sheets"]=xlsx(data,name.startswith("ASO"))
                elif filename.endswith(".docx"):
                    doc=zipfile.ZipFile(io.BytesIO(data));xml=ET.fromstring(doc.read("word/document.xml"));item["text"]=" ".join(t.text or "" for t in xml.iter() if t.tag.endswith("}t"))
                else:item["text"]=data.decode("utf-8-sig")[:150000]
                parsed.append(item)
            study["parsedSupplementTables"]=parsed
    except Exception as e:study["error"]={"type":type(e).__name__,"message":str(e)};R["errors"].append({"study":name,**study["error"]})
    R["sources"].append(study)
R["finishedUtc"]=datetime.now(timezone.utc).isoformat();Path("campaign-output").mkdir(exist_ok=True);Path("campaign-output/clinical-primary-supplement-audit.json").write_text(json.dumps(R,indent=2)+"\n");print("EMC_PRIMARY_CLINICAL_RESULT_BEGIN");print(json.dumps(R,separators=(",",":")));print("EMC_PRIMARY_CLINICAL_RESULT_END")
