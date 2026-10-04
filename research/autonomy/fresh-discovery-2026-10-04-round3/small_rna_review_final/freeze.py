import pathlib,hashlib,json,datetime
R=pathlib.Path(__file__).resolve().parent
f=[{'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(R.iterdir()) if p.is_file() and p.name!='MANIFEST.json']
(R/'MANIFEST.json').write_text(json.dumps({'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':f,'bytes_excluding_manifest':sum(x['bytes'] for x in f),'owned_processes_running':False},indent=2))
print(json.dumps({'files':len(f)+1,'total_bytes':sum(p.stat().st_size for p in R.iterdir() if p.is_file()),'manifest_sha256':hashlib.sha256((R/'MANIFEST.json').read_bytes()).hexdigest()},indent=2))
