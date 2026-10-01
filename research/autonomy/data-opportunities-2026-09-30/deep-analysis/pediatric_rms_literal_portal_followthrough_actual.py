import json,re,io,zipfile,hashlib,datetime,urllib.parse,collections
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
import spatial_marker_followthrough_actual as sm
import pediatric_rms_exact_primary_annotations_actual as audit
OUT=sm.OUT;PORTAL='https://pecan.stjude.cloud/static/RMS-scrna-atlas-2020/';ROOTS=[Path('restored-artifacts'),Path('restored-artifacts-extra'),Path('restored-artifacts-third'),OUT]
def rec(p):return {'saved':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def fail(stage,e,**kw):return {'stage':stage,'error_type':type(e).__name__,'error':str(e),'absence_claim':False,**kw}
def literal_links(text,base):
 soup=BeautifulSoup(text,'html.parser');links=[]
 for e in soup.find_all(['a','script','link']):
  for attr in ['href','src']:
   if e.get(attr):links.append(urllib.parse.urljoin(base,e[attr]))
 for e in soup.find_all('meta'):
  if str(e.get('http-equiv','')).lower()=='refresh':
   m=re.search(r'url\s*=\s*[\"\']?(.+?)[\"\']?$',str(e.get('content','')),re.I)
   if m:links.append(urllib.parse.urljoin(base,m.group(1)))
 for v in re.findall(r'https?://[^\s<>\"\']+',text):links.append(v.replace('&amp;','&'))
 for v in re.findall(r'[\"\']([^\"\']+\.(?:json|csv|tsv|txt|rds|rda|h5ad|h5|gz|js|xlsx)(?:\?[^\"\']*)?)[\"\']',text,re.I):
  if not re.search(r'\s',v):links.append(urllib.parse.urljoin(base,v))
 return list(dict.fromkeys(u for u in links if u.startswith(('https://','http://'))))
def get(url,label,r,cap=512*1024**2):
 p,rc=sm.getfull(url,label,cap);r['all_access_receipts'].append(rc);return p,rc
def main():
 OUT.mkdir(parents=True,exist_ok=True);r={'schema':'emc-RMS-literal-study-portal-and-supplements/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Exactprimary literal16NIHattachments/actualstudyportal and its own declarations; noannotationinvention','all_access_receipts':[],'supplements':[],'portal_documents':[],'portal_literal_data_candidates':[],'errors':[]};native={}
 for root in ROOTS:
  for p in root.rglob('RMS-recovered-*-NIHMS1800632-supplement-*'):
   m=re.search(r'(NIHMS1800632-supplement-\d+\.(?:xlsx|pdf))$',p.name)
   if m:native.setdefault(m.group(1),[]).append(p)
 def acquire(name):
  original='https://pmc.ncbi.nlm.nih.gov/articles/instance/9133224/bin/'+name;queue=[]
  for p in native.get(name,[]):
   raw=p.read_bytes()
   if name.endswith('.xlsx') and zipfile.is_zipfile(io.BytesIO(raw)):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
     if 'xl/workbook.xml' in z.namelist():return p,rec(p)
   text=raw.decode(errors='replace');r.setdefault('original_transport_interstitial_audit',[]).append({'literal_attachment':name,'response_receipt':rec(p),'first2000_literal_chars':text[:2000]});queue.extend(literal_links(text,original))
  queue+=[original,'https://pmc.ncbi.nlm.nih.gov/articles/PMC9133224/bin/'+name,'https://europepmc.org/articles/PMC9133224/bin/'+name,'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9133224/bin/'+name];done=set();attempt=0
  while queue and attempt<12:
   url=queue.pop(0)
   if url in done:continue
   done.add(url)
   if not re.search(re.escape(name)+r'(?:[?#]|$)',url) and 'cdn.ncbi.nlm.nih.gov/' not in url:continue
   attempt+=1
   try:
    p,rc=get(url,'RMS-literal-supplement-'+str(attempt)+'-'+name,r);raw=p.read_bytes()
    if name.endswith('.xlsx') and zipfile.is_zipfile(io.BytesIO(raw)):
     with zipfile.ZipFile(io.BytesIO(raw)) as z:
      if 'xl/workbook.xml' in z.namelist():return p,rc
    elif name.endswith('.pdf') and raw.startswith(b'%PDF-'):return p,rc
    text=raw.decode(errors='replace');queue=literal_links(text,rc['final_url'])+queue;r.setdefault('non_source_download_response_audit',[]).append({'literal_attachment':name,'response_receipt':rc,'first2000_literal_chars':text[:2000]})
   except Exception as e:r['errors'].append(fail('Literalpublishedattachment',e,name=name,url=url))
  return None,None
 for k in range(2,17):
  name='NIHMS1800632-supplement-'+str(k)+'.xlsx';p,rc=acquire(name)
  if p is None:r['supplements'].append({'literal_attachment':name,'status':'finitepublicacquisition_not_yet_resolved','biological_absence':False});continue
  books=pd.read_excel(p,sheet_name=None,header=None);r['supplements'].append({'literal_attachment':name,'status':'fully_decoded','source_receipt':rc,'tables':[audit.audit_frame(f,'RMS-literal-'+str(k)+'-'+str(s)) for s,f in books.items()]})
 pages=[]
 try:
  p,rc=get(PORTAL,'RMS-literal-study-portal.html',r,32*1024**2);text=p.read_text(errors='replace');pages.append((PORTAL,text,rc));own_scripts=[u for u in literal_links(text,PORTAL) if u.startswith(PORTAL) and re.search(r'\.js(?:[?#]|$)',u)];r['all_declared_portal_scripts']=[u for u in literal_links(text,PORTAL) if re.search(r'\.js(?:[?#]|$)',u)]
  for i,u in enumerate(dict.fromkeys(own_scripts)):
   try:p,rc=get(u,'RMS-literal-study-script-'+str(i)+'.js',r,64*1024**2);pages.append((u,p.read_text(errors='replace'),rc))
   except Exception as e:r['errors'].append(fail('Declaredstudyportal_script',e,url=u))
  candidates={}
  for u,text,rc in pages:
   ll=literal_links(text,u);r['portal_documents'].append({'source_receipt':rc,'all_literal_links':ll,'all_relevant_literal_lines':[{'line_1based':i+1,'literal_text':line} for i,line in enumerate(text.splitlines()) if re.search(r'barcode|cell.?type|cell.?state|annotation|paraxial|myoblast|myocyte|dataset|sample|label|SJRHB|json|tsv|csv|download|matrix',line,re.I)]})
   for v in ll:
    if (v.startswith(PORTAL) or v.startswith('https://pecan.stjude.cloud/')) and re.search(r'\.(?:json|csv|tsv|txt|gz|rds|rda|h5ad|h5)(?:[?#]|$)',v):candidates.setdefault(v,[]).append(u)
  for i,(u,owners) in enumerate(candidates.items()):
   item={'literal_url':u,'declared_by':owners};r['portal_literal_data_candidates'].append(item)
   try:
    name=Path(urllib.parse.urlparse(u).path).name;p,rc=get(u,'RMS-portal-declared-'+str(i)+'-'+name,r,1024*1024**2);item['source_receipt']=rc;ext=Path(name).suffix.lower()
    if ext in ['.csv','.tsv','.txt']:f=pd.read_csv(p,sep='\t' if ext!='.csv' else',',header=None,dtype=str);item['table_audit']=audit.audit_frame(f,'RMS-portal-'+str(i)+'-'+name)
    elif ext=='.json':
     d=json.loads(p.read_bytes());item['JSON_type']=type(d).__name__;item['JSON_keys']=list(d) if isinstance(d,dict) else None;item['JSON_rows']=len(d) if isinstance(d,(list,dict)) else None
     if isinstance(d,list) and d and isinstance(d[0],dict):item['table_audit']=audit.audit_frame(pd.DataFrame(d),'RMS-portal-'+str(i)+'-'+name)
     else:item['first_literal_JSON']=d if len(p.read_bytes())<100000 else None
    else:item['next_finite_action']='Readacquiredliteralstudyfile format/barcodes andjoin actualsaved88target matrices before source-state inference'
   except Exception as e:item['error']=fail('Declaredstudyportal_data',e)
 except Exception as e:r['errors'].append(fail('Exactpublishedstudyportal',e,url=PORTAL))
 r['next_finite_action']='Inspectfullydecodedmodeltables/portalconfig; actualsourcecellstate/barcodejoins andallfrozengenes. No countredo/clinicalpatientpaddingnormalization/sourceauthorEGFRrediscoverynovelty.';dest=OUT/'RMS-literal-study-portal-and-supplements-actual.json';dest.write_text(json.dumps(sm.clean(r),allow_nan=False,default=str));print('EMC_RMS_LITERAL_PORTAL_FOLLOWTHROUGH_BEGIN');print(json.dumps(sm.clean(r),allow_nan=False,default=str));print('EMC_RMS_LITERAL_PORTAL_FOLLOWTHROUGH_END')
if __name__=='__main__':main()
