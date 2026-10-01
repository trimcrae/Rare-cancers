import json,hashlib,zipfile
from pathlib import Path
root=Path('campaign-output')
src=root/'methylation-emc-MTAP-author-BAF'
cache=src/'R-dependency-cache.zip'
receipt=json.loads((src/'R-dependency-cache-receipt.json').read_text())
assert cache.stat().st_size==receipt['bytes'] and hashlib.sha256(cache.read_bytes()).hexdigest()==receipt['sha256']
dest=root/'methylation-emc-MTAP'/'R-library'
dest.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(cache) as z:
 for info in z.infolist():
  target=dest/info.filename
  assert target.resolve().is_relative_to(dest.resolve())
  if info.is_dir():target.mkdir(parents=True,exist_ok=True)
  else:
   target.parent.mkdir(parents=True,exist_ok=True)
   target.write_bytes(z.read(info))
   mode=(info.external_attr>>16)&0o777
   if mode:target.chmod(mode)
(root/'methylation-emc-MTAP'/'dependency-cache-reuse-receipt.json').write_text(json.dumps({'source_cache_sha256':receipt['sha256'],'source_run':36923792066,'source_artifact':11194577827,'scope':'Exact installed dependencies reused; each pinned conumee source is reinstalled before its fit'},indent=2)+'\n')
print('EMC_R_CACHE_RESTORED',len(list(dest.iterdir())))
