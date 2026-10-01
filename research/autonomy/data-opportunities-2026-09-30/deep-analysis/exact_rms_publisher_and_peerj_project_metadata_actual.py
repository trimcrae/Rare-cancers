import json,re,io,gzip,csv,time,hashlib,datetime,urllib.request as U,urllib.parse as Q,xml.etree.ElementTree as E,zipfile
from pathlib import Path
import numpy as np,pandas as pd,fitz
import spatial_marker_followthrough_actual as sm
import peerj_expression_diagnostic_actual as p
import peerj_fullmatrix_export_forensics_actual as fx
import scientific_source_access_followthrough as src
OUT=sm.OUT
PROJECT='PRJNA1357027';DOI='10.1016/j.devcel.2022.04.003'
def receipt(path):return {'saved':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def get(url,label):
 rec={'url':url,'label':label};raw=None
 for attempt in range(2):
  try:
   with U.urlopen(U.Request(url,headers={'User-Agent':'public-sarcoma-reanalysis/1','Accept-Encoding':'identity'}),timeout=40) as r:raw=r.read(32*1024*1024+1);rec.update(final_url=r.geturl(),http_status=r.status,content_type=r.headers.get('Content-Type'))
   assert len(raw)<=32*1024*1024
   break
  except Exception as e:
   rec.update(error_type=type(e).__name__,error=str(e),absence_claim=False)
   if attempt==0:time.sleep(1)
 if raw is None:return None,rec
 rec.pop('error',None);rec.pop('error_type',None)
 path=OUT/label;path.write_bytes(raw);rec.update(receipt(path));decoded=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
 rec.update(decoded_bytes=len(decoded),decoded_sha256=hashlib.sha256(decoded).hexdigest());return decoded,rec
def nc(db,op,params,label):
 time.sleep(.4);return get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'+op+'.fcgi?'+Q.urlencode({'db':db,**params}),label)
def text(node):return ' '.join(node.itertext()).strip() if node is not None else ''
def ids(value):return sorted(set(re.findall(r'(?<![A-Za-z0-9])Si\d+(?![A-Za-z0-9])',str(value))))
def attrs(node):
 return [{k:text(v.find('./'+tag)) for k,tag in [('tag','TAG'),('value','VALUE'),('units','UNITS')]} for v in node.findall('.//SAMPLE_ATTRIBUTE')]
def main():
 OUT.mkdir(parents=True,exist_ok=True);pub={'exact_DOI':DOI,'asset_attempts':[]};piis=[];b,r=nc('pubmed','efetch',{'id':'35483358','retmode':'xml'},'RMS-PMID35483358.xml');pub['pubmed_receipt']=r
 if b:
  root=E.fromstring(b);lit=[text(x) for x in root.findall('.//ArticleId') if x.attrib.get('IdType')=='doi'];assert DOI in lit
  pub['article_ids']=[{'type':x.attrib.get('IdType'),'value':text(x)} for x in root.findall('.//ArticleId')]
  piis.extend(re.sub(r'[^A-Za-z0-9]','',text(x)) for x in root.findall('.//ArticleId') if x.attrib.get('IdType')=='pii')
 b,r=get('https://api.crossref.org/works/'+Q.quote(DOI,safe=''),'RMS-exact-DOI-crossref.json');pub['crossref_receipt']=r
 if b:
  d=json.loads(b)['message'];assert d['DOI'].lower()==DOI;pub['crossref_primary_links']=d.get('link',[])
  for x in d.get('link',[]):piis+=re.findall(r'S\d{15}[0-9X]',str(x))
 piis=sorted(set(x for x in piis if re.fullmatch(r'S\d{15}[0-9X]',x)));pub['exact_primary_PIIs']=piis
 if len(piis)==1:
  for k in range(1,17):
   ext='pdf' if k==1 else 'xlsx';name=f'RMS-ARS-mmc{k}.{ext}';url=f'https://ars.els-cdn.com/content/image/1-s2.0-{piis[0]}-mmc{k}.{ext}';b,r=get(url,name);item={'NIHMS_attachment':f'NIHMS1800632-supplement-{k}.{ext}','route_rule':'ExactPII/publicARS/declaredorder;realcontents required','receipt':r};pub['asset_attempts'].append(item)
   if not b:continue
   try:
    if ext=='pdf':
     assert b.startswith(b'%PDF');doc=fitz.open(stream=b,filetype='pdf');full='\n'.join(page.get_text() for page in doc);q=OUT/'RMS-ARS-mmc1-complete-text.txt';q.write_text(full);item.update(status='real_PDF',pages=len(doc),complete_text=receipt(q),annotation_context=[full[max(0,m.start()-150):m.end()+300] for m in list(re.finditer(r'cell state|myoblast|paraxial|barcode|clinical|patient',full,re.I))[:30]]);doc.close()
    else:
     assert b.startswith(b'PK') and 'xl/workbook.xml' in zipfile.ZipFile(io.BytesIO(b)).namelist();book=pd.ExcelFile(io.BytesIO(b));sheets=[]
     for j,sheet in enumerate(book.sheet_names):
      df=pd.read_excel(book,sheet_name=sheet,header=None);q=OUT/f'RMS-ARS-mmc{k}-sheet{j}.tsv';df.to_csv(q,sep='\t',index=False,header=False);strings=df.astype(str);joined='\n'.join(strings.apply(lambda row:'\t'.join(row),axis=1));sheets.append({'sheet':sheet,'shape':list(df.shape),'full_table':receipt(q),'first8_rows':json.loads(df.head(8).to_json(orient='values',date_format='iso')),'model_mentions':sorted(set(re.findall(r'SJRHB\d+',joined))),'annotation_terms':sorted(set(m.group().lower() for m in re.finditer(r'barcode|cell state|myoblast|paraxial|myocyte|malignant|histolog|patient',joined,re.I)))})
     item.update(status='real_XLSX',all_sheets=sheets)
   except Exception as e:item.update(status='not_valid_source_asset',error_type=type(e).__name__,error=str(e),absence_claim=False)
 else:pub['asset_disposition']='Unique exactPII unresolved'
 meta={'exact_project':PROJECT,'receipts':[]};ena=[];packages=[];runinfo=[];bs=[]
 b,r=get('https://www.ebi.ac.uk/ena/portal/api/returnFields?result=read_run&format=json','PeerJ-ENA-read_run-fields.json');meta['receipts'].append(r)
 if b:
  catalog=json.loads(b);available={x.get('columnId') for x in catalog};wanted=['run_accession','experiment_accession','sample_accession','secondary_sample_accession','study_accession','sample_alias','sample_title','experiment_alias','experiment_title','library_name','library_strategy','library_layout','read_count','base_count'];fields=[f for f in wanted if f in available];meta['ENA_fields']=fields
  url='https://www.ebi.ac.uk/ena/portal/api/filereport?'+Q.urlencode({'accession':PROJECT,'result':'read_run','fields':','.join(fields),'format':'tsv','download':'false'})
  b,r=get(url,'PeerJ-project-ENA-metadata.tsv');meta['receipts'].append(r)
  if b:ena=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig')),delimiter='\t'))
 b,r=nc('sra','esearch',{'term':PROJECT+'[BioProject]','retmode':'json','retmax':'1000'},'PeerJ-project-SRA-search.json');meta['receipts'].append(r)
 if b:
  search=json.loads(b)['esearchresult'];assert int(search['count'])<=1000;uids=search['idlist'];meta['SRA_exact_query_count']=int(search['count'])
  if uids:
   b,r=nc('sra','efetch',{'id':','.join(uids),'retmode':'xml'},'PeerJ-project-SRA-packages.xml');meta['receipts'].append(r)
   if b:
    for pack in E.fromstring(b).findall('.//EXPERIMENT_PACKAGE'):
     sample=pack.find('./SAMPLE');exp=pack.find('./EXPERIMENT');study=pack.find('./STUDY');runs=pack.findall('.//RUN_SET/RUN');bi=[text(v) for v in sample.findall('./IDENTIFIERS/EXTERNAL_ID') if 'biosample' in str(v.attrib.get('namespace','')).lower()] if sample is not None else []
     packages.append({'attributes':attrs(sample) if sample is not None else [],'sample':sample.attrib if sample is not None else {},'sample_title':text(sample.find('./TITLE')) if sample is not None else '', 'experiment':exp.attrib if exp is not None else {},'experiment_title':text(exp.find('./TITLE')) if exp is not None else '', 'study':study.attrib if study is not None else {},'biosample_ids':bi,'runs':[v.attrib for v in runs]})
   b,r=nc('sra','efetch',{'id':','.join(uids),'rettype':'runinfo','retmode':'text'},'PeerJ-project-SRA-runinfo.csv');meta['receipts'].append(r)
   if b:runinfo=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
 access=sorted(set([v for q in packages for v in q['biosample_ids']]+[v for row in ena for k,v in row.items() if k in ['sample_accession','secondary_sample_accession'] and re.fullmatch(r'SAM[NED][A-Z]*\d+',v or '')]))
 if access:
  b,r=nc('biosample','esearch',{'term':' OR '.join(a+'[Accession]' for a in access),'retmode':'json','retmax':'1000'},'PeerJ-linked-BioSample-search.json');meta['receipts'].append(r)
  if b:
   sr=json.loads(b)['esearchresult'];assert int(sr['count'])<=1000;uids=sr['idlist']
   if uids:
    b,r=nc('biosample','efetch',{'id':','.join(uids),'retmode':'xml'},'PeerJ-linked-BioSample-records.xml');meta['receipts'].append(r)
    if b:
     for node in E.fromstring(b).iter('BioSample'):
      ac=node.attrib.get('accession');assert ac in access
      bs.append({'accession':ac,'title':text(node.find('./Description/Title')),'identifiers':[{'attributes':v.attrib,'value':text(v)} for v in node.findall('./Ids/Id')],'attributes':[{'attributes':v.attrib,'value':text(v)} for v in node.findall('./Attributes/Attribute')]})
 bsmap={v['accession']:v for v in bs};pkgmap={r.get('accession'):q for q in packages for r in q['runs']};infomap={v.get('Run'):v for v in runinfo}
 for row in ena:
  ac=row.get('run_accession');q=pkgmap.get(ac,{});bio=[row.get('sample_accession'),row.get('secondary_sample_accession')]+q.get('biosample_ids',[]);row['literal_Si_ids']=ids(json.dumps([row,q,[bsmap[a] for a in bio if a in bsmap]]))
 for q in packages:q['literal_Si_ids']=ids(json.dumps([q,[bsmap[a] for a in q['biosample_ids'] if a in bsmap]]))
 meta.update(all_ENA_records=ena,all_SRA_packages=packages,all_SRA_runinfo=runinfo,BioSample_records=bs)
 qualified=[];join=[]
 for si in p.IDS:
  rows=[r for r in ena if r['literal_Si_ids']==[si]];provider='ENA_read_count';counts=[int(r.get('read_count') or 0) for r in rows];samples={r.get('sample_accession') for r in rows};exps={r.get('experiment_accession') for r in rows};runs=[r.get('run_accession') for r in rows]
  if not rows:
   qs=[q for q in packages if q['literal_Si_ids']==[si]];rr=[r for q in qs for r in q['runs']];runs=[r.get('accession') for r in rr];counts=[int(infomap.get(a,{}).get('spots') or 0) for a in runs];samples={q['sample'].get('accession') for q in qs};exps={q['experiment'].get('accession') for q in qs};provider='SRA_spots_not_reads'
  ok=bool(runs) and len(runs)==len(set(runs)) and len(samples)==1 and None not in samples and '' not in samples and len(exps)==1 and None not in exps and '' not in exps and all(c>0 for c in counts)
  row={'specimen':si,'provider_units':provider,'run_accessions':runs,'sample_accessions':sorted(str(x) for x in samples),'experiment_accessions':sorted(str(x) for x in exps),'run_counts':counts,'qualified':ok,'summed_quantity':sum(counts) if ok else None};join.append(row)
  if ok:qualified.append(row)
 meta['exact_Si_quantity_joins']=join;tests=[]
 groups=[[r for r in qualified if r['provider_units']==unit] for unit in ['ENA_read_count','SRA_spots_not_reads']];qualified=next((g for g in groups if len(g)>=8),[]);meta['diagnostic_specimens']=[r['specimen'] for r in qualified]
 if len(qualified)>=8:
  path,rec=p.get();book=src.xlsx_tables(path.read_bytes());sheet=next(t for t in book['tables'] if t['sheet']=='EMC_Gene-expression_Log2CPM');rows=sheet['rows'];assert rows[0]==['symbol']+p.IDS;V=np.array([[float(v) for v in row[1:]] for row in rows[1:]]);assert V.shape==(9500,12) and np.isfinite(V).all();symbols=[str(row[0]) for row in rows[1:]];chosen=[r['specimen'] for r in qualified];ix=[p.IDS.index(si) for si in chosen];z=np.log10([r['summed_quantity'] for r in qualified])[:,None];saved_ids=p.IDS
  try:
   p.IDS=chosen
   for j,(left,right) in enumerate(p.PAIRS):assert symbols.count(left)==symbols.count(right)==1;tests.append(fx.test(V[symbols.index(left),ix],V[symbols.index(right),ix],z,['log10_actual_source_quantity'],'actual_source_count_qualification',left,right,2026100160+j))
  finally:p.IDS=saved_ids
  fx.bh(tests,'approximate_conditional_residual_permutation_p','BH_q_fixed3_source_qualification',3);meta['frozen_expression_receipt']=rec
 meta['all3_quantity_diagnostics']=tests;meta['quantity_disposition']='LiteralSi/accession joins;selected3gene diagnostic;no outcomes'
 out={'schema':'emc-exact-publisher-project-followthrough/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'RMS_publisher':pub,'PeerJ_project_metadata':meta,'limits':['No FASTQ acquired; no guessed labels/outcomes','Literalclinicalfields only','Source/assay/selection limits remain']}
 q=OUT/'exact-RMS-publisher-and-PeerJ-project-metadata-actual.json';q.write_text(json.dumps(sm.clean(out),allow_nan=False));print('EMC_EXACT_PUBLISHER_PROJECT_FOLLOWTHROUGH_BEGIN');print(json.dumps(sm.clean(out),allow_nan=False));print('EMC_EXACT_PUBLISHER_PROJECT_FOLLOWTHROUGH_END')
if __name__=='__main__':main()
