#!/usr/bin/env python3
"""PER-FRAME cysteine RSA over the committed NR4A1/NR4A2/NR4A3 unbiased release ensembles.

WHY. `research/modalities/nr4a-paralogue-dynamics.json` publishes only QUANTILE SUMMARIES of the
per-cysteine RSA (n/min/p10/median/p90/max/mean/sd) per species per ensemble. Every exposure figure
quoted downstream — the pooled paralogue ceiling 0.2126, C397's pooled p10 0.298 / median 0.416, and
the first-round per-replica margins — is therefore read off quantiles, and NO exact frame-level
overlap fraction between NR4A3's unique cysteines and the paralogue cysteines has ever been computed.
This module recomputes RSA FRAME BY FRAME from the same committed conformers with the same committed
routine, reproduces the published quantiles as its validation, and then answers the overlap question
exactly.

WHAT IT DOES NOT DO. No sampling, no docking, no structure prediction, no network, no GPU. It reuses
`nr4a_differential_atlas.parse_pdb / shrake_rupley / residue_rsa` and
`nr4a_paralogue_dynamics.construct_frame / cysteines_of` unchanged; the term-(a) reach envelope
(the expensive Monte-Carlo part) is NOT recomputed and nothing here touches it.

SCOPE. RSA is a geometric quantity on MD conformers. Nothing here bears on thiol pKa,
nucleophilicity, adduct stability, promiscuity, degradation, cellular selectivity, efficacy, safety,
therapeutic window or clinical readiness. There is no wet lab.
"""
from __future__ import annotations

import json
import math
import os
import sys
from multiprocessing import Pool

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "research", "modalities"))

import nr4a_differential_atlas as ATLAS          # noqa: E402
import nr4a_paralogue_dynamics as D              # noqa: E402
import nr4a3_basin_search as B                   # noqa: E402

COMMITTED = os.path.join(REPO, "research", "modalities", "nr4a-paralogue-dynamics.json")
REPLICAS = ("release_rep0", "release_rep1", "release_rep2")
NR4A3_UNIQUE = ("C397", "C420", "C559")
OUT = os.path.join(os.path.dirname(__file__), "artifacts", "per-frame-rsa-overlap.json")


def frame_paths(species, subdir):
    d = os.path.join(D.ENSEMBLE_ROOT[species], subdir)
    if not os.path.isdir(d):
        return []
    out = []
    for name in sorted(os.listdir(d)):
        p = os.path.join(d, name, "frame.pdb")
        if os.path.isfile(p):
            out.append((name, p))
    return out


_CTX = {}


def _init():
    seqs = json.load(open(D.SEQ_CACHE))
    ref = B.load_paralogue(D.STATIC_MODEL["NR4A3"])
    u = json.load(open(D.UNIQUE_JSON))
    _CTX["seqs"] = seqs
    _CTX["ref"] = ref
    _CTX["ref_aa_of"] = ref["aa_of"]
    _CTX["ref_pocket_local"] = [x - B.UNIPROT_OFFSET for x in u["cryptic_pocket_uniprot"]]


def _one(job):
    species, ensemble, frame, path = job
    model = B.load_paralogue(path)
    residues, atoms = ATLAS.parse_pdb(path)                     # with H — the committed convention
    rsa = ATLAS.residue_rsa(residues, ATLAS.shrake_rupley(atoms))
    off, _pocket, _missing = D.construct_frame(model, species, _CTX["seqs"], _CTX["ref"],
                                               _CTX["ref_pocket_local"])
    cys = D.cysteines_of(model, off, _CTX["ref"], _CTX["ref_aa_of"])
    return {"species": species, "ensemble": ensemble, "frame": frame,
            "cys": {c["label"]: round(rsa.get(c["local_resid"], 0.0), 4) for c in cys}}


def main():
    jobs = []
    for sp in D.SPECIES:
        for rep in REPLICAS:
            for frame, path in frame_paths(sp, rep):
                jobs.append((sp, rep, frame, path))
    print(f"[pf] {len(jobs)} frames", flush=True)
    with Pool(4, initializer=_init) as pool:
        rows = pool.map(_one, jobs, chunksize=4)
    rows.sort(key=lambda r: (r["species"], r["ensemble"], r["frame"]))

    # ---------- validation: reproduce the committed per-ensemble quantiles exactly ----------
    committed = json.load(open(COMMITTED))["term_a"]["by_species"]
    checks, mismatches = 0, []
    for sp in D.SPECIES:
        for rep in REPLICAS:
            cells = [r for r in rows if r["species"] == sp and r["ensemble"] == rep]
            pub = committed[sp]["ensembles"][rep]["summary"]
            labs = sorted({lab for r in cells for lab in r["cys"]})
            for lab in labs:
                mine = D.quantiles([r["cys"][lab] for r in cells if lab in r["cys"]])
                theirs = pub.get(lab, {}).get("rsa")
                if theirs is None:
                    mismatches.append({"species": sp, "ensemble": rep, "cys": lab,
                                       "problem": "absent from committed artifact"})
                    continue
                for k in ("n", "min", "p10", "median", "p90", "max", "mean", "sd"):
                    checks += 1
                    if abs(float(mine[k]) - float(theirs[k])) > 1e-9:
                        mismatches.append({"species": sp, "ensemble": rep, "cys": lab, "stat": k,
                                           "recomputed": mine[k], "committed": theirs[k]})

    # ---------- exact frame-level overlap ----------
    def para_frames(rep):
        """(label, rsa) for every NR4A1/NR4A2 cysteine in every frame of `rep`."""
        out = []
        for r in rows:
            if r["species"] in ("NR4A1", "NR4A2") and r["ensemble"] == rep:
                for lab, v in r["cys"].items():
                    out.append((f"{r['species']}:{lab}@{r['frame']}", v))
        return out

    def nr4a3_frames(lab, rep):
        return [r["cys"][lab] for r in rows
                if r["species"] == "NR4A3" and r["ensemble"] == rep and lab in r["cys"]]

    per_replica = {}
    for rep in REPLICAS:
        pf = para_frames(rep)
        ceil_lab, ceil = max(pf, key=lambda t: t[1])
        vals = [v for _, v in pf]
        row = {"n_paralogue_cys_frame_observations": len(pf),
               "paralogue_ceiling": round(ceil, 4), "paralogue_ceiling_source": ceil_lab}
        for lab in NR4A3_UNIQUE:
            xs = nr4a3_frames(lab, rep)
            above = sum(1 for x in xs if x > ceil)
            dom = sum(1 for x in xs for v in vals if x > v)
            row[lab] = {
                "n_frames": len(xs),
                "n_frames_above_replica_paralogue_ceiling": above,
                "frac_frames_above_replica_paralogue_ceiling": round(above / len(xs), 4) if xs else None,
                "exact_pairwise_dominance": round(dom / (len(xs) * len(vals)), 4) if xs and vals else None,
                "min": round(min(xs), 4) if xs else None,
                "median": D.quantiles(xs).get("median") if xs else None,
            }
        per_replica[rep] = row

    pooled_pf = [t for rep in REPLICAS for t in para_frames(rep)]
    pooled_vals = [v for _, v in pooled_pf]
    pooled_ceil_lab, pooled_ceil = max(pooled_pf, key=lambda t: t[1])
    pooled = {"n_paralogue_cys_frame_observations": len(pooled_pf),
              "paralogue_ceiling": round(pooled_ceil, 4),
              "paralogue_ceiling_source": pooled_ceil_lab}
    for lab in NR4A3_UNIQUE:
        xs = [x for rep in REPLICAS for x in nr4a3_frames(lab, rep)]
        above = sum(1 for x in xs if x > pooled_ceil)
        dom = sum(1 for x in xs for v in pooled_vals if x > v)
        pooled[lab] = {"n_frames": len(xs),
                       "n_frames_above_pooled_paralogue_ceiling": above,
                       "frac_frames_above_pooled_paralogue_ceiling": round(above / len(xs), 4),
                       "exact_pairwise_dominance": round(dom / (len(xs) * len(pooled_vals)), 4),
                       "quantiles": D.quantiles(xs)}

    # cross-replica worst case: NR4A3 replica i against paralogue replica j
    cross = {}
    for ri in REPLICAS:
        for rj in REPLICAS:
            pf = para_frames(rj)
            ceil = max(v for _, v in pf)
            xs = nr4a3_frames("C397", ri)
            above = sum(1 for x in xs if x > ceil)
            cross[f"C397@{ri} vs ceiling@{rj}"] = {
                "ceiling": round(ceil, 4), "n_frames": len(xs),
                "frac_frames_above": round(above / len(xs), 4) if xs else None}

    # the failed positive control, per replica, per frame
    c551 = {}
    for rep in REPLICAS:
        xs = [r["cys"]["C551"] for r in rows
              if r["species"] == "NR4A1" and r["ensemble"] == rep and "C551" in r["cys"]]
        c551[rep] = {"n_frames": len(xs), "max": round(max(xs), 4) if xs else None,
                     "quantiles": D.quantiles(xs),
                     "n_frames_above_replica_paralogue_ceiling":
                         sum(1 for x in xs if x > per_replica[rep]["paralogue_ceiling"])}

    res = {
        "_title": "Per-frame cysteine RSA and EXACT overlap fractions — NR4A1/NR4A2/NR4A3 unbiased release ensembles",
        "_status": ("DESIGN PREP. Geometric exposure only. Nothing here is a claim about binding, "
                    "reactivity, degradation, selectivity in cells, efficacy, safety, therapeutic "
                    "window or clinical readiness. No wet lab."),
        "_inputs": {
            "conformers": {sp: os.path.relpath(D.ENSEMBLE_ROOT[sp], REPO) for sp in D.SPECIES},
            "subsets": list(REPLICAS),
            "biased_metad_excluded": True,
            "committed_artifact_for_validation": os.path.relpath(COMMITTED, REPO),
            "rsa_routine": "nr4a_differential_atlas.shrake_rupley (n_points=96) / Tien max-ASA, hydrogens kept",
        },
        "validation_against_committed_quantiles": {
            "_what": ("every per-species per-replica per-cysteine RSA quantile block in the committed "
                      "artifact, recomputed from the frames and compared exactly"),
            "n_statistics_compared": checks,
            "n_mismatches": len(mismatches),
            "mismatches": mismatches,
            "reproduces": not mismatches,
        },
        "per_replica_exact_overlap": per_replica,
        "pooled_exact_overlap": pooled,
        "cross_replica_C397": cross,
        "positive_control_NR4A1_C551": c551,
        "per_frame_rsa": rows,
        "_limits": [
            "Exposure (RSA) is necessary, not sufficient, for covalent targeting; no chemistry is tested.",
            "Release ensembles are biased-CV-released MD, not Boltzmann-weighted: frame fractions are "
            "heterogeneity statements, not populations.",
            "Replica indices are not physically paired across species; the cross-replica block is "
            "reported because the pairing is arbitrary.",
            "The paralogue ceiling is a max over frame observations and grows with sample size; the "
            "exact pairwise dominance statistic is reported alongside it for that reason.",
            "25 frames per species per replica — small-sample fractions.",
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(res, fh, indent=1)
        fh.write("\n")
    print(f"[pf] validation: {checks} statistics compared, {len(mismatches)} mismatches", flush=True)
    for rep in REPLICAS:
        r = per_replica[rep]
        print(f"[pf] {rep}: ceiling {r['paralogue_ceiling']} ({r['paralogue_ceiling_source']}) "
              f"C397 above {r['C397']['n_frames_above_replica_paralogue_ceiling']}/{r['C397']['n_frames']} "
              f"dominance {r['C397']['exact_pairwise_dominance']}", flush=True)
    print(f"[pf] pooled ceiling {pooled['paralogue_ceiling']} ({pooled['paralogue_ceiling_source']}); "
          f"C397 above {pooled['C397']['n_frames_above_pooled_paralogue_ceiling']}/{pooled['C397']['n_frames']}",
          flush=True)
    print(f"[pf] wrote {os.path.relpath(OUT, REPO)}", flush=True)
    return 0 if not mismatches else 3


if __name__ == "__main__":
    sys.exit(main())
