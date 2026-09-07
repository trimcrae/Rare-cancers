"""Download only identified primary methods bodies, preserving access receipts."""
from pathlib import Path
import datetime, hashlib, json, urllib.request
ROOT = Path(__file__).resolve().parent
CACHE = ROOT.parents[2] / '.cache' / 'ipd-partial-order-prior-art-2026-09-06'
CACHE.mkdir(parents=True, exist_ok=True)
SOURCES = {
 'coolen_monotonicity_author.pdf': 'https://tahanimaturi.com/pdfs/Logrank-ComStats-rev-20210507-Final.pdf',
 'interval_vignette.pdf': 'https://stat.ethz.ch/CRAN/web/packages/interval/vignettes/intervalCensoring.pdf',
 'coolen_accelerated.html': 'https://link.springer.com/article/10.1007/s00184-021-00807-4',
 'interval_ictest.R': 'https://raw.githubusercontent.com/cran/interval/master/R/ictest.R',
 'interval_ictest.Rd': 'https://raw.githubusercontent.com/cran/interval/master/man/ictest.Rd',
 'denoeux_rank.pdf': 'https://www.hds.utc.fr/~tdenoeux/dokuwiki/_media/en/publi/fss2642v4.pdf',
 'golovin_ecd.pdf': 'https://www.cs.cmu.edu/~dgolovin/papers/nips10.pdf',
 'coolen_monotonicity_publisher.pdf': 'https://www.tandfonline.com/doi/pdf/10.1080/03610926.2021.1952270',
}
receipts = []
old_path = ROOT/'sources'/'download-receipts.json'
old = {r['name']:r for r in json.loads(old_path.read_text())} if old_path.exists() else {}
for name, url in SOURCES.items():
    if name in old:
        receipts.append(old[name])
        continue
    row = dict(name=name, url=url, accessed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=25) as response:
            body=response.read()
            row.update(status=response.status, final_url=response.url, content_type=response.headers.get('Content-Type'))
        path=CACHE/name
        path.write_bytes(body)
        row.update(bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), local_path=str(path))
        if name.endswith('.pdf'):
            from pypdf import PdfReader
            pages=PdfReader(path).pages
            (CACHE/(name+'.txt')).write_text('\n'.join(f'\n=== PDF PAGE {i+1} ===\n'+p.extract_text() for i,p in enumerate(pages)), encoding='utf-8')
            row['pdf_pages']=len(pages)
    except Exception as exc:
        row['error']=str(exc)
    receipts.append(row)
    print(json.dumps(row))
(ROOT/'sources'/'download-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n', encoding='utf-8')
