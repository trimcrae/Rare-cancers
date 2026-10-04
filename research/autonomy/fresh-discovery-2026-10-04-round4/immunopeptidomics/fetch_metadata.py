import json,concurrent.futures,urllib.parse
from fetch_sources import D,get
JOBS={
 'pediatric-tableS4.xlsx':'https://pmc-oa-opendata.s3.amazonaws.com/PMC8642810.1/NIHMS1759318-supplement-5.xlsx',
 'jci2023-table1.html':'https://insight.jci.org/articles/view/170324/table/1',
 'jci2023-table2.html':'https://insight.jci.org/articles/view/170324/table/2',
 'jci2023-table3.html':'https://insight.jci.org/articles/view/170324/table/3',
 'pride-search-myxoid.json':'https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects?keyword=myxoid&pageSize=100&page=0',
 'pride-search-sarcoma.json':'https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects?keyword=sarcoma&pageSize=100&page=0',
}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: out=list(pool.map(get,JOBS.items()))
 (D/'metadata-fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 print(json.dumps(out,indent=2))
