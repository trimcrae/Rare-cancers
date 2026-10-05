from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent
d=json.loads((p/'SOURCE-DOCUMENTED-CONSTRUCTS.json').read_text())
for s in d['sources']:
 b=Path(s['path']).read_bytes();assert len(b)==s['bytes'] and hashlib.sha256(b).hexdigest()==s['sha256']
lines=Path(d['sources'][0]['path']).read_text().splitlines()
for x in d['pc_js_lines']:assert lines[x['line']-1]==x['text']
config=json.loads(Path(d['sources'][1]['path']).read_text())
assert config.get('API_URL') is None
assert 'config.API_URL' in lines[44]
assert '"/api/proxi/v0.1/datasets"' in lines[49] and '"/api/proxi/v0.1/datasets"' in lines[63]
print('PASS exact two original hashes/bytes, selected source lines, API_URL-only projection and both explicit fallbacks; zero network.')
