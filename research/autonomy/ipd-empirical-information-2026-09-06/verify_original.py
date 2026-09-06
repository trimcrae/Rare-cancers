"""Separate R verification of realized original-IPD statistics after the frozen run."""
import csv,hashlib,io,json,pathlib,subprocess,zipfile
HERE=pathlib.Path(__file__).resolve().parent
BASE=pathlib.Path('C:/Users/mcrae/.codex/worktrees/ipd-baselines-20260906/EMC-Research')
def main():
    manifest=json.loads((HERE/'source-manifest.json').read_text())
    planned=json.loads((HERE/'development/planned-cases.json').read_text())
    attempts=json.loads((HERE/'development/attempts.json').read_text())['cases']
    assert {c['case_id'] for c in attempts}=={c['case_id'] for c in planned},'wait for full accounting'
    cases={}
    for c in attempts:
        if c.get('original') is not None:cases.setdefault((c['curve']['curve_id'],c['seed']),c)
    inputs=[]
    with zipfile.ZipFile(manifest['archive']) as z:
        for (curve,seed),c in cases.items():
            rows=list(csv.DictReader(io.TextIOWrapper(z.open('RealIPD/IPD/'+curve+'.csv'))))
            rows.sort(key=lambda r:hashlib.sha256((str(seed)+'|'+r['id']).encode()).hexdigest())
            cut=len(rows)//2
            inputs.append({'case':curve+'-'+str(seed),'records':[{'time':float(r['time']),'event':int(float(r['status'])),'arm':'a' if i<cut else 'b'} for i,r in enumerate(rows)]})
    inp=HERE/'development/original-check-input.json';out=HERE/'development/original-check-r.json'
    inp.write_text(json.dumps(inputs)+'\n',encoding='utf-8')
    cp=subprocess.run([str(BASE/'.cache/R-4.6.1/bin/Rscript.exe'),'--vanilla',str(HERE/'verify_original.R'),str(BASE/'.cache/R-library'),str(inp),str(out)],capture_output=True,text=True)
    (HERE/'development/original-check.log').write_text(cp.stdout+'\n'+cp.stderr,encoding='utf-8');assert cp.returncode==0
    checks=[]
    for r in json.loads(out.read_text()):
        curve,seed=r['case'].split('-');expected=cases[(curve,int(seed))]['original']
        assert r['evaluable']==expected['evaluable']
        if r['evaluable']:
            delta=max(abs(r[k]-expected[k]) for k in ('z','q','p'))
            assert delta<1e-7*max(1,expected['q'])
        else:delta=None
        checks.append({'case':r['case'],'evaluable':r['evaluable'],'max_z_q_p_discrepancy':delta})
    receipt={'passed':True,'checked_original_assignments':len(checks),'cases':checks,'source_scope':'Only development curves represented in completed run; no reserved sources opened','input_sha256':hashlib.sha256(inp.read_bytes()).hexdigest()}
    (HERE/'development/original-verification.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'checked_original_assignments':len(checks)}))
if __name__=='__main__':main()
