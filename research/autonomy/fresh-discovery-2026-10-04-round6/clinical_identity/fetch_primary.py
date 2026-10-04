import json,concurrent.futures,urllib.parse
from fetch_sources import D,get
jobs={
 'timepoint-title-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':'TITLE:"Three-Time-Point PET Analysis"','format':'json','resultType':'core'}),
 'hirmas2023.html':'https://jnm.snmjournals.org/content/64/5/711',
 'hirmas2024.html':'https://jnm.snmjournals.org/content/65/3/372',
 'interobserver-repository.html':'https://cris.unibo.it/handle/11585/957757',
 'liver2026.html':'https://link.springer.com/article/10.1007/s44178-026-00295-4'
}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:out=list(p.map(get,jobs.items()))
(D/'primary-fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
