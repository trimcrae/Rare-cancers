import json
d=json.load(open('../PUB-ANDGATE/fusion-andgate-trans-competition.json'))
uM=1e-6; KD1,KD2,EM,L=10*uM,100*uM,1e-3,1*uM
def wsym(C):
    Zf=1+L/KD1+L/KD2+(L/KD1)*(EM/KD2+C/KD2); Zw=1+(L/KD1)*(1+C/KD2)
    return ((Zf-1)/Zf)/((Zw-1)/Zw)
print("PUB-ANDGATE committed trans_competition_sweep, rows at/above C_E=EM=1mM:")
for r in d['trans_competition_sweep']:
    if r['C_E_M']>=1e-3:
        print("  C_E=%8.1f uM  committed window=%.3f  fusion_frac=%.4f  |  symmetric window=%.3f"
              %(r['C_E_uM'], r['window'], r['fusion_fraction_bound'], wsym(r['C_E_M'])))
print("\nfusion_fraction_bound values over the WHOLE committed sweep:",
      sorted({r['fusion_fraction_bound'] for r in d['trans_competition_sweep']}))
