"""Small, bounded source retrieval; cached bytes and HTTP outcomes are retained."""
import datetime, hashlib, json, pathlib, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent
SOURCES = ROOT / 'sources'
SOURCES.mkdir(exist_ok=True)
LOG = ROOT / 'retrieval.jsonl'

def fetch(name, url, limit=20*1024*1024):
    dest = SOURCES / name
    if dest.exists():
        return dest
    row = dict(name=name, url=url, utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'EMC-junction-research/1.0'})
        with urllib.request.urlopen(req, timeout=45) as response:
            data = response.read(limit+1)
            if len(data)>limit:
                raise ValueError('bounded download exceeded limit')
            row.update(status=response.status, content_type=response.headers.get('Content-Type'), final_url=response.url)
        dest.write_bytes(data)
        row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    except Exception as exc:
        row['error'] = str(exc)
        dest = None
    with LOG.open('a',encoding='utf-8') as out:
        out.write(json.dumps(row)+'\n')
    print(json.dumps(row))
    return dest

if __name__ == '__main__':
    fetch('Bangerter-2023.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9813045/fullTextXML')
    fetch('Bangerter-figure4.png','https://media.springernature.com/full/springer-static/image/art%3A10.1007%2Fs13577-022-00818-x/MediaObjects/13577_2022_818_Fig4_HTML.png')
    for i in (1,2):
        fetch(f'Bangerter-supplement{i}.pdf',f'https://static-content.springer-cdn.com/esm/art%3A10.1007%2Fs13577-022-00818-x/MediaObjects/13577_2022_818_MOESM{i}_ESM.pdf')
