"""Quiet public API retrieval; no browser, reconstruction, or access bypass."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

PACKET = Path(__file__).resolve().parent
CACHE = Path('/workspace/emc-r6-radiotherapy/source-cache')
CACHE.mkdir(exist_ok=True)
MAX_BYTES = 64 * 1024 * 1024

def fetch(task):
    key, url = task
    receipt = {'key': key, 'url': url, 'utc': datetime.now(timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'EMC-public-evidence-pilot/1.0'}), timeout=40) as response:
            content = response.read(8 * 1024 * 1024 + 1)
            if len(content) > 8 * 1024 * 1024:
                raise ValueError('Per-source 8 MiB limit reached; evidence remains pending')
            total = sum(p.stat().st_size for p in CACHE.iterdir() if p.is_file())
            if total + len(content) > MAX_BYTES:
                raise ValueError('Retained raw-source cap reached; evidence remains pending')
            (CACHE / key).write_bytes(content)
            receipt.update(status=response.status, bytes=len(content), sha256=sha256(content).hexdigest(), final_url=response.url,
                           content_type=response.headers.get('Content-Type'), cache=str(CACHE / key))
    except Exception as error:
        receipt['error'] = str(error)
    return receipt

def search():
    queries = {
        'rt_search.json': '("extraskeletal myxoid chondrosarcoma" OR "extraosseous myxoid chondrosarcoma") AND (radiotherapy OR radiation OR margins OR surgery)',
        'aliases_search.json': '("myxoid chondrosarcoma of soft parts" OR "NR4A3") AND (radiotherapy OR "local recurrence")',
        'broader_search.json': '"myxoid chondrosarcoma" AND ("soft tissue sarcoma" OR "soft-tissue sarcoma") AND (radiotherapy OR radiation OR "local control")',
        'series_search.json': '"extraskeletal myxoid chondrosarcoma" AND (Bishop OR Gusho OR Brodsky OR Kawaguchi OR Saleh OR Meis-Kindblom OR McGrory)',
        'recent_search.json': '"extraskeletal myxoid chondrosarcoma" AND FIRST_PDATE:[2024-01-01 TO 2026-10-04]',
    }
    tasks = [(key, 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode({'query': q, 'format': 'json', 'resultType': 'core', 'pageSize': '1000'})) for key, q in queries.items()]
    receipts = list(ThreadPoolExecutor(max_workers=5).map(fetch, tasks))
    (PACKET / 'search-receipts.json').write_text(json.dumps({'queries':queries,'receipts':receipts}, indent=2) + '\n')
    dedup = {}
    for key in queries:
        p = CACHE / key
        if not p.exists():
            continue
        data = json.loads(p.read_text())
        for row in data.get('resultList', {}).get('result', []):
            dedup[row['source'] + ':' + row['id']] = row
    (CACHE / 'discovery-metadata.json').write_text(json.dumps(list(dedup.values()), indent=2) + '\n')
    for row in dedup.values():
        print(row.get('pubYear'), row.get('id'), row.get('pmcid'), row.get('doi'), row.get('title'))

def extract_xml(key):
    p = CACHE / key
    root = ET.fromstring(p.read_bytes())
    def flat(el):
        return ' '.join(' '.join(el.itertext()).split())
    data = {'source_file':key, 'source_sha256':sha256(p.read_bytes()).hexdigest(),
            'tables':[{'id':el.attrib.get('id'), 'text': flat(el), 'rows':[flat(row) for row in el.findall('.//tr')]} for el in root.findall('.//table-wrap')],
            'sections':[{'title':flat(el.find('title')) if el.find('title') is not None else None, 'text':flat(el)} for el in root.findall('.//body/sec')],
            'supplements':[flat(el) for el in root.findall('.//supplementary-material')],
            'references':[flat(el) for el in root.findall('.//ref-list/ref')]}
    (CACHE / (key.removesuffix('.xml') + '-extract.json')).write_text(json.dumps(data, indent=2) + '\n')
    return data

if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['search']:
        search()
    elif len(sys.argv) > 2 and sys.argv[1] == 'xml':
        receipts = list(ThreadPoolExecutor(max_workers=4).map(fetch, [(pmc + '.xml', 'https://www.ebi.ac.uk/europepmc/webservices/rest/' + pmc + '/fullTextXML') for pmc in sys.argv[2:]]))
        receipt_path = PACKET / ('xml-receipts-' + datetime.now(timezone.utc).strftime('%H%M%S%f') + '.json')
        receipt_path.write_text(json.dumps(receipts, indent=2) + '\n')
        for row in receipts:
            print(row['key'], row.get('status'), row.get('error'), row.get('bytes'))
            if row.get('status') == 200:
                try:
                    data = extract_xml(row['key'])
                    print('tables',len(data['tables']),'supplements',data['supplements'])
                except Exception as error:
                    print('not parsed:', str(error))
    else:
        raise SystemExit('Usage: retrieve.py search | xml PMC...')
