import concurrent.futures,datetime,hashlib,json,pathlib,urllib.request
P=pathlib.Path(__file__).parent
URLS={
'velcade.html':'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1521d321-e724-4ffc-adad-34bf4f44fac7',
'kyprolis.html':'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ea66eb30-e665-4693-99a1-a9d3b4bbe2d6',
'ninlaro.html':'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=038f2461-834b-4488-9ebd-863c83eef5a7',
'gsrs-ixazomib-citrate.html':'https://precision.fda.gov/ginas/app/ui/substances/46CWK97Z3K',
'gsrs-niraparib-tosylate.html':'https://precision.fda.gov/ginas/app/ui/substances/75KE12AY9U',
'pubchem-56844015.json':'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/56844015/property/InChIKey,CanonicalSMILES/JSON',
'pubchem-49867936.json':'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/49867936/property/InChIKey,CanonicalSMILES/JSON',
'doxorubicin.html':'https://www.dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=e0349f98-42fa-4003-b6d8-a1db1401b0ef&type=display',
'mln9708-original.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:20160034&resultType=core&format=xml',
'conoidin-original.xml':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3043594/fullTextXML'
}
def fetch(kv):
 name,url=kv; d=dict(file=name,url=url,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 try:
  r=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-research-source-audit/1.0'}),timeout=25);b=r.read();(P/'sources'/name).write_bytes(b);d.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),status=r.status,content_type=r.headers.get('Content-Type'))
 except Exception as e:d.update(error=str(e))
 return d
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:r=list(pool.map(fetch,URLS.items()))
 (P/'source-provenance.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
