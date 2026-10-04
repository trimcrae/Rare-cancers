"""Append tighter title/abstract searches and repository receipts.

Initial full-text searches are high recall and have incomplete broad-query
pagination. They remain preserved rather than represented as exhaustive.
"""
import concurrent.futures, datetime, hashlib, json, pathlib, urllib.parse, urllib.request
from source_pilot import ROOT, RAW, retrieve

QUERIES = {
 'epmc_ta_sarcoma_single': 'TITLE_ABS:sarcoma AND (TITLE_ABS:"single-cell" OR TITLE_ABS:"single cell")',
 'epmc_ta_sarcoma_spatial': 'TITLE_ABS:sarcoma AND (TITLE_ABS:"spatial transcriptomic" OR TITLE_ABS:"spatial transcriptomics")',
 'epmc_ta_chondro_single': 'TITLE_ABS:chondrosarcoma AND (TITLE_ABS:"single-cell" OR TITLE_ABS:"single cell" OR TITLE_ABS:spatial)',
 'epmc_emc_atlas': '"extraskeletal myxoid chondrosarcoma" AND (atlas OR "malignant cells" OR "single-nucleus")',
}

def repo(name,url,limit=8*1024*1024):
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-research-public-source-pilot/1.0'}),timeout=40) as resp:
   data=resp.read(limit+1);status=resp.status
  if len(data)>limit: raise RuntimeError('response budget exceeded')
  path=RAW/(name+'.json');path.write_bytes(data)
  return {'id':name,'url':url,'utc':now,'status':status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'path':str(path.relative_to(ROOT))}
 except Exception as e:return {'id':name,'url':url,'utc':now,'error':repr(e)}

if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(retrieve,QUERIES.items()))
 (ROOT/'FOLLOWUP-SEARCH-RECEIPTS.json').write_text(json.dumps([r for r,s in results],indent=2)+'\n')
 (ROOT/'FOLLOWUP-SEARCH-RESULTS.json').write_text(json.dumps({r['id']:s for r,s in results},indent=2)+'\n')
 for r,s in results: print(r['id'],r.get('hit_count',r.get('error')),'returned',len(s))
 term='("extraskeletal myxoid chondrosarcoma" OR "myxoid chondrosarcoma" OR "NR4A3" OR "NCC-EMC1" OR "USZ20" OR "USZ22")'
 urls={
 'geo_alias_search':'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urllib.parse.urlencode({'db':'gds','term':term,'retmode':'json','retmax':500}),
 'biostudies_emc':'https://www.ebi.ac.uk/biostudies/api/v1/search?'+urllib.parse.urlencode({'query':'"extraskeletal myxoid chondrosarcoma"','pageSize':100}),
 'cellxgene_collections':'https://api.cellxgene.cziscience.com/curation/v1/collections',
 }
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rec=list(pool.map(lambda item:repo(*item),urls.items()))
 (ROOT/'REPOSITORY-SEARCH-RECEIPTS.json').write_text(json.dumps(rec,indent=2)+'\n')
 for r in rec:print(r['id'],r.get('status',r.get('error')),r.get('bytes'))
