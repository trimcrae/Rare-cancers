#!/usr/bin/env python3
import argparse,base64,datetime,hashlib,io,json,pathlib,re,shutil,subprocess,zipfile
import fitz
from PIL import Image
def digest(b):return hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--zip',default='campaign-output/aso-pdf-sources/ASO_HAGEDORN_TOX.zip');p.add_argument('--pages',default='');p.add_argument('--max-image-bytes',type=int,default=500000);a=p.parse_args()
root=pathlib.Path('campaign-output/aso-burel-s6-ocr');root.mkdir(parents=True,exist_ok=True);source=pathlib.Path(a.zip)
if not source.is_file():
 hits=list(pathlib.Path('campaign-output').rglob('ASO_HAGEDORN_TOX.zip'))
 if len(hits)!=1:raise RuntimeError('Expected one restored Burel ZIP: '+str(hits))
 source=hits[0]
zb=source.read_bytes()
with zipfile.ZipFile(io.BytesIO(zb)) as z:
 hits=[n for n in z.namelist() if pathlib.PurePosixPath(n).name=='supp_gkv1210_nar-02589-f-2015-File008.pdf']
 if len(hits)!=1:raise RuntimeError('Exact PDF member not unique')
 member=hits[0];pdf=z.read(member)
assert len(pdf)==4440222 and digest(pdf)=='ac8bb7a1034a6bce3c4a4360495e912396b2a03610b0261d229ddd842b91d519'
(root/'burel-gkv1210-supplement.pdf').write_bytes(pdf)
if not shutil.which('tesseract'):
 subprocess.run(['sudo','apt-get','update'],check=True);subprocess.run(['sudo','apt-get','install','-y','tesseract-ocr'],check=True)
version=subprocess.run(['tesseract','--version'],text=True,capture_output=True,check=True).stdout.splitlines()[0];doc=fitz.open(stream=pdf,filetype='pdf');assert len(doc)==28;rows=[]
for i,page in enumerate(doc):
 n=i+1;png=root/('page-%02d.png'%n);page.get_pixmap(matrix=fitz.Matrix(2,2),colorspace=fitz.csGRAY,alpha=False).save(str(png));r=subprocess.run(['tesseract',str(png),'stdout','--psm','11'],capture_output=True,text=True,check=True);txt=r.stdout;(root/('page-%02d.txt'%n)).write_text(txt,encoding='utf-8');cap=bool(re.search(r'(?:supplement(?:ary|al)?\s*)?(?:figure|fig\.?)[\s:.-]*s?\s*6\b',txt,re.I));names=re.findall(r'\b(?:PTEN|SOD1|FXI|BIRC5|FVII|MYD88|RNase|off.target|partial(?:ly)?\s+match)\b',txt,re.I);rows.append({'page':n,'nativeTextChars':len(page.get_text().strip()),'ocrText':txt,'ocrBytes':len(txt.encode()),'figureS6CaptionDetected':cap,'priorityScore':(100 if cap else 0)+len(names),'pngPath':str(png),'pngSha256':digest(png.read_bytes())});print('OCR page',n,flush=True)
if a.pages:
 chosen=[int(x) for x in a.pages.split(',') if x.strip()];assert len(chosen)<=2 and len(chosen)==len(set(chosen)) and all(1<=x<=len(doc) for x in chosen);reason='Explicit source-review pages'
else:
 direct=[r['page'] for r in rows if r['figureS6CaptionDetected']];chosen=direct[:2] if direct else [r['page'] for r in sorted(rows,key=lambda r:(-r['priorityScore'],r['page']))[:2]];reason='OCR S6 caption or highest source-relevant scores; visual identification required'
images=[]
for n in chosen:
 src=pathlib.Path(rows[n-1]['pngPath']);im=Image.open(src).convert('L')
 while True:
  b=io.BytesIO();im.save(b,format='PNG',optimize=True);data=b.getvalue()
  if len(data)<=a.max_image_bytes:break
  if min(im.size)<400:raise RuntimeError('Cannot fit bounded PNG budget')
  im=im.resize((int(im.width*.85),int(im.height*.85)),Image.Resampling.LANCZOS)
 path=root/('page-%02d-review.png'%n);path.write_bytes(data);item={'page':n,'mimeType':'image/png','bytes':len(data),'sha256':digest(data),'width':im.width,'height':im.height,'path':str(path),'base64':base64.b64encode(data).decode()};images.append({k:v for k,v in item.items() if k!='base64'});print('ASO_S6_IMAGE_BEGIN');print(json.dumps(item,separators=(',',':')));print('ASO_S6_IMAGE_END',flush=True)
out={'schema':'aso-burel-image-supplement-ocr/1','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'primaryDOI':'10.1093/nar/gkv1210','primaryPMCID':'PMC4797265','zipReceipt':{'path':str(source),'bytes':len(zb),'sha256':digest(zb)},'pdfMember':member,'pdfBytes':len(pdf),'pdfSha256':digest(pdf),'pageCount':len(doc),'tesseractVersion':version,'pages':rows,'reviewImages':images,'selectionReason':reason,'limits':['OCR is a recovery aid, not verified measurements.','Exact candidate bases/mismatches require image inspection.','No toxicity or cleavage truth inferred from an alignment.']}
(root/'ocr-result.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print('ASO_BUREL_S6_OCR_BEGIN');print(json.dumps(out,separators=(',',':')));print('ASO_BUREL_S6_OCR_END',flush=True)
