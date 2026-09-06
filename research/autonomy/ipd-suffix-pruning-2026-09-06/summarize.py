"""Summarize saved outputs; no inference or new case selection."""
from fractions import Fraction as F
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
new=json.loads((ROOT/'results.json').read_text())
old=json.loads((ROOT.parent/'ipd-frontier-bounds-2026-09-06'/'results.json').read_text())
prior={x['case_id']:x['result'] for x in old['cases']}
rows=[]
for item in new['cases']:
    r=item['result'];p=prior[item['case_id']]
    width=lambda q:None if q[1]=='infinity' else float(F(q[1])-F(q[0]))
    rows.append({'case_id':item['case_id'],'partition':'stress' if item['source'].startswith('stress') else 'development',
                 'decision':r['decision'],'prior_decision':p['decision'],'q_lower_float':float(F(r['q_outer'][0])),
                 'q_upper_float':None if r['q_outer'][1]=='infinity' else float(F(r['q_outer'][1])),
                 'width_float':width(r['q_outer']),'prior_width_float':width(p['q_outer']),
                 'joint_transitions':r['transitions'],'prior_joint_transitions':p['transitions'],
                 'work_units':r['work_units'],'pruned_marginal_transitions':sum(a['pruned_transitions'] for a in r['arms'].values()),
                 'cached_true':sum(a['proved_true'] for a in r['arms'].values()),
                 'cached_false':sum(a['proved_false'] for a in r['arms'].values()),
                 'unknown_returns':sum(a['unknown_returns'] for a in r['arms'].values()),
                 'cache_hits':sum(a['hits_true']+a['hits_false'] for a in r['arms'].values()),
                 'expanded_states':r['expanded_states'],'peak_joint_states':r['peak_live_states'],
                 'seconds':r['elapsed_seconds'],'prior_seconds':p['elapsed_seconds'],
                 'peak_traced_bytes':r['tracemalloc_peak_bytes'],'prior_peak_traced_bytes':p['tracemalloc_peak_bytes']})
summary={'cases':rows,'total_run_seconds':new['elapsed_seconds'],'prior_total_run_seconds':old['elapsed_seconds']}
for partition in ['development','stress']:
    group=[x for x in rows if x['partition']==partition]
    summary[partition]={'certificates':sum(x['decision'].startswith('stable_') for x in group),
                        'prior_certificates':sum(x['prior_decision'].startswith('stable_') for x in group),
                        'joint_transitions':sum(x['joint_transitions'] for x in group),
                        'prior_joint_transitions':sum(x['prior_joint_transitions'] for x in group),
                        'seconds_sum':sum(x['seconds'] for x in group),
                        'work_units':sum(x['work_units'] for x in group),
                        'cached_true':sum(x['cached_true'] for x in group),
                        'cached_false':sum(x['cached_false'] for x in group),
                        'pruned_marginal_transitions':sum(x['pruned_marginal_transitions'] for x in group)}
(ROOT/'comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
