import json,shutil
from pathlib import Path
root=Path('restored-artifacts')
assert root.is_dir()
n=0
for src in root.rglob('*'):
 if not src.is_file():continue
 parts=src.relative_to(root).parts
 for prefix in ('campaign-output','deep-output','research'):
  if prefix in parts:
   i=parts.index(prefix);dest=Path(*parts[i:]);dest.parent.mkdir(parents=True,exist_ok=True)
   if src.resolve()!=dest.resolve():shutil.copy2(src,dest)
   n+=1;break
assert n
print('EMC_RESTORED_FILES '+str(n))
