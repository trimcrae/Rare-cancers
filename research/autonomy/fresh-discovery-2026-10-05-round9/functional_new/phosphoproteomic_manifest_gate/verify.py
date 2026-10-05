#!/usr/bin/env python3
"""Verify source and metadata schemas without reading phosphoproteomic outcome cells."""
from pathlib import Path
import json, hashlib
p=Path(__file__).resolve().parent
read=lambda f:json.loads(f.read_text())
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
checks=[]
for r in read(p/'PLAN.json')['reuse']:
 f=Path(r['path']);checks.append({'check':'immutable shared input','path':r['path'],'pass':f.is_file() and sha(f)==r['sha256']})
for r in read(p/'PORTABILITY.json')['raw_sources']:
 f=p/r['path'];checks.append({'check':'retained source hash','path':r['path'],'pass':f.is_file() and sha(f)==r['sha256']})
coh=read(p/'raw-cache/public-cohort-names.source')
checks.append({'check':'actual public cohort strings','pass':coh==['LUAD_CPTAC','BRCA_CPTAC','UCEC_CPTAC','CPTAC_PAN_Cancer']})
schema=read(p/'raw-cache/public-column-schema.source')
checks.append({'check':'19clinicalschema objects, not specimen or measurementvalues','pass':isinstance(schema,list) and len(schema)==19 and all(isinstance(x,dict) and 'dataField' in x for x in schema)})
repo=read(p/'raw-cache/TOPAS-repository.json')
checks.append({'check':'exact narrow author repository scope','pass':repo['total_count']==1 and repo['items'][0]['full_name']=='kusterlab/topas-pipeline' and repo['incomplete_results'] is False})
checks.append({'check':'exact title repository scope only','pass':read(p/'raw-cache/exact-title-repository.json')['total_count']==0})
d=read(p/'DECISION.json');checks.append({'check':'no outcome cells or numerical stage','pass':d['measurement_values_parsed']==0 and d['kinase_scores_parsed']==0 and d['new_finding_promoted'] is False})
r=read(p/'PORTABILITY.json');checks.append({'check':'finite authorized source storage and floor','pass':r['new_raw_bytes']<=r['new_stage_authorized_cap_bytes'] and r['free_bytes']>=r['free_floor_bytes']})
print(json.dumps({'scope':'Hash/source/cohort-schema verification only, no outcome values or UI.','checks':checks,'passed':all(x['pass'] for x in checks),'checks_count':len(checks)},indent=2))
raise SystemExit(0 if all(x['pass'] for x in checks) else 1)
