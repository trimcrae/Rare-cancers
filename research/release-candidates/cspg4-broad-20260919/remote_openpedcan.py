from pathlib import Path
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
import hashlib,json,shutil,subprocess,urllib.request
W=Path(__file__).resolve().parent
now=datetime.now(ZoneInfo('America/New_York'));assert not 6<=now.hour<10
free=shutil.disk_usage(W).free;assert free>=13*1024**3
plan=json.loads((W/'OPENPEDCAN-DESIGN.json').read_text())
out=W/'openpedcan-result';out.mkdir()
matrix=W/'openpedcan-tpm.rds'; h=hashlib.md5();s=hashlib.sha256();total=0
with urllib.request.urlopen(plan['matrix_url'],timeout=120) as response,matrix.open('wb') as f:
    while chunk:=response.read(1024**2):
        total+=len(chunk);assert total<=300_000_000
        h.update(chunk);s.update(chunk);f.write(chunk)
assert total==plan['expected_compressed_bytes'] and h.hexdigest()==plan['source_md5']
ids=W/'openpedcan-selected-ids.txt';ids.write_text('\n'.join(plan['selected_ids'])+'\n')
subprocess.run(['Rscript',str(W/'extract_openpedcan.R'),str(matrix),str(ids),str(out/'CSPG4.tsv'),str(out/'schema.txt')],check=True)
assert shutil.disk_usage(W).free>=10*1024**3
receipt={'utc':datetime.now(timezone.utc).isoformat(),'local_time':now.isoformat(),'runner_free_before_bytes':free,'runner_free_after_bytes':shutil.disk_usage(W).free,'source_url':plan['matrix_url'],'source_bytes':total,'source_md5':h.hexdigest(),'source_sha256':s.hexdigest(),'design_sha256':hashlib.sha256((W/'OPENPEDCAN-DESIGN.json').read_bytes()).hexdigest(),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()},'only_CSPG4_exported':True}
(out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
