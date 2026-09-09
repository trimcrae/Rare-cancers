#!/usr/bin/env python3
"""BIOMARKER-DEP-2 — validate the unapplied producer amendment `producer-dispersion-retention.diff`.

Three questions, all answerable offline:

  Q1 BACKWARD COMPATIBILITY. Does the amended `stats()` / `subtype_mean()` emit every field the
     committed version emits, with the same name, definition and rounding? If not, the amendment
     would silently move published numbers and must not be applied.
  Q2 CORRECTNESS OF THE NEW FIELDS. Do the added dispersion / order-statistic / count fields equal
     an INDEPENDENT pure-Python computation on the same input?
  Q3 PAYOFF. By how much does retaining a five-number summary narrow the distribution-free bound on
     P(X < t) at a cut other than the published -0.5 — the quantity DEP-THRESHOLD showed is
     undetermined from what the producer currently keeps?

⛔ No network, no GPU, no paid compute, no EMC observation. pandas is NOT installed in this sandbox
(see checks/02-pandas-probe), so the producer cannot be executed end to end. Instead the REAL source
text of the two nested functions is extracted from the committed file and from the patched copy and
`exec`-ed under a minimal duck-typed Series/Frame shim implementing exactly the pandas methods those
functions call, with pandas' own semantics (ddof=1 sd, linear-interpolation quantiles). This tests
the committed code TEXT, not a paraphrase of it; it does not test pandas itself. That is the stated
limitation, not a hidden one.
"""
import json, os, random, re, subprocess, sys, textwrap

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..", ".."))
ORIG = os.path.join(REPO, "research/modalities/depmap_sarcoma_dependency.py")
PATCHED = sys.argv[1]  # scratch copy with the diff applied
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "amendment-validation.json")
THR = -0.5

# ---------------------------------------------------------------- minimal pandas shim
def _quantile(xs, q):
    """numpy/pandas default 'linear' interpolation quantile."""
    s = sorted(xs); n = len(s)
    if n == 1: return float(s[0])
    pos = (n - 1) * q
    lo = int(pos); hi = min(lo + 1, n - 1); frac = pos - lo
    return float(s[lo] + (s[hi] - s[lo]) * frac)

class Bool:
    def __init__(self, v): self.v = list(v)
    def mean(self): return sum(self.v) / len(self.v)
    def sum(self): return sum(self.v)

class Series:
    def __init__(self, v): self.v = [float(x) for x in v]
    def dropna(self): return Series([x for x in self.v if x == x])
    def __len__(self): return len(self.v)
    def __lt__(self, t): return Bool([1 if x < t else 0 for x in self.v])
    def mean(self): return sum(self.v) / len(self.v)
    def min(self): return min(self.v)
    def max(self): return max(self.v)
    def median(self): return _quantile(self.v, 0.5)
    def quantile(self, q): return _quantile(self.v, q)
    def std(self):  # pandas default ddof=1
        n = len(self.v); m = self.mean()
        return (sum((x - m) ** 2 for x in self.v) / (n - 1)) ** 0.5 if n > 1 else float("nan")
    def reindex(self, idx): return self

class Frame:
    def __init__(self, cols): self.cols = cols
    @property
    def columns(self): return list(self.cols)
    def __getitem__(self, g): return Series(self.cols[g])

# ---------------------------------------------------------------- source extraction
def extract(path, name):
    src = open(path).read()
    m = re.search(r"^(    def %s\(.*?)(?=^    [a-zA-Z_#]|\Z)" % name, src, re.S | re.M)
    assert m, "could not extract %s from %s" % (name, path)
    return textwrap.dedent(m.group(1))

def build(path, patched):
    ns = {"DEPENDENT_THRESHOLD": THR}
    if patched:
        exec(extract(path, "_dispersion"), ns)
    exec(extract(path, "stats"), ns)
    return ns

# ---------------------------------------------------------------- Q1 / Q2
random.seed(20260909)
PUBLISHED = ["gene", "sarcoma_mean", "rest_mean", "selectivity",
             "sarcoma_frac_dependent", "rest_frac_dependent", "n_sarcoma"]
NEW = ["n_rest", "sarcoma_sd", "sarcoma_min", "sarcoma_q25", "sarcoma_median", "sarcoma_q75",
       "sarcoma_max", "n_dependent_sarcoma", "rest_sd", "rest_min", "rest_q25", "rest_median",
       "rest_q75", "rest_max", "n_dependent_rest"]

cases, mismatch_pub, mismatch_new = [], [], []
for trial in range(200):
    n_s, n_r = 91, random.choice([943, 1178, 2014])
    shape = random.choice(["pan_essential", "null", "selective", "bimodal"])
    if shape == "pan_essential":
        s = [random.gauss(-1.8, .35) for _ in range(n_s)]; r = [random.gauss(-1.7, .40) for _ in range(n_r)]
    elif shape == "null":
        s = [random.gauss(0.10, .18) for _ in range(n_s)]; r = [random.gauss(0.09, .20) for _ in range(n_r)]
    elif shape == "selective":
        s = [random.gauss(-0.25, .45) for _ in range(n_s)]; r = [random.gauss(-0.01, .22) for _ in range(n_r)]
    else:
        s = [random.gauss(-1.1, .25) if random.random() < .5 else random.gauss(.05, .2) for _ in range(n_s)]
        r = [random.gauss(-0.9, .30) if random.random() < .2 else random.gauss(.05, .2) for _ in range(n_r)]
    ge = Frame({"G": s + r}); sar = Frame({"G": s}); rest = Frame({"G": r})
    env = {"ge": ge, "sar": sar, "rest": rest}
    o = build(ORIG, False); o.update(env);   a = build(PATCHED, True); a.update(env)
    ro = eval("stats('G')", o); ra = eval("stats('G')", a)
    for k in PUBLISHED:
        if ro[k] != ra[k]: mismatch_pub.append({"trial": trial, "field": k, "committed": ro[k], "amended": ra[k]})
    if list(ra)[:7] != PUBLISHED: mismatch_pub.append({"trial": trial, "field": "_key_order", "committed": PUBLISHED, "amended": list(ra)[:7]})
    # independent recomputation of every new field
    ind = {"n_rest": len(r),
           "sarcoma_sd": round(Series(s).std(), 3), "rest_sd": round(Series(r).std(), 3),
           "sarcoma_min": round(min(s), 3), "rest_min": round(min(r), 3),
           "sarcoma_max": round(max(s), 3), "rest_max": round(max(r), 3),
           "sarcoma_q25": round(_quantile(s, .25), 3), "rest_q25": round(_quantile(r, .25), 3),
           "sarcoma_median": round(_quantile(s, .5), 3), "rest_median": round(_quantile(r, .5), 3),
           "sarcoma_q75": round(_quantile(s, .75), 3), "rest_q75": round(_quantile(r, .75), 3),
           "n_dependent_sarcoma": sum(1 for x in s if x < THR),
           "n_dependent_rest": sum(1 for x in r if x < THR)}
    for k in NEW:
        if k not in ra: mismatch_new.append({"trial": trial, "field": k, "problem": "absent"})
        elif ra[k] != ind[k]: mismatch_new.append({"trial": trial, "field": k, "amended": ra[k], "independent": ind[k]})
    cases.append(shape)

# ---------------------------------------------------------------- Q3 payoff
def bound_mean_frac(mean, frac, L, U, t):
    """Exact range of P(X<t) over all distributions on [L,U] with the given mean and P(X<-0.5)=frac.
    Two-point-per-region LP: mass frac below -0.5 and 1-frac above, each placed to extremise
    P(X<t) subject to the mean. Returns (lo, hi) or None if infeasible."""
    def feasible(p):  # p = P(X<t); can the mean be attained?
        if t <= THR:
            if p > frac: return None
            lo = p * L + (frac - p) * t + (1 - frac) * THR
            hi = p * t + (frac - p) * THR + (1 - frac) * U
        else:
            if p < frac: return None
            lo = frac * L + (p - frac) * THR + (1 - p) * t
            hi = frac * THR + (p - frac) * t + (1 - p) * U
        return lo - 1e-9 <= mean <= hi + 1e-9
    grid = [i / 2000 for i in range(2001)]
    ok = [p for p in grid if feasible(p)]
    return (min(ok), max(ok)) if ok else None

def bound_five_number(fn, t, n, tol=5e-4):
    """Rigorous range of P(X<t) given the RETAINED five-number summary of n points.

    Two effects make the naive [0.25,0.5]-style bound WRONG, and the harness caught it (see
    checks/05, a real failure preserved): (i) the retained values are rounded to 3 dp, so the true
    quantile lies within +/-5e-4 of what is written; (ii) with n points and linear-interpolation
    quantiles, P(X < q_f) need not equal f exactly -- it can differ by up to 1/n. Both are absorbed
    here. n is itself a retained field under this amendment (n_sarcoma / n_rest), so using it is
    legitimate. The bound is conservative by construction.
    """
    mn, q25, med, q75, mx = fn
    slack = 1.0 / n
    lo, hi = 0.0, 1.0
    if t <= mn - tol: return (0.0, 0.0)
    if t > mx + tol: return (1.0, 1.0)
    for v, f in ((mn, 0.0), (q25, 0.25), (med, 0.50), (q75, 0.75), (mx, 1.0)):
        if t > v + tol: lo = max(lo, f - slack)
        if t < v - tol: hi = min(hi, f + slack)
    return (max(0.0, lo), min(1.0, hi))

payoff = []
for t in (-2.0, -1.0, -0.75, -0.25, 0.0):
    widths_old, widths_new, widths_both, det_old, det_new, det_both = [], [], [], 0, 0, 0
    for trial in range(200):
        random.seed(1000 + trial)
        s = [random.gauss(-0.9, .5) for _ in range(91)]
        mean = round(sum(s) / 91, 3); frac = round(sum(1 for x in s if x < THR) / 91, 3)
        fn = tuple(round(x, 3) for x in (min(s), _quantile(s, .25), _quantile(s, .5), _quantile(s, .75), max(s)))
        bo = bound_mean_frac(mean, frac, -4.0, 1.5, t); bn = bound_five_number(fn, t, 91)
        wo = (bo[1] - bo[0]) if bo else 1.0
        wn = bn[1] - bn[0]
        # The amendment retains the OLD fields as well as the new ones, so the bound a reader
        # actually gets is the INTERSECTION of the two. It is never worse than either alone.
        bb = (max(bo[0], bn[0]), min(bo[1], bn[1])) if bo else bn
        wb = max(0.0, bb[1] - bb[0])
        widths_old.append(wo); widths_new.append(wn); widths_both.append(wb)
        det_old += wo < 1e-6; det_new += wn < 1e-6; det_both += wb < 1e-6
        true = sum(1 for x in s if x < t) / 91
        assert bb[0] - 1e-3 <= true <= bb[1] + 1e-3, ("intersection excludes truth", t, trial, bb, true)
        assert bn[0] - 1e-9 <= true <= bn[1] + 1e-9, ("five-number bound excludes truth", t, trial, bn, true)
        if bo: assert bo[0] - 1e-3 <= true <= bo[1] + 1e-3, ("mean/frac bound excludes truth", t, trial, bo, true)
    payoff.append({"t": t,
                   "median_width_committed_fields": round(sorted(widths_old)[100], 3),
                   "median_width_with_five_number": round(sorted(widths_new)[100], 3),
                   "max_width_with_five_number": round(max(widths_new), 3),
                   "median_width_amendment_intersection": round(sorted(widths_both)[100], 3),
                   "max_width_amendment_intersection": round(max(widths_both), 3),
                   "n_exactly_determined_intersection": det_both,
                   "n_exactly_determined_committed": det_old,
                   "n_exactly_determined_amended": det_new,
                   "n_arms": 200})

res = {
  "_note": "Validation of the UNAPPLIED amendment producer-dispersion-retention.diff. Synthetic "
           "input only. No DepMap line, no EMC observation, no efficacy/safety/selectivity/"
           "therapeutic-window claim.",
  "committed_producer": "research/modalities/depmap_sarcoma_dependency.py",
  "diff": "producer-dispersion-retention.diff",
  "pandas_available": False,
  "shim": "duck-typed Series/Frame; pandas semantics: std ddof=1, quantile linear interpolation",
  "Q1_backward_compatibility": {
      "trials": len(cases), "distribution_shapes": sorted(set(cases)),
      "published_fields_checked": PUBLISHED,
      "mismatches": mismatch_pub,
      "verdict": "IDENTICAL — no published field changes" if not mismatch_pub else "FAIL"},
  "Q2_new_field_correctness": {
      "new_fields": NEW, "mismatches": mismatch_new,
      "verdict": "all new fields equal an independent computation" if not mismatch_new else "FAIL"},
  "Q3_threshold_indeterminacy": {
      "_note": "P(X<t) bound width from what the producer keeps now (mean + one fraction at -0.5 + "
               "assumed support [-4.0,1.5]) vs. from the retained five-number summary. Width 0 = the "
               "value is exactly recoverable. Both bounds were asserted to contain the true value.",
      "rows": payoff},
}
json.dump(res, open(OUT, "w"), indent=2)
print(json.dumps({k: v for k, v in res.items() if k.startswith("Q")}, indent=2))
print("\nwrote", OUT, file=sys.stderr)
sys.exit(1 if (mismatch_pub or mismatch_new) else 0)
