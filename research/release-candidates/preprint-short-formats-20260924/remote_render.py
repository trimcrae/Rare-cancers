from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess,sys,shutil,json,hashlib,re,unicodedata,zipfile,os
from pypdf import PdfReader
from lxml import etree
W=Path(__file__).resolve().parent;O=W/'render-result';O.mkdir(exist_ok=True)
def guard():
    local=datetime.now(ZoneInfo('America/New_York'))
    authorized=local.date().isoformat()=='2026-09-24'
    assert not 6<=local.hour<10 or authorized
    free=shutil.disk_usage(W).free;assert free>=10*1024**3
    return {'America_New_York':local.isoformat(),'free_bytes':free,'explicit_task_date_authorization':authorized}
def norm(s):return re.sub(r'[^\w]+','',unicodedata.normalize('NFKC',s).lower())
receipt={'before':guard(),'inputs':{},'documents':{}}
for doc in sorted((W/'inputs').glob('*.docx')):
    if doc.name=='CSPG4-cover-letter.docx':continue
    guard();receipt['inputs'][doc.name]=hashlib.sha256(doc.read_bytes()).hexdigest()
    out=O/doc.stem
    subprocess.run([sys.executable,str(W/'render_docx.py'),str(doc),'--output_dir',str(out),'--dpi','120','--emit_pdf'],check=True,timeout=420)
    pdf=out/(doc.stem+'.pdf');reader=PdfReader(pdf)
    texts=[p.extract_text() or '' for p in reader.pages];(out/'pages.txt').write_text('\n\f\n'.join(texts),encoding='utf8')
    # Exclude the running footer so a paragraph split at a page boundary is contiguous.
    whole=''.join(re.sub(r'(?m)^\s*\d+\s*$','',re.sub(r'CSPG4 RNA across sarcoma types\s*\|\s*\d+','',s)) for s in texts);whole=norm(whole)
    with zipfile.ZipFile(doc) as z:root=etree.fromstring(z.read('word/document.xml'))
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragraphs=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in root.xpath('.//w:p',namespaces=ns)]
    missing=[s for s in paragraphs if len(norm(s))>1 and norm(s) not in whole]
    receipt['documents'][doc.name]={'pages':len(reader.pages),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'nonempty_source_paragraphs':sum(bool(norm(s)) for s in paragraphs),'paragraphs_not_contiguous_in_pdf_text':missing,'page_text_characters':[len(s) for s in texts],'page_sizes':[[float(p.mediabox.width),float(p.mediabox.height)] for p in reader.pages],'output_files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in out.iterdir() if p.is_file()}}
graph=W/'inputs/ASO-graphical-abstract.pdf'
if graph.exists():
    guard(); dest=O/'ASO-graphical-abstract';dest.mkdir(exist_ok=True);shutil.copyfile(graph,dest/graph.name)
    subprocess.run(['pdftoppm','-scale-to','1594','-png','-singlefile',str(graph),str(dest/'page-1')],check=True,timeout=60)
    receipt['graphical_abstract']={'input_sha256':hashlib.sha256(graph.read_bytes()).hexdigest(),'pages':len(PdfReader(graph).pages),'output_files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in dest.iterdir() if p.is_file()}}
receipt['after']=guard();(O/'RENDER-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:{'pages':v['pages'],'missing_paragraphs':len(v['paragraphs_not_contiguous_in_pdf_text'])} for k,v in receipt['documents'].items()}))
