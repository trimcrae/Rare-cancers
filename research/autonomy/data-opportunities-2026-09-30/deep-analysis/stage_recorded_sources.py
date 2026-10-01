import json,urllib.request,hashlib
from pathlib import Path
root=Path('research/autonomy/data-opportunities-2026-09-30/deep-analysis')
p=root/'results/clinical-and-ASO-primary-supplements.json'
j=json.loads(p.read_text());out=root/'outputs/primary-supplements-staged.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(j['result']))
url='https://raw.githubusercontent.com/trimcrae/Rare-cancers/af7211708205b5189d8c537c1ce2a23aa4bea076/research/modalities/km-figure-readings.json'
with urllib.request.urlopen(url,timeout=60) as r:b=r.read(8*1024*1024+1)
assert len(b)<=8*1024*1024
q=root/'outputs/legacy-km-figure-readings.json';q.write_bytes(b)
print(json.dumps({'staged_primary':str(out),'primary_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'legacy_url':url,'legacy_sha256':hashlib.sha256(b).hexdigest()}))
