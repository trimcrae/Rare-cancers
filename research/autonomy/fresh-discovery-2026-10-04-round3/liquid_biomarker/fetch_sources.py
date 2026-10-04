from pathlib import Path
import urllib.request, hashlib, json, datetime, shutil
BASE=Path(__file__).resolve().parent
SOURCES={'localized2020':'PMC7349923','structural2020':'PMC7761870','omori2022':'PMC9527174','review2021':'PMC7920076','review2025':'PMC12504171'}
def fetch(name,url,limit=2*1024*1024):
    used=sum(p.stat().st_size for p in BASE.rglob('*') if p.is_file())
    assert shutil.disk_usage(BASE).free-limit>=10*1024**3
    # 2026-10-04 lead STORAGE-AMENDMENT-02 authorized15MiB for bounded follow-up.
    assert used+limit<=15*1024**2
    receipt={'name':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'EMCResearch-public-literature-evaluation/1.0'})
        with urllib.request.urlopen(req,timeout=45) as r:
            data=r.read(limit+1); assert len(data)<=limit
            receipt.update(status=r.status,final_url=r.url,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        (BASE/name).write_bytes(data)
    except Exception as e: receipt['error']=str(e)
    return receipt
if __name__=='__main__':
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as pool:
        receipts=list(pool.map(lambda kv:fetch(kv[0]+'.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/'+kv[1]+'/fullTextXML'),SOURCES.items()))
    (BASE/'source_receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf8')
    print(json.dumps(receipts,indent=2))
