"""Verify a newly extracted portable archive against its frozen accepted outputs.

Usage: python verify_archive.py --work NEW_DIRECTORY
Writes only to a new task-specific directory and the specified report path.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--work', type=Path, required=True)
p.add_argument('--report', type=Path, required=True)
args = p.parse_args()
args.work.mkdir(parents=True, exist_ok=False)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
with zipfile.ZipFile(ROOT / 'reproducibility.zip') as z:
    for name in z.namelist():
        dest = (args.work / name).resolve()
        assert dest.is_relative_to(args.work.resolve()), name
    z.extractall(args.work)
manifest = json.loads((args.work/'MANIFEST.json').read_text())
for entry in manifest:
    assert sha(args.work/entry['path']) == entry['sha256'], entry['path']
run = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(args.work/'2026-09-30-full-catalogue/analyze_catalogue.py'), '--output', str(args.work/'regenerated')], capture_output=True, text=True)
(args.work/'reproduction.stdout.txt').write_text(run.stdout,encoding='utf-8')
(args.work/'reproduction.stderr.txt').write_text(run.stderr,encoding='utf-8')
assert run.returncode == 0, run.stderr[-2000:]
comparisons=[]
for path in sorted((args.work/'regenerated').iterdir()):
    original=args.work/'2026-09-30-full-catalogue/results'/path.name
    assert original.is_file(),path.name
    same=sha(path)==sha(original)
    comparisons.append({'file':path.name,'sha256':sha(path),'byte_identical':same})
    assert same,path.name
result={'status':'PASS','purpose':'New portable archive dependency and reproduction check; accepted numerical verifier not rerun','archive_sha256':sha(ROOT/'reproducibility.zip'),'manifest_files_checked':len(manifest),'analysis_exit':run.returncode,'comparisons':comparisons}
args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','files_compared':len(comparisons),'archive_files':len(manifest)}))
