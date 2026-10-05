import concurrent.futures, datetime, hashlib, json, pathlib, shutil, threading, urllib.parse, urllib.request
BASE=pathlib.Path(__file__).resolve().parent
RAW=BASE/'raw'
MAX=64*1024*1024
LOCK=threading.Lock()
QUERIES={
 'direct_redox':'"extraskeletal myxoid chondrosarcoma" AND (ferroptosis OR GPX4 OR SLC7A11 OR cystine OR glutathione OR lipid OR oxidative OR metabolism)',
 'disease_metabolic':'"extraskeletal myxoid chondrosarcoma" AND (metabolomics OR metabolomic OR "amino acid" OR glutamine OR glucose OR lactate OR fatty OR iron OR peroxidation)',
 'historic_alias_redox':'("extraskeletal chondrosarcoma" OR "NCC-EMC1-C1" OR "USZ20-EMC1" OR "USZ22-EMC2") AND (ferroptosis OR GPX4 OR SLC7A11 OR cystine OR lipid OR metabolism OR oxidative)',
 'generic_sarcoma_ferroptosis':'sarcoma AND (ferroptosis OR "cystine deprivation") AND ("myxoid chondrosarcoma" OR NR4A3 OR "extraskeletal myxoid")',
 'rescue':'"extraskeletal myxoid chondrosarcoma" AND (ferrostatin OR liproxstatin OR erastin OR RSL3 OR sulfasalazine OR sorafenib)',
 'model_publication':'"NCC-EMC1-C1" OR "USZ20-EMC1" OR "USZ22-EMC2" OR "USZ23-EMC3"',
 'model_lipid_record':'("H-EMC-SS" OR HEMCSS OR "MUG-EMCS") AND (ferroptosis OR metabolism OR lipid OR oxidative OR GPX4)',
 'broad_ferroptosis_roster':'sarcoma AND ferroptosis AND ("patient-derived" OR "cell line")'
}
def fetch(item):
 key,q=item;url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','pageSize':'100','resultType':'core'})
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();receipt={'key':key,'query':q,'url':url,'utc':start,'source':'EuropePMC ordinary public REST'}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'EMC-public-source-pilot/1.0'})
  with urllib.request.urlopen(req,timeout=45) as r:
   blob=r.read(8*1024*1024+1);receipt.update(status=r.status,content_type=r.headers.get('Content-Type'))
  if len(blob)>8*1024*1024:raise RuntimeError('response exceeds8MiB stage limit')
  with LOCK:
   used=sum(x.stat().st_size for x in BASE.rglob('*') if x.is_file())
   if used+len(blob)>MAX or shutil.disk_usage(BASE).free-len(blob)<10*1024**3:raise RuntimeError('retained cap/free-floor blocks stage; report pending')
   p=RAW/(key+'.json');p.write_bytes(blob)
  receipt.update(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),cache_path='raw/'+p.name)
  o=json.loads(blob);receipt.update(hit_count=o.get('hitCount'),returned=len(o.get('resultList',{}).get('result',[])),next_cursor=o.get('nextCursorMark'))
  rows=[]
  for x in o.get('resultList',{}).get('result',[]):
   rows.append({'id':x.get('id'),'source':x.get('source'),'pmid':x.get('pmid'),'pmcid':x.get('pmcid'),'doi':x.get('doi'),'title':x.get('title'),'year':x.get('pubYear'),'author':x.get('authorString'),'isOpenAccess':x.get('isOpenAccess'),'inEPMC':x.get('inEPMC')})
  return receipt,rows
 except Exception as e:
  receipt.update(error=type(e).__name__+': '+str(e),disposition='actual source-search failure; not negative evidence');return receipt,[]
def main():
 RAW.mkdir(exist_ok=True);out=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(fetch,QUERIES.items()))
 (BASE/'SEARCH-RECEIPTS.json').write_text(json.dumps([r for r,_ in out],indent=2)+'\n')
 (BASE/'SEARCH-CANDIDATES.json').write_text(json.dumps({r['key']:v for r,v in out},indent=2)+'\n')
 for r,v in out:print(r['key'],r.get('hit_count'),len(v),r.get('error',''))
if __name__=='__main__':main()
