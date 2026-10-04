"""Bounded public-source eligibility searches; no biological value selection.

Standard library only. Keep TLS/proxy defaults. Hash original response bytes.
"""
import concurrent.futures, datetime, hashlib, json, pathlib, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
RAW = ROOT / 'sources'
RAW.mkdir(exist_ok=True)
CUTOFF = 'FIRST_PDATE:[* TO 2026-10-04]'
QUERIES = {
 'epmc_emc_single': '("extraskeletal myxoid chondrosarcoma" OR "myxoid chondrosarcoma") AND ("single cell" OR "single-cell" OR "scRNA" OR "spatial transcriptomic")',
 'epmc_nr4a3_single': '(NR4A3 OR "EWSR1-NR4A3" OR "TAF15-NR4A3") AND ("single cell" OR "single-cell" OR "spatial transcriptomic")',
 'epmc_sarcoma_spatial': 'sarcoma AND ("spatial transcriptomics" OR "spatial transcriptomic")',
 'epmc_sarcoma_atlas': 'sarcoma AND ("single-cell atlas" OR "single cell atlas" OR "single-cell RNA sequencing" OR "single-cell RNA-seq")',
 'epmc_models_single': '("USZ20" OR "USZ22" OR "NCC-EMC1" OR "EMC005") AND ("single-cell" OR "single cell" OR spatial)',
 'epmc_historical': '("extraskeletal chondrosarcoma" OR "myxochondrosarcoma" OR "TEC fusion" OR "CHN fusion") AND ("single-cell" OR "single cell" OR spatial)',
}

def retrieve(item):
 name, query = item
 url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode({'query':f'({query}) AND {CUTOFF}', 'format':'json','pageSize':1000,'resultType':'core'})
 now = datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-research-public-source-pilot/1.0'}), timeout=45) as resp:
   data = resp.read(16*1024*1024+1)
   if len(data)>16*1024*1024: raise RuntimeError('response budget exceeded')
   status = resp.status
  dest = RAW / (name + '.json')
  dest.write_bytes(data)
  obj=json.loads(data)
  rows=obj.get('resultList',{}).get('result',[])
  receipt={'id':name,'query':query,'url':url,'utc':now,'status':status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'path':str(dest.relative_to(ROOT)), 'hit_count':obj.get('hitCount'),'returned':len(rows)}
  summary=[{k:r.get(k) for k in ('id','source','pmcid','doi','title','authorString','firstPublicationDate','isOpenAccess','abstractText')} for r in rows]
  return receipt,summary
 except Exception as e:
  return {'id':name,'query':query,'url':url,'utc':now,'error':repr(e)},[]

if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  results=list(pool.map(retrieve,QUERIES.items()))
 (ROOT/'SEARCH-RECEIPTS.json').write_text(json.dumps([r for r,s in results],indent=2)+'\n')
 (ROOT/'SEARCH-RESULTS.json').write_text(json.dumps({r['id']:s for r,s in results},indent=2)+'\n')
 for r,s in results:
  print(r['id'],r.get('hit_count',r.get('error')),'returned',len(s))
