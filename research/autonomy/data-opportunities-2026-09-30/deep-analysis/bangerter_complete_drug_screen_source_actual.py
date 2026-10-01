import base64,hashlib,io,json,re,shutil,subprocess,zipfile
from pathlib import Path
from datetime import datetime,timezone
import xml.etree.ElementTree as E
import requests
from PIL import Image
O=Path('campaign-output/bangerter-drug-screen');O.mkdir(parents=True,exist_ok=True)
AP=Path('campaign-output/bangerter-genotypes/declared-supplements.zip')
ASH='f81f4cad2ff8a456aadf971db0e38db3e8fecbd4f9aa5ac94c52a412f5c45c93'
XU='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9813045/fullTextXML'
ZU='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9813045/supplementaryFiles'
R={'schema':'bangerter-complete-drug-screen-source-v1','executed_utc':datetime.now(timezone.utc).isoformat(),'doi':'10.1007/s13577-022-00818-x','pmcid':'PMC9813045','sources':[],'tables':[],'figures':[],'images':[],'errors':[],'limits':['Source acquisition and literal measurement qualification. Two patient-derived models are not a patient-response cohort; no target causality or clinical efficacy inferred. Image-only numbers must be explicitly labelled if digitized later.']}
S=requests.Session();S.headers.update({'User-Agent':'EMC-public-measured-source-audit/1.0'})
def sha(b):return hashlib.sha256(b).hexdigest()
def get(u,label):
 q=S.get(u,timeout=(15,90));b=q.content
 R['sources'].append({'label':label,'url':u,'finalURL':q.url,'http':q.status_code,'bytes':len(b),'contentType':q.headers.get('Content-Type'),'sha256':sha(b)})
 if q.status_code!=200:raise ValueError(str(q.status_code)+' '+u)
 if len(b)>25000000:raise ValueError('Unexpected >25MB source')
 (O/(label+'.html')).write_bytes(b);return b
xp=O/'primary.xml';xb=xp.read_bytes() if xp.exists() else get(XU,'exact-primary-xml');xp.write_bytes(xb);root=E.fromstring(xb)
def text(n):return re.sub(r'\s+',' ',''.join(n.itertext())).strip() if n is not None else ''
ids=[text(n) for n in root.iter('article-id')]
if R['doi'] not in ids:raise ValueError('Primary DOI identity not verified: '+repr(ids))
R['articleIdentifiers']=ids;R['primaryTitle']=text(root.find('.//article-title'));body=root.find('body');R['fullPrimaryBodyText']=text(body)
R['drugScreenParagraphs']=[text(n) for n in body.iter('p') if re.search(r'drug|compound|viability|screen|IC.?50|EC.?50|area under|AUC|dose',text(n),re.I)]
for w in root.iter('table-wrap'):
 rows=[]
 for tr in w.iter('tr'):rows.append([text(x) for x in tr if x.tag in ['th','td']])
 R['tables'].append({'id':w.get('id'),'label':text(w.find('label')),'caption':text(w.find('caption')),'rows':rows,'fullText':text(w)})
for f in root.iter('fig'):
 g=[]
 for n in f.iter('graphic'):g +=[v for k,v in n.attrib.items() if k.endswith('href')]
 R['figures'].append({'id':f.get('id'),'label':text(f.find('label')),'caption':text(f.find('caption')),'graphics':g})
R['supplementDeclarations']=[{'text':text(n),'attributes':dict(n.attrib),'hrefs':[v for x in n.iter() for k,v in x.attrib.items() if k.endswith('href')]} for n in root.iter('supplementary-material')]
if AP.exists():
 zb=AP.read_bytes()
 if sha(zb)!=ASH:raise ValueError('Restored archive SHA mismatch')
 R['sources'].append({'label':'restored-verified-archive','path':str(AP),'bytes':len(zb),'sha256':sha(zb),'verified':True})
else:
 zb=get(ZU,'exact-supplementary-archive')
 if sha(zb)!=ASH:raise ValueError('Previously verified archive identity changed')
z=zipfile.ZipFile(io.BytesIO(zb));R['archiveMembers']=[{'name':x.filename,'bytes':x.file_size} for x in z.infolist()]
selected=[f for f in R['figures'] if re.search(r'drug|compound|viability|screen|IC.?50|EC.?50|AUC|sensitivity|inhibitor',f['caption'],re.I)];R['drugRelevantFigureIDs']=[f['id'] for f in selected];ocr=None
for f in selected:
 for g in f['graphics']:
  base=Path(g).name;matches=[n for n in z.namelist() if Path(n).name==base or Path(n).stem==base];jpg=[n for n in matches if Path(n).suffix.lower() in ['.jpg','.jpeg','.png','.tif','.tiff']]
  if jpg:matches=jpg
  if not matches:R['errors'].append({'figure':f['id'],'graphic':g,'error':'Declared figure graphic not found in genuine archive'});continue
  for name in matches:
   b=z.read(name);p=O/Path(name).name;p.write_bytes(b)
   try:
    im=Image.open(io.BytesIO(b));im.load();rgb=im.convert('RGB');png=p.with_suffix('.png');rgb.save(png,optimize=True)
    a={'figure':f['id'],'label':f['label'],'caption':f['caption'],'member':name,'sourceSHA256':sha(b),'bytes':len(b),'size':list(rgb.size),'sourcePath':str(p),'pngPath':str(png)}
    if shutil.which('tesseract'):
     t=subprocess.run(['tesseract',str(png),'stdout','--psm','11'],capture_output=True,text=True,timeout=180);a.update(ocrEngine='tesseract',ocrExitCode=t.returncode,ocrText=t.stdout,ocrStderr=t.stderr)
    else:
     import numpy as np
     from rapidocr_onnxruntime import RapidOCR
     if ocr is None:ocr=RapidOCR()
     rr,elapsed=ocr(np.asarray(rgb));a.update(ocrEngine='RapidOCR-CPU',ocrRecords=rr,ocrElapsed=elapsed,ocrText='\n'.join(x[1] for x in (rr or [])))
    png.with_suffix('.txt').write_text(a['ocrText']);v=rgb.copy();v.thumbnail((3000,3000))
    while True:
     buf=io.BytesIO();v.save(buf,format='PNG',optimize=True);vb=buf.getvalue()
     if len(vb)<=450000 or min(v.size)<500:break
     v.thumbnail((int(v.width*.8),int(v.height*.8)))
    vp=png.with_name(png.stem+'-view.png');vp.write_bytes(vb);a.update(viewPath=str(vp),viewSize=list(v.size),viewBytes=len(vb));R['images'].append(a)
    if len(vb)<=450000:
     print('BANGERTER_SCREEN_VIEW_BEGIN');print(json.dumps({'figure':f['id'],'member':name,'sourceSHA256':sha(b),'base64':base64.b64encode(vb).decode()}));print('BANGERTER_SCREEN_VIEW_END')
   except Exception as e:R['errors'].append({'member':name,'error':str(e)})
(O/'result.json').write_text(json.dumps(R,indent=2))
print('BANGERTER_SCREEN_SOURCE_BEGIN');print(json.dumps(R));print('BANGERTER_SCREEN_SOURCE_END')
