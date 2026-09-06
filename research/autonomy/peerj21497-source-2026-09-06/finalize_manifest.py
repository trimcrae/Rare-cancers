"""Package bookkeeping only; run once when settled, then verify_packet.py."""
import pathlib,hashlib,json,datetime,subprocess
ROOT=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
deps=['research/autonomy/atlas-sample-organ-2026-09-06/protocol.md']
m={'base_revision':'5adfaead4dfcd5c2a78079fbe50c7fdf53bf8b4a','scope':'Exact PeerJ 21497 Data S1 source inspection; no inference or contrasts','owner':'/root/peerj_source','resource':'paper:PUB-SURFACE-TARGETS:peerj21497-source','model':'GPT-6 family per runtime identity; exact execution model and reasoning telemetry unavailable to this script','first_new_retrieval_completed_utc':'2026-09-06T05:17:50.958329+00:00','finalized_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'usage':'unknown','permissions':'approval never; danger-full-access per developer runtime instructions','files':[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(ROOT.iterdir()) if p.is_file() and p.name not in ('manifest.json','verification-receipt.json')],'dependencies':[{'path':p,'sha256':sha(ROOT.parents[2]/p)} for p in deps]}
(ROOT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
