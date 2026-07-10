#!/usr/bin/env python3
"""AF2↔NMR vs NMR↔NMR Cα-RMSD decomposition (review P1 20).

Reviewer's question (§2.2): is the AF2 NR4A3-LBD working model a legitimate member of the experimental
conformational ensemble, or a structural outlier — overall and at the cryptic pocket? We answer it by
comparing two RMSD distributions on the 8XTT NMR ensemble:
  * AF2↔NMR  — RMSD of the AF2 model to EACH 8XTT NMR model (after Kabsch superposition),
  * NMR↔NMR  — RMSD between every PAIR of 8XTT NMR models (the ensemble's OWN internal spread),
each computed over (i) all shared Cα and (ii) the Pocket-5 lining Cα only. If AF2↔NMR is within the
NMR↔NMR spread, AF2 is "as close to the NMR structures as they are to each other" — a valid ensemble
member; if AF2↔NMR ≫ NMR↔NMR, it is an outlier (report honestly, overall and at the pocket).

Pure numeric core (kabsch_rmsd, parse_ca_models, rmsd_over_residues, summarize) is unit-tested (numpy only,
no mdtraj/biopython). Structure fetch + the job run in af2-nmr-rmsd-aws.yml (ubuntu CPU; RCSB/AFDB reachable
there). Output: nr4a3-af2-nmr-rmsd.json.
"""
from __future__ import annotations

import json
import os

# NR4A3 UniProt Q92570; 8XTT = experimental NR4A3-LBD NMR ensemble. Pocket-5 lining (UniProt numbering).
AF2_ACC = "Q92570"
NMR_PDB = "8XTT"
POCKET5 = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "nr4a3-af2-nmr-rmsd.json")


# ------------------------- pure, unit-tested core (numpy only) -------------------------

def kabsch_rmsd(P, Q):
    """Minimum Cα-RMSD between coordinate sets P and Q (each (N,3)) after optimal Kabsch superposition
    (rotation + translation; reflection-corrected). Pure (numpy)."""
    import numpy as np
    P = np.asarray(P, float); Q = np.asarray(Q, float)
    if P.shape != Q.shape or P.ndim != 2 or P.shape[1] != 3 or P.shape[0] < 1:
        raise ValueError("P and Q must be equal (N,3) with N>=1")
    Pc = P - P.mean(0); Qc = Q - Q.mean(0)
    H = Qc.T @ Pc
    U, S, Vt = np.linalg.svd(H)
    d = 1.0 if np.linalg.det(Vt.T @ U.T) >= 0 else -1.0
    R = Vt.T @ np.diag([1.0, 1.0, d]) @ U.T           # rotates Qc onto Pc
    diff = Pc - Qc @ R.T
    return float(np.sqrt((diff * diff).sum() / P.shape[0]))


def parse_ca_models(pdb_text):
    """Parse a PDB (possibly multi-MODEL NMR ensemble) into a list of models, each {resSeq(int): (x,y,z)}
    for Cα atoms of the first chain encountered. Pure (stdlib). A single-model file -> a 1-element list."""
    models = []
    cur = {}
    started = False
    for line in pdb_text.splitlines():
        rec = line[:6].strip()
        if rec == "MODEL":
            cur = {}; started = True
        elif rec == "ENDMDL":
            models.append(cur); cur = {}; started = False
        elif rec == "ATOM" and line[12:16].strip() == "CA" and line[16] in (" ", "A"):
            try:
                rs = int(line[22:26]); x = float(line[30:38]); y = float(line[38:46]); z = float(line[46:54])
            except ValueError:
                continue
            cur.setdefault(rs, (x, y, z))              # first altloc/chain wins
    if cur or not models:
        models.append(cur)                             # trailing single model (no MODEL/ENDMDL records)
    return [m for m in models if m]


def rmsd_over_residues(model_a, model_b, resseqs):
    """Kabsch RMSD between two {resSeq:(x,y,z)} models over the residues in `resseqs` that BOTH contain.
    Returns (rmsd, n_used). Pure."""
    import numpy as np
    common = [r for r in resseqs if r in model_a and r in model_b]
    if len(common) < 3:
        return None, len(common)
    P = np.array([model_a[r] for r in common], float)
    Q = np.array([model_b[r] for r in common], float)
    return kabsch_rmsd(P, Q), len(common)


def summarize(values):
    """min/mean/max of a list of floats (ignoring None); {} if empty. Pure."""
    xs = [v for v in values if v is not None]
    if not xs:
        return {}
    return {"n": len(xs), "min": round(min(xs), 3), "mean": round(sum(xs) / len(xs), 3),
            "max": round(max(xs), 3)}


def decompose(af2_model, nmr_models, all_resseqs, pocket_resseqs):
    """Build the AF2↔NMR and NMR↔NMR RMSD distributions over the all-Cα set and the pocket-Cα set, plus the
    verdict (is AF2↔NMR within the NMR↔NMR spread?). Pure — takes already-parsed models."""
    def dists(region):
        a2n = [rmsd_over_residues(af2_model, m, region)[0] for m in nmr_models]
        n2n = [rmsd_over_residues(nmr_models[i], nmr_models[j], region)[0]
               for i in range(len(nmr_models)) for j in range(i + 1, len(nmr_models))]
        return summarize(a2n), summarize(n2n)
    out = {}
    for label, region in (("all_ca", all_resseqs), ("pocket_ca", pocket_resseqs)):
        a2n, n2n = dists(region)
        within = (bool(a2n) and bool(n2n) and a2n["mean"] <= n2n["max"])
        out[label] = {"af2_to_nmr": a2n, "nmr_to_nmr": n2n,
                      "af2_within_nmr_spread": within,
                      "_verdict": ("AF2 is within the NMR ensemble spread"
                                   if within else "AF2 mean exceeds the NMR internal spread (outlier)")}
    return out


# ------------------------- job (fetch + run; ubuntu CPU) -------------------------

def _fetch(url):
    import urllib.request
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def _fetch_af2(acc):
    import urllib.request
    try:
        meta = json.loads(_fetch(f"https://alphafold.ebi.ac.uk/api/prediction/{acc}"))
        u = (meta[0] or {}).get("pdbUrl") if meta else None
        if u:
            return _fetch(u)
    except Exception:  # noqa: BLE001
        pass
    for v in ("v6", "v5", "v4", "v3", "v2", "v1"):
        try:
            return _fetch(f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_{v}.pdb")
        except urllib.error.HTTPError:
            continue
    raise RuntimeError(f"could not fetch AlphaFold model for {acc}")


def main():
    af2_txt = _fetch_af2(AF2_ACC)
    nmr_txt = _fetch(f"https://files.rcsb.org/download/{NMR_PDB}.pdb")
    af2 = parse_ca_models(af2_txt)[0]
    nmr = parse_ca_models(nmr_txt)
    if len(nmr) < 2:
        raise RuntimeError(f"{NMR_PDB} parsed {len(nmr)} model(s); need an NMR ensemble (>=2 models)")
    # all shared residues = those present in AF2 and in EVERY NMR model (a common frame for a fair RMSD)
    common = set(af2)
    for m in nmr:
        common &= set(m)
    all_resseqs = sorted(common)
    pocket_resseqs = [r for r in POCKET5 if r in common]
    res = decompose(af2, nmr, all_resseqs, pocket_resseqs)
    out = {"_title": "AF2 vs 8XTT-NMR Cα-RMSD decomposition (review P1 20)",
           "_method": "Kabsch Cα-RMSD; AF2-to-each-NMR-model vs NMR-model-to-model, over all shared Cα and "
                      "Pocket-5 Cα; AF2 counts as an ensemble member if its mean RMSD <= the NMR internal max.",
           "af2_acc": AF2_ACC, "nmr_pdb": NMR_PDB, "n_nmr_models": len(nmr),
           "n_all_ca_shared": len(all_resseqs), "pocket5_shared": pocket_resseqs, "results": res}
    json.dump(out, open(OUT, "w"), indent=2)
    for label, r in res.items():
        print(f"{label}: AF2->NMR {r['af2_to_nmr']} | NMR->NMR {r['nmr_to_nmr']} | {r['_verdict']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
