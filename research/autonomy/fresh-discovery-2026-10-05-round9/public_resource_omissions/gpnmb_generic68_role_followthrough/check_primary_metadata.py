import sys
if '--fetch' not in sys.argv:
    raise SystemExit('Acquisition is disabled by default. Use validate_cached_sources.py for offline replay; do not repeat unchanged official requests.')
"""Exact source publication availability only; no title/abstract/mechanism/values."""
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import urllib.parse,json,hashlib
P=Path(__file__).resolve().parent
query='EXT_ID:41651400 AND SRC:MED';u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':query,'format':'json','resultType':'core','pageSize':'1'})
before={'created_utc':datetime.now(timezone.utc).isoformat(),'actual_source':'PMID41651400 / DOI10.1016/j.canlet.2026.218300 fromlockedGSE299349Series_pubmed_id/web_link','route':u,'scope':'Availability/PMCID/DOI/officialfulltext/supplementURL metadata only; title/abstract/scientificsummary/mechanismcontents closed. SCstatesno previousbody/denial initsownedgate.','attempts':1,'timeout':10,'cap_bytes':1048576,'stop':'NoOA oraccessdenial meansno alternatearticle/preprint/sourcebody; only genuinelyauthorreleasedmetadata manifests maybetested.'}
(P/'PRIMARY-AVAILABILITY-QUERY-FROZEN.json').write_text(json.dumps(before,indent=2)+'\n');r={'started_utc':datetime.now(timezone.utc).isoformat(),'route':u,'attempts':1}
try:
 with urlopen(Request(u,headers={'User-Agent':'EMC-public-source-research/1.0'}),timeout=10) as f:
  b=f.read(1048577);assert len(b)<=1048576;q=P/'raw-cache/PMID41651400-official-metadata.json';q.write_bytes(b);o=json.loads(b);r.update({'http_status':f.status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'cache_path':str(q),'hit_count':o.get('hitCount'),'source_metadata':[{k:x.get(k) for k in ['id','source','pmid','pmcid','doi','isOpenAccess','inPMC','inEPMC','hasSuppl','fullTextUrlList','pubTypeList']} for x in o.get('resultList',{}).get('result',[])]})
except HTTPError as e:r.update({'http_status':e.code,'error_type':type(e).__name__})
except Exception as e:r.update({'error_type':type(e).__name__,'error':str(e)})
r['closed_utc']=datetime.now(timezone.utc).isoformat();r['scientific_title_abstract_projected']=False;r['new_outcomes']=0
(P/'PRIMARY-AVAILABILITY-RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
