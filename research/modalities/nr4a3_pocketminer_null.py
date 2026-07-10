#!/usr/bin/env python3
"""
Statistical null for review comment 8: is PocketMiner's Pocket-5 enrichment (mean 0.64 vs 0.47 LBD
background) better than random 10-residue sets, or an artifact of the high-scoring N-terminal truncation
edge? We build an empirical permutation null over the full per-residue PocketMiner scores and report the
observed Pocket-5 mean's percentile, WITH and WITHOUT a terminal mask (residues 373-398, the isolated-LBD
chain-terminus flexibility artifact the paper already flags), plus a contiguous-window control.

Input: results/nr4a3-pocketminer/pocketminer_nr4a3_result.json (full 254-residue array, archived from S3).
Output: nr4a3-pocketminer-null.json. Pure + unit-tested (deterministic: fixed seed, stdlib random).
"""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(REPO, "results", "nr4a3-pocketminer", "pocketminer_nr4a3_result.json")
OUT = os.path.join(HERE, "nr4a3-pocketminer-null.json")
POCKET5 = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]
TERMINAL_MASK = set(range(373, 399))  # N-terminal truncation edge (top-scoring artifact region)
N_PERM = 20000
SEED = 20260710


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def permutation_pvalue(scores, target_residues, n_perm=N_PERM, seed=SEED, exclude=frozenset()):
    """scores: {resnum(int): score}. Returns (observed_mean, null_mean, p_value, pool_size).
    p = fraction of random same-size residue sets (drawn from pool minus `exclude` minus the target)
    whose mean score >= the observed target mean. One-sided (enrichment)."""
    target = [r for r in target_residues if r in scores]
    obs = _mean([scores[r] for r in target])
    pool = [r for r in scores if r not in exclude and r not in target_residues]
    k = len(target)
    if k == 0 or len(pool) < k:
        raise ValueError("empty target or pool too small")
    rng = random.Random(seed)
    null_means = []
    ge = 0
    for _ in range(n_perm):
        sample = rng.sample(pool, k)
        m = _mean([scores[r] for r in sample])
        null_means.append(m)
        if m >= obs:
            ge += 1
    p = (ge + 1) / (n_perm + 1)   # add-one (never reports p=0)
    return obs, _mean(null_means), p, len(pool)


def contiguous_pvalue(scores, target_residues, seed=SEED, exclude=frozenset()):
    """Null over contiguous windows of the same size (tests spatial-patch, not just random-set)."""
    target = [r for r in target_residues if r in scores]
    obs = _mean([scores[r] for r in target])
    resnums = sorted(r for r in scores if r not in exclude)
    k = len(target)
    windows = [resnums[i:i + k] for i in range(len(resnums) - k + 1)]
    means = [_mean([scores[r] for r in w]) for w in windows]
    ge = sum(1 for m in means if m >= obs)
    return obs, _mean(means) if means else 0.0, (ge + 1) / (len(means) + 1), len(windows)


def main():
    d = json.load(open(SRC))
    scores = {int(k): float(v) for k, v in d["per_residue_scores"].items()}
    res = {}
    obs, nmean, p, pool = permutation_pvalue(scores, POCKET5)
    res["random_all"] = {"observed_mean": round(obs, 4), "null_mean": round(nmean, 4),
                         "p_value": round(p, 5), "pool_size": pool}
    obs, nmean, p, pool = permutation_pvalue(scores, POCKET5, exclude=TERMINAL_MASK)
    res["random_terminal_masked"] = {"observed_mean": round(obs, 4), "null_mean": round(nmean, 4),
                                     "p_value": round(p, 5), "pool_size": pool,
                                     "_note": "N-terminal edge 373-398 excluded from the null pool"}
    obs, nmean, p, nw = contiguous_pvalue(scores, POCKET5, exclude=TERMINAL_MASK)
    res["contiguous_terminal_masked"] = {"observed_mean": round(obs, 4), "null_mean": round(nmean, 4),
                                         "p_value": round(p, 5), "n_windows": nw}
    out = {
        "_title": "PocketMiner Pocket-5 enrichment permutation null (review comment 8)",
        "_method": f"Empirical one-sided permutation null, {N_PERM} random same-size residue sets "
                   "(add-one p); terminal mask 373-398; contiguous-window control.",
        "n_residues_scored": len(scores),
        "pocket5_residues": POCKET5,
        "results": res,
    }
    json.dump(out, open(OUT, "w"), indent=2)
    for k, r in res.items():
        print(f"{k}: pocket5 mean {r['observed_mean']} vs null {r['null_mean']} -> p={r['p_value']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
