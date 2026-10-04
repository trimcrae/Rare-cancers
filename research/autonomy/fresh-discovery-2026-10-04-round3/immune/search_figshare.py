from pathlib import Path
import urllib.request,json,datetime,hashlib
B=Path(__file__).resolve().parent
url='https://api.figshare.com/v2/articles/search'
body=json.dumps({'search_for':'"CCR-24-1782"','limit':100}).encode()
req=urllib.request.Request(url,data=body,headers={'Content-Type':'application/json'})
data=urllib.request.urlopen(req,timeout=45).read(2*1024*1024)
(B/'moura-figshare-search.json').write_bytes(data)
print([(r['id'],r['title']) for r in json.loads(data)])
(B/'moura-figshare-search-receipt.json').write_text(json.dumps(dict(url=url,body=body.decode(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)),indent=2))
