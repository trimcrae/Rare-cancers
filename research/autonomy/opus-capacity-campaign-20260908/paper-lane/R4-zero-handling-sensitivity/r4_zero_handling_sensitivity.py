#!/usr/bin/env python3
"""
R4 - bounded zero-handling sensitivity measurement on the retained fourth-cohort tables.

WHAT THIS IS
    A sensitivity measurement of ONE analysis choice - how a cell that reads 0 in the
    retained tables is handled - on the per-gene statistic and on the panel rank set.
    It re-uses the arithmetic that W20/W20d/W20e used and changes nothing else.

WHAT THIS IS NOT
    Not a hypothesis test. No p-value is computed anywhere in this file, deliberately.
    Not a new endpoint. The declared TAF15/FUS sentinels are used ONCE, as an
    implementation gate on delta and on the panel percentile, and their scientific
    endpoint (the exact-enumeration p-values of W20) is NOT re-run.
    Not a change of default. Convention B is the committed pipeline and stays the default.
    No gene-biology claim, no patient classification, no network access.

THE UNIT
    The retained tables carry TWO units:
      * emc-fourth-cohort-probe-counts.tsv - one row per RETAINED 50-nt SEQUENCE
        (213,007 rows) x 12 runs, plus an `assigned_gene` label.
      * emc-fourth-cohort-gene-counts.tsv  - one row per GENE (862 rows), whose cell is
        documented as "RAW READS PER GENE, summed over the probes assigned to that gene"
        and "understated by at most `support_floor_reads` PER PROBE".
    The persistence floor is therefore a PER-PROBE quantity. The conventions below are
    consequently defined at the PROBE unit and aggregated to the gene, never applied to a
    gene as if a gene were a probe.

FOUR STATES, NEVER COLLAPSED
    1 OBSERVED_ZERO   - a cell known to be a measured zero.
                        NOT AVAILABLE in these tables: the source module states
                        "a zero in the probe table ... may have been observed below the
                        persistence cap. It is not a measurement of zero reads."
                        No cell is ever placed in this state by this script.
    2 ABSENT_FILTERED - cell reads 0: the sequence was not among the counts persisted for
                        that run. Indeterminate in [0, support_floor_reads].
    3 MISSING_MAPPING - the sequence carries no gene assignment (`assigned_gene` =
                        'unassigned'), so no gene-level cell exists for it at all.
    4 UNCOMPUTABLE    - a comparison that cannot be formed (an arm left with 0 valid runs,
                        or a convention the retained tables do not support).

THE THREE CONVENTIONS (probe unit -> gene)
    Let P(g) be the probes with assigned_gene == g, c(p,r) the retained cell, and
    F(r) = per_run[r].support_floor_reads.
    Let Z(g,r) = { p in P(g) : c(p,r) == 0 }  (state 2 cells).

    B  LITERAL  (COMMITTED DEFAULT, UNCHANGED)
         value(g,r) = sum_p c(p,r).  A state-2 cell contributes 0.
    C  FLOOR_IMPUTED (probe-aware upper bound)
         value(g,r) = sum_{p not in Z} c(p,r) + |Z(g,r)| * F(r).
         JUSTIFICATION FOR |Z| * F RATHER THAN A SINGLE F: the module's own lossy-counting
         guarantee is stated per probe, so a gene whose k probes are all unpersisted is
         understated by up to k*F, not by F. Applying one probe's floor to a multi-probe
         gene would understate the imputation by a factor of k. This is an UPPER BOUND on
         the understatement, not a point estimate.
    A  DROP_CENSORED
         if |Z(g,r)| >= 1 the gene's value in run r is a lower bound, not a measurement,
         so run r is INELIGIBLE for gene g. Runs are dropped per gene, not globally.

    Under A both the ESTIMAND (which runs enter each arm mean) and the RANK SET (which
    genes have a computable statistic) can change. Both are reported.

STATISTIC (W20's, unchanged)
    CPM(g,r)   = value(g,r) / L(r) * 1e6
    L(r)       = the committed panel library size = column sum of the committed
                 gene-counts table for run r. HELD FIXED across all three conventions so
                 that the convention moves the numerator only; the library-size inflation
                 convention C would cause if propagated is reported separately as a
                 diagnostic, and is not applied.
    delta(g)   = mean_{FISH-negative}( log2(CPM+1) ) - mean_{FISH-positive}( log2(CPM+1) )
                 Sign convention is W20's: delta < 0 means higher in the FISH-POSITIVE arm.
    percentile = rank of delta(g) among the ELIGIBLE RANK SET for that convention.
    TIE RULE   : i = #{ h in rank set : delta(h) < delta(g) } - strictly-less count, so
                 tied genes all receive the same (minimum) rank. This is W20's rule and is
                 confirmed by the sentinel gate below.
    UNITS      : percentile is reported in PERCENT (0-100), at both offsets, i/n and
                 (i+0.5)/n. The offset between them is exactly 0.5/n * 100 PERCENTAGE
                 POINTS and is DERIVED FROM THE ACTUAL n of each rank set. It is an
                 arithmetic property of the reporting convention. It is NOT a significance
                 threshold and NOT a biological-importance threshold, and W20e's `0.10`
                 gate tolerance is NOT treated here as a unit-free universal constant.

GATE (run once)
    TAF15 delta = -0.8347, panel pct i/n = 9.05 ; FUS delta = +0.0789, pct i/n = 62.06
    (W20, reproduced by W20d and W20e). Reproducing these fixes the pipeline, the sign
    convention, the FISH split, the rank set and the tie rule in one shot.
    The sentinels' p-values are NOT recomputed: that would be re-running their endpoint.

FENCES HONOURED
    Reads only retained artifacts. Writes only under R4-zero-handling-sensitivity/.
    No network, no commit, no push, no test suite, no preflight, no source fetch.
"""
import json, math, os, sys, collections

REPO = "/home/user/Rare-cancers"
MOD = os.path.join(REPO, "research/modalities")
OUT = os.path.join(REPO, "research/autonomy/opus-capacity-campaign-20260908/paper-lane/R4-zero-handling-sensitivity")

PROBES_TSV = os.path.join(MOD, "emc-fourth-cohort-probe-counts.tsv")
GENES_TSV  = os.path.join(MOD, "emc-fourth-cohort-gene-counts.tsv")
QUANT_JSON = os.path.join(MOD, "emc-fourth-cohort-quant.json")

SENTINELS = {"TAF15": (-0.8347, 9.05), "FUS": (0.0789, 62.06)}
DP = 4  # delta rounding for the gate

def log(*a): print(*a)

# ---------------------------------------------------------------- inputs
quant = json.load(open(QUANT_JSON))
per_run = quant["per_run"]

gh = open(GENES_TSV).readline().rstrip("\n").split("\t")[1:]
RUNS = [c.split(":")[0] for c in gh]
ph = open(PROBES_TSV).readline().rstrip("\n").split("\t")[2:]
PRUNS = [c.split(":")[0] for c in ph]
assert RUNS == PRUNS, "probe and gene tables disagree on run order"

FISH  = [per_run[r]["ewsr1_break_apart_fish"] for r in RUNS]
FLOOR = [float(per_run[r]["support_floor_reads"]) for r in RUNS]
NEG = [i for i, f in enumerate(FISH) if f == "EWSR1-"]
POS = [i for i, f in enumerate(FISH) if f == "EWSR1+"]

# committed gene table (= convention B by construction) and its library sizes
gene_committed = {}
for line in open(GENES_TSV).read().splitlines()[1:]:
    p = line.split("\t"); gene_committed[p[0]] = [int(x) for x in p[1:]]
L = [sum(gene_committed[g][r] for g in gene_committed) for r in range(len(RUNS))]

# probes, grouped by assigned gene; unassigned rows counted only for the state-3 census
probes = collections.defaultdict(list)
n_rows = n_unassigned = 0
unassigned_with_zero = 0
runs_persisted_hist = collections.Counter()
reads_by_k = collections.Counter()
with open(PROBES_TSV) as f:
    f.readline()
    for line in f:
        p = line.rstrip("\n").split("\t")
        v = [int(x) for x in p[2:]]
        n_rows += 1
        k = sum(1 for x in v if x > 0)
        runs_persisted_hist[k] += 1; reads_by_k[k] += sum(v)
        if p[1] == "unassigned":
            n_unassigned += 1
            if k < len(RUNS): unassigned_with_zero += 1
            continue
        probes[p[1]].append(v)

GENES = sorted(probes)
# integrity: the gene table must be exactly the probe sums
bad = [g for g in GENES if [sum(ps[r] for ps in probes[g]) for r in range(len(RUNS))] != gene_committed[g]]
assert not bad and len(GENES) == len(gene_committed), f"gene table is not the probe sum: {bad[:3]}"

# ---------------------------------------------------------------- conventions
def gene_cells(g):
    """per run: (observed_sum, n_state2_probes, n_probes)"""
    ps = probes[g]
    out = []
    for r in range(len(RUNS)):
        obs = sum(p[r] for p in ps if p[r] > 0)
        z = sum(1 for p in ps if p[r] == 0)
        out.append((obs, z, len(ps)))
    return out

def value_and_eligibility(g, conv):
    """-> (values[run] or None, eligible[run] bool)"""
    cells = gene_cells(g); vals = []; elig = []
    for r, (obs, z, npb) in enumerate(cells):
        if conv == "B":
            vals.append(float(obs)); elig.append(True)              # state 2 contributes 0
        elif conv == "C":
            vals.append(float(obs) + z * FLOOR[r]); elig.append(True)  # |Z| * F, not F
        elif conv == "A":
            if z >= 1: vals.append(None); elig.append(False)        # censored -> ineligible
            else:      vals.append(float(obs)); elig.append(True)
    return vals, elig

def delta(g, conv):
    """-> (delta or None, n_neg, n_pos, reason)"""
    vals, elig = value_and_eligibility(g, conv)
    neg = [i for i in NEG if elig[i]]; pos = [i for i in POS if elig[i]]
    if not neg or not pos:
        return None, len(neg), len(pos), ("UNCOMPUTABLE: FISH-negative arm has 0 valid runs" if not neg
                                          else "UNCOMPUTABLE: FISH-positive arm has 0 valid runs")
    l2 = lambda i: math.log2(vals[i] / L[i] * 1e6 + 1.0)
    d = sum(l2(i) for i in neg) / len(neg) - sum(l2(i) for i in pos) / len(pos)
    return d, len(neg), len(pos), ""

def percentiles(dmap):
    """dmap: gene -> delta over the eligible rank set. -> gene -> (n, pct_i_n, pct_mid)"""
    ds = sorted(dmap.values()); n = len(ds)
    import bisect
    out = {}
    for g, d in dmap.items():
        i = bisect.bisect_left(ds, d)          # strictly-less count; ties share min rank
        out[g] = (n, 100.0 * i / n, 100.0 * (i + 0.5) / n)
    return out

# ---------------------------------------------------------------- compute
log("=" * 78)
log("R4 zero-handling sensitivity - retained fourth-cohort tables")
log("=" * 78)
log(f"runs={len(RUNS)}  FISH-negative={[RUNS[i] for i in NEG]}  n_pos={len(POS)}")
log(f"panel genes={len(GENES)}  assigned probes={sum(len(v) for v in probes.values())}")
log(f"probes-per-gene distribution={dict(sorted(collections.Counter(len(v) for v in probes.values()).items()))}")
log(f"library sizes (committed panel column sums)={L}")
log(f"support_floor_reads per run={FLOOR}")
log("")

log("--- STATE CENSUS over the retained tables ---")
gr_state2 = sum(1 for g in GENES for (o, z, n) in gene_cells(g) if z >= 1)
gr_all2   = sum(1 for g in GENES for (o, z, n) in gene_cells(g) if z == n)
log(f"1 OBSERVED_ZERO   : 0 cells - NOT REPRESENTABLE in these tables (source caveat "
    f"'a zero in the probe table ... is not a measurement of zero reads').")
log(f"2 ABSENT_FILTERED : gene x run cells with >=1 unpersisted contributing probe = {gr_state2} "
    f"of {len(GENES)*len(RUNS)}; cells with ALL probes unpersisted = {gr_all2}")
log(f"3 MISSING_MAPPING : {n_unassigned} of {n_rows} retained sequences carry no gene assignment; "
    f"{unassigned_with_zero} of those have >=1 unpersisted run")
log(f"    -> no gene-level cell exists for them, under ANY convention.")
log("")
log("runs_persisted  n_sequences      reads   pct_reads   n_assigned_to_a_gene")
n_assigned_by_k = collections.Counter()
for g in GENES:
    for p in probes[g]:
        n_assigned_by_k[sum(1 for x in p if x > 0)] += 1
totreads = sum(reads_by_k.values())
for k in range(len(RUNS) + 1):
    log(f"{k:>13}  {runs_persisted_hist[k]:>11}  {reads_by_k[k]:>10}  {100*reads_by_k[k]/totreads:9.4f}  {n_assigned_by_k[k]:>21}")
log("")

results = {}   # conv -> gene -> dict
for conv in ("A", "B", "C"):
    dmap = {}; rows = {}
    for g in GENES:
        d, nn, np_, why = delta(g, conv)
        rows[g] = dict(delta=d, n_neg=nn, n_pos=np_, reason=why)
        if d is not None: dmap[g] = d
    pcts = percentiles(dmap) if dmap else {}
    for g in GENES:
        if rows[g]["delta"] is None:
            rows[g].update(rank_n=len(dmap), pct_in=None, pct_mid=None)
        else:
            n, a, b = pcts[g]; rows[g].update(rank_n=n, pct_in=a, pct_mid=b)
    results[conv] = rows
    n_unc = sum(1 for g in GENES if rows[g]["delta"] is None)
    off = 100 * 0.5 / len(dmap) if dmap else float("nan")
    log(f"convention {conv}: eligible rank-set size n={len(dmap)}  UNCOMPUTABLE genes={n_unc}  "
        f"i/n vs (i+0.5)/n offset = 0.5/{len(dmap)} = {off:.6f} percentage points")
log("")

# ---------------------------------------------------------------- gate (once)
log("--- GATE: reproduce the declared TAF15/FUS sentinel arithmetic (ONCE) ---")
log("    p-values are deliberately NOT recomputed - that would re-run their endpoint.")
gate_ok = True
for g, (ed, ep) in SENTINELS.items():
    r = results["B"][g]
    d_ok = round(r["delta"], DP) == round(ed, DP)
    p_ok = round(r["pct_in"], 2) == round(ep, 2)
    gate_ok &= d_ok and p_ok
    log(f"  {g:6s} probes={len(probes[g])}  delta={r['delta']:+.4f} (expected {ed:+.4f} "
        f"{'OK' if d_ok else 'FAIL'})  pct i/n={r['pct_in']:.2f} (expected {ep:.2f} "
        f"{'OK' if p_ok else 'FAIL'})  pct (i+0.5)/n={r['pct_mid']:.2f}  rank-set n={r['rank_n']}")
log(f"  GATE: {'PASS' if gate_ok else 'FAIL'}")
log("")

# ---------------------------------------------------------------- sensitivity
log("--- SIGN / RANK SENSITIVITY, invalid cells RETAINED ---")
flips = shifted = both_ok = 0
maxdd = maxpp = 0.0
for g in GENES:
    a, b, c = (results[k][g]["delta"] for k in "ABC")
    if b is not None and c is not None:
        both_ok += 1
        maxdd = max(maxdd, abs(c - b))
        if (b > 0) != (c > 0): flips += 1
        pa, pc = results["B"][g]["pct_in"], results["C"][g]["pct_in"]
        maxpp = max(maxpp, abs(pc - pa))
        if abs(pc - pa) > 0: shifted += 1
log(f"genes with a computable delta under all three conventions: "
    f"{sum(1 for g in GENES if all(results[k][g]['delta'] is not None for k in 'ABC'))} of {len(GENES)}")
log(f"sign flips B->C : {flips}")
log(f"genes whose panel percentile moves at all B->C : {shifted}")
log(f"max |delta_C - delta_B| over the panel  = {maxdd:.10f} log2 units")
log(f"max |pct_C - pct_B| over the panel      = {maxpp:.10f} percentage points")
d_ab = max((abs(results['A'][g]['delta'] - results['B'][g]['delta'])
            for g in GENES if results['A'][g]['delta'] is not None), default=float('nan'))
log(f"max |delta_A - delta_B| over the panel  = {d_ab:.10f} log2 units")
log(f"arms under A: every gene retains n_neg={results['A'][GENES[0]]['n_neg']}, "
    f"n_pos={results['A'][GENES[0]]['n_pos']}"
    if len({(results['A'][g]['n_neg'], results['A'][g]['n_pos']) for g in GENES}) == 1
    else "arms under A vary by gene - see the per-gene table")
log("")

# convention-C library-size inflation, diagnostic only (NOT applied)
infl = []
for r in range(len(RUNS)):
    add = sum(z * FLOOR[r] for g in GENES for (o, z, n) in [gene_cells(g)[r]])
    infl.append(add / L[r])
log(f"DIAGNOSTIC (not applied): convention-C library-size inflation per run = "
    f"{[round(x,8) for x in infl]}")
log("")

# ---------------------------------------------------------------- write tables
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "R4-per-gene-convention-table.tsv"), "w") as f:
    f.write("\t".join(["gene", "n_contributing_probes", "n_runs_with_state2_cell",
                       "convention", "convention_name", "n_valid_neg", "n_valid_pos",
                       "statistic", "delta_log2cpm", "eligible_rank_set_n", "tie_rule",
                       "pct_units", "pct_i_over_n", "pct_i_plus_half_over_n",
                       "offset_pp_from_actual_n", "cell_state", "uncomputable_reason"]) + "\n")
    names = {"A": "DROP_CENSORED", "B": "LITERAL(committed default)", "C": "FLOOR_IMPUTED(|Z|*F)"}
    for g in GENES:
        cells = gene_cells(g)
        n2 = sum(1 for (o, z, n) in cells if z >= 1)
        for conv in ("A", "B", "C"):
            r = results[conv][g]
            off = 100 * 0.5 / r["rank_n"] if r["rank_n"] else float("nan")
            state = "ABSENT_FILTERED_present" if n2 else "no_state2_cell"
            f.write("\t".join([
                g, str(len(probes[g])), str(n2), conv, names[conv],
                str(r["n_neg"]), str(r["n_pos"]),
                "mean log2(CPM+1) FISHneg - FISHpos",
                "UNCOMPUTABLE" if r["delta"] is None else f"{r['delta']:+.6f}",
                str(r["rank_n"]), "strictly-less count; ties share the minimum rank",
                "percent (0-100)",
                "UNCOMPUTABLE" if r["pct_in"] is None else f"{r['pct_in']:.4f}",
                "UNCOMPUTABLE" if r["pct_mid"] is None else f"{r['pct_mid']:.4f}",
                f"{off:.6f}", state, r["reason"] or "-"]) + "\n")

with open(os.path.join(OUT, "R4-sign-rank-sensitivity.tsv"), "w") as f:
    f.write("\t".join(["gene", "n_probes", "n_runs_with_state2_cell",
                       "delta_A", "delta_B", "delta_C",
                       "sign_A", "sign_B", "sign_C", "sign_unstable",
                       "delta_shift_C_minus_B_log2", "delta_shift_A_minus_B_log2",
                       "pct_B_i_over_n", "pct_C_i_over_n", "pct_A_i_over_n",
                       "pct_shift_C_minus_B_pp", "pct_shift_A_minus_B_pp",
                       "rank_n_A", "rank_n_B", "rank_n_C", "invalid_cells"]) + "\n")
    sgn = lambda d: "-" if d is None else ("+" if d > 0 else ("-" if d < 0 else "0"))
    fm = lambda d: "UNCOMPUTABLE" if d is None else f"{d:+.6f}"
    fp = lambda d: "UNCOMPUTABLE" if d is None else f"{d:.4f}"
    for g in GENES:
        A, B, C = (results[k][g] for k in "ABC")
        cells = gene_cells(g); n2 = sum(1 for (o, z, n) in cells if z >= 1)
        unstable = "no"
        if None in (A["delta"], B["delta"], C["delta"]): unstable = "UNCOMPUTABLE"
        elif len({sgn(A["delta"]), sgn(B["delta"]), sgn(C["delta"])}) > 1: unstable = "YES"
        inv = [k for k in "ABC" if results[k][g]["delta"] is None]
        f.write("\t".join([
            g, str(len(probes[g])), str(n2), fm(A["delta"]), fm(B["delta"]), fm(C["delta"]),
            sgn(A["delta"]), sgn(B["delta"]), sgn(C["delta"]), unstable,
            "UNCOMPUTABLE" if None in (C["delta"], B["delta"]) else f"{C['delta']-B['delta']:+.6f}",
            "UNCOMPUTABLE" if None in (A["delta"], B["delta"]) else f"{A['delta']-B['delta']:+.6f}",
            fp(B["pct_in"]), fp(C["pct_in"]), fp(A["pct_in"]),
            "UNCOMPUTABLE" if None in (C["pct_in"], B["pct_in"]) else f"{C['pct_in']-B['pct_in']:+.4f}",
            "UNCOMPUTABLE" if None in (A["pct_in"], B["pct_in"]) else f"{A['pct_in']-B['pct_in']:+.4f}",
            str(A["rank_n"]), str(B["rank_n"]), str(C["rank_n"]),
            ",".join(inv) if inv else "-"]) + "\n")

summary = dict(
    runs=RUNS, fish_negative=[RUNS[i] for i in NEG], n_pos=len(POS),
    panel_genes=len(GENES), assigned_probes=sum(len(v) for v in probes.values()),
    retained_sequences=n_rows, unassigned_sequences=n_unassigned,
    unassigned_with_at_least_one_state2_run=unassigned_with_zero,
    gene_run_cells=len(GENES) * len(RUNS),
    gene_run_cells_with_state2=gr_state2, gene_run_cells_all_probes_state2=gr_all2,
    rank_set_n={k: results[k][GENES[0]]["rank_n"] for k in "ABC"},
    offset_pp={k: 100 * 0.5 / results[k][GENES[0]]["rank_n"] for k in "ABC"},
    sign_flips_B_to_C=flips, genes_with_any_percentile_move_B_to_C=shifted,
    max_abs_delta_shift_C_minus_B=maxdd, max_abs_pct_shift_C_minus_B_pp=maxpp,
    max_abs_delta_shift_A_minus_B=d_ab,
    convention_C_library_inflation_fraction_per_run=infl,
    gate=dict(passed=bool(gate_ok),
              sentinels={g: dict(delta=results["B"][g]["delta"], pct_i_over_n=results["B"][g]["pct_in"],
                                 pct_mid=results["B"][g]["pct_mid"],
                                 expected_delta=SENTINELS[g][0], expected_pct=SENTINELS[g][1],
                                 n_probes=len(probes[g])) for g in SENTINELS},
              pvalues_recomputed=False),
)
json.dump(summary, open(os.path.join(OUT, "R4-summary.json"), "w"), indent=1)
log(f"wrote R4-per-gene-convention-table.tsv, R4-sign-rank-sensitivity.tsv, R4-summary.json into {OUT}")
sys.exit(0 if gate_ok else 4)
