import argparse,csv,datetime,hashlib,io,json,pathlib,re,urllib.parse,urllib.request,unicodedata,zipfile,xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pypdf import PdfReader
P=pathlib.Path;TITLE='Hepatotoxic potential of therapeutic oligonucleotides can be predicted from their sequence and modification pattern'
p=argparse.ArgumentParser();p.add_argument('--input',default='research/autonomy/data-opportunities-2026-09-30/deep-analysis/results/ASO-primary-PDF-and-negative-PROTAC-controls-final.json');a=p.parse_args();folder=P('campaign-output/hagedorn2013-primary');folder.mkdir(parents=True,exist_ok=True)
out={'schema':'aso-exact-hagedorn2013-source/1','completedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accessAttempts':[],'acquiredFiles':[],'documents':[],'errors':[],'limits':['Reported236 is not236 acquiredrows.','Retainliteralchemistry/endpoints; no inferred measuredTm/offtarget labels.']}
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKC',re.sub(r'-\s*\n\s*','',s or '')).lower() if c.isalnum())
def txt(n):return ''.join(n.itertext()).strip() if n is not None else ''
def save(b,name):
 p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);r={'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};out['acquiredFiles'].append(r);return r
def get(url,name):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-public-measurement-audit/1'}),timeout=90) as f:b=f.read(256*1024**2+1);assert len(b)<=256*1024**2;r={'url':url,'status':f.status,'finalUrl':f.url,'contentType':f.headers.get('Content-Type')}
  r.update(save(b,name));out['accessAttempts'].append(r);return b,r
 except Exception as e:out['accessAttempts'].append({'url':url,'status':getattr(e,'code',None),'error':type(e).__name__+': '+str(e)});return None,None
def candidates(rows):return [{'row':i+1,'literalCells':row} for i,row in enumerate(rows) if any(re.fullmatch(r'[ACGTEacgt]{10,35}',re.sub(r'\s+','',str(c))) for c in row)]
def xml_document(b,name):
 root=ET.fromstring(b);tables=[]
 for t in root.iter('table-wrap'):
  rows=[[txt(c) for c in row if c.tag.rsplit('}',1)[-1] in ('td','th')] for row in t.iter('tr')];tables.append({'id':t.attrib.get('id'),'label':txt(t.find('label')),'caption':txt(t.find('caption')),'footnotes':txt(t.find('table-wrap-foot')),'rows':rows,'candidateSequenceRows':candidates(rows)})
 out['documents'].append({'source':name,'kind':'xml','tables':tables,'cohortOrEndpointPassages':[txt(p) for p in root.iter('p') if re.search(r'\b236\b|alanine|aminotransferase|\bALT\b|sequence|modification pattern',txt(p),re.I)]});return root
def inspect(b,name):
 ext=P(name).suffix.lower()
 try:
  if ext=='.pdf':
   pages=[]
   for i,p in enumerate(PdfReader(io.BytesIO(b)).pages):pages.append({'page':i+1,'plainText':p.extract_text() or ''})
   out['documents'].append({'source':name,'kind':'pdf','nPages':len(pages),'nLowTextPages':sum(len(p['plainText'])<100 for p in pages),'pages':pages})
  elif ext in ('.xml','.nxml'):xml_document(b,name)
  elif ext=='.docx':
   with zipfile.ZipFile(io.BytesIO(b)) as z:root=ET.fromstring(z.read('word/document.xml'))
   ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};tables=[]
   for t in root.findall('.//w:tbl',ns):
    rows=[[''.join(x.text or '' for x in c.findall('.//w:t',ns)) for c in r.findall('w:tc',ns)] for r in t.findall('w:tr',ns)];tables.append({'rows':rows,'candidateSequenceRows':candidates(rows)})
   out['documents'].append({'source':name,'kind':'docx','tables':tables})
  elif ext in ('.csv','.tsv','.txt'):
   s=b.decode('utf-8-sig',errors='replace')
   if ext=='.txt':out['documents'].append({'source':name,'kind':'text','text':s})
   else:rows=list(csv.reader(io.StringIO(s),delimiter='\t' if ext=='.tsv' else ','));out['documents'].append({'source':name,'kind':'delimited','rows':rows,'candidateSequenceRows':candidates(rows)})
  elif ext in ('.xlsx','.xls'):
   import pandas as pd
   wb=pd.read_excel(io.BytesIO(b),sheet_name=None,header=None,dtype=str,keep_default_na=False);out['documents'].append({'source':name,'kind':'spreadsheet','sheets':[{'name':str(k),'nRows':len(df),'rows':df.values.tolist(),'candidateSequenceRows':candidates(df.values.tolist())} for k,df in wb.items()]})
  else:out['documents'].append({'source':name,'kind':'unparsed','extension':ext})
 except Exception as e:out['documents'].append({'source':name,'kind':'parse-error','error':type(e).__name__+': '+str(e)})
def main():
 b=P(a.input).read_bytes();d=json.loads(b)
 while isinstance(d,dict) and isinstance(d.get('result'),dict):d=d['result']
 panel=next(x for x in d['ASOSupplements'] if x['pmcid']=='PMC5725219');pdf=next(x for x in panel['pdfs'] if x['member']=='mmc2.pdf');assert pdf['sha256']=='b2132e89351f53dc997ffd3bec1d8f9e0cf3fa8c5771b720071b414ed56d6747';reference=next(x for x in pdf['pages'] if x['page']==9)['plainText'];assert norm(TITLE) in norm(reference) and 'Hagedorn' in reference and '(2013)' in reference
 out['citedSource']={'pmcid':'PMC5725219','inputPath':a.input,'inputSHA256':hashlib.sha256(b).hexdigest(),'member':pdf['member'],'memberSHA256':pdf['sha256'],'page':9,'literalReference':reference,'reportedCohortExpectation':236}
 q='TITLE:"'+TITLE+'" AND AUTH_LAST:Hagedorn AND FIRST_PDATE:[2013-01-01 TO 2013-12-31]';url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','resultType':'core','pageSize':20});b,r=get(url,'exact-query.json');assert b is not None;results=json.loads(b).get('resultList',{}).get('result',[]);exact=[x for x in results if norm(x.get('title',''))==norm(TITLE) and str(x.get('pubYear',''))=='2013' and re.match(r'^Hagedorn\b',x.get('authorString',''),re.I)];out['query']=q;out['nQueryHits']=len(results);assert len(exact)==1,'Uniqueexactidentityrequired';hit=exact[0];out['primaryCitation']=hit;pmcid=hit.get('pmcid');visited=set()
 def acquire(url,name):
  if url in visited:return
  visited.add(url);name=hashlib.sha256(url.encode()).hexdigest()[:10]+'-'+name;b,r=get(url,name)
  if b is None:return
  if zipfile.is_zipfile(io.BytesIO(b)) and P(name).suffix.lower() not in ('.xlsx','.docx'):
   with zipfile.ZipFile(io.BytesIO(b)) as z:
    out['supplementManifest']=[{'member':n.filename,'bytes':n.file_size} for n in z.infolist()]
    for i,n in enumerate(z.infolist()):
     if n.is_dir():continue
     mb=z.read(n);rec=save(mb,'members/'+hashlib.sha256(b).hexdigest()[:10]+'/%03d-'%i+P(n.filename).name);rec['archiveMember']=n.filename;inspect(mb,n.filename)
  else:
   c=(r['contentType'] or '').lower()
   if b.lstrip().startswith(b'<') and ('xml' in c or name.endswith('.xml')):
    try:
     root=xml_document(b,name);links=[]
     for node in root.iter('supplementary-material'):
      for e in node.iter():
       links.extend(v for k,v in e.attrib.items() if k.rsplit('}',1)[-1]=='href' and v.startswith(('https://','http://')))
     for i,u in enumerate(sorted(set(links))):acquire(u,'xml-supp-%03d-'%i+(P(urllib.parse.urlsplit(u).path).name or 'source'))
    except ET.ParseError:inspect(b,name)
   elif 'html' in c or name.endswith('.html'):
    class Links(HTMLParser):
     def __init__(self):super().__init__();self.links=[];self.current=None
     def handle_starttag(self,t,attrs):
      if t=='a':self.current=[dict(attrs).get('href',''),'']
     def handle_data(self,t):
      if self.current is not None:self.current[1]+=t
     def handle_endtag(self,t):
      if t=='a' and self.current is not None:self.links.append(self.current);self.current=None
    parser=Links();parser.feed(b.decode('utf-8',errors='replace'));urls=[]
    for href,label in parser.links:
     u=urllib.parse.urljoin(r['finalUrl'],href)
     if urllib.parse.urlsplit(u).scheme not in ('https','http'):continue
     if re.search(r'supplement|supporting information|suppl[_/-]|/mmc\d',href+' '+label,re.I) or re.search(r'\.(xlsx?|docx?|csv|tsv|zip)$',urllib.parse.urlsplit(u).path,re.I):urls.append(u)
    out['documents'].append({'source':name,'kind':'html','exactPrimarySupplementLinks':sorted(set(urls))})
    for i,u in enumerate(sorted(set(urls))):acquire(u,'linked-%03d-'%i+(P(urllib.parse.urlsplit(u).path).name or 'source.html'))
   else:inspect(b,name)
 if pmcid:acquire('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/fullTextXML','primary.xml');acquire('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/supplementaryFiles','supplements.zip')
 links=hit.get('fullTextUrlList',{}).get('fullTextUrl',[]);out['indexedPublicFullTextLinks']=links
 for i,x in enumerate(links):
  if x.get('availability','').lower() not in ('open access','free') or not x.get('url'):continue
  style=(x.get('documentStyle') or '').lower();acquire(x['url'],'indexed-%03d.'%i+(style if style in ('pdf','xml') else 'html'))
 if not pmcid and hit.get('doi'):acquire('https://doi.org/'+hit['doi'],'exact-doi.html')
 out['sourceRecoveryStatus']='Resolvedexactprimary; acquired literal sources require endpoint/row review.'
try:main()
except Exception as e:out['errors'].append(type(e).__name__+': '+str(e))
P('campaign-output/aso-hagedorn2013-source.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('ASO_HAGEDORN2013_SOURCE_BEGIN');print(json.dumps(out,ensure_ascii=False));print('ASO_HAGEDORN2013_SOURCE_END')
