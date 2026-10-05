from pathlib import Path
import hashlib,json
from lxml import etree
b=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((b/'PORTABILITY.json').read_text())
assert r['new_raw_bytes']<=r['cap_bytes']
for a in r['raw_files']:
 p=b/a['path']; assert p.stat().st_size==a['bytes'] and sha(p)==a['sha256']
x=json.loads((b/'EVALUATED-PRIMARY-METHODS.json').read_text());t=etree.parse(str(b/x['source']['path']))
for title,ps in x['selected_sections'].items():
 ss=[s for s in t.xpath('//sec') if ' '.join(s.xpath('./title//text()'))==title]
 assert len(ss)==1 and [' '.join(p.xpath('.//text()')) for p in ss[0].xpath('./p')]==ps
for f in ['REUSED-DECISIONS.json','QPOP-REUSE-DISPOSITION.json']:
 for a in json.loads((b/f).read_text())['source_bindings']:
  p=Path(a['path']); assert sha(p)==a['sha256'] and p.stat().st_size==a['bytes']
print('PASS: all six raw hashes/bytes, three selected primary method sections and seven reused exact source bindings; no numerical endpoint analysis.')
