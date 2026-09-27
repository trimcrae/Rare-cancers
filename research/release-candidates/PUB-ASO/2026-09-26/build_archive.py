"""Prepare a local repository upload without republishing literature PDFs/figures."""
from pathlib import Path
import hashlib, json, zipfile

ROOT=Path(__file__).resolve().parent
E=ROOT/'evidence'
OUT=ROOT/'repository-deposit'; OUT.mkdir(exist_ok=True)
excluded=[]; files=[]
for p in sorted(E.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts:continue
    rel=p.relative_to(E)
    # Keep exact computational inputs, sequence references and source receipts.
    # Literature downloads remain in the review supplement and local evidence;
    # the public archive links them via the source ledger and retrieval receipts.
    if rel.parts[0]=='sources' and not (
        p.suffix=='.gb' or p.name.startswith(('ENSP','ENST','hg19-')) or
        '-RefSeq.json' in p.name or p.name in ['parent-refseq-accessions.json','DElite-metadata.csv','PRJNA692081-ena.tsv']):
        excluded.append(rel.as_posix());continue
    files.append(p)
rows=[dict(path='evidence/'+p.relative_to(E).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
with zipfile.ZipFile(OUT/'EMC-junction-provenance-data-and-code.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files:z.write(p,'evidence/'+p.relative_to(E).as_posix())
    z.writestr('archive-manifest.json',json.dumps(rows,indent=2)+'\n')
    z.write(ROOT/'supplementary-methods.md','source-ledger-and-methods.md')
    z.write(ROOT.parents[3]/'LICENSE','LICENSE')
    z.writestr('README.txt',
        'EMC junction provenance and normal-parent sequence comparisons\n\n'
        'Unzip, enter evidence, and run python analyze.py (Python 3.11 or later).\n'
        'All eleven result files should reproduce exactly; no extra packages or network are needed.\n'
        'The archive preserves computational inputs, versioned public sequence references, results,\n'
        'source receipts and corrections. Source-ledger-and-methods.md links original publications.\n'
        'Downloaded literature articles, abstracts, figures and supplements are omitted from this\n'
        'repository upload; this does not remove an input used by the offline sequence analysis.\n'
        'The journal review supplement retains the larger local source-evidence collection.\n'
        'Third-party sequence records retain their source attribution and applicable terms.\n'
        'Original repository software retains Apache-2.0 licensing; see LICENSE.\n'
        'The negative read-prefix experiment is optional to replay and needs a separate 128 MiB download.\n'
        'This is sequence evidence, not evidence of RNA cleavage, safety or therapeutic benefit.\n')
archive=OUT/'EMC-junction-provenance-data-and-code.zip'
(OUT/'archive-build.json').write_text(json.dumps(dict(files=len(rows),omitted_literature_files=excluded,archive=archive.name,bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),state='local_only_not_uploaded'),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(files=len(rows),bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest())))
