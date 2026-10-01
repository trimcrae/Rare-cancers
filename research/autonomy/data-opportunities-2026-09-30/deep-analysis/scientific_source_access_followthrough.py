import io,json,hashlib,datetime,urllib.request,urllib.parse,zipfile,xml.etree.ElementTree as ET,posixpath,re,csv,collections
from pathlib import Path
from mcd_partial_access import probe_mcd,FILES as MCD_FILES,BASE as MCD_BASE
from tiff_partial_access import probe_tiff,PILOTS
BASE=Path('research/autonomy/data-opportunities-2026-09-30/deep-analysis');OUT=BASE/'outputs';SOURCE=BASE/'sources';CAP=8*1024*1024;NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch(url,label):
 req=urllib.request.Request(url,headers={'User-Agent':'EMC-public-data-reanalysis/1','Accept-Encoding':'identity'})
 with urllib.request.urlopen(req,timeout=60) as r:b=r.read(CAP+1);rec={'url':url,'final_url':r.geturl(),'http_status':r.status,'Content_Type':r.headers.get('Content-Type'),'bytes':len(b),'sha256':sha(b)}
 assert len(b)<=CAP,'Response>8MiB; not absence'
 SOURCE.mkdir(parents=True,exist_ok=True);(SOURCE/label).write_bytes(b);rec['saved']=str(SOURCE/label);return b,rec
def safe(label,fn):
 print('EMC_SOURCE_STEP '+label,flush=True)
 try:return {'name':label,'status':'completed','result':fn()}
 except Exception as e:return {'name':label,'status':'error','error_type':type(e).__name__,'error':str(e)}
_single_source_fetch=fetch
def fetch(url,label):
 import http.client,time,urllib.error
 for attempt in range(3):
  try:return _single_source_fetch(url,label)
  except (http.client.HTTPException,urllib.error.URLError,ConnectionError,TimeoutError):
   if attempt==2:raise
   time.sleep(1+attempt)
def jsonget(url,label):b,r=fetch(url,label);r['metadata']=json.loads(b);return r
def xlsx_tables(b):
 z=zipfile.ZipFile(io.BytesIO(b));ss=[]
 if 'xl/sharedStrings.xml' in z.namelist():ss=[''.join(n.itertext()) for n in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
 rel={x.attrib['Id']:x.attrib['Target'] for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))};tables=[]
 for s in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',NS):
  target=rel[s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']];path=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target);rows=[];styles={}
  for row in ET.fromstring(z.read(path)).findall('m:sheetData/m:row',NS):
   cells={}
   for c in row.findall('m:c',NS):
    label=re.match('[A-Z]+',c.attrib['r']).group();idx=0
    for char in label:idx=idx*26+ord(char)-64
    node=c.find('m:v',NS);val=node.text if node is not None else None
    if c.attrib.get('t')=='s' and val is not None:val=ss[int(val)]
    elif c.attrib.get('t')=='inlineStr':val=''.join(c.find('m:is',NS).itertext())
    cells[idx-1]=val
    if 's' in c.attrib:styles[c.attrib['r']]=c.attrib['s']
   if cells:rows.append([cells.get(i) for i in range(max(cells)+1)])
  tables.append({'sheet':s.attrib['name'],'n_rows':len(rows),'rows':rows,'cell_style_indices':styles})
 return {'tables':tables,'numeric_interpretation':'Preserve numeric/date serial strings+styles; no inferred clinical dates'}
def imc_metadata():
 b,r=fetch(MCD_BASE+'metadata_STS.xlsx','biostudies1555-metadata_STS.xlsx');assert len(b)==24478;r.update(xlsx_tables(b));return r
def author_annotations():
 repo='https://raw.githubusercontent.com/svanoost/immunogenic-features-of-ups-and-mfs/bd1417ecee3c0d7ea7724c05c11c6c02ab3e9465/input_files/'
 pins={'IMC_sample_annotation.tsv':'94d94ba9d817ef7d1d754fca0940f4fef768a820','IMC_pre_post_sample_annotation.tsv':'ffb7bc68b8a8d2b8e0f723aa5739f18397f799d0','phenotype_annotations.tsv':'1b68b992eb62f00ac49d139e009ae7b7eb598af5'};out=[]
 for name,pin in pins.items():
  b,r=fetch(repo+name,name);assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\x00'+b).hexdigest()==pin
  rows=list(csv.DictReader(io.StringIO(b.decode()),delimiter='\t'));r.update(Git_blob=pin,rows=rows,row_count=len(rows))
  if 'Pat_ID' in (rows[0] if rows else {}):r['unique_patients']=len({x['Pat_ID'] for x in rows});r['diagnosis_counts']=dict(collections.Counter(x.get('Diagnosis') for x in rows))
  out.append(r)
 return out
def supplements_zip(pmcid,label):
 b,r=fetch('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/supplementaryFiles',label+'-'+pmcid+'-supplements.zip');z=zipfile.ZipFile(io.BytesIO(b));r['members']=[{'name':i.filename,'bytes':i.file_size,'compressed':i.compress_size} for i in z.infolist()];r['small_workbooks']=[]
 for i in z.infolist():
  if i.filename.lower().endswith('.xlsx') and i.file_size<=2*1024*1024:
   raw=z.read(i);record={'name':i.filename,'bytes':len(raw),'sha256':sha(raw),**xlsx_tables(raw)}
   for t in record['tables']:
    if len(t['rows'])>500:t['rows']=t['rows'][:50];t['display_truncated']=True;t['cell_style_indices']={}
   r['small_workbooks'].append(record)
 return r
def primary_xml(pmcid,label):
 b,r=fetch('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/fullTextXML',label+'-'+pmcid+'.xml');root=ET.fromstring(b);sections=[]
 for sec in root.iter('sec'):
  heading='; '.join(''.join(t.itertext()) for t in sec.findall('title'));text=' '.join(sec.itertext())
  if re.search(r'access|availab|deposit|coordinate|segment|phenotyp|single.cell|GEO|EGA|clinical|cohort|region of interest|spatial',heading+' '+text,re.I):sections.append({'heading':heading,'text':text[:20000]})
 links=[]
 for e in root.iter():
  if e.tag.split('}')[-1] in ['supplementary-material','ext-link']:links.append({'tag':e.tag,'attributes':{k.split('}')[-1]:v for k,v in e.attrib.items()},'text':' '.join(e.itertext())[:1000]})
 r.update(pmcid=pmcid,selected_primary_sections=sections,supplement_and_external_links=links);r['supplement_zip_manifest']=safe(label+'-'+pmcid+'-supplements',lambda:supplements_zip(pmcid,label));return r
def publication(label,query,title):
 search='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':query,'format':'json','resultType':'core','pageSize':5});rec=jsonget(search,label+'-epmc-search.json');hits=rec['metadata'].get('resultList',{}).get('result',[]);rec['primary_texts']=[]
 for row in hits:
  pmcid=row.get('pmcid')
  if pmcid:rec['primary_texts'].append(safe(label+'-'+pmcid,lambda pmcid=pmcid:primary_xml(pmcid,label)))
 if not hits and title:rec['crossref_title_lookup']=safe(label+'-crossref',lambda:jsonget('https://api.crossref.org/works?'+urllib.parse.urlencode({'query.title':title,'rows':5}),label+'-crossref.json'))
 return rec
def pacini_project():
 rec=jsonget('https://api.figshare.com/v2/projects/78252/articles?page_size=100','pacini78252-project-articles.json');listing=rec['metadata'];assert isinstance(listing,list);rec['article_manifests']=[]
 for item in listing[:100]:
  aid=int(item['id']);rec['article_manifests'].append(safe('pacini-'+str(aid),lambda aid=aid:jsonget('https://api.figshare.com/v2/articles/'+str(aid),'pacini-'+str(aid)+'.json')))
 rec['listing_truncated']=len(listing)>100;return rec
def scpca_metadata():
 base='https://api.scpca.alexslemonade.org/v1/';records=[safe('scpca-project-options',lambda:jsonget(base+'project-options/','scpca-project-options.json'))]
 for diagnosis in ['Ewing Sarcoma','Rhabdomyosarcoma']:
  query=urllib.parse.urlencode({'limit':2000,'diagnosis':diagnosis,'has_single_cell_data':'true','includes_anndata':'true'});records.append(safe('scpca-'+diagnosis,lambda query=query,diagnosis=diagnosis:jsonget(base+'samples/?'+query,'scpca-'+diagnosis.replace(' ','-')+'-samples.json')))
 return {'scope':'PublicmetadataGETonly,no terms/token/email/download. Alternatecohort; filtersrequireAPIvalidation','requests':records}
def actual_filelists():
 pins=[('S-BIAD1555','IMC/Files_list_STS.json','875d37478c701ba5bb4d7cf0c365317e99f8d06f3515e6191ed4e6ca47e517a2'),('S-BIAD1597','EWS_Opal/Panel2.json','9c851cfd2bc866fba1c84ea3ac8cd541db0c790c7e8a82678c056438aaee5073'),('S-BIAD1597','EWS_Opal/Panel3.json','a5431c748b890c073fb05b7d5b652f1d32425543c66393e7c905c98008055463')];out=[]
 for acc,path,pin in pins:
  r=jsonget('https://www.ebi.ac.uk/biostudies/files/'+acc+'/'+path,acc+'-'+Path(path).name);assert r['sha256']==pin;out.append(r)
 allrows=[f for r in out for f in r['metadata']]
 for url,size in PILOTS:
  path=url.split('/S-BIAD1597/')[1];found=[r for r in allrows if r.get('path')==path];assert len(found)==1 and int(found[0]['size'])==size
 for name,size in MCD_FILES:
  found=[r for r in allrows if r.get('path')=='IMC/'+name];assert len(found)==1 and int(found[0]['size'])==size
 return out
def main():
 OUT.mkdir(parents=True,exist_ok=True);SOURCE.mkdir(parents=True,exist_ok=True)
 results=[safe('pinned-BioStudies-filelists',actual_filelists),safe('UPS-MFS-clinical-workbook',imc_metadata),safe('UPS-MFS-author-annotations',author_annotations)]
 studies=[('pediatric-atlas','TITLE:"A single-cell atlas of cancer-educated ecotypes across high-risk pediatric sarcomas"','A single-cell atlas of cancer-educated ecotypes across high-risk pediatric sarcomas'),('UPS-MFS-primary','DOI:10.1007/s00262-025-04123-y',None),('Ewing-primary','TITLE:"Proteomic landscape of Ewing sarcoma primary tumors and metastases"','Proteomic landscape of Ewing sarcoma primary tumors and metastases')]
 for label,query,title in studies:results.append(safe(label,lambda label=label,query=query,title=title:publication(label,query,title)))
 results.append(safe('pediatric-Zenodo-exact-title',lambda:jsonget('https://zenodo.org/api/records?'+urllib.parse.urlencode({'q':'title:"A single-cell atlas of cancer-educated ecotypes across high-risk pediatric sarcomas"','size':25}),'pediatric-zenodo-search.json')))
 results.extend([safe('ScPCA-alternate-metadata',scpca_metadata),safe('Pacini-project78252',pacini_project)])
 for name,size in MCD_FILES:results.append(safe('MCD-'+name,lambda name=name,size=size:probe_mcd(MCD_BASE+name,size)))
 for url,size in PILOTS:results.append(safe('TIFF-'+url.split('/')[-2]+'-'+Path(url).name,lambda url=url,size=size:probe_tiff(url,size)))
 out={'schema':'emc-scientific-source-access-followthrough/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':results,'scope':['Source metadata/primaries/processed-export search +rawpixel pilots','Wrappercompletiondoesnotmeanallsourcessuccessful','Pixelaccessnotcompletedcell/patientanalysis','EwingPSMAantibodyPSMA3(HPA000905),notFOLH1','RestrictedMACSimaimageZenodonotRNAcontrolledaccessproof']}
 (OUT/'scientific-source-access-followthrough.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print('EMC_SOURCE_ACCESS_FOLLOWTHROUGH_BEGIN');print(json.dumps(out,separators=(',',':'),allow_nan=False));print('EMC_SOURCE_ACCESS_FOLLOWTHROUGH_END')
if __name__=='__main__':main()
