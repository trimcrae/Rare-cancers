import hashlib,io,json,pathlib,re,urllib.request,urllib.parse,zipfile,datetime
from bs4 import BeautifulSoup
import pdfplumber,openpyxl
D='10.1089/nat.2013.0436'
B=pathlib.Path('campaign-output/aso2013-publisher');B.mkdir(parents=True,exist_ok=True)
O={'schema':'exact-ASO2013-normal-publisher/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verifiedPrimary':{'doi':D,'pmid':'23952551','pmcid':'PMC3760025','HTMLsha256':'321e2baa5ef304351a867592f3cb4337e7b2ad368c5d23ce1ec94cc616550a4c'},'attempts':[],'documents':[],'limits':['Normal public requests only; no challenge handling.','Derived normal provider routes are not literal publisher links or confirmed assets.','No236-row or measuredTm claim without labels.']}
seen=set();queue=[]
def get(u,why):
 if u in seen:return None
 seen.add(u);r={'url':u,'reason':why};O['attempts'].append(r)
 try:
  with urllib.request.urlopen(u,timeout=45) as q:
   b=q.read(30000001);r.update(status=q.status,finalURL=q.url,mime=q.headers.get('Content-Type',''))
  if len(b)>30000000:raise ValueError('30MB per-file bound, not source absence')
  h=hashlib.sha256(b).hexdigest();name=pathlib.Path(urllib.parse.urlparse(u).path).name or 'landing'
  ext='.pdf' if b.lstrip().startswith(b'%PDF-') else ('.xlsx' if b.startswith(b'PK') and '.xlsx' in u else ('.zip' if b.startswith(b'PK') else '.html'))
  p=B/(h[:12]+'-'+name+ext);p.write_bytes(b);r.update(path=str(p),bytes=len(b),sha256=h)
  return b,r
 except Exception as e:r['error']=type(e).__name__+': '+str(e);return None
def pdf(b,r,member=None):
 with pdfplumber.open(io.BytesIO(b)) as z:
  pages=[{'page':i+1,'text':p.extract_text(layout=True) or '', 'tables':p.extract_tables()} for i,p in enumerate(z.pages)]
 O['documents'].append({'receipt':r,'member':member,'sha256':hashlib.sha256(b).hexdigest(),'kind':'genuinePDF','pages':pages})
def links(b,r):
 if b.lstrip().startswith(b'%PDF-'):pdf(b,r);return
 if zipfile.is_zipfile(io.BytesIO(b)):
  with zipfile.ZipFile(io.BytesIO(b)) as z:
   if 'xl/workbook.xml' in z.namelist():
    w=openpyxl.load_workbook(io.BytesIO(b),read_only=True,data_only=False)
    O['documents'].append({'receipt':r,'kind':'genuineXLSX','sheets':{a.title:[[str(v) if isinstance(v,(datetime.date,datetime.datetime)) else v for v in row] for row in a.iter_rows(values_only=True)] for a in w.worksheets}})
   else:
    for n in z.namelist():
     if n.lower().endswith('.pdf'):
      x=z.read(n)
      if x.lstrip().startswith(b'%PDF-'):pdf(x,r,n)
     elif n.lower().endswith(('.txt','.csv','.tsv')):
      x=z.read(n);O['documents'].append({'receipt':r,'member':n,'sha256':hashlib.sha256(x).hexdigest(),'kind':'sourceTextTable','text':x.decode('utf8',errors='replace')})
  return
 if 'text/csv' in r['mime'].lower():
  O['documents'].append({'receipt':r,'kind':'sourceTextTable','text':b.decode('utf8',errors='replace')});return
 soup=BeautifulSoup(b,'html.parser')
 for a in soup.find_all(['a','meta','link']):
  for key in ['href','content','data-href','data-download-url']:
   v=a.get(key)
   if not v or not isinstance(v,str):continue
   u=urllib.parse.urljoin(r['finalURL'],v);p=urllib.parse.urlparse(u);context=str(a)
   if p.scheme!='https' or not any(p.netloc==s or p.netloc.endswith('.'+s) for s in ['sagepub.com','liebertpub.com','figshare.com']):continue
   if re.search(r'\.(pdf|zip|xlsx?|csv)(?:$|[?])|suppl|supplement|ndownloader',u,re.I) and (D.lower() in urllib.parse.unquote(u).lower() or re.search('supplement|suppl',context,re.I)):
    queue.append((u,'literal publisher anchor/meta: '+context[:500]))
m=get('https://api.crossref.org/works/'+D,'exact DOI registry metadata')
if m:
 try:
  v=json.loads(m[0])['message'];assert v['DOI'].lower()==D
  t=' '.join(v.get('title',[]));assert 'hepatotoxic potential' in t.lower() and 'modification pattern' in t.lower()
  O['crossref']={'receipt':m[1],'metadata':v}
  for x in v.get('link',[]):queue.append((x['URL'],'literal Crossref link'))
  u=v.get('resource',{}).get('primary',{}).get('URL')
  if u and 'doi.org' not in u:queue.append((u,'literal Crossref primary publisher URL'))
 except Exception as e:O['metadataError']=str(e)
for host in ['journals.sagepub.com','www.liebertpub.com']:
 for route in ['doi/','doi/suppl/']:queue.append(('https://'+host+'/'+route+D,'normal exact-DOI publisher route'))
for h in ['journals.sagepub.com','www.liebertpub.com']:
 for n in ['Supp_Table1.pdf','Supp_Fig1.pdf']+['Supp_Table%d.pdf'%i for i in range(2,7)]:queue.append(('https://'+h+'/doi/suppl/'+D+'/suppl_file/'+n,'derived normal provider route from verified DOI and primary-literal filename'))
while queue and len(seen)<30:
 u,why=queue.pop(0);r=get(u,why)
 if r:links(*r)
O['qualifiedPDFCount']=sum(x['kind']=='genuinePDF' for x in O['documents']);O['unattempted_queue']=queue
(B/'result.json').write_text(json.dumps(O,indent=2,allow_nan=False))
print('ASO2013_PUBLISHER_BEGIN');print(json.dumps(O,separators=(',',':'),allow_nan=False));print('ASO2013_PUBLISHER_END')
