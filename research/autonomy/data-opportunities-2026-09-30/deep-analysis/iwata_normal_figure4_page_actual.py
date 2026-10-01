import requests,hashlib,json,re,io,base64,html
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime,timezone
from bs4 import BeautifulSoup
from PIL import Image
O=Path('campaign-output/iwata-normal-figure4');O.mkdir(parents=True,exist_ok=True)
U='https://link.springer.com/article/10.1007/s13577-025-01250-7/figures/4'
R={'schema':'iwata-normal-figure4-v1','executed_utc':datetime.now(timezone.utc).isoformat(),'routeProvenance':'Ordinary publisher figure-page route constructed from the independently verified exact article DOI; not a literal link recovered from the subscription preview.','doi':'10.1007/s13577-025-01250-7','sources':[],'captions':[],'images':[],'errors':[],'limits':['Only genuine publicly returned figure/caption assets are used. No complete article methods, replicate count, error-bar definition or quantitative curve value inferred from pixels.']}
S=requests.Session();S.headers.update({'User-Agent':'public-primary-source-audit/1.0'})
def sha(b):return hashlib.sha256(b).hexdigest()
def get(u,label):
 try:
  q=S.get(u,timeout=(15,90));b=q.content
  if len(b)>25000000:raise ValueError('Unexpected source >25MB')
  p=O/(label+'-'+sha(b)[:12]+'.html');p.write_bytes(b)
  R['sources'].append({'url':u,'finalURL':q.url,'http':q.status_code,'contentType':q.headers.get('Content-Type'),'bytes':len(b),'sha256':sha(b),'path':str(p)})
  return (b,q.url) if q.status_code==200 else (None,q.url)
 except Exception as e:R['errors'].append({'url':u,'error':str(e)});return None,u
b,final=get(U,'canonical-figure4-page');urls=[]
if b:
 soup=BeautifulSoup(b,'html.parser');R['pageTitle']=soup.title.get_text(' ',strip=True) if soup.title else None;R['pageText']=soup.get_text(' ',strip=True)
 R['previewOrChallenge']=bool(re.search(r'preview of subscription|access denied|checking your browser|buy article',R['pageText'],re.I))
 for n in soup.select('figcaption, .c-article-section__figure-caption, .figure-caption, #caption'):
  t=n.get_text(' ',strip=True)
  if t and t not in R['captions']:R['captions'].append(t)
 for n in soup.find_all(['img','source']):
  for a in ['src','data-src']:
   if n.get(a):urls.append(urljoin(final,n[a]))
  for a in ['srcset','data-srcset']:
   for v in str(n.get(a,'')).split(','):
    if v.strip():urls.append(urljoin(final,v.strip().split()[0]))
 for n in soup.find_all('a',href=True):
  u=urljoin(final,n['href'])
  if '13577_2025_1250_Fig4' in u:urls.append(u)
 for m in re.finditer(r'https?[^\s\"\'<>]+13577_2025_1250_Fig4[^\s\"\'<>]+',b.decode('utf-8','replace')):urls.append(html.unescape(m.group(0)).replace('\\/','/'))
urls=list(dict.fromkeys(u for u in urls if '13577_2025_1250_Fig4' in u and u.startswith('https://media.springernature.com/')));R['literalReturnedFigure4ImageURLs']=urls
for i,u in enumerate(urls):
 if '/m312/' in u:continue
 raw,fu=get(u,'literal-returned-figure4-image-'+str(i))
 if not raw:continue
 try:
  im=Image.open(io.BytesIO(raw));im.load();rgb=im.convert('RGB');p=O/('figure4-'+str(i)+'-full.png');rgb.save(p,optimize=True)
  x={'url':u,'finalURL':fu,'sourceSHA256':sha(raw),'format':im.format,'size':list(rgb.size),'fullPNGPath':str(p)};v=rgb.copy();v.thumbnail((3000,3000))
  while True:
   z=io.BytesIO();v.save(z,format='PNG',optimize=True);vb=z.getvalue()
   if len(vb)<=450000 or min(v.size)<500:break
   v.thumbnail((int(v.width*.8),int(v.height*.8)))
  vp=O/('figure4-'+str(i)+'-view.png');vp.write_bytes(vb);x.update(viewPath=str(vp),viewSize=list(v.size),viewBytes=len(vb));R['images'].append(x)
  if len(R['images'])<=4 and len(vb)<=450000:
   print('IWATA_MAIN_VIEW_BEGIN');print(json.dumps({'index':i,'sourceSHA256':sha(raw),'base64':base64.b64encode(vb).decode()}));print('IWATA_MAIN_VIEW_END')
 except Exception as e:R['errors'].append({'url':u,'imageError':str(e)})
(O/'result.json').write_text(json.dumps(R,indent=2))
print('IWATA_NORMAL_FIGURE4_BEGIN');print(json.dumps(R));print('IWATA_NORMAL_FIGURE4_END')
