"""Verify the independent frozen repository trace and bind selected review files."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
S=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics/research/autonomy/fresh-discovery-2026-10-04-round3/mirna_deposition')
manifest=S/'file-manifest.json'
expected='e17b1efbd2d4c8e2597cd981f559b3ebf96ff709565f74663946c71e325f67ac'
assert hashlib.sha256(manifest.read_bytes()).hexdigest()==expected
rows=[]
for name in ['file-manifest.json','freeze-status.json','RESULTS.txt','COVERAGE.txt','HANDOFF.txt','AMENDMENT-01.txt','trace-evaluation.json','linked-project-evaluation.json']:
    p=S/name;raw=p.read_bytes()
    rows.append(dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
(B/'deposition-review-reuse.json').write_text(json.dumps(dict(checked_utc=datetime.now(timezone.utc).isoformat(),source_manifest_verified=True,files=rows,
 scope='Independent deposition trace and complete candidate metadata; no numerical miRNA values. Scientific source-gate interpretation reviewed in COVERAGE.txt.'),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(bound_files=len(rows),source_manifest_sha256=expected)))
