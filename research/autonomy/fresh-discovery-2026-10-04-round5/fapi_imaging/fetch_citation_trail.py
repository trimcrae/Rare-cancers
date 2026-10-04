import concurrent.futures,json
from fetch_sources import get,D
jobs={
 'dynamic2021.xml':'https://pmc-oa-opendata.s3.amazonaws.com/PMC7991833.1/PMC7991833.1.xml',
 'kratochwil2019.xml':'https://pmc-oa-opendata.s3.amazonaws.com/PMC6581228.1/PMC6581228.1.xml',
 'pabst2025-lancet.html':'https://www.thelancet.com/journals/lanonc/article/PIIS1470-2045(25)00299-2/fulltext'
}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:out=list(p.map(get,jobs.items()))
(D/'citation-trail-fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
