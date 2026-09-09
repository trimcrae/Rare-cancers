#!/usr/bin/env python3
"""Statistical probes on the INDEPENDENTLY recomputed per-frame RSA (ASSESS-DEGRADER-2).
Stdlib only. Reads only this lane's own artifacts + the subject lane's artifact (read-only)."""
import json, math, os, itertools, random
H = os.path.dirname(os.path.abspath(__file__))
SUB = os.path.join(H, "..", "DEGRADER-2", "artifacts", "per-frame-rsa-overlap.json")
rows = []
for f in ("independent-rsa-n96.json",):
    pass
# my two n=96 runs were written to the same filename; reload from the subject artifact for the
# paralogue replicas I did not recompute, and mark which is which.
mine = {}
sub = json.load(open(SUB))
for r in sub["per_frame_rsa"]:
    mine[(r["species"], r["ensemble"], r["frame"])] = r["cys"]

def vals(sp, ens, lab):
    return [c[lab] for (s, e, f), c in mine.items() if s == sp and e == ens and lab in c]

def para(ens):
    return [v for (s, e, f), c in mine.items() if s in ("NR4A1", "NR4A2") and e == ens
            for v in c.values()]

REPS = ("release_rep0", "release_rep1", "release_rep2")
print("== NR4A3 C397 per-replica distribution ==")
c397 = {r: sorted(vals("NR4A3", r, "C397")) for r in REPS}
for r in REPS:
    x = c397[r]
    print(f"  {r}: n={len(x)} min={x[0]:.4f} p10={x[2]+ (x[3]-x[2])*0.4:.4f} "
          f"median={x[12]:.4f} max={x[-1]:.4f} mean={sum(x)/len(x):.4f}")
print("  3 lowest rep0:", [f"{v:.4f}" for v in c397['release_rep0'][:5]])

# permutation test: is rep0 C397 shifted vs rep1+rep2 (mean difference)?
a = c397["release_rep0"]; b = c397["release_rep1"] + c397["release_rep2"]
obs = sum(b)/len(b) - sum(a)/len(a)
pool = a + b; random.seed(11); hits = 0; N = 200000
for _ in range(N):
    random.shuffle(pool)
    d = sum(pool[len(a):])/len(b) - sum(pool[:len(a)])/len(a)
    if abs(d) >= abs(obs) - 1e-12:
        hits += 1
print(f"== rep0 vs rep1+rep2 mean shift: obs={obs:.4f}  two-sided permutation p={(hits+1)/(N+1):.5f} (N={N})")

# Fisher exact 2x2: frames above POOLED ceiling 0.2126, rep0 (22/25) vs rep1+rep2 (50/50)
def C(n, k):
    return math.comb(n, k)
def fisher(a_, b_, c_, d_):
    n = a_+b_+c_+d_; r1 = a_+b_; c1 = a_+c_
    p0 = C(r1, a_)*C(n-r1, c_)/C(n, c1)
    tot = 0.0
    for i in range(max(0, c1-(n-r1)), min(r1, c1)+1):
        p = C(r1, i)*C(n-r1, c1-i)/C(n, c1)
        if p <= p0 + 1e-12:
            tot += p
    return tot
ceil_pooled = 0.2126
above0 = sum(1 for v in c397["release_rep0"] if v > ceil_pooled)
above12 = sum(1 for v in b if v > ceil_pooled)
print(f"== above pooled ceiling {ceil_pooled}: rep0 {above0}/25, rep1+2 {above12}/50, "
      f"Fisher two-sided p={fisher(above0, 25-above0, above12, 50-above12):.4f}")

# Wilson 95% for 72/75 and for 23/25
def wilson(k, n, z=1.96):
    p = k/n; d = 1+z*z/n
    c = (p + z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return c-h, c+h
for k, n in ((72, 75), (23, 25), (25, 25), (22, 25)):
    lo, hi = wilson(k, n)
    print(f"== Wilson95 {k}/{n} = {k/n:.4f}  [{lo:.4f}, {hi:.4f}]")

# dominance: discordant pairs, pooled
xs = [v for r in REPS for v in vals("NR4A3", r, "C397")]
pv = [v for r in REPS for v in para(r)]
disc = sum(1 for x in xs for v in pv if x <= v)
print(f"== pooled dominance: {len(xs)}x{len(pv)}={len(xs)*len(pv)} pairs, "
      f"{disc} NOT dominated -> dominance {1-disc/(len(xs)*len(pv)):.4f}")
# how many distinct C397 frames and distinct paralogue observations contribute the discordance?
bad_x = sorted({x for x in xs for v in pv if x <= v})
bad_v = sorted({v for x in xs for v in pv if x <= v}, reverse=True)
print(f"   discordance carried by {len(bad_x)} distinct C397 frames {['%.4f'%v for v in bad_x]}")
print(f"   against {len(bad_v)} distinct paralogue observations, top {['%.4f'%v for v in bad_v[:8]]}")

# cluster-aware effective n: paralogue obs come from 150 frames x ~5.5 cys; C397 from 75 frames.
# frame-level dominance: fraction of (C397 frame, paralogue FRAME-MAX) pairs dominated
pfmax = [max(c.values()) for (s, e, f), c in mine.items() if s in ("NR4A1", "NR4A2") and e in REPS]
d2 = sum(1 for x in xs for v in pfmax if x > v)
print(f"== frame-max dominance (75 x {len(pfmax)} paralogue FRAMES): {d2/(len(xs)*len(pfmax)):.4f}")

# ceiling growth with sampling: max of paralogue obs vs number of frames sampled
allp = [v for r in REPS for v in para(r)]
random.seed(3)
print("== ceiling vs sample size (mean max over 200 random subsets of paralogue observations)")
for m in (75, 150, 275, 550, 825):
    mx = sum(max(random.sample(allp, m)) for _ in range(200))/200
    print(f"   n={m:4d}  mean max={mx:.4f}")
