from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,datetime,concurrent.futures,gzip
P=Path(__file__).resolve().parent;S=P/'sources'
urls={
 'epitoc2_primary.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7315560/fullTextXML',
 'improved_counter_2024.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11101651/fullTextXML',
 'exact_emc_literature.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':'("extraskeletal myxoid chondrosarcoma" OR "extraskeletal myxoid chondrosarcomas" OR "chordoid sarcoma") AND (methylation OR methylome OR epigenetic)','format':'json','resultType':'core','pageSize':100}),
 'classifiers_primary.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':'EXT_ID:30895378 OR EXT_ID:33479225','format':'json','resultType':'core','pageSize':10}),
 'geo_discovery_summary.json':'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id=200310848,200310743,200162288,200140880,200087748,200087747&retmode=json',
 'GSE140686_family.soft.gz':'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE140nnn/GSE140686/soft/GSE140686_family.soft.gz',
}
def get(kv):
 n,u=kv; r={'name':n,'url':u,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(u,timeout=40) as f:
   b=f.read(32*1024**2+1);assert len(b)<=32*1024**2,'source exceeds bounded32MiB response'
   (S/n).write_bytes(b);r.update(status=f.status,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),final_url=f.url)
 except Exception as e:r['error']=str(e)
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rs=list(ex.map(get,urls.items()))
(P/'FOLLOWUP-RECEIPTS.json').write_text(json.dumps(rs,indent=2)+'\n')
for r in rs:print(r['name'],r.get('status',r.get('error')),r.get('bytes'))
for n in ['exact_emc_literature.json','classifiers_primary.json']:
 d=json.loads((S/n).read_text());print(n,'count',d.get('hitCount'))
 for r in d.get('resultList',{}).get('result',[]):print(r.get('id'),r.get('pmcid'),r.get('doi'),r.get('title'))
