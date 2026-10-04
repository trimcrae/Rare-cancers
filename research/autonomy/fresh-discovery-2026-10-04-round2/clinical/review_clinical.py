from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,math
P=Path(__file__).resolve().parent
C=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-microenvironment/research/autonomy/fresh-discovery-2026-10-04-round2/clinical')
a=json.loads((C/'conditional-pilot-results.json').read_text())
s=json.loads((C/'oliveira2000-table2-tables.json').read_text())['tables'][0]
assert len(s)==24
# Independently checked every source phrase against the transcribed endpoints.
for r in a['rows']:assert r['original_source_row']==s[r['id']]
ids=[2,4,7,8,11,12,14,17,18,19,21,22]
assert a['late']['landmark_ids']==ids
surv=(11/12)*(6/7);risk=1-surv
G=1/(12*11)+1/(7*6);z=1.959963984540054
v=math.log(-math.log(surv));se=math.sqrt(G)/abs(math.log(surv))
ci=[1-math.exp(-math.exp(v-z*se)),1-math.exp(-math.exp(v+z*se))]
assert abs(risk-a['late']['risk'])<1e-12
assert max(abs(x-y) for x,y in zip(ci,a['late']['risk_loglog_greenwood_95ci']))<1e-12
out={'date':datetime.now(timezone.utc).isoformat(),'decision':'Shelve standalone conditional-risk paper on current evidence; no meaningful new disease inference beyond established late metastatic risk.','raw_row_crosscheck':'All23 rows retained; three baseline metastatic cases3/6/15 correctly excluded. Twelve alive/metastasis-free at5; two events5.5/9; source dates diagnosis, not necessarily definitive resection. Local recurrences7/21 do not invalidate metastasis-free endpoint.','independent_late_risk':risk,'independent_late_ci':ci,'arithmetic':'(11/12)*(6/7); first event shares rounded year5.5 with censor17, sensitivity22.08% properly retained. No pre-metastatic deaths among20 so net and competing-event estimates coincide within this observed series, not generally.','scope_limits':['No untreated natural-history or surveillance-benefit inference. Histology-era cohort with no systematic NR4A3 confirmation; uncertain detection/surveillance schedule.','Oliveira explicitly says15 cases will be described by McGrory et al Clin Orthop in press: do not pool McGrory2001 as independent.','Drilon2008 clock from wide local excision differs from Oliveira diagnosis. Ogura publisher preview plus aggregate tables retrieved by worker; full methods/time-origin gap remains.','12 at5,7 at9,6 observed event-free at10 and two late events give very broad uncertainty; cannot establish equivalence of early and late risks or demonstrate persistent constant hazard.','A 21.4% conditional summary is new arithmetic on fully published cases; known late metastasis and already printed5/10year survival support same belief. A narrower title does not supply novelty.'], 'coverage_challenge':['Meis-Kindblom1999 n117, McGrory2001, Saleh1992, Kawaguchi2003, Drilon2008, Ogura2012, Bishop2019, Chiusole2020, Paioli2021, Brodsky2023, Japanese registry2025 are relevant for a general prognosis claim; this receipt has not evaluated all and cannot certify coverage.','Source2014 molecular-fusion cohorts could overlap clinical cohorts; verify source institutions/dates before pooled estimates.','Current suggestion: stop additional full extraction for a shelved weak contribution, retain all pending eligible evidence visibly rather than call coverage complete.'], 'hashes':{n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in ['conditional_pilot.py','conditional-pilot-results.json','oliveira2000-table2-tables.json','oliveira2000-full-paragraphs.json']}}
(P/'clinical-independent-challenge.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'risk':risk,'ci':ci,'decision':out['decision']}))

