from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parent
src=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-microenvironment/research/autonomy/fresh-discovery-2026-10-04-round7/fusion_transcripts/functional-models-independent-review.json')
b=src.read_bytes();assert hashlib.sha256(b).hexdigest()=='b387c31f1c6e756914460c9b707117a352c65052858f4543272db562d8929c4d'
x=json.loads(b)
for f in x['files']:
 name=f['path'].replace('\\','/').split('/')[-1]
 assert hashlib.sha256((R/name).read_bytes()).hexdigest()==f['sha256'],name
(R/'independent-review-binding.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_path':str(src),'source_sha256':hashlib.sha256(b).hexdigest(),'all_reviewed_hashes_match':True,'review':x},indent=2)+'\n',encoding='utf-8')
print('Independent review hashes: PASS')