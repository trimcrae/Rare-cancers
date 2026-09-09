"""Reconcile the ONE failing identity in check 01: are 0.700 / 0.580 real values or
2-dp restatements? Reads the committed artifacts directly. CPU, stdlib, no network."""
import json, os
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
pub = json.load(open(os.path.join(B, "PUB-ANDGATE", "fusion-andgate-trans-competition.json")))
a3 = json.load(open(os.path.join(B, "ANDGATE-3", "andgate3-symmetric-trans-competition.json")))

rows = {r["C_E_uM"]: r for r in pub["trans_competition_sweep"]}
print("PUB-ANDGATE committed sweep, the two disputed rows:")
for c in (3000.0, 10000.0):
    print("  C_E=%8.0f uM  window=%r  (dp printed: %d)"
          % (c, rows[c]["window"], len(str(rows[c]["window"]).split(".")[-1])))

def w_asym(C_E, Kd1=1e-5, Kd2=1e-4, EM=1e-3, L=1e-6):
    zf = 1 + L/Kd1 + L/Kd2 + (L/Kd1)*(EM/Kd2)
    zw = 1 + (L/Kd1)*(1 + C_E/Kd2)
    return ((zf-1)/zf) / ((zw-1)/zw)

print("\nFull-precision asymmetric recomputation:")
for c in (3e-3, 1e-2):
    v = w_asym(c)
    print("  C_E=%6.4f M  exact=%.6f  round2=%.2f  round3=%.3f" % (c, v, round(v,2), round(v,3)))

print("\nANDGATE-3's OWN artifact, cost_curve_published_vs_symmetric_n1 tail:")
cc = a3["cost_curve_published_vs_symmetric_n1"]
for r in cc[-3:]:
    print("  C_E=%8.1f uM  window_as_published=%r  window_symmetric=%r"
          % (r["C_E_uM"], r["window_as_published"], r["window_symmetric"]))
print("  max C_E in ANDGATE-3 artifact: %.1f uM  (10 mM = 10000 uM present? %s)"
      % (max(r["C_E_uM"] for r in cc), any(r["C_E_uM"] == 10000.0 for r in cc)))

print("""
RECONCILIATION
  0.700 -> PUB-ANDGATE committed 0.7 at 2 dp; exact 0.695765. ANDGATE-3's own artifact
           prints 0.696. The "0.700" appears only in ANDGATE-3's PROSE, which re-quoted a
           2-dp value with a spurious third digit. Arithmetic agrees; the precision does not.
  0.580 -> PUB-ANDGATE committed 0.58 at 2 dp; exact 0.578152. ANDGATE-3's sweep STOPS at
           3 mM, so neither 0.580 nor its symmetric partner 1.008 is backed by ANDGATE-3's
           own artifact. ANDGATE-4 computes 1.008258 independently, so 1.008 is arithmetically
           CORRECT but was, in ANDGATE-3, an unevidenced prose figure.
  1.064 -> present in ANDGATE-3's artifact AND independently reproduced. Sound.
""")
