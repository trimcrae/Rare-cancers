"""All-sample SOFT metadata for credible broader/model sources, no matrices."""
import concurrent.futures,json,urllib.parse
from source_followup import repo, ROOT

SERIES=['GSE319327','GSE319124','GSE200529','GSE184118','GSE243381','GSE336655']
if __name__=='__main__':
 urls={x:'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?'+urllib.parse.urlencode({'acc':x,'targ':'self','form':'text','view':'full'}) for x in SERIES}
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rec=list(pool.map(lambda item:repo(*item,limit=2*1024*1024),urls.items()))
 (ROOT/'GEO-CANDIDATE-SELF-RECEIPTS.json').write_text(json.dumps(rec,indent=2)+'\n')
 for r in rec:print(r['id'],r.get('status',r.get('error')),r.get('bytes'))
