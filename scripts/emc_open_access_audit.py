"""Look for public-copy candidates; never infer absence or completed reading."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/literature/emc-census-2026-09-12'


def validate_response(response, requested_dois):
    """Reject incomplete results; preserve index duplicates/aliases for review."""
    results = response['results']
    if response['meta']['count'] != len(results):
        raise ValueError('Unexpected pagination: results must be complete')
    expected = {doi.lower() for doi in requested_dois}
    seen, unrequested, duplicates = set(), [], []
    for record in results:
        doi = (record.get('doi') or '').lower().removeprefix('https://doi.org/')
        if not doi:
            raise ValueError('Missing DOI in index response')
        if doi in seen:
            duplicates.append(doi)
        if doi not in expected:
            unrequested.append(doi)
        seen.add(doi)
    return {'unrequested_dois': unrequested, 'duplicate_dois': duplicates}


def main():
    if shutil.disk_usage(ROOT).free < 10 * 1024**3 + 10 * 1024**2:
        raise RuntimeError('10 GiB headroom plus 10 MiB metadata budget required')
    data = json.loads((ROOT / 'site/literature.json').read_text(encoding='utf-8'))
    rows = [r for r in data['records'] if r['discovery_scope'] in ('title', 'abstract')
            and r['access'] == 'unresolved' and r.get('doi')]
    dois = sorted({r['doi'].lower() for r in rows})
    receipts, candidates = [], []
    for start in range(0, len(dois), 40):
        batch = dois[start:start + 40]
        url = 'https://api.openalex.org/works?' + urlencode({
            'filter': 'doi:' + '|'.join('https://doi.org/' + x for x in batch),
            'per-page': 50,
            'select': 'id,doi,title,open_access,best_oa_location,locations'})
        batch_key = hashlib.sha256(url.encode()).hexdigest()[:16]
        path = OUT / 'sources' / f'openalex-access-{batch_key}.json.gz'
        try:
            if not path.exists() and shutil.disk_usage(ROOT).free < 10 * 1024**3 + 4 * 1024**2:
                raise RuntimeError('Insufficient headroom for another bounded metadata response')
            payload = gzip.decompress(path.read_bytes()) if path.exists() else urlopen(url, timeout=30).read(2 * 1024**2 + 1)
            if len(payload) > 2 * 1024**2:
                raise ValueError('Response exceeds 2 MiB per-batch limit')
            response = json.loads(payload)
            possible_aliases = validate_response(response, batch)
            if not path.exists():
                path.write_bytes(gzip.compress(payload, mtime=0))
            receipts.append({'url': url, 'requested_dois': batch,
                             'identity_review': possible_aliases,
                             'returned': len(response['results']),
                             'sha256': hashlib.sha256(payload).hexdigest(),
                             'cache': str(path.relative_to(ROOT))})
            for r in response['results']:
                locations = [x for x in r.get('locations', []) if x.get('is_oa')]
                if locations:
                    candidates.append({'doi': r['doi'], 'title': r['title'],
                                       'locations': locations,
                                       'status': 'candidate_identity_and_access_not_verified'})
            print(f'{start}: {len(response["results"])} records, {len(candidates)} cumulative candidates', flush=True)
        except Exception as exc:
            receipts.append({'url': url, 'requested_dois': batch, 'error': str(exc)})
            print(f'{start}: {type(exc).__name__}', flush=True)
            if getattr(exc, 'code', None) in (401, 403, 429):
                break
    result = {'date': '2026-09-12', 'input_catalogue_records': len(data['records']),
              'requested_unique_dois': len(dois), 'batches': receipts, 'candidates': candidates,
              'policy': 'OA indexing supplies discovery candidates only. Closed or missing records do not prove absence of public copies. No reading credit or site-link update is inferred.'}
    (OUT / 'open-access-audit.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
