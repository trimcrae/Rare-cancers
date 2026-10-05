"""Quiet public-source retrieval. No browser; originals are ignored cache only."""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
QUERIES = {
    "precise-emc-apa": '(TITLE_ABS:"extraskeletal myxoid chondrosarcoma" OR TITLE_ABS:"extra-skeletal myxoid chondrosarcoma" OR TITLE_ABS:NR4A3) AND (TITLE_ABS:polyadenylation OR TITLE_ABS:"3 prime UTR" OR TITLE_ABS:"3\' UTR" OR TITLE_ABS:"cleavage site")',
    "three-seq-apa": '("3SEQ" OR "3-seq" OR "3\'-end sequencing for expression quantification") AND "alternative polyadenylation"',
    "emc-processing": '(TITLE_ABS:"extraskeletal myxoid chondrosarcoma" OR TITLE_ABS:"extra-skeletal myxoid chondrosarcoma") AND (TITLE_ABS:"intron retention" OR TITLE_ABS:"alternative splicing" OR TITLE_ABS:"RNA processing")',
}


def retrieve(item):
    name, query = item
    url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode(
        {'query': query, 'format': 'json', 'resultType': 'core', 'pageSize': 100})
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(url, timeout=35) as response:
            body, status = response.read(), response.status
        path = ROOT / 'raw' / (name + '.json')
        path.write_bytes(body)
        parsed = json.loads(body)
        rows = parsed.get('resultList', {}).get('result', [])
        return {'name': name, 'query': query, 'url': url, 'utc': stamp,
                'status': status, 'bytes': len(body),
                'sha256': hashlib.sha256(body).hexdigest(),
                'path': 'raw/' + path.name, 'hitCount': parsed.get('hitCount'),
                'returned': len(rows),
                'hits': [{k: row.get(k) for k in ['id', 'pmcid', 'doi', 'title', 'pubYear', 'abstractText']} for row in rows]}
    except Exception as error:
        return {'name': name, 'query': query, 'url': url, 'utc': stamp, 'error': str(error)}


if __name__ == '__main__':
    receipts = list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(retrieve, QUERIES.items()))
    (ROOT / 'PRECISE-SEARCH-RECEIPTS.json').write_text(json.dumps(receipts, indent=2) + '\n')
    for receipt in receipts:
        print(receipt['name'], receipt.get('hitCount'), receipt.get('returned'), receipt.get('error'))
        for row in receipt.get('hits', []):
            print(row['id'], row['title'])
