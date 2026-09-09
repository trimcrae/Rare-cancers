import json, math
from math import comb
d=json.load(open('research/manuscripts/fusion-partner/emc-fusion-partner-pooling.json'))
b=d['analyses']['B_outcome_by_partner']
print("pooled object present:", 'disease_specific_death' in b)
o=b['source_verified_recorded_outcomes']['disease_specific_death']
a,n1=o['taf15_arm']['events'],o['taf15_arm']['denom']
c,n2=o['comparator_arm']['events'],o['comparator_arm']['denom']
print("counts",a,n1,c,n2)
print("pct taf15", round(100*a/n1,1), "stored", o['taf15_arm']['percent'])
print("pct comp", round(100*c/n2,1), "stored", o['comparator_arm']['percent'])
# Fisher two-sided
def hyp(k,n1,n2,K):
    return comb(n1,k)*comb(n2,K-k)/comb(n1+n2,K)
K=a+c; N1,N2=n1,n2
p0=hyp(a,N1,N2,K)
tot=0.0
for k in range(max(0,K-N2), min(N1,K)+1):
    p=hyp(k,N1,N2,K)
    if p<=p0*(1+1e-9): tot+=p
print("fisher two-sided recomputed", round(tot,4), "stored", o['fisher_exact_two_sided_p'])
# Wilson
def wilson(x,n,z=1.959963985):
    ph=x/n; den=1+z*z/n
    ctr=(ph+z*z/(2*n))/den
    half=z*math.sqrt(ph*(1-ph)/n+z*z/(4*n*n))/den
    return round(100*(ctr-half),1), round(100*(ctr+half),1)
print("wilson taf15", wilson(a,n1), "stored", o['taf15_arm']['ci95_lo_percent'], o['taf15_arm']['ci95_hi_percent'])
print("wilson comp", wilson(c,n2), "stored", o['comparator_arm']['ci95_lo_percent'], o['comparator_arm']['ci95_hi_percent'])
print("diff pp", round(100*c/n2-100*a/n1,1), "stored", o['comparator_minus_taf15_percentage_points'])
# withdrawn pooled, for reference only (not reinstated)
print("pooled_cohorts", b['pooled_cohorts'], "cohorts_pooled", b['cohorts_pooled'])
