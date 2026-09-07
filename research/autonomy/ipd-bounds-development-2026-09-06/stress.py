"""Prespecified development stress extension; see development-amendment.md."""
import hashlib
import json
import random
import time
from pathlib import Path
from bounds import release_arm,solve
from develop import generate_arm,counts
from verify import subject_score,summarize
from fractions import Fraction as F

ROOT=Path(__file__).resolve().parent


def main():
    rng=random.Random(2026090601);fixtures=[];truth=[];results=[];start=time.perf_counter()
    for n,k,digits in [(80,12,2),(200,12,2),(80,6,1),(200,20,2)]:
        name=f'n{n}-k{k}-digits{digits}'
        a=generate_arm(rng,n,k,.08,.04);b=generate_arm(rng,n,k,.12,.04)
        risk_times=[1,1+k//2]
        rel={'schema':'discrete-km-release-v1','synthetic':True,'grid':list(range(1,k+1)),
             'probability_digits':digits,'a':release_arm(a,k,digits,risk_times),'b':release_arm(b,k,digits,risk_times)}
        fixtures.append({'case_id':name,'release':rel})
        truth.append({'case_id':name,'a':a,'b':b,'n':n,'k':k,'probability_digits':digits})
    (ROOT/'stress-releases.json').write_text(json.dumps({'synthetic':True,'partition':'development','cases':fixtures},indent=2)+'\n')
    (ROOT/'stress-truth.json').write_text(json.dumps({'synthetic':True,'partition':'development','cases':truth},indent=2)+'\n')
    for fixture,original in zip(fixtures,truth):
        result=solve(fixture['release'],seconds=8,max_pairs=25000,max_nodes=300000,max_paths=10000)
        # Verification occurs only after solve and cannot enter its release-only interface.
        a=list(map(tuple,original['a']));b=list(map(tuple,original['b']));q=subject_score(a,b)
        for arm,rows in [('a',a),('b',b)]:
            assert summarize(rows,original['k'],original['probability_digits'],[1,1+original['k']//2])==fixture['release'][arm]
        if result['complete']:
            lo,hi=map(F,result['q_outer']);assert lo<=q<=hi
        else:
            assert result['decision']=='unresolved' and result['q_outer']==['0','infinity'] and result['p_outer']==[0,1]
        results.append({'case_id':fixture['case_id'],'result':result,'verification':{'true_q':str(q),'release_matches':True,'finite_bound_containment':True if result['complete'] else None}})
        print(json.dumps({'case_id':fixture['case_id'],'complete':result['complete'],'decision':result['decision'],
                          'reason':result['reason'],'paths':[result['arm_enumerations'][arm]['accepted_paths'] for arm in ['a','b']],
                          'pairs':result['enumerated_pairs'],'elapsed_seconds':result['elapsed_seconds']}),flush=True)
    out={'synthetic':True,'partition':'development','seed':2026090601,'cases':results,
         'amendment_sha256':hashlib.sha256((ROOT/'development-amendment.md').read_bytes()).hexdigest(),
         'elapsed_seconds':time.perf_counter()-start}
    (ROOT/'stress-results.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':main()
