"""Render with standard LibreOffice and Poppler commands; no bundled skill code."""
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
        dest=OUT/name;dest.mkdir()
        profile=OUT/(name+'-lo-profile')
        cmd=['libreoffice','-env:UserInstallation='+profile.as_uri(),'--headless','--convert-to','pdf','--outdir',str(dest),str(HERE/(name+'.docx'))]
        run(cmd,OUT/(name+'.log'),240)
        pdf=dest/(name+'.pdf');assert pdf.is_file()
        run(['pdftoppm','-r','120','-png',str(pdf),str(dest/'page')],OUT/(name+'-images.log'),120)
        if profile.exists():
            assert profile.resolve().parent==OUT.resolve()
            shutil.rmtree(profile)
        reader=PdfReader(pdf)
        text='\n'.join(page.extract_text() for page in reader.pages)
        (dest/'rendered-text.txt').write_text(text,encoding='utf-8')
        record['documents'].append({'name':name,'docx_sha256':sha(HERE/(name+'.docx')),'pdf_sha256':sha(pdf),'pages':len(reader.pages),'page_images':[{'file':p.name,'sha256':sha(p)} for p in sorted(dest.glob('page-*.png'))]})
    record['status']='passed'
finally:
    record['free_bytes_after']=shutil.disk_usage('.').free
    (OUT/'render-receipt.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
