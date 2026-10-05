"""One genuine published supplement bundle, schema only; no expression cell projection."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,io
from urllib.request import Request,urlopen
from urllib.error import HTTPError
P=Path(__file__).resolve().parent
U='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12728484/supplementaryFiles'
cap=64*1024**2
am={'created_utc':datetime.now(timezone.utc).isoformat(),'actual_author_attachment':'CAC2-45-1760-s002.xlsx, named in cached primary SupportingInformation/DataAvailability','route':U,'prior_trace':'R9 FB states no attachment/bundle request in owned gate. Targeted filename/API-route search of centrally retained R6/R8/R9 compact records finds only original NgoDA pointer; this is scoped evidence, not whole-cache proof. Previous authorrepo and request-only EGA routes reused and not repeated.','finite_route':'One ordinary EuropePMC published supplement service request for this primary; public source route, not guessed filename/internal API or bypass.','cap_bytes':cap,'timeout_seconds':20,'attempts':1,'before_values':'Inspect member filenames/hashes and workbook sheet/header/identity fields only; no numeric outcomes/wholematrices.','one_empirical_question_if_ready':'Additional source-qualified GPNMB–LGFMS RNA reproducibility for localization sampling. No fixed-marker covariance rescue. Require all authentic EMC and compatible LGFMS conditions, source overlap/preparation/units; unknown donor overlap means descriptive additional context, not independent patients.','stop':'Any denied/auth/private response or no actualcrosswalk/data file ends this route without retry/alternate guess. Genuine supplement source-dependent results do not confer discovery.'}
(P/'AMENDMENT-02-GENUINE-SUPPLEMENT-AND-ONE-QUESTION.json').write_text(json.dumps(am,indent=2)+'\n')
receipt={'started_utc':datetime.now(timezone.utc).isoformat(),'url':U,'cap_bytes':cap,'attempts':1}
try:
 with urlopen(Request(U,headers={'User-Agent':'EMC-public-source-research/1.0'}),timeout=20) as r:
  receipt.update({'http_status':r.status,'content_type':r.headers.get('Content-Type'),'final_url':r.geturl()})
  if r.status==200:
   b=bytearray()
   while True:
    c=r.read(65536)
    if not c:break
    b.extend(c)
    if len(b)>cap:raise ValueError('Source exceeds64MiB, stopped; notaccepted')
   q=P/'raw-cache/Ngo-primary-supplement-bundle';q.write_bytes(b)
   receipt.update({'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'cache_path':str(q),'valid_zip':zipfile.is_zipfile(q)})
   if receipt['valid_zip']:
    with zipfile.ZipFile(q) as z:
     receipt['published_members']=[{'name':x.filename,'bytes':x.file_size,'compressed_bytes':x.compress_size} for x in z.infolist()]
     selected=[x for x in z.infolist() if x.filename.endswith('CAC2-45-1760-s002.xlsx')]
     if len(selected)==1:
      x=selected[0];payload=z.read(x);dest=P/'raw-cache/CAC2-45-1760-s002.xlsx';dest.write_bytes(payload)
      receipt['selected_workbook']={'name':x.filename,'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'cache_path':str(dest),'valid_ooxml':zipfile.is_zipfile(dest)}
except HTTPError as e:receipt.update({'http_status':e.code,'content_type':e.headers.get('Content-Type'),'final_url':e.geturl(),'error_type':type(e).__name__})
except Exception as e:receipt['error_type']=type(e).__name__;receipt['error']=str(e)
receipt['closed_utc']=datetime.now(timezone.utc).isoformat();receipt['expression_values_read']=0
(P/'NGO-PUBLISHED-SUPPLEMENT-ACCESS.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
