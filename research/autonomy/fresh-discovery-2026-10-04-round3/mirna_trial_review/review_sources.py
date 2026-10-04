"""Read-only source binding and selected registry/HTML checks; no biological calculation."""
import hashlib, json, re, shutil
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

B = Path(__file__).resolve().parent
S = Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-functional/research/autonomy/fresh-discovery-2026-10-04-round3/mirna_trial')
assert shutil.disk_usage(B).free >= 10 * 1024**3
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]
    def handle_data(self, data): self.parts.append(data)

names = ['PLAN.txt', 'AMENDMENT-01.txt', 'source-receipts.json', 'mirror-receipts.json', 'decoded-image-receipts.json',
 'trial-NCT06260774.json', 'esmo-poster-mirror.decoded.html', 'esmo-poster-mirror-tm2528668d1_ex99-2img001.jpg',
 'june-deck-mirror.decoded.html', 'june-deck-mirror-tm2618153d1_ex99-1img013.jpg', 'june-deck-mirror-tm2618153d1_ex99-1img017.jpg',
 'sept-release-mirror.decoded.html', 'sept-release-mirror-tm2626237d1_ex99-1img01.jpg',
 'march-receipt.json', 'march2026-selected.pdf', 'march2026-selected-text.json', 'march-slide18.jpg']
bindings=[]
for name in names:
    p=S/name; raw=p.read_bytes()
    bindings.append(dict(path=str(p), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
trial=json.loads((S/'trial-NCT06260774.json').read_text(encoding='utf-8'))
protocol=trial['protocolSection']
html_checks=[]
for name in ['june-deck-mirror.decoded.html','sept-release-mirror.decoded.html']:
    parser=Text(); parser.feed((S/name).read_text(encoding='utf-8'))
    text=re.sub(r'\s+', ' ', ' '.join(parser.parts))
    words=['September', 'June', '2026', '102-001', 'NCT06260774', '18 months', '16 months']
    hits=[]
    for word in words:
        for m in list(re.finditer(re.escape(word), text, re.I))[:3]:
            hits.append(dict(term=word, context=text[max(0,m.start()-100):m.end()+220]))
    html_checks.append(dict(file=name, contexts=hits))
out=dict(checked_utc=datetime.now(timezone.utc).isoformat(), source_bindings=bindings,
 registry=dict(identification=protocol['identificationModule'], status=protocol['statusModule'],
 enrollment=protocol['designModule']['enrollmentInfo'], hasResults=trial['hasResults']),
 html_contexts=html_checks,
 limitations='Manual visual labels are recorded separately. No pixel digitization, outcome estimate, efficacy estimate or target-engagement inference was performed.')
(B/'source-crosscheck.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(bound_files=len(bindings), registry_id=out['registry']['identification']['nctId'], html_contexts=html_checks),indent=2))
