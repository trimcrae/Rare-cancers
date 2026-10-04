import json,concurrent.futures
from fetch_sources import D,get
JOBS={
 'novruzov2026-supp.pdf':'https://pmc-oa-opendata.s3.amazonaws.com/PMC12963560.1/41824_2026_295_MOESM1_ESM.pdf',
 'ferdinandus2022.xml':'https://pmc-oa-opendata.s3.amazonaws.com/PMC9527500.1/PMC9527500.1.xml',
 'ferdinandus2022-s3-list.xml':'https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=PMC9527500'
}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(get,JOBS.items()))
 (D/'supplement-fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
