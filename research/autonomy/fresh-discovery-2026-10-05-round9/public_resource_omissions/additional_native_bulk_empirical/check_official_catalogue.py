"""Official OA catalogue metadata for the genuine unresolved published supplementary file."""
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import json,hashlib,xml.etree.ElementTree as ET
P=Path(__file__).resolve().parent
U='https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC12728484'
am={'created_utc':datetime.now(timezone.utc).isoformat(),'source':'Same actual author-published CAC2-45-1760-s002.xlsx unresolved supplementary source, distinct official publication archive catalogue','first_route':'EuropePMC genuine ZIP returned200butbodyreadtimeout; no archive accepted/no retry ofsamefilehost. This was transport incompleteness, not access denial.','route':U,'expected_new_input':'Official NCBIOA source-package link/size/status metadata. No guessedfile or privatecontent; only actual returnedpubliclink may support one boundedsourcearchive stage.','cap_bytes':262144,'timeout':15,'attempts':1,'before_values':'No gene outcomes; identity/header schema only if genuine authorpackageaccepted. Source loss would close this entire branch.'}
(P/'AMENDMENT-03-OFFICIAL-PUBLIC-ARCHIVE-METADATA.json').write_text(json.dumps(am,indent=2)+'\n')
o={'started_utc':datetime.now(timezone.utc).isoformat(),'url':U,'attempts':1,'cap_bytes':262144}
try:
 with urlopen(Request(U,headers={'User-Agent':'EMC-public-source-research/1.0'}),timeout=15) as r:
  b=r.read(262145);assert len(b)<=262144;q=P/'raw-cache/Ngo-NCBI-OA-catalogue.xml';q.write_bytes(b);o.update({'http_status':r.status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'cache_path':str(q)})
  root=ET.fromstring(b);o['official_records']=[{'pmcid':x.get('id'),'citation':x.get('citation'),'license':x.get('license'),'links':[dict(y.attrib) for y in x.findall('link')]} for x in root.findall('.//record')];o['errors']=[{'code':x.get('code'),'text':x.text} for x in root.findall('.//error')]
except HTTPError as e:o.update({'http_status':e.code,'error_type':type(e).__name__})
except Exception as e:o.update({'error_type':type(e).__name__,'error':str(e)})
o['closed_utc']=datetime.now(timezone.utc).isoformat();o['new_expression_values']=0
(P/'NGO-OFFICIAL-PACKAGE-CATALOGUE.json').write_text(json.dumps(o,indent=2)+'\n');print(json.dumps(o,indent=2))
