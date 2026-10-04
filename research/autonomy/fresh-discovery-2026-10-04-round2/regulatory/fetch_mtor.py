from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,concurrent.futures
P=Path(__file__).resolve().parent
urls={
 'everolimus2011-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='+urllib.parse.quote('TITLE:"Combination mTOR and IGF-1R inhibition"')+'&format=json&resultType=core',
 'merimsky2008-metadata.json':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:18827568&format=json&resultType=core',
 'NCT01396408.json':'https://clinicaltrials.gov/api/v2/studies/NCT01396408',
 'everolimus2011.html':'https://aacrjournals.org/clincancerres/article/17/4/871/11904/Combination-mTOR-and-IGF-1R-Inhibition-Phase-I',
 'merimsky2008.html':'https://journals.lww.com/anti-cancerdrugs/abstract/2008/11000/targeting_the_mammalian_target_of_rapamycin_in_myxoid.9.aspx',
 'NCC-EMC1-C1-cellosaurus.txt':'https://www.cellosaurus.org/CVCL_E2B4.txt'}
def one(pair):
 name,u=pair;r={'name':name,'url':u}
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 scientific source check'}),timeout=35) as q:b=q.read(3000000);r.update(final_url=q.url,status=q.status,content_type=q.headers.get('Content-Type'))
  (P/name).write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:r['error']=str(e)
 return r
out=list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(one,urls.items()))
(P/'mtor-fetch-receipts.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
for n in ['everolimus2011-metadata.json','merimsky2008-metadata.json']:
 a=json.loads((P/n).read_text());print(n,json.dumps(a.get('resultList'),ensure_ascii=False)[:12000])
