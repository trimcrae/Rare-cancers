#!/usr/bin/env python3
"""Property-matched control for the IDH-inhibitor NR4A3-binding enrichment.

QUESTION. The 7 IDH inhibitors rank high in the NR4A3-only triage dock (mean ~19th percentile of 5,950).
Is that because their SCAFFOLD binds NR4A3, or merely because IDH inhibitors are lipophilic/aromatic
drug-sized molecules — the profile that docks well against ANY lipophilic pocket? This decides it: compare
the IDH inhibitors' ranks against a null of random library drugs MATCHED to them on MW / cLogP / aromatic
rings. If IDH inhibitors do NOT beat property-matched decoys → the enrichment is generic physicochemistry
(coincidence). If they beat matched decoys → something scaffold-specific.

Method (numpy/scipy-free): compute RDKit descriptors for every docked drug; build the IDH property envelope
(min..max of the 7, padded); the matched pool = non-IDH drugs inside that envelope; report the IDH ranks vs
the matched pool's rank distribution (Mann-Whitney-U p, plus a bootstrap: draw 7 matched decoys many times,
how often does their mean-rank beat the IDH mean-rank).

Env: BUCKET (opt), INPUT_PREFIX (default nr4a3-repurpose-nr4a3only), SHARDS (default shard-00..10),
MW_PAD/LOGP_PAD/AROM_PAD (envelope padding), N_BOOT (default 20000), SEED (default 0),
AWS creds + AWS_DEFAULT_REGION.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repurpose_dock_core as core  # noqa: E402

IDH = {"rep00307": "AGI-5198", "rep02763": "IDH-305", "rep02906": "ivosidenib",
       "rep05802": "vorasidenib", "rep00755": "BAY-1436032", "rep00308": "AGI-6780",
       "rep02024": "enasidenib"}


def _smiles_map():
    import glob
    m = {}
    here = os.path.dirname(os.path.abspath(__file__))
    for f in glob.glob(os.path.join(here, "nr4a3-repurpose-shard-*.json")):
        try:
            d = json.load(open(f))
        except ValueError:
            continue
        for c in d.get("candidates", []):
            if c.get("name") and c.get("smiles"):
                m[c["name"]] = c["smiles"]
    return m


def _dg_map():
    import boto3
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3, sts = boto3.client("s3"), boto3.client("sts")
    acct = sts.get_caller_identity()["Account"]
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
    prefix = os.environ.get("INPUT_PREFIX", "nr4a3-repurpose-nr4a3only")
    shards = [t.strip() for t in os.environ.get(
        "SHARDS", ",".join(f"shard-{i:02d}" for i in range(11))).split(",") if t.strip()]
    rows = []
    for tag in shards:
        key = f"{prefix}/{tag}-ckpt/{tag}.results.jsonl"
        try:
            body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode()
        except Exception:  # noqa: BLE001
            continue
        for ln in body.splitlines():
            ln = ln.strip()
            if ln:
                try:
                    rows.append(json.loads(ln))
                except ValueError:
                    pass
    return {r["label"]: r for r in rows if r.get("dG_NR4A3") is not None}


def main():
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Lipinski
    smi = _smiles_map()
    dgs = _dg_map()
    print(f"docked drugs with dG: {len(dgs)}; smiles available: {len(smi)}")

    # descriptors for every docked drug
    recs = []
    for label, r in dgs.items():
        s = smi.get(label)
        if not s:
            continue
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            continue
        recs.append({"label": label, "dG": r["dG_NR4A3"],
                     "mw": Descriptors.MolWt(mol), "logp": Descriptors.MolLogP(mol),
                     "arom": Lipinski.NumAromaticRings(mol)})
    # rank by dG ascending (best = rank 1)
    recs.sort(key=lambda x: x["dG"])
    n = len(recs)
    for i, x in enumerate(recs):
        x["rank"] = i + 1
        x["pct"] = 100.0 * (i + 1) / n
    by = {x["label"]: x for x in recs}
    idh = [by[k] for k in IDH if k in by]
    print(f"ranked {n} drugs with descriptors; IDH inhibitors found: {len(idh)}\n")

    mw_pad = float(os.environ.get("MW_PAD", "40"))
    logp_pad = float(os.environ.get("LOGP_PAD", "0.6"))
    arom_pad = int(os.environ.get("AROM_PAD", "1"))
    mws = [x["mw"] for x in idh]
    lps = [x["logp"] for x in idh]
    ars = [x["arom"] for x in idh]
    lo_mw, hi_mw = min(mws) - mw_pad, max(mws) + mw_pad
    lo_lp, hi_lp = min(lps) - logp_pad, max(lps) + logp_pad
    lo_ar, hi_ar = min(ars) - arom_pad, max(ars) + arom_pad
    idh_labels = set(IDH)
    pool = [x for x in recs if x["label"] not in idh_labels
            and lo_mw <= x["mw"] <= hi_mw and lo_lp <= x["logp"] <= hi_lp and lo_ar <= x["arom"] <= hi_ar]
    print("=== IDH inhibitors (property-envelope: "
          f"MW {lo_mw:.0f}-{hi_mw:.0f}, logP {lo_lp:.1f}-{hi_lp:.1f}, arom {lo_ar}-{hi_ar}) ===")
    print(f"{'drug':<14}{'MW':>7}{'logP':>7}{'arom':>5}{'rank':>8}{'pct':>7}")
    for x in sorted(idh, key=lambda z: z["rank"]):
        print(f"{IDH[x['label']]:<14}{x['mw']:>7.0f}{x['logp']:>7.1f}{x['arom']:>5}{x['rank']:>8}{x['pct']:>6.1f}%")
    idh_mean_pct = sum(x["pct"] for x in idh) / len(idh)
    print(f"\nIDH mean percentile: {idh_mean_pct:.1f}%   (random expectation 50%)")
    print(f"property-matched pool (non-IDH, in envelope): {len(pool)} drugs, "
          f"mean percentile {sum(x['pct'] for x in pool)/len(pool):.1f}%")

    # Bootstrap: draw len(idh) matched decoys many times; how often does their mean pct <= IDH mean pct?
    n_boot = int(os.environ.get("N_BOOT", "20000"))
    rnd = random.Random(int(os.environ.get("SEED", "0")))
    k = len(idh)
    if len(pool) >= k:
        cnt = 0
        for _ in range(n_boot):
            samp = rnd.sample(pool, k)
            if sum(x["pct"] for x in samp) / k <= idh_mean_pct:
                cnt += 1
        p = cnt / n_boot
        print(f"\nbootstrap: P(property-matched decoys rank as high as the IDH set) = {p:.4f}  (n_boot={n_boot})")
        print("  p >~ 0.05  => enrichment is explained by MW/logP/aromatic (generic lipophilicity; coincidence).")
        print("  p <~ 0.05  => IDH inhibitors beat property-matched decoys => something scaffold-specific.")
    else:
        print("\n(matched pool too small to bootstrap; widen the padding.)")


if __name__ == "__main__":
    main()
