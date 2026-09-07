"""Hash the frozen bounded-round artifacts and their repository inputs."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

files=[p for p in ROOT.rglob('*') if p.is_file() and p.name!='hash-manifest.json' and '__pycache__' not in p.parts]
inputs=['AGENTS.md','research/autonomy/OPERATING_PROTOCOL.md',
        'research/autonomy/portfolio-2026-09-05/recommendation.md',
        'research/autonomy/trial-discoverability-2026-09-05/decision.md',
        'research/literature/emc-ipd-admissibility-2026-08-12.json',
        'research/modalities/emc-ipd-survival.json','research/modalities/emc_ipd_survival.py']
payload={'algorithm':'sha256','base_revision':'b72f8ad547b29daca2e460da9278fff6ec252117',
         'artifacts':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sorted(files)},
         'repository_inputs':{p:digest(REPO/p) for p in inputs},
         'note':'Self excluded; coordinator commits source and generated data together. No worker commit authorized.'}
(ROOT/'hash-manifest.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(files),'manifest_sha256':digest(ROOT/'hash-manifest.json')}))
