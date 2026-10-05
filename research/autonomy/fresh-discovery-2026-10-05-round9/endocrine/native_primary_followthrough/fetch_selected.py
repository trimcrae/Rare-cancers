#!/usr/bin/env python3
"""Two fixed ordinary public primary routes; retain bodies only in ignored cache."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT/'AMENDMENT-01-SOURCE-SELECTION.json').read_text())
def fetch(source):
    url = source['public_route']
    path = ROOT/'raw-cache'/(source['PMCID']+'.xml')
    receipt = {'utc':datetime.now(timezone.utc).isoformat(),'url':url,'path':str(path),'cap_bytes':1048576,'cache_only':True}
    if path.exists():
        data = path.read_bytes()
        receipt['status'] = 'existing cache reused; no network'
    else:
        try:
            with urlopen(Request(url, headers={'User-Agent':'EMC research source linkage'}),timeout=35) as response:
                receipt['status'] = response.status
                receipt['content_type'] = response.headers.get('Content-Type')
                data = response.read(1048577)
                if len(data)>1048576:
                    receipt['status'] = 'cap exceeded, no body staged'
                    return receipt
        except HTTPError as e:
            data = e.read(1048576)
            receipt['status'] = e.code
        except (URLError, TimeoutError) as e:
            receipt['status'] = type(e).__name__
            receipt['error'] = str(e)
            return receipt
        path.write_bytes(data)
    receipt['bytes'] = len(data)
    receipt['sha256'] = hashlib.sha256(data).hexdigest()
    return receipt
with ThreadPoolExecutor(max_workers=2) as pool:
    receipts = list(pool.map(fetch,PLAN['selected_sources']))
(ROOT/'SELECTED-SOURCE-RECEIPTS.json').write_text(json.dumps(receipts,indent=2)+'\n')
print(json.dumps(receipts))
