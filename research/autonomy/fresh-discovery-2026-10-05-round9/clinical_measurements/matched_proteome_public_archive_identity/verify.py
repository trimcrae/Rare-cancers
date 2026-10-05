#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,shutil
P=Path(__file__).resolve().parent;checks=[]
def c(name,ok):
 checks.append({'name':name,'pass':bool(ok)});assert ok,name
plan=json.loads((P/'PLAN-FROZEN.json').read_text());access=json.loads((P/'ACCESS.json').read_text());schema=json.loads((P/'RESPONSE-SCHEMA.json').read_text());d=json.loads((P/'DECISION.json').read_text())
c('only exact two planned metadata calls',len(access)==len(plan['routes'])==2)
for i,(a,r,s) in enumerate(zip(access,plan['routes'],schema)):
 c('exact planned url'+str(i),a['url']==r['url']);c('http200'+str(i),a['status']==200);c('json content'+str(i),'json' in a['content_type']);c('ten second timeout'+str(i),a['timeout_seconds']==10)
 raw=Path(a['cache_path']).read_bytes();c('source bytes'+str(i),len(raw)==a['bytes']);c('source hash'+str(i),hashlib.sha256(raw).hexdigest()==a['sha256']);c('empty metadata list'+str(i),json.loads(raw)==[]);c('matching evaluatedschema'+str(i),s['returned']==0 and s['root_type']=='list')
for a in json.loads((P/'REUSED-SOURCE-BINDINGS.json').read_text()):
 raw=Path(a['path']).read_bytes();c('priorhash '+Path(a['path']).name,hashlib.sha256(raw).hexdigest()==a['sha256']);c('priorbytes '+Path(a['path']).name,len(raw)==a['bytes'])
c('rawbelowcap',sum(a['bytes'] for a in access)==6<=2097152);c('free>=10GiB',shutil.disk_usage('/workspace').free>=10737418240);c('no protein quantities',d['new_protein_quantities']==0);c('no sequence bodies',d['new_peptide_or_sequence_bodies']==0);c('no matrices',d['raw_matrices_downloaded']==0);c('unresolvedrelease retained','do not infer global NO' in d['release_status']);c('deadline scientificclose',d['scientific_close_utc']<=plan['deadline_utc'])
report={'status':'PASS','checks':checks,'number_checks':len(checks),'scope':'Offline exactmetadata/sourcehash/emptyresponse/provenance/budget/decision checks only; no biological or protein numerical verification.','network_calls_during_verification':0}
(P/'VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
