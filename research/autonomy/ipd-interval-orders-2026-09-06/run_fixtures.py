import json,subprocess,sys,time
from pathlib import Path
p=Path(__file__).resolve().parent;(p/'results').mkdir(exist_ok=True);runs=[]
for name in ['wide','exact_boundary','ordered_impossible','unknown_events','n3_boundary']:
 command=[sys.executable,'-B',str(p/'oracle.py'),str(p/'releases'/f'{name}.json'),str(p/'results'/f'{name}.json'),'--node-limit','1000000'];t=time.monotonic()
 with (p/'results'/f'{name}.log').open('w') as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 runs.append(dict(case=name,command=command,exit_code=r.returncode,elapsed_seconds=time.monotonic()-t));print(runs[-1],flush=True)
(p/'runs.json').write_text(json.dumps(runs,indent=2)+'\n')
