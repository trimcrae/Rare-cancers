import concurrent.futures,json
from fetch_sources import get,D
jobs=[('interobserver-main.html','https://jnm.snmjournals.org/content/64/7/1043'),('timepoint2023.pdf','https://jnm.snmjournals.org/content/jnumed/64/4/618.full.pdf')]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:r=list(p.map(get,jobs))
(D/'supplement-link-fetch-receipts.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
