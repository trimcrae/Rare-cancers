#!/usr/bin/env python3
"""Ordinary quiet source requests, bounded original cache and compact receipts."""
import concurrent.futures, datetime, hashlib, json, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent;CACHE=ROOT/'raw-cache'
SOURCES={
 'PMC6011095.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6011095/fullTextXML',
 'PMC4110079.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4110079/fullTextXML',
 'Kandoussi2024-preview.html':'https://link.springer.com/article/10.1007/s00256-024-04800-6',
}
QUERIES={
 'emc-diffusion':'("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" OR "extraskeletal myxoid") AND (diffusion OR "apparent diffusion" OR ADC OR DWI)',
 'broader-myxoid-diffusion':'(myxoid AND (sarcoma OR liposarcoma OR myxofibrosarcoma OR fibromyxoid)) AND ("apparent diffusion" OR diffusion-weighted OR ADC)',
 'sarcoma-threshold-priorart':'("soft tissue" AND (tumor OR tumour)) AND (ADC OR "apparent diffusion") AND (myxoid OR threshold OR cutoff OR cut-off)'
}

def fetch(name,url):
 path=CACHE/name;utc=datetime.datetime.now(datetime.timezone.utc).isoformat();rec={'utc':utc,'url':url,'local_path':str(path),'cap_bytes':4194304,'cache_only':True}
 if path.exists():raise RuntimeError('Preserve originals; refuse overwrite:'+str(path))
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-public-source-gate/1'}),timeout=30) as r:
   body=r.read(4194305);assert len(body)<=4194304,'source cap exceeded';path.write_bytes(body);rec.update(status=r.status,bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),content_type=r.headers.get('content-type'),final_url=r.geturl())
 except Exception as e:rec.update(status='request_failed',error=str(e))
 return rec

def main():
 CACHE.mkdir(parents=True,exist_ok=True);jobs=dict(SOURCES)
 for name,q in QUERIES.items():jobs[name+'.json']='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','pageSize':1000,'resultType':'lite'})
 jobs['PMID39256245.json']='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':'EXT_ID:39256245 AND SRC:MED','format':'json','resultType':'lite'})
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:receipts=list(pool.map(lambda x:fetch(*x),jobs.items()))
 (ROOT/'SOURCE-RETRIEVAL.json').write_text(json.dumps(receipts,indent=2)+'\n')
 summaries={}
 for name,q in QUERIES.items():
  f=CACHE/(name+'.json')
  if f.exists():
   data=json.loads(f.read_text());summaries[name]={'query':q,'hitCount':data.get('hitCount'),'returned':len(data.get('resultList',{}).get('result',[]))}
 (ROOT/'SEARCH-SCOPE.json').write_text(json.dumps(summaries,indent=2)+'\n');print(json.dumps({'requests':len(receipts),'sources':[{'name':Path(r['local_path']).name,'status':r['status'],'bytes':r.get('bytes')} for r in receipts],'queries':summaries}))

if __name__=='__main__':main()
