"""Save exact normal public HTTP responses and auditable attempts; no authentication."""
import concurrent.futures, datetime, hashlib, json, pathlib, sys, urllib.request, urllib.error, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parent
def get(item):
    name, url, *extra = item
    form=extra[0] if extra else None
    rec = {'file':name,'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'GET'}
    try:
        if form is not None: rec.update(method='POST',form=form)
        data=urllib.parse.urlencode(form).encode() if form is not None else None
        with urllib.request.urlopen(urllib.request.Request(url,data=data,headers={'User-Agent':'EMC-public-provenance-recovery/1.0'}),timeout=40) as r:
            data=r.read(); rec.update(status=r.status,final_url=r.url,content_type=r.headers.get('Content-Type'))
    except urllib.error.HTTPError as e:
        data=e.read(); rec.update(status=e.code,final_url=e.url,error=str(e),content_type=e.headers.get('Content-Type'))
    except Exception as e:
        rec.update(error=repr(e)); return rec
    (ROOT/name).write_bytes(data)
    rec.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),representation='exact HTTP response body bytes')
    return rec
if __name__=='__main__':
    items=json.loads((ROOT/sys.argv[1]).read_text(encoding='utf-8-sig'))
    out=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(get,items))
    p=ROOT/'retrievals.json'; records=json.loads(p.read_text()) if p.exists() else []
    records.extend(out); p.write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
