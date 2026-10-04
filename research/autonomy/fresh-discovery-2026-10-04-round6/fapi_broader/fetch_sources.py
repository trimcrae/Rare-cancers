#!/usr/bin/env python3
"""Bounded ordinary public HTTP source retrieval; no browser or TLS bypass."""
import concurrent.futures, datetime, hashlib, json, pathlib, shutil, threading, urllib.request, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent
RAW = ROOT / 'raw'
RAW.mkdir(exist_ok=True)
CAP = 64 * 1024 * 1024
WRITE_LOCK = threading.Lock()

def fetch(spec):
    name, url = spec
    result = {'name': name, 'url': url, 'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        if shutil.disk_usage(ROOT).free < 10*1024**3:
            raise RuntimeError('free storage below 10 GiB')
        req = urllib.request.Request(url, headers={'User-Agent':'EMC-public-evidence-research/1.0'})
        with urllib.request.urlopen(req, timeout=40) as resp:
            data = resp.read(12*1024*1024 + 1)
            if len(data) > 12*1024*1024:
                raise RuntimeError('single response cap exceeded')
            result.update(status=resp.status, final_url=resp.url, content_type=resp.headers.get('Content-Type'))
        path = RAW / name
        with WRITE_LOCK:
            if sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file()) + len(data) > CAP:
                raise RuntimeError('retention cap exceeded including all task copies/outputs')
            if shutil.disk_usage(ROOT).free - len(data) < 10*1024**3:
                raise RuntimeError('download would leave less than 10 GiB free')
            path.write_bytes(data)
        result.update(path=str(path.relative_to(ROOT)), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    except Exception as e:
        result['error'] = type(e).__name__ + ': ' + str(e)
    return result

QUERIES = {
 'three_timepoint_metadata.json':'EXT_ID:11927082 OR PMC11927082',
 'hirmas2023_metadata.json':'AUTH_LAST:Hirmas AND JOURNAL_ABBR:"J Nucl Med" AND FIRST_PDATE:[2023-01-01 TO 2023-12-31]',
 'hirmas2024_metadata.json':'AUTH_LAST:Hirmas AND JOURNAL_ABBR:"J Nucl Med" AND FIRST_PDATE:[2024-01-01 TO 2024-12-31]',
 'interobserver2023_metadata.json':'JOURNAL_ABBR:"J Nucl Med" AND FIRST_PDATE:[2023-01-01 TO 2023-12-31] AND interobserver AND FAPI',
 'liver2026_metadata.json':'DOI:10.1007/s44178-026-00295-4',
}

if __name__ == '__main__':
    specs = [(name,'https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&pageSize=100&query='+urllib.parse.quote(q)) for name,q in QUERIES.items()]
    specs += [('three_timepoint_full.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11927082/fullTextXML')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        receipts = list(ex.map(fetch, specs))
    (ROOT/'fetch-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
    print(json.dumps([{k:v for k,v in r.items() if k in ['name','status','bytes','error']} for r in receipts],indent=2))
