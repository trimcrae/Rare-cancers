#!/usr/bin/env python3
"""Quiet public metadata scout; raw responses cached, compact catalog/receipts portable."""
import concurrent.futures,datetime,hashlib,json,pathlib,urllib.parse,urllib.request
P=pathlib.Path(__file__).resolve().parent;C=P/'.cache';C.mkdir(exist_ok=True)
D='("extraskeletal myxoid chondrosarcoma" OR "extraskeletal myxoid chondrosarcomas" OR EMCS)'
QUERIES={
 'serial_tissue':D+' AND (paired OR serial OR longitudinal OR "pre-treatment" OR "post-treatment" OR rebiopsy OR "repeat biopsy" OR "acquired resistance")',
 'kinase_treatment':D+' AND (sunitinib OR pazopanib OR imatinib OR sorafenib OR axitinib) AND (molecular OR RET OR kinase OR phospho OR biopsy OR genomic)',
 'therapy_assays':D+' AND (radiotherapy OR radiation OR chemotherapy OR immunotherapy) AND (RNA OR transcriptom* OR genomic OR pathology OR blood OR biomarker OR pharmacodynamic)',
 'fusion_resistance':'(NR4A3 OR "CHN fusion" OR "TEC fusion") AND ("acquired resistance" OR pharmacodynamic OR "post-treatment" OR "repeat biopsy" OR longitudinal)',
 'broader_serial':'sarcoma AND (pharmacodynamic OR "paired biopsies" OR "serial biopsies") AND ("myxoid chondrosarcoma" OR NR4A3 OR "extraskeletal myxoid")',
 'historical_serial':'"myxoid chondrosarcoma" AND ("post-treatment" OR "pre-treatment" OR paired OR "repeat biopsy" OR "acquired resistance")',
 'treatment_pathology':D+' AND ("histological response" OR "pathological response" OR "histologic response" OR "treatment effect" OR "sarcomatous transformation" OR "dedifferentiation")'
}
def fetch(name,q):
 t=datetime.datetime.now(datetime.timezone.utc).isoformat();url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','resultType':'core','pageSize':'1000'})
 try:
  with urllib.request.urlopen(url,timeout=40) as r:b=r.read();status=r.status
  (C/(name+'-metadata.json')).write_bytes(b);a=json.loads(b); rows=a.get('resultList',{}).get('result',[])
  compact=[{k:x.get(k) for k in ['id','source','pmid','pmcid','doi','title','pubYear','authorString','isOpenAccess','hasSuppl','hasData','firstPublicationDate']} for x in rows]
  return name,{'utc':t,'url':url,'status':status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'hitCount':a.get('hitCount'),'returned':len(rows),'complete_metadata_page':len(rows)==a.get('hitCount'),'query':q,'records':compact}
 except Exception as e:return name,{'utc':t,'url':url,'query':q,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool: results=dict(pool.map(lambda x:fetch(*x),QUERIES.items()))
(C/'SEARCH-CATALOG.json').write_text(json.dumps(results,indent=2)+'\n')
(P/'SEARCH-SUMMARY.json').write_text(json.dumps({k:{x:y for x,y in v.items() if x!='records'} for k,v in results.items()},indent=2)+'\n')
for k,v in results.items(): print(k,v.get('hitCount'),v.get('returned'),v.get('error'))
