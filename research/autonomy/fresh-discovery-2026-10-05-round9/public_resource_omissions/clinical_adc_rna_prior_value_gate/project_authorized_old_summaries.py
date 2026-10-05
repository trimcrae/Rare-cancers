"""Project the exact authorized two-row old result; no statistic recomputation."""
import csv,json,hashlib,datetime,math
from pathlib import Path
P=Path(__file__).resolve().parent
proposal=P/'PROPOSED-OLD-SUMMARY-REUSE-FROZEN.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(proposal)=='3a287546408558847d9d9dc22ae3ddde6d267b25c53b4b322fd6278dee4afd07'
auth=json.loads((P/'AMENDMENT-02-AUTHORIZED-EXACT-PRIOR-REUSE.json').read_text())
fields=auth['fields']; assert len(fields)==24
source=Path('/workspace/Rare-cancers')/auth['source']; assert sha(source)==auth['source_sha256']
rows=[]
with source.open() as h:
 reader=csv.DictReader(h,delimiter='\t');assert all(x in reader.fieldnames for x in fields)
 for row in reader:
  if row['gene'] in auth['genes']:rows.append({k:row[k] for k in fields})
assert len(rows)==2 and {r['gene'] for r in rows}==set(auth['genes'])
rows.sort(key=lambda x:auth['genes'].index(x['gene']))
checks=[]
for r in rows:
 f=lambda k:float(r[k])
 for k in fields:
  if k not in ['gene','allocated'] and not k.endswith('_p_method'):assert math.isfinite(f(k))
 clauses=[{'clause':'BH_q<=0.05','passed':f('BH_q')<=.05},{'clause':'median_EMC_TPM>=5','passed':f('median_EMC_TPM')>=5},{'clause':'minimum_EMC_TPM>=1','passed':f('minimum_EMC_TPM')>=1}]
 for c in ['Myxoid liposarcoma','Low-grade fibromyxoid sarcoma','Synovial sarcoma']:
  clauses += [{'clause':c+'_A>=0.85','passed':f(c+'_A')>=.85},{'clause':c+'_matched_A>=0.85','passed':f(c+'_matched_A')>=.85},{'clause':c+'_median_log2_contrast>=1','passed':f(c+'_median_log2_contrast')>=1}]
 assert (r['allocated']=='True')==all(x['passed'] for x in clauses)
 checks.append({'gene':r['gene'],'original_allocation_clauses':clauses,'failed_clauses':[x['clause'] for x in clauses if not x['passed']],'source_flag_matches_original_rule':True})
out={'date':'2026-10-05','projected_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(source),'source_sha256':sha(source),'authorization_sha256':sha(P/'AMENDMENT-02-AUTHORIZED-EXACT-PRIOR-REUSE.json'),'proposal_sha256':sha(proposal),'fields_exact':fields,'rows':rows,'original_rule_decomposition':checks,'scope':'Existing original nine-specimen summaries only; no data/statistic/test/rank/adjustment recomputation. Original thresholds are administrative, not a biological or clinical decision.','exposure':'First current-stage numerical projection; historical campaign values already exposed.','unit_limits':'Nine source specimens not all13, not proved independent donors. All other tissue/array/3SEQ/culture/normal and source-mapping gaps still pending.','multiplicity':'BH_q belongs original whole surface-gene universe; not a two-gene or current seven-family correction.'}
(P/'AUTHORIZED-OLD-SUMMARY-PROJECTION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
