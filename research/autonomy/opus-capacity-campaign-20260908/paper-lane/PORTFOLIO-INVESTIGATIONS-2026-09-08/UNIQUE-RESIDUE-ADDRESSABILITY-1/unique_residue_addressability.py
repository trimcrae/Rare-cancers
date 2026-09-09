#!/usr/bin/env python3
"""UNIQUE-RESIDUE-ADDRESSABILITY-1 — are NR4A3's unique INDEL residues addressable geometry?

Per-frame Shrake-Rupley RSA and side-chain-heavy-atom-centroid distance to the nearest cryptic-pocket
heavy atom, over the committed NR4A3 conformer ensemble, for every residue of the modelled LBD; then a
uniqueness-LABEL PERMUTATION that must abolish any clustering.

Geometry only. Exposure and pocket proximity are NOT druggability, selectivity, efficacy or safety.
Reuses the committed routines unchanged (ATLAS.parse_pdb / shrake_rupley / residue_rsa,
B.load_paralogue, PDYN.construct_frame). Read-only outside this lane directory.
"""
from __future__ import annotations
import glob, hashlib, itertools, json, math, os, random, sys, time
from multiprocessing import Pool

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "research", "modalities"))
import nr4a_differential_atlas as ATLAS
import nr4a3_basin_search as B
import nr4a_paralogue_dynamics as PDYN
import nr4a_paralogue_unique_residues as UNIQ

CENSUS = os.path.join(REPO, "research", "modalities", "nr4a-reciprocal-uniqueness-census.json")
SEQS = os.path.join(REPO, "research", "modalities", "nr4a-sequences-cache.json")
ENS = os.path.join(REPO, "results", "nr4a3-pocket-reharmonize")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unique-residue-addressability.json")
NPOINTS = int(os.environ.get("NPOINTS", "96"))
NPERM = int(os.environ.get("NPERM", "20000"))
SEED = 20260908


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def frame_paths():
    out = []
    for rep in ("release_rep0", "release_rep1", "release_rep2"):
        out.extend(sorted(glob.glob(os.path.join(ENS, rep, "*", "frame.pdb"))))
    return out


def indel_sets(census):
    """NR4A3-present / paralogue-absent indel runs, expanded to UniProt residue numbers."""
    pc = census["pairwise_indel_census"]
    runs = []
    for key, absent in (("NR4A3_present__NR4A1_absent", "NR4A1"), ("NR4A3_present__NR4A2_absent", "NR4A2")):
        for r in pc[key]:
            if r.get("terminal"):
                continue
            runs.append({"absent_in": absent, "first": r["first_resnum"], "last": r["last_resnum"],
                         "length": r["length"], "segment": r["segment"],
                         "robust_both_aligners": bool(r.get("robust_both_aligners"))})
    three = {}
    for r in census["three_way_indels"]:
        if r.get("terminal"):
            continue
        for u in range(r["first_resnum"], r["last_resnum"] + 1):
            three[u] = bool(r.get("robust_both_aligners"))
    by_res = {}
    for r in runs:
        for u in range(r["first"], r["last"] + 1):
            e = by_res.setdefault(u, {"absent_in": [], "robust_runs": 0, "runs": 0, "run_lengths": []})
            e["absent_in"].append(r["absent_in"])
            e["runs"] += 1
            e["run_lengths"].append(r["length"])
            if r["robust_both_aligners"]:
                e["robust_runs"] += 1
    for u, e in by_res.items():
        e["three_way"] = u in three
        e["absent_in"] = sorted(set(e["absent_in"]))
    return runs, by_res


def subst_unique(census):
    """NR4A3 unique-and-robust positions whose partners are both real residues (a substitution, not a gap)."""
    out = {}
    for row in census["directions"]["NR4A3"]["unique_and_robust_rows"]:
        p = row["partners"]
        gap = any(p[k]["residue"] == "-" for k in p)
        out[row["resnum"]] = {"residue": row["residue"], "gap_partner": gap}
    return out


def score_frame(path):
    model = B.load_paralogue(path)
    residues, atoms = ATLAS.parse_pdb(path)
    sasa = ATLAS.shrake_rupley(atoms, n_points=NPOINTS)
    rsa = ATLAS.residue_rsa(residues, sasa)
    pocket_local = [x - B.UNIPROT_OFFSET for x in UNIQ.CRYPTIC_POCKET_UNIPROT]
    off, pocket, missing = PDYN.construct_frame(model, "NR4A3", SEQ_CACHE, model, pocket_local)
    patoms = []
    for r in pocket:
        patoms.extend((a["x"], a["y"], a["z"]) for a in model["atoms_by_res"].get(r, []))
    rows = {}
    for rid, aa in model["residues"]:
        c = model["cb"].get(rid)
        if c is None:
            continue
        d = min(math.dist(c, q) for q in patoms) if patoms else None
        rows[rid] = {"aa": aa, "uniprot": rid + off, "rsa": rsa.get(rid), "d_pocket": d, "xyz": c}
    return {"path": os.path.relpath(path, REPO), "offset": off, "n_res": len(rows),
            "pocket_local": pocket, "pocket_missing": missing, "rows": rows}


def _init():
    global SEQ_CACHE
    SEQ_CACHE = json.load(open(SEQS))


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def quant(xs, q):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    i = q * (len(xs) - 1)
    lo, hi = int(math.floor(i)), int(math.ceil(i))
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def perm_test(values, labelled_idx, pool_idx, nperm, rng, lower_is_extreme):
    """Label permutation: draw |labelled| indices uniformly from pool_idx."""
    obs = mean([values[i] for i in labelled_idx])
    k = len(labelled_idx)
    null = []
    for _ in range(nperm):
        s = rng.sample(pool_idx, k)
        null.append(mean([values[i] for i in s]))
    if lower_is_extreme:
        hits = sum(1 for v in null if v <= obs)
    else:
        hits = sum(1 for v in null if v >= obs)
    return {"observed": obs, "null_mean": mean(null), "null_sd": (sum((v - mean(null)) ** 2 for v in null) / (len(null) - 1)) ** 0.5,
            "null_p05": quant(null, 0.05), "null_p50": quant(null, 0.5), "null_p95": quant(null, 0.95),
            "n_perm": nperm, "p_one_sided": (hits + 1) / (nperm + 1),
            "direction": "lower" if lower_is_extreme else "higher"}


def block_shift_test(values, label_vec, pool_mask, lower_is_extreme):
    """Circular-shift randomisation along the chain: preserves the contiguous run structure of the labels."""
    n = len(label_vec)
    idx0 = [i for i in range(n) if label_vec[i] and pool_mask[i]]
    obs = mean([values[i] for i in idx0])
    null = []
    for s in range(1, n):
        idx = [(i + s) % n for i in range(n) if label_vec[i]]
        idx = [i for i in idx if pool_mask[i]]
        v = mean([values[i] for i in idx])
        if v is not None:
            null.append(v)
    hits = sum(1 for v in null if (v <= obs if lower_is_extreme else v >= obs))
    return {"observed": obs, "n_shifts": len(null), "null_p50": quant(null, 0.5),
            "null_p05": quant(null, 0.05), "null_p95": quant(null, 0.95),
            "p_one_sided": (hits + 1) / (len(null) + 1),
            "direction": "lower" if lower_is_extreme else "higher"}


def spatial_stats(coords):
    """Mean pairwise distance and radius of gyration of a set of side-chain centroids."""
    n = len(coords)
    if n < 2:
        return None, None
    ds = [math.dist(a, b) for a, b in itertools.combinations(coords, 2)]
    cx = [sum(c[i] for c in coords) / n for i in range(3)]
    rg = (sum(math.dist(c, cx) ** 2 for c in coords) / n) ** 0.5
    return sum(ds) / len(ds), rg


def main():
    t0 = time.time()
    census = json.load(open(CENSUS))
    seqs = json.load(open(SEQS))
    runs, indel_by_res = indel_sets(census)
    subst = subst_unique(census)
    paths = frame_paths()
    print(f"[lane] {len(paths)} frames, NPOINTS={NPOINTS}, NPERM={NPERM}", flush=True)
    with Pool(4, initializer=_init) as p:
        frames = p.map(score_frame, paths)
    print(f"[lane] scored in {time.time()-t0:.1f}s", flush=True)

    offsets = sorted({f["offset"] for f in frames})
    locals_all = sorted(frames[0]["rows"])
    for f in frames:
        assert sorted(f["rows"]) == locals_all, f["path"]
    off = offsets[0]
    assert len(offsets) == 1, offsets
    uni_of = {r: r + off for r in locals_all}
    pocket_uni = set(UNIQ.CRYPTIC_POCKET_UNIPROT)

    per_res = {}
    for r in locals_all:
        rsas = [f["rows"][r]["rsa"] for f in frames]
        ds = [f["rows"][r]["d_pocket"] for f in frames]
        per_res[r] = {
            "uniprot": uni_of[r], "aa": frames[0]["rows"][r]["aa"],
            "rsa_mean": mean(rsas), "rsa_p10": quant(rsas, 0.10), "rsa_median": quant(rsas, 0.5),
            "rsa_p90": quant(rsas, 0.90), "rsa_max": max(rsas),
            "frac_frames_rsa_ge_0.25": sum(1 for v in rsas if v >= 0.25) / len(rsas),
            "d_pocket_mean": mean(ds), "d_pocket_median": quant(ds, 0.5), "d_pocket_min": min(ds),
            "d_pocket_p10": quant(ds, 0.10),
        }

    order = locals_all
    rsa_vec = [per_res[r]["rsa_mean"] for r in order]
    d_vec = [per_res[r]["d_pocket_mean"] for r in order]
    is_pocket = [uni_of[r] in pocket_uni for r in order]

    label_defs = {
        "indel_union": lambda u: u in indel_by_res,
        "indel_three_way": lambda u: indel_by_res.get(u, {}).get("three_way", False),
        "indel_alignment_robust": lambda u: indel_by_res.get(u, {}).get("robust_runs", 0) > 0,
        "unique_robust_substitution": lambda u: (u in subst and not subst[u]["gap_partner"]),
        "unique_robust_any": lambda u: u in subst,
    }
    rng = random.Random(SEED)
    pool_all = list(range(len(order)))
    pool_nonpocket = [i for i in pool_all if not is_pocket[i]]

    label_results = {}
    for name, fn in label_defs.items():
        vec = [fn(uni_of[r]) for r in order]
        idx = [i for i in pool_all if vec[i]]
        idx_np = [i for i in idx if not is_pocket[i]]
        entry = {"n_labelled_in_modelled_lbd": len(idx),
                 "uniprot": [uni_of[order[i]] for i in idx],
                 "n_overlapping_pocket_definition": len(idx) - len(idx_np)}
        if len(idx_np) >= 2:
            entry["rsa"] = {
                "permutation_vs_all_modelled": perm_test(rsa_vec, idx_np, pool_nonpocket, NPERM, random.Random(SEED), False),
                "circular_block_shift": block_shift_test(rsa_vec, vec, [not p for p in is_pocket], False),
            }
            entry["d_pocket"] = {
                "permutation_vs_all_modelled": perm_test(d_vec, idx_np, pool_nonpocket, NPERM, random.Random(SEED + 1), True),
                "circular_block_shift": block_shift_test(d_vec, vec, [not p for p in is_pocket], True),
            }
            # spatial clustering: mean pairwise distance among labelled side-chain centroids, per frame
            obs_mpd, obs_rg = [], []
            for f in frames:
                co = [f["rows"][order[i]]["xyz"] for i in idx_np]
                a, g = spatial_stats(co)
                obs_mpd.append(a); obs_rg.append(g)
            r2 = random.Random(SEED + 2)
            nperm_sp = min(NPERM, 2000)
            null_mpd = []
            f0 = frames[0]
            for _ in range(nperm_sp):
                s = r2.sample(pool_nonpocket, len(idx_np))
                a, g = spatial_stats([f0["rows"][order[i]]["xyz"] for i in s])
                null_mpd.append(a)
            hits = sum(1 for v in null_mpd if v <= mean(obs_mpd))
            entry["spatial_clustering"] = {
                "statistic": "mean pairwise distance (A) between labelled side-chain heavy-atom centroids",
                "observed_mean_over_frames": mean(obs_mpd),
                "observed_sd_over_frames": (sum((v - mean(obs_mpd)) ** 2 for v in obs_mpd) / (len(obs_mpd) - 1)) ** 0.5,
                "observed_radius_of_gyration_A": mean(obs_rg),
                "null_frame": f0["path"], "n_perm": nperm_sp,
                "null_p05": quant(null_mpd, 0.05), "null_p50": quant(null_mpd, 0.5), "null_p95": quant(null_mpd, 0.95),
                "p_one_sided_more_compact": (hits + 1) / (nperm_sp + 1),
            }
        else:
            entry["note"] = "fewer than 2 labelled residues inside the modelled LBD — no statistic computable"
        label_results[name] = entry

    doc = {
        "_title": "UNIQUE-RESIDUE-ADDRESSABILITY-1 — geometry of NR4A3's unique indel residues over the committed conformer ensemble",
        "_lane": "UNIQUE-RESIDUE-ADDRESSABILITY-1",
        "_campaign": "OPUS-CAPACITY-CAMPAIGN-20260908",
        "_date": "2026-09-09",
        "⛔_scope": ("GEOMETRY ONLY. Solvent exposure and pocket proximity are NOT druggability, ligandability, "
                    "selectivity, efficacy, safety or a therapeutic window. No such claim is made or implied. "
                    "No docking, no structure prediction, no new sampling, no GPU."),
        "_boundary_vs_DEGRADER-2": ("DEGRADER-2 scored the three NR4A3-unique CYSTEINES (a reactive residue class) "
                                    "for per-frame RSA only, on all three species' ensembles. This lane scores INDEL "
                                    "residues of every class on the NR4A3 ensemble only, adds a pocket-distance axis, "
                                    "and adds a uniqueness-label permutation null that DEGRADER-2 did not run. "
                                    "No variance decomposition is computed (that is PARALOGUE-SHAPE-1's lane)."),
        "_inputs": {
            "census": {"path": os.path.relpath(CENSUS, REPO), "sha256": sha256(CENSUS), "bytes": os.path.getsize(CENSUS)},
            "sequences": {"path": os.path.relpath(SEQS, REPO), "sha256": sha256(SEQS)},
            "ensemble": {"root": os.path.relpath(ENS, REPO), "n_frames": len(paths),
                         "frames_sha256": {os.path.relpath(p, REPO): sha256(p) for p in paths}},
            "code_reused_unchanged": ["nr4a_differential_atlas.parse_pdb/shrake_rupley/residue_rsa",
                                      "nr4a3_basin_search.load_paralogue (side-chain heavy-atom centroids)",
                                      "nr4a_paralogue_dynamics.construct_frame (offset + homologous pocket)",
                                      "nr4a_paralogue_unique_residues.CRYPTIC_POCKET_UNIPROT"],
        },
        "_method": {
            "rsa": f"Shrake-Rupley, n_points={NPOINTS}, Tien max-ASA normalisation — the committed routine, unchanged.",
            "d_pocket": "distance from each residue's side-chain heavy-atom centroid to the nearest heavy atom of the "
                        "cryptic-pocket residues, in each frame's own coordinates (glycine falls back to CA).",
            "pocket": {"uniprot": list(UNIQ.CRYPTIC_POCKET_UNIPROT),
                       "local_present": frames[0]["pocket_local"], "local_missing": frames[0]["pocket_missing"]},
            "ensemble": "3 replicas x 25 committed unbiased conformers = 75 frames; the biased `metad` subset is excluded, "
                        "exactly as the source ensembles' committed analyses exclude it.",
            "modelled_window_uniprot": [min(uni_of.values()), max(uni_of.values())],
            "local_to_uniprot_offset": off,
            "permutation": "uniqueness-label permutation over the modelled residues (pocket-lining residues excluded from "
                           "both the labelled set and the null pool), plus a circular chain-shift randomisation that "
                           "preserves the contiguous run structure of an indel label.",
            "⚠_convergence": "ASSESS-DEGRADER-2 established that per-frame geometric statistics on this data are "
                             "quadrature-sensitive and that maximum-based ceilings grow with sampling. Distributional "
                             "statements and permutation ranks are reported in preference to exact integers; see "
                             "resolution_floor.",
        },
        "indel_census_used": {
            "n_nr4a3_present_runs_nonterminal": len(runs),
            "n_indel_residues_total": len(indel_by_res),
            "n_indel_residues_inside_modelled_lbd": sum(1 for u in indel_by_res if min(uni_of.values()) <= u <= max(uni_of.values())),
            "runs": runs,
        },
        "per_residue": {str(uni_of[r]): dict(per_res[r], **{
            "is_indel": uni_of[r] in indel_by_res,
            "indel": indel_by_res.get(uni_of[r]),
            "is_unique_robust_substitution": (uni_of[r] in subst and not subst[uni_of[r]]["gap_partner"]),
            "is_pocket_lining": uni_of[r] in pocket_uni,
        }) for r in order},
        "label_tests": label_results,
        "n_frames": len(frames),
        "runtime_s": round(time.time() - t0, 1),
    }
    json.dump(doc, open(OUT, "w"), indent=1)
    print(f"[lane] wrote {OUT} ({os.path.getsize(OUT)} B) in {doc['runtime_s']}s", flush=True)
    for k, v in label_results.items():
        if "rsa" in v:
            print(f"  {k}: n={v['n_labelled_in_modelled_lbd']} "
                  f"RSA obs={v['rsa']['permutation_vs_all_modelled']['observed']:.3f} "
                  f"null={v['rsa']['permutation_vs_all_modelled']['null_p50']:.3f} p={v['rsa']['permutation_vs_all_modelled']['p_one_sided']:.4f} | "
                  f"d obs={v['d_pocket']['permutation_vs_all_modelled']['observed']:.2f} "
                  f"null={v['d_pocket']['permutation_vs_all_modelled']['null_p50']:.2f} p={v['d_pocket']['permutation_vs_all_modelled']['p_one_sided']:.4f} | "
                  f"mpd={v['spatial_clustering']['observed_mean_over_frames']:.2f} "
                  f"null={v['spatial_clustering']['null_p50']:.2f} p={v['spatial_clustering']['p_one_sided_more_compact']:.4f}")
        else:
            print(f"  {k}: n={v['n_labelled_in_modelled_lbd']} — {v.get('note')}")


if __name__ == "__main__":
    _init()
    main()
