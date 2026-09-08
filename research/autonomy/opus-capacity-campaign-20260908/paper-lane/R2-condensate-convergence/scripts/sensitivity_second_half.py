import json, sys, copy, statistics as st
sys.path.insert(0,'research/modalities')
import emc_condensate_calvados as M
A=json.load(open('research/modalities/emc-condensate-calvados.json'))
runs=A['runs']

# --- drift structure on the committed panel -------------------------------
sd=A['pooled_replicate_sd_nu']
exc=[r for r in runs if abs(r['nu_half_vs_full_delta'])>sd]
print("pooled_sd=%.6f  n_exceeding=%d/%d"%(sd,len(exc),len(runs)))
from collections import Counter
print("exceeding by construct:", dict(Counter(r['construct'] for r in exc)))
deltas=[r['nu_second_half']-r['nu'] for r in runs]
print("signed drift (second_half - full): mean=%+.5f  sd=%.5f  n_pos=%d n_neg=%d"%(
    st.mean(deltas), st.pstdev(deltas), sum(d>0 for d in deltas), sum(d<0 for d in deltas)))
# per-construct mean signed drift
bc={}
for r in runs: bc.setdefault(r['construct'],[]).append(r['nu_second_half']-r['nu'])
print("\nper-construct mean signed drift:")
for k,v in sorted(bc.items(), key=lambda kv:-abs(st.mean(kv[1]))):
    print("  %-10s n=%d mean=%+.5f" % (k,len(v),st.mean(v)))

# --- A: re-score committed panel with the frozen scorer (reproduction) -----
rep=M.score(copy.deepcopy(runs))
print("\n[A] reproduce committed: verdict=%s sd=%.6f thr=%.6f"%(rep['verdict'],rep['pooled_replicate_sd_nu'],rep['separation_threshold_nu']))
print("    matches committed sd:", abs(rep['pooled_replicate_sd_nu']-sd)<1e-12,
      " verdict match:", rep['verdict']==A['verdict'])

# --- B: sensitivity - nu := nu_second_half --------------------------------
alt=copy.deepcopy(runs)
for r in alt:
    r['nu']=r['nu_second_half']
sec=M.score(alt)
print("\n[B] second-half estimator: verdict=%s"%sec.get('verdict'))
print("    reasons:", sec.get('reasons'))
print("    pooled_sd=%.6f thr=%.6f"%(sec['pooled_replicate_sd_nu'] or -1, sec['separation_threshold_nu'] or -1))
for k,v in sec.get('pairs',{}).items():
    if v['family']=='primary':
        print("    %-16s dnu=%+.5f sep=%s p=%.4f holm=%s"%(k,v['delta_nu_mean'],v['separated_D1'],v['permutation']['p'],v.get('holm_reject_at_0.05')))
json.dump({'A_reproduction':rep,'B_second_half':sec},
          open('/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/sens_out.json','w'),indent=1)
