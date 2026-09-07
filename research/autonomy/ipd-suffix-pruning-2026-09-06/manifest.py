"""Archive the finished packet and read-only dependencies; exclude self manifest."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent.parent
files=[]
for p in sorted(ROOT.iterdir()):
    if p.is_file() and p.name!='manifest.json':files.append(p)
for name in ['frontier.py','results.json','protocol.md']:
    files.append(ROOT.parent/'ipd-frontier-bounds-2026-09-06'/name)
for name in ['bounds.py','verify.py','development-releases.json','stress-releases.json','development-results.json']:
    files.append(ROOT.parent/'ipd-bounds-development-2026-09-06'/name)
manifest={'schema':'ipd-suffix-checkpoint-manifest-v1','base_revision':'3aa9bfc2cc5e1d2e0ac6ba0f9162a6a620f5e7c8',
          'synthetic':True,'protocol_frozen_before_execution':True,'normal_preflight_claimed':False,
          'ultra_review_claimed':False,'processes_finished':True,
          'files':[{'path':p.relative_to(REPO).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'files':len(files),'protocol_sha256':hashlib.sha256((ROOT/'protocol.md').read_bytes()).hexdigest(),
                  'solver_sha256':hashlib.sha256((ROOT/'suffix.py').read_bytes()).hexdigest()}))
