import json,concurrent.futures
from fetch_sources import D,get
JOBS={
 'novruzov2026.xml':'https://pmc-oa-opendata.s3.amazonaws.com/PMC12963560.1/PMC12963560.1.xml',
 'novruzov2026-s3-list.xml':'https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=PMC12963560.1/',
 'liu2026-publisher.html':'https://academic.oup.com/bjr/article-abstract/99/1184/1598/8677614'
}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(get,JOBS.items()))
 (D/'2026-fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
