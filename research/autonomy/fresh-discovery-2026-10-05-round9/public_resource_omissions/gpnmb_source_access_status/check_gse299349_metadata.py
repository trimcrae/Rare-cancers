"""One new source-declared all68GSM metadata projection, no biological values or mechanism bodies."""
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import json,hashlib,re
P=Path(__file__).resolve().parent
U='https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE299349&targ=gsm&form=text&view=brief'
r={'started_utc':datetime.now(timezone.utc).isoformat(),'route':U,'timeout_seconds':10,'attempts':1,'expected_source':'Actual GSE29934968declared GSMs, individually uninspected histology/model/treatment/library/procfile map; priorseries/titles retained, notreretrieved','cap_bytes':67108864}
rows=[]
try:
 with urlopen(Request(U,headers={'User-Agent':'EMC-public-source-research/1.0'}),timeout=10) as f:
  b=f.read(67108865);assert len(b)<=67108864
  q=P/'raw-cache/GSE299349-individual-GSM-brief.txt';q.write_bytes(b);r.update({'http_status':f.status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'cache_path':str(q),'final_url':f.geturl()})
  current=None
  for line in b.decode('utf-8').splitlines():
   if line.startswith('^SAMPLE = '):
    current={'GSM':line.split(' = ',1)[1],'identity_attributes':[],'actual_processed_source_links':[]};rows.append(current)
   elif current is not None:
    if line.startswith('!Sample_supplementary_file'):
     current['actual_processed_source_links'].append(line.split(' = ',1)[-1])
    elif line.startswith(('!Sample_geo_accession = ','!Sample_source_name_ch1 = ','!Sample_organism_ch1 = ','!Sample_molecule_ch1 = ','!Sample_platform_id = ')):
     key,value=line.split(' = ',1);current[key.removeprefix('!Sample_')]=value
    elif line.startswith('!Sample_title = '):
     value=line.split(' = ',1)[1]
     if not re.search('fusion|variant|mutation|rearrange|HLA|FAP|glycan|DNA|CNA|STR',value,re.I):current['source_alias_only']=value
     else:current['title_not_projected']='Contains excluded mechanism/content scope; no identity transfer.'
    elif line.startswith('!Sample_characteristics_ch1 = '):
     value=line.split(' = ',1)[1];key=value.partition(':')[0].strip().lower()
     if key in ['cell line','cell type','histology','histological type','tumor type','tissue','tissue type','treatment','treatment condition','sample type','model','disease','diagnosis','passage','gender','sex']:
      if not re.search('HLA|FAP|glycan|DNA|CNA|STR|rearrange|fusion.break|sequence',value,re.I):current['identity_attributes'].append(value)
  r['sample_records']=len(rows);r['schema_ok']=len(rows)==68
except HTTPError as e:r.update({'http_status':e.code,'error_type':type(e).__name__})
except Exception as e:r.update({'error_type':type(e).__name__,'error':str(e)})
r['closed_utc']=datetime.now(timezone.utc).isoformat();r['new_expression_values']=0
(P/'GSE299349-NEW-SAMPLE-METADATA-ACCESS.json').write_text(json.dumps(r,indent=2)+'\n')
if rows:(P/'GSE299349-ALL68-EVALUATED-SOURCE-FIELDS.json').write_text(json.dumps({'created_utc':r['closed_utc'],'raw_source_sha256':r.get('sha256'),'fields_scope':'Source/identity/condition/assay/filelinks only. Aliases are not histotype authentication; no mechanism/protocol/design/sequence/quantities projected.','samples':rows},indent=2)+'\n')
print(json.dumps(r,indent=2));print('explicit_EMC_identity_rows',json.dumps([x for x in rows if any(re.search('extraskeletal.myxoid.chondrosarcoma|\\bEMC\\b',a,re.I) for a in x['identity_attributes'])]))
