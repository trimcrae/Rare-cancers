"""Quiet primary metadata source gate; retain originals and bounded query receipts."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime
import hashlib
import json
import shutil
import urllib.parse
import urllib.request

HERE = Path(__file__).resolve().parent
CACHE = HERE / 'source-cache'
QUERIES = {
    'exact_EMC_protein_imaging': '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" OR "extraosseous myxoid chondrosarcoma" OR EMCS) AND ("imaging mass cytometry" OR CODEX OR MIBI OR "spatial proteomics" OR "multiplex immunofluorescence" OR "multiplexed ion beam")',
    'sarcoma_protein_imaging': 'sarcoma AND ("imaging mass cytometry" OR CODEX OR MIBI OR "spatial proteomics" OR "multiplexed ion beam" OR "spatial protein")',
    'recent_broader_protein_imaging': '("pan-cancer" OR "rare cancer" OR "rare tumor") AND ("imaging mass cytometry" OR CODEX OR MIBI OR "spatial proteomics" OR "multiplexed ion beam") AND FIRST_PDATE:[2025-01-01 TO 2026-12-31]',
}

def fetch(item):
    key, query = item
    url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode({'query': query, 'format': 'json', 'resultType': 'core', 'pageSize': 1000})
    path = CACHE / (key + '.json')
    assert not path.exists(), 'No unchanged retry/source overwrite'
    receipt = {'key': key, 'query': query, 'url': url,
               'utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'EMC-public-research/1.0'}), timeout=45) as response:
            raw = response.read(12 * 1024 * 1024 + 1)
        assert len(raw) <= 12 * 1024 * 1024, 'Per-source pilot limit; no large bundle'
        path.write_bytes(raw)
        data = json.loads(raw)
        rows = data.get('resultList', {}).get('result', [])
        receipt.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                       path=str(path), hit_count=data.get('hitCount'), returned=len(rows),
                       status='metadata retrieved; not full source eligibility')
        print(key, data.get('hitCount'), len(rows), len(raw))
        for row in rows:
            title = row.get('title', '')
            if any(word in title.lower() for word in ['sarcoma', 'pan-cancer', 'atlas', 'rare', 'spatial', 'imaging', 'immune']):
                print(row.get('id'), row.get('pmcid'), row.get('doi'), title)
    except Exception as error:
        receipt['error'] = str(error)
    return receipt

def main():
    CACHE.mkdir(exist_ok=True)
    assert shutil.disk_usage(HERE).free >= 10 * 1024**3
    with ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(fetch, QUERIES.items()))
    (HERE / 'SEARCH-RECEIPTS.json').write_text(json.dumps(records, indent=2) + '\n')
    assert sum(path.stat().st_size for path in CACHE.rglob('*') if path.is_file()) <= 64 * 1024 * 1024

if __name__ == '__main__':
    main()
