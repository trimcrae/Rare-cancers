"""Finite remote rendering with daily-window and10GiB headroom guards."""
import datetime,hashlib,json,os,pathlib,shutil,signal,subprocess,time,zoneinfo
from pypdf import PdfReader
from guarded_process import allowed,run
HERE=pathlib.Path(__file__).resolve().parent
OUT=pathlib.Path('/tmp/foundation-render');OUT.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
record={'revision':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'scope':'Document rendering only; no science execution','documents':[]}
try:
    for name in ['human-genetics-correspondence','online-resource-1']:
        assert allowed(),'Daily restriction';assert shutil.disk_usage('.').free>10.5*1024**3
        dest=OUT/name
        cmd=['python3',str(HERE/'tools'/'render_docx.py'),str(HERE/(name+'.docx')),'--output_dir',str(dest),'--emit_pdf','--dpi','120']
        run(cmd,OUT/(name+'.log'),240)
        pdf=dest/(name+'.pdf');reader=PdfReader(pdf)
        text='\n'.join(page.extract_text() for page in reader.pages)
        (dest/'rendered-text.txt').write_text(text,encoding='utf-8')
        record['documents'].append({'name':name,'docx_sha256':sha(HERE/(name+'.docx')),'pdf_sha256':sha(pdf),'pages':len(reader.pages),'page_images':[{'file':p.name,'sha256':sha(p)} for p in sorted(dest.glob('page-*.png'))]})
    record['status']='passed'
finally:
    record['free_bytes_after']=shutil.disk_usage('.').free
    (OUT/'render-receipt.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
