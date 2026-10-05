#!/usr/bin/env python3
"""Complete the focused prior-art metadata query; retain original bodies ignored.

No interrupted-content paper is followed. Metadata enumeration is not empirical
coverage. One newly eligible general TLS source is acquired for source gating.
"""
from pathlib import Path
import json, hashlib, datetime, urllib.request, urllib.parse
P=Path(__file__).parent
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def acquire(url,name):
    receipt={'utc':now(),'url':url,'path':'raw/'+name}
    try:
        with urllib.request.urlopen(url,timeout=40) as r:
            body=r.read(4*1024*1024+1)
            assert len(body)<=4*1024*1024,'bounded source limit'
            receipt.update({'status':r.status,'final_url':r.url,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
        (P/'raw'/name).write_bytes(body)
        return receipt,body
    except Exception as e:
        receipt['error']=repr(e)
        return receipt,None
frozen=json.loads((P/'PRECISE-PRIOR-ART-RECEIPT.json').read_text())
first=json.loads((P/'raw/prior_art_precise.json').read_text())
url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':frozen['query'],'format':'json','pageSize':100,'resultType':'core','cursorMark':first['nextCursorMark']})
receipt,body=acquire(url,'prior_art_precise_page2.json')
records=list(first['resultList']['result'])
if body:
    page=json.loads(body);records+=page['resultList']['result']
    receipt.update({'hitCount':page['hitCount'],'returned':len(page['resultList']['result']),'unique_total':len({(x['source'],x['id']) for x in records}),
                    'pagination_complete':len({(x['source'],x['id']) for x in records})==page['hitCount']})
    # Only title/identifier observations from the broad metadata catalogue.
    relevant=[]
    for r in records:
        title=r.get('title','')
        if any(s in title.lower() for s in ['glycan','glycos','hexosamine','fibroblast activation','hla']):continue
        if any(s in title.lower() for s in ['extraskeletal','tertiary lymphoid','macrophage','immune landscape','immune microenvironment']):
            relevant.append({k:r.get(k) for k in ['source','id','pmcid','doi','title','pubYear']})
    (P/'FOCUSED-PRIOR-ART-TITLE-OBSERVATIONS.json').write_text(json.dumps({'utc':now(),'scope':'Only focused candidate identifiers/titles; bibliography is not evaluation of all experiments. Interrupted-content topics excluded without follow-up.','records':relevant},indent=2)+'\n')
(P/'PRECISE-PRIOR-ART-PAGINATION-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
r,b=acquire('https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13255587/fullTextXML','TLS2026-PMC13255587.xml')
(P/'TLS2026-SOURCE-RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'pagination':receipt,'TLS2026':r},indent=2))
