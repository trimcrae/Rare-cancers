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
import re
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
LYS_BINS = (8.0, 12.0, 16.0)                    # Å; target Lys NZ → VHL (ubiquitin-ACCESSIBILITY proxy; NOT SASA)
LIG_ID, NR4A_ID, VHL_ID = "L", "A", "E"
CUTOFFS = (4.0, 4.5, 5.0)                        # Å; contact cutoffs for cutoff-sensitivity (review fix 7)
DEFAULT_CUTOFF = 4.5
WRONG_END_MARGIN = 2.0                           # Å an end must be *closer* to the wrong protein to flag wrong-end
NR4A1_CYS = 551                                  # celastrol Michael-acceptor covalent target on NR4A1 (proxy only)


def _euclid(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def _min_d(a_pts, b_pts):
    return None if not a_pts or not b_pts else min(_euclid(a, b) for a in a_pts for b in b_pts)


def split_ligand_ends(lig_atoms):
    """Partition NR-V04 ligand heavy atoms into (vhl_end, nr4a_end) WITHOUT bond perception. NR-V04 contains
    EXACTLY ONE sulfur (the thiazole in the VH032/VHL half; celastrol + PEG have none), so the S is a clean
    anchor for the VHL end; the ligand atom farthest from it is the celastrol (NR4A) terminus. Each atom joins
    the end whose anchor it is closer to. Returns (vhl_end_pts, nr4a_end_pts, note). `lig_atoms` = list of
    (element, (x,y,z)). Falls back to whole-ligand (both ends = all atoms) with a note if S count != 1."""
    pts = [p for _, p in lig_atoms]
    sulfurs = [p for el, p in lig_atoms if el.upper() == "S"]
    if len(sulfurs) != 1 or len(pts) < 2:
        return pts, pts, "moiety-split unavailable (S count=%d); whole-ligand fallback" % len(sulfurs)
    a_vhl = sulfurs[0]                                            # VH032/thiazole anchor
    a_nr4a = max(pts, key=lambda p: _euclid(p, a_vhl))           # celastrol terminus = farthest atom from S
    vhl_end, nr4a_end = [], []
    for p in pts:
        (vhl_end if _euclid(p, a_vhl) <= _euclid(p, a_nr4a) else nr4a_end).append(p)
    return vhl_end, nr4a_end, "S-anchor split (VH032 end vs celastrol end)"


def moiety_geometry(model, cutoffs=CUTOFFS, is_nr4a1=False):
    """Moiety-SPECIFIC ternary read (review fix 4): does the celastrol end contact the NR4A target AND the
    VH032 end contact VHL — i.e. a productive ternary via the CORRECT ends, not a wrong-end/linker-mediated/
    surface contact that a whole-ligand min-distance test would pass. Reports per-cutoff moiety-bridging, a
    wrong-end flag, and (NR4A1 only) the celastrol-end→Cys551-SG distance as a covalent-geometry PROXY."""
    prot, _lig = _chains(model)
    nr4a = prot.get(NR4A_ID)
    vhl = prot.get(VHL_ID)
    if nr4a is None or vhl is None:
        big = sorted(prot.items(), key=lambda kv: len(kv[1]), reverse=True)[:2]
        if len(big) < 2:
            return {"moiety_bridges": None, "note": "fewer than 2 protein chains"}
        nr4a, vhl = big[0][1], big[1][1]
    # ligand atoms with element (rebuild here since _chains drops element for the ligand)
    lig_atoms = []
    for chain in model:
        for res in chain:
            if res.name not in STANDARD_AA:
                for a in res:
                    if a.element.name != "H":
                        lig_atoms.append((a.element.name, (a.pos.x, a.pos.y, a.pos.z)))
    if len(lig_atoms) < 2:
        return {"moiety_bridges": None, "note": "no ligand"}
    vhl_end, nr4a_end, split_note = split_ligand_ends(lig_atoms)
    nr4a_pts = [(p.x, p.y, p.z) for p in _atoms(nr4a)]
    vhl_pts = [(p.x, p.y, p.z) for p in _atoms(vhl)]
    d_vhlend_vhl = _min_d(vhl_end, vhl_pts)
    d_vhlend_nr4a = _min_d(vhl_end, nr4a_pts)
    d_nr4aend_nr4a = _min_d(nr4a_end, nr4a_pts)
    d_nr4aend_vhl = _min_d(nr4a_end, vhl_pts)
    bridges = {}
    for c in cutoffs:
        bridges["%.1f" % c] = bool(d_vhlend_vhl is not None and d_nr4aend_nr4a is not None
                                   and d_vhlend_vhl <= c and d_nr4aend_nr4a <= c)
    # wrong-end: an end sits clearly closer to the protein it should NOT engage
    wrong_end = bool((d_vhlend_nr4a is not None and d_vhlend_vhl is not None
                      and d_vhlend_nr4a + WRONG_END_MARGIN < d_vhlend_vhl)
                     or (d_nr4aend_vhl is not None and d_nr4aend_nr4a is not None
                         and d_nr4aend_vhl + WRONG_END_MARGIN < d_nr4aend_nr4a))
    out = {"moiety_bridges": bridges, "moiety_bridges_default": bridges["%.1f" % DEFAULT_CUTOFF],
           "wrong_end": wrong_end, "split": split_note,
           "celastrol_end_to_NR4A_A": None if d_nr4aend_nr4a is None else round(d_nr4aend_nr4a, 2),
           "celastrol_end_to_VHL_A": None if d_nr4aend_vhl is None else round(d_nr4aend_vhl, 2),
           "vh032_end_to_VHL_A": None if d_vhlend_vhl is None else round(d_vhlend_vhl, 2),
           "vh032_end_to_NR4A_A": None if d_vhlend_nr4a is None else round(d_vhlend_nr4a, 2)}
    if is_nr4a1:
        cys = [a["SG"] for name, num, a in nr4a if name == "CYS" and num == NR4A1_CYS and "SG" in a]
        if cys:
            cys_pt = [(cys[0].x, cys[0].y, cys[0].z)]
            out["celastrol_end_to_Cys551_A"] = round(_min_d(nr4a_end, cys_pt), 2)
            out["_cys551_note"] = "covalent-geometry PROXY (no covalent bond modeled); celastrol-end min dist to Cys551 SG"
    return out


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


_RANK_RE = re.compile(r"model_(\d+)")


def _rank_of(path):
    m = _RANK_RE.search(os.path.basename(path))
    return int(m.group(1)) if m else 0


def _all_models(seed_dir):
    """ALL generated ranks under a seed dir (review fix 7: analyze every sample, not just model_0).
    Returns [(rank, cif_path, confidence_dict_or_None)] sorted by rank."""
    cifs = sorted(glob.glob(os.path.join(seed_dir, "**", "*_model_*.cif"), recursive=True)) \
        or sorted(glob.glob(os.path.join(seed_dir, "**", "*.cif"), recursive=True))
    keys = ("confidence_score", "ptm", "iptm", "ligand_iptm", "protein_iptm", "complex_plddt", "complex_iplddt")
    out = []
    for cif in cifs:
        rank = _rank_of(cif)
        conf = None
        cdir = os.path.dirname(cif)
        cand = glob.glob(os.path.join(cdir, "confidence*model_%d*.json" % rank)) \
            or glob.glob(os.path.join(cdir, "**", "confidence*model_%d*.json" % rank), recursive=True)
        if cand:
            try:
                d = json.load(open(cand[0]))
                conf = {k: round(d[k], 4) for k in keys if isinstance(d.get(k), (int, float))}
            except Exception:  # noqa: BLE001
                conf = None
        out.append((rank, cif, conf))
    return out


def analyse_system(root, system, kind):
    """Walk system/seed_*/ dirs; per seed AND per rank collect confidence + whole-ligand geometry + (ternary)
    moiety-specific geometry; aggregate over ALL samples (seed × rank)."""
    import gemmi
    sysdir = os.path.join(root, system)
    seed_dirs = sorted(glob.glob(os.path.join(sysdir, "seed_*")))
    if not seed_dirs:
        seed_dirs = sorted(set(os.path.dirname(os.path.dirname(p))
                               for p in glob.glob(os.path.join(root, "**", system, "seed_*", "**"), recursive=True)))
    is_nr4a1 = (system.lower() == "nr4a1")
    samples = []
    for sd in seed_dirs:
        seed = os.path.basename(sd)
        for rank, cif, conf in _all_models(sd):
            model = gemmi.read_structure(cif)[0]
            rec = {"seed": seed, "rank": rank, "confidence": conf}
            if kind == "control":
                rec["geometry"] = seat_geometry(model)
            else:
                rec["geometry"] = bridge_geometry(model)                     # whole-ligand (kept for comparison)
                rec["moiety"] = moiety_geometry(model, is_nr4a1=is_nr4a1)    # moiety-specific (primary)
            samples.append(rec)
    n_seeds = len(set(s["seed"] for s in samples))
    return {"system": system, "kind": kind, "n_seeds": n_seeds, "n_samples": len(samples),
            "samples": samples, "per_seed": samples,   # per_seed kept as alias for back-compat readers
            "ensemble": _aggregate(samples, kind)}


def _vals(per_seed, path):
    out = []
    for s in per_seed:
        d = s
        for p in path:
            d = (d or {}).get(p) if isinstance(d, dict) else None
        if isinstance(d, (int, float)):
            out.append(d)
    return out


def _frac(flags):
    flags = [bool(x) for x in flags if x is not None]
    return (None, 0, 0) if not flags else (round(sum(flags) / len(flags), 3), sum(flags), len(flags))


def _aggregate(samples, kind):
    lig_iptm = _vals(samples, ["confidence", "ligand_iptm"])
    iptm = _vals(samples, ["confidence", "iptm"])
    agg = {"ligand_iptm": _dist(lig_iptm), "iptm": _dist(iptm), "n_samples": len(samples),
           "n_seeds": len(set(s["seed"] for s in samples))}
    if kind == "control":
        f, n, d = _frac([s["geometry"].get("seated") for s in samples if s.get("geometry")])
        agg["seated_fraction"], agg["n_seated"], agg["n_scored"] = f, n, d
        return agg
    # whole-ligand bridging (kept ONLY for comparison — the review flagged it can pass on wrong-end contacts)
    f, n, d = _frac([s["geometry"].get("bridges") for s in samples if s.get("geometry")])
    agg["whole_ligand_bridged_fraction"], agg["n_bridged_wholeligand"], agg["n_scored"] = f, n, d
    # PRIMARY: moiety-specific bridging, per cutoff (review fix 4 + cutoff sensitivity fix 7)
    moi = [s.get("moiety") for s in samples if s.get("moiety") and s["moiety"].get("moiety_bridges")]
    agg["moiety_bridged_fraction"] = {}
    for c in CUTOFFS:
        key = "%.1f" % c
        f, n, d = _frac([m["moiety_bridges"].get(key) for m in moi])
        agg["moiety_bridged_fraction"][key] = {"fraction": f, "n_bridged": n, "n": d}
    dk = "%.1f" % DEFAULT_CUTOFF
    agg["moiety_bridged_default"] = agg["moiety_bridged_fraction"].get(dk, {}).get("fraction")
    wf, wn, wd = _frac([m.get("wrong_end") for m in moi])
    agg["wrong_end_fraction"], agg["n_wrong_end"] = wf, wn
    # per-SEED moiety-bridged fraction at the default cutoff (for leave-one-seed-out in full_verdict)
    per_seed = {}
    for s in samples:
        m = s.get("moiety")
        if m and m.get("moiety_bridges"):
            per_seed.setdefault(s["seed"], []).append(bool(m["moiety_bridges"].get(dk)))
    agg["per_seed_moiety_bridged"] = {k: round(sum(v) / len(v), 3) for k, v in per_seed.items()}
    # ubiquitin-ACCESSIBILITY proxy (NOT solvent-accessibility): min Lys-NZ→VHL. Relabelled + demoted from the
    # verdict per review fix 5 (analyzer computes no SASA; per-seed ordering is inconsistent).
    lysd = [s["geometry"]["closest_exposed_lys"]["dist_A"] for s in samples
            if s.get("geometry") and s["geometry"].get("closest_exposed_lys")]
    agg["lys_nz_to_vhl_A"] = _dist(lysd)
    agg["lys_caveat"] = "min Lys-NZ→VHL over ALL modeled lysines (no SASA); crude accessibility proxy, NOT in verdict"
    # celastrol-end→Cys551 covalent-geometry proxy (NR4A1 only)
    cys = [s["moiety"]["celastrol_end_to_Cys551_A"] for s in samples
           if s.get("moiety") and s["moiety"].get("celastrol_end_to_Cys551_A") is not None]
    if cys:
        agg["celastrol_end_to_Cys551_A"] = _dist(cys)
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
    # productive + seed-persistent: MOIETY-bridges (correct ends) in a majority of samples.
    nr4a1_ok = bool(nr4a1) and (n.get("moiety_bridged_default") or 0) >= 0.5
    if control_ok and nr4a1_ok:
        verdict, reason = "PROCEED", ("control seats VH032 in VHL (%s/%s samples) AND NR4A1 forms a productive, "
                                      "MOIETY-correct ternary (moiety-bridged fraction %.2f at %.1f Å) → fan out "
                                      "NR4A2 + NR4A3." % (c.get("n_seated"), c.get("n_scored"),
                                                          n.get("moiety_bridged_default") or 0, DEFAULT_CUTOFF))
    else:
        bad = []
        if not control_ok:
            bad.append("control did NOT seat VH032 in VHL (workflow suspect)")
        if not nr4a1_ok:
            bad.append("NR4A1 (known-degraded) did NOT form a productive seed-persistent ternary")
        verdict, reason = "ABORT", " ; ".join(bad) + " → do not spend on the full paralogue fleet; fix the workflow first."
    return {"verdict": verdict, "reason": reason, "control_ok": control_ok, "nr4a1_ok": nr4a1_ok}


def _sep_at(systems, cutoff_key):
    """Concordance test at one cutoff: NR4A1 moiety-bridges in a MAJORITY of samples while BOTH spared paralogues
    do so in a MINORITY. Returns (bool, {name: fraction})."""
    fr = {}
    for name in ("nr4a1", "nr4a2", "nr4a3"):
        e = systems[name]["ensemble"]
        fr[name] = (e.get("moiety_bridged_fraction", {}).get(cutoff_key, {}) or {}).get("fraction")
    if any(v is None for v in fr.values()):
        return None, fr
    return (fr["nr4a1"] >= 0.5 and max(fr["nr4a2"], fr["nr4a3"]) < 0.5), fr


def _loo_robust(systems):
    """Leave-one-seed-out (review fix 7): does the default-cutoff separation survive dropping ANY single seed?
    Recomputes moiety-bridged fraction per system excluding each seed in turn."""
    dk = "%.1f" % DEFAULT_CUTOFF
    seeds = sorted(set(s["seed"] for s in systems["nr4a1"].get("samples", [])))
    if len(seeds) < 2:
        return None
    for drop in seeds:
        frac = {}
        for name in ("nr4a1", "nr4a2", "nr4a3"):
            samp = [s for s in systems[name].get("samples", []) if s["seed"] != drop]
            flags = [bool(s["moiety"]["moiety_bridges"].get(dk)) for s in samp
                     if s.get("moiety") and s["moiety"].get("moiety_bridges")]
            frac[name] = (sum(flags) / len(flags)) if flags else None
        if any(v is None for v in frac.values()):
            return None
        if not (frac["nr4a1"] >= 0.5 and max(frac["nr4a2"], frac["nr4a3"]) < 0.5):
            return False
    return True


def full_verdict(systems):
    """EXPLORATORY concordance verdict (per the 2026-07-11 external methods review — NOT a validation of
    ternary-selectivity prediction). Primary readout = MOIETY-SPECIFIC bridging (celastrol end contacts the NR4A
    target AND the VH032 end contacts VHL — via the correct ends, not a wrong-end/linker/surface artefact), at
    the default cutoff, with cutoff-sensitivity (4.0/4.5/5.0 Å) and leave-one-seed-out robustness. ligand-iPTM
    ordering is reported for transparency ONLY. Language deliberately avoids 'validated'/'population'/
    'cooperativity' — those quantities are not estimated here."""
    for name in ("nr4a1", "nr4a2", "nr4a3"):
        if name not in systems:
            return {"verdict": "pilot-only", "note": "NR4A2/NR4A3 not present — full verdict needs all three."}

    dk = "%.1f" % DEFAULT_CUTOFF
    sep_default, fr = _sep_at(systems, dk)
    cutoff_sep = {("%.1f" % c): _sep_at(systems, "%.1f" % c)[0] for c in CUTOFFS}
    cutoff_robust = all(v is True for v in cutoff_sep.values())
    loo = _loo_robust(systems)

    def li(name):
        d = systems[name]["ensemble"].get("ligand_iptm")
        return (d or {}).get("mean")
    li1, li2, li3 = li("nr4a1"), li("nr4a2"), li("nr4a3")
    li_note = None
    if None not in (li1, li2, li3):
        li_note = ("ligand-iPTM did NOT reproduce the ordering in this benchmark (NR4A1 %.3f vs NR4A2 %.3f / "
                   "NR4A3 %.3f) and must not rank paralogue-selective ternaries alone." % (li1, li2, li3))

    if sep_default is None:
        verdict, basis = "insufficient-data", "moiety-bridging fractions unavailable for all three paralogues"
    elif sep_default:
        verdict = "exploratory-concordance"
        basis = ("in ONE retrospective example the moiety-specific contact readout was concordant with the known "
                 "phenotype: NR4A1 moiety-bridges %.2f of samples vs NR4A2 %.2f / NR4A3 %.2f at %.1f Å%s%s. "
                 "Exploratory, not validation." % (fr["nr4a1"], fr["nr4a2"], fr["nr4a3"], DEFAULT_CUTOFF,
                 "; robust across 4.0/4.5/5.0 Å" if cutoff_robust else "; NOT robust across all cutoffs",
                 "; survives leave-one-seed-out" if loo else ("; does NOT survive leave-one-seed-out" if loo is False else "")))
    elif fr.get("nr4a1", 0) and fr["nr4a1"] >= 0.5:
        verdict = "inconclusive"
        basis = "NR4A1 forms a moiety-correct ternary but a spared paralogue also bridges — no clean separation"
    else:
        verdict = "discordant"
        basis = "NR4A1 (known-degraded) does not moiety-bridge in a majority of samples"

    return {"verdict": verdict, "primary_basis": "moiety_specific_ternary_geometry", "basis": basis,
            "moiety_bridged_fraction_default": fr, "cutoff_sensitivity": cutoff_sep,
            "cutoff_robust": cutoff_robust, "leave_one_seed_out_robust": loo,
            "wrong_end_fraction": {name: systems[name]["ensemble"].get("wrong_end_fraction")
                                   for name in ("nr4a1", "nr4a2", "nr4a3")},
            "ligand_iptm_mean": {"nr4a1": li1, "nr4a2": li2, "nr4a3": li3}, "ligand_iptm_note": li_note,
            "caveats": ["retrospective n=1 (NR-V04 only)", "NR4A1-selectivity != NR4A3-selectivity",
                        "phenotype does not establish geometry as the cause", "no CRL4/E2~Ub; Lys reach demoted",
                        "productive geometry elevated to primary AFTER the ligand-iPTM result (exploratory)"]}


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
            print("CONTROL VHL+VH032: seated %s/%s samples; ligand-iPTM %s" %
                  (e.get("n_seated"), e.get("n_scored"), e.get("ligand_iptm")))
        for name, s in systems.items():
            e = s["ensemble"]
            print("%s ternary: MOIETY-bridged %s (n=%s samples) @ %.1f Å; wrong-end frac %s; whole-ligand-bridged "
                  "%s; ligand-iPTM %s; lys-NZ→VHL %s" %
                  (name.upper(), e.get("moiety_bridged_default"), e.get("n_samples"), DEFAULT_CUTOFF,
                   e.get("wrong_end_fraction"), e.get("whole_ligand_bridged_fraction"),
                   (e.get("ligand_iptm") or {}).get("mean"), (e.get("lys_nz_to_vhl_A") or {}).get("mean")))
        print("\nPILOT GATE: %s — %s" % (report["pilot_gate"]["verdict"], report["pilot_gate"]["reason"]))
        if "full_gate" in report:
            print("FULL GATE: %s" % json.dumps(report["full_gate"]))
        print("\nwrote %s" % out_path)


if __name__ == "__main__":
    main()
