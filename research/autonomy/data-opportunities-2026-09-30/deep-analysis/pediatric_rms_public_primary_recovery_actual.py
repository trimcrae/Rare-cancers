import json,io,re,zipfile,hashlib,datetime,urllib.parse,collections
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
import fitz
import spatial_marker_followthrough_actual as sm
import pediatric_rms_exact_primary_annotations_actual as audit
OUT=sm.OUT;PMC='PMC9133224';DOI='10.1016/j.devcel.2022.04.003';TITLE='the myogenesis program drives clonal selection and drug resistance in rhabdomyosarcoma'
ROOTS=[Path('restored-artifacts'),Path('restored-artifacts-extra'),Path('restored-artifacts-third'),OUT]
def rec(p):return {'saved':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def norm(s):return re.sub(r'\s+',' ',s).lower()
def identify(s):return TITLE in norm(s) or DOI in norm(s)
def urls(s):return sorted(set(re.findall(r'https?://[^\s<>\"\']+',s)))
def error(stage,e,**extra):return {'stage':stage,'error_type':type(e).__name__,'error':str(e),'absence_claim':False,**extra}
def main():
 OUT.mkdir(parents=True,exist_ok=True);r={'schema':'emc-RMS-exact-public-primary-recovery/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'identity':{'pmcid':PMC,'doi':DOI,'PMID':'35483358','NIH_manuscript':'NIHMS1800632','indexed_OA':'N; freeauthor manuscript isreadable afterembargo'},'attempts':[],'primary_documents':[],'literal_external_links':[],'supplements':[],'errors':[]};links={};texts=[]
 html_urls=['https://pmc.ncbi.nlm.nih.gov/articles/'+PMC+'/','https://europepmc.org/articles/'+PMC,'https://www.ncbi.nlm.nih.gov/pmc/articles/'+PMC+'/','https://pmc.ncbi.nlm.nih.gov/articles/'+PMC+'/?report=reader']
 for k,url in enumerate(html_urls):
  try:
   p,receipt=sm.getfull(url,'RMS-exact-author-manuscript-'+str(k)+'.html',32*1024**2);r['attempts'].append(receipt);body=p.read_text(errors='replace');soup=BeautifulSoup(body,'html.parser');text=soup.get_text(' ',strip=True)
   if not identify(text):raise ValueError('Response doesnotidentify exactfreeauthor manuscript; preserve receipt, notsourceabsence')
   texts.append(text);r['primary_documents'].append({'source_receipt':receipt,'text_chars':len(text),'complete_text_saved':str(p),'kind':'HTML'})
   for a in soup.find_all('a',href=True):
    u=urllib.parse.urljoin(receipt['final_url'],a['href']);label=a.get_text(' ',strip=True)
    if u.startswith(('https://','http://')) and not a['href'].startswith('#'):links.setdefault(u,[]).append(label)
   break
  except Exception as e:r['errors'].append(error('FreeauthorHTML',e,url=url))
 pdf_urls=[u for u in links if re.search(r'\.pdf(?:[?#]|$)|[?&]pdf=',u,re.I)]
 if not texts:pdf_urls+=['https://europepmc.org/articles/'+PMC+'?pdf=render','https://pmc.ncbi.nlm.nih.gov/articles/'+PMC+'/pdf/nihms-1800632.pdf','https://pmc.ncbi.nlm.nih.gov/articles/'+PMC+'/pdf/nihms1800632.pdf']
 for k,url in enumerate(dict.fromkeys(pdf_urls)):
  if texts:break
  try:
   p,receipt=sm.getfull(url,'RMS-exact-author-manuscript-'+str(k)+'.pdf',128*1024**2);r['attempts'].append(receipt)
   with fitz.open(p) as doc:text='\n'.join(page.get_text() for page in doc);plinks=[v.get('uri') for page in doc for v in page.get_links() if v.get('uri')]
   if not identify(text):raise ValueError('PDF doesnotidentify exactprimary')
   texts.append(text);tp=OUT/'RMS-exact-author-manuscript-pdf-text.txt';tp.write_text(text);r['primary_documents'].append({'source_receipt':receipt,'text_chars':len(text),'complete_text_receipt':rec(tp),'kind':'PDF'})
   for u in plinks+urls(text):links.setdefault(u,[]).append('LiteralprimaryPDFlink')
  except Exception as e:r['errors'].append(error('FreeauthorPDF',e,url=url))
 assert texts,'Exactpublicprimary recovery unfinished; noannotationabsenceclaim'
 for u,label in sorted(links.items()):
  if re.search(r'github|zenodo|figshare|stjude|GSE\d+|geo/query|supp|mmc|nihms.*-supp|\.(xlsx?|csv|tsv|zip|rds|h5ad|rda)(?:[?#]|$)',u+' '+' '.join(label),re.I):r['literal_external_links'].append({'url':u,'literal_labels':label})
 text='\n'.join(texts);tp=OUT/'RMS-exact-public-primary-complete-text.txt';tp.write_text(text);r['complete_primary_text_receipt']=rec(tp);r['literal_model_mentions']=dict(collections.Counter(re.findall(r'\bSJRHB\d+(?:_[A-Za-z0-9]+)*\b',text)));r['GEO_accessions']=sorted(set(re.findall(r'\bGSE\d+\b',text)));sentences=re.split(r'(?<=[.!?])\s+',text);r['source_annotation_code_data_passages']=[s for s in sentences if re.search(r'data availab|code availab|barcode|annotation|cell.?state|cell.?type|fusion|single.?cell|single.?nucleus|seurat|paraxial|myoblast|myocyte|github|stjude',s,re.I)]
 attachments=[]
 for u,label in links.items():
  s=u+' '+' '.join(label)
  if re.search(r'\.(xlsx?|csv|tsv|txt|zip|rds|rda|h5ad|pdf)(?:[?#]|$)',u,re.I) and re.search(r'/bin/|/supp|/mmc|supplement|additional.*file|supporting.*file',s,re.I):attachments.append(u)
 for k,url in enumerate(dict.fromkeys(attachments)):
  try:
   name=Path(urllib.parse.urlparse(url).path).name;ext=Path(name).suffix.lower();p,receipt=sm.getfull(url,'RMS-recovered-'+str(k)+'-'+name,512*1024**2);r['attempts'].append(receipt);entry={'literal_url':url,'literal_labels':links[url],'source_receipt':receipt,'tables':[]};r['supplements'].append(entry);raw=p.read_bytes()
   if ext in ['.xlsx','.xls']:books=pd.read_excel(io.BytesIO(raw),sheet_name=None,header=None);entry['tables']=[audit.audit_frame(frame,'RMS-recovered-'+str(k)+'-'+name+'-'+str(sheet)) for sheet,frame in books.items()]
   elif ext in ['.csv','.tsv']:entry['tables']=[audit.audit_frame(pd.read_csv(io.BytesIO(raw),sep='\t' if ext=='.tsv' else',',header=None,dtype=str),'RMS-recovered-'+str(k)+'-'+name)]
   elif ext=='.pdf':
    with fitz.open(p) as doc:st='\n'.join(pg.get_text() for pg in doc)
    sp=OUT/(p.stem+'.txt');sp.write_text(st);entry.update(complete_pdf_text=rec(sp),literal_model_mentions=dict(collections.Counter(re.findall(r'\bSJRHB\d+(?:_[A-Za-z0-9]+)*\b',st))),literal_external_urls=urls(st));entry['source_annotation_passages']=[s for s in re.split(r'(?<=[.!?])\s+',st) if re.search(r'annotation|cell.?state|cell.?type|model|fusion|barcode|SJRHB|github',s,re.I)]
   elif ext=='.zip':
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
     entry['all_members']=[{'name':m.filename,'bytes':m.file_size} for m in z.infolist()]
     for m in z.infolist():
      if not re.search(r'\.(xlsx?|csv|tsv|txt)$',m.filename,re.I):continue
      b=z.read(m);mp=OUT/('RMS-recovered-'+str(k)+'-'+Path(m.filename).name);mp.write_bytes(b);item={'member':m.filename,'source_receipt':rec(mp),'tables':[]};entry.setdefault('members',[]).append(item)
      if re.search(r'\.xlsx?$',m.filename,re.I):books=pd.read_excel(io.BytesIO(b),sheet_name=None,header=None);item['tables']=[audit.audit_frame(f,'RMS-'+str(k)+'-'+Path(m.filename).name+'-'+str(s)) for s,f in books.items()]
      elif re.search(r'\.(csv|tsv)$',m.filename,re.I):item['tables']=[audit.audit_frame(pd.read_csv(io.BytesIO(b),sep='\t' if m.filename.lower().endswith('.tsv') else',',header=None,dtype=str),'RMS-'+str(k)+'-'+Path(m.filename).name)]
      else:item['text_chars']=len(b.decode(errors='replace'));item['literal_external_urls']=urls(b.decode(errors='replace'))
   else:entry['finite_next_action']='Read acquired sourceannotation format; noprematureabsence'
  except Exception as e:r['errors'].append(error('Literalprimarysupplement',e,url=url))
 code_links=[x for x in r['literal_external_links'] if 'github.com/' in x['url']];r['public_code_source_readme_audit']=[]
 for k,v in enumerate(code_links):
  m=re.search(r'github\.com/([^/\s?#]+)/([^/\s?#]+)',v['url'])
  if not m:continue
  repo=m.group(1)+'/'+m.group(2).removesuffix('.git');api='https://api.github.com/repos/'+repo
  try:
   p,rr=sm.getfull(api,'RMS-literal-code-repo-'+str(k)+'.json',8*1024**2);info=json.loads(p.read_bytes());branch=info['default_branch'];url='https://api.github.com/repos/'+repo+'/git/trees/'+urllib.parse.quote(branch,safe='')+'?recursive=1';p,tr=sm.getfull(url,'RMS-literal-code-tree-'+str(k)+'.json',32*1024**2);tree=json.loads(p.read_bytes());files=[x for x in tree.get('tree',[]) if x.get('type')=='blob'];candidate=[x for x in files if re.search(r'annotation|metadata|cell.?type|cell.?state|barcode|cluster|seurat|readme|\.rds$|\.h5ad$',x['path'],re.I)];ci={'literal_primary_code_link':v,'repository':repo,'default_branch':branch,'repo_receipt':rr,'complete_tree_receipt':tr,'tree_truncated':tree.get('truncated'),'candidate_source_files':candidate,'source_file_passages':[]};r['public_code_source_readme_audit'].append(ci)
   for j,f in enumerate(candidate):
    if not re.search(r'\.(r|py|md|txt|csv|tsv|json)$',f['path'],re.I) or f.get('size',0)>16*1024**2:continue
    url='https://raw.githubusercontent.com/'+repo+'/'+urllib.parse.quote(branch,safe='')+'/'+urllib.parse.quote(f['path']);p,fr=sm.getfull(url,'RMS-source-code-'+str(k)+'-'+str(j)+'-'+Path(f['path']).name,32*1024**2);st=p.read_text(errors='replace');ci['source_file_passages'].append({'source_path':f['path'],'source_receipt':fr,'all_relevant_lines':[{'line':i+1,'literal_text':line} for i,line in enumerate(st.splitlines()) if re.search(r'annotation|barcode|cell.?state|cell.?type|cluster|readRDS|read_csv|Read10X|download|http|GSE174376|SJRHB',line,re.I)]})
  except Exception as e:r['errors'].append(error('Literalprimarypubliccode',e,repository=repo))
 r['next_finite_action']='Inspectactual sourceannotations/modelmetadata/format and join exact42library/barcode receipts; executeavailable frozen-target state/subtype analysis. Do not infercelllabels or closeattransportfailure.';dest=OUT/'RMS-exact-public-primary-recovery-actual.json';dest.write_text(json.dumps(sm.clean(r),allow_nan=False,default=str));print('EMC_RMS_PUBLIC_PRIMARY_RECOVERY_BEGIN');print(json.dumps(sm.clean(r),allow_nan=False,default=str));print('EMC_RMS_PUBLIC_PRIMARY_RECOVERY_END')
if __name__=='__main__':main()
