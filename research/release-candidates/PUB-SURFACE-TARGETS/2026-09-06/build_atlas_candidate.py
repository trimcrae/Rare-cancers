from pathlib import Path
import sys,subprocess,time,json,datetime,hashlib
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'research/manuscripts'))
import build_submission_pdf as renderer
chrome=Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
assert chrome.is_file()
assert 'surface-tissue-rna' in renderer.PAPERS
renderer.find_chrome=lambda:str(chrome)
class PortableWS(renderer.WS):
 def call(self,method,**params):
  if method=='Page.navigate' and params.get('url','').startswith('file://'):
   params['url']=Path(params['url'][7:]).resolve().as_uri()
  return super().call(method,**params)
renderer.WS=PortableWS
started=time.monotonic()
code=renderer.main(['--paper','surface-tissue-rna','--style','preprint'])
receipt={'exit_code':code,'elapsed_seconds':round(time.monotonic()-started,3),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'chrome':str(chrome),'builder':'research/manuscripts/build_submission_pdf.py','adapter':str(Path(__file__).resolve()),'scope':'Actual registered manuscript and supplement PDF build; visual QA separately recorded'}
(root/'.cache/atlas-pdf-build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
raise SystemExit(code)
