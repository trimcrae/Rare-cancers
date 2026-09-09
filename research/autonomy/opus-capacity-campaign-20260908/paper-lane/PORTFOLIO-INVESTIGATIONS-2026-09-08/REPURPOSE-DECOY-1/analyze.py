#!/usr/bin/env python3
"""REPURPOSE-DECOY-1: is the shortlist separable from property-matched decoys?

Read-only. Scores only already-computed, committed docking / MM-GBSA numbers.
Docking scores are NOT affinities and NOT efficacy; nothing here supports any
efficacy, safety, selectivity-in-cells or clinical claim about any drug.
"""
import hashlib, json, os, random, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
def R(p): return os.path.join(ROOT, p)

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest(), os.path.getsize(p)

INPUTS = [
    "research/modalities/nr4a3-repurpose-candidates.json",
    "research/modalities/property_matched_control.py",
    "research/modalities/repurpose_dock_core.py",
    "research/modalities/decoy_library.py",
    "research/modalities/_reports/nr4a3-repurpose-fm-report.txt",
    "results/nr4a3-matrix/nr4a3-matrix.json",
    "results/nr4a3-matrix/candidates.sdf",
    "results/nr4a3-decoy/MANIFEST.json",
    "results/nr4a3-decoy/-matrix/nr4a3-matrix.json",
    "results/nr4a3-decoy/-matrix/candidates.sdf",
    "results/nr4a3-decoy/-mmgbsa/nr4a3-mmgbsa.json",
    "results/nr4a3-decoy/-mmgbsa-ms/nr4a3-mmgbsa.json",
    "results/nr4a3-genmatched-scramble-mmgbsa/nr4a3-mmgbsa.json",
    "results/nr4a3-generation-matched-null/nr4a3-generation-matched-null.json",
    "results/nr4a3-genmatched-control-c/nr4a3-release-druggable.json",
]
prov = {}
for p in INPUTS:
    d, n = sha(R(p))
    prov[p] = {"sha256": d, "bytes": n}

# ---------- statistics (no scipy dependency for the core numbers) ----------
def auc(pos, neg):
    """P(random positive scores better than random negative); ties = 0.5.
    Inputs already oriented so LARGER = better."""
    n = 0.0
    for a in pos:
        for b in neg:
            n += 1.0 if a > b else (0.5 if a == b else 0.0)
    return n / (len(pos) * len(neg))

def perm_p(pos, neg, iters=20000, seed=0):
    """Two-sided permutation p on AUC (label shuffle)."""
    rng = random.Random(seed)
    obs = abs(auc(pos, neg) - 0.5)
    all_v = list(pos) + list(neg)
    k = len(pos)
    hit = 0
    for _ in range(iters):
        rng.shuffle(all_v)
        if abs(auc(all_v[:k], all_v[k:]) - 0.5) >= obs - 1e-12:
            hit += 1
    return (hit + 1) / (iters + 1)

def boot_ci(pos, neg, iters=4000, seed=1):
    rng = random.Random(seed)
    vals = []
    for _ in range(iters):
        p = [rng.choice(pos) for _ in pos]
        n = [rng.choice(neg) for _ in neg]
        vals.append(auc(p, n))
    vals.sort()
    return [round(vals[int(0.025 * iters)], 4), round(vals[int(0.975 * iters) - 1], 4)]

def ef(pos, neg, frac):
    """Enrichment factor at top `frac` of the pooled ranking."""
    pool = [(v, 1) for v in pos] + [(v, 0) for v in neg]
    pool.sort(key=lambda t: -t[0])
    k = max(1, int(round(frac * len(pool))))
    top = sum(t[1] for t in pool[:k])
    base = len(pos) / len(pool)
    return {"frac": frac, "n_top": k, "n_actives_in_top": top,
            "EF": round((top / k) / base, 3)}

# ---------- load committed score sets ----------
mat = json.load(open(R("results/nr4a3-matrix/nr4a3-matrix.json")))
dec = json.load(open(R("results/nr4a3-decoy/-matrix/nr4a3-matrix.json")))
short = mat["candidates"]
decs = dec["candidates"]

def sdf_smiles(path):
    from rdkit import Chem
    out = {}
    for m in Chem.SDMolSupplier(path, removeHs=True, sanitize=True):
        if m is None:
            continue
        out[m.GetProp("_Name")] = Chem.MolToSmiles(m)
    return out

s_smi = sdf_smiles(R("results/nr4a3-matrix/candidates.sdf"))
d_smi = sdf_smiles(R("results/nr4a3-decoy/-matrix/candidates.sdf"))

from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, Lipinski, rdMolDescriptors

def props(smiles):
    m = Chem.MolFromSmiles(smiles)
    return {"MW": round(Descriptors.MolWt(m), 2), "cLogP": round(Crippen.MolLogP(m), 3),
            "HA": m.GetNumHeavyAtoms(), "arom_rings": Lipinski.NumAromaticRings(m),
            "TPSA": round(rdMolDescriptors.CalcTPSA(m), 2),
            "rotb": Lipinski.NumRotatableBonds(m),
            "HBD": Lipinski.NumHDonors(m), "HBA": Lipinski.NumHAcceptors(m)}

def rows(cands, smi):
    out = []
    for c in cands:
        lab = c["label"]
        s = smi.get(lab)
        r = {"label": lab, "dG_NR4A3": c["dG"]["NR4A3"],
             "dG_NR4A1": c["dG"]["NR4A1"], "dG_NR4A2": c["dG"]["NR4A2"],
             "dock_min_margin": round(min(c["margin_vs_NR4A1"], c["margin_vs_NR4A2"]), 4),
             "smiles": s}
        if s:
            r.update(props(s))
        out.append(r)
    return out

S = rows(short, s_smi)
D = rows(decs, d_smi)
missing = [r["label"] for r in S + D if not r.get("smiles")]

# ---------- 1. property match audit ----------
def mwu_p(a, b, seed=7):
    return round(perm_p(a, b, 10000, seed), 5)

prop_audit = {}
for k in ["MW", "cLogP", "HA", "arom_rings", "TPSA", "rotb", "HBD", "HBA"]:
    a = [r[k] for r in S if k in r]
    b = [r[k] for r in D if k in r]
    prop_audit[k] = {
        "shortlist_median": round(sorted(a)[len(a) // 2], 3),
        "decoy_median": round(sorted(b)[len(b) // 2], 3),
        "shortlist_range": [min(a), max(a)], "decoy_range": [min(b), max(b)],
        "AUC_property_separates": round(auc(a, b), 4),
        "perm_p": mwu_p(a, b),
    }

# ---------- 2. docking separability, full decoy set ----------
sc = lambda rs, key: [-r[key] if key.startswith("dG") else r[key] for r in rs]
res = {}
for key, label in [("dG_NR4A3", "NR4A3 docking score (more negative = better)"),
                   ("dock_min_margin", "docking selectivity margin vs paralogues")]:
    pos, neg = sc(S, key), sc(D, key)
    res[key] = {"metric": label, "n_shortlist": len(pos), "n_decoy": len(neg),
                "AUC": round(auc(pos, neg), 4), "AUC_95CI_boot": boot_ci(pos, neg),
                "perm_p": round(perm_p(pos, neg), 5),
                "EF": [ef(pos, neg, f) for f in (0.05, 0.10, 0.20)]}

# ---------- 3. property-only null scorers ----------
prop_auc = {}
for k in ["MW", "HA", "cLogP", "arom_rings", "TPSA"]:
    pos = [r[k] for r in S if k in r]
    neg = [r[k] for r in D if k in r]
    prop_auc[k] = {"AUC_as_scorer": round(auc(pos, neg), 4),
                   "perm_p": round(perm_p(pos, neg, 10000, 11), 5)}

# ---------- 4. property-matched decoy subset ----------
PAD = {"MW": 25.0, "cLogP": 0.5, "arom_rings": 1}
lo_mw, hi_mw = min(r["MW"] for r in S) - PAD["MW"], max(r["MW"] for r in S) + PAD["MW"]
lo_lp, hi_lp = min(r["cLogP"] for r in S) - PAD["cLogP"], max(r["cLogP"] for r in S) + PAD["cLogP"]
hi_ar = max(r["arom_rings"] for r in S) + PAD["arom_rings"]
lo_ar = max(0, min(r["arom_rings"] for r in S) - PAD["arom_rings"])
Dm = [r for r in D if lo_mw <= r["MW"] <= hi_mw and lo_lp <= r["cLogP"] <= hi_lp
      and lo_ar <= r["arom_rings"] <= hi_ar]
matched = {"envelope": {"MW": [round(lo_mw, 1), round(hi_mw, 1)],
                        "cLogP": [round(lo_lp, 2), round(hi_lp, 2)],
                        "arom_rings": [lo_ar, hi_ar]},
           "pad": PAD, "n_decoys_in_envelope": len(Dm),
           "labels": [r["label"] for r in Dm]}
if len(Dm) >= 3:
    for key in ["dG_NR4A3", "dock_min_margin"]:
        pos, neg = sc(S, key), sc(Dm, key)
        matched[key] = {"AUC": round(auc(pos, neg), 4), "AUC_95CI_boot": boot_ci(pos, neg),
                        "perm_p": round(perm_p(pos, neg), 5)}
else:
    matched["note"] = "too few decoys inside the shortlist property envelope for a stable AUC"

# ---------- 5. REQUIRED CHECK: generation-matched scramble must land at chance ----------
scr = json.load(open(R("results/nr4a3-genmatched-scramble-mmgbsa/nr4a3-mmgbsa.json")))["candidates"]
dms = json.load(open(R("results/nr4a3-decoy/-mmgbsa-ms/nr4a3-mmgbsa.json")))["candidates"]
dss = json.load(open(R("results/nr4a3-decoy/-mmgbsa/nr4a3-mmgbsa.json")))["candidates"]

def mmr(cands, key):
    """Drop rows whose MM-GBSA value is null (an unscored/failed row is not a zero)."""
    if key == "mm_min_margin":
        v = [c.get("mm_min_margin") for c in cands]
    else:
        v = [(-c["dG_mmgbsa"]["NR4A3"] if (c.get("dG_mmgbsa") or {}).get("NR4A3") is not None else None)
             for c in cands]
    return [x for x in v if x is not None], sum(1 for x in v if x is None)

chance = {}
for dname, dset, note in [("decoy_multisnapshot", dms, "10-frame MD average, same MM-GBSA scheme as the scramble set"),
                          ("decoy_singlesnapshot", dss, "single-snapshot; scheme MISMATCHED to the scramble set")]:
    for key in ["mm_min_margin", "dG_mmgbsa_NR4A3"]:
        (pos, np_drop), (neg, nn_drop) = mmr(scr, key), mmr(dset, key)
        chance[f"scramble_vs_{dname}::{key}"] = {
            "comparator_note": note, "n_scramble": len(pos), "n_decoy": len(neg),
            "n_scramble_rows_dropped_null": np_drop, "n_decoy_rows_dropped_null": nn_drop,
            "AUC": round(auc(pos, neg), 4), "AUC_95CI_boot": boot_ci(pos, neg),
            "perm_p": round(perm_p(pos, neg), 5)}

# ---------- 6. how much does the committed decoy bar depend on which committed decoy run it is read from ----------
import math
def pct(v, q):
    v = sorted(v); k = (len(v) - 1) * q / 100.0
    f, c = math.floor(k), math.ceil(k)
    return v[int(k)] if f == c else v[f] + (v[c] - v[f]) * (k - f)

bar = {}
for tag, path in [("single_snapshot", "results/nr4a3-decoy/-mmgbsa/nr4a3-mmgbsa.json"),
                  ("multi_snapshot", "results/nr4a3-decoy/-mmgbsa-ms/nr4a3-mmgbsa.json"),
                  ("multi_snapshot_metad", "results/nr4a3-decoy/-mmgbsa-metad-ms/nr4a3-mmgbsa.json")]:
    dd = json.load(open(R(path)))
    v = [c["mm_min_margin"] for c in dd["candidates"] if c.get("mm_min_margin") is not None]
    bar[tag] = {"source": path, "n": len(v), "scheme": dd["method"]["scheme"],
                "p95_mm_min_margin": round(pct(v, 95), 4), "max": round(max(v), 2)}
bar["committed_bar_in_use"] = {
    "value": json.load(open(R("results/nr4a3-generation-matched-null/nr4a3-generation-matched-null.json")))["params"]["decoy_threshold"],
    "matches": "single_snapshot",
    "applied_to": ("the generation-matched scramble set and the de-novo rescoring, which are scored with the "
                   "MULTI-snapshot 10-frame scheme, whose own decoy p95 is 6.69"),
    "spread_across_committed_decoy_runs": "6.69 to 17.70 kcal/mol (2.6x) depending on which committed decoy MM-GBSA run the 95th percentile is taken from"}

# ---------- 6. how much does the committed decoy bar depend on which committed decoy run it is read from ----------
import math
def pct(v, q):
    v = sorted(v); k = (len(v) - 1) * q / 100.0
    f, c = math.floor(k), math.ceil(k)
    return v[int(k)] if f == c else v[f] + (v[c] - v[f]) * (k - f)

bar = {}
for tag, path in [("single_snapshot", "results/nr4a3-decoy/-mmgbsa/nr4a3-mmgbsa.json"),
                  ("multi_snapshot", "results/nr4a3-decoy/-mmgbsa-ms/nr4a3-mmgbsa.json"),
                  ("multi_snapshot_metad", "results/nr4a3-decoy/-mmgbsa-metad-ms/nr4a3-mmgbsa.json")]:
    dd = json.load(open(R(path)))
    v = [c["mm_min_margin"] for c in dd["candidates"] if c.get("mm_min_margin") is not None]
    bar[tag] = {"source": path, "n": len(v), "scheme": dd["method"]["scheme"],
                "p95_mm_min_margin": round(pct(v, 95), 4), "max": round(max(v), 2)}
bar["committed_bar_in_use"] = {
    "value": json.load(open(R("results/nr4a3-generation-matched-null/nr4a3-generation-matched-null.json")))["params"]["decoy_threshold"],
    "matches": "single_snapshot",
    "applied_to": ("the generation-matched scramble set and the de-novo rescoring, which are scored with the "
                   "MULTI-snapshot 10-frame scheme, whose own decoy p95 is 6.69"),
    "spread_across_committed_decoy_runs": "6.69 to 17.70 kcal/mol (2.6x) depending on which committed decoy MM-GBSA run the 95th percentile is taken from"}

out = {
    "_note": ("REPURPOSE-DECOY-1. Separability of the committed NR4A3 shortlist from the committed "
              "decoy negative-control set, scored only on already-computed committed docking and "
              "MM-GBSA numbers. DOCKING AND MM-GBSA SCORES ARE NOT AFFINITIES AND NOT EFFICACY. "
              "Nothing here is a claim of efficacy, safety, selectivity in cells, therapeutic window "
              "or clinical readiness for any drug, and no drug here is a candidate for use."),
    "lane": "REPURPOSE-DECOY-1",
    "date": "2026-09-09",
    "provenance_sha256": prov,
    "sets": {
        "shortlist": {"source": "results/nr4a3-matrix/nr4a3-matrix.json",
                      "n": len(S), "labels": [r["label"] for r in S],
                      "identity": "13 literature NR4A-active reference compounds in the 3-receptor selectivity tier"},
        "decoy": {"source": "results/nr4a3-decoy/-matrix/nr4a3-matrix.json",
                  "n": len(D), "candidate_source": dec.get("candidate_source"),
                  "decoy_library_self_description": (
                      "decoy_library.py: 'This is a property-spanning negative set, not a "
                      "property-matched DUD-E set'")},
        "scramble": {"source": "results/nr4a3-genmatched-scramble-mmgbsa/nr4a3-mmgbsa.json",
                     "n": len(scr)},
        "smiles_missing": missing,
    },
    "property_match_audit": prop_audit,
    "separability_full_decoy_set": res,
    "property_only_null_scorers": prop_auc,
    "separability_property_matched_subset": matched,
    "required_check_scramble_at_chance": chance,
    "decoy_bar_scheme_sensitivity": bar,
    "shortlist_rows": S,
    "decoy_rows": D,
}
json.dump(out, open(os.path.join(os.path.dirname(__file__), "repurpose-decoy-enrichment.json"), "w"),
          indent=1, sort_keys=False)
print(json.dumps({k: out[k] for k in ["property_match_audit", "separability_full_decoy_set",
                                      "property_only_null_scorers",
                                      "separability_property_matched_subset",
                                      "required_check_scramble_at_chance",
                                      "decoy_bar_scheme_sensitivity"]}, indent=1))
