import pathlib,json,hashlib,datetime,shutil,subprocess
D=pathlib.Path(__file__).resolve().parent
R=pathlib.Path(r'C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-functional/research/autonomy/fresh-discovery-2026-10-04-round5/independent_challenge')
# Restore exact independently reviewed coverage bytes; add verified bibliography in a separate receipt.
p=D/'COVERAGE.json';j=json.loads(p.read_text())
for x in j['sources']:
 if x['source']=='Gu2022':x.pop('doi',None);x.pop('source_sha256',None)
 if x['source']=='Zhang2022':x.pop('preprint_sha256',None)
p.write_text(json.dumps(j,indent=2),encoding='utf-8')
review=json.loads((R/'FINAL-REVIEW.json').read_text())
for x in review['reviewed_owner_final_files']:
 q=pathlib.Path(x['path']);assert hashlib.sha256(q.read_bytes()).hexdigest()==x['sha256'],str(q)
o={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'review_receipt':str(R/'FINAL-REVIEW.json'),'review_receipt_sha256':hashlib.sha256((R/'FINAL-REVIEW.json').read_bytes()).hexdigest(),'reviewer_manifest_sha256':'c7a44387cec0714f56431870796b9af7d141d40b0adb333b1dd29f5e16b7c7f5','all_three_reviewed_owner_hashes_match':True,'decision':review['decision'],'sources_reused':[{'source':'Gu2022','doi':'10.1007/s00259-022-05700-4','path':str(R/'gu2022.xml'),'sha256':'5529103dd806780784cb5c9b2b23714f330316d68b031a2f5d788642da66016f'},{'source':'Zhang2022','doi':'10.1016/j.ejrad.2022.110507','preprint':'rs-1463611/v1','path':str(R/'zhang2022-preprint.pdf'),'sha256':'47ccc6ffb43f3ee600049ffb605abae67a740d366d51022653948d2ec866b830'}]}
for x in o['sources_reused']:assert hashlib.sha256(pathlib.Path(x['path']).read_bytes()).hexdigest()==x['sha256']
(D/'INDEPENDENT-REVIEW-BINDING.json').write_text(json.dumps(o,indent=2),encoding='utf-8')
files=[p for p in D.iterdir() if p.is_file() and p.name!='MANIFEST.json'];rows=[{'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)]
assert sum(x['bytes'] for x in rows)<10*1024**2
free=shutil.disk_usage(D).free;assert free>=10*1024**3
manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files_excluding_manifest':rows,'bytes_excluding_manifest':sum(x['bytes'] for x in rows),'free_bytes':free,'git_head':'373a430957178c1ce76cab89b3ae21b337cb3fc0','git_status':'untracked ownedpacket; no commits/pushes','owned_running_processes':[],'decision':'SHELVE standalone; no EMCfinding; sourcegaps notexhausted'}
(D/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for x in rows:assert hashlib.sha256((D/x['path']).read_bytes()).hexdigest()==x['sha256']
print(json.dumps({'files_including_manifest':len(rows)+1,'bytes_including_manifest':sum(x['bytes'] for x in rows)+(D/'MANIFEST.json').stat().st_size,'manifest_sha256':hashlib.sha256((D/'MANIFEST.json').read_bytes()).hexdigest(),'free_bytes':free,'independent_review_bound':True},indent=2))
