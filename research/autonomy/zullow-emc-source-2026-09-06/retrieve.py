import urllib.request, urllib.error, pathlib, hashlib, json, datetime, sys
ROOT=pathlib.Path(__file__).parent
def fetch(url,name):
    t=datetime.datetime.now(datetime.timezone.utc).isoformat()
    req=urllib.request.Request(url,headers={'User-Agent':'EMC-source-provenance/1.0'})
    try:
        with urllib.request.urlopen(req,timeout=60) as r:
            data=r.read(30_000_001)
            if len(data)>30_000_000: raise RuntimeError('30 MB source cap exceeded')
            rec={'url':url,'final_url':r.url,'status':r.status,'headers':dict(r.headers),'retrieved_utc':t,'file':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
            (ROOT/name).write_bytes(data)
    except Exception as e:
        rec={'url':url,'retrieved_utc':t,'file':name,'error':str(e)}
    with (ROOT/'retrievals.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(rec)+'\n')
    print(json.dumps(rec))
if __name__=='__main__':fetch(sys.argv[1],sys.argv[2])
