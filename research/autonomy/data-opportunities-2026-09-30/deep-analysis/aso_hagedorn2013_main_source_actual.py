import pathlib,json,hashlib,datetime,urllib.request,urllib.parse,subprocess,shutil,concurrent.futures,base64,io
from bs4 import BeautifulSoup
from PIL import Image
OUT=pathlib.Path('campaign-output/hagedorn2013-main-measured-source');OUT.mkdir(parents=True,exist_ok=True)
PIN='321e2baa5ef304351a867592f3cb4337e7b2ad368c5d23ce1ec94cc616550a4c';roots=[pathlib.Path('restored-artifacts'),pathlib.Path('restored-artifacts-extra')];source=next((p for root in roots for p in root.rglob('*indexed-000.html') if hashlib.sha256(p.read_bytes()).hexdigest()==PIN),None);assert source,'Restore exactprimaryHTML'
raw=source.read_bytes();soup=BeautifulSoup(raw,'html.parser');article=soup.find('article') or soup.find(id='main-content');assert article is not None
body=article.get_text(' ',strip=True);assert len(body)>15000 and 'Hepatotoxic potential' in body;(OUT/'primary-complete-text.txt').write_text(body)
result={'schema':'ASO2013-main-measured-source-audit/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'identity':{'PMID':'23952551','PMCID':'PMC3760025','DOI':'10.1089/nat.2013.0436'},'input_receipt':{'path':str(source),'bytes':len(raw),'sha256':PIN},'primary_complete_text':body,'literal_figure_table_inventory':[],'primary_asset_attempts':[],'qualified_assets':[],'limits':['OCR assists source transcription; no validatednumeric plot digitization or inferredTm. Only literal primaryHTMLassets; originalbinary hashes preserved. PNG conversions preserve pixel dimensions for visualinspection.']}
base='https://pmc.ncbi.nlm.nih.gov/articles/PMC3760025/';assets={}
for box in article.find_all(['figure','div']):
 classes=box.get('class',[])
 if not any(c in classes for c in ['fig','table-wrap','fig-inline']):continue
 row={'id':box.get('id'),'complete_caption_and_text':box.get_text(' ',strip=True),'images':[],'literal_anchors':[]}
 for im in box.find_all('img'):row['images'].append({k:im.get(k) for k in ['src','data-src','srcset','alt'] if im.get(k)})
 for a in box.find_all('a',href=True):row['literal_anchors'].append({'href':a['href'],'label':a.get_text(' ',strip=True)})
 result['literal_figure_table_inventory'].append(row)
result['all_literal_primary_images']=[]
for im in article.find_all('img'):
 d={k:im.get(k) for k in ['src','data-src','srcset','alt'] if im.get(k)};result['all_literal_primary_images'].append(d)
 for key in ['src','data-src']:
  if d.get(key):assets[urllib.parse.urljoin(base,d[key])]={'kind':'literal_primary_image','literal':d}
for a in soup.find_all('a',href=True):
 h=a['href'];u=urllib.parse.urljoin(base,h)
 if '/PMC3760025/pdf/' in u and u.lower().endswith('.pdf'):assets[u]={'kind':'literal_primary_PDF','literal_href':h}
 if any(x in urllib.parse.urlparse(u).path.lower() for x in ['.png','.jpg','.jpeg','.gif','.tif']) and a.find_parent(['figure']) is not None:assets[u]={'kind':'literal_primary_image','literal_href':h}
assert len(assets)<=32
def get(item):
 u,context=item
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Rare-cancers-public-source-audit/1'}),timeout=45) as f:b=f.read(16*1024**2+1);status=f.status;mime=f.headers.get('Content-Type');final=f.url
  assert len(b)<=16*1024**2;path=OUT/(hashlib.sha256(u.encode()).hexdigest()[:8]+'-'+(pathlib.Path(urllib.parse.urlsplit(u).path).name or 'asset'));path.write_bytes(b);r={'url':u,'status':status,'mime':mime,'final_url':final,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'path':str(path),'context':context};doc={'receipt':r,'qualified_measured_asset':False}
  if b.startswith(b'%PDF'):
   from pypdf import PdfReader
   doc.update(qualified_measured_asset=True,complete_pdf_text='\n'.join(p.extract_text(extraction_mode='layout') or '' for p in PdfReader(io.BytesIO(b)).pages))
  else:
   try:
    im=Image.open(io.BytesIO(b));im.load();doc.update(qualified_measured_asset=True,original_image_format=im.format,pixel_dimensions=list(im.size))
    if shutil.which('tesseract'):
     q=subprocess.run(['tesseract',str(path),'stdout'],capture_output=True,text=True,timeout=45);doc.update(OCR_text=q.stdout,OCR_status=q.returncode)
    buf=io.BytesIO();im.convert('RGB').save(buf,format='PNG');view=buf.getvalue()
    if len(view)<=1024**2:doc.update(image_base64=base64.b64encode(view).decode(),view_mime='image/png')
   except Exception as e:doc.update(non_image_reason=str(e),response_prefix=b[:150].decode('utf-8','replace'))
  return r,doc
 except Exception as e:return {'url':u,'context':context,'error_type':type(e).__name__,'error':str(e)},None
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for receipt,doc in pool.map(get,sorted(assets.items())):
  result['primary_asset_attempts'].append(receipt)
  if doc is not None:result['qualified_assets'].append(doc)
result['qualified_measured_asset_count']=sum(d.get('qualified_measured_asset',False) for d in result['qualified_assets']);(OUT/'ASO2013-main-measured-source.json').write_text(json.dumps(result,allow_nan=False));print('ASO2013_MAIN_MEASURED_SOURCE_BEGIN');print(json.dumps(result,allow_nan=False));print('ASO2013_MAIN_MEASURED_SOURCE_END')
