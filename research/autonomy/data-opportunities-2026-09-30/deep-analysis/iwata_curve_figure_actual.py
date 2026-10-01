import base64,hashlib,io,json,re,shutil,subprocess
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime,timezone
import requests
from bs4 import BeautifulSoup
from PIL import Image
import openpyxl
OUT=Path('campaign-output/iwata-curve-figures');OUT.mkdir(parents=True,exist_ok=True)
ROOT=Path('campaign-output/iwata-exact-provider')
HTML=ROOT/'springer-canonical-html-0952bcd068f8.html'
TIFF=ROOT/'literal-publisher-184-6d59176cc4d6.html'
XLS=ROOT/'s6-IC50-exact-2fe320a6fc39.xlsx'
BASE='https://link.springer.com/article/10.1007/s13577-025-01250-7'
TU='https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs13577-025-01250-7/MediaObjects/13577_2025_1250_MOESM2_ESM.tiff'
XU='https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs13577-025-01250-7/MediaObjects/13577_2025_1250_MOESM6_ESM.xlsx'
SH={'html':'0952bcd068f8c43395a5882e805a509d9497c0427c31f62bf371be90177d4e4f','tiff':'6d59176cc4d61ec5e334c1c7ee234e291060c1183924fbab75ae268a8bbcbf05','xlsx':'2fe320a6fc39a5a8dc21aa36830772caabb3e4d51c8fffb7dca132ca101cbd28'}
R={'schema':'iwata-literal-curve-figures-v1','executed_utc':datetime.now(timezone.utc).isoformat(),'sources':[],'images':[],'errors':[],'limits':['Figure-label audit only; no curve digitization or inferred complete methods. OCR hits require visual confirmation; workbook rows are not proof that every row has a released curve.']}
S=requests.Session();S.headers.update({'User-Agent':'public-primary-source-audit/1.0'})
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(url,label):
 try:
  q=S.get(url,timeout=(15,90));b=q.content
  if len(b)>25000000:raise ValueError('Unexpected source >25MB')
  p=OUT/(label+'-'+sha(b)[:12]+'.html');p.write_bytes(b)
  R['sources'].append({'label':label,'url':url,'finalURL':q.url,'http':q.status_code,'contentType':q.headers.get('Content-Type'),'bytes':len(b),'sha256':sha(b),'path':str(p)})
  return b if q.status_code==200 else None
 except Exception as e:R['errors'].append({'url':url,'error':str(e)});return None
def restored(p,key,url):
 if p.exists():
  b=p.read_bytes()
  if sha(b)!=SH[key]:raise ValueError('Restored SHA mismatch: '+str(p))
  R['sources'].append({'label':'restored-'+key,'url':url,'bytes':len(b),'sha256':sha(b),'path':str(p),'verified':True});return b
 b=fetch(url,'missing-'+key)
 if b is None:raise ValueError('Missing source: '+key)
 if key!='html' and sha(b)!=SH[key]:raise ValueError('Source changed: '+key)
 return b
OCR=None
def add_image(b,label,url=None):
 global OCR
 try:
  im=Image.open(io.BytesIO(b));im.load();count=getattr(im,'n_frames',1)
  for k in range(count):
   im.seek(k);rgb=im.convert('RGB');p=OUT/(label+'-frame-'+str(k+1)+'.png');rgb.save(p,optimize=True)
   x={'label':label,'url':url,'frame':k+1,'frames':count,'format':im.format,'size':list(rgb.size),'sourceSHA256':sha(b),'pngPath':str(p)}
   if shutil.which('tesseract'):
    z=subprocess.run(['tesseract',str(p),'stdout','--psm','11'],capture_output=True,text=True,timeout=180);text=z.stdout;x.update(ocrEngine='tesseract',ocrExitCode=z.returncode,ocrText=text,ocrStderr=z.stderr)
   else:
    import numpy as np
    from rapidocr_onnxruntime import RapidOCR
    if OCR is None:OCR=RapidOCR()
    rr,elapsed=OCR(np.asarray(rgb));x.update(ocrEngine='RapidOCR-CPU',ocrRecords=rr,ocrElapsed=elapsed);text='\n'.join(q[1] for q in (rr or []));x['ocrText']=text
   op=p.with_suffix('.txt');op.write_text(text);x['ocrPath']=str(op)
   view=rgb.copy();view.thumbnail((2600,2600))
   while True:
    buf=io.BytesIO();view.save(buf,format='PNG',optimize=True);vb=buf.getvalue()
    if len(vb)<=450000 or min(view.size)<500:break
    view.thumbnail((int(view.width*.8),int(view.height*.8)))
   vp=OUT/(label+'-frame-'+str(k+1)+'-view.png');vp.write_bytes(vb);x.update(viewPath=str(vp),viewBytes=len(vb),viewSize=list(view.size));R['images'].append(x)
   if len(R['images'])<=4 and len(vb)<=450000:
    print('IWATA_VIEW_BEGIN');print(json.dumps({'label':label,'frame':k+1,'sourceSHA256':sha(b),'base64':base64.b64encode(vb).decode()}));print('IWATA_VIEW_END')
  return True
 except Exception as e:R['errors'].append({'label':label,'url':url,'imageError':str(e)});return False
def parse_html(b,url,label):
 soup=BeautifulSoup(b,'html.parser');text=soup.get_text(' ',strip=True)
 R.setdefault('html',[]).append({'label':label,'url':url,'sha256':sha(b),'preview':bool(re.search(r'preview of subscription|buy article|log in via an institution',text,re.I)),'text':text})
 contexts=[];images=[];links=[]
 for a in soup.find_all('a',href=True):
  at=a.get_text(' ',strip=True);u=urljoin(url,a['href'])
  if re.search(r'/figures/4(?:$|[?#])',u) or re.fullmatch(r'Fig\.?\s*4',at,re.I):links.append(u)
 nodes=[]
 for node in soup.find_all(['figure','div','section']):
  if re.fullmatch(r'(?:Fig|fig|figure)[-_]?4',str(node.get('id',''))):nodes.append(node)
 if '/figures/4' in url:
  nodes+=soup.find_all('figure');nodes+=soup.select('.c-article-section__figure-caption, .c-article-section__figure-content')
 for node in nodes:
  contexts.append(node.get_text(' ',strip=True))
  for im in node.find_all('img'):
   for attr in ['src','data-src']:
    if im.get(attr):images.append(urljoin(url,im[attr]))
   for attr in ['srcset','data-srcset']:
    for part in str(im.get(attr,'')).split(','):
     if part.strip():images.append(urljoin(url,part.strip().split()[0]))
 for im in soup.find_all('img'):
  if re.search(r'(?:Fig\.?\s*4|_Fig4|_fig4)',str(im.get('alt',''))+' '+str(im.get('src',''))):
   for attr in ['src','data-src']:
    if im.get(attr):images.append(urljoin(url,im[attr]))
 for m in re.finditer(r'Supplementary Fig\.?\s*2',text,re.I):contexts.append(text[max(0,m.start()-80):m.start()+450])
 R.setdefault('literalFigureContexts',[]).append({'label':label,'contexts':list(dict.fromkeys(contexts)),'figureLinks':list(dict.fromkeys(links)),'imageURLs':list(dict.fromkeys(images))})
 return list(dict.fromkeys(links)),list(dict.fromkeys(images))
h=restored(HTML,'html',BASE);t=restored(TIFF,'tiff',TU);xb=restored(XLS,'xlsx',XU);add_image(t,'supplementary-figure-2',TU)
wb=openpyxl.load_workbook(io.BytesIO(xb),read_only=True,data_only=True);rows=[]
for ws in wb:
 for row in ws.iter_rows(values_only=True):
  if len(row)>=3 and isinstance(row[2],(int,float)) and isinstance(row[1],str):rows.append({'sheet':ws.title,'name':row[1],'IC50_nM':row[2],'CAS':row[0]})
R['completeIC50Rows']=rows
links,urls=parse_html(h,BASE,'restored-main-preview')
for i,u in enumerate(links[:4]):
 if not re.match(r'https://(?:link|www\.link)\.springer\.com/',u) or u.split('#')[0]==BASE:continue
 b=fetch(u,'literal-figure4-page-'+str(i))
 if b:
  more,ims=parse_html(b,u,'literal-figure4-page-'+str(i));urls+=ims
seen=set()
for i,u in enumerate(urls):
 if u in seen:continue
 seen.add(u)
 if len(seen)>8:break
 if not re.match(r'https://(?:media\.springernature\.com|static-content\.springer-cdn\.com|link\.springer\.com)/',u):continue
 b=fetch(u,'literal-main-figure4-image-'+str(i))
 if b:add_image(b,'main-figure4-'+str(i),u)
def norm(s):return re.sub(r'[^a-z0-9]+',' ',s.lower()).strip()
for item in R['images']:
 tx=' '+norm(item.get('ocrText',''))+' ';hits=[]
 for row in rows:
  name=row['name'];variants=[name]
  if name=='Doxorubicin (Adriamycin)':variants+=['Doxorubicin','Adriamycin']
  for v in variants:
   if ' '+norm(v)+' ' in tx:hits.append(name);break
 item['exactNormalizedOCRNameHits']=hits
R['reconciliation']={'workbookRows':len(rows),'uniqueWorkbookNames':len(set(r['name'] for r in rows)),'supplementaryOCRNames':sorted(set(n for x in R['images'] if x['label']=='supplementary-figure-2' for n in x['exactNormalizedOCRNameHits'])),'mainFigure4OCRNames':sorted(set(n for x in R['images'] if x['label'].startswith('main-figure4') for n in x['exactNormalizedOCRNameHits'])),'status':'Complete OCR and literal image acquisition; final source-label reconciliation requires actual image inspection. No inferred 3+21 split.'}
(OUT/'result.json').write_text(json.dumps(R,indent=2))
print('IWATA_CURVE_FIGURES_BEGIN');print(json.dumps(R));print('IWATA_CURVE_FIGURES_END')
