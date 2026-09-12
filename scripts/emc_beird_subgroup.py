#!/usr/bin/env python3
"""Recover the HEMCSS column from the authors' published 2026 screen matrix.

This preserves a historical-model subgroup, not molecularly confirmed EMC evidence.
No cross-assay potency pooling or normal-tissue selectivity inference is performed.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/literature/emc-census-2026-09-12'
CACHE = ROOT / '.cache/emc-literature-fulltext/beird2026'
NAME = 'GCC_SARC_ALl_AUC_FA-2016_inputforfilter-250815.txt'
MATCHES = {
    'BORTEZOMIB': 'bortezomib',
    'DOXORUBICIN HYDROCHLORIDE': 'doxorubicin hydrochloride',
    'CARFILZOMIB': 'carfilzomib',
    'PANOBINOSTAT (LBH589)': 'panobinostat',
    'ABT-199 (GDC-0199)': 'venetoclax',
}


def extract():
    receipts = json.loads((OUT / 'beird-2026-source-receipts.json').read_text())
    source = next(x for x in receipts if x['file'] == NAME)
    path = CACHE / NAME
    if not path.exists():
        if shutil.disk_usage(ROOT).free < 10 * 1024**3 + 1024**2:
            raise RuntimeError('Insufficient headroom for 1 MiB scoped retrieval')
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_bytes(urlopen(source['url'], timeout=40).read())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256']
    # The source contains byte 0xb1 and is not valid UTF-8. Preserve raw bytes;
    # Windows-1252 decodes the source labels without dropping characters.
    reader = csv.DictReader(io.StringIO(path.read_bytes().decode('cp1252')), delimiter='\t')
    rows, matched = [], []
    for index, row in enumerate(reader, 2):
        value = float(row['HEMCSS']) if row['HEMCSS'].strip() else None
        record = {'source_row': index, 'compound': row['cmpd1'], 'HEMCSS_auc': value}
        rows.append(record)
        if row['cmpd1'] in MATCHES:
            comparators = [float(v) for k, v in row.items() if k not in ('cmpd1', 'HEMCSS') and v.strip()]
            matched.append(dict(record, normalized_name=MATCHES[row['cmpd1']],
                other_cancer_models_measured=len(comparators),
                other_cancer_models_mean_auc=sum(comparators)/len(comparators),
                other_cancer_models_with_higher_auc=sum(v > value for v in comparators)))
    assert len(rows) == 1387 and len(matched) == len(MATCHES)
    return {'doi': '10.1158/2767-9764.CRC-26-0142',
        'dataset_doi': '10.5281/zenodo.19098295',
        'publisher_url': 'https://aacrjournals.org/cancerrescommun/article/6/6/1425/785836/Drug-Screening-of-Sarcoma-Cells-Finding-Shared',
        'source': source, 'source_encoding_used': 'cp1252',
        'extracted_date': '2026-09-12', 'model': 'H-EMC-SS',
        'model_identity': 'Authors dataset maps HEMCSS to CVCL_1238 and CS. Gartrell Figure 2 reports no detected EWSR1 translocation; not treated as a confirmed NR4A3-fusion model.',
        'metric': 'Published normalized AUC of fraction affected; higher indicates stronger growth inhibition within this assay. Preserve negative values.',
        'limitations': ['These are one model subgroup values, not patient outcomes.',
            'Comparator means describe other cancer models, not a therapeutic window.',
            'Matched drug names are explicit aliases, not substring matches.',
            'Main paper partly read; figures, QC and complete supplemental analysis remain pending.',
            'All 1387 values extracted computationally; this is not a claim of manual review of every row.'],
        'cross_study_candidates': matched, 'records': rows}


if __name__ == '__main__':
    result = extract()
    (OUT / 'beird-2026-hemcss-extraction.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(result['cross_study_candidates'], indent=2))
