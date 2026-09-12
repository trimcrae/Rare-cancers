#!/usr/bin/env python3
"""Add title-matched Crossref discovery records; preserve the original census."""
from collections import Counter
import gzip
import json
import re
from pathlib import Path
from urllib.parse import urlencode
from emc_literature_census import fetch, plain, DISEASE, normalize

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/literature/emc-census-2026-09-12'

def main():
    params = {'query.title': 'extraskeletal myxoid chondrosarcoma', 'rows': 1000,
        'select': 'DOI,title,author,type,published,container-title,URL'}
    url = 'https://api.crossref.org/works?' + urlencode(params)
    cache = OUT / 'sources/crossref-title-1000.json.gz'
    if cache.exists():
        payload = gzip.decompress(cache.read_bytes())
    else:
        payload = fetch(url)
        cache.write_bytes(gzip.compress(payload, mtime=0))
    response = json.loads(payload)
    records = response['message']['items']
    data = json.loads((ROOT / 'site/literature.json').read_text(encoding='utf-8'))
    known = {p['doi'].lower() for p in data['records'] if p['doi']}
    added = []
    matched = 0
    for r in records:
        title = plain(' '.join(r.get('title', [])))
        if not DISEASE.search(title):
            continue
        matched += 1
        doi = r['DOI'].lower()
        if doi in known:
            continue
        known.add(doi)
        parts = r.get('published', {}).get('date-parts', [[]])[0]
        year = str(parts[0]) if parts else ''
        authors = ', '.join(' '.join(filter(None, [a.get('given'), a.get('family')])) for a in r.get('author', []))
        # Supplement identifiers are a screening hint, not confirmation of report type.
        types = [r.get('type', 'unknown')]
        record = {'id': 'DOI:' + doi, 'title': title, 'authors': authors, 'year': year,
            'date': '-'.join(str(x).zfill(2) for x in parts), 'journal': '; '.join(r.get('container-title', [])),
            'doi': doi, 'pmid': '', 'pmcid': '', 'publication_types': types,
            'record_url': 'https://doi.org/' + doi, 'publisher_url': 'https://doi.org/' + doi,
            'free_links': [], 'access': 'unresolved', 'discovery_scope': 'title',
            'screening_status': 'not_adjudicated', 'reading_status': 'not_read', 'abstract_available': False,
            'metadata_source': 'Crossref title relevance search, first 1000 results'}
        added.append(record)
    data['records'].extend(added)
    historical = OUT / 'sources/historical-model-aliases.json.gz'
    if historical.exists():
        query = '("H-EMC-SS" OR "HEMCSS" OR "hTAFII68-TEC" OR "hTAF(II)68-TEC" OR "TAF2N-TEC" OR "EWS-NOR1" OR "CHN-EWS")'
        results = json.loads(gzip.decompress(historical.read_bytes()))
        batch = results['resultList']['result']
        if len(batch) != results['hitCount']:
            raise ValueError('Historical query needs pagination')
        aliases = re.compile(r'H[ -]?EMC[ -]?SS|HEMCSS|hTAF.*?68[ -]TEC|TAF2N[ -]TEC|EWS[ -]NOR1|CHN[ -]EWS', re.I)
        ids = {p['id'] for p in data['records']}
        dois = {p['doi'].lower() for p in data['records'] if p['doi']}
        for raw in batch:
            p = normalize(raw)
            if p['id'] in ids or (p['doi'] and p['doi'].lower() in dois):
                continue
            p['metadata_source'] = 'Europe PMC historical fusion and model aliases'
            if aliases.search(p['title']):
                p['discovery_scope'] = 'title'
            elif aliases.search(plain(raw.get('abstractText'))):
                p['discovery_scope'] = 'abstract'
            if raw['source'] == 'PAT':
                p['publication_types'] = ['Patent']
            data['records'].append(p)
            ids.add(p['id'])
            if p['doi']:
                dois.add(p['doi'].lower())
        data['queries']['historical_models'] = {
            'query': query, 'hit_count': results['hitCount'],
            'url': 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urlencode({'query': query, 'format': 'json', 'resultType': 'core', 'pageSize': 1000}),
            'note': 'Historical model and fusion names; model identity and incidental mentions require adjudication.',
        }
    manual = OUT / 'manual-records.json'
    if manual.exists():
        entries = json.loads(manual.read_text(encoding='utf-8'))['records']
        # Preserve report manifestations with stable society identifiers; suspected
        # journal/cohort relationships are annotated rather than silently merged.
        ids = {p['id'] for p in data['records']}
        data['records'].extend(p for p in entries if p['id'] not in ids)
        by_id = {p['id']: p for p in entries}
        for p in data['records']:
            if p['id'] in by_id:
                p.update(by_id[p['id']])
        data['counts']['manually_sourced_reports'] = len(entries)
    # These two conference records have been read from their public ASCO source.
    # This does not resolve other reports from the same cohort.
    verified = {
        '10.1200/jco.2025.43.16_suppl.11513': ('https://ascopubs.org/doi/10.1200/JCO.2025.43.16_suppl.11513', 'abstract_read'),
        '10.1200/jco.2026.44.16_suppl.e23561': ('https://ascopubs.org/doi/10.1200/JCO.2026.44.16_suppl.e23561', 'not_read'),
    }
    for p in data['records']:
        if p['doi'].lower() in verified:
            source_url, reading = verified[p['doi'].lower()]
            p['publication_types'] = ['Conference abstract']
            p['reading_status'] = reading
            p['screening_status'] = 'EMC_report_identified'
            if reading == 'abstract_read':
                p['free_links'] = [{'url': source_url, 'label': 'Free conference abstract', 'evidence': 'ASCO publisher abstract read 2026-09-12; not a full journal report'}]
                p['access'] = 'free_link_indexed'
    overrides = json.loads((ROOT / 'site/literature-overrides.json').read_text(encoding='utf-8'))
    for p in data['records']:
        p['title'] = plain(p['title'])
        p.update(overrides['records'].get(p['doi'].lower(), {}))
        p['access'] = 'free_link_indexed' if p['free_links'] else 'unresolved'
    data['records'].sort(key=lambda p: (p['year'], p['date'], p['title']), reverse=True)
    data['queries']['crossref_title'] = {'query': params['query.title'], 'hit_count': response['message']['total-results'], 'url': url,
        'retrieved': len(records), 'title_matched': matched, 'new_records': sum(p.get('metadata_source', '').startswith('Crossref') for p in data['records']),
        'note': 'Fuzzy relevance search; total-results is not an EMC count. Only disease/fusion title matches from the first 1000 results are included.'}
    pubmed = OUT / 'pubmed-count.json'
    if pubmed.exists():
        result = json.loads(pubmed.read_text(encoding='utf-8-sig'))
        data['queries']['pubmed_exact_phrase'] = {'query': '"extraskeletal myxoid chondrosarcoma"',
            'hit_count': int(result['esearchresult']['count']),
            'url': 'https://pubmed.ncbi.nlm.nih.gov/?term=%22extraskeletal+myxoid+chondrosarcoma%22',
            'note': 'Independent count check; record-level PubMed union not yet performed.'}
        union = OUT / 'sources/pubmed-union.json.gz'
        if union.exists():
            result = json.loads(gzip.decompress(union.read_bytes()))['esearchresult']
            missing = sorted(set(result['idlist']) - {p['pmid'] for p in data['records']})
            if len(result['idlist']) != int(result['count']) or missing:
                raise ValueError('PubMed union requires missing record recovery: ' + repr(missing))
            data['queries']['pubmed_exact_phrase'].update(hit_count=int(result['count']),
                note=f"All {result['count']} PubMed identifiers were retrieved and matched to catalogue records; no additional records from this exact-phrase query.")
    data['counts'].update({'deduplicated_records': len(data['records']), 'scope_counts': dict(Counter(p['discovery_scope'] for p in data['records'])),
        'access_counts': dict(Counter(p['access'] for p in data['records'])), 'crossref_added': data['queries']['crossref_title']['new_records']})
    (ROOT / 'site/literature.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    (OUT / 'crossref-summary.json').write_text(json.dumps(data['queries']['crossref_title'], indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(data['counts']))

if __name__ == '__main__':
    main()
