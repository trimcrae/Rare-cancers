import concurrent.futures, datetime, hashlib, json, pathlib, sys, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent
def fetch(pair):
    name, url = pair
    entry = dict(file=name, url=url, retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'EMC-provenance-research/1.0'}), timeout=90) as r:
            data=r.read(); entry.update(status=r.status, final_url=r.url, headers=dict(r.headers))
        (ROOT/name).write_bytes(data)
        entry.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    except Exception as e: entry.update(error=str(e))
    return entry
if __name__=='__main__':
    pairs=[tuple(x.split('=',1)) for x in sys.argv[1:]]
    records=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(fetch,pairs))
    path=ROOT/'retrievals.json'
    old=json.loads(path.read_text()) if path.exists() else []
    path.write_text(json.dumps(old+records,indent=2)+'\n')
    print(json.dumps(records,indent=2))
