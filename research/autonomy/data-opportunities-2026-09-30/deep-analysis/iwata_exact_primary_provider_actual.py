import hashlib, html, io, json, re, urllib.parse, urllib.request,datetime
from pathlib import Path
import pandas as pd
O=Path('campaign-output/iwata-exact-provider'); O.mkdir(parents=True,exist_ok=True)
D='10.1007/s13577-025-01250-7'
R={'schema':'Iwata-exact-primary-provider-and-unit-audit/1','doi':D,'executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':[],'limits':['Public access only; preview/challenge is not full primary','No new efficacy or endpoint-cause claim','Exact workbook unit, not magnitude inference']}
seen=set()
def get(u,label):
 if u in seen:return None
 seen.add(u); q={'label':label,'url':u}; R['sources'].append(q)
 try:
  req=urllib.request.Request(u,headers={'User-Agent':'Rare-cancers-exact-primary-source-audit/1','Accept-Encoding':'identity'})
  with urllib.request.urlopen(req,timeout=45) as f:
   b=f.read(32*1024**2+1); q.update(http=f.status,finalURL=f.url,contentType=f.headers.get('Content-Type',''))
  if len(b)>32*1024**2:raise ValueError('Source cap exceeded, not absence')
  h=hashlib.sha256(b).hexdigest(); ext='.pdf' if b.startswith(b'%PDF') else ('.xlsx' if b.startswith(b'PK') and '.xlsx' in u else ('.json' if b.lstrip().startswith((b'{',b'[')) else '.html'))
  p=O/(label+'-'+h[:12]+ext); p.write_bytes(b)
  q.update(bytes=len(b),sha256=h,path=str(p))
  if b.startswith(b'%PDF'):
   from pypdf import PdfReader
   s='\n'.join(page.extract_text() or '' for page in PdfReader(io.BytesIO(b)).pages); q['validPDF']=True
  elif b.startswith(b'PK'):s=''
  else:
   s=b.decode('utf8',errors='replace'); s=re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',s,flags=re.I|re.S)
   s=' '.join(html.unescape(re.sub(r'<[^>]+>',' ',s)).split())
  q['textCharacters']=len(s)
  q['previewOrChallenge']=bool(re.search(r'preview of subscription|access denied|just a moment|buy article PDF|verify you are human',s,re.I))
  q['methodsPresent']=bool(re.search(r'materials? and methods|drug screening|cell viability assay',s,re.I))
  q['sourceText']=s[:180000] if q.get('validPDF') or '/fullTextXML' in u else s[:45000]
  return b
 except Exception as e:q['error']=type(e).__name__+': '+str(e); return None
b=get('https://api.crossref.org/works/'+urllib.parse.quote(D,safe=''),'crossref-exact')
if b:
 try:
  m=json.loads(b)['message']; assert m['DOI'].lower()==D
  R['crossrefIdentity']={k:m.get(k) for k in ['DOI','title','container-title','published','license','link']}
  for j,v in enumerate(m.get('link',[])):
   u=v.get('URL','')
   if urllib.parse.urlparse(u).scheme=='https':get(u,'crossref-declared-'+str(j))
 except Exception as e:R['crossrefParseError']=str(e)
b=get('https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='+urllib.parse.quote('DOI:'+D)+'&resultType=core&format=json','epmc-core')
if b:
 try:
  ms=[x for x in json.loads(b)['resultList']['result'] if x.get('doi','').lower()==D]
  R['exactEuropePMCMetadata']=ms
  for j,m in enumerate(ms):
   pid=m.get('pmcid',''); pmid=m.get('id','') if m.get('source')=='MED' else ''
   if re.fullmatch(r'\d+',pmid):get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='+pmid+'&retmode=xml','pubmed-'+pmid)
   if re.fullmatch(r'PMC\d+',pid):
    get('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pid+'/fullTextXML','epmc-full-'+pid)
    get('https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id='+pid,'pmc-oa-'+pid)
    get('https://pmc.ncbi.nlm.nih.gov/articles/'+pid+'/','pmc-html-'+pid)
   for k,v in enumerate(m.get('fullTextUrlList',{}).get('fullTextUrl',[])):
    u=v.get('url','')
    if urllib.parse.urlparse(u).scheme=='https':get(u,'metadata-fulltext-'+str(j)+'-'+str(k))
 except Exception as e:R['epmcParseError']=str(e)
get('https://link.springer.com/content/pdf/'+D+'.pdf','springer-canonical-pdf')
b=get('https://link.springer.com/article/'+D,'springer-canonical-html')
if b:
 s=b.decode('utf8',errors='replace')
 hrefs=dict.fromkeys(html.unescape(x) for x in re.findall(r'href=[\"\']([^\"\']+)[\"\']',s,re.I))
 for j,u in enumerate(hrefs):
  u=urllib.parse.urljoin('https://link.springer.com/article/'+D,u)
  exactpdf=re.search(r'\.pdf(?:\?|$)',u,re.I) and D in urllib.parse.unquote(u)
  exactfig='13577_2025_1250_MOESM2_ESM' in u
  if urllib.parse.urlparse(u).scheme=='https' and (exactpdf or exactfig):get(u,'literal-publisher-'+str(j))
u='https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs13577-025-01250-7/MediaObjects/13577_2025_1250_MOESM6_ESM.xlsx'
b=get(u,'s6-IC50-exact')
if b:
 assert hashlib.sha256(b).hexdigest()=='2fe320a6fc39a5a8dc21aa36830772caabb3e4d51c8fffb7dca132ca101cbd28'
 R['completeIC50Workbook']={n:[[None if pd.isna(v) else v for v in row] for row in d.values.tolist()] for n,d in pd.read_excel(io.BytesIO(b),sheet_name=None,header=None).items()}
(O/'execution-summary.json').write_text(json.dumps(R,indent=2,allow_nan=False)+'\n')
print('IWATA_EXACT_PROVIDER_BEGIN'); print(json.dumps(R,allow_nan=False)); print('IWATA_EXACT_PROVIDER_END')
