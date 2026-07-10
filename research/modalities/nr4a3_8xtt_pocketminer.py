#!/usr/bin/env python3
"""
PocketMiner cryptic-pocket cross-check on the EXPERIMENTAL apo NR4A3 LBD (PDB 8XTT) — the review's
explicit ask, rebased off the AF2 model onto the experimental NMR ensemble.

WHY. `entry.py` (the original PocketMiner cross-check) runs on the AF2 apo model (AFDB AF-Q92570). The
2026-07-10 8XTT benchmark (nr4a3-8xtt-benchmark-findings.md) showed the experimental apo NMR ensemble
reproduces our cryptic-druggability distribution (~20% of 20 conformers druggable) BUT the AF2 *atomic*
pocket geometry diverges (~3.5 A pocket-local Ca-RMSD). So the orthogonal cryptic-pocket predictor
(PocketMiner, an independent GVP GNN) must be re-run on the EXPERIMENTAL structure: does it still enrich
the Pocket-5 residues over the LBD background on 8XTT, not just on AF2?

This module is the PURE analysis layer (no TensorFlow / mdtraj / biopython / network) — it takes the raw
per-residue PocketMiner scores (keyed by 8XTT author residue number) plus the UniProt->8XTT numbering map
(built by nr4a3_8xtt_benchmark.map_uniprot_to_pdb inside the AWS job) and computes, PER CONFORMER, the
Pocket-5-over-LBD enrichment + flagged-residue overlap, then aggregates a DISTRIBUTION across the scored
8XTT conformers and a plain verdict. All dependency-free so tests/test_8xtt_pocketminer.py exercises it
locally without any of the heavy stack. The SageMaker orchestration (fetch/split/PocketMiner inference/
mapping) lives in pocketminer_src/entry_8xtt_pm.py.

Reuses nr4a3_8xtt_benchmark for the constants + distribution_stats (single source of truth) and mirrors
the overlap/enrichment fields emitted by pocketminer_src/entry.py::analyse so the two cross-checks are
directly comparable (AF2 vs experimental).
"""
import nr4a3_8xtt_benchmark as bm

# Single source of truth for the site definition (identical to entry.py / the benchmark).
UNIPROT = bm.UNIPROT                          # Q92570
POCKET5 = list(bm.POCKET5)                    # 10 Pocket-5 lining residues (UniProt numbering)
HANDLES = list(bm.HANDLES)                    # 7 selectivity handles (subset, UniProt numbering)
# PocketMiner emits a per-residue cryptic-pocket probability in [0,1]. Report several cutoffs so the
# overlap claim is not threshold-cherry-picked (same cutoffs as entry.py).
HIGH_CUTOFF = 0.7
MODERATE_CUTOFF = 0.5
# The "enriches" bar for the verdict: Pocket-5 mean must beat the LBD background by this factor AND at
# least one Pocket-5 residue must clear the moderate cutoff. Kept modest + transparent (a weak-but-real
# enrichment is not a null — the same honest framing entry.py uses).
ENRICH_REF = 1.0


def analyse_conformer(scores_by_auth, uni_to_auth, high=HIGH_CUTOFF, mod=MODERATE_CUTOFF):
    """Per-conformer PocketMiner analysis on ONE 8XTT conformer, mapped back to UniProt numbering.

    `scores_by_auth`: {8XTT_author_resnum -> cryptic score in [0,1]} for every scored LBD residue of this
        conformer (exactly what PocketMiner returns, keyed by the loaded structure's resSeq).
    `uni_to_auth`: {UniProt_resnum -> 8XTT_author_resnum} numbering map (from
        nr4a3_8xtt_benchmark.map_uniprot_to_pdb). Pocket-5 is defined in UniProt numbering, so we translate
        it onto this conformer's author numbering before scoring.

    Returns a dict mirroring pocketminer_src/entry.py::analyse's `overlap` block (so AF2 and 8XTT results
    are directly comparable), plus the per-Pocket-5-residue scores + percentile ranks. Pure."""
    if not scores_by_auth:
        return {"n_residues_scored": 0, "_status": "no scores for this conformer"}
    # Pocket-5 (and handles) translated onto THIS conformer's author numbering.
    p5_auth = {u: uni_to_auth[u] for u in POCKET5 if u in uni_to_auth and uni_to_auth[u] in scores_by_auth}
    p5_scores_uni = {u: scores_by_auth[a] for u, a in p5_auth.items()}
    p5_vals = list(p5_scores_uni.values())
    lbd_vals = list(scores_by_auth.values())

    def _mean(xs):
        return (sum(xs) / len(xs)) if xs else None

    lbd_mean = _mean(lbd_vals)
    p5_mean = _mean(p5_vals)
    p5_max = max(p5_vals) if p5_vals else None
    enrichment = (round(p5_mean / lbd_mean, 3) if (p5_mean and lbd_mean) else None)

    # flagged residues (author numbering) at each cutoff, and Pocket-5 overlap with them.
    flagged_high = sorted(a for a, s in scores_by_auth.items() if s >= high)
    flagged_mod = sorted(a for a, s in scores_by_auth.items() if s >= mod)
    p5_auth_set = set(p5_auth.values())
    p5_in_high = sorted(p5_auth_set & set(flagged_high))
    p5_in_mod = sorted(p5_auth_set & set(flagged_mod))

    # percentile rank of each Pocket-5 residue among all scored LBD residues (1.0 = top-scoring).
    ranked = sorted(scores_by_auth.items(), key=lambda kv: kv[1], reverse=True)
    order = [a for a, _ in ranked]
    n = len(order)
    p5_pct = {str(u): round(1 - order.index(a) / n, 3) for u, a in p5_auth.items()}

    return {
        "n_residues_scored": n,
        "pocket5_scores_uniprot": {str(u): round(s, 4) for u, s in sorted(p5_scores_uni.items())},
        "pocket5_percentile_rank_uniprot": p5_pct,
        "flagged_high_authnum": flagged_high,
        "score_cutoffs": {"high": high, "moderate": mod},
        "overlap": {
            "n_pocket5_mapped": len(p5_auth),
            "pocket5_in_flagged_high": p5_in_high,
            "pocket5_in_flagged_moderate": p5_in_mod,
            "frac_pocket5_high": (round(len(p5_in_high) / len(p5_auth), 3) if p5_auth else None),
            "frac_pocket5_moderate": (round(len(p5_in_mod) / len(p5_auth), 3) if p5_auth else None),
            "pocket5_mean_score": (round(p5_mean, 4) if p5_mean is not None else None),
            "pocket5_max_score": (round(p5_max, 4) if p5_max is not None else None),
            "lbd_mean_score": (round(lbd_mean, 4) if lbd_mean is not None else None),
            "enrichment_pocket5_over_lbd": enrichment,
        },
    }


def aggregate_conformers(per_conformer, enrich_ref=ENRICH_REF):
    """Aggregate the per-conformer analyses into DISTRIBUTIONS across the scored 8XTT conformers + a
    verdict. `per_conformer` is a list of {"model": int, "analysis": <analyse_conformer dict>}.

    Reuses nr4a3_8xtt_benchmark.distribution_stats for the min/median/max/IQR/mean bookkeeping so the
    stats convention matches the druggability benchmark exactly. Returns a dict with the enrichment,
    Pocket-5-mean, Pocket-5-max and frac-moderate distributions + a transparent verdict. Pure."""
    enr, p5mean, p5max, frac_mod = [], [], [], []
    for rec in per_conformer:
        ov = (rec.get("analysis") or {}).get("overlap")
        if not ov:
            continue
        if ov.get("enrichment_pocket5_over_lbd") is not None:
            enr.append(ov["enrichment_pocket5_over_lbd"])
        if ov.get("pocket5_mean_score") is not None:
            p5mean.append(ov["pocket5_mean_score"])
        if ov.get("pocket5_max_score") is not None:
            p5max.append(ov["pocket5_max_score"])
        if ov.get("frac_pocket5_moderate") is not None:
            frac_mod.append(ov["frac_pocket5_moderate"])
    enrich_dist = bm.distribution_stats(enr, threshold=enrich_ref)
    p5mean_dist = bm.distribution_stats(p5mean, threshold=MODERATE_CUTOFF)
    p5max_dist = bm.distribution_stats(p5max, threshold=MODERATE_CUTOFF)
    frac_mod_dist = bm.distribution_stats(frac_mod, threshold=0.0)

    median_enr = enrich_dist.get("median")
    any_flagged = (p5max_dist.get("max") or 0.0) >= MODERATE_CUTOFF
    # enriches: the experimental ensemble's Pocket-5 typically scores ABOVE the LBD background
    # (median enrichment > ref) AND at least one conformer flags a Pocket-5 residue at the moderate cutoff.
    enriches = (median_enr is not None and median_enr > enrich_ref and any_flagged)
    if enrich_dist.get("n", 0) == 0:
        verdict = "no-data"
        rationale = "no conformer produced a Pocket-5-over-LBD enrichment (mapping/scoring failed)"
    elif enriches:
        verdict = "enriches"
        rationale = (f"median Pocket-5/LBD enrichment {median_enr} > {enrich_ref} across "
                     f"{enrich_dist['n']} conformers, and Pocket-5 reaches the moderate cutoff "
                     f"(max Pocket-5 score {p5max_dist.get('max')}) — PocketMiner independently flags the "
                     "orthosteric site on the EXPERIMENTAL structure, corroborating the AF2 cross-check.")
    else:
        verdict = "weak-or-null"
        rationale = (f"median Pocket-5/LBD enrichment {median_enr} (n={enrich_dist['n']}); "
                     f"max Pocket-5 score {p5max_dist.get('max')} vs moderate cutoff {MODERATE_CUTOFF} — "
                     "enrichment on the experimental structure is weak/absent; report honestly, not as "
                     "corroboration.")
    return {
        "n_conformers_scored": enrich_dist.get("n", 0),
        "enrichment_distribution": enrich_dist,
        "pocket5_mean_distribution": p5mean_dist,
        "pocket5_max_distribution": p5max_dist,
        "frac_pocket5_moderate_distribution": frac_mod_dist,
        "enrich_ref": enrich_ref,
        "moderate_cutoff": MODERATE_CUTOFF,
        "verdict": verdict,
        "rationale": rationale,
    }


def select_models(available, requested):
    """Resolve the requested conformer list against those actually present in the split 8XTT ensemble.

    `available`: iterable of 1-based model indices present after splitting 8XTT (e.g. range(1,21)).
    `requested`: 'all' (case-insensitive) -> every available model, or a comma/space list like
        '2,8,20,6' -> exactly those, intersected with `available` (order preserved, dedup). Fails loud on
        an empty/garbage request or when NONE of the requested models exist. Pure."""
    avail = list(dict.fromkeys(int(m) for m in available))
    if not avail:
        raise ValueError("no 8XTT conformers available to select from")
    if requested is None or str(requested).strip().lower() in ("all", ""):
        return avail
    want = []
    for tok in str(requested).replace(",", " ").split():
        want.append(int(tok))
    if not want:
        raise ValueError(f"could not parse requested models from {requested!r}")
    avail_set = set(avail)
    chosen = [m for m in dict.fromkeys(want) if m in avail_set]
    if not chosen:
        raise ValueError(f"none of the requested models {want} are in the available set {avail}")
    return chosen
