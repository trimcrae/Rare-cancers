import json,sys,statistics as st
sys.path.insert(0,'research/modalities')
import emc_condensate_calvados as M
A=json.load(open('research/modalities/emc-condensate-calvados.json'))
runs=A['runs']; thr=A['separation_threshold_nu']
bc={}; bd={}
for r in runs:
    bc.setdefault(r['construct'],[]).append(r['nu'])
    bd.setdefault(r['construct'],[]).append(r['nu_second_half']-r['nu'])
maxdrift=max(abs(d) for v in bd.values() for d in v)
print("max |per-run drift| = %.5f ; separation threshold = %.5f"%(maxdrift,thr))
print("\nprimary pairs: current |dnu|, worst-case |dnu| if BOTH construct means shift by their")
print("own observed mean drift in the most separating direction, and by +/- max per-run drift:")
for a,b in M.PRIMARY_FAMILY:
    d=st.mean(bc[a])-st.mean(bc[b])
    obs=abs(d)+abs(st.mean(bd[a]))+abs(st.mean(bd[b]))
    adv=abs(d)+2*maxdrift
    print("  %-14s |dnu|=%.5f  obs-drift-worst=%.5f  adversarial(+/-max)=%.5f  thr=%.5f  clears=%s/%s"
          %(a+"_vs_"+b,abs(d),obs,adv,thr,obs>=thr,adv>=thr))
e=st.mean(bc['E264']); e15=st.mean(bc['E264_E15'])
print("\ninstrument control E264_E15 - E264 = %+.5f  (needs >= %.5f) margin=%+.5f"%(e15-e,thr,(e15-e)-thr))
# same under second-half
bc2={}
for r in runs: bc2.setdefault(r['construct'],[]).append(r['nu_second_half'])
import copy
alt=[dict(r,nu=r['nu_second_half']) for r in runs]
s2=M.score(alt); thr2=s2['separation_threshold_nu']
print("second-half: E264_E15 - E264 = %+.5f (needs >= %.5f) margin=%+.5f"
      %(st.mean(bc2['E264_E15'])-st.mean(bc2['E264']),thr2,st.mean(bc2['E264_E15'])-st.mean(bc2['E264'])-thr2))
print("\nnu range over all runs: %.4f .. %.4f  (NU_BROKEN %s, NU_EXPECTED %s)"
      %(min(r['nu'] for r in runs),max(r['nu'] for r in runs),M.NU_BROKEN_RANGE,M.NU_EXPECTED_RANGE))
print("nu_second_half range: %.4f .. %.4f"%(min(r['nu_second_half'] for r in runs),max(r['nu_second_half'] for r in runs)))
