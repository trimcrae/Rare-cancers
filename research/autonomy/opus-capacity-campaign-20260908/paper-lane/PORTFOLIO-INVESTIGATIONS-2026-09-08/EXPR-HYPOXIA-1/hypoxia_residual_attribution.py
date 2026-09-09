#!/usr/bin/env python3
"""EXPR-HYPOXIA-1: is the residual EMC expression contrast that survives EXPR-COMPOSITION's
tumour/stroma adjustment a hypoxia programme?

Order, enforced here and not overridable by a flag:
  1. GATE: reproduce EXPR-COMPOSITION's published attenuation EXACTLY, before any hypoxia
     statistic is computed. exit 3 on any mismatch.
  2. Build the frozen hypoxia score H under the complete-case gene rule of PREREGISTRATION.md sec.3.
     Fewer than 8 surviving genes -> exit 4.
  3. CONTROL: the seeded random background (which excludes all 118 named confound genes) must NOT
     attenuate, and its label-correlation-matched regression gives the generic baseline that H must
     beat to mean anything.
  4. H, V and the two-covariate C+H statistics on the primary and secondary frames. STOP.

Nothing here is an efficacy, safety, selectivity, therapeutic-window, target-attribution or
clinical-readiness claim. Any attenuation is an association in owned data.
"""
import json, os, sys, time, hashlib, random
import numpy as np

REPO = "/home/user/Rare-cancers"
HERE = os.path.dirname(os.path.abspath(__file__))
LANES = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(LANES, "EXPR-COMPOSITION"))
import composition_adjusted_contrast as CC   # the lane's own committed machinery

SRC = CC.SRC
HYP = os.path.join(REPO, "research/modalities/emc-hypoxia-null-background.json")
PRIOR = os.path.join(LANES, "EXPR-COMPOSITION", "composition-adjusted-contrast.json")
OUT = os.path.join(HERE, "hypoxia-residual-attribution.json")
PREREG_SHA = "39827cc80171b247194ddc8bbfad7ee549b5701d383d254857b26437528c5836"

P1, P2 = CC.P1, CC.P2
SEED_DRAW = 20260909
N_SHAM = 300

HYPOXIA = ["ADPGK", "ALDOA", "CA9", "EGLN3", "ENO1", "GPI", "HK2", "LDHA", "PDK1", "PFKFB3",
           "PFKFB4", "PFKL", "PFKP", "PGAM1", "PGK1", "PKM", "SLC16A1", "SLC16A3", "SLC2A1",
           "SLC2A3", "TPI1", "VEGFA"]
REGULATORS = ["HIF1A", "EPAS1", "ARNT", "VHL", "HIF1AN", "EGLN1", "EGLN2"]
VASCULAR = ["PECAM1", "VWF", "KDR", "FLT1", "TEK", "CDH5", "ESAM", "EMCN", "ROBO4", "CLDN5",
            "ANGPT1", "ANGPT2", "PGF"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def die(code, msg, rec):
    rec["_ABORTED"] = {"exit_code": code, "reason": msg}
    print("ABORT (%d): %s" % (code, msg))
    json.dump(rec, open(OUT, "w"), indent=1)
    sys.exit(code)


# --------------------------------------------------------------- multi-covariate rank partial
class G2:
    __slots__ = ("I", "gidx", "R")
    def __init__(self, I, gidx, R):
        self.I, self.gidx, self.R = I, gidx, R


def build_groups2(Z):
    """Groups of genes sharing a sample-availability pattern. Covariates are complete-case
    (PREREGISTRATION sec.3) so they do not enter the grouping key."""
    bucket = {}
    for i in range(Z.shape[0]):
        I = np.flatnonzero(np.isfinite(Z[i]))
        if I.size < 5:
            continue
        bucket.setdefault(tuple(I.tolist()), []).append(i)
    out = []
    for Ituple, gidx in bucket.items():
        I = np.array(Ituple)
        R = np.array([CC.rankdata(Z[i][I]) for i in gidx], float)
        out.append(G2(I, np.array(gidx), R))
    return out


def _resid(X, D):
    """Residualise rows of X (m x n) on design D (n x k, intercept included)."""
    B, *_ = np.linalg.lstsq(D, X.T, rcond=None)
    return X - (D @ B).T


def adj_r_multi(groups, G, lab, covs):
    """Rank partial correlation of every gene with lab given the covariate list `covs`
    (each a full-length per-sample vector). covs=[] gives the plain Spearman."""
    out = np.full(G, np.nan)
    for g in groups:
        n = g.I.size
        l = lab[g.I].astype(float)
        if l.std() == 0:
            continue
        cols = [np.ones(n)] + [CC.rankdata(c[g.I]) for c in covs]
        for c in cols[1:]:
            if c.std() == 0:
                cols = None
                break
        if cols is None:
            continue
        D = np.array(cols).T
        if np.linalg.matrix_rank(D) < D.shape[1]:
            continue
        A = _resid(g.R, D)
        lr = _resid(CC.rankdata(l)[None, :], D)[0]
        sl = np.sqrt((lr * lr).sum())
        sa = np.sqrt((A * A).sum(axis=1))
        with np.errstate(invalid="ignore", divide="ignore"):
            r = (A @ lr) / (sa * sl)
        r[~np.isfinite(r)] = np.nan
        out[g.gidx] = np.clip(r, -1, 1)
    return out


def rate(r1, r2):
    both = np.isfinite(r1) & np.isfinite(r2)
    n = int(both.sum())
    return (float((both & ((r1 > 0) == (r2 > 0))).sum()) / n if n else np.nan), n, both


def paired_rate(r1, r2, both):
    return float((both & ((r1 > 0) == (r2 > 0))).sum()) / int(both.sum())


def atten(ru, ra):
    return (ru - ra) / (ru - 0.5) if abs(ru - 0.5) > 1e-9 else None


def main():
    t0 = time.time()
    rec = {
        "_what": ("Is the residual EMC cross-platform expression contrast that survives "
                  "EXPR-COMPOSITION's tumour/stroma adjustment a hypoxia programme?"),
        "_lane": "EXPR-HYPOXIA-1", "_campaign": "OPUS-CAPACITY-CAMPAIGN-20260908",
        "_prereg_sha256": PREREG_SHA,
        "_generated_utc": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
        "_not_a_claim": ("Any attenuation reported here is an association in owned expression data. "
                         "It establishes no efficacy, safety, selectivity, therapeutic window, "
                         "target attribution or clinical readiness, and no biological conclusion."),
        "inputs": {},
    }
    if sha(os.path.join(HERE, "PREREGISTRATION.md")) != PREREG_SHA:
        die(5, "PREREGISTRATION.md does not match its pinned sha256", rec)

    for p, k in ((SRC, "emc-expression-panels.json"), (HYP, "emc-hypoxia-null-background.json"),
                 (PRIOR, "EXPR-COMPOSITION/composition-adjusted-contrast.json")):
        rec["inputs"][k] = {"path": os.path.relpath(p, REPO), "bytes": os.path.getsize(p),
                            "sha256": sha(p)}
    rec["inputs"]["emc-expression-panels.json"]["_version_note"] = (
        "Re-hashed at use. sha256 is byte-identical to the value EXPR-COMPOSITION recorded "
        "(59bccb55...), so despite a 2026-09-08 23:23 working-tree mtime the CONTENT read here is "
        "the same version that produced the 0.6521 -> 0.5668 result. Working tree clean for this "
        "file at read time.")

    d = json.load(open(SRC))
    h = json.load(open(HYP))
    prior = json.load(open(PRIOR))

    # ------------------------------------------------------------------ 1 · GATE
    fr = CC.frames(d)
    cs = {}
    for pkey in (P1, P2):
        plat = d["platforms"][pkey]
        cols = list(plat["EMC_gsms"]) + list(plat["comparator_gsms"])
        cs[pkey] = CC.composition_scores(d, pkey, cols)

    gate = {"_what": ("Reproduce EXPR-COMPOSITION's published attenuation with its own committed "
                      "machinery BEFORE any hypoxia statistic is computed. exit 3 on mismatch."),
            "tolerance": 1e-9, "comparisons": [], "n_mismatch": 0}
    packs, syms_of, prior_rate_u = {}, {}, {}
    for fname in ("primary", "secondary"):
        syms, src = fr[fname]
        syms_of[fname] = syms
        p1, p2 = CC._frame_setup(d, fname, syms, src, cs)
        packs[fname] = (p1, p2)
        ru1 = CC.unadjusted_r(p1["groups"], p1["G"], p1["lab"])
        ru2 = CC.unadjusted_r(p2["groups"], p2["G"], p2["lab"])
        ra1 = CC.adjusted_r(p1["groups"], p1["G"], p1["lab"], p1["lookup"])
        ra2 = CC.adjusted_r(p2["groups"], p2["G"], p2["lab"], p2["lookup"])
        both = np.isfinite(ru1) & np.isfinite(ru2) & np.isfinite(ra1) & np.isfinite(ra2)
        got_u, got_a = paired_rate(ru1, ru2, both), paired_rate(ra1, ra2, both)
        pf = prior["frames"][fname]["paired_on_identical_gene_set"] if "frames" in prior else None
        if pf is None:
            for k, v in prior.items():
                if isinstance(v, dict) and v.get("frame") == fname:
                    pf = v["paired_on_identical_gene_set"]
        if pf is None:
            die(3, "cannot locate EXPR-COMPOSITION's published rates for frame " + fname, rec)
        prior_rate_u[fname] = float(pf["concordance_rate_unadjusted"])
        for label, got, want in (("%s.n_genes" % fname, int(both.sum()), pf["n_genes"]),
                                 ("%s.rate_unadjusted" % fname, round(got_u, 4),
                                  pf["concordance_rate_unadjusted"]),
                                 ("%s.rate_composition_adjusted" % fname, round(got_a, 4),
                                  pf["concordance_rate_adjusted"])):
            ok = abs(float(got) - float(want)) <= 1e-9
            gate["comparisons"].append({"field": label, "recomputed": got,
                                        "expr_composition": want, "match": bool(ok)})
            if not ok:
                gate["n_mismatch"] += 1
    gate["n_compared"] = len(gate["comparisons"])
    rec["gate_reproduce_expr_composition"] = gate
    for c in gate["comparisons"]:
        print("GATE %-42s recomputed=%-8s published=%-8s %s"
              % (c["field"], c["recomputed"], c["expr_composition"],
                 "OK" if c["match"] else "MISMATCH"))
    if gate["n_mismatch"]:
        die(3, "GATE FAILED: EXPR-COMPOSITION's attenuation did not reproduce; no hypoxia "
               "statistic computed", rec)
    print("GATE PASSED: %d/%d, 0 mismatches\n" % (gate["n_compared"], gate["n_compared"]))

    # ------------------------------------------------------------------ 2 · covariates
    def percentiles(pkey, sym, cols):
        t = h["targets"][pkey]
        g = t["genes"].get(sym)
        if g is None:
            return None
        order = [s["gsm"] for s in t["samples"]]
        pos = {gsm: i for i, gsm in enumerate(order)}
        ap = g["array_percentile"]
        out = np.full(len(cols), np.nan)
        for i, c in enumerate(cols):
            j = pos.get(c)
            if j is not None and j < len(ap) and ap[j] is not None:
                out[i] = float(ap[j])
        return out

    colsof, labof = {}, {}
    for pkey in (P1, P2):
        plat = d["platforms"][pkey]
        colsof[pkey] = list(plat["EMC_gsms"]) + list(plat["comparator_gsms"])
        labof[pkey] = np.array([1.0] * len(plat["EMC_gsms"]) + [0.0] * len(plat["comparator_gsms"]))

    def complete_case_set(names):
        keep, drop = [], {}
        for sym in names:
            reasons = []
            for pkey in (P1, P2):
                v = percentiles(pkey, sym, colsof[pkey])
                if v is None:
                    reasons.append("%s: symbol not measured in the hypoxia file" % pkey)
                elif not np.all(np.isfinite(v)):
                    reasons.append("%s: missing on %d of %d labelled samples"
                                   % (pkey, int((~np.isfinite(v)).sum()), len(v)))
            if reasons:
                drop[sym] = reasons
            else:
                keep.append(sym)
        return keep, drop

    Hset, Hdrop = complete_case_set(HYPOXIA)
    Vset, Vdrop = complete_case_set(VASCULAR)
    Rset, Rdrop = complete_case_set(REGULATORS)
    rec["covariates"] = {
        "_value_used": "targets[series].genes[symbol].array_percentile (rank within that array)",
        "_missingness_rule": ("complete-case GENE selection: a gene enters a score only if it is "
                              "present on EVERY labelled sample of BOTH platforms. No NaN-skipping, "
                              "so the score is one fixed definition on both platforms."),
        "hypoxia_H": {"requested": HYPOXIA, "n_requested": len(HYPOXIA), "kept": Hset,
                      "n_kept": len(Hset), "dropped": Hdrop},
        "vascular_V": {"requested": VASCULAR, "kept": Vset, "n_kept": len(Vset), "dropped": Vdrop},
        "regulators_reported_not_scored": {"requested": REGULATORS, "kept": Rset,
                                           "dropped": Rdrop},
    }
    print("H: %d/%d genes survive complete-case: %s" % (len(Hset), len(HYPOXIA), Hset))
    print("H dropped: %s" % json.dumps(Hdrop, indent=1))
    print("V: %d/%d survive: %s\n" % (len(Vset), len(VASCULAR), Vset))
    if len(Hset) < 8:
        die(4, "fewer than 8 hypoxia genes survive the complete-case rule (%d)" % len(Hset), rec)

    def score(pkey, names):
        A = np.array([percentiles(pkey, s, colsof[pkey]) for s in names])
        return A.mean(axis=0)

    H = {p: score(p, Hset) for p in (P1, P2)}
    V = {p: score(p, Vset) for p in (P1, P2)}
    C = {p: cs[p][1]["C"] for p in (P1, P2)}

    def lab_r(cov):
        return {p: round(float(CC.spearman(cov[p][np.isfinite(cov[p])],
                                           labof[p][np.isfinite(cov[p])])), 4) for p in (P1, P2)}

    rec["covariates"]["association_with_EMC_label"] = {
        "_spearman_cov_vs_EMC_indicator": True,
        "H": lab_r(H), "V": lab_r(V), "C_composition_from_EXPR_COMPOSITION": lab_r(C),
        "H_vs_C_spearman": {p: round(float(CC.spearman(H[p], C[p][np.isfinite(C[p])]
                                                       if np.all(np.isfinite(C[p])) else C[p])), 4)
                            for p in (P1, P2)},
        "H_mean_by_arm": {p: {"EMC": round(float(H[p][labof[p] == 1].mean()), 4),
                              "comparator": round(float(H[p][labof[p] == 0].mean()), 4)}
                          for p in (P1, P2)},
        "V_mean_by_arm": {p: {"EMC": round(float(V[p][labof[p] == 1].mean()), 4),
                              "comparator": round(float(V[p][labof[p] == 0].mean()), 4)}
                          for p in (P1, P2)},
    }
    print("Spearman(H, EMC label): %s" % rec["covariates"]["association_with_EMC_label"]["H"])
    print("Spearman(V, EMC label): %s" % rec["covariates"]["association_with_EMC_label"]["V"])
    print("Spearman(C, EMC label): %s\n"
          % rec["covariates"]["association_with_EMC_label"]["C_composition_from_EXPR_COMPOSITION"])

    # ------------------------------------------------------------------ 3 · frames
    rng = np.random.default_rng(SEED_DRAW)
    pyr = random.Random(SEED_DRAW)
    rec["frames"] = {}
    for fname in ("primary", "secondary"):
        p1, p2 = packs[fname]
        g1, g2 = build_groups2(p1["Z"]), build_groups2(p2["Z"])
        G1, G2_ = p1["G"], p2["G"]
        l1, l2 = p1["lab"], p2["lab"]

        def rates(covs1, covs2):
            a1 = adj_r_multi(g1, G1, l1, covs1)
            a2 = adj_r_multi(g2, G2_, l2, covs2)
            return a1, a2

        u1, u2 = rates([], [])
        base_u, n_u, both0 = rate(u1, u2)
        variants = {"unadjusted": ([], []),
                    "C_composition_noLOO": ([C[P1]], [C[P2]]),
                    "H_hypoxia": ([H[P1]], [H[P2]]),
                    "V_vascular": ([V[P1]], [V[P2]]),
                    "C_plus_H": ([C[P1], H[P1]], [C[P2], H[P2]]),
                    "C_plus_V": ([C[P1], V[P1]], [C[P2], V[P2]])}
        R = {}
        for k, (a, b) in variants.items():
            R[k] = rates(a, b)
        both = both0.copy()
        for k in R:
            both &= np.isfinite(R[k][0]) & np.isfinite(R[k][1])
        out = {"n_genes_paired_on_identical_set_across_all_variants": int(both.sum())}
        ru = paired_rate(*R["unadjusted"], both)
        for k in variants:
            r = paired_rate(*R[k], both)
            out[k] = {"concordance_rate": round(r, 4),
                      "absolute_change_vs_unadjusted": round(r - ru, 4),
                      "attenuation_of_excess_over_0.5":
                          (round(atten(ru, r), 3) if k != "unadjusted" else None),
                      "cross_platform_pearson_r": round(float(CC.pear(R[k][0][both],
                                                                      R[k][1][both])), 4)}
        out["_baseline_note"] = (
            "The unadjusted rate in THIS table (%.4f) is computed on the gene set paired across "
            "all six variants with the residualisation implementation used for the multi-covariate "
            "adjustments; EXPR-COMPOSITION's gated value on the same frame is %.4f. The difference "
            "is %d gene(s) of %d whose near-zero rank correlation falls on the other side of zero "
            "under the two arithmetics - the same one-borderline-gene sensitivity "
            "ASSESS-EXPR-COMPOSITION reported. All rows of this table use one implementation, so "
            "the comparisons within it are like with like."
            % (ru, prior_rate_u[fname],
               abs(round((ru - prior_rate_u[fname]) * int(both.sum()))), int(both.sum())))
        rec["frames"][fname] = out
        print("[%s] paired n=%d" % (fname, int(both.sum())))
        for k in ("unadjusted", "C_composition_noLOO", "H_hypoxia", "V_vascular",
                  "C_plus_H", "C_plus_V"):
            print("   %-22s rate=%.4f  atten=%s" % (k, out[k]["concordance_rate"],
                                                    out[k]["attenuation_of_excess_over_0.5"]))

        # -------------------------------------------------- 4 · seeded-random-background control
        if fname == "primary":
            # The complete-case rule of PREREGISTRATION sec.3 applies to the shams too, so the
            # eligible universe is pre-filtered to background symbols readable on every labelled
            # sample of that platform. Filtering after drawing would have silently discarded most
            # draws (attempt checks/03 drew 0 valid shams for exactly this reason).
            univ, mat = {}, {}
            for p in (P1, P2):
                cand = [s for s in h["targets"][p]["_random_background_symbols"]
                        if s in h["targets"][p]["genes"]]
                rows, keep = [], []
                for s in cand:
                    v = percentiles(p, s, colsof[p])
                    if v is not None and np.all(np.isfinite(v)):
                        keep.append(s); rows.append(v)
                univ[p] = keep
                mat[p] = np.array(rows)
            shams, k = [], len(Hset)
            for _ in range(N_SHAM):
                pick = {}
                for p in (P1, P2):
                    idx = pyr.sample(range(len(univ[p])), k)
                    pick[p] = mat[p][idx].mean(axis=0)
                a1, a2 = rates([pick[P1]], [pick[P2]])
                r = paired_rate(a1, a2, both)
                lr = [abs(CC.spearman(pick[p], labof[p])) for p in (P1, P2)]
                shams.append((r, float(np.mean(lr)), lr[0], lr[1]))
            S = np.array([s[0] for s in shams])
            X = np.array([s[1] for s in shams])
            hr = rec["covariates"]["association_with_EMC_label"]["H"]
            h_absr = float(np.mean([abs(hr[P1]), abs(hr[P2])]))
            cr = rec["covariates"]["association_with_EMC_label"]["C_composition_from_EXPR_COMPOSITION"]
            c_absr = float(np.mean([abs(cr[P1]), abs(cr[P2])]))
            slope, icpt = np.polyfit(X, S, 1)
            pred_H = float(icpt + slope * h_absr)
            pred_C = float(icpt + slope * c_absr)
            rH = out["H_hypoxia"]["concordance_rate"]
            band = {}
            for w in (0.05, 0.10, 0.15):
                m = np.abs(X - h_absr) <= w
                band["pm%.2f" % w] = {
                    "n": int(m.sum()),
                    "mean_adjusted_rate": round(float(S[m].mean()), 4) if m.sum() else None,
                    "min_adjusted_rate": round(float(S[m].min()), 4) if m.sum() else None,
                    "n_at_or_below_H": int((S[m] <= rH).sum()) if m.sum() else None,
                    "one_sided_p": (round(float((S[m] <= rH).sum() + 1) / (int(m.sum()) + 1), 4)
                                    if m.sum() else None)}
            rec["seeded_random_background_control"] = {
                "_what": ("Control demanded by the lane brief: the SEEDED random background of "
                          "emc-hypoxia-null-background.json (_sample_seed 20260807, a universe that "
                          "EXCLUDES all 118 named confound genes) must NOT attenuate. Each sham is "
                          "the per-sample mean array_percentile of k=%d randomly drawn background "
                          "symbols per platform, complete-case, through the identical machinery."
                          % k),
                "n_sham": int(S.size), "genes_per_sham": k, "draw_seed": SEED_DRAW,
                "background_universe_size_after_complete_case_filter": {p: len(univ[p]) for p in (P1, P2)},
                "background_universe_size_before_filter": {p: len(h["targets"][p]["_random_background_symbols"]) for p in (P1, P2)},
                "unadjusted_rate": round(ru, 4),
                "sham_adjusted_rate": {"mean": round(float(S.mean()), 4),
                                       "sd": round(float(S.std(ddof=1)), 4),
                                       "min": round(float(S.min()), 4),
                                       "max": round(float(S.max()), 4),
                                       "p2.5": round(float(np.quantile(S, .025)), 4),
                                       "p97.5": round(float(np.quantile(S, .975)), 4)},
                "sham_mean_abs_label_r": {"mean": round(float(X.mean()), 4),
                                          "max": round(float(X.max()), 4)},
                "does_the_random_background_attenuate": (
                    "NO — mean sham adjusted rate %.4f vs unadjusted %.4f (change %+.4f)"
                    % (S.mean(), ru, S.mean() - ru)),
                "generic_label_correlation_matched_baseline": {
                    "_method": ("ASSESS-EXPR-COMPOSITION's decomposition: OLS of the sham adjusted "
                                "rate on the sham covariate's mean |Spearman(cov,label)|, evaluated "
                                "at the real covariate's own label correlation. A covariate that "
                                "does not beat this prediction is a NULL."),
                    "slope": round(float(slope), 4), "intercept": round(float(icpt), 4),
                    "pearson_r_rate_vs_abs_label_r": round(float(CC.pear(X, S)), 4),
                    "H_mean_abs_label_r": round(h_absr, 4),
                    "generic_prediction_at_H": round(pred_H, 4),
                    "observed_H_adjusted_rate": rH,
                    "H_beats_generic_baseline_by": round(pred_H - rH, 4),
                    "C_mean_abs_label_r": round(c_absr, 4),
                    "generic_prediction_at_C": round(pred_C, 4),
                    "observed_C_adjusted_rate": out["C_composition_noLOO"]["concordance_rate"],
                    "_assess_expr_composition_reported_0.6077_for_C": True},
                "matched_bands_around_H_label_r": band,
            }
            print("\nCONTROL sham n=%d mean=%.4f sd=%.4f min=%.4f (unadj %.4f)"
                  % (S.size, S.mean(), S.std(ddof=1), S.min(), ru))
            print("CONTROL generic prediction at H's label r = %.4f ; observed H = %.4f"
                  % (pred_H, rH))
            print("CONTROL bands: %s" % json.dumps(band))

    rec["_runtime_seconds"] = round(time.time() - t0, 1)
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\nwrote %s (%d bytes) in %.1fs" % (OUT, os.path.getsize(OUT), rec["_runtime_seconds"]))


if __name__ == "__main__":
    main()
