import json,io,zipfile,hashlib,datetime,re,urllib.parse,xml.etree.ElementTree as ET,collections
from pathlib import Path
import pandas as pd,numpy as np
import spatial_marker_followthrough_actual as sm
import scientific_source_access_followthrough as src
OUT=sm.OUT;DOI='10.1016/j.devcel.2022.04.003'
def rec(p):return {'saved':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def audit_frame(frame,label):
 rows=frame.where(pd.notna(frame),None).values.tolist();flat=[str(v) for row in rows for v in row if v is not None];models=collections.Counter(m for v in flat for m in re.findall(r'\bSJRHB\d+(?:_[A-Za-z0-9]+)*\b',v));accessions=collections.Counter(m for v in flat for m in re.findall(r'\bGSM\d+\b',v));barcode_count=sum(bool(re.fullmatch(r'[ACGT]{12,24}(?:-\d+)?',v)) for v in flat);headers=[]
 for i,row in enumerate(rows[:12]):
  if any(re.search(r'barcode|cell.?type|cell.?state|cluster|sample|specimen|model|patient|fusion|histolog',str(v),re.I) for v in row if v is not None):headers.append({'row_1based':i+1,'literal_cells':row})
 path=OUT/(re.sub(r'[^A-Za-z0-9_.-]','_',label)+'.decoded.tsv');frame.to_csv(path,sep='\t',index=False,header=False);out={'label':label,'shape':list(frame.shape),'decoded_table_receipt':rec(path),'literal_model_mentions':dict(models),'GSM_mentions':dict(accessions),'barcode_like_cell_count':barcode_count,'candidate_literal_header_rows':headers,'first12_rows':rows[:12],'identity_rule':'Literal tokens, no paddingnormalization/inferredlabels'}
 if frame.shape[0]<=500 and frame.shape[1]<=40:out['all_small_source_rows']=rows
 return out
def main():
 OUT.mkdir(parents=True,exist_ok=True);result={'schema':'emc-RMS-exact-primary-annotations/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'ExactoriginalDOI/fullpublicsupplements/allworksheets; sourcetoken/annotationaudit, noinferredlabels','errors':[]};q=src.jsonget('https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':'DOI:'+DOI,'format':'json','resultType':'core','pageSize':5}),'RMS-original-epmc.json');hits=[r for r in q['metadata'].get('resultList',{}).get('result',[]) if r.get('doi','').lower()==DOI];assert len(hits)==1;primary=hits[0];result['exact_primary_record']=primary;result['search_receipt']={k:v for k,v in q.items() if k!='metadata'};pmcid=primary.get('pmcid');result['public_external_links']=[];result['primary_sections']=[];result['supplement_tables']=[]
 if pmcid:
  try:
   b,r=src.fetch('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/fullTextXML','RMS-original-full-primary.xml');root=ET.fromstring(b);result['primary_xml_receipt']=r
   for e in root.iter():
    tag=e.tag.split('}')[-1]
    if tag in ['ext-link','supplementary-material','media']:result['public_external_links'].append({'tag':tag,'attributes':e.attrib,'literal_text':' '.join(e.itertext())})
    if tag=='sec':
     head=' '.join(' '.join(t.itertext()) for t in e.findall('title'));text=' '.join(e.itertext())
     if re.search(r'data availab|code availab|single.cell|single.nucleus|cell.type|cell.state|annotation|lineage|xenograft|fusion',head+' '+text,re.I):result['primary_sections'].append({'heading':head,'literal_text':text})
  except Exception as e:result['errors'].append({'stage':'primaryXML','error_type':type(e).__name__,'error':str(e),'absence_claim':False})
  try:
   p,r=sm.getfull('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid+'/supplementaryFiles','RMS-original-complete-supplements.zip',256*1024**2);result['supplement_zip_receipt']=r
   with zipfile.ZipFile(p) as z:
    result['all_supplement_members']=[{'name':v.filename,'bytes':v.file_size,'compressed_bytes':v.compress_size} for v in z.infolist()]
    for member in z.infolist():
     if not re.search(r'\.(xlsx|xls|csv|tsv|txt)$',member.filename,re.I):continue
     if member.file_size>64*1024**2:result['errors'].append({'stage':'Large numericmember focusedacquisitionpending','member':member.filename,'bytes':member.file_size,'absence_claim':False});continue
     raw=z.read(member);saved=OUT/('RMS-original-'+Path(member.filename).name);saved.write_bytes(raw);item={'member':member.filename,'receipt':rec(saved),'tables':[]};result['supplement_tables'].append(item)
     try:
      if re.search(r'\.xlsx?$',member.filename,re.I):books=pd.read_excel(io.BytesIO(raw),sheet_name=None,header=None);item['tables']=[audit_frame(f,Path(member.filename).stem+'-'+str(s)) for s,f in books.items()]
      elif re.search(r'\.(csv|tsv)$',member.filename,re.I):item['tables']=[audit_frame(pd.read_csv(io.BytesIO(raw),sep='\t' if member.filename.lower().endswith('.tsv') else',',header=None,dtype=str),Path(member.filename).stem)]
      else:text=raw.decode('utf-8',errors='replace');item['text_chars']=len(text);item['literal_text']=text if len(text)<=300000 else None;item['external_urls']=sorted(set(re.findall(r'https?://[^\s<>]+',text)))
     except Exception as e:item['parse_error']={'error_type':type(e).__name__,'error':str(e),'absence_claim':False}
  except Exception as e:result['errors'].append({'stage':'Fullpublicsupplements','error_type':type(e).__name__,'error':str(e),'absence_claim':False})
 else:result['errors'].append({'stage':'NoindexedPMC','free_full_text_urls':primary.get('fullTextUrlList'),'absence_claim':False})
 result['needs_finite_followthrough']='Inspectliteralcode/data links andactualbarcode/type/modeljoins beforeannoabsenceclaim';dest=OUT/'RMS-exact-primary-annotations-actual.json';dest.write_text(json.dumps(sm.clean(result),allow_nan=False,default=str));print('EMC_RMS_PRIMARY_ANNOTATIONS_BEGIN');print(json.dumps(sm.clean(result),allow_nan=False,default=str));print('EMC_RMS_PRIMARY_ANNOTATIONS_END')
if __name__=='__main__':main()
