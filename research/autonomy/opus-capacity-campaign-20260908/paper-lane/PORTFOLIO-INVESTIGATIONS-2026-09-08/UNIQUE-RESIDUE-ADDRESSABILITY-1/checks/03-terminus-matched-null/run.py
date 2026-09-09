"""Control: is the indel exposure signal just a construct-terminus effect?
Null pool restricted to residues at a comparable distance from the nearest construct terminus."""
import json, random, statistics, sys
L="/home/user/Rare-cancers/research/autonomy/opus-capacity-campaign-20260908/paper-lane/PORTFOLIO-INVESTIGATIONS-2026-09-08/UNIQUE-RESIDUE-ADDRESSABILITY-1"
d=json.load(open(L+"/unique-residue-addressability.json"))
pr=d["per_residue"]; off=d["_method"]["local_to_uniprot_offset"]
uni=sorted(int(u) for u in pr); n=len(uni)
loc={u:u-off for u in uni}
def termdist(u): return min(loc[u]-1, n-loc[u])
pocket=set(d["_method"]["pocket"]["uniprot"])
lab=d["label_tests"]["indel_union"]["uniprot"]
lab=[u for u in lab if u not in pocket]
print("labelled terminus distances:", {u:termdist(u) for u in lab})
for band,(lo,hi) in {"tight_+-5":(-5,5),"wide_+-10":(-10,10)}.items():
    rng=random.Random(20260908)
    obs_r=statistics.fmean(pr[str(u)]["rsa_mean"] for u in lab)
    obs_d=statistics.fmean(pr[str(u)]["d_pocket_mean"] for u in lab)
    nullr=[];nulld=[];skipped=0
    for _ in range(20000):
        pick=[]
        ok=True
        for u in lab:
            t=termdist(u)
            cand=[v for v in uni if v not in pocket and v not in pick and lo<=termdist(v)-t<=hi]
            if not cand: ok=False;break
            pick.append(rng.choice(cand))
        if not ok: skipped+=1;continue
        nullr.append(statistics.fmean(pr[str(v)]["rsa_mean"] for v in pick))
        nulld.append(statistics.fmean(pr[str(v)]["d_pocket_mean"] for v in pick))
    pr_r=(sum(1 for v in nullr if v>=obs_r)+1)/(len(nullr)+1)
    pr_d=(sum(1 for v in nulld if v<=obs_d)+1)/(len(nulld)+1)
    print(f"{band}: n_null={len(nullr)} RSA obs={obs_r:.4f} null_median={statistics.median(nullr):.4f} p_higher={pr_r:.4f} | "
          f"d_pocket obs={obs_d:.2f} null_median={statistics.median(nulld):.2f} p_closer={pr_d:.4f}")
