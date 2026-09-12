#!/usr/bin/env python3
"""Reproducible EMC discovery census. Search records are NOT adjudicated studies.

Stores original API responses compressed outside the public site. Uses only stdlib.
The broad Europe PMC query searches full text too; title/abstract flags are triage,
not scientific inclusion decisions. No access-unresolved item is called paywall-only.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search'
QUERIES = {
    'exact_phrase': '"extraskeletal myxoid chondrosarcoma"',
    'expanded': '("extraskeletal myxoid chondrosarcoma" OR "extra-skeletal myxoid chondrosarcoma" OR "extraskeletal myxoid chondrosarcomas" OR "EWSR1-NR4A3" OR "TAF15-NR4A3" OR "EWS-CHN" OR "EWS-TEC")',
    'med_title_abstract': 'SRC:MED AND (TITLE_ABS:"extraskeletal myxoid chondrosarcoma" OR TITLE_ABS:"extra-skeletal myxoid chondrosarcoma")',
    'med_title': 'SRC:MED AND (TITLE:"extraskeletal myxoid chondrosarcoma" OR TITLE:"extra-skeletal myxoid chondrosarcoma")',
}
DISEASE = re.compile(r'extra[ -]?skeletal myxoid chondrosarcom|(?:EWSR1|TAF15)[\s:/-]+NR4A3|EWS[/-](?:CHN|TEC)', re.I)

def fetch(url):
    for attempt in range(4):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'EMC-Literature-Census/1.0 (research bibliography)'}), timeout=90) as r:
                return r.read()
        except Exception as error:
            if isinstance(error, HTTPError) and error.code in (400, 401, 403, 404):
                raise
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)

def plain(s):
    import html
    return html.unescape(re.sub('<[^>]+>', ' ', s or '')).strip()

def normalize(r):
    title, abstract = plain(r.get('title')), plain(r.get('abstractText'))
    urls = []
    for link in r.get('fullTextUrlList', {}).get('fullTextUrl', []):
        url = link.get('url', '')
        if (link.get('availability') in ('Open access', 'Free')
                and link.get('documentStyle') in ('html', 'pdf', 'doi')
                and url.startswith(('https://', 'http://'))):
            urls.append({'url': url, 'label': link.get('site', 'Free full text'), 'evidence': 'Europe PMC free/open-access link metadata'})
    pmcid = r.get('pmcid', '')
    if pmcid:
        urls.insert(0, {'url': f'https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/', 'label': 'PMC full text', 'evidence': 'PMC identifier in Europe PMC record'})
    urls = list({x['url']: x for x in urls}.values())
    source, rid = r.get('source', ''), r['id']
    return {
        'id': f'{source}:{rid}', 'title': title, 'authors': r.get('authorString', ''),
        'year': r.get('pubYear', ''), 'date': r.get('firstPublicationDate', ''),
        'journal': r.get('journalInfo', {}).get('journal', {}).get('title', ''),
        'doi': r.get('doi', ''), 'pmid': rid if source == 'MED' else '', 'pmcid': pmcid,
        'publication_types': r.get('pubTypeList', {}).get('pubType', []),
        'record_url': f'https://europepmc.org/article/{source}/{rid}',
        'publisher_url': 'https://doi.org/' + r['doi'] if r.get('doi') else '',
        'free_links': urls, 'access': 'free_link_indexed' if urls else 'unresolved',
        'discovery_scope': 'title' if DISEASE.search(title) else ('abstract' if DISEASE.search(abstract) else 'full_text_or_index'),
        'screening_status': 'not_adjudicated', 'reading_status': 'not_read',
        'abstract_available': bool(abstract),
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    out = ROOT / 'research/literature/emc-census-2026-09-12'
    raw = out / 'sources'
    raw.mkdir(parents=True, exist_ok=True)
    queries, records = {}, []
    for name, query in QUERIES.items():
        pages, cursor, number = [], '*', 0
        while True:
            number += 1
            url = BASE + '?' + urlencode({'query': query, 'format': 'json', 'resultType': 'core' if name == 'expanded' else 'lite', 'pageSize': 100 if name == 'expanded' else 1, 'cursorMark': cursor})
            path = raw / f'{name}-{number:03}.json.gz'
            if path.exists() and not args.refresh:
                payload = gzip.decompress(path.read_bytes())
            else:
                payload = fetch(url)
                path.write_bytes(gzip.compress(payload, mtime=0))
            data = json.loads(payload)
            pages.append({'file': str(path.relative_to(ROOT)).replace('\\', '/'), 'url': url, 'sha256': hashlib.sha256(payload).hexdigest()})
            batch = data.get('resultList', {}).get('result', [])
            if name == 'expanded':
                records.extend(batch)
            queries[name] = {'query': query, 'hit_count': data['hitCount'], 'pages': pages}
            print(name, number, data['hitCount'], len(batch), flush=True)
            nxt = data.get('nextCursorMark')
            if name != 'expanded' or not batch or not nxt or nxt == cursor or len(records) >= data['hitCount']:
                break
            cursor = nxt
            time.sleep(.4)
    # Deduplicate identifiers/DOIs; retain linked source IDs. Study-level and version
    # deduplication require adjudication and are deliberately not inferred here.
    normalized, by_key = [], {}
    for r in records:
        p = normalize(r)
        key = p['doi'].lower() if p['doi'] else p['id']
        if key in by_key:
            old = by_key[key]
            old.setdefault('other_record_ids', []).append(p['id'])
            old['free_links'] = list({x['url']: x for x in old['free_links'] + p['free_links']}.values())
            old['access'] = 'free_link_indexed' if old['free_links'] else 'unresolved'
        else:
            by_key[key] = p
            normalized.append(p)
    normalized.sort(key=lambda p: (p['year'], p['date'], p['title']), reverse=True)
    from collections import Counter
    manifest = {'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'queries': queries,
        'retrieved_records': len(records), 'deduplicated_records': len(normalized),
        'scope_counts': dict(Counter(p['discovery_scope'] for p in normalized)),
        'access_counts': dict(Counter(p['access'] for p in normalized)),
        'complete_worldwide_census': False,
        'limitations': ['Discovery records, not adjudicated EMC studies.', 'Conference coverage is incomplete; supplements, posters, datasets and unindexed outputs require separate searches.', 'DOI/identifier deduplication does not deduplicate studies, overlapping cohorts or preprint versions.', 'A free link is index metadata, not a successful full-text retrieval or reading.', 'Access unresolved never means no public version exists.', 'Full-text mention matches can be incidental; title matches can still be mimics or differential diagnoses.']}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    catalogue = {'updated_date': manifest['retrieved_utc'][:10], 'description': 'EMC research discovery catalogue — screening in progress',
        'counts': {k: manifest[k] for k in ('retrieved_records', 'deduplicated_records', 'scope_counts', 'access_counts')},
        'queries': {k: {'query': v['query'], 'hit_count': v['hit_count'], 'url': v['pages'][0]['url']} for k, v in queries.items()},
        'limitations': manifest['limitations'], 'records': normalized}
    (ROOT / 'site/literature.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: manifest[k] for k in ('retrieved_records', 'deduplicated_records', 'scope_counts', 'access_counts')}), flush=True)

if __name__ == '__main__':
    main()
