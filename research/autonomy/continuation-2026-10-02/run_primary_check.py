"""Bounded cloud launch of independent primary workbook re-extraction."""
import hashlib
import argparse
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
parser=argparse.ArgumentParser(description=__doc__)
source_args=parser.add_mutually_exclusive_group()
source_args.add_argument('--workbook',type=Path)
source_args.add_argument('--archive',type=Path)
args=parser.parse_args()
source_option=['--workbook',str(args.workbook.resolve())] if args.workbook else (['--archive',str(args.archive.resolve())] if args.archive else ['--fetch-primary'])
command=[sys.executable,str(HERE/'foundation/foundation_primary_workbook_check.py'),
         *source_option,'--mapping',str(OUT/'mapping.json'),'--export',str(OUT/'data_sv.txt'),
         '--corrected',str(corrected)]
try:
    run=subprocess.run(command,capture_output=True,text=True,timeout=240)
    returncode=run.returncode
    try:
        result=json.loads(run.stdout)
    except (ValueError,TypeError):
        result={'schema':'foundation-primary-workbook-independent-check/1','status':'failed',
                'error_type':'InvalidReceipt','message':run.stderr[-1500:]}
        returncode=returncode or 1
except subprocess.TimeoutExpired:
    returncode=124
    result={'schema':'foundation-primary-workbook-independent-check/1','status':'failed',
            'error_type':'TimeoutExpired','message':'Primary extraction subprocess exceeded240seconds; no verification claim.'}
result['execution']={'commit':__import__('os').environ['GITHUB_SHA'],
                     'run_id':__import__('os').environ['GITHUB_RUN_ID'],
                     'returncode':returncode,'seconds':time.monotonic()-start}
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print('EMC_PRIMARY_WORKBOOK_BEGIN')
print(json.dumps(result,indent=2))
print('EMC_PRIMARY_WORKBOOK_END')
sys.exit(returncode)
