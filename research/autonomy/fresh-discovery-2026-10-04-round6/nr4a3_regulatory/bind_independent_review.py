from pathlib import Path
import hashlib,json,datetime
R=Path(__file__).resolve().parent
src=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-genomics/research/autonomy/fresh-discovery-2026-10-04-round6/clinical_identity/independent-regulatory-review.json')
b=src.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='1d43745f9889b074b933383ffa61363140cafa1eb8dd9cbdf92200f9405bdc8c'
x=json.loads(b)
for n,want in x['reviewed_final_sha256'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==want,n
(R/'independent-review-binding.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_path':str(src),'source_sha256':h,'review':x,'verified_all_reviewed_hashes_match':True},indent=2)+'\n',encoding='utf-8')