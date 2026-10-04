import json,time,urllib.parse,xml.etree.ElementTree as E
from pathlib import Path
from fetch_sources import fetch
ROOT=Path(__file__).resolve().parent
queries={
 'emc-cell':'("extraskeletal myxoid" OR "extra-skeletal myxoid" OR "NR4A3") AND ("single cell" OR "single-cell" OR "single nucleus" OR "spatial" OR "CITE-seq")',
 'sarcoma-cell':'sarcoma AND ("single cell" OR "single-cell" OR "single nucleus" OR "spatial" OR "CITE-seq") AND gse[ETYP]',
 'wagner':'sarcoma AND Wagner[Author] AND gse[ETYP]',
}
receipts=[];result={}
for label,q in queries.items():
 u='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urllib.parse.urlencode({'db':'gds','term':q,'retmode':'json','retmax':500})
 n=label+'-search.json';r=fetch(n,u);receipts.append(r);time.sleep(.4)
 if 'error' in r:continue
 d=json.loads((ROOT/n).read_text(encoding='utf-8'))['esearchresult'];ids=d['idlist'];result[label]={'query':q,'count':d['count'],'ids':ids}
 if ids:
  u='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?'+urllib.parse.urlencode({'db':'gds','id':','.join(ids),'retmode':'json'})
  n=label+'-summary.json';r=fetch(n,u);receipts.append(r);time.sleep(.4)
  if 'error' not in r:
   z=json.loads((ROOT/n).read_text(encoding='utf-8'))['result']
   result[label]['records']=[{k:z[i].get(k) for k in ['accession','title','summary','taxon','n_samples','samples']} for i in z['uids']]
(ROOT/'geo-search-receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf-8')
(ROOT/'geo-candidates.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
for k,v in result.items():
 print(k,v['count']);print([(r['accession'],r['title']) for r in v.get('records',[])])
