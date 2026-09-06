"""Package exact existing artifacts and frozen inputs; no scientific evaluation."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

HERE=Path(__file__).resolve().parent
AUTONOMY=HERE.parent
ORIGINAL=AUTONOMY/'trial-frozen-baseline-2026-09-06'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8'))

freeze=read(ORIGINAL/'freeze.json')
for rel,digest in freeze['hashes'].items(): assert sha(AUTONOMY/rel)==digest,rel
outputs=read(ORIGINAL/'output-manifest.json')
assert {p.name for p in ORIGINAL.iterdir() if p.is_file()}==set(outputs)|{'output-manifest.json'}
for name,digest in outputs.items(): assert sha(ORIGINAL/name)==digest,name
for name,digest in read(ORIGINAL/'first-run-hashes.json').items(): assert sha(ORIGINAL/name)==digest,name
paths={AUTONOMY/rel for rel in freeze['hashes']}|{p for p in ORIGINAL.iterdir() if p.is_file()}
entries={p.relative_to(AUTONOMY).as_posix():{'size':p.stat().st_size,'sha256':sha(p)} for p in sorted(paths)}
archive=HERE/'frozen-experiment.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name in entries:
        info=zipfile.ZipInfo(name,date_time=(2026,9,6,0,0,0))
        info.compress_type=zipfile.ZIP_STORED if name.endswith('.gz') else zipfile.ZIP_DEFLATED
        info.external_attr=0o100644<<16
        z.writestr(info,(AUTONOMY/name).read_bytes())
with zipfile.ZipFile(archive) as z:
    assert set(z.namelist())==set(entries)
    for name,entry in entries.items():
        b=z.read(name); assert len(b)==entry['size'] and hashlib.sha256(b).hexdigest()==entry['sha256']
manifest={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'path_root':'research/autonomy','archive':'frozen-experiment.zip','archive_size':archive.stat().st_size,
    'archive_sha256':sha(archive),'entries':entries,
    'freeze_inputs_verified':len(freeze['hashes']),'original_output_manifest_entries_verified':len(outputs),
    'first_run_result_hashes_verified':5,'original_experiment_bytes_preserved':True}
(HERE/'archive-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
for name in ['rank-results.json','execution.json']: shutil.copyfile(ORIGINAL/name,HERE/name)
print(json.dumps({k:v for k,v in manifest.items() if k!='entries'},indent=2))
