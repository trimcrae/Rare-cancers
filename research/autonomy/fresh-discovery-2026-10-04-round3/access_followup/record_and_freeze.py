"""Record already observed supported-browser results and hash only this owned packet."""
from pathlib import Path
import json,datetime,hashlib,subprocess,shutil
B=Path(__file__).parent
immune=B.parent/'immune'
inputs=[Path('C:/Users/mcrae/.codex/plugins/cache/openai-bundled/computer-use/26.924.22138/skills/computer-use/SKILL.md'),Path('C:/Users/mcrae/.codex/plugins/cache/openai-bundled/computer-use/26.924.22138/docs/guidance.md'),Path('C:/Users/mcrae/.codex/plugins/cache/openai-bundled/computer-use/26.924.22138/docs/confirmations.md'),Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-lead/research/autonomy/fresh-discovery-2026-10-04-round3/ACCESS-FOLLOWUP-CONTRACT.json'),immune/'MANIFEST.json',immune/'kelly2020.html']
obs={'date':'2026-10-04','timezone':'America/New_York','scientific_data_newly_read':False,'operations':[{'local_time_precheck':'2026-10-04T14:40:19.7541273-04:00','method':'cua.createBrowserTab','browser':'iab','url':'https://pmc.ncbi.nlm.nih.gov/articles/instance/6990941/bin/jamaoncol-6-402-s001.pdf','options':{'visible':False},'observed_result':'Browser is not available: iab','source_loaded':False},{'local_time_precheck':'2026-10-04T14:40:35.2114108-04:00','method':'cua.listBrowsers','observed_result':[]}],'galitskiy_status':'Not attempted because supported browser inventory was empty; do not report as a browser website barrier.','original_immune_packet_modified':False,'tabs_created':0,'downloads_created':0,'custom_automation_or_challenge_bypass':False,'sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in inputs]}
(B/'observations.json').write_text(json.dumps(obs,indent=2),encoding='utf8')
old=json.loads((immune/'MANIFEST.json').read_text(encoding='utf8'))
bad=[r['path'] for r in old['files'] if hashlib.sha256((immune/r['path']).read_bytes()).hexdigest()!=r['sha256']]
assert not bad,bad
rows=[]
for p in sorted(B.iterdir()):
 if p.is_file() and p.name!='MANIFEST.json':rows.append({'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':subprocess.check_output(['git','-C',str(B.parents[3]),'rev-parse','HEAD'],text=True).strip(),'files':rows,'payload_bytes_excluding_manifest':sum(x['bytes'] for x in rows),'original_immune_manifest_sha256':hashlib.sha256((immune/'MANIFEST.json').read_bytes()).hexdigest(),'original_immune_file_mismatches':bad,'new_commit':False,'pushed':False,'free_C_bytes':shutil.disk_usage(B).free,'retained_budget_bytes':5*1024**2}
p=B/'MANIFEST.json';p.write_text(json.dumps(r,indent=2),encoding='utf8')
print(json.dumps({'manifest_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'total_bytes':r['payload_bytes_excluding_manifest']+p.stat().st_size,'files':len(rows)+1,'head':r['head'],'free_C_bytes':r['free_C_bytes'],'original_immune_file_mismatches':bad},indent=2))
