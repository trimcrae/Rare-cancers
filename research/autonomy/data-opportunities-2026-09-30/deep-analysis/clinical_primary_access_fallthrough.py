import hashlib,io,json,re,shutil,subprocess,time,xml.etree.ElementTree as E
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request,urlopen
O=Path('campaign-output/clinical-public-fallback');O.mkdir(parents=True,exist_ok=True);R=dict(schema='clinical-primary-public-access-fallthrough/1',sources=[],limits=['Access/metadata discovery is not proof of source nonexistence','Redirect/challenge HTML is not a clinical primary','HTMLfull-primary detection is provisional until patienttables/fulltext are reviewed','No outreach, authentication, author requests or overlapping-cohort pooling'])
class HP(HTMLParser):
 def __init__(self):super().__init__();self.a=[];self.skip=0;self.ts=[];self.t=None;self.row=None;self.cell=None
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
  if t=='table':self.t=[]
  if t=='tr' and self.t is not None:self.row=[]
  if t in ('td','th') and self.row is not None:self.cell=[]
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
  if t in ('td','th') and self.cell is not None:self.row.append(' '.join(self.cell).strip());self.cell=None
  if t=='tr' and self.row is not None:self.t.append(self.row);self.row=None
  if t=='table' and self.t is not None:self.ts.append(self.t);self.t=None
 def handle_data(self,d):
  if not self.skip:self.a.append(d)
  if self.cell is not None:self.cell.append(d)
def local(x):return x.tag.rsplit('}',1)[-1]
def textof(x):return ' '.join(' '.join(x.itertext()).split())
def fetch(u):
 with urlopen(Request(u,headers={'User-Agent':'Rare-cancers-primary-source-audit','Accept':'*/*'}),timeout=35) as x:b=x.read(32*1024*1024+1);ct=x.headers.get('Content-Type','');final=x.url
 if len(b)>32*1024*1024:raise ValueError('32MiB response cap')
 return b,ct,final
def parse(b,ct,p):
 if b.startswith(b'%PDF') or 'application/pdf' in ct:
  f=p.with_suffix('.pdf');f.write_bytes(b);txt=f.with_suffix('.txt')
  if shutil.which('pdftotext'):
   v=subprocess.run(['pdftotext','-layout',str(f),str(txt)],capture_output=True,text=True,timeout=45)
   if v.returncode:raise ValueError('PDF text extraction failed '+v.stderr[:200])
   text=txt.read_text();reader='pdftotext-layout'
  else:
   from pypdf import PdfReader
   text='\n'.join(page.extract_text() or '' for page in PdfReader(io.BytesIO(b)).pages);txt.write_text(text);reader='pypdf'
  return dict(kind='PDF',text=text,tables=[],reader=reader)
 s=b.decode('utf-8','replace')
 if s.lstrip().startswith('<?xml') or '<article' in s or '<OAI-PMH' in s:
  root=E.fromstring(b);body=[x for x in root.iter() if local(x)=='body'];paras=[textof(x) for z in body for x in z.iter() if local(x)=='p'];tables=[]
  for tab in root.iter():
   if local(tab)!='table-wrap':continue
   rows=[[textof(c) for c in row if local(c) in ('td','th')] for row in tab.iter() if local(row)=='tr'];tables.append(dict(id=tab.get('id'),text=textof(tab),rows=rows))
  return dict(kind='XML',text='\n'.join(paras) if paras else textof(root),tables=tables,articleBody=bool(body))
 h=HP();h.feed(s);return dict(kind='HTML',text=' '.join(' '.join(h.a).split()),tables=h.ts)
def useful(q):
 t=q['text'];bad=re.search(r'just a moment|verify you are human|enable javascript and cookies|access denied|checking your browser',t,re.I)
 if bad:return False
 if q['kind']=='PDF':return len(t)>1000 and bool(re.search(r'myxoid|NR4A3',t,re.I))
 if q['kind']=='XML':return bool(q.get('articleBody')) and len(t)>3000
 return len(t)>8000 and bool(q['tables']) and bool(re.search(r'follow.up|clinical outcome|survival',t,re.I))
cases=[('AGARAM','10.1016/j.humpath.2014.01.007',['https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4015728/fullTextXML','https://pmc.ncbi.nlm.nih.gov/articles/PMC4015728/','https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4015728/','https://europepmc.org/articles/PMC4015728','https://europepmc.org/articles/PMC4015728?pdf=render','https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC4015728','https://www.ncbi.nlm.nih.gov/pmc/utils/oai/oai.cgi?verb=GetRecord&identifier=oai:pubmedcentral.nih.gov:4015728&metadataPrefix=pmc']),('WHOLE_LUNG','10.1016/j.clon.2023.03.004',['https://www.clinicaloncologyonline.net/article/S0936-6555(23)00111-5/fulltext','https://www.clinicaloncologyonline.net/article/S0936-6555(23)00111-5/pdf','https://www.sciencedirect.com/science/article/pii/S0936655523001115']),('HUANG','10.1016/j.modpat.2023.100161',['https://www.modernpathology.org/article/S0893395223000662/fulltext','https://www.modernpathology.org/article/S0893395223000662/pdf','https://www.sciencedirect.com/science/article/pii/S0893395223000662'])]
for key,doi,urls in cases:
 item=dict(id=key,doi=doi,attempts=[],fullPrimaries=[]);R['sources'].append(item)
 try:
  u='https://api.openalex.org/works/https://doi.org/'+doi;b,ct,f=fetch(u);a=json.loads(b);item['openAlex']=dict(url=u,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),openAccess=a.get('open_access'),bestOA=a.get('best_oa_location'));locations=[a.get('best_oa_location')]+a.get('locations',[]);extra=[]
  for z in locations:
   if not z or not z.get('is_oa'):continue
   for field in ('pdf_url','landing_page_url'):
    v=z.get(field)
    if v and v not in extra:extra.append(v)
  urls+=extra[:5]
 except Exception as e:item['openAlexError']=dict(type=type(e).__name__,message=str(e))
 urls=list(dict.fromkeys(urls))
 for j,u in enumerate(urls):
  attempts=3 if key=='AGARAM' and j==0 else 1
  for trial in range(attempts):
   rec=dict(url=u,retry=trial);item['attempts'].append(rec)
   try:
    b,ct,f=fetch(u);rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),contentType=ct,finalURL=f);p=O/(key+'-'+str(j)+'-'+str(trial));p.with_suffix('.raw').write_bytes(b);q=parse(b,ct,p);rec.update(kind=q['kind'],textCharacters=len(q['text']),usablePrimary=useful(q));p.with_suffix('.txt').write_text(q['text'])
    if rec['usablePrimary']:item['fullPrimaries'].append(dict(route=u,receipt=rec,fullText=q['text'],tables=q['tables'],kind=q['kind']));break
   except Exception as e:rec['error']=dict(type=type(e).__name__,message=str(e))
   if trial+1<attempts:time.sleep(10)
  if item['fullPrimaries']:break
 item['status']='primary-acquired' if item['fullPrimaries'] else 'bounded-public-routes-exhausted-no-primary-acquired'
(O/'clinical-primary-public-fallback.json').write_text(json.dumps(R,indent=2)+'\n');print(json.dumps(R,separators=(',',':')))
