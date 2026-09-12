#!/usr/bin/env python3
"""Recover focused PMC texts to a local cache; receipt never asserts they were read."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
from emc_literature_census import fetch

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache/emc-literature-fulltext'
OUT = ROOT / 'research/literature/emc-census-2026-09-12'

def retrieve(p):
    pmcid = p['pmcid']
    url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML'
    row = {'id': p['id'], 'pmcid': pmcid, 'url': url, 'reading_status': 'not_read', 'supplements_checked': False, 'figures_checked': False}
    path = CACHE / (pmcid + '.xml.gz')
    try:
        if path.exists():
            payload = gzip.decompress(path.read_bytes())
        else:
            payload = fetch(url)
        root = ET.fromstring(payload)
        body = root.find('body')
        if root.tag != 'article' or body is None:
            raise ValueError('Response is not an article with body text')
        path.write_bytes(gzip.compress(payload, mtime=0))
        blocks = []
        for section in [root.find('front'), body, root.find('back')]:
            if section is not None:
                blocks.append('\n'.join(' '.join(''.join(el.itertext()).split()) for el in section.iter() if el.tag in ('article-title','title','p','table','ref','caption')))
        text = '\n\n'.join(blocks)
        (CACHE / (pmcid + '.txt')).write_text(text, encoding='utf-8')
        row.update({'retrieval_status': 'body_xml_retrieved', 'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest(), 'text_characters': len(text),
            'supplement_references': len(list(root.iter('supplementary-material'))), 'figure_count': len(list(root.iter('fig')))})
    except Exception as error:
        row.update({'retrieval_status': 'unresolved', 'error': str(error)[:250]})
    return row

def main():
    if shutil.disk_usage(ROOT).free < 10 * 1024**3 + 200 * 1024**2:
        raise SystemExit('Insufficient headroom for a 200 MiB retrieval budget')
    CACHE.mkdir(parents=True, exist_ok=True)
    data = json.loads((ROOT / 'site/literature.json').read_text(encoding='utf-8'))
    papers = {p['pmcid']: p for p in data['records'] if p['pmcid'] and p['discovery_scope'] != 'full_text_or_index'}
    rows = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        for row in pool.map(retrieve, papers.values()):
            rows.append(row)
            if len(rows) % 20 == 0:
                print(f'Retrieved/attempted {len(rows)}/{len(papers)}', flush=True)
            (OUT / 'retrieval-ledger.json').write_text(json.dumps({'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                'scope': 'Title/abstract matched records with a PMC identifier only. Retrieval is not reading. Figures/supplements not verified.', 'records': rows}, indent=2) + '\n', encoding='utf-8')
    print('Finished', len(rows), 'attempts;', sum(r['retrieval_status'] == 'body_xml_retrieved' for r in rows), 'article bodies recovered', flush=True)

if __name__ == '__main__':
    main()
