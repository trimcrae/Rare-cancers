#!/usr/bin/env python3
"""Extract published model-screen tables without pooling incompatible assays.

Requires openpyxl for read-only extraction. Original publisher files stay in cache;
the output preserves source cells, units, retrieval hashes and unresolved methods.
"""
import hashlib
import json
import shutil
from pathlib import Path
from urllib.request import urlopen
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache/emc-literature-fulltext'
OUT = ROOT / 'research/literature/emc-census-2026-09-12'


def extract():
    sources = json.loads((OUT / 'model-source-receipts.json').read_text())
    rows = []
    for number, first, fields in [
        (5, 4, ['cas', 'drug', 'viability_percent', 'sd_percentage_points']),
        (6, 4, ['cas', 'drug', 'ic50_nM']),
    ]:
        filename = f'Iwata2025-s{number}.xlsx'
        path = CACHE / filename
        source = next(s for s in sources if s['file'] == filename)
        if not path.exists():
            if shutil.disk_usage(ROOT).free < 10 * 1024**3 + 1024**2:
                raise RuntimeError('Insufficient headroom for 1 MiB scoped retrieval')
            CACHE.mkdir(parents=True, exist_ok=True)
            path.write_bytes(urlopen(source['url'], timeout=40).read())
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256']
        sheet = load_workbook(path, read_only=True, data_only=True).active
        table = []
        for index, values in enumerate(sheet.values, 1):
            if index < first or not values[1]:
                continue
            row = dict(zip(fields, values))
            row.update(sheet=sheet.title, source_row=index)
            table.append(row)
        assert len(table) == (221 if number == 5 else 24)
        rows.append({'source': source, 'records': table})
    return {
        'doi': '10.1007/s13577-025-01250-7',
        'publisher_url': 'https://link.springer.com/article/10.1007/s13577-025-01250-7',
        'extracted_date': '2026-09-12',
        'model': 'NCC-EMC1-C1', 'independent_patient_models': 1,
        'reading_scope': 'Publisher abstract and all rows of supplementary Tables 1, 3 and 4 read. Main methods, figures and remaining supplements pending.',
        'unresolved': [
            'Screen concentration, exposure duration, replicate count and normalization require main methods.',
            'Do not compare screen viability with IC50 or pool with the Bangerter assay.',
            'Salt forms and distinct CAS identifiers remain separate source rows.',
            'Negative normalized viability and values above 100 are preserved, not clipped.',
            'Supplementary figure caption says 21 agents whereas Table 4 lists 24; reconcile against full text.',
            'Low IC50 does not establish target dependence, selectivity, achievable exposure or clinical efficacy.'
        ], 'tables': rows,
    }


if __name__ == '__main__':
    result = extract()
    (OUT / 'iwata-2025-screen-extraction.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Extracted 221 screen rows and 24 IC50 rows with source-cell provenance.')
