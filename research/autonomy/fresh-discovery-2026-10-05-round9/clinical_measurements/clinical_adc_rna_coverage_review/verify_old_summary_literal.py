"""Exact two-row literal replay only; no expression/statistical computation."""
from pathlib import Path
import csv,json,hashlib
P=Path(__file__).resolve().parent
O=Path('/workspace/emc-r6-diagnostic/research/autonomy/fresh-discovery-2026-10-05-round9/public_resource_omissions/clinical_adc_rna_prior_value_gate')
checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(n,ok):
 checks.append({'check':n,'pass':bool(ok)})
 assert ok,n
proposal=O/'PROPOSED-OLD-SUMMARY-REUSE-FROZEN.json'
check('Exact authorizedproposal',sha(proposal)=='3a287546408558847d9d9dc22ae3ddde6d267b25c53b4b322fd6278dee4afd07')
q=json.loads(proposal.read_text());check('Literal24count includesmethods',len(q['fields'])==24)
am=O/'AMENDMENT-02-AUTHORIZED-EXACT-PRIOR-REUSE.json'
check('Ownerdatedamendment',sha(am)=='eb175efadc0fd2ecca6d03e48027a0c6fcb6b47dce53cc20b78d7f47fb2af081')
projection=O/'AUTHORIZED-OLD-SUMMARY-PROJECTION.json'
check('Frozenexactprojection',sha(projection)=='51a7a210764db8365d264556d2be168fc54303add234975c1ff3ee4df66a3110')
j=json.loads(projection.read_text());check('Projectionfields exactly authorized',j['fields_exact']==q['fields'])
check('Exactly two authorizedgenes',[r['gene'] for r in j['rows']]==q['existing_rows'])
check('Owneramendment linked',j['authorization_sha256']==sha(am))
src=Path(j['source']);check('ImmutableoldTSVsourcehash',sha(src)=='4a1ab07eff5aa9ae3746ec432bad525e77cd478db2156adf6346d49218487dc8')
# Inspect header then first literal symbol only on other lines. Parse only two selected rows.
selected=[]
with src.open() as h:
 header=next(csv.reader([h.readline()],delimiter='\t'));check('Canonical exactfieldorder',header==q['fields'])
 for line in h:
  if line.split('\t',1)[0] not in q['existing_rows']:continue
  row=dict(zip(header,next(csv.reader([line],delimiter='\t'))))
  selected.append({k:row[k] for k in q['fields']})
check('Exactly two canonicaloldrows',len(selected)==2)
for row in j['rows']:
 canonical=next(r for r in selected if r['gene']==row['gene'])
 check(row['gene']+'exactfieldset',list(row)==q['fields'])
 for field in q['fields']:check(row['gene']+' literal '+field,canonical[field]==row[field])
# Original coverage remains byte-exact; do not rerun or rewrite its artifacts.
f=json.loads(P.joinpath('FREEZE.json').read_text())
check('Originalcoveragefreeze',sha(P/'FREEZE.json')=='579281665176bda88771c8f70605a5df4c3977c5fc2767b951abaf9f93f3c238')
for r in f['files']:check('Original '+r['name'],sha(P/r['name'])==r['sha256'] and (P/r['name']).stat().st_size==r['bytes'])
ownerfreeze=O/'PRIOR-REUSE-FREEZE.json';check('Ownerreusefreezeexact',sha(ownerfreeze)=='8a9d41e040e5b15203c58945f591351b4f72e43ab7ed58737ca71e64b5d129ca')
v=json.loads(ownerfreeze.read_text())
for r in v['files']:
 name=r.get('path',r.get('name'));check('Ownerreuse '+name,sha(O/name)==r['sha256'] and (O/name).stat().st_size==r['bytes'])
print(json.dumps({'count':len(checks),'checks':checks,'all_pass':all(x['pass'] for x in checks),'new_expression_or_statistics':0,'selected_rows_only':2,'selected_fields_only':24,'no_network':True},indent=2))
