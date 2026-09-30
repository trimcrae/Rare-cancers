"""Capture small attributable PGR inputs. Run once; offline analysis uses saved bytes."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / 'sources'


def fetch(name, url):
    path = SOURCES / name
    if path.exists():
        raise FileExistsError(f'Refusing to replace captured evidence: {path}')
    with urlopen(Request(url, headers={'User-Agent': 'EMC-sequence-research/1.0'}), timeout=45) as response:
        data = response.read()
        receipt = dict(file=name, url=url, final_url=response.url, status=response.status,
                       retrieved_utc=datetime.now(timezone.utc).isoformat(), bytes=len(data),
                       sha256=hashlib.sha256(data).hexdigest())
    path.write_bytes(data)
    with (SOURCES / 'retrieval.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(receipt) + '\n')
    return data


def main():
    SOURCES.mkdir(exist_ok=True)
    gene = json.loads(fetch('PGR-Ensembl-gene.json',
        'https://rest.ensembl.org/lookup/id/ENSG00000082175?content-type=application/json'))
    assert gene['display_name'] == 'PGR' and gene['assembly_name'] == 'GRCh38'
    url = ('https://api.genome.ucsc.edu/getData/track?genome=hg38;track=ncbiRefSeqCurated;'
           f"chrom=chr{gene['seq_region_name']};start={gene['start']-1};end={gene['end']}")
    track = json.loads(fetch('PGR-hg38-RefSeq.json', url))
    rows = [r for r in track['ncbiRefSeqCurated'] if r['name2'] == 'PGR']
    accessions = sorted({r['name'] for r in rows})
    assert accessions and all(re.fullmatch(r'N[MR]_\d+\.\d+', a) for a in accessions)
    fetch('PGR-curated-RefSeq.gb',
          'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id='
          + ','.join(accessions) + '&rettype=gbwithparts&retmode=text')
    (SOURCES / 'PGR-accessions.json').write_text(json.dumps(
        dict(gene='PGR', assembly='hg38', selection="name2 == 'PGR' within captured gene-interval query",
             accessions=accessions, query_records=len(track['ncbiRefSeqCurated']),
             included_records=len(rows)), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(accessions=accessions, source_bytes=sum(p.stat().st_size for p in SOURCES.iterdir()))))


if __name__ == '__main__':
    main()
