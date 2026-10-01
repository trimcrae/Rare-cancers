import hashlib,io,json,pathlib,re,urllib.parse,urllib.request,xml.etree.ElementTree as ET,zipfile,subprocess,shutil
OUT=pathlib.Path('campaign-output/methylation-emc-MTAP-prior-art');OUT.mkdir(parents=True,exist_ok=True);receipts=[];errors=[]
def get(url,name,limit=12000000):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-public-source-audit/1.0'}),timeout=60) as r:b=r.read(limit+1);status=r.status;ct=r.headers.get('Content-Type','')
  if len(b)>limit:raise ValueError('bounded source exceeds declared byte limit')
  (OUT/name).write_bytes(b);receipts.append({'url':url,'file':name,'status':status,'content_type':ct,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});return b
 except Exception as e:errors.append({'url':url,'error':str(e)});return None
url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':'EXT_ID:30895378 AND SRC:MED','format':'json','resultType':'core','pageSize':5})
b=get(url,'PMID30895378-core.json');hits=json.loads(b)['resultList']['result'] if b else [];assert len(hits)<=1
record=hits[0] if hits else {};pmcid=record.get('pmcid');passages=[];alltext=[('indexed_abstract',record.get('abstractText',''))];supplement_exports=[]
ids=['200406080083_R06C01','3998909033_R02C02','3999547153_R01C02','3999547153_R06C01','3999547153_R05C01','3999547153_R04C01','3999547153_R03C01','3999547153_R02C01','200406080083_R01C01','201172580026_R03C01'];gsms=['GSM4180874','GSM4181103','GSM4181117','GSM4181118','GSM4181119','GSM4181120','GSM4181121','GSM4181122','GSM4181387','GSM4180711']
if pmcid:
 x=None
 for source_url in ['https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id='+pmcid.removeprefix('PMC')+'&retmode=xml','https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/fullTextXML']:
  candidate=get(source_url,'primary-'+hashlib.sha256(source_url.encode()).hexdigest()[:8]+'.xml')
  if not candidate:continue
  try:
   root_candidate=ET.fromstring(candidate)
   if any(n.tag.split('}')[-1]=='article' for n in root_candidate.iter()):x=candidate;break
  except ET.ParseError:pass
 if x:
  root=ET.fromstring(x)
  for el in root.iter():
   if el.tag.split('}')[-1] in ('p','table','supplementary-material'):
    s=' '.join(' '.join(el.itertext()).split());alltext.append(('primary.xml',s))
    if re.search('myxoid chondrosarcoma|EMCS|copy.number|chromosomal|9p21|MTAP|CDKN2|GSE',s,re.I):passages.append(s[:10000])
 if not x:
  from bs4 import BeautifulSoup
  for host in ['https://europepmc.org/articles/','https://pmc.ncbi.nlm.nih.gov/articles/']:
   raw=get(host+pmcid,'primary-fallback-'+hashlib.sha256(host.encode()).hexdigest()[:6]+'.html')
   if not raw:continue
   s=BeautifulSoup(raw,'html.parser').get_text(' ',strip=True)
   if re.search('myxoid chondrosarcoma',s,re.I) and len(s)>10000:
    alltext.append(('qualified-primary-HTML',s));passages.extend([v for v in re.split(r'(?<=[.!?])\s+',s) if re.search('copy.number|chromosomal|9p21|MTAP|CDKN2|GSE',v,re.I)]);break
 z=get('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/supplementaryFiles','supplementary-files.zip',20000000)
 if z:
  try:
   with zipfile.ZipFile(io.BytesIO(z)) as zz:
    for it in zz.infolist():
     if it.is_dir():continue
     if it.file_size>10000000:errors.append({'supplement':it.filename,'error':'individual supplement exceeds10MB audit bound'});continue
     raw=zz.read(it);name=pathlib.Path(it.filename).name;target=OUT/('supp-'+name);target.write_bytes(raw);supplement_exports.append({'name':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
     if name.lower().endswith(('.txt','.csv','.tsv','.xml','.html')):alltext.append((name,raw.decode('utf-8','replace')))
     elif name.lower().endswith('.xlsx'):
      import openpyxl
      wb=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True);st=[]
      for ws in wb:
       for row in ws.iter_rows(values_only=True):
        line=' | '.join('' if v is None else str(v) for v in row);st.append(ws.title+' '+line)
        if re.search('myxoid chondrosarcoma|EMCS|copy.number|9p21|MTAP|CDKN2|GSE',line,re.I):passages.append(name+': '+line[:10000])
      alltext.append((name,'\n'.join(st)))
     elif name.lower().endswith('.pdf'):
      from pypdf import PdfReader
      s='\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(raw)).pages);alltext.append((name,s))
      for para in s.split('\n\n'):
       if re.search('myxoid chondrosarcoma|EMCS|copy.number|9p21|MTAP|CDKN2|GSE',para,re.I):passages.append(name+': '+' '.join(para.split())[:10000])
  except Exception as e:errors.append({'stage':'OA supplementary zip','error':str(e)})
merged='\n'.join(s for _,s in alltext);matches=[{'source':name,'literal_identifier':v} for name,s in alltext for v in ids+gsms if v in s];geo=sorted(set(re.findall(r'GSE\d+',merged)))
result={'schema':'exact-PMID30895378-EMC-CNV-prior-art/1','PMID':'30895378','record':record,'source_receipts':receipts,'errors':errors,'CNV_EMC_primary_and_supplement_passages':passages,'exact_target_identifier_matches':matches,'GEO_series_mentioned':geo,'supplement_exports':supplement_exports,'overlap_interpretation':'Exact matches can establish reuse; absent/unpublished identifiers cannot establish independence','novelty_boundary':'Published NatCommun2021 EMCS source already says recurrent chromosomal alterations are not observed and most cases have flat CN profiles; no first-EMC-CNV or novel-general-flat-profile claim'}
(OUT/'prior-art-results.json').write_text(json.dumps(result,indent=2)+'\n');print('EMC_CNV_PRIOR_ART_BEGIN');print(json.dumps(result));print('EMC_CNV_PRIOR_ART_END')
