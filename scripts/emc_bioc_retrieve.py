"""Recover unresolved PMC text via the documented NCBI BioC API.

Source files stay in the local cache. A successful download never earns reading
credit, and BioC conversion does not replace figure/supplement inspection.
"""
import hashlib
import json
import shutil
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/literature/emc-census-2026-09-12'
CACHE = ROOT / '.cache/emc-literature-fulltext'


def retrieve(pmc):
    url = f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{pmc}/unicode'
    row = {'pmcid': pmc, 'url': url, 'reading_status': 'not_inferred_from_retrieval'}
    try:
        path = CACHE / (pmc + '-bioc.json')
        if path.exists():
            payload = path.read_bytes()
        else:
            with urllib.request.urlopen(url, timeout=25) as response:
                payload = response.read(5 * 1024**2 + 1)
        if len(payload) > 5 * 1024**2:
            raise ValueError('Exceeded 5 MiB per-article limit')
        data = json.loads(payload)
        docs = [doc for collection in data for doc in collection.get('documents', [])]
        matched = [d for d in docs if str(d.get('id', '')).removeprefix('PMC') == pmc.removeprefix('PMC')]
        if len(matched) != 1:
            raise ValueError('Missing or mismatched PMC identifier')
        passages = matched[0].get('passages', [])
        body = [p for p in passages if p.get('infons', {}).get('section_type') in ('INTRO', 'METHODS', 'RESULTS', 'DISCUSS', 'CONCL', 'CASE')]
        if not body or sum(len(p.get('text', '')) for p in body) < 500:
            raise ValueError('No substantial article body identified; manual review required')
        if not path.exists():
            path.write_bytes(payload)
        row.update(retrieval_status='body_bioc_retrieved', bytes=len(payload),
                   sha256=hashlib.sha256(payload).hexdigest(), body_passages=len(body),
                   license=matched[0].get('infons', {}).get('license', ''),
                   local_file=str(path.relative_to(ROOT)).replace('\\', '/'))
    except Exception as error:
        row.update(retrieval_status='unresolved', error=str(error)[:200])
    return row


if __name__ == '__main__':
    if shutil.disk_usage(ROOT).free < 10 * 1024**3 + 200 * 1024**2:
        raise SystemExit('Insufficient headroom for bounded recovery')
    source = json.loads((OUT / 'retrieval-ledger.json').read_text(encoding='utf-8'))
    ids = sorted({r['pmcid'] for r in source['records'] if r['retrieval_status'] == 'unresolved'})
    rows = []
    for pmc in ids:
        row = retrieve(pmc)
        rows.append(row)
        result = {'retrieved_utc': datetime.now(timezone.utc).isoformat(),
                  'scope': 'Alternative retrieval of the 37 unresolved PMC records from the initial focused retrieval ledger; not exhaustive literature reading.',
                  'records': rows}
        (OUT / 'bioc-recovery-ledger.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
        print(len(rows), '/', len(ids), pmc, row['retrieval_status'], flush=True)
