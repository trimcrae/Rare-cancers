from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,datetime,concurrent.futures
P=Path(__file__).resolve().parent
S=P/'sources';S.mkdir(exist_ok=True)
queries={
 'emc_methylation':'("extraskeletal myxoid chondrosarcoma" OR "NR4A3" OR "EMCS") AND (methylation OR epigenetic)',
 'mitotic_clock':'(epiTOC2 OR epiTOC OR "mitotic clock") AND (cancer OR sarcoma)',
 'epiTOC2_primary':'epiTOC2',
}
jobs=[(k,'https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':v,'format':'json','resultType':'core','pageSize':100}),'GET') for k,v in queries.items()]
jobs += [('geo_alias_search','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urllib.parse.urlencode({'db':'gds','term':'("extraskeletal myxoid chondrosarcoma" OR "EMCS" OR "NR4A3" OR "chordoid sarcoma") AND (methylation OR methylome OR methylated)','retmode':'json','retmax':500}),'GET')]
for platform in ['GPL13534','GPL21145']:
 url='https://ftp.ncbi.nlm.nih.gov/geo/series/GSE140nnn/GSE140686/suppl/GSE140686_'+platform+'_matrix_processed.txt.gz'
 jobs.append((platform+'_matrix_size',url,'HEAD'))
jobs.append(('GSE140686_listing','https://ftp.ncbi.nlm.nih.gov/geo/series/GSE140nnn/GSE140686/suppl/','GET'))
def fetch(j):
 name,url,method=j;r={'name':name,'url':url,'method':method,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,method=method),timeout=40) as f:
   b=f.read(8*1024*1024) if method=='GET' else b''
   r.update(status=f.status,headers=dict(f.headers),final_url=f.url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
   if method=='GET':(S/(name+'.json' if name!='GSE140686_listing' else name+'.html')).write_bytes(b)
 except Exception as e:r['error']=str(e)
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(fetch,jobs))
(P/'SOURCE-GATE-RECEIPTS.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:print(r['name'],r.get('status',r.get('error')),r.get('headers',{}).get('Content-Length'),r.get('bytes'))
for name in queries:
 try:
  d=json.loads((S/(name+'.json')).read_text());print('QUERY',name,'hits',d.get('hitCount'))
  for r in d.get('resultList',{}).get('result',[]):print(r.get('id'),r.get('pmcid'),r.get('doi'),r.get('title'))
 except Exception as e:print(name,e)
