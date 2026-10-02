"""Bounded primary metadata identity audit; no methylation values or fits."""
import csv, gzip, hashlib, io, json, re, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parent
CAP=2_000_000
receipts=[]
def fetch(name,url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-primary-metadata-identity/1'}),timeout=35) as r:
            b=r.read(CAP+1); status=r.status; final=r.url
        if len(b)>CAP: raise ValueError('metadata response exceeds 2 MB cap')
        (ROOT/name).write_bytes(b)
        receipts.append(dict(file=name,url=url,final_url=final,status=status,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
        return b
    except Exception as e:
        receipts.append(dict(file=name,url=url,status='access_failed',error=str(e)))
        return None
def workbook(b):
    w=openpyxl.load_workbook(io.BytesIO(b),read_only=True,data_only=True)
    return [{'sheet':s.title,'rows':[[str(v) if v is not None else '' for v in row] for row in s.iter_rows(values_only=True)]} for s in w]
def snippets(b,terms):
    t=ET.fromstring(b)
    return [' '.join(' '.join(p.itertext()).split()) for p in t.findall('.//p') if any(term in ' '.join(p.itertext()).lower() for term in terms)]
ko=fetch('koelsche.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7819999/fullTextXML')
ly=fetch('lyskjaer.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8185366/fullTextXML')
base='https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-020-20603-4/MediaObjects/'
books={}
for n in (4,5,6,7):
    name=f'41467_2020_20603_MOESM{n}_ESM.xlsx'
    b=fetch(name,base+name)
    if b: books[str(n)]=workbook(b)
sdrf=fetch('E-MTAB-9875.sdrf.txt','https://www.ebi.ac.uk/biostudies/files/E-MTAB-9875/E-MTAB-9875.sdrf.txt')
out={'paper_snippets':{'koelsche':snippets(ko,['different patients','individual/different','validation set included']) if ko else [],
                      'lyskjaer':snippets(ly,['patient','reference cohort','training set','reference set']) if ly else []},
     'workbooks':{k:[{'sheet':s['sheet'],'n_rows':len(s['rows']),'first_rows':s['rows'][:3]} for s in v] for k,v in books.items()}}
(ROOT/'workbook-rows.json').write_text(json.dumps(books,indent=2)+'\n',encoding='utf-8')
if sdrf:
    rr=list(csv.reader(io.StringIO(sdrf.decode('utf-8-sig')),delimiter='\t'))
    out['sdrf']={'n_rows':len(rr)-1,'headers':rr[0],'first_rows':rr[1:3]}
(ROOT/'initial-audit.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
(ROOT/'retrieval-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=True))
