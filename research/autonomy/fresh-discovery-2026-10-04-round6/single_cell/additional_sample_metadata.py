"""Complete newly traced clinical libraries and the pediatric sibling metadata.

No previous series are fetched again. No expression values are downloaded.
"""
import concurrent.futures, json, re, urllib.parse
from source_followup import ROOT,repo
from sample_metadata import FIELDS
SERIES=['GSE318841','GSE313859','GSE313858','GSE279852']
if __name__=='__main__':
 ids={};byseries={}
 for acc in SERIES:
  text=(ROOT/'sources'/(acc+'.json')).read_text()
  gsm=re.findall(r'^!Series_sample_id = (GSM\d+)',text,re.M);byseries[acc]=gsm
  for s in gsm:ids[s]='https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?'+urllib.parse.urlencode({'acc':s,'targ':'self','form':'text','view':'full'})
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rec=list(pool.map(lambda x:repo(*x,limit=128*1024),ids.items()))
 out={}
 for r in rec:
  s=r['id'];row={'accession':s,'source_sha256':r.get('sha256'),'source_status':r.get('status',r.get('error'))}
  if 'path' in r:
   text=(ROOT/r['path']).read_text()
   for f in FIELDS+('data_processing',): row[f]=re.findall(r'^!Sample_'+f+r' = (.*)',text,re.M)
  out[s]=row
 (ROOT/'ADDITIONAL-GSM-SOURCE-RECEIPTS.json').write_text(json.dumps(rec,indent=2)+'\n')
 (ROOT/'ADDITIONAL-GSM-ELIGIBILITY-OBSERVATIONS.json').write_text(json.dumps({'by_series':byseries,'libraries':out},indent=2)+'\n')
 print('libraries',len(out),'failed',sum('path' not in r for r in rec))
 for acc,gsm in byseries.items():print(acc,'libraries',len(gsm))
