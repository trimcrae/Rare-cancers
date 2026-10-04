"""Evaluate every library in candidate series from source metadata, not values."""
import concurrent.futures, json, re, urllib.parse
from source_followup import ROOT,repo
from source_pilot import retrieve
SERIES=['GSE319327','GSE319124','GSE200529','GSE184118','GSE243381','GSE336655']
FIELDS=('title','source_name_ch1','characteristics_ch1','description','extract_protocol_ch1','supplementary_file','relation','library_strategy','status')
if __name__=='__main__':
 ids={};byseries={}
 for acc in SERIES:
  text=(ROOT/'sources'/(acc+'.json')).read_text()
  gsm=re.findall(r'^!Series_sample_id = (GSM\d+)',text,re.M);byseries[acc]=gsm
  for s in gsm:ids[s]='https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?'+urllib.parse.urlencode({'acc':s,'targ':'self','form':'text','view':'full'})
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rec=list(pool.map(lambda x:repo(*x,limit=256*1024),ids.items()))
 out={}
 for r in rec:
  s=r['id'];row={'accession':s,'source_sha256':r.get('sha256'),'source_status':r.get('status',r.get('error'))}
  if 'path' in r:
   text=(ROOT/r['path']).read_text()
   for f in FIELDS: row[f]=re.findall(r'^!Sample_'+f+r' = (.*)',text,re.M)
  out[s]=row
 (ROOT/'GSM-SOURCE-RECEIPTS.json').write_text(json.dumps(rec,indent=2)+'\n')
 (ROOT/'GSM-ELIGIBILITY-OBSERVATIONS.json').write_text(json.dumps({'by_series':byseries,'libraries':out},indent=2)+'\n')
 r,s=retrieve(('epmc_sctumor_primary','EXT_ID:42124572 AND SRC:MED'))
 (ROOT/'SCTUMOR-PRIMARY-SEARCH.json').write_text(json.dumps({'receipt':r,'results':s},indent=2)+'\n')
 print('libraries',len(out),'failed',sum('path' not in r for r in rec))
 for r in s:print(r['pmcid'],r['doi'],r['title'])
 for acc,gsm in byseries.items():
  labels={tuple(out[s].get('characteristics_ch1',[])) for s in gsm};print(acc,'n_libraries',len(gsm),'distinct_characteristic_strings',len(labels))
