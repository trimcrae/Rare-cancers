#!/usr/bin/env python3
"""DEGRADER-3 independent re-derivation of DEGRADER-2's two load-bearing numbers.

Recomputes per-frame cysteine RSA over the 225 committed unbiased release conformers with the
committed Shrake-Rupley routine, then computes ONLY:
  (1) how many of C397's 75 frames lie strictly above the pooled paralogue ceiling (claim: 72/75),
      and which replica the exceptions are in (claim: all in release_rep0);
  (2) exact pairwise dominance of C397 over the 825 NR4A1/NR4A2 cysteine-by-frame observations
      (claim: 0.9993);
  (3) the worst cross-replica pairing fraction (claim: 0.88).
No sampling, no docking, no network, no GPU. RSA is geometric only.
"""
from __future__ import annotations
import hashlib, json, os, sys
from multiprocessing import Pool

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "research", "modalities"))
import nr4a_differential_atlas as ATLAS   # noqa: E402
import nr4a_paralogue_dynamics as D       # noqa: E402
import nr4a3_basin_search as B            # noqa: E402

REPLICAS = ("release_rep0", "release_rep1", "release_rep2")
_CTX = {}

def _init():
    ref = B.load_paralogue(D.STATIC_MODEL["NR4A3"])
    u = json.load(open(D.UNIQUE_JSON))
    _CTX.update(seqs=json.load(open(D.SEQ_CACHE)), ref=ref, ref_aa_of=ref["aa_of"],
                pocket=[x - B.UNIPROT_OFFSET for x in u["cryptic_pocket_uniprot"]])

def _one(job):
    sp, rep, frame, path = job
    model = B.load_paralogue(path)
    residues, atoms = ATLAS.parse_pdb(path)
    rsa = ATLAS.residue_rsa(residues, ATLAS.shrake_rupley(atoms))
    off, _p, _m = D.construct_frame(model, sp, _CTX["seqs"], _CTX["ref"], _CTX["pocket"])
    cys = D.cysteines_of(model, off, _CTX["ref"], _CTX["ref_aa_of"])
    return {"species": sp, "ensemble": rep, "frame": frame,
            "cys": {c["label"]: round(rsa.get(c["local_resid"], 0.0), 4) for c in cys},
            "sha256_frame_pdb": hashlib.sha256(open(path, "rb").read()).hexdigest()}

def main():
    jobs = []
    for sp in D.SPECIES:
        for rep in REPLICAS:
            d = os.path.join(D.ENSEMBLE_ROOT[sp], rep)
            if not os.path.isdir(d):
                continue
            for name in sorted(os.listdir(d)):
                p = os.path.join(d, name, "frame.pdb")
                if os.path.isfile(p):
                    jobs.append((sp, rep, name, p))
    print(f"[rederive] {len(jobs)} frames", flush=True)
    with Pool(4, initializer=_init) as pool:
        rows = pool.map(_one, jobs, chunksize=4)
    rows.sort(key=lambda r: (r["species"], r["ensemble"], r["frame"]))

    para = [(r["ensemble"], f"{r['species']}:{lab}@{r['frame']}", v)
            for r in rows if r["species"] in ("NR4A1", "NR4A2") for lab, v in r["cys"].items()]
    c397 = [(r["ensemble"], r["frame"], r["cys"]["C397"])
            for r in rows if r["species"] == "NR4A3" and "C397" in r["cys"]]

    ceiling = max(v for _, _, v in para)
    ceil_who = [lab for _, lab, v in para if v == ceiling]
    above = [(rep, fr, v) for rep, fr, v in c397 if v > ceiling]
    below = [(rep, fr, v) for rep, fr, v in c397 if v <= ceiling]
    dom = sum(1 for _, _, a in c397 for _, _, b in para if a > b) / (len(c397) * len(para))

    per_rep_ceiling = {rep: max(v for e, _, v in para if e == rep) for rep in REPLICAS}
    cross = {}
    for cr in REPLICAS:
        vals = [v for e, _, v in c397 if e == cr]
        for pr in REPLICAS:
            n = sum(1 for v in vals if v > per_rep_ceiling[pr])
            cross[f"C397@{cr}_vs_ceiling@{pr}"] = {"n_above": n, "n": len(vals),
                                                   "fraction": round(n / len(vals), 4)}
    worst = min(cross.items(), key=lambda kv: kv[1]["fraction"])

    out = {
        "_what": "DEGRADER-3 independent re-derivation of DEGRADER-2's 72/75, 0.9993 and 0.88",
        "_scope_ceiling": ("RSA is geometric. Nothing here is an EMC efficacy, safety, selectivity, "
                           "therapeutic-window or clinical-readiness claim. No wet lab."),
        "n_frames": len(rows),
        "n_c397_frames": len(c397),
        "n_paralogue_observations": len(para),
        "pooled_paralogue_ceiling": ceiling,
        "pooled_paralogue_ceiling_attribution": ceil_who,
        "c397_frames_strictly_above_pooled_ceiling": {
            "n_above": len(above), "n": len(c397),
            "fraction": round(len(above) / len(c397), 4),
            "exceptions": sorted(below, key=lambda t: t[2]),
        },
        "c397_pairwise_dominance_vs_paralogue_observations": round(dom, 4),
        "per_replica_paralogue_ceiling": per_rep_ceiling,
        "cross_replica_pairings": cross,
        "worst_cross_replica_pairing": {"pairing": worst[0], **worst[1]},
        "degrader2_claims": {"72/75": len(above) == 72 and len(c397) == 75,
                             "exceptions_all_release_rep0": all(r == "release_rep0" for r, _, _ in below),
                             "dominance_0.9993": round(dom, 4) == 0.9993,
                             "worst_cross_replica_0.88": worst[1]["fraction"] == 0.88},
        "frames": rows,
    }
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts",
                       "rederivation-degrader2-numbers.json")
    json.dump(out, open(dst, "w"), indent=2)
    print(json.dumps({k: v for k, v in out.items() if k != "frames"}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
