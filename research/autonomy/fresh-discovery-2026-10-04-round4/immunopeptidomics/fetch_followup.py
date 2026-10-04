import json,concurrent.futures
from fetch_sources import D,get
JOBS={
 'pediatric-s3-list.xml':'https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=PMC8642810.1/',
 'pride-PXD017130.json':'https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD017130',
 'pride-PXD030304.json':'https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD030304',
 'monash-molbi2026.pdf':'https://www.monash.edu/__data/assets/pdf_file/0011/4242476/Lorne_2026_MoLBi_FINAL.pdf',
 'jci2023-t1.html':'https://insight.jci.org/articles/view/170324/figure/7',
 'jci2023-supp-index.html':'https://insight.jci.org/articles/view/170324/sd/1'
}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: out=list(pool.map(get,JOBS.items()))
 (D/'followup-fetch-receipts.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 print(json.dumps(out,indent=2))
