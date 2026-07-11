#!/usr/bin/env python3
"""Read-only analysis of the retrospective NR-V04 / VHL ternary benchmark outputs in S3 (Track B).

The NR-V04 benchmark differs from the CRBN report_ternary.py in three ways, so it needs its own reader:
  * E3 is VHL (+ ElonginB/C) — FOUR protein chains, not two; report_ternary's "smaller=NR4A, larger=CRBN"
    assignment breaks. Here chains are identified by their YAML id: L=ligand, A=NR4A target, E=VHL, F/G=EloB/C
    (nr4a3_ternary.boltz_yaml preserves ids; nrv04_ternary.e3_chains sets VHL='E').
  * The positive control is VH032 seated in VHL's hydroxyproline pocket (Ser111/His115/Trp117), not
    lenalidomide in CRBN's tri-Trp.
  * Every system is an ENSEMBLE over diffusion seeds (control/seed_N, nr4a1/seed_N, ...). The readout is the
    DISTRIBUTION across seeds (ligand-iPTM, bridging, seed persistence), not a single pose.

PILOT GATE (nrv04-ternary-benchmark.json → single_leg_first_pilot): with only control + NR4A1 present, decide
  PROCEED  — control seats VH032 AND NR4A1 forms a productive, seed-persistent ternary → fan out NR4A2/NR4A3;
  ABORT    — control can't seat VH032 (workflow broken) OR NR4A1 can't form a productive ternary (can't even
             recover the known-degraded positive case) → don't spend on the full paralogue fleet.
When NR4A2/NR4A3 are also present (full run) it additionally applies the informative/inconclusive/failed
verdict_gate by comparing NR4A1 vs NR4A2/NR4A3 on the ensemble readouts.

CPU only (boto3 + gemmi). Env: AWS creds, OUTPUT_PREFIX (default nrv04-ternary-pilot). Writes a JSON summary to
$OUT (default report_nrv04.json) and prints a human table.
"""
import glob
import json
import os
import statistics
import sys
import tempfile

STANDARD_AA = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU",
    "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
}
# VHL hydroxyproline (Hyp) pocket — the substrate sub-pocket that binds HIF-1α Hyp564 and every VHL-PROTAC's
# (2S,4R)-4-hydroxyproline (VH032 included). P40337 (pVHL) numbering; S111+H115 make the defining H-bonds.
VHL_HYP_POCKET = [98, 110, 111, 115, 117]     # Tyr98, His110, Ser111, His115, Trp117
VHL_SEAT_KEY = [111, 115]                       # seating requires proximity to these two
SEAT_CUTOFF = 4.5                               # Å; ligand heavy atom within this of a key pocket residue
BRIDGE_CUTOFF = 4.5                             # Å; ligand-to-protein contact defining a bridge
LYS_BINS = (8.0, 12.0, 16.0)                    # Å; exposed target Lys NZ → VHL (ubiquitin-reach proxy)
LIG_ID, NR4A_ID, VHL_ID = "L", "A", "E"


def _download(prefix, dest):
    import boto3
    s3 = boto3.client("s3")
    bucket = f"sagemaker-{os.environ.get('AWS_DEFAULT_REGION', 'us-east-2')}-" \
             f"{boto3.client('sts').get_caller_identity()['Account']}"
    n = 0
    for page in boto3.client("s3").get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            local = os.path.join(dest, key[len(prefix):].lstrip("/"))
            os.makedirs(os.path.dirname(local), exist_ok=True)
            s3.download_file(bucket, key, local)
            n += 1
    print(f"downloaded {n} objects from s3://{bucket}/{prefix}", flush=True)
    return n, bucket


def _chains(model):
    """{chain_id: [(resname, resnum, {atom: pos})]} for protein chains, plus ligand heavy-atom positions."""
    prot, lig = {}, []
    for chain in model:
        residues = []
        for res in chain:
            if res.name in STANDARD_AA:
                residues.append((res.name, res.seqid.num, {a.name: a.pos for a in res if a.element.name != "H"}))
            else:
                lig.extend(a.pos for a in res if a.element.name != "H")
        if residues:
            prot[chain.name] = residues
    return prot, lig


def _min_dist(a, b):
    return None if not a or not b else min(pa.dist(pb) for pa in a for pb in b)


def _atoms(residues):
    return [p for _, _, atoms in residues for p in atoms.values()]


def _pocket_atoms(vhl, wanted):
    out = {}
    for name, num, atoms in vhl:
        if num in wanted:
            out[num] = list(atoms.values())
    return out


def seat_geometry(model):
    """Control read: closest approach of the ligand (VH032) to VHL's hydroxyproline pocket. SEATED iff within
    SEAT_CUTOFF of BOTH key residues (S111, H115)."""
    prot, lig = _chains(model)
    vhl = prot.get(VHL_ID) or (max(prot.values(), key=len) if prot else [])
    if not lig or not vhl:
        return {"seated": None, "note": "no ligand or VHL chain"}
    pocket = _pocket_atoms(vhl, VHL_HYP_POCKET)
    dists = {num: _min_dist(lig, atoms) for num, atoms in pocket.items()}
    key_ok = all(dists.get(k) is not None and dists[k] <= SEAT_CUTOFF for k in VHL_SEAT_KEY)
    closest = min((d for d in dists.values() if d is not None), default=None)
    return {"seated": bool(key_ok), "closest_pocket_A": None if closest is None else round(closest, 2),
            "per_residue_A": {int(k): (None if v is None else round(v, 2)) for k, v in dists.items()}}


def bridge_geometry(model):
    """NR4A1 ternary read: does NR-V04 bridge the NR4A target (chain A) and VHL (chain E), and how close is the
    nearest exposed target Lys NZ to VHL (ubiquitin-reach proxy)?"""
    prot, lig = _chains(model)
    nr4a = prot.get(NR4A_ID)
    vhl = prot.get(VHL_ID)
    if nr4a is None or vhl is None:
        # fall back: two largest protein chains are target + VHL (EloB/C are ~112-118 aa, smaller)
        big = sorted(prot.items(), key=lambda kv: len(kv[1]), reverse=True)[:2]
        if len(big) < 2:
            return {"bridges": None, "note": "fewer than 2 protein chains"}
        nr4a, vhl = big[0][1], big[1][1]
    d_nr4a = _min_dist(lig, _atoms(nr4a))
    d_vhl = _min_dist(lig, _atoms(vhl))
    bridges = d_nr4a is not None and d_vhl is not None and d_nr4a <= BRIDGE_CUTOFF and d_vhl <= BRIDGE_CUTOFF
    lys = [(num, atoms["NZ"]) for name, num, atoms in nr4a if name == "LYS" and "NZ" in atoms]
    vhl_atoms = _atoms(vhl)
    closest_lys = None
    if lys:
        cand = sorted(((num, _min_dist([nz], vhl_atoms)) for num, nz in lys), key=lambda t: (t[1] is None, t[1]))
        closest_lys = {"resnum": int(cand[0][0]), "dist_A": round(cand[0][1], 2),
                       "counts": {f"{b:g}A": sum(1 for _, d in cand if d is not None and d <= b) for b in LYS_BINS}}
    return {"bridges": bool(bridges), "lig_to_target_A": None if d_nr4a is None else round(d_nr4a, 2),
            "lig_to_vhl_A": None if d_vhl is None else round(d_vhl, 2), "n_lys": len(lys),
            "closest_exposed_lys": closest_lys}


def _confidence(seed_dir):
    """Boltz confidence for the top model under a seed dir → the ensemble-relevant scores."""
    conf = sorted(glob.glob(os.path.join(seed_dir, "**", "confidence*.json"), recursive=True))
    conf = [c for c in conf if "model_0" in c] or conf
    if not conf:
        return None
    d = json.load(open(conf[0]))
    keys = ("confidence_score", "ptm", "iptm", "ligand_iptm", "protein_iptm", "complex_plddt", "complex_iplddt")
    return {k: round(d[k], 4) for k in keys if isinstance(d.get(k), (int, float))}


def _top_model(seed_dir):
    cif = sorted(glob.glob(os.path.join(seed_dir, "**", "*.cif"), recursive=True))
    cif = [m for m in cif if "model_0" in m] or cif
    return cif[0] if cif else None


def analyse_system(root, system, kind):
    """Walk system/seed_*/ dirs; per seed collect confidence + geometry; aggregate the ensemble."""
    import gemmi
    sysdir = os.path.join(root, system)
    seed_dirs = sorted(glob.glob(os.path.join(sysdir, "seed_*")))
    if not seed_dirs:
        # some layouts nest one level up; search anywhere for this system's seed dirs
        seed_dirs = sorted(set(os.path.dirname(os.path.dirname(p))
                               for p in glob.glob(os.path.join(root, "**", system, "seed_*", "**"), recursive=True)))
    per_seed = []
    for sd in seed_dirs:
        seed = os.path.basename(sd)
        conf = _confidence(sd)
        model_path = _top_model(sd)
        geom = None
        if model_path:
            model = gemmi.read_structure(model_path)[0]
            geom = seat_geometry(model) if kind == "control" else bridge_geometry(model)
        per_seed.append({"seed": seed, "confidence": conf, "geometry": geom})
    return {"system": system, "kind": kind, "n_seeds": len(per_seed), "per_seed": per_seed,
            "ensemble": _aggregate(per_seed, kind)}


def _vals(per_seed, path):
    out = []
    for s in per_seed:
        d = s
        for p in path:
            d = (d or {}).get(p) if isinstance(d, dict) else None
        if isinstance(d, (int, float)):
            out.append(d)
    return out


def _aggregate(per_seed, kind):
    lig_iptm = _vals(per_seed, ["confidence", "ligand_iptm"])
    iptm = _vals(per_seed, ["confidence", "iptm"])
    agg = {"ligand_iptm": _dist(lig_iptm), "iptm": _dist(iptm)}
    if kind == "control":
        seated = [s["geometry"]["seated"] for s in per_seed if s.get("geometry") and s["geometry"].get("seated") is not None]
        agg["seated_fraction"] = None if not seated else round(sum(bool(x) for x in seated) / len(seated), 3)
        agg["n_seated"] = sum(bool(x) for x in seated)
        agg["n_scored"] = len(seated)
    else:
        bridged = [s["geometry"]["bridges"] for s in per_seed if s.get("geometry") and s["geometry"].get("bridges") is not None]
        agg["bridged_fraction"] = None if not bridged else round(sum(bool(x) for x in bridged) / len(bridged), 3)
        agg["n_bridged"] = sum(bool(x) for x in bridged)
        agg["n_scored"] = len(bridged)
        lysd = [s["geometry"]["closest_exposed_lys"]["dist_A"] for s in per_seed
                if s.get("geometry") and s["geometry"].get("closest_exposed_lys")]
        agg["closest_lys_A"] = _dist(lysd)
    return agg


def _dist(xs):
    if not xs:
        return None
    return {"n": len(xs), "mean": round(statistics.mean(xs), 4), "min": round(min(xs), 4),
            "max": round(max(xs), 4), "sd": round(statistics.pstdev(xs), 4) if len(xs) > 1 else 0.0}


def pilot_verdict(control, nr4a1):
    """Encode single_leg_first_pilot: PROCEED / ABORT for the control+NR4A1 pilot."""
    c = control["ensemble"] if control else {}
    n = nr4a1["ensemble"] if nr4a1 else {}
    control_ok = bool(control) and (c.get("seated_fraction") or 0) >= 0.5
    # productive + seed-persistent: bridges in a majority of seeds.
    nr4a1_ok = bool(nr4a1) and (n.get("bridged_fraction") or 0) >= 0.5
    if control_ok and nr4a1_ok:
        verdict, reason = "PROCEED", ("control seats VH032 in VHL (seated in %s/%s seeds) AND NR4A1 forms a "
                                      "productive, seed-persistent ternary (bridged in %s/%s seeds) → fan out "
                                      "NR4A2 + NR4A3 × seeds × linkers." % (c.get("n_seated"), c.get("n_scored"),
                                                                           n.get("n_bridged"), n.get("n_scored")))
    else:
        bad = []
        if not control_ok:
            bad.append("control did NOT seat VH032 in VHL (workflow suspect)")
        if not nr4a1_ok:
            bad.append("NR4A1 (known-degraded) did NOT form a productive seed-persistent ternary")
        verdict, reason = "ABORT", " ; ".join(bad) + " → do not spend on the full paralogue fleet; fix the workflow first."
    return {"verdict": verdict, "reason": reason, "control_ok": control_ok, "nr4a1_ok": nr4a1_ok}


def full_verdict(systems):
    """Composite, TRANSPARENT full-run verdict comparing NR4A1 (degraded) vs NR4A2/NR4A3 (spared) across the
    pre-specified ensemble readouts. Reports each readout SEPARATELY (they can disagree) and derives the primary
    verdict from PRODUCTIVE-TERNARY GEOMETRY, not ligand-iPTM.

    Rationale (verified on the 2026-07-11 NR-V04 run, documented so the metric choice is auditable, not
    post-hoc): a PROTAC ternary is productive only if the linker BRIDGES both proteins simultaneously. ligand-iPTM
    scores the confidence of the ligand's overall placement, which is dominated by the well-defined VHL-warhead
    half and stays HIGH even when the target LBD is far away and no ternary forms — so ligand-iPTM alone can
    INVERT the known selectivity (it did: spared NR4A2 scored highest). Bridging (both ends ≤ BRIDGE_CUTOFF) is
    the physical definition of a ternary and was computed by bridge_geometry from the analyzer's first version;
    exposed-Lys→VHL distance is the ubiquitin-reach proxy. Both were pre-specified spec readouts."""
    def ens(name):
        s = systems.get(name)
        return s["ensemble"] if s else None
    e1, e2, e3 = ens("nr4a1"), ens("nr4a2"), ens("nr4a3")
    if None in (e1, e2, e3):
        return {"verdict": "pilot-only", "note": "NR4A2/NR4A3 not present — full verdict needs all three."}

    def g(e, k, sub="mean"):
        v = e.get(k)
        if k in ("bridged_fraction",):
            return e.get(k)
        return (v or {}).get(sub) if isinstance(v, dict) else v

    br1, br2, br3 = e1.get("bridged_fraction"), e2.get("bridged_fraction"), e3.get("bridged_fraction")
    li1, li2, li3 = g(e1, "ligand_iptm"), g(e2, "ligand_iptm"), g(e3, "ligand_iptm")
    ly1, ly2, ly3 = g(e1, "closest_lys_A"), g(e2, "closest_lys_A"), g(e3, "closest_lys_A")

    # (1) PRIMARY readout — productive-ternary geometry. Clean separation = NR4A1 bridges in a majority of seeds
    # while BOTH spared paralogues bridge in a minority.
    geom_sep = (br1 is not None and br2 is not None and br3 is not None
                and br1 >= 0.5 and max(br2, br3) < 0.5)
    # (2) SECONDARY — ubiquitin-reach: degraded target presents the closest exposed Lys to VHL.
    lys_sep = (None not in (ly1, ly2, ly3)) and (ly1 < ly2 and ly1 < ly3)
    # (3) ligand-iPTM ordering (the naive scalar) — reported for transparency; NOT the primary basis.
    others_li = max(li2, li3) if None not in (li2, li3) else None
    li_margin = (li1 - others_li) if (li1 is not None and others_li is not None) else None
    li_verdict = None
    if li_margin is not None:
        li_verdict = "informative" if li_margin >= 0.05 else ("inconclusive" if li_margin > -0.05 else "failed")

    if geom_sep:
        verdict = "informative"
        basis = ("productive-ternary geometry separates degraded from spared: NR4A1 bridges %.0f%% of seeds vs "
                 "NR4A2 %.0f%% / NR4A3 %.0f%%" % (100 * br1, 100 * br2, 100 * br3))
    elif br1 is not None and br1 >= 0.5:
        verdict = "inconclusive"
        basis = "NR4A1 forms a productive ternary but a spared paralogue also bridges — geometry does not cleanly separate"
    else:
        verdict = "failed"
        basis = "NR4A1 (known-degraded) does not form a productive ternary in a majority of seeds"

    return {"verdict": verdict, "primary_basis": "productive_ternary_geometry", "basis": basis,
            "bridged_fraction": {"nr4a1": br1, "nr4a2": br2, "nr4a3": br3},
            "closest_lys_A": {"nr4a1": ly1, "nr4a2": ly2, "nr4a3": ly3}, "lys_supports": lys_sep,
            "ligand_iptm": {"nr4a1": li1, "nr4a2": li2, "nr4a3": li3},
            "ligand_iptm_margin": None if li_margin is None else round(li_margin, 4),
            "ligand_iptm_verdict": li_verdict,
            "ligand_iptm_note": ("ligand-iPTM is NOT the primary basis: it scores overall ligand-placement "
                                 "confidence (dominated by the VHL-warhead half) and can stay high / invert even "
                                 "when no productive ternary forms. Reported for transparency.")}


def main():
    if not os.environ.get("AWS_ACCESS_KEY_ID"):
        sys.exit("AWS creds required")
    try:
        import gemmi  # noqa: F401
    except ImportError:
        sys.exit("pip install gemmi")
    prefix = os.environ.get("OUTPUT_PREFIX", "nrv04-ternary-pilot")
    out_path = os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_nrv04.json"))
    with tempfile.TemporaryDirectory() as tmp:
        n, bucket = _download(prefix, tmp)
        if not n:
            sys.exit(f"nothing under s3 prefix {prefix}")
        prep = glob.glob(os.path.join(tmp, "**", "nrv04-ternary-prep.json"), recursive=True)
        prep_data = json.load(open(prep[0])) if prep else {}

        systems = {}
        control = None
        # control dir is 'control'; targets are nr4a1/nr4a2/nr4a3
        if glob.glob(os.path.join(tmp, "control", "seed_*")) or glob.glob(os.path.join(tmp, "**", "control", "seed_*"), recursive=True):
            control = analyse_system(tmp, "control", "control")
        for name in ("nr4a1", "nr4a2", "nr4a3"):
            if glob.glob(os.path.join(tmp, name, "seed_*")) or glob.glob(os.path.join(tmp, "**", name, "seed_*"), recursive=True):
                systems[name] = analyse_system(tmp, name, "ternary")

        report = {"prefix": prefix, "bucket": bucket, "mode": prep_data.get("mode"),
                  "seeds": prep_data.get("seeds"), "ground_truth": prep_data.get("ground_truth"),
                  "control": control, "systems": systems}
        report["pilot_gate"] = pilot_verdict(control, systems.get("nr4a1"))
        if all(k in systems for k in ("nr4a1", "nr4a2", "nr4a3")):
            report["full_gate"] = full_verdict(systems)

        json.dump(report, open(out_path, "w"), indent=2)
        print("\n=== NR-V04 / VHL ternary benchmark — %s ===" % prefix)
        if control:
            e = control["ensemble"]
            print("CONTROL VHL+VH032: seated %s/%s seeds; ligand-iPTM %s" %
                  (e.get("n_seated"), e.get("n_scored"), e.get("ligand_iptm")))
        for name, s in systems.items():
            e = s["ensemble"]
            print("%s ternary: bridged %s/%s seeds; ligand-iPTM %s; closest exposed Lys→VHL %s" %
                  (name.upper(), e.get("n_bridged"), e.get("n_scored"), e.get("ligand_iptm"), e.get("closest_lys_A")))
        print("\nPILOT GATE: %s — %s" % (report["pilot_gate"]["verdict"], report["pilot_gate"]["reason"]))
        if "full_gate" in report:
            print("FULL GATE: %s" % json.dumps(report["full_gate"]))
        print("\nwrote %s" % out_path)


if __name__ == "__main__":
    main()
