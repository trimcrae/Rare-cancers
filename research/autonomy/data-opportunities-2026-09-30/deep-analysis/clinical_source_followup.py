import hashlib,html,io,json,re,shutil,subprocess,zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
OUT=Path('campaign-output/clinical-followup');OUT.mkdir(parents=True,exist_ok=True);CAP=512*1024*1024
R=dict(schema='clinical-source-followup/2',sources=[],errors=[],limits=['A retrieved publisher landing page is not automatically full primary text','Case reports do not identify comparative efficacy','Preserve literal patient IDs, followup time/event and selection context before synthesis','No Immunosarc1-to-ImmunoSarc dataset substitution'])
def get(url):
 with urlopen(Request(url,headers={'User-Agent':'Rare-cancers-clinical-public-source-reuse'}),timeout=90) as f:b=f.read(CAP+1);typ=f.headers.get('Content-Type','');final=f.url
 if len(b)>CAP:raise ValueError('Public source exceeded512MiB')
 return b,typ,final
def txt(e):return ' '.join(' '.join(e.itertext()).split())
def receipt(url,b,typ,final,key,ext):
 sha=hashlib.sha256(b).hexdigest();p=OUT/(key+'-'+sha[:12]+ext);p.write_bytes(b);return dict(url=url,finalURL=final,contentType=typ,bytes=len(b),sha256=sha,artifact=str(p))
def pdf_text(b,key):
 p=OUT/(key+'.pdf');p.write_bytes(b)
 if shutil.which('pdftotext'):
  q=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,text=True,timeout=90)
  if q.returncode:raise ValueError('pdftotext '+q.stderr[:300])
  return q.stdout,'pdftotext-layout'
 from pypdf import PdfReader
 return '\n'.join(page.extract_text() or '' for page in PdfReader(io.BytesIO(b)).pages),'pypdf'
RX=re.compile(r'patient|case|metasta|survival|follow.up|progress|censor|NR4A3|TAF15|EWSR1|radiat|dose|lung|toxicit|HTG|gene.expression|GEO|data.avail|accession|clinicalresults|xlsx|sample|supplement',re.I)
def add_text(q,s,key,reader):
 p=OUT/(key+'-extracted.txt');p.write_text(s);q['extractedText']=dict(path=str(p),characters=len(s),reader=reader,sha256=hashlib.sha256(s.encode()).hexdigest());q['matchedText']=[v.strip() for v in re.split(r'\n\s*\n|(?<=[.!?])\s+(?=[A-Z])',s) if RX.search(v)][:180]
 if 'just a moment' in s.casefold() or 'access denied' in s.casefold() or 'making sure you' in s.casefold():q['accessChallengeDetected']=True
for key,pmid in [('SABR','41323055'),('WHOLE_LUNG','36944557'),('HDR','35494187'),('AGARAM_PARTNER','24746215'),('HUANG_PARTNER','36948401')]:
 q=dict(id=key,pmid=pmid,attempts=[]);R['sources'].append(q)
 try:
  u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='+quote('EXT_ID:'+pmid+' AND SRC:MED')+'&resultType=core&format=json';b,typ,final=get(u);q['metadataReceipt']=receipt(u,b,typ,final,key+'-metadata','.json');hits=json.loads(b)['resultList']['result'];assert hits,'No exact primary metadata';m=hits[0];q['metadata']=m
  if m.get('pmcid'):
   u='https://www.ebi.ac.uk/europepmc/webservices/rest/'+m['pmcid']+'/fullTextXML';b,typ,final=get(u);q['primaryReceipt']=receipt(u,b,typ,final,key+'-primary','.xml');z=ET.fromstring(b);q['fullTextRoute']='PMC JATS';add_text(q,txt(z),key,'ElementTree');q['primaryParagraphs']=[txt(e) for e in z.findall('.//body//p') if RX.search(txt(e))];q['tables']=[dict(id=t.get('id'),literalXML=ET.tostring(t,encoding='unicode'),text=txt(t),rows=[[txt(c) for c in row if c.tag in ('td','th')] for row in t.findall('.//tr')]) for t in z.findall('.//table-wrap')]
  else:
   urls=[v['url'] for v in m.get('fullTextUrlList',{}).get('fullTextUrl',[]) if v.get('url')]
   if m.get('doi'):urls.append('https://doi.org/'+m['doi'])
   seen=set()
   for u in urls:
    if u in seen:continue
    seen.add(u)
    try:
     b,typ,final=get(u);pdf=b.startswith(b'%PDF');a=receipt(u,b,typ,final,key+'-publisher','.pdf' if pdf else '.html');q['attempts'].append(a)
     if pdf:s,reader=pdf_text(b,key)
     else:
      s=b.decode('utf-8',errors='replace');s=re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',s,flags=re.I|re.S);s=html.unescape(re.sub(r'<[^>]+>','\n',s));s=re.sub(r'\n\s*\n','\n\n',s);reader='HTML literal text'
     a['characters']=len(s);add_text(a,s,key+'-publisher-'+a['sha256'][:8],reader)
    except Exception as e:q['attempts'].append(dict(url=u,error=type(e).__name__,message=str(e)))
 except Exception as e:q['error']=dict(type=type(e).__name__,message=str(e))
q=dict(id='IMMUNOSARC1_SUPPLEMENT_PDF');R['sources'].append(q)
try:
 u='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7674086/supplementaryFiles';b,typ,final=get(u);q['archiveReceipt']=receipt(u,b,typ,final,'immunosarc1-archive','.zip');z=zipfile.ZipFile(io.BytesIO(b));q['archiveMembers']=[dict(name=v.filename,bytes=v.file_size) for v in z.infolist()];members=[v for v in z.infolist() if v.filename.endswith('jitc-2020-001561supp001.pdf')];assert len(members)==1;v=members[0];b=z.read(v);q['pdfReceipt']=receipt(u+'#'+v.filename,b,'application/pdf',u,'immunosarc1-supp','.pdf');s,reader=pdf_text(b,'immunosarc1-supp');add_text(q,s,'immunosarc1-supp',reader);q['accessionLiterals']=sorted(set(re.findall(r'\b(?:GSE|GSM|GDS|E-MTAB-|PRJNA|SRP)\d+\b',s)));q['workbookLiterals']=sorted(set(re.findall(r'[^\s/]+\.(?:xlsx|xls|csv|tsv)',s,re.I)))
except Exception as e:q['error']=dict(type=type(e).__name__,message=str(e))
Path('campaign-output/clinical-source-followup.json').write_text(json.dumps(R,indent=2)+'\n');print('EMC_CLINICAL_FOLLOWUP_RESULT_BEGIN');print(json.dumps(R,separators=(',',':')));print('EMC_CLINICAL_FOLLOWUP_RESULT_END')
