import json,io,zipfile,hashlib,re,datetime
from pathlib import Path
import spatial_marker_followthrough_actual as sm
import scientific_source_access_followthrough as src
import atlas_panel_extension as atlas
OUT=sm.OUT;OUT.mkdir(parents=True,exist_ok=True)
PEDS=[('a45759fd4aaaf001e2897ff2.xlsx',14025,'antibodies'),('878d9cc368e36466cbbbb537.xlsx',16829,'cellranger_metrics'),('383819d0ac9d17d45f6df4d3.xlsx',10333976,'entity_marker_DEG'),('612a1c3ddfcb119bdceef161.xlsx',17665,'TME_abundance'),('22cef30afd9e9b61fdb72a80.xlsx',13732,'ligand_receptor')]
EWING_ZIP_SHA='5d63ebc0d8c922aec62dcab0027a2254af0200dc0c85b01a85ef7f16d4abac7f'
EWING_MEMBERS={'41467_2026_70449_MOESM4_ESM.xlsx':(18803408,'6cbdcfce4c6e64c79b09611f97a6bec30205eea3bc130cfc4ebafd79c653f2e0'),'41467_2026_70449_MOESM6_ESM.xlsx':(20023510,'bfe009bbe5e000e661cf93fd846e2f7a1090a8b265d288b35a735cb89c6e3d89')}
TARGETS=set(['CSPG4','SEMA3C','PPARG','ENO3','NR2F1','NR2F2','NR2F6','PXN','TYMS','H1FX','H1-10','CD3D','CD3E','CD8A','CD68','CD163','HLA-DRA','MRC1','NKX2-2','PSMA3']+sum(atlas.GROUPS.values(),[])+atlas.NR_GENES)
AMENDMENT={'dated_utc':'2026-10-01','target_membership':'Exact historical atlas panel memberships plus 20 explicit source/clinical marker symbols, frozen before these numeric exports','source_units':'Published selected DEG/abundance/interaction/protein exports; original authors already selected/tested genes. These are not raw counts or independently fitted patient-level differential-expression tests.','matching':'Exact complete trimmed cell text only; no split protein groups, optimized signatures, identifier guessing or absence-from-DEG=>RNA-absence inference','clinical':'Actual patient/specimen joins must be audited; binary three-year EFS is not an individual time/event survival record.'}
def sparse_row(row,i):return {'parsed_row_ordinal_1based':i,'cells':{str(j+1):v for j,v in enumerate(row) if v is not None and str(v)!=''}}
def audit_table(table,full=False):
 rows=table['rows'];hits=[];found=set()
 for i,row in enumerate(rows,1):
  matched=sorted({str(v).strip() for v in row if v is not None}&TARGETS)
  if matched:hits.append({**sparse_row(row,i),'exact_target_matches':matched});found.update(matched)
 out={'sheet':table['sheet'],'n_parsed_rows':len(rows),'max_columns':max(map(len,rows),default=0),'first25_rows':[sparse_row(r,i) for i,r in enumerate(rows[:25],1)],'target_hit_rows':hits,'targets_present':sorted(found),'targets_not_in_selected_export':sorted(TARGETS-found),'numeric_interpretation':'Cached Excel numeric/date serial strings and styles preserved; parsed ordinal excludes entirely empty XML rows.'}
 if full:out['all_rows']=[sparse_row(r,i) for i,r in enumerate(rows,1)]
 return out
def write(result,dest):dest.write_text(json.dumps(sm.clean(result),allow_nan=False))
def error(label,e):return {'label':label,'status':'error','error_type':type(e).__name__,'error':str(e),'absence_claim':False}
def main():
 dest=OUT/'public-derived-export-followthrough-actual.json';result={'schema':'emc-public-derived-export-followthrough/1','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'amendment':AMENDMENT,'frozen_targets':sorted(TARGETS),'pediatric':[],'ewing':[],'ScPCA_projects':[],'complete':False};write(result,dest)
 for filename,size,label in PEDS:
  try:
   path,receipt=sm.getfull('https://assets-eu.researchsquare.com/files/rs-10374394/v1/'+filename,'pediatric-'+filename,32*1024**2);assert receipt['bytes']==size;parsed=src.xlsx_tables(path.read_bytes());result['pediatric'].append({'label':label,'status':'retrieved','receipt':receipt,'tables':[audit_table(t,full=label!='entity_marker_DEG') for t in parsed['tables']]})
  except Exception as e:result['pediatric'].append(error(label,e))
  write(result,dest)
 try:
  path,receipt=sm.getfull('https://www.researchsquare.com/article/rs-10374394/v1.pdf?c=1784288974000','pediatric-primary-manuscript.pdf',64*1024**2)
  from pypdf import PdfReader
  text='\n'.join(page.extract_text() or '' for page in PdfReader(path).pages);textpath=OUT/'pediatric-primary-manuscript.txt';textpath.write_text(text);needles=['data availability','accession','controlled','European Genome','GEO','GSE','Zenodo','https://'];snippets=[]
  for needle in needles:
   for m in list(re.finditer(re.escape(needle),text,re.I))[:30]:snippets.append({'needle':needle,'text':text[max(0,m.start()-250):min(len(text),m.end()+1000)]})
  result['pediatric_primary']={'status':'retrieved','receipt':receipt,'text_saved':str(textpath),'text_sha256':hashlib.sha256(textpath.read_bytes()).hexdigest(),'text_chars':len(text),'accessions':sorted(set(re.findall(r'\b(?:GSE\d+|E-MTAB-\d+|EGAS\d+|EGAD\d+|PRJNA\d+)\b',text))),'public_urls':sorted(set(re.findall(r'https?://[^\s<>]+',text))),'source_data_availability_snippets':snippets}
 except Exception as e:result['pediatric_primary']=error('pediatric-primary',e)
 write(result,dest)
 try:
  path,receipt=sm.getfull('https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13111610/supplementaryFiles','ewing-primary-supplements.zip',256*1024**2);result['ewing_supplement_receipt']={**receipt,'frozen_container_sha256':EWING_ZIP_SHA,'container_matches_prior':receipt['sha256']==EWING_ZIP_SHA,'identity_rule':'Both selected full workbook members must match frozen byte sizes and SHA256; regenerated container identity recorded separately'}
  with zipfile.ZipFile(path) as z:
   for name,(size,sha) in EWING_MEMBERS.items():
    candidates=[v for v in z.namelist() if Path(v).name==name];assert len(candidates)==1;raw=z.read(candidates[0]);assert len(raw)==size and hashlib.sha256(raw).hexdigest()==sha;saved=OUT/name;saved.write_bytes(raw);parsed=src.xlsx_tables(raw);tables=[]
    for t in parsed['tables']:
     full=(name.endswith('MOESM4_ESM.xlsx') and not (str(t['sheet']).strip()=='4' or len(t['rows'])>1000)) or (name.endswith('MOESM6_ESM.xlsx') and str(t['sheet']).strip().lower() in ['5bc','6ac','6dg','s6']);tables.append(audit_table(t,full=full))
    result['ewing'].append({'label':name,'status':'retrieved','source_zip_member':candidates[0],'receipt':{'saved':str(saved),'bytes':size,'sha256':sha},'tables':tables});write(result,dest)
 except Exception as e:result['ewing'].append(error('ewing-derived-workbooks',e))
 for project in ['SCPCP000005','SCPCP000015']:
  try:rec=src.jsonget('https://api.scpca.alexslemonade.org/v1/projects/'+project+'/','ScPCA-public-project-'+project);result['ScPCA_projects'].append({'project':project,'status':'retrieved',**rec})
  except Exception as e:result['ScPCA_projects'].append(error(project,e))
  write(result,dest)
 result['complete']=True;write(result,dest);result['full_result']=str(dest);result['full_result_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest();print('EMC_PUBLIC_DERIVED_EXPORT_FOLLOWTHROUGH_BEGIN');print(json.dumps(sm.clean(result),allow_nan=False));print('EMC_PUBLIC_DERIVED_EXPORT_FOLLOWTHROUGH_END')
if __name__=='__main__':main()
