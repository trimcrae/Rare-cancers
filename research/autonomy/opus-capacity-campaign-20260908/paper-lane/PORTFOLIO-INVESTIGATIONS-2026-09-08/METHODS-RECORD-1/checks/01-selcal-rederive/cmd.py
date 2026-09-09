import json,itertools
from statistics import mean
d=json.load(open("research/modalities/selcal-verdict.json"))
A=[d["model_means_A"][k] for k in sorted(d["model_means_A"],key=int)]
B=[d["model_means_B"][k] for k in sorted(d["model_means_B"],key=int)]
print("A",A); print("B",B)
mA,mB=mean(A),mean(B)
print("mean_A %.6f rec %s"%(mA,d["mean_A"]))
print("mean_B %.6f rec %s"%(mB,d["mean_B"]))
obs=mA-mB
print("stat %.6f rec %s"%(obs,d["statistic"]))
pool=A+B; na=len(A)
arr=list(itertools.combinations(range(len(pool)),na))
print("n_arrangements",len(arr),"rec",d["n_arrangements"])
stats=[]
for idx in arr:
    s=set(idx); a=[pool[i] for i in idx]; b=[pool[i] for i in range(len(pool)) if i not in s]
    stats.append(mean(a)-mean(b))
tol=1e-9
p_less=sum(1 for s in stats if s<=obs+tol)/len(stats)
p_greater=sum(1 for s in stats if s>=obs-tol)/len(stats)
print("p(less)  %.6f rec %s"%(p_less,d["p"]))
print("p(mirror)%.6f rec %s"%(p_greater,d["p_mirror"]))
print("min_attainable 1/462 = %.7f rec %s"%(1/len(arr),d["min_attainable_p"]))
