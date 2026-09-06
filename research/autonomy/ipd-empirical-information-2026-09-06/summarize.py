"""Fixed descriptive comparisons; never reads archive/held-out outcomes."""
import collections,json,math,pathlib
HERE=pathlib.Path(__file__).resolve().parent
CRIT=1.959963984540054
METHODS=('IPDfromKM','CIFresolve')
def good(c,m):return c.get('methods',{}).get(m,{}).get('status')=='success'
def margin(c,m):return abs(abs(c['methods'][m]['statistic']['z'])-CRIT)
def confidence(c,m,rule):
    other=METHODS[1] if m==METHODS[0] else METHODS[0]
    if rule=='margin':return (margin(c,m),)
    if rule=='margin_minus_disagreement':return (margin(c,m)-abs(c['methods'][m]['statistic']['z']-c['methods'][other]['statistic']['z']),)
    return (int(c['methods'][m]['statistic']['reject']==c['methods'][other]['statistic']['reject']),margin(c,m))
def selected(cases,m,rule,retention):
    ordered=sorted(cases,key=lambda c:c['case_id'])
    ordered.sort(key=lambda c:confidence(c,m,rule),reverse=True)
    return ordered[:math.floor(len(ordered)*retention)]
def assessment(selected,m):
    errors=[c for c in selected if c['methods'][m]['threshold_error']]
    return {'retained':len(selected),'errors':len(errors),'error_rate':len(errors)/len(selected) if selected else None,
            'error_source_groups':sorted({c['source_group'] for c in errors}),
            'error_cases':[c['case_id'] for c in errors],
            'flip_counts':dict(collections.Counter(c['methods'][m]['flip_direction'] for c in errors)),
            'original_rejects':sum(c['original']['reject'] for c in selected),
            'predicted_rejects':sum(c['methods'][m]['statistic']['reject'] for c in selected),
            'sign_flips':sum(c['methods'][m]['sign_flip'] for c in selected)}
def compare(cases,m):
    out={}
    for retention in (.5,.75,.9,1.):
        out[str(retention)]={rule:assessment(selected(cases,m,rule,retention),m) for rule in ('margin','margin_minus_disagreement','binary_agreement_then_margin')}
    return out
def summarize(cases):
    common=[c for c in cases if all(good(c,m) for m in METHODS)]
    valid=[c for c in cases if c.get('original') is not None and c['original']['evaluable']]
    primary=compare(common,METHODS[0]);p75=primary['0.75'];bm=p75['margin'];aug=p75['margin_minus_disagreement']
    ms=selected(common,METHODS[0],'margin',.75);ds=selected(common,METHODS[0],'margin_minus_disagreement',.75)
    per_source=[];loo=[]
    for group in sorted({c['source_group'] for c in cases}):
        me=sum(c['source_group']==group and c['methods'][METHODS[0]]['threshold_error'] for c in ms)
        de=sum(c['source_group']==group and c['methods'][METHODS[0]]['threshold_error'] for c in ds)
        per_source.append({'source_group':group,'margin_errors':me,'augmented_errors':de,'gain':me-de})
        rest=[c for c in common if c['source_group']!=group]
        comp=compare(rest,METHODS[0])['0.75']
        loo.append({'excluded_source':group,'gain':comp['margin']['errors']-comp['margin_minus_disagreement']['errors']})
    incumbent_errors=[c for c in cases if good(c,METHODS[0]) and c['methods'][METHODS[0]]['threshold_error']]
    checks={'complete_planned_execution':not any(c['status'].startswith('unrun') or c['status']=='verification_discrepancy' for c in cases),
            'at_least_8_incumbent_errors':len(incumbent_errors)>=8,
            'at_least_3_error_sources':len({c['source_group'] for c in incumbent_errors})>=3,
            'dual_success_at_least_80pct':len(common)>=.8*len(cases) if cases else False,
            'primary_gain_at_least_2':bm['errors']-aug['errors']>=2,
            'primary_relative_gain_at_least_20pct':bm['errors']>0 and (bm['errors']-aug['errors'])/bm['errors']>=.2,
            'gain_at_least_2_sources':sum(r['gain']>0 for r in per_source)>=2,
            'no_leave_one_source_out_reversal':all(r['gain']>=0 for r in loo)}
    information=[]
    by_key={(c['curve']['curve_id'],c['seed'],c['precision'],c['density']):c for c in cases}
    for c in cases:
        if c['density']!='sparse':continue
        dense=by_key.get((c['curve']['curve_id'],c['seed'],c['precision'],'dense'))
        if dense is None:continue
        for m in METHODS:
            information.append({'source_group':c['source_group'],'sparse_case':c['case_id'],'dense_case':dense['case_id'],'method':m,
                 'sparse_success':good(c,m),'dense_success':good(dense,m),
                 'sparse_error':c['methods'][m]['threshold_error'] if good(c,m) else None,
                 'dense_error':dense['methods'][m]['threshold_error'] if good(dense,m) else None})
    return {'attempted_cases':len(cases),'source_groups':len({c['source_group'] for c in cases}),
            'execution_status':dict(collections.Counter(c['status'] for c in cases)),
            'valid_original_cases':len(valid),'original_rejects':sum(c['original']['reject'] for c in valid),
            'always_nonsignificant':{'errors':sum(c['original']['reject'] for c in valid),'retained':len(valid)},
            'dual_success_cases':len(common),'dual_success_fraction':len(common)/len(cases) if cases else None,
            'primary_common_success':primary,'secondary_common_success':compare(common,METHODS[1]),
            'individual_method_margins':{m:{str(r):assessment(selected([c for c in cases if good(c,m)],m,'margin',r),m) for r in (.5,.75,.9,1.)} for m in METHODS},
            'source_primary_gains':per_source,'leave_one_source_out':loo,'density_pairs':information,
            'continuation_checks':checks,'continue_to_held_out':all(checks.values()),
            'scope':'Descriptive development only; source-dependent repetitions, randomized pseudoarms, no population-null error label or clinical claim.'}
if __name__=='__main__':
    data=json.loads((HERE/'development/attempts.json').read_text());out=summarize(data['cases'])
    (HERE/'development/summary.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ('attempted_cases','source_groups','dual_success_cases','continuation_checks','continue_to_held_out')}))
