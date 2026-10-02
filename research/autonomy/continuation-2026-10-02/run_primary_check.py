"""Bounded cloud launch of independent primary workbook re-extraction."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

HERE=Path(__file__).resolve().parent
OUT=HERE/'primary-check-output'
assert shutil.disk_usage(HERE).free >= 10*1024**3+128*1024**2
OUT.mkdir(exist_ok=False)
plan=json.loads((HERE/'foundation/foundation_recovery_check.json').read_text())
for key,name in [('mapping','mapping.json'),('export','data_sv.txt')]:
    source=plan[key]
    with urllib.request.urlopen(source['url'],timeout=45) as response:
        raw=response.read(source['bytes']+1)
    assert len(raw)==source['bytes'] and hashlib.sha256(raw).hexdigest()==source['sha256']
    (OUT/name).write_bytes(raw)
corrected=HERE/'verification-artifacts/small/outputs-small/foundation/data_sv.identity_corrected.tsv'
start=time.monotonic()
command=[sys.executable,str(HERE/'foundation/foundation_primary_workbook_check.py'),
         '--fetch-primary','--mapping',str(OUT/'mapping.json'),'--export',str(OUT/'data_sv.txt'),
         '--corrected',str(corrected)]
run=subprocess.run(command,capture_output=True,text=True,timeout=240)
try:
    result=json.loads(run.stdout)
except Exception:
    raise RuntimeError(run.stderr[-2000:])
result['execution']={'commit':__import__('os').environ['GITHUB_SHA'],
                     'run_id':__import__('os').environ['GITHUB_RUN_ID'],
                     'returncode':run.returncode,'seconds':time.monotonic()-start}
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print('EMC_PRIMARY_WORKBOOK_BEGIN')
print(json.dumps(result,indent=2))
print('EMC_PRIMARY_WORKBOOK_END')
sys.exit(run.returncode)
