import concurrent.futures,datetime,hashlib,json,pathlib,shutil,urllib.parse,urllib.request
D=pathlib.Path(__file__).resolve().parent
def get(job):
 name,url=job;r={'file':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 assert shutil.disk_usage(D).free>=10*1024**3
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EMC-clinical-linkage-source-audit/1.0'}),timeout=30) as a:
   b=a.read(2*1024**2+1);r.update(status=a.status,final_url=a.url)
  assert len(b)<=2*1024**2
  assert sum(x.stat().st_size for x in D.rglob('*') if x.is_file())+len(b)<=8*1024**2
  (D/name).write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:r['error']=str(e)
 return r
if __name__=='__main__':
 queries={'sunitinib2012':'EXT_ID:23058004 AND SRC:MED','sunitinib2014':'DOI:10.1016/j.ejca.2014.03.013','pazopanib2019':'EXT_ID:31331701 AND SRC:MED','huang2023':'EXT_ID:36948401 AND SRC:MED','suemitsu2025':'EXT_ID:40828003 AND SRC:MED','paioli2020':'EXT_ID:32572850 AND SRC:MED'}
 jobs=[(k+'-metadata.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':v,'format':'json','resultType':'core'})) for k,v in queries.items()]
 jobs.append(('anthracycline2013.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3879193/fullTextXML'))
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:rs=list(p.map(get,jobs))
 (D/'source-fetch-receipts.json').write_text(json.dumps(rs,indent=2))
 print(json.dumps(rs,indent=2))
 for k in queries:
  p=D/(k+'-metadata.json')
  if p.exists():print(k,[{a:r.get(a) for a in ['id','pmcid','doi','title','fullTextUrlList']} for r in json.loads(p.read_text()).get('resultList',{}).get('result',[])])
