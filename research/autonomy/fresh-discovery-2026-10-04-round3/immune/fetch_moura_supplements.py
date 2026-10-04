from fetch_sources import BASE,one
import urllib.request,json,concurrent.futures,shutil
ids=[27754884,27754881,27754878,27754875,27754869,27754866,27754857,27754854,27754851]
def metadata(i):
 name=f'moura-figshare-{i}.json';r=one((name,f'https://api.figshare.com/v2/articles/{i}'))
 if 'error' in r:return r,None
 return r,json.loads((BASE/name).read_text())
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:meta=list(ex.map(metadata,ids))
total=sum(f['size'] for _,d in meta if d for f in d['files'])
retained=sum(p.stat().st_size for p in BASE.rglob('*') if p.is_file())
if retained+total>30*1024**2 or shutil.disk_usage(BASE).free-total<10*1024**3:raise RuntimeError(f'budget gate {retained=} {total=}')
urls={}
for r,d in meta:
 if d:
  for f in d['files']:urls['moura-'+f['name']]=f['download_url']
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:rows=list(ex.map(one,urls.items()))
(BASE/'moura-supp-retrieval.json').write_text(json.dumps(dict(metadata=[r for r,d in meta],files=rows,total_source_bytes=total),indent=2))
print('SUPPLEMENTS',[(r['name'],r.get('bytes'),r.get('error')) for r in rows])
