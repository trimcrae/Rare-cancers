"""Generate only explicitly synthetic DEVELOPMENT fixtures and retain every case."""
import hashlib
import json
import random
import time
from pathlib import Path
from bounds import release_arm, solve, score, threshold_proof

ROOT=Path(__file__).resolve().parent
SEED=20260906


def generate_arm(rng,n,k,hazard,censor_hazard):
    rows=[]
    for _ in range(n):
        for t in range(1,k+1):
            if rng.random()<hazard:
                rows.append([t,1]);break
            if rng.random()<censor_hazard or t==k:
                rows.append([t,0]);break
    return sorted(rows)


def counts(rows,k):
    return tuple((sum(x==t and e==1 for x,e in rows),sum(x==t and e==0 for x,e in rows)) for t in range(1,k+1))


def main():
    start=time.perf_counter();rng=random.Random(SEED);truth=[];releases=[]
    for n in [20,40,80]:
        for hazard_b in [.18,.32,.65]:
            case=f'n{n}-hazard-b-{hazard_b}'
            a=generate_arm(rng,n,6,.18,.08);b=generate_arm(rng,n,6,hazard_b,.08)
            truth.append({'case_id':case,'synthetic':True,'a':a,'b':b,
                          'hazard_a':.18,'hazard_b':hazard_b,'conditional_censor_hazard':.08,
                          'true_q':str(score(counts(a,6),counts(b,6)))})
            for density,risk_times in [('sparse',[1,4]),('dense',[1,2,3,4,5,6])]:
                rel={'schema':'discrete-km-release-v1','synthetic':True,'grid':list(range(1,7)),
                     'probability_digits':2,'a':release_arm(a,6,2,risk_times),'b':release_arm(b,6,2,risk_times)}
                releases.append({'case_id':case+'-'+density,'parent_case_id':case,'risk_density':density,'release':rel})
    (ROOT/'development-truth.json').write_text(json.dumps({'synthetic':True,'partition':'development','seed':SEED,'cases':truth},indent=2)+'\n',encoding='utf-8')
    (ROOT/'development-releases.json').write_text(json.dumps({'synthetic':True,'partition':'development','seed':SEED,'cases':releases},indent=2)+'\n',encoding='utf-8')
    # Release fixture is saved before solve; solver only receives released summaries.
    print(json.dumps({'event':'fixtures_written','cases':len(truth),'releases':len(releases)}),flush=True)
    results=[]
    for item in releases:
        result=solve(item['release'],seconds=8,max_pairs=25000,max_nodes=300000,max_paths=10000)
        results.append({'case_id':item['case_id'],'result':result})
        print(json.dumps({'case_id':item['case_id'],'complete':result['complete'],'decision':result['decision'],
                          'reason':result['reason'],'paths':[result['arm_enumerations'][a]['accepted_paths'] for a in ['a','b']],
                          'pairs':result['enumerated_pairs'],'seconds':result['elapsed_seconds']}),flush=True)
    out={'synthetic':True,'partition':'development','seed':SEED,'threshold_proof':threshold_proof(),
         'protocol_sha256':hashlib.sha256((ROOT/'protocol.md').read_bytes()).hexdigest(),
         'release_sha256':hashlib.sha256((ROOT/'development-releases.json').read_bytes()).hexdigest(),
         'cases':results,'elapsed_seconds':time.perf_counter()-start}
    (ROOT/'development-results.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
