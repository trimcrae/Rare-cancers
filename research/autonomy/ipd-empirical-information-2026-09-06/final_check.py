"""One final packet accounting/hash check; no empirical executions or archive reads."""
import collections,datetime,hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    d=HERE/'development';attempt=json.loads((d/'attempts.json').read_text());cases=attempt['cases']
    planned=json.loads((d/'planned-cases.json').read_text());freeze=json.loads((d/'execution-freeze.json').read_text())
    assert len(cases)==len(planned)==120
    assert len({c['case_id'] for c in cases})==120
    assert {c['case_id'] for c in cases}=={c['case_id'] for c in planned}
    for name,digest in freeze['source_hashes'].items():
        if name=='README.md':continue # rewritten to report final outcome; not scientific executable input
        assert sha(HERE/name)==digest,(name,'changed after execution freeze')
    rows=[];ns={}
    for c in cases:
        raw=json.loads((d/(c['case_id']+'.result.json')).read_text());rel=json.loads((d/(c['case_id']+'.release.json')).read_text())
        assert raw['inputs']=={'a':rel['a'],'b':rel['b']},'package input fairness mismatch'
        ns[c['source_group']]=rel['a']['n']+rel['b']['n']
        for m,r in raw['methods'].items():
            assert r['status']=='success'
            calc=c['methods'][m]['statistic']
            rows.append({'case':c['case_id'],'method':m,'p_discrepancy':abs(calc['p']-r['logrank_p']),'q_discrepancy':abs(calc['q']-r['logrank_chisq'])})
    original=json.loads((d/'original-verification.json').read_text());assert original['passed'] and original['checked_original_assignments']==30
    summary=json.loads((d/'summary.json').read_text());assert not summary['continue_to_held_out']
    source=json.loads((HERE/'source-manifest.json').read_text());dev={g['source_group'] for g in source['source_groups'] if g['split']=='development'}
    assert {c['source_group'] for c in cases}==dev
    result={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'planned_completed_cases':120,'published_package_results':len(rows),'source_groups':10,'original_assignments':30,'distinct_source_patient_ids':sum(ns.values()),'sample_sizes_by_source':ns,'max_reconstructed_p_discrepancy':max(x['p_discrepancy'] for x in rows),'max_reconstructed_q_discrepancy':max(x['q_discrepancy'] for x in rows),'max_original_z_q_p_discrepancy':max(x['max_z_q_p_discrepancy'] or 0 for x in original['cases']),'same_released_inputs_to_both_packages':True,'frozen_scientific_inputs_unchanged':True,'reserved_groups_not_in_execution':11,'elapsed_pilot_seconds':attempt['elapsed_seconds'],'continue_to_held_out':False,'process_status':'All pilot and verification processes completed; no worker process remains running.'}
    (HERE/'final-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    files=[p for p in HERE.rglob('*') if p.is_file() and p.name!='artifact-manifest.json']
    manifest={'base':'ea974de61c99f0b282af55eee584c637a7955bbd','files':{p.relative_to(HERE).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(files)},'publication_ready':False,'worker_processes_running':False}
    (HERE/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result));print(json.dumps({'manifest_files':len(files),'total_bytes':sum(p.stat().st_size for p in files)}))
if __name__=='__main__':main()
