#!/usr/bin/env python3
"""Retrieve public Europe PMC figures/supplements with bounded local storage.

Retrieval is never a reading receipt. Nested archives are retained, not extracted.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache/emc-literature-fulltext'
OUT = ROOT / 'research/literature/emc-census-2026-09-12/asset-retrieval-ledger.json'
CAP = 10 * 1024**2
EXPANSION = 25 * 1024**2


def retrieve(pmc):
    if not re.fullmatch(r'PMC[0-9]+', pmc):
        raise ValueError('Expected a PMC identifier')
    url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/supplementaryFiles'
    if shutil.disk_usage(ROOT).free < 10 * 1024**3 + CAP + EXPANSION:
        raise RuntimeError('Insufficient storage headroom')
    CACHE.mkdir(parents=True, exist_ok=True)
    archive = CACHE / (pmc + '-assets.zip')
    payload = archive.read_bytes() if archive.exists() else urlopen(url, timeout=30).read(CAP + 1)
    if len(payload) > CAP:
        raise ValueError('Archive exceeds 10 MiB cap')
    source = zipfile.ZipFile(io.BytesIO(payload))
    if sum(m.file_size for m in source.infolist()) > EXPANSION:
        raise ValueError('Archive exceeds 25 MiB expansion cap')
    if not archive.exists():
        archive.write_bytes(payload)
    dest = CACHE / (pmc + '-assets')
    dest.mkdir(exist_ok=True)
    files, names = [], set()
    for member in source.infolist():
        if member.is_dir():
            continue
        # Never extract archive paths or run embedded content.
        name = Path(member.filename.replace('\\', '/')).name
        if name in names:
            raise ValueError('Colliding archive basenames')
        names.add(name)
        content = source.read(member)
        receipt = {'name': name, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}
        if Path(name).suffix.lower() in ('.jpg', '.jpeg', '.png', '.pdf', '.zip', '.tif', '.tiff', '.xlsx', '.docx'):
            target = dest / name
            if not target.exists():
                target.write_bytes(content)
            elif target.read_bytes() != content:
                raise ValueError('Existing asset differs from retrieved source: ' + name)
            receipt['local_file'] = str(target.relative_to(ROOT)).replace('\\', '/')
        files.append(receipt)
    return {'pmcid': pmc, 'url': url, 'archive_sha256': hashlib.sha256(payload).hexdigest(),
            'archive_bytes': len(payload), 'files': files, 'reading_status': 'not_inferred_from_retrieval'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pmcids', nargs='+')
    args = parser.parse_args()
    ledger = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {}
    for pmc in args.pmcids:
        try:
            ledger[pmc] = retrieve(pmc)
            print(pmc, len(ledger[pmc]['files']), 'assets indexed')
        except Exception as error:
            print(pmc, type(error).__name__, str(error))
            ledger.setdefault(pmc, {'pmcid': pmc})['latest_retrieval_error'] = str(error)
        OUT.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
